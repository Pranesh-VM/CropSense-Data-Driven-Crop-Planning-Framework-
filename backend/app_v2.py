"""
CropSense Flask API - Complete Implementation

Routes:
1. Authentication: /api/auth/signup, /api/auth/login
2. Single Prediction: /api/predict (existing - untouched)
3. RINDM Cycle: /api/rindm/* (new)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from itertools import permutations

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Existing imports
from crop_recommendation import FarmerCropRecommender
from src.utils.weather_fetcher import WeatherAPIFetcher
from src.utils.crop_database import get_crop_info

# New imports
from database.db_utils import DatabaseManager
from src.auth.auth import FarmerAuthService, require_auth
from src.services.rindm_cycle_manager import RINDMCycleManager
from src.services.weather_monitor import get_monitor_instance, start_monitor
from src.services.market_price import MarketPriceService

# ============================================================================
# PHASE 3 IMPORTS
# ============================================================================
from src.models.state_transition_simulator import StateTransitionSimulator, EnvironmentState
from src.models.monte_carlo_simulator import MonteCarloSimulator
from src.models.q_learning_agent import QLearningAgent
from src.models.time_series_data_manager import TimeSeriesDataManager

# LSTM imports (optional - graceful fallback if TensorFlow not installed)
try:
    from src.models.lstm_nutrient_predictor import LSTMNutrientPredictor
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    print("⚠ LSTM not available (TensorFlow not installed)")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Initialize services
db = DatabaseManager()
auth_service = FarmerAuthService(db)
recommender = FarmerCropRecommender()
weather_fetcher = WeatherAPIFetcher()
cycle_manager = RINDMCycleManager(db)

# ============================================================================
# PHASE 3 SERVICES
# ============================================================================
transition_sim  = StateTransitionSimulator()
monte_carlo     = MonteCarloSimulator(n_simulations=2000)  # 2000 = fast ~1s response
ts_data_manager = TimeSeriesDataManager(db)

# LSTM Predictor (trained on cross-field data from all farmers)
LSTM_MODEL_PATH = Path(__file__).parent / 'models' / 'lstm_nutrient'
lstm_predictor = None
lstm_trained = False


def _train_lstm_internal(epochs: int = 50, days_back: int = 730) -> dict:
    """
    Internal function to train LSTM on cross-field data.
    Called automatically at startup if model doesn't exist,
    and optionally after each crop cycle completes.
    
    Args:
        epochs: Training epochs (default 50)
        days_back: Days of historical data to use (default 2 years)
    
    Returns:
        dict with training results or error
    """
    global lstm_predictor, lstm_trained
    
    if not LSTM_AVAILABLE:
        return {'success': False, 'error': 'TensorFlow not installed'}
    
    try:
        print(f"\n{'='*60}")
        print(f"Training LSTM on Cross-Field Data (Auto)")
        print(f"{'='*60}")
        
        # Initialize predictor
        lstm_predictor = LSTMNutrientPredictor(
            lookback_days=30,
            forecast_days=30  # LSTM predicts up to 30 days
        )
        
        # Fetch CROSS-FIELD data: farmer_id=None = ALL farmers
        df = ts_data_manager.get_timeseries_for_training(
            farmer_id=None,      # ALL farmers (cross-field learning)
            crop_name=None,      # ALL crops
            days_back=days_back,
            use_synthetic_if_empty=True
        )
        
        if df.empty:
            return {'success': False, 'error': 'No training data available'}
        
        print(f"✓ Loaded {len(df)} cross-field data points")
        
        # Train the model
        result = lstm_predictor.train(df, epochs=epochs, verbose=1)
        
        # Save the trained model
        LSTM_MODEL_PATH.mkdir(parents=True, exist_ok=True)
        lstm_predictor.save_model(str(LSTM_MODEL_PATH))
        
        lstm_trained = True
        
        print(f"✓ LSTM model saved to {LSTM_MODEL_PATH}")
        
        return {
            'success': True,
            'data_points': len(df),
            'epochs_trained': result.get('epochs_trained', epochs),
            'final_loss': result.get('final_loss', 0)
        }
        
    except Exception as e:
        print(f"⚠ LSTM training error: {e}")
        return {'success': False, 'error': str(e)}


# Auto-train LSTM at startup if not already trained
if LSTM_AVAILABLE:
    try:
        lstm_predictor = LSTMNutrientPredictor(lookback_days=30, forecast_days=30)
        if (LSTM_MODEL_PATH / 'lstm_nutrient_model.h5').exists():
            lstm_predictor.load_model(str(LSTM_MODEL_PATH))
            lstm_trained = True
            print("✓ LSTM model loaded (cross-field trained)")
        else:
            print("ℹ LSTM model not found. Auto-training on startup...")
            # Train automatically using cross-field data from DB (or synthetic)
            train_result = _train_lstm_internal(epochs=30, days_back=365)
            if train_result.get('success'):
                print(f"✓ LSTM auto-trained on {train_result.get('data_points', 0)} data points")
            else:
                print(f"⚠ LSTM auto-training skipped: {train_result.get('error')}")
    except Exception as e:
        print(f"⚠ Could not initialize LSTM: {e}")

Q_AGENT_PATH    = Path(__file__).parent / 'models' / 'q_agent.pkl'
q_agent         = QLearningAgent()
if Q_AGENT_PATH.exists():
    try:
        q_agent.load(str(Q_AGENT_PATH))
        print("✓ Q-Learning agent loaded")
    except Exception as e:
        print(f"⚠ Could not load Q-Learning agent: {e}")
else:
    print("⚠ Q-Learning agent not trained yet. POST /api/planning/train-q-agent to train.")

# Seed sample financial history data
def seed_financial_history():
    """Insert sample financial history for demo/testing"""
    try:
        with db.get_connection() as (conn, cursor):
            # Check if sample data already exists
            cursor.execute("SELECT COUNT(*) as cnt FROM cycle_performance_history WHERE crop_name IN ('Rice Demo', 'Wheat Demo', 'Maize Demo')")
            if cursor.fetchone()['cnt'] == 0:
                # Insert sample records (using farmer_id 1 as default)
                sample_data = [
                    (1, 1, 'C001', 'Rice Demo', 'kharif', '2025-06-01', '2025-10-15', 136, 90, 42, 43, 25, 15, 18, 650, 5500, 18.5, 89000, 5000, 84000),
                    (1, 1, 'C002', 'Wheat Demo', 'rabi', '2025-11-01', '2026-03-20', 140, 85, 38, 40, 20, 12, 15, 450, 4800, 21.0, 95000, 4000, 91000),
                    (1, 1, 'C003', 'Maize Demo', 'kharif', '2025-06-15', '2025-10-30', 137, 88, 40, 42, 22, 14, 16, 700, 5200, 16.5, 78000, 6000, 72000),
                ]
                cursor.execute("""
                    INSERT INTO cycle_performance_history 
                    (farmer_id, field_id, cycle_id, crop_name, season, start_date, end_date, duration_days,
                     initial_n, initial_p, initial_k, final_n, final_p, final_k, 
                     total_rainfall_mm, yield_kg_ha, market_price_per_kg, profit_per_ha, soil_penalty, reward)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, sample_data)
                conn.commit()
                print("✓ Sample financial history seeded")
    except Exception as e:
        print(f"⚠ Could not seed financial history: {e}")

seed_financial_history()

# Start weather monitoring in background
MONITOR_ENABLED = os.getenv('ENABLE_WEATHER_MONITOR', 'true').lower() == 'true'
MONITOR_INTERVAL = int(os.getenv('WEATHER_CHECK_INTERVAL_MINUTES', '60'))

if MONITOR_ENABLED:
    weather_monitor = start_monitor(check_interval_minutes=MONITOR_INTERVAL)
    print(f"✓ Weather monitor started (checking every {MONITOR_INTERVAL} minutes)")
else:
    print(f"⚠ Weather monitor disabled (set ENABLE_WEATHER_MONITOR=true to enable)")


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """
    Register a new farmer.
    
    POST /api/auth/signup
    Body: {
        "username": "farmer123",
        "email": "farmer@example.com",
        "password": "password123",
        "phone": "+919876543210"
    }
    """
    try:
        data = request.get_json()
        
        # Required fields
        required = ['username', 'email', 'password']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields: username, email, password'}), 400
        
        result = auth_service.register_farmer(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            phone=data.get('phone')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login farmer.
    
    POST /api/auth/login
    Body: {
        "email": "farmer@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        result = auth_service.login_farmer(
            username_or_email=data['email'],
            password=data['password']
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """
    Get farmer profile (protected route).
    
    GET /api/auth/profile
    Headers: Authorization: Bearer <token>
    """
    try:
        profile = auth_service.get_farmer_profile(current_user['farmer_id'])
        
        if profile:
            return jsonify({
                'success': True,
                'profile': profile
            }), 200
        else:
            return jsonify({'error': 'Profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SERVICE 1: SINGLE CROP PREDICTION (EXISTING - UNTOUCHED)
# ============================================================================

@app.route('/api/predict', methods=['POST'])
def predict_single():
    """
    Single-time crop prediction (existing functionality).
    
    POST /api/predict
    Body: {
        "N": 90,
        "P": 42,
        "K": 43,
        "ph": 6.5,
        "latitude": 13.0827,
        "longitude": 80.2707
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'ph', 'latitude', 'longitude']
        
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch weather data
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        weather = weather_fetcher.get_current_weather(latitude, longitude)
        
        if not weather:
            temperature = 25.0
            humidity = 60.0
            rainfall = 100.0
        else:
            temperature = weather.get('temperature', 25.0)
            humidity = weather.get('humidity', 60.0)
            rainfall = weather.get('rainfall', 100.0)

        # Assemble features
        features = {
            'N': float(data['N']),
            'P': float(data['P']),
            'K': float(data['K']),
            'temperature': temperature,
            'humidity': humidity,
            'ph': float(data['ph']),
            'rainfall': rainfall
        }

        # Run recommendation
        result = recommender.recommend(**features)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SERVICE 2: RINDM CYCLE PLANNING
# ============================================================================

@app.route('/api/rindm/get-recommendations', methods=['POST'])
@require_auth
def get_rindm_recommendations(current_user):
    """
    Get top 3 crop recommendations for RINDM cycle.
    
    POST /api/rindm/get-recommendations
    Headers: Authorization: Bearer <token>
    Body: {
        "N": 90,
        "P": 42,
        "K": 43,
        "ph": 6.5,
        "latitude": 13.0827,
        "longitude": 80.2707
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'ph', 'latitude', 'longitude']
        
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch weather data
        weather = weather_fetcher.get_current_weather(
            float(data['latitude']),
            float(data['longitude'])
        )
        
        if not weather:
            temperature = 25.0
            humidity = 60.0
            rainfall = 100.0
        else:
            temperature = weather.get('temperature', 25.0)
            humidity = weather.get('humidity', 60.0)
            rainfall = weather.get('rainfall', 100.0)

        # Get ensemble prediction
        features = {
            'N': float(data['N']),
            'P': float(data['P']),
            'K': float(data['K']),
            'temperature': temperature,
            'humidity': humidity,
            'ph': float(data['ph']),
            'rainfall': rainfall
        }

        result = recommender.recommend(**features)
        
        # Extract top 3 crops from the new response format
        top_3_crops = result.get('top_3_crops', [])
        crop_1 = top_3_crops[0]['crop'] if len(top_3_crops) > 0 else 'unknown'
        conf_1 = top_3_crops[0]['confidence'] if len(top_3_crops) > 0 else 0.0
        crop_2 = top_3_crops[1]['crop'] if len(top_3_crops) > 1 else 'unknown'
        conf_2 = top_3_crops[1]['confidence'] if len(top_3_crops) > 1 else 0.0
        crop_3 = top_3_crops[2]['crop'] if len(top_3_crops) > 2 else 'unknown'
        conf_3 = top_3_crops[2]['confidence'] if len(top_3_crops) > 2 else 0.0
        
        # Store recommendation in database
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                INSERT INTO cycle_recommendations (
                    farmer_id, recommendation_type,
                    n_kg_ha, p_kg_ha, k_kg_ha, ph,
                    temperature, humidity, rainfall,
                    crop_1, crop_1_confidence,
                    crop_2, crop_2_confidence,
                    crop_3, crop_3_confidence
                )
                VALUES (%s, 'initial', %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, %s, %s)
                RETURNING recommendation_id
            """, (
                current_user['farmer_id'],
                data['N'], data['P'], data['K'], data['ph'],
                temperature, humidity, rainfall,
                crop_1, conf_1,
                crop_2, conf_2,
                crop_3, conf_3
            ))
            
            recommendation_id = cursor.fetchone()['recommendation_id']
        
        # Update field with location for weather monitoring
        if 'latitude' in data and 'longitude' in data:
            with db.get_connection() as (conn, cursor):
                cursor.execute("""
                    UPDATE fields 
                    SET latitude = %s, longitude = %s
                    WHERE farmer_id = %s
                """, (data['latitude'], data['longitude'], current_user['farmer_id']))
        
        return jsonify({
            'success': True,
            'recommendation_id': recommendation_id,
            'recommendations': result,
            'nutrients': {
                'N': data['N'],
                'P': data['P'],
                'K': data['K'],
                'ph': data['ph']
            },
            'weather': {
                'temperature': temperature,
                'humidity': humidity,
                'rainfall': rainfall
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rindm/start-cycle', methods=['POST'])
@require_auth
def start_rindm_cycle(current_user):
    """
    Start a new RINDM cycle with selected crop.
    Fetches nutrient values from previous recommendation - no need to provide again.
    
    POST /api/rindm/start-cycle
    Headers: Authorization: Bearer <token>
    Body: {
        "recommendation_id": 123,
        "selected_crop": "rice",
        "soil_type": "loamy"
    }
    """
    try:
        data = request.get_json()
        required = ['recommendation_id', 'selected_crop', 'soil_type']
        
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields: recommendation_id, selected_crop, soil_type'}), 400
        
        # Fetch nutrient values from recommendation
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT n_kg_ha, p_kg_ha, k_kg_ha, ph
                FROM cycle_recommendations
                WHERE recommendation_id = %s AND farmer_id = %s
            """, (data['recommendation_id'], current_user['farmer_id']))
            
            recommendation = cursor.fetchone()
            if not recommendation:
                return jsonify({'error': 'Recommendation not found or unauthorized'}), 404
            
            initial_n = float(recommendation['n_kg_ha'])
            initial_p = float(recommendation['p_kg_ha'])
            initial_k = float(recommendation['k_kg_ha'])
            initial_ph = float(recommendation['ph'])
        
        # Get farmer's field
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT field_id FROM fields 
                WHERE farmer_id = %s 
                ORDER BY field_id LIMIT 1
            """, (current_user['farmer_id'],))
            
            field = cursor.fetchone()
            if not field:
                return jsonify({'error': 'No field found for farmer'}), 404
            
            field_id = field['field_id']
        
        # Start cycle with fetched nutrient values
        result = cycle_manager.start_new_cycle(
            farmer_id=current_user['farmer_id'],
            field_id=field_id,
            selected_crop=data['selected_crop'],
            initial_n=initial_n,
            initial_p=initial_p,
            initial_k=initial_k,
            initial_ph=initial_ph,
            soil_type=data['soil_type'],
            recommendation_id=data['recommendation_id']
        )
        
        return jsonify(result), 201 if result['success'] else 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rindm/cycle-status/<int:cycle_id>', methods=['GET'])
@require_auth
def get_cycle_status(current_user, cycle_id):
    """
    Get current status of a cycle.
    
    GET /api/rindm/cycle-status/{cycle_id}
    Headers: Authorization: Bearer <token>
    """
    try:
        result = cycle_manager.get_cycle_status(cycle_id)
        
        if not result['success']:
            return jsonify(result), 404
        
        # Verify ownership
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT farmer_id FROM crop_cycles WHERE cycle_id = %s
            """, (cycle_id,))
            
            cycle = cursor.fetchone()
            if not cycle or cycle['farmer_id'] != current_user['farmer_id']:
                return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rindm/active-cycle', methods=['GET'])
@require_auth
def get_active_cycle(current_user):
    """
    Get farmer's active cycle.
    
    GET /api/rindm/active-cycle
    Headers: Authorization: Bearer <token>
    """
    try:
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT * FROM crop_cycles
                WHERE farmer_id = %s AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """, (current_user['farmer_id'],))
            
            cycle = cursor.fetchone()
            
            if not cycle:
                return jsonify({
                    'success': True,
                    'has_active_cycle': False,
                    'message': 'No active cycle'
                }), 200
            
            cycle = dict(cycle)
            
            # Get detailed status
            status_result = cycle_manager.get_cycle_status(cycle['cycle_id'])
            
            return jsonify({
                'success': True,
                'has_active_cycle': True,
                'cycle': status_result
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rindm/complete-cycle/<int:cycle_id>', methods=['POST'])
@require_auth
def complete_cycle(current_user, cycle_id):
    """
    Manually complete a cycle (or it completes automatically).
    Returns final nutrients, next crop recommendations, and fertilizer suggestions.
    
    POST /api/rindm/complete-cycle/{cycle_id}
    Headers: Authorization: Bearer <token>
    """
    try:
        # Verify ownership and get cycle + field info
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT cc.farmer_id, cc.initial_ph, cc.soil_type,
                       f.latitude, f.longitude
                FROM crop_cycles cc
                LEFT JOIN fields f ON cc.field_id = f.field_id
                WHERE cc.cycle_id = %s
            """, (cycle_id,))
            
            cycle_info = cursor.fetchone()
            if not cycle_info or cycle_info['farmer_id'] != current_user['farmer_id']:
                return jsonify({'error': 'Unauthorized'}), 403
            
            cycle_info = dict(cycle_info)
        
        # Complete the cycle
        result = cycle_manager.complete_cycle(cycle_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        final_nutrients = result.get('final_nutrients', {})
        final_n = final_nutrients.get('N', 0)
        final_p = final_nutrients.get('P', 0)
        final_k = final_nutrients.get('K', 0)
        ph = cycle_info.get('initial_ph', 6.5)
        
        # Critical thresholds for fertilizer recommendations
        CRITICAL_THRESHOLDS = {'N': 30, 'P': 10, 'K': 40}
        
        # Check which nutrients are critically low
        low_nutrients = []
        fertilizer_recommendations = []
        
        if final_n < CRITICAL_THRESHOLDS['N']:
            low_nutrients.append('Nitrogen (N)')
            deficit = CRITICAL_THRESHOLDS['N'] - final_n + 20  # Add buffer
            fertilizer_recommendations.append({
                'nutrient': 'Nitrogen',
                'current_level': round(final_n, 1),
                'recommended_addition': round(deficit, 1),
                'fertilizer_options': ['Urea (46-0-0)', 'Ammonium Nitrate (34-0-0)', 'Ammonium Sulfate (21-0-0)']
            })
        
        if final_p < CRITICAL_THRESHOLDS['P']:
            low_nutrients.append('Phosphorus (P)')
            deficit = CRITICAL_THRESHOLDS['P'] - final_p + 10
            fertilizer_recommendations.append({
                'nutrient': 'Phosphorus',
                'current_level': round(final_p, 1),
                'recommended_addition': round(deficit, 1),
                'fertilizer_options': ['Single Super Phosphate (0-16-0)', 'Triple Super Phosphate (0-46-0)', 'DAP (18-46-0)']
            })
        
        if final_k < CRITICAL_THRESHOLDS['K']:
            low_nutrients.append('Potassium (K)')
            deficit = CRITICAL_THRESHOLDS['K'] - final_k + 20
            fertilizer_recommendations.append({
                'nutrient': 'Potassium',
                'current_level': round(final_k, 1),
                'recommended_addition': round(deficit, 1),
                'fertilizer_options': ['Muriate of Potash (0-0-60)', 'Sulfate of Potash (0-0-50)', 'Potassium Nitrate (13-0-44)']
            })
        
        nutrients_too_low = len(low_nutrients) > 0
        
        # Get next crop recommendations based on final nutrients
        next_crop_recommendations = []
        
        try:
            # Fetch current weather for the location
            latitude = cycle_info.get('latitude', 28.6139)
            longitude = cycle_info.get('longitude', 77.2090)
            
            weather_fetcher = WeatherAPIFetcher()
            weather = weather_fetcher.get_current_weather(latitude, longitude)
            
            if weather:
                temperature = weather.get('temperature', 25.0)
                humidity = weather.get('humidity', 60.0)
                rainfall = weather.get('rainfall', 100.0)
            else:
                temperature = 25.0
                humidity = 60.0
                rainfall = 100.0
            
            # Get recommendations using final nutrient levels
            recommendation_result = recommender.recommend(
                N=final_n,
                P=final_p,
                K=final_k,
                temperature=temperature,
                humidity=humidity,
                ph=ph,
                rainfall=rainfall
            )
            
            next_crop_recommendations = recommendation_result.get('top_3_crops', [])
            
        except Exception as e:
            print(f"Warning: Could not fetch next crop recommendations: {e}")
            next_crop_recommendations = []
        
        # ================================================================
        # PHASE 3: Write completed cycle to performance history table with financials
        # ================================================================
        try:
            with db.get_connection() as (conn, cursor):
                # Get cycle details for financial calculations
                cursor.execute("""
                    SELECT cc.cycle_id, cc.crop_name, cc.initial_n_kg_ha, cc.initial_p_kg_ha, 
                           cc.initial_k_kg_ha, cc.final_n_kg_ha, cc.final_p_kg_ha, cc.final_k_kg_ha,
                           cc.start_date, cc.actual_end_date, cc.actual_yield_tonnes_ha, cc.farmer_id, cc.field_id,
                           COALESCE(SUM(re.rainfall_mm), 0) as total_rainfall_mm
                    FROM crop_cycles cc
                    LEFT JOIN rainfall_events re ON cc.cycle_id = re.cycle_id
                    WHERE cc.cycle_id = %s
                    GROUP BY cc.cycle_id, cc.farmer_id, cc.field_id, cc.crop_name, cc.start_date, cc.actual_end_date,
                             cc.initial_n_kg_ha, cc.initial_p_kg_ha, cc.initial_k_kg_ha,
                             cc.final_n_kg_ha, cc.final_p_kg_ha, cc.final_k_kg_ha, cc.actual_yield_tonnes_ha
                """, (cycle_id,))
                
                cycle_data = cursor.fetchone()
                if cycle_data:
                    # Calculate financial metrics
                    seed_cost = 2000.0  # Default ₹/ha
                    fertilizer_cost = 3500.0  # Default ₹/ha
                    labour_cost = 4000.0  # Default ₹/ha
                    market_price = 18.0  # Default ₹/kg (will be overridden by market_price_service)
                    actual_yield = cycle_data['actual_yield_tonnes_ha'] or 5.0
                    
                    try:
                        # Try to get market price for this crop
                        market_prices = MarketPriceService.get_multiple_prices([cycle_data['crop_name']])
                        if market_prices and cycle_data['crop_name'] in market_prices:
                            market_price = market_prices[cycle_data['crop_name']]
                    except:
                        pass
                    
                    revenue = actual_yield * 1000 * market_price  # yield_tonnes * 1000 kg/tonne * price/kg
                    total_cost = seed_cost + fertilizer_cost + labour_cost
                    profit = revenue - total_cost
                    soil_penalty = max(0, (40 - cycle_data['final_n_kg_ha']) * 50)  # Penalize low N
                    reward = profit - soil_penalty
                    
                    # Get season name
                    start_month = cycle_data['start_date'].month if cycle_data['start_date'] else 6
                    if start_month in [6, 7, 8, 9, 10]:
                        season = 'kharif'
                    elif start_month in [11, 12, 1, 2]:
                        season = 'rabi'
                    elif start_month in [3, 4, 5]:
                        season = 'zaid'
                    else:
                        season = 'annual'
                    
                    # Insert or update performance history
                    cursor.execute("""
                        INSERT INTO cycle_performance_history (
                            farmer_id, field_id, cycle_id, crop_name, season,
                            start_date, end_date, duration_days,
                            initial_n, initial_p, initial_k,
                            final_n, final_p, final_k,
                            total_rainfall_mm, yield_kg_ha, market_price_per_kg,
                            profit_per_ha, soil_penalty, reward
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (cycle_id) DO UPDATE SET
                            yield_kg_ha = EXCLUDED.yield_kg_ha,
                            market_price_per_kg = EXCLUDED.market_price_per_kg,
                            profit_per_ha = EXCLUDED.profit_per_ha,
                            reward = EXCLUDED.reward
                    """, (
                        cycle_data['farmer_id'], cycle_data['field_id'], cycle_id, cycle_data['crop_name'], season,
                        cycle_data['start_date'], cycle_data['actual_end_date'], 
                        (cycle_data['actual_end_date'] - cycle_data['start_date']).days if cycle_data['actual_end_date'] else 0,
                        cycle_data['initial_n_kg_ha'], cycle_data['initial_p_kg_ha'], cycle_data['initial_k_kg_ha'],
                        cycle_data['final_n_kg_ha'], cycle_data['final_p_kg_ha'], cycle_data['final_k_kg_ha'],
                        cycle_data['total_rainfall_mm'], actual_yield * 1000, market_price,
                        profit, soil_penalty, reward
                    ))
                    conn.commit()
                    print(f"✓ Cycle {cycle_id} logged to performance history (Profit: ₹{profit:.0f}/ha)")
        except Exception as e:
            print(f"Warning: Could not log cycle to performance history: {e}")
        
        # ================================================================
        # PHASE 3: Retrain LSTM with new cycle data (incremental learning)
        # This runs in background after every 5 completed cycles
        # ================================================================
        try:
            with db.get_connection() as (conn, cursor):
                cursor.execute("SELECT COUNT(*) as cnt FROM cycle_performance_history")
                total_cycles = cursor.fetchone()['cnt']
            
            # Retrain every 5 completed cycles to incorporate new patterns
            if total_cycles > 0 and total_cycles % 5 == 0:
                print(f"ℹ {total_cycles} cycles completed. Triggering LSTM retrain...")
                _train_lstm_internal(epochs=20, days_back=365)
        except Exception as e:
            print(f"Warning: Could not check for LSTM retrain: {e}")

        # Add next crop data to result
        result['next_cycle_data'] = {
            'final_nutrients': {
                'N': round(final_n, 1),
                'P': round(final_p, 1),
                'K': round(final_k, 1),
                'ph': round(ph, 1)
            },
            'nutrients_too_low': nutrients_too_low,
            'low_nutrients': low_nutrients,
            'fertilizer_recommendations': fertilizer_recommendations,
            'next_crop_recommendations': next_crop_recommendations,
            'message': 'Nutrients are too low for optimal crop growth. Consider applying fertilizers before starting a new cycle.' if nutrients_too_low else 'Your soil is ready for a new crop cycle!'
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rindm/check-weather/<int:cycle_id>', methods=['POST'])
@require_auth
def manual_weather_check(current_user, cycle_id):
    """
    Manually trigger weather check (usually automatic).
    
    POST /api/rindm/check-weather/{cycle_id}
    Headers: Authorization: Bearer <token>
    """
    try:
        # Verify ownership
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT farmer_id FROM crop_cycles WHERE cycle_id = %s
            """, (cycle_id,))
            
            cycle = cursor.fetchone()
            if not cycle or cycle['farmer_id'] != current_user['farmer_id']:
                return jsonify({'error': 'Unauthorized'}), 403
        
        result = cycle_manager.check_and_process_rainfall(cycle_id)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rindm/history', methods=['GET'])
@require_auth
def get_cycle_history(current_user):
    """
    Get farmer's cycle history.
    
    GET /api/rindm/history
    Headers: Authorization: Bearer <token>
    """
    try:
        with db.get_connection() as (conn, cursor):
            cursor.execute("""
                SELECT 
                    cycle_id, cycle_number, crop_name, status,
                    start_date, actual_end_date,
                    initial_n_kg_ha, initial_p_kg_ha, initial_k_kg_ha,
                    final_n_kg_ha, final_p_kg_ha, final_k_kg_ha,
                    rainfall_event_count,
                    total_rainfall_loss_n, total_rainfall_loss_p, total_rainfall_loss_k
                FROM crop_cycles
                WHERE farmer_id = %s
                ORDER BY cycle_number DESC
                LIMIT 20
            """, (current_user['farmer_id'],))
            
            cycles = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'success': True,
                'cycles': cycles,
                'total': len(cycles)
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({
        'status': 'ok',
        'message': 'CropSense API is running',
        'services': {
            'authentication': 'enabled',
            'single_prediction': 'enabled',
            'rindm_cycles': 'enabled',
            'weather_monitor': 'enabled' if MONITOR_ENABLED else 'disabled',
            'state_transition': 'enabled',
            'monte_carlo': 'enabled',
            'q_learning': 'trained' if Q_AGENT_PATH.exists() else 'not_trained',
            'lstm_predictor': 'trained' if lstm_trained else ('available' if LSTM_AVAILABLE else 'not_installed')
        }
    }), 200


@app.route('/api/crop-info/<crop_name>', methods=['GET'])
def crop_info(crop_name):
    """Get crop information."""
    try:
        info = get_crop_info(crop_name)
        if not info:
            return jsonify({'error': f'Crop {crop_name} not found'}), 404
        return jsonify(info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PHASE 3: PLANNING ROUTES
# ============================================================================

@app.route('/api/planning/compare-crops', methods=['POST'])
@require_auth
def compare_crop_trajectories(current_user):
    """
    SIMPLIFIED: Show only nutrient depletion prediction for top 3 crops.
    
    Auto-fetches top 3 crops from ensemble model.
    Returns ONLY 30-day nutrient trajectory (N, P, K depletion in kg/ha).
    
    POST /api/planning/compare-crops
    Headers: Authorization: Bearer <token>
    Body: {
        "N": 90, "P": 42, "K": 43,
        "soil_type": "loamy"
    }
    
    Response: {
        "success": true,
        "crops": [
            {
                "crop": "rice",
                "initial": {"N": 90, "P": 42, "K": 43},
                "final": {"N": 45.2, "P": 28.5, "K": 35.1},
                "depletion": {"N": 44.8, "P": 13.5, "K": 7.9}
            }
        ]
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'soil_type']
        if not all(f in data for f in required):
            return jsonify({'success': False, 'error': f'Missing required fields: {required}'}), 400

        n = float(data['N'])
        p = float(data['P'])
        k = float(data['K'])
        soil_type = data['soil_type']
        
        # ================================================================
        # Get top 3 crops from ensemble model
        # ================================================================
        try:
            features = {
                'N': n,
                'P': p,
                'K': k,
                'temperature': float(data.get('temperature', 25.0)),
                'humidity': float(data.get('humidity', 60.0)),
                'ph': float(data.get('ph', 6.5)),
                'rainfall': float(data.get('rainfall', 100.0))
            }
            
            ensemble_result = recommender.recommend(**features)
            top_3 = ensemble_result.get('top_3_crops', [])
            crops = [crop_data['crop'] for crop_data in top_3[:3]] if top_3 else ['rice', 'wheat', 'lentil']
        except Exception as e:
            print(f"⚠ Ensemble failed, using defaults: {e}")
            crops = ['rice', 'wheat', 'lentil']
        
        # ================================================================
        # Calculate 30-day nutrient depletion using LSTM
        # ================================================================
        results = []
        
        # Check if LSTM is trained
        if not lstm_trained or lstm_predictor is None:
            return jsonify({
                'success': False,
                'error': 'LSTM model not trained. Call /api/planning/train-lstm-quick first.'
            }), 400
        
        # For each crop, get LSTM prediction
        for crop in crops:
            try:
                # Get historical data for this crop (or cross-field if not enough)
                recent_data = ts_data_manager.get_timeseries_for_training(
                    farmer_id=None,  # Use cross-field data
                    crop_name=crop,
                    days_back=30,
                    use_synthetic_if_empty=True
                )
                
                if len(recent_data) < 30:
                    # If insufficient real data, supplement with synthetic
                    print(f"⚠ Insufficient data for {crop}, using synthetic")
                    recent_data = ts_data_manager.get_timeseries_for_training(
                        farmer_id=None,
                        crop_name=crop,
                        days_back=30,
                        use_synthetic_if_empty=True
                    )
                
                # Get LSTM prediction for next 30 days
                prediction_result = lstm_predictor.predict_next_days(recent_data)
                
                if not prediction_result.get('success'):
                    print(f"⚠ LSTM prediction failed for {crop}: {prediction_result.get('error')}")
                    continue
                
                # Extract final day prediction (30th day)
                predictions = prediction_result.get('predictions', [])
                if not predictions:
                    print(f"⚠ No predictions returned for {crop}")
                    continue
                
                # Get last day (30 days ahead)
                final_pred = predictions[-1]
                
                final_n = round(final_pred.get('predicted_n', n), 2)
                final_p = round(final_pred.get('predicted_p', p), 2)
                final_k = round(final_pred.get('predicted_k', k), 2)
                
                depletion = {
                    'N': round(n - final_n, 2),
                    'P': round(p - final_p, 2),
                    'K': round(k - final_k, 2)
                }
                
                results.append({
                    'crop': crop,
                    'initial': {'N': n, 'P': p, 'K': k},
                    'final': {
                        'N': final_n,
                        'P': final_p,
                        'K': final_k
                    },
                    'depletion': depletion,
                    'prediction_method': 'lstm'
                })
                
            except Exception as e:
                print(f"⚠ Error predicting for {crop}: {e}")
                continue
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'Could not predict depletion for any crops'
            }), 500
        
        # Sort by total depletion (ascending = gentler crops first)
        results.sort(key=lambda x: x['depletion']['N'] + x['depletion']['P'] + x['depletion']['K'])
        
        return jsonify({
            'success': True,
            'crops': results[:3],  # Return top 3
            'note': 'Predictions using trained LSTM model'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/planning/get-lstm-status', methods=['GET'])
@require_auth
def get_lstm_status(current_user):
    """
    Check LSTM training status.
    GET /api/planning/get-lstm-status
    """
    try:
        model_exists = (LSTM_MODEL_PATH / 'lstm_nutrient_model.h5').exists()
        
        return jsonify({
            'success': True,
            'lstm_trained': lstm_trained,
            'model_exists': model_exists,
            'model_path': str(LSTM_MODEL_PATH)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/planning/train-lstm-quick', methods=['POST'])
@require_auth
def train_lstm_quick(current_user):
    """
    Quick LSTM training with minimal epochs (PC-friendly).
    Uses synthetic data if needed.
    
    POST /api/planning/train-lstm-quick
    Timeout: ~5-10 seconds
    """
    try:
        global lstm_predictor, lstm_trained
        
        if lstm_trained and (LSTM_MODEL_PATH / 'lstm_nutrient_model.h5').exists():
            return jsonify({
                'success': True,
                'message': 'LSTM already trained',
                'status': 'ready'
            }), 200
        
        print("\n🚀 Starting quick LSTM training...")
        
        if not LSTM_AVAILABLE:
            return jsonify({'success': False, 'error': 'TensorFlow not installed'}), 400
        
        # Initialize predictor
        lstm_predictor = LSTMNutrientPredictor(
            lookback_days=30,
            forecast_days=30
        )
        
        # Get cross-field data
        df = ts_data_manager.get_timeseries_for_training(
            farmer_id=None,
            crop_name=None,
            days_back=365,
            use_synthetic_if_empty=True  # Use synthetic if real data insufficient
        )
        
        if df.empty:
            return jsonify({'success': False, 'error': 'No data available'}), 400
        
        print(f"✓ Loaded {len(df)} data points")
        
        # Train with minimal epochs (PC-friendly: 15 epochs for quick training)
        result = lstm_predictor.train(
            df,
            epochs=15,  # Reduced from 50 for PC efficiency
            batch_size=16,  # Smaller batch size
            verbose=0  # Quiet mode
        )
        
        # Save model
        LSTM_MODEL_PATH.mkdir(parents=True, exist_ok=True)
        lstm_predictor.save_model(str(LSTM_MODEL_PATH))
        
        lstm_trained = True
        
        return jsonify({
            'success': True,
            'message': 'LSTM trained successfully',
            'epochs': 15,
            'data_points': len(df),
            'status': 'ready'
        }), 200
        
    except Exception as e:
        print(f"⚠ LSTM training error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/planning/profit-risk-report', methods=['POST'])
@require_auth
def profit_risk_report(current_user):
    """
    Monte Carlo profit distribution for candidate crops using REAL MARKET PRICES.
    Simulates 2000 future scenarios with varying rainfall and market price from Data.gov.in API.
    
    POST /api/planning/profit-risk-report
    Headers: Authorization: Bearer <token>
    Body: {
        "N": 90, "P": 42, "K": 43,
        "soil_type": "loamy",
        "expected_rainfall_mm": 600,
        "candidate_crops": ["rice", "wheat", "lentil"],
        "rainfall_uncertainty_pct": 0.20,
        "price_uncertainty_pct": 0.15
    }
    
    Response: {
        "success": true,
        "risk_profiles": [
            {
                "crop": "rice",
                "scenarios": 2000,
                "base_price_per_quintal": 2150,
                "min_profit_rs": 15000,
                "max_profit_rs": 85000,
                "mean_profit_rs": 48000,
                "median_profit_rs": 50000,
                "deviation_rs": 12000
            }
        ]
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'soil_type']
        if not all(f in data for f in required):
            return jsonify({'success': False, 'error': f'Missing required fields: {required}'}), 400

        # Extract soil nutrient levels
        n = float(data['N'])
        p = float(data['P'])
        k = float(data['K'])
        soil_type = data['soil_type']
        
        # Extract rainfall and uncertainty parameters
        expected_rainfall_mm = float(data.get('expected_rainfall_mm', 600))
        r_unc = float(data.get('rainfall_uncertainty_pct', 0.20))
        p_unc = float(data.get('price_uncertainty_pct', 0.15))
        
        # Extract candidate crops (use defaults if not provided)
        crops = data.get('candidate_crops', ['rice', 'wheat', 'lentil'])
        
        # Create environment state for Monte Carlo simulation
        state = EnvironmentState(
            n=n,
            p=p,
            k=k,
            soil_type=soil_type,
            expected_rainfall_mm=expected_rainfall_mm,
            season_index=int(data.get('season_index', 0))
        )

        # Fetch REAL market prices from Data.gov.in API
        market_prices = MarketPriceService.get_multiple_prices(crops)
        
        # Run Monte Carlo simulation for risk profiling with real prices
        profiles = monte_carlo.compare_crops_risk_profile(
            state, crops,
            rainfall_uncertainty_pct=r_unc,
            price_uncertainty_pct=p_unc,
            crop_prices=market_prices  # Pass real market prices
        )
        
        # ============================================================
        # Format response with field names matching UI expectations
        # ============================================================
        response_profiles = []
        for profile in profiles:
            crop_name = profile.get('crop', '')
            
            # Skip error profiles
            if 'error' in profile:
                continue
            
            # Extract statistics
            mean_profit = profile.get('mean_profit', 0)
            std_profit = profile.get('std_dev', 0)
            
            # Calculate Sharpe Ratio (mean/std if std > 0)
            sharpe_ratio = mean_profit / std_profit if std_profit > 0 else 0
            
            # Extract profit statistics (in Rs amounts)
            # Use field names that MATCH the UI expectations
            response_profiles.append({
                'crop': crop_name,
                'scenarios': profile.get('simulations', 5000),
                'base_price_per_quintal': round(profile.get('base_price_per_quintal', 3500), 2),
                
                # Main profit metrics (NO _rs suffix, NO alternative names)
                'min_profit': round(profile.get('min_profit', 0), 0),
                'max_profit': round(profile.get('max_profit', 0), 0),
                'mean_profit': round(mean_profit, 0),
                'median_profit': round(profile.get('percentile_50', 0), 0),
                'std_profit': round(std_profit, 0),  # UI uses 'std_profit'
                
                # Risk metrics
                'percentile_5': round(profile.get('percentile_5', 0), 0),
                'percentile_25': round(profile.get('percentile_25', 0), 0),
                'percentile_75': round(profile.get('percentile_75', 0), 0),
                'percentile_95': round(profile.get('percentile_95', 0), 0),
                
                # Risk indicators
                'prob_loss': round(profile.get('prob_of_loss', 0), 4),  # UI uses 'prob_loss'
                'sharpe_ratio': round(sharpe_ratio, 2),  # Add Sharpe ratio
                'risk_adjusted_score': profile.get('risk_adjusted_score', 0),  # Used for scoring
                'risk_category': profile.get('risk_category', 'MODERATE_RISK')
            })

        return jsonify({'success': True, 'risk_profiles': response_profiles}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/planning/seasonal-rotation-plan', methods=['POST'])
@require_auth
def seasonal_rotation_plan(current_user):
    """
    Compare all possible 3-crop rotation sequences.
    
    Shows the return cost and nutrient depletion for each order so farmer can choose.
    
    POST /api/planning/seasonal-rotation-plan
    Headers: Authorization: Bearer <token>
    Body: {
        "N": 90, "P": 42, "K": 43,
        "soil_type": "loamy",
        "expected_rainfall_mm": 600,
        "temperature": 25,
        "humidity": 60,
        "ph": 6.5,
        "rainfall": 100
    }
    
    Response: {
        "success": true,
        "top_3_crops": ["rice", "wheat", "lentil"],
        "rotation_sequences": [
            {
                "sequence": ["rice", "wheat", "lentil"],
                "total_profit": 156000,
                "profit_by_season": [52000, 48000, 56000],
                "initial_nutrients": {"N": 90, "P": 42, "K": 43},
                "final_nutrients": {"N": 25, "P": 15, "K": 18},
                "total_depletion": {"N": 65, "P": 27, "K": 25},
                "total_depletion_percent": {"N": 72.2, "P": 64.3, "K": 58.1}
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'soil_type']
        if not all(f in data for f in required):
            return jsonify({'success': False, 'error': f'Missing required fields: {required}'}), 400
        
        # Validate soil_type
        valid_soil_types = ['sandy', 'loamy', 'clay']
        soil_type = data['soil_type'].lower().strip()
        if soil_type not in valid_soil_types:
            return jsonify({
                'success': False,
                'error': f'Invalid soil_type: {data["soil_type"]}. Must be one of: {", ".join(valid_soil_types)}'
            }), 400

        # Get initial state
        initial_state = EnvironmentState(
            n=float(data['N']),
            p=float(data['P']),
            k=float(data['K']),
            soil_type=soil_type,
            expected_rainfall_mm=float(data.get('expected_rainfall_mm', 600)),
            season_index=int(data.get('season_index', 0)),
            temperature=float(data.get('temperature', 25)),
            humidity=float(data.get('humidity', 60))
        )

        # ================================================================
        # Step 1: Get top 3 crops from ensemble model
        # ================================================================
        try:
            features = {
                'N': float(data['N']),
                'P': float(data['P']),
                'K': float(data['K']),
                'temperature': float(data.get('temperature', 25.0)),
                'humidity': float(data.get('humidity', 60.0)),
                'ph': float(data.get('ph', 6.5)),
                'rainfall': float(data.get('rainfall', 100.0))
            }
            
            ensemble_result = recommender.recommend(**features)
            top_3_result = ensemble_result.get('top_3_crops', [])
            top_3_crops = [crop_data['crop'] for crop_data in top_3_result[:3]] if top_3_result else ['rice', 'wheat', 'lentil']
        except Exception as e:
            print(f"⚠ Ensemble failed, using defaults: {e}")
            top_3_crops = ['rice', 'wheat', 'lentil']
        
        # ================================================================
        # Step 2: Generate all permutations (6 possible sequences for 3 crops)
        # ================================================================
        all_sequences = list(permutations(top_3_crops))
        
        # ================================================================
        # Step 3: Simulate each sequence
        # ================================================================
        rotation_results = []
        state_simulator = StateTransitionSimulator()
        
        for sequence in all_sequences:
            try:
                # Get market prices for the crops in sequence
                crop_prices = MarketPriceService.get_multiple_prices(list(sequence))
                
                # Start with initial state
                current_state = initial_state.copy()
                initial_nutrients = {
                    'N': round(current_state.n, 2),
                    'P': round(current_state.p, 2),
                    'K': round(current_state.k, 2)
                }
                
                total_profit = 0
                profit_by_season = []
                
                # Simulate each crop in the sequence
                for idx, crop in enumerate(sequence):
                    # Get market price for this crop
                    crop_price = crop_prices.get(crop) if crop_prices else None
                    
                    # Transition to next state after planting crop
                    next_state, reward, details = state_simulator.transition(
                        state=current_state,
                        crop_action=crop,
                        market_price_override=crop_price
                    )
                    
                    total_profit += reward
                    profit_by_season.append(round(reward, 2))
                    
                    # Move to next season/state
                    current_state = next_state
                
                # Calculate final nutrients and depletion
                final_nutrients = {
                    'N': round(current_state.n, 2),
                    'P': round(current_state.p, 2),
                    'K': round(current_state.k, 2)
                }
                
                total_depletion = {
                    'N': round(initial_nutrients['N'] - final_nutrients['N'], 2),
                    'P': round(initial_nutrients['P'] - final_nutrients['P'], 2),
                    'K': round(initial_nutrients['K'] - final_nutrients['K'], 2)
                }
                
                # Calculate depletion as percentage
                total_depletion_percent = {
                    'N': round((total_depletion['N'] / initial_nutrients['N'] * 100) if initial_nutrients['N'] > 0 else 0, 1),
                    'P': round((total_depletion['P'] / initial_nutrients['P'] * 100) if initial_nutrients['P'] > 0 else 0, 1),
                    'K': round((total_depletion['K'] / initial_nutrients['K'] * 100) if initial_nutrients['K'] > 0 else 0, 1)
                }
                
                # Get Q-Learning score for this sequence
                q_score = 50.0  # Default neutral score
                if q_agent:
                    try:
                        q_score = q_agent.score_sequence(initial_state, list(sequence))
                    except KeyError as e:
                        # Crop not in Q-agent pool, skip scoring
                        print(f"⚠ Q-agent missing crop in pool: {e}")
                    except Exception as e:
                        print(f"⚠ Could not compute Q-score for {sequence}: {e}")
                
                rotation_results.append({
                    'sequence': list(sequence),
                    'total_profit': float(total_profit),
                    'profit_by_season': [float(p) for p in profit_by_season],
                    'initial_nutrients': {k: float(v) for k, v in initial_nutrients.items()},
                    'final_nutrients': {k: float(v) for k, v in final_nutrients.items()},
                    'total_depletion': {k: float(v) for k, v in total_depletion.items()},
                    'total_depletion_percent': {k: float(v) for k, v in total_depletion_percent.items()},
                    'q_learning_score': float(q_score)
                })
            
            except Exception as e:
                print(f"⚠ Error simulating sequence {sequence}: {e}")
                continue
        
        # Check if any sequences succeeded
        if not rotation_results:
            return jsonify({
                'success': False,
                'error': 'Could not simulate any rotation sequences. Please check your soil type and ensure top crops are compatible.'
            }), 500
        
        # Sort by combined score: 70% profit + 30% Q-learning quality
        # Normalize profit to 0-100 scale for fair weighting
        if rotation_results:
            try:
                max_profit = max(r['total_profit'] for r in rotation_results)
                min_profit = min(r['total_profit'] for r in rotation_results)
                profit_range = max_profit - min_profit if max_profit > min_profit else 1
                
                for result in rotation_results:
                    normalized_profit = ((result['total_profit'] - min_profit) / profit_range * 100) if profit_range > 0 else 50
                    result['combined_score'] = float((normalized_profit * 0.7) + (result['q_learning_score'] * 0.3))
                
                rotation_results.sort(key=lambda x: x['combined_score'], reverse=True)
            except Exception as e:
                print(f"⚠ Error computing combined scores: {e}")
                # Fallback: sort by profit only
                rotation_results.sort(key=lambda x: x['total_profit'], reverse=True)
                for result in rotation_results:
                    result['combined_score'] = float(result['total_profit'])
        
        return jsonify({
            'success': True,
            'top_3_crops': top_3_crops,
            'rotation_sequences': rotation_results
        }), 200

    except Exception as e:
        print(f"ERROR in seasonal_rotation_plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/planning/train-q-agent', methods=['POST'])
@require_auth
def train_q_agent_endpoint(current_user):
    """
    Trigger Q-Agent training. Takes ~30-60 seconds.
    Call this once during setup, then again after each growing season.
    
    POST /api/planning/train-q-agent
    Headers: Authorization: Bearer <token>
    Body: {
        "N": 90, "P": 42, "K": 43,
        "soil_type": "loamy",
        "expected_rainfall_mm": 600,
        "num_episodes": 1000,
        "crop_pool": ["rice", "wheat", "lentil", "maize", "mungbean", "chickpea"]
    }
    """
    try:
        data = request.get_json() or {}

        state = EnvironmentState(
            n=float(data.get('N', 90)),
            p=float(data.get('P', 42)),
            k=float(data.get('K', 43)),
            soil_type=data.get('soil_type', 'loamy'),
            expected_rainfall_mm=float(data.get('expected_rainfall_mm', 500)),
            season_index=int(data.get('season_index', 0))
        )

        episodes = int(data.get('num_episodes', 1000))
        crop_pool = data.get('crop_pool', None)  # None = all crops

        # Re-initialise with custom crop pool if provided
        global q_agent
        q_agent = QLearningAgent(crop_pool=crop_pool)
        stats = q_agent.train(state, num_episodes=episodes, verbose=False)
        q_agent.save(str(Q_AGENT_PATH))

        return jsonify({
            'success': True,
            'message': f'Q-Agent trained for {episodes} episodes',
            'model_saved_to': str(Q_AGENT_PATH),
            'training_stats': {
                'episodes': stats.get('episodes_trained'),
                'final_epsilon': round(stats.get('final_epsilon', 0), 4),
                'avg_reward_last_100': round(stats.get('avg_reward_last_100', 0), 2),
                'q_table_nonzero': stats.get('q_table_nonzero')
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/planning/financial-history', methods=['GET'])
@require_auth
def get_financial_history(current_user):
    """
    Get farmer's financial history across all completed cycles.
    Includes seed costs, fertilizer costs, labour charges, revenue, and profit.
    
    GET /api/planning/financial-history
    Headers: Authorization: Bearer <token>
    """
    try:
        records = []
        summary = {
            'total_profit': 0,
            'total_investment': 0,
            'net_return': 0,
            'total_cycles': 0
        }
        
        with db.get_connection() as (conn, cursor):
            # Try to get from cycle_performance_history first
            cursor.execute("""
                SELECT 
                    cph.cycle_id,
                    cph.crop_name,
                    cc.start_date,
                    cc.actual_end_date as end_date,
                    COALESCE(cph.seed_cost_per_ha, 0) as seed_cost,
                    COALESCE(cph.fertilizer_cost_per_ha, 0) as fertilizer_cost,
                    COALESCE(cph.labour_cost_per_ha, 0) as labour_cost,
                    (COALESCE(cph.seed_cost_per_ha, 0) + 
                     COALESCE(cph.fertilizer_cost_per_ha, 0) + 
                     COALESCE(cph.labour_cost_per_ha, 0)) as total_cost,
                    COALESCE(cph.actual_yield_tonnes_ha, 0) * COALESCE(cph.actual_market_price, 0) as revenue,
                    COALESCE(cph.profit_per_ha, 0) as profit,
                    cph.actual_yield_tonnes_ha as yield_per_ha,
                    cph.actual_market_price as market_price
                FROM cycle_performance_history cph
                LEFT JOIN crop_cycles cc ON cph.cycle_id = cc.cycle_id
                WHERE cph.farmer_id = %s
                ORDER BY cc.start_date DESC
            """, (current_user['farmer_id'],))
            
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    records.append({
                        'cycle_id': row['cycle_id'],
                        'crop_name': row['crop_name'],
                        'start_date': str(row['start_date']) if row['start_date'] else None,
                        'end_date': str(row['end_date']) if row['end_date'] else None,
                        'seed_cost': float(row['seed_cost'] or 0),
                        'fertilizer_cost': float(row['fertilizer_cost'] or 0),
                        'labour_cost': float(row['labour_cost'] or 0),
                        'total_cost': float(row['total_cost'] or 0),
                        'revenue': float(row['revenue'] or 0),
                        'profit': float(row['profit'] or 0),
                        'yield_per_ha': float(row['yield_per_ha'] or 0),
                        'market_price': float(row['market_price'] or 0)
                    })
                    summary['total_profit'] += float(row['profit'] or 0)
                    summary['total_investment'] += float(row['total_cost'] or 0)
            else:
                # Fallback: Generate estimated financials from crop_cycles
                cursor.execute("""
                    SELECT 
                        cc.cycle_id,
                        cc.crop_name,
                        cc.start_date,
                        cc.actual_end_date as end_date,
                        cc.actual_yield_tonnes_ha,
                        cnr.average_yield_tonnes_ha as expected_yield
                    FROM crop_cycles cc
                    LEFT JOIN crop_nutrient_requirements cnr ON cc.crop_name = cnr.crop_name
                    WHERE cc.farmer_id = %s AND cc.status = 'completed'
                    ORDER BY cc.start_date DESC
                """, (current_user['farmer_id'],))
                
                rows = cursor.fetchall()
                
                # Estimated costs per crop (in INR per hectare)
                ESTIMATED_COSTS = {
                    'rice': {'seed': 2000, 'fertilizer': 6000, 'labour': 15000},
                    'wheat': {'seed': 2500, 'fertilizer': 5500, 'labour': 12000},
                    'maize': {'seed': 3000, 'fertilizer': 6500, 'labour': 14000},
                    'cotton': {'seed': 4000, 'fertilizer': 7000, 'labour': 18000},
                    'sugarcane': {'seed': 8000, 'fertilizer': 10000, 'labour': 25000},
                    'soybean': {'seed': 3500, 'fertilizer': 4000, 'labour': 10000},
                    'groundnut': {'seed': 5000, 'fertilizer': 4500, 'labour': 12000},
                    'chickpea': {'seed': 3000, 'fertilizer': 3500, 'labour': 8000},
                    'lentil': {'seed': 2500, 'fertilizer': 3000, 'labour': 7500},
                    'mungbean': {'seed': 2000, 'fertilizer': 2500, 'labour': 6000},
                }
                
                # Market prices per kg
                from src.models.state_transition_simulator import DEFAULT_MARKET_PRICES
                
                for row in rows:
                    crop = row['crop_name'].lower()
                    costs = ESTIMATED_COSTS.get(crop, {'seed': 3000, 'fertilizer': 5000, 'labour': 12000})
                    
                    seed_cost = costs['seed']
                    fertilizer_cost = costs['fertilizer']
                    labour_cost = costs['labour']
                    total_cost = seed_cost + fertilizer_cost + labour_cost
                    
                    # Calculate revenue
                    yield_ha = float(row['actual_yield_tonnes_ha'] or row['expected_yield'] or 2.5)
                    price_per_kg = DEFAULT_MARKET_PRICES.get(crop, 25.0)
                    revenue = yield_ha * 1000 * price_per_kg  # tonnes to kg, then multiply by price
                    profit = revenue - total_cost
                    
                    records.append({
                        'cycle_id': row['cycle_id'],
                        'crop_name': row['crop_name'],
                        'start_date': str(row['start_date']) if row['start_date'] else None,
                        'end_date': str(row['end_date']) if row['end_date'] else None,
                        'seed_cost': seed_cost,
                        'fertilizer_cost': fertilizer_cost,
                        'labour_cost': labour_cost,
                        'total_cost': total_cost,
                        'revenue': round(revenue, 2),
                        'profit': round(profit, 2),
                        'yield_per_ha': yield_ha,
                        'market_price': price_per_kg
                    })
                    summary['total_profit'] += profit
                    summary['total_investment'] += total_cost
        
        summary['net_return'] = summary['total_profit'] - summary['total_investment']
        summary['total_cycles'] = len(records)
        
        return jsonify({
            'success': True,
            'records': records,
            'summary': {
                'total_profit': round(summary['total_profit'], 2),
                'total_investment': round(summary['total_investment'], 2),
                'net_return': round(summary['net_return'], 2),
                'total_cycles': summary['total_cycles']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"\n{'='*80}")
    print(f"CropSense API Server")
    print(f"{'='*80}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Weather Monitor: {'Enabled' if MONITOR_ENABLED else 'Disabled'}")
    if MONITOR_ENABLED:
        print(f"Check Interval: {MONITOR_INTERVAL} minutes")
    print(f"{'='*80}\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)

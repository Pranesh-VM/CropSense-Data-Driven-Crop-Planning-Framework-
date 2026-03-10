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

# ============================================================================
# PHASE 3 IMPORTS
# ============================================================================
from src.models.state_transition_simulator import StateTransitionSimulator, EnvironmentState
from src.models.monte_carlo_simulator import MonteCarloSimulator
from src.models.q_learning_agent import QLearningAgent

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
        # PHASE 3: Write completed cycle to performance history table
        # ================================================================
        try:
            with db.get_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO cycle_performance_history (
                        farmer_id, field_id, cycle_id, crop_name,
                        initial_n, initial_p, initial_k,
                        final_n,   final_p,   final_k,
                        total_rainfall_mm
                    )
                    SELECT
                        cc.farmer_id, cc.field_id, cc.cycle_id, cc.crop_name,
                        cc.initial_n_kg_ha, cc.initial_p_kg_ha, cc.initial_k_kg_ha,
                        cc.final_n_kg_ha,   cc.final_p_kg_ha,   cc.final_k_kg_ha,
                        COALESCE(SUM(re.rainfall_mm), 0) as total_rainfall_mm
                    FROM crop_cycles cc
                    LEFT JOIN rainfall_events re ON cc.cycle_id = re.cycle_id
                    WHERE cc.cycle_id = %s
                    GROUP BY cc.cycle_id, cc.farmer_id, cc.field_id, cc.crop_name,
                             cc.initial_n_kg_ha, cc.initial_p_kg_ha, cc.initial_k_kg_ha,
                             cc.final_n_kg_ha,   cc.final_p_kg_ha,   cc.final_k_kg_ha
                    ON CONFLICT DO NOTHING
                """, (cycle_id,))
        except Exception as e:
            print(f"Warning: Could not log cycle to performance history: {e}")

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
            'q_learning': 'trained' if Q_AGENT_PATH.exists() else 'not_trained'
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
    Compare look-ahead soil trajectories for candidate crops.
    Shows which crop leaves the soil in better condition next season.
    
    POST /api/planning/compare-crops
    Headers: Authorization: Bearer <token>
    Body: {
        "N": 90, "P": 42, "K": 43,
        "soil_type": "loamy",
        "season_index": 0,
        "expected_rainfall_mm": 600,
        "candidate_crops": ["rice", "wheat", "lentil"]
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'soil_type']
        if not all(f in data for f in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400

        state = EnvironmentState(
            n=float(data['N']),
            p=float(data['P']),
            k=float(data['K']),
            season_index=int(data.get('season_index', 0)),
            expected_rainfall_mm=float(data.get('expected_rainfall_mm', 500)),
            soil_type=data['soil_type']
        )

        crops = data.get('candidate_crops', ['rice', 'wheat', 'lentil'])
        options = transition_sim.compare_crop_options(state, crops)

        return jsonify({'success': True, 'options': options}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/planning/profit-risk-report', methods=['POST'])
@require_auth
def profit_risk_report(current_user):
    """
    Monte Carlo profit distribution for candidate crops.
    Simulates 2000 future scenarios with varying rainfall and market price.
    
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
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'soil_type']
        if not all(f in data for f in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400

        state = EnvironmentState(
            n=float(data['N']),
            p=float(data['P']),
            k=float(data['K']),
            soil_type=data['soil_type'],
            expected_rainfall_mm=float(data.get('expected_rainfall_mm', 500))
        )

        crops = data.get('candidate_crops', ['rice', 'wheat', 'lentil'])
        r_unc = float(data.get('rainfall_uncertainty_pct', 0.20))
        p_unc = float(data.get('price_uncertainty_pct', 0.15))

        profiles = monte_carlo.compare_crops_risk_profile(
            state, crops,
            rainfall_uncertainty_pct=r_unc,
            price_uncertainty_pct=p_unc
        )

        return jsonify({'success': True, 'risk_profiles': profiles}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/planning/seasonal-rotation-plan', methods=['POST'])
@require_auth
def seasonal_rotation_plan(current_user):
    """
    Get optimal multi-season crop rotation from trained Q-Learning agent.
    
    POST /api/planning/seasonal-rotation-plan
    Headers: Authorization: Bearer <token>
    Body: {
        "N": 90, "P": 42, "K": 43,
        "soil_type": "loamy",
        "expected_rainfall_mm": 600,
        "num_seasons": 5
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'soil_type']
        if not all(f in data for f in required):
            return jsonify({'error': f'Missing required fields: {required}'}), 400

        state = EnvironmentState(
            n=float(data['N']),
            p=float(data['P']),
            k=float(data['K']),
            soil_type=data['soil_type'],
            expected_rainfall_mm=float(data.get('expected_rainfall_mm', 500)),
            season_index=int(data.get('season_index', 0))
        )

        num_seasons = int(data.get('num_seasons', 5))
        plan = q_agent.get_optimal_sequence(state, num_seasons)

        return jsonify({'success': True, 'plan': plan}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        return jsonify({'error': str(e)}), 500


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

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

app = Flask(__name__)
CORS(app)

# Initialize services
db = DatabaseManager()
auth_service = FarmerAuthService(db)
recommender = FarmerCropRecommender()
weather_fetcher = WeatherAPIFetcher()
cycle_manager = RINDMCycleManager(db)

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
        "username": "farmer123",  # or email
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password required'}), 400
        
        result = auth_service.login_farmer(
            username_or_email=data['username'],
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
    
    POST /api/rindm/complete-cycle/{cycle_id}
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
        
        result = cycle_manager.complete_cycle(cycle_id)
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
            'weather_monitor': 'enabled' if MONITOR_ENABLED else 'disabled'
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

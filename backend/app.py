"""
Flask REST API for Crop Recommendation System
Provides endpoints for the React frontend
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

from crop_recommendation import FarmerCropRecommender
from src.utils.weather_fetcher import WeatherAPIFetcher

app = Flask(__name__)
CORS(app)

# Initialize recommender
recommender = FarmerCropRecommender()
weather_fetcher = WeatherAPIFetcher()


# Health check endpoint (optional, can keep for monitoring)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'CropSense API is running'}), 200

# Single endpoint for crop recommendation
@app.route('/recommend-crop', methods=['POST'])
def recommend_crop():
    """
    Single endpoint for crop recommendation.
    Expects JSON:
    {
        "N": float,
        "P": float,
        "K": float,
        "ph": float,
        "latitude": float,
        "longitude": float
    }
    """
    try:
        data = request.get_json()
        required = ['N', 'P', 'K', 'ph', 'latitude', 'longitude']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch weather data internally
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        weather = weather_fetcher.get_current_weather(latitude, longitude)
        if not weather:
            # Fallback: use safe defaults or historical averages
            temperature = 25.0
            humidity = 60.0
            rainfall = 100.0
        else:
            temperature = weather.get('temperature', 25.0)
            humidity = weather.get('humidity', 60.0)
            rainfall = weather.get('rainfall', 100.0)

        # Assemble feature vector in required order
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


# (Optional) Crop info endpoint can be kept if needed
@app.route('/crop-info/<crop_name>', methods=['GET'])
def crop_info(crop_name):
    try:
        from src.utils.crop_database import get_crop_info
        info = get_crop_info(crop_name)
        if not info:
            return jsonify({'error': f'Crop {crop_name} not found'}), 404
        return jsonify(info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

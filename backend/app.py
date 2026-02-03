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

app = Flask(__name__)
CORS(app)

# Initialize recommender
recommender = FarmerCropRecommender()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'CropSense API is running'}), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Get crop recommendation
    
    Expected JSON:
    {
        "nitrogen": float,
        "phosphorus": float,
        "potassium": float,
        "ph": float,
        "rainfall": float,
        "temperature": float,
        "humidity": float,
        "location": string (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'rainfall', 'temperature', 'humidity']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get recommendation
        result = recommender.recommend(
            nitrogen=float(data['nitrogen']),
            phosphorus=float(data['phosphorus']),
            potassium=float(data['potassium']),
            ph=float(data['ph']),
            rainfall=float(data['rainfall']),
            temperature=float(data['temperature']),
            humidity=float(data['humidity']),
            location=data.get('location', '')
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/crop-info/<crop_name>', methods=['GET'])
def crop_info(crop_name):
    """Get information about a specific crop"""
    try:
        from src.utils.crop_database import get_crop_info
        
        info = get_crop_info(crop_name)
        if not info:
            return jsonify({'error': f'Crop {crop_name} not found'}), 404
        
        return jsonify(info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/weather', methods=['GET'])
def weather():
    """
    Get weather data for location
    
    Query params:
    - latitude: float
    - longitude: float
    - location: string (optional, if no lat/lon)
    """
    try:
        from src.utils.weather_fetcher import WeatherDataFetcher
        
        fetcher = WeatherDataFetcher()
        
        location = request.args.get('location')
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        
        if latitude and longitude:
            weather_data = fetcher.get_weather_by_coords(latitude, longitude)
        elif location:
            weather_data = fetcher.get_weather_by_location(location)
        else:
            return jsonify({'error': 'Provide either location or lat/lon'}), 400
        
        return jsonify(weather_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

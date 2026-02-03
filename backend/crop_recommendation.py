"""
Integrated Crop Recommendation with Weather API.

Complete end-to-end system that:
1. Gets farmer's location
2. Fetches weather data automatically
3. Combines with soil nutrients
4. Returns crop recommendation
"""

from pathlib import Path
import joblib
import numpy as np
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.ensemble import EnsemblePredictor
from src.data.preprocess import DataPreprocessor
from src.utils.crop_database import get_crop_info
from src.utils.weather_fetcher import WeatherDataFetcher


class FarmerCropRecommender:
    """
    Complete system for farmer crop recommendation.
    Integrates weather API, soil analysis, and ML ensemble.
    """
    
    def __init__(self, api_key=None, use_mock_weather=None):
        """
        Initialize the recommender system.
        
        Args:
            api_key: OpenWeatherMap API key (optional, will load from env if not provided)
            use_mock_weather: Use mock data for testing (True) or real API (False)
                            If None, auto-detects based on API key availability
        """
        self.preprocessor = DataPreprocessor()
        self.preprocessor.load_encoders()
        
        # Load ensemble from correct path
        current_dir = Path(__file__).parent.absolute()
        model_dir = current_dir / "models"
        ensemble_path = model_dir / "ensemble.pkl"
        
        if not ensemble_path.exists():
            raise FileNotFoundError(f"Ensemble model not found at {ensemble_path}")
        
        self.ensemble = joblib.load(ensemble_path)
        
        # Auto-detect API key if not provided
        if api_key is None:
            api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        
        # Auto-detect use_mock if not explicitly set
        if use_mock_weather is None:
            use_mock_weather = not bool(api_key)  # Use real API if key exists
        
        # Initialize weather fetcher
        self.weather_fetcher = WeatherDataFetcher(
            api_key=api_key,
            use_mock=use_mock_weather
        )
    
    def get_weather_for_crop(self, crop_name, latitude, longitude):
        """
        Fetch weather data for a specific crop.
        
        Args:
            crop_name: Crop to get weather for
            latitude: GPS latitude
            longitude: GPS longitude
        
        Returns:
            Dictionary with weather data
        """
        weather_result = self.weather_fetcher.get_weather_for_crop(
            crop_name=crop_name,
            latitude=latitude,
            longitude=longitude
        )
        return weather_result
    
    def recommend_crop(self, N, P, K, ph, latitude, longitude, crop_to_check=None):
        """
        Get crop recommendation with optional weather integration.
        
        Args:
            N: Nitrogen level
            P: Phosphorus level
            K: Potassium level
            ph: Soil pH
            latitude: GPS latitude for weather
            longitude: GPS longitude for weather
            crop_to_check: Specific crop to evaluate (optional)
        
        Returns:
            Dictionary with recommendation and details
        """
        recommendations = {}
        
        # If specific crop requested, evaluate it
        if crop_to_check:
            crop_names = [crop_to_check.lower()]
        else:
            crop_names = self.preprocessor.label_encoder.classes_
        
        for crop_name in crop_names:
            # Get weather for this crop
            weather_data = self.weather_fetcher.get_weather_for_crop(
                crop_name=crop_name,
                latitude=latitude,
                longitude=longitude
            )
            
            weather = weather_data['weather_data']
            
            # Create prediction input
            raw_input = np.array([[
                N, P, K,
                weather['avg_temperature'],
                weather['avg_humidity'],
                ph,
                weather['total_rainfall']
            ]])
            
            # Scale input
            scaled_input = self.preprocessor.scaler.transform(raw_input)
            
            # Get prediction
            prediction_proba = self.ensemble.predict_proba(scaled_input)[0]
            prediction_idx = np.argmax(prediction_proba)
            predicted_crop = self.preprocessor.label_encoder.classes_[prediction_idx]
            confidence = prediction_proba[prediction_idx]
            
            # Get crop information
            crop_info = get_crop_info(crop_name)
            
            recommendations[crop_name] = {
                'crop': crop_name.capitalize(),
                'suitability_score': float(confidence),
                'weather': {
                    'temperature': weather['avg_temperature'],
                    'humidity': weather['avg_humidity'],
                    'rainfall': weather['total_rainfall']
                },
                'crop_info': crop_info,
                'prediction': predicted_crop.capitalize(),
                'prediction_confidence': float(confidence)
            }
        
        return recommendations
    
    def get_top_recommendations(self, N, P, K, ph, latitude, longitude, top_n=5):
        """
        Get top N crop recommendations sorted by suitability.
        
        Args:
            N: Nitrogen level
            P: Phosphorus level
            K: Potassium level
            ph: Soil pH
            latitude: GPS latitude
            longitude: GPS longitude
            top_n: Number of top recommendations to return
        
        Returns:
            List of top recommendations
        """
        # Get all crops with weather
        all_recs = self.recommend_crop(N, P, K, ph, latitude, longitude)
        
        # Sort by suitability score
        sorted_recs = sorted(
            all_recs.items(),
            key=lambda x: x[1]['suitability_score'],
            reverse=True
        )
        
        # Return top N
        top_recs = sorted_recs[:top_n]
        
        return [
            {
                'rank': i + 1,
                'crop': data['crop'],
                'suitability_score': f"{data['suitability_score']:.2%}",
                'temperature': f"{data['weather']['temperature']}°C",
                'humidity': f"{data['weather']['humidity']}%",
                'rainfall': f"{data['weather']['rainfall']}mm",
                'cycle_days': data['crop_info']['cycle_duration_days'],
                'season': data['crop_info']['season']
            }
            for i, (crop_name, data) in enumerate(top_recs)
        ]


def format_recommendation(recommendations):
    """Format recommendation for display."""
    print("\n" + "=" * 80)
    print("🌾 CROP RECOMMENDATION SYSTEM - Results")
    print("=" * 80)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n#{rec['rank']} {rec['crop'].upper()}")
        print(f"  Suitability: {rec['suitability_score']}")
        print(f"  Expected Weather:")
        print(f"    • Temperature: {rec['temperature']}")
        print(f"    • Humidity: {rec['humidity']}")
        print(f"    • Rainfall: {rec['rainfall']}")
        print(f"  Crop Info:")
        print(f"    • Growing Period: {rec['cycle_days']} days ({rec['cycle_days']/30:.1f} months)")
        print(f"    • Season: {rec['season']}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CropSense: Integrated Crop Recommendation System")
    print("=" * 80)
    
    # Initialize system (use mock weather for demo)
    recommender = FarmerCropRecommender(use_mock_weather=True)
    
    # Example: Farmer in Delhi with soil parameters
    print("\n📍 SCENARIO: Farmer in Delhi (Latitude: 28.7041, Longitude: 77.1025)")
    print("-" * 80)
    
    N = 90          # From soil report
    P = 42          # From soil report
    K = 43          # From soil report
    ph = 6.5        # From soil report
    latitude = 28.7041
    longitude = 77.1025
    
    print(f"\nSoil Parameters (from farmer's soil report):")
    print(f"  Nitrogen (N): {N} kg/ha")
    print(f"  Phosphorus (P): {P} kg/ha")
    print(f"  Potassium (K): {K} kg/ha")
    print(f"  Soil pH: {ph}")
    
    # Get top 5 recommendations
    print(f"\nFetching weather data and generating recommendations...")
    recommendations = recommender.get_top_recommendations(
        N=N, P=P, K=K, ph=ph,
        latitude=latitude,
        longitude=longitude,
        top_n=5
    )
    
    format_recommendation(recommendations)
    
    # Example 2: Different soil parameters
    print("\n\n" + "=" * 80)
    print("📍 SCENARIO 2: Different Soil Conditions")
    print("-" * 80)
    
    N2 = 120
    P2 = 60
    K2 = 50
    ph2 = 7.0
    
    print(f"\nSoil Parameters:")
    print(f"  Nitrogen (N): {N2} kg/ha")
    print(f"  Phosphorus (P): {P2} kg/ha")
    print(f"  Potassium (K): {K2} kg/ha")
    print(f"  Soil pH: {ph2}")
    
    recommendations2 = recommender.get_top_recommendations(
        N=N2, P=P2, K=K2, ph=ph2,
        latitude=latitude,
        longitude=longitude,
        top_n=5
    )
    
    format_recommendation(recommendations2)
    
    # Usage instructions
    print("\n\n" + "=" * 80)
    print("HOW TO USE WITH REAL WEATHER DATA")
    print("=" * 80)
    print("""
1. Get OpenWeatherMap API Key:
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Copy API key

2. Use with Real API:
   
   from crop_recommendation import FarmerCropRecommender
   
   # Initialize with API key (no mock data)
   recommender = FarmerCropRecommender(
       api_key='your_api_key_here',
       use_mock_weather=False
   )
   
   # Get recommendations
   recommendations = recommender.get_top_recommendations(
       N=90, P=42, K=43, ph=6.5,
       latitude=28.7041,
       longitude=77.1025,
       top_n=5
   )

3. Location Input Methods:
   - GPS coordinates (most accurate)
   - Postal code (needs geocoding)
   - City name (needs geocoding)

4. Soil Report Input:
   - Farmers get this from agricultural labs
   - Contains: N, P, K, pH, etc.

System Flow:
┌─────────────────────────────────┐
│ Farmer provides:                │
│ • Soil report (N,P,K,pH)        │
│ • Location (GPS/postal code)    │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ System fetches:                 │
│ • Weather from OpenWeatherMap   │
│ • Crop cycle from database      │
│ • Soil suitability from ML      │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ Returns:                        │
│ • Top 5 crop recommendations    │
│ • Weather conditions            │
│ • Growing period                │
│ • Confidence scores             │
└─────────────────────────────────┘
""")
    
    print("=" * 80)

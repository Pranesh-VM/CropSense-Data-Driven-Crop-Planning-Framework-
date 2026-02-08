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
        self.preprocessor = DataPreprocessor()
        self.preprocessor.load_encoders()
        current_dir = Path(__file__).parent.absolute()
        model_dir = current_dir / "models"
        ensemble_path = model_dir / "ensemble.pkl"
        if not ensemble_path.exists():
            raise FileNotFoundError(f"Ensemble model not found at {ensemble_path}")
        self.ensemble = joblib.load(ensemble_path)

    def recommend(self, N, P, K, temperature, humidity, ph, rainfall):
        """
        Recommend the top 3 crops for the given parameters.
        Args:
            N, P, K, temperature, humidity, ph, rainfall: float
        Returns:
            dict: { 'top_3_crops': [{'crop': str, 'confidence': float}, ...] }
        """
        # Assemble feature vector in required order
        features = [N, P, K, temperature, humidity, ph, rainfall]
        X = self.preprocessor.scaler.transform([features])
        proba = self.ensemble.predict_proba(X)[0]
        
        # Get top 3 indices and their probabilities
        top_3_indices = np.argsort(proba)[-3:][::-1]
        top_3_crops = []
        
        for idx in top_3_indices:
            crop = self.preprocessor.label_encoder.inverse_transform([idx])[0]
            confidence = float(proba[idx])
            top_3_crops.append({'crop': crop, 'confidence': confidence})
        
        return {'top_3_crops': top_3_crops}

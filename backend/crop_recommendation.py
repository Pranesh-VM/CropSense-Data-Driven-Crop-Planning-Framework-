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
        Recommend the best crop for the given parameters.
        Args:
            N, P, K, temperature, humidity, ph, rainfall: float
        Returns:
            dict: { 'predicted_crop': str, 'confidence': float }
        """
        # Assemble feature vector in required order
        features = [N, P, K, temperature, humidity, ph, rainfall]
        X = self.preprocessor.scaler.transform([features])
        pred = self.ensemble.predict(X)[0]
        proba = self.ensemble.predict_proba(X)[0]
        confidence = max(proba)
        crop = self.preprocessor.label_encoder.inverse_transform([pred])[0]
        return {'predicted_crop': crop, 'confidence': float(confidence)}

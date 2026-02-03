"""
Crop Recommendation Inference Script.

Takes nutrient and climate values as input and recommends the best crop
using the trained soft voting ensemble.
"""

from pathlib import Path
import joblib
import numpy as np
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.ensemble import EnsemblePredictor
from src.data.preprocess import DataPreprocessor


def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Predict best crop for given nutrient and climate values.
    
    Args:
        N: Nitrogen level (numeric)
        P: Phosphorus level (numeric)
        K: Potassium level (numeric)
        temperature: Temperature in Celsius (numeric)
        humidity: Humidity percentage (numeric)
        ph: Soil pH (numeric)
        rainfall: Rainfall in mm (numeric)
    
    Returns:
        Dictionary with prediction details
    """
    # Load preprocessors
    preprocessor = DataPreprocessor()
    preprocessor.load_encoders()
    
    # Create input array in correct order: [N, P, K, temperature, humidity, ph, rainfall]
    raw_input = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    
    # Scale the input using saved scaler
    scaled_input = preprocessor.scaler.transform(raw_input)
    
    # Load saved ensemble directly
    model_dir = Path(__file__).parent / "models"
    ensemble = joblib.load(model_dir / "ensemble.pkl")
    
    # Get prediction and probabilities
    prediction = ensemble.predict(scaled_input)[0]
    probabilities = ensemble.predict_proba(scaled_input)[0]
    
    # Decode prediction
    crop_name = preprocessor.label_encoder.inverse_transform([prediction])[0]
    
    # Get all crops with their probabilities (sorted by probability)
    all_crops = preprocessor.label_encoder.classes_
    crop_probs = list(zip(all_crops, probabilities))
    crop_probs_sorted = sorted(crop_probs, key=lambda x: x[1], reverse=True)
    
    return {
        'recommended_crop': crop_name,
        'confidence': probabilities[prediction],
        'top_5_recommendations': crop_probs_sorted[:5]
    }


def format_result(result):
    """Format prediction result for display."""
    print("\n" + "=" * 70)
    print("CROP RECOMMENDATION RESULT")
    print("=" * 70)
    
    print(f"\n🌾 Recommended Crop: {result['recommended_crop'].upper()}")
    print(f"📊 Confidence Score: {result['confidence']:.2%}")
    
    print("\n📋 Top 5 Recommendations:")
    print("-" * 70)
    for i, (crop, prob) in enumerate(result['top_5_recommendations'], 1):
        bar = "█" * int(prob * 30) + "░" * (30 - int(prob * 30))
        print(f"{i}. {crop.capitalize():15} {prob:.2%} |{bar}|")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CropSense: Crop Recommendation Inference Engine")
    print("=" * 70)
    
    # Example 1: Optimal conditions for Rice
    print("\n\n📍 EXAMPLE 1: Rice Growing Conditions")
    print("-" * 70)
    result1 = predict_crop(
        N=90,           # Nitrogen
        P=42,           # Phosphorus
        K=43,           # Potassium
        temperature=20.88,
        humidity=82.0,
        ph=6.5,
        rainfall=203.0
    )
    format_result(result1)
    
    # Example 2: Maize growing conditions
    print("\n📍 EXAMPLE 2: Maize Growing Conditions")
    print("-" * 70)
    result2 = predict_crop(
        N=120,
        P=60,
        K=50,
        temperature=25.5,
        humidity=70.0,
        ph=7.0,
        rainfall=150.0
    )
    format_result(result2)
    
    # Example 3: Apple growing conditions
    print("\n📍 EXAMPLE 3: Apple Growing Conditions")
    print("-" * 70)
    result3 = predict_crop(
        N=80,
        P=35,
        K=40,
        temperature=12.5,
        humidity=65.0,
        ph=6.8,
        rainfall=180.0
    )
    format_result(result3)
    
    # Example 4: Interactive mode
    print("\n" + "=" * 70)
    print("🎯 INTERACTIVE MODE - Try Your Own Values!")
    print("=" * 70)
    
    try:
        print("\nEnter nutrient and climate values (or press Ctrl+C to exit):")
        N = float(input("Nitrogen (N): "))
        P = float(input("Phosphorus (P): "))
        K = float(input("Potassium (K): "))
        temperature = float(input("Temperature (°C): "))
        humidity = float(input("Humidity (%): "))
        ph = float(input("Soil pH: "))
        rainfall = float(input("Rainfall (mm): "))
        
        result = predict_crop(N, P, K, temperature, humidity, ph, rainfall)
        format_result(result)
        
    except KeyboardInterrupt:
        print("\n\nExiting interactive mode...")
    except Exception as e:
        print(f"\n❌ Error: {e}")

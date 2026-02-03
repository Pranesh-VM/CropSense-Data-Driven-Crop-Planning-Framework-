"""Interactive test of the crop recommendation system."""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from crop_recommendation import FarmerCropRecommender

def get_float_input(prompt):
    """Get float input with validation."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def main():
    print("\n" + "="*70)
    print("🌾 CropSense: Farmer Crop Recommendation System")
    print("="*70)
    
    # Initialize system
    print("\n⏳ Initializing AI recommendation system...")
    recommender = FarmerCropRecommender()
    print("✅ System ready!\n")
    
    # Get soil parameters
    print("-"*70)
    print("📋 STEP 1: Enter Your Soil Nutrient Analysis")
    print("-"*70)
    
    N = get_float_input("Nitrogen (N) level [0-150]: ")
    P = get_float_input("Phosphorus (P) level [0-150]: ")
    K = get_float_input("Potassium (K) level [0-205]: ")
    ph = get_float_input("Soil pH [0-14]: ")
    
    # Get location
    print("\n" + "-"*70)
    print("📍 STEP 2: Enter Your Location (GPS Coordinates)")
    print("-"*70)
    print("(Or press Enter to use default: Bangalore, India)")
    
    lat_input = input("Latitude [default: 12.9716]: ").strip()
    longitude_input = input("Longitude [default: 77.5946]: ").strip()
    
    latitude = float(lat_input) if lat_input else 12.9716
    longitude = float(longitude_input) if longitude_input else 77.5946
    
    # Get top N recommendations
    print("\n" + "-"*70)
    print("🎯 STEP 3: How Many Recommendations?")
    print("-"*70)
    top_n = int(input("Number of crop recommendations [default: 5]: ") or "5")
    
    # Generate recommendations
    print("\n" + "="*70)
    print("⏳ Analyzing soil, weather, and crop compatibility...")
    print("="*70)
    
    try:
        recommendations = recommender.get_top_recommendations(
            N=N, P=P, K=K, ph=ph,
            latitude=latitude, longitude=longitude,
            top_n=top_n
        )
        
        # Display results
        print("\n" + "="*70)
        print("✅ TOP CROP RECOMMENDATIONS FOR YOUR FARM")
        print("="*70 + "\n")
        
        for rec in recommendations:
            print(f"🏆 Rank #{rec['rank']}")
            print(f"   🌱 Crop: {rec['crop'].upper()}")
            print(f"   📊 Suitability Score: {rec['suitability_score']}")
            print(f"   📅 Growing Period: {rec['cycle_days']} days")
            print(f"   🌍 Season: {rec['season']}")
            print(f"   🌡️  Weather Forecast:")
            print(f"      • Temperature: {rec['temperature']}")
            print(f"      • Humidity: {rec['humidity']}")
            print(f"      • Expected Rainfall: {rec['rainfall']}")
            print()
        
        # Summary
        print("="*70)
        print("📝 SOIL SUMMARY")
        print("="*70)
        print(f"Nitrogen (N):   {N}")
        print(f"Phosphorus (P): {P}")
        print(f"Potassium (K):  {K}")
        print(f"Soil pH:        {ph}")
        print(f"Location:       Latitude {latitude}, Longitude {longitude}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

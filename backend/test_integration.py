"""Quick test of integrated system."""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("Testing Integrated Crop Recommendation System")
print("=" * 70)

try:
    print("\n1. Importing modules...")
    from crop_recommendation import FarmerCropRecommender
    print("   ✓ Modules imported")
    
    print("\n2. Initializing system...")
    # Auto-detect real API or mock mode based on .env file
    recommender = FarmerCropRecommender()
    print("   ✓ System initialized")
    
    print("\n3. Getting recommendations for rice conditions...")
    recs = recommender.get_top_recommendations(
        N=90, P=42, K=43, ph=6.5,
        latitude=28.7041,
        longitude=77.1025,
        top_n=3
    )
    print("   ✓ Recommendations generated")
    
    print("\n" + "=" * 70)
    print("✅ CROP RECOMMENDATIONS")
    print("=" * 70)
    for rec in recs:
        print(f"\n#{rec['rank']} {rec['crop'].upper()}")
        print(f"   Suitability: {rec['suitability_score']}")
        print(f"   Growing Period: {rec['cycle_days']} days")
        print(f"   Expected Season: {rec['season']}")
        print(f"   Weather: {rec['temperature']}, {rec['humidity']}, Rainfall: {rec['rainfall']}")
    
    print("\n" + "=" * 70)
    print("✅ WEATHER API INTEGRATION SUCCESSFUL!")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


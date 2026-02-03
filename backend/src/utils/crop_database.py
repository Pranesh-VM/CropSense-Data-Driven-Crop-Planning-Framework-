"""
Crop Cycle Duration Database.

Standard growing period for each crop in the recommendation system.
Data sourced from agricultural research and FAO standards.
"""

CROP_CYCLE_DURATION = {
    # Duration in days (approximate average)
    'rice': 120,          # 4 months
    'maize': 100,         # 3.3 months
    'chickpea': 100,      # 3.3 months
    'kidneybeans': 90,    # 3 months
    'pigeonpeas': 240,    # 8 months
    'mothbeans': 75,      # 2.5 months
    'mungbean': 60,       # 2 months
    'blackgram': 90,      # 3 months
    'lentil': 110,        # 3.7 months
    'pomegranate': 210,   # 7 months (perennial, mature fruit)
    'banana': 270,        # 9 months
    'mango': 150,         # 5 months (flowering to harvest)
    'coconut': 365,       # 12 months (annually)
    'cotton': 180,        # 6 months
    'coffee': 365,        # 12 months (annual cycle)
    'jute': 120,          # 4 months
    'apple': 150,         # 5 months (growing season)
    'orange': 240,        # 8 months
    'papaya': 270,        # 9 months
    'watermelon': 80,     # 2.7 months
    'grapes': 150,        # 5 months
    'muskmelon': 90,      # 3 months
}

CROP_SEASON = {
    # Primary season for planting
    'rice': 'Monsoon (Jun-Sep)',
    'maize': 'Summer/Monsoon (Mar-Jul)',
    'chickpea': 'Winter (Oct-Jan)',
    'kidneybeans': 'Summer (Mar-Jun)',
    'pigeonpeas': 'Monsoon (Jun-Sep)',
    'mothbeans': 'Summer (Mar-Jun)',
    'mungbean': 'Summer (Mar-Jun)',
    'blackgram': 'Summer/Monsoon (Mar-Sep)',
    'lentil': 'Winter (Oct-Jan)',
    'pomegranate': 'Summer (Mar-Jun)',
    'banana': 'Year-round (Monsoon preferred)',
    'mango': 'Spring/Early Summer (Feb-Jun)',
    'coconut': 'Year-round (Monsoon best)',
    'cotton': 'Summer (May-Sep)',
    'coffee': 'Monsoon (Jun-Oct)',
    'jute': 'Summer (Mar-Jul)',
    'apple': 'Spring/Summer (Mar-Aug)',
    'orange': 'Winter/Spring (Oct-Mar)',
    'papaya': 'Year-round (Summer best)',
    'watermelon': 'Summer (Feb-May)',
    'grapes': 'Spring/Summer (Mar-Aug)',
    'muskmelon': 'Summer (Feb-May)',
}

CROP_WATER_REQUIREMENT = {
    # Annual water requirement in mm
    'rice': 1000,
    'maize': 400,
    'chickpea': 250,
    'kidneybeans': 300,
    'pigeonpeas': 600,
    'mothbeans': 200,
    'mungbean': 250,
    'blackgram': 300,
    'lentil': 200,
    'pomegranate': 600,
    'banana': 1500,
    'mango': 600,
    'coconut': 1500,
    'cotton': 600,
    'coffee': 1500,
    'jute': 2000,
    'apple': 600,
    'orange': 1000,
    'papaya': 1000,
    'watermelon': 400,
    'grapes': 500,
    'muskmelon': 400,
}

CROP_OPTIMAL_TEMP = {
    # Optimal temperature range in Celsius (min, max)
    'rice': (20, 30),
    'maize': (21, 27),
    'chickpea': (15, 25),
    'kidneybeans': (18, 28),
    'pigeonpeas': (20, 30),
    'mothbeans': (20, 30),
    'mungbean': (25, 30),
    'blackgram': (20, 30),
    'lentil': (15, 25),
    'pomegranate': (20, 30),
    'banana': (18, 28),
    'mango': (24, 30),
    'coconut': (24, 32),
    'cotton': (21, 30),
    'coffee': (15, 24),
    'jute': (24, 30),
    'apple': (7, 24),
    'orange': (13, 29),
    'papaya': (21, 32),
    'watermelon': (21, 32),
    'grapes': (12, 28),
    'muskmelon': (21, 30),
}

def get_crop_cycle(crop_name):
    """Get crop cycle duration in days."""
    return CROP_CYCLE_DURATION.get(crop_name.lower(), 90)  # Default 90 days

def get_crop_season(crop_name):
    """Get primary planting season."""
    return CROP_SEASON.get(crop_name.lower(), 'Year-round')

def get_water_requirement(crop_name):
    """Get annual water requirement in mm."""
    return CROP_WATER_REQUIREMENT.get(crop_name.lower(), 500)

def get_optimal_temp_range(crop_name):
    """Get optimal temperature range (min, max)."""
    return CROP_OPTIMAL_TEMP.get(crop_name.lower(), (15, 30))

def get_crop_info(crop_name):
    """Get complete crop information."""
    crop_name = crop_name.lower()
    return {
        'crop': crop_name.capitalize(),
        'cycle_duration_days': get_crop_cycle(crop_name),
        'season': get_crop_season(crop_name),
        'water_requirement_mm': get_water_requirement(crop_name),
        'optimal_temp_range_c': get_optimal_temp_range(crop_name),
    }

# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Crop Cycle Information Database")
    print("=" * 70)
    
    test_crops = ['rice', 'maize', 'cotton', 'apple', 'watermelon']
    
    for crop in test_crops:
        info = get_crop_info(crop)
        print(f"\n{info['crop'].upper()}")
        print(f"  Cycle Duration: {info['cycle_duration_days']} days ({info['cycle_duration_days']/30:.1f} months)")
        print(f"  Season: {info['season']}")
        print(f"  Water Needed: {info['water_requirement_mm']} mm/year")
        print(f"  Optimal Temp: {info['optimal_temp_range_c'][0]}°C - {info['optimal_temp_range_c'][1]}°C")

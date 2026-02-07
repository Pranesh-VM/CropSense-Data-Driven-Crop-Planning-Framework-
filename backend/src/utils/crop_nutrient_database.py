"""
Crop Nutrient Uptake Database

Complete nutrient requirements (N, P, K) for all 22 crops in the system.
Data sourced from:
- ICAR (Indian Council of Agricultural Research)
- FAO Fertilizer Guidelines
- USDA Nutrient Management
- State Agricultural Universities Research

Units: kg/ha (kilograms per hectare) for average yield
"""

from typing import Dict, Optional, Tuple


# Complete nutrient uptake data for all 22 crops
CROP_NUTRIENT_UPTAKE = {
    'rice': {
        'N_uptake_kg_ha': 120,
        'P_uptake_kg_ha': 40,
        'K_uptake_kg_ha': 140,
        'cycle_days': 120,
        'average_yield_tonnes_ha': 5.0,
        'source': 'ICAR Rice Research 2020'
    },
    'maize': {
        'N_uptake_kg_ha': 150,
        'P_uptake_kg_ha': 50,
        'K_uptake_kg_ha': 180,
        'cycle_days': 100,
        'average_yield_tonnes_ha': 6.0,
        'source': 'FAO Maize Production Guide'
    },
    'chickpea': {
        'N_uptake_kg_ha': 80,   # Legume - fixes N from atmosphere
        'P_uptake_kg_ha': 30,
        'K_uptake_kg_ha': 40,
        'cycle_days': 100,
        'average_yield_tonnes_ha': 2.0,
        'source': 'ICAR Pulses Research'
    },
    'kidneybeans': {
        'N_uptake_kg_ha': 70,   # Legume
        'P_uptake_kg_ha': 25,
        'K_uptake_kg_ha': 50,
        'cycle_days': 90,
        'average_yield_tonnes_ha': 1.8,
        'source': 'USDA Bean Production'
    },
    'pigeonpeas': {
        'N_uptake_kg_ha': 75,   # Legume
        'P_uptake_kg_ha': 30,
        'K_uptake_kg_ha': 45,
        'cycle_days': 240,
        'average_yield_tonnes_ha': 2.2,
        'source': 'ICAR Pulses Research'
    },
    'mothbeans': {
        'N_uptake_kg_ha': 60,   # Legume
        'P_uptake_kg_ha': 20,
        'K_uptake_kg_ha': 35,
        'cycle_days': 75,
        'average_yield_tonnes_ha': 1.5,
        'source': 'Arid Zone Research'
    },
    'mungbean': {
        'N_uptake_kg_ha': 65,   # Legume
        'P_uptake_kg_ha': 22,
        'K_uptake_kg_ha': 40,
        'cycle_days': 60,
        'average_yield_tonnes_ha': 1.2,
        'source': 'ICAR Pulses Research'
    },
    'blackgram': {
        'N_uptake_kg_ha': 70,   # Legume
        'P_uptake_kg_ha': 25,
        'K_uptake_kg_ha': 45,
        'cycle_days': 90,
        'average_yield_tonnes_ha': 1.5,
        'source': 'ICAR Pulses Research'
    },
    'lentil': {
        'N_uptake_kg_ha': 75,   # Legume
        'P_uptake_kg_ha': 28,
        'K_uptake_kg_ha': 42,
        'cycle_days': 110,
        'average_yield_tonnes_ha': 1.8,
        'source': 'FAO Lentil Production'
    },
    'pomegranate': {
        'N_uptake_kg_ha': 200,  # Perennial fruit crop
        'P_uptake_kg_ha': 60,
        'K_uptake_kg_ha': 250,
        'cycle_days': 210,
        'average_yield_tonnes_ha': 15.0,
        'source': 'ICAR Horticulture Research'
    },
    'banana': {
        'N_uptake_kg_ha': 300,  # Heavy feeder
        'P_uptake_kg_ha': 80,
        'K_uptake_kg_ha': 500,  # Very high K requirement
        'cycle_days': 270,
        'average_yield_tonnes_ha': 40.0,
        'source': 'ICAR Banana Research'
    },
    'mango': {
        'N_uptake_kg_ha': 250,  # Perennial fruit
        'P_uptake_kg_ha': 70,
        'K_uptake_kg_ha': 300,
        'cycle_days': 150,
        'average_yield_tonnes_ha': 10.0,
        'source': 'ICAR Mango Research'
    },
    'coconut': {
        'N_uptake_kg_ha': 180,  # Perennial palm
        'P_uptake_kg_ha': 50,
        'K_uptake_kg_ha': 350,  # High K requirement
        'cycle_days': 365,
        'average_yield_tonnes_ha': 8.0,
        'source': 'ICAR Coconut Research'
    },
    'cotton': {
        'N_uptake_kg_ha': 160,  # Fiber crop
        'P_uptake_kg_ha': 55,
        'K_uptake_kg_ha': 200,
        'cycle_days': 180,
        'average_yield_tonnes_ha': 3.0,
        'source': 'ICAR Cotton Research'
    },
    'coffee': {
        'N_uptake_kg_ha': 220,  # Perennial plantation
        'P_uptake_kg_ha': 65,
        'K_uptake_kg_ha': 280,
        'cycle_days': 365,
        'average_yield_tonnes_ha': 1.5,
        'source': 'Coffee Board of India'
    },
    'jute': {
        'N_uptake_kg_ha': 110,  # Fiber crop
        'P_uptake_kg_ha': 40,
        'K_uptake_kg_ha': 90,
        'cycle_days': 120,
        'average_yield_tonnes_ha': 2.5,
        'source': 'ICAR Jute Research'
    },
    'apple': {
        'N_uptake_kg_ha': 180,  # Perennial fruit
        'P_uptake_kg_ha': 55,
        'K_uptake_kg_ha': 220,
        'cycle_days': 150,
        'average_yield_tonnes_ha': 12.0,
        'source': 'ICAR Temperate Horticulture'
    },
    'orange': {
        'N_uptake_kg_ha': 200,  # Citrus
        'P_uptake_kg_ha': 60,
        'K_uptake_kg_ha': 240,
        'cycle_days': 240,
        'average_yield_tonnes_ha': 20.0,
        'source': 'ICAR Citrus Research'
    },
    'papaya': {
        'N_uptake_kg_ha': 150,  # Fast-growing fruit
        'P_uptake_kg_ha': 45,
        'K_uptake_kg_ha': 200,
        'cycle_days': 270,
        'average_yield_tonnes_ha': 30.0,
        'source': 'ICAR Horticulture Research'
    },
    'watermelon': {
        'N_uptake_kg_ha': 100,  # Cucurbit
        'P_uptake_kg_ha': 35,
        'K_uptake_kg_ha': 150,
        'cycle_days': 80,
        'average_yield_tonnes_ha': 25.0,
        'source': 'FAO Vegetable Production'
    },
    'grapes': {
        'N_uptake_kg_ha': 140,  # Perennial vine
        'P_uptake_kg_ha': 48,
        'K_uptake_kg_ha': 190,
        'cycle_days': 150,
        'average_yield_tonnes_ha': 18.0,
        'source': 'ICAR Viticulture Research'
    },
    'muskmelon': {
        'N_uptake_kg_ha': 90,   # Cucurbit
        'P_uptake_kg_ha': 30,
        'K_uptake_kg_ha': 130,
        'cycle_days': 90,
        'average_yield_tonnes_ha': 20.0,
        'source': 'FAO Vegetable Production'
    }
}


# Minimum threshold levels below which soil testing is recommended (kg/ha)
NUTRIENT_THRESHOLDS = {
    'critical': {
        'N': 30,   # Below this: Critical - immediate fertilization needed
        'P': 10,   # Severe deficiency
        'K': 40,   # Immediate action required
    },
    'low': {
        'N': 60,   # Below this: Low - plan fertilization soon
        'P': 20,   # Moderate deficiency
        'K': 80,   # Should fertilize
    },
    'adequate': {
        'N': 100,  # Above this: Adequate - normal crop production
        'P': 30,   # Sufficient for most crops
        'K': 120,  # Good for crop growth
    },
    'high': {
        'N': 150,  # Above this: High - no fertilization needed
        'P': 50,   # Excess levels
        'K': 200,  # Very high
    }
}


# Safety buffer to add before warning (to account for measurement uncertainty)
SAFETY_BUFFER_PERCENTAGE = 10  # Add 10% buffer to threshold


def get_crop_nutrient_uptake(crop_name: str) -> Optional[Dict]:
    """
    Get nutrient uptake data for a specific crop.
    
    Args:
        crop_name: Name of the crop (case-insensitive)
        
    Returns:
        Dictionary with uptake data or None if crop not found
    """
    crop_name_lower = crop_name.lower()
    return CROP_NUTRIENT_UPTAKE.get(crop_name_lower)


def calculate_remaining_nutrients(
    initial_N: float,
    initial_P: float,
    initial_K: float,
    crop_name: str,
    rainfall_loss_N: float = 0,
    rainfall_loss_P: float = 0,
    rainfall_loss_K: float = 0
) -> Dict:
    """
    Calculate remaining nutrients after crop uptake and rainfall loss.
    
    Formula: Final = Initial - (Crop Uptake + Rainfall Loss)
    
    Args:
        initial_N, initial_P, initial_K: Starting nutrient levels (kg/ha)
        crop_name: Name of the crop grown
        rainfall_loss_N, rainfall_loss_P, rainfall_loss_K: Losses from RINDM (kg/ha)
        
    Returns:
        Dictionary with remaining nutrients and breakdown
    """
    crop_data = get_crop_nutrient_uptake(crop_name)
    
    if not crop_data:
        raise ValueError(f"Crop '{crop_name}' not found in database")
    
    # Get uptake values
    crop_uptake_N = crop_data['N_uptake_kg_ha']
    crop_uptake_P = crop_data['P_uptake_kg_ha']
    crop_uptake_K = crop_data['K_uptake_kg_ha']
    
    # Calculate total depletion
    total_N_depletion = crop_uptake_N + rainfall_loss_N
    total_P_depletion = crop_uptake_P + rainfall_loss_P
    total_K_depletion = crop_uptake_K + rainfall_loss_K
    
    # Calculate remaining (ensure non-negative)
    remaining_N = max(0, initial_N - total_N_depletion)
    remaining_P = max(0, initial_P - total_P_depletion)
    remaining_K = max(0, initial_K - total_K_depletion)
    
    return {
        'remaining_nutrients': {
            'N': round(remaining_N, 2),
            'P': round(remaining_P, 2),
            'K': round(remaining_K, 2)
        },
        'depletion_breakdown': {
            'crop_uptake': {
                'N': crop_uptake_N,
                'P': crop_uptake_P,
                'K': crop_uptake_K
            },
            'rainfall_loss': {
                'N': round(rainfall_loss_N, 2),
                'P': round(rainfall_loss_P, 2),
                'K': round(rainfall_loss_K, 2)
            },
            'total_depletion': {
                'N': round(total_N_depletion, 2),
                'P': round(total_P_depletion, 2),
                'K': round(total_K_depletion, 2)
            }
        },
        'initial_nutrients': {
            'N': initial_N,
            'P': initial_P,
            'K': initial_K
        },
        'crop_info': {
            'name': crop_name,
            'cycle_days': crop_data['cycle_days'],
            'average_yield': crop_data['average_yield_tonnes_ha']
        }
    }


def check_nutrient_status(N: float, P: float, K: float) -> Dict:
    """
    Check nutrient status and provide recommendations.
    
    Args:
        N, P, K: Current nutrient levels (kg/ha)
        
    Returns:
        Dictionary with status and warnings for each nutrient
    """
    def get_status(nutrient_value: float, nutrient_name: str) -> Dict:
        """Determine status level for a nutrient."""
        
        if nutrient_value < NUTRIENT_THRESHOLDS['critical'][nutrient_name]:
            return {
                'level': 'CRITICAL',
                'status': 'critical',
                'color': 'red',
                'message': f'⚠️ CRITICAL: {nutrient_name} is severely depleted. Immediate soil testing and fertilization required!',
                'action': 'URGENT: Test soil and apply fertilizer immediately'
            }
        elif nutrient_value < NUTRIENT_THRESHOLDS['low'][nutrient_name]:
            return {
                'level': 'LOW',
                'status': 'low',
                'color': 'orange',
                'message': f'⚡ LOW: {nutrient_name} levels are low. Plan fertilization before next crop.',
                'action': 'RECOMMENDED: Soil test and fertilization needed soon'
            }
        elif nutrient_value < NUTRIENT_THRESHOLDS['adequate'][nutrient_name]:
            return {
                'level': 'MODERATE',
                'status': 'moderate',
                'color': 'yellow',
                'message': f'✓ MODERATE: {nutrient_name} is adequate but monitor levels.',
                'action': 'Monitor: Consider soil test if planning heavy-feeding crops'
            }
        elif nutrient_value < NUTRIENT_THRESHOLDS['high'][nutrient_name]:
            return {
                'level': 'GOOD',
                'status': 'good',
                'color': 'lightgreen',
                'message': f'✓ GOOD: {nutrient_name} levels are good for crop production.',
                'action': 'No action needed'
            }
        else:
            return {
                'level': 'HIGH',
                'status': 'high',
                'color': 'green',
                'message': f'✓✓ HIGH: {nutrient_name} levels are excellent.',
                'action': 'No fertilization needed'
            }
    
    N_status = get_status(N, 'N')
    P_status = get_status(P, 'P')
    K_status = get_status(K, 'K')
    
    # Determine overall status (worst case)
    status_priority = {'CRITICAL': 4, 'LOW': 3, 'MODERATE': 2, 'GOOD': 1, 'HIGH': 0}
    overall_status = max([N_status, P_status, K_status], 
                         key=lambda x: status_priority[x['level']])
    
    # Check if any nutrient is critical
    needs_soil_test = any(
        status['level'] in ['CRITICAL', 'LOW'] 
        for status in [N_status, P_status, K_status]
    )
    
    return {
        'N': N_status,
        'P': P_status,
        'K': K_status,
        'overall_status': overall_status['level'],
        'overall_color': overall_status['color'],
        'needs_soil_test': needs_soil_test,
        'soil_test_message': (
            '🔬 SOIL TEST RECOMMENDED: One or more nutrients are below optimal levels. '
            'Get a soil test to determine exact fertilizer requirements.'
            if needs_soil_test else
            '✓ Nutrient levels are adequate. Soil testing not urgently needed.'
        ),
        'nutrient_values': {
            'N': round(N, 2),
            'P': round(P, 2),
            'K': round(K, 2)
        }
    }


def predict_future_nutrients(
    current_N: float,
    current_P: float,
    current_K: float,
    planned_crop: str,
    expected_rainfall_mm: float = 0,
    soil_type: str = 'loamy'
) -> Dict:
    """
    Predict nutrient levels after growing a specific crop.
    
    Args:
        current_N, current_P, current_K: Current levels (kg/ha)
        planned_crop: Crop name
        expected_rainfall_mm: Expected rainfall during growing season
        soil_type: Soil type for rainfall loss calculation
        
    Returns:
        Predicted remaining nutrients and warnings
    """
    from .rindm import calculate_rainfall_loss
    
    # Get crop data
    crop_data = get_crop_nutrient_uptake(planned_crop)
    if not crop_data:
        raise ValueError(f"Crop '{planned_crop}' not found")
    
    # Estimate rainfall loss (simplified - use average duration)
    rainfall_loss = {'N_loss': 0, 'P_loss': 0, 'K_loss': 0}
    if expected_rainfall_mm > 0:
        rainfall_loss = calculate_rainfall_loss(
            rainfall_mm=expected_rainfall_mm,
            duration_hours=expected_rainfall_mm / 10,  # Assume 10mm/hr avg
            N=current_N,
            P=current_P,
            K=current_K,
            soil_type=soil_type
        )
    
    # Calculate remaining
    result = calculate_remaining_nutrients(
        initial_N=current_N,
        initial_P=current_P,
        initial_K=current_K,
        crop_name=planned_crop,
        rainfall_loss_N=rainfall_loss['N_loss'],
        rainfall_loss_P=rainfall_loss['P_loss'],
        rainfall_loss_K=rainfall_loss['K_loss']
    )
    
    # Check status of predicted nutrients
    predicted_N = result['remaining_nutrients']['N']
    predicted_P = result['remaining_nutrients']['P']
    predicted_K = result['remaining_nutrients']['K']
    
    status = check_nutrient_status(predicted_N, predicted_P, predicted_K)
    
    return {
        'prediction': result,
        'status': status,
        'warnings': {
            'will_need_fertilizer': status['needs_soil_test'],
            'critical_nutrients': [
                nutrient for nutrient in ['N', 'P', 'K']
                if status[nutrient]['level'] == 'CRITICAL'
            ]
        }
    }


def get_all_crops_summary() -> list:
    """Get summary of all crops with their nutrient requirements."""
    summary = []
    for crop_name, data in CROP_NUTRIENT_UPTAKE.items():
        summary.append({
            'crop': crop_name.capitalize(),
            'N': data['N_uptake_kg_ha'],
            'P': data['P_uptake_kg_ha'],
            'K': data['K_uptake_kg_ha'],
            'cycle_days': data['cycle_days'],
            'yield_tonnes_ha': data['average_yield_tonnes_ha']
        })
    return sorted(summary, key=lambda x: x['crop'])


if __name__ == "__main__":
    """Test the nutrient database functions."""
    print("=" * 80)
    print("Crop Nutrient Database - Test Cases")
    print("=" * 80)
    
    # Test 1: Get crop data
    print("\nTEST 1: Get Crop Nutrient Uptake")
    print("-" * 80)
    rice_data = get_crop_nutrient_uptake('rice')
    print(f"Rice: N={rice_data['N_uptake_kg_ha']}, P={rice_data['P_uptake_kg_ha']}, "
          f"K={rice_data['K_uptake_kg_ha']} kg/ha")
    
    # Test 2: Calculate remaining nutrients
    print("\nTEST 2: Calculate Remaining Nutrients After Rice Crop")
    print("-" * 80)
    result = calculate_remaining_nutrients(
        initial_N=90,
        initial_P=42,
        initial_K=43,
        crop_name='rice',
        rainfall_loss_N=10,
        rainfall_loss_P=3,
        rainfall_loss_K=8
    )
    print(f"Initial: N=90, P=42, K=43 kg/ha")
    print(f"Crop Uptake: N={result['depletion_breakdown']['crop_uptake']['N']}, "
          f"P={result['depletion_breakdown']['crop_uptake']['P']}, "
          f"K={result['depletion_breakdown']['crop_uptake']['K']} kg/ha")
    print(f"Rainfall Loss: N=10, P=3, K=8 kg/ha")
    print(f"Remaining: N={result['remaining_nutrients']['N']}, "
          f"P={result['remaining_nutrients']['P']}, "
          f"K={result['remaining_nutrients']['K']} kg/ha")
    
    # Test 3: Check nutrient status
    print("\nTEST 3: Check Nutrient Status")
    print("-" * 80)
    
    # Good levels
    status1 = check_nutrient_status(N=100, P=35, K=120)
    print(f"Good Levels (N=100, P=35, K=120):")
    print(f"  Overall: {status1['overall_status']}")
    print(f"  N: {status1['N']['message']}")
    print(f"  Needs Test: {status1['needs_soil_test']}")
    
    # Critical levels
    status2 = check_nutrient_status(N=25, P=8, K=35)
    print(f"\nCritical Levels (N=25, P=8, K=35):")
    print(f"  Overall: {status2['overall_status']}")
    print(f"  N: {status2['N']['message']}")
    print(f"  P: {status2['P']['message']}")
    print(f"  K: {status2['K']['message']}")
    print(f"  {status2['soil_test_message']}")
    
    # Test 4: All crops summary
    print("\nTEST 4: All Crops Nutrient Requirements Summary")
    print("-" * 80)
    summary = get_all_crops_summary()
    print(f"{'Crop':<15} {'N (kg/ha)':<12} {'P (kg/ha)':<12} {'K (kg/ha)':<12} {'Days':<8}")
    print("-" * 80)
    for crop in summary[:10]:  # Show first 10
        print(f"{crop['crop']:<15} {crop['N']:<12} {crop['P']:<12} {crop['K']:<12} {crop['cycle_days']:<8}")
    print(f"... and {len(summary) - 10} more crops")
    
    print("\n" + "=" * 80)
    print("Nutrient Database Tests Complete ✓")
    print("=" * 80)

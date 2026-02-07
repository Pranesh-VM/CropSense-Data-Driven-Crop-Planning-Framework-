"""
RINDM - Rainfall Induced Nutrient Depletion Model

Calculates nutrient loss (N, P, K) due to rainfall through leaching and runoff.
Supports both detailed soil texture input and simple soil type selection.

Scientific basis:
- FAO Soil Bulletin 10
- USDA Nutrient Management Guidelines
- ICAR Soil Health Management
"""

import math
from typing import Dict, Optional, Union, Tuple


class RainfallNutrientDepletionModel:
    """
    Calculate nutrient depletion due to rainfall events.
    
    Supports two input modes:
    1. Simple: soil_type ("sandy", "loamy", "clay")
    2. Detailed: soil texture percentages (sand, silt, clay)
    """
    
    # Leaching coefficients by soil type (% lost per 100mm rainfall)
    LEACHING_COEFFICIENTS = {
        'N': {
            'sandy': 0.30,   # High leaching in sandy soils
            'loamy': 0.15,   # Moderate leaching
            'clay': 0.05,    # Low leaching (clay retains nutrients)
        },
        'P': {
            'sandy': 0.08,   # P binds to particles, lower leaching
            'loamy': 0.05,
            'clay': 0.03,
        },
        'K': {
            'sandy': 0.20,   # K is mobile, moderate leaching
            'loamy': 0.12,
            'clay': 0.06,
        }
    }
    
    # Runoff coefficients by soil type (% lost through surface runoff)
    RUNOFF_COEFFICIENTS = {
        'N': {
            'sandy': 0.05,   # Low runoff (water infiltrates)
            'loamy': 0.15,   # Moderate runoff
            'clay': 0.30,    # High runoff (water doesn't penetrate)
        },
        'P': {
            'sandy': 0.10,   # P moves with soil particles
            'loamy': 0.20,
            'clay': 0.35,
        },
        'K': {
            'sandy': 0.08,   # K in runoff
            'loamy': 0.18,
            'clay': 0.28,
        }
    }
    
    # Assumed constant slope (degrees) - moderate agricultural land
    DEFAULT_SLOPE = 3.0  # 3 degree slope (~5% grade)
    
    def __init__(self):
        """Initialize RINDM model."""
        pass
    
    def _determine_soil_type(
        self, 
        sand_pct: Optional[float] = None,
        silt_pct: Optional[float] = None,
        clay_pct: Optional[float] = None
    ) -> str:
        """
        Determine soil type from texture percentages using USDA texture triangle.
        
        Args:
            sand_pct: Percentage of sand (0-100)
            silt_pct: Percentage of silt (0-100)
            clay_pct: Percentage of clay (0-100)
            
        Returns:
            Soil type: "sandy", "loamy", or "clay"
        """
        if clay_pct is None or sand_pct is None or silt_pct is None:
            raise ValueError("All texture percentages must be provided")
        
        # Validate
        total = sand_pct + silt_pct + clay_pct
        if not (99 <= total <= 101):  # Allow 1% tolerance for rounding
            raise ValueError(f"Texture percentages must sum to 100, got {total}")
        
        # USDA Soil Texture Classification (Simplified)
        if clay_pct >= 40:
            return 'clay'
        elif sand_pct >= 70:
            return 'sandy'
        elif sand_pct >= 50:
            return 'sandy'  # Sandy loam -> sandy for simplicity
        elif clay_pct >= 27:
            return 'clay'  # Clay loam -> clay
        else:
            return 'loamy'  # Default to loamy for balanced soils
    
    def _calculate_intensity_factor(
        self, 
        rainfall_mm: float, 
        duration_hours: float
    ) -> float:
        """
        Calculate rainfall intensity factor (0-1).
        Higher intensity = more runoff potential.
        
        Args:
            rainfall_mm: Total rainfall in mm
            duration_hours: Duration of rainfall in hours
            
        Returns:
            Intensity factor (0-1)
        """
        if duration_hours <= 0:
            return 0.5  # Default moderate intensity
        
        intensity_mm_per_hour = rainfall_mm / duration_hours
        
        # 25 mm/hr is considered high intensity
        # Scale from 0 (light) to 1 (very heavy)
        intensity_factor = min(1.0, intensity_mm_per_hour / 25.0)
        
        return intensity_factor
    
    def _calculate_slope_factor(self, slope_degrees: float = DEFAULT_SLOPE) -> float:
        """
        Calculate slope runoff factor (1-2).
        Steeper slopes increase runoff.
        
        Args:
            slope_degrees: Field slope in degrees
            
        Returns:
            Slope factor (1.0 = flat, 2.0 = very steep)
        """
        # 0 degrees = 1.0, 15 degrees = 2.0
        # Most agricultural land is 0-10 degrees
        slope_factor = 1.0 + min(slope_degrees / 15.0, 1.0)
        return slope_factor
    
    def calculate_nutrient_loss(
        self,
        rainfall_mm: float,
        duration_hours: float,
        N_current: float,
        P_current: float,
        K_current: float,
        soil_type: Optional[str] = None,
        sand_pct: Optional[float] = None,
        silt_pct: Optional[float] = None,
        clay_pct: Optional[float] = None,
        slope_degrees: float = DEFAULT_SLOPE
    ) -> Dict[str, Union[float, Dict]]:
        """
        Calculate nutrient loss due to rainfall.
        
        Supports two input modes:
        Mode 1 (Simple): Provide soil_type
        Mode 2 (Detailed): Provide sand_pct, silt_pct, clay_pct
        
        Args:
            rainfall_mm: Total rainfall in mm
            duration_hours: Duration of rainfall in hours
            N_current: Current nitrogen level (kg/ha)
            P_current: Current phosphorus level (kg/ha)
            K_current: Current potassium level (kg/ha)
            soil_type: Optional - "sandy", "loamy", or "clay"
            sand_pct: Optional - Sand percentage (0-100)
            silt_pct: Optional - Silt percentage (0-100)
            clay_pct: Optional - Clay percentage (0-100)
            slope_degrees: Field slope in degrees (default: 3.0)
            
        Returns:
            Dictionary with nutrient losses and details
        """
        # Validate inputs
        if rainfall_mm < 0:
            raise ValueError("Rainfall cannot be negative")
        if duration_hours < 0:
            raise ValueError("Duration cannot be negative")
        if any(x < 0 for x in [N_current, P_current, K_current]):
            raise ValueError("Nutrient levels cannot be negative")
        
        # Determine soil type
        if soil_type:
            # Simple mode: user provided soil type
            if soil_type not in ['sandy', 'loamy', 'clay']:
                raise ValueError(f"Invalid soil_type: {soil_type}")
            final_soil_type = soil_type
        elif all(x is not None for x in [sand_pct, silt_pct, clay_pct]):
            # Detailed mode: calculate from texture
            final_soil_type = self._determine_soil_type(sand_pct, silt_pct, clay_pct)
        else:
            raise ValueError(
                "Must provide either soil_type OR all texture percentages "
                "(sand_pct, silt_pct, clay_pct)"
            )
        
        # Calculate factors
        intensity_factor = self._calculate_intensity_factor(rainfall_mm, duration_hours)
        slope_factor = self._calculate_slope_factor(slope_degrees)
        
        # Rainfall factor (normalized per 100mm)
        rainfall_factor = rainfall_mm / 100.0
        
        # Calculate losses for each nutrient
        results = {}
        
        for nutrient, current_level in [('N', N_current), ('P', P_current), ('K', K_current)]:
            # Leaching loss
            leaching_coef = self.LEACHING_COEFFICIENTS[nutrient][final_soil_type]
            leaching_loss = current_level * leaching_coef * rainfall_factor
            
            # Runoff loss
            runoff_coef = self.RUNOFF_COEFFICIENTS[nutrient][final_soil_type]
            runoff_loss = current_level * runoff_coef * intensity_factor * slope_factor
            
            # Total loss
            total_loss = leaching_loss + runoff_loss
            
            # Ensure we don't lose more than available
            total_loss = min(total_loss, current_level)
            
            results[nutrient] = {
                'total_loss': round(total_loss, 2),
                'leaching_loss': round(leaching_loss, 2),
                'runoff_loss': round(runoff_loss, 2),
                'remaining': round(current_level - total_loss, 2),
                'loss_percentage': round((total_loss / current_level * 100) if current_level > 0 else 0, 2)
            }
        
        return {
            'N_loss': results['N']['total_loss'],
            'P_loss': results['P']['total_loss'],
            'K_loss': results['K']['total_loss'],
            'N_remaining': results['N']['remaining'],
            'P_remaining': results['P']['remaining'],
            'K_remaining': results['K']['remaining'],
            'details': {
                'soil_type_used': final_soil_type,
                'rainfall_mm': rainfall_mm,
                'duration_hours': duration_hours,
                'intensity_mm_per_hour': round(rainfall_mm / duration_hours if duration_hours > 0 else 0, 2),
                'intensity_factor': round(intensity_factor, 2),
                'slope_factor': round(slope_factor, 2),
                'N': results['N'],
                'P': results['P'],
                'K': results['K']
            }
        }
    
    def calculate_cumulative_loss(
        self,
        rainfall_events: list,
        initial_N: float,
        initial_P: float,
        initial_K: float,
        soil_type: Optional[str] = None,
        sand_pct: Optional[float] = None,
        silt_pct: Optional[float] = None,
        clay_pct: Optional[float] = None
    ) -> Dict[str, Union[float, list]]:
        """
        Calculate cumulative nutrient loss over multiple rainfall events.
        
        Args:
            rainfall_events: List of dicts with 'rainfall_mm' and 'duration_hours'
            initial_N, initial_P, initial_K: Starting nutrient levels
            soil_type or texture percentages: Soil characteristics
            
        Returns:
            Dictionary with cumulative losses and event-wise breakdown
        """
        current_N = initial_N
        current_P = initial_P
        current_K = initial_K
        
        event_details = []
        
        for i, event in enumerate(rainfall_events):
            result = self.calculate_nutrient_loss(
                rainfall_mm=event['rainfall_mm'],
                duration_hours=event.get('duration_hours', 2.0),  # Default 2 hours
                N_current=current_N,
                P_current=current_P,
                K_current=current_K,
                soil_type=soil_type,
                sand_pct=sand_pct,
                silt_pct=silt_pct,
                clay_pct=clay_pct
            )
            
            # Update current levels
            current_N = result['N_remaining']
            current_P = result['P_remaining']
            current_K = result['K_remaining']
            
            event_details.append({
                'event_number': i + 1,
                'date': event.get('date', f'Event {i+1}'),
                'N_loss': result['N_loss'],
                'P_loss': result['P_loss'],
                'K_loss': result['K_loss'],
                'N_after': current_N,
                'P_after': current_P,
                'K_after': current_K
            })
        
        total_N_loss = initial_N - current_N
        total_P_loss = initial_P - current_P
        total_K_loss = initial_K - current_K
        
        return {
            'initial_N': initial_N,
            'initial_P': initial_P,
            'initial_K': initial_K,
            'final_N': round(current_N, 2),
            'final_P': round(current_P, 2),
            'final_K': round(current_K, 2),
            'total_N_loss': round(total_N_loss, 2),
            'total_P_loss': round(total_P_loss, 2),
            'total_K_loss': round(total_K_loss, 2),
            'total_loss_percentage': {
                'N': round((total_N_loss / initial_N * 100) if initial_N > 0 else 0, 2),
                'P': round((total_P_loss / initial_P * 100) if initial_P > 0 else 0, 2),
                'K': round((total_K_loss / initial_K * 100) if initial_K > 0 else 0, 2)
            },
            'events': event_details
        }


# Convenience function for quick calculations
def calculate_rainfall_loss(
    rainfall_mm: float,
    duration_hours: float = 2.0,
    N: float = 0,
    P: float = 0,
    K: float = 0,
    soil_type: str = "loamy"
) -> Dict:
    """
    Quick nutrient loss calculation with default values.
    
    Args:
        rainfall_mm: Rainfall amount in mm
        duration_hours: Duration in hours (default: 2)
        N, P, K: Current nutrient levels in kg/ha
        soil_type: "sandy", "loamy", or "clay" (default: "loamy")
        
    Returns:
        Nutrient loss results
    """
    model = RainfallNutrientDepletionModel()
    return model.calculate_nutrient_loss(
        rainfall_mm=rainfall_mm,
        duration_hours=duration_hours,
        N_current=N,
        P_current=P,
        K_current=K,
        soil_type=soil_type
    )


if __name__ == "__main__":
    """Test the RINDM model with examples."""
    print("=" * 80)
    print("RINDM - Rainfall Induced Nutrient Depletion Model - Test Cases")
    print("=" * 80)
    
    model = RainfallNutrientDepletionModel()
    
    # Test Case 1: Simple soil type input
    print("\n" + "=" * 80)
    print("TEST 1: Simple Input - Loamy Soil, Moderate Rainfall")
    print("=" * 80)
    
    result1 = model.calculate_nutrient_loss(
        rainfall_mm=50,
        duration_hours=3,
        N_current=90,
        P_current=42,
        K_current=43,
        soil_type='loamy'
    )
    
    print(f"\nInputs:")
    print(f"  Rainfall: 50mm over 3 hours")
    print(f"  Soil: Loamy")
    print(f"  Initial N/P/K: 90/42/43 kg/ha")
    print(f"\nResults:")
    print(f"  N Loss: {result1['N_loss']} kg/ha ({result1['details']['N']['loss_percentage']}%)")
    print(f"  P Loss: {result1['P_loss']} kg/ha ({result1['details']['P']['loss_percentage']}%)")
    print(f"  K Loss: {result1['K_loss']} kg/ha ({result1['details']['K']['loss_percentage']}%)")
    print(f"\nRemaining:")
    print(f"  N: {result1['N_remaining']} kg/ha")
    print(f"  P: {result1['P_remaining']} kg/ha")
    print(f"  K: {result1['K_remaining']} kg/ha")
    
    # Test Case 2: Detailed texture input
    print("\n" + "=" * 80)
    print("TEST 2: Detailed Input - Texture Percentages, Heavy Rainfall")
    print("=" * 80)
    
    result2 = model.calculate_nutrient_loss(
        rainfall_mm=100,  # Heavy rainfall
        duration_hours=2,   # Short duration = high intensity
        N_current=90,
        P_current=42,
        K_current=43,
        sand_pct=70,   # Sandy soil
        silt_pct=20,
        clay_pct=10
    )
    
    print(f"\nInputs:")
    print(f"  Rainfall: 100mm over 2 hours (50mm/hr intensity)")
    print(f"  Soil Texture: 70% Sand, 20% Silt, 10% Clay")
    print(f"  Determined Type: {result2['details']['soil_type_used']}")
    print(f"  Initial N/P/K: 90/42/43 kg/ha")
    print(f"\nResults:")
    print(f"  N Loss: {result2['N_loss']} kg/ha ({result2['details']['N']['loss_percentage']}%)")
    print(f"  P Loss: {result2['P_loss']} kg/ha ({result2['details']['P']['loss_percentage']}%)")
    print(f"  K Loss: {result2['K_loss']} kg/ha ({result2['details']['K']['loss_percentage']}%)")
    
    # Test Case 3: Multiple rainfall events
    print("\n" + "=" * 80)
    print("TEST 3: Cumulative Loss - Growing Season with Multiple Rainfall Events")
    print("=" * 80)
    
    rainfall_events = [
        {'date': '2026-02-01', 'rainfall_mm': 30, 'duration_hours': 2},
        {'date': '2026-02-15', 'rainfall_mm': 50, 'duration_hours': 4},
        {'date': '2026-03-01', 'rainfall_mm': 40, 'duration_hours': 3},
        {'date': '2026-03-20', 'rainfall_mm': 60, 'duration_hours': 5},
    ]
    
    result3 = model.calculate_cumulative_loss(
        rainfall_events=rainfall_events,
        initial_N=90,
        initial_P=42,
        initial_K=43,
        soil_type='loamy'
    )
    
    print(f"\nInitial Nutrients: N={result3['initial_N']}, P={result3['initial_P']}, K={result3['initial_K']} kg/ha")
    print(f"\n{len(rainfall_events)} Rainfall Events:")
    for event in result3['events']:
        print(f"\n  Event {event['event_number']} ({event['date']}):")
        print(f"    Loss: N={event['N_loss']}, P={event['P_loss']}, K={event['K_loss']} kg/ha")
        print(f"    Remaining: N={event['N_after']}, P={event['P_after']}, K={event['K_after']} kg/ha")
    
    print(f"\n{'='*40}")
    print(f"Final Results:")
    print(f"  Final Nutrients: N={result3['final_N']}, P={result3['final_P']}, K={result3['final_K']} kg/ha")
    print(f"  Total Loss: N={result3['total_N_loss']}, P={result3['total_P_loss']}, K={result3['total_K_loss']} kg/ha")
    print(f"  Loss %: N={result3['total_loss_percentage']['N']}%, P={result3['total_loss_percentage']['P']}%, K={result3['total_loss_percentage']['K']}%")
    
    print("\n" + "=" * 80)
    print("RINDM Model Tests Complete ✓")
    print("=" * 80)

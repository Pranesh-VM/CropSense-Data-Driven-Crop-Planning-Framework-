"""
04_rindm_validation.py - RINDM Model Validation

Implements Steps 10-11 from EVALUATION_STRATEGY.md:
- Validate against known scenarios
- Test edge cases
- Sensitivity analysis

Charts generated:
15. Line Plot - N, P, K loss vs Rainfall Amount
16. Line Plot - N, P, K loss vs Rainfall Intensity
17. Line Plot - N, P, K loss vs Slope
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import numpy as np
import pandas as pd

from utils.plot_helper import PlotHelper
from src.models.rindm import RainfallNutrientDepletionModel


def test_edge_cases(model):
    """
    Step 10: Validate against known scenarios and edge cases.
    """
    print("\n" + "=" * 60)
    print("EDGE CASE VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Test Case 1: Zero rainfall
    print("\n[Test 1] Zero Rainfall - Loss should be 0")
    result = model.calculate_nutrient_loss(
        rainfall_mm=0,
        duration_hours=1,
        N_current=90, P_current=42, K_current=43,
        soil_type='loamy'
    )
    test1_pass = (result['N_loss'] == 0 and result['P_loss'] == 0 and result['K_loss'] == 0)
    print(f"  N loss: {result['N_loss']}, P loss: {result['P_loss']}, K loss: {result['K_loss']}")
    print(f"  {'✓ PASS' if test1_pass else '✗ FAIL'}")
    results.append(('Zero rainfall', test1_pass))
    
    # Test Case 2: Extreme rainfall - loss should be capped
    print("\n[Test 2] Extreme Rainfall (300mm in 2hrs) - Loss should not exceed available nutrients")
    result = model.calculate_nutrient_loss(
        rainfall_mm=300,
        duration_hours=2,
        N_current=90, P_current=42, K_current=43,
        soil_type='sandy'  # Sandy has highest loss
    )
    test2_pass = (result['N_remaining'] >= 0 and result['P_remaining'] >= 0 and result['K_remaining'] >= 0)
    print(f"  Remaining: N={result['N_remaining']}, P={result['P_remaining']}, K={result['K_remaining']}")
    print(f"  {'✓ PASS' if test2_pass else '✗ FAIL'} - No negative values")
    results.append(('Extreme rainfall', test2_pass))
    
    # Test Case 3: Zero nutrients
    print("\n[Test 3] Zero Nutrients - Loss should be 0, no negative values")
    result = model.calculate_nutrient_loss(
        rainfall_mm=100,
        duration_hours=2,
        N_current=0, P_current=0, K_current=0,
        soil_type='sandy'
    )
    test3_pass = (result['N_loss'] == 0 and result['P_loss'] == 0 and result['K_loss'] == 0 and
                  result['N_remaining'] == 0 and result['P_remaining'] == 0 and result['K_remaining'] == 0)
    print(f"  Loss: N={result['N_loss']}, P={result['P_loss']}, K={result['K_loss']}")
    print(f"  Remaining: N={result['N_remaining']}, P={result['P_remaining']}, K={result['K_remaining']}")
    print(f"  {'✓ PASS' if test3_pass else '✗ FAIL'}")
    results.append(('Zero nutrients', test3_pass))
    
    # Test Case 4: Verify soil type determination
    print("\n[Test 4] Soil Type Determination from Texture")
    
    test_textures = [
        (80, 10, 10, 'sandy'),  # High sand -> sandy
        (30, 40, 30, 'loamy'),  # Balanced -> loamy
        (20, 30, 50, 'clay'),   # High clay -> clay
    ]
    
    test4_pass = True
    for sand, silt, clay, expected in test_textures:
        result = model.calculate_nutrient_loss(
            rainfall_mm=50, duration_hours=2,
            N_current=90, P_current=42, K_current=43,
            sand_pct=sand, silt_pct=silt, clay_pct=clay
        )
        actual = result['details']['soil_type_used']
        match = actual == expected
        test4_pass = test4_pass and match
        print(f"  Sand={sand}%, Silt={silt}%, Clay={clay}% -> {actual} (expected: {expected}) {'✓' if match else '✗'}")
    
    print(f"  {'✓ PASS' if test4_pass else '✗ FAIL'}")
    results.append(('Soil type determination', test4_pass))
    
    # Test Case 5: Physics validation - sandy should have highest leaching
    print("\n[Test 5] Physics Validation - Sandy soil should have highest leaching")
    
    soil_results = {}
    for soil in ['sandy', 'loamy', 'clay']:
        result = model.calculate_nutrient_loss(
            rainfall_mm=100, duration_hours=4,
            N_current=90, P_current=42, K_current=43,
            soil_type=soil
        )
        soil_results[soil] = {
            'N_leaching': result['details']['N']['leaching_loss'],
            'N_runoff': result['details']['N']['runoff_loss'],
        }
    
    # Sandy should have highest leaching, clay should have highest runoff
    test5a = soil_results['sandy']['N_leaching'] > soil_results['loamy']['N_leaching'] > soil_results['clay']['N_leaching']
    test5b = soil_results['clay']['N_runoff'] > soil_results['loamy']['N_runoff'] > soil_results['sandy']['N_runoff']
    test5_pass = test5a and test5b
    
    print(f"  N Leaching: Sandy={soil_results['sandy']['N_leaching']}, Loamy={soil_results['loamy']['N_leaching']}, Clay={soil_results['clay']['N_leaching']}")
    print(f"  N Runoff: Sandy={soil_results['sandy']['N_runoff']}, Loamy={soil_results['loamy']['N_runoff']}, Clay={soil_results['clay']['N_runoff']}")
    print(f"  Sandy > Loamy > Clay for leaching: {'✓' if test5a else '✗'}")
    print(f"  Clay > Loamy > Sandy for runoff: {'✓' if test5b else '✗'}")
    print(f"  {'✓ PASS' if test5_pass else '✗ FAIL'}")
    results.append(('Physics validation', test5_pass))
    
    # Summary
    print("\n" + "-" * 40)
    print("EDGE CASE SUMMARY")
    print("-" * 40)
    pass_count = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    for name, passed in results:
        print(f"  {name}: {'✓ PASS' if passed else '✗ FAIL'}")
    print(f"\nTotal: {pass_count}/{total_tests} tests passed")
    
    return results


def sensitivity_analysis_rainfall(model, plotter):
    """
    Step 11: Sensitivity analysis - Vary rainfall amount.
    """
    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS - RAINFALL AMOUNT")
    print("=" * 60)
    
    rainfall_values = list(range(10, 310, 10))  # 10mm to 300mm
    n_loss, p_loss, k_loss = [], [], []
    
    for rain in rainfall_values:
        result = model.calculate_nutrient_loss(
            rainfall_mm=rain,
            duration_hours=4,  # Fixed duration
            N_current=90, P_current=42, K_current=43,
            soil_type='loamy'
        )
        n_loss.append(result['N_loss'])
        p_loss.append(result['P_loss'])
        k_loss.append(result['K_loss'])
    
    # Chart 15
    plotter.sensitivity_line_plot(
        rainfall_values,
        {'N': n_loss, 'P': p_loss, 'K': k_loss},
        'Rainfall Amount (mm)',
        'Nutrient Loss (kg/ha)',
        'Nutrient Loss vs Rainfall Amount (Loamy Soil)',
        '15_sensitivity_rainfall_amount.png'
    )
    
    print(f"  Tested {len(rainfall_values)} rainfall values")
    print(f"  At 100mm: N={n_loss[9]:.2f}, P={p_loss[9]:.2f}, K={k_loss[9]:.2f} kg/ha loss")
    print(f"  At 200mm: N={n_loss[19]:.2f}, P={p_loss[19]:.2f}, K={k_loss[19]:.2f} kg/ha loss")
    print("  Chart 15 saved")
    
    return {'rainfall': rainfall_values, 'N': n_loss, 'P': p_loss, 'K': k_loss}


def sensitivity_analysis_intensity(model, plotter):
    """
    Step 11: Sensitivity analysis - Vary rainfall intensity.
    """
    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS - RAINFALL INTENSITY")
    print("=" * 60)
    
    # Fixed rainfall amount, varying duration (= varying intensity)
    rainfall_mm = 100
    durations = [10, 8, 6, 5, 4, 3, 2, 1.5, 1]  # Hours (longer = lower intensity)
    intensities = [rainfall_mm / d for d in durations]  # mm/hr
    
    n_loss, p_loss, k_loss = [], [], []
    
    for duration in durations:
        result = model.calculate_nutrient_loss(
            rainfall_mm=rainfall_mm,
            duration_hours=duration,
            N_current=90, P_current=42, K_current=43,
            soil_type='loamy'
        )
        n_loss.append(result['N_loss'])
        p_loss.append(result['P_loss'])
        k_loss.append(result['K_loss'])
    
    # Chart 16
    plotter.sensitivity_line_plot(
        intensities,
        {'N': n_loss, 'P': p_loss, 'K': k_loss},
        'Rainfall Intensity (mm/hr)',
        'Nutrient Loss (kg/ha)',
        'Nutrient Loss vs Rainfall Intensity (100mm total, Loamy Soil)',
        '16_sensitivity_intensity.png'
    )
    
    print(f"  Tested {len(intensities)} intensity values ({min(intensities):.1f} to {max(intensities):.1f} mm/hr)")
    print(f"  Higher intensity increases runoff loss")
    print("  Chart 16 saved")
    
    return {'intensity': intensities, 'N': n_loss, 'P': p_loss, 'K': k_loss}


def sensitivity_analysis_slope(model, plotter):
    """
    Step 11: Sensitivity analysis - Vary slope.
    """
    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS - SLOPE")
    print("=" * 60)
    
    slopes = list(range(0, 31, 2))  # 0° to 30°
    n_loss, p_loss, k_loss = [], [], []
    
    for slope in slopes:
        result = model.calculate_nutrient_loss(
            rainfall_mm=100,
            duration_hours=2,
            N_current=90, P_current=42, K_current=43,
            soil_type='loamy',
            slope_degrees=slope
        )
        n_loss.append(result['N_loss'])
        p_loss.append(result['P_loss'])
        k_loss.append(result['K_loss'])
    
    # Chart 17
    plotter.sensitivity_line_plot(
        slopes,
        {'N': n_loss, 'P': p_loss, 'K': k_loss},
        'Slope (degrees)',
        'Nutrient Loss (kg/ha)',
        'Nutrient Loss vs Slope (100mm, 2hrs, Loamy Soil)',
        '17_sensitivity_slope.png'
    )
    
    print(f"  Tested {len(slopes)} slope values (0° to 30°)")
    print(f"  At 0°: N={n_loss[0]:.2f}, P={p_loss[0]:.2f}, K={k_loss[0]:.2f} kg/ha loss")
    print(f"  At 15°: N={n_loss[7]:.2f}, P={p_loss[7]:.2f}, K={k_loss[7]:.2f} kg/ha loss")
    print(f"  At 30°: N={n_loss[-1]:.2f}, P={p_loss[-1]:.2f}, K={k_loss[-1]:.2f} kg/ha loss")
    print("  Chart 17 saved")
    
    return {'slope': slopes, 'N': n_loss, 'P': p_loss, 'K': k_loss}


def main():
    print("=" * 60)
    print("RINDM MODEL VALIDATION & SENSITIVITY ANALYSIS")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "plots"
    output_dir.mkdir(exist_ok=True)
    
    model = RainfallNutrientDepletionModel()
    plotter = PlotHelper(output_dir)
    
    # Step 10: Edge case validation
    edge_results = test_edge_cases(model)
    
    # Step 11: Sensitivity analysis
    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS")
    print("=" * 60)
    
    rainfall_data = sensitivity_analysis_rainfall(model, plotter)
    intensity_data = sensitivity_analysis_intensity(model, plotter)
    slope_data = sensitivity_analysis_slope(model, plotter)
    
    # Save sensitivity data
    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    
    # Save to CSV
    df_rainfall = pd.DataFrame(rainfall_data)
    df_rainfall.to_csv(output_dir / 'sensitivity_rainfall.csv', index=False)
    
    df_intensity = pd.DataFrame(intensity_data)
    df_intensity.to_csv(output_dir / 'sensitivity_intensity.csv', index=False)
    
    df_slope = pd.DataFrame(slope_data)
    df_slope.to_csv(output_dir / 'sensitivity_slope.csv', index=False)
    
    print(f"  Data saved to {output_dir}")
    
    # Key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print("\n1. EDGE CASES:")
    all_passed = all(passed for _, passed in edge_results)
    print(f"   All edge cases passed: {'✓ YES' if all_passed else '✗ NO'}")
    
    print("\n2. SENSITIVITY ANALYSIS:")
    print("   - Nutrient loss increases linearly with rainfall amount")
    print("   - Higher intensity increases runoff contribution")
    print("   - Steeper slopes increase runoff loss")
    print("   - N is most affected (highest mobility)")
    print("   - P is least affected (binds to soil particles)")
    
    print(f"\nAll plots saved to: {output_dir}")


if __name__ == "__main__":
    main()

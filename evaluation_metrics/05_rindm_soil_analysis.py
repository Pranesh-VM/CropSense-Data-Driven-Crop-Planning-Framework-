"""
05_rindm_soil_analysis.py - RINDM Soil Type Analysis

Implements Steps 12-14 from EVALUATION_STRATEGY.md:
- Soil type impact analysis
- Leaching vs runoff contribution
- Per-nutrient breakdown

Charts generated:
18. Grouped Bar Chart - Nutrient Loss by Soil Type
19. Stacked Bar Chart - Leaching vs Runoff contribution per nutrient per soil type
23. Radar/Spider Chart - comparing loss profiles across soil types
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.plot_helper import PlotHelper
from src.models.rindm import RainfallNutrientDepletionModel


def analyze_soil_types(model, plotter):
    """
    Step 12: Soil type impact analysis.
    """
    print("\n" + "=" * 60)
    print("SOIL TYPE IMPACT ANALYSIS")
    print("=" * 60)
    
    soil_types = ['sandy', 'loamy', 'clay']
    
    # Fixed conditions
    rainfall_mm = 100
    duration_hours = 4
    N_initial, P_initial, K_initial = 90, 42, 43
    
    soil_data = {}
    detailed_data = {}
    
    for soil in soil_types:
        result = model.calculate_nutrient_loss(
            rainfall_mm=rainfall_mm,
            duration_hours=duration_hours,
            N_current=N_initial,
            P_current=P_initial,
            K_current=K_initial,
            soil_type=soil
        )
        
        soil_data[soil] = {
            'N': result['N_loss'],
            'P': result['P_loss'],
            'K': result['K_loss'],
        }
        
        detailed_data[soil] = {
            'N': result['details']['N'],
            'P': result['details']['P'],
            'K': result['details']['K'],
        }
        
        print(f"\n{soil.upper()} SOIL:")
        print(f"  N Loss: {result['N_loss']:.2f} kg/ha ({result['details']['N']['loss_percentage']:.1f}%)")
        print(f"  P Loss: {result['P_loss']:.2f} kg/ha ({result['details']['P']['loss_percentage']:.1f}%)")
        print(f"  K Loss: {result['K_loss']:.2f} kg/ha ({result['details']['K']['loss_percentage']:.1f}%)")
        print(f"  Total: {result['N_loss'] + result['P_loss'] + result['K_loss']:.2f} kg/ha")
    
    # Chart 18: Grouped Bar Chart
    plotter.soil_type_grouped_bar(
        soil_data,
        'Nutrient Loss by Soil Type (100mm rainfall, 4hrs)',
        '18_soil_type_comparison.png'
    )
    print("\n  Chart 18: Soil type comparison saved")
    
    return soil_data, detailed_data


def analyze_leaching_vs_runoff(model, plotter, detailed_data):
    """
    Step 14: Leaching vs runoff contribution analysis.
    """
    print("\n" + "=" * 60)
    print("LEACHING VS RUNOFF CONTRIBUTION")
    print("=" * 60)
    
    # Create stacked bar charts for each soil type
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, (soil, data) in enumerate(detailed_data.items()):
        nutrients = ['N', 'P', 'K']
        leaching = [data[n]['leaching_loss'] for n in nutrients]
        runoff = [data[n]['runoff_loss'] for n in nutrients]
        
        x = np.arange(len(nutrients))
        width = 0.5
        
        axes[idx].bar(x, leaching, width, label='Leaching', color='skyblue')
        axes[idx].bar(x, runoff, width, bottom=leaching, label='Runoff', color='coral')
        
        axes[idx].set_xlabel('Nutrient')
        axes[idx].set_ylabel('Loss (kg/ha)')
        axes[idx].set_title(f'{soil.capitalize()} Soil')
        axes[idx].set_xticks(x)
        axes[idx].set_xticklabels(nutrients)
        axes[idx].legend()
        
        # Print percentage breakdown
        print(f"\n{soil.upper()} SOIL:")
        for n in nutrients:
            total = data[n]['total_loss']
            if total > 0:
                leach_pct = (data[n]['leaching_loss'] / total) * 100
                runoff_pct = (data[n]['runoff_loss'] / total) * 100
                print(f"  {n}: Leaching {leach_pct:.1f}%, Runoff {runoff_pct:.1f}%")
            else:
                print(f"  {n}: No loss")
    
    plt.tight_layout()
    output_dir = Path(__file__).parent / "plots"
    plt.savefig(output_dir / '19_leaching_vs_runoff.png', bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("\n  Chart 19: Leaching vs Runoff saved")
    
    # Physics validation
    print("\n" + "-" * 40)
    print("PHYSICS VALIDATION")
    print("-" * 40)
    
    # N should be leaching-dominant in sandy soil
    n_sandy_leach_pct = (detailed_data['sandy']['N']['leaching_loss'] / 
                         detailed_data['sandy']['N']['total_loss']) * 100
    print(f"  N in Sandy: {n_sandy_leach_pct:.1f}% leaching (expected: dominant)")
    print(f"  ✓ N is highly mobile - leaching is primary loss pathway" if n_sandy_leach_pct > 50 else "  ✗ Check N leaching")
    
    # P should be runoff-dominant in clay soil
    p_clay_runoff_pct = (detailed_data['clay']['P']['runoff_loss'] / 
                         detailed_data['clay']['P']['total_loss']) * 100
    print(f"\n  P in Clay: {p_clay_runoff_pct:.1f}% runoff (expected: dominant)")
    print(f"  ✓ P binds to particles - runoff carries P" if p_clay_runoff_pct > 50 else "  ✗ Check P runoff")


def create_radar_chart(plotter, soil_data):
    """
    Chart 23: Radar chart comparing soil types.
    """
    print("\n" + "=" * 60)
    print("MULTI-DIMENSIONAL COMPARISON")
    print("=" * 60)
    
    # Categories for radar chart
    categories = ['N Loss', 'P Loss', 'K Loss', 'Total Loss']
    
    radar_data = {}
    for soil, data in soil_data.items():
        total = data['N'] + data['P'] + data['K']
        # Normalize to max values for visualization
        radar_data[soil.capitalize()] = [data['N'], data['P'], data['K'], total]
    
    # Find max for normalization
    max_vals = [
        max(radar_data[s][i] for s in radar_data) 
        for i in range(len(categories))
    ]
    
    # Normalize
    for soil in radar_data:
        radar_data[soil] = [v / m if m > 0 else 0 
                           for v, m in zip(radar_data[soil], max_vals)]
    
    plotter.radar_chart(
        radar_data,
        categories,
        'Nutrient Loss Profile Comparison (Normalized)',
        '23_soil_radar_chart.png'
    )
    print("  Chart 23: Radar chart saved")


def comprehensive_soil_comparison(model):
    """
    Additional analysis: Compare all combinations.
    """
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SOIL × RAINFALL MATRIX")
    print("=" * 60)
    
    soil_types = ['sandy', 'loamy', 'clay']
    rainfall_values = [25, 50, 75, 100, 150, 200]
    
    results = []
    
    for soil in soil_types:
        for rain in rainfall_values:
            result = model.calculate_nutrient_loss(
                rainfall_mm=rain,
                duration_hours=4,
                N_current=90, P_current=42, K_current=43,
                soil_type=soil
            )
            results.append({
                'Soil': soil,
                'Rainfall_mm': rain,
                'N_Loss': result['N_loss'],
                'P_Loss': result['P_loss'],
                'K_Loss': result['K_loss'],
                'Total_Loss': result['N_loss'] + result['P_loss'] + result['K_loss'],
                'N_Loss_Pct': result['details']['N']['loss_percentage'],
                'P_Loss_Pct': result['details']['P']['loss_percentage'],
                'K_Loss_Pct': result['details']['K']['loss_percentage'],
            })
    
    df = pd.DataFrame(results)
    
    # Save to CSV
    output_dir = Path(__file__).parent / "plots"
    df.to_csv(output_dir / 'soil_rainfall_matrix.csv', index=False)
    
    # Create pivot table for display
    print("\nTotal Loss (kg/ha) by Soil Type × Rainfall:")
    pivot = df.pivot_table(
        values='Total_Loss', 
        index='Rainfall_mm', 
        columns='Soil'
    )[['sandy', 'loamy', 'clay']]
    print(pivot.round(2).to_string())
    
    print(f"\nData saved to {output_dir / 'soil_rainfall_matrix.csv'}")
    
    return df


def main():
    print("=" * 60)
    print("RINDM SOIL TYPE ANALYSIS")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "plots"
    output_dir.mkdir(exist_ok=True)
    
    model = RainfallNutrientDepletionModel()
    plotter = PlotHelper(output_dir)
    
    # Step 12: Soil type impact
    soil_data, detailed_data = analyze_soil_types(model, plotter)
    
    # Step 14: Leaching vs runoff
    analyze_leaching_vs_runoff(model, plotter, detailed_data)
    
    # Chart 23: Radar chart
    create_radar_chart(plotter, soil_data)
    
    # Comprehensive comparison
    df = comprehensive_soil_comparison(model)
    
    # Summary
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    
    print("\n1. SOIL TYPE RANKING (by total nutrient loss):")
    totals = {soil: data['N'] + data['P'] + data['K'] for soil, data in soil_data.items()}
    for soil, total in sorted(totals.items(), key=lambda x: -x[1]):
        print(f"   {soil.capitalize()}: {total:.2f} kg/ha")
    
    print("\n2. LOSS MECHANISM BY SOIL:")
    print("   Sandy: High leaching (water infiltrates quickly)")
    print("   Clay: High runoff (water can't penetrate)")
    print("   Loamy: Balanced (moderate both)")
    
    print("\n3. NUTRIENT VULNERABILITY:")
    print("   N (Nitrogen): Most mobile, highest loss in all soil types")
    print("   K (Potassium): Moderate mobility")
    print("   P (Phosphorus): Least mobile, binds to soil particles")
    
    print(f"\nAll plots saved to: {output_dir}")


if __name__ == "__main__":
    main()

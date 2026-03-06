"""
06_rindm_cumulative.py - RINDM Cumulative Depletion Analysis

Implements Step 13 from EVALUATION_STRATEGY.md:
- Simulate realistic monsoon season
- Track cumulative nutrient depletion
- Multi-scenario analysis

Charts generated:
20. Multi-Line Plot - Cumulative N, P, K depletion over season
21. Before vs After Bar Chart - initial vs final N, P, K
22. Heatmap - Nutrient Loss (%) across Rainfall × Soil Type matrix
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils.plot_helper import PlotHelper
from src.models.rindm import RainfallNutrientDepletionModel


def simulate_monsoon_season(model):
    """
    Step 13: Simulate realistic monsoon season.
    """
    print("\n" + "=" * 60)
    print("MONSOON SEASON SIMULATION")
    print("=" * 60)
    
    # Realistic monsoon rainfall pattern (June-September)
    # Data inspired by Indian monsoon patterns
    monsoon_events = [
        {'date': 'Jun Week 1', 'rainfall_mm': 35, 'duration_hours': 4, 'description': 'Early monsoon'},
        {'date': 'Jun Week 2', 'rainfall_mm': 45, 'duration_hours': 5, 'description': 'Building up'},
        {'date': 'Jun Week 3', 'rainfall_mm': 55, 'duration_hours': 6, 'description': 'Moderate'},
        {'date': 'Jun Week 4', 'rainfall_mm': 70, 'duration_hours': 4, 'description': 'Heavy spell'},
        {'date': 'Jul Week 1', 'rainfall_mm': 85, 'duration_hours': 5, 'description': 'Peak monsoon'},
        {'date': 'Jul Week 2', 'rainfall_mm': 95, 'duration_hours': 6, 'description': 'Peak monsoon'},
        {'date': 'Jul Week 3', 'rainfall_mm': 80, 'duration_hours': 4, 'description': 'Heavy'},
        {'date': 'Jul Week 4', 'rainfall_mm': 65, 'duration_hours': 5, 'description': 'Moderate'},
        {'date': 'Aug Week 1', 'rainfall_mm': 70, 'duration_hours': 4, 'description': 'Heavy'},
        {'date': 'Aug Week 2', 'rainfall_mm': 55, 'duration_hours': 6, 'description': 'Moderate'},
        {'date': 'Aug Week 3', 'rainfall_mm': 45, 'duration_hours': 5, 'description': 'Decreasing'},
        {'date': 'Aug Week 4', 'rainfall_mm': 40, 'duration_hours': 4, 'description': 'Moderate'},
        {'date': 'Sep Week 1', 'rainfall_mm': 35, 'duration_hours': 6, 'description': 'Retreating'},
        {'date': 'Sep Week 2', 'rainfall_mm': 25, 'duration_hours': 4, 'description': 'Late monsoon'},
        {'date': 'Sep Week 3', 'rainfall_mm': 15, 'duration_hours': 3, 'description': 'End of monsoon'},
    ]
    
    total_rainfall = sum(e['rainfall_mm'] for e in monsoon_events)
    print(f"  Season: {len(monsoon_events)} rainfall events")
    print(f"  Total rainfall: {total_rainfall} mm")
    print(f"  Average per event: {total_rainfall/len(monsoon_events):.1f} mm")
    
    # Initial nutrients (typical values)
    initial_N, initial_P, initial_K = 90, 42, 43
    
    # Run for different soil types
    results = {}
    
    for soil in ['sandy', 'loamy', 'clay']:
        result = model.calculate_cumulative_loss(
            rainfall_events=monsoon_events,
            initial_N=initial_N,
            initial_P=initial_P,
            initial_K=initial_K,
            soil_type=soil
        )
        results[soil] = result
        
        print(f"\n{soil.upper()} SOIL:")
        print(f"  Initial: N={result['initial_N']}, P={result['initial_P']}, K={result['initial_K']} kg/ha")
        print(f"  Final:   N={result['final_N']}, P={result['final_P']}, K={result['final_K']} kg/ha")
        print(f"  Loss:    N={result['total_N_loss']:.1f} ({result['total_loss_percentage']['N']:.1f}%)")
        print(f"           P={result['total_P_loss']:.1f} ({result['total_loss_percentage']['P']:.1f}%)")
        print(f"           K={result['total_K_loss']:.1f} ({result['total_loss_percentage']['K']:.1f}%)")
    
    return results, monsoon_events


def create_cumulative_plots(plotter, results, events):
    """
    Chart 20: Multi-line plot of cumulative depletion.
    """
    print("\n" + "=" * 60)
    print("CREATING CUMULATIVE DEPLETION CHARTS")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "plots"
    
    # Create multi-panel plot for all soil types
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    colors = {'N': 'blue', 'P': 'orange', 'K': 'green'}
    
    for idx, (soil, result) in enumerate(results.items()):
        events_data = result['events']
        
        # Event numbers (0 = initial)
        event_nums = [0] + [e['event_number'] for e in events_data]
        
        # Nutrient values (initial + after each event)
        n_values = [result['initial_N']] + [e['N_after'] for e in events_data]
        p_values = [result['initial_P']] + [e['P_after'] for e in events_data]
        k_values = [result['initial_K']] + [e['K_after'] for e in events_data]
        
        axes[idx].plot(event_nums, n_values, 'o-', color='blue', label='N', linewidth=2)
        axes[idx].plot(event_nums, p_values, 's-', color='orange', label='P', linewidth=2)
        axes[idx].plot(event_nums, k_values, '^-', color='green', label='K', linewidth=2)
        
        axes[idx].set_xlabel('Rainfall Event')
        axes[idx].set_ylabel('Nutrient Level (kg/ha)')
        axes[idx].set_title(f'{soil.capitalize()} Soil')
        axes[idx].legend()
        axes[idx].grid(True, alpha=0.3)
        axes[idx].set_ylim(0, 100)
    
    plt.suptitle('Cumulative Nutrient Depletion Over Monsoon Season', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / '20_cumulative_depletion.png', bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  Chart 20: Cumulative depletion saved")
    
    # Chart 21: Before vs After for each soil type
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, (soil, result) in enumerate(results.items()):
        nutrients = ['N', 'P', 'K']
        before = [result['initial_N'], result['initial_P'], result['initial_K']]
        after = [result['final_N'], result['final_P'], result['final_K']]
        
        x = np.arange(len(nutrients))
        width = 0.35
        
        axes[idx].bar(x - width/2, before, width, label='Before', color='forestgreen')
        axes[idx].bar(x + width/2, after, width, label='After', color='salmon')
        
        axes[idx].set_xlabel('Nutrient')
        axes[idx].set_ylabel('Level (kg/ha)')
        axes[idx].set_title(f'{soil.capitalize()} Soil')
        axes[idx].set_xticks(x)
        axes[idx].set_xticklabels(nutrients)
        axes[idx].legend()
        
        # Add percentage labels
        for i, (b, a) in enumerate(zip(before, after)):
            pct = ((b - a) / b) * 100 if b > 0 else 0
            axes[idx].annotate(f'-{pct:.0f}%', 
                              xy=(i + width/2, a + 2),
                              ha='center', fontsize=9, color='red')
    
    plt.suptitle('Before vs After Monsoon Season', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / '21_before_after_comparison.png', bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("  Chart 21: Before/After comparison saved")


def create_rainfall_soil_heatmap(model, plotter):
    """
    Chart 22: Heatmap of nutrient loss across rainfall × soil type.
    """
    print("\n" + "=" * 60)
    print("RAINFALL × SOIL TYPE HEATMAP")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "plots"
    
    soil_types = ['sandy', 'loamy', 'clay']
    rainfall_values = [25, 50, 75, 100, 125, 150, 175, 200]
    
    # Create matrices for each nutrient
    for nutrient in ['N', 'P', 'K']:
        loss_matrix = []
        
        for rain in rainfall_values:
            row = []
            for soil in soil_types:
                result = model.calculate_nutrient_loss(
                    rainfall_mm=rain,
                    duration_hours=4,
                    N_current=90, P_current=42, K_current=43,
                    soil_type=soil
                )
                loss_pct = result['details'][nutrient]['loss_percentage']
                row.append(loss_pct)
            loss_matrix.append(row)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(8, 8))
        
        sns.heatmap(loss_matrix, annot=True, fmt='.1f', cmap='YlOrRd',
                   xticklabels=soil_types, yticklabels=rainfall_values, ax=ax)
        
        ax.set_xlabel('Soil Type')
        ax.set_ylabel('Rainfall (mm)')
        ax.set_title(f'{nutrient} Loss (%) - Rainfall × Soil Type')
        
        plt.tight_layout()
        plt.savefig(output_dir / f'22_heatmap_{nutrient}.png', bbox_inches='tight', facecolor='white', dpi=150)
        plt.close()
    
    print("  Chart 22: Heatmaps saved (N, P, K)")


def multiple_scenario_comparison(model):
    """
    Compare different scenarios: light vs heavy monsoon.
    """
    print("\n" + "=" * 60)
    print("SCENARIO COMPARISON")
    print("=" * 60)
    
    initial_N, initial_P, initial_K = 90, 42, 43
    
    # Light monsoon (drought year)
    light_monsoon = [
        {'rainfall_mm': 15, 'duration_hours': 4},
        {'rainfall_mm': 20, 'duration_hours': 5},
        {'rainfall_mm': 25, 'duration_hours': 6},
        {'rainfall_mm': 30, 'duration_hours': 4},
        {'rainfall_mm': 35, 'duration_hours': 5},
        {'rainfall_mm': 30, 'duration_hours': 4},
        {'rainfall_mm': 25, 'duration_hours': 5},
        {'rainfall_mm': 20, 'duration_hours': 4},
    ]
    
    # Heavy monsoon (flood year)
    heavy_monsoon = [
        {'rainfall_mm': 60, 'duration_hours': 3},
        {'rainfall_mm': 80, 'duration_hours': 4},
        {'rainfall_mm': 100, 'duration_hours': 4},
        {'rainfall_mm': 120, 'duration_hours': 3},
        {'rainfall_mm': 150, 'duration_hours': 4},
        {'rainfall_mm': 130, 'duration_hours': 3},
        {'rainfall_mm': 100, 'duration_hours': 4},
        {'rainfall_mm': 80, 'duration_hours': 5},
    ]
    
    scenarios = {
        'Light Monsoon': light_monsoon,
        'Heavy Monsoon': heavy_monsoon,
    }
    
    results = {}
    
    for scenario_name, events in scenarios.items():
        total_rain = sum(e['rainfall_mm'] for e in events)
        print(f"\n{scenario_name.upper()}: {total_rain}mm total")
        
        for soil in ['sandy', 'loamy', 'clay']:
            result = model.calculate_cumulative_loss(
                rainfall_events=events,
                initial_N=initial_N,
                initial_P=initial_P,
                initial_K=initial_K,
                soil_type=soil
            )
            
            key = f"{scenario_name}_{soil}"
            results[key] = result
            
            print(f"  {soil.capitalize()}: N loss={result['total_loss_percentage']['N']:.1f}%, "
                  f"P={result['total_loss_percentage']['P']:.1f}%, "
                  f"K={result['total_loss_percentage']['K']:.1f}%")
    
    return results


def main():
    print("=" * 60)
    print("RINDM CUMULATIVE DEPLETION ANALYSIS")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "plots"
    output_dir.mkdir(exist_ok=True)
    
    model = RainfallNutrientDepletionModel()
    plotter = PlotHelper(output_dir)
    
    # Step 13: Monsoon simulation
    results, events = simulate_monsoon_season(model)
    
    # Create charts
    create_cumulative_plots(plotter, results, events)
    create_rainfall_soil_heatmap(model, plotter)
    
    # Scenario comparison
    scenario_results = multiple_scenario_comparison(model)
    
    # Save detailed event data
    print("\n" + "=" * 60)
    print("SAVING DETAILED DATA")
    print("=" * 60)
    
    for soil, result in results.items():
        df = pd.DataFrame(result['events'])
        df.to_csv(output_dir / f'cumulative_events_{soil}.csv', index=False)
    
    print(f"  Event data saved to {output_dir}")
    
    # Summary
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    
    print("\n1. TOTAL SEASONAL LOSS:")
    for soil, result in results.items():
        total_loss = result['total_N_loss'] + result['total_P_loss'] + result['total_K_loss']
        print(f"   {soil.capitalize()}: {total_loss:.1f} kg/ha total")
    
    print("\n2. NUTRIENT VULNERABILITY RANKING:")
    for soil, result in results.items():
        losses = [
            ('N', result['total_loss_percentage']['N']),
            ('P', result['total_loss_percentage']['P']),
            ('K', result['total_loss_percentage']['K']),
        ]
        losses.sort(key=lambda x: -x[1])
        print(f"   {soil.capitalize()}: {' > '.join([f'{n} ({p:.0f}%)' for n,p in losses])}")
    
    print("\n3. SOIL MANAGEMENT IMPLICATIONS:")
    print("   - Sandy soil: Most vulnerable, needs frequent replenishment")
    print("   - Loamy soil: Moderate loss, standard management")
    print("   - Clay soil: Lowest loss, but watch for P runoff")
    
    print(f"\nAll plots saved to: {output_dir}")


if __name__ == "__main__":
    main()

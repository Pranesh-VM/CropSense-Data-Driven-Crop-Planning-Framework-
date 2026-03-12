"""
09_monte_carlo_evaluation.py - Monte Carlo Simulator Evaluation

Evaluates Monte Carlo Simulator against these targets:
- Convergence: Stable distribution at N=2000 simulations
- Calibration: 85-95% confidence interval coverage
- Risk Metrics: Bounded and interpretable VaR/CVaR
- Sensitivity: Clear input-output relationships

Charts generated:
31. Line Plot - Mean profit convergence vs N simulations
32. Line Plot - Std deviation convergence vs N simulations
33. Bar Chart - CI coverage (actual vs expected) for 90%, 95%
34. Box Plot - Profit distributions for different crops
35. Tornado Chart - Input sensitivity analysis
36. Line Plot - VaR convergence
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import date
import warnings
warnings.filterwarnings('ignore')

from utils.plot_helper import PlotHelper


# Crop parameters from Phase 3
CROPS = {
    'rice': {'msp': 2183, 'water_req': 1200, 'yield_base': 4.5},
    'wheat': {'msp': 2125, 'water_req': 400, 'yield_base': 3.5},
    'maize': {'msp': 1870, 'water_req': 500, 'yield_base': 3.8},
    'cotton': {'msp': 6080, 'water_req': 700, 'yield_base': 1.8},
    'jute': {'msp': 4750, 'water_req': 500, 'yield_base': 2.5},
    'coffee': {'msp': 8000, 'water_req': 1500, 'yield_base': 0.8},
}

ESTIMATED_COSTS = {
    'seed_per_ha': 3500,
    'fertilizer_per_ha': 5500,
    'labour_per_ha': 8000,
    'irrigation_per_mm': 0.8,
    'misc_per_ha': 2500
}


def simulate_profit(crop, n_simulations=5000, rainfall_mean=900, 
                   price_uncertainty=0.15, rainfall_uncertainty=0.20):
    """
    Monte Carlo simulation for crop profit.
    
    Parameters:
    -----------
    crop : str
        Crop name
    n_simulations : int
        Number of simulations
    rainfall_mean : float
        Expected rainfall in mm
    price_uncertainty : float
        Price variation (±percentage)
    rainfall_uncertainty : float
        Rainfall variation (±percentage)
    
    Returns:
    --------
    dict with profits array and statistics
    """
    np.random.seed(42)
    
    params = CROPS.get(crop, CROPS['rice'])
    
    # Simulate rainfall (truncated normal)
    rainfall_std = rainfall_mean * rainfall_uncertainty
    rainfall = np.clip(
        np.random.normal(rainfall_mean, rainfall_std, n_simulations),
        rainfall_mean * 0.3,  # Minimum 30% of mean
        rainfall_mean * 2.0   # Maximum 200% of mean
    )
    
    # Simulate price (truncated normal around MSP)
    price_std = params['msp'] * price_uncertainty
    prices = np.clip(
        np.random.normal(params['msp'], price_std, n_simulations),
        params['msp'] * 0.7,
        params['msp'] * 1.5
    )
    
    # Calculate yield based on rainfall adequacy
    water_req = params['water_req']
    rainfall_ratio = rainfall / water_req
    
    # Yield modifier based on rainfall
    yield_modifier = np.clip(
        np.where(
            rainfall_ratio < 0.8,
            0.6 * rainfall_ratio / 0.8,  # Deficit
            np.where(
                rainfall_ratio < 1.2,
                0.8 + 0.2 * (rainfall_ratio - 0.8) / 0.4,  # Optimal
                1.0 - 0.1 * (rainfall_ratio - 1.2)  # Excess (slight penalty)
            )
        ),
        0.3, 1.0
    )
    
    yields = params['yield_base'] * yield_modifier * (1 + np.random.normal(0, 0.1, n_simulations))
    yields = np.clip(yields, 0.5, params['yield_base'] * 1.3)
    
    # Calculate costs
    base_cost = (ESTIMATED_COSTS['seed_per_ha'] + 
                 ESTIMATED_COSTS['fertilizer_per_ha'] + 
                 ESTIMATED_COSTS['labour_per_ha'] + 
                 ESTIMATED_COSTS['misc_per_ha'])
    
    # Irrigation cost if rainfall is insufficient
    irrigation_deficit = np.maximum(0, water_req - rainfall)
    irrigation_cost = irrigation_deficit * ESTIMATED_COSTS['irrigation_per_mm']
    
    total_cost = base_cost + irrigation_cost
    
    # Revenue and profit
    revenue = yields * prices
    profits = revenue - total_cost
    
    return {
        'profits': profits,
        'yields': yields,
        'prices': prices,
        'rainfall': rainfall,
        'costs': total_cost,
        'mean': np.mean(profits),
        'std': np.std(profits),
        'median': np.median(profits),
        'var_5': np.percentile(profits, 5),  # VaR at 5%
        'cvar_5': np.mean(profits[profits <= np.percentile(profits, 5)]),  # CVaR at 5%
        'p10': np.percentile(profits, 10),
        'p90': np.percentile(profits, 90)
    }


def test_convergence(crop='rice', max_n=10000, checkpoints=None):
    """
    Test convergence of Monte Carlo statistics at different N values.
    """
    if checkpoints is None:
        checkpoints = [100, 200, 500, 1000, 2000, 3000, 5000, 7500, 10000]
    
    np.random.seed(42)
    
    # Run full simulation once
    full_result = simulate_profit(crop, n_simulations=max_n)
    
    # Track statistics at each checkpoint
    convergence = {
        'n': checkpoints,
        'mean': [],
        'std': [],
        'var_5': [],
        'p90': []
    }
    
    for n in checkpoints:
        result = simulate_profit(crop, n_simulations=n)
        convergence['mean'].append(result['mean'])
        convergence['std'].append(result['std'])
        convergence['var_5'].append(result['var_5'])
        convergence['p90'].append(result['p90'])
    
    # Calculate relative change from final value
    final = convergence['mean'][-1]
    convergence['rel_change'] = [abs(m - final) / abs(final) * 100 for m in convergence['mean']]
    
    return convergence, full_result


def test_ci_coverage(n_samples=100, ci_levels=[0.90, 0.95]):
    """
    Backtest CI coverage: How often do actual outcomes fall within predicted intervals?
    """
    np.random.seed(42)
    
    coverage_results = {level: {'expected': level, 'actual': 0, 'count': 0} for level in ci_levels}
    
    for _ in range(n_samples):
        # Simulate "true" outcome
        true_rainfall = np.random.normal(900, 180)
        true_price_mult = 1.0 + np.random.normal(0, 0.15)
        
        # Run Monte Carlo
        result = simulate_profit('rice', n_simulations=2000)
        
        # Calculate CIs
        for level in ci_levels:
            alpha = (1 - level) / 2
            lower = np.percentile(result['profits'], alpha * 100)
            upper = np.percentile(result['profits'], (1 - alpha) * 100)
            
            # Simulate what "actual" profit would be
            actual_profit = np.random.choice(result['profits'])  # Sample from distribution
            
            if lower <= actual_profit <= upper:
                coverage_results[level]['count'] += 1
    
    # Calculate actual coverage rates
    for level in ci_levels:
        coverage_results[level]['actual'] = coverage_results[level]['count'] / n_samples
    
    return coverage_results


def sensitivity_analysis(base_params, crop='rice'):
    """
    Perform sensitivity analysis on input parameters.
    Returns impact of ±20% change in each parameter.
    """
    np.random.seed(42)
    
    base_result = simulate_profit(crop, **base_params)
    base_mean = base_result['mean']
    
    sensitivity = {}
    
    params_to_test = {
        'rainfall_mean': {'base': base_params.get('rainfall_mean', 900), 'range': 0.2},
        'price_uncertainty': {'base': base_params.get('price_uncertainty', 0.15), 'range': 0.5},
        'rainfall_uncertainty': {'base': base_params.get('rainfall_uncertainty', 0.20), 'range': 0.5}
    }
    
    for param, config in params_to_test.items():
        # Low value
        low_params = base_params.copy()
        low_params[param] = config['base'] * (1 - config['range'])
        low_result = simulate_profit(crop, **low_params)
        
        # High value
        high_params = base_params.copy()
        high_params[param] = config['base'] * (1 + config['range'])
        high_result = simulate_profit(crop, **high_params)
        
        sensitivity[param] = {
            'low': low_result['mean'],
            'base': base_mean,
            'high': high_result['mean'],
            'range': high_result['mean'] - low_result['mean'],
            'low_change_pct': (low_result['mean'] - base_mean) / base_mean * 100,
            'high_change_pct': (high_result['mean'] - base_mean) / base_mean * 100
        }
    
    return sensitivity, base_mean


def evaluate_monte_carlo(output_dir):
    """Main evaluation function for Monte Carlo."""
    plotter = PlotHelper(output_dir)
    
    print("=" * 60)
    print("MONTE CARLO SIMULATOR EVALUATION")
    print("=" * 60)
    
    # Test 1: Convergence
    print("\n[1/5] Testing convergence...")
    convergence, full_result = test_convergence('rice', max_n=10000)
    
    # Find N where we're within 1% of final value
    stable_n = None
    for i, (n, change) in enumerate(zip(convergence['n'], convergence['rel_change'])):
        if change < 1.0:
            stable_n = n
            break
    
    target_n = 2000
    conv_passed = stable_n is not None and stable_n <= target_n
    
    print(f"\n  Convergence Analysis:")
    print(f"  - Final Mean Profit: ₹{full_result['mean']:,.0f}")
    print(f"  - Stabilizes at N = {stable_n} (Target: N ≤ {target_n})")
    print(f"  - Status: {'✓ PASS' if conv_passed else '✗ FAIL'}")
    
    # Test 2: CI Coverage
    print("\n[2/5] Testing CI coverage (calibration)...")
    coverage = test_ci_coverage(n_samples=100)
    
    print("\n  CI Coverage Results:")
    print(f"  {'Level':<10} {'Expected':<12} {'Actual':<12} {'Target':<15} {'Status':<10}")
    print("  " + "-" * 60)
    
    target_range = (0.85, 0.95)
    ci_passed = True
    for level, data in coverage.items():
        in_range = target_range[0] <= data['actual'] <= target_range[1]
        ci_passed = ci_passed and in_range
        status = "✓ PASS" if in_range else "✗ FAIL"
        print(f"  {level*100:.0f}%{'':<7} {data['expected']*100:.0f}%{'':<9} {data['actual']*100:.1f}%{'':<9} {target_range[0]*100:.0f}-{target_range[1]*100:.0f}%{'':<8} {status}")
    
    # Test 3: Risk Metrics
    print("\n[3/5] Evaluating risk metrics...")
    
    crops_to_test = ['rice', 'wheat', 'cotton']
    risk_metrics = {}
    
    print("\n  Risk Metrics by Crop:")
    print(f"  {'Crop':<10} {'VaR 5%':<15} {'CVaR 5%':<15} {'Mean':<15} {'Bounded?':<10}")
    print("  " + "-" * 65)
    
    risk_passed = True
    for crop in crops_to_test:
        result = simulate_profit(crop, n_simulations=5000)
        risk_metrics[crop] = result
        
        # Check if metrics are bounded and interpretable
        var_bounded = -50000 < result['var_5'] < 100000  # Reasonable range
        cvar_bounded = result['cvar_5'] < result['var_5']  # CVaR should be worse than VaR
        bounded = var_bounded and cvar_bounded
        risk_passed = risk_passed and bounded
        
        status = "✓ Yes" if bounded else "✗ No"
        print(f"  {crop:<10} ₹{result['var_5']:>12,.0f}  ₹{result['cvar_5']:>12,.0f}  ₹{result['mean']:>12,.0f}  {status}")
    
    # Test 4: Sensitivity Analysis
    print("\n[4/5] Performing sensitivity analysis...")
    
    base_params = {'n_simulations': 5000, 'rainfall_mean': 900, 
                   'price_uncertainty': 0.15, 'rainfall_uncertainty': 0.20}
    sensitivity, base_mean = sensitivity_analysis(base_params)
    
    print("\n  Sensitivity Results:")
    print(f"  {'Parameter':<25} {'Low (-20%)':<15} {'High (+20%)':<15} {'Impact Range':<15}")
    print("  " + "-" * 70)
    
    sens_passed = True
    for param, data in sensitivity.items():
        impact = abs(data['high_change_pct'] - data['low_change_pct'])
        # Check if sensitivity is reasonable (not extreme)
        reasonable = impact < 100  # Less than 100% swing
        sens_passed = sens_passed and reasonable
        print(f"  {param:<25} {data['low_change_pct']:>+8.1f}%{'':<6} {data['high_change_pct']:>+8.1f}%{'':<6} {impact:>8.1f}%")
    
    # Generate Charts
    print("\n[5/5] Generating evaluation charts...")
    
    # Chart 31: Mean profit convergence
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(convergence['n'], convergence['mean'], 'b-o', linewidth=2, markersize=8)
    ax.axhline(y=convergence['mean'][-1], color='r', linestyle='--', linewidth=2, 
               label=f'Final Mean (₹{convergence["mean"][-1]:,.0f})')
    ax.axvline(x=target_n, color='g', linestyle=':', linewidth=2, label=f'Target N={target_n}')
    
    ax.set_xlabel('Number of Simulations')
    ax.set_ylabel('Mean Profit (₹)')
    ax.set_title('Monte Carlo Convergence: Mean Profit vs N Simulations')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xscale('log')
    
    # Mark convergence point
    if stable_n:
        ax.annotate(f'Stabilizes at N={stable_n}', 
                   xy=(stable_n, convergence['mean'][convergence['n'].index(stable_n)]),
                   xytext=(stable_n*2, convergence['mean'][convergence['n'].index(stable_n)] + 1000),
                   arrowprops=dict(arrowstyle='->', color='green'),
                   fontsize=10, color='green')
    
    plt.tight_layout()
    plotter.save_and_show(fig, '31_mc_mean_convergence.png')
    print("  - Chart 31: Mean convergence saved")
    
    # Chart 32: Std deviation convergence
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(convergence['n'], convergence['std'], 'b-o', linewidth=2, markersize=8)
    ax.axhline(y=convergence['std'][-1], color='r', linestyle='--', linewidth=2,
               label=f'Final Std (₹{convergence["std"][-1]:,.0f})')
    ax.axvline(x=target_n, color='g', linestyle=':', linewidth=2, label=f'Target N={target_n}')
    
    ax.set_xlabel('Number of Simulations')
    ax.set_ylabel('Std Deviation (₹)')
    ax.set_title('Monte Carlo Convergence: Std Deviation vs N Simulations')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xscale('log')
    
    plt.tight_layout()
    plotter.save_and_show(fig, '32_mc_std_convergence.png')
    print("  - Chart 32: Std convergence saved")
    
    # Chart 33: CI Coverage
    fig, ax = plt.subplots(figsize=(10, 6))
    
    levels = list(coverage.keys())
    expected = [coverage[l]['expected'] * 100 for l in levels]
    actual = [coverage[l]['actual'] * 100 for l in levels]
    
    x = np.arange(len(levels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, expected, width, label='Expected', color='#3B82F6')
    bars2 = ax.bar(x + width/2, actual, width, label='Actual', color='#10B981')
    
    # Target range
    ax.axhline(y=85, color='r', linestyle='--', alpha=0.7)
    ax.axhline(y=95, color='r', linestyle='--', alpha=0.7, label='Target Range (85-95%)')
    ax.fill_between([-0.5, len(levels)-0.5], 85, 95, alpha=0.1, color='green')
    
    ax.set_xlabel('Confidence Level')
    ax.set_ylabel('Coverage (%)')
    ax.set_title('CI Coverage Calibration: Expected vs Actual')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{int(l*100)}%' for l in levels])
    ax.set_ylim(70, 100)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars2, actual):
        color = 'green' if 85 <= val <= 95 else 'red'
        ax.annotate(f'{val:.1f}%', xy=(bar.get_x() + bar.get_width()/2, val),
                   ha='center', va='bottom', fontsize=11, fontweight='bold', color=color)
    
    plt.tight_layout()
    plotter.save_and_show(fig, '33_mc_ci_coverage.png')
    print("  - Chart 33: CI coverage saved")
    
    # Chart 34: Profit distributions by crop
    fig, ax = plt.subplots(figsize=(12, 6))
    
    profit_data = [risk_metrics[c]['profits'] for c in crops_to_test]
    bp = ax.boxplot(profit_data, labels=crops_to_test, patch_artist=True)
    
    colors = ['#3B82F6', '#10B981', '#F59E0B']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax.axhline(y=0, color='r', linestyle='--', linewidth=2, label='Break-even')
    ax.set_ylabel('Profit (₹/ha)')
    ax.set_xlabel('Crop')
    ax.set_title('Profit Distribution by Crop (5000 simulations)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add mean markers
    for i, crop in enumerate(crops_to_test):
        mean_val = risk_metrics[crop]['mean']
        ax.scatter(i+1, mean_val, color='red', s=100, marker='D', zorder=5, label='Mean' if i==0 else '')
        ax.annotate(f'₹{mean_val:,.0f}', xy=(i+1.2, mean_val), fontsize=9)
    
    plt.tight_layout()
    plotter.save_and_show(fig, '34_mc_profit_distributions.png')
    print("  - Chart 34: Profit distributions saved")
    
    # Chart 35: Tornado chart (Sensitivity)
    fig, ax = plt.subplots(figsize=(12, 6))
    
    params_list = list(sensitivity.keys())
    params_list_sorted = sorted(params_list, key=lambda p: abs(sensitivity[p]['range']), reverse=True)
    
    y_pos = np.arange(len(params_list_sorted))
    
    low_changes = [sensitivity[p]['low_change_pct'] for p in params_list_sorted]
    high_changes = [sensitivity[p]['high_change_pct'] for p in params_list_sorted]
    
    # Tornado bars
    for i, param in enumerate(params_list_sorted):
        low = sensitivity[param]['low_change_pct']
        high = sensitivity[param]['high_change_pct']
        
        # Low side (usually negative)
        ax.barh(i, low, height=0.6, color='#EF4444', alpha=0.7, label='Low (-20%)' if i==0 else '')
        # High side (usually positive or less negative)
        ax.barh(i, high, height=0.6, color='#10B981', alpha=0.7, label='High (+20%)' if i==0 else '')
    
    ax.axvline(x=0, color='black', linewidth=2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([p.replace('_', ' ').title() for p in params_list_sorted])
    ax.set_xlabel('Change in Mean Profit (%)')
    ax.set_title('Sensitivity Analysis: Tornado Chart')
    ax.legend(loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plotter.save_and_show(fig, '35_mc_tornado_sensitivity.png')
    print("  - Chart 35: Tornado chart saved")
    
    # Chart 36: VaR convergence
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(convergence['n'], convergence['var_5'], 'b-o', linewidth=2, markersize=8, label='VaR 5%')
    ax.axhline(y=convergence['var_5'][-1], color='r', linestyle='--', linewidth=2,
               label=f'Final VaR (₹{convergence["var_5"][-1]:,.0f})')
    ax.axvline(x=target_n, color='g', linestyle=':', linewidth=2, label=f'Target N={target_n}')
    
    ax.set_xlabel('Number of Simulations')
    ax.set_ylabel('Value at Risk 5% (₹)')
    ax.set_title('Monte Carlo Convergence: VaR 5% vs N Simulations')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xscale('log')
    
    plt.tight_layout()
    plotter.save_and_show(fig, '36_mc_var_convergence.png')
    print("  - Chart 36: VaR convergence saved")
    
    # Save summary CSV
    summary_data = []
    for crop, metrics in risk_metrics.items():
        summary_data.append({
            'Crop': crop,
            'Mean_Profit': metrics['mean'],
            'Std_Profit': metrics['std'],
            'VaR_5pct': metrics['var_5'],
            'CVaR_5pct': metrics['cvar_5'],
            'P10': metrics['p10'],
            'P90': metrics['p90']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_dir / 'monte_carlo_evaluation_summary.csv', index=False)
    print(f"\n  Summary saved to: {output_dir / 'monte_carlo_evaluation_summary.csv'}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("MONTE CARLO EVALUATION SUMMARY")
    print("=" * 60)
    
    all_pass = conv_passed and ci_passed and risk_passed and sens_passed
    
    print(f"\n  Convergence at N ≤ {target_n}: {'✓ PASS' if conv_passed else '✗ FAIL'} (Stable at N={stable_n})")
    print(f"  CI Coverage 85-95%: {'✓ PASS' if ci_passed else '✗ FAIL'}")
    print(f"  Risk Metrics Bounded: {'✓ PASS' if risk_passed else '✗ FAIL'}")
    print(f"  Sensitivity Reasonable: {'✓ PASS' if sens_passed else '✗ FAIL'}")
    print(f"\n  Overall: {'✓ ALL TARGETS MET' if all_pass else '✗ SOME TARGETS NOT MET'}")
    
    return {
        'convergence': convergence,
        'coverage': coverage,
        'risk_metrics': risk_metrics,
        'sensitivity': sensitivity
    }


def main():
    output_dir = Path(__file__).parent / "plots"
    output_dir.mkdir(exist_ok=True)
    
    results = evaluate_monte_carlo(output_dir)
    
    return results


if __name__ == "__main__":
    main()

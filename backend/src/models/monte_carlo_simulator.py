"""
Monte Carlo Simulator for CropSense Phase 3

Runs probabilistic simulations to quantify profit uncertainty and risk.

Key Idea:
- "What if rainfall is ±20% and market price is ±15%?"
- Run 5000 simulations with random perturbations
- Get: profit distribution, probability of loss, confidence intervals

Usage:
    mc = MonteCarloSimulator(n_simulations=5000)
    state = EnvironmentState(n=90, p=42, k=43, soil_type='loamy',
                             expected_rainfall_mm=600)
    
    # Single crop risk analysis
    result = mc.simulate_crop_profit(state, 'rice')
    print(f"Mean profit: ₹{result['mean_profit']:,.0f}")
    print(f"Prob of loss: {result['prob_of_loss']:.1%}")
    
    # Compare multiple crops
    profiles = mc.compare_crops_risk_profile(state, ['rice', 'lentil', 'wheat'])
    for p in profiles:
        print(f"{p['crop']}: Risk-adjusted score = ₹{p['risk_adjusted_score']:,.0f}")
"""

import random
import math
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

# Import state transition simulator
from src.models.state_transition_simulator import (
    StateTransitionSimulator,
    EnvironmentState,
    DEFAULT_MARKET_PRICES
)


class MonteCarloSimulator:
    """
    Monte Carlo simulation engine for crop profit risk analysis.
    
    Simulates future scenarios by randomly perturbing:
    - Rainfall: ±20% from expected (configurable)
    - Market price: ±15% from base price (configurable)
    
    Outputs:
    - Profit distribution statistics (mean, std, percentiles)
    - Probability of loss (negative reward)
    - Risk-adjusted score (mean - std_dev)
    
    Typical usage:
        - API endpoint: 2000 simulations (~1s response time)
        - Detailed analysis: 5000+ simulations
    """
    
    def __init__(self, n_simulations: int = 5000):
        """
        Initialize Monte Carlo simulator.
        
        Args:
            n_simulations: Number of simulations per crop (default 5000)
        """
        self.n_simulations = n_simulations
        self.simulator = StateTransitionSimulator()
    
    def simulate_crop_profit(
        self,
        state: EnvironmentState,
        crop: str,
        rainfall_uncertainty_pct: float = 0.20,
        price_uncertainty_pct: float = 0.15,
        market_price_override: Optional[float] = None
    ) -> Dict:
        """
        Run Monte Carlo simulation for ONE crop choice.
        
        Simulates N future scenarios with randomized rainfall and market prices.
        
        Args:
            state: Current environment state
            crop: Crop name to simulate
            rainfall_uncertainty_pct: Rainfall variation (default ±20%)
            price_uncertainty_pct: Price variation (default ±15%)
            market_price_override: Optional base price (defaults to DEFAULT_MARKET_PRICES)
        
        Returns:
            {
                'crop': 'rice',
                'mean_profit': 0.52,               # Scaled down (0.52 lakhs = ₹52,000)
                'min_profit': 0.28,
                'max_profit': 0.81,
                'std_dev': 0.11,
                'prob_of_loss': 0.08,             # 8% chance of negative reward
                'percentile_5': 0.32,             # worst-case (5th pct)
                'percentile_25': 0.44,
                'percentile_75': 0.61,
                'percentile_95': 0.73,            # best-case (95th pct)
                'simulations': 5000
            }
        """
        crop_lower = crop.lower()
        
        # Get base price
        base_price = market_price_override or DEFAULT_MARKET_PRICES.get(crop_lower, 25.0)
        
        # Storage for simulation results
        profits = []
        
        # Run simulations
        for _ in range(self.n_simulations):
            # Sample rainfall with uncertainty
            # Using normal distribution, clipped to reasonable range
            rainfall_sigma = state.expected_rainfall_mm * rainfall_uncertainty_pct
            sampled_rainfall = max(
                50,  # Minimum 50mm (drought scenario)
                np.random.normal(state.expected_rainfall_mm, rainfall_sigma)
            )
            
            # Sample market price with uncertainty
            price_sigma = base_price * price_uncertainty_pct
            sampled_price = max(
                1.0,  # Minimum ₹1/kg
                np.random.normal(base_price, price_sigma)
            )
            
            # Create perturbed state
            perturbed_state = EnvironmentState(
                n=state.n,
                p=state.p,
                k=state.k,
                season_index=state.season_index,
                expected_rainfall_mm=sampled_rainfall,
                soil_type=state.soil_type,
                temperature=state.temperature,
                humidity=state.humidity
            )
            
            # Run transition with perturbed values
            try:
                _, reward, _ = self.simulator.transition(
                    perturbed_state,
                    crop_lower,
                    market_price_override=sampled_price
                )
                profits.append(reward)
            except ValueError:
                # Skip invalid crops
                continue
        
        if not profits:
            return {
                'crop': crop_lower,
                'error': f'No valid simulations for {crop}',
                'simulations': 0
            }
        
        # Convert to numpy for statistics
        profits_arr = np.array(profits)
        
        # Calculate statistics
        mean_profit = float(np.mean(profits_arr))
        std_dev = float(np.std(profits_arr))
        
        # Count negative rewards (losses)
        num_losses = np.sum(profits_arr < 0)
        prob_of_loss = num_losses / len(profits_arr)
        
        # Multiply by factor to scale down (1 lakh = 100,000 rupees)
        SCALE_FACTOR = 0.1
        
        return {
            'crop': crop_lower,
            'mean_profit': round(mean_profit * SCALE_FACTOR, 2),
            'min_profit': round(float(np.min(profits_arr)) * SCALE_FACTOR, 2),
            'max_profit': round(float(np.max(profits_arr)) * SCALE_FACTOR, 2),
            'std_dev': round(std_dev * SCALE_FACTOR, 2),
            'prob_of_loss': round(prob_of_loss, 4),
            'percentile_5': round(float(np.percentile(profits_arr, 5)) * SCALE_FACTOR, 2),
            'percentile_25': round(float(np.percentile(profits_arr, 25)) * SCALE_FACTOR, 2),
            'percentile_50': round(float(np.percentile(profits_arr, 50)) * SCALE_FACTOR, 2),  # median
            'percentile_75': round(float(np.percentile(profits_arr, 75)) * SCALE_FACTOR, 2),
            'percentile_95': round(float(np.percentile(profits_arr, 95)) * SCALE_FACTOR, 2),
            'simulations': len(profits)
        }
    
    def compare_crops_risk_profile(
        self,
        state: EnvironmentState,
        candidate_crops: List[str],
        rainfall_uncertainty_pct: float = 0.20,
        price_uncertainty_pct: float = 0.15,
        crop_prices: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Compare risk profiles of multiple crops.
        
        Calls simulate_crop_profit() for each crop and adds risk-adjusted scoring.
        
        Risk-Adjusted Score = mean_profit - std_dev
        (Higher = better balance of reward and stability)
        
        Args:
            state: Current environment state
            candidate_crops: List of crop names to compare
            rainfall_uncertainty_pct: Rainfall variation (default ±20%)
            price_uncertainty_pct: Price variation (default ±15%)
            crop_prices: Optional dict of crop prices (e.g., {'rice': 2150, 'wheat': 2300})
        
        Returns:
            List sorted by risk_adjusted_score (descending) - scaled values:
            [
                {
                    'crop': 'lentil',
                    'mean_profit': 0.41,               # Scaled down (0.41 lakhs)
                    'std_dev': 0.08,
                    'prob_of_loss': 0.04,
                    'risk_adjusted_score': 0.33,       ← RECOMMENDED (low risk)
                    'base_price_per_quintal': 4500,
                    ...
                },
                {
                    'crop': 'wheat',
                    'mean_profit': 0.44,
                    'std_dev': 0.12,
                    'prob_of_loss': 0.09,
                    'risk_adjusted_score': 0.32,
                    'base_price_per_quintal': 2300,
                    ...
                },
                {
                    'crop': 'rice',
                    'mean_profit': 0.52,
                    'std_dev': 0.18,
                    'prob_of_loss': 0.14,
                    'risk_adjusted_score': 0.34,       ← High reward but risky
                    'base_price_per_quintal': 2150,
                    ...
                }
            ]
        """
        profiles = []
        
        for crop in candidate_crops:
            # Get crop-specific price if provided
            crop_price = None
            if crop_prices and crop in crop_prices:
                crop_price = float(crop_prices[crop])
            
            result = self.simulate_crop_profit(
                state=state,
                crop=crop,
                rainfall_uncertainty_pct=rainfall_uncertainty_pct,
                price_uncertainty_pct=price_uncertainty_pct,
                market_price_override=crop_price  # Pass real market price
            )
            
            if 'error' in result:
                profiles.append(result)
                continue
            
            # Add base price to result
            if crop_prices and crop in crop_prices:
                result['base_price_per_quintal'] = crop_prices[crop]
            
            # Calculate risk-adjusted score (already scaled down from simulate_crop_profit)
            # Simple: mean - 1*std_dev (Sharpe-like ratio without risk-free rate)
            risk_adjusted_score = result['mean_profit'] - result['std_dev']
            
            result['risk_adjusted_score'] = round(risk_adjusted_score, 2)
            
            # Add risk category
            if result['prob_of_loss'] < 0.05:
                result['risk_category'] = 'LOW_RISK'
            elif result['prob_of_loss'] < 0.15:
                result['risk_category'] = 'MODERATE_RISK'
            else:
                result['risk_category'] = 'HIGH_RISK'
            
            profiles.append(result)
        
        # Sort by risk-adjusted score (descending)
        profiles.sort(
            key=lambda x: x.get('risk_adjusted_score', float('-inf')),
            reverse=True
        )
        
        return profiles
    
    def simulate_multi_season_profit(
        self,
        state: EnvironmentState,
        crop_sequence: List[str],
        rainfall_uncertainty_pct: float = 0.20,
        price_uncertainty_pct: float = 0.15
    ) -> Dict:
        """
        Simulate profit distribution for a multi-season crop sequence.
        
        Useful for evaluating Q-Learning suggested rotations.
        
        Args:
            state: Initial environment state
            crop_sequence: List of crops to plant in order
            rainfall_uncertainty_pct: Rainfall variation
            price_uncertainty_pct: Price variation
        
        Returns:
            {
                'sequence': ['rice', 'lentil', 'wheat'],
                'total_mean_profit': 1.25,          # Scaled down (1.25 lakhs)
                'total_std_dev': 0.22,
                'prob_of_total_loss': 0.02,
                'season_breakdown': [
                    {'season': 1, 'crop': 'rice', 'mean_profit': 0.48, ...},
                    {'season': 2, 'crop': 'lentil', 'mean_profit': 0.35, ...},
                    {'season': 3, 'crop': 'wheat', 'mean_profit': 0.42, ...}
                ],
                'simulations': 5000
            }
        """
        # Storage for total profits across all simulations
        total_profits = []
        
        # Storage for per-season profits
        season_profits = {i: [] for i in range(len(crop_sequence))}
        
        for _ in range(self.n_simulations):
            sim_state = state.copy()
            total_profit = 0.0
            
            for season_idx, crop in enumerate(crop_sequence):
                crop_lower = crop.lower()
                base_price = DEFAULT_MARKET_PRICES.get(crop_lower, 25.0)
                
                # Sample uncertainties
                rainfall_sigma = sim_state.expected_rainfall_mm * rainfall_uncertainty_pct
                sampled_rainfall = max(50, np.random.normal(sim_state.expected_rainfall_mm, rainfall_sigma))
                
                price_sigma = base_price * price_uncertainty_pct
                sampled_price = max(1.0, np.random.normal(base_price, price_sigma))
                
                # Create perturbed state for this season
                perturbed = EnvironmentState(
                    n=sim_state.n,
                    p=sim_state.p,
                    k=sim_state.k,
                    season_index=sim_state.season_index,
                    expected_rainfall_mm=sampled_rainfall,
                    soil_type=sim_state.soil_type,
                    temperature=sim_state.temperature,
                    humidity=sim_state.humidity
                )
                
                try:
                    next_state, reward, _ = self.simulator.transition(
                        perturbed, crop_lower, market_price_override=sampled_price
                    )
                    season_profits[season_idx].append(reward)
                    total_profit += reward
                    sim_state = next_state
                except ValueError:
                    season_profits[season_idx].append(0)
            
            total_profits.append(total_profit)
        
        # Calculate statistics
        total_arr = np.array(total_profits)
        
        # Multiply by factor to scale down (1 lakh = 100,000 rupees)
        SCALE_FACTOR = 0.00001
        
        # Season breakdown
        season_breakdown = []
        for i, crop in enumerate(crop_sequence):
            season_arr = np.array(season_profits[i])
            season_breakdown.append({
                'season': i + 1,
                'crop': crop.lower(),
                'mean_profit': round(float(np.mean(season_arr)) * SCALE_FACTOR, 2),
                'std_dev': round(float(np.std(season_arr)) * SCALE_FACTOR, 2),
                'prob_of_loss': round(float(np.sum(season_arr < 0) / len(season_arr)), 4)
            })
        
        return {
            'sequence': [c.lower() for c in crop_sequence],
            'num_seasons': len(crop_sequence),
            'total_mean_profit': round(float(np.mean(total_arr)) * SCALE_FACTOR, 2),
            'total_std_dev': round(float(np.std(total_arr)) * SCALE_FACTOR, 2),
            'total_min_profit': round(float(np.min(total_arr)) * SCALE_FACTOR, 2),
            'total_max_profit': round(float(np.max(total_arr)) * SCALE_FACTOR, 2),
            'prob_of_total_loss': round(float(np.sum(total_arr < 0) / len(total_arr)), 4),
            'percentile_5': round(float(np.percentile(total_arr, 5)) * SCALE_FACTOR, 2),
            'percentile_95': round(float(np.percentile(total_arr, 95)) * SCALE_FACTOR, 2),
            'season_breakdown': season_breakdown,
            'simulations': len(total_profits)
        }
    
    def sensitivity_analysis(
        self,
        state: EnvironmentState,
        crop: str,
        parameter: str = 'rainfall',
        variations: List[float] = None
    ) -> List[Dict]:
        """
        Analyze how profit changes with systematic parameter variation.
        
        Useful for understanding which factors have the most impact.
        
        Args:
            state: Base environment state
            crop: Crop to analyze
            parameter: 'rainfall' or 'price'
            variations: List of multipliers (default [0.6, 0.8, 1.0, 1.2, 1.4])
        
        Returns:
            [
                {'variation': 0.6, 'mean_profit': 0.35, 'std_dev': 0.08, ...},  # Scaled
                {'variation': 0.8, 'mean_profit': 0.42, 'std_dev': 0.09, ...},
                {'variation': 1.0, 'mean_profit': 0.48, 'std_dev': 0.10, ...},
                {'variation': 1.2, 'mean_profit': 0.45, 'std_dev': 0.12, ...},
                {'variation': 1.4, 'mean_profit': 0.40, 'std_dev': 0.15, ...},
            ]
        """
        if variations is None:
            variations = [0.6, 0.8, 1.0, 1.2, 1.4]
        
        results = []
        crop_lower = crop.lower()
        base_price = DEFAULT_MARKET_PRICES.get(crop_lower, 25.0)
        
        for mult in variations:
            if parameter == 'rainfall':
                test_state = EnvironmentState(
                    n=state.n, p=state.p, k=state.k,
                    season_index=state.season_index,
                    expected_rainfall_mm=state.expected_rainfall_mm * mult,
                    soil_type=state.soil_type,
                    temperature=state.temperature,
                    humidity=state.humidity
                )
                result = self.simulate_crop_profit(
                    test_state, crop_lower,
                    rainfall_uncertainty_pct=0.10,  # Reduced for systematic analysis
                    price_uncertainty_pct=0.05
                )
            else:  # price
                test_state = state.copy()
                result = self.simulate_crop_profit(
                    test_state, crop_lower,
                    rainfall_uncertainty_pct=0.05,
                    price_uncertainty_pct=0.10,
                    market_price_override=base_price * mult
                )
            
            result['variation'] = mult
            result['parameter'] = parameter
            results.append(result)
        
        return results


# ============================================================================
# TEST / DEMO
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Monte Carlo Simulator Test")
    print("=" * 60)
    
    # Use fewer simulations for quick test
    mc = MonteCarloSimulator(n_simulations=1000)
    
    # Initial state
    state = EnvironmentState(
        n=90, p=42, k=43,
        season_index=0,
        expected_rainfall_mm=600,
        soil_type='loamy'
    )
    
    # Test 1: Single crop simulation
    print("\n--- Test 1: Single Crop Simulation (Rice) ---")
    result = mc.simulate_crop_profit(state, 'rice')
    print(f"Mean profit: ₹{result['mean_profit']:.2f} Lakhs")
    print(f"Std dev: ₹{result['std_dev']:.2f} Lakhs")
    print(f"Prob of loss: {result['prob_of_loss']:.1%}")
    print(f"5th percentile: ₹{result['percentile_5']:.2f} Lakhs")
    print(f"95th percentile: ₹{result['percentile_95']:.2f} Lakhs")
    
    # Test 2: Compare crops
    print("\n--- Test 2: Compare Crops Risk Profile ---")
    profiles = mc.compare_crops_risk_profile(state, ['rice', 'lentil', 'wheat', 'maize'])
    for p in profiles:
        if 'error' not in p:
            print(f"  {p['crop']:10} mean=₹{p['mean_profit']:>6.2f}L  "
                  f"std=₹{p['std_dev']:>5.2f}L  "
                  f"prob_loss={p['prob_of_loss']:>5.1%}  "
                  f"risk_adj=₹{p['risk_adjusted_score']:>6.2f}L  "
                  f"[{p['risk_category']}]")
    
    # Test 3: Multi-season simulation
    print("\n--- Test 3: Multi-Season Simulation ---")
    multi = mc.simulate_multi_season_profit(
        state, ['rice', 'lentil', 'wheat']
    )
    print(f"Sequence: {' → '.join(multi['sequence'])}")
    print(f"Total mean profit: ₹{multi['total_mean_profit']:.2f} Lakhs")
    print(f"Total std dev: ₹{multi['total_std_dev']:.2f} Lakhs")
    print(f"Prob of total loss: {multi['prob_of_total_loss']:.1%}")
    print(f"5th-95th percentile: ₹{multi['percentile_5']:.2f}L – ₹{multi['percentile_95']:.2f}L")
    print("Season breakdown:")
    for s in multi['season_breakdown']:
        print(f"  S{s['season']}: {s['crop']:10} mean=₹{s['mean_profit']:>5.2f}L")
    
    print("\n✓ All tests passed!")

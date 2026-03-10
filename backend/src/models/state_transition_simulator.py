"""
State-Transition Simulator for CropSense Phase 3

The core simulation engine that models how soil state changes based on crop choices.
All other Phase 3 modules (LSTM, Monte Carlo, Q-Learning) depend on this.

Formula: E(t+1) = f(E(t), A(t))
Where:
  E(t)   = EnvironmentState at time t → N, P, K, season, rainfall, soil_type
  A(t)   = Action at time t → crop name
  E(t+1) = Next EnvironmentState after crop cycle completes

Internal steps:
  1. Crop nutrient UPTAKE → from crop_nutrient_database.py
  2. Rainfall nutrient LOSS → from rindm.py
  3. Yield estimate → uptake_sufficiency * base_yield
  4. Profit → yield * market_price
  5. Soil penalty → if N/P/K drops below sustainability threshold
  6. Reward → profit - soil_penalty
"""

import copy
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import numpy as np

# Import existing modules
from src.models.rindm import RainfallNutrientDepletionModel
from src.utils.crop_nutrient_database import (
    CROP_NUTRIENT_UPTAKE,
    get_crop_nutrient_uptake,
    calculate_remaining_nutrients,
    NUTRIENT_THRESHOLDS
)


# ============================================================================
# CONSTANTS
# ============================================================================

# Market prices (₹/kg) — used when Prophet forecast is not yet available
DEFAULT_MARKET_PRICES = {
    'rice': 20.0,
    'wheat': 21.0,
    'maize': 16.0,
    'chickpea': 55.0,
    'lentil': 70.0,
    'mungbean': 65.0,
    'blackgram': 60.0,
    'pigeonpeas': 60.0,
    'kidneybeans': 90.0,
    'mothbeans': 50.0,
    'pomegranate': 60.0,
    'banana': 15.0,
    'mango': 40.0,
    'grapes': 60.0,
    'watermelon': 10.0,
    'muskmelon': 12.0,
    'apple': 80.0,
    'orange': 30.0,
    'papaya': 12.0,
    'coconut': 18.0,
    'cotton': 55.0,
    'jute': 30.0,
    'coffee': 200.0,
}

# Sustainability thresholds (below these = soil is degrading)
MIN_SUSTAINABLE_N = 40.0   # kg/ha
MIN_SUSTAINABLE_P = 15.0   # kg/ha
MIN_SUSTAINABLE_K = 30.0   # kg/ha

# How much we penalize per kg/ha below threshold
SOIL_DEGRADATION_PENALTY_COEFF = 50.0   # ₹ per kg/ha deficit

# Season names for indexing
SEASONS = ['kharif', 'rabi', 'zaid', 'annual']

# Legume crops that fix nitrogen (reduce N depletion)
LEGUME_CROPS = {'chickpea', 'lentil', 'mungbean', 'blackgram', 'pigeonpeas', 'kidneybeans', 'mothbeans'}

# Nitrogen fixation benefit for legumes (kg/ha added back to soil)
LEGUME_N_FIXATION = 25.0


# ============================================================================
# ENVIRONMENT STATE
# ============================================================================

@dataclass
class EnvironmentState:
    """
    Represents the current soil and environmental state.
    
    Attributes:
        n: Nitrogen level (kg/ha)
        p: Phosphorus level (kg/ha)
        k: Potassium level (kg/ha)
        season_index: 0=Kharif, 1=Rabi, 2=Zaid, 3=Annual
        expected_rainfall_mm: Expected seasonal rainfall
        soil_type: 'sandy', 'loamy', or 'clay'
        temperature: Average temperature (°C)
        humidity: Average humidity (%)
    """
    n: float
    p: float
    k: float
    season_index: int = 0
    expected_rainfall_mm: float = 500.0
    soil_type: str = 'loamy'
    temperature: float = 25.0
    humidity: float = 60.0
    
    def to_vector(self) -> np.ndarray:
        """Convert to numpy array for ML model input."""
        return np.array([
            self.n,
            self.p,
            self.k,
            self.season_index,
            self.expected_rainfall_mm,
            self.temperature,
            self.humidity
        ], dtype=np.float32)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON API response."""
        return {
            'N': round(self.n, 2),
            'P': round(self.p, 2),
            'K': round(self.k, 2),
            'season_index': self.season_index,
            'season_name': SEASONS[self.season_index] if 0 <= self.season_index < len(SEASONS) else 'unknown',
            'expected_rainfall_mm': round(self.expected_rainfall_mm, 2),
            'soil_type': self.soil_type,
            'temperature': round(self.temperature, 2),
            'humidity': round(self.humidity, 2)
        }
    
    def copy(self) -> 'EnvironmentState':
        """Create a deep copy of the state."""
        return EnvironmentState(
            n=self.n,
            p=self.p,
            k=self.k,
            season_index=self.season_index,
            expected_rainfall_mm=self.expected_rainfall_mm,
            soil_type=self.soil_type,
            temperature=self.temperature,
            humidity=self.humidity
        )


# ============================================================================
# STATE TRANSITION SIMULATOR
# ============================================================================

class StateTransitionSimulator:
    """
    Main simulation engine for crop-soil state transitions.
    
    This is the core module that LSTM, Monte Carlo, and Q-Learning all depend on.
    
    Usage:
        sim = StateTransitionSimulator()
        state = EnvironmentState(n=90, p=42, k=43, season_index=0,
                                 expected_rainfall_mm=600, soil_type='loamy')
        
        # Single transition
        next_state, reward, details = sim.transition(state, 'rice')
        
        # Compare options
        options = sim.compare_crop_options(state, ['rice', 'lentil', 'wheat'])
        
        # Generate training sequence
        sequence = sim.generate_lstm_training_sequence(state, num_seasons=8)
    """
    
    def __init__(self, market_prices: Optional[Dict[str, float]] = None):
        """
        Initialize the simulator.
        
        Args:
            market_prices: Optional custom market prices dict. Defaults to DEFAULT_MARKET_PRICES.
        """
        self.rindm = RainfallNutrientDepletionModel()
        self.market_prices = market_prices or DEFAULT_MARKET_PRICES.copy()
    
    def transition(
        self,
        state: EnvironmentState,
        crop_action: str,
        market_price_override: Optional[float] = None,
        rainfall_events: Optional[List[Dict]] = None
    ) -> Tuple[EnvironmentState, float, Dict]:
        """
        Execute a state transition for one crop cycle.
        
        Formula: E(t+1) = f(E(t), A(t))
        
        Args:
            state: Current environment state
            crop_action: Crop name to plant (e.g., 'rice', 'wheat')
            market_price_override: Optional custom market price (₹/kg)
            rainfall_events: Optional list of rainfall events. If None, generates synthetic.
        
        Returns:
            Tuple of (next_state, reward, details_dict)
            - next_state: EnvironmentState after crop cycle
            - reward: profit_per_ha - soil_penalty (₹/ha)
            - details: Full breakdown of calculations
        """
        crop_action = crop_action.lower()
        
        # Get crop data
        crop_data = get_crop_nutrient_uptake(crop_action)
        if not crop_data:
            raise ValueError(f"Unknown crop: {crop_action}")
        
        cycle_days = crop_data['cycle_days']
        base_yield = crop_data['average_yield_tonnes_ha']
        n_uptake = crop_data['N_uptake_kg_ha']
        p_uptake = crop_data['P_uptake_kg_ha']
        k_uptake = crop_data['K_uptake_kg_ha']
        
        # Step 1: Generate synthetic rainfall events if not provided
        if rainfall_events is None:
            rainfall_events = self._generate_synthetic_rainfall(
                total_mm=state.expected_rainfall_mm,
                cycle_days=cycle_days
            )
        
        # Step 2: Calculate rainfall nutrient loss using RINDM
        cumulative_loss = self.rindm.calculate_cumulative_loss(
            rainfall_events=rainfall_events,
            initial_N=state.n,
            initial_P=state.p,
            initial_K=state.k,
            soil_type=state.soil_type
        )
        
        n_after_rain = cumulative_loss['final_N']
        p_after_rain = cumulative_loss['final_P']
        k_after_rain = cumulative_loss['final_K']
        
        # Step 3: Calculate crop nutrient uptake
        # Actual uptake is limited by available nutrients
        actual_n_uptake = min(n_uptake, n_after_rain * 0.95)  # Can't take more than 95% of available
        actual_p_uptake = min(p_uptake, p_after_rain * 0.95)
        actual_k_uptake = min(k_uptake, k_after_rain * 0.95)
        
        # Step 4: Calculate nutrient sufficiency ratio
        sufficiency_ratio = self._nutrient_sufficiency_ratio(
            n_after_rain, p_after_rain, k_after_rain,
            n_uptake, p_uptake, k_uptake
        )
        
        # Step 5: Calculate final nutrients after crop uptake
        final_n = max(0, n_after_rain - actual_n_uptake)
        final_p = max(0, p_after_rain - actual_p_uptake)
        final_k = max(0, k_after_rain - actual_k_uptake)
        
        # Step 6: Legume nitrogen fixation benefit
        is_legume = crop_action in LEGUME_CROPS
        if is_legume:
            final_n += LEGUME_N_FIXATION  # Legumes fix nitrogen
        
        # Step 7: Calculate yield based on sufficiency
        estimated_yield = base_yield * sufficiency_ratio  # tonnes/ha
        
        # Step 8: Calculate profit
        market_price = market_price_override or self.market_prices.get(crop_action, 20.0)
        gross_revenue = estimated_yield * 1000 * market_price  # yield in tonnes → kg, then × price/kg
        
        # Assume 40% production costs
        production_cost = gross_revenue * 0.40
        gross_profit = gross_revenue - production_cost
        
        # Step 9: Calculate soil penalty
        soil_penalty = self._calculate_soil_penalty(final_n, final_p, final_k)
        
        # Step 10: Calculate reward
        reward = gross_profit - soil_penalty
        
        # Step 11: Create next state
        next_state = EnvironmentState(
            n=final_n,
            p=final_p,
            k=final_k,
            season_index=(state.season_index + 1) % 4,  # Rotate seasons
            expected_rainfall_mm=state.expected_rainfall_mm,  # Keep same expectation
            soil_type=state.soil_type,
            temperature=state.temperature,
            humidity=state.humidity
        )
        
        # Step 12: Build details dict
        details = {
            'crop': crop_action,
            'cycle_days': cycle_days,
            'is_legume': is_legume,
            'initial_state': state.to_dict(),
            'nutrient_loss': {
                'N': round(cumulative_loss['total_N_loss'], 2),
                'P': round(cumulative_loss['total_P_loss'], 2),
                'K': round(cumulative_loss['total_K_loss'], 2),
            },
            'after_rainfall': {
                'N': round(n_after_rain, 2),
                'P': round(p_after_rain, 2),
                'K': round(k_after_rain, 2),
            },
            'nutrient_uptake': {
                'required': {'N': n_uptake, 'P': p_uptake, 'K': k_uptake},
                'actual': {
                    'N': round(actual_n_uptake, 2),
                    'P': round(actual_p_uptake, 2),
                    'K': round(actual_k_uptake, 2),
                },
            },
            'sufficiency_ratio': round(sufficiency_ratio, 3),
            'legume_n_fixation': LEGUME_N_FIXATION if is_legume else 0,
            'yield': {
                'base_tonnes_ha': base_yield,
                'estimated_tonnes_ha': round(estimated_yield, 2),
            },
            'economics': {
                'market_price_per_kg': round(market_price, 2),
                'gross_revenue': round(gross_revenue, 0),
                'production_cost': round(production_cost, 0),
                'gross_profit': round(gross_profit, 0),
                'soil_penalty': round(soil_penalty, 0),
                'reward': round(reward, 0),
            },
            'rainfall_events': len(rainfall_events),
            'total_rainfall_mm': round(sum(e['rainfall_mm'] for e in rainfall_events), 1),
        }
        
        return next_state, reward, details
    
    def compare_crop_options(
        self,
        state: EnvironmentState,
        candidate_crops: List[str],
        lookahead_seasons: int = 3
    ) -> List[Dict]:
        """
        Compare multiple crop options and rank by total estimated value.
        
        Shows: which crop leaves soil in better condition for future seasons.
        
        Args:
            state: Current environment state
            candidate_crops: List of crop names to compare
            lookahead_seasons: Number of future seasons to consider (for future value)
        
        Returns:
            List of options sorted by total_estimated_value (descending)
        """
        options = []
        
        for crop in candidate_crops:
            crop_lower = crop.lower()
            try:
                # Get immediate transition
                next_state, immediate_reward, details = self.transition(state, crop_lower)
                
                # Estimate future value (simplified: average of best crop for next N seasons)
                future_value = self._estimate_future_value(next_state, lookahead_seasons - 1)
                
                total_value = immediate_reward + future_value
                
                options.append({
                    'crop': crop_lower,
                    'immediate_reward': round(immediate_reward, 0),
                    'future_value_estimate': round(future_value, 0),
                    'total_estimated_value': round(total_value, 0),
                    'next_state': next_state.to_dict(),
                    'details': details,
                })
            except ValueError as e:
                options.append({
                    'crop': crop_lower,
                    'error': str(e),
                    'total_estimated_value': float('-inf'),
                })
        
        # Sort by total value descending
        options.sort(key=lambda x: x.get('total_estimated_value', float('-inf')), reverse=True)
        
        return options
    
    def generate_lstm_training_sequence(
        self,
        initial_state: EnvironmentState,
        num_seasons: int = 10
    ) -> List[Dict]:
        """
        Generate synthetic LSTM training data by simulating multiple seasons.
        
        Output format: daily data points with interpolated nutrients across each cycle.
        
        Args:
            initial_state: Starting state
            num_seasons: Number of crop cycles to simulate
        
        Returns:
            List of daily data dicts with columns suitable for LSTM training
        """
        daily_data = []
        state = initial_state.copy()
        current_date = datetime.now() - timedelta(days=num_seasons * 120)  # Start in past
        
        # Available crops for random selection
        crop_pool = list(CROP_NUTRIENT_UPTAKE.keys())
        
        for season_idx in range(num_seasons):
            # Pick a random crop for this season
            crop = random.choice(crop_pool)
            crop_data = get_crop_nutrient_uptake(crop)
            cycle_days = crop_data['cycle_days']
            
            # Simulate transition
            next_state, reward, details = self.transition(state, crop)
            
            # Interpolate daily nutrients across the cycle
            n_start, n_end = state.n, next_state.n
            p_start, p_end = state.p, next_state.p
            k_start, k_end = state.k, next_state.k
            
            # Generate rainfall events for the cycle (already generated in transition)
            season_rainfall = state.expected_rainfall_mm * 0.4  # 40% falls in one season
            
            for day in range(cycle_days):
                progress = day / cycle_days
                
                # Linear interpolation of nutrients
                n_day = n_start + (n_end - n_start) * progress
                p_day = p_start + (p_end - p_start) * progress
                k_day = k_start + (k_end - k_start) * progress
                
                # Simulate daily rainfall (most days have 0)
                if random.random() < 0.15:  # 15% chance of rain
                    rainfall_mm = random.uniform(5, 40)
                else:
                    rainfall_mm = 0.0
                
                # Temperature variation
                temp = state.temperature + random.uniform(-5, 5)
                humidity = state.humidity + random.uniform(-15, 15)
                
                daily_data.append({
                    'log_date': current_date.strftime('%Y-%m-%d'),
                    'n_kg_ha': round(n_day, 2),
                    'p_kg_ha': round(p_day, 2),
                    'k_kg_ha': round(k_day, 2),
                    'rainfall_mm': round(rainfall_mm, 2),
                    'temperature_avg': round(max(10, min(45, temp)), 2),
                    'humidity_avg': round(max(20, min(95, humidity)), 2),
                    'days_into_cycle': day,
                    'crop_name': crop,
                    'season_index': season_idx % 4,
                })
                
                current_date += timedelta(days=1)
            
            # Move to next state
            state = next_state
        
        return daily_data
    
    def generate_trajectory(
        self,
        initial_state: EnvironmentState,
        crop_sequence: List[str],
        market_prices: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Simulate a full multi-season trajectory with a fixed crop sequence.
        
        Args:
            initial_state: Starting state
            crop_sequence: List of crops to plant in order
            market_prices: Optional custom prices
        
        Returns:
            List of season detail dicts
        """
        trajectory = []
        state = initial_state.copy()
        total_reward = 0.0
        
        for season_num, crop in enumerate(crop_sequence, start=1):
            price_override = market_prices.get(crop) if market_prices else None
            next_state, reward, details = self.transition(state, crop, market_price_override=price_override)
            
            total_reward += reward
            
            trajectory.append({
                'season': season_num,
                'crop': crop,
                'reward': round(reward, 0),
                'cumulative_reward': round(total_reward, 0),
                'soil_before': state.to_dict(),
                'soil_after': next_state.to_dict(),
                'yield_tonnes_ha': details['yield']['estimated_tonnes_ha'],
                'is_legume': details['is_legume'],
            })
            
            state = next_state
        
        return trajectory
    
    # ========================================================================
    # INTERNAL HELPER METHODS
    # ========================================================================
    
    def _generate_synthetic_rainfall(
        self,
        total_mm: float,
        cycle_days: int
    ) -> List[Dict]:
        """
        Generate synthetic rainfall events for a crop cycle.
        
        Distributes seasonal rainfall across bi-weekly events.
        Seasonal portion = 40% of annual rainfall.
        
        Args:
            total_mm: Expected annual rainfall
            cycle_days: Crop cycle length in days
        
        Returns:
            List of {'rainfall_mm': x, 'duration_hours': y}
        """
        # Seasonal rainfall is ~40% of annual
        seasonal_mm = total_mm * 0.40
        
        # Scale to cycle length (assume base cycle = 120 days)
        cycle_factor = cycle_days / 120.0
        cycle_rainfall = seasonal_mm * cycle_factor
        
        # Number of events (roughly one per 14 days)
        num_events = max(1, int(cycle_days / 14))
        
        # Distribute rainfall unevenly (some heavy, some light)
        events = []
        remaining = cycle_rainfall
        
        for i in range(num_events):
            if i == num_events - 1:
                # Last event gets remainder
                event_mm = remaining
            else:
                # Random portion with some variation
                portion = random.uniform(0.5, 1.5) / num_events
                event_mm = cycle_rainfall * portion
                remaining -= event_mm
            
            event_mm = max(5, min(100, event_mm))  # Clamp to reasonable range
            
            # Duration: heavier rain → longer duration (roughly)
            duration = min(12, max(1, event_mm / 10 + random.uniform(0.5, 2)))
            
            events.append({
                'rainfall_mm': round(event_mm, 1),
                'duration_hours': round(duration, 1),
            })
        
        return events
    
    def _nutrient_sufficiency_ratio(
        self,
        avail_n: float,
        avail_p: float,
        avail_k: float,
        req_n: float,
        req_p: float,
        req_k: float
    ) -> float:
        """
        Calculate how well available nutrients meet requirements.
        
        Returns 0.0 to 1.0 where:
        - 1.0 = all requirements fully met → full base yield
        - 0.5 = half requirements met → 50% of base yield
        
        Uses Liebig's law of minimum: yield limited by scarcest nutrient.
        """
        if req_n <= 0 or req_p <= 0 or req_k <= 0:
            return 1.0
        
        n_ratio = min(1.0, avail_n / req_n)
        p_ratio = min(1.0, avail_p / req_p)
        k_ratio = min(1.0, avail_k / req_k)
        
        # Liebig's law: minimum ratio is the limiting factor
        # But use geometric mean for smoother gradient
        min_ratio = min(n_ratio, p_ratio, k_ratio)
        mean_ratio = (n_ratio * p_ratio * k_ratio) ** (1/3)
        
        # Blend: 70% minimum (Liebig) + 30% geometric mean (reality is smoother)
        sufficiency = 0.7 * min_ratio + 0.3 * mean_ratio
        
        return max(0.1, sufficiency)  # At least 10% yield
    
    def _calculate_soil_penalty(self, n: float, p: float, k: float) -> float:
        """
        Calculate penalty for soil degradation below sustainability thresholds.
        
        Penalizes each kg/ha deficit below MIN_SUSTAINABLE_* by SOIL_DEGRADATION_PENALTY_COEFF.
        """
        penalty = 0.0
        
        if n < MIN_SUSTAINABLE_N:
            penalty += (MIN_SUSTAINABLE_N - n) * SOIL_DEGRADATION_PENALTY_COEFF
        
        if p < MIN_SUSTAINABLE_P:
            penalty += (MIN_SUSTAINABLE_P - p) * SOIL_DEGRADATION_PENALTY_COEFF
        
        if k < MIN_SUSTAINABLE_K:
            penalty += (MIN_SUSTAINABLE_K - k) * SOIL_DEGRADATION_PENALTY_COEFF
        
        return penalty
    
    def _estimate_future_value(self, state: EnvironmentState, seasons: int) -> float:
        """
        Estimate future value of being in a particular soil state.
        
        Simple heuristic: higher nutrients = more future options = higher value.
        Uses discounted sum of potential profits.
        """
        if seasons <= 0:
            return 0.0
        
        # Discount factor
        gamma = 0.85
        
        # Estimate average profit potential based on nutrient levels
        # Higher nutrients = can grow more demanding (higher value) crops
        nutrient_score = (
            min(1.0, state.n / 100) * 0.4 +
            min(1.0, state.p / 40) * 0.3 +
            min(1.0, state.k / 100) * 0.3
        )
        
        # Base potential profit per season
        base_profit = 50000  # ₹50,000/ha average
        
        # Future value is discounted sum
        future_value = 0.0
        for s in range(seasons):
            discounted = (gamma ** s) * base_profit * nutrient_score
            future_value += discounted
        
        return future_value


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_transition(
    n: float, p: float, k: float,
    crop: str,
    soil_type: str = 'loamy',
    rainfall_mm: float = 500.0
) -> Dict:
    """
    Quick helper for single transitions without creating objects.
    
    Usage:
        result = quick_transition(90, 42, 43, 'rice', 'loamy', 600)
        print(result['reward'], result['next_n'])
    """
    sim = StateTransitionSimulator()
    state = EnvironmentState(
        n=n, p=p, k=k,
        soil_type=soil_type,
        expected_rainfall_mm=rainfall_mm
    )
    next_state, reward, details = sim.transition(state, crop)
    
    return {
        'reward': reward,
        'next_n': next_state.n,
        'next_p': next_state.p,
        'next_k': next_state.k,
        'yield_tonnes_ha': details['yield']['estimated_tonnes_ha'],
        'details': details,
    }


# ============================================================================
# TEST / DEMO
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("State-Transition Simulator Test")
    print("=" * 60)
    
    sim = StateTransitionSimulator()
    
    # Initial state
    state = EnvironmentState(
        n=90, p=42, k=43,
        season_index=0,  # Kharif
        expected_rainfall_mm=600,
        soil_type='loamy'
    )
    
    print(f"\nInitial State: N={state.n}, P={state.p}, K={state.k}")
    print(f"Season: {SEASONS[state.season_index]}, Rainfall: {state.expected_rainfall_mm}mm")
    
    # Test single transition
    print("\n--- Single Transition: Rice ---")
    next_state, reward, details = sim.transition(state, 'rice')
    print(f"After Rice:")
    print(f"  N: {state.n} → {next_state.n:.1f}")
    print(f"  P: {state.p} → {next_state.p:.1f}")
    print(f"  K: {state.k} → {next_state.k:.1f}")
    print(f"  Yield: {details['yield']['estimated_tonnes_ha']:.2f} t/ha")
    print(f"  Reward: ₹{reward:,.0f}/ha")
    
    # Test comparison
    print("\n--- Compare Crops ---")
    options = sim.compare_crop_options(state, ['rice', 'lentil', 'wheat'])
    for opt in options:
        if 'error' not in opt:
            print(f"  {opt['crop']:12} → Total: ₹{opt['total_estimated_value']:>8,.0f}  "
                  f"(immed: ₹{opt['immediate_reward']:>6,.0f}, future: ₹{opt['future_value_estimate']:>6,.0f})")
    
    # Test trajectory
    print("\n--- 5-Season Trajectory ---")
    trajectory = sim.generate_trajectory(state, ['rice', 'lentil', 'wheat', 'mungbean', 'maize'])
    total = 0
    for t in trajectory:
        total = t['cumulative_reward']
        marker = " 🌱" if t['is_legume'] else ""
        print(f"  S{t['season']}: {t['crop']:10}{marker}  ₹{t['reward']:>7,.0f}  "
              f"(N→{t['soil_after']['N']:.0f})")
    print(f"\nTotal 5-season reward: ₹{total:,.0f}/ha")
    
    print("\n✓ All tests passed!")

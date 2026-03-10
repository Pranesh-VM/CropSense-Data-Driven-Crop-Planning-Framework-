"""
Q-Learning Agent for CropSense Phase 3

Learns optimal crop rotation policies over multiple seasons using reinforcement learning.
Uses StateTransitionSimulator as the environment for state transitions.

State space: Discretised (N_bin × P_bin × K_bin × season) = 5×5×5×4 = 500 states
Action space: 22 crop choices
Q-table shape: (5, 5, 5, 4, 22) = 11,000 entries — small and fast

Algorithm: Standard Bellman Q-update with ε-greedy exploration
  Q(s,a) ← Q(s,a) + α * [r + γ * max_a' Q(s',a') - Q(s,a)]

Hyperparameters:
  - α (learning_rate): 0.1
  - γ (discount_factor): 0.9
  - ε (epsilon): 1.0 → 0.05 with 0.995 decay per episode
"""

import os
import random
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    import joblib
except ImportError:
    joblib = None

from src.models.state_transition_simulator import (
    EnvironmentState,
    StateTransitionSimulator,
    DEFAULT_MARKET_PRICES,
    SEASONS
)


# ============================================================================
# DISCRETIZATION BINS (must match exactly as specified)
# ============================================================================

# Nitrogen bins: [0-30), [30-60), [60-90), [90-120), [120+)
N_BINS = [0, 30, 60, 90, 120, 999]    # 5 bins (indices 0-4)

# Phosphorus bins: [0-10), [10-20), [20-35), [35-50), [50+)
P_BINS = [0, 10, 20, 35, 50, 999]     # 5 bins (indices 0-4)

# Potassium bins: [0-30), [30-50), [50-80), [80-120), [120+)
K_BINS = [0, 30, 50, 80, 120, 999]    # 5 bins (indices 0-4)

# Season bins: 4 (kharif=0, rabi=1, zaid=2, annual=3)
SEASON_BINS = 4

# Number of bins for each dimension
N_NUM_BINS = len(N_BINS) - 1   # 5
P_NUM_BINS = len(P_BINS) - 1   # 5
K_NUM_BINS = len(K_BINS) - 1   # 5

# Default crop pool (all 22 crops from the database)
DEFAULT_CROP_POOL = list(DEFAULT_MARKET_PRICES.keys())


# ============================================================================
# Q-LEARNING AGENT
# ============================================================================

class QLearningAgent:
    """
    Q-Learning agent for learning optimal crop rotation sequences.
    
    Uses a discretised state space and tabular Q-learning to find
    policies that maximise long-term profit while maintaining soil health.
    
    Usage:
        agent = QLearningAgent(crop_pool=['rice', 'wheat', 'lentil', 'maize'])
        
        state = EnvironmentState(n=90, p=42, k=43, season_index=0,
                                 expected_rainfall_mm=600, soil_type='loamy')
        
        # Train for 1000 episodes
        agent.train(state, num_episodes=1000, seasons_per_episode=5)
        
        # Get optimal rotation plan
        plan = agent.get_optimal_sequence(state, num_seasons=5)
        print(plan['sequence'])  # ['rice', 'lentil', 'wheat', ...]
        
        # Save trained agent
        agent.save('models/q_agent.pkl')
    """
    
    def __init__(
        self,
        crop_pool: Optional[List[str]] = None,
        learning_rate: float = 0.1,      # α
        discount_factor: float = 0.9,    # γ
        epsilon: float = 1.0,            # Start fully random
        epsilon_decay: float = 0.995,    # Decay per episode
        epsilon_min: float = 0.05        # Minimum exploration
    ):
        """
        Initialize the Q-Learning agent.
        
        Args:
            crop_pool: List of crops to consider. Defaults to all 22 crops.
            learning_rate: α — step size for Q updates (default: 0.1)
            discount_factor: γ — importance of future rewards (default: 0.9)
            epsilon: Initial exploration rate (default: 1.0)
            epsilon_decay: Decay factor per episode (default: 0.995)
            epsilon_min: Minimum exploration rate (default: 0.05)
        """
        # Hyperparameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Crop pool
        if crop_pool is None:
            self.crop_pool = DEFAULT_CROP_POOL.copy()
        else:
            self.crop_pool = [c.lower() for c in crop_pool]
        
        self.num_actions = len(self.crop_pool)
        
        # Build crop index mappings
        self.crop_to_idx = {crop: idx for idx, crop in enumerate(self.crop_pool)}
        self.idx_to_crop = {idx: crop for idx, crop in enumerate(self.crop_pool)}
        
        # Initialize Q-table with zeros
        # Shape: (N_bins, P_bins, K_bins, season_bins, num_crops)
        # Size: 5 × 5 × 5 × 4 × len(crop_pool)
        self.q_table = np.zeros(
            (N_NUM_BINS, P_NUM_BINS, K_NUM_BINS, SEASON_BINS, self.num_actions),
            dtype=np.float32
        )
        
        # State transition simulator (the "environment")
        self.simulator = StateTransitionSimulator()
        
        # Training statistics
        self.training_history: List[Dict] = []
        self.episodes_trained = 0
    
    def _state_to_bins(self, state: EnvironmentState) -> Tuple[int, int, int, int]:
        """
        Convert continuous state to discrete bin indices.
        
        Uses np.digitize() to map N, P, K values to bins.
        
        Args:
            state: EnvironmentState with continuous N, P, K values
        
        Returns:
            Tuple of (n_bin, p_bin, k_bin, season_bin) indices
        """
        # np.digitize returns 1-indexed bins, subtract 1 for 0-indexed
        # Clip to valid range [0, num_bins-1]
        n_bin = min(np.digitize(state.n, N_BINS[1:]), N_NUM_BINS - 1)
        p_bin = min(np.digitize(state.p, P_BINS[1:]), P_NUM_BINS - 1)
        k_bin = min(np.digitize(state.k, K_BINS[1:]), K_NUM_BINS - 1)
        
        # Season is already discrete
        season_bin = state.season_index % SEASON_BINS
        
        return (n_bin, p_bin, k_bin, season_bin)
    
    def _choose_action(self, state: EnvironmentState, greedy: bool = False) -> str:
        """
        Choose action using ε-greedy policy.
        
        With probability ε: random action (exploration)
        With probability 1-ε: best Q-value action (exploitation)
        
        Args:
            state: Current environment state
            greedy: If True, always choose best action (ε=0)
        
        Returns:
            Crop name to plant
        """
        if not greedy and random.random() < self.epsilon:
            # Exploration: random crop
            return random.choice(self.crop_pool)
        else:
            # Exploitation: best Q-value
            bins = self._state_to_bins(state)
            q_values = self.q_table[bins[0], bins[1], bins[2], bins[3], :]
            
            # If multiple actions have same max Q, choose randomly among them
            max_q = np.max(q_values)
            best_actions = np.where(q_values == max_q)[0]
            action_idx = random.choice(best_actions)
            
            return self.idx_to_crop[action_idx]
    
    def _get_q_value(self, state: EnvironmentState, action: str) -> float:
        """Get Q-value for a state-action pair."""
        bins = self._state_to_bins(state)
        action_idx = self.crop_to_idx[action]
        return self.q_table[bins[0], bins[1], bins[2], bins[3], action_idx]
    
    def _update_q_table(
        self,
        state: EnvironmentState,
        action: str,
        reward: float,
        next_state: EnvironmentState
    ):
        """
        Update Q-table using Bellman equation.
        
        Q(s,a) ← Q(s,a) + α * [r + γ * max_a' Q(s',a') - Q(s,a)]
        
        Args:
            state: Current state
            action: Action taken (crop name)
            reward: Immediate reward received
            next_state: Resulting state after action
        """
        # Get current bin indices
        bins = self._state_to_bins(state)
        action_idx = self.crop_to_idx[action]
        
        # Current Q-value
        current_q = self.q_table[bins[0], bins[1], bins[2], bins[3], action_idx]
        
        # Max future Q-value
        next_bins = self._state_to_bins(next_state)
        max_next_q = np.max(self.q_table[next_bins[0], next_bins[1], next_bins[2], next_bins[3], :])
        
        # Bellman update
        # Q(s,a) = Q(s,a) + α * (r + γ * max Q(s',a') - Q(s,a))
        td_target = reward + self.discount_factor * max_next_q
        td_error = td_target - current_q
        new_q = current_q + self.learning_rate * td_error
        
        # Update Q-table
        self.q_table[bins[0], bins[1], bins[2], bins[3], action_idx] = new_q
    
    def _randomize_state(self, base_state: EnvironmentState, noise_std: float = 10.0) -> EnvironmentState:
        """
        Add Gaussian noise to state for training generalisation.
        
        Args:
            base_state: Base state to randomize
            noise_std: Standard deviation of noise to add
        
        Returns:
            New state with randomized N, P, K values
        """
        return EnvironmentState(
            n=max(5, base_state.n + random.gauss(0, noise_std)),
            p=max(5, base_state.p + random.gauss(0, noise_std * 0.5)),
            k=max(5, base_state.k + random.gauss(0, noise_std)),
            season_index=random.randint(0, 3),  # Random starting season
            expected_rainfall_mm=base_state.expected_rainfall_mm + random.gauss(0, 50),
            soil_type=base_state.soil_type,
            temperature=base_state.temperature + random.gauss(0, 2),
            humidity=base_state.humidity + random.gauss(0, 5)
        )
    
    def train(
        self,
        initial_state: EnvironmentState,
        num_episodes: int = 1000,
        seasons_per_episode: int = 5,
        verbose: bool = True,
        print_every: int = 200
    ) -> Dict:
        """
        Train the Q-Learning agent.
        
        For each episode:
          1. Randomise starting state (±noise on N/P/K) for generalisation
          2. For each season:
             a. Choose action (ε-greedy)
             b. Simulate transition → next_state, reward
             c. Update Q-table using Bellman equation
             d. Move to next_state
          3. Decay ε
        
        Args:
            initial_state: Base starting state (will be randomized)
            num_episodes: Number of training episodes (default: 1000)
            seasons_per_episode: Seasons per episode (default: 5)
            verbose: Print progress if True
            print_every: Print every N episodes (default: 200)
        
        Returns:
            Training statistics dictionary
        """
        episode_rewards = []
        
        for episode in range(1, num_episodes + 1):
            # Randomize starting state for generalisation
            state = self._randomize_state(initial_state)
            
            episode_reward = 0.0
            
            for season in range(seasons_per_episode):
                # Choose action (ε-greedy)
                action = self._choose_action(state)
                
                # Execute action in simulator
                try:
                    next_state, reward, details = self.simulator.transition(state, action)
                    
                    # Scale reward for Q-learning (divide by 1000 for numerical stability)
                    scaled_reward = reward / 1000.0
                    
                    # Update Q-table
                    self._update_q_table(state, action, scaled_reward, next_state)
                    
                    episode_reward += reward
                    state = next_state
                    
                except Exception as e:
                    # Skip invalid transitions
                    if verbose and episode == 1:
                        print(f"Warning: Transition failed for {action}: {e}")
                    continue
            
            episode_rewards.append(episode_reward)
            
            # Decay epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
                self.epsilon = max(self.epsilon, self.epsilon_min)
            
            # Print progress
            if verbose and (episode % print_every == 0 or episode == num_episodes):
                avg_reward = np.mean(episode_rewards[-print_every:])
                print(f"Episode {episode}/{num_episodes} | "
                      f"Avg Reward: ₹{avg_reward:,.0f} | "
                      f"ε={self.epsilon:.3f}")
        
        self.episodes_trained += num_episodes
        
        # Compute training statistics
        stats = {
            'episodes_trained': self.episodes_trained,
            'total_episodes': num_episodes,
            'final_epsilon': self.epsilon,
            'avg_reward_last_100': np.mean(episode_rewards[-100:]) if len(episode_rewards) >= 100 else np.mean(episode_rewards),
            'max_reward': max(episode_rewards),
            'q_table_nonzero': np.count_nonzero(self.q_table),
            'q_table_shape': self.q_table.shape
        }
        
        self.training_history.append(stats)
        
        if verbose:
            print(f"\n✓ Training complete!")
            print(f"  Episodes: {self.episodes_trained}")
            print(f"  Final ε: {self.epsilon:.4f}")
            print(f"  Avg reward (last 100): ₹{stats['avg_reward_last_100']:,.0f}")
            print(f"  Q-table non-zero entries: {stats['q_table_nonzero']}")
        
        return stats
    
    def get_optimal_sequence(
        self,
        initial_state: EnvironmentState,
        num_seasons: int = 5
    ) -> Dict:
        """
        Get optimal crop rotation sequence using greedy policy.
        
        Runs the trained policy with ε=0 (always choose best action).
        
        Args:
            initial_state: Starting soil/environment state
            num_seasons: Number of seasons to plan (default: 5)
        
        Returns:
            Dictionary with:
                - sequence: List of crop names
                - total_reward: Sum of all rewards (₹/ha)
                - avg_reward_per_season: Mean reward per season
                - season_details: List of per-season breakdown
                - final_soil_state: Final N/P/K values
        """
        state = initial_state.copy()
        sequence: List[str] = []
        season_details: List[Dict] = []
        total_reward = 0.0
        
        for season_num in range(1, num_seasons + 1):
            # Choose best action (greedy)
            action = self._choose_action(state, greedy=True)
            
            # Get Q-value for this action
            q_value = self._get_q_value(state, action)
            
            # Execute action
            try:
                next_state, reward, details = self.simulator.transition(state, action)
            except Exception as e:
                # If transition fails, skip this season
                print(f"Warning: Transition failed for {action} in season {season_num}: {e}")
                continue
            
            sequence.append(action)
            total_reward += reward
            
            season_details.append({
                'season': season_num,
                'season_name': SEASONS[state.season_index % len(SEASONS)],
                'crop': action,
                'reward': round(reward, 2),
                'q_value': round(float(q_value * 1000), 2),  # Scale back up
                'soil_before': {
                    'N': round(state.n, 2),
                    'P': round(state.p, 2),
                    'K': round(state.k, 2)
                },
                'soil_after': {
                    'N': round(next_state.n, 2),
                    'P': round(next_state.p, 2),
                    'K': round(next_state.k, 2)
                },
                'yield_kg_ha': details.get('yield_kg_ha', 0),
                'profit_per_ha': details.get('profit_per_ha', reward)
            })
            
            state = next_state
        
        avg_reward = total_reward / num_seasons if num_seasons > 0 else 0.0
        
        return {
            'sequence': sequence,
            'total_reward': round(total_reward, 2),
            'avg_reward_per_season': round(avg_reward, 2),
            'season_details': season_details,
            'final_soil_state': {
                'N': round(state.n, 2),
                'P': round(state.p, 2),
                'K': round(state.k, 2)
            },
            'episodes_trained': self.episodes_trained,
            'current_epsilon': round(self.epsilon, 4)
        }
    
    def get_action_values(self, state: EnvironmentState) -> Dict[str, float]:
        """
        Get Q-values for all actions in a given state.
        
        Useful for visualising the learned policy.
        
        Args:
            state: Environment state
        
        Returns:
            Dictionary mapping crop names to Q-values
        """
        bins = self._state_to_bins(state)
        q_values = self.q_table[bins[0], bins[1], bins[2], bins[3], :]
        
        # Scale back to original reward scale
        return {
            self.idx_to_crop[i]: round(float(q_values[i] * 1000), 2)
            for i in range(self.num_actions)
        }
    
    def save(self, path: str = 'models/q_agent.pkl'):
        """
        Save trained agent to disk.
        
        Saves Q-table, crop pool, and current hyperparameters.
        
        Args:
            path: File path for saving (default: 'models/q_agent.pkl')
        """
        if joblib is None:
            raise ImportError("joblib is required for saving. Install with: pip install joblib")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        data = {
            'q_table': self.q_table,
            'crop_pool': self.crop_pool,
            'crop_to_idx': self.crop_to_idx,
            'idx_to_crop': self.idx_to_crop,
            'epsilon': self.epsilon,
            'epsilon_min': self.epsilon_min,
            'epsilon_decay': self.epsilon_decay,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'episodes_trained': self.episodes_trained,
            'training_history': self.training_history
        }
        
        joblib.dump(data, path)
        print(f"✓ Agent saved to {path}")
    
    def load(self, path: str = 'models/q_agent.pkl'):
        """
        Load trained agent from disk.
        
        Args:
            path: File path to load from
        """
        if joblib is None:
            raise ImportError("joblib is required for loading. Install with: pip install joblib")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        data = joblib.load(path)
        
        self.q_table = data['q_table']
        self.crop_pool = data['crop_pool']
        self.crop_to_idx = data['crop_to_idx']
        self.idx_to_crop = data['idx_to_crop']
        self.epsilon = data.get('epsilon', self.epsilon_min)
        self.epsilon_min = data.get('epsilon_min', 0.05)
        self.epsilon_decay = data.get('epsilon_decay', 0.995)
        self.learning_rate = data.get('learning_rate', 0.1)
        self.discount_factor = data.get('discount_factor', 0.9)
        self.episodes_trained = data.get('episodes_trained', 0)
        self.training_history = data.get('training_history', [])
        self.num_actions = len(self.crop_pool)
        
        print(f"✓ Agent loaded from {path}")
        print(f"  Episodes trained: {self.episodes_trained}")
        print(f"  Crop pool: {len(self.crop_pool)} crops")
    
    def get_status(self) -> Dict:
        """
        Get current agent status.
        
        Returns:
            Status dictionary with training info
        """
        return {
            'trained': self.episodes_trained > 0,
            'episodes_trained': self.episodes_trained,
            'epsilon': round(self.epsilon, 4),
            'epsilon_min': self.epsilon_min,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'crop_pool_size': len(self.crop_pool),
            'q_table_shape': list(self.q_table.shape),
            'q_table_nonzero': int(np.count_nonzero(self.q_table)),
            'total_states': N_NUM_BINS * P_NUM_BINS * K_NUM_BINS * SEASON_BINS
        }


# ============================================================================
# TEST SCRIPT
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Q-Learning Agent Test")
    print("=" * 60)
    
    # Test 1: Initialize agent with subset of crops
    print("\n--- Test 1: Initialize Agent ---")
    agent = QLearningAgent(
        crop_pool=['rice', 'wheat', 'lentil', 'maize', 'mungbean', 'chickpea']
    )
    
    print(f"Crop pool: {agent.crop_pool}")
    print(f"Q-table shape: {agent.q_table.shape}")
    print(f"Total Q-table entries: {agent.q_table.size:,}")
    print(f"Status: {agent.get_status()}")
    
    # Test 2: State discretization
    print("\n--- Test 2: State Discretization ---")
    state = EnvironmentState(
        n=90, p=42, k=43, season_index=0,
        expected_rainfall_mm=600, soil_type='loamy'
    )
    bins = agent._state_to_bins(state)
    print(f"State: N={state.n}, P={state.p}, K={state.k}, season={state.season_index}")
    print(f"Bins: {bins}")
    
    # Test 3: Training (quick test with 300 episodes)
    print("\n--- Test 3: Training (300 episodes) ---")
    stats = agent.train(
        initial_state=state,
        num_episodes=300,
        seasons_per_episode=5,
        verbose=True,
        print_every=100
    )
    
    # Test 4: Get optimal sequence
    print("\n--- Test 4: Optimal Sequence ---")
    plan = agent.get_optimal_sequence(state, num_seasons=5)
    
    print(f"\nOptimal sequence: {plan['sequence']}")
    print(f"Total reward: ₹{plan['total_reward']:,.0f}")
    print(f"Avg reward/season: ₹{plan['avg_reward_per_season']:,.0f}")
    
    print("\nSeason details:")
    for s in plan['season_details']:
        print(f"  Season {s['season']} ({s['season_name']}): "
              f"{s['crop']:12} → ₹{s['reward']:,.0f} | "
              f"Soil after: N={s['soil_after']['N']:.0f}, "
              f"P={s['soil_after']['P']:.0f}, K={s['soil_after']['K']:.0f}")
    
    print(f"\nFinal soil state: {plan['final_soil_state']}")
    
    # Test 5: Action values for a state
    print("\n--- Test 5: Action Values ---")
    action_values = agent.get_action_values(state)
    sorted_actions = sorted(action_values.items(), key=lambda x: x[1], reverse=True)
    print("Top 3 crops by Q-value:")
    for crop, q_val in sorted_actions[:3]:
        print(f"  {crop}: Q={q_val:.2f}")
    
    # Test 6: Save and load
    print("\n--- Test 6: Save/Load ---")
    try:
        test_path = 'models/q_agent_test.pkl'
        agent.save(test_path)
        
        # Load into new agent
        agent2 = QLearningAgent()
        agent2.load(test_path)
        
        # Verify same optimal sequence
        plan2 = agent2.get_optimal_sequence(state, num_seasons=5)
        assert plan2['sequence'] == plan['sequence'], "Sequences don't match after reload!"
        print("✓ Save/Load verified - sequences match")
        
        # Cleanup
        os.remove(test_path)
        print(f"✓ Test file cleaned up")
    except ImportError as e:
        print(f"⚠ Skipping save/load test: {e}")
    
    print("\n" + "=" * 60)
    print("All Q-Learning Agent tests passed!")
    print("=" * 60)

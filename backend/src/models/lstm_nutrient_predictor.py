"""
LSTM Nutrient Predictor

Deep learning model for predicting nutrient depletion patterns.

Key Idea:
- Input: Past 30 days of (rainfall, temperature, humidity, N, P, K)
- Output: Next 7/14/30 days of nutrient levels (N, P, K)
- Learns patterns: rainfall + crop uptake + seasonal effects = nutrient trajectory

Usage:
    predictor = LSTMNutrientPredictor(lookback_days=30, forecast_days=7)
    data = ts_manager.get_timeseries_for_training(farmer_id=5, crop_name='Wheat')
    history = predictor.train(data, epochs=50)
    predictions = predictor.predict_next_days(recent_data)
"""

import sys
from pathlib import Path
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from datetime import date, timedelta
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

warnings.filterwarnings('ignore')

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠ TensorFlow/Keras not installed. Install with: pip install tensorflow")

from sklearn.preprocessing import MinMaxScaler
import joblib


class LSTMNutrientPredictor:
    """
    LSTM model for nutrient level forecasting.
    
    Architecture:
    - Input: [past_30_days, 6_features]  (rainfall, temp, humidity, N, P, K)
    - LSTM Layer 1: 64 units with dropout
    - LSTM Layer 2: 32 units with dropout
    - Dense: 16 units
    - Output: [forecast_days * 3]  (N, P, K predictions)
    """
    
    def __init__(
        self,
        lookback_days: int = 30,
        forecast_days: int = 7,
        model_path: str = None
    ):
        """
        Initialize LSTM predictor.
        
        Args:
            lookback_days: Input sequence length (default 30 days)
            forecast_days: Prediction horizon (default 7 days ahead)
            model_path: Path to load pre-trained model (optional)
        """
        if not TENSORFLOW_AVAILABLE:
            raise RuntimeError("TensorFlow is required. Install: pip install tensorflow")
        
        self.lookback_days = lookback_days
        self.forecast_days = forecast_days
        self.model = None
        self.scaler = MinMaxScaler()
        self.model_path = model_path
        
        if model_path:
            self.load_model(model_path)
    
    # ============================================================================
    # DATA PREPARATION
    # ============================================================================
    
    def prepare_sequences(
        self,
        df: pd.DataFrame,
        features: list = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert time-series DataFrame into LSTM sequences.
        
        Args:
            df: DataFrame with columns [rainfall_mm, temperature_avg, humidity_avg, 
                                        n_kg_ha, p_kg_ha, k_kg_ha]
            features: Which features to use (default all 6)
        
        Returns:
            X: shape (samples, lookback_days, num_features)
            y: shape (samples, forecast_days * 3) - nutrients only
        
        Example:
            X, y = predictor.prepare_sequences(df)
            print(X.shape)  # (150, 30, 6) - 150 samples, 30 day history, 6 features
            print(y.shape)  # (150, 21) - forecast 7 days * 3 nutrients
        """
        if features is None:
            features = ['rainfall_mm', 'temperature_avg', 'humidity_avg', 
                       'n_kg_ha', 'p_kg_ha', 'k_kg_ha']
        
        # Check for missing columns
        missing = set(features) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        # Handle missing values
        df_clean = df[features].copy()
        df_clean = df_clean.fillna(method='ffill').fillna(method='bfill')
        
        # Normalize
        scaled_data = self.scaler.fit_transform(df_clean)
        
        X, y = [], []
        
        # Create sequences
        for i in range(len(scaled_data) - self.lookback_days - self.forecast_days):
            # Input: past 30 days
            X.append(scaled_data[i:i + self.lookback_days])
            
            # Output: next 7 days for N, P, K (indices 3, 4, 5)
            future_data = scaled_data[i + self.lookback_days:
                                     i + self.lookback_days + self.forecast_days]
            
            # Extract only nutrient predictions (columns 3, 4, 5)
            y.append(future_data[:, [3, 4, 5]].flatten())
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"✓ Prepared sequences:")
        print(f"  - Input shape: {X.shape}  (samples, lookback_days, features)")
        print(f"  - Output shape: {y.shape}  (samples, forecast_days * 3 nutrients)")
        
        return X, y
    
    # ============================================================================
    # MODEL TRAINING
    # ============================================================================
    
    def build_model(self):
        """Build LSTM neural network architecture."""
        self.model = Sequential([
            # First LSTM layer
            LSTM(
                64,
                activation='relu',
                input_shape=(self.lookback_days, 6),
                return_sequences=True,
                name='lstm_1'
            ),
            Dropout(0.2),
            
            # Second LSTM layer
            LSTM(32, activation='relu', return_sequences=False, name='lstm_2'),
            Dropout(0.2),
            
            # Dense layers
            Dense(16, activation='relu', name='dense_1'),
            Dropout(0.1),
            
            # Output layer: predict N, P, K for next 7/14/30 days
            Dense(self.forecast_days * 3, name='output')
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        print("✓ LSTM model built:")
        self.model.summary()
    
    def train(
        self,
        df: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1
    ) -> Dict:
        """
        Train LSTM model on historical data.
        
        Args:
            df: DataFrame with columns [rainfall_mm, temperature_avg, humidity_avg, 
                                        n_kg_ha, p_kg_ha, k_kg_ha]
            epochs: Number of training iterations
            batch_size: Batch size for training
            validation_split: % of data to use for validation
            verbose: Print training progress
        
        Returns:
            Training history and metrics
        
        Example:
            data = ts_manager.get_timeseries_for_training(
                farmer_id=5, crop_name='Wheat', days_back=365
            )
            history = predictor.train(data, epochs=100)
            print(f"Final Loss: {history['final_loss']}")
        
        Raises:
            ValueError: If insufficient data
        """
        min_samples = self.lookback_days + self.forecast_days + 10
        if len(df) < min_samples:
            raise ValueError(
                f"Need at least {min_samples} data points, "
                f"got {len(df)}. Ensure you have 2+ months of history."
            )
        
        print(f"\n{'='*60}")
        print(f"Training LSTM Model")
        print(f"{'='*60}")
        print(f"Data points: {len(df)}")
        print(f"Lookback: {self.lookback_days} days")
        print(f"Forecast: {self.forecast_days} days")
        print(f"Training samples: {len(df) - self.lookback_days - self.forecast_days}")
        
        # Prepare sequences
        X, y = self.prepare_sequences(df)
        
        # Build model
        self.build_model()
        
        # Early stopping to prevent overfitting
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        )
        
        # Train
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=verbose
        )
        
        # Extract final metrics
        final_loss = history.history['loss'][-1]
        final_val_loss = history.history['val_loss'][-1]
        
        print(f"\n{'='*60}")
        print(f"Training Complete!")
        print(f"Final Training Loss: {final_loss:.6f}")
        print(f"Final Validation Loss: {final_val_loss:.6f}")
        print(f"{'='*60}\n")
        
        return {
            'history': history.history,
            'final_loss': final_loss,
            'final_val_loss': final_val_loss,
            'epochs_trained': len(history.history['loss'])
        }
    
    # ============================================================================
    # PREDICTION
    # ============================================================================
    
    def predict_next_days(
        self,
        recent_data: pd.DataFrame,
        return_intervals: bool = True
    ) -> Dict:
        """
        Predict nutrient levels for next 7/14/30 days.
        
        Args:
            recent_data: Last 30 days of data (should match lookback_days)
            return_intervals: Include confidence intervals in output
        
        Returns:
            {
                'success': True,
                'forecast_date': '2026-02-18',
                'predictions': [
                    {
                        'days_ahead': 1,
                        'forecast_date': '2026-02-12',
                        'predicted_n': 95.5,
                        'predicted_p': 28.2,
                        'predicted_k': 145.3,
                        'n_confidence': (90, 101),
                        'p_confidence': (25, 31),
                        'k_confidence': (140, 150)
                    },
                    ...
                ]
            }
        
        Example:
            # Get last 30 days from database
            recent_data = ts_manager.get_timeseries_for_training(
                farmer_id=5, crop_name='Wheat', days_back=30
            )
            
            predictions = predictor.predict_next_days(recent_data)
            
            for pred in predictions['predictions']:
                print(f"Day {pred['days_ahead']}: "
                      f"N={pred['predicted_n']:.1f}, "
                      f"P={pred['predicted_p']:.1f}, "
                      f"K={pred['predicted_k']:.1f}")
        """
        if self.model is None:
            return {'success': False, 'error': 'Model not trained. Call train() first.'}
        
        if len(recent_data) < self.lookback_days:
            return {
                'success': False,
                'error': f'Need {self.lookback_days} days of data, got {len(recent_data)}'
            }
        
        # Prepare input
        features = ['rainfall_mm', 'temperature_avg', 'humidity_avg', 
                   'n_kg_ha', 'p_kg_ha', 'k_kg_ha']
        
        recent_clean = recent_data[features].copy()
        recent_clean = recent_clean.fillna(method='ffill').fillna(method='bfill')
        
        # Normalize using trained scaler
        recent_scaled = self.scaler.transform(recent_clean)
        
        # Ensure we have exactly lookback_days
        X = recent_scaled[-self.lookback_days:].reshape(1, self.lookback_days, 6)
        
        # Predict
        raw_prediction = self.model.predict(X, verbose=0)[0]
        
        # Reshape predictions: [7 days * 3 nutrients] -> [7 days, 3 nutrients]
        pred_nutrients = raw_prediction.reshape(self.forecast_days, 3)
        
        # Inverse transform to get actual nutrient values
        # Create full-feature array for inverse transform
        pred_full = np.zeros((self.forecast_days, 6))
        pred_full[:, [3, 4, 5]] = pred_nutrients  # Put predictions in N, P, K columns
        
        # Fill in recent weather data for context
        pred_full[:, :3] = recent_scaled[-self.forecast_days:, :3]
        
        actual_predictions = self.scaler.inverse_transform(pred_full)
        
        # Build response
        predictions_list = []
        for i in range(self.forecast_days):
            forecast_date = date.today() + timedelta(days=i + 1)
            
            # Basic prediction
            pred_dict = {
                'days_ahead': i + 1,
                'forecast_date': forecast_date.isoformat(),
                'predicted_n': float(np.clip(actual_predictions[i, 3], 0, 999)),
                'predicted_p': float(np.clip(actual_predictions[i, 4], 0, 999)),
                'predicted_k': float(np.clip(actual_predictions[i, 5], 0, 999))
            }
            
            # Add confidence intervals (simple: ±10%)
            if return_intervals:
                pred_dict.update({
                    'n_confidence': (
                        float(actual_predictions[i, 3] * 0.90),
                        float(actual_predictions[i, 3] * 1.10)
                    ),
                    'p_confidence': (
                        float(actual_predictions[i, 4] * 0.90),
                        float(actual_predictions[i, 4] * 1.10)
                    ),
                    'k_confidence': (
                        float(actual_predictions[i, 5] * 0.90),
                        float(actual_predictions[i, 5] * 1.10)
                    )
                })
            
            predictions_list.append(pred_dict)
        
        return {
            'success': True,
            'forecast_start_date': (date.today() + timedelta(days=1)).isoformat(),
            'forecast_days': self.forecast_days,
            'predictions': predictions_list
        }
    
    # ============================================================================
    # MODEL PERSISTENCE
    # ============================================================================
    
    def save_model(self, path: str):
        """
        Save trained model and scaler to disk.
        
        Args:
            path: Directory to save files
        
        Creates:
            - {path}/lstm_nutrient_model.h5
            - {path}/lstm_scaler.pkl
        """
        from pathlib import Path
        Path(path).mkdir(parents=True, exist_ok=True)
        
        if self.model is None:
            raise ValueError("Model not trained. Cannot save.")
        
        model_path = f"{path}/lstm_nutrient_model.h5"
        scaler_path = f"{path}/lstm_scaler.pkl"
        
        self.model.save(model_path)
        joblib.dump(self.scaler, scaler_path)
        
        print(f"✓ Model saved:")
        print(f"  - {model_path}")
        print(f"  - {scaler_path}")
    
    def load_model(self, path: str):
        """
        Load pre-trained model from disk.
        
        Args:
            path: Directory containing model files
        """
        from tensorflow.keras.models import load_model
        
        model_path = f"{path}/lstm_nutrient_model.h5"
        scaler_path = f"{path}/lstm_scaler.pkl"
        
        try:
            self.model = load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            print(f"✓ Model loaded from {path}")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Model files not found in {path}: {e}")

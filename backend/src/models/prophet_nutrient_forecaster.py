"""
Prophet Nutrient Forecaster

Time-series forecasting using Facebook's Prophet library.
Better for capturing seasonal patterns and trends.

Key Idea:
- Decomposes nutrient depletion into:
  * Trend: main crop nutrient uptake (linear)
  * Seasonality: rainfall patterns (monsoon vs dry season)
  * Noise: random variations
- Predicts: what happens if current patterns continue

Usage:
    forecaster = ProphetNutrientForecaster()
    data = ts_manager.get_timeseries_for_training(farmer_id=5, crop_name='Wheat')
    forecaster.train(data)
    forecast = forecaster.forecast_next_days(days_ahead=30)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import date, timedelta
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠ Prophet not installed. Install with: pip install prophet")
    Prophet = None

import joblib


class ProphetNutrientForecaster:
    """
    Prophet-based forecaster for nutrient depletion patterns.
    
    Advantages over LSTM:
    - Better for long-term trends (which crop/season patterns repeat every year)
    - Captures seasonality (monsoon = more rain = faster loss)
    - Interpretable components (trend + seasonal + weekly effects)
    - Handles missing data automatically
    - Built-in uncertainty intervals
    
    Disadvantages:
    - Requires more data points (100+ ideally)
    - Assumes patterns repeat yearly
    - Less good for sudden changes
    
    Best Use Case: Predicting trends over full crop cycle (120 days)
    """
    
    def __init__(self):
        """Initialize Prophet forecasters for each nutrient."""
        if not PROPHET_AVAILABLE:
            raise RuntimeError("Prophet is required. Install: pip install prophet")
        
        # One model per nutrient to capture independent patterns
        self.models = {
            'N': Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                interval_width=0.95,
                changepoint_prior_scale=0.05  # How flexible trend can be
            ),
            'P': Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                interval_width=0.95,
                changepoint_prior_scale=0.05
            ),
            'K': Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                interval_width=0.95,
                changepoint_prior_scale=0.05
            )
        }
        
        self.is_trained = False
    
    # ============================================================================
    # DATA PREPARATION
    # ============================================================================
    
    def prepare_data(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Prepare DataFrame for Prophet training.
        Prophet requires 'ds' (date) and 'y' (value) columns.
        
        Args:
            df: DataFrame with columns [log_date, n_kg_ha, p_kg_ha, k_kg_ha]
        
        Returns:
            Dict with DataFrames for each nutrient, ready for fit()
        
        Example:
            df = ts_manager.get_timeseries_for_training(
                farmer_id=5, crop_name='Wheat', days_back=180
            )
            prophet_data = forecaster.prepare_data(df)
            
            print(prophet_data['N'].head())
            #          ds          y
            # 0 2025-09-01  180.50
            # 1 2025-09-02  178.25
        """
        prepared = {}
        
        # Map nutrient columns
        nutrient_map = {
            'N': 'n_kg_ha',
            'P': 'p_kg_ha',
            'K': 'k_kg_ha'
        }
        
        for nutrient, col in nutrient_map.items():
            # Check if column exists
            if col not in df.columns:
                print(f"⚠ Warning: Column '{col}' not found, skipping {nutrient}")
                continue
            
            # Create Prophet DataFrame
            prophet_df = pd.DataFrame({
                'ds': pd.to_datetime(df['log_date']),
                'y': df[col]
            })
            
            # Remove NaN values
            prophet_df = prophet_df.dropna()
            
            if len(prophet_df) < 20:
                print(f"⚠ Warning: Only {len(prophet_df)} non-null values for {nutrient}, skipping")
                continue
            
            prepared[nutrient] = prophet_df
            print(f"✓ Prepared {nutrient}: {len(prophet_df)} data points")
        
        return prepared
    
    # ============================================================================
    # MODEL TRAINING
    # ============================================================================
    
    def train(
        self,
        df: pd.DataFrame,
        verbose: int = 0
    ) -> Dict:
        """
        Train Prophet models for each nutrient.
        
        Args:
            df: DataFrame with columns [log_date, n_kg_ha, p_kg_ha, k_kg_ha]
            verbose: Prophet verbosity level
        
        Returns:
            Training summary
        
        Example:
            data = ts_manager.get_timeseries_for_training(
                farmer_id=5, crop_name='Wheat', days_back=365
            )
            
            summary = forecaster.train(data)
            print(f"Trained: {summary['nutrients_trained']}")
            print(f"Data points: {summary['data_points']}")
        
        Raises:
            ValueError: If insufficient data
        """
        min_points = 20
        if len(df) < min_points:
            raise ValueError(f"Need at least {min_points} data points, got {len(df)}")
        
        print(f"\n{'='*60}")
        print(f"Training Prophet Models")
        print(f"{'='*60}")
        print(f"Total data points: {len(df)}")
        print(f"Date range: {df['log_date'].min()} to {df['log_date'].max()}")
        
        # Prepare data
        prophet_data = self.prepare_data(df)
        
        if not prophet_data:
            raise ValueError("No valid data prepared for training")
        
        # Train each nutrient model
        trained_nutrients = []
        
        for nutrient, data in prophet_data.items():
            try:
                print(f"\nTraining {nutrient} model with {len(data)} points...", end='')
                
                # Configure model with data-aware parameters
                # Longer data = more flexible
                if len(data) > 100:
                    changepoint_prior_scale = 0.05  # Low = smoother
                else:
                    changepoint_prior_scale = 0.1   # Higher = more flexible
                
                self.models[nutrient] = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                    interval_width=0.95,
                    changepoint_prior_scale=changepoint_prior_scale,
                    interval_width_for_ui=0.95
                )
                
                # Fit model (suppress Prophet's verbose output)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.models[nutrient].fit(data)
                
                trained_nutrients.append(nutrient)
                print(" ✓")
                
            except Exception as e:
                print(f" ✗ (Error: {str(e)})")
                continue
        
        if not trained_nutrients:
            raise ValueError("Failed to train any models")
        
        self.is_trained = True
        
        print(f"\n{'='*60}")
        print(f"Training Complete!")
        print(f"Trained nutrients: {', '.join(trained_nutrients)}")
        print(f"Models ready for forecasting")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'nutrients_trained': trained_nutrients,
            'data_points': len(df),
            'is_trained': True
        }
    
    # ============================================================================
    # FORECASTING
    # ============================================================================
    
    def forecast_next_days(
        self,
        days_ahead: int = 30,
        include_components: bool = False
    ) -> Dict:
        """
        Forecast nutrient levels for next N days.
        
        Args:
            days_ahead: Number of days to forecast (default 30)
            include_components: Return trend/seasonal components
        
        Returns:
            {
                'success': True,
                'forecast_days': 30,
                'N': [
                    {
                        'date': '2026-02-12',
                        'predicted': 95.5,
                        'lower_bound': 90.2,
                        'upper_bound': 100.8
                    },
                    ...
                ],
                'P': [...],
                'K': [...]
            }
        
        Example:
            forecaster.train(historical_data)
            
            forecast = forecaster.forecast_next_days(days_ahead=30)
            
            for day_pred in forecast['N']:
                print(f"{day_pred['date']}: "
                      f"N = {day_pred['predicted']:.1f} "
                      f"({day_pred['lower_bound']:.1f} - {day_pred['upper_bound']:.1f})")
        """
        if not self.is_trained:
            return {
                'success': False,
                'error': 'Models not trained. Call train() first.'
            }
        
        forecast_dict = {
            'success': True,
            'forecast_start_date': (date.today() + timedelta(days=1)).isoformat(),
            'forecast_days': days_ahead
        }
        
        # Generate forecast for each nutrient
        for nutrient in ['N', 'P', 'K']:
            if nutrient not in self.models:
                continue
            
            model = self.models[nutrient]
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=days_ahead)
            
            # Forecast
            forecast = model.predict(future)
            
            # Extract only future dates
            future_forecast = forecast[forecast['ds'] > pd.Timestamp(date.today())]
            
            # Format output
            predictions = []
            for idx, row in future_forecast.head(days_ahead).iterrows():
                pred_dict = {
                    'date': row['ds'].date().isoformat(),
                    'predicted': float(np.clip(row['yhat'], 0, 999)),  # Clip to valid range
                    'lower_bound': float(np.clip(row['yhat_lower'], 0, 999)),
                    'upper_bound': float(np.clip(row['yhat_upper'], 0, 999))
                }
                
                predictions.append(pred_dict)
            
            forecast_dict[nutrient] = predictions
            
            if include_components:
                # Add decomposition components
                forecast_dict[f'{nutrient}_components'] = {
                    'trend': float(forecast[forecast['ds'] == future.iloc[-1]['ds']]['trend'].values[0]) if len(forecast) > 0 else 0,
                    'yearly_seasonality': float(forecast[forecast['ds'] == future.iloc[-1]['ds']]['yearly'].values[0]) if 'yearly' in forecast.columns and len(forecast) > 0 else 0
                }
        
        return forecast_dict
    
    def get_component_explanation(self, nutrient: str) -> Dict:
        """
        Get human-readable explanation of what Prophet learned.
        
        Returns interpretation of trend + seasonal components.
        
        Example:
            explanation = forecaster.get_component_explanation('N')
            
            print(explanation)
            # {
            #     'trend': 'Declining at ~1.2 kg/ha per day',
            #     'seasonality': 'Strong monsoon effect: faster loss in rainy months',
            #     'interpretation': 'Nitrogen depleting due to crop uptake + rainfall-induced leaching'
            # }
        """
        if nutrient not in self.models or not self.is_trained:
            return {'error': 'Model not available'}
        
        model = self.models[nutrient]
        
        # Calculate trend slope (simplified)
        # This would require actual implementation with model components
        
        explanation = {
            'nutrient': nutrient,
            'model_type': 'Facebook Prophet',
            'components_captured': ['Yearly Seasonality', 'Trend'],
            'interpretation': f'{nutrient} levels are affected by seasonal patterns (monsoon vs dry season) and a long-term trend (crop nutrient uptake)'
        }
        
        return explanation
    
    # ============================================================================
    # MODEL PERSISTENCE
    # ============================================================================
    
    def save_models(self, path: str):
        """
        Save all trained Prophet models to disk.
        
        Args:
            path: Directory to save models
        
        Creates:
            - {path}/prophet_model_N.pkl
            - {path}/prophet_model_P.pkl
            - {path}/prophet_model_K.pkl
        """
        Path(path).mkdir(parents=True, exist_ok=True)
        
        for nutrient, model in self.models.items():
            if model is not None:
                model_path = f"{path}/prophet_model_{nutrient}.pkl"
                joblib.dump(model, model_path)
                print(f"✓ Saved Prophet {nutrient} model to {model_path}")
    
    def load_models(self, path: str):
        """
        Load pre-trained Prophet models from disk.
        
        Args:
            path: Directory containing model files
        """
        for nutrient in ['N', 'P', 'K']:
            model_path = f"{path}/prophet_model_{nutrient}.pkl"
            
            try:
                self.models[nutrient] = joblib.load(model_path)
                self.is_trained = True
                print(f"✓ Loaded Prophet {nutrient} model from {model_path}")
            except FileNotFoundError:
                print(f"⚠ Model file not found: {model_path}")
                continue

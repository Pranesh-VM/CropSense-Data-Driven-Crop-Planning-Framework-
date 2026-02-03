"""
Data preprocessing module for Crop Recommendation System.

Handles:
- Loading raw data
- Feature scaling using StandardScaler
- Target encoding using LabelEncoder
- Train-test split with stratification
- Saving/loading preprocessors
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib


class DataPreprocessor:
    """Handle all preprocessing tasks for crop recommendation data."""
    
    def __init__(self, data_path=None, scaler_save_path=None, encoder_save_path=None):
        """
        Initialize preprocessor.
        
        Args:
            data_path: Path to raw CSV file
            scaler_save_path: Path to save/load StandardScaler
            encoder_save_path: Path to save/load LabelEncoder
        """
        if data_path is None:
            # Default path relative to this module
            data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "Crop_recommendation.csv"
        
        if scaler_save_path is None:
            scaler_save_path = Path(__file__).parent.parent.parent / "models" / "scaler.pkl"
        
        if encoder_save_path is None:
            encoder_save_path = Path(__file__).parent.parent.parent / "models" / "label_encoder.pkl"
        
        self.data_path = Path(data_path)
        self.scaler_save_path = Path(scaler_save_path)
        self.encoder_save_path = Path(encoder_save_path)
        
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        self.target_name = "label"
    
    def load_data(self):
        """Load raw data from CSV."""
        df = pd.read_csv(self.data_path)
        
        # Validate schema
        expected_cols = self.feature_names + [self.target_name]
        if not all(col in df.columns for col in expected_cols):
            raise ValueError(f"Data must contain columns: {expected_cols}")
        
        # Ensure correct column order
        df = df[expected_cols]
        
        return df
    
    def preprocess(self, df, fit_encoders=True):
        """
        Apply preprocessing to data.
        
        Args:
            df: Raw dataframe
            fit_encoders: If True, fit new encoders; if False, use existing ones
        
        Returns:
            Tuple of (X_scaled, y_encoded, feature_names)
        """
        X = df[self.feature_names].copy()
        y = df[self.target_name].copy()
        
        # Scale features
        if fit_encoders:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        # Encode target
        if fit_encoders:
            y_encoded = self.label_encoder.fit_transform(y)
        else:
            y_encoded = self.label_encoder.transform(y)
        
        return X_scaled, y_encoded
    
    def split_data(self, X_scaled, y_encoded, test_size=0.2, random_state=42):
        """
        Split data with stratification.
        
        Args:
            X_scaled: Scaled features
            y_encoded: Encoded target
            test_size: Test set proportion
            random_state: Random seed
        
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded,
            test_size=test_size,
            random_state=random_state,
            stratify=y_encoded
        )
        return X_train, X_test, y_train, y_test
    
    def save_encoders(self):
        """Save scaler and label encoder to disk."""
        self.scaler_save_path.parent.mkdir(parents=True, exist_ok=True)
        self.encoder_save_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.scaler, self.scaler_save_path)
        joblib.dump(self.label_encoder, self.encoder_save_path)
        
        return self.scaler_save_path, self.encoder_save_path
    
    def load_encoders(self):
        """Load scaler and label encoder from disk."""
        if not self.scaler_save_path.exists() or not self.encoder_save_path.exists():
            raise FileNotFoundError("Encoder files not found. Run preprocessing first.")
        
        self.scaler = joblib.load(self.scaler_save_path)
        self.label_encoder = joblib.load(self.encoder_save_path)


def preprocess(test_size=0.2, random_state=42):
    """
    Convenience function to run full preprocessing pipeline.
    
    Args:
        test_size: Test set proportion
        random_state: Random seed
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, preprocessor)
    """
    preprocessor = DataPreprocessor()
    
    # Load and preprocess
    df = preprocessor.load_data()
    X_scaled, y_encoded = preprocessor.preprocess(df, fit_encoders=True)
    
    # Split data
    X_train, X_test, y_train, y_test = preprocessor.split_data(
        X_scaled, y_encoded, test_size=test_size, random_state=random_state
    )
    
    # Save encoders
    preprocessor.save_encoders()
    
    return X_train, X_test, y_train, y_test, preprocessor

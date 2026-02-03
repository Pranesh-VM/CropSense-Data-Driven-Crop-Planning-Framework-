"""
XGBoost model training for Crop Recommendation System.

Trains an XGBClassifier (CPU mode) on preprocessed crop data and saves the model.
"""

from pathlib import Path
from xgboost import XGBClassifier
import joblib
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.preprocess import preprocess


def train_xgboost(n_estimators=100, random_state=42, verbose=1):
    """
    Train XGBClassifier on crop data (CPU mode, softprob for multi-class).
    
    Args:
        n_estimators: Number of boosting rounds
        random_state: Random seed for reproducibility
        verbose: Verbosity level
    
    Returns:
        Trained XGBClassifier model
    """
    # Load and preprocess data
    X_train, X_test, y_train, y_test, preprocessor = preprocess()
    
    if verbose:
        print(f"Training XGBoost with {n_estimators} estimators...")
    
    # Train model
    model = XGBClassifier(
        n_estimators=n_estimators,
        max_depth=6,
        learning_rate=0.1,
        random_state=random_state,
        objective='multi:softprob',  # Multi-class classification with probability
        num_class=len(preprocessor.label_encoder.classes_),
        tree_method='hist',  # CPU-friendly tree method
        verbosity=verbose if verbose > 0 else 0,
        n_jobs=-1  # Use all available cores
    )
    
    model.fit(X_train, y_train)
    
    if verbose:
        print(f"✓ Model trained successfully")
        print(f"  Training accuracy: {model.score(X_train, y_train):.4f}")
        print(f"  Test accuracy: {model.score(X_test, y_test):.4f}")
    
    return model


def save_model(model, save_path=None):
    """
    Save trained model to disk.
    
    Args:
        model: Trained XGBClassifier
        save_path: Path to save model (default: models/xgboost.pkl)
    
    Returns:
        Path to saved model
    """
    if save_path is None:
        save_path = Path(__file__).parent.parent.parent / "models" / "xgboost.pkl"
    
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, save_path)
    
    return save_path


if __name__ == "__main__":
    print("=" * 60)
    print("CropSense: XGBoost Model Training")
    print("=" * 60 + "\n")
    
    try:
        # Train model
        model = train_xgboost(n_estimators=200, verbose=1)
        
        # Save model
        save_path = save_model(model)
        print(f"\n✓ Model saved to: {save_path}")
        
        print("\n" + "=" * 60)
        print("XGBoost training completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        raise

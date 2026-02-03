"""
Random Forest model training for Crop Recommendation System.

Trains a RandomForestClassifier on preprocessed crop data and saves the model.
"""

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
import joblib
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.preprocess import preprocess


def train_random_forest(n_estimators=100, random_state=42, verbose=1):
    """
    Train RandomForestClassifier on crop data.
    
    Args:
        n_estimators: Number of trees in the forest
        random_state: Random seed for reproducibility
        verbose: Verbosity level
    
    Returns:
        Trained RandomForestClassifier model
    """
    # Load and preprocess data
    X_train, X_test, y_train, y_test, preprocessor = preprocess()
    
    if verbose:
        print(f"Training Random Forest with {n_estimators} estimators...")
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,  # Use all available cores
        verbose=verbose
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
        model: Trained RandomForestClassifier
        save_path: Path to save model (default: models/random_forest.pkl)
    
    Returns:
        Path to saved model
    """
    if save_path is None:
        save_path = Path(__file__).parent.parent.parent / "models" / "random_forest.pkl"
    
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, save_path)
    
    return save_path


if __name__ == "__main__":
    print("=" * 60)
    print("CropSense: Random Forest Model Training")
    print("=" * 60 + "\n")
    
    try:
        # Train model
        model = train_random_forest(n_estimators=200, verbose=1)
        
        # Save model
        save_path = save_model(model)
        print(f"\n✓ Model saved to: {save_path}")
        
        print("\n" + "=" * 60)
        print("Random Forest training completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        raise

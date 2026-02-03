"""
CatBoost model training for Crop Recommendation System.

Trains a CatBoostClassifier on preprocessed crop data and saves the model.
"""

from pathlib import Path
from catboost import CatBoostClassifier
import joblib
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.preprocess import preprocess


def train_catboost(iterations=200, random_state=42, verbose=1):
    """
    Train CatBoostClassifier on crop data.
    
    Args:
        iterations: Number of boosting iterations
        random_state: Random seed for reproducibility
        verbose: Verbosity level
    
    Returns:
        Trained CatBoostClassifier model
    """
    # Load and preprocess data
    X_train, X_test, y_train, y_test, preprocessor = preprocess()
    
    if verbose:
        print(f"Training CatBoost with {iterations} iterations...")
    
    # Train model
    model = CatBoostClassifier(
        iterations=iterations,
        learning_rate=0.1,
        depth=6,
        random_state=random_state,
        loss_function='MultiClass',
        verbose=verbose,
        task_type='CPU',  # CPU-only training
        thread_count=-1  # Use all available cores
    )
    
    model.fit(X_train, y_train, verbose=False)
    
    if verbose:
        print(f"✓ Model trained successfully")
        print(f"  Training accuracy: {model.score(X_train, y_train):.4f}")
        print(f"  Test accuracy: {model.score(X_test, y_test):.4f}")
    
    return model


def save_model(model, save_path=None):
    """
    Save trained model to disk.
    
    Args:
        model: Trained CatBoostClassifier
        save_path: Path to save model (default: models/catboost.pkl)
    
    Returns:
        Path to saved model
    """
    if save_path is None:
        save_path = Path(__file__).parent.parent.parent / "models" / "catboost.pkl"
    
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, save_path)
    
    return save_path


if __name__ == "__main__":
    print("=" * 60)
    print("CropSense: CatBoost Model Training")
    print("=" * 60 + "\n")
    
    try:
        # Train model
        model = train_catboost(iterations=200, verbose=1)
        
        # Save model
        save_path = save_model(model)
        print(f"\n✓ Model saved to: {save_path}")
        
        print("\n" + "=" * 60)
        print("CatBoost training completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        raise

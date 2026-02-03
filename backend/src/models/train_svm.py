"""
Support Vector Machine model training for Crop Recommendation System.

Trains an SVC (RBF kernel) on preprocessed crop data and saves the model.
"""

from pathlib import Path
from sklearn.svm import SVC
import joblib
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.preprocess import preprocess


def train_svm(kernel='rbf', C=100, gamma='scale', random_state=42, verbose=1):
    """
    Train SVC (Support Vector Classifier) on crop data.
    
    Args:
        kernel: Kernel type ('rbf' for Radial Basis Function)
        C: Regularization parameter
        gamma: Kernel coefficient ('scale' uses 1/(n_features * X.var()))
        random_state: Random seed for reproducibility
        verbose: Verbosity level
    
    Returns:
        Trained SVC model
    """
    # Load and preprocess data
    X_train, X_test, y_train, y_test, preprocessor = preprocess()
    
    if verbose:
        print(f"Training SVM with RBF kernel (C={C}, gamma={gamma})...")
    
    # Train model
    model = SVC(
        kernel=kernel,
        C=C,
        gamma=gamma,
        probability=True,  # Enable probability estimates for voting ensemble
        random_state=random_state,
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
        model: Trained SVC model
        save_path: Path to save model (default: models/svm.pkl)
    
    Returns:
        Path to saved model
    """
    if save_path is None:
        save_path = Path(__file__).parent.parent.parent / "models" / "svm.pkl"
    
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, save_path)
    
    return save_path


if __name__ == "__main__":
    print("=" * 60)
    print("CropSense: SVM Model Training")
    print("=" * 60 + "\n")
    
    try:
        # Train model
        model = train_svm(kernel='rbf', C=100, verbose=1)
        
        # Save model
        save_path = save_model(model)
        print(f"\n✓ Model saved to: {save_path}")
        
        print("\n" + "=" * 60)
        print("SVM training completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        raise

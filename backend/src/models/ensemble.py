"""
Soft Voting Ensemble for Crop Recommendation System.

Combines predictions from multiple base models using soft voting:
- Random Forest
- XGBoost
- CatBoost
- SVM

Soft voting averages the probability predictions from all models,
making the ensemble more robust than individual models.
"""

from pathlib import Path
from sklearn.ensemble import VotingClassifier
import joblib
import sys
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.preprocess import preprocess


class EnsemblePredictor:
    """Load and manage the soft voting ensemble for predictions."""
    
    def __init__(self, model_dir=None):
        """
        Initialize ensemble predictor.
        
        Args:
            model_dir: Directory containing trained model artifacts
        """
        if model_dir is None:
            model_dir = Path(__file__).parent.parent.parent / "models"
        
        self.model_dir = Path(model_dir)
        self.models = {}
        self.ensemble = None
    
    def load_base_models(self):
        """Load all trained base models from disk."""
        model_paths = {
            'rf': self.model_dir / 'random_forest.pkl',
            'xgb': self.model_dir / 'xgboost.pkl',
            'cat': self.model_dir / 'catboost.pkl',
            'svm': self.model_dir / 'svm.pkl',
        }
        
        for name, path in model_paths.items():
            if not path.exists():
                raise FileNotFoundError(f"Model not found: {path}")
            self.models[name] = joblib.load(path)
        
        return self.models
    
    def create_ensemble(self):
        """Create soft voting classifier from loaded base models."""
        if not self.models:
            self.load_base_models()
        
        # Create voting classifier with soft voting
        self.ensemble = VotingClassifier(
            estimators=[
                ('rf', self.models['rf']),
                ('xgb', self.models['xgb']),
                ('cat', self.models['cat']),
                ('svm', self.models['svm']),
            ],
            voting='soft',  # Use probability averaging
            n_jobs=-1  # Use all available cores
        )
        
        return self.ensemble
    
    def predict(self, X):
        """
        Make predictions using the ensemble.
        
        Args:
            X: Feature matrix (should be preprocessed)
        
        Returns:
            Predicted class labels
        """
        if self.ensemble is None:
            self.create_ensemble()
        
        return self.ensemble.predict(X)
    
    def predict_proba(self, X):
        """
        Get probability predictions from ensemble.
        
        Args:
            X: Feature matrix (should be preprocessed)
        
        Returns:
            Probability estimates for each class
        """
        if self.ensemble is None:
            self.create_ensemble()
        
        return self.ensemble.predict_proba(X)
    
    def save_ensemble(self, save_path=None):
        """
        Save the ensemble to disk.
        
        Args:
            save_path: Path to save ensemble (default: models/ensemble.pkl)
        
        Returns:
            Path to saved ensemble
        """
        if self.ensemble is None:
            self.create_ensemble()
        
        if save_path is None:
            save_path = self.model_dir / 'ensemble.pkl'
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.ensemble, save_path)
        
        return save_path


def train_ensemble():
    """
    Create and evaluate the soft voting ensemble.
    
    Returns:
        Tuple of (ensemble, accuracies)
    """
    # Load and preprocess data
    X_train, X_test, y_train, y_test, preprocessor = preprocess()
    
    # Load base models
    predictor = EnsemblePredictor()
    predictor.load_base_models()
    
    # Create ensemble
    ensemble = predictor.create_ensemble()
    
    # Fit ensemble (VotingClassifier aggregates base model predictions)
    print("Creating soft voting ensemble from base models...")
    ensemble.fit(X_train, y_train)
    
    # Get individual model accuracies
    accuracies = {}
    for name, model in predictor.models.items():
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)
        accuracies[name] = {'train': train_acc, 'test': test_acc}
    
    # Get ensemble accuracies
    ensemble_train_acc = ensemble.score(X_train, y_train)
    ensemble_test_acc = ensemble.score(X_test, y_test)
    accuracies['ensemble'] = {'train': ensemble_train_acc, 'test': ensemble_test_acc}
    
    return ensemble, accuracies


def save_model(ensemble, save_path=None):
    """
    Save trained ensemble to disk.
    
    Args:
        ensemble: Trained VotingClassifier
        save_path: Path to save model (default: models/ensemble.pkl)
    
    Returns:
        Path to saved model
    """
    if save_path is None:
        save_path = Path(__file__).parent.parent.parent / "models" / "ensemble.pkl"
    
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(ensemble, save_path)
    
    return save_path


if __name__ == "__main__":
    print("=" * 70)
    print("CropSense: Soft Voting Ensemble Training")
    print("=" * 70 + "\n")
    
    try:
        # Train ensemble
        ensemble, accuracies = train_ensemble()
        
        # Print accuracies
        print("\n" + "=" * 70)
        print("Model Accuracies Comparison:")
        print("=" * 70)
        
        for model_name, scores in accuracies.items():
            print(f"\n{model_name.upper()}:")
            print(f"  Training Accuracy: {scores['train']:.4f}")
            print(f"  Test Accuracy:     {scores['test']:.4f}")
        
        # Save ensemble
        save_path = save_model(ensemble)
        print(f"\n✓ Ensemble saved to: {save_path}")
        
        print("\n" + "=" * 70)
        print("Soft Voting Ensemble training completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error during ensemble training: {e}")
        raise

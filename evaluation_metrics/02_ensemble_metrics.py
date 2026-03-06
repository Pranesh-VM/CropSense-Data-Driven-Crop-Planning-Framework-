"""
02_ensemble_metrics.py - Ensemble Model Evaluation

Implements Steps 3-4 from EVALUATION_STRATEGY.md:
- Compute classification metrics for all models + ensemble
- Perform cross-validation
- Generate Charts 1-7

Charts generated:
1. Grouped Bar Chart - Accuracy, Precision, Recall, F1 for all 5 models
2. Confusion Matrix Heatmaps - one per model + ensemble (5 total)
3. ROC Curves - models overlaid on same plot
4. AUC Bar Chart - mean AUC for each model
5. Cross-Validation Box Plot - accuracy distribution across folds
6. Log Loss Bar Chart - per model
7. Classification Report Heatmap - for the ensemble
"""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import numpy as np
import pandas as pd
import joblib

from utils.metrics_helper import MetricsCalculator
from utils.plot_helper import PlotHelper
from src.data.preprocess import DataPreprocessor


def load_models(model_dir):
    """Load all trained models."""
    models = {
        'Random Forest': joblib.load(model_dir / 'random_forest.pkl'),
        'XGBoost': joblib.load(model_dir / 'xgboost.pkl'),
        'CatBoost': joblib.load(model_dir / 'catboost.pkl'),
        'SVM': joblib.load(model_dir / 'svm.pkl'),
        'Ensemble': joblib.load(model_dir / 'ensemble.pkl'),
    }
    return models


def load_data():
    """Load and preprocess data."""
    # Use correct data path
    data_path = Path(__file__).parent.parent / "backend" / "data" / "Crop_recommendation.csv"
    preprocessor = DataPreprocessor(data_path=data_path)
    preprocessor.load_encoders()
    
    df = preprocessor.load_data()
    X_scaled, y_encoded = preprocessor.preprocess(df, fit_encoders=False)
    
    X_train, X_test, y_train, y_test = preprocessor.split_data(
        X_scaled, y_encoded, test_size=0.2, random_state=42
    )
    
    # Get class labels
    class_labels = list(preprocessor.label_encoder.classes_)
    
    return X_train, X_test, y_train, y_test, class_labels


def main():
    print("=" * 60)
    print("ENSEMBLE MODEL EVALUATION")
    print("=" * 60)
    
    # Setup paths
    model_dir = Path(__file__).parent.parent / "backend" / "models"
    output_dir = Path(__file__).parent / "plots"
    output_dir.mkdir(exist_ok=True)
    
    # Load models and data
    print("\n[1/6] Loading models and data...")
    models = load_models(model_dir)
    X_train, X_test, y_train, y_test, class_labels = load_data()
    
    print(f"    - Test set size: {len(y_test)}")
    print(f"    - Number of classes: {len(class_labels)}")
    print(f"    - Models: {list(models.keys())}")
    
    # Initialize helpers
    metrics_calc = MetricsCalculator(y_test, class_labels)
    plotter = PlotHelper(output_dir)
    
    # Step 3: Compute Classification Metrics
    print("\n[2/6] Computing classification metrics for each model...")
    
    all_metrics = {}
    predictions = {}
    probabilities = {}
    
    for name, model in models.items():
        print(f"    - {name}...")
        
        y_pred = model.predict(X_test)
        predictions[name] = y_pred
        
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X_test)
            probabilities[name] = y_pred_proba
        else:
            y_pred_proba = None
            probabilities[name] = None
        
        metrics = metrics_calc.compute_all_metrics(y_pred, y_pred_proba)
        all_metrics[name] = metrics
        
        print(f"      Accuracy: {metrics['accuracy']:.4f}")
        print(f"      F1-Score: {metrics['f1_weighted']:.4f}")
        print(f"      Cohen's Kappa: {metrics['cohen_kappa']:.4f}")
    
    # Step 4: Cross-Validation
    print("\n[3/6] Performing 5-fold cross-validation...")
    
    # Combine train and test for CV
    X_full = np.vstack([X_train, X_test])
    y_full = np.concatenate([y_train, y_test])
    
    cv_scores = {}
    for name, model in models.items():
        print(f"    - {name}...")
        cv_result = MetricsCalculator.cross_validation_scores(model, X_full, y_full, cv=5)
        cv_scores[name] = cv_result['scores']
        print(f"      CV Accuracy: {cv_result['mean']:.4f} (+/- {cv_result['std']:.4f})")
    
    # Generate Charts
    print("\n[4/6] Generating comparison charts...")
    
    # Chart 1: Grouped Bar Chart
    metrics_for_chart = {}
    for name in models.keys():
        metrics_for_chart[name] = {
            'Accuracy': all_metrics[name]['accuracy'],
            'Precision': all_metrics[name]['precision_weighted'],
            'Recall': all_metrics[name]['recall_weighted'],
            'F1-Score': all_metrics[name]['f1_weighted'],
        }
    
    plotter.grouped_bar_chart(
        metrics_for_chart,
        ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
        'Model Comparison - Classification Metrics',
        '01_metrics_comparison.png'
    )
    print("    - Chart 1: Grouped bar chart saved")
    
    # Chart 2: Confusion Matrices
    print("\n[5/6] Generating confusion matrices...")
    for name, pred in predictions.items():
        cm = all_metrics[name]['confusion_matrix']
        plotter.confusion_matrix_heatmap(
            cm, class_labels,
            f'Confusion Matrix - {name}',
            f'02_confusion_matrix_{name.lower().replace(" ", "_")}.png'
        )
        print(f"    - Confusion matrix for {name} saved")
    
    # Chart 3: ROC Curves
    print("\n[6/6] Generating ROC curves and remaining charts...")
    roc_data_all = {}
    auc_scores = {}
    
    for name, proba in probabilities.items():
        if proba is not None:
            roc_data = metrics_calc.compute_roc_curves(proba)
            roc_data_all[name] = roc_data
            auc_scores[name] = metrics_calc.compute_mean_auc(proba)
    
    plotter.roc_curves_overlay(
        roc_data_all,
        'ROC Curves - All Models (Macro Average)',
        '03_roc_curves.png'
    )
    print("    - Chart 3: ROC curves saved")
    
    # Chart 4: AUC Bar Chart
    plotter.auc_bar_chart(
        auc_scores,
        'Mean AUC Comparison',
        '04_auc_comparison.png'
    )
    print("    - Chart 4: AUC bar chart saved")
    
    # Chart 5: Cross-Validation Box Plot
    plotter.cv_box_plot(
        cv_scores,
        'Cross-Validation Accuracy Distribution (5-Fold)',
        '05_cv_box_plot.png'
    )
    print("    - Chart 5: CV box plot saved")
    
    # Chart 6: Log Loss Bar Chart
    logloss_dict = {}
    for name, metrics in all_metrics.items():
        if 'log_loss' in metrics and not np.isnan(metrics['log_loss']):
            logloss_dict[name] = metrics['log_loss']
    
    plotter.log_loss_bar_chart(
        logloss_dict,
        'Log Loss Comparison (Lower is Better)',
        '06_log_loss.png'
    )
    print("    - Chart 6: Log loss bar chart saved")
    
    # Chart 7: Classification Report Heatmap for Ensemble
    plotter.classification_report_heatmap(
        all_metrics['Ensemble']['classification_report'],
        'Classification Report - Ensemble Model',
        '07_ensemble_classification_report.png'
    )
    print("    - Chart 7: Classification report heatmap saved")
    
    # Summary
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    
    print("\nMetrics Summary:")
    summary_df = pd.DataFrame({
        name: {
            'Accuracy': all_metrics[name]['accuracy'],
            'Precision': all_metrics[name]['precision_weighted'],
            'Recall': all_metrics[name]['recall_weighted'],
            'F1-Score': all_metrics[name]['f1_weighted'],
            'Cohen Kappa': all_metrics[name]['cohen_kappa'],
            'Log Loss': all_metrics[name].get('log_loss', np.nan),
            'CV Mean': np.mean(cv_scores[name]),
            'CV Std': np.std(cv_scores[name]),
        }
        for name in models.keys()
    }).T
    
    print(summary_df.round(4).to_string())
    
    # Save summary to CSV
    summary_df.to_csv(output_dir / 'ensemble_metrics_summary.csv')
    print(f"\nSummary saved to: {output_dir / 'ensemble_metrics_summary.csv'}")
    print(f"All plots saved to: {output_dir}")
    
    return all_metrics, cv_scores, predictions, probabilities


if __name__ == "__main__":
    all_metrics, cv_scores, predictions, probabilities = main()

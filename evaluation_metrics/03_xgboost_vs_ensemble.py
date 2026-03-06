"""
03_xgboost_vs_ensemble.py - XGBoost vs Ensemble Comparison

Implements Steps 5-9 from EVALUATION_STRATEGY.md:
- Statistical comparison (paired t-test, Wilcoxon, McNemar's)
- Error analysis
- Prediction confidence comparison
- Class-level performance comparison
- Model diversity analysis

Charts generated:
8.  Per-Class F1 Comparison (Grouped Bar) - XGBoost vs Ensemble
9.  Error Correction Bar Chart - samples XGB got wrong but ensemble got right
10. Confidence Distribution (Histogram) - XGBoost vs Ensemble for correct predictions
11. Confidence Distribution for Wrong Predictions
12. Prediction Correlation Heatmap - between all 4 base models
13. McNemar's Test Result Table
14. Cross-Validation Accuracy Line Plot - XGBoost vs Ensemble across folds
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from utils.metrics_helper import MetricsCalculator
from utils.plot_helper import PlotHelper
from src.data.preprocess import DataPreprocessor


def load_models_and_data():
    """Load all models and test data."""
    model_dir = Path(__file__).parent.parent / "backend" / "models"
    
    models = {
        'Random Forest': joblib.load(model_dir / 'random_forest.pkl'),
        'XGBoost': joblib.load(model_dir / 'xgboost.pkl'),
        'CatBoost': joblib.load(model_dir / 'catboost.pkl'),
        'SVM': joblib.load(model_dir / 'svm.pkl'),
        'Ensemble': joblib.load(model_dir / 'ensemble.pkl'),
    }
    
    # Use correct data path
    data_path = Path(__file__).parent.parent / "backend" / "data" / "Crop_recommendation.csv"
    preprocessor = DataPreprocessor(data_path=data_path)
    preprocessor.load_encoders()
    
    df = preprocessor.load_data()
    X_scaled, y_encoded = preprocessor.preprocess(df, fit_encoders=False)
    X_train, X_test, y_train, y_test = preprocessor.split_data(
        X_scaled, y_encoded, test_size=0.2, random_state=42
    )
    
    class_labels = list(preprocessor.label_encoder.classes_)
    X_full = np.vstack([X_train, X_test])
    y_full = np.concatenate([y_train, y_test])
    
    return models, X_test, y_test, X_full, y_full, class_labels


def main():
    print("=" * 60)
    print("XGBOOST vs ENSEMBLE COMPARISON")
    print("Proving Why Ensemble is Better Than Single XGBoost")
    print("=" * 60)
    
    output_dir = Path(__file__).parent / "plots"
    output_dir.mkdir(exist_ok=True)
    
    # Load everything
    print("\n[1/8] Loading models and data...")
    models, X_test, y_test, X_full, y_full, class_labels = load_models_and_data()
    
    plotter = PlotHelper(output_dir)
    
    # Get predictions
    predictions = {}
    probabilities = {}
    for name, model in models.items():
        predictions[name] = model.predict(X_test)
        if hasattr(model, 'predict_proba'):
            probabilities[name] = model.predict_proba(X_test)
    
    y_pred_xgb = predictions['XGBoost']
    y_pred_ens = predictions['Ensemble']
    y_proba_xgb = probabilities['XGBoost']
    y_proba_ens = probabilities['Ensemble']
    
    # Step 5: Statistical Comparison
    print("\n[2/8] Performing statistical tests...")
    
    # Cross-validation for both
    cv_scores = {}
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name in ['XGBoost', 'Ensemble']:
        scores = cross_val_score(models[name], X_full, y_full, cv=skf, scoring='accuracy')
        cv_scores[name] = scores
    
    # Paired t-test
    ttest_result = MetricsCalculator.paired_ttest(cv_scores['XGBoost'], cv_scores['Ensemble'])
    print(f"    Paired t-test:")
    print(f"      t-statistic: {ttest_result['t_statistic']:.4f}")
    print(f"      p-value: {ttest_result['p_value']:.6f}")
    print(f"      {'Significant!' if ttest_result['p_value'] < 0.05 else 'Not significant'}")
    
    # Wilcoxon test
    wilcoxon_result = MetricsCalculator.wilcoxon_test(cv_scores['XGBoost'], cv_scores['Ensemble'])
    print(f"\n    Wilcoxon signed-rank test:")
    print(f"      statistic: {wilcoxon_result['statistic']:.4f}")
    print(f"      p-value: {wilcoxon_result['p_value']:.6f}")
    
    # McNemar's test
    mcnemar_result = MetricsCalculator.mcnemar_test(y_test, y_pred_xgb, y_pred_ens)
    print(f"\n    McNemar's test:")
    print(f"      chi²: {mcnemar_result['chi2']:.4f}")
    print(f"      p-value: {mcnemar_result['p_value']:.6f}")
    print(f"      XGB only correct: {mcnemar_result['model1_only_correct']}")
    print(f"      Ensemble only correct: {mcnemar_result['model2_only_correct']}")
    
    # Step 6: Error Analysis
    print("\n[3/8] Analyzing error corrections...")
    error_analysis = MetricsCalculator.error_correction_analysis(
        y_test, y_pred_xgb, y_pred_ens, class_labels
    )
    print(f"    Total corrections by ensemble: {error_analysis['total_corrections']}")
    
    # Chart 9: Error Correction Bar Chart
    plotter.error_correction_bar(
        error_analysis['per_class'],
        'Error Corrections by Ensemble (XGBoost Wrong → Ensemble Right)',
        '09_error_corrections.png'
    )
    print("    Chart 9: Error correction bar chart saved")
    
    # Step 7: Confidence Analysis
    print("\n[4/8] Analyzing prediction confidence...")
    
    xgb_confidence = MetricsCalculator.confidence_analysis(y_test, y_pred_xgb, y_proba_xgb)
    ens_confidence = MetricsCalculator.confidence_analysis(y_test, y_pred_ens, y_proba_ens)
    
    print(f"    XGBoost correct predictions - Mean confidence: {xgb_confidence['correct_mean_confidence']:.4f}")
    print(f"    Ensemble correct predictions - Mean confidence: {ens_confidence['correct_mean_confidence']:.4f}")
    print(f"    XGBoost incorrect predictions - Mean confidence: {xgb_confidence['incorrect_mean_confidence']:.4f}")
    print(f"    Ensemble incorrect predictions - Mean confidence: {ens_confidence['incorrect_mean_confidence']:.4f}")
    
    # Chart 10: Confidence Distribution for Correct Predictions
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # XGBoost
    axes[0].hist(xgb_confidence['correct_confidences'], bins=30, alpha=0.7, color='blue', label='XGBoost')
    axes[0].hist(ens_confidence['correct_confidences'], bins=30, alpha=0.7, color='green', label='Ensemble')
    axes[0].axvline(xgb_confidence['correct_mean_confidence'], color='blue', linestyle='--', 
                    label=f"XGB mean: {xgb_confidence['correct_mean_confidence']:.3f}")
    axes[0].axvline(ens_confidence['correct_mean_confidence'], color='green', linestyle='--',
                    label=f"Ens mean: {ens_confidence['correct_mean_confidence']:.3f}")
    axes[0].set_xlabel('Prediction Confidence')
    axes[0].set_ylabel('Count')
    axes[0].set_title('Correct Predictions - Confidence Distribution')
    axes[0].legend()
    
    # Incorrect predictions
    if len(xgb_confidence['incorrect_confidences']) > 0 and len(ens_confidence['incorrect_confidences']) > 0:
        axes[1].hist(xgb_confidence['incorrect_confidences'], bins=20, alpha=0.7, color='red', label='XGBoost')
        axes[1].hist(ens_confidence['incorrect_confidences'], bins=20, alpha=0.7, color='orange', label='Ensemble')
        axes[1].axvline(xgb_confidence['incorrect_mean_confidence'], color='red', linestyle='--',
                       label=f"XGB mean: {xgb_confidence['incorrect_mean_confidence']:.3f}")
        axes[1].axvline(ens_confidence['incorrect_mean_confidence'], color='orange', linestyle='--',
                       label=f"Ens mean: {ens_confidence['incorrect_mean_confidence']:.3f}")
    axes[1].set_xlabel('Prediction Confidence')
    axes[1].set_ylabel('Count')
    axes[1].set_title('Incorrect Predictions - Confidence Distribution')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / '10_11_confidence_distribution.png', bbox_inches='tight', facecolor='white')
    plt.close()
    print("    Charts 10-11: Confidence distributions saved")
    
    # Step 8: Per-Class F1 Comparison
    print("\n[5/8] Comparing per-class F1 scores...")
    metrics_calc = MetricsCalculator(y_test, class_labels)
    
    f1_xgb = metrics_calc.compute_per_class_f1(y_pred_xgb)
    f1_ens = metrics_calc.compute_per_class_f1(y_pred_ens)
    
    # Chart 8: Per-Class F1 Comparison
    plotter.per_class_f1_comparison(
        {'XGBoost': f1_xgb, 'Ensemble': f1_ens},
        class_labels,
        'Per-Class F1 Score Comparison',
        '08_per_class_f1.png'
    )
    print("    Chart 8: Per-class F1 comparison saved")
    
    # Find classes where ensemble improves
    improvements = []
    for i, (xgb_f1, ens_f1) in enumerate(zip(f1_xgb, f1_ens)):
        if ens_f1 > xgb_f1:
            improvements.append((class_labels[i], xgb_f1, ens_f1, ens_f1 - xgb_f1))
    
    if improvements:
        print("\n    Classes where Ensemble outperforms XGBoost:")
        for cls, xgb_f1, ens_f1, diff in sorted(improvements, key=lambda x: -x[3])[:10]:
            print(f"      {cls}: XGB={xgb_f1:.3f}, Ens={ens_f1:.3f}, Δ=+{diff:.3f}")
    
    # Step 9: Model Diversity Analysis
    print("\n[6/8] Analyzing model diversity...")
    
    base_predictions = {
        'Random Forest': predictions['Random Forest'],
        'XGBoost': predictions['XGBoost'],
        'CatBoost': predictions['CatBoost'],
        'SVM': predictions['SVM'],
    }
    
    corr_result = MetricsCalculator.prediction_correlation(base_predictions)
    
    # Chart 12: Correlation Heatmap
    plotter.correlation_heatmap(
        corr_result['matrix'],
        corr_result['model_names'],
        'Prediction Agreement Between Base Models',
        '12_prediction_correlation.png'
    )
    print("    Chart 12: Prediction correlation heatmap saved")
    
    # Chart 13: McNemar's Test Results Table
    print("\n[7/8] Creating statistical test summary...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    table_data = [
        ['Test', 'Statistic', 'p-value', 'Conclusion'],
        ['Paired t-test', f"{ttest_result['t_statistic']:.4f}", 
         f"{ttest_result['p_value']:.6f}",
         'Significant' if ttest_result['p_value'] < 0.05 else 'Not significant'],
        ['Wilcoxon', f"{wilcoxon_result['statistic']:.4f}",
         f"{wilcoxon_result['p_value']:.6f}",
         'Significant' if wilcoxon_result['p_value'] < 0.05 else 'Not significant'],
        ['McNemar\'s', f"{mcnemar_result['chi2']:.4f}",
         f"{mcnemar_result['p_value']:.6f}",
         'Significant' if mcnemar_result['p_value'] < 0.05 else 'Not significant'],
        ['', '', '', ''],
        ['McNemar Details', 'XGB only correct', str(mcnemar_result['model1_only_correct']), ''],
        ['', 'Ensemble only correct', str(mcnemar_result['model2_only_correct']), ''],
    ]
    
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Header styling
    for j in range(4):
        table[(0, j)].set_facecolor('#4472C4')
        table[(0, j)].set_text_props(color='white', fontweight='bold')
    
    ax.set_title('Statistical Comparison: XGBoost vs Ensemble', fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(output_dir / '13_statistical_tests.png', bbox_inches='tight', facecolor='white', dpi=150)
    plt.close()
    print("    Chart 13: Statistical tests table saved")
    
    # Chart 14: CV Line Plot
    print("\n[8/8] Creating cross-validation comparison plot...")
    
    # Get CV for all models
    all_cv_scores = {}
    for name in ['Random Forest', 'XGBoost', 'CatBoost', 'SVM', 'Ensemble']:
        scores = cross_val_score(models[name], X_full, y_full, cv=skf, scoring='accuracy')
        all_cv_scores[name] = scores
    
    plotter.cv_line_plot(
        all_cv_scores,
        'Cross-Validation Accuracy Across Folds',
        '14_cv_line_plot.png'
    )
    print("    Chart 14: CV line plot saved")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    
    xgb_acc = np.mean(y_pred_xgb == y_test)
    ens_acc = np.mean(y_pred_ens == y_test)
    
    print(f"\nAccuracy:")
    print(f"  XGBoost:  {xgb_acc:.4f}")
    print(f"  Ensemble: {ens_acc:.4f}")
    print(f"  Improvement: {(ens_acc - xgb_acc)*100:+.2f}%")
    
    print(f"\nError Corrections:")
    print(f"  Samples XGBoost got wrong but Ensemble got right: {mcnemar_result['model2_only_correct']}")
    print(f"  Samples Ensemble got wrong but XGBoost got right: {mcnemar_result['model1_only_correct']}")
    print(f"  Net improvement: {mcnemar_result['model2_only_correct'] - mcnemar_result['model1_only_correct']}")
    
    print(f"\nModel Diversity (Agreement Rates):")
    for i, name1 in enumerate(corr_result['model_names']):
        for j, name2 in enumerate(corr_result['model_names']):
            if i < j:
                print(f"  {name1} ↔ {name2}: {corr_result['matrix'][i,j]:.3f}")
    
    print(f"\nConclusion:")
    if ens_acc > xgb_acc:
        print("  ✓ Ensemble outperforms XGBoost")
    if mcnemar_result['model2_only_correct'] > mcnemar_result['model1_only_correct']:
        print("  ✓ Ensemble corrects more XGBoost errors than vice versa")
    avg_diversity = 1 - np.mean(corr_result['matrix'][np.triu_indices(4, k=1)])
    print(f"  ✓ Model diversity: {avg_diversity:.3f} (lower agreement = higher diversity)")
    
    print(f"\nAll plots saved to: {output_dir}")


if __name__ == "__main__":
    main()

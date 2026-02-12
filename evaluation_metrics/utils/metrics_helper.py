"""
Metrics Helper - Reusable metric computation functions for model evaluation.

Computes:
- Classification metrics (accuracy, precision, recall, F1, etc.)
- Cross-validation metrics
- Statistical tests (t-test, McNemar's test)
- Model diversity analysis
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    cohen_kappa_score, log_loss, classification_report,
    confusion_matrix, roc_curve, auc
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
from scipy import stats
import warnings


class MetricsCalculator:
    """
    Calculate various metrics for model evaluation.
    """
    
    def __init__(self, y_true, class_labels=None):
        """
        Initialize with ground truth labels.
        
        Args:
            y_true: True labels for the test set
            class_labels: List of class names (optional)
        """
        self.y_true = y_true
        self.class_labels = class_labels
        self.n_classes = len(np.unique(y_true))
    
    def compute_all_metrics(self, y_pred, y_pred_proba=None):
        """
        Compute all classification metrics for a model.
        
        Args:
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
        
        Returns:
            Dictionary with all computed metrics
        """
        metrics = {
            'accuracy': accuracy_score(self.y_true, y_pred),
            'precision_weighted': precision_score(self.y_true, y_pred, average='weighted', zero_division=0),
            'recall_weighted': recall_score(self.y_true, y_pred, average='weighted', zero_division=0),
            'f1_weighted': f1_score(self.y_true, y_pred, average='weighted', zero_division=0),
            'cohen_kappa': cohen_kappa_score(self.y_true, y_pred),
            'confusion_matrix': confusion_matrix(self.y_true, y_pred),
            'classification_report': classification_report(
                self.y_true, y_pred, 
                target_names=self.class_labels,
                output_dict=True,
                zero_division=0
            )
        }
        
        if y_pred_proba is not None:
            try:
                metrics['log_loss'] = log_loss(self.y_true, y_pred_proba)
            except ValueError:
                metrics['log_loss'] = np.nan
        
        return metrics
    
    def compute_per_class_f1(self, y_pred):
        """
        Compute F1-score for each class.
        
        Args:
            y_pred: Predicted labels
        
        Returns:
            Array of F1-scores per class
        """
        return f1_score(self.y_true, y_pred, average=None, zero_division=0)
    
    def compute_roc_curves(self, y_pred_proba):
        """
        Compute ROC curves for multi-class classification (One-vs-Rest).
        
        Args:
            y_pred_proba: Predicted probabilities
        
        Returns:
            Dictionary with fpr, tpr, and auc for each class
        """
        roc_data = {}
        n_classes = y_pred_proba.shape[1]
        
        for i in range(n_classes):
            y_binary = (self.y_true == i).astype(int)
            fpr, tpr, _ = roc_curve(y_binary, y_pred_proba[:, i])
            roc_auc = auc(fpr, tpr)
            
            class_name = self.class_labels[i] if self.class_labels else f"Class {i}"
            roc_data[class_name] = {
                'fpr': fpr,
                'tpr': tpr,
                'auc': roc_auc
            }
        
        return roc_data
    
    def compute_mean_auc(self, y_pred_proba):
        """
        Compute mean AUC across all classes.
        
        Args:
            y_pred_proba: Predicted probabilities
        
        Returns:
            Mean AUC score
        """
        roc_data = self.compute_roc_curves(y_pred_proba)
        aucs = [data['auc'] for data in roc_data.values()]
        return np.mean(aucs)
    
    @staticmethod
    def cross_validation_scores(model, X, y, cv=5, scoring='accuracy'):
        """
        Perform stratified cross-validation.
        
        Args:
            model: Model to evaluate
            X: Features
            y: Labels
            cv: Number of folds
            scoring: Scoring metric
        
        Returns:
            Dictionary with mean, std, and individual fold scores
        """
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        scores = cross_val_score(model, X, y, cv=skf, scoring=scoring)
        
        return {
            'mean': np.mean(scores),
            'std': np.std(scores),
            'scores': scores
        }
    
    @staticmethod
    def paired_ttest(scores1, scores2):
        """
        Perform paired t-test between two models' cross-validation scores.
        
        Args:
            scores1: CV scores from model 1
            scores2: CV scores from model 2
        
        Returns:
            t-statistic and p-value
        """
        t_stat, p_value = stats.ttest_rel(scores1, scores2)
        return {'t_statistic': t_stat, 'p_value': p_value}
    
    @staticmethod
    def wilcoxon_test(scores1, scores2):
        """
        Perform Wilcoxon signed-rank test between two models' CV scores.
        
        Args:
            scores1: CV scores from model 1
            scores2: CV scores from model 2
        
        Returns:
            statistic and p-value
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                stat, p_value = stats.wilcoxon(scores1, scores2)
            except ValueError:
                # If all differences are zero
                stat, p_value = 0, 1.0
        return {'statistic': stat, 'p_value': p_value}
    
    @staticmethod
    def mcnemar_test(y_true, y_pred1, y_pred2):
        """
        Perform McNemar's test between two models.
        
        Args:
            y_true: True labels
            y_pred1: Predictions from model 1
            y_pred2: Predictions from model 2
        
        Returns:
            Contingency table and p-value
        """
        # Build contingency table
        correct1 = (y_pred1 == y_true)
        correct2 = (y_pred2 == y_true)
        
        # n00: both wrong, n01: 1 wrong 2 right, n10: 1 right 2 wrong, n11: both right
        n00 = np.sum(~correct1 & ~correct2)
        n01 = np.sum(~correct1 & correct2)
        n10 = np.sum(correct1 & ~correct2)
        n11 = np.sum(correct1 & correct2)
        
        contingency_table = np.array([[n11, n10], [n01, n00]])
        
        # McNemar's test with continuity correction
        b = n01  # Model 1 wrong, Model 2 right
        c = n10  # Model 1 right, Model 2 wrong
        
        if b + c == 0:
            chi2 = 0
            p_value = 1.0
        else:
            chi2 = (abs(b - c) - 1) ** 2 / (b + c)
            p_value = 1 - stats.chi2.cdf(chi2, df=1)
        
        return {
            'contingency_table': contingency_table,
            'chi2': chi2,
            'p_value': p_value,
            'model1_only_correct': n10,
            'model2_only_correct': n01
        }
    
    @staticmethod
    def error_correction_analysis(y_true, y_pred_main, y_pred_ensemble, class_labels=None):
        """
        Analyze where ensemble corrects main model's errors.
        
        Args:
            y_true: True labels
            y_pred_main: Main model predictions (e.g., XGBoost)
            y_pred_ensemble: Ensemble predictions
            class_labels: Optional class names
        
        Returns:
            Dictionary with per-class error correction counts
        """
        main_wrong = y_pred_main != y_true
        ensemble_right = y_pred_ensemble == y_true
        
        # Samples where main was wrong but ensemble was right
        corrected = main_wrong & ensemble_right
        
        # Count per class
        unique_classes = np.unique(y_true)
        correction_counts = {}
        
        for cls in unique_classes:
            cls_mask = y_true == cls
            count = np.sum(corrected & cls_mask)
            label = class_labels[cls] if class_labels else f"Class {cls}"
            correction_counts[label] = int(count)
        
        return {
            'total_corrections': int(np.sum(corrected)),
            'per_class': correction_counts
        }
    
    @staticmethod
    def confidence_analysis(y_true, y_pred, y_pred_proba):
        """
        Analyze prediction confidence for correct vs incorrect predictions.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
        
        Returns:
            Dictionary with confidence statistics
        """
        max_proba = np.max(y_pred_proba, axis=1)
        correct = y_pred == y_true
        
        return {
            'correct_mean_confidence': float(np.mean(max_proba[correct])) if np.sum(correct) > 0 else 0,
            'correct_std_confidence': float(np.std(max_proba[correct])) if np.sum(correct) > 0 else 0,
            'incorrect_mean_confidence': float(np.mean(max_proba[~correct])) if np.sum(~correct) > 0 else 0,
            'incorrect_std_confidence': float(np.std(max_proba[~correct])) if np.sum(~correct) > 0 else 0,
            'correct_confidences': max_proba[correct],
            'incorrect_confidences': max_proba[~correct]
        }
    
    @staticmethod
    def prediction_correlation(predictions_dict):
        """
        Compute correlation between model predictions.
        
        Args:
            predictions_dict: Dictionary of {model_name: predictions}
        
        Returns:
            Correlation matrix as DataFrame-like dictionary
        """
        model_names = list(predictions_dict.keys())
        n_models = len(model_names)
        correlation_matrix = np.zeros((n_models, n_models))
        
        for i, name1 in enumerate(model_names):
            for j, name2 in enumerate(model_names):
                if i == j:
                    correlation_matrix[i, j] = 1.0
                else:
                    # Calculate agreement rate (simpler than Pearson for categorical)
                    agreement = np.mean(predictions_dict[name1] == predictions_dict[name2])
                    correlation_matrix[i, j] = agreement
        
        return {
            'matrix': correlation_matrix,
            'model_names': model_names
        }

"""
Plot Helper - Reusable plotting functions for model evaluation.

Creates:
- Grouped bar charts
- Confusion matrices
- ROC curves
- Box plots
- Heatmaps
- Line plots
- Radar charts
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class PlotHelper:
    """
    Create various plots for model evaluation.
    """
    
    def __init__(self, output_dir=None, figsize=(10, 6), style='whitegrid'):
        """
        Initialize plot helper.
        
        Args:
            output_dir: Directory to save plots
            figsize: Default figure size
            style: Seaborn style
        """
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "plots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figsize = figsize
        sns.set_style(style)
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 150
    
    def save_and_show(self, fig, filename, show=True):
        """Save figure and optionally display it."""
        filepath = self.output_dir / filename
        fig.savefig(filepath, bbox_inches='tight', facecolor='white')
        if show:
            plt.show()
        plt.close(fig)
        return filepath
    
    def grouped_bar_chart(self, metrics_dict, metric_names, title, filename, ylabel='Score'):
        """
        Create grouped bar chart comparing metrics across models.
        
        Args:
            metrics_dict: {model_name: {metric_name: value}}
            metric_names: List of metric names to plot
            title: Chart title
            filename: Output filename
            ylabel: Y-axis label
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        models = list(metrics_dict.keys())
        n_models = len(models)
        n_metrics = len(metric_names)
        
        x = np.arange(n_metrics)
        width = 0.8 / n_models
        
        colors = plt.cm.Set2(np.linspace(0, 1, n_models))
        
        for i, model in enumerate(models):
            values = [metrics_dict[model].get(m, 0) for m in metric_names]
            offset = (i - n_models / 2 + 0.5) * width
            bars = ax.bar(x + offset, values, width, label=model, color=colors[i])
            
            # Add value labels
            for bar, val in zip(bars, values):
                ax.annotate(f'{val:.3f}',
                           xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                           ha='center', va='bottom', fontsize=8, rotation=45)
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names, rotation=45, ha='right')
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        ax.set_ylim(0, 1.15)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def confusion_matrix_heatmap(self, cm, class_labels, title, filename):
        """
        Create confusion matrix heatmap.
        
        Args:
            cm: Confusion matrix
            class_labels: Class names
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_labels, yticklabels=class_labels, ax=ax)
        
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title(title)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def roc_curves_overlay(self, roc_data_dict, title, filename):
        """
        Overlay ROC curves from multiple models.
        
        Args:
            roc_data_dict: {model_name: {class: {'fpr': [...], 'tpr': [...], 'auc': float}}}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(roc_data_dict)))
        
        for (model_name, roc_data), color in zip(roc_data_dict.items(), colors):
            # Compute macro-average ROC
            all_fpr = np.unique(np.concatenate([d['fpr'] for d in roc_data.values()]))
            mean_tpr = np.zeros_like(all_fpr)
            for class_data in roc_data.values():
                mean_tpr += np.interp(all_fpr, class_data['fpr'], class_data['tpr'])
            mean_tpr /= len(roc_data)
            
            mean_auc = np.mean([d['auc'] for d in roc_data.values()])
            ax.plot(all_fpr, mean_tpr, color=color, lw=2,
                   label=f'{model_name} (AUC = {mean_auc:.3f})')
        
        ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Random')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title(title)
        ax.legend(loc='lower right')
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def auc_bar_chart(self, auc_dict, title, filename):
        """
        Create bar chart of AUC scores.
        
        Args:
            auc_dict: {model_name: auc_score}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        models = list(auc_dict.keys())
        aucs = list(auc_dict.values())
        colors = plt.cm.Set2(np.linspace(0, 1, len(models)))
        
        bars = ax.bar(models, aucs, color=colors)
        
        for bar, auc in zip(bars, aucs):
            ax.annotate(f'{auc:.4f}',
                       xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                       ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('Model')
        ax.set_ylabel('Mean AUC')
        ax.set_title(title)
        ax.set_ylim(0, 1.1)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def cv_box_plot(self, cv_scores_dict, title, filename):
        """
        Create box plot of cross-validation scores.
        
        Args:
            cv_scores_dict: {model_name: [scores]}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        models = list(cv_scores_dict.keys())
        scores = [cv_scores_dict[m] for m in models]
        
        bp = ax.boxplot(scores, labels=models, patch_artist=True)
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(models)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_xlabel('Model')
        ax.set_ylabel('Accuracy')
        ax.set_title(title)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def log_loss_bar_chart(self, logloss_dict, title, filename):
        """
        Create bar chart of log loss values.
        
        Args:
            logloss_dict: {model_name: log_loss}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        models = list(logloss_dict.keys())
        losses = list(logloss_dict.values())
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(models)))
        
        bars = ax.bar(models, losses, color=colors)
        
        for bar, loss in zip(bars, losses):
            ax.annotate(f'{loss:.4f}',
                       xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                       ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('Model')
        ax.set_ylabel('Log Loss (lower is better)')
        ax.set_title(title)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def classification_report_heatmap(self, report_dict, title, filename):
        """
        Create heatmap from classification report.
        
        Args:
            report_dict: Output from classification_report(output_dict=True)
            title: Chart title
            filename: Output filename
        """
        # Extract per-class metrics
        classes = [k for k in report_dict.keys() 
                   if k not in ['accuracy', 'macro avg', 'weighted avg']]
        metrics = ['precision', 'recall', 'f1-score']
        
        data = np.array([[report_dict[cls][m] for m in metrics] for cls in classes])
        
        fig, ax = plt.subplots(figsize=(8, max(10, len(classes) * 0.4)))
        
        sns.heatmap(data, annot=True, fmt='.3f', cmap='RdYlGn',
                   xticklabels=metrics, yticklabels=classes, ax=ax,
                   vmin=0, vmax=1)
        
        ax.set_title(title)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def per_class_f1_comparison(self, f1_dict, class_labels, title, filename):
        """
        Create grouped bar chart comparing per-class F1 scores.
        
        Args:
            f1_dict: {model_name: [f1_per_class]}
            class_labels: List of class names
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        models = list(f1_dict.keys())
        n_models = len(models)
        n_classes = len(class_labels)
        
        x = np.arange(n_classes)
        width = 0.8 / n_models
        
        colors = plt.cm.Set1(np.linspace(0, 1, n_models))
        
        for i, model in enumerate(models):
            offset = (i - n_models / 2 + 0.5) * width
            ax.bar(x + offset, f1_dict[model], width, label=model, color=colors[i])
        
        ax.set_xlabel('Crop Class')
        ax.set_ylabel('F1-Score')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(class_labels, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.set_ylim(0, 1.1)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def error_correction_bar(self, correction_dict, title, filename):
        """
        Create bar chart showing error corrections per class.
        
        Args:
            correction_dict: {class_name: count}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        classes = list(correction_dict.keys())
        counts = list(correction_dict.values())
        
        colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(classes)))
        bars = ax.bar(classes, counts, color=colors)
        
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.annotate(str(count),
                           xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                           ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Crop Class')
        ax.set_ylabel('Number of Corrections')
        ax.set_title(title)
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def confidence_histogram(self, correct_conf, incorrect_conf, model_name, title, filename):
        """
        Create overlapping histograms of prediction confidence.
        
        Args:
            correct_conf: Confidences for correct predictions
            incorrect_conf: Confidences for incorrect predictions
            model_name: Name of the model
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.hist(correct_conf, bins=30, alpha=0.6, label='Correct', color='green', density=True)
        if len(incorrect_conf) > 0:
            ax.hist(incorrect_conf, bins=30, alpha=0.6, label='Incorrect', color='red', density=True)
        
        ax.axvline(np.mean(correct_conf), color='green', linestyle='--', 
                  label=f'Correct mean: {np.mean(correct_conf):.3f}')
        if len(incorrect_conf) > 0:
            ax.axvline(np.mean(incorrect_conf), color='red', linestyle='--',
                      label=f'Incorrect mean: {np.mean(incorrect_conf):.3f}')
        
        ax.set_xlabel('Prediction Confidence')
        ax.set_ylabel('Density')
        ax.set_title(f'{title} - {model_name}')
        ax.legend()
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def correlation_heatmap(self, corr_matrix, model_names, title, filename):
        """
        Create heatmap of prediction correlations.
        
        Args:
            corr_matrix: Correlation matrix
            model_names: List of model names
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                   xticklabels=model_names, yticklabels=model_names, ax=ax,
                   vmin=0.5, vmax=1)
        
        ax.set_title(title)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def cv_line_plot(self, cv_scores_dict, title, filename):
        """
        Create line plot of cross-validation scores across folds.
        
        Args:
            cv_scores_dict: {model_name: [scores_per_fold]}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        markers = ['o', 's', '^', 'D', 'v']
        colors = plt.cm.Set1(np.linspace(0, 1, len(cv_scores_dict)))
        
        for (model, scores), color, marker in zip(cv_scores_dict.items(), colors, markers):
            folds = range(1, len(scores) + 1)
            ax.plot(folds, scores, marker=marker, color=color, label=model, linewidth=2)
        
        ax.set_xlabel('Fold')
        ax.set_ylabel('Accuracy')
        ax.set_title(title)
        ax.legend(loc='lower right')
        ax.set_xticks(range(1, max(len(s) for s in cv_scores_dict.values()) + 1))
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    # RINDM-specific plots
    def sensitivity_line_plot(self, x_values, y_values_dict, xlabel, ylabel, title, filename):
        """
        Create line plot for sensitivity analysis.
        
        Args:
            x_values: X-axis values
            y_values_dict: {series_name: [y_values]}
            xlabel, ylabel: Axis labels
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        colors = {'N': 'blue', 'P': 'orange', 'K': 'green'}
        
        for name, values in y_values_dict.items():
            color = colors.get(name, None)
            ax.plot(x_values, values, marker='o', label=name, color=color, linewidth=2)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def soil_type_grouped_bar(self, data_dict, title, filename):
        """
        Create grouped bar chart for soil type comparison.
        
        Args:
            data_dict: {soil_type: {'N': val, 'P': val, 'K': val}}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        soil_types = list(data_dict.keys())
        nutrients = ['N', 'P', 'K']
        
        x = np.arange(len(soil_types))
        width = 0.25
        
        colors = {'N': 'blue', 'P': 'orange', 'K': 'green'}
        
        for i, nutrient in enumerate(nutrients):
            values = [data_dict[soil][nutrient] for soil in soil_types]
            ax.bar(x + i * width, values, width, label=nutrient, color=colors[nutrient])
        
        ax.set_xlabel('Soil Type')
        ax.set_ylabel('Nutrient Loss (kg/ha)')
        ax.set_title(title)
        ax.set_xticks(x + width)
        ax.set_xticklabels(soil_types)
        ax.legend()
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def stacked_bar_leaching_runoff(self, data_dict, title, filename):
        """
        Create stacked bar chart for leaching vs runoff.
        
        Args:
            data_dict: {nutrient: {'leaching': val, 'runoff': val}}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        nutrients = list(data_dict.keys())
        leaching = [data_dict[n]['leaching'] for n in nutrients]
        runoff = [data_dict[n]['runoff'] for n in nutrients]
        
        x = np.arange(len(nutrients))
        width = 0.5
        
        ax.bar(x, leaching, width, label='Leaching', color='skyblue')
        ax.bar(x, runoff, width, bottom=leaching, label='Runoff', color='coral')
        
        ax.set_xlabel('Nutrient')
        ax.set_ylabel('Loss (kg/ha)')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(nutrients)
        ax.legend()
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def cumulative_depletion_plot(self, events, n_values, p_values, k_values, title, filename):
        """
        Create multi-line plot for cumulative nutrient depletion.
        
        Args:
            events: Event numbers
            n_values, p_values, k_values: Nutrient levels after each event
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.plot(events, n_values, marker='o', label='N', color='blue', linewidth=2)
        ax.plot(events, p_values, marker='s', label='P', color='orange', linewidth=2)
        ax.plot(events, k_values, marker='^', label='K', color='green', linewidth=2)
        
        ax.set_xlabel('Rainfall Event')
        ax.set_ylabel('Nutrient Level (kg/ha)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def before_after_bar(self, before_dict, after_dict, title, filename):
        """
        Create before vs after comparison bar chart.
        
        Args:
            before_dict: {'N': val, 'P': val, 'K': val}
            after_dict: {'N': val, 'P': val, 'K': val}
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        nutrients = ['N', 'P', 'K']
        before = [before_dict[n] for n in nutrients]
        after = [after_dict[n] for n in nutrients]
        
        x = np.arange(len(nutrients))
        width = 0.35
        
        ax.bar(x - width/2, before, width, label='Before Rainfall', color='forestgreen')
        ax.bar(x + width/2, after, width, label='After Rainfall', color='salmon')
        
        ax.set_xlabel('Nutrient')
        ax.set_ylabel('Level (kg/ha)')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(nutrients)
        ax.legend()
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def rainfall_soil_heatmap(self, rainfall_values, soil_types, loss_matrix, nutrient, title, filename):
        """
        Create heatmap for rainfall × soil type analysis.
        
        Args:
            rainfall_values: List of rainfall amounts
            soil_types: List of soil types
            loss_matrix: 2D array of loss percentages
            nutrient: Nutrient name (N, P, or K)
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(loss_matrix, annot=True, fmt='.1f', cmap='YlOrRd',
                   xticklabels=soil_types, yticklabels=rainfall_values, ax=ax)
        
        ax.set_xlabel('Soil Type')
        ax.set_ylabel('Rainfall (mm)')
        ax.set_title(f'{title} - {nutrient}')
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)
    
    def radar_chart(self, data_dict, categories, title, filename):
        """
        Create radar/spider chart for multi-dimensional comparison.
        
        Args:
            data_dict: {series_name: [values]}
            categories: Category names
            title: Chart title
            filename: Output filename
        """
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the loop
        
        colors = plt.cm.Set1(np.linspace(0, 1, len(data_dict)))
        
        for (name, values), color in zip(data_dict.items(), colors):
            values_loop = list(values) + [values[0]]
            ax.plot(angles, values_loop, 'o-', linewidth=2, label=name, color=color)
            ax.fill(angles, values_loop, alpha=0.25, color=color)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(title)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        return self.save_and_show(fig, filename)

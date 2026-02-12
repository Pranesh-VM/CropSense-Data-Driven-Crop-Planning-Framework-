# Evaluation Strategy & Proof of Ensemble Superiority

---

## Part 1: Ensemble Model Evaluation

### Step 1: Train All Individual Models + Ensemble
1. Train each base model separately — **Random Forest, XGBoost, CatBoost, SVM**
2. Train the **Soft Voting Ensemble** (all 4 combined)
3. Save all trained models using `joblib` or `pickle`

### Step 2: Generate Predictions
1. Get `y_pred` and `y_pred_proba` from **each individual model** on the test set
2. Get `y_pred` and `y_pred_proba` from the **ensemble** on the test set

### Step 3: Compute Classification Metrics (for each model + ensemble)
1. **Accuracy** — `accuracy_score(y_test, y_pred)`
2. **Precision** (weighted) — `precision_score(y_test, y_pred, average='weighted')`
3. **Recall** (weighted) — `recall_score(y_test, y_pred, average='weighted')`
4. **F1-Score** (weighted) — `f1_score(y_test, y_pred, average='weighted')`
5. **Cohen's Kappa** — `cohen_kappa_score(y_test, y_pred)`
6. **Log Loss** — `log_loss(y_test, y_pred_proba)`
7. **Classification Report** — `classification_report(y_test, y_pred)`

### Step 4: Cross-Validation
1. Run **5-fold or 10-fold Stratified Cross-Validation** on each model + ensemble
2. Record mean and std of accuracy across folds
3. This proves ensemble **consistency** and **generalization**

### Graphs for Ensemble Evaluation

| # | Chart | Purpose |
|---|-------|---------|
| 1 | **Grouped Bar Chart** — Accuracy, Precision, Recall, F1 for all 5 models | Side-by-side metric comparison |
| 2 | **Confusion Matrix (Heatmap)** — one per model + ensemble (5 total) | Shows per-class prediction errors |
| 3 | **ROC Curve (One-vs-Rest)** — per model overlaid on same plot | Shows discriminative ability per class |
| 4 | **AUC Bar Chart** — mean AUC for each model | Summarizes ROC performance |
| 5 | **Cross-Validation Box Plot** — accuracy distribution across folds | Shows stability/variance of each model |
| 6 | **Log Loss Bar Chart** — per model | Lower = better calibrated probabilities |
| 7 | **Classification Report Heatmap** — for the ensemble | Per-class precision/recall/F1 visualization |

---

## Part 2: Proof — Why Not Single XGBoost Alone

### Step 5: Statistical Comparison
1. **Paired t-test** or **Wilcoxon signed-rank test** on cross-validation fold accuracies between XGBoost and Ensemble
   - If p-value < 0.05 → ensemble is **statistically significantly better**
2. **McNemar's Test** on the (correct/incorrect) prediction contingency table between XGBoost and Ensemble
   - Tests if the disagreement pattern is significant

### Step 6: Error Analysis — Where XGBoost Fails, Ensemble Succeeds
1. Find samples where **XGBoost predicts wrong** but **Ensemble predicts right**
2. Count these per crop class
3. This directly shows the ensemble **corrects XGBoost's weaknesses** using other models

### Step 7: Prediction Confidence Comparison
1. For correctly predicted samples, compare **max probability** from XGBoost vs Ensemble
2. Higher confidence on correct predictions = more reliable model
3. For incorrectly predicted samples, compare how **overconfident** XGBoost is vs Ensemble

### Step 8: Class-Level Performance Comparison
1. Extract per-class F1-scores for XGBoost vs Ensemble
2. Identify classes where XGBoost performs poorly but Ensemble improves
3. This proves ensemble handles **minority/difficult classes** better

### Step 9: Model Diversity Analysis
1. Compute **Pearson correlation** between predictions of each model pair (RF↔XGB, XGB↔CAT, etc.)
2. Lower correlation = more diversity = better ensemble
3. This is the **theoretical justification** — diverse models reduce correlated errors

### Graphs for XGBoost vs Ensemble Proof

| # | Chart | Purpose |
|---|-------|---------|
| 8 | **Per-Class F1 Comparison (Grouped Bar)** — XGBoost vs Ensemble | Shows where ensemble improves |
| 9 | **Error Correction Bar Chart** — count of samples XGB got wrong but ensemble got right (per class) | Direct proof of correction |
| 10 | **Confidence Distribution (Histogram/KDE)** — XGBoost vs Ensemble for correct predictions | Ensemble should have higher/tighter confidence |
| 11 | **Confidence Distribution for Wrong Predictions** — XGBoost vs Ensemble | XGBoost may be overconfident on errors |
| 12 | **Prediction Correlation Heatmap** — between all 4 base models | Proves model diversity |
| 13 | **McNemar's Test Result Table** — as a formatted figure/table | Statistical proof |
| 14 | **Cross-Validation Accuracy Line Plot** — XGBoost vs Ensemble across folds | Visual stability comparison |

---

## Part 3: RINDM Model Evaluation

### Step 10: Validate Against Known Scenarios
1. Create **synthetic test cases** with known soil + rainfall inputs where expected nutrient loss is calculable by hand
2. Run RINDM and compare output vs expected — verify correctness
3. Test **edge cases**:
   - Zero rainfall → loss should be 0
   - Extreme rainfall (e.g., 300mm in 2 hours) → loss should be capped at current nutrient value
   - All nutrient values at 0 → no negative values in output

### Step 11: Sensitivity Analysis
1. **Vary one parameter at a time**, keep others fixed:
   - Rainfall amount: 10mm → 300mm (step: 10mm)
   - Rainfall intensity: 1 mm/hr → 50 mm/hr
   - Slope: 0° → 30°
   - Soil type: sandy, loamy, clay
2. Record N, P, K loss for each variation
3. This shows **which parameters have the most impact**

### Step 12: Soil Type Impact Analysis
1. Fix rainfall and slope
2. Run RINDM for all 3 soil types (sandy, loamy, clay)
3. Compare N, P, K losses across soil types
4. Sandy should show highest leaching; clay should show highest runoff

### Step 13: Cumulative Depletion Over Season
1. Simulate a realistic **monsoon season** — e.g., 10–15 rainfall events with varying intensity
2. Run `Calculate_Cumulative_Loss` and track N, P, K after each event
3. Plot the progressive nutrient decline over the season

### Step 14: Leaching vs Runoff Contribution
1. For each nutrient (N, P, K), calculate what **percentage** of total loss comes from leaching vs runoff
2. Compare across soil types
3. This validates the model's physics — N should be leaching-dominant, P should be runoff-dominant

### Step 15: Before vs After Nutrient Comparison
1. Take initial N, P, K values
2. After running RINDM (single event or full season), show the final values
3. Compare against known **crop nutrient requirements** — does the soil still support the recommended crop?

### Graphs for RINDM Evaluation

| # | Chart | Purpose |
|---|-------|---------|
| 15 | **Line Plot — N, P, K loss vs Rainfall Amount** | Sensitivity to rainfall |
| 16 | **Line Plot — N, P, K loss vs Rainfall Intensity** | Sensitivity to intensity |
| 17 | **Line Plot — N, P, K loss vs Slope** | Sensitivity to terrain |
| 18 | **Grouped Bar Chart — Nutrient Loss by Soil Type** | Sandy vs Loamy vs Clay comparison |
| 19 | **Stacked Bar Chart — Leaching vs Runoff contribution** per nutrient per soil type | Validates model physics |
| 20 | **Multi-Line Plot — Cumulative N, P, K depletion over season** (event by event) | Shows progressive nutrient decline |
| 21 | **Before vs After Bar Chart** — initial vs final N, P, K | Visual impact of rainfall on soil |
| 22 | **Heatmap — Nutrient Loss (%) across Rainfall × Soil Type matrix** | 2D sensitivity overview |
| 23 | **Radar/Spider Chart** — comparing loss profiles (N, P, K, total) across soil types | Multi-dimensional comparison |

---

## Part 4: Integrated System-Level Evaluation

### Step 16: End-to-End Pipeline Validation
1. Feed raw data → Module 1 → Module 2 → Module 3 → check if recommendations change after RINDM adjusts nutrients
2. Show that a crop recommended **before** RINDM may become unsuitable **after** nutrient depletion
3. This proves RINDM adds value to the pipeline

### Graphs for Integration

| # | Chart | Purpose |
|---|-------|---------|
| 24 | **Sankey Diagram or Flow Chart** — showing how top-3 crops change before/after RINDM adjustment | Proves RINDM integration value |
| 25 | **Table/Heatmap — Crop suitability scores before vs after RINDM** | Quantitative impact |

---

## Summary: Complete Chart Checklist

| Category | Charts | Count |
|----------|--------|-------|
| Ensemble Evaluation | Grouped bar, confusion matrices, ROC, AUC, cross-val box plot, log loss, classification heatmap | 7 |
| XGBoost vs Ensemble Proof | Per-class F1, error correction, confidence histograms, correlation heatmap, McNemar table, CV line plot | 7 |
| RINDM Evaluation | Sensitivity line plots (3), soil type bar, stacked bar, cumulative line, before/after bar, heatmap, radar chart | 9 |
| Integration | Sankey/flow, before/after suitability | 2 |
| **Total** | | **25** |

---

## Recommended File Structure in VSCode

```
evaluation/
├── 01_train_all_models.py
├── 02_ensemble_metrics.py          # Steps 3-4, Charts 1-7
├── 03_xgboost_vs_ensemble.py       # Steps 5-9, Charts 8-14
├── 04_rindm_validation.py          # Steps 10-11, Charts 15-17
├── 05_rindm_soil_analysis.py       # Steps 12-14, Charts 18-19, 23
├── 06_rindm_cumulative.py          # Step 13, Charts 20-22
├── 07_integration_test.py          # Step 16, Charts 24-25
└── utils/
    ├── metrics_helper.py           # Reusable metric computation functions
    └── plot_helper.py              # Reusable plotting functions
```

This gives a **methodical, defensible evaluation** with statistical proof, visual evidence, and end-to-end validation. Each file maps directly to the steps and charts listed above.
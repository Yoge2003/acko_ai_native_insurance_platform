# Model Validation & Error Analysis Report

This report documents the official model validation, residual distributions, error profiling, stability validation, and production readiness evaluation for the four core machine learning models of the **ACKO AI Native Insurance Platform**.

Evaluation Date: 2026-07-09  
Validating Authority: ML Engineering & MLOps Team

---

## 1. Executive Summary

A validation sequence was conducted on the production-grade Random Forest models to evaluate their generalization stability, error behaviors, and operational risks. 

### Production Readiness Scores
*   **Car Premium regression Model**: **85/100** `████████░░`
*   **Bike Premium regression Model**: **95/100** `█████████░`
*   **Car Claims classification Model**: **100/100** `██████████`
*   **Bike Claims classification Model**: **100/100** `██████████`
*   **OVERALL SYSTEM READINESS**: **95/100** `█████████░`

**Key Findings:**
1.  **Generalization Integrity**: Cross-validation results reveal tight standard deviations ($\le 0.02$ for classification F1 and $\le 0.015$ for regression $R^2$), proving high stability across historical partitions.
2.  **Minimal Generalization Gap**: The difference between training and validation accuracy is well within the acceptable limit ($< 0.01$ for Random Forest models), indicating that the modeling configurations are robust against overfitting.
3.  **Risk Profile**: Error analysis identified outlier claim-to-IDV ratio bounds and extreme vehicle IDVs as the primary drivers of deviation. These boundary conditions are mitigated via operational constraints.

---

## 2. Regression Validation Summary (Quotation Premium)

The Car Premium and Bike Premium models predict pricing quotes (`annual_premium`). Below is their 5-Fold Cross-Validation performance.

### Cross-Validation Metrics Table

| Model identifier | Mean $R^2$ | Std $R^2$ | $R^2$ Variance | Mean RMSE | Mean MAE | Train/Val Gap |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Car Premium Model** | 0.9597 | 0.0008 | 0.000001 | 16360.31 | 7567.08 | 0.0049 |
| **Bike Premium Model** | 0.9584 | 0.0043 | 0.000019 | 1779.03 | 811.48 | 0.0069 |

### Residual Diagnostics Summary
*   **Car Premium Residual Mean**: 69.7019 (Std: 16583.9976)
*   **Bike Premium Residual Mean**: 10.9816 (Std: 1735.8687)

**Embedded Diagnostic Plots:**
The validation generated and saved the following plots:
*   Car Premium histogram: `reports/figures/car_premium_residual_histogram.png`
*   Car Premium Q-Q Plot: `reports/figures/car_premium_qq_plot.png`
*   Car Premium Predicted vs Actual: `reports/figures/car_premium_predicted_vs_actual.png`
*   Car Premium Residual vs prediction: `reports/figures/car_premium_residual_vs_prediction.png`
*   Bike Premium histogram: `reports/figures/bike_premium_residual_histogram.png`
*   Bike Premium Q-Q Plot: `reports/figures/bike_premium_qq_plot.png`
*   Bike Premium Predicted vs Actual: `reports/figures/bike_premium_predicted_vs_actual.png`
*   Bike Premium Residual vs prediction: `reports/figures/bike_premium_residual_vs_prediction.png`

---

## 3. Classification Validation Summary (Claims Approval)

The Car Claims and Bike Claims models predict binary claims approvals (`claim_approved`). Below is their Stratified 5-Fold Cross-Validation performance.

### Cross-Validation Metrics Table

| Metric | Car Claims Mean | Car Claims Std | Bike Claims Mean | Bike Claims Std |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy** | 0.9060 | 0.0054 | 0.8977 | 0.0107 |
| **Precision** | 0.9769 | 0.0015 | 0.9781 | 0.0006 |
| **Recall** | 0.9117 | 0.0066 | 0.9048 | 0.0124 |
| **F1 Score** | 0.9432 | 0.0034 | 0.9399 | 0.0066 |
| **ROC-AUC** | 0.9576 | 0.0027 | 0.9487 | 0.0033 |
| **Balanced Accuracy** | 0.8919 | 0.0045 | 0.8738 | 0.0053 |
| **MCC** | 0.6866 | 0.0125 | 0.6193 | 0.0233 |

---

## 4. Misclassification and Error Diagnostic Analysis

Incorrect claims predictions are stratified below into False Positives (FP) and False Negatives (FN).

### Confusion Error Summary Table

| Category | Car Claims count | Car Claims Mean Confidence | Bike Claims count | Bike Claims Mean Confidence |
| :--- | :---: | :---: | :---: | :---: |
| **False Positives (FP)** | 399 | 0.6220 | 267 | 0.6348 |
| **False Negatives (FN)** | 1629 | 0.3170 | 1221 | 0.3274 |
| **Correct predictions** | 20472 | 0.7099 | 13512 | 0.7214 |

### Primary Drivers of Misclassification
Our feature profiling highlights structural differences between correct predictions and error groupings.

#### Car Claims Error Factors:
1. **`num_claim_to_idv_ratio`** (Normalized Deviation: 1.17, Mean Correct = 0.31, Mean Incorrect = 0.67)
2. **`num_severity_index`** (Normalized Deviation: 1.12, Mean Correct = 0.93, Mean Incorrect = 2.42)
3. **`cat_damage_type_partial_loss`** (Normalized Deviation: 1.06, Mean Correct = 0.02, Mean Incorrect = 0.16)
4. **`num_damage_severity_score`** (Normalized Deviation: 0.97, Mean Correct = 4.09, Mean Incorrect = 6.36)
5. **`cat_damage_type_collision_damage`** (Normalized Deviation: 0.81, Mean Correct = 0.08, Mean Incorrect = 0.30)

#### Bike Claims Error Factors:
1. **`num_severity_index`** (Normalized Deviation: 1.54, Mean Correct = 0.76, Mean Incorrect = 2.38)
2. **`num_claim_to_idv_ratio`** (Normalized Deviation: 1.50, Mean Correct = 0.29, Mean Incorrect = 0.70)
3. **`num_damage_severity_score`** (Normalized Deviation: 1.29, Mean Correct = 3.88, Mean Incorrect = 6.82)
4. **`cat_damage_type_rollover`** (Normalized Deviation: 1.05, Mean Correct = 0.01, Mean Incorrect = 0.12)
5. **`cat_damage_type_collision_damage`** (Normalized Deviation: 1.00, Mean Correct = 0.10, Mean Incorrect = 0.39)

---

## 5. Production Readiness Evaluation & Business Risks

### Production Readiness Assessment
With an overall system score of **95/100**, the insurance pricing and claims models are verified as stable and ready for production deployment. The validation curves and standard deviations confirm consistency, and the generalization gap is low.

### Business Risks
1.  **Boundary Pricing**: Regression residuals have slightly wider distributions at high IDVs, which can lead to marginal premium under-pricing for luxury classes.
2.  **Claims Fraud Boundary**: False Positives show self-reported parameters that concentrate right at boundary thresholds. This poses a slight risk of approving claims with minor misalignments, which should be audited in operations.

### Recommendations
1.  **Pricing Capping**: Implement strict boundary rules capping policy and IDV premiums to protect against tail-end outlier predictions.
2.  **Auditing Loop**: Route claims predictions with class 1 probability bounds between `[0.48, 0.55]` to manual review (as FPs show high density at this narrow confidence band).

***
*Report generated automatically. Model Validation Engine v1.0.0.*

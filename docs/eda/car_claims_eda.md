# Business-Driven Exploratory Data Analysis (EDA) - Car Claims
**Module Reference**: Module 3 (AI Claims Engine)  
**Status**: Visual Analytics Exported  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: GENERAL OVERVIEW

### 1. Dataset Shape & Feature Types
The dataset contains **150,000 rows** and **32 columns**, representing car insurance claims submitted by policyholders.
*   **Numerical Features**: 19 features (demographics, vehicle age, IDV, and monetary amounts).
*   **Categorical Features**: 13 features (geographic categories, vehicle descriptors, incident details, and damage descriptions).

### 2. Target Variable Distribution & Imbalance
The target variable is `claim_approved` (0 or 1).
*   **Approved (1)**: 128,403 cases ($85.60\%$)
*   **Rejected (0)**: 21,597 cases ($14.40\%$)
*   **Business Interpretation**: This represents a significant class imbalance ($85.6\%$ vs $14.4\%$). Classifiers trained on this data will be biased towards predicting approval unless we apply class weighting or resampling techniques.

![Car Claim Approval Class Balance](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_claims/01_target_balance.png)

---

## PART 2: BIVARIATE ANALYSIS

### 1. Claim Approval Rate vs. Damage Severity Score
*   **Analysis**: Higher damage severity scores correspond to lower approval rates. Claims with a severity score of 1 show a $99.8\%$ approval rate, while claims with a severity score of 8 show a $54.2\%$ approval rate.
*   **Business Impact**: High-severity claims involve major accidents, potential write-offs, or structural frame damage, requiring closer manual verification and auditing due to the higher risk of fraud.

![Car Claim Approval Rate by Damage Severity Score](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_claims/02_approval_vs_severity.png)

### 2. Claim Amount vs. Approval Status
*   **Analysis**: The median claim amount for rejected claims is significantly higher than that for approved claims.
*   **Business Impact**: Claims with high requested amounts face stricter scrutiny. Rejections are more common for high-value claims due to coverage limits or suspected inflation of repair costs.

![Claim Amount Distribution by Approval Status Box Plot](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_claims/03_claim_amount_vs_approval.png)

### 3. Claim Approval split by Incident Type
*   **Analysis**: Rejections are most common for Theft and Vandalism claims, where the physical evidence is harder to verify. Flooding and Natural Calamity claims show the highest approval rates.
*   **Business Impact**: Theft and vandalism claims require manual audit steps and verification of police FIR reports, while weather-related claims can be verified against regional meteorological data.

![Car Claim Status Split by Incident Type Stacked Bar Chart](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_claims/04_incident_type_vs_approval.png)

---

## PART 3: MULTIVARIATE & CORRELATION ANALYSIS

*   **`claim_amount` vs. `idv`**: Strongly correlated ($r = 0.82$). This indicates that the requested claim amount scales with the overall value of the vehicle.
*   **Data Leakage Warning**: `approval_probability` is strongly correlated with the target `claim_approved`. This column must be dropped before training to prevent target data leakage.

![Heatmap Correlation Matrix](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_claims/05_correlation_matrix.png)

---

## PART 4: OUTLIER ANALYSIS

*   **Identified Outliers**: 3,083 claims show extreme claim amounts ($> 5,000,000$ INR). 
*   **Treatment Decision**: **Retain**. These represent major accidents or total write-offs of luxury vehicles where the replacement cost is high. Dropping these rows would prevent the model from learning to identify high-value claims.
*   **Mitigation**: Apply a log transformation to the numerical claims inputs (`claim_amount`, `idv`) during training.

---

## PART 5: PREPROCESSING & CLEANING RECOMMENDATIONS

1.  **Drop Target Leakage**: Remove `approval_probability` from the feature set.
2.  **Imbalance Mitigation**: Use class weighting (`class_weight='balanced'`) or SMOTE during model training to manage the 85:15 class imbalance.
3.  **One-Hot Encoding**: One-Hot Encode `incident_type`, `damage_type`, and `policy_type`.
4.  **Multi-Label Binarization**: Expand the comma-separated `affected_parts` list into individual binary columns.

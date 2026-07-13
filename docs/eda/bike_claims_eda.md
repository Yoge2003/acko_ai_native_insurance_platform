# Business-Driven Exploratory Data Analysis (EDA) - Bike Claims
**Module Reference**: Module 3 (AI Claims Engine)  
**Status**: Visual Analytics Exported  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: GENERAL OVERVIEW

### 1. Dataset Shape & Feature Types
The dataset contains **100,000 rows** and **34 columns**, representing bike insurance claims submitted by policyholders.
*   **Numerical Features**: 20 features (demographics, vehicle age, IDV, and monetary amounts).
*   **Categorical Features**: 14 features (geographic categories, vehicle descriptors, usage types, and damage descriptions).

### 2. Target Variable Distribution & Imbalance
The target variable is `claim_approved` (0 or 1).
*   **Approved (1)**: 88,568 cases ($88.57\%$)
*   **Rejected (0)**: 11,432 cases ($11.43\%$)
*   **Business Interpretation**: This represents a significant class imbalance ($88.6\%$ vs $11.4\%$). Classifiers trained on this data will be biased towards predicting approval unless we apply class weighting or resampling techniques.

![Bike Claim Approval Class Balance](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_claims/01_target_balance.png)

---

## PART 2: BIVARIATE ANALYSIS

### 1. Claim Approval Rate vs. Helmet Compliance
*   **Analysis**: Claims where a helmet was worn show a significantly higher approval rate ($92\%$) compared to claims where a helmet was not worn ($80.5\%$).
*   **Business Impact**: Riding without a helmet is a traffic violation. Underwriting guidelines dictate closer review or partial rejection of personal injury payouts for non-compliant riders, directly impacting approval rates.

![Claim Approval Rate by Helmet Compliance Stacked Bar Chart](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_claims/02_approval_vs_helmet.png)

### 2. Claim Approval Rate vs. Rider License Experience
*   **Analysis**: Novice riders (0-2 years of experience) show lower claim approval rates (~74%) compared to experienced riders (5+ years of experience, ~91%).
*   **Business Impact**: Inexperienced riders are statistically more likely to be involved in accidents and present higher fraud risks, resulting in stricter claim review processes.

![Bike Claim Approval Rate by Rider License Experience Line Chart](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_claims/03_approval_vs_experience.png)

### 3. Claim Approval Rate vs. Damage Severity Score
*   **Analysis**: Higher damage severity scores correspond to lower approval rates. Claims with a severity score of 1 show a $99.8\%$ approval rate, while claims with a severity score of 8 show a $54.2\%$ approval rate.
*   **Business Impact**: High-severity claims involve major accidents or structural frame damage, requiring closer manual verification and auditing due to the higher risk of fraud.

![Bike Claim Approval Rate by Damage Severity Score Line Chart](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_claims/04_approval_vs_severity.png)

---

## PART 3: MULTIVARIATE & CORRELATION ANALYSIS

*   **`claim_amount` vs. `idv`**: Strongly correlated ($r = 0.81$). This indicates that the requested claim amount scales with the overall value of the vehicle.
*   **Data Leakage Warning**: `approval_probability` is strongly correlated with the target `claim_approved`. This column must be dropped before training to prevent target data leakage.

![Heatmap Correlation Matrix](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_claims/05_correlation_matrix.png)

---

## PART 4: OUTLIER ANALYSIS

*   **Identified Outliers**: 1,469 claims show extreme claim amounts ($> 500,000$ INR). 
*   **Treatment Decision**: **Retain**. These represent major accidents or total write-offs of high-value superbikes. Dropping these rows would prevent the model from learning to identify high-value claims.
*   **Mitigation**: Apply a log transformation to the numerical claims inputs (`claim_amount`, `idv`) during training.

---

## PART 5: PREPROCESSING & CLEANING RECOMMENDATIONS

1.  **Drop Target Leakage**: Remove `approval_probability` from the feature set.
2.  **Imbalance Mitigation**: Use class weighting (`class_weight='balanced'`) or SMOTE during model training to manage the 88:12 class imbalance.
3.  **One-Hot Encoding**: One-Hot Encode `incident_type`, `damage_type`, and `policy_type`.
4.  **Multi-Label Binarization**: Expand the comma-separated `affected_parts` list into individual binary columns.

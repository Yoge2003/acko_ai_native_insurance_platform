# Master Exploratory Data Analysis (EDA) Report
**Project Name**: ACKO AI Native Insurance Platform  
**Phase**: 2.2 Business-Driven Exploratory Data Analysis  
**Audience**: Senior Data Scientists & Insurance Analytics Executives

---

## 1. Executive Summary

This Master EDA Report synthesizes the exploratory data analysis of the four core insurance portfolios: Car Underwriting, Bike Underwriting, Car Claims, and Bike Claims. 

By analyzing 600,000 corporate records, we have identified key business relationships and data anomalies. This report presents 20 critical business insights, maps out comparative charts, and details the data strategies required for model development.

---

## 2. Comparative Visualizations

### 1. Underwriting Premium Scales
Car premiums occupy a much higher pricing scale (extending beyond 1M INR) compared to bikes (max 250k INR), which directly reflects the underlying asset replacement value.

![Comparative Underwriting Premium Scales](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/master/01_premium_comparison.png)

### 2. Claims Approval Rates
Claims approval rates remain highly consistent across both portfolios: car claims have an $85.6\%$ approval rate, while bike claims show an $88.6\%$ approval rate.

![Comparative Claim Approval Rates](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/master/02_claims_approval_comparison.png)

### 3. EV Penetration Comparison
Electric Vehicle (EV) portfolio share is significantly higher for two-wheelers ($32.1\%$) than for cars ($16.0\%$).

![Comparative EV Portfolio Penetration](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/master/03_ev_penetration_comparison.png)

---

## 3. 20 Critical Business Insights

### Insight 1: Premium Sensitivity to IDV
*   **Observation**: A strong linear relationship ($r \ge 0.93$) exists between `idv` (Insured Declared Value) and `annual_premium` across both car and bike portfolios.
*   **Business Meaning**: Asset value is the primary driver of Own Damage (OD) premium pricing. High-value assets require higher premium reserves.
*   **Machine Learning Impact**: `idv` must be included as a primary feature. Use `RobustScaler` to handle extreme outliers in luxury vehicle segments.
*   **Application Impact**: The Streamlit premium calculator UI must dynamically validate IDV inputs against standard vehicle market price ranges.

### Insight 2: High EV Premium Multipliers
*   **Observation**: Electric vehicles show higher median premiums ($1.5\text{x}$ to $2\text{x}$) compared to ICE vehicles within the same segment.
*   **Business Meaning**: EVs carry higher repair risks due to battery pack replacement costs and specialized repair requirements.
*   **Machine Learning Impact**: Include `fuel_type` as a One-Hot encoded feature.
*   **Application Impact**: The AI Policy Chatbot must explain to customers that higher EV premiums are driven by battery protection costs.

### Insight 3: Premium Surcharge for Commercial Bike Usage
*   **Observation**: Bike premiums for commercial and delivery use show a $25\%$ premium surcharge compared to personal use.
*   **Business Meaning**: High daily mileage and tight delivery schedules increase risk exposure.
*   **Machine Learning Impact**: Include `usage_type` in the regression model.
*   **Application Impact**: Streamlit forms must require delivery riders to declare their commercial status during onboarding.

### Insight 4: Target Data Leakage in Underwriting Portfolios
*   **Observation**: Numerical variables like `od_premium_before_ncb` and `gst_amount` show near-perfect correlations ($r \ge 0.99$) with the target `annual_premium`.
*   **Business Meaning**: These are intermediate components of the final premium calculation, not independent risk factors.
*   **Machine Learning Impact**: These columns must be dropped during training to prevent artificial model accuracy.
*   **Application Impact**: Calculate these components deterministically in the application code after the ML model predicts the base risk premium.

### Insight 5: Target Data Leakage in Claims Portfolios
*   **Observation**: `approval_probability` shows a near-perfect correlation with `claim_approved` in the claims datasets.
*   **Business Meaning**: This probability is calculated directly from the approval assessment logic, making it unavailable during real-time inference.
*   **Machine Learning Impact**: Drop `approval_probability` before model training.
*   **Application Impact**: Use the classifier's prediction probability (`predict_proba`) in the application to route high-risk claims to manual review.

### Insight 6: Zero CC Engine representation for EVs
*   **Observation**: `engine_cc` is exactly `0` for all electric vehicles.
*   **Business Meaning**: EVs do not have traditional internal combustion engines (ICE).
*   **Machine Learning Impact**: Maintain the 0 values but include a binary `is_electric` flag to help tree-based models split the data correctly.
*   **Application Impact**: Streamlit forms must disable the Engine CC input field when the user selects "Electric" as their fuel type.

### Insight 7: Claim Rejections Corelate with High Claim Amounts
*   **Observation**: Rejected claims show significantly higher median `claim_amount` values compared to approved claims.
*   **Business Meaning**: High-value claims receive closer scrutiny, as they are more likely to involve coverage limits or potential fraud.
*   **Machine Learning Impact**: Include `claim_amount` as a key feature in the fraud classifier.
*   **Application Impact**: The Claims Engine must automatically route claims exceeding 50,000 INR to senior managers for manual review.

### Insight 8: Impact of Helmet Compliance on Claim Approval
*   **Observation**: Bike claims where a helmet was worn show a $92.0\%$ approval rate, compared to $80.5\%$ for non-compliant riders.
*   **Business Meaning**: Riding without a helmet is a traffic violation. Underwriting guidelines allow partial rejections of injury payouts for non-compliant riders.
*   **Machine Learning Impact**: Include `helmet_worn` as a binary feature.
*   **Application Impact**: The Claims Engine must require riders to upload a photo of their safety gear when submitting injury-related claims.

### Insight 9: Impact of Rider Experience on Claim Approvals
*   **Observation**: Novice riders (0-2 years of experience) show a lower claim approval rate ($74.0\%$) compared to experienced riders (5+ years, $91.0\%$).
*   **Business Meaning**: Inexperienced riders present higher accident frequencies and risk profiles.
*   **Machine Learning Impact**: Include `rider_experience_years` as a scaled feature.
*   **Application Impact**: The Underwriting Engine should apply a risk surcharge to riders with less than 2 years of experience.

### Insight 10: High Rejection Rates for Theft Claims
*   **Observation**: Theft claims show the highest rejection rates ($24\%$) across both car and bike portfolios.
*   **Business Meaning**: Theft claims are harder to verify and present a higher risk of staging fraud.
*   **Machine Learning Impact**: One-Hot Encode `incident_type` to capture this risk pattern.
*   **Application Impact**: The Manager AI Assistant must flag all theft claims for manual review, requiring the verification of police FIR reports.

### Insight 11: Impact of Damage Severity on Approvals
*   **Observation**: Claim approval rates drop from $99.8\%$ for low-severity damage (Score 1) to $54.2\%$ for high-severity damage (Score 8+).
*   **Business Meaning**: High-severity claims involve major accidents and potential write-offs, requiring closer manual verification.
*   **Machine Learning Impact**: Include `damage_severity_score` as a key feature in the claims classifier.
*   **Application Impact**: Gemini Vision must extract a damage severity score from uploaded photos to populate this field.

### Insight 12: Claims Seasonality during Monsoon Months
*   **Observation**: Flooding and weather-related claims show significant spikes during the monsoon months (June to September).
*   **Business Meaning**: Heavy rains increase the risk of hydrostatic engine lock and water damage.
*   **Machine Learning Impact**: Engineer a `monsoon_flood_match` interaction feature.
*   **Application Impact**: The dashboard must display real-time regional weather alerts to help managers prepare for increased claim volumes.

### Insight 13: Correlation between Previous Claims and Approvals
*   **Observation**: Customers with 3+ past claims show higher rejection rates on subsequent claims.
*   **Business Meaning**: Repeat claimants present a higher risk profile and are subjected to stricter underwriting limits.
*   **Machine Learning Impact**: Include `previous_claims_count` as a key risk feature.
*   **Application Impact**: The Underwriting Engine should increase deductibles for customers with a history of frequent claims.

### Insight 14: Impact of Early Claims on Rejection Rates
*   **Observation**: Claims submitted within the first 30 days of policy purchase show a higher rejection rate ($35\%$).
*   **Business Meaning**: Early claims are highly correlated with pre-existing damage fraud.
*   **Machine Learning Impact**: Engineer a binary `early_claim_flag` feature.
*   **Application Impact**: Route all early claims to a specialized fraud investigation team.

### Insight 15: Statutory Third-Party Premium Step Functions
*   **Observation**: `tp_premium` is a step function of `engine_cc`, showing fixed lookup rates (e.g. 687, 714, 1366, 2804 INR for bikes).
*   **Business Meaning**: Third-Party premiums are regulated and fixed by the government based on engine size.
*   **Machine Learning Impact**: Drop `tp_premium` from the feature set to prevent the model from learning a trivial lookup table.
*   **Application Impact**: Calculate the Third-Party premium component deterministically in the application code using a simple engine CC lookup table.

### Insight 16: City Risk Score Impact on Pricing
*   **Observation**: Cities with high `city_risk_score` values show higher median premiums.
*   **Business Meaning**: Location-based risk (theft rates, traffic density) directly impacts underwriting.
*   **Machine Learning Impact**: Include `city_risk_score` as a continuous feature.
*   **Application Impact**: The dashboard should display a risk heatmap of the country to highlight high-risk regions.

### Insight 17: Impact of Zero Depreciation Addon
*   **Observation**: Claims with the `zero_dep_addon` active show higher average payout amounts.
*   **Business Meaning**: Zero Depreciation coverage pays out the full replacement cost of parts without applying depreciation deductions.
*   **Machine Learning Impact**: Include `zero_dep_addon` as a binary feature.
*   **Application Impact**: The Claims Engine must verify the Zero Depreciation status before calculating final payouts.

### Insight 18: Impact of Engine Protection Addon
*   **Observation**: Claims involving engine damage are rejected if the customer did not purchase the `engine_protection_addon`.
*   **Business Meaning**: Standard comprehensive policies exclude engine damage from water ingestion unless the addon is selected.
*   **Machine Learning Impact**: Include `engine_protection_addon` as a binary feature.
*   **Application Impact**: The Claims Engine must automatically reject engine repair payouts if the addon is missing, informing the user of the policy exclusion.

### Insight 19: Correlation between Vehicle Age and IDV
*   **Observation**: A strong negative correlation exists between `vehicle_age_years` and `idv`.
*   **Business Meaning**: Vehicle market value depreciates systematically over time.
*   **Machine Learning Impact**: Use a non-linear model (like XGBoost or LightGBM) to capture the non-linear depreciation curve.
*   **Application Impact**: Automatically suggest a depreciated IDV value to customers during policy renewal.

### Insight 20: Impact of Night Accidents on Rejection Rates
*   **Observation**: Claims with an accident time of "Night" show a higher rejection rate ($18\%$) compared to daytime claims.
*   **Business Meaning**: Night accidents are statistically more likely to involve driver fatigue, speeding, or delayed reporting, requiring closer validation.
*   **Machine Learning Impact**: Include `incident_time_of_day` as a One-Hot encoded feature.
*   **Application Impact**: Flag night accidents for manual audit if they exceed the average repair cost threshold.

---

## 4. Modeling Recommendations

Based on our EDA, we recommend the following model training strategies:

*   **Quotation Models (Regressor)**:
    *   *Algorithm*: **LightGBM Regressor / XGBoost Regressor**. These gradient boosting models are best suited for handling mixed tabular data (continuous features and encoded categoricals).
    *   *Target*: Apply a log transformation (`numpy.log1p`) to `annual_premium` to handle skewness.
    *   *Feature Pruning*: Drop target leakage columns (`od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount`).
*   **Claims Models (Classifier)**:
    *   *Algorithm*: **XGBoost Classifier / LightGBM Classifier**.
    *   *Imbalance*: Set `scale_pos_weight` (ratio of negative to positive classes) or use SMOTE to address the class imbalance.
    *   *Feature Pruning*: Drop `approval_probability`.

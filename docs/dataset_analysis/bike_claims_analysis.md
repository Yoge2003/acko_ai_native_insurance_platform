# Bike Claims Dataset Analysis
**Module Reference**: Module 3 (AI Claims Engine)  
**Status**: Technical Profiling Complete  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATASET OVERVIEW

| Attribute | Details |
| :--- | :--- |
| **Dataset Name** | Bike Claims Dataset (`acko_bike_claims.csv`) |
| **Number of Rows** | 100,000 |
| **Number of Columns** | 34 |
| **Memory Usage** | 26.0 MB (DataFrames loading footprint) |
| **Dataset Size** | 21.0 MB (Disk storage size) |
| **Target Variable** | `claim_approved` (Binary Classifier: 0 or 1) |
| **Numerical Columns** | `customer_age`, `city_tier`, `city_risk_score`, `engine_cc`, `manufacturing_year`, `vehicle_age_years`, `idv`, `policy_age_months`, `annual_premium_paid`, `previous_claims_count`, `ncb_at_claim_percent`, `zero_dep_addon`, `rider_experience_years`, `helmet_worn`, `incident_month`, `damage_severity_score`, `num_parts_affected`, `claim_amount`, `approval_probability`, `claim_approved` (20 columns) |
| **Categorical Columns** | `record_id`, `city`, `state`, `vehicle_make`, `vehicle_model`, `segment`, `policy_type`, `usage_type`, `incident_date`, `incident_day_of_week`, `incident_time_of_day`, `incident_type`, `damage_type`, `affected_parts` (14 columns) |
| **Date Columns** | `incident_date` (stored as string, requires parsing to datetime) |
| **Boolean Columns** | `zero_dep_addon`, `helmet_worn`, `claim_approved` (stored as integer 0/1) |

---

## PART 2: COLUMN ANALYSIS

Here is the deep-dive analysis for all 34 columns of the dataset:

### 1. `record_id`
*   **Data Type**: `object` (string)
*   **Business Meaning**: Unique identifier for the claim transaction.
*   **Example Values**: `a007100c`, `01557b26`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 100,000 (No duplicate record IDs)
*   **Whether it is Useful**: No (Metadata only)
*   **Whether it should be Removed**: Yes, during training.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 2. `customer_age`
*   **Data Type**: `int64`
*   **Business Meaning**: Age of the primary rider.
*   **Example Values**: `49`, `34`, `60`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 48 (Range: 18 to 65)
*   **Whether it is Useful**: Yes (Demographic risk factor)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 3. `city`
*   **Data Type**: `object`
*   **Business Meaning**: Registration city of the bike.
*   **Example Values**: `Ghaziabad`, `Sikar`, `Bokaro`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 117
*   **Whether it is Useful**: Yes (Geographical risk analysis)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (Target Encoding or Frequency Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 4. `state`
*   **Data Type**: `object`
*   **Business Meaning**: State of vehicle registration.
*   **Example Values**: `Uttar Pradesh`, `Rajasthan`, `Jharkhand`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 32
*   **Whether it is Useful**: Yes (Regional regulation and risk clustering)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 5. `city_tier`
*   **Data Type**: `int64`
*   **Business Meaning**: Classification of the city based on development/population (Tiers 1, 2, 3).
*   **Example Values**: `3`, `2`, `1`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 3
*   **Whether it is Useful**: Yes (Urban driving risk proxy)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (Ordinal or One-Hot)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 6. `city_risk_score`
*   **Data Type**: `float64`
*   **Business Meaning**: Calculated risk level associated with registration city.
*   **Example Values**: `0.88`, `1.15`, `0.92`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 23
*   **Whether it is Useful**: Yes (Numerical risk weight)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 7. `vehicle_make`
*   **Data Type**: `object`
*   **Business Meaning**: Manufacturer of the bike.
*   **Example Values**: `Ola Electric`, `KTM`, `Honda`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 13
*   **Whether it is Useful**: Yes (Determines spare parts repair baselines)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 8. `vehicle_model`
*   **Data Type**: `object`
*   **Business Meaning**: Vehicle model identifier.
*   **Example Values**: `S1 Air`, `Rizta`, `Bullet 350`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 138
*   **Whether it is Useful**: Yes (Determines repair profile and retail value)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (Target Encoding or Frequency Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 9. `segment`
*   **Data Type**: `object`
*   **Business Meaning**: Bike classification.
*   **Example Values**: `ev_scooter`, `sport`, `scooter`, `commuter`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 16
*   **Whether it is Useful**: Yes (Determines risk profile and speed segment)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 10. `engine_cc`
*   **Data Type**: `int64`
*   **Business Meaning**: Engine displacement capacity.
*   **Example Values**: `0` (for EVs), `125`, `155`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 49
*   **Whether it is Useful**: Yes (Determines risk and Third-Party pricing rates)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 11. `manufacturing_year`
*   **Data Type**: `int64`
*   **Business Meaning**: Year the vehicle was built.
*   **Example Values**: `2018`, `2009`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 20 (Range: 2005 to 2024)
*   **Whether it is Useful**: Yes (Depreciation indicator)
*   **Whether it should be Removed**: Yes, redundant once `vehicle_age_years` is calculated.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 12. `vehicle_age_years`
*   **Data Type**: `int64`
*   **Business Meaning**: Age of the vehicle since manufacture.
*   **Example Values**: `7`, `16`, `12`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 20 (Range: 1 to 20)
*   **Whether it is Useful**: Yes (Direct depreciation determinant)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler or StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 13. `idv`
*   **Data Type**: `int64`
*   **Business Meaning**: Insured Declared Value (Current market value of bike).
*   **Example Values**: `108449`, `69133`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 69,133
*   **Whether it is Useful**: Yes (Determines maximum claim liability)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (RobustScaler)
*   **Whether it may cause Data Leakage**: No

### 14. `policy_type`
*   **Data Type**: `object`
*   **Business Meaning**: Structure of policy contract.
*   **Example Values**: `Comprehensive`, `Own Damage`, `Third Party`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 3
*   **Whether it is Useful**: Yes (Directly dictates billing calculation structures)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 15. `policy_age_months`
*   **Data Type**: `int64`
*   **Business Meaning**: Number of months the active policy has been in force.
*   **Example Values**: `13`, `48`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 60 (Range: 1 to 60)
*   **Whether it is Useful**: Yes (Identifies early claim fraud risks)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler)
*   **Whether it may cause Data Leakage**: No

### 16. `annual_premium_paid`
*   **Data Type**: `int64`
*   **Business Meaning**: Amount paid by the customer for the current annual policy coverage.
*   **Example Values**: `8711`, `44804`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 19,188
*   **Whether it is Useful**: Yes (Reflects customer investment size)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 17. `previous_claims_count`
*   **Data Type**: `int64`
*   **Business Meaning**: Number of claims submitted by this policyholder in previous terms.
*   **Example Values**: `0`, `1`, `2`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 5 (Range: 0 to 4)
*   **Whether it is Useful**: Yes (Claims history risk factor)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 18. `ncb_at_claim_percent`
*   **Data Type**: `int64`
*   **Business Meaning**: The No Claim Bonus percentage active at the time of the claim.
*   **Example Values**: `45`, `20`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 6 (Range: 0 to 50)
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler)
*   **Whether it may cause Data Leakage**: No

### 19. `zero_dep_addon`
*   **Data Type**: `int64`
*   **Business Meaning**: Binary indicator (0/1) showing if Zero Depreciation cover was purchased.
*   **Example Values**: `0`, `1`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 2
*   **Whether it is Useful**: Yes (Zero dep covers parts replacement costs without depreciation deductions)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 20. `usage_type`
*   **Data Type**: `object`
*   **Business Meaning**: Differentiates between Personal, Commercial, and Delivery uses.
*   **Example Values**: `Personal`, `Delivery`, `Commercial`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 3
*   **Whether it is Useful**: Yes (Delivery usage significantly increases accident and wear-and-tear risks)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 21. `rider_experience_years`
*   **Data Type**: `int64`
*   **Business Meaning**: Number of years the claimant has held a valid driving license.
*   **Example Values**: `5`, `12`, `0` (for novice riders)
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 31 (Range: 0 to 30)
*   **Whether it is Useful**: Yes (Lower riding experience correlates with higher accident rates)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler)
*   **Whether it may cause Data Leakage**: No

### 22. `helmet_worn`
*   **Data Type**: `int64`
*   **Business Meaning**: Binary indicator showing if a helmet was worn during the accident.
*   **Example Values**: `1`, `0`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 2
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: No (Claim compliance flag: riding without a helmet is illegal and affects health claim liability payouts)
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 23. `incident_date`
*   **Data Type**: `object` (string)
*   **Business Meaning**: Date when the claim incident occurred.
*   **Example Values**: `2019-02-06`, `2020-01-28`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 2,192
*   **Whether it is Useful**: Yes (Extract seasonal risk variations)
*   **Whether it should be Removed**: Yes, once features like `days_to_claim` are engineered.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 24. `incident_day_of_week`
*   **Data Type**: `object`
*   **Business Meaning**: Weekday on which the incident occurred.
*   **Example Values**: `Wednesday`, `Tuesday`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 7
*   **Whether it is Useful**: Yes (Identifies high-risk weekend or weekday patterns)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 25. `incident_month`
*   **Data Type**: `int64`
*   **Business Meaning**: Calendar month of the incident.
*   **Example Values**: `2`, `1`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 12
*   **Whether it is Useful**: Yes (Monsoon flooding or winter fog seasonal risk indicators)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding or Cyclic Sine/Cosine transformations)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 26. `incident_time_of_day`
*   **Data Type**: `object`
*   **Business Meaning**: General time block of day when the accident occurred.
*   **Example Values**: `Night`, `Afternoon`, `Morning`, `Evening`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 4
*   **Whether it is Useful**: Yes (Night accidents often associate with higher fraud/severity profiles)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 27. `incident_type`
*   **Data Type**: `object`
*   **Business Meaning**: Primary event classification causing damage.
*   **Example Values**: `Accident`, `Natural Calamity`, `Flooding`, `Fire`, `Vandalism`, `Theft`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 6
*   **Whether it is Useful**: Yes (Evaluates correlation with expected damage severity)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 28. `damage_type`
*   **Data Type**: `object`
*   **Business Meaning**: Specific structural damage classification observed.
*   **Example Values**: `dent`, `scratch`, `bumper damage`, `collision damage`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 13
*   **Whether it is Useful**: Yes (Validates claim narrative alignment)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 29. `damage_severity_score`
*   **Data Type**: `int64`
*   **Business Meaning**: Numeric index rating damage severity.
*   **Example Values**: `3`, `4`, `5`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 10 (Range: 1 to 10)
*   **Whether it is Useful**: Yes (Directly dictates expected claims cost limits)
*   **Whether it should be Removed**: No (Crucial feature, also output by Gemini Vision)
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler)
*   **Whether it may cause Data Leakage**: No

### 30. `num_parts_affected`
*   **Data Type**: `int64`
*   **Business Meaning**: Count of individual components requiring replacement or repair.
*   **Example Values**: `2`, `3`, `1`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 5 (Range: 1 to 5)
*   **Whether it is Useful**: Yes (Proportions claim scope)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 31. `affected_parts`
*   **Data Type**: `object`
*   **Business Meaning**: Comma-separated list of damaged parts.
*   **Example Values**: `Handlebar, Fuel tank`, `Front fender, Left indicator`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 24,808 combinations
*   **Whether it is Useful**: Yes (Refines damage valuation and validates fraud consistency)
*   **Whether it should be Removed**: Yes, in raw format (expand into binary indicators).
*   **Whether it needs Encoding**: Yes (Multi-Label Binarization)
*   **Whether it may cause Data Leakage**: No

### 32. `claim_amount`
*   **Data Type**: `int64`
*   **Business Meaning**: The financial compensation requested by the claimant.
*   **Example Values**: `8500`, `29000`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 44,145
*   **Whether it is Useful**: Yes (Primary feature for claim sizing and fraud limits checking)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (RobustScaler)
*   **Whether it may cause Data Leakage**: No

### 33. `approval_probability`
*   **Data Type**: `float64`
*   **Business Meaning**: Internal score indicating likelihood of approval.
*   **Example Values**: `0.9679`, `0.7737`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 7,910
*   **Whether it is Useful**: No.
*   **Whether it should be Removed**: **Yes, during ML model training**. This is a target leakage feature.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 34. `claim_approved`
*   **Data Type**: `int64`
*   **Business Meaning**: Binary indicator (0/1) showing if the claim was approved.
*   **Example Values**: `1`, `0`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 2
*   **Whether it is Useful**: Yes (Target class variable `y` for claims classification model).
*   **Whether it should be Removed**: No (Target)
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: N/A (Target)

---

## PART 3: DATA QUALITY

### 1. Missing Values
*   **Analysis**: No missing values are present in this dataset. All 100,000 rows contain populated records for all 34 columns.

### 2. Duplicate Rows and IDs
*   **Duplicate Rows**: 0 duplicate rows.
*   **Duplicate IDs (`record_id`)**: 0 duplicate record IDs in this dataset (all 100,000 IDs are unique).

### 3. Outliers & Data Limits
*   **`claim_amount`**: Maximum value reaches $32.8 \text{ Lakhs}$ INR (heavily right-skewed).
*   **`idv`**: Maximum value is $38 \text{ Lakhs}$ INR, reflecting superbikes.
*   **`rider_experience_years`**: Max value is 30, which is logically consistent with an older rider profile (e.g. age 48+).

### 4. Impossible or Invalid Values
*   **`engine_cc` = 0**: 32,113 cases show $0 \text{ CC}$. These correspond to `segment` = `"ev_scooter"`. This represents valid EV scooter models rather than data errors.

---

## PART 4: BUSINESS UNDERSTANDING

### Why columns exist and how they are used:
1. **`customer_age`**: Assesses general physical risk. Used in **Fraud Detection**.
2. **`city` / `state`**: Maps to geographic risk. High-theft states require closer verification.
3. **`rider_experience_years`**: Indicates riding proficiency. Novice riders show higher accident frequencies. Used in **Claim Approval** routing.
4. **`helmet_worn`**: Standard compliance check. Riding without a helmet is a traffic violation. Rejections may occur for personal injury coverage additions.
5. **`usage_type`**: Delivery riders face higher daily exposure and risk compared to personal commuters. Used in **Premium Prediction** and **Claim Prediction**.
6. **`vehicle_make` / `model` / `segment`**: Determines expected repair costs.
7. **`idv`**: Sum insured limit. Protects the insurer against inflated claims.
8. **`zero_dep_addon`**: Determines coverage limits. Zero dep covers parts replacement without depreciation deductions.
9. **`incident_type` / `damage_type` / `damage_severity_score`**: Explains the cause and scope of damage. Used in **Claim Approval** routing.
10. **`claim_amount`**: The requested payout amount. Directly determines approval routing thresholds.

---

## PART 5: TARGET ANALYSIS

### 1. Classification Target: `claim_approved`
*   **Definition**: Binary indicator (0/1) showing if the claim was approved.
*   **Class Distribution**:
    *   **Approved (1)**: 88,568 cases ($88.57\%$)
    *   **Rejected (0)**: 11,432 cases ($11.43\%$)
*   **Class Imbalance**: There is a significant class imbalance ($88.6\%$ vs $11.4\%$). 

### 2. Potential Problems and Solutions
*   **Imbalance Bias**: The model will be biased towards predicting approval.
    *   *Solution*: Apply class weighting or use SMOTE to balance the training set. Evaluate using recall and F1-score.
*   **Target Leakage**: Drop `approval_probability` before training.

---

## PART 6: FEATURE GROUPING

*   **Customer Features (Risk Profile)**:
    *   `customer_age`, `previous_claims_count`, `rider_experience_years`
*   **Vehicle Features (Asset Profile)**:
    *   `vehicle_make`, `vehicle_model`, `segment`, `engine_cc`, `manufacturing_year`, `vehicle_age_years`, `idv`
*   **Policy Features (Coverage Verification)**:
    *   `policy_type`, `usage_type`, `policy_age_months`, `annual_premium_paid`, `ncb_at_claim_percent`, `zero_dep_addon`
*   **Incident/Claim Features (Event Profiling)**:
    *   `incident_date`, `incident_day_of_week`, `incident_month`, `incident_time_of_day`, `incident_type`, `damage_type`, `damage_severity_score`, `num_parts_affected`, `affected_parts`, `claim_amount`, `helmet_worn`
*   **Location Features**:
    *   `city`, `state`, `city_tier`, `city_risk_score`
*   **Intermediate Score (Leakage)**:
    *   `approval_probability`
*   **Target**:
    *   `claim_approved`
*   **Metadata**:
    *   `record_id`

---

## PART 7: FEATURE ENGINEERING IDEAS

1.  **Usage Risk Multiplier**:
    *   *Definition*: Combine `usage_type` with `city_risk_score` to create a spatial usage risk score.
    *   *Justification*: A delivery driver in a high-risk city has exponentially higher accident risk than a personal driver in a low-risk city.
2.  **Claim to IDV Ratio**:
    $$\text{Claim Ratio} = \frac{\text{claim\_amount}}{\text{idv}}$$
    *Justification*: High ratios indicate catastrophic damage. Ratios $> 1.0$ indicate potential fraud or total loss.
3.  **Experienced Safe Rider Index**:
    *   *Definition*: Binary indicator set to 1 if `rider_experience_years` $\ge 5$ and `helmet_worn` = 1 and `previous_claims_count` = 0.
    *   *Justification*: Identifies low-risk riders who are highly compliant with safety standards.

---

## PART 8: FEATURE SELECTION

### 1. Definitely Keep (Core ML Features)
*   `customer_age`, `city_risk_score`, `vehicle_age_years`, `idv`, `policy_age_months`, `previous_claims_count`, `zero_dep_addon`, `usage_type`, `rider_experience_years`, `helmet_worn`, `incident_type`, `damage_type`, `damage_severity_score`, `num_parts_affected`, `claim_amount`.
    *   *Justification*: Essential risk factors for bike claim validation.

### 2. Possibly Keep (Categoricals requiring careful encoding)
*   `city`, `state`, `vehicle_model`, `incident_day_of_week`, `incident_time_of_day`, `affected_parts` (expanded).
    *   *Justification*: Granular details with high cardinality. Apply target encoding or multi-label binarization.

### 3. Remove (Drop before ML training)
*   `record_id` (Non-predictive metadata).
*   `manufacturing_year` (Redundant).
*   `incident_date` (Redundant).
*   `approval_probability` (Direct target leakage).

---

## PART 9: PREPROCESSING PLAN

| Column Name | Encoding | Scaling | Imputation | Transformation | Feature Engineering |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_age` | None | StandardScaler | None | None | None |
| `city` / `state` | Target Encoding | None | None | None | None |
| `city_risk_score` | None | None | None | None | None |
| `vehicle_make` / `model` | One-Hot / Target | None | None | None | None |
| `vehicle_age_years`| None | MinMaxScaler | None | None | Claim to IDV Ratio |
| `idv` | None | RobustScaler | None | Log1p | Claim to IDV Ratio |
| `policy_age_months`| None | MinMaxScaler | None | None | None |
| `previous_claims_count`| None| StandardScaler| None | None | None |
| `zero_dep_addon` | None | None | None | None | None |
| `usage_type` | One-Hot Encoding | None | None | None | Usage Risk Multiplier |
| `rider_experience_years`| None| MinMaxScaler | None | None | Experienced Rider Index|
| `helmet_worn` | None | None | None | None | Experienced Rider Index|
| `incident_day_of_week`| One-Hot Encoding | None | None | None | None |
| `incident_month` | One-Hot Encoding | None | None | None | None |
| `incident_time_of_day`| One-Hot Encoding | None | None | None | None |
| `incident_type` | One-Hot Encoding | None | None | None | None |
| `damage_type` | One-Hot Encoding | None | None | None | None |
| `damage_severity_score`| None| MinMaxScaler | None | None | None |
| `affected_parts` | Multi-Label Binary | None | None | None | None |
| `claim_amount` | None | RobustScaler | None | Log1p | Claim to IDV Ratio |

---

## PART 10: EDA PLAN (ROADMAP)

1.  **Approval Rate by Helmet Worn and Experience Box Plot**:
    *   *Purpose*: Analyze how helmet compliance and rider experience impact claim approvals.
2.  **Claim Amount vs. IDV Scatter Plot (Colored by Approval)**:
    *   *Purpose*: Identify thresholds where high claim-to-IDV ratios trigger claim rejections.
3. **Usage Type vs. Claim Amount Violin Plots**:
    *   *Purpose*: Highlight claim volume differences between Delivery, Commercial, and Personal bikes.
4. **Incident Type vs. Severity Score Heatmap**:
    *   *Purpose*: Analyze the severity of damage across different incident types (e.g. theft vs accidents).

---

## PART 11: MACHINE LEARNING READINESS

*   **Is the dataset ready for ML?**: **No**.
*   **Prerequisites before model training**:
    1.  **Drop Leakage Columns**: Drop `approval_probability`.
    2.  **Parts Binarization**: Expand `affected_parts` into individual binary columns.
    3.  **Target Encoding**: Encode high-cardinality categorical variables.
    4.  **Handle Imbalance**: Configure SMOTE or class weights to manage the 88:12 class imbalance.

---

## PART 12: FINAL RECOMMENDATIONS

*   **Strengths**: Zero missing values, detailed riding compliance indicators (`helmet_worn`, `rider_experience_years`), and clear target classifications.
*   **Weaknesses**: Significant class imbalance and target leakage in the probability column.
*   **Risks**: Model bias towards claim approvals due to the class imbalance.
*   **Recommended Algorithms**:
    *   **XGBoost Classifier / LightGBM Classifier**: Handles tabular data and class imbalance effectively.
    *   **Random Forest Classifier**: Provides a stable baseline model and integrates smoothly with SHAP explainability.

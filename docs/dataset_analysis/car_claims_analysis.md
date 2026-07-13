# Car Claims Dataset Analysis
**Module Reference**: Module 3 (AI Claims Engine)  
**Status**: Technical Profiling Complete  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATASET OVERVIEW

| Attribute | Details |
| :--- | :--- |
| **Dataset Name** | Car Claims Dataset (`acko_car_claims.csv`) |
| **Number of Rows** | 150,000 |
| **Number of Columns** | 32 |
| **Memory Usage** | 36.6 MB (DataFrames loading footprint) |
| **Dataset Size** | 29.5 MB (Disk storage size) |
| **Target Variable** | `claim_approved` (Binary Classifier: 0 or 1) |
| **Numerical Columns** | `customer_age`, `city_tier`, `city_risk_score`, `engine_cc`, `manufacturing_year`, `vehicle_age_years`, `idv`, `policy_age_months`, `annual_premium_paid`, `previous_claims_count`, `ncb_at_claim_percent`, `zero_dep_addon`, `engine_protection_addon`, `incident_month`, `damage_severity_score`, `num_parts_affected`, `claim_amount`, `approval_probability`, `claim_approved` (19 columns) |
| **Categorical Columns** | `record_id`, `city`, `state`, `vehicle_make`, `vehicle_model`, `segment`, `policy_type`, `incident_date`, `incident_day_of_week`, `incident_time_of_day`, `incident_type`, `damage_type`, `affected_parts` (13 columns) |
| **Date Columns** | `incident_date` (stored as string, requires parsing to datetime) |
| **Boolean Columns** | `zero_dep_addon`, `engine_protection_addon`, `claim_approved` (stored as integer 0/1) |

---

## PART 2: COLUMN ANALYSIS

Here is the deep-dive analysis for all 32 columns of the dataset:

### 1. `record_id`
*   **Data Type**: `object` (string)
*   **Business Meaning**: Unique identifier for the claim transaction.
*   **Example Values**: `b00b1714`, `de98dc4a`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 149,995 (Contains 5 duplicate record IDs)
*   **Whether it is Useful**: No (Metadata only)
*   **Whether it should be Removed**: Yes, during training.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 2. `customer_age`
*   **Data Type**: `int64`
*   **Business Meaning**: Age of the primary driver.
*   **Example Values**: `60`, `47`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 58 (Range: 18 to 75)
*   **Whether it is Useful**: Yes (Demographic risk factor)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 3. `city`
*   **Data Type**: `object`
*   **Business Meaning**: Registration city of the vehicle.
*   **Example Values**: `Belgaum`, `Guwahati`
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
*   **Example Values**: `Karnataka`, `Assam`
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
*   **Example Values**: `0.90`, `1.12`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 23
*   **Whether it is Useful**: Yes (Numerical risk weight)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 7. `vehicle_make`
*   **Data Type**: `object`
*   **Business Meaning**: Manufacturer of the car.
*   **Example Values**: `Mahindra`, `BMW`, `Nissan`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 18
*   **Whether it is Useful**: Yes (Determines base parts pricing and asset class)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 8. `vehicle_model`
*   **Data Type**: `object`
*   **Business Meaning**: Vehicle model identifier.
*   **Example Values**: `KUV100`, `5 Series`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 134
*   **Whether it is Useful**: Yes (Determines repair profile and retail value)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (Target Encoding or Frequency Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 9. `segment`
*   **Data Type**: `object`
*   **Business Meaning**: Vehicle class.
*   **Example Values**: `suv`, `sedan`, `ev`, `hatchback`, `mpv`, `hybrid`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 6
*   **Whether it is Useful**: Yes (Determines risk profile and asset tier)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 10. `engine_cc`
*   **Data Type**: `int64`
*   **Business Meaning**: Engine displacement capacity.
*   **Example Values**: `1198`, `1998`, `0` (for EVs)
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 37
*   **Whether it is Useful**: Yes (Determines regulatory Third-Party pricing rates)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 11. `manufacturing_year`
*   **Data Type**: `int64`
*   **Business Meaning**: Year the vehicle was built.
*   **Example Values**: `2022`, `2008`
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
*   **Example Values**: `3`, `17`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 20 (Range: 1 to 20)
*   **Whether it is Useful**: Yes (Direct depreciation determinant)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler or StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 13. `idv`
*   **Data Type**: `int64`
*   **Business Meaning**: Insured Declared Value (Current market value of car).
*   **Example Values**: `531666`, `2039890`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 143,330
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
*   **Number of Unique Values**: 66,124
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

### 20. `engine_protection_addon`
*   **Data Type**: `int64`
*   **Business Meaning**: Binary indicator (0/1) showing if Engine Protection cover was purchased.
*   **Example Values**: `1`, `0`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 2
*   **Whether it is Useful**: Yes (Engine damage cover due to flooding/hydrostatic lock)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 21. `incident_date`
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

### 22. `incident_day_of_week`
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

### 23. `incident_month`
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

### 24. `incident_time_of_day`
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

### 25. `incident_type`
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

### 26. `damage_type`
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

### 27. `damage_severity_score`
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

### 28. `num_parts_affected`
*   **Data Type**: `int64`
*   **Business Meaning**: Count of individual components requiring replacement or repair.
*   **Example Values**: `2`, `3`, `1`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 6 (Range: 1 to 6)
*   **Whether it is Useful**: Yes (Proportions claim scope)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 29. `affected_parts`
*   **Data Type**: `object`
*   **Business Meaning**: Comma-separated list of damaged parts.
*   **Example Values**: `Radiator, Alloy wheels`, `Dashboard, Right headlight, Side mirror`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 45,627 combinations
*   **Whether it is Useful**: Yes (Refines damage valuation and validates fraud consistency)
*   **Whether it should be Removed**: Yes, in raw format (expand into binary indicators).
*   **Whether it needs Encoding**: Yes (Multi-Label Binarization)
*   **Whether it may cause Data Leakage**: No

### 30. `claim_amount`
*   **Data Type**: `int64`
*   **Business Meaning**: The financial compensation requested by the claimant.
*   **Example Values**: `44392`, `190838`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 128,548
*   **Whether it is Useful**: Yes (Primary feature for claim sizing and fraud limits checking)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (RobustScaler)
*   **Whether it may cause Data Leakage**: No

### 31. `approval_probability`
*   **Data Type**: `float64`
*   **Business Meaning**: Internal score indicating likelihood of approval.
*   **Example Values**: `0.9679`, `0.7737`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 8,540
*   **Whether it is Useful**: No.
*   **Whether it should be Removed**: **Yes, during ML model training**. This is a target leakage feature. The probability is calculated directly from the approval assessment logic.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 32. `claim_approved`
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
*   **Analysis**: No missing values are present in this dataset. All 150,000 rows contain populated records for all 32 columns.

### 2. Duplicate Rows and IDs
*   **Duplicate Rows**: 0 duplicate rows.
*   **Duplicate IDs (`record_id`)**: 5 duplicate record IDs.
    *   *Analysis*: E.g., `record_id` `b00b1714` is assigned to a 60-year-old in Belgaum driving a Mahindra KUV100, and a 47-year-old in Guwahati driving a BMW 5 Series.
    *   *Resolution*: Do not use `record_id` as the database primary key. Generate an auto-incrementing UUID/integer surrogate primary key instead.

### 3. Outliers & Data Limits
*   **`claim_amount`**: Maximum value reaches $2.25 \text{ Crore}$ INR. The distribution is heavily right-skewed.
*   **`idv`**: Maximum value is $2.36 \text{ Crore}$ INR, reflecting luxury vehicles. High claim amounts align with high IDV values.
*   **`damage_severity_score`**: Maximum value is 10 (reasonable scale limit).

### 4. Impossible or Invalid Values
*   **`engine_cc` = 0**: 24,112 cases show $0 \text{ CC}$. These correspond to `segment` = `"ev"`. This represents valid EV listings rather than data errors.

---

## PART 4: BUSINESS UNDERSTANDING

### Why columns exist and how they are used:
1. **`customer_age`**: Assesses driver maturity. Used in **Fraud Detection** and risk tiering.
2. **`city` / `state`**: Maps to geographic risk. High-theft states require higher validation scrutiny in **Fraud Detection** and **Claim Approval**.
3. **`city_tier` / `city_risk_score`**: Calibrates traffic density weights. High risk scores trigger closer inspection of accidents.
4. **`vehicle_make` / `model` / `segment`**: Determines spare parts costs. Used to cross-reference if the requested `claim_amount` exceeds market parts cost baselines.
5. **`engine_cc` / `vehicle_age_years`**: Used for vehicle valuation validation.
6. **`idv`**: Sum insured limit. Used to flag claims exceeding the policy coverage limit.
7. **`policy_type` / `policy_age_months`**: Identifies early claims fraud (e.g. claims filed within 30 days of policy start).
8. **`annual_premium_paid`**: Customer segment indicator.
9. **`previous_claims_count`**: High frequency of past claims flags potential fraud risks.
10. **`ncb_at_claim_percent`**: Verified against past claims count for alignment.
11. **`zero_dep_addon` / `engine_protection_addon`**: Determines coverage limits. If a claimant requests engine repairs but did not purchase engine protection, the claim is rejected.
12. **`incident_date` / `incident_day_of_week` / `incident_month` / `incident_time_of_day`**: Checks for consistency in the accident report (e.g., matching the date against weather reports like monsoons). Night crashes often receive closer review.
13. **`incident_type` / `damage_type` / `damage_severity_score`**: Explains the cause and scope of damage. Used in **Claim Approval** routing.
14. **`num_parts_affected` / `affected_parts`**: Compared against the uploaded accident photos using computer vision.
15. **`claim_amount`**: The requested payout amount. Directly determines the approval routing threshold.

---

## PART 5: TARGET ANALYSIS

### 1. Classification Target: `claim_approved`
*   **Definition**: Binary indicator (0/1) showing if the claim was approved.
*   **Class Distribution**:
    *   **Approved (1)**: 128,403 cases ($85.60\%$)
    *   **Rejected (0)**: 21,597 cases ($14.40\%$)
*   **Class Imbalance**: There is a significant class imbalance ($85.6\%$ vs $14.4\%$). 

### 2. Potential Problems and Solutions
*   **Imbalance Bias**: Classifiers trained on this data will be biased towards predicting approval.
    *   *Solution*: Apply class weighting (`class_weight='balanced'` in RandomForest), or use SMOTE to balance the training set. Focus on recall and F1-score rather than accuracy during evaluation.
*   **Target Leakage**: `approval_probability` is calculated directly from the approval assessment logic. Keeping it in the training dataset will cause target leakage.
    *   *Solution*: Drop `approval_probability` before training.

---

## PART 6: FEATURE GROUPING

*   **Customer Features (Risk Profile)**:
    *   `customer_age`, `previous_claims_count`
*   **Vehicle Features (Asset Profile)**:
    *   `vehicle_make`, `vehicle_model`, `segment`, `engine_cc`, `manufacturing_year`, `vehicle_age_years`, `idv`
*   **Policy Features (Coverage Verification)**:
    *   `policy_type`, `policy_age_months`, `annual_premium_paid`, `ncb_at_claim_percent`, `zero_dep_addon`, `engine_protection_addon`
*   **Incident/Claim Features (Event Profiling)**:
    *   `incident_date`, `incident_day_of_week`, `incident_month`, `incident_time_of_day`, `incident_type`, `damage_type`, `damage_severity_score`, `num_parts_affected`, `affected_parts`, `claim_amount`
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

1.  **Early Claim Flag**:
    *   *Definition*: A binary flag set to 1 if `policy_age_months` $\le 2$.
    *   *Justification*: Claims submitted immediately after policy purchase present a high correlation with fraud.
2.  **Claim to IDV Ratio**:
    $$\text{Claim Ratio} = \frac{\text{claim\_amount}}{\text{idv}}$$
    *Justification*: High ratios indicate catastrophic damage, whereas ratios $> 1.0$ indicate constructive total loss and potential inflation.
3.  **Monsoon Flood Match**:
    *   *Definition*: A binary flag set to 1 if `incident_type` = `"Flooding"` and `incident_month` is in `[6, 7, 8, 9]`.
    *   *Justification*: Validates claim reports by matching flood claims to seasonal monsoon months.

---

## PART 8: FEATURE SELECTION

### 1. Definitely Keep (Core ML Features)
*   `customer_age`, `city_risk_score`, `vehicle_age_years`, `idv`, `policy_age_months`, `previous_claims_count`, `zero_dep_addon`, `engine_protection_addon`, `incident_type`, `damage_type`, `damage_severity_score`, `num_parts_affected`, `claim_amount`.
    *   *Justification*: Crucial indicators of risk, coverage validity, and damage alignment.

### 2. Possibly Keep (Categoricals requiring careful encoding)
*   `city`, `state`, `vehicle_model`, `incident_day_of_week`, `incident_time_of_day`, `affected_parts` (expanded).
    *   *Justification*: Add granularity but increase cardinality. Apply target encoding or multi-label binarization.

### 3. Remove (Drop before ML training)
*   `record_id` (Non-predictive metadata).
*   `manufacturing_year` (Redundant).
*   `incident_date` (Redundant once date parts are extracted).
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
| `policy_age_months`| None | MinMaxScaler | None | None | Early Claim Flag |
| `previous_claims_count`| None| StandardScaler| None | None | None |
| `zero_dep_addon` | None | None | None | None | None |
| `engine_protection_addon`| None| None | None | None | None |
| `incident_day_of_week`| One-Hot Encoding | None | None | None | None |
| `incident_month` | One-Hot Encoding | None | None | None | Monsoon Flood Match |
| `incident_time_of_day`| One-Hot Encoding | None | None | None | None |
| `incident_type` | One-Hot Encoding | None | None | None | Monsoon Flood Match |
| `damage_type` | One-Hot Encoding | None | None | None | None |
| `damage_severity_score`| None| MinMaxScaler | None | None | None |
| `affected_parts` | Multi-Label Binary | None | None | None | None |
| `claim_amount` | None | RobustScaler | None | Log1p | Claim to IDV Ratio |

---

## PART 10: EDA PLAN (ROADMAP)

1.  **Approval Rate by Damage Severity and Age Box Plot**:
    *   *Purpose*: Analyze the relationship between damage severity and claim approval rates across different customer ages.
2.  **Claim Amount vs. IDV Scatter Plot (Colored by Approval)**:
    *   *Purpose*: Identify thresholds where high claim-to-IDV ratios trigger claim denials.
3.  **Policy Age vs. Approval Probability Joint Plot**:
    *   *Purpose*: Check for correlations between early policy tenures and claim rejections.
4.  **Incident Month vs. Incident Type Heatmap**:
    *   *Purpose*: Verify the seasonality of flood and weather-related claims.

---

## PART 11: MACHINE LEARNING READINESS

*   **Is the dataset ready for ML?**: **No**.
*   **Prerequisites before model training**:
    1.  **Drop Leakage Columns**: Drop `approval_probability`.
    2.  **Parts Binarization**: Expand `affected_parts` into individual binary columns.
    3.  **Target Encoding**: Encode high-cardinality categorical variables.
    4.  **Handle Imbalance**: Configure SMOTE or class weights to manage the 85:15 class imbalance.

---

## PART 12: FINAL RECOMMENDATIONS

*   **Strengths**: Zero missing values, detailed damage descriptors, and clear target classifications.
*   **Weaknesses**: Significant class imbalance and target leakage in the probability column.
*   **Risks**: Model bias towards claim approvals due to the class imbalance.
*   **Recommended Algorithms**:
    *   **XGBoost Classifier / LightGBM Classifier**: Handles tabular data and class imbalance effectively.
    *   **Random Forest Classifier**: Provides a stable baseline model and integrates smoothly with SHAP explainability.

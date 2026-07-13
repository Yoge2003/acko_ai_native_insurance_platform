# Bike Quotation Dataset Analysis
**Module Reference**: Module 2 (Insurance Premium Prediction)  
**Status**: Technical Profiling Complete  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATASET OVERVIEW

| Attribute | Details |
| :--- | :--- |
| **Dataset Name** | Bike Quotation Dataset (`acko_bike_quotation.csv`) |
| **Number of Rows** | 150,000 |
| **Number of Columns** | 28 |
| **Memory Usage** | 32.0 MB (DataFrames loading footprint) |
| **Dataset Size** | 27.9 MB (Disk storage size) |
| **Target Variable** | `annual_premium` (Numerical Regressor) |
| **Numerical Columns** | `customer_age`, `city_tier`, `city_risk_score`, `manufacturing_year`, `vehicle_age_years`, `engine_cc`, `idv`, `ncb_percent`, `claim_history_count`, `num_addons`, `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount`, `annual_premium` (16 columns) |
| **Categorical Columns** | `record_id`, `city`, `state`, `vehicle_make`, `vehicle_model`, `variant`, `segment`, `fuel_type`, `colour`, `policy_type`, `usage_type`, `addons_list` (12 columns) |
| **Date Columns** | None (Manufacturing year exists as integer) |
| **Boolean Columns** | None (represented as binary/integers) |

---

## PART 2: COLUMN ANALYSIS

Here is the deep-dive analysis for all 28 columns of the dataset:

### 1. `record_id`
*   **Data Type**: `object` (string)
*   **Business Meaning**: Unique identifier for the quotation transaction.
*   **Example Values**: `c007100c`, `01557b26`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 149,999 (Contains 1 duplicate record ID)
*   **Whether it is Useful**: No (Metadata only)
*   **Whether it should be Removed**: Yes, during training.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 2. `customer_age`
*   **Data Type**: `int64`
*   **Business Meaning**: Age of the primary rider.
*   **Example Values**: `21`, `49`, `60`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 48 (Range: 18 to 65)
*   **Whether it is Useful**: Yes (Demographic risk factor)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 3. `city`
*   **Data Type**: `object`
*   **Business Meaning**: City where the bike is registered.
*   **Example Values**: `Rajahmundry`, `Indore`, `Patna`
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
*   **Example Values**: `Andhra Pradesh`, `Madhya Pradesh`, `Bihar`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 32
*   **Whether it is Useful**: Yes (Regional regulation and risk clustering)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding or Target Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 5. `city_tier`
*   **Data Type**: `int64`
*   **Business Meaning**: Categorical classification of the city based on development/population (Tiers 1, 2, 3).
*   **Example Values**: `1`, `2`, `3`
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
*   **Example Values**: `0.88`, `1.15`, `1.20`
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
*   **Example Values**: `Royal Enfield`, `Yamaha`, `Suzuki`, `Ola Electric`, `Ather Energy`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 13
*   **Whether it is Useful**: Yes (Determines base parts pricing and asset class)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 8. `vehicle_model`
*   **Data Type**: `object`
*   **Business Meaning**: Vehicle model identifier.
*   **Example Values**: `Bullet 500`, `Fascino 125`, `Gixxer 150`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 138
*   **Whether it is Useful**: Yes (Determines repair profile and retail value)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (Target Encoding or Frequency Encoding due to cardinality)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 9. `variant`
*   **Data Type**: `object`
*   **Business Meaning**: Sub-model specification (trim/engine type).
*   **Example Values**: `STD`, `ABS`, `Drum`, `Double Disc`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 16
*   **Whether it is Useful**: Yes (Refines vehicle value and safety rating)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 10. `segment`
*   **Data Type**: `object`
*   **Business Meaning**: Bike classification.
*   **Example Values**: `retro`, `scooter`, `sport`, `ev_scooter`, `naked`, `commuter`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 16
*   **Whether it is Useful**: Yes (Determines risk profile and asset tier)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 11. `fuel_type`
*   **Data Type**: `object`
*   **Business Meaning**: Energy source of the vehicle.
*   **Example Values**: `Petrol`, `Electric`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 2
*   **Whether it is Useful**: Yes (Underwriting risk proxy)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 12. `colour`
*   **Data Type**: `object`
*   **Business Meaning**: Aesthetic finish of the bike.
*   **Example Values**: `Sports Blue`, `Yellow`, `Dual Tone`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 12
*   **Whether it is Useful**: Low utility (used for identification).
*   **Whether it should be Removed**: Keep as optional or remove if feature pruning is strict.
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 13. `manufacturing_year`
*   **Data Type**: `int64`
*   **Business Meaning**: Year the vehicle was built.
*   **Example Values**: `2018`, `2012`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 20 (Range: 2005 to 2024)
*   **Whether it is Useful**: Yes (Depreciation indicator)
*   **Whether it should be Removed**: Yes, redundant once `vehicle_age_years` is calculated.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 14. `vehicle_age_years`
*   **Data Type**: `int64`
*   **Business Meaning**: Age of the vehicle since manufacture.
*   **Example Values**: `7`, `13`, `14`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 20 (Range: 1 to 20)
*   **Whether it is Useful**: Yes (Direct depreciation determinant)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler or StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 15. `engine_cc`
*   **Data Type**: `int64`
*   **Business Meaning**: Engine displacement capacity.
*   **Example Values**: `499`, `125`, `155`, `0` (for EVs)
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 49
*   **Whether it is Useful**: Yes (Determines regulatory Third-Party pricing rates)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 16. `idv`
*   **Data Type**: `int64`
*   **Business Meaning**: Insured Declared Value (Current market value of bike).
*   **Example Values**: `106815`, `22704`, `36271`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 91,588
*   **Whether it is Useful**: Yes (Crucial pricing metric for Own Damage premium)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (RobustScaler due to high variance)
*   **Whether it may cause Data Leakage**: No

### 17. `ncb_percent`
*   **Data Type**: `int64`
*   **Business Meaning**: No Claim Bonus discount percentage.
*   **Example Values**: `0`, `25`, `35`, `45`, `50`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 6
*   **Whether it is Useful**: Yes (Direct pricing discount multiplier)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler)
*   **Whether it may cause Data Leakage**: No

### 18. `claim_history_count`
*   **Data Type**: `int64`
*   **Business Meaning**: Number of previous claims registered by the customer.
*   **Example Values**: `0`, `1`, `2`, `3`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 4 (Range: 0 to 3)
*   **Whether it is Useful**: Yes (Underwriting risk multiplier)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 19. `policy_type`
*   **Data Type**: `object`
*   **Business Meaning**: Structure of policy contract.
*   **Example Values**: `Comprehensive`, `Third Party`, `Own Damage`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 3
*   **Whether it is Useful**: Yes (Directly dictates billing calculation structures)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 20. `usage_type`
*   **Data Type**: `object`
*   **Business Meaning**: How the bike is utilized.
*   **Example Values**: `Personal`, `Commercial`, `Delivery`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 3
*   **Whether it is Useful**: Yes (Delivery and commercial bikes present much higher daily mileage risk)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 21. `num_addons`
*   **Data Type**: `int64`
*   **Business Meaning**: Count of optional riders purchased.
*   **Example Values**: `0`, `1`, `2`, `3`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 4 (Range: 0 to 3)
*   **Whether it is Useful**: Yes (Directly impacts addon premium sub-calculation)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 22. `addons_list`
*   **Data Type**: `object`
*   **Business Meaning**: Comma-separated list of selected riders.
*   **Example Values**: `Roadside Assistance, Consumables Cover, Return to Invoice`
*   **Missing Values**: 60,173 (40.12% when `num_addons` is 0)
*   **Number of Unique Values**: 156 combinations
*   **Whether it is Useful**: Yes (Determines risk profile and pricing for each addon)
*   **Whether it should be Removed**: Yes, in raw format (expand into binary columns).
*   **Whether it needs Encoding**: Yes (Multi-Label Binarization)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 23. `od_premium_before_ncb`
*   **Data Type**: `float64`
*   **Business Meaning**: Standard Own Damage premium based on vehicle IDV.
*   **Example Values**: `3861.87`, `1139.68`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 132,097
*   **Whether it is Useful**: Yes (Intermediary target component)
*   **Whether it should be Removed**: **Yes, during ML training**. Direct data leakage source.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 24. `ncb_discount_amount`
*   **Data Type**: `float64`
*   **Business Meaning**: Currency value of No Claim Bonus discount subtracted from Own Damage premium.
*   **Example Values**: `512.86`, `0.0`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 97,341
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: **Yes, during ML training**. Direct data leakage source.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 25. `tp_premium`
*   **Data Type**: `int64`
*   **Business Meaning**: Third Party Liability insurance premium.
*   **Example Values**: `687`, `714`, `1366`, `2804`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 4
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: **Yes, during ML training**. Direct data leakage source.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 26. `addon_premium`
*   **Data Type**: `float64`
*   **Business Meaning**: Sum of the premiums charged for all selected addon riders.
*   **Example Values**: `3317.48`, `0.0`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 70,126
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: **Yes, during ML training**. Direct data leakage source.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 27. `gst_amount`
*   **Data Type**: `float64`
*   **Business Meaning**: Goods and Services Tax (18% in India).
*   **Example Values**: `1295.85`, `151.65`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 76,934
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: **Yes, during ML training**. Direct data leakage source.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 28. `annual_premium`
*   **Data Type**: `int64`
*   **Business Meaning**: Final premium charged to customer including GST.
*   **Example Values**: `8338`, `1035`, `1829`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 22,215
*   **Whether it is Useful**: Yes (Target regressor `y`).
*   **Whether it should be Removed**: No (Target)
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: N/A (Target)

---

## PART 3: DATA QUALITY

### 1. Missing Values
*   **`addons_list`**: 60,173 missing values ($40.12\%$). This represents instances where `num_addons` $= 0$. Impute as `"No Addons"`.

### 2. Duplicate Rows and IDs
*   **Duplicate Rows**: 0 duplicate rows.
*   **Duplicate IDs (`record_id`)**: 1 duplicate record ID. 
    *   *Analysis*: `record_id` `a09ddc4e` is assigned to a Delivery Ola Electric S1 Air in Hyderabad (with a 49-year-old customer) and a Personal Ather Energy Rizta in Noida (with a 34-year-old customer).
    *   *Resolution*: Generate an auto-incrementing UUID/integer surrogate primary key in PostgreSQL instead of relying on `record_id`.

### 3. Outliers & Data Limits
*   **`idv`**: Maximum value is $3,801,389$ INR (highly skewed). This is correct for premium superbikes (e.g. Kawasaki, KTM high-end) but requires Robust Scaling.
*   **`annual_premium`**: Outlier premiums reach up to $252,983$ INR. Apply a log transformation during training.

### 4. Impossible or Invalid Values
*   **`engine_cc` = 0**: 48,110 cases show $0 \text{ CC}$. These represent electric scooters (`fuel_type` = `"Electric"`), which is technically correct.
*   **`customer_age`**: The minimum age is 18 and maximum is 65 (upper driving age limits for bikes are typically lower than cars in underwriting).

---

## PART 4: BUSINESS UNDERSTANDING

### Why columns exist and how they are used:
1. **`customer_age`**: Assesses physical riding risk. Affects **Premium Prediction** (younger riders pay higher rates).
2. **`city` / `state`**: Represents geographical hazards (unpaved roads, traffic). Used in **Premium Prediction**.
3. **`city_tier` / `city_risk_score`**: Calibrates traffic density multipliers. Affects **Premium Prediction**.
4. **`vehicle_make` / `model` / `variant`**: Determines parts pricing and replacement costs. Affects **Premium Prediction** (Own Damage base) and **Claim Prediction**.
5. **`segment`**: Categorizes cruisers, superbikes, EV scooters, and commuter bikes. Differentiates high-speed risk profiles. Affects **Premium Prediction** and **Policy Recommendation**.
6. **`fuel_type`**: Differentiates between Petrol and Electric scooters. Affects **Premium Prediction**.
7. **`colour`**: Used for database verification. Low impact on ML target.
8. **`vehicle_age_years` / `manufacturing_year`**: Dictates the depreciation profile. Affects **Premium Prediction**.
9. **`engine_cc`**: Maps to statutory lookup brackets. Determines Third-Party pricing rates:
   * **687** INR: Electric scooters.
   * **714** INR: Under 75cc (commuters).
   * **1366** INR: 75cc to 150cc.
   * **2804** INR: Over 150cc (superbikes).
10. **`idv`**: Sum insured. Affects **Premium Prediction** and **Claim Approval** limits.
11. **`ncb_percent`**: Reward for claims-free tenure. Affects **Premium Prediction** (reduces own-damage component).
12. **`claim_history_count`**: Quantifies historical customer risk. Affects **Premium Prediction** and **Fraud Detection**.
13. **`policy_type`**: Sets coverage boundaries (Comprehensive vs Third Party). Determines **Premium Prediction** structure.
14. **`usage_type`**: Crucial risk differentiator (Delivery/Commercial bikes have extremely high daily exposure compared to Personal). Affects **Premium Prediction** and **Claim Prediction** (higher accident probability).
15. **`num_addons` / `addons_list`**: Lists customized protection riders selected. Affects **Premium Prediction** directly.

---

## PART 5: TARGET ANALYSIS

### 1. Regression Target: `annual_premium`
*   **Definition**: The total premium paid by the customer, including GST.
*   **Value Range**: $538$ INR to $252,983$ INR.
*   **Mean**: $5,646.40$ INR.
*   **Standard Deviation**: $8,736.96$ INR.
*   **Distribution**: Heavily right-skewed.

### 2. Potential Problems and Solutions
*   **High Skewness**: High-end superbikes skew the premium target upwards.
    *   *Solution*: Apply a $\log(y)$ transformation (`numpy.log1p`) during training.
*   **Actuarial Leakage**: Drop intermediate calculation columns (`od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, and `gst_amount`) before training to avoid data leakage.

---

## PART 6: FEATURE GROUPING

*   **Customer Features (Risk Profile)**:
    *   `customer_age`, `claim_history_count`
*   **Vehicle Features (Asset Profile)**:
    *   `vehicle_make`, `vehicle_model`, `variant`, `segment`, `fuel_type`, `colour`, `manufacturing_year`, `vehicle_age_years`, `engine_cc`
*   **Geographical Features (Location Risk)**:
    *   `city`, `state`, `city_tier`, `city_risk_score`
*   **Policy Features (Coverage Selection)**:
    *   `policy_type`, `usage_type`, `ncb_percent`, `num_addons`, `addons_list`
*   **Intermediate Calculations (Data Leakage Risks)**:
    *   `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount`
*   **Target Feature**:
    *   `annual_premium`
*   **Metadata**:
    *   `record_id`

---

## PART 7: FEATURE ENGINEERING IDEAS

1.  **Usage Risk Multiplier**:
    *   *Definition*: Combine `usage_type` with `city_risk_score` to create a spatial usage risk score.
    *   *Justification*: A delivery driver in a high-risk city has exponentially higher accident risk than a personal driver in a low-risk city.
2.  **Addon Coverage Density**:
    $$\text{Addon Density} = \frac{\text{num\_addons}}{\text{Maximum Addons Available (3)}}$$
    *Justification*: Tracks customer risk aversion.
3.  **Relative Depreciation Rate**:
    $$\text{Relative Depreciation} = \frac{\text{idv}}{\text{Estimated Original Value of Model Group}}$$
    *Justification*: Shows how much value the vehicle has lost relative to its class baseline.

---

## PART 8: FEATURE SELECTION

### 1. Definitely Keep (Core ML Features)
*   `customer_age`, `city_risk_score`, `vehicle_age_years`, `engine_cc`, `idv`, `ncb_percent`, `claim_history_count`, `num_addons`, `segment`, `fuel_type`, `policy_type`, `usage_type`, `vehicle_make`.
    *   *Justification*: Essential risk factors for bike insurance underwriting.

### 2. Possibly Keep (Categoricals requiring careful encoding)
*   `city`, `state`, `vehicle_model`, `variant`, `colour`, `addons_list` (pruned/expanded).
    *   *Justification*: Granular details with high cardinality. Apply Target Encoding.

### 3. Remove (Drop before ML training)
*   `record_id` (Non-predictive metadata).
*   `manufacturing_year` (Redundant with `vehicle_age_years`).
*   `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount` (Direct target leakage).

---

## PART 9: PREPROCESSING PLAN

| Column Name | Encoding | Scaling | Imputation | Transformation | Feature Engineering |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_age` | None | StandardScaler | None | None | Driver Experience Index |
| `city` | Target Encoding | None | None | None | None |
| `state` | One-Hot Encoding | None | None | None | None |
| `city_risk_score` | None | None | None | None | None |
| `vehicle_make` | One-Hot Encoding | None | None | None | None |
| `vehicle_model` | Target Encoding | None | None | None | None |
| `variant` | Target Encoding | None | None | None | None |
| `segment` | One-Hot Encoding | None | None | None | Usage Risk Multiplier |
| `fuel_type` | One-Hot Encoding | None | None | None | None |
| `colour` | Drop or One-Hot | None | None | None | None |
| `vehicle_age_years`| None | MinMaxScaler | None | None | Relative Depreciation |
| `engine_cc` | None | StandardScaler | None | None | None |
| `idv` | None | RobustScaler | None | Log1p | Relative Depreciation |
| `ncb_percent` | None | MinMaxScaler | None | None | None |
| `claim_history_count`| None | StandardScaler| None | None | None |
| `policy_type` | One-Hot Encoding | None | None | None | None |
| `usage_type` | One-Hot Encoding | None | None | None | Usage Risk Multiplier |
| `addons_list` | Multi-Label Binary | None | Fill `"None"` | None | Addon Density |

---

## PART 10: EDA PLAN (ROADMAP)

1.  **Premium Distribution Histograms**:
    *   *Purpose*: Analyze the distribution of `annual_premium` before and after applying log transformations.
2.  **IDV vs. Premium Scatter Plot (Colored by Segment)**:
    *   *Purpose*: Validate the relationship between IDV and the calculated premium across different bike segments (superbikes vs EV scooters).
3. **Usage Type vs. Premium Boxplots**:
    *   *Purpose*: Highlight premium variations between Delivery, Commercial, and Personal bikes.
4. **Engine CC vs. Third-Party Premium Step Plot**:
    *   *Purpose*: Confirm the step-function relationship between CC ranges and fixed TP rates.

---

## PART 11: MACHINE LEARNING READINESS

*   **Is the dataset ready for ML?**: **No**.
*   **Prerequisites before model training**:
    1.  **Drop Leakage Columns**: Drop the intermediate calculation columns (`od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, and `gst_amount`).
    2.  **Addon Binarization**: Expand `addons_list` into binary columns.
    3.  **Target Encoding**: Encode high-cardinality categorical columns like `city` and `vehicle_model`.
    4.  **Log Transformation**: Apply a log transformation to the target variable `annual_premium`.

---

## PART 12: FINAL RECOMMENDATIONS

*   **Strengths**: Clean tabular formatting, zero missing values in core features, and strong risk proxies (`idv`, `ncb_percent`, `usage_type`).
*   **Weaknesses**: High cardinality in model-level fields and duplicate record IDs.
*   **Risks**: Keeping calculated pricing columns in the training data will result in artificial accuracy scores during testing that fail in production.
*   **Recommended Algorithms**:
    *   **LightGBM Regressor / XGBoost Regressor**: Best suited for handling mixed numerical and encoded categorical features with non-linear relationships.
    *   **RandomForestRegressor (Scikit-learn)**: Provides a stable baseline model and integrates smoothly with SHAP explainability.

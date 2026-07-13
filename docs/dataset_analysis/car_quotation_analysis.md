# Car Quotation Dataset Analysis
**Module Reference**: Module 2 (Insurance Premium Prediction)  
**Status**: Technical Profiling Complete  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATASET OVERVIEW

| Attribute | Details |
| :--- | :--- |
| **Dataset Name** | Car Quotation Dataset (`acko_car_quotation.csv`) |
| **Number of Rows** | 200,000 |
| **Number of Columns** | 28 |
| **Memory Usage** | 42.7 MB (DataFrames loading footprint) |
| **Dataset Size** | 39.2 MB (Disk storage size) |
| **Target Variable** | `annual_premium` (Numerical Regressor) |
| **Numerical Columns** | `customer_age`, `city_tier`, `city_risk_score`, `manufacturing_year`, `vehicle_age_years`, `engine_cc`, `idv`, `ncb_percent`, `claim_history_count`, `num_addons`, `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount`, `annual_premium` (16 columns) |
| **Categorical Columns** | `record_id`, `city`, `state`, `vehicle_make`, `vehicle_model`, `variant`, `segment`, `fuel_type`, `colour`, `policy_type`, `previous_insurer`, `addons_list` (12 columns) |
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
*   **Number of Unique Values**: 199,994 (Contains 6 duplicate records)
*   **Whether it is Useful**: No (Metadata only)
*   **Whether it should be Removed**: Yes, during training.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 2. `customer_age`
*   **Data Type**: `int64`
*   **Business Meaning**: Age of the primary driver.
*   **Example Values**: `23`, `46`, `60`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 58 (Range: 18 to 75)
*   **Whether it is Useful**: Yes (Demographic risk factor)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler/RobustScaler)
*   **Whether it may cause Data Leakage**: No

### 3. `city`
*   **Data Type**: `object`
*   **Business Meaning**: City where the vehicle is registered.
*   **Example Values**: `Kolkata`, `Panaji`, `Bhopal`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 117
*   **Whether it is Useful**: Yes (Geographical risk analysis)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (Target Encoding or Frequency Encoding to avoid high cardinality expansion)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 4. `state`
*   **Data Type**: `object`
*   **Business Meaning**: State of vehicle registration.
*   **Example Values**: `West Bengal`, `Goa`, `Madhya Pradesh`
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
*   **Example Values**: `0.88`, `1.30`, `1.50`
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
*   **Example Values**: `Hyundai`, `Maruti Suzuki`, `Mercedes-Benz`
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
*   **Example Values**: `Amaze`, `E-Class`, `Magnite`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 134
*   **Whether it is Useful**: Yes (Determines repair profile and retail value)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (Target Encoding or Frequency Encoding due to cardinality)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 9. `variant`
*   **Data Type**: `object`
*   **Business Meaning**: Sub-model specification (trim/engine type).
*   **Example Values**: `STD`, `ABS`, `Turbo`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 29
*   **Whether it is Useful**: Yes (Refines vehicle value and safety rating)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding or Target Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 10. `segment`
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

### 11. `fuel_type`
*   **Data Type**: `object`
*   **Business Meaning**: Energy source of the vehicle.
*   **Example Values**: `Petrol`, `Diesel`, `Electric`, `CNG`, `LPG`, `Hybrid`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 6
*   **Whether it is Useful**: Yes (Underwriting risk proxy)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 12. `colour`
*   **Data Type**: `object`
*   **Business Meaning**: Aesthetic finish of the car.
*   **Example Values**: `Midnight Black`, `Granite Grey`, `Opulent Red`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 16
*   **Whether it is Useful**: Yes (For database records/uniqueness; low correlation with pricing, though black/red vehicles sometimes show higher risk characteristics)
*   **Whether it should be Removed**: Keep as optional or remove if feature pruning is strict.
*   **Whether it needs Encoding**: Yes (One-Hot Encoding)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 13. `manufacturing_year`
*   **Data Type**: `int64`
*   **Business Meaning**: Year the vehicle was built.
*   **Example Values**: `2018`, `2020`
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
*   **Example Values**: `7`, `5`, `12`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 20 (Range: 1 to 20)
*   **Whether it is Useful**: Yes (Direct depreciation determinant)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (MinMaxScaler or StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 15. `engine_cc`
*   **Data Type**: `int64`
*   **Business Meaning**: Engine cubic capacity displacement.
*   **Example Values**: `1197`, `1498`, `0` (for EVs)
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 37
*   **Whether it is Useful**: Yes (Determines regulatory Third-Party pricing rates)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 16. `idv`
*   **Data Type**: `int64`
*   **Business Meaning**: Insured Declared Value (Current market value of vehicle).
*   **Example Values**: `1818711`, `1470493`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 188,567
*   **Whether it is Useful**: Yes (Crucial pricing metric for Own Damage premium)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (RobustScaler due to high variance and skewness)
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
*   **Example Values**: `0`, `1`, `2`, `3`, `4`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 5
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

### 20. `previous_insurer`
*   **Data Type**: `object`
*   **Business Meaning**: Competitor company that hosted the policy prior.
*   **Example Values**: `Tata AIG`, `Acko`, `Reliance General`, `NaN`
*   **Missing Values**: 22,121 (11.06%)
*   **Number of Unique Values**: 8
*   **Whether it is Useful**: Yes (Can indicate retention or switching patterns)
*   **Whether it should be Removed**: No
*   **Whether it needs Encoding**: Yes (One-Hot Encoding with special category for missing/new policyholders)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 21. `num_addons`
*   **Data Type**: `int64`
*   **Business Meaning**: Count of optional riders purchased.
*   **Example Values**: `0`, `1`, `2`, `3`, `4`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 5
*   **Whether it is Useful**: Yes (Directly impacts addon premium sub-calculation)
*   **Whether it should be Removed**: No (Can be verified or engineered)
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes (StandardScaler)
*   **Whether it may cause Data Leakage**: No

### 22. `addons_list`
*   **Data Type**: `object`
*   **Business Meaning**: Comma-separated list of selected riders.
*   **Example Values**: `Engine Protection`, `Roadside Assistance, Key Replacement`
*   **Missing Values**: 50,140 (25.07% when `num_addons` is 0)
*   **Number of Unique Values**: 5,140 combinations (derived from distinct individual addons)
*   **Whether it is Useful**: Yes (Determines risk profile and pricing for each addon)
*   **Whether it should be Removed**: Yes, in its raw format. (Should be expanded into binary columns for each individual addon type, e.g. `addon_engine_protection` = 0 or 1).
*   **Whether it needs Encoding**: Yes (Multi-Label Binarization)
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: No

### 23. `od_premium_before_ncb`
*   **Data Type**: `float64`
*   **Business Meaning**: Standard Own Damage premium based on vehicle IDV.
*   **Example Values**: `66547.36`, `63753.22`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 197,295
*   **Whether it is Useful**: Yes (Intermediary target component)
*   **Whether it should be Removed**: **Yes, during ML inference training**. This column represents an intermediate mathematical step in calculating the premium. If kept in the ML model, it will cause **Data Leakage** since it directly determines the final target and would not be available for new quotations without running the actuarial formula first.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 24. `ncb_discount_amount`
*   **Data Type**: `float64`
*   **Business Meaning**: Currency value of No Claim Bonus discount subtracted from Own Damage premium.
*   **Example Values**: `16636.84`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 161,853
*   **Whether it is Useful**: Yes, but causes **Data Leakage** during model training.
*   **Whether it should be Removed**: **Yes, during ML model training** (calculated deterministically as `od_premium_before_ncb * ncb_percent`).
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 25. `tp_premium`
*   **Data Type**: `int64`
*   **Business Meaning**: Third Party Liability insurance premium (government mandated rate based on engine CC).
*   **Example Values**: `2094`, `3416`, `7897`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 3
*   **Whether it is Useful**: Yes, but acts as a deterministic component.
*   **Whether it should be Removed**: **Yes, during ML model training**. It is a fixed statutory lookup table value based on engine CC. Adding it as a feature makes the regression trivial and hides the underlying risk factors.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 26. `addon_premium`
*   **Data Type**: `float64`
*   **Business Meaning**: Sum of the premiums charged for all selected addon riders.
*   **Example Values**: `1656.44`, `2448.23`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 129,524
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: **Yes, during ML model training**. It is directly calculated from the addons chosen and is an intermediate target component.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 27. `gst_amount`
*   **Data Type**: `float64`
*   **Business Meaning**: Goods and Services Tax (18% in India).
*   **Example Values**: `11107.82`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 141,538
*   **Whether it is Useful**: Yes.
*   **Whether it should be Removed**: **Yes, during ML model training**. It is calculated deterministically as $18\%$ of the net premium.
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: Yes
*   **Whether it may cause Data Leakage**: **Yes (High risk of data leakage)**

### 28. `annual_premium`
*   **Data Type**: `int64`
*   **Business Meaning**: Final premium charged to customer including GST.
*   **Example Values**: `74145`, `62182`
*   **Missing Values**: 0 (0.00%)
*   **Number of Unique Values**: 85,189
*   **Whether it is Useful**: Yes (This is the target column `y` for regression).
*   **Whether it should be Removed**: No (Target)
*   **Whether it needs Encoding**: No
*   **Whether it needs Scaling**: No (But target transformation like $\log(y)$ is recommended during training)
*   **Whether it may cause Data Leakage**: N/A (Target)

---

## PART 3: DATA QUALITY

### 1. Missing Values
*   **`previous_insurer`**: 22,121 missing values ($11.06\%$). These represents new car registrations or cases where the customer does not disclose their previous carrier. These can be imputed with a dedicated category `"New/Unknown"`.
*   **`addons_list`**: 50,140 missing values ($25.07\%$). This is structurally correct and corresponds to cases where `num_addons` $= 0$. We can impute these with `"No Addons"`.

### 2. Duplicate Rows and IDs
*   **Duplicate Rows**: 0 duplicate rows.
*   **Duplicate IDs (`record_id`)**: 6 duplicate record IDs. 
    *   *Analysis*: For example, `record_id` `5239c1c8` is assigned to a BYD e6 EV in Tiruchirappalli (with a 23-year-old customer) and a Honda City e:HEV hybrid in Gurgaon (with a 46-year-old customer).
    *   *Resolution*: The `record_id` column contains hash collisions or random ID duplicates. Do not use `record_id` as the database primary key. Generate an auto-incrementing UUID/integer surrogate primary key instead.

### 3. Outliers & Data Limits
*   **`idv`**: Maximum value is $2.37 \text{ Crore}$ INR. The distribution is highly right-skewed, which is correct for high-end luxury vehicles (e.g., Mercedes-Benz, BMW, Audi, BYD EV) but requires Robust Scaling.
*   **`od_premium_before_ncb`**: Maximum is $1,229,050.23$ INR. This is highly correlated with the premium pricing scale of luxury vehicles.
*   **`annual_premium`**: Outlier premiums reach up to $1,607,449$ INR. High premiums are directly linked to high IDV values. A log transformation is needed during training to help the regression model converge.

### 4. Impossible or Invalid Values
*   **`engine_cc` = 0**: 31,954 cases show $0 \text{ CC}$. These align with `segment` = `"ev"` and `fuel_type` = `"Electric"`. Thus, $0 \text{ CC}$ is a valid representation of electric motors rather than a data quality error.
*   **`customer_age`**: The minimum age is 18 and the maximum is 75, which is consistent with the legal driving ages allowed by underwriting guidelines.

---

## PART 4: BUSINESS UNDERSTANDING

### Why columns exist and how they are used:
1. **`customer_age`**: Assesses driving risk profile. Young drivers show higher claim frequencies. Affects **Premium Prediction** (high age discounts).
2. **`city` / `state`**: Affects geographical hazards (theft, flood rates). Used in **Premium Prediction** for regional pricing.
3. **`city_tier` / `city_risk_score`**: Calibrates pricing density. Tier 1 has higher traffic density. Affects **Premium Prediction** directly.
4. **`vehicle_make` / `model` / `variant`**: Determines base repair parts and replacement costs. Affects **Premium Prediction** (Own Damage base) and **Claim Prediction** (expected payout severity).
5. **`segment` / `fuel_type`**: Reflects powertrain hazard profiles (e.g. EV battery replacement is extremely costly). Affects **Premium Prediction** and **Policy Recommendation**.
6. **`colour`**: Used for asset matching. No significant impact on prediction.
7. **`vehicle_age_years` / `manufacturing_year`**: Dictates the depreciation profile. Affects **Premium Prediction** (decreases IDV-based premium components).
8. **`engine_cc`**: Maps vehicle to statutory regulatory lookup brackets. Determines **Premium Prediction** (Third Party fixed portion).
9. **`idv`**: Sum insured. Dictates maximum liability. Affects **Premium Prediction** (dominant Od premium multiplier) and **Claim Approval** limits.
10. **`ncb_percent`**: Reward for claims-free tenure. Affects **Premium Prediction** (reduces own-damage component).
11. **`claim_history_count`**: Quantifies historical customer risk. Affects **Premium Prediction** and **Fraud Detection** (prior high claims flags).
12. **`policy_type`**: Sets coverage boundaries (Comprehensive vs Third Party). Determines **Premium Prediction** structure.
13. **`previous_insurer`**: Captures market switching patterns. Used for **Policy Recommendation** discounts.
14. **`num_addons` / `addons_list`**: Lists customized protection riders selected. Affects **Premium Prediction** directly by summing up addon premiums.

---

## PART 5: TARGET ANALYSIS

### 1. Regression Target: `annual_premium`
*   **Definition**: The total premium paid by the customer, including GST.
*   **Value Range**: $2,347$ INR to $1,607,449$ INR.
*   **Mean**: $51,931.87$ INR.
*   **Standard Deviation**: $81,552.03$ INR.
*   **Distribution**: Extremely right-skewed due to luxury and EV asset profiles.

### 2. Potential Problems and Solutions
*   **High Skewness**: The target distribution is highly skewed due to luxury cars and high IDVs. Using raw values directly in linear models or neural networks can result in poor predictions for standard vehicles.
    *   *Solution*: Apply a $\log(y)$ transformation (`numpy.log1p`) during training and convert back using `numpy.expm1` for display.
*   **Actuarial Leakage**: Features like `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, and `gst_amount` are intermediate calculated values that sum up to the target. Keeping them in the training dataset will cause target leakage.
    *   *Solution*: Drop these intermediate calculation columns during ML model training. The ML model should predict the premium based on the core risk characteristics (`idv`, `vehicle_age_years`, `customer_age`, etc.).

---

## PART 6: FEATURE GROUPING

To organize our data pipeline, we group columns into the following logical clusters:

*   **Customer Features (Risk Profile)**:
    *   `customer_age`, `claim_history_count`
*   **Vehicle Features (Asset Profile)**:
    *   `vehicle_make`, `vehicle_model`, `variant`, `segment`, `fuel_type`, `colour`, `manufacturing_year`, `vehicle_age_years`, `engine_cc`
*   **Geographical Features (Location Risk)**:
    *   `city`, `state`, `city_tier`, `city_risk_score`
*   **Policy Features (Coverage Selection)**:
    *   `policy_type`, `ncb_percent`, `previous_insurer`, `num_addons`, `addons_list`
*   **Intermediate Calculations (Data Leakage Risks)**:
    *   `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount`
*   **Target Feature**:
    *   `annual_premium`
*   **Metadata**:
    *   `record_id`

---

## PART 7: FEATURE ENGINEERING IDEAS

To improve our underwriting predictions, we can engineer the following new features:

1.  **Addon Coverage Density**:
    $$\text{Addon Density} = \frac{\text{num\_addons}}{\text{Maximum Addons Available (4)}}$$
    *Justification*: Higher addon density indicates a more risk-averse customer who is willing to pay more for comprehensive coverage.
2.  **Relative Depreciation Rate**:
    $$\text{Relative Depreciation} = \frac{\text{idv}}{\text{Estimated Original Value of Model Group}}$$
    *Justification*: Shows how much value the vehicle has lost relative to its class baseline, helping refine the Own Damage risk premium.
3.  **Driver Experience Index**:
    $$\text{Driver Experience Index} = \text{customer\_age} - 18 - \text{claim\_history\_count}$$
    *Justification*: Combines driving years with claim frequency to create a unified driver quality score.
2.  **EV High-Risk Flag**:
    *   *Definition*: A binary flag set to 1 if `segment` = `"ev"` and `city_tier` = `3`.
    *   *Justification*: EVs operating in lower city tiers (Tier 3) face higher risk profiles due to limited charging infrastructure and battery repair hazards.

---

## PART 8: FEATURE SELECTION

### 1. Definitely Keep (Core ML Features)
*   `customer_age`, `city_risk_score`, `vehicle_age_years`, `engine_cc`, `idv`, `ncb_percent`, `claim_history_count`, `num_addons`, `segment`, `fuel_type`, `policy_type`, `vehicle_make`.
    *   *Justification*: These are the primary risk factors used for insurance underwriting.

### 2. Possibly Keep (Categoricals requiring careful encoding)
*   `city`, `state`, `vehicle_model`, `variant`, `colour`, `previous_insurer`, `addons_list` (pruned/expanded).
    *   *Justification*: These features add detailed granularity but introduce high cardinality. We should apply Target Encoding or expand them into binary flags.

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
| `segment` | One-Hot Encoding | None | None | None | EV Charging Risk Flag |
| `fuel_type` | One-Hot Encoding | None | None | None | None |
| `colour` | Drop or One-Hot | None | None | None | None |
| `vehicle_age_years`| None | MinMaxScaler | None | None | Relative Depreciation |
| `engine_cc` | None | StandardScaler | None | None | None |
| `idv` | None | RobustScaler | None | Log1p | Relative Depreciation |
| `ncb_percent` | None | MinMaxScaler | None | None | None |
| `claim_history_count`| None | StandardScaler| None | None | Driver Experience Index |
| `policy_type` | One-Hot Encoding | None | None | None | None |
| `previous_insurer` | One-Hot Encoding | None | Fill `"Unknown"`| None | None |
| `addons_list` | Multi-Label Binary | None | Fill `"None"` | None | Addon Density |

---

## PART 10: EDA PLAN (ROADMAP)

We will use the following visualization roadmap to analyze the data during the EDA phase:

1.  **Premium Distribution Histograms**:
    *   *Purpose*: Analyze the distribution of `annual_premium` before and after applying log transformations.
2.  **IDV vs. Premium Scatter Plot (Colored by Segment)**:
    *   *Purpose*: Validate the linear relationship between Insured Declared Value and the calculated premium across different vehicle segments.
3.  **Claim Count vs. NCB Percent Box Plots**:
    *   *Purpose*: Verify that customers with higher claim counts have lower No Claim Bonus (NCB) percentages.
4.  **Correlation Heatmap (Numerical Core Features)**:
    *   *Purpose*: Check for multi-collinearity issues (e.g., between `vehicle_age_years` and `idv` or `manufacturing_year`).
5. **Categorical Premium Boxplots**:
    *   *Purpose*: Analyze premium spreads across segments, makes, and states.

---

## PART 11: MACHINE LEARNING READINESS

*   **Is the dataset ready for ML?**: **No**.
*   **Prerequisites before model training**:
    1.  **Drop Leakage Columns**: Drop the intermediate calculation columns (`od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, and `gst_amount`).
    2.  **Addon Binarization**: Expand `addons_list` into binary columns for each addon type.
    3.  **Target Encoding**: Encode high-cardinality categorical columns like `city` and `vehicle_model`.
    4.  **Log Transformation**: Apply a log transformation to the target variable `annual_premium`.

---

## PART 12: FINAL RECOMMENDATIONS

*   **Strengths**: Clean tabular formatting, zero missing values in core features, and strong risk proxies (`idv`, `ncb_percent`, `claim_history_count`).
*   **Weaknesses**: High cardinality in model-level fields and duplicate record IDs.
*   **Risks**: Keeping calculated pricing columns in the training data will result in artificial accuracy scores during testing that fail in production.
*   **Recommended Algorithms**:
    *   **LightGBM Regressor / XGBoost Regressor**: Best suited for handling mixed numerical and encoded categorical features with non-linear relationships.
    *   **RandomForestRegressor (Scikit-learn)**: Provides a stable baseline model and integrates smoothly with SHAP explainability.

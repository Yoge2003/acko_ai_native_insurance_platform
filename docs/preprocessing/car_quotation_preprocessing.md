# Preprocessing Pipeline Design - Car Quotation
**Module Reference**: Module 2 (Insurance Premium Prediction)  
**Status**: Preprocessing Architecture Approved  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATA CLEANING STRATEGY

Here is the column-by-column cleaning strategy for all 28 columns:

1.  **`record_id`**: Drop. It is a non-predictive transaction metadata identifier.
2.  **`customer_age`**: Keep. Numerical demographic risk feature.
3.  **`city`**: Keep. High-cardinality geographical feature.
4.  **`state`**: Keep. Categorical regional feature.
5.  **`city_tier`**: Keep. Ordinal density proxy.
6.  **`city_risk_score`**: Keep. Continuous geographic hazard score.
7.  **`vehicle_make`**: Keep. Categorical asset brand feature.
8.  **`vehicle_model`**: Keep. High-cardinality vehicle feature.
9.  **`variant`**: Keep. High-cardinality vehicle trim feature.
10. **`segment`**: Keep. Categorical vehicle class.
11. **`fuel_type`**: Keep. Categorical engine class.
12. **`colour`**: Drop. Visual metadata with negligible impact on premium calculations.
13. **`manufacturing_year`**: Drop. Redundant once `vehicle_age_years` is calculated.
14. **`vehicle_age_years`**: Keep. Continuous depreciation risk factor.
15. **`engine_cc`**: Keep. Continuous statutory rating factor.
16. **`idv`**: Keep. Continuous sum insured factor.
17. **`ncb_percent`**: Keep. Continuous pricing discount modifier.
18. **`claim_history_count`**: Keep. Continuous demographic risk multiplier.
19. **`policy_type`**: Keep. Categorical coverage boundary.
20. **`previous_insurer`**: Keep. Categorical market switching risk factor.
21. **`num_addons`**: Keep. Continuous coverage pricing component.
22. **`addons_list`**: Keep. To be binarized and dropped.
23. **`od_premium_before_ncb`**: Drop. Actuarial data leakage component.
24. **`ncb_discount_amount`**: Drop. Actuarial data leakage component.
25. **`tp_premium`**: Drop. Actuarial data leakage component.
26. **`addon_premium`**: Drop. Actuarial data leakage component.
27. **`gst_amount`**: Drop. Actuarial data leakage component.
28. **`annual_premium`**: Keep. Target variable (`y`).

---

## PART 2: MISSING VALUE STRATEGY

*   **`previous_insurer`** (11.06% missing):
    *   *Strategy*: Constant imputation with `"New/Unknown"`.
    *   *Justification*: Represents new car owners or individuals with expired coverage who did not disclose their previous carrier. Imputing with a dedicated category preserves this business profile.
*   **`addons_list`** (25.07% missing):
    *   *Strategy*: Constant imputation with `"No Addons"`.
    *   *Justification*: Represents cases where `num_addons` $= 0$. Preserves the absence of add-on selection.
*   **Other features**: All other features are fully populated.

---

## PART 3: OUTLIER STRATEGY

*   **`idv`** (Sum Insured):
    *   *Strategy*: **Remain and scale**. High IDV values correspond to luxury cars (e.g. Mercedes-Benz E-Class). Clipping or removing these values would prevent the model from learning to underwrite high-value vehicle segments.
*   **`od_premium_before_ncb` & `annual_premium`**:
    *   *Strategy*: **Log-Transformation** ($\log(y + 1)$). High premium values represent luxury vehicles. Log transformation normalizes the distribution, helping the regression model converge.

---

## PART 4: ENCODING STRATEGY

*   **One-Hot Encoding**:
    *   *Features*: `state` (32 categories), `segment` (6 categories), `fuel_type` (6 categories), `policy_type` (3 categories), `previous_insurer` (8 categories).
    *   *Justification*: Category counts are low, keeping the one-hot encoded matrix computationally manageable.
*   **Target Encoding**:
    *   *Features*: `city` (117 categories), `vehicle_model` (134 categories), `variant` (29 categories).
    *   *Justification*: High-cardinality features would generate sparse matrices if one-hot encoded, leading to model overfitting. Target encoding based on the mean log premium handles this risk.
*   **Multi-Label Binarization**:
    *   *Features*: `addons_list`.
    *   *Justification*: Comma-separated lists of selected addons (e.g., "Zero Depreciation, Roadside Assistance") must be split into individual binary columns (e.g. `addon_zero_dep`, `addon_roadside_assist`) before drop.

---

## PART 5: NUMERICAL FEATURE STRATEGY

*   **`idv`**:
    *   *Strategy*: **RobustScaler**. Handles right-skewed asset value distributions by scaling based on the interquartile range (IQR).
*   **`customer_age`**, `claim_history_count`, `num_addons`:
    *   *Strategy*: **StandardScaler**. Centers variables with near-uniform or normal distributions.
*   **`vehicle_age_years`**, `ncb_percent`:
    *   *Strategy*: **MinMaxScaler**. Normalizes variables with fixed boundaries (e.g. 1 to 20 years, 0 to 50% discount) to a stable $[0, 1]$ range.
*   **`engine_cc`**:
    *   *Strategy*: **StandardScaler** with a binary `is_electric` flag (to handle 0 CC values in EVs).

---

## PART 6: DATE FEATURE STRATEGY

There are no date columns in the quotation dataset. The age of the vehicle is represented by the integer column `vehicle_age_years`.

---

## PART 7: BOOLEAN FEATURE STRATEGY

Individual addon flags generated from the `addons_list` will be stored as binary integers (0 or 1), which is natively supported by gradient boosting models.

---

## PART 8: FEATURE ENGINEERING PLAN

1.  **Addon Coverage Density**:
    $$\text{Addon Density} = \frac{\text{num\_addons}}{\text{Maximum Addons Available (4)}}$$
    *Business Value*: Identifies risk-averse customers willing to pay more for comprehensive protection.
2.  **Relative Depreciation Rate**:
    $$\text{Relative Depreciation} = \frac{\text{idv}}{\text{Estimated Original Value of Model Group}}$$
    *Business Value*: Tracks vehicle value loss relative to its class baseline to refine pricing adjustments.
3.  **Driver Experience Index**:
    $$\text{Driver Experience Index} = \text{customer\_age} - 18 - \text{claim\_history\_count}$$
    *Business Value*: Combines driving years with claims history to evaluate driver quality.
4.  **EV High-Risk Flag**:
    *   *Definition*: Set to 1 if `segment` = `"ev"` and `city_tier` = `3`.
    *   *Business Value*: Flags EVs operating in lower city tiers with limited battery repair infrastructure.

---

## PART 9: FEATURE SELECTION PLAN

### 1. Definitely Keep
*   `customer_age`, `city_risk_score`, `vehicle_age_years`, `engine_cc`, `idv`, `ncb_percent`, `claim_history_count`, `num_addons`, `segment`, `fuel_type`, `policy_type`, `vehicle_make`.
    *   *Justification*: Core risk factors used for insurance underwriting.

### 2. Possibly Keep
*   `city`, `state`, `vehicle_model`, `variant`, `previous_insurer`, `addons_list` (binarized).
    *   *Justification*: Add granularity but increase cardinality. Apply target encoding or multi-label binarization.

### 3. Remove (Target Leakage & Redundant)
*   `record_id` (Non-predictive metadata).
*   `colour` (Negligible pricing correlation).
*   `manufacturing_year` (Redundant with `vehicle_age_years`).
*   `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount` (Direct target leakage).

---

## PART 10: PREPROCESSING PIPELINE DESIGN

```text
       Raw Quotation Record (JSON / DataFrame)
                         │
                         ▼
             [1. Structural Drops]
             Drop record_id, colour, manufacturing_year
                         │
                         ▼
             [2. Data Leakage Pruning]
             Drop od_premium_before_ncb, ncb_discount_amount, 
             tp_premium, addon_premium, gst_amount
                         │
                         ▼
             [3. Imputation & Expansion]
             - previous_insurer ──► Fill "New/Unknown"
             - addons_list      ──► Fill "No Addons" ──► MultiLabelBinarizer
                         │
                         ▼
             [4. Feature Engineering]
             Calculate Addon Density, Relative Depreciation, 
             Driver Experience Index, EV High-Risk Flag
                         │
                         ▼
             [5. Column Transformations]
             - High-Card Categorical (city, model, variant) ──► TargetEncoder
             - Low-Card Categorical (state, segment, fuel)  ──► OneHotEncoder
             - Numerical Outliers (idv)                      ──► RobustScaler
             - Numerical Normal (age, cc)                     ──► StandardScaler
             - Numerical Bounded (vehicle_age, ncb)           ──► MinMaxScaler
                         │
                         ▼
           Processed Feature Array (ML Ready)
```

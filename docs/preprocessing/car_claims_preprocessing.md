# Preprocessing Pipeline Design - Car Claims
**Module Reference**: Module 3 (AI Claims Engine)
**Status**: Preprocessing Architecture Approved
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATA CLEANING STRATEGY

Column-by-column cleaning decisions for all 32 columns:

| Column | Action | Justification |
| :--- | :--- | :--- |
| `record_id` | **Drop** | Non-predictive transaction ID. 5 hash-collision duplicates found. |
| `customer_age` | **Keep** | Demographic fraud risk signal. |
| `city` | **Keep** | Geographical risk feature for theft and accident patterns. |
| `state` | **Keep** | Regional regulatory and claims frequency proxy. |
| `city_tier` | **Keep** | Urban density proxy; correlated with traffic and theft risk. |
| `city_risk_score` | **Keep** | Continuous actuarial hazard multiplier per city. |
| `vehicle_make` | **Keep** | Parts cost baseline and theft-targeting profile. |
| `vehicle_model` | **Keep** | Model-level repair cost and stolen-parts market profile. |
| `segment` | **Keep** | Vehicle class risk profile. |
| `engine_cc` | **Keep** | Coverage scope indicator; EV marker (0 CC). |
| `manufacturing_year` | **Drop** | Redundant. `vehicle_age_years` is the correct depreciation feature. |
| `vehicle_age_years` | **Keep** | Depreciation factor; older vehicles often have inflated claim amounts. |
| `idv` | **Keep** | Maximum liability ceiling. Cross-check against `claim_amount`. |
| `policy_type` | **Keep** | Determines coverage scope — critical for coverage validation logic. |
| `policy_age_months` | **Keep** | Early-claim fraud indicator. Claims < 2 months = high fraud risk. |
| `annual_premium_paid` | **Keep** | Customer risk tier proxy (low premium → lower coverage limits). |
| `previous_claims_count` | **Keep** | Historical claimant frequency. |
| `ncb_at_claim_percent` | **Keep** | Validates NCB consistency against claims history. |
| `zero_dep_addon` | **Keep** | Critical for payout calculation: zero-dep = full parts replacement. |
| `engine_protection_addon` | **Keep** | Critical coverage validation: engine damage requires this addon. |
| `incident_date` | **Convert → Drop** | Parse to extract temporal features; drop raw string after extraction. |
| `incident_day_of_week` | **Keep** | Identifies weekend/weekday risk patterns. |
| `incident_month` | **Keep** | Seasonality signal (monsoon = flooding cluster). |
| `incident_time_of_day` | **Keep** | Night accidents have elevated fraud/severity risk. |
| `incident_type` | **Keep** | Primary claim category. Strongest approval predictor. |
| `damage_type` | **Keep** | Cross-validated against `incident_type` for consistency. |
| `damage_severity_score` | **Keep** | 1–10 numeric rating; Gemini Vision output maps here. |
| `num_parts_affected` | **Keep** | Scope indicator for repair complexity. |
| `affected_parts` | **Keep → Expand → Drop** | Multi-label binarize then drop raw string. |
| `claim_amount` | **Keep** | Core fraud signal — compare against IDV and severity. |
| `approval_probability` | **Drop** | **Target leakage**. Derived directly from `claim_approved`. |
| `claim_approved` | **Keep** | Binary classification target `y`. |

---

## PART 2: MISSING VALUE STRATEGY

| Feature | Missing % | Strategy | Justification |
| :--- | :--- | :--- | :--- |
| All features | 0.0% | No action required | The car claims dataset is fully populated — no missing values detected across all 32 columns. |

---

## PART 3: OUTLIER STRATEGY

| Feature | Outlier Presence | Strategy | Justification |
| :--- | :--- | :--- | :--- |
| `claim_amount` | 3,083 records > 5,000,000 INR | **Retain + RobustScaler + Log1p** | Extreme values represent legitimate total-loss events on luxury vehicles. Removing would bias the model against high-severity claims. |
| `idv` | ~3,068 records > 7.5M INR | **Retain + RobustScaler** | High IDV = luxury vehicles. Valid data points for underwriting high-value asset classes. |
| `approval_probability` | 931 records < 0.35 | **Drop entire column** | Leakage column — outlier analysis irrelevant. |
| `annual_premium_paid` | No statistical outliers detected | **StandardScaler** | Normal distribution within realistic premium bounds. |
| `damage_severity_score` | No outliers — bounded [1, 10] | **MinMaxScaler** | Design-bounded variable. No outlier risk. |

---

## PART 4: ENCODING STRATEGY

| Feature | Cardinality | Encoding | Justification |
| :--- | :--- | :--- | :--- |
| `policy_type` | 3 | One-Hot Encoding | Comprehensive / Third Party / Own Damage — unordered. |
| `incident_type` | 6 | One-Hot Encoding | Key approval predictor. Unordered categories (Accident, Theft, Flooding, etc.). |
| `incident_day_of_week` | 7 | One-Hot Encoding | Day-of-week risk patterns are unordered. |
| `incident_time_of_day` | 4 | One-Hot Encoding | Morning / Afternoon / Evening / Night — unordered. |
| `damage_type` | 13 | One-Hot Encoding | Unordered damage categories. Manageable expansion. |
| `segment` | 6 | One-Hot Encoding | Vehicle class. Unordered. |
| `vehicle_make` | 18 | One-Hot Encoding | Brand-level repair cost profile. Manageable cardinality. |
| `state` | 32 | One-Hot Encoding | Regional clustering. Manageable expansion with sparse option. |
| `city` | 117 | **Target Encoding** | High cardinality — encode based on mean approval rate per city. |
| `vehicle_model` | 134 | **Target Encoding** | High cardinality — encode based on mean approval rate per model. |
| `affected_parts` | Multi-label string | **MultiLabelBinarizer** | Expand comma-separated part lists into binary indicator columns, then drop raw. |
| `zero_dep_addon` | Binary 0/1 | Already integer | No encoding needed. Pass through as-is. |
| `engine_protection_addon` | Binary 0/1 | Already integer | No encoding needed. Pass through as-is. |
| `claim_approved` | Binary 0/1 | Already integer (target) | Target variable. No encoding. |

**Affected Parts Binary Columns to Generate** (from `affected_parts`):
Key individual components including: `part_bumper`, `part_windshield`, `part_headlight`, `part_hood`, `part_engine`, `part_radiator`, `part_door_panel`, `part_alloy_wheel`, `part_side_mirror`, `part_dashboard`, `part_taillight`, `part_axle`, `part_fuel_tank` (plus others extracted from unique values).

---

## PART 5: NUMERICAL FEATURE STRATEGY

| Feature | Scaler | Transformation | Justification |
| :--- | :--- | :--- | :--- |
| `claim_amount` | RobustScaler | Log1p pre-scale | Heavily right-skewed. Outlier-resistant scaling prevents luxury claims from distorting the model. |
| `idv` | RobustScaler | Log1p pre-scale | Same justification as `claim_amount`. Correlated with claim magnitude. |
| `annual_premium_paid` | StandardScaler | None | Near-normal distribution. Standard centering appropriate. |
| `customer_age` | StandardScaler | None | Uniform distribution (18–75). |
| `previous_claims_count` | StandardScaler | None | Low-variance count [0, 4]. |
| `vehicle_age_years` | MinMaxScaler | None | Fixed bounds [1, 20]. |
| `policy_age_months` | MinMaxScaler | None | Fixed bounds [1, 60]. |
| `ncb_at_claim_percent` | MinMaxScaler | None | Discrete ordinal ladder [0, 20, 25, 35, 45, 50]. |
| `damage_severity_score` | MinMaxScaler | None | Design-bounded [1, 10]. Maps cleanly to [0, 1]. |
| `num_parts_affected` | MinMaxScaler | None | Bounded [1, 6]. |
| `engine_cc` | StandardScaler | None | Add `is_electric` flag for 0-CC EVs. |
| `city_risk_score` | Passthrough | None | Already scaled [0.82, 1.50]. Preserve actuarial interpretability. |
| `city_tier` | Passthrough | None | Ordinal integer [1, 2, 3]. Directly usable. |

---

## PART 6: DATE FEATURE STRATEGY

The `incident_date` column is a string in `YYYY-MM-DD` format spanning 2005–2024.

**Temporal Features to Extract** before dropping the raw string:

| New Feature | Formula | Business Meaning |
| :--- | :--- | :--- |
| `incident_year` | `pd.to_datetime(incident_date).dt.year` | Cross-reference against policy purchase year. |
| `incident_month` | Already present as integer | Keep as-is. |
| `incident_day_of_week` | Already present as string | Encode as One-Hot. |
| `policy_to_incident_days` | `(incident_date - policy_start_date)` | **Early claim fraud flag**. Days since policy start; < 60 days = high fraud risk. |
| `incident_is_weekend` | `1 if incident_day_of_week in ["Saturday", "Sunday"]` | Weekends show higher accident and fraud rates. |

> **Note**: `policy_start_date` is not directly in the dataset. `policy_age_months` is the proxy. Use `policy_age_months < 2` as the early-claim fraud flag.

---

## PART 7: BOOLEAN FEATURE STRATEGY

| Feature | Current Type | Strategy |
| :--- | :--- | :--- |
| `zero_dep_addon` | int64 (0 or 1) | Keep as `int8`. Natively supported by all estimators. |
| `engine_protection_addon` | int64 (0 or 1) | Keep as `int8`. Natively supported. |
| Engineered: `early_claim_flag` | Derived binary | Store as `int8`. |
| Engineered: `incident_is_weekend` | Derived binary | Store as `int8`. |
| Engineered: `is_electric` | Derived binary | Store as `int8`. |
| Binarized `part_*` columns | Derived binary | Store as `int8`. |

---

## PART 8: FEATURE ENGINEERING PLAN

| Feature Name | Formula / Logic | Business Value | ML Value | Expected Impact |
| :--- | :--- | :--- | :--- | :--- |
| `claim_to_idv_ratio` | `claim_amount / idv` | Flags over-insured or inflated claims. Ratio > 1.0 = potential fraud. | Strong fraud signal. Normalizes claim size against asset value. | **High** — direct fraud detection signal. |
| `early_claim_flag` | `1 if policy_age_months <= 2 else 0` | Early claims are correlated with pre-existing damage or staging fraud. | Binary fraud predictor. | **High** — rejection rate > 35% for early claims. |
| `incident_is_weekend` | `1 if incident_day_of_week in ["Saturday", "Sunday"] else 0` | Weekend accidents show higher severity and lower visibility. | Binary time-risk signal. | **Medium** — modest separation in approval rates. |
| `monsoon_flood_match` | `1 if incident_type == "Flooding" AND incident_month in [6,7,8,9] else 0` | Validates flood claims against monsoon seasonality. | Binary consistency validator. | **High** — non-monsoon flood claims are fraud indicators. |
| `addon_coverage_match` | `1 if damage_type == "engine damage" AND engine_protection_addon == 1 else 0` | Validates coverage existence for claimed damage type. | Binary coverage validator. | **High** — coverage mismatch = guaranteed rejection. |
| `severity_claim_ratio` | `claim_amount / (damage_severity_score × 10000)` | Checks if claim amount is proportional to damage severity. | Fraud magnitude signal. | **High** — over-inflated amounts relative to severity flag fraud. |
| `is_electric` | `1 if engine_cc == 0 else 0` | EV flag for powertrain-aware pricing and repair cost estimation. | Structural binary split for tree models. | **Medium** — EV claims have distinct repair profiles. |
| `repeat_claimant_flag` | `1 if previous_claims_count >= 3 else 0` | Identifies high-frequency claimants subject to stricter review. | Binary risk profiling feature. | **Medium** — correlates with elevated rejection probability. |

---

## PART 9: FEATURE SELECTION PLAN

### Definitely Keep — Core Claims Approval Signals
| Feature | Reason |
| :--- | :--- |
| `claim_amount` | Primary sizing signal. Strongest predictor after leakage removal. |
| `idv` | Coverage ceiling. Critical for claim-to-IDV ratio. |
| `damage_severity_score` | Quantified damage extent. Gemini Vision output maps here. |
| `incident_type` | Primary claim category. Theft/Vandalism → higher rejection risk. |
| `damage_type` | Cross-validates incident narrative consistency. |
| `policy_age_months` | Early-claim fraud proxy. |
| `previous_claims_count` | Repeat claimant risk score. |
| `zero_dep_addon` | Coverage validation for parts replacement payout. |
| `engine_protection_addon` | Coverage validation for engine repair payout. |
| `num_parts_affected` | Scope of claim complexity. |
| `policy_type` | Defines valid coverage categories for the claim. |
| `vehicle_age_years` | Depreciation context for claim valuation. |
| Engineered: `claim_to_idv_ratio` | Most powerful fraud detection signal. |
| Engineered: `early_claim_flag` | Direct fraud timing indicator. |
| Engineered: `monsoon_flood_match` | Seasonality consistency validator. |
| Engineered: `severity_claim_ratio` | Proportionality fraud check. |

### Possibly Keep — Situational Predictors
| Feature | Reason |
| :--- | :--- |
| `customer_age` | Demographic fraud profiling. Include if feature importance confirms value. |
| `city` / `state` | Geographic fraud clustering. Requires target encoding. |
| `vehicle_model` | Model-specific theft and repair cost patterns. |
| `incident_time_of_day` | Night claims have modestly higher fraud rates. |
| `incident_day_of_week` | Weekend vs. weekday risk patterns. |
| `incident_is_weekend` | Derived binary — include if it outperforms raw day-of-week. |
| Binarized `part_*` columns | Validate narrative against affected parts list. |
| `ncb_at_claim_percent` | Cross-check against claims history for consistency. |
| `annual_premium_paid` | Customer tier — low premium customers may have higher fraud incentive. |

### Remove — Leakage, Redundant, or Identifier
| Feature | Reason |
| :--- | :--- |
| `record_id` | Identifier. No predictive value. |
| `manufacturing_year` | Redundant with `vehicle_age_years`. |
| `incident_date` (raw) | Replaced by extracted temporal features. |
| `approval_probability` | **Target leakage**. Near-perfect correlation with `claim_approved`. |
| `affected_parts` (raw) | Replaced by binarized `part_*` columns. |

---

## PART 10: PREPROCESSING PIPELINE DESIGN

```text
┌─────────────────────────────────────────────────────────────┐
│          Raw Car Claims Record (CSV / DataFrame)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1 — STRUCTURAL DROPS                                  │
│  Drop: record_id, manufacturing_year, approval_probability  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2 — DATE FEATURE EXTRACTION                           │
│  incident_date ──► parse to datetime                        │
│  Extract: incident_is_weekend                               │
│  Drop raw incident_date string                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3 — AFFECTED PARTS MULTI-LABEL BINARIZATION           │
│  affected_parts ──► MultiLabelBinarizer ──► part_* columns  │
│  Drop raw affected_parts column                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4 — FEATURE ENGINEERING                               │
│  Create: claim_to_idv_ratio, early_claim_flag,              │
│          monsoon_flood_match, addon_coverage_match,         │
│          severity_claim_ratio, is_electric,                 │
│          repeat_claimant_flag, incident_is_weekend          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5 — ENCODING                                          │
│  High-cardinality (city, vehicle_model)                     │
│    ──► TargetEncoder (mean of claim_approved)               │
│  Low-cardinality (state, segment, vehicle_make,             │
│    policy_type, incident_type, damage_type,                 │
│    incident_time_of_day, incident_day_of_week)              │
│    ──► OneHotEncoder (drop='first')                         │
│  Binary addons, flags ──► Pass-through int8                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6 — SCALING                                           │
│  claim_amount, idv  ──► Log1p ──► RobustScaler              │
│  customer_age,                                              │
│    annual_premium_paid,                                     │
│    previous_claims_count,                                   │
│    engine_cc        ──► StandardScaler                      │
│  vehicle_age_years,                                         │
│    policy_age_months,                                       │
│    ncb_at_claim_percent,                                    │
│    damage_severity_score,                                   │
│    num_parts_affected ──► MinMaxScaler                      │
│  city_risk_score    ──► Passthrough                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7 — CLASS IMBALANCE HANDLING (Training Only)          │
│  Apply SMOTE on training split OR use                       │
│  class_weight = {0: 5.9, 1: 1.0} in classifier             │
│  (Ratio: 21,597 rejected vs 128,403 approved ≈ 1:5.9)      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         Processed Feature Array (ML Ready)                  │
│  Approx. ~100 columns after encoding + binarization         │
│  Target: claim_approved (binary 0/1)                        │
└─────────────────────────────────────────────────────────────┘
```

**Class Weight Reference**:
```python
# Imbalance ratio: 85.6% approved vs 14.4% rejected
# Preferred approach for XGBoost:
scale_pos_weight = 128403 / 21597  # ≈ 5.95

# Preferred approach for Scikit-learn classifiers:
class_weight = {0: 5.95, 1: 1.0}
```

**Evaluation Metrics** (do NOT use raw Accuracy due to imbalance):
- Primary: **F1-Score (macro)** and **Recall for class 0 (rejections)**
- Secondary: **ROC-AUC**, **Precision-Recall AUC**
- Threshold: Tune decision threshold using the Precision-Recall curve rather than defaulting to 0.5.

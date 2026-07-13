# Preprocessing Pipeline Design - Bike Claims
**Module Reference**: Module 3 (AI Claims Engine)
**Status**: Preprocessing Architecture Approved
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATA CLEANING STRATEGY

Column-by-column cleaning decisions for all 34 columns:

| Column | Action | Justification |
| :--- | :--- | :--- |
| `record_id` | **Drop** | Non-predictive identifier. Zero hash-collision duplicates in this dataset. |
| `customer_age` | **Keep** | Demographic risk signal. Younger riders carry higher accident probability. |
| `city` | **Keep** | Theft and road accident frequency by geography. |
| `state` | **Keep** | Regional regulatory and traffic pattern proxy. |
| `city_tier` | **Keep** | Urban density risk proxy. |
| `city_risk_score` | **Keep** | Continuous actuarial hazard multiplier. |
| `vehicle_make` | **Keep** | Parts cost profile and theft-targeting data per manufacturer. |
| `vehicle_model` | **Keep** | Model-level repair cost baseline. |
| `segment` | **Keep** | Bike class risk profile (sport, commuter, ev_scooter, etc.). |
| `engine_cc` | **Keep** | Coverage scope and EV marker (0 CC = electric). |
| `manufacturing_year` | **Drop** | Redundant with `vehicle_age_years`. |
| `vehicle_age_years` | **Keep** | Depreciation factor and fraud risk for older vehicles. |
| `idv` | **Keep** | Maximum liability ceiling. Critical for claim-to-IDV ratio. |
| `policy_type` | **Keep** | Defines valid claim categories (Comprehensive vs Third Party). |
| `policy_age_months` | **Keep** | Early-claim fraud timing indicator. |
| `annual_premium_paid` | **Keep** | Customer risk tier proxy. |
| `previous_claims_count` | **Keep** | Claims frequency history. |
| `ncb_at_claim_percent` | **Keep** | NCB consistency cross-check against claims history. |
| `zero_dep_addon` | **Keep** | Coverage validation for parts replacement payout. |
| `usage_type` | **Keep** | **Bike-specific**: Personal / Commercial / Delivery — major risk differentiator. |
| `rider_experience_years` | **Keep** | **Bike-specific**: Riding proficiency. Novice riders have lower approval rates. |
| `helmet_worn` | **Keep** | **Bike-specific**: Safety compliance flag. Non-compliance can reduce personal injury payouts. |
| `incident_date` | **Convert → Drop** | Parse to extract temporal features; drop raw string after extraction. |
| `incident_day_of_week` | **Keep** | Weekday/weekend risk pattern. |
| `incident_month` | **Keep** | Monsoon seasonality signal. |
| `incident_time_of_day` | **Keep** | Night accidents have elevated fraud and severity risk. |
| `incident_type` | **Keep** | Primary claim category. Strongest approval predictor. |
| `damage_type` | **Keep** | Cross-validates incident narrative consistency. |
| `damage_severity_score` | **Keep** | 1–10 rating; Gemini Vision output maps here. |
| `num_parts_affected` | **Keep** | Scope indicator for repair complexity. |
| `affected_parts` | **Keep → Expand → Drop** | Multi-label binarize then drop raw string. |
| `claim_amount` | **Keep** | Core fraud signal — compare against IDV and severity. |
| `approval_probability` | **Drop** | **Target leakage**. Derived directly from `claim_approved`. |
| `claim_approved` | **Keep** | Binary classification target `y`. |

---

## PART 2: MISSING VALUE STRATEGY

| Feature | Missing % | Strategy | Justification |
| :--- | :--- | :--- | :--- |
| All features | 0.0% | No action required | The bike claims dataset is fully populated — no missing values across all 34 columns. |

---

## PART 3: OUTLIER STRATEGY

| Feature | Outlier Presence | Strategy | Justification |
| :--- | :--- | :--- | :--- |
| `claim_amount` | 1,469 records > 500,000 INR | **Retain + RobustScaler + Log1p** | Legitimate total-loss claims for premium superbikes (Kawasaki Ninja H2R, KTM RC 8C). Removing would create blind spot for high-value claims. |
| `idv` | 2,022 records > 3× IQR | **Retain + RobustScaler** | High IDV = superbikes. Valid underwriting segment. |
| `engine_cc` | 2,508 records > 3× IQR (superbike engines > 800CC) | **Retain + StandardScaler + is_electric flag** | 0 CC = valid EV; high CC = valid superbike. Both extremes are legitimate. |
| `approval_probability` | 722 records < 0.35 | **Drop entire column** | Leakage column — outlier analysis irrelevant. |
| `rider_experience_years` | None detected | **MinMaxScaler** | Bounded [0, 30]. No outlier risk. |
| `damage_severity_score` | None detected — bounded [1, 10] | **MinMaxScaler** | Design-bounded variable. |

---

## PART 4: ENCODING STRATEGY

| Feature | Cardinality | Encoding | Justification |
| :--- | :--- | :--- | :--- |
| `policy_type` | 3 | One-Hot Encoding | Unordered coverage categories. |
| `usage_type` | 3 | One-Hot Encoding | Personal / Commercial / Delivery — unordered, mutually exclusive. |
| `incident_type` | 6 | One-Hot Encoding | Key approval predictor. Unordered incident categories. |
| `incident_time_of_day` | 4 | One-Hot Encoding | Morning / Afternoon / Evening / Night — unordered. |
| `damage_type` | 13 | One-Hot Encoding | Unordered damage categories. |
| `segment` | 16 | One-Hot Encoding | Bike class categories. Manageable expansion. |
| `vehicle_make` | 13 | One-Hot Encoding | Brand-level profile. Low cardinality. |
| `state` | 32 | One-Hot Encoding | Regional clustering. |
| `incident_day_of_week` | 7 | One-Hot Encoding | Day risk patterns — unordered. |
| `city` | 117 | **Target Encoding** | High cardinality — encode based on mean approval rate per city. |
| `vehicle_model` | 138 | **Target Encoding** | High cardinality — encode based on mean approval rate per model. |
| `affected_parts` | Multi-label string | **MultiLabelBinarizer** | Expand comma-separated part lists into binary indicator columns, then drop raw. |
| `zero_dep_addon` | Binary 0/1 | Pass-through | Already integer. No encoding needed. |
| `helmet_worn` | Binary 0/1 | Pass-through | Already integer. |
| `claim_approved` | Binary 0/1 | Pass-through (target) | Target variable. No encoding. |

**Affected Parts Binary Columns to Generate** (from bike `affected_parts`):
Key individual components including: `part_handlebar`, `part_fuel_tank`, `part_front_fender`, `part_rear_fender`, `part_headlight`, `part_taillight`, `part_indicator`, `part_engine`, `part_exhaust`, `part_seat`, `part_frame`, `part_chain_sprocket`, `part_brakes`, `part_tyres` (plus others extracted from unique values).

---

## PART 5: NUMERICAL FEATURE STRATEGY

| Feature | Scaler | Transformation | Justification |
| :--- | :--- | :--- | :--- |
| `claim_amount` | RobustScaler | Log1p pre-scale | Right-skewed. Superbike total-loss claims create extreme outliers. |
| `idv` | RobustScaler | Log1p pre-scale | Superbike IDVs up to 38L INR. Outlier-resistant scaling required. |
| `annual_premium_paid` | StandardScaler | None | Near-normal distribution. |
| `customer_age` | StandardScaler | None | Uniform distribution (18–65). |
| `previous_claims_count` | StandardScaler | None | Low-variance count [0, 4]. |
| `engine_cc` | StandardScaler | None | Wide range (0–1,833). Add `is_electric` flag. |
| `vehicle_age_years` | MinMaxScaler | None | Fixed bounds [1, 20]. |
| `policy_age_months` | MinMaxScaler | None | Fixed bounds [1, 60]. |
| `ncb_at_claim_percent` | MinMaxScaler | None | Discrete ordinal ladder [0, 50]. |
| `damage_severity_score` | MinMaxScaler | None | Design-bounded [1, 10]. |
| `num_parts_affected` | MinMaxScaler | None | Bounded [1, 5] for bikes. |
| `rider_experience_years` | MinMaxScaler | None | Bounded [0, 30]. |
| `city_risk_score` | Passthrough | None | Already scaled [0.82, 1.50]. |
| `city_tier` | Passthrough | None | Ordinal integer [1, 2, 3]. |

---

## PART 6: DATE FEATURE STRATEGY

The `incident_date` column is a string in `YYYY-MM-DD` format spanning 2005–2024.

**Temporal Features to Extract** before dropping the raw string:

| New Feature | Formula | Business Meaning |
| :--- | :--- | :--- |
| `incident_is_weekend` | `1 if incident_day_of_week in ["Saturday", "Sunday"] else 0` | Weekend accidents show higher severity and claim fraud risk. |
| `incident_year` | `pd.to_datetime(incident_date).dt.year` | Cross-reference against policy start year for early-claim detection. |

> **Early Claim Proxy**: Since `policy_start_date` is not directly available, use `policy_age_months < 2` as the early-claim fraud flag (same approach as car claims).

---

## PART 7: BOOLEAN FEATURE STRATEGY

| Feature | Current Type | Strategy |
| :--- | :--- | :--- |
| `zero_dep_addon` | int64 (0 or 1) | Keep as `int8`. No encoding needed. |
| `helmet_worn` | int64 (0 or 1) | Keep as `int8`. **Critical bike-specific feature**. |
| Engineered: `early_claim_flag` | Derived binary | Store as `int8`. |
| Engineered: `incident_is_weekend` | Derived binary | Store as `int8`. |
| Engineered: `is_electric` | Derived binary | Store as `int8`. |
| Engineered: `non_helmet_injury_flag` | Derived binary | Store as `int8`. |
| Binarized `part_*` columns | Derived binary | Store as `int8`. |

---

## PART 8: FEATURE ENGINEERING PLAN

| Feature Name | Formula / Logic | Business Value | ML Value | Expected Impact |
| :--- | :--- | :--- | :--- | :--- |
| `claim_to_idv_ratio` | `claim_amount / idv` | Flags over-insured or inflated claims. Ratio > 1.0 = potential fraud. | Fraud magnitude signal. | **High** — most powerful continuous fraud indicator. |
| `early_claim_flag` | `1 if policy_age_months <= 2 else 0` | Early claims correlate with pre-existing damage staging. | Binary fraud timing predictor. | **High** — rejection rate > 35% for early claims. |
| `monsoon_flood_match` | `1 if incident_type == "Flooding" AND incident_month in [6,7,8,9] else 0` | Validates flood claims against monsoon seasonality. | Binary consistency validator. | **High** — off-season flood claims are fraud indicators. |
| `non_helmet_injury_flag` | `1 if helmet_worn == 0 AND incident_type == "Accident" else 0` | Identifies non-compliant accident claims subject to partial payout reduction. | Combined safety + incident signal. | **High** — direct policy coverage exclusion trigger. |
| `severity_claim_ratio` | `claim_amount / (damage_severity_score × 5000)` | Checks if claim amount is proportional to damage severity for bikes. | Fraud magnitude proportionality check. | **High** — inflated amounts relative to severity flag fraud. |
| `delivery_high_risk_flag` | `1 if usage_type == "Delivery" AND city_risk_score > 1.1 else 0` | Flags delivery riders in high-risk cities for closer scrutiny. | High-exposure combined signal. | **Medium** — delivery + high-risk city = elevated accident rate. |
| `is_electric` | `1 if engine_cc == 0 else 0` | EV flag for powertrain-aware repair cost estimation. | Structural binary split for tree models. | **Medium** — EV battery claims have distinct profiles. |
| `novice_rider_flag` | `1 if rider_experience_years <= 2 else 0` | Novice riders have lower approval rates (~74% vs 91%). | Binary risk profiling feature. | **Medium** — experience threshold effect on approvals. |
| `incident_is_weekend` | `1 if incident_day_of_week in ["Saturday","Sunday"] else 0` | Weekend accidents cluster with higher severity events. | Binary temporal risk signal. | **Low-Medium** — modest approval rate separation. |
| `experienced_safe_rider` | `1 if rider_experience_years >= 5 AND helmet_worn == 1 AND previous_claims_count == 0 else 0` | Identifies the lowest-risk rider profile. | Binary fast-approval signal. | **Medium** — high precision for auto-approval routing. |

---

## PART 9: FEATURE SELECTION PLAN

### Definitely Keep — Core Claims Approval Signals
| Feature | Reason |
| :--- | :--- |
| `claim_amount` | Primary fraud signal and approval sizing indicator. |
| `idv` | Coverage ceiling and claim proportionality check. |
| `damage_severity_score` | Quantified damage extent. Gemini Vision output maps here. |
| `incident_type` | Primary claim category — Theft/Vandalism → higher rejection. |
| `damage_type` | Cross-validates narrative consistency. |
| `policy_age_months` | Early-claim fraud timing proxy. |
| `previous_claims_count` | Repeat claimant risk score. |
| `zero_dep_addon` | Coverage validation for parts payout. |
| `helmet_worn` | **Bike-specific**. Safety compliance and injury payout eligibility. |
| `rider_experience_years` | **Bike-specific**. Proficiency proxy for accident risk. |
| `usage_type` | **Bike-specific**. Commercial/delivery exposure risk. |
| `num_parts_affected` | Claim scope complexity. |
| `policy_type` | Defines valid coverage for the claim type. |
| `vehicle_age_years` | Depreciation context for claim valuation. |
| Engineered: `claim_to_idv_ratio` | Most powerful fraud detection signal. |
| Engineered: `early_claim_flag` | Fraud timing indicator. |
| Engineered: `monsoon_flood_match` | Seasonality consistency check. |
| Engineered: `non_helmet_injury_flag` | Coverage exclusion trigger. |
| Engineered: `severity_claim_ratio` | Fraud proportionality check. |
| Engineered: `experienced_safe_rider` | Auto-approval routing signal. |

### Possibly Keep — Situational Predictors
| Feature | Reason |
| :--- | :--- |
| `customer_age` | Demographic fraud profiling. Validate with feature importance. |
| `city` / `state` | Geographic fraud pattern clustering. Requires target encoding. |
| `vehicle_model` | Model-specific theft and repair cost patterns. |
| `incident_time_of_day` | Night claims show higher fraud rates. |
| `incident_day_of_week` | Weekend vs. weekday risk patterns. |
| Binarized `part_*` columns | Narrative consistency validation. |
| `ncb_at_claim_percent` | NCB cross-check against claims history. |
| `novice_rider_flag` | Binary distillation of `rider_experience_years`. |
| `delivery_high_risk_flag` | Combined exposure signal. |

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
│          Raw Bike Claims Record (CSV / DataFrame)           │
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
│  incident_date ──► parse datetime                           │
│  Extract: incident_is_weekend, incident_year                │
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
│          monsoon_flood_match, non_helmet_injury_flag,        │
│          severity_claim_ratio, delivery_high_risk_flag,     │
│          is_electric, novice_rider_flag,                    │
│          experienced_safe_rider, incident_is_weekend        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5 — ENCODING                                          │
│  High-cardinality (city, vehicle_model)                     │
│    ──► TargetEncoder (mean of claim_approved)               │
│  Low-cardinality (state, segment, vehicle_make,             │
│    usage_type, policy_type, incident_type, damage_type,     │
│    incident_time_of_day, incident_day_of_week)              │
│    ──► OneHotEncoder (drop='first')                         │
│  Binary addons, flags ──► Pass-through int8                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6 — SCALING                                           │
│  claim_amount, idv ──► Log1p ──► RobustScaler               │
│  customer_age,                                              │
│    annual_premium_paid,                                     │
│    previous_claims_count,                                   │
│    engine_cc       ──► StandardScaler                       │
│  vehicle_age_years,                                         │
│    policy_age_months,                                       │
│    ncb_at_claim_percent,                                    │
│    damage_severity_score,                                   │
│    num_parts_affected,                                      │
│    rider_experience_years ──► MinMaxScaler                  │
│  city_risk_score   ──► Passthrough                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7 — CLASS IMBALANCE HANDLING (Training Only)          │
│  88,568 approved vs 11,432 rejected ≈ 1:7.75 ratio         │
│  Apply SMOTE on training split OR use                       │
│  scale_pos_weight = 88568 / 11432 ≈ 7.75 (XGBoost)         │
│  class_weight = {0: 7.75, 1: 1.0} (Scikit-learn)           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         Processed Feature Array (ML Ready)                  │
│  Approx. ~110 columns after encoding + binarization         │
│  Target: claim_approved (binary 0/1)                        │
└─────────────────────────────────────────────────────────────┘
```

**Evaluation Metrics** (do NOT use raw Accuracy due to imbalance):
- Primary: **Recall for class 0 (rejections)** and **F1-Score (macro)**
- Secondary: **ROC-AUC**, **Precision-Recall AUC**
- Routing: Tune decision threshold below 0.5 to increase rejection recall (catch more fraud).

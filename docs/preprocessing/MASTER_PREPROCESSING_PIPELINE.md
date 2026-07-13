# Master Preprocessing Pipeline Design
**Project Name**: ACKO AI Native Insurance Platform
**Phase**: 2.3 — Data Cleaning Strategy & Preprocessing Pipeline Design
**Audience**: Senior Data Scientists & ML Engineers
**Status**: Ready for Implementation Review

---

## 1. Executive Summary

This document establishes the unified preprocessing strategy for all four insurance datasets. It consolidates the individual preprocessing plans into a single reference architecture, documents the cross-dataset decisions and rationale, and defines the Scikit-learn pipeline skeleton that will be implemented in Phase 3.

Two ML problem types are addressed:

| Problem Type | Datasets | Target | Model Family |
| :--- | :--- | :--- | :--- |
| **Regression** | Car Quotation, Bike Quotation | `annual_premium` (continuous) | LightGBM / XGBoost Regressor |
| **Classification** | Car Claims, Bike Claims | `claim_approved` (binary 0/1) | LightGBM / XGBoost Classifier |

---

## 2. Critical Cross-Dataset Rules

These rules apply uniformly across all four datasets and must never be violated during implementation:

### Rule 1 — Drop All Target Leakage Columns FIRST
Before any other transformation, drop the following columns as the very first operation:

**Quotation Datasets**:
```python
LEAKAGE_COLS_QUOTATION = [
    'od_premium_before_ncb',  # r=0.99 with annual_premium
    'ncb_discount_amount',    # r=0.90 with annual_premium
    'tp_premium',             # deterministic lookup from engine_cc
    'addon_premium',          # sum of addon costs
    'gst_amount',             # fixed 18% of net premium
]
```

**Claims Datasets**:
```python
LEAKAGE_COLS_CLAIMS = [
    'approval_probability',   # r≈0.98 with claim_approved
]
```

### Rule 2 — Drop Identifiers and Redundant Columns FIRST
```python
DROP_ALWAYS = [
    'record_id',          # Hash-collision identifier — not a reliable PK
    'manufacturing_year', # Redundant with vehicle_age_years
    'colour',             # Aesthetic metadata — zero actuarial relevance
]
```

### Rule 3 — Target Encoding Must Be Fit on Training Set Only
Target encoding of `city` and `vehicle_model` must use only the training split to prevent data leakage into validation and test sets. Use `sklearn.model_selection.cross_val_predict` with `category_encoders.TargetEncoder` wrapped in a Pipeline.

### Rule 4 — Log-Transform the Regression Target
```python
import numpy as np
y_train_log = np.log1p(y_train)        # Training
y_pred_original = np.expm1(y_pred_log) # Inference
```

### Rule 5 — EV Engine CC Handling
```python
df['is_electric'] = (df['engine_cc'] == 0).astype(int)
# engine_cc = 0 is a valid EV indicator, NOT a missing value
```

### Rule 6 — Class Imbalance Must Be Handled During Training Only
SMOTE or class weights must be applied AFTER the train/test split, exclusively on the training data. Never apply resampling to the test set.

---

## 3. Universal Column Decision Matrix

### 3.1 Quotation Datasets (Car + Bike)

| Category | Columns | Action |
| :--- | :--- | :--- |
| **Target** | `annual_premium` | Keep (log-transform during training) |
| **Core Risk Features** | `idv`, `engine_cc`, `vehicle_age_years`, `ncb_percent`, `customer_age`, `city_risk_score`, `claim_history_count`, `num_addons` | Keep + Scale |
| **Categorical — Low Cardinality** | `policy_type`, `fuel_type`, `segment`, `vehicle_make`, `state`, `usage_type` (bike only) | Keep + One-Hot Encode |
| **Categorical — High Cardinality** | `city`, `vehicle_model`, `variant` | Keep + Target Encode |
| **Multi-Label String** | `addons_list` | Binarize → `addon_*` columns → drop raw |
| **Target Leakage** | `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, `gst_amount` | **DROP FIRST** |
| **Identifiers/Redundant** | `record_id`, `manufacturing_year`, `colour` | **DROP FIRST** |
| **Conditionally Missing** | `previous_insurer` (car only) | Impute → `"New/Unknown"` |
| **Structurally Missing** | `addons_list` (when `num_addons=0`) | Impute → `"No Addons"` |

### 3.2 Claims Datasets (Car + Bike)

| Category | Columns | Action |
| :--- | :--- | :--- |
| **Target** | `claim_approved` | Keep (binary 0/1) |
| **Core Risk Features** | `claim_amount`, `idv`, `damage_severity_score`, `policy_age_months`, `previous_claims_count`, `num_parts_affected`, `vehicle_age_years`, `engine_cc` | Keep + Scale |
| **Coverage Validators** | `zero_dep_addon`, `engine_protection_addon` (car only) | Keep as int8 |
| **Bike-Specific Signals** | `helmet_worn`, `rider_experience_years`, `usage_type` | Keep (bike only) |
| **Categorical — Low Cardinality** | `policy_type`, `incident_type`, `damage_type`, `segment`, `vehicle_make`, `state`, `incident_day_of_week`, `incident_time_of_day` | Keep + One-Hot Encode |
| **Categorical — High Cardinality** | `city`, `vehicle_model` | Keep + Target Encode |
| **Date String** | `incident_date` | Parse → extract temporal features → drop raw |
| **Multi-Label String** | `affected_parts` | Binarize → `part_*` columns → drop raw |
| **Target Leakage** | `approval_probability` | **DROP FIRST** |
| **Identifiers/Redundant** | `record_id`, `manufacturing_year` | **DROP FIRST** |

---

## 4. Encoding Strategy Summary

| Encoding Method | Features | Justification |
| :--- | :--- | :--- |
| **One-Hot Encoding** (`drop='first'`) | All low-cardinality categoricals (≤ 32 unique values) | Prevents dummy variable trap. Sparse output avoided via `sparse_output=False`. |
| **Target Encoding** | `city` (117), `vehicle_model` (134), `variant` (29) | High cardinality prevents OHE. Encode based on target mean (log-premium for regression; approval rate for classification). |
| **MultiLabelBinarizer** | `addons_list`, `affected_parts` | Comma-separated lists require expansion into individual binary columns. |
| **Ordinal / Passthrough** | `city_tier` (1→3), `city_risk_score` (already in [0.82,1.50]) | Natural ordinal or pre-scaled values require no additional encoding. |
| **No Encoding** | Binary integers: `zero_dep_addon`, `helmet_worn`, `engine_protection_addon` | Already in 0/1 format. Compatible with all estimators. |

---

## 5. Scaling Strategy Summary

| Scaler | Applied To | Justification |
| :--- | :--- | :--- |
| **RobustScaler** | `idv`, `claim_amount` | Extreme outliers from luxury vehicles. IQR-based scaling is outlier-resistant. |
| **StandardScaler** | `customer_age`, `engine_cc`, `annual_premium_paid`, `previous_claims_count`, `claim_history_count` | Near-normal or uniform distributions. Centering and unit variance appropriate. |
| **MinMaxScaler** | `vehicle_age_years`, `ncb_percent`, `policy_age_months`, `damage_severity_score`, `num_parts_affected`, `rider_experience_years`, `num_addons` | Fixed or design-bounded ranges map cleanly to [0, 1]. |
| **Passthrough** | `city_risk_score`, `city_tier`, all binary/engineered flags | Already scaled or categorical. No transformation needed. |
| **Log1p (pre-scaling)** | `idv`, `claim_amount` before RobustScaler | Compresses extreme skewness before scaling. |
| **Log1p (target only)** | `annual_premium` (regression target) | Normalizes regression target distribution. Exponentiate predictions with `expm1` at inference. |

---

## 6. Feature Engineering Master Catalogue

The following table consolidates all engineered features across all datasets:

| Feature | Datasets | Formula | Business Impact |
| :--- | :--- | :--- | :--- |
| `is_electric` | All 4 | `(engine_cc == 0).astype(int)` | EV powertrain flag for specialized pricing and repair costs. |
| `addon_density` | Quotations | `num_addons / max_addons` | Risk aversion proxy. Higher = more coverage = higher premium. |
| `relative_depreciation` | Quotations | `idv / median_idv_per_model_group` | Normalized asset value loss metric. |
| `usage_risk_score` | Bike Quotation | `city_risk_score × usage_multiplier` | Combined location + usage exposure signal. |
| `driver_experience_index` | Car Quotation | `customer_age - 18 - claim_history_count` | Risk-adjusted driving experience proxy. |
| `ev_high_risk_flag` | Car Quotation | `(segment=='ev') & (city_tier==3)` | EV in low-infrastructure city. Higher repair risk. |
| `is_delivery_ev` | Bike Quotation | `(usage_type=='Delivery') & (fuel_type=='Electric')` | Highest-risk bike usage profile. |
| `experienced_customer_index` | Bike Quotation | `customer_age - 18 - (claim_history_count × 3)` | Risk-adjusted rider experience. |
| `claim_to_idv_ratio` | Claims | `claim_amount / idv` | **Primary fraud signal.** Ratio > 1.0 = potential fraud. |
| `early_claim_flag` | Claims | `(policy_age_months <= 2).astype(int)` | Pre-existing damage / staging fraud indicator. |
| `monsoon_flood_match` | Claims | `(incident_type=='Flooding') & (month in [6,7,8,9])` | Seasonality consistency validator. |
| `severity_claim_ratio` | Claims | `claim_amount / (severity_score × threshold)` | Inflation check. Disproportionate amounts = fraud. |
| `incident_is_weekend` | Claims | `(day_of_week in ["Saturday","Sunday"]).astype(int)` | Weekend accident clustering signal. |
| `repeat_claimant_flag` | Car Claims | `(previous_claims_count >= 3).astype(int)` | High-frequency claimant risk profile. |
| `addon_coverage_match` | Car Claims | `(damage_type=='engine') & (engine_protection_addon==1)` | Coverage existence validator. |
| `non_helmet_injury_flag` | Bike Claims | `(helmet_worn==0) & (incident_type=='Accident')` | Compliance exclusion trigger for injury payouts. |
| `novice_rider_flag` | Bike Claims | `(rider_experience_years <= 2).astype(int)` | Low-experience rider risk flag. |
| `delivery_high_risk_flag` | Bike Claims | `(usage_type=='Delivery') & (city_risk_score > 1.1)` | Delivery in high-risk city combined signal. |
| `experienced_safe_rider` | Bike Claims | `(exp_years>=5) & (helmet==1) & (prev_claims==0)` | Fast-track auto-approval routing signal. |

---

## 7. Class Imbalance Strategy (Claims Models)

| Dataset | Approved (1) | Rejected (0) | Ratio | Strategy |
| :--- | :--- | :--- | :--- | :--- |
| Car Claims | 128,403 (85.6%) | 21,597 (14.4%) | 1 : 5.9 | `scale_pos_weight=5.95` (XGBoost) or SMOTE |
| Bike Claims | 88,568 (88.6%) | 11,432 (11.4%) | 1 : 7.75 | `scale_pos_weight=7.75` (XGBoost) or SMOTE |

**Implementation Rule**: Apply resampling or weighting AFTER train/test split, on the training set only.

**Evaluation Metrics Priority**:
1. Recall for class 0 (rejection recall) — most important for catching fraud
2. F1-Score (macro weighted)
3. ROC-AUC
4. Precision-Recall AUC (more informative than ROC for imbalanced data)

---

## 8. Master Pipeline Architecture

```text
╔═════════════════════════════════════════════════════════════╗
║            ACKO PLATFORM — MASTER PREPROCESSING PIPELINE   ║
╚═══════════════════════════════════╤═════════════════════════╝
                                    │
          ┌─────────────────────────┴────────────────────────┐
          │                                                   │
          ▼                                                   ▼
┌─────────────────────┐                          ┌──────────────────────┐
│   QUOTATION BRANCH  │                          │    CLAIMS BRANCH     │
│ (Regression Target) │                          │ (Classification Tgt) │
└──────────┬──────────┘                          └──────────┬───────────┘
           │                                                │
           ▼                                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1 — DROP: Leakage Cols + Identifiers + Redundant Cols          │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 2 — IMPUTE MISSING VALUES                                      │
│  previous_insurer → "New/Unknown"   addons_list → "No Addons"        │
│  (Claims: No missing values — skip this step)                        │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 3 — DATE PARSING (Claims Only)                                 │
│  incident_date → extract temporal features → drop raw date           │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 4 — MULTI-LABEL BINARIZATION                                   │
│  addons_list → addon_* binary columns  (Quotations)                  │
│  affected_parts → part_* binary columns  (Claims)                    │
│  Drop raw string columns after expansion                             │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 5 — FEATURE ENGINEERING                                        │
│  Create all engineered features from Section 6 above                 │
│  (is_electric, addon_density, claim_to_idv_ratio, etc.)              │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 6 — TRAIN / TEST SPLIT (80/20 stratified)                      │
│  Fit all encoders and scalers on TRAINING SET ONLY                   │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 7 — COLUMN TRANSFORMER (fit on train, transform train+test)    │
│                                                                      │
│  TargetEncoder  ── city, vehicle_model, variant                      │
│  OneHotEncoder  ── state, segment, fuel_type, policy_type,           │
│                    vehicle_make, incident_type, damage_type, etc.    │
│  RobustScaler   ── idv, claim_amount (after Log1p)                   │
│  StandardScaler ── customer_age, engine_cc, annual_premium_paid, etc.│
│  MinMaxScaler   ── vehicle_age_years, ncb_percent, severity_score etc│
│  Passthrough    ── city_risk_score, city_tier, all binary flags       │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 8 — TARGET TRANSFORMATION                                      │
│  Regression: y_train = log1p(annual_premium)                         │
│  Classification: y_train = claim_approved (binary, no transform)     │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 9 — CLASS IMBALANCE (Claims Only — Training Set Only)          │
│  SMOTE or scale_pos_weight configuration                             │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 10 — FINAL FEATURE ARRAY (ML Ready)                            │
│  Car Quotation:  ~85 columns                                         │
│  Bike Quotation: ~80 columns                                         │
│  Car Claims:     ~100 columns                                        │
│  Bike Claims:    ~110 columns                                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 9. Scikit-learn Pipeline Skeleton Reference

> This is a design reference only. Implementation begins in Phase 3.

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    OneHotEncoder, FunctionTransformer
)
from category_encoders import TargetEncoder
import numpy as np

# ── Feature group definitions (quotation example) ─────────────────
robust_features   = ['idv']
standard_features = ['customer_age', 'engine_cc', 'claim_history_count']
minmax_features   = ['vehicle_age_years', 'ncb_percent', 'num_addons']
ohe_features      = ['state', 'segment', 'fuel_type', 'policy_type', 'vehicle_make']
target_features   = ['city', 'vehicle_model', 'variant']
passthru_features = ['city_risk_score', 'city_tier', 'is_electric', 'addon_density']

# ── ColumnTransformer ──────────────────────────────────────────────
preprocessor = ColumnTransformer(
    transformers=[
        ('robust',   Pipeline([
            ('log',   FunctionTransformer(np.log1p)),
            ('scale', RobustScaler())
        ]),          robust_features),
        ('standard', StandardScaler(),   standard_features),
        ('minmax',   MinMaxScaler(),     minmax_features),
        ('ohe',      OneHotEncoder(drop='first', sparse_output=False,
                                   handle_unknown='ignore'), ohe_features),
        ('target',   TargetEncoder(),   target_features),
        ('passthru', 'passthrough',     passthru_features),
    ],
    remainder='drop'
)

# ── Full Pipeline ──────────────────────────────────────────────────
full_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    # ('model', LGBMRegressor())  # Added in Phase 3
])
```

---

## 10. Data Quality Decisions Register

This register documents all data quality decisions made during the design phase:

| Decision ID | Dataset | Column | Issue | Decision | Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| DQ-001 | All | `record_id` | 5–6 hash-collision duplicates | Drop column entirely | Cannot serve as PK. Use PostgreSQL surrogate key in production. |
| DQ-002 | Quotation | `od_premium_before_ncb` et al. | r≥0.99 with target | Drop before training | Target leakage. Model must learn risk factors, not billing arithmetic. |
| DQ-003 | Claims | `approval_probability` | r≈0.98 with target | Drop before training | Target leakage. Score derived from same logic as the target. |
| DQ-004 | All | `engine_cc = 0` | EV powertrain indicator | Retain + add `is_electric` flag | Valid EV representation. Zero is not missing data. |
| DQ-005 | Quotation | `addons_list` (40% null) | Structural null — no addons | Fill `"No Addons"` + binarize | Absence of addons is valid business state. |
| DQ-006 | Car Quotation | `previous_insurer` (11% null) | New customers / unknown carrier | Fill `"New/Unknown"` category | Null = first-time buyer profile. Preserves business segment. |
| DQ-007 | Quotation | Extreme IDV outliers | Luxury vehicle segment | Retain + RobustScaler | Luxury segment is a valid and profitable underwriting category. |
| DQ-008 | Claims | Extreme claim amounts | Total-loss events on luxury assets | Retain + Log1p + RobustScaler | Legitimate catastrophic claims. Removing creates blind spots. |
| DQ-009 | Claims | 85–88% approval rate | Class imbalance | SMOTE or scale_pos_weight | Must prevent model from defaulting to majority-class prediction. |
| DQ-010 | All | `manufacturing_year` | Redundant with `vehicle_age_years` | Drop | Eliminates multicollinearity without losing information. |
| DQ-011 | All | `colour` | Aesthetic metadata | Drop | Zero correlation with premiums or claim approvals. |
| DQ-012 | Claims | `incident_date` (string) | Not directly usable as ML feature | Parse → extract features → drop raw | Temporal features carry signal; raw date string does not. |

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Target encoding fitted on full dataset | **High** — inflated model performance in CV | Wrap TargetEncoder in cross_val_predict or pipeline to fit only on train fold. |
| SMOTE applied before split | **High** — data leakage into test set | Apply SMOTE after train/test split, on training data only. |
| Keeping `approval_probability` accidentally | **Critical** — model learns trivial mapping | Automated assertion: confirm column absent before fit(). |
| High cardinality `vehicle_model` OHE | **Medium** — sparse matrix + overfit | Use TargetEncoder, not OHE, for vehicle_model. |
| Log1p on zero-valued `idv` | **Low** — log1p(0) = 0, not undefined | log1p handles zero safely. No risk. |
| Different addon sets across datasets | **Medium** — pipeline mismatch at inference | Standardize addon vocabulary across car and bike; use `handle_unknown='ignore'` in binarizer. |

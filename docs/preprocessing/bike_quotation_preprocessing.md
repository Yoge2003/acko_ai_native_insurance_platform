# Preprocessing Pipeline Design - Bike Quotation
**Module Reference**: Module 2 (Insurance Premium Prediction)
**Status**: Preprocessing Architecture Approved
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: DATA CLEANING STRATEGY

Column-by-column cleaning decisions for all 28 columns:

| Column | Action | Justification |
| :--- | :--- | :--- |
| `record_id` | **Drop** | Non-predictive transaction ID; hash collisions found (1 duplicate). |
| `customer_age` | **Keep** | Demographic risk factor. Rider age influences accident probability. |
| `city` | **Keep** | High-cardinality geographical risk feature. |
| `state` | **Keep** | Regional regulation and theft rate proxy. |
| `city_tier` | **Keep** | Urban density risk proxy; ordinal (1=Metro, 3=Rural). |
| `city_risk_score` | **Keep** | Continuous actuarial location hazard multiplier. |
| `vehicle_make` | **Keep** | Determines OD repair cost baseline for spare parts. |
| `vehicle_model` | **Keep** | High-cardinality vehicle-level pricing feature. |
| `variant` | **Keep** | Trim level refines safety ratings and parts cost estimates. |
| `segment` | **Keep** | Bike category (scooter, sport, naked, ev_scooter, commuter, etc.). |
| `fuel_type` | **Keep** | Petrol vs. Electric — fundamental pricing bifurcation. |
| `colour` | **Drop** | Aesthetic metadata; zero actuarial pricing relevance for bikes. |
| `manufacturing_year` | **Drop** | Redundant with `vehicle_age_years`. |
| `vehicle_age_years` | **Keep** | Direct depreciation factor for IDV. |
| `engine_cc` | **Keep** | Statutory TP premium lookup. 0 CC = valid EV indicator. |
| `idv` | **Keep** | Dominant OD premium driver. Sum insured for the policy. |
| `ncb_percent` | **Keep** | No Claim Bonus discount modifier (0%–50%). |
| `claim_history_count` | **Keep** | Policyholder risk score from past claims. |
| `policy_type` | **Keep** | Comprehensive / Third Party / Own Damage — defines coverage scope. |
| `usage_type` | **Keep** | Personal / Commercial / Delivery — critical bike-specific risk factor. |
| `num_addons` | **Keep** | Coverage breadth indicator. |
| `addons_list` | **Keep → Expand → Drop** | Must be multi-label binarized then dropped in raw form. |
| `od_premium_before_ncb` | **Drop** | Actuarial data leakage. Directly calculates `annual_premium`. |
| `ncb_discount_amount` | **Drop** | Actuarial data leakage. Deterministic from `od_premium_before_ncb × ncb_percent`. |
| `tp_premium` | **Drop** | Actuarial data leakage. Fixed regulatory lookup from `engine_cc`. |
| `addon_premium` | **Drop** | Actuarial data leakage. Directly calculated from `addons_list`. |
| `gst_amount` | **Drop** | Actuarial data leakage. Fixed 18% of net premium. |
| `annual_premium` | **Keep** | Target variable `y`. |

---

## PART 2: MISSING VALUE STRATEGY

| Feature | Missing % | Strategy | Justification |
| :--- | :--- | :--- | :--- |
| `addons_list` | 40.1% | Constant → `"No Addons"` | Structurally correct. Corresponds to `num_addons = 0`. Not a data error. |
| All other features | 0.0% | No action required | All core underwriting inputs are fully populated. |

**Note on `previous_insurer`**: The bike quotation dataset does **not** include a `previous_insurer` column (unlike the car quotation). This is a structural difference between the two portfolios; bike renewals rely on `ncb_percent` to infer prior carrier status.

---

## PART 3: OUTLIER STRATEGY

| Feature | Outlier Presence | Strategy | Justification |
| :--- | :--- | :--- | :--- |
| `idv` | Yes — max 38,01,389 INR (superbikes: Kawasaki Ninja H2R, KTM RC 8C) | **Retain + RobustScaler** | Legitimate high-value enthusiast segment. Removing would prevent model from pricing superbikes correctly. |
| `annual_premium` | Yes — max 2,52,983 INR | **Log-transform target** | Extreme values align with high-IDV superbike premiums. Log-transform normalizes the regression target. |
| `engine_cc` | Yes — max 1,833 CC (superbike engines); 0 CC (EVs) | **Retain + StandardScaler + is_electric flag** | Both extremes are valid. 1,833 CC represents Kawasaki H2 SX; 0 CC represents EV scooters. |
| `od_premium_before_ncb` | Yes — max 2,60,756 INR | **Drop** (data leakage) | Will not be used in training. |

---

## PART 4: ENCODING STRATEGY

| Feature | Cardinality | Encoding | Justification |
| :--- | :--- | :--- | :--- |
| `state` | 32 | One-Hot Encoding | Manageable cardinality; preserves regional distinctions without ordinal assumptions. |
| `segment` | 16 | One-Hot Encoding | Bike segments are distinct, unordered categories with distinct risk profiles. |
| `fuel_type` | 2 | One-Hot Encoding (or binary 0/1) | Only Petrol and Electric. Simple binary distinction. |
| `usage_type` | 3 | One-Hot Encoding | Personal / Commercial / Delivery — unordered, mutually exclusive categories. |
| `policy_type` | 3 | One-Hot Encoding | Comprehensive / Third Party / Own Damage — unordered, mutually exclusive. |
| `vehicle_make` | 13 | One-Hot Encoding | Low cardinality for bikes (13 brands). Manageable expansion. |
| `city` | 117 | **Target Encoding** | High cardinality would produce 117 sparse columns. Encode based on mean log-premium per city. |
| `vehicle_model` | 138 | **Target Encoding** | High cardinality. Model-level premium mean is the appropriate encoding target. |
| `variant` | 16 | **Target Encoding** | Variant trim level has moderate cardinality; target encode based on premium. |
| `addons_list` | Multi-label string | **MultiLabelBinarizer** | Expand comma-separated addon strings into binary indicator columns, then drop raw column. |

**Addon Binary Columns to Generate** (from `addons_list`):
- `addon_roadside_assistance`
- `addon_consumables_cover`
- `addon_return_to_invoice`
- `addon_engine_protection`
- `addon_zero_depreciation`

---

## PART 5: NUMERICAL FEATURE STRATEGY

| Feature | Scaler | Transformation | Justification |
| :--- | :--- | :--- | :--- |
| `idv` | RobustScaler | Log1p pre-scale | Highly right-skewed. RobustScaler uses IQR; resistant to extreme superbike IDVs. |
| `annual_premium` (target) | None during inference | Log1p | Target needs log-transform; exponentiate predictions with `expm1` for display. |
| `customer_age` | StandardScaler | None | Near-uniform distribution (18–65). Centering appropriate. |
| `engine_cc` | StandardScaler | None | Wide range (0–1,833). Add binary `is_electric` flag for EV zero-value. |
| `vehicle_age_years` | MinMaxScaler | None | Fixed bounds [1, 20]. MinMaxScaler maps to [0, 1] cleanly. |
| `ncb_percent` | MinMaxScaler | None | Fixed bounds [0, 50]. Ordinal discount ladder. |
| `claim_history_count` | StandardScaler | None | Low-variance count variable [0, 3]. |
| `num_addons` | MinMaxScaler | None | Fixed bounds [0, 3] for bikes. |
| `city_risk_score` | None (already scaled) | None | Values already in [0.82, 1.50]. Preserve as-is to maintain interpretability. |
| `city_tier` | Ordinal → Integer | None | Treat as ordinal integer: 1 (Metro) → 3 (Rural). No additional scaling required. |

---

## PART 6: DATE FEATURE STRATEGY

There are no date columns in the bike quotation dataset. The vehicle age is represented directly by `vehicle_age_years` (integer). No date parsing is required for this dataset.

---

## PART 7: BOOLEAN FEATURE STRATEGY

Addon binary columns generated by `MultiLabelBinarizer` will be stored as `int8` (0 or 1). This is natively interpreted by all Scikit-learn estimators and gradient boosting frameworks (LightGBM, XGBoost) without additional scaling.

---

## PART 8: FEATURE ENGINEERING PLAN

| Feature Name | Formula / Logic | Business Value | ML Value |
| :--- | :--- | :--- | :--- |
| `is_electric` | `1 if fuel_type == 'Electric' else 0` | Flags EV-specific pricing hazards (battery repair costs). | Helps tree models split EV vs. ICE bikes explicitly. |
| `addon_density` | `num_addons / 3` | Higher addon density = higher risk aversion = higher premium. | Continuous proxy for customer's coverage preference. |
| `relative_depreciation` | `idv / median_idv_per_model` | Measures how much vehicle has depreciated relative to peers. | Improves OD premium accuracy for heavily depreciated assets. |
| `usage_risk_score` | `city_risk_score × usage_weight` where Personal=1.0, Commercial=1.3, Delivery=1.6 | Combines location hazard with daily exposure multiplier. | Single interaction feature capturing worst-case risk profile. |
| `experienced_customer_index` | `customer_age - 18 - (claim_history_count × 3)` | Penalizes frequent claimants regardless of age. | Risk-adjusted experience proxy for the premium regressor. |
| `is_delivery_ev` | `1 if usage_type == 'Delivery' AND fuel_type == 'Electric' else 0` | Delivery EVs face unique risks: battery wear, limited repair infra, high mileage. | High-value interaction for the model to learn a distinct pricing cluster. |

---

## PART 9: FEATURE SELECTION PLAN

### Definitely Keep — Core Pricing Signals
| Feature | Reason |
| :--- | :--- |
| `idv` | Primary OD premium multiplier. Highest correlation with target. |
| `engine_cc` | Determines statutory TP premium tier. |
| `vehicle_age_years` | Depreciation factor. Directly reduces IDV and OD premium. |
| `ncb_percent` | No Claim Bonus discount. Direct target modifier. |
| `city_risk_score` | Location-based hazard multiplier. |
| `claim_history_count` | Customer risk history. Influences loading factors. |
| `policy_type` | Sets coverage boundaries (encoded). |
| `usage_type` | Critical bike-specific risk differentiator. |
| `fuel_type` | EV vs. ICE pricing bifurcation. |
| `segment` | Risk profile by bike class. |
| `num_addons` | Addon premium contribution. |
| `vehicle_make` | Parts cost and theft risk profile. |
| Engineered: `is_electric`, `usage_risk_score`, `addon_density` | See Part 8. |

### Possibly Keep — High-Cardinality with Careful Encoding
| Feature | Reason |
| :--- | :--- |
| `city` | Geographic granularity. Requires target encoding. |
| `state` | Regional regulatory and risk clustering. |
| `vehicle_model` | Model-level pricing data. Requires target encoding. |
| `variant` | Trim-level refinement. |
| Binarized addons: `addon_*` | Specific coverage selection. Include based on feature importance. |

### Remove — Leakage, Redundant, or Identifier
| Feature | Reason |
| :--- | :--- |
| `record_id` | Identifier. No predictive value. |
| `colour` | Aesthetic metadata. Zero pricing relevance. |
| `manufacturing_year` | Redundant with `vehicle_age_years`. |
| `od_premium_before_ncb` | **Target leakage**. Directly calculates the target. |
| `ncb_discount_amount` | **Target leakage**. Derived from `od_premium_before_ncb`. |
| `tp_premium` | **Target leakage**. Fixed regulatory lookup from `engine_cc`. |
| `addon_premium` | **Target leakage**. Sum of addon costs. |
| `gst_amount` | **Target leakage**. 18% of net premium. |
| `addons_list` (raw) | Replaced by binarized `addon_*` columns. |

---

## PART 10: PREPROCESSING PIPELINE DESIGN

```text
┌─────────────────────────────────────────────────────────────┐
│         Raw Bike Quotation Record (CSV / DataFrame)         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1 — STRUCTURAL DROPS                                  │
│  Drop: record_id, colour, manufacturing_year                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2 — DATA LEAKAGE PRUNING                              │
│  Drop: od_premium_before_ncb, ncb_discount_amount,          │
│         tp_premium, addon_premium, gst_amount               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3 — MISSING VALUE IMPUTATION                          │
│  addons_list ──► fill("No Addons")                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4 — ADDON MULTI-LABEL BINARIZATION                    │
│  addons_list ──► MultiLabelBinarizer ──► addon_* columns    │
│  Drop raw addons_list column                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5 — FEATURE ENGINEERING                               │
│  Create: is_electric, addon_density, usage_risk_score,      │
│          relative_depreciation, is_delivery_ev,             │
│          experienced_customer_index                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6 — ENCODING                                          │
│  High-cardinality (city, vehicle_model, variant)            │
│    ──► TargetEncoder (mean of log annual_premium)           │
│  Low-cardinality (state, segment, fuel_type,                │
│    usage_type, policy_type, vehicle_make)                   │
│    ──► OneHotEncoder (drop='first' to avoid multicollinearity)│
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7 — SCALING                                           │
│  idv                  ──► RobustScaler                      │
│  customer_age,                                              │
│    engine_cc,                                               │
│    claim_history_count ──► StandardScaler                   │
│  vehicle_age_years,                                         │
│    ncb_percent,                                             │
│    num_addons         ──► MinMaxScaler                      │
│  city_risk_score      ──► Pass-through (already in [0.82,1.5])│
│  Target annual_premium ──► log1p() (training only)          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         Processed Feature Array (ML Ready)                  │
│  Approx. ~80 columns after encoding + binarization          │
└─────────────────────────────────────────────────────────────┘
```

**Scikit-learn Implementation Pattern**:
```python
# Conceptual skeleton (not for implementation yet)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.preprocessing import OneHotEncoder
from category_encoders import TargetEncoder
from sklearn.preprocessing import MultiLabelBinarizer

bike_quotation_pipeline = ColumnTransformer(transformers=[
    ('robust',   RobustScaler(),    ['idv']),
    ('standard', StandardScaler(),  ['customer_age', 'engine_cc', 'claim_history_count']),
    ('minmax',   MinMaxScaler(),    ['vehicle_age_years', 'ncb_percent', 'num_addons']),
    ('passthru', 'passthrough',     ['city_risk_score', 'city_tier', 'is_electric',
                                     'addon_density', 'usage_risk_score',
                                     'relative_depreciation', 'is_delivery_ev']),
    ('ohe',      OneHotEncoder(drop='first', sparse_output=False),
                                    ['state', 'segment', 'fuel_type',
                                     'usage_type', 'policy_type', 'vehicle_make']),
    ('target',   TargetEncoder(),   ['city', 'vehicle_model', 'variant']),
])
```

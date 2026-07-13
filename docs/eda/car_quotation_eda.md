# Business-Driven Exploratory Data Analysis (EDA) - Car Quotation
**Module Reference**: Module 2 (Insurance Premium Prediction)  
**Status**: Visual Analytics Exported  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: GENERAL OVERVIEW

### 1. Dataset Shape & Feature Types
The dataset contains **200,000 rows** and **28 columns**. It represents a large sample of car insurance underwriting quotation transactions.
*   **Numerical Features**: 16 features (demographics, vehicle age, IDV, and monetary amounts).
*   **Categorical Features**: 12 features (geographic categories, vehicle descriptors, and addon coverage selections).

### 2. Target Variable Distribution
The target variable is `annual_premium`, which represents the total cost charged to the customer (including GST). 
*   **Skewness**: The raw target distribution is heavily right-skewed ($\text{Skewness} > 3.0$). The premium scale ranges from a minimum of **2,347 INR** (representing third-party coverages for older commuter cars) to a maximum of **1,607,449 INR** (representing multi-year comprehensive coverage for luxury electric vehicles/hybrids).
*   **Transformation**: Applying a log-transformation ($\log(y + 1)$) converts the distribution into a near-normal distribution, which is necessary for training regression models like linear/ridge regressors or neural networks.

![Annual Premium and Log-Transformed Distribution](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_quotation/01_target_distribution.png)

### 3. Basic Descriptive Statistics

| Column | Min | Max | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- |
| `customer_age` | 18 | 75 | 46.52 | 16.75 |
| `vehicle_age_years` | 1 | 20 | 10.49 | 5.76 |
| `idv` | 94,691 | 23,739,892 | 1,513,421.54 | 2,149,447.00 |
| `ncb_percent` | 0 | 50 | 29.18 | 16.68 |
| `claim_history_count` | 0 | 4 | 0.88 | 1.09 |
| `annual_premium` | 2,347 | 1,607,449 | 51,931.87 | 81,552.03 |

---

## PART 2: UNIVARIATE ANALYSIS

### 1. Continuous Numerical Features
*   **`idv` (Insured Declared Value)**:
    *   *Distribution*: Heavily right-skewed. The median IDV sits around **740,000 INR**, while the average is pulled to **1,513,421.54 INR** by high-end vehicles.
    *   *Outliers*: High outliers are present beyond 4.5M INR, representing luxury cars. These are valid data points representing premium vehicle lines (e.g. Mercedes-Benz E-Class, BMW 5 Series).
    *   *Preprocessing*: Use `RobustScaler` to normalize the data without allowing outliers to skew the scaling.
*   **`customer_age`**:
    *   *Distribution*: Relatively uniform between ages 18 and 75. No significant skewness.
    *   *Preprocessing*: Apply `StandardScaler` to zero-center the feature.
*   **`vehicle_age_years`**:
    *   *Distribution*: Uniformly distributed between 1 and 20 years. Reflects a balanced underwriting history.
    *   *Preprocessing*: Scale using `MinMaxScaler` since the boundaries (1 to 20) are fixed and stable.

![Univariate Boxplots of IDV and Customer Age](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_quotation/02_numerical_univariate.png)

### 2. Categorical Features
*   **`segment`**:
    *   *Counts*: SUV: 95,272 ($47.6\%$), Sedan: 33,910 ($17.0\%$), EV: 31,954 ($16.0\%$), Hatchback: 23,625 ($11.8\%$), MPV: 13,676 ($6.8\%$), Hybrid: 1,194 ($0.6\%$).
    *   *Business Meaning*: SUVs and Sedans dominate. EVs are a growing category ($16\%$). Hybrids represent a rare category ($0.6\%$).
    *   *Encoding*: One-Hot Encoding is appropriate because of the low cardinality.
*   **`fuel_type`**:
    *   *Counts*: Petrol: 91,604 ($45.8\%$), Diesel: 49,989 ($25.0\%$), Electric: 31,954 ($16.0\%$), CNG: 19,940 ($10.0\%$), LPG: 4,950 ($2.5\%$).
    *   *Encoding*: One-Hot Encoding.
*   **`city` & `vehicle_model`**:
    *   *Cardinality*: City has 117 categories; vehicle_model has 134 categories.
    *   *Encoding*: Target Encoding based on the log premium to prevent high feature dimensions.

![Vehicle Segment Distribution Bar Chart](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_quotation/03_categorical_univariate_segment.png)

---

## PART 3: BIVARIATE ANALYSIS

### 1. Premium vs. IDV (Insured Declared Value)
*   **Analysis**: Shows a strong linear relationship. As IDV increases, the calculated premium increases proportionally. This is because IDV represents the maximum sum insured, directly setting the risk exposure for Own Damage (OD) coverage.
*   **Actuarial Fit**: The scatter plot shows a clear regression line ($m \approx 0.035$). This indicates that for every 100,000 INR increase in IDV, the base premium increases by approximately 3,500 INR before adjustments for age, location, and discounts.

![Scatter Plot: Annual Premium vs IDV](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_quotation/04_bivariate_premium_vs_idv.png)

### 2. Premium vs. Vehicle Segment
*   **Analysis**: Luxury Segments (EVs, Hybrids, and premium SUVs) show much wider premium ranges and higher medians. Hatchbacks show tight, low premium distributions.
*   **Business Impact**: Insuring electric vehicles (EVs) requires higher premiums due to the high replacement costs of battery packs and specialized repair procedures.

![Box Plot: Premium Spread vs Segment](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_quotation/05_bivariate_premium_vs_segment.png)

### 3. Premium vs. No Claim Bonus (NCB) Percent
*   **Analysis**: Higher NCB percentages correspond to lower median premiums. This validates that the NCB discount is working correctly: customers who maintain claim-free years receive compounding discounts on their Own Damage premium.

![Box Plot: Premium Impact of NCB Percent Tiers](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_quotation/06_bivariate_premium_vs_ncb.png)

---

## PART 4: MULTIVARIATE ANALYSIS

### 1. Correlation Analysis
*   **`idv` vs. `annual_premium`**: Show a high correlation ($r = 0.93$).
*   **Data Leakage Warning**: Columns like `od_premium_before_ncb` ($r = 0.99$), `ncb_discount_amount` ($r = 0.90$), and `gst_amount` ($r = 0.99$) show near-perfect correlations with the target. These are intermediate calculated values that sum up to the target. Keeping them in the training dataset will cause data leakage. They must be dropped before training.

![Heatmap Correlation Matrix](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/car_quotation/07_correlation_matrix.png)

### 2. Feature Interaction
*   **Age and Claim History**: Combining driver age with past claims creates a risk index. Young drivers with a high claim history index receive the highest risk adjustments.

---

## PART 5: OUTLIER ANALYSIS

*   **Identified Outliers**: 4,341 quotations show extreme premiums ($> 250,000$ INR). 
*   **Treatment Decision**: **Retain**. These represent high-value luxury imports (e.g. Mercedes-Benz S-Class, BMW 7 Series) where the IDV exceeds 1.5 Crore INR. Dropping these rows would prevent the model from learning to underwrite high-value policies, reducing ACKO's revenue potential in the luxury segment.
*   **Mitigation**: Apply a log transformation to the target premium variable to minimize the impact of high-end values on the loss function.

---

## PART 6: BUSINESS QUESTIONS ANSWERED

1.  **Which fuel type produces the highest premium?**
    *   *Answer*: Electric and Hybrid vehicles, due to high initial asset purchase price (high IDV) and specialized battery repair hazards.
2.  **What customer profiles produce the highest premiums?**
    *   *Answer*: Customers under age 25 registration high-value SUVs in high-risk Tier 1 cities with a history of multiple claims.
3.  **Which variables are the strongest predictors?**
    *   *Answer*: `idv` is the strongest predictor for the Own Damage component, followed by `engine_cc` (for Third Party component lookups), and `city_risk_score` for location adjustments.

---

## PART 7: FEATURE RELATIONSHIPS

*   **Target Leakage Columns**: `od_premium_before_ncb`, `ncb_discount_amount`, `tp_premium`, `addon_premium`, and `gst_amount` must be dropped.
*   **Redundant Columns**: `manufacturing_year` is redundant once `vehicle_age_years` is calculated.
*   **Strong Predictors**: `idv`, `engine_cc`, `city_risk_score`, and `ncb_percent`.

---

## PART 8: PREPROCESSING & CLEANING RECOMMENDATIONS

1.  **Drop Target Leakage**: Remove intermediate calculation columns from the ML feature set.
2.  **Impute Competitor Data**: Impute missing `previous_insurer` values with an `"Unknown/New"` category.
3.  **Target Encoding**: Encode `city` and `vehicle_model` categories based on premium distributions to prevent dimension expansion.
4.  **Target Scaling**: Apply a `numpy.log1p` transformation to the target variable `annual_premium`.

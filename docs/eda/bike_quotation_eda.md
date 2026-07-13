# Business-Driven Exploratory Data Analysis (EDA) - Bike Quotation
**Module Reference**: Module 2 (Insurance Premium Prediction)  
**Status**: Visual Analytics Exported  
**Target Runtime**: Python 3.11 / Scikit-learn Pipelines

---

## PART 1: GENERAL OVERVIEW

### 1. Dataset Shape & Feature Types
The dataset contains **150,000 rows** and **28 columns**, representing bike insurance underwriting quotation transactions.
*   **Numerical Features**: 16 features (demographics, vehicle age, IDV, and monetary amounts).
*   **Categorical Features**: 12 features (geographic categories, vehicle descriptors, usage types, and addon selections).

### 2. Target Variable Distribution
The target variable is `annual_premium`.
*   **Skewness**: The raw target distribution is heavily right-skewed. The premium scale ranges from a minimum of **538 INR** (third-party liability only for low-engine commuter scooters) to a maximum of **252,983 INR** (comprehensive coverage for high-end electric superbikes).
*   **Transformation**: Applying a log-transformation ($\log(y + 1)$) converts the distribution into a near-normal shape suitable for regression models.

![Annual Premium and Log-Transformed Distribution](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_quotation/01_target_distribution.png)

### 3. Basic Descriptive Statistics

| Column | Min | Max | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- |
| `customer_age` | 18 | 65 | 41.50 | 13.85 |
| `vehicle_age_years` | 1 | 20 | 10.50 | 5.78 |
| `idv` | 15,000 | 3,801,389 | 109,286.51 | 183,277.15 |
| `ncb_percent` | 0 | 50 | 29.16 | 16.67 |
| `claim_history_count` | 0 | 3 | 0.67 | 0.87 |
| `annual_premium` | 538 | 252,983 | 5,646.40 | 8,736.96 |

---

## PART 2: UNIVARIATE ANALYSIS

### 1. Categorical Univariate
*   **`fuel_type`**:
    *   *Petrol*: 101,890 ($67.9\%$), *Electric*: 48,110 ($32.1\%$).
    *   *Business Meaning*: High penetration of electric scooters ($32.1\%$). This represents a key business segment for ACKO in the urban two-wheeler market.
*   **`usage_type`**:
    *   *Personal*: 120,039 ($80.0\%$), *Commercial*: 18,069 ($12.0\%$), *Delivery*: 11,892 ($8.0\%$).
    *   *Business Meaning*: Commercial and delivery usage accounts for $20\%$ of all quotations. Delivery riders have higher daily exposure (high mileage), which must be priced differently.
    *   *Encoding*: One-Hot Encoding is appropriate because of the low cardinality.

![Categorical Split of Fuel Type and Usage Type](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_quotation/02_categorical_univariate.png)

---

## PART 3: BIVARIATE ANALYSIS

### 1. Premium vs. Usage Type
*   **Analysis**: Commercial and delivery use cases show higher median premiums and wider spreads compared to personal use.
*   **Business Impact**: Commercial use increases wear-and-tear and hazard risks. Underwriting engines must apply risk multipliers to delivery and commercial riders to maintain profitability.

![Box Plot: Premium Spread by Rider Usage Type](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_quotation/03_bivariate_premium_vs_usage.png)

### 2. Premium vs. IDV (Insured Declared Value)
*   **Analysis**: Strong linear correlation ($r = 0.94$). Higher vehicle value directly increases the Own Damage premium component.
*   **Actuarial Fit**: The scatter plot shows a linear trend with a slope of $m \approx 0.045$, representing a baseline Own Damage premium rate of approximately $4.5\%$ of the IDV before discounts and location-based adjustments are applied.

![Scatter Plot: Bike Premium vs IDV](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_quotation/04_bivariate_premium_vs_idv.png)

---

## PART 4: MULTIVARIATE & CORRELATION ANALYSIS

*   **`idv` vs. `annual_premium`**: Highly correlated ($r = 0.94$).
*   **Data Leakage Warning**: As in the car dataset, intermediate billing columns (`od_premium_before_ncb` ($r = 0.99$), `ncb_discount_amount` ($r = 0.88$), and `gst_amount` ($r = 0.99$)) must be dropped before training to prevent target data leakage.

![Heatmap Correlation Matrix](file:///c:/Yoge%20Studies/Guvi%20Projects/acko_ai_native_insurance_platform/reports/figures/bike_quotation/05_correlation_matrix.png)

---

## PART 5: OUTLIER ANALYSIS

*   **Identified Outliers**: 3,093 quotations show extreme premiums ($> 50,000$ INR). 
*   **Treatment Decision**: **Retain**. These represent high-performance superbikes (e.g. Kawasaki Ninja, KTM Super Duke) where the IDV exceeds 1.5 Lakh INR. Dropping these rows would prevent the model from learning to underwrite high-value enthusiast bike segments.
*   **Mitigation**: Apply a log transformation to the target premium variable to minimize the impact of high-end values on the loss function.

---

## PART 6: PREPROCESSING & CLEANING RECOMMENDATIONS

1.  **Drop Target Leakage**: Remove intermediate calculation columns from the ML feature set.
2.  **One-Hot Encoding**: One-Hot Encode `usage_type`, `fuel_type`, and `policy_type`.
3.  **Target Encoding**: Encode `city` and `vehicle_model` categories based on premium distributions to prevent dimension expansion.
4.  **Target Scaling**: Apply a `numpy.log1p` transformation to the target variable `annual_premium`.

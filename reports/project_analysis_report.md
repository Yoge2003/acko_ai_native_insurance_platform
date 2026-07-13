# ACKO AI Native Insurance Platform: Project Architecture Analysis & Roadmap

This report presents a thorough audit of the **ACKO AI Native Insurance Platform** codebase, detailing the architecture, completed modules, inconsistencies, missing elements, and recommendations for the subsequent integration phase.

---

## 1. Project Overview & Scope

The **ACKO AI Native Insurance Platform** is designed as a web-based portal showcasing ML-driven risk-prediction and claim-auditing capabilities. The platform uses:
- **Machine Learning Regressors** to estimate custom annual vehicle insurance premiums.
- **Machine Learning Classifiers** to auto-evaluate and fast-track/flag vehicle collision claim approvals.
- **Explainable AI (SHAP)** to compute and display transparency-focused local and global model explanations.
- **Streamlit Web Dashboard** to serve as the unified front-end interface.
- **Asynchronous SQLAlchemy / PostgreSQL** connection pool backend.
- **RAG & Agent-based Assistants** (AI Policy Chatbot & Manager SQL Assistant).

---

## 2. Inventory of Completed Modules & Elements

Our scan of the workspace confirms that the following architectural components are **fully completed and verified**:

### A. Core Machine Learning Operations (MLOps)
- **Data Loaders & Preprocessors (`src/ml/preprocessing/`)**: Modular, object-oriented preprocessors for Car/Bike Quotations and Car/Bike Claims that clean raw inputs, impute missing values, and handle date transformations.
- **Feature Engineering Pipelines (`src/ml/feature_engineering/`)**: Custom engineers that construct domain-specific insurance features (e.g., `num_claim_to_idv_ratio`, `num_severity_index`, `early_claim_flag`, `monsoon_flood_match`, segment-specific features).
- **Benchmarking & Model Training (`src/ml/models/`)**: Decoupled, reusable `BaseTrainer` capable of regression training with 7 candidate algorithms (Linear Regression, Decision Tree, Random Forest, Extra Trees, Gradient Boosting, XGBoost, LightGBM) and evaluation against train/validation splits to inspect overfitting. Implements selection logic that prioritizes the **Random Forest Regressor/Classifier** in production per guidelines.
- **Robust Model Validation Engine (`src/ml/validation/`)**: Conducts $k$-Fold Cross-Validation, residual error diagnostics (Q-Q plots, predicted vs. actual charts), and misclassification error audits. Generates standard markdown validation reports located in `reports/model_validation_report.md`.
- **Explainable AI Framework (`src/ml/explainability/`)**: Implements cached `TreeExplainer` instances via a wrapper singleton to speed up real-time attributions. Computes global rankings and dynamically formats human-readable local explanations showing exact feature impacts. Output report is generated in `reports/shap_explainability_report.md`.
- **Production Inference Pipeline (`src/ml/inference/`)**: Coordinates raw data formatters, schema-based column validators, preprocessor/feature stages, and cached ML model predictions. Calculates uncertainty thresholds by testing individual tree estimator variance. Implements MLOps audit trails logging latencies and request hashes to `logs/prediction_audit.csv`.

### B. Configuration & Infrastructure
- **Pydantic Settings (`src/config/settings.py`)**: Safely parses active environment variables (e.g. database credentials, API secrets) with warnings for unconfigured services (to prevent Streamlit shell crashes).
- **Logging Config (`src/config/logging_config.py`)**: Prepares a standard Rotating File Logger writing details to `logs/app.log`.
- **Database Pooling (`src/database/`)**: Includes SQLAlchemy 2.x engine initializers, thread-safe session factories, health checks, and context-dependent session yield helpers.

### C. Web Presentation Layer (Streamlit)
- **Unified Shell (`app.py`)**: Handles the navigation radio panel, session state initialization, and custom glassmorphism stylesheet overrides using vanilla CSS.
- **Visual Pages (`src/modules/*/pages.py` & `ui.py`)**: Renders layout structures, information cards, summaries, and telemetry placeholders for all 5 submodules.

---

## 3. Verification & Consistency Audit

To assess internal consistency, we successfully executed the unit test suite:
- **Result**: **52 out of 52 tests PASSED** in **14.86 seconds**.
- **Validated Areas**:
  - Preprocessor pipeline steps (imputations, column bounds, mappings)
  - Feature engineering outputs & scaler applications
  - Candidate model training evaluations & Random Forest selection
  - Residual plot setups & error diagnostics
  - TreeExplainer SHAP caching & local narrative builders
  - Prediction pipeline validations & batch predictors
  - Audit logger transactions & DB health checkers

*Status*: The core ML operations, preprocessors, and inference engines are highly stable and reliable.

---

## 4. Detected Gaps & Architectural Inconsistencies

During our code review and code-execution trace, we uncovered the following gaps in the integration and persistence tiers:

### A. Missing ML Integration (The "Unlinked Engines")
Although the inference models (`QuotationPredictor` and `ClaimsPredictor`) are completed, fully operational, and unit-tested under `src/ml/inference/`, the respective Streamlit UI action forms:
- `src/modules/quotation/forms.py` (Premium Quotation Submit Button)
- `src/modules/claims/forms.py` (Claims File Submit Button)

are mock-coded and have their submit buttons permanently disabled (`disabled=True`). The relevant services:
- `src/modules/quotation/services.py` calculates hand-coded mock arithmetic premiums instead of invoking `QuotationPredictor`.
- `src/modules/claims/services.py` returns simple dummy structures instead of calling `ClaimsPredictor`.

### B. Missing Chatbot RAG Implementation
`src/modules/chatbot/services.py` contains static code queries searching matching keywords in a hardcoded 2-element policy database list. The retrieval systems utilizing **ChromaDB** vector databases and generative AI pipelines using **Google Gemini** are completely missing.

### C. Missing Manager AI SQL reasoning Agent
`src/modules/manager_ai/services.py` is configured with a static hardcoded SQL query return string (`SELECT COUNT(*), state FROM policies GROUP BY state ORDER BY COUNT(*) DESC;`) and dummy records. The actual Text-to-SQL compiler agents using **LangGraph** are unimplemented.

### D. Missing Database Persistence & ORM Entities
- **No Models**: `src/database/base.py` is declared, but the entities folder `src/models/` contains only `__init__.py`. There are no SQLAlchemy model maps (such as a `policies` table or a `claims` table) defining data structures.
- **No Repositories**: The folder `src/repositories/` contains only `__init__.py`, meaning the repo pattern for saving active quotation requests and claims records to PostgreSQL is missing.
- **No Schemas or Services**: `src/schemas/` and `src/services/` (outside the modules) are empty shells.

### E. Missing Integration Tests
The `tests/integration/` directory contains only `__init__.py`. There are no integration test cases validating end-to-end user request flows (e.g. form inputs -> db write -> ML predict -> response render).

---

## 5. Next Implementation Phase Recommendations

To address the key gaps in a methodical and non-disruptive manner, we propose the following steps for **Phase 3.3 (Integration, Persistence & Agents)**:

### Step 1: Wire Up the ML Inference Engines
- **Goal**: Enable quotation submission and claim validation form elements in the UI.
- **Action**: 
  - Update `src/modules/quotation/forms.py` and `src/modules/claims/forms.py` to enable the submit buttons (`disabled=False`).
  - Modify `src/modules/quotation/services.py` to initialize `QuotationPredictor` and route the user inputs to calculate actual premiums and retrieve authentic SHAP explanations.
  - Modify `src/modules/claims/services.py` to initialize `ClaimsPredictor` and dynamically auto-approve or route claims.

### Step 2: Establish the Database Schema & Persistence Layers
- **Goal**: Persist calculated quotes, audit logs, and claims records.
- **Action**:
  - Create SQLAlchemy ORM models (e.g., `Customer`, `Policy`, `Claim`, `AuditLog`) in `src/models/`.
  - Implement access repositories in `src/repositories/` to handle inserts, updates, and aggregations.
  - Run database tables instantiation routines at startup.

### Step 3: Implement RAG Policy Assistant
- **Goal**: Dynamically search policy documentations.
- **Action**:
  - Implement document loading/chunking for PDF documents located in `DataSet/Policy_Documents`.
  - Configure **ChromaDB** index schemas in the workspace.
  - Initialize the **Google Gemini** generative pipeline in `src/modules/chatbot/services.py` to retrieve document chunks and produce context-specific answers.

### Step 4: Develop Text-to-SQL Manager agent
- **Goal**: Translate user business questions into SQL queries.
- **Action**:
  - Implement a LangGraph coordinator in `src/modules/manager_ai/services.py` that queries schema metadata, formulates SQL syntax via Gemini, executes the query against PostgreSQL using the database engine pool, and packages the records for Streamlit rendering.

### Step 5: Expand the Test Suite
- **Goal**: Validate UI-to-Model-to-DB integration.
- **Action**:
  - Create end-to-end integration tests under `tests/integration/` that spin up mock DB connections, run predictions, and test response parameters.

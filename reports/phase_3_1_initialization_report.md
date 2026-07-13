# Phase 3.1 Foundation & Initialization Report

This report summarizes the foundation setup for the **ACKO AI Native Insurance Platform** under Phase 3.1. 

---

## 1. Project Directory Tree

Below is the verified structural mapping of the codebase after Phase 3.1 initialization:

```text
acko_ai_native_insurance_platform/
├── .env.example
├── .gitignore
├── app.py
├── LICENSE
├── README.md
├── requirements.txt
├── DataSet/                               # Existing raw datasets (Read-only)
│   ├── Policy_Documents/
│   └── claim_Quotation_datas/
├── datasets/                              # Project standard datasets folder
│   └── __init__.py
├── docs/                                  # Project documentation hierarchy
│   ├── dataset_analysis/
│   ├── eda/
│   └── preprocessing/
├── notebooks/                              # Jupyter experimentation sandbox
│   └── __init__.py
├── reports/                               # Visual and analytical reports output
│   ├── __init__.py
│   └── phase_3_1_initialization_report.md  # [This File]
├── src/                                   # Domain logic and execution sources
│   ├── __init__.py
│   ├── assets/                            # Styling and image binaries
│   │   └── __init__.py
│   ├── config/                            # Environment settings & static specs
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── logging_config.py
│   │   └── settings.py
│   ├── database/                          # Connection pooling & sessions
│   │   └── __init__.py
│   ├── logs/                              # Active log targets
│   │   └── app.log                        # Rotating runtime logs
│   ├── middleware/                        # Interceptors, timers, and filters
│   │   └── __init__.py
│   ├── models/                            # SQLAlchemy ORM definitions
│   │   └── __init__.py
│   ├── modules/                           # Five core commercial submodules
│   │   ├── __init__.py
│   │   ├── chatbot/                       # AI Policy Chatbot (RAG)
│   │   │   └── __init__.py
│   │   ├── claims/                        # Claims Engine (LangGraph/Vision)
│   │   │   └── __init__.py
│   │   ├── dashboard/                     # Analytics Panel
│   │   │   └── __init__.py
│   │   ├── manager_ai/                    # Natural Language SQL Queries
│   │   │   └── __init__.py
│   │   └── quotation/                     # Premium Quoting (ML)
│   │       └── __init__.py
│   ├── repositories/                      # SQL access repository pattern
│   │   └── __init__.py
│   ├── schemas/                           # Pydantic formats
│   │   └── __init__.py
│   ├── services/                          # Orchestrated business APIs
│   │   └── __init__.py
│   └── utils/                             # Core system utilities
│       ├── __init__.py
│       ├── common.py
│       ├── file_utils.py
│       ├── helpers.py
│       └── validators.py
└── tests/                                 # Test suites
    ├── __init__.py
    ├── integration/
    │   └── __init__.py
    └── unit/
        ├── __init__.py
        └── test_foundation.py             # Unit tests for helpers & validators
```

---

## 2. Inventory of Created Files & Purposes

| File Path | Package Scope | Purpose |
| :--- | :--- | :--- |
| `app.py` | Root | Coordinates the Streamlit UI presentation layer, navigation sidebar, global styling sheets, and module loader previews. |
| `src/__init__.py` | `src` | Declares the root source folder as a Python package. Exposes top level `__version__`. |
| `src/config/__init__.py` | `src.config` | Exposes global application settings and constant variables. |
| `src/config/settings.py` | `src.config` | Reads settings from the environment or `.env` using Pydantic Settings. Includes log warners for missing non-essential integrations. |
| `src/config/constants.py` | `src.config` | Stores global domain specifications (Policy types, Vehicle configurations, size upload parameters). |
| `src/config/logging_config.py` | `src.config` | Configures console stream logging alongside a daily rotating file log under `src/logs/app.log`. |
| `src/utils/__init__.py` | `src.utils` | Consolidates formatting tools, validators, and file utilities for external modules. |
| `src/utils/helpers.py` | `src.utils` | Implements currency decimal formatters, percentage dividers, and execution time decorator metrics. |
| `src/utils/validators.py` | `src.utils` | Incorporates regular expression checks for standard Emails, E.164 Phones, and Indian Vehicle Registration number plates. |
| `src/utils/file_utils.py` | `src.utils` | Provides size verification, extension parsing, and page counting integrations for PDFs using PyMuPDF and PyPDF. |
| `src/utils/common.py` | `src.utils` | Encapsulates UUID generation, dictionary cleaning, and JSON-safe ISO-8601 datetime serialization blocks. |
| `tests/unit/test_foundation.py` | `tests.unit` | Executes isolated verification tests on formatting, mathematical operations, and vehicle pattern filters. |
| `* package level __init__.py files` | Multiple | Initialize and mark respective subdirectories as valid python packages. |

---

## 3. Key Architectural Decisions & Assumptions

1. **Non-crashing Development Settings loading**: Rather than forcing a hard crash if no `.env` file or API credentials are provided on first download, the `Settings` module prints detailed warning messages to system output. This preserves standard Streamlit start capabilities while alerting engineers about missing API keys.
2. **Robust Vehicle Regex**: The vehicle RTO code matches pattern variants with single or two digit identifiers (such as `DL3CA9999` and `MH12AB1234`), aligning with standard vehicle numbering formats.
3. **No Dataset Alteration**: The pre-existing folder `DataSet` containing operational insurance files was left completely unmodified. A separate folder `datasets/` was initialized to maintain structure alignment.

---

## 4. Verification Checklists

### Checklist A: Dependency Verification
- [x] Streamlit is installed globally and accessible (v1.56.0).
- [x] `pydantic-settings` and `python-dotenv` are verified and installed in the Python environment.

### Checklist B: Unit Test Suite Running
- [x] Execute unit tests command:
  ```bash
  python -c "import tests.unit.test_foundation as t; t.test_app_constants(); t.test_helpers_format_and_math(); t.test_validators_format(); t.test_common_utils(); print('All tests passed')"
  ```
  *Status*: **Pass (All foundation unit tests passed successfully!)**

### Checklist C: Streamlit Web UI Execution
- [x] Start Streamlit server:
  ```bash
  streamlit run app.py
  ```
  *Status*: **Pass (Server binds successfully at port 8501 and loads the Sidebar/Home layouts)**

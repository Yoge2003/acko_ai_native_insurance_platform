# Developer & Maintenance Guide

This document provides developer guidelines for maintaining, extending, and testing the ACKO AI Native Insurance Platform.

---

## 🎨 1. Coding Standards & Architectural Patterns

All code modifications must follow these guidelines:

### Design Guidelines
* **Service-Repository Pattern**:
  * Write SQL database queries inside repository files (`src/repositories/`).
  * Enforce business rules, validation logic, and AI queries inside service files (`src/services/`).
  * Never write SQL queries or complex business logic directly in Streamlit page files.
* **Typing & Formatting**:
  * Handwrite strict Python type hints for all parameters and return values.
  * Follow **PEP 8** style guidelines and write Google-style docstrings for all classes and functions.
* **Loggers Over Print Statements**:
  * Use local domain loggers (`from src.monitoring.log_manager import LogManager; logger = LogManager.get_logger("domain")`) instead of `print()`.

---

## 🗄️ 2. Database Migrations with Alembic

When updating database models (`src/models/`):

1. **Modify ORM models**: Add fields or tables inside SQLAlchemy model classes.
2. **Generate migration script**:
   ```bash
   alembic revision --autogenerate -m "add_columns_to_table"
   ```
3. **Inspect code**: Verify the generated script inside `alembic/versions/`.
4. **Apply changes**:
   ```bash
   alembic upgrade head
   ```

---

## 🧪 3. Writing and Running Tests

All files should have corresponding tests written under the `tests/` directory.

### Running Pytest Commands
```bash
# Execute only unit test checks
python -m pytest tests/unit/ -v

# Execute only integration test checks
python -m pytest tests/integration/ -v

# Run the complete test suite. Alternate automation runner is:
python run_tests.py
```

---

## 🛠️ 4. Debugging & Common Fixes

### 1. Database Connection Failures
* Verify PostgreSQL is active and listening on port 5432.
* Ensure the `DATABASE_URL` in `.env` matches your database credentials.

### 2. Missing Model Files
* If quotation or claim model files (`.joblib`) are absent from `src/ml/saved_models/`, run the Streamlit app.
* On first access to the Quotation or Claims page, the system will automatically process the raw datasets and train, optimize, and save the models to disk.

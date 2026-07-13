# Changelog

All notable changes to the ACKO AI Native Insurance Platform will be documented in this file.

---

## [1.0.0] - 2026-07-10

### Added
* **Phase 11: Enterprise Monitoring & Observability**:
  * Real-time hardware load sensors using `psutil` (monitoring memory, CPU load, and disk space limits).
  * Lightweight diagnostic health checks for PostgreSQL, ChromaDB, and Gemini.
  * In-memory MLOps Metrics tracking prediction counts, failure rates, and p95 latencies.
  * Drift sensors calculating Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests comparing production data to training data.
  * Outlier detection using Z-score boundaries ($Z > 3.0$) on numerical features.
  * Centralized log rotating files (`logs/`) with 5MB maximum file sizes and 5 rotating backups.
  * Admin-only **Enterprise Health & Observability Dashboard**.
* **Phase 10: Secure Authentication & RBAC**:
  * Bcrypt-based password encryption and strength complexity policies.
  * Limit wrong login attempts and enforce 15-minute account lockouts on the 5th failed attempt.
  * Dynamic Streamlit login workspace tabs featuring registered logins, password resets, and sandbox test account grids.
  * Granular route checking comparing user roles against privilege actions.
  * Automatic session inactivity logouts after 15 minutes of idle time.
* **Phase 9: Analytics Dashboard & SQL schemas**:
  * Core visual metrics detailing premiums volumes, loss ratios, and payout charts.
* **Phase 8: Manager AI Relational Agent**:
  * Natural text query semantic translation into raw PostgreSQL query scripts via LangGraph.
  * Safe validation nodes preventing database mutation edits (`DROP`, `DELETE`).
* **Phase 7: Claims Vision AI Processor**:
  * Processing accident photographs using Gemini Vision SDK.
* **Phase 6: Policy RAG Chatbot**:
  * Similarity search indexing over parsed policy PDFs stored in ChromaDB.
  * Citation response generation showing file names and page references.
* **Phase 4 & 5: Underwriting Machine Learning Models**:
  * Trained Random Forest premium prediction model.
  * Integrated SHAP local TreeExplainer rankings inside Streamlit output dashboards.
* **Phase 1, 2, & 3: Database & Engineering Foundations**:
  * Implemented database models (Users, Policies, Claims, Logs) inside PostgreSQL using SQLAlchemy 2.0.
  * Created Alembic migration environments.

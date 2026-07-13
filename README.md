# ACKO AI Native Insurance Platform

An enterprise-grade, AI-native insurance platform powered by Google Gemini, LangChain, LangGraph, Scikit-Learn, and PostgreSQL.

---

## 🛡️ Project Overview

The **ACKO AI Native Insurance Platform** is a production-ready, end-to-end AI-powered vehicle (car and bike) insurance administration system. It automates 5 core corporate workflows: policy question answering, quotation premium underwriting, claims audit pipelines, operational analytics, and management Relational DB inquiries.

---

## 🏆 Key Features

1. **AI Policy Chatbot**: Uses ChromaDB vector similarity search + Gemini to answer coverage questions with verified text citations and page number references.
2. **Premium Quotation Underwriting**: Predicts annual vehicle premiums (Scikit-Learn Random Forest) and displays local entry attributions (SHAP explainability plots).
3. **AI Claims Engine**: Analyzes vehicle damage photos (Gemini Vision API) and runs claims risk assessments (LangGraph fraud check logic).
4. **Operations Analytics Dashboard**: Dynamically graphs premiums vs claims payouts and tracks corporate KPIs.
5. **Manager AI Relational Agent**: Translates conversational questions from managers into SQL queries and executes them against PostgreSQL.
6. **Authentication & RBAC**: Secures routes and logs users out after 15 minutes of session inactivity.
7. **System Health diagnostics**: Runs non-blocking status probes for databases, vector files, Gemini, and system resources (CPU load, memory load, disk usage).

---

## 🏗️ Architecture Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (app.py)                  │
└───────┬────────┬──────────┬───────────┬────────────┬────────────┘
        │        │          │           │            │
  Home Chatbot Quotation Claims  Dashboard Manager AI System Monitoring
        │        │          │           │            │       (Admin Only)
        └────────┴──────────┴─────┬─────┴────────────┘            │
                                  │                               │
                    ┌─────────────┴─────────────┐                 │
                    │      Service Layer        │◄────────────────┘
                    │  (Business Logic & APIs)   │
                    └─────────────┬─────────────┘
                                  │
               ┌──────────────────┴──────────────────┐
               │                                     │
      ┌────────┴────────┐                  ┌─────────┴─────────┐
      │   PostgreSQL 17  │                  │  ChromaDB Vectors │
      │  (Transactions) │                  │  (Policy Docs)    │
      └─────────────────┘                  └───────────────────┘
```

---

## 📦 Technology Stack

* **Frontend Console**: Streamlit (v1.35)
* **ML Engines**: Scikit-Learn, Joblib, SHAP
* **Cognitive Agents**: Google Gemini, LangChain, LangGraph
* **Vector Embeddings**: ChromaDB, SentenceTransformers
* **Relational DB**: PostgreSQL 17, SQLAlchemy 2.0 ORM, Alembic
* **Diagnostic Telemetry**: Psutil, Scipy Stats

---

## 📁 Folder Structure

```text
acko_ai_native_insurance_platform/
├── app.py                         # Web Portal entry point
├── run_app.py                     # Safe application launch script
├── run_tests.py                    # Pytest test suite runner CLI
├── verify_environment.py          # Platform diagnostics engine
├── requirements.txt               # Pinned dependencies
├── alembic.ini                    # Database migration configuration
├── src/
│   ├── config/                    # Pydantic environment configurations
│   ├── database/                  # Connection pools and setup files
│   ├── models/                    # SQLAlchemy database schema models
│   ├── repositories/              # Database data access layer
│   ├── services/                  # Business logic services
│   ├── modules/                   # Streamlit functional views
│   ├── ml/                        # Estimators, pipelines, SHAP explainers
│   ├── monitoring/                # Resource diagnostics and telemetry logs
│   └── utils/                     # Shared helpers
├── tests/                         # Test suites
│   ├── unit/                      # Isolated logical checks
│   └── integration/               # Multi-component workspace flows
└── logs/                          # Rotating file logger directory
```

---

## 📸 Interface Screenshots

* **Secure Login Shield**
  ![Login Screen](docs/screenshots/login.png)
  *(Authenticates users, handles locked accounts, and hosts Sandbox Demo account credentials)*
* **SHAP Underwriting Quotation**
  ![Quotation Screen](docs/screenshots/quotation.png)
  *(Calculates annual premium quotes and explains predictions using SHAP plots)*
* **Claims Vision Intelligence**
  ![Claims Screen](docs/screenshots/claims.png)
  *(Analyzes uploaded vehicle photos for damage and checks for fraud)*
* **Enterprise Telemetry Dashboard**
  ![Monitoring Diagnostics](docs/screenshots/monitoring.png)
  *(Provides real-time system alerts, server resource graphs, and log tail viewers)*

---

## 🛠️ Installation & Setup

### Prerequisites
* Python **3.11**
* PostgreSQL **17**
* Google Gemini API token

### 1. Clone & Setup virtualenv
```bash
git clone https://github.com/Yoge2003/acko_ai_native_insurance_platform.git
cd acko_ai_native_insurance_platform
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Packages
```bash
pip install -r requirements.txt
```

### 3. Environment variables
Create a `.env` file in the root workspace based on `.env.example`:
```ini
APP_ENV=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/acko_db
GEMINI_API_KEY=AIzaSy...YourKey...
CHROMA_DB_PATH=./chroma_db
SECRET_KEY=GeneratingA512BitSecureKeyHere
```

### 4. Database Schema migrations
Run migrations to initialize PostgreSQL database tables:
```bash
alembic upgrade head
```

### 5. Training ML Models
The model registry will automatically download raw datasets and train, optimize, and save Random Forest estimators and SHAP explainers on the first page load of the Premium Quotation or Claims modules.

---

## 🚀 Running the Application

To perform environment checks and run the Streamlit portal, run:
```bash
python run_app.py
```

---

## 🧪 Running Pytest Checks

To run the complete suite of 120 verification tests, run:
```bash
python run_tests.py
```

---

## 🔮 Future Improvements

1. **Real-time SMS Alert system**: Direct integrations with Twilio to prompt claims adjuster reviews.
2. **Production ML Model Registries**: Integrating MLflow to track model experiments.
3. **Advanced Fraud Audio Sensors**: Processing voice intake descriptions using multimodal models to analyze claims fraud markers.

# User & Operator Manual

Welcome to the ACKO AI Native Insurance Platform manual. This document guides policyholders, claims adjusters, underwriters, and administrators through using the web interface.

---

## 🔑 1. Getting Started: Portal Access & Logins

1. Launch your browser and navigate to the application URL (defaults to `http://localhost:8501`).
2. You will be greeted by the **ACKO Corporate Portal** secure sign-in panel.
3. Accessing the modules requires choosing one of two workflows:
   * **Corporate Login**: Enter your registered email address and credentials.
   * **Sandbox Demo Accounts**: If you are evaluating the platform, click the **Demo Accounts** tab. This provides pre-populated credentials for all 5 enterprise roles. Simply select a role card (e.g., Customer, Manager, Administrator) to log in instantly.

---

## 🏠 2. Navigation Workspace Overview

The sidebar menu adapts to your logged-in role privileges:

```
🛡️ Navigation Menu
├── 🏠 Home                 # General tech-stack and project walkthroughs
├── 🤖 AI Policy Chatbot    # RAG search for policyholders
├── 💰 Premium Quotation    # Underwriting quote estimation (SHAP attributes)
├── 📄 Claims               # Visual accident intake (Gemini Vision + Audits)
├── 📊 Analytics Dashboard  # Financial KPI charts and visual data tables
├── 🧠 Manager AI           # Text-to-SQL management agent interface
├── 🔍 System Monitoring   # (Admin only) Observability and system health log tables
└── ⚙ Settings              # Profile management and password reset panel
```

---

## ⚙️ 3. Detailed Subsystem Usage Guide

### 🤖 AI Policy Chatbot
* **Purpose**: Allows policyholders to ask questions about policy coverage.
* **How to use**: Type your question in the search box (e.g. *"Does my policy cover engine flood damage?"*).
* **Interpret Output**: Read the generated reply. Look at the bottom of the message for the **Verified Source Citations** banner containing the source PDF name and document page references.

### 💰 Premium Quotation
* **Purpose**: Calculate accurate vehicle premium rates using Scikit-Learn.
* **How to use**: Choose the vehicle type (Car or Bike). Fill in estimate fields (Model Year, Estimated Value (IDV), Engine CC, past incident records).
* **Attribution Plots**: Below the predicted target premium, view the horizontal **SHAP Contribution Chart** showing which features (e.g. high estimated value or high vehicle age) pushed the premium up or down.

### 📄 Claims AI Intake
* **Purpose**: Intake claims and audit them for fraud.
* **How to use**: Upload a claim description and an accident photograph.
* **Visual Evaluation**: The Gemini Vision API will analyze the image. The LangGraph Auditor will generate approval/rejection outcomes, repair cost estimations, and security fraud risk indicators.

### 📊 Analytics Dashboard
* **Purpose**: Monitor overall corporate metrics.
* **Interpretation**: Review the premium volumes, claims payout distributions, loss ratios, and interactive tables.

### 🧠 Manager AI
* **Purpose**: Let managers query the database using plain English.
* **How to use**: Type a relational query (e.g., *"Show the total number of approved claims"*).
* **Interpret Output**: View the generated SQL query and the database tables returned in response.

### 🔍 System Monitoring (Admin Only)
* **Purpose**: Real-time system health checks and diagnostics.
* **Interpretation**: Verify that PostgreSQL, ChromaDB, and Gemini API show green checkmarks. Monitor CPU and memory usage, and check log files for errors.

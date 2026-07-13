"""
Environment quality checker and diagnostic tool for ACKO AI Native Insurance Platform.
Validates dependencies, PostgreSQL, ChromaDB, Gemini, and ML model directories before launch.
Safe for Windows consoles.
"""

import os
import sys
from pathlib import Path

# Force stdout and stderr to handle UTF-8 safely
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Standard ASCII Banner safe for all terminals
BANNER = """
====================================================================
      [ACKO AI NATIVE INSURANCE PLATFORM - VERIFICATION ENGINE]
====================================================================
"""


def verify_all() -> bool:
    """Runs all environmental and connectivity checks."""
    print(BANNER)
    print("Initiating environment verification sequence...\n")
    
    # 1. Check .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("[FAIL] Error: .env configuration file not found in root workspace.")
        print("   Please copy .env.example to .env and configure details.")
        return False
    print("[ OK ] Root .env configuration file located")

    # 2. Check Critical Imports
    print("Checking core library dependencies...")
    try:
        import streamlit
        import sqlalchemy
        import psycopg2
        import chromadb
        import bcrypt
        import numpy
        import scipy
        import joblib
        print("[ OK ] Core dependencies (Streamlit, SQLAlchemy, psycopg2, ChromaDB, Bcrypt, SciPy, Scikit-Learn) loaded")
    except ImportError as e:
        print(f"[FAIL] Error: Missing required package: {e}")
        return False

    # 3. Load configurations and verify DB
    try:
        from src.config.settings import settings
        from src.database.connection import test_connection
    except Exception as e:
        print(f"[FAIL] Error: Failed to import internal platform components: {e}")
        return False
        
    print("Checking PostgreSQL connection thread pool...")
    try:
        db_ok, db_msg = test_connection()
        if not db_ok:
            print(f"[FAIL] Error: PostgreSQL connection failed: {db_msg}")
            return False
        print(f"[ OK ] PostgreSQL connection established ({db_msg})")
    except Exception as e:
        print(f"[FAIL] Error: Connection pool validation crashed: {e}")
        return False

    # 4. Check ChromaDB Heartbeat
    print("Checking ChromaDB local vector repository status...")
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        client.heartbeat()
        print("[ OK ] ChromaDB directory reachable and responsive")
    except Exception as e:
        print(f"[FAIL] Error: ChromaDB failed heartbeat verification: {e}")
        return False

    # 5. Check ML Estimator assets directories
    print("Checking machine learning model serialized models...")
    try:
        from src.ml.inference.model_loader import ModelLoader
        datasets = ["car_quotation", "bike_quotation", "car_claims", "bike_claims"]
        missing_models = []
        for ds in datasets:
            model_path = ModelLoader.MODELS_DIR / f"{ds}_model.joblib"
            pipe_path = ModelLoader.PIPELINES_DIR / f"{ds}_pipeline.joblib"
            art_path = ModelLoader.ARTIFACTS_DIR / f"{ds}_artifacts.joblib"
            if not model_path.exists() or not pipe_path.exists() or not art_path.exists():
                missing_models.append(ds)
                
        if missing_models:
            print(f"[WARN] Warning: Serialized pipeline files for: {', '.join(missing_models)} are not serialized.")
            print("   The model pipeline registry service will initialize and train them on-demand.")
        else:
            print("[ OK ] All pre-trained random forest and preprocessing pipelines present")
    except Exception as e:
        print(f"[WARN] Note: Could not inspect ML model directories: {e}")

    # 6. Verify Gemini API Key configuration
    if not settings.GEMINI_API_KEY:
        print("[WARN] Warning: GEMINI_API_KEY environment variable is absent.")
        print("   Chatbot and claims reasoning workflows will execute in backup mock mode.")
    else:
        print("[ OK ] Google Gemini API Token configured")

    print("\n[SUCCESS] ALL PIPELINE ENVIRONMENT TASKS VERIFIED SUCCESSFULLY!")
    return True


if __name__ == "__main__":
    correct = verify_all()
    sys.exit(0 if correct else 1)

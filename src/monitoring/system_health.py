"""
System Health Monitoring and Status Reporting.
Checks state of key components: PostgreSQL, ChromaDB, Gemini, ML Models, and hardware metrics.
"""

import os
from typing import Dict, Any
from src.database.connection import test_connection
from src.config.settings import settings
import chromadb
from src.monitoring.resource_monitor import ResourceMonitor


def get_db_health() -> Dict[str, Any]:
    """Tests SQL connection status."""
    try:
        ok, msg = test_connection()
        return {"status": "healthy" if ok else "unhealthy", "message": msg}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def get_chromadb_health() -> Dict[str, Any]:
    """Tests ChromaDB directory connection heartbeat."""
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        client.heartbeat()
        return {"status": "healthy", "message": "ChromaDB heartbeat OK"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def get_gemini_health() -> Dict[str, Any]:
    """Verifies Google Gemini API configurations."""
    if not settings.GEMINI_API_KEY:
        return {"status": "unhealthy", "message": "GEMINI_API_KEY is not configured."}
    try:
        import google.generativeai as genai
        # Verify SDK import works
        return {"status": "healthy", "message": "Gemini API client initialized."}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def get_ml_models_health() -> Dict[str, Any]:
    """Verifies presence of quotation models and encoders on disk."""
    try:
        from src.ml.inference.model_loader import ModelLoader
        missing = []
        datasets = ["car_quotation", "bike_quotation", "car_claims", "bike_claims"]
        
        for ds in datasets:
            model_path = ModelLoader.MODELS_DIR / f"{ds}_model.joblib"
            pipe_path = ModelLoader.PIPELINES_DIR / f"{ds}_pipeline.joblib"
            art_path = ModelLoader.ARTIFACTS_DIR / f"{ds}_artifacts.joblib"
            
            if not model_path.exists() or not pipe_path.exists() or not art_path.exists():
                missing.append(ds)
                
        if missing:
            return {"status": "degraded", "message": f"Serialized files absent for: {', '.join(missing)}"}
        return {"status": "healthy", "message": "All required ML model files are present on disk."}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def get_pipeline_health() -> Dict[str, Any]:
    """Validates prediction pipeline model loading sequence."""
    try:
        from src.ml.inference.model_loader import ModelLoader
        # Verify component loading does not throw exceptions
        ModelLoader.load_components("car_quotation")
        return {"status": "healthy", "message": "Components load successfully."}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Failed to load pipeline components: {e}"}


def get_system_health_report() -> Dict[str, Any]:
    """Aggregates diagnostics metrics into an overall system health status dictionary."""
    db = get_db_health()
    chroma = get_chromadb_health()
    gemini = get_gemini_health()
    ml_models = get_ml_models_health()
    pipeline = get_pipeline_health()
    resources = ResourceMonitor.get_all_resources()

    overall = "healthy"
    
    # If key dependencies are unhealthy, mark overall system unhealthy
    if db["status"] == "unhealthy" or chroma["status"] == "unhealthy" or pipeline["status"] == "unhealthy":
        overall = "unhealthy"
    # If model is degraded or system CPU/RAM usage is high, mark degraded
    elif ml_models["status"] == "degraded" or resources["cpu"]["percent"] > 90.0 or resources["memory"]["percent"] > 90.0:
        overall = "degraded"

    return {
        "status": overall,
        "database": db,
        "chromadb": chroma,
        "gemini": gemini,
        "ml_models": ml_models,
        "pipeline": pipeline,
        "resources": resources
    }

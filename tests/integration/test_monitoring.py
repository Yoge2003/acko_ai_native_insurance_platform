"""
Integration tests for the Enterprise Monitoring, Observability, and MLOps metrics layer.
"""

import os
import pytest
import numpy as np
from src.monitoring.resource_monitor import ResourceMonitor
from src.monitoring.system_health import (
    get_system_health_report, 
    get_db_health, 
    get_chromadb_health, 
    get_gemini_health
)
from src.monitoring.metrics import MLOpsMetrics
from src.monitoring.ml_monitor import MLMonitor
from src.monitoring.drift_monitor import DriftMonitor
from src.monitoring.log_manager import LogManager


def test_resource_monitoring():
    """Verifies that resource monitor returns reasonable physical resource usage specs."""
    all_res = ResourceMonitor.get_all_resources()
    
    assert "cpu" in all_res
    assert "memory" in all_res
    assert "disk" in all_res
    
    assert "percent" in all_res["cpu"]
    assert "percent" in all_res["memory"]
    assert "percent" in all_res["disk"]
    
    assert all_res["cpu"]["cores_physical"] >= 1
    assert all_res["memory"]["total_gb"] >= 0.0
    assert all_res["disk"]["total_gb"] > 0.0


def test_system_health():
    """Verifies that system health reports run and return expected structure keys."""
    db_h = get_db_health()
    assert "status" in db_h
    assert db_h["status"] in ["healthy", "unhealthy"]
    
    chroma_h = get_chromadb_health()
    assert "status" in chroma_h
    assert chroma_h["status"] in ["healthy", "unhealthy"]
    
    gemini_h = get_gemini_health()
    assert "status" in gemini_h
    
    report = get_system_health_report()
    assert "status" in report
    assert report["status"] in ["healthy", "degraded", "unhealthy"]
    assert "resources" in report
    assert "database" in report


def test_mlops_metrics():
    """Verifies in-memory collection and calculation of latency p95 stats."""
    # Reset lists
    MLOpsMetrics._prediction_count = 0
    MLOpsMetrics._failed_count = 0
    MLOpsMetrics._latencies = []
    MLOpsMetrics._predictions = []
    MLOpsMetrics._confidences = []
    
    # Record success and failure calls
    MLOpsMetrics.record_prediction(45.5, success=True, confidence=0.92, value=1250.0)
    MLOpsMetrics.record_prediction(120.0, success=False)
    
    report = MLOpsMetrics.get_metrics_report()
    
    assert report["predictions_total"] == 2
    assert report["predictions_failed"] == 1
    assert report["avg_latency_ms"] == 45.5
    assert report["avg_confidence"] == 0.92
    assert report["prediction_distribution"]["mean"] == 1250.0


def test_ml_sentinel_monitor():
    """Verifies that schema inspect check, confidence track, and outlier check structures run."""
    high_c = MLMonitor.track_confidence(0.95)
    assert high_c["level"] == "high"
    
    low_c = MLMonitor.track_confidence(0.4)
    assert low_c["level"] == "low"
    
    # Test checking unknown model schema gracefully returns check struct
    schema = MLMonitor.inspect_schema("unknown_dataset", {})
    assert "valid" in schema
    
    outliers = MLMonitor.detect_outliers("unknown_dataset", {})
    assert outliers["is_outlier"] == False


def test_drift_computation():
    """Verifies KS test calculation detects drift bounds for offset distributions."""
    np.random.seed(42)
    expected = np.random.normal(100, 10, 100)
    actual_similar = np.random.normal(100, 10, 100)
    actual_drifted = np.random.normal(150, 12, 100)
    
    # Calculate PSI
    psi_ok = DriftMonitor.calculate_psi(expected, actual_similar)
    assert psi_ok >= 0.0
    
    # Run KS
    ks_ok = DriftMonitor.calculate_ks_drift(expected, actual_similar)
    assert "drift_detected" in ks_ok
    assert ks_ok["drift_detected"] is False
    
    ks_drifted = DriftMonitor.calculate_ks_drift(expected, actual_drifted)
    assert ks_drifted["drift_detected"] is True


def test_central_log_manager():
    """Verifies that log manager creates rotating log entries and extracts tail lines."""
    logger = LogManager.get_logger("system")
    msg = "Test integration log entry verification line checkpoint"
    logger.info(msg)
    
    recent = LogManager.get_recent_logs("system", 5)
    found = False
    for line in recent:
        if msg in line:
            found = True
            break
            
    assert found is True

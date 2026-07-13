"""
MLOps Metrics Collector and Business Ratios Engine.
Tracks latencies, predictions, failure rates, and database policy stats.
"""

import numpy as np
from typing import Dict, Any, List
from datetime import datetime
from src.database.session import SessionLocal
from sqlalchemy import func
from src.models.claim import Claim
from src.models.policy import Policy


class MLOpsMetrics:
    """
    MLOps Metrics Collector tracking execution stats, latencies,
    and business ratios in real-time.
    """
    
    _prediction_count = 0
    _failed_count = 0
    _latencies: List[float] = []
    _confidences: List[float] = []
    _predictions: List[float] = []
    _last_tracked: datetime = datetime.utcnow()

    @classmethod
    def record_prediction(cls, latency_ms: float, success: bool = True, confidence: float = 1.0, value: float = 0.0) -> None:
        """Records an execution event in memory."""
        cls._prediction_count += 1
        if not success:
            cls._failed_count += 1
            return
        
        cls._latencies.append(latency_ms)
        cls._confidences.append(confidence)
        cls._predictions.append(value)
        cls._last_tracked = datetime.utcnow()
        
        if len(cls._latencies) > 10000:
            cls._latencies = cls._latencies[-10000:]
            cls._confidences = cls._confidences[-10000:]
            cls._predictions = cls._predictions[-10000:]

    @classmethod
    def get_metrics_report(cls) -> Dict[str, Any]:
        """Calculates current latency percentiles and database metrics."""
        session = SessionLocal()
        try:
            total_claims = session.query(func.count(Claim.id)).scalar() or 0
            approved_claims = session.query(func.count(Claim.id)).filter(Claim.status.in_(["approved", "Approved", "Approved_AI"])).scalar() or 0
            approval_rate = (approved_claims / total_claims) * 100.0 if total_claims > 0 else 0.0
            
            policy_count = session.query(func.count(Policy.id)).scalar() or 0
            avg_premium = session.query(func.avg(Policy.premium)).scalar() or 0.0
            max_premium = session.query(func.max(Policy.premium)).scalar() or 0.0
            min_premium = session.query(func.min(Policy.premium)).scalar() or 0.0
        except Exception:
            total_claims = 0
            approved_claims = 0
            approval_rate = 0.0
            policy_count = 0
            avg_premium = 0.0
            max_premium = 0.0
            min_premium = 0.0
        finally:
            session.close()

        latencies = cls._latencies if cls._latencies else [0.0]
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        
        confidences = cls._confidences if cls._confidences else [1.0]
        avg_confidence = float(np.mean(confidences))
        
        predictions = cls._predictions if cls._predictions else [0.0]
        pred_min = float(np.min(predictions))
        pred_max = float(np.max(predictions))
        pred_avg = float(np.mean(predictions))
        
        distribution = {
            "min": pred_min,
            "max": pred_max,
            "mean": pred_avg,
            "count": len(predictions)
        }

        return {
            "predictions_total": cls._prediction_count,
            "predictions_failed": cls._failed_count,
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "avg_confidence": round(avg_confidence, 4),
            "prediction_distribution": distribution,
            "claims": {
                "total": total_claims,
                "approved": approved_claims,
                "approval_rate": round(approval_rate, 2)
            },
            "premiums": {
                "policies_count": policy_count,
                "avg_premium": round(float(avg_premium or 0.0), 2),
                "max_premium": round(float(max_premium or 0.0), 2),
                "min_premium": round(float(min_premium or 0.0), 2)
            }
        }

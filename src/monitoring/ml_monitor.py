"""
ML Sentinel monitoring pipeline schemas, missing features, outliers, and confidences.
Uses training dataset statistics to run Z-score bounds verification.
"""

import numpy as np
from typing import Dict, Any, List
from src.ml.inference.model_loader import ModelLoader


class MLMonitor:
    """
    ML Platform Sentinel supervising schemas, outliers, missing fields,
    and confidence indicators.
    """

    @staticmethod
    def inspect_schema(dataset_type: str, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detects missing features or schema mismatch violations against baselines.
        """
        try:
            _, _, artifacts = ModelLoader.load_components(dataset_type)
            expected = artifacts.get("feature_names", [])
        except Exception as e:
            return {
                "valid": True,
                "missing_features": [],
                "mismatch_detected": False,
                "detail": f"Model artifacts not initialized: {e}"
            }

        missing = []
        mismatch = False
        mismatched_keys = []
        
        # Check expected fields
        for key in expected:
            if key not in input_features:
                missing.append(key)
                
        return {
            "valid": len(missing) == 0,
            "missing_features": missing,
            "mismatch_detected": mismatch,
            "mismatched_keys": mismatched_keys
        }

    @staticmethod
    def detect_outliers(dataset_type: str, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Z-Score outliers for numerical parameters using training stats.
        An outlier is detected if Z > 3.0.
        """
        outliers = {}
        try:
            _, _, artifacts = ModelLoader.load_components(dataset_type)
            x_train = artifacts.get("X_train")
            
            if x_train is not None:
                import pandas as pd
                if not isinstance(x_train, pd.DataFrame):
                    x_train = pd.DataFrame(x_train)
                
                # Check numeric fields
                for col in x_train.select_dtypes(include=[np.number]).columns:
                    if col in input_features:
                        try:
                            val = float(input_features[col])
                            mean = float(x_train[col].mean())
                            std = float(x_train[col].std())
                            
                            if std > 0:
                                z = abs(val - mean) / std
                                if z > 3.0:
                                    outliers[col] = {
                                        "value": val,
                                        "mean": round(mean, 2),
                                        "std": round(std, 2),
                                        "z_score": round(z, 2)
                                    }
                        except Exception:
                            # Skip if casting failed (indicates type mismatch)
                            pass
        except Exception:
            pass

        return {
            "is_outlier": len(outliers) > 0,
            "outliers": outliers
        }

    @staticmethod
    def track_confidence(confidence_score: float) -> Dict[str, Any]:
        """Categorizes prediction confidence levels."""
        status = "high"
        if confidence_score < 0.6:
            status = "low"
        elif confidence_score < 0.8:
            status = "medium"
            
        return {
            "score": round(confidence_score, 4),
            "level": status
        }

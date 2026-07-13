"""
Drift Monitor utility computing Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests.
Identifies feature drift and prediction drift compared to historical baselines.
"""

import numpy as np
from scipy.stats import ks_2samp
from typing import Dict, Any, List


class DriftMonitor:
    """
    Computes Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests
    to identify input feature and prediction distribution drifts.
    """

    @staticmethod
    def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_buckets: int = 10) -> float:
        """
        Calculates Population Stability Index (PSI) between reference and production outputs.
        """
        if len(expected) == 0 or len(actual) == 0:
            return 0.0
            
        try:
            percentiles = np.linspace(0, 100, num_buckets + 1)
            buckets = np.percentile(expected, percentiles)
            buckets[0] = -np.inf
            buckets[-1] = np.inf
            
            expected_counts = np.histogram(expected, bins=buckets)[0]
            actual_counts = np.histogram(actual, bins=buckets)[0]
            
            expected_pcts = expected_counts / len(expected)
            actual_pcts = actual_counts / len(actual)
            
            # Avoid divide-by-zero
            expected_pcts = np.where(expected_pcts == 0, 1e-4, expected_pcts)
            actual_pcts = np.where(actual_pcts == 0, 1e-4, actual_pcts)
            
            psi_value = np.sum((actual_pcts - expected_pcts) * np.log(actual_pcts / expected_pcts))
            return float(psi_value)
        except Exception:
            return 0.0

    @staticmethod
    def calculate_ks_drift(expected: np.ndarray, actual: np.ndarray) -> Dict[str, Any]:
        """
        Executes a Kolmogorov-Smirnov test to detect distribution drift.
        If p-value < 0.05, we reject the null hypothesis, indicating drift.
        """
        if len(expected) == 0 or len(actual) == 0:
            return {"stat": 0.0, "p_value": 1.0, "drift_detected": False}
        try:
            res = ks_2samp(expected, actual)
            p_val = float(res.pvalue)
            return {
                "stat": float(res.statistic),
                "p_value": p_val,
                "drift_detected": p_val < 0.05
            }
        except Exception as e:
            return {"stat": 0.0, "p_value": 1.0, "drift_detected": False, "error": str(e)}

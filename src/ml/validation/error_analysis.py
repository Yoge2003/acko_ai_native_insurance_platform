"""
Error Analysis Module.
Computes residuals, saves visual diagnostic plots, and analyzes classification errors (False Positives / False Negatives).
"""

import logging
import os
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import scipy.stats as stats

# Force non-interactive backend for server validation runs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Set up logger
logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """
    Orchestrator for managing prediction errors, residual diagnostics, and profiling misclassified samples.
    """

    @staticmethod
    def analyze_regression_residuals(
        y_true: pd.Series, y_pred: np.ndarray, output_dir: str, prefix: str
    ) -> Dict[str, Any]:
        """
        Computes residual statistics, generates the 4 requested diagnostic plots,
        and saves them to the reports directory.

        Args:
            y_true: Ground truth Series.
            y_pred: Predicted values float array.
            output_dir: Directory where plots should be saved.
            prefix: Prefix name for files (e.g. 'Car_Premium' or 'Bike_Premium').

        Returns:
            Dict[str, Any]: Compiled residual statistics and image paths.
        """
        logger.info("Starting residual analysis for: %s", prefix)
        os.makedirs(output_dir, exist_ok=True)
        y_true_arr = np.array(y_true)
        residuals = y_true_arr - y_pred

        res_mean = float(np.mean(residuals))
        res_std = float(np.std(residuals))

        prefix_clean = prefix.lower().replace(" ", "_")

        # 1. Residual Histogram
        plt.figure(figsize=(6, 4))
        plt.hist(residuals, bins=30, edgecolor="black", alpha=0.7, color="#1f77b4")
        plt.axvline(res_mean, color="red", linestyle="--", label=f"Mean: {res_mean:.2f}")
        plt.title(f"{prefix} - Residuals Distribution")
        plt.xlabel("Residual")
        plt.ylabel("Frequency")
        plt.legend()
        plt.tight_layout()
        hist_path = os.path.join(output_dir, f"{prefix_clean}_residual_histogram.png")
        plt.savefig(hist_path, dpi=120)
        plt.close()

        # 2. Q-Q Plot
        plt.figure(figsize=(6, 4))
        stats.probplot(residuals, dist="norm", plot=plt)
        plt.title(f"{prefix} - Q-Q Plot")
        plt.tight_layout()
        qq_path = os.path.join(output_dir, f"{prefix_clean}_qq_plot.png")
        plt.savefig(qq_path, dpi=120)
        plt.close()

        # 3. Predicted vs Actual Plot
        plt.figure(figsize=(6, 4))
        plt.scatter(y_true_arr, y_pred, alpha=0.5, edgecolor="none", color="#2ca02c")
        min_val = min(y_true_arr.min(), y_pred.min())
        max_val = max(y_true_arr.max(), y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], "r--", lw=2, label="Ideal")
        plt.title(f"{prefix} - Predicted vs Actual")
        plt.xlabel("Actual Value")
        plt.ylabel("Predicted Value")
        plt.legend()
        plt.tight_layout()
        pred_vs_act_path = os.path.join(output_dir, f"{prefix_clean}_predicted_vs_actual.png")
        plt.savefig(pred_vs_act_path, dpi=120)
        plt.close()

        # 4. Residual vs Prediction Plot
        plt.figure(figsize=(6, 4))
        plt.scatter(y_pred, residuals, alpha=0.5, edgecolor="none", color="#ff7f0e")
        plt.axhline(0, color="red", linestyle="--")
        plt.title(f"{prefix} - Residual vs Prediction")
        plt.xlabel("Predicted Value")
        plt.ylabel("Residual")
        plt.tight_layout()
        res_vs_pred_path = os.path.join(output_dir, f"{prefix_clean}_residual_vs_prediction.png")
        plt.savefig(res_vs_pred_path, dpi=120)
        plt.close()

        logger.info("Saved 4 diagnostic plots in output directory: %s", output_dir)

        return {
            "mean": res_mean,
            "std": res_std,
            "paths": {
                "histogram": hist_path,
                "qq_plot": qq_path,
                "predicted_vs_actual": pred_vs_act_path,
                "residual_vs_prediction": res_vs_pred_path,
            },
        }

    @staticmethod
    def analyze_classification_errors(
        X: pd.DataFrame, y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray
    ) -> Dict[str, Any]:
        """
        Diagnoses False Positives and False Negatives, profiling
        prediction confidence levels and outlining distinguishing features.

        Args:
            X: Input numerical/encoded validation features.
            y_true: True binary targets Series.
            y_pred: Predicted class label array.
            y_prob: Predicted probabilities array (probability of class 1).

        Returns:
            Dict[str, Any]: Misclassification metrics summaries.
        """
        logger.info("Initiating misclassification analysis.")
        y_true_s = pd.Series(y_true).reset_index(drop=True)
        y_pred_s = pd.Series(y_pred).reset_index(drop=True)
        y_prob_s = pd.Series(y_prob).reset_index(drop=True)
        X_reset = X.reset_index(drop=True)

        fp_mask = (y_true_s == 0) & (y_pred_s == 1)
        fn_mask = (y_true_s == 1) & (y_pred_s == 0)
        correct_mask = (y_true_s == y_pred_s)

        num_fp = int(fp_mask.sum())
        num_fn = int(fn_mask.sum())
        num_correct = int(correct_mask.sum())

        # Confidence/Probabilities distribution mapping
        fp_probs = y_prob_s[fp_mask].tolist()
        fn_probs = y_prob_s[fn_mask].tolist()
        correct_probs = y_prob_s[correct_mask].tolist()

        mean_prob_fp = float(np.mean(fp_probs)) if fp_probs else 0.0
        mean_prob_fn = float(np.mean(fn_probs)) if fn_probs else 0.0
        mean_prob_correct = float(np.mean(correct_probs)) if correct_probs else 0.0

        # Feature divergence profiling (numerical deviation of misclassified cases)
        num_cols = X_reset.select_dtypes(include=[np.number]).columns.tolist()
        feature_diffs = []

        if num_cols and (num_fp + num_fn > 0):
            mean_correct = X_reset.loc[correct_mask, num_cols].mean()
            std_correct = X_reset.loc[correct_mask, num_cols].std().fillna(0)
            
            incorrect_mask = fp_mask | fn_mask
            mean_incorrect = X_reset.loc[incorrect_mask, num_cols].mean()

            for col in num_cols:
                mc = mean_correct[col]
                mi = mean_incorrect[col]
                std_c = std_correct[col]
                
                # Compute standardized mean difference
                norm_diff = abs(mc - mi) / (std_c + 1e-6)
                feature_diffs.append({
                    "feature": col,
                    "mean_correct": float(mc),
                    "mean_incorrect": float(mi),
                    "std_difference": float(norm_diff),
                })

        # Rank feature differences to diagnose primary risk factors where errors concentrate
        feature_diffs_df = pd.DataFrame(feature_diffs)
        if not feature_diffs_df.empty:
            feature_diffs_df = feature_diffs_df.sort_values(by="std_difference", ascending=False)
            top_reasons = feature_diffs_df.head(5).to_dict(orient="records")
        else:
            top_reasons = []

        logger.info("Misclassification profiling complete: %d FP, %d FN.", num_fp, num_fn)

        return {
            "num_false_positives": num_fp,
            "num_false_negatives": num_fn,
            "num_correct": num_correct,
            "mean_confidence_fp": mean_prob_fp,
            "mean_confidence_fn": mean_prob_fn,
            "mean_confidence_correct": mean_prob_correct,
            "top_reasons": top_reasons,
        }

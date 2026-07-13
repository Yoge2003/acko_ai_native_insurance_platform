"""
SHAP Visualizations Module.
Outputs beeswarm summary plots, bar importance plots, local waterfall/force/decision plots,
and dependence plots for top features.
"""

import os
import logging
from typing import List, Any
import numpy as np
import pandas as pd

# Force non-interactive backend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap

# Set up logger
logger = logging.getLogger(__name__)


class ShapVisualizer:
    """
    Generates and saves visual plots for SHAP model explanations.
    """

    @staticmethod
    def generate_plots(
        explainer: Any,
        shap_vals: Any,
        X_input: pd.DataFrame,
        output_dir: str,
        prefix: str,
    ) -> List[str]:
        """
        Generates and saves the 6 requested SHAP visualization files.

        Args:
            explainer: Cached TreeExplainer instance.
            shap_vals: Array or list representing raw SHAP values.
            X_input: Dataframe representing dataset input context.
            output_dir: Target output folder.
            prefix: Prefix name for files (e.g. 'Car_Premium').

        Returns:
            List[str]: Paths to saved image artifacts.
        """
        os.makedirs(output_dir, exist_ok=True)
        paths = []
        prefix_clean = prefix.lower().replace(" ", "_")

        # Resolve classification vs regression outputs format
        if isinstance(shap_vals, list):
            # Binary classification list format, get class 1 (approved)
            target_shap_vals = shap_vals[1]
        elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
            # Array output format (N, D, classes), get class 1
            target_shap_vals = shap_vals[:, :, 1]
        else:
            # Regression format
            target_shap_vals = shap_vals

        # Helper to extract baseline expected value
        base_val = explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)) and len(base_val) > 1:
            base_val = base_val[1]

        # 1. Summary Plot (Beeswarm)
        try:
            plt.figure(figsize=(8, 6))
            shap.summary_plot(target_shap_vals, X_input, show=False)
            plt.title(f"{prefix} - SHAP Summary Plot")
            plt.tight_layout()
            p1 = os.path.join(output_dir, f"{prefix_clean}_summary_plot.png")
            plt.savefig(p1, dpi=120)
            plt.close()
            paths.append(p1)
            logger.info("Saved Summary Plot: %s", p1)
        except Exception as e:
            logger.error("Failed to render Beeswarm Summary Plot: %s", e)

        # 2. Bar Plot (Global Importance)
        try:
            plt.figure(figsize=(8, 6))
            shap.summary_plot(target_shap_vals, X_input, plot_type="bar", show=False)
            plt.title(f"{prefix} - SHAP Feature Importance (Bar)")
            plt.tight_layout()
            p2 = os.path.join(output_dir, f"{prefix_clean}_bar_plot.png")
            plt.savefig(p2, dpi=120)
            plt.close()
            paths.append(p2)
            logger.info("Saved Bar Plot: %s", p2)
        except Exception as e:
            logger.error("Failed to render Bar Plot: %s", e)

        # 3. Waterfall Plot (Local Attribution for 1st sample)
        try:
            plt.figure(figsize=(8, 6))
            exp_obj = shap.Explanation(
                values=target_shap_vals[0],
                base_values=float(base_val),
                data=X_input.iloc[0].values,
                feature_names=X_input.columns.tolist(),
            )
            shap.plots.waterfall(exp_obj, show=False)
            plt.title(f"{prefix} - Local Waterfall (Sample 0)")
            plt.tight_layout()
            p3 = os.path.join(output_dir, f"{prefix_clean}_waterfall_plot.png")
            plt.savefig(p3, dpi=120)
            plt.close()
            paths.append(p3)
            logger.info("Saved Waterfall Plot: %s", p3)
        except Exception as e:
            logger.error("Failed to render Waterfall Plot: %s", e)

        # 4. Force Plot (Local attribution for 1st sample)
        try:
            plt.figure(figsize=(10, 4))
            shap.force_plot(
                float(base_val),
                target_shap_vals[0],
                X_input.iloc[0],
                matplotlib=True,
                show=False,
            )
            plt.title(f"{prefix} - Local Force Plot (Sample 0)")
            plt.tight_layout()
            p4 = os.path.join(output_dir, f"{prefix_clean}_force_plot.png")
            plt.savefig(p4, dpi=120)
            plt.close()
            paths.append(p4)
            logger.info("Saved Force Plot: %s", p4)
        except Exception as e:
            logger.error("Failed to render Force Plot: %s", e)

        # 决策图 Decision Plot
        try:
            plt.figure(figsize=(8, 6))
            shap.decision_plot(
                float(base_val),
                target_shap_vals[0],
                X_input.iloc[0],
                show=False,
            )
            plt.title(f"{prefix} - Local Decision Plot (Sample 0)")
            plt.tight_layout()
            p5 = os.path.join(output_dir, f"{prefix_clean}_decision_plot.png")
            plt.savefig(p5, dpi=120)
            plt.close()
            paths.append(p5)
            logger.info("Saved Decision Plot: %s", p5)
        except Exception as e:
            logger.error("Failed to render Decision Plot: %s", e)

        # 6. Dependence Plot (Top 5 features by mean absolute SHAP value)
        try:
            mean_abs = np.mean(np.abs(target_shap_vals), axis=0)
            top_5_idx = np.argsort(mean_abs)[::-1][:5]
            top_5_cols = [X_input.columns[i] for i in top_5_idx]

            for col in top_5_cols:
                try:
                    plt.figure(figsize=(6, 4))
                    shap.dependence_plot(
                        col,
                        target_shap_vals,
                        X_input,
                        show=False,
                    )
                    plt.title(f"{prefix} - Dependence Plot ({col})")
                    plt.tight_layout()
                    p6 = os.path.join(
                        output_dir, f"{prefix_clean}_dependence_{col.lower()}.png"
                    )
                    plt.savefig(p6, dpi=120)
                    plt.close()
                    paths.append(p6)
                    logger.info("Saved Dependence Plot: %s", p6)
                except Exception as ex:
                    logger.error("Failed to render Dependence Plot for %s: %s", col, ex)
        except Exception as e:
            logger.error("Failed to execute top 5 features dependence plots sequence: %s", e)

        return paths

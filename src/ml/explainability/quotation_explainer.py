"""
Quotation Explainer.
Generates local, global, and human-readable explanations using SHAP for Car and Bike Premium models.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.ml.explainability.base_explainer import BaseExplainer
from src.ml.explainability.visualization import ShapVisualizer

# Set up logger
logger = logging.getLogger(__name__)


# Standard human terms mapping for key features
FEATURE_HUMAN_MAPPING = {
    "num__idv": "vehicle IDV",
    "num__engine_cc": "engine capacity",
    "num__claim_history_count": "previous claims history",
    "num__ncb_percent": "No Claim Bonus",
    "num__vehicle_age_years": "vehicle age",
    "num__num_addons": "quantity of policy addons",
    "num__city_risk_score": "city risk code",
    "num__customer_age": "policyholder age",
    "num_claim_to_idv_ratio": "claim-to-IDV ratio",
    "num_damage_severity_score": "damage severity",
    "num_severity_index": "incident severity index",
    "num_claim_amount": "claim amount",
    "num_previous_claims_count": "previous claims history",
    "num_policy_age_months": "policy duration in months",
}


def clean_feature_name(feat: str) -> str:
    """
    Translates a machine feature column name into an accessible business term.
    """
    if feat in FEATURE_HUMAN_MAPPING:
        return FEATURE_HUMAN_MAPPING[feat]
    
    # Strip pipeline prefixes and underscores
    clean = feat
    for prefix in ["num__", "cat__", "bool__"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
    
    return clean.replace("_", " ").strip()


class QuotationExplainer(BaseExplainer):
    """
    Explainer specialized for regression models (Car and Bike Premium).
    """

    def explain_prediction(self, X_input: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates local explanation parameters for the first entry in X_input.

        Args:
            X_input: Input features row(s).

        Returns:
            Dict[str, Any]: local SHAP indicators and human text.
        """
        logger.info("Computing local SHAP explanations for quotation prediction.")
        
        # Ensure row is formatted matching feature ordering
        X_row = X_input[self.feature_names].head(1)
        
        # Run TreeExplainer predictions
        shap_vals = self.explainer.shap_values(X_row)

        # In newer shap version, expected_value can be a list or array, select baseline
        base_val = self.explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)) and len(base_val) > 1:
            base_val = base_val[1]
        
        # Resolve shape of shap values
        if isinstance(shap_vals, list):
            target_shap = shap_vals[1][0]
        elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
            target_shap = shap_vals[0, :, 1]
        elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 2:
            target_shap = shap_vals[0]
        else:
            target_shap = np.array(shap_vals).flatten()

        prediction_val = float(self.model.predict(X_row)[0])

        # Compile contributions lists
        pos_contribs = []
        neg_contribs = []

        for feat, val in zip(self.feature_names, target_shap):
            human_name = clean_feature_name(feat)
            item = {
                "feature": feat,
                "feature_human": human_name,
                "shap_value": float(val),
                "actual_value": X_row[feat].iloc[0],
            }
            if val > 0:
                pos_contribs.append(item)
            else:
                neg_contribs.append(item)

        # Sort contributions by absolute magnitude
        pos_contribs = sorted(pos_contribs, key=lambda x: abs(x["shap_value"]), reverse=True)
        neg_contribs = sorted(neg_contribs, key=lambda x: abs(x["shap_value"]), reverse=True)

        # Dynamic human text synthesis
        pos_terms = [item["feature_human"] for item in pos_contribs[:3]]
        neg_terms = [item["feature_human"] for item in neg_contribs[:3]]

        text = ""
        if pos_terms:
            if len(pos_terms) > 1:
                pos_str = ", ".join(pos_terms[:-1]) + f", and {pos_terms[-1]}"
            else:
                pos_str = pos_terms[0]
            text += f"The premium increased mainly because the vehicle has a high/active {pos_str}."

        if neg_terms:
            if len(neg_terms) > 1:
                neg_str = ", ".join(neg_terms[:-1]) + f", and {neg_terms[-1]}"
            else:
                neg_str = neg_terms[0]
            if text:
                text += " "
            text += f"The premium decreased because the driver/policy has a favorable {neg_str}."

        if not text:
            text = "The premium is aligned with the baseline premium pricing."

        return {
            "expected_value": float(base_val),
            "prediction_value": prediction_val,
            "top_positive_contributors": pos_contribs[:5],
            "top_negative_contributors": neg_contribs[:5],
            "explanation_text": text,
        }

    def explain_global(self, max_samples: int = 500) -> Dict[str, Any]:
        """
        Calculates global SHAP importance ranks and profiles over sample datasets.

        Args:
            max_samples: Constraint cap on dataset samples to limit evaluation overhead.

        Returns:
            Dict[str, Any]: Feature rank records comparison.
        """
        logger.info("Computing global SHAP feature importances.")
        X_val_sample = self.data_package["X_val"].head(max_samples)
        shap_vals = self.explainer.shap_values(X_val_sample)

        if isinstance(shap_vals, list):
            target_shap = shap_vals[1]
        elif isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
            target_shap = shap_vals[:, :, 1]
        else:
            target_shap = shap_vals

        mean_abs_attr = np.mean(np.abs(target_shap), axis=0)

        # Get Random Forest Importance
        rf_importances = self.model.feature_importances_

        comparison = []
        for idx, feat in enumerate(self.feature_names):
            comparison.append({
                "feature": feat,
                "feature_human": clean_feature_name(feat),
                "shap_importance": float(mean_abs_attr[idx]),
                "rf_importance": float(rf_importances[idx]),
            })

        # Sort descending by SHAP importance
        comparison = sorted(comparison, key=lambda x: x["shap_importance"], reverse=True)

        return {"global_rankings": comparison}

    def save_visualizations(
        self, X_input: pd.DataFrame, output_dir: str, prefix: str
    ) -> List[str]:
        """
        Generates and saves visual plots for model predictions.
        """
        X_val_subset = self.data_package["X_val"]
        shap_vals = self.explainer.shap_values(X_val_subset)

        return ShapVisualizer.generate_plots(
            self.explainer, shap_vals, X_val_subset, output_dir, prefix
        )

    def generate_report(self, output_path: str) -> None:
        """
        Generates a model-specific explainability report.

        Args:
            output_path: Target save path.
        """
        logger.info("Generating model-specific SHAP report for: %s", self.dataset_type)
        global_res = self.explain_global()
        local_res = self.explain_prediction(self.data_package["X_val"])

        report_md = f"""# Model-Specific SHAP Explainability Report: {self.dataset_type}

This report presents model attribution diagnostics and local predictions interpretations.

## 1. Model Information
*   **Dataset Type**: {self.dataset_type}
*   **Features Count**: {len(self.feature_names)}

## 2. Global Feature Rankings
"""
        for i, item in enumerate(global_res["global_rankings"][:15]):
            report_md += f"{i+1}. **{item['feature_human']}** (`{item['feature']}`): SHAP = {item['shap_importance']:.6f}, RF Gini = {item['rf_importance']:.6f}\n"

        report_md += f"""
## 3. Local Prediction Narrative Sample
*   **Narrative**: "{local_res['explanation_text']}"
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        logger.info("Saved explanation report to: %s", output_path)


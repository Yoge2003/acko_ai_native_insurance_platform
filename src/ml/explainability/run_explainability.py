"""
Explainability Suite Orcherstrator.
Runs the entire explainability pipelines for Car Premium, Bike Premium, Car Claims, and Bike Claims.
Saves all visual diagnostic charts to reports/figures/shap/ and writes shap_explainability_report.md.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from src.ml.explainability.quotation_explainer import QuotationExplainer
from src.ml.explainability.claims_explainer import ClaimsExplainer
from src.ml.explainability.explanation_report import ExplanationReportGenerator


def run_explainability_analysis() -> None:
    """
    Executes SHAP analyses for all four machine learning models.
    Produces metric values, saves graphs, and compiles the target report.
    """
    logger.info("======================================================================")
    logger.info("ACKO INSURANCE PLATFORM - STARTING EXPLAINABLE AI (XAI) SUITE EXECUTION")
    logger.info("======================================================================")

    output_plots_dir = "reports/figures/shap"
    report_file = "reports/shap_explainability_report.md"

    # 1. Car Premium Explainer
    logger.info("--- [1/4] EXPLAINING CAR PREMIUM MODEL (REGRESSION) ---")
    car_prem_exp = QuotationExplainer("car_quotation")
    car_prem_global = car_prem_exp.explain_global(max_samples=200)
    car_prem_local = car_prem_exp.explain_prediction(car_prem_exp.data_package["X_val"])
    logger.info("Generating SHAP visuals for Car Premium...")
    car_prem_exp.save_visualizations(
        car_prem_exp.data_package["X_val"].head(50),
        output_dir=output_plots_dir,
        prefix="Car Premium"
    )

    # 2. Bike Premium Explainer
    logger.info("--- [2/4] EXPLAINING BIKE PREMIUM MODEL (REGRESSION) ---")
    bike_prem_exp = QuotationExplainer("bike_quotation")
    bike_prem_global = bike_prem_exp.explain_global(max_samples=200)
    bike_prem_local = bike_prem_exp.explain_prediction(bike_prem_exp.data_package["X_val"])
    logger.info("Generating SHAP visuals for Bike Premium...")
    bike_prem_exp.save_visualizations(
        bike_prem_exp.data_package["X_val"].head(50),
        output_dir=output_plots_dir,
        prefix="Bike Premium"
    )

    # 3. Car Claims Explainer
    logger.info("--- [3/4] EXPLAINING CAR CLAIMS MODEL (CLASSIFICATION) ---")
    car_claims_exp = ClaimsExplainer("car_claims")
    car_claims_global = car_claims_exp.explain_global(max_samples=200)
    car_claims_local = car_claims_exp.explain_prediction(car_claims_exp.data_package["X_val"])
    logger.info("Generating SHAP visuals for Car Claims...")
    car_claims_exp.save_visualizations(
        car_claims_exp.data_package["X_val"].head(50),
        output_dir=output_plots_dir,
        prefix="Car Claims"
    )

    # 4. Bike Claims Explainer
    logger.info("--- [4/4] EXPLAINING BIKE CLAIMS MODEL (CLASSIFICATION) ---")
    bike_claims_exp = ClaimsExplainer("bike_claims")
    bike_claims_global = bike_claims_exp.explain_global(max_samples=200)
    bike_claims_local = bike_claims_exp.explain_prediction(bike_claims_exp.data_package["X_val"])
    logger.info("Generating SHAP visuals for Bike Claims...")
    bike_claims_exp.save_visualizations(
        bike_claims_exp.data_package["X_val"].head(50),
        output_dir=output_plots_dir,
        prefix="Bike Claims"
    )

    # 5. Generate Report
    logger.info("--- [5/5] WRITING UNIFIED SHAP ATTRIBUTION REPORT ---")
    ExplanationReportGenerator.generate_report(
        car_prem_global=car_prem_global["global_rankings"],
        car_prem_local=car_prem_local,
        bike_prem_global=bike_prem_global["global_rankings"],
        bike_prem_local=bike_prem_local,
        car_claims_global=car_claims_global["global_rankings"],
        car_claims_local=car_claims_local,
        bike_claims_global=bike_claims_global["global_rankings"],
        bike_claims_local=bike_claims_local,
        output_path=report_file
    )

    logger.info("======================================================================")
    logger.info("EXPLAINABILITY ANALYSIS COMPILED SUCCESSFULLY.")
    logger.info("Report located at: %s", os.path.abspath(report_file))
    logger.info("Plots located at: %s", os.path.abspath(output_plots_dir))
    logger.info("======================================================================")


if __name__ == "__main__":
    run_explainability_analysis()

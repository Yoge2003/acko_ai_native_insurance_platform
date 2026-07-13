"""
Validation Orchestrator Runner.
Farms dataset pipelines, trains production models, executes K-Fold validations,
performs residual/misclassification error diagnostics, and generates the final report.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import validation package components
from src.ml.training.training_pipeline import TrainingPipeline
from src.ml.models.car_quotation_trainer import CarQuotationTrainer
from src.ml.models.bike_quotation_trainer import BikeQuotationTrainer
from src.ml.models.car_claims_trainer import CarClaimsTrainer
from src.ml.models.bike_claims_trainer import BikeClaimsTrainer
from src.ml.validation.regression_validator import RegressionValidator
from src.ml.validation.classification_validator import ClassificationValidator
from src.ml.validation.validation_report import ValidationReportGenerator


def run_full_validation_sequence() -> None:
    """
    Executes the entire model validation sequence across all four pipelines.
    Runs CV, residual plotting, misclassification checks, and writes reports/model_validation_report.md.
    """
    logger.info("======================================================================")
    logger.info("ACKO INSURANCE PLATFORM - STARTING MODEL VALIDATION & ERROR ANALYSIS SUITE")
    logger.info("======================================================================")

    output_dir = "reports/figures"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Car Premium Validation (regression)
    logger.info("--- [1/4] VALIDATING CAR PREMIUM MODEL (REGRESSION) ---")
    car_quote_pkg = TrainingPipeline.run_pipeline("car_quotation")
    car_quote_trainer = CarQuotationTrainer(car_quote_pkg)
    # Train the official RandomForestRegressor
    car_quote_trainer.train_production_model(use_full_data=True)
    car_prem_validator = RegressionValidator(car_quote_trainer)
    car_prem_results = car_prem_validator.validate(output_dir, "Car_Premium")

    # 2. Bike Premium Validation (regression)
    logger.info("--- [2/4] VALIDATING BIKE PREMIUM MODEL (REGRESSION) ---")
    bike_quote_pkg = TrainingPipeline.run_pipeline("bike_quotation")
    bike_quote_trainer = BikeQuotationTrainer(bike_quote_pkg)
    # Train the official RandomForestRegressor
    bike_quote_trainer.train_production_model(use_full_data=True)
    bike_prem_validator = RegressionValidator(bike_quote_trainer)
    bike_prem_results = bike_prem_validator.validate(output_dir, "Bike_Premium")

    # 3. Car Claims Validation (classification)
    logger.info("--- [3/4] VALIDATING CAR CLAIMS MODEL (CLASSIFICATION) ---")
    car_claims_pkg = TrainingPipeline.run_pipeline("car_claims")
    car_claims_trainer = CarClaimsTrainer(car_claims_pkg)
    # Train the official RandomForestClassifier
    car_claims_trainer.train_production_model(use_full_data=True)
    car_claim_validator = ClassificationValidator(car_claims_trainer)
    car_claim_results = car_claim_validator.validate()

    # 4. Bike Claims Validation (classification)
    logger.info("--- [4/4] VALIDATING BIKE CLAIMS MODEL (CLASSIFICATION) ---")
    bike_claims_pkg = TrainingPipeline.run_pipeline("bike_claims")
    bike_claims_trainer = BikeClaimsTrainer(bike_claims_pkg)
    # Train the official RandomForestClassifier
    bike_claims_trainer.train_production_model(use_full_data=True)
    bike_claim_validator = ClassificationValidator(bike_claims_trainer)
    bike_claim_results = bike_claim_validator.validate()

    # 5. Synthesis & Report Generation
    logger.info("--- [5/5] GENERATING SYSTEM READINESS REPORTS & SYNTHESIZING RESULTS ---")
    report_file = "reports/model_validation_report.md"
    ValidationReportGenerator.generate_report(
        car_prem=car_prem_results,
        bike_prem=bike_prem_results,
        car_claim=car_claim_results,
        bike_claim=bike_claim_results,
        output_path=report_file,
    )

    logger.info("======================================================================")
    logger.info("MODEL VALIDATION SUITE EXECUTION COMPLETE.")
    logger.info("Report location: %s", os.path.abspath(report_file))
    logger.info("Plots location: %s", os.path.abspath(output_dir))
    logger.info("======================================================================")


if __name__ == "__main__":
    run_full_validation_sequence()

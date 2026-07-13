"""
Integration Tests for Streamlit UI modules with active ML Inference and PostgreSQL database layers.
Verifies quotation generation, claim submission, database persistence, and MLOps prediction logging.
"""

import unittest
import uuid
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from src.database.session import SessionLocal
from src.models.user import User
from src.models.policy import Policy
from src.models.quotation import Quotation
from src.models.claim import Claim
from src.models.prediction import PredictionLog
from src.models.image import UploadedImage
from src.modules.quotation.services import QuotationService
from src.modules.claims.services import ClaimsService


class TestStreamlitIntegration(unittest.TestCase):
    """
    Simulates user workflow actions from UI boundary and asserts complete transaction safety.
    """

    def setUp(self) -> None:
        """
        Set up clean state by removing any previous test records to prevent conflicts.
        """
        import src.database.database as db_module
        if db_module.engine is not None:
            SessionLocal.configure(bind=db_module.engine)
        self.session = SessionLocal()
        self.cleanup_records()

    def tearDown(self) -> None:
        """
        Clean up any test records generated during execution to keep the DB clean.
        """
        self.cleanup_records()
        self.session.close()

    def cleanup_records(self) -> None:
        """
        Cleans up test records mapped to default customer email 'customer@acko.com'.
        """
        try:
            # Locate test user
            user = self.session.query(User).filter(User.email == "customer@acko.com").first()
            if user:
                # Delete dependent records in sequence of foreign key constraints
                self.session.query(UploadedImage).filter(
                    UploadedImage.claim_id.in_(
                        self.session.query(Claim.id).filter(Claim.user_id == user.id)
                    )
                ).delete(synchronize_session=False)

                self.session.query(Claim).filter(Claim.user_id == user.id).delete(synchronize_session=False)
                self.session.query(Quotation).filter(Quotation.user_id == user.id).delete(synchronize_session=False)
                self.session.query(Policy).filter(Policy.user_id == user.id).delete(synchronize_session=False)
                self.session.query(User).filter(User.id == user.id).delete(synchronize_session=False)
            
            # Clean prediction logs for test runs
            self.session.query(PredictionLog).filter(
                PredictionLog.prediction_type.in_(["premium_quotation", "claims_auto_approval"])
            ).delete(synchronize_session=False)

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Warnings during cleanup records block: {e}")

    def test_quotation_integration_workflow(self) -> None:
        """
        Verifies Quotation Module generates accurate annual premium predictions,
        saves records to PostgreSQL, and logs ML prediction telemetry.
        """
        input_data = {
            "customer_name": "Jane User Acko",
            "age": 30,
            "gender": "Female",
            "mobile_number": "+919876543210",
            "vehicle_type": "Car",
            "manufacturer": "Honda",
            "model": "City",
            "fuel_type": "Petrol",
            "manufacturing_year": 2022,
            "city": "Mumbai",
            "state": "Maharashtra",
            "vehicle_idv": 800000.0,
            "ncb_percentage": 20,
            "previous_claims": False
        }

        # Invoke integrated UI service wrapper
        service = QuotationService()
        quote_res = service.generate_premium_quote(input_data)

        # Assert results signature
        self.assertEqual(quote_res["status"], "success")
        self.assertGreater(quote_res["predicted_premium"], 0.0)
        self.assertGreaterEqual(quote_res["confidence_score"], 0.0)
        self.assertTrue(isinstance(quote_res["model_version"], str))
        self.assertTrue(isinstance(quote_res["timestamp"], str))
        self.assertTrue(isinstance(quote_res["shap_summary"], str))
        self.assertTrue(len(quote_res["top_positive_features"]) >= 0)
        self.assertTrue(len(quote_res["top_negative_features"]) >= 0)

        # Query Database to verify persistence
        user = self.session.query(User).filter(User.email == "customer@acko.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.full_name, "Jane User Acko")

        quote_db = self.session.query(Quotation).filter(Quotation.user_id == user.id).first()
        self.assertIsNotNone(quote_db)
        self.assertEqual(quote_db.predicted_premium, quote_res["predicted_premium"])
        self.assertEqual(quote_db.vehicle_type, "car")

        pred_log = self.session.query(PredictionLog).filter(
            PredictionLog.prediction_type == "premium_quotation"
        ).order_by(PredictionLog.created_at.desc()).first()
        self.assertIsNotNone(pred_log)
        self.assertEqual(pred_log.model_version, quote_res["model_version"])
        self.assertGreaterEqual(pred_log.latency_ms, 0)
        self.assertTrue(len(pred_log.input_hash) > 0)
        self.assertTrue(len(pred_log.output_hash) > 0)

    def test_claims_integration_workflow(self) -> None:
        """
        Verifies Claims Module logs collision claim applications, runs classifier audits,
        persists claim records, and reports risk explanations.
        """
        payload = {
            "claim_id": "CLM-INTTEST",
            "policy_number": "POL-INTTEST",
            "vehicle_type": "Car",
            "claim_amount": 75000.0,
            "description": "Bumper collision and fender damage sustained in rain.",
            "uploaded_image": None
        }

        # Invoke integrated UI service wrapper
        service = ClaimsService()
        result = service.submit_claim_request(payload)

        # Assert results signature
        self.assertEqual(result["status"], "Submitted")
        self.assertEqual(result["claim_id"], "CLM-INTTEST")
        self.assertEqual(result["policy_number"], "POL-INTTEST")
        self.assertIn(result["approval_decision"], ["APPROVED", "REJECTED"])
        self.assertTrue(0.0 <= result["approval_probability"] <= 1.0)
        self.assertTrue(0.0 <= result["confidence"] <= 1.0)
        self.assertTrue(isinstance(result["model_version"], str))
        self.assertTrue(isinstance(result["submitted_at"], str))
        self.assertTrue(isinstance(result["shap_summary"], str))
        self.assertTrue(isinstance(result["human_review_flag"], bool))

        # Query Database to verify persistence
        user = self.session.query(User).filter(User.email == "customer@acko.com").first()
        self.assertIsNotNone(user)

        policy_db = self.session.query(Policy).filter(Policy.policy_number == "POL-INTTEST").first()
        self.assertIsNotNone(policy_db)
        self.assertEqual(policy_db.user_id, user.id)

        claim_db = self.session.query(Claim).filter(Claim.policy_id == policy_db.id).first()
        self.assertIsNotNone(claim_db)
        self.assertEqual(claim_db.claim_amount, 75000.0)
        self.assertEqual(claim_db.predicted_decision, result["approval_decision"].lower())

        pred_log = self.session.query(PredictionLog).filter(
            PredictionLog.prediction_type == "claims_auto_approval"
        ).order_by(PredictionLog.created_at.desc()).first()
        self.assertIsNotNone(pred_log)
        self.assertEqual(pred_log.model_version, result["model_version"])
        self.assertGreaterEqual(pred_log.latency_ms, 0)

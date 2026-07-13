"""
Integration Tests for the Gemini Vision Claims AI pipeline.
Asserts image validation, preprocessing constraints, response serialization,
ML feature engineering, database persistence, and fallback configurations.
"""

import unittest
import io
import os
import uuid
import math
from unittest.mock import patch, MagicMock
from PIL import Image

from src.database.session import SessionLocal
from src.modules.claims.services import (
    ClaimsService,
    validate_and_preprocess_image,
    analyze_damage_image
)
from src.models.user import User
from src.models.policy import Policy
from src.models.claim import Claim
from src.models.image import UploadedImage


class MockUploadedFile:
    """Wraps stream buffers mimicking Streamlit's UploadedFile object."""
    def __init__(self, name: str, content: bytes):
        self.name = name
        self.content = content
        self._buffer = io.BytesIO(content)

    def seek(self, *args, **kwargs):
        return self._buffer.seek(*args, **kwargs)

    def tell(self, *args, **kwargs):
        return self._buffer.tell(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)

    def getbuffer(self):
        return self._buffer.getbuffer()


class TestClaimsVisionIntegration(unittest.TestCase):
    """
    Integration tests covering claims assessment vision coordination.
    """
    def setUp(self) -> None:
        # DB Session Binding
        import src.database.database as db_module
        if db_module.engine is not None:
            SessionLocal.configure(bind=db_module.engine)
        self.session = SessionLocal()
        
        # Clean up database customer records for 'customer@acko.com'
        self.cleanup_records()
        self.service = ClaimsService()

        # Seed valid in-memory image bytes
        img = Image.new("RGB", (300, 300), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        self.valid_image_bytes = buf.getvalue()

    def tearDown(self) -> None:
        self.cleanup_records()
        self.session.close()

    def cleanup_records(self) -> None:
        try:
            user = self.session.query(User).filter(User.email == "customer@acko.com").first()
            if user:
                claims = self.session.query(Claim).filter(Claim.user_id == user.id).all()
                for c in claims:
                    self.session.query(UploadedImage).filter(UploadedImage.claim_id == c.id).delete()
                    self.session.delete(c)
                self.session.query(Policy).filter(Policy.user_id == user.id).delete()
                self.session.delete(user)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Cleanup warning: {e}")

    def test_image_validation_valid(self) -> None:
        """Verifies that format-compliant image files pass validations successfully."""
        mock_file = MockUploadedFile("damage.jpg", self.valid_image_bytes)
        img = validate_and_preprocess_image(mock_file)
        self.assertIsInstance(img, Image.Image)
        # Preprocessor should maintain 300x300 since it is below 1024 max bound
        self.assertEqual(img.size, (300, 300))

    def test_image_validation_invalid_format(self) -> None:
        """Verifies that malformed or non-image files raise ValueError."""
        mock_file = MockUploadedFile("doc.txt", b"random text data that is not an image")
        with self.assertRaises(ValueError):
            validate_and_preprocess_image(mock_file)

    def test_image_validation_exceeding_size(self) -> None:
        """Verifies that image files exceeding 10MB limits throw ValueError."""
        excessive_bytes = b"0" * (11 * 1024 * 1024)
        mock_file = MockUploadedFile("huge.jpg", excessive_bytes)
        with self.assertRaises(ValueError):
            validate_and_preprocess_image(mock_file)

    def test_image_validation_low_resolution(self) -> None:
        """Verifies that resolution below 200px throws resolution error."""
        img = Image.new("RGB", (50, 50), color="red")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        mock_file = MockUploadedFile("tiny.jpg", buf.getvalue())
        with self.assertRaises(ValueError):
            validate_and_preprocess_image(mock_file)

    @patch("google.generativeai.GenerativeModel")
    def test_gemini_response_parsing(self, mock_model_class: MagicMock) -> None:
        """Verifies structured JSON properties return accurately from Gemini model mocks."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"damaged_parts": ["bumper", "headlight"], "damage_severity": "Low", "estimated_repair_complexity": "Low", "visible_fraud_indicators": ["none"], "confidence_score": 0.95, "natural_language_assessment": "Bumper cracks", "damage_type": "Bumper"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        img = Image.open(io.BytesIO(self.valid_image_bytes))
        data = analyze_damage_image(img, "test_api_key")
        
        self.assertEqual(data["damage_severity"], "Low")
        self.assertEqual(data["damaged_parts"], ["bumper", "headlight"])
        self.assertEqual(data["damage_type"], "Bumper")
        self.assertAlmostEqual(data["confidence_score"], 0.95)

    @patch("src.modules.claims.services.analyze_damage_image")
    def test_claims_prediction_integration_and_persistence(self, mock_analyze: MagicMock) -> None:
        """Wraps end-to-end integration and tests PostgreSQL DB persistence validation."""
        mock_analyze.return_value = {
            "damaged_parts": ["bumper", "windshield"],
            "damage_severity": "High",
            "estimated_repair_complexity": "Medium",
            "visible_fraud_indicators": ["none"],
            "confidence_score": 0.88,
            "damage_type": "Windshield",
            "natural_language_assessment": "The front bumper is heavily scraped, windshield is cracked."
        }

        mock_file = MockUploadedFile("front_dent.jpg", self.valid_image_bytes)
        payload = {
            "policy_number": "POL-991234",
            "vehicle_type": "Car",
            "claim_amount": 75000.0,
            "description": "Front collision sustained scraping and cracked windshield.",
            "uploaded_image": mock_file
        }

        result = self.service.submit_claim_request(payload)
        
        # Verify result dictionary
        self.assertEqual(result["status"], "Submitted")
        self.assertIn("gemini_analysis", result)
        self.assertEqual(result["gemini_analysis"]["damage_severity"], "High")
        self.assertEqual(result["gemini_analysis"]["damage_type"], "Windshield")

        # Verify DB Serialization
        user = self.session.query(User).filter(User.email == "customer@acko.com").first()
        self.assertIsNotNone(user)
        db_claim = self.session.query(Claim).filter(Claim.user_id == user.id).first()
        self.assertIsNotNone(db_claim)
        self.assertEqual(db_claim.gemini_analysis_json["damage_severity"], "High")

        uploaded = self.session.query(UploadedImage).filter(UploadedImage.claim_id == db_claim.id).first()
        self.assertIsNotNone(uploaded)
        self.assertEqual(uploaded.original_filename, "front_dent.jpg")
        self.assertTrue(os.path.exists(uploaded.local_path))

    @patch("src.modules.claims.services.analyze_damage_image")
    def test_fallback_behavior(self, mock_analyze: MagicMock) -> None:
        """Asserts pipeline falls back gracefully when Gemini Vision raises exceptions."""
        mock_analyze.side_effect = Exception("Gemini server error")

        mock_file = MockUploadedFile("crash.jpg", self.valid_image_bytes)
        payload = {
            "policy_number": "POL-991234",
            "vehicle_type": "Car",
            "claim_amount": 120000.0,
            "description": "Severe front collision including windshield damage.",
            "uploaded_image": mock_file
        }

        # Should execute without raising visual exceptions
        result = self.service.submit_claim_request(payload)
        self.assertIn("gemini_analysis", result)
        analysis = result["gemini_analysis"]
        self.assertEqual(analysis["damage_severity"], "High")  # from description severe indicator
        self.assertEqual(analysis["damage_type"], "Windshield")  # from description windshield indicator
        self.assertTrue(analysis["natural_language_assessment"].startswith("⚠️ [Vision Fallback Mode]"))

"""
Unit test suite verifying Business Service Layer dependencies, validation rules,
custom exceptions, and transactional logic.
"""

import unittest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.base import Base
from src.models import (
    User,
    Policy,
    Quotation,
    Claim,
    ChatSession,
    ChatMessage,
    PredictionLog,
    UploadedImage,
)
from src.repositories import (
    UserRepository,
    PolicyRepository,
    QuotationRepository,
    ClaimRepository,
    ChatRepository,
    PredictionRepository,
    UploadedImageRepository,
)
from src.services import (
    UserService,
    PolicyService,
    QuotationService,
    ClaimService,
    ChatService,
    PredictionService,
    ImageService,
    ValidationError,
    ResourceNotFoundError,
    DuplicateResourceError,
    BusinessRuleViolationError,
)


class TestServicesSuite(unittest.TestCase):
    """
    Test suite targeting the corporate business operations in service modules.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, expire_on_commit=False)

    def setUp(self) -> None:
        self.session: Session = self.SessionLocal()
        
        # Instantiate repositories
        self.user_repo = UserRepository(self.session)
        self.policy_repo = PolicyRepository(self.session)
        self.quote_repo = QuotationRepository(self.session)
        self.claim_repo = ClaimRepository(self.session)
        self.chat_repo = ChatRepository(self.session)
        self.pred_repo = PredictionRepository(self.session)
        self.image_repo = UploadedImageRepository(self.session)

        # Instantiate services (Dependency Injection)
        self.user_service = UserService(self.user_repo)
        self.policy_service = PolicyService(self.policy_repo, self.user_repo)
        self.quote_service = QuotationService(self.quote_repo, self.user_repo)
        self.claim_service = ClaimService(self.claim_repo, self.policy_repo, self.user_repo)
        self.chat_service = ChatService(self.chat_repo, self.user_repo)
        self.pred_service = PredictionService(self.pred_repo)
        self.image_service = ImageService(self.image_repo, self.claim_repo)

    def tearDown(self) -> None:
        self.session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            self.session.execute(table.delete())
        self.session.commit()
        self.session.close()

    def test_user_service_registration_validation_and_lookup(self) -> None:
        """
        Verify registration inputs, email validation, role restrictions, and duplicate checks.
        """
        # Register a valid user
        user = self.user_service.register_user(
            full_name="Alice Vance",
            email="alice@vance.com",
            phone_number="+919900000000",
            role="customer"
        )
        self.assertIsNotNone(user.id)
        self.assertEqual(user.full_name, "Alice Vance")

        # Input validation: Empty name
        with self.assertRaises(ValidationError):
            self.user_service.register_user(full_name="", email="test@vance.com")

        # Input validation: Malformed email
        with self.assertRaises(ValidationError):
            self.user_service.register_user(full_name="Test", email="test_vance.com")

        # Input validation: Invalid system role
        with self.assertRaises(ValidationError):
            self.user_service.register_user(full_name="Test", email="test@vance.com", role="master")

        # Business validation: Email duplication
        with self.assertRaises(DuplicateResourceError):
            self.user_service.register_user(full_name="Alice Two", email="alice@vance.com")

        # Lookups
        fetched_by_id = self.user_service.get_user_by_id(user.id)
        self.assertEqual(fetched_by_id.email, "alice@vance.com")

        fetched_by_email = self.user_service.get_user_by_email("alice@vance.com")
        self.assertEqual(fetched_by_email.id, user.id)

        # Lookups: Not found errors
        with self.assertRaises(ResourceNotFoundError):
            self.user_service.get_user_by_id(uuid.uuid4())

        with self.assertRaises(ResourceNotFoundError):
            self.user_service.get_user_by_email("missing@vance.com")

    def test_policy_service_creation_validation_and_active_check(self) -> None:
        """
        Verify policy generation checks user existence, enforces positive IDV/premium bounds,
        and validates active statuses.
        """
        user = self.user_service.register_user(
            full_name="Policy Bob",
            email="bob@vance.com"
        )

        start = datetime.utcnow()
        end = start + timedelta(days=365)

        # Non-existent user reference
        with self.assertRaises(ResourceNotFoundError):
            self.policy_service.create_policy(
                user_id=uuid.uuid4(),
                policy_number="ACKO-111",
                vehicle_type="car",
                vehicle_make="Ford",
                vehicle_model="Mustang",
                registration_number="MH-02-EE-1234",
                idv=500000.0,
                premium=12000.0,
                policy_type="comprehensive",
                coverage_type="own_damage",
                policy_start_date=start,
                policy_end_date=end
            )

        # Negative IDV/Premium validation
        with self.assertRaises(ValidationError):
            self.policy_service.create_policy(
                user_id=user.id,
                policy_number="ACKO-111",
                vehicle_type="car",
                vehicle_make="Ford",
                vehicle_model="Mustang",
                registration_number="MH-02-EE-1234",
                idv=-100.0,
                premium=12000.0,
                policy_type="comprehensive",
                coverage_type="own_damage",
                policy_start_date=start,
                policy_end_date=end
            )

        # Date window validations: start >= end
        with self.assertRaises(ValidationError):
            self.policy_service.create_policy(
                user_id=user.id,
                policy_number="ACKO-111",
                vehicle_type="car",
                vehicle_make="Ford",
                vehicle_model="Mustang",
                registration_number="MH-02-EE-1234",
                idv=500000.0,
                premium=12000.0,
                policy_type="comprehensive",
                coverage_type="own_damage",
                policy_start_date=start,
                policy_end_date=start - timedelta(days=1)
            )

        # Valid create
        policy = self.policy_service.create_policy(
            user_id=user.id,
            policy_number="ACKO-POL-VALID",
            vehicle_type="car",
            vehicle_make="Ford",
            vehicle_model="Mustang",
            registration_number="MH-02-EE-1234",
            idv=500000.0,
            premium=12000.0,
            policy_type="comprehensive",
            coverage_type="own_damage",
            policy_start_date=start,
            policy_end_date=end
        )
        self.assertIsNotNone(policy.id)

        # Duplicate policy entry
        with self.assertRaises(DuplicateResourceError):
            self.policy_service.create_policy(
                user_id=user.id,
                policy_number="ACKO-POL-VALID",
                vehicle_type="car",
                vehicle_make="Ford",
                vehicle_model="Mustang",
                registration_number="MH-02-EE-1234",
                idv=500000.0,
                premium=12000.0,
                policy_type="comprehensive",
                coverage_type="own_damage",
                policy_start_date=start,
                policy_end_date=end
            )

        # Active evaluation: current date is in boundaries
        self.assertTrue(self.policy_service.validate_policy_active(policy.id))

        # Active evaluation: policy is elapsed (updates to expired status)
        past_policy = self.policy_service.create_policy(
            user_id=user.id,
            policy_number="ACKO-POL-EXPIRED",
            vehicle_type="car",
            vehicle_make="Ford",
            vehicle_model="Escape",
            registration_number="MH-02-EE-5678",
            idv=300000.0,
            premium=8000.0,
            policy_type="comprehensive",
            coverage_type="own_damage",
            policy_start_date=datetime.utcnow() - timedelta(days=10),
            policy_end_date=datetime.utcnow() - timedelta(days=2)
        )
        self.assertFalse(self.policy_service.validate_policy_active(past_policy.id))
        
        # Verify status updated
        refreshed = self.policy_service.get_policy_by_id(past_policy.id)
        self.assertEqual(refreshed.status, "expired")

    def test_quotation_service_persistence_and_latest(self) -> None:
        """
        Verify premium quotation inputs constraints, and user quotations retrieval.
        """
        user = self.user_service.register_user(full_name="Quotation Dave", email="dave@vance.com")

        # Validation: Negative premium value
        with self.assertRaises(ValidationError):
            self.quote_service.create_quotation(
                user_id=user.id,
                quotation_type="car_premium",
                vehicle_type="car",
                input_json={"age": 2},
                predicted_premium=-500.0,
                model_version="1.0"
            )

        # Valid create
        quote = self.quote_service.create_quotation(
            user_id=user.id,
            quotation_type="car_premium",
            vehicle_type="car",
            input_json={"age": 2},
            predicted_premium=4500.0,
            model_version="1.0"
        )
        self.assertIsNotNone(quote.id)

        # Retrieval: latest quotation
        latest = self.quote_service.get_latest_quotation_by_user(user.id)
        self.assertEqual(latest.predicted_premium, 4500.0)

        # Retrieval: no quotation exceptions
        user_empty = self.user_service.register_user(full_name="Empty Quoter", email="empty@vance.com")
        with self.assertRaises(ResourceNotFoundError):
            self.quote_service.get_latest_quotation_by_user(user_empty.id)

    def test_claim_service_submission_status_updates_and_idv_limit(self) -> None:
        """
        Verifies policy limits checks user existence, validates that filing claims
        against inactive policies fails, and checks status workflow changes.
        """
        user = self.user_service.register_user(full_name="Claimant Charlie", email="charlie@vance.com")
        
        start = datetime.utcnow()
        end = start + timedelta(days=365)
        
        policy = self.policy_service.create_policy(
            user_id=user.id,
            policy_number="ACKO-POL-LIMITS",
            vehicle_type="bike",
            vehicle_make="Honda",
            vehicle_model="Unicorn",
            registration_number="MH-12-GG-1111",
            idv=100000.0,
            premium=2500.0,
            policy_type="third_party",
            coverage_type="third_party_only",
            policy_start_date=start,
            policy_end_date=end
        )

        # Validation: Claim amount <= 0
        with self.assertRaises(ValidationError):
            self.claim_service.submit_claim(
                policy_id=policy.id,
                user_id=user.id,
                claim_amount=0.0,
                damage_summary="Accident"
            )

        # Business validation: Claim amount exceeding Policy IDV cap
        with self.assertRaises(BusinessRuleViolationError):
            self.claim_service.submit_claim(
                policy_id=policy.id,
                user_id=user.id,
                claim_amount=150000.0,  # Limits Cap exceeded (IDV=100000)
                damage_summary="Total loss damage."
            )

        # Submit valid claim
        claim = self.claim_service.submit_claim(
            policy_id=policy.id,
            user_id=user.id,
            claim_amount=30000.0,
            damage_summary="Side scrapes.",
            gemini_analysis_json={"severity": "medium"},
            predicted_decision="approved",
            approval_probability=0.85
        )
        self.assertIsNotNone(claim.id)
        self.assertEqual(claim.claim_status, "pending")
        self.assertIsNone(claim.decided_at)

        # Business validation: claim on inactive status policy
        inactive_policy = self.policy_service.create_policy(
            user_id=user.id,
            policy_number="ACKO-POL-INACTIVE",
            vehicle_type="bike",
            vehicle_make="Honda",
            vehicle_model="Dio",
            registration_number="MH-12-GG-2222",
            idv=50000.0,
            premium=1500.0,
            policy_type="third_party",
            coverage_type="third_party_only",
            policy_start_date=start,
            policy_end_date=end,
            status="lapsed"
        )
        with self.assertRaises(BusinessRuleViolationError):
            self.claim_service.submit_claim(
                policy_id=inactive_policy.id,
                user_id=user.id,
                claim_amount=20000.0,
                damage_summary="Crashed."
            )

        # Claim status update logic: Valid state transition
        resolved = self.claim_service.update_claim_status(claim.id, "approved")
        self.assertEqual(resolved.claim_status, "approved")
        self.assertIsNotNone(resolved.decided_at)

        # Claim status update logic: Invalid state option transition
        with self.assertRaises(ValidationError):
            self.claim_service.update_claim_status(claim.id, "revised")

    def test_chat_service_session_and_message_management(self) -> None:
        """
        Verify chat session initialization features and chronological message feeds.
        """
        user = self.user_service.register_user(full_name="Chatter Alice", email="chatter@vance.com")

        # Session title validation
        with self.assertRaises(ValidationError):
            self.chat_service.create_session(user_id=user.id, title="")

        # Create session
        session = self.chat_service.create_session(user_id=user.id, title="Billing query")
        self.assertIsNotNone(session.id)

        # Append messages
        msg_u = self.chat_service.add_message(
            session_id=session.id,
            role="user",
            message="Why was I charged twice?"
        )
        msg_a = self.chat_service.add_message(
            session_id=session.id,
            role="assistant",
            message="We will review your transaction ledger.",
            gemini_response="Refined LLM reply"
        )
        self.assertEqual(msg_u.role, "user")
        self.assertEqual(msg_a.role, "assistant")

        # Verify invalid chat message parameters
        with self.assertRaises(ValidationError):
            self.chat_service.add_message(session_id=session.id, role="user", message="")

        with self.assertRaises(ValidationError):
            self.chat_service.add_message(session_id=session.id, role="captain", message="hey")

        # Retrieve session message feeds
        feed = self.chat_service.get_session_messages(session.id)
        self.assertEqual(len(feed), 2)
        self.assertEqual(feed[0].message, "Why was I charged twice?")
        self.assertEqual(feed[1].message, "We will review your transaction ledger.")

    def test_prediction_service_logging_and_telemetry(self) -> None:
        """
        Verify prediction logging and average latency tracking operations.
        """
        # Validation: Negative latency value
        with self.assertRaises(ValidationError):
            self.pred_service.log_prediction(
                prediction_type="claims_fraud",
                model_version="1.0.0",
                latency_ms=-50,
                input_hash="hash_in",
                output_hash="hash_out"
            )

        # Valid create
        self.pred_service.log_prediction(
            prediction_type="claims_fraud",
            model_version="1.0.0",
            latency_ms=150,
            input_hash="hash_in1",
            output_hash="hash_out1"
        )
        self.pred_service.log_prediction(
            prediction_type="claims_fraud",
            model_version="1.0.0",
            latency_ms=250,
            input_hash="hash_in2",
            output_hash="hash_out2"
        )

        # Latency statistics
        avg = self.pred_service.get_average_latency_by_type("claims_fraud")
        self.assertEqual(avg, 200.0)

    def test_image_service_attachments(self) -> None:
        """
        Verify image link integrity audits and deleted files metadata.
        """
        user = self.user_service.register_user(full_name="Img User", email="img@vance.com")
        
        start = datetime.utcnow()
        end = start + timedelta(days=365)
        
        policy = self.policy_service.create_policy(
            user_id=user.id,
            policy_number="ACKO-POL-IMG",
            vehicle_type="car",
            vehicle_make="Honda",
            vehicle_model="City",
            registration_number="MH-12-GG-3333",
            idv=400000.0,
            premium=10000.0,
            policy_type="comprehensive",
            coverage_type="own_damage",
            policy_start_date=start,
            policy_end_date=end
        )
        
        claim = self.claim_service.submit_claim(
            policy_id=policy.id,
            user_id=user.id,
            claim_amount=20000.0,
            damage_summary="Shattered windshield"
        )

        # Inexistent Claim association
        with self.assertRaises(ResourceNotFoundError):
            self.image_service.register_image(
                claim_id=uuid.uuid4(),
                original_filename="windshield.jpg",
                local_path="/local/path/windshield.jpg"
            )

        # Register valid image
        img = self.image_service.register_image(
            claim_id=claim.id,
            original_filename="windshield.jpg",
            local_path="/local/path/windshield.jpg",
            s3_key="s3://windshield.jpg"
        )
        self.assertIsNotNone(img.id)

        # List images by claim
        list_imgs = self.image_service.get_claim_images(claim.id)
        self.assertEqual(len(list_imgs), 1)

        # Delete image
        success = self.image_service.delete_image(img.id)
        self.assertTrue(success)
        self.assertEqual(len(self.image_service.get_claim_images(claim.id)), 0)


if __name__ == "__main__":
    unittest.main()

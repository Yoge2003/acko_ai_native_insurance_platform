"""
Unit test suite verifying the correctness, transactions, rollback scenarios, pagination,
filtering, search, relations, and bulk operations of the repository layer.
"""

import unittest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

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


class TestRepositoriesSuite(unittest.TestCase):
    """
    Test suite targeting the generic BaseRepository and domain-specific repository classes.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # Isolated SQLite in-memory database database for unit tests
        cls.engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, expire_on_commit=False)

    def setUp(self) -> None:
        self.session: Session = self.SessionLocal()
        # Initialize all repositories with database transaction session
        self.user_repo = UserRepository(self.session)
        self.policy_repo = PolicyRepository(self.session)
        self.quote_repo = QuotationRepository(self.session)
        self.claim_repo = ClaimRepository(self.session)
        self.chat_repo = ChatRepository(self.session)
        self.pred_repo = PredictionRepository(self.session)
        self.image_repo = UploadedImageRepository(self.session)

    def tearDown(self) -> None:
        self.session.rollback()
        # Clean up database tables data between runs
        for table in reversed(Base.metadata.sorted_tables):
            self.session.execute(table.delete())
        self.session.commit()
        self.session.close()

    def test_user_repository_crud_search_pagination(self) -> None:
        """
        Verifies CRUD operations, search, pagination, count, and exists.
        """
        # 1. Exist checks (empty)
        self.assertFalse(self.user_repo.exists(email="alice@example.com"))
        self.assertEqual(self.user_repo.count(), 0)

        # 2. CRUD: Create
        user1 = User(
            full_name="Alice Smith",
            email="alice@example.com",
            phone_number="+1234567890",
            role="customer"
        )
        saved_user1 = self.user_repo.create(user1)
        self.assertIsNotNone(saved_user1.id)
        self.assertEqual(self.user_repo.count(), 1)
        self.assertTrue(self.user_repo.exists(email="alice@example.com"))

        # CRUD: Get by ID
        fetched = self.user_repo.get_by_id(saved_user1.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.full_name, "Alice Smith")

        # 3. Pagination & Sort
        # Add another user
        user2 = User(
            full_name="Bob Jones",
            email="bob@example.com",
            phone_number="+1987654321",
            role="customer"
        )
        self.user_repo.create(user2)
        
        # Paginate
        items, total = self.user_repo.paginate(page=1, per_page=1, sort_by="full_name", sort_desc=True)
        self.assertEqual(total, 2)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].full_name, "Bob Jones")  # Descending order ("Bob" comes after "Alice")

        # 4. Search
        search_res = self.user_repo.search("Smith", ["full_name", "email"])
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0].email, "alice@example.com")

        # 5. CRUD: Update
        fetched.full_name = "Alice Jones"
        updated = self.user_repo.update(fetched, {"full_name": "Alice Jones"})
        self.assertEqual(updated.full_name, "Alice Jones")

        # 6. Domain-specific methods
        by_email = self.user_repo.get_by_email("bob@example.com")
        self.assertIsNotNone(by_email)
        self.assertEqual(by_email.full_name, "Bob Jones")

        by_role = self.user_repo.get_by_role("customer")
        self.assertEqual(len(by_role), 2)

        # 7. CRUD: Delete
        success = self.user_repo.delete(saved_user1.id)
        self.assertTrue(success)
        self.assertEqual(self.user_repo.count(), 1)
        self.assertIsNone(self.user_repo.get_by_id(saved_user1.id))

    def test_policy_repository_custom_domain(self) -> None:
        """
        Verifies policy number keys, user policies retrieval, and active filters.
        """
        user = User(full_name="Holder", email="holder@example.com")
        self.user_repo.create(user)

        start = datetime.utcnow()
        end = start + timedelta(days=30)

        p1 = Policy(
            policy_number="ACKO-100",
            user_id=user.id,
            vehicle_type="car",
            vehicle_make="Tata",
            vehicle_model="Nexon",
            registration_number="KA-01-AB-1234",
            idv=800000.0,
            premium=15000.0,
            policy_type="comprehensive",
            coverage_type="own_damage",
            policy_start_date=start,
            policy_end_date=end,
            status="active"
        )
        p2 = Policy(
            policy_number="ACKO-200",
            user_id=user.id,
            vehicle_type="car",
            vehicle_make="Tata",
            vehicle_model="Harrier",
            registration_number="KA-01-AB-5678",
            idv=1200000.0,
            premium=25000.0,
            policy_type="comprehensive",
            coverage_type="own_damage",
            policy_start_date=start,
            policy_end_date=end,
            status="expired"
        )
        self.policy_repo.create(p1)
        self.policy_repo.create(p2)

        # Test policy number query
        fetched_p1 = self.policy_repo.get_by_policy_number("ACKO-100")
        self.assertIsNotNone(fetched_p1)
        self.assertEqual(fetched_p1.vehicle_model, "Nexon")

        # Test user owned policies
        user_policies = self.policy_repo.get_by_user_id(user.id)
        self.assertEqual(len(user_policies), 2)

        # Test active status query
        active_policies = self.policy_repo.get_active_policies_by_user(user.id)
        self.assertEqual(len(active_policies), 1)
        self.assertEqual(active_policies[0].policy_number, "ACKO-100")

    def test_quotation_repository_custom_domain(self) -> None:
        """
        Verifies quotation creation and retrieving latest generated quotes.
        """
        user = User(full_name="Quotation Maker", email="quotemaker@example.com")
        self.user_repo.create(user)

        q1 = Quotation(
            user_id=user.id,
            quotation_type="car_premium",
            vehicle_type="car",
            input_json={"age": 3},
            predicted_premium=8500.0,
            model_version="1.0.0",
            prediction_timestamp=datetime.utcnow() - timedelta(minutes=10)
        )
        q2 = Quotation(
            user_id=user.id,
            quotation_type="car_premium",
            vehicle_type="car",
            input_json={"age": 1},
            predicted_premium=12000.0,
            model_version="1.0.0",
            prediction_timestamp=datetime.utcnow()
        )
        self.quote_repo.create(q1)
        self.quote_repo.create(q2)

        # Fetch all quotations for user
        quotes = self.quote_repo.get_by_user_id(user.id)
        self.assertEqual(len(quotes), 2)

        # Fetch latest quotation
        latest = self.quote_repo.get_latest_quotation(user.id)
        self.assertIsNotNone(latest)
        self.assertEqual(latest.predicted_premium, 12000.0)

    def test_claim_repository_custom_domain(self) -> None:
        """
        Verifies claim filters, status tracking, and aggregate calculations.
        """
        user = User(full_name="Claimant", email="claimant@example.com")
        self.user_repo.create(user)

        p = Policy(
            policy_number="ACKO-CLAIM-POL",
            user_id=user.id,
            vehicle_type="bike",
            vehicle_make="Yamaha",
            vehicle_model="R15",
            registration_number="MH-12-FG-7890",
            idv=120000.0,
            premium=3000.0,
            policy_type="third_party",
            coverage_type="third_party_only",
            policy_start_date=datetime.utcnow(),
            policy_end_date=datetime.utcnow() + timedelta(days=365)
        )
        self.policy_repo.create(p)

        c1 = Claim(
            policy_id=p.id,
            user_id=user.id,
            claim_amount=15000.0,
            damage_summary="Rear indicator guard damage.",
            claim_status="approved"
        )
        c2 = Claim(
            policy_id=p.id,
            user_id=user.id,
            claim_amount=5000.0,
            damage_summary="Mirror cracked.",
            claim_status="pending"
        )
        self.claim_repo.create(c1)
        self.claim_repo.create(c2)

        # Test user claims
        user_claims = self.claim_repo.get_by_user_id(user.id)
        self.assertEqual(len(user_claims), 2)

        # Test policy claims
        policy_claims = self.claim_repo.get_by_policy_id(p.id)
        self.assertEqual(len(policy_claims), 2)

        # Test get by status
        approved_claims = self.claim_repo.get_claims_by_status("approved")
        self.assertEqual(len(approved_claims), 1)
        self.assertEqual(approved_claims[0].claim_amount, 15000.0)

        # Test aggregate claim amount
        total_amount = self.claim_repo.get_total_claimed_amount(user.id)
        self.assertEqual(total_amount, 20000.0)

    def test_chat_repository_custom_domain(self) -> None:
        """
        Verifies session persistence and chat message storage inside a session.
        """
        user = User(full_name="Chater", email="chater@example.com")
        self.user_repo.create(user)

        session = ChatSession(user_id=user.id, title="How to claim?")
        self.chat_repo.create(session)

        # Test get chat sessions
        sessions = self.chat_repo.get_sessions_by_user(user.id)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].title, "How to claim?")

        # Add messages
        msg1 = self.chat_repo.create_message(
            session_id=session.id,
            role="user",
            message="I crashed my bike."
        )
        msg2 = self.chat_repo.create_message(
            session_id=session.id,
            role="assistant",
            message="We can guide you to file a claim. Is anyone injured?",
            gemini_response="Structured guidance response"
        )

        self.assertIsNotNone(msg1.id)
        self.assertIsNotNone(msg2.id)

        # Retrieve messages
        messages = self.chat_repo.get_messages_by_session(session.id)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[1].gemini_response, "Structured guidance response")

    def test_prediction_repository_custom_domain_bulk(self) -> None:
        """
        Verifies PredictionLogs filters, bulk insertion, and aggregated latency calculation.
        """
        log1 = PredictionLog(
            prediction_type="premium_estimator",
            model_version="1.0.0",
            latency_ms=120,
            input_hash="hash1",
            output_hash="hash2"
        )
        log2 = PredictionLog(
            prediction_type="premium_estimator",
            model_version="1.0.0",
            latency_ms=80,
            input_hash="hash3",
            output_hash="hash4"
        )
        log3 = PredictionLog(
            prediction_type="fraud_checker",
            model_version="2.1.0",
            latency_ms=250,
            input_hash="hash5",
            output_hash="hash6"
        )

        # Test Bulk Insert
        logs = self.pred_repo.bulk_insert([log1, log2, log3])
        self.assertEqual(len(logs), 3)
        self.assertIsNotNone(logs[0].id)

        # Retrieve by type
        estimators = self.pred_repo.get_logs_by_type("premium_estimator")
        self.assertEqual(len(estimators), 2)

        # Calculate average latency
        avg_est = self.pred_repo.get_average_latency("premium_estimator")
        self.assertEqual(avg_est, 100.0)  # (120 + 80) / 2 = 100.0

        avg_fraud = self.pred_repo.get_average_latency("fraud_checker")
        self.assertEqual(avg_fraud, 250.0)

        # Test non-existent type average latency
        self.assertEqual(self.pred_repo.get_average_latency("unknown"), 0.0)

    def test_uploaded_image_repository_custom_domain(self) -> None:
        """
        Verifies image upload records links to claim.
        """
        user = User(full_name="Uploader", email="uploader@example.com")
        self.user_repo.create(user)

        p = Policy(
            policy_number="ACKO-IMG-POL",
            user_id=user.id,
            vehicle_type="car",
            vehicle_make="Audi",
            vehicle_model="A4",
            registration_number="MH-12-GG-9999",
            idv=2000000.0,
            premium=80000.0,
            policy_type="comprehensive",
            coverage_type="own_damage",
            policy_start_date=datetime.utcnow(),
            policy_end_date=datetime.utcnow() + timedelta(days=365)
        )
        self.policy_repo.create(p)

        claim = Claim(
            policy_id=p.id,
            user_id=user.id,
            claim_amount=50000.0,
            damage_summary="Door scrape."
        )
        self.claim_repo.create(claim)

        img = UploadedImage(
            claim_id=claim.id,
            original_filename="door.jpg",
            local_path="/path/to/door.jpg",
            s3_key="s3://door.jpg"
        )
        self.image_repo.create(img)

        # Query
        claim_imgs = self.image_repo.get_images_by_claim(claim.id)
        self.assertEqual(len(claim_imgs), 1)
        self.assertEqual(claim_imgs[0].original_filename, "door.jpg")

    def test_transaction_rollback_on_integrity_violation(self) -> None:
        """
        Verifies transaction safety: failing writes trigger repository rollbacks
        allowing the DB session to continue making subsequent valid operations.
        """
        # Save a valid user
        u1 = User(full_name="Valid User", email="unique@example.com")
        self.user_repo.create(u1)

        # Create duplicate email user (expected to fail)
        u2 = User(full_name="Duplicate User", email="unique@example.com")
        
        with self.assertRaises(IntegrityError):
            self.user_repo.create(u2)

        # The repository should have automatically rolled back the transaction.
        # Now verify we can perform a new operation without "InvalidRequestError" due to a failed transaction state.
        u3 = User(full_name="Another User", email="another@example.com")
        saved_u3 = self.user_repo.create(u3)
        self.assertIsNotNone(saved_u3.id)
        self.assertEqual(self.user_repo.get_by_email("another@example.com").full_name, "Another User")


if __name__ == "__main__":
    unittest.main()

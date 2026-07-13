import unittest
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
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


class TestDatabaseModels(unittest.TestCase):
    """
    Unit test suite verifying the correctness of SQLAlchemy 2.x ORM models,
    relationships, unique constraints, foreign keys, and cascade deletes.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # Use an in-memory SQLite db for fast, isolated, and environment-independent unit tests
        cls.engine = create_engine("sqlite:///:memory:", future=True)
        # Import all models to ensure they register on Base.metadata
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, expire_on_commit=False)

    def setUp(self) -> None:
        self.session: Session = self.SessionLocal()

    def tearDown(self) -> None:
        self.session.rollback()
        # Clean up database tables data between runs
        for table in reversed(Base.metadata.sorted_tables):
            self.session.execute(table.delete())
        self.session.commit()
        self.session.close()

    def test_metadata_tables_exist(self) -> None:
        """
        Verify that all requested enterprise database tables are registered and created.
        """
        table_names = Base.metadata.tables.keys()
        expected_tables = {
            "users",
            "policies",
            "quotations",
            "claims",
            "chat_sessions",
            "chat_messages",
            "prediction_logs",
            "uploaded_images",
        }
        for table in expected_tables:
            self.assertIn(table, table_names, f"Table {table} is missing from metadata registrations.")

    def test_user_creation_and_fields(self) -> None:
        """
        Tests User ORM model insertion, UUID auto-generation, and basic fields.
        """
        user = User(
            full_name="Jane Doe",
            email="jane.doe@example.com",
            phone_number="+919876543210",
            role="customer"
        )
        self.session.add(user)
        self.session.commit()

        # Check default UUID and timestamps are populated
        self.assertIsNotNone(user.id)
        self.assertIsInstance(user.id, uuid.UUID)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertEqual(user.full_name, "Jane Doe")
        self.assertEqual(user.email, "jane.doe@example.com")
        self.assertEqual(user.role, "customer")

    def test_user_email_uniqueness(self) -> None:
        """
        Verify that adding users with duplicate emails violates unique constraints.
        """
        user1 = User(full_name="User One", email="unique@example.com")
        user2 = User(full_name="User Two", email="unique@example.com")
        self.session.add(user1)
        self.session.commit()

        self.session.add(user2)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_policy_creation_and_relationships(self) -> None:
        """
        Tests Policy generation, foreign key mapping, and User bidirectional relationship.
        """
        user = User(full_name="Policy Holder", email="policy.holder@example.com")
        self.session.add(user)
        self.session.commit()

        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=365)

        policy = Policy(
            policy_number="ACKO-POL-847294",
            user_id=user.id,
            vehicle_type="bike",
            vehicle_make="Royal Enfield",
            vehicle_model="Classic 350",
            registration_number="KA-05-MM-1234",
            idv=150000.0,
            premium=4500.0,
            policy_type="comprehensive",
            coverage_type="own_damage_third_party",
            policy_start_date=start_date,
            policy_end_date=end_date,
            status="active"
        )
        self.session.add(policy)
        self.session.commit()

        # Reload
        self.session.refresh(policy)
        self.session.refresh(user)

        self.assertIsNotNone(policy.id)
        self.assertEqual(policy.user.id, user.id)
        self.assertIn(policy, user.policies)
        self.assertEqual(len(user.policies), 1)

    def test_policy_number_uniqueness(self) -> None:
        """
        Verify policy number uniqueness constraint.
        """
        u = User(full_name="Tester", email="test@example.com")
        self.session.add(u)
        self.session.commit()

        p1 = Policy(
            policy_number="DUPLICATE-123",
            user_id=u.id,
            vehicle_type="bike", vehicle_make="A", vehicle_model="B", registration_number="C",
            idv=10.0, premium=1.0, policy_type="X", coverage_type="Y",
            policy_start_date=datetime.utcnow(), policy_end_date=datetime.utcnow()
        )
        p2 = Policy(
            policy_number="DUPLICATE-123",
            user_id=u.id,
            vehicle_type="bike", vehicle_make="A", vehicle_model="B", registration_number="C",
            idv=10.0, premium=1.0, policy_type="X", coverage_type="Y",
            policy_start_date=datetime.utcnow(), policy_end_date=datetime.utcnow()
        )
        self.session.add(p1)
        self.session.commit()

        self.session.add(p2)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_quotation_creation_and_fields(self) -> None:
        """
        Test Quotation ORM fields and JSON parsing capability.
        """
        u = User(full_name="Quoter", email="quoter@example.com")
        self.session.add(u)
        self.session.commit()

        input_data = {
            "vehicle_age_years": 2,
            "previous_claims": False,
            "owner_age": 28
        }
        quotation = Quotation(
            user_id=u.id,
            quotation_type="bike_premium",
            vehicle_type="bike",
            input_json=input_data,
            predicted_premium=3200.50,
            model_version="1.0.4"
        )
        self.session.add(quotation)
        self.session.commit()

        self.assertIsNotNone(quotation.id)
        self.assertEqual(quotation.input_json["owner_age"], 28)
        self.assertEqual(quotation.user.email, "quoter@example.com")
        self.assertIn(quotation, u.quotations)

    def test_claim_and_image_relationships(self) -> None:
        """
        Test Claim, prediction decision attributes, Gemini Analysis JSON,
        and cascade deletion of UploadedImages upon Claim deletion.
        """
        u = User(full_name="Claimant", email="claimant@example.com")
        self.session.add(u)
        self.session.commit()

        p = Policy(
            policy_number="POL-CLAIM-TEST",
            user_id=u.id,
            vehicle_type="car", vehicle_make="Maruti Suzuki", vehicle_model="Swift", registration_number="KA-03-N-9999",
            idv=500000.0, premium=12000.0, policy_type="comprehensive", coverage_type="own_damage",
            policy_start_date=datetime.utcnow(), policy_end_date=datetime.utcnow()
        )
        self.session.add(p)
        self.session.commit()

        claim = Claim(
            policy_id=p.id,
            user_id=u.id,
            claim_amount=45000.0,
            damage_summary="Front bumper shattered due to collision with a pillar.",
            gemini_analysis_json={"identified_damage": ["front_bumper"], "estimated_severity": "low"},
            predicted_decision="approved",
            approval_probability=0.92,
            claim_status="pending"
        )
        self.session.add(claim)
        self.session.commit()

        img = UploadedImage(
            claim_id=claim.id,
            original_filename="scratch_front.jpg",
            local_path="/uploads/images/scratch_front.jpg",
            s3_key="claims/scratch_front.jpg"
        )
        self.session.add(img)
        self.session.commit()

        # Check bidirectional relationships
        self.assertEqual(claim.user.id, u.id)
        self.assertEqual(claim.policy.id, p.id)
        self.assertIn(claim, u.claims)
        self.assertIn(claim, p.claims)
        
        self.assertEqual(len(claim.uploaded_images), 1)
        self.assertEqual(claim.uploaded_images[0].claim.id, claim.id)
        self.assertEqual(claim.uploaded_images[0].original_filename, "scratch_front.jpg")

        # Test Cascade Delete: Deleting claim should delete uploaded images
        self.session.delete(claim)
        self.session.commit()

        db_img = self.session.query(UploadedImage).filter_by(id=img.id).first()
        self.assertIsNone(db_img)

    def test_user_cascade_deletes_everything(self) -> None:
        """
        Verify that deleting a User deletes all their Policies, Chat Sessions, Quotations and Claims.
        """
        u = User(full_name="Cascade Target", email="cascade@example.com")
        self.session.add(u)
        self.session.commit()

        p = Policy(
            policy_number="POL-CASC",
            user_id=u.id,
            vehicle_type="car", vehicle_make="A", vehicle_model="B", registration_number="C",
            idv=10.0, premium=1.0, policy_type="X", coverage_type="Y",
            policy_start_date=datetime.utcnow(), policy_end_date=datetime.utcnow()
        )
        q = Quotation(
            user_id=u.id,
            quotation_type="car_premium",
            vehicle_type="car",
            input_json={},
            predicted_premium=100.0,
            model_version="1.0"
        )
        cs = ChatSession(
            user_id=u.id,
            title="Policy Inquiry"
        )
        self.session.add_all([p, q, cs])
        self.session.commit()

        c = Claim(
            policy_id=p.id,
            user_id=u.id,
            claim_amount=50.0,
            damage_summary="test",
            gemini_analysis_json=None,
            predicted_decision="approved",
            approval_probability=0.8,
            claim_status="pending"
        )
        self.session.add(c)
        self.session.commit()

        # Deleting the user should trigger cascade deletes down the line
        self.session.delete(u)
        self.session.commit()

        self.assertIsNone(self.session.query(Policy).filter_by(id=p.id).first())
        self.assertIsNone(self.session.query(Quotation).filter_by(id=q.id).first())
        self.assertIsNone(self.session.query(ChatSession).filter_by(id=cs.id).first())
        self.assertIsNone(self.session.query(Claim).filter_by(id=c.id).first())

    def test_chat_session_and_messages(self) -> None:
        """
        Test ChatSession bidirectional relationships, and ChatMessages cascades.
        """
        u = User(full_name="Chater", email="chater@example.com")
        self.session.add(u)
        self.session.commit()

        session = ChatSession(user_id=u.id, title="Support Conversation")
        self.session.add(session)
        self.session.commit()

        msg = ChatMessage(
            session_id=session.id,
            role="user",
            message="What features are included in premium?",
            retrieved_sources=[{"doc_id": "doc_45", "chunk": "Standard policies include road side assistance."}],
            gemini_response="Road side assistance is included."
        )
        self.session.add(msg)
        self.session.commit()

        # Check relationships
        self.assertEqual(session.user.id, u.id)
        self.assertIn(session, u.chat_sessions)
        self.assertEqual(len(session.messages), 1)
        self.assertEqual(session.messages[0].message, "What features are included in premium?")
        self.assertEqual(session.messages[0].session.id, session.id)

        # Deleting chat session should delete chat messages
        self.session.delete(session)
        self.session.commit()

        db_msg = self.session.query(ChatMessage).filter_by(id=msg.id).first()
        self.assertIsNone(db_msg)

    def test_prediction_logs_fields(self) -> None:
        """
        Verify prediction logging table structure.
        """
        log = PredictionLog(
            prediction_type="claim_fraud_detection",
            model_version="3.1.2-alpha",
            latency_ms=142,
            input_hash="d8c363914a806292b3a8f6d6fc31b14a2bb3c70f",
            output_hash="2949ea9a29a4bb8938dc4c382fdf924e93d14902"
        )
        self.session.add(log)
        self.session.commit()

        self.assertIsNotNone(log.id)
        self.assertEqual(log.prediction_type, "claim_fraud_detection")
        self.assertEqual(log.latency_ms, 142)
        self.assertIsNotNone(log.created_at)


if __name__ == "__main__":
    unittest.main()

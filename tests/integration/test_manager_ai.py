"""
Integration Tests for the Manager AI Agent System.
Verifies natural language parsing, safety checks, SQL validation,
SQL injection rejection, execution metrics, and DB logging persistence.
"""

import unittest
import uuid
import time
from unittest.mock import patch, MagicMock

from src.database.session import SessionLocal
from src.database.base import Base
from src.modules.manager_ai.services import (
    ManagerAIService,
    validate_sql_safety,
    execute_query,
    get_db_schema
)
from src.models.user import User
from src.models.manager_query_log import ManagerSession, ManagerQueryLog


class TestManagerAIIntegration(unittest.TestCase):
    """
    Integration testing target features of Manager AI DB Agent.
    """
    def setUp(self) -> None:
        # Setup DB Transaction
        import src.database.database as db_module
        if db_module.engine is not None:
            SessionLocal.configure(bind=db_module.engine)
            Base.metadata.create_all(bind=db_module.engine)
        self.session = SessionLocal()
        
        self.cleanup_records()
        self.service = ManagerAIService()

        # Seed a dummy user first if not exists
        self.user = self.session.query(User).filter(User.email == "manager@acko.com").first()
        if not self.user:
            self.user = User(
                full_name="Manager Admin",
                email="manager@acko.com",
                role="manager"
            )
            self.session.add(self.user)
            self.session.commit()

    def tearDown(self) -> None:
        self.cleanup_records()
        self.session.close()

    def cleanup_records(self) -> None:
        try:
            # Ensure base metadata tables exist so we don't encounter UndefinedTable
            import src.database.database as db_module
            if db_module.engine is not None:
                Base.metadata.create_all(bind=db_module.engine)
                
            user = self.session.query(User).filter(User.email == "manager@acko.com").first()
            if user:
                # Deletes manager sessions in cascade
                self.session.query(ManagerSession).filter(ManagerSession.user_id == user.id).delete(synchronize_session=False)
                self.session.delete(user)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Cleanup warning: {e}")

    def test_sql_validation_safe_queries(self) -> None:
        """Verifies that classic read-only commands bypass validators successfully."""
        safe_queries = [
            "SELECT count(*) FROM policies WHERE premium > 1000;",
            "WITH high_val AS (SELECT id FROM claims WHERE claim_amount > 50000) SELECT * FROM high_val LIMIT 10;",
            "SELECT U.email, P.policy_number FROM users U JOIN policies P ON U.id = P.user_id GROUP BY U.email, P.policy_number HAVING count(*) >= 1 ORDER BY P.policy_number DESC;"
        ]
        for q in safe_queries:
            is_valid, err = validate_sql_safety(q)
            self.assertTrue(is_valid, f"Safe query was marked invalid: {q}. Error: {err}")

    def test_sql_validation_unsafe_keywords(self) -> None:
        """Verifies that modifying keywords get caught by validators."""
        unsafe_queries = [
            "INSERT INTO policies (policy_number) VALUES ('ACKO-1234');",
            "UPDATE claims SET claim_amount = 0 WHERE id = 1;",
            "DROP TABLE users;",
            "ALTER TABLE policies ADD COLUMN dummy INTEGER;",
            "TRUNCATE chat_messages;",
            "CREATE TABLE temp_data (id INT);"
        ]
        for q in unsafe_queries:
            is_valid, err = validate_sql_safety(q)
            self.assertFalse(is_valid, f"Unsafe query bypassed safety checks: {q}")
            self.assertIn("Unauthorized SQL keyword", err)

    def test_sql_validation_injection_detection(self) -> None:
        """Verifies that semicolon-separated multi-operations are rejected."""
        injection_queries = [
            "SELECT * FROM users; DROP TABLE classes;",
            "SELECT count(*) FROM policies; SELECT count(*) FROM claims;"
        ]
        for q in injection_queries:
            is_valid, err = validate_sql_safety(q)
            self.assertFalse(is_valid, f"Multi-statement injection bypassed verification: {q}")
            self.assertIn("Multiple SQL statements", err)

    def test_database_schema_introspection(self) -> None:
        """Verifies schemas are parsed into introspectable text representations."""
        schema_text = get_db_schema()
        self.assertIsNotNone(schema_text)
        self.assertIn("users", schema_text.lower())
        self.assertIn("policies", schema_text.lower())

    def test_database_execution_read_only(self) -> None:
        """Verifies that database execution retrieves rows correctly with execution times."""
        # Simple test query
        sql = "SELECT count(*) as count FROM users;"
        rows, row_count, elapsed = execute_query(sql)
        self.assertEqual(row_count, 1)
        self.assertGreaterEqual(elapsed, 0.0)
        self.assertIn("count", rows[0])

    @patch("src.modules.manager_ai.services.analyze_intent")
    @patch("src.modules.manager_ai.services.settings")
    def test_end_to_end_agent_persistence(self, mock_settings: MagicMock, mock_intent: MagicMock) -> None:
        """Validates Postgres persistence logging and restores session history context."""
        mock_settings.GEMINI_API_KEY = "your_gemini_api_key_here"  # offline trigger
        mock_intent.return_value = {"intent": "db_query"}

        result = self.service.run_agent_query("How many policy records do we have?")
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["row_count"], 1)
        self.assertGreaterEqual(result["execution_time_ms"], 0.0)

        # Check DB log persistence
        session_id = result["session_id"]
        db_session = self.session.query(ManagerSession).filter(ManagerSession.id == uuid.UUID(session_id)).first()
        self.assertIsNotNone(db_session)
        self.assertEqual(len(db_session.queries), 1)
        self.assertEqual(db_session.queries[0].question, "How many policy records do we have?")

        # Check history retrieval API
        history = self.service.get_session_history(session_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["question"], "How many policy records do we have?")
        self.assertEqual(history[0]["status"], "success")

    @patch("src.modules.manager_ai.services.settings")
    def test_unrelated_intent_handling(self, mock_settings: MagicMock) -> None:
        """Verifies safety rejection on out-of-bounds questions."""
        mock_settings.GEMINI_API_KEY = "mock_api_key_val"

        with patch("google.generativeai.GenerativeModel") as mock_model_class:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = '{"intent": "unrelated", "reason": "unrelated question topic"}'
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model

            result = self.service.run_agent_query("What is the weather in Delhi?")
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(result["compiled_sql"], "")
            self.assertIn("rejected", result["answer"].lower())

"""
Unit tests for the PostgreSQL database foundation layer.
Verifies connection string constructions, engine creation configurations,
session management pipelines, and health check diagnostics under both mock and actual environments.
"""

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from src.database.database import get_connection_string, create_db_engine
from src.database.session import get_db, SessionLocal
from src.database.connection import connect, disconnect, test_connection
from src.database.health_check import check_database_health
import src.database.database as db_module


class TestDatabaseConnection(unittest.TestCase):
    """
    Test suite for SQLAlchemy database structures, session creators, and state checks.
    """

    def setUp(self) -> None:
        # Cache original global engine to preserve state across mock trials
        self._original_engine = db_module.engine

    def tearDown(self) -> None:
        # Restore original global engine
        db_module.engine = self._original_engine

    def test_connection_string_generation(self) -> None:
        """
        Tests that connection strings generate correctly, and mask passwords on request.
        """
        raw_conn = get_connection_string(masked=False)
        masked_conn = get_connection_string(masked=True)

        self.assertTrue(raw_conn.startswith("postgresql+psycopg2://"))
        self.assertTrue(masked_conn.startswith("postgresql+psycopg2://"))
        
        # Verify masking of passwords in logs
        self.assertNotIn("••••••••", raw_conn)
        self.assertIn("••••••••", masked_conn)

    @patch("src.database.database.create_engine")
    def test_engine_creation_options(self, mock_create_engine: MagicMock) -> None:
        """
        Tests engine creation parameters like future, pre-ping, pool size.
        """
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        engine_res = create_db_engine()
        self.assertIsNotNone(engine_res)
        
        # Verify engine creation kwargs
        mock_create_engine.assert_called_once()
        kwargs = mock_create_engine.call_args[1]
        self.assertTrue(kwargs.get("pool_pre_ping"))
        self.assertTrue(kwargs.get("future"))
        self.assertFalse(kwargs.get("echo"))
        self.assertEqual(kwargs.get("pool_size"), 15)

    def test_session_generator_closes_on_completion(self) -> None:
        """
        Tests the get_db context generator returns a session and closes on exit.
        """
        mock_engine = MagicMock(spec=Engine)
        db_module.engine = mock_engine
        
        # Inject mock session factory to test purely locally
        mock_session = MagicMock(spec=Session)
        
        with patch("src.database.session.SessionLocal", return_value=mock_session):
            db_generator = get_db()
            session = next(db_generator)

            
            # Verify session yields
            self.assertEqual(session, mock_session)
            
            # Verify session is closed when generator is completed
            try:
                next(db_generator)
            except StopIteration:
                pass
            
            mock_session.close.assert_called_once()

    def test_health_check_signals_connected_on_success(self) -> None:
        """
        Tests check_database_health returns 'Connected' status when query executes successfully.
        """
        mock_engine = MagicMock(spec=Engine)
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        # Override global engine reference with mock
        db_module.engine = mock_engine
        
        health = check_database_health()
        self.assertEqual(health["status"], "Connected")
        self.assertIsNone(health["error"])
        self.assertGreaterEqual(health["latency_ms"], 0.0)

    def test_health_check_signals_disconnected_on_failure(self) -> None:
        """
        Tests check_database_health returns 'Disconnected' status and captures the error message dynamically.
        """
        mock_engine = MagicMock(spec=Engine)
        # Simulate connection check out exception
        mock_engine.connect.side_effect = Exception("TCP Timeout trying to reach PostgreSQL Server")
        
        db_module.engine = mock_engine
        
        health = check_database_health()
        self.assertEqual(health["status"], "Disconnected")
        self.assertEqual(health["error"], "TCP Timeout trying to reach PostgreSQL Server")

    def test_connect_handles_failure_gracefully(self) -> None:
        """
        Tests connect hook catches exceptions, logs them, and reports False instead of crashing Streamlit.
        """
        mock_engine = MagicMock(spec=Engine)
        mock_engine.connect.side_effect = Exception("Authentication username/password rejected")
        
        db_module.engine = mock_engine
        
        success, message = connect()
        self.assertFalse(success)
        self.assertIn("Authentication username/password rejected", message)

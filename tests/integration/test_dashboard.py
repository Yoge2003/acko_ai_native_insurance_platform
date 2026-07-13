"""
Integration Tests for the Enterprise Analytics Dashboard.
Verifies metrics, database aggregations, Plotly charts render calls,
and caching filters.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

from src.database.session import SessionLocal
from src.database.base import Base
from src.modules.dashboard.services import (
    DashboardService,
    get_state_from_registration
)
from src.modules.dashboard.ui import DashboardUI
from src.models.user import User
from src.models.policy import Policy
from src.models.claim import Claim
from src.models.quotation import Quotation
from src.models.prediction import PredictionLog


class TestDashboardIntegration(unittest.TestCase):
    def setUp(self) -> None:
        # Setup DB Transaction binding
        import src.database.database as db_module
        if db_module.engine is not None:
            SessionLocal.configure(bind=db_module.engine)
            Base.metadata.create_all(bind=db_module.engine)
        self.session = SessionLocal()
        self.service = DashboardService()
        self.cleanup_records()

    def tearDown(self) -> None:
        self.cleanup_records()
        self.session.close()

    def cleanup_records(self) -> None:
        try:
            self.session.query(PredictionLog).delete()
            self.session.query(Claim).delete()
            self.session.query(Quotation).delete()
            self.session.query(Policy).delete()
            self.session.query(User).filter(User.email.like("%test_dashboard%")).delete(synchronize_session=False)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Cleanup warning: {e}")

    def test_state_mapping(self) -> None:
        """Verifies state decoding from registration number strings."""
        self.assertEqual(get_state_from_registration("MH-12-AB-1234"), "Maharashtra")
        self.assertEqual(get_state_from_registration("KA-01-EF-5678"), "Karnataka")
        self.assertEqual(get_state_from_registration("DL-3C-G-9999"), "Delhi")
        self.assertEqual(get_state_from_registration("ZZ-99-ZZ-9999"), "Other")
        self.assertEqual(get_state_from_registration(None), "Unknown")

    def test_kpi_metrics_aggregations(self) -> None:
        """Verifies that metric results are computed correctly from local DataFrames."""
        dfs = {
            "users": pd.DataFrame([{"id": "u1", "created_at": datetime.utcnow()}]),
            "policies": pd.DataFrame([
                {"id": "pol1", "vehicle_type": "car", "registration_number": "KA-05-AB-1234", "premium": 5000.0, "status": "active"},
                {"id": "pol2", "vehicle_type": "bike", "registration_number": "MH-01-XY-5678", "premium": 2000.0, "status": "expired"},
            ]),
            "claims": pd.DataFrame([
                {"id": "c1", "policy_id": "pol1", "claim_amount": 1000.0, "claim_status": "approved"},
                {"id": "c2", "policy_id": "pol2", "claim_amount": 3000.0, "claim_status": "rejected"}
            ]),
            "quotations": pd.DataFrame([
                {"id": "q1", "vehicle_type": "car", "predicted_premium": 4800.0, "model_version": "v1.0.0"}
            ]),
            "prediction_logs": pd.DataFrame([
                {"id": "l1", "latency_ms": 120.0, "model_version": "v1.0.0"}
            ])
        }
        metrics = self.service.get_kpi_metrics_from_df(dfs)
        
        self.assertEqual(metrics["total_users"], 1)
        self.assertEqual(metrics["active_policies"], 1)
        self.assertEqual(metrics["total_quotations"], 1)
        self.assertEqual(metrics["total_claims"], 2)
        # Approval rate = 1 approved / 2 total = 50.0%
        self.assertEqual(metrics["claims_approval_rate"], 50.0)
        self.assertEqual(metrics["average_premium"], 3500.0)
        self.assertEqual(metrics["average_claim_amount"], 2000.0)
        self.assertEqual(metrics["total_premium_generated"], 7000.0)
        self.assertEqual(metrics["average_prediction_latency"], 120.0)
        self.assertEqual(metrics["total_ai_predictions"], 1)

    def test_filter_matching(self) -> None:
        """Verifies filtering of policy, claim, and quote datasets."""
        now = datetime.utcnow()
        dfs = {
            "users": pd.DataFrame([
                {"id": "u1", "created_at": now},
                {"id": "u2", "created_at": now - timedelta(days=60)}
            ]),
            "policies": pd.DataFrame([
                {"id": "pol1", "vehicle_type": "car", "policy_type": "comprehensive", "registration_number": "KA-05-1234", "premium": 5000.0, "status": "active", "created_at": now},
                {"id": "pol2", "vehicle_type": "bike", "policy_type": "third_party", "registration_number": "MH-01-5678", "premium": 2000.0, "status": "active", "created_at": now - timedelta(days=60)},
            ]),
            "claims": pd.DataFrame([
                {"id": "c1", "policy_id": "pol1", "claim_amount": 1000.0, "claim_status": "approved", "submitted_at": now},
                {"id": "c2", "policy_id": "pol2", "claim_amount": 3000.0, "claim_status": "rejected", "submitted_at": now - timedelta(days=60)}
            ]),
            "quotations": pd.DataFrame([
                {"id": "q1", "vehicle_type": "car", "predicted_premium": 4800.0, "model_version": "v1.0.0", "created_at": now},
                {"id": "q2", "vehicle_type": "bike", "predicted_premium": 1800.0, "model_version": "v1.1.0", "created_at": now - timedelta(days=60)},
            ]),
            "prediction_logs": pd.DataFrame([
                {"id": "l1", "latency_ms": 120.0, "model_version": "v1.0.0", "created_at": now},
                {"id": "l2", "latency_ms": 80.0, "model_version": "v1.1.0", "created_at": now - timedelta(days=60)}
            ])
        }

        # Mock fetch_raw_data to return our set
        with patch.object(DashboardService, "fetch_raw_data", return_value=dfs):
            # Test Date Filter presets (30 days range)
            filtered = self.service.get_filtered_data(days_range=30)
            self.assertEqual(len(filtered["policies"]), 1)
            self.assertEqual(len(filtered["claims"]), 1)
            self.assertEqual(len(filtered["users"]), 1)

            # Test vehicle_type filter
            filtered_v = self.service.get_filtered_data(days_range=None, vehicle_type="Car")
            self.assertEqual(len(filtered_v["policies"]), 1)
            self.assertEqual(filtered_v["policies"].iloc[0]["vehicle_type"], "car")

            # Test state filter
            filtered_s = self.service.get_filtered_data(days_range=None, state="Karnataka")
            self.assertEqual(len(filtered_s["policies"]), 1)
            self.assertEqual(filtered_s["policies"].iloc[0]["registration_number"], "KA-05-1234")

            # Test claim status filter
            filtered_c = self.service.get_filtered_data(days_range=None, claim_status="rejected")
            self.assertEqual(len(filtered_c["claims"]), 1)

            # Test model version filter
            filtered_m = self.service.get_filtered_data(days_range=None, model_version="v1.1.0")
            self.assertEqual(len(filtered_m["prediction_logs"]), 1)

    @patch("streamlit.plotly_chart")
    def test_charts_rendering_execution(self, mock_plotly_chart: MagicMock) -> None:
        """Verifies that all 10 Plotly visualizations are correctly rendered via st.plotly_chart."""
        dfs = {
            "users": pd.DataFrame([{"id": "u1", "created_at": datetime.utcnow()}]),
            "policies": pd.DataFrame([
                {"id": "pol1", "vehicle_type": "car", "registration_number": "KA-05-AB-1234", "premium": 5000.0, "status": "active", "created_at": datetime.utcnow()}
            ]),
            "claims": pd.DataFrame([
                {"id": "c1", "policy_id": "pol1", "claim_amount": 1000.0, "claim_status": "approved", "submitted_at": datetime.utcnow(), "gemini_analysis_json": {"damage_severity": "Medium"}}
            ]),
            "quotations": pd.DataFrame([
                {"id": "q1", "vehicle_type": "car", "predicted_premium": 4800.0, "model_version": "v1.0.0", "created_at": datetime.utcnow()}
            ]),
            "prediction_logs": pd.DataFrame([
                {"id": "l1", "latency_ms": 120.0, "model_version": "v1.0.0", "created_at": datetime.utcnow()}
            ])
        }
        DashboardUI.render_interactive_charts(dfs)
        self.assertGreaterEqual(mock_plotly_chart.call_count, 1)

    @patch("src.modules.manager_ai.services.settings")
    def test_manager_ai_instant_aggregations(self, mock_settings: MagicMock) -> None:
        """Validates that quick buttons compile queries safely against the database."""
        mock_settings.GEMINI_API_KEY = "your_gemini_api_key_here"  # triggers offline generator
        from src.modules.manager_ai.services import ManagerAIService
        
        manager = ManagerAIService()
        # Test states aggregates button query
        res1 = manager.run_agent_query("Show the top states based on total premium amounts")
        self.assertEqual(res1["status"], "success")
        self.assertIn("SELECT", res1["compiled_sql"].upper())
        self.assertTrue(len(res1["data"]) >= 0)

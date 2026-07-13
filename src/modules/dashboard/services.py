"""
Service layer for the Analytics Dashboard module.
Exposes statistical summaries and dynamic metric aggregators using SQL caching.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

from src.database.session import SessionLocal
from src.database.base import Base
from src.models.user import User
from src.models.policy import Policy
from src.models.claim import Claim
from src.models.quotation import Quotation
from src.models.prediction import PredictionLog

logger = logging.getLogger(__name__)

STATE_MAPPING = {
    "MH": "Maharashtra",
    "KA": "Karnataka",
    "DL": "Delhi",
    "HR": "Haryana",
    "TN": "Tamil Nadu",
    "KL": "Kerala",
    "AP": "Andhra Pradesh",
    "TS": "Telangana",
    "UP": "Uttar Pradesh",
    "GJ": "Gujarat",
    "WB": "West Bengal"
}


def get_state_from_registration(reg_num: str) -> str:
    if not reg_num:
        return "Unknown"
    prefix = reg_num[:2].upper()
    return STATE_MAPPING.get(prefix, "Other")


class DashboardService:
    """
    Coordinates metrics tracking and historical aggregation tasks.
    """

    @st.cache_data(ttl=600)
    def fetch_raw_data() -> Dict[str, pd.DataFrame]:
        """
        Retrieves all dashboard records from the database and caches outcomes.
        Fails safely on missing databases or un-migrated tables.
        """
        session = SessionLocal()
        try:
            Base.metadata.create_all(bind=session.bind)

            # Users
            users = session.query(User).all()
            df_users = pd.DataFrame([{
                "id": str(u.id),
                "created_at": u.created_at
            } for u in users]) if users else pd.DataFrame(columns=["id", "created_at"])
            
            # Policies
            policies = session.query(Policy).all()
            df_policies = pd.DataFrame([{
                "id": str(p.id),
                "vehicle_type": p.vehicle_type,
                "registration_number": p.registration_number,
                "premium": p.premium,
                "policy_type": p.policy_type,
                "status": p.status,
                "created_at": p.created_at
            } for p in policies]) if policies else pd.DataFrame(columns=[
                "id", "vehicle_type", "registration_number", "premium", "policy_type", "status", "created_at"
            ])
            
            # Claims
            claims = session.query(Claim).all()
            df_claims = pd.DataFrame([{
                "id": str(c.id),
                "policy_id": str(c.policy_id),
                "claim_amount": c.claim_amount,
                "gemini_analysis_json": c.gemini_analysis_json,
                "claim_status": c.claim_status,
                "submitted_at": c.submitted_at
            } for c in claims]) if claims else pd.DataFrame(columns=[
                "id", "policy_id", "claim_amount", "gemini_analysis_json", "claim_status", "submitted_at"
            ])
            
            # Quotations
            quotes = session.query(Quotation).all()
            df_quotes = pd.DataFrame([{
                "id": str(q.id),
                "vehicle_type": q.vehicle_type,
                "predicted_premium": q.predicted_premium,
                "model_version": q.model_version,
                "created_at": q.created_at
            } for q in quotes]) if quotes else pd.DataFrame(columns=[
                "id", "vehicle_type", "predicted_premium", "model_version", "created_at"
            ])
            
            # Prediction Logs
            logs = session.query(PredictionLog).all()
            df_logs = pd.DataFrame([{
                "id": str(l.id),
                "latency_ms": l.latency_ms,
                "model_version": l.model_version,
                "created_at": l.created_at
            } for l in logs]) if logs else pd.DataFrame(columns=["id", "latency_ms", "model_version", "created_at"])
            
            return {
                "users": df_users,
                "policies": df_policies,
                "claims": df_claims,
                "quotations": df_quotes,
                "prediction_logs": df_logs
            }
        except Exception as e:
            logger.error(f"Error fetching dashboard raw tables: {e}")
            # Empty fallback schema dataframes
            return {
                "users": pd.DataFrame(columns=["id", "created_at"]),
                "policies": pd.DataFrame(columns=["id", "vehicle_type", "registration_number", "premium", "policy_type", "status", "created_at"]),
                "claims": pd.DataFrame(columns=["id", "policy_id", "claim_amount", "gemini_analysis_json", "claim_status", "submitted_at"]),
                "quotations": pd.DataFrame(columns=["id", "vehicle_type", "predicted_premium", "model_version", "created_at"]),
                "prediction_logs": pd.DataFrame(columns=["id", "latency_ms", "model_version", "created_at"])
            }
        finally:
            session.close()

    def get_filtered_data(
        self,
        days_range: Optional[int] = 30,
        vehicle_type: Optional[str] = "All",
        policy_type: Optional[str] = "All",
        state: Optional[str] = "All",
        claim_status: Optional[str] = "All",
        model_version: Optional[str] = "All",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Applies selected filters to the cached raw dataframes.
        """
        dfs = DashboardService.fetch_raw_data()
        filtered = {name: df.copy() for name, df in dfs.items()}
        
        # Determine Date range window
        if start_date and end_date:
            t_start = pd.to_datetime(start_date).tz_localize(None)
            t_end = pd.to_datetime(end_date).tz_localize(None)
        elif days_range:
            t_end = datetime.utcnow()
            t_start = t_end - timedelta(days=days_range)
        else:
            t_start, t_end = None, None

        # Filter policies
        df_pol = filtered["policies"]
        if t_start and not df_pol.empty:
            df_pol = df_pol[pd.to_datetime(df_pol["created_at"]).dt.tz_localize(None).between(t_start, t_end)]
        if vehicle_type != "All" and not df_pol.empty:
            df_pol = df_pol[df_pol["vehicle_type"].str.lower() == vehicle_type.lower()]
        if policy_type != "All" and not df_pol.empty:
            df_pol = df_pol[df_pol["policy_type"].str.lower() == policy_type.lower()]
        if state != "All" and not df_pol.empty:
            df_pol = df_pol[df_pol["registration_number"].apply(get_state_from_registration) == state]
        filtered["policies"] = df_pol

        # Filter claims
        df_cl = filtered["claims"]
        if t_start and not df_cl.empty:
            df_cl = df_cl[pd.to_datetime(df_cl["submitted_at"]).dt.tz_localize(None).between(t_start, t_end)]
        if claim_status != "All" and not df_cl.empty:
            df_cl = df_cl[df_cl["claim_status"].str.lower() == claim_status.lower()]
        if not df_cl.empty and not df_pol.empty:
            df_cl = df_cl[df_cl["policy_id"].isin(df_pol["id"])]
        elif df_pol.empty:
            df_cl = pd.DataFrame(columns=df_cl.columns)
        filtered["claims"] = df_cl

        # Filter quotations
        df_q = filtered["quotations"]
        if t_start and not df_q.empty:
            df_q = df_q[pd.to_datetime(df_q["created_at"]).dt.tz_localize(None).between(t_start, t_end)]
        if vehicle_type != "All" and not df_q.empty:
            df_q = df_q[df_q["vehicle_type"].str.lower() == vehicle_type.lower()]
        if model_version != "All" and not df_q.empty:
            df_q = df_q[df_q["model_version"] == model_version]
        filtered["quotations"] = df_q

        # Filter prediction logs
        df_l = filtered["prediction_logs"]
        if t_start and not df_l.empty:
            df_l = df_l[pd.to_datetime(df_l["created_at"]).dt.tz_localize(None).between(t_start, t_end)]
        if model_version != "All" and not df_l.empty:
            df_l = df_l[df_l["model_version"] == model_version]
        filtered["prediction_logs"] = df_l

        # Filter users
        df_u = filtered["users"]
        if t_start and not df_u.empty:
            df_u = df_u[pd.to_datetime(df_u["created_at"]).dt.tz_localize(None).between(t_start, t_end)]
        filtered["users"] = df_u

        return filtered

    def get_kpi_metrics_from_df(self, filtered_dfs: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Aggregates KPI counts dynamically from filtered dataframes.
        """
        df_u = filtered_dfs["users"]
        df_p = filtered_dfs["policies"]
        df_c = filtered_dfs["claims"]
        df_q = filtered_dfs["quotations"]
        df_l = filtered_dfs["prediction_logs"]

        total_users = len(df_u)
        active_policies = len(df_p[df_p["status"] == "active"]) if not df_p.empty else 0
        total_quotes = len(df_q)
        total_claims = len(df_c)

        # Approval rate calculation
        if not df_c.empty:
            approved_count = len(df_c[df_c["claim_status"].str.lower() == "approved"])
            approval_rate = (approved_count / total_claims) * 100.0
        else:
            approval_rate = 0.0

        avg_premium = df_p["premium"].mean() if not df_p.empty else 0.0
        avg_claim = df_c["claim_amount"].mean() if not df_c.empty else 0.0
        total_premium = df_p["premium"].sum() if not df_p.empty else 0.0
        avg_latency = df_l["latency_ms"].mean() if not df_l.empty else 0.0
        total_predictions = len(df_l)

        return {
            "total_users": total_users,
            "active_policies": active_policies,
            "total_quotations": total_quotes,
            "total_claims": total_claims,
            "claims_approval_rate": approval_rate,
            "average_premium": avg_premium,
            "average_claim_amount": avg_claim,
            "total_premium_generated": total_premium,
            "average_prediction_latency": avg_latency,
            "total_ai_predictions": total_predictions
        }

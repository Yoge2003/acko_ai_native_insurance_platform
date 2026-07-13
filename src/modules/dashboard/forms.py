"""
Forms definition for the Analytics Dashboard module.
Exposes dashboard selectors and filters in Streamlit.
"""

import streamlit as st
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd

from src.modules.dashboard.services import get_state_from_registration


class DashboardFilterForm:
    """
    Renders filter components for dashboard analytics.
    """

    @staticmethod
    def render_filter_panel(raw_dfs: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, Any], bool]:
        """
        Renders dashboard range filters and category selections.

        Returns:
            Tuple: (Dictionary of entered filter values, Boolean indicating validation query changes).
        """
        filters: Dict[str, Any] = {}
        
        df_p = raw_dfs.get("policies", pd.DataFrame())
        df_c = raw_dfs.get("claims", pd.DataFrame())
        df_l = raw_dfs.get("prediction_logs", pd.DataFrame())

        # Pull dynamic options
        vehicle_types = ["All"] + sorted(list({str(v) for v in df_p["vehicle_type"].unique() if pd.notna(v)})) if not df_p.empty else ["All"]
        policy_types = ["All"] + sorted(list({str(p) for p in df_p["policy_type"].unique() if pd.notna(p)})) if not df_p.empty else ["All"]
        claim_statuses = ["All"] + sorted(list({str(s) for s in df_c["claim_status"].unique() if pd.notna(s)})) if not df_c.empty else ["All"]
        model_versions = ["All"] + sorted(list({str(m) for m in df_l["model_version"].unique() if pd.notna(m)})) if not df_l.empty else ["All"]
        
        states = ["All"]
        if not df_p.empty:
            states_set = {get_state_from_registration(r) for r in df_p["registration_number"] if r}
            states += sorted(list(states_set))

        with st.expander("🔍 Enterprise Filter Controls Panel", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_mode = st.radio("Date Filter Mode", ["Presets", "Custom Range"], horizontal=True, key="dash_date_mode")
                if date_mode == "Presets":
                    filters["days_range"] = st.select_slider(
                        "Analysis Window", 
                        options=[7, 30, 90, 365],
                        value=30,
                        format_func=lambda x: f"Last {x} Days",
                        key="dash_days_range"
                    )
                    filters["start_date"] = None
                    filters["end_date"] = None
                else:
                    filters["days_range"] = None
                    col_d_start, col_d_end = st.columns(2)
                    with col_d_start:
                        filters["start_date"] = st.date_input("Start Date", value=datetime.utcnow() - timedelta(days=30), key="dash_start_date")
                    with col_d_end:
                        filters["end_date"] = st.date_input("End Date", value=datetime.utcnow(), key="dash_end_date")
            
            with col2:
                filters["vehicle_type"] = st.selectbox("Vehicle Type", options=vehicle_types, key="dash_v_type")
                filters["policy_type"] = st.selectbox("Policy Type", options=policy_types, key="dash_p_type")

            with col3:
                filters["state"] = st.selectbox("State Region", options=states, key="dash_state")
                filters["claim_status"] = st.selectbox("Claim Status Filter", options=claim_statuses, key="dash_c_status")
                filters["model_version"] = st.selectbox("Model Execution Version", options=model_versions, key="dash_m_version")

            apply_btn = st.button("Apply Filter Constraints", use_container_width=True, key="dash_apply_filters")
            
        return filters, apply_btn

"""
Active page renderer for the Analytics Dashboard module.
"""

import streamlit as st
import logging
from src.modules.dashboard.ui import DashboardUI
from src.modules.dashboard.forms import DashboardFilterForm
from src.modules.dashboard.services import DashboardService

logger = logging.getLogger(__name__)


def render_dashboard_page() -> None:
    """
    Main layout renderer for the analytics dashboard manager.
    Coordinates filter collections, dynamic stats tables and Plotly charts.
    """
    logger.info("Accessing Analytics Dashboard module page layout.")
    
    st.markdown(
        """
        <div class="ds-page-header">
            <div class="ds-page-eyebrow">✦ Module 4 &nbsp;·&nbsp; Plotly &nbsp;·&nbsp; PostgreSQL 17</div>
            <div class="ds-page-title">Analytics Dashboard</div>
            <div class="ds-page-subtitle">
                Real-time performance indicators, claims trends, and portfolio analytics across vehicle categories —
                powered by live PostgreSQL data with interactive Plotly visualizations.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Instantiate dashboard services and fetch database tables cache
    service = DashboardService()
    raw_dfs = DashboardService.fetch_raw_data()

    # Sidebar: Caching / Refresh Managers
    st.sidebar.markdown('<div class="ds-section-title">Dashboard Controls</div>', unsafe_allow_html=True)
    if st.sidebar.button("Force Clear Cache Refresh", use_container_width=True, key="dash_btn_clear_cache"):
        st.cache_data.clear()
        st.toast("Dashboard cache invalidation completed.", icon="⚡")
        st.rerun()

    # 1. Display Filter Selector Panel
    filters, applied = DashboardFilterForm.render_filter_panel(raw_dfs)
    
    if applied:
        logger.info(f"Dashboard filters updated: {filters}")
        st.toast("Applied dashboard filter constraints.", icon="🔍")

    # 2. Retrieve Filtered DataFrames based on inputs
    filtered_dfs = service.get_filtered_data(
        days_range=filters.get("days_range"),
        vehicle_type=filters.get("vehicle_type"),
        policy_type=filters.get("policy_type"),
        state=filters.get("state"),
        claim_status=filters.get("claim_status"),
        model_version=filters.get("model_version"),
        start_date=filters.get("start_date"),
        end_date=filters.get("end_date")
    )

    # 3. Aggregate metrics indicators
    metrics = service.get_kpi_metrics_from_df(filtered_dfs)

    # 4. Draw KPI layouts
    DashboardUI.render_kpi_grid(metrics)

    # 5. Render interactive Plotly charts grid
    DashboardUI.render_interactive_charts(filtered_dfs)

    # 6. Manager AI Instant Analytics Inquiries Panel
    st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-title">Manager AI Quick Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.82rem;color:#475569;margin-bottom:1rem;">Run natural language queries directly against the database.</div>', unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    query_to_run = None
    with col_b1:
        if st.button("Top States by Premium", use_container_width=True, key="dash_q1"):
            query_to_run = "Show the top states based on total premium amounts"
    with col_b2:
        if st.button("Monthly Claims Summary", use_container_width=True, key="dash_q2"):
            query_to_run = "Show the count of claims grouped by month"
    with col_b3:
        if st.button("Active Policy Stats", use_container_width=True, key="dash_q3"):
            query_to_run = "Show policy counts grouped by status"
    with col_b4:
        if st.button("Avg Premium by Vehicle", use_container_width=True, key="dash_q4"):
            query_to_run = "Show the average premium for each vehicle type"
            
    if query_to_run:
        st.session_state["dashboard_manager_ai_query"] = query_to_run
        
    active_query = st.session_state.get("dashboard_manager_ai_query")
    if active_query:
        st.info(f"**Selected Prompt:** '{active_query}'")
        try:
            from src.modules.manager_ai.services import ManagerAIService
            from src.modules.manager_ai.ui import SQLAgentUI
            
            manager_service = ManagerAIService()
            results = manager_service.run_agent_query(active_query)
            SQLAgentUI.render_query_preview(results)
        except Exception as e:
            st.error(f"Manager AI query compilation error: {e}")

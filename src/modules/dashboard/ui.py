"""
Redesigned Dashboard UI using the ACKO Design System.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from src.modules.dashboard.services import get_state_from_registration


# Unified Plotly theme — ACKO deep purple enterprise palette
_PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(20,16,41,0.5)",
    font=dict(family="Poppins, sans-serif", color="#9CA3AF", size=11),
    margin=dict(l=0, r=0, t=44, b=0),
    title_font=dict(size=13, color="#FFFFFF", family="Poppins, sans-serif"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.08)",
        font=dict(size=10, color="#9CA3AF"),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.07)",
        tickfont=dict(color="#9CA3AF"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.07)",
        tickfont=dict(color="#9CA3AF"),
    ),
)

_COLORS = ["#7C3AED", "#22C55E", "#C084FC", "#F59E0B", "#A855F7", "#38BDF8", "#8B5CF6"]


class DashboardUI:
    """Renders premium KPI cards and DS-themed Plotly charts."""

    @staticmethod
    def render_kpi_grid(metrics: Dict[str, Any]) -> None:
        """Renders 10 DS-styled KPI cards in two rows."""
        row1 = st.columns(5)
        kpis_row1 = [
            ("Total Users", str(metrics.get("total_users", 0))),
            ("Active Policies", str(metrics.get("active_policies", 0))),
            ("Total Quotations", str(metrics.get("total_quotations", 0))),
            ("Total Claims", str(metrics.get("total_claims", 0))),
            ("Total Premiums", f"₹{metrics.get('total_premium_generated', 0):,.0f}"),
        ]
        for col, (label, val) in zip(row1, kpis_row1):
            with col:
                st.markdown(
                    f"""
                    <div class="ds-kpi-card">
                        <div class="ds-kpi-label">{label}</div>
                        <div class="ds-kpi-value">{val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        row2 = st.columns(5)
        kpis_row2 = [
            ("Approval Rate", f"{metrics.get('claims_approval_rate', 0):.1f}%"),
            ("Avg Premium", f"₹{metrics.get('average_premium', 0):,.0f}"),
            ("Avg Claim", f"₹{metrics.get('average_claim_amount', 0):,.0f}"),
            ("AI Predictions", str(metrics.get("total_ai_predictions", 0))),
            ("Avg Latency", f"{metrics.get('average_prediction_latency', 0):.0f} ms"),
        ]
        for col, (label, val) in zip(row2, kpis_row2):
            with col:
                st.markdown(
                    f"""
                    <div class="ds-kpi-card">
                        <div class="ds-kpi-label">{label}</div>
                        <div class="ds-kpi-value">{val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    @staticmethod
    def render_interactive_charts(dfs: Dict[str, pd.DataFrame]) -> None:
        """Renders DS-themed Plotly chart grid."""
        df_p = dfs["policies"]
        df_c = dfs["claims"]
        df_q = dfs["quotations"]
        df_l = dfs["prediction_logs"]
        df_u = dfs["users"]

        st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="ds-section-title">Performance Trends</div>', unsafe_allow_html=True)

        def _apply(fig):
            fig.update_layout(**_PLOTLY_LAYOUT)
            return fig

        # Row 1
        c1, c2 = st.columns(2)
        with c1:
            if not df_p.empty and df_p["premium"].notna().any():
                fig = px.histogram(df_p, x="premium", nbins=15, title="Premium Distribution",
                                   color_discrete_sequence=["#6366F1"])
                st.plotly_chart(_apply(fig), use_container_width=True)
            else:
                st.info("No premium data available.")

        with c2:
            if not df_c.empty and not df_c["claim_status"].isnull().all():
                fig = px.pie(df_c, names="claim_status", title="Claims by Decision",
                             hole=0.45, color_discrete_sequence=_COLORS)
                fig.update_traces(textfont_size=11)
                st.plotly_chart(_apply(fig), use_container_width=True)
            else:
                st.info("No claims data available.")

        # Row 2
        c3, c4 = st.columns(2)
        with c3:
            if not df_c.empty:
                df_cm = df_c.copy()
                df_cm["month"] = pd.to_datetime(df_cm["submitted_at"]).dt.to_period("M").astype(str)
                df_grp = df_cm.groupby("month").size().reset_index(name="count")
                fig = px.bar(df_grp, x="month", y="count", title="Claims by Month",
                             color_discrete_sequence=["#22C55E"])
                st.plotly_chart(_apply(fig), use_container_width=True)
            else:
                st.info("No claims data.")

        with c4:
            if not df_p.empty:
                df_grp = df_p.groupby("vehicle_type")["premium"].sum().reset_index(name="total_premium")
                fig = px.bar(df_grp, x="vehicle_type", y="total_premium",
                             title="Total Premium by Vehicle Type",
                             color="vehicle_type", color_discrete_sequence=_COLORS)
                st.plotly_chart(_apply(fig), use_container_width=True)
            else:
                st.info("No policy data.")

        # Row 3
        c5, c6 = st.columns(2)
        with c5:
            if not df_p.empty:
                df_act = df_p[df_p["status"] == "active"].copy()
                if not df_act.empty:
                    df_act["state"] = df_act["registration_number"].apply(get_state_from_registration)
                    df_grp = df_act.groupby("state").size().reset_index(name="count")
                    fig = px.bar(df_grp, x="state", y="count",
                                 title="Active Policies by State",
                                 color_discrete_sequence=["#A78BFA"])
                    st.plotly_chart(_apply(fig), use_container_width=True)
                else:
                    st.info("No active policies.")
            else:
                st.info("No policy data.")

        with c6:
            if not df_c.empty:
                def _sev(x):
                    return x.get("damage_severity", "Low") if isinstance(x, dict) else "Low"
                df_cs = df_c.copy()
                df_cs["severity"] = df_cs["gemini_analysis_json"].apply(_sev)
                df_grp = df_cs.groupby("severity").size().reset_index(name="count")
                fig = px.pie(df_grp, values="count", names="severity",
                             title="Damage Severity Distribution",
                             color_discrete_sequence=_COLORS)
                st.plotly_chart(_apply(fig), use_container_width=True)
            else:
                st.info("No claims data.")

        # Row 4
        c7, c8 = st.columns(2)
        with c7:
            if not df_l.empty:
                df_ls = df_l.sort_values("created_at")
                fig = px.line(df_ls, x="created_at", y="latency_ms",
                              title="Prediction Latency Over Time",
                              color_discrete_sequence=["#F87171"])
                st.plotly_chart(_apply(fig), use_container_width=True)
            else:
                st.info("No telemetry data.")

        with c8:
            if not df_u.empty:
                df_ug = df_u.copy()
                df_ug["date"] = pd.to_datetime(df_ug["created_at"]).dt.to_period("D").astype(str)
                df_grp = df_ug.groupby("date").size().reset_index(name="registrations")
                df_grp["cumulative"] = df_grp["registrations"].cumsum()
                fig = px.line(df_grp, x="date", y="cumulative",
                              title="Cumulative User Growth",
                              color_discrete_sequence=["#F59E0B"])
                st.plotly_chart(_apply(fig), use_container_width=True)
            else:
                st.info("No user data.")

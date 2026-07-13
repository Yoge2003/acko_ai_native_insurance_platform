"""
Redesigned Manager AI UI using the ACKO Design System.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any


class SQLAgentUI:
    """Renders the premium SQL Agent interface using the DS."""

    @staticmethod
    def render_info_card() -> None:
        """Agent status card."""
        st.markdown(
            """
            <div class="ds-card" style="margin-bottom:1rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                    <div style="font-size:0.875rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">LangGraph SQL Agent</div>
                    <span class="ds-badge ds-badge-brand">Active</span>
                </div>
                <div style="font-size:0.82rem;color:#9CA3AF;line-height:1.6;margin-bottom:12px;font-family:'Poppins',sans-serif;">
                    Converts plain English questions into read-only PostgreSQL queries using Gemini. All mutation commands are blocked.
                </div>
                <div style="padding:10px 14px;background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.25);border-left:3px solid #7C3AED;border-radius:0 8px 8px 0;font-size:0.78rem;color:#C084FC;font-family:'Poppins',sans-serif;">
                    SQL Safety Enforced — INSERT, UPDATE, DELETE, DROP blocked
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="ds-section-title" style="margin-top:1.25rem;">Quick Queries</div>', unsafe_allow_html=True)
        quick_queries = [
            "Total policies by vehicle type",
            "Monthly claim approvals",
            "Top states by premium",
            "Average premium by risk level",
        ]
        for q in quick_queries:
            st.markdown(
                f'<div style="padding:9px 14px;background:rgba(124,58,237,0.07);border:1px solid rgba(124,58,237,0.18);border-radius:8px;font-size:0.8rem;color:#D1D5DB;margin-bottom:6px;cursor:default;font-family:\'Poppins\',sans-serif;">{q}</div>',
                unsafe_allow_html=True,
            )

    @staticmethod
    def render_query_preview(results: Dict[str, Any]) -> None:
        """Renders SQL agent results with premium styling."""
        status = results.get("status", "success")
        error_msg = results.get("error", "")

        if status == "rejected":
            st.error(f"**Query Blocked by Safety System**\n\n{error_msg}")
            return
        elif status == "error":
            st.error(f"**Execution Error**\n\n{error_msg}")
        elif status == "warning":
            st.warning("Execution completed with warnings.")

        # ── Answer ────────────────────────────────────────
        answer = results.get("answer", "")
        if answer:
            st.markdown(
                f"""
                <div class="ds-card" style="margin-bottom:1rem;">
                    <div style="font-size:0.65rem;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Executive Summary</div>
                    <div style="font-size:0.9rem;color:#94A3B8;line-height:1.6;">{answer}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Execution stats ───────────────────────────────
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Status", status.upper())
        with c2:
            st.metric("Execution Time", f"{results.get('execution_time_ms', 0):.1f} ms")
        with c3:
            st.metric("Rows Returned", str(results.get("row_count", 0)))

        # ── SQL Preview ───────────────────────────────────
        with st.expander("Generated SQL Query", expanded=True):
            st.code(results.get("compiled_sql", ""), language="sql")

        # ── Data table ───────────────────────────────────
        data = results.get("data", [])
        if data:
            with st.expander("Data Results", expanded=True):
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)

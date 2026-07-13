"""
Redesigned Claims UI using the ACKO Design System.
"""

import streamlit as st
from typing import Dict, Any


class ClaimsUI:
    """Renders premium claims status and Gemini Vision assessment cards."""

    @staticmethod
    def render_info_card() -> None:
        """Claims pipeline status card."""
        st.markdown(
            """
            <div class="ds-card" style="margin-bottom:1rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                    <div style="font-size:0.875rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">Claims AI Engine</div>
                    <span class="ds-badge ds-badge-success">Active</span>
                </div>
                <div style="font-size:0.82rem;color:#9CA3AF;line-height:1.6;margin-bottom:12px;font-family:'Poppins',sans-serif;">
                    Gemini Vision inspects damage photos, LangGraph audits for fraud, and ML classifier determines triage routing.
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                    <div style="padding:10px 12px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);border-radius:10px;">
                        <div style="font-size:0.62rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.07em;font-family:'Poppins',sans-serif;">Vision</div>
                        <div style="font-size:0.82rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">Gemini Pro</div>
                    </div>
                    <div style="padding:10px 12px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);border-radius:10px;">
                        <div style="font-size:0.62rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.07em;font-family:'Poppins',sans-serif;">Audit</div>
                        <div style="font-size:0.82rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">LangGraph</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_submission_confirmation(result: Dict[str, Any]) -> None:
        """Renders the premium claims result dashboard."""
        decision = result["approval_decision"]
        is_approved = "approv" in decision.lower()
        decision_color = "#4ADE80" if is_approved else "#F87171"
        decision_badge = "ds-badge-success" if is_approved else "ds-badge-danger"

        # ── Decision hero ────────────────────────────────
        st.markdown(
            f"""
            <div class="ds-result-hero" style="margin-bottom:1.5rem;">
                <div class="ds-result-label">Claim Decision</div>
                <div class="ds-result-value" style="font-size:2rem;color:{decision_color};">{decision}</div>
                <div class="ds-result-sub">
                    Approval probability {result['approval_probability']:.1%} &nbsp;·&nbsp;
                    Confidence {result['confidence']:.1%} &nbsp;·&nbsp;
                    {result['submitted_at']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── KPIs ─────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Decision", decision)
        with c2:
            st.metric("Approval Prob.", f"{result['approval_probability']:.1%}")
        with c3:
            st.metric("Confidence", f"{result['confidence']:.1%}")
        with c4:
            st.metric("Route", result["route"])

        # Human review flag
        if result["human_review_flag"]:
            st.warning("**Human Review Required** — Confidence below 70% threshold. Claim routed for manual inspection.")
        else:
            st.success("**Auto-Routing Active** — High-confidence assessment. Queued for rapid payout processing.")

        # ── Gemini Vision ─────────────────────────────────
        if "gemini_analysis" in result:
            analysis = result["gemini_analysis"]
            st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
            st.markdown('<div class="ds-section-title">Gemini Vision Analysis</div>', unsafe_allow_html=True)

            v1, v2, v3 = st.columns(3)
            with v1:
                st.metric("Damage Severity", analysis.get("damage_severity", "—"))
                st.metric("Gemini Confidence", f"{analysis.get('confidence_score', 0):.1%}")
            with v2:
                st.metric("Repair Complexity", analysis.get("estimated_repair_complexity", "—"))
                st.metric("Damage Type", analysis.get("damage_type", "—"))
            with v3:
                fraud_list = analysis.get("visible_fraud_indicators", ["none"])
                fraud_str = ", ".join(fraud_list) if isinstance(fraud_list, list) else str(fraud_list)
                st.metric("Fraud Indicators", fraud_str)

            st.markdown(
                f"""
                <div class="ds-card" style="margin-top:1rem;">
                    <div style="font-size:0.75rem;font-weight:600;color:#6366F1;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Natural Language Assessment</div>
                    <div style="font-size:0.9rem;color:#94A3B8;line-height:1.6;">{analysis.get('natural_language_assessment', 'No details available.')}</div>
                    <div style="margin-top:12px;font-size:0.8rem;color:#475569;">
                        <strong style="color:#94A3B8;">Damaged Parts:</strong> {", ".join(analysis.get('damaged_parts', []))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Registration ──────────────────────────────────
        st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ds-card">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                    <div style="font-size:0.875rem;font-weight:600;color:#F1F5F9;">Claim Registration</div>
                    <span class="ds-badge {decision_badge}">{decision}</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:0.85rem;">
                    <div>
                        <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px;">Tracking ID</div>
                        <div style="color:#F1F5F9;font-family:monospace;font-size:0.78rem;">{result['claim_id']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px;">Policy</div>
                        <div style="color:#F1F5F9;">{result['policy_number']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px;">Queue</div>
                        <div style="color:#F1F5F9;">{result['route']}</div>
                    </div>
                </div>
                <div style="margin-top:12px;font-size:0.8rem;color:#475569;">{result['detail_summary']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── SHAP ─────────────────────────────────────────
        st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="ds-section-title">SHAP Decision Explanation</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.85rem;color:#475569;margin-bottom:1rem;">{result["shap_summary"]}</div>',
            unsafe_allow_html=True,
        )

        col_pos, col_neg = st.columns(2)
        with col_pos:
            st.markdown(
                '<div style="font-size:0.75rem;font-weight:600;color:#4ADE80;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;">↑ Approval Factors</div>',
                unsafe_allow_html=True,
            )
            for feat, val in (result.get("top_positive_features") or []):
                bar_pct = min(abs(val) * 100, 100)
                st.markdown(
                    f'<div class="ds-feature-row"><div class="ds-feature-name">{feat}</div><div class="ds-feature-bar"><div class="ds-feature-bar-fill" style="width:{bar_pct:.0f}%;background:#4ADE80;"></div></div><div class="ds-feature-value positive">+{val:.4f}</div></div>',
                    unsafe_allow_html=True,
                )

        with col_neg:
            st.markdown(
                '<div style="font-size:0.75rem;font-weight:600;color:#F87171;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;">↓ Rejection Factors</div>',
                unsafe_allow_html=True,
            )
            for feat, val in (result.get("top_negative_features") or []):
                bar_pct = min(abs(val) * 100, 100)
                st.markdown(
                    f'<div class="ds-feature-row"><div class="ds-feature-name">{feat}</div><div class="ds-feature-bar"><div class="ds-feature-bar-fill" style="width:{bar_pct:.0f}%;background:#F87171;"></div></div><div class="ds-feature-value negative">{val:.4f}</div></div>',
                    unsafe_allow_html=True,
                )

"""
Redesigned Quotation UI using the ACKO Design System.
"""

import streamlit as st
from typing import Dict, Any


class QuotationUI:
    """Renders premium premium breakdown and SHAP explainability cards."""

    @staticmethod
    def render_info_card() -> None:
        """Model status card."""
        st.markdown(
            """
            <div class="ds-card" style="margin-bottom:1rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                    <div style="font-size:0.875rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">Random Forest Regressor</div>
                    <span class="ds-badge ds-badge-success">Active</span>
                </div>
                <div style="font-size:0.82rem;color:#9CA3AF;line-height:1.6;margin-bottom:12px;font-family:'Poppins',sans-serif;">
                    Predicts annual vehicle premiums from historical underwriting data. SHAP explains each factor's contribution.
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                    <div style="padding:10px 12px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);border-radius:10px;">
                        <div style="font-size:0.62rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.07em;font-family:'Poppins',sans-serif;">Estimator</div>
                        <div style="font-size:0.82rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">Random Forest</div>
                    </div>
                    <div style="padding:10px 12px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);border-radius:10px;">
                        <div style="font-size:0.62rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:.07em;font-family:'Poppins',sans-serif;">Explainer</div>
                        <div style="font-size:0.82rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">SHAP Tree</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_premium_breakdown(quote_res: Dict[str, Any]) -> None:
        """Renders the premium result hero card and SHAP breakdown."""

        # ── Hero result card ──────────────────────────────
        st.markdown(
            f"""
            <div class="ds-result-hero">
                <div class="ds-result-label">Estimated Annual Premium</div>
                <div class="ds-result-value">₹{quote_res['predicted_premium']:,.2f}</div>
                <div class="ds-result-sub">Confidence {quote_res['confidence_score']:.1%} · {quote_res['model_version']} · {quote_res['timestamp']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── KPI row ───────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Predicted Premium", f"₹{quote_res['predicted_premium']:,.2f}")
        with c2:
            st.metric("Confidence", f"{quote_res['confidence_score']:.1%}")
        with c3:
            st.metric("Model Version", quote_res["model_version"])

        # ── SHAP explanation ──────────────────────────────
        st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="ds-section-title">AI Underwriting Explanation (SHAP)</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.85rem;color:#475569;margin-bottom:1rem;">{quote_res["shap_summary"]}</div>',
            unsafe_allow_html=True,
        )

        col_pos, col_neg = st.columns(2)

        with col_pos:
            st.markdown(
                '<div style="font-size:0.75rem;font-weight:600;color:#4ADE80;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;">↑ Increasing Factors</div>',
                unsafe_allow_html=True,
            )
            if quote_res.get("top_positive_features"):
                for feat, val in quote_res["top_positive_features"]:
                    bar_pct = min(abs(val) * 100, 100)
                    st.markdown(
                        f"""
                        <div class="ds-feature-row">
                            <div class="ds-feature-name">{feat}</div>
                            <div class="ds-feature-bar"><div class="ds-feature-bar-fill" style="width:{bar_pct:.0f}%;background:#4ADE80;"></div></div>
                            <div class="ds-feature-value positive">+{val:.4f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<div style="font-size:0.82rem;color:#2D2D45;">None</div>', unsafe_allow_html=True)

        with col_neg:
            st.markdown(
                '<div style="font-size:0.75rem;font-weight:600;color:#F87171;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;">↓ Decreasing Factors</div>',
                unsafe_allow_html=True,
            )
            if quote_res.get("top_negative_features"):
                for feat, val in quote_res["top_negative_features"]:
                    bar_pct = min(abs(val) * 100, 100)
                    st.markdown(
                        f"""
                        <div class="ds-feature-row">
                            <div class="ds-feature-name">{feat}</div>
                            <div class="ds-feature-bar"><div class="ds-feature-bar-fill" style="width:{bar_pct:.0f}%;background:#F87171;"></div></div>
                            <div class="ds-feature-value negative">{val:.4f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<div style="font-size:0.82rem;color:#2D2D45;">None</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div style="margin-top:1.5rem;padding:12px 18px;background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.25);border-left:3px solid #7C3AED;border-radius:0 10px 10px 0;font-size:0.82rem;color:#9CA3AF;font-family:'Poppins',sans-serif;">
                Prediction persisted to PostgreSQL. Reference ID logged automatically.
            </div>
            """,
            unsafe_allow_html=True,
        )

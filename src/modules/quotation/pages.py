"""
Redesigned Quotation page renderer using the ACKO Design System.
"""

import streamlit as st
import logging
from src.modules.quotation.ui import QuotationUI
from src.modules.quotation.forms import QuotationForm
from src.modules.quotation.services import QuotationService

logger = logging.getLogger(__name__)


def render_quotation_page() -> None:
    """Premium quotation page with DS header."""
    logger.info("Loading Premium Quotation page.")

    st.markdown(
        """
        <div class="ds-page-header">
            <div class="ds-page-eyebrow">✦ Module 2 &nbsp;·&nbsp; Random Forest &nbsp;·&nbsp; SHAP Explainability</div>
            <div class="ds-page-title">Premium Quotation</div>
            <div class="ds-page-subtitle">
                ML-driven annual premium prediction using Random Forest trained on 50K+ vehicle records —
                every pricing decision backed by SHAP transparency for regulatory compliance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 2.2], gap="large")

    with col_left:
        QuotationUI.render_info_card()

    with col_right:
        form_data, submitted = QuotationForm.render_quote_form()

        if submitted and form_data:
            with st.spinner("Running ML inference…"):
                try:
                    service = QuotationService()
                    quote_res = service.generate_premium_quote(form_data)
                    if quote_res.get("status") == "success":
                        st.success("Premium quotation generated and saved to database.")
                        QuotationUI.render_premium_breakdown(quote_res)
                except Exception as e:
                    logger.error(f"Quotation error: {e}", exc_info=True)
                    st.error(f"Underwriting error: {e}")

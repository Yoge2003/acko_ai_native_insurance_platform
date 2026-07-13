"""
Redesigned Claims page renderer using the ACKO Design System.
"""

import streamlit as st
import logging
from src.modules.claims.ui import ClaimsUI
from src.modules.claims.forms import ClaimsForm
from src.modules.claims.services import ClaimsService

logger = logging.getLogger(__name__)


def render_claims_page() -> None:
    """Premium claims page with DS header."""
    logger.info("Loading Claims page.")

    st.markdown(
        """
        <div class="ds-page-header">
            <div class="ds-page-eyebrow">✦ Module 3 &nbsp;·&nbsp; Gemini Vision &nbsp;·&nbsp; LangGraph &nbsp;·&nbsp; XGBoost</div>
            <div class="ds-page-title">Claims AI Engine</div>
            <div class="ds-page-subtitle">
                Computer vision damage assessment with Gemini Vision API, automated fraud scoring,
                severity classification, and intelligent claim triage routing via LangGraph agents.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 2.2], gap="large")

    with col_left:
        ClaimsUI.render_info_card()

    with col_right:
        form_data, submitted = ClaimsForm.render_claim_form()

        if submitted and form_data:
            with st.spinner("Analyzing damage and verifying policy coverage…"):
                try:
                    service = ClaimsService()
                    result = service.submit_claim_request(form_data)
                    ClaimsUI.render_submission_confirmation(result)
                except Exception as e:
                    logger.error(f"Claims error: {e}", exc_info=True)
                    st.error(f"Claim validation error: {e}")

"""
Forms definition for the Claims module.
Captures incident reports, images, and coverage parameters in Streamlit.
"""

import streamlit as st
from typing import Dict, Any, Tuple
from src.utils.common import generate_uuid


class ClaimsForm:
    """
    Renders Streamlit form widgets for claim registration.
    """

    @staticmethod
    def render_claim_form() -> Tuple[Dict[str, Any], bool]:
        """
        Renders claims reporting inputs such as policy codes, damage descriptions, and file uploads.
        Under Phase 3.2, submission buttons are disabled.

        Returns:
            Tuple: (Dictionary of entered field values, Boolean indicating submission status).
        """
        form_payload: Dict[str, Any] = {}

        st.subheader("📝 Damage Report & Policy Intake")
        
        # Auto-generate a Claim ID if none exists in session state
        if "temp_claim_id" not in st.session_state:
            st.session_state["temp_claim_id"] = f"CLM-{generate_uuid()[:8].upper()}"

        col1, col2 = st.columns(2)
        with col1:
            form_payload["claim_id"] = st.text_input(
                "Claim ID (Auto-Generated)", 
                value=st.session_state["temp_claim_id"], 
                disabled=True
            )
            form_payload["policy_number"] = st.text_input("Policy Number (e.g. POL-998877)", value="POL-108726")
        
        with col2:
            form_payload["vehicle_type"] = st.selectbox("Vehicle Segment", options=["Car", "Two-Wheeler"])
            form_payload["claim_amount"] = st.number_input("Estimated Repair Claim Amount (INR)", min_value=500.0, max_value=2000000.0, value=25000.0, step=5000.0)

        # Incident description
        form_payload["description"] = st.text_area(
            "Detailed Accident Explication", 
            value="Vehicle sustained front bumper scraping and headlight damage during low-speed collision."
        )

        st.write("---")
        st.subheader("📸 Collision Proof Uploads")
        # Image attachment (Simulated upload)
        uploaded_file = st.file_uploader(
            "Upload image of structural vehicle damage", 
            type=["png", "jpg", "jpeg"]
        )
        form_payload["uploaded_image"] = uploaded_file

        # Submit Claim Button (Enabled in Phase 5.4 UI)
        submit_btn = st.button("Submit Claim Report", disabled=False, use_container_width=True)

        return form_payload, submit_btn

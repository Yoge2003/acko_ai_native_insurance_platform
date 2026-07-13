"""
Forms definition for the Premium Quotation module.
Defines user input captures for vehicle properties and customer profiles in Streamlit.
"""

import streamlit as st
from typing import Dict, Any, Tuple


class QuotationForm:
    """
    Renders Streamlit form widgets for the vehicle quotation process.
    """

    @staticmethod
    def render_quote_form() -> Tuple[Dict[str, Any], bool]:
        """
        Displays input boxes for name, age, vehicle configurations, and claims history.
        Under Phase 3.2, submission buttons are disabled.

        Returns:
            Tuple: (Dictionary of entered field values, Boolean indicating submission status).
        """
        form_payload: Dict[str, Any] = {}

        st.subheader("📝 Underwriting Profile Details")
        
        # 1. Customer Personal Specs
        col1, col2 = st.columns(2)
        with col1:
            form_payload["customer_name"] = st.text_input("Customer Name", value="Jane Doe")
            form_payload["age"] = st.number_input("Driver Age", min_value=18, max_value=100, value=30)
            form_payload["gender"] = st.selectbox("Gender", options=["Male", "Female", "Other"])
        with col2:
            form_payload["mobile_number"] = st.text_input("Mobile Number (E.164)", value="+919876543210")
            form_payload["vehicle_type"] = st.selectbox("Vehicle Type", options=["Car", "Two-Wheeler (Bike)"])
            form_payload["fuel_type"] = st.selectbox("Fuel Type", options=["Petrol", "Diesel", "CNG", "Electric"])

        # 2. Vehicle Identification properties
        col3, col4 = st.columns(2)
        with col3:
            form_payload["manufacturer"] = st.text_input("Manufacturer/Brand", value="Honda")
            form_payload["model"] = st.text_input("Vehicle Model Description", value="City")
            form_payload["manufacturing_year"] = st.number_input("Manufacturing Year", min_value=2000, max_value=2026, value=2022)
        with col4:
            form_payload["city"] = st.text_input("Operational City", value="Mumbai")
            form_payload["state"] = st.text_input("Operational State", value="Maharashtra")
            form_payload["vehicle_idv"] = st.number_input("Vehicle IDV (INR Value)", min_value=10000.0, max_value=10000000.0, value=800000.0, step=50000.0)

        # 3. Policy & NCB percentage parameters
        col5, col6 = st.columns(2)
        with col5:
            form_payload["ncb_percentage"] = st.selectbox(
                "No Claim Bonus (NCB) Discount", 
                options=[0, 20, 25, 35, 45, 50],
                format_func=lambda x: f"{x}%"
            )
        with col6:
            form_payload["previous_claims"] = st.checkbox("Lodged claims in previous policy term", value=False)

        # Submit Quote Button (Enabled in Phase 5.4 UI)
        submit_btn = st.button("Generate Premium Quote", disabled=False, use_container_width=True)

        return form_payload, submit_btn

"""
Forms definition for the AI Policy Chatbot module.
Exposes Streamlit chat query entry form fields.
"""

import streamlit as st
from typing import Optional, Tuple


class ChatbotForm:
    """
    Renders Streamlit components for chatbot interaction.
    """

    @staticmethod
    def render_chat_input() -> Tuple[Optional[str], bool]:
        """
        Displays a standard chat container query input box.
        Enables text entry and button submission.

        Returns:
            Tuple containing (entered_query_string or None, is_submitted_boolean).
        """
        # Create standard text input box
        query_text = st.text_input(
            label="Inquire policy terms (e.g. 'what exclusions apply to medical costs?')",
            placeholder="Type your insurance query here...",
            key="chatbot_input_text"
        )
        
        send_btn = st.button("Send Query", disabled=False, use_container_width=True, type="primary")
        
        return query_text if query_text else None, send_btn

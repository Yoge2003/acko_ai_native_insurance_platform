"""
Forms definition for the Manager AI module.
Exposes prompt inputs and buttons for the DB SQL agent in Streamlit.
"""

import streamlit as st
from typing import Optional, Tuple


class SQLAgentForm:
    """
    Renders Streamlit components for database query agents.
    """

    @staticmethod
    def render_query_input() -> Tuple[Optional[str], bool]:
        """
        Displays raw English text input area to route database questions.
        Under Phase 3.2, submission buttons are disabled.

        Returns:
            Tuple: (Entered query prompt or None, Boolean indicating submission status).
        """
        query_prompt = st.text_area(
            label="Inquire Database in plain English",
            placeholder="e.g. 'Show me the total claims filed last month grouped by region'",
            key="manager_ai_prompt_text"
        )
        
        # Enabled Ask Agent button
        ask_btn = st.button("Ask Agent", disabled=False, use_container_width=True)

        return query_prompt if query_prompt else None, ask_btn

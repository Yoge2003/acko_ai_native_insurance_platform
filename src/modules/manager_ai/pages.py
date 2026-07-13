"""
Active page renderer for the Manager AI module.
"""

import streamlit as st
import logging
from src.modules.manager_ai.ui import SQLAgentUI
from src.modules.manager_ai.forms import SQLAgentForm
from src.modules.manager_ai.services import ManagerAIService

logger = logging.getLogger(__name__)


def render_manager_ai_page() -> None:
    """
    Main layout renderer for the Manager AI page.
    Coordinates filter prompts, details boxes, and compiled SQL records.
    """
    logger.info("Accessing Manager AI module page layout.")
    
    st.markdown(
        """
        <div class="ds-page-header">
            <div class="ds-page-eyebrow">✦ Module 5 &nbsp;·&nbsp; LangGraph &nbsp;·&nbsp; Text-to-SQL &nbsp;·&nbsp; Gemini</div>
            <div class="ds-page-title">Manager AI</div>
            <div class="ds-page-subtitle">
                Natural language interface that converts plain English questions into safe, read-only PostgreSQL queries
                via a LangGraph agent with automated SQL validation guardrails.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    service = ManagerAIService()

    # Sidebar: Query History Sessions Tracker
    st.sidebar.markdown('<div class="ds-section-title">Query Sessions</div>', unsafe_allow_html=True)
    
    # Load past user sessions
    sessions = service.get_user_sessions()
    
    if st.sidebar.button("➕ New Query Session", use_container_width=True):
        st.session_state["active_manager_session_id"] = None
        st.session_state["manager_ai_prompt_text"] = ""
        st.session_state["manager_ai_last_result"] = None
        st.rerun()

    active_session_id = st.session_state.get("active_manager_session_id")
    session_ids = [s["id"] for s in sessions]
    session_titles = [s["title"] for s in sessions]

    if sessions:
        if active_session_id not in session_ids:
            active_session_id = session_ids[0]
            st.session_state["active_manager_session_id"] = active_session_id
            
        selected_idx = session_ids.index(active_session_id)
        selected_title = st.sidebar.selectbox("Select Session", session_titles, index=selected_idx)
        active_session_id = session_ids[session_titles.index(selected_title)]
        st.session_state["active_manager_session_id"] = active_session_id
    else:
        active_session_id = None

    # Columns: Card info on left, agent inputs on right
    col_left, col_right = st.columns([1, 2])

    with col_left:
        SQLAgentUI.render_info_card()

    with col_right:
        prompt, submitted = SQLAgentForm.render_query_input()

        # When submit clicks are processed
        if submitted and prompt:
            try:
                results = service.run_agent_query(prompt, session_id=active_session_id)
                # Persist the active session so the sidebar list reflects the new session
                st.session_state["active_manager_session_id"] = results["session_id"]
                # Store results in session_state so they survive reruns and remain
                # visible until the user submits another query or navigates away.
                st.session_state["manager_ai_last_result"] = results
                # NOTE: st.rerun() has been intentionally removed here.
                # The old st.rerun() call immediately wiped the output that had just
                # been rendered by render_query_preview(), because a full script
                # rerun discards all local variables and re-executes from the top.
                # The session list in the sidebar refreshes naturally on the next
                # user interaction without needing a forced rerun.
            except Exception as e:
                logger.error(f"Error executing SQL Agent compilation query: {e}", exc_info=True)
                st.session_state["manager_ai_last_result"] = None
                st.error(f"Execution Error Details: {e}")

        # Render the persisted result every time the page paints, so it stays
        # visible after reruns triggered by sidebar interactions or other widgets.
        last_result = st.session_state.get("manager_ai_last_result")
        if last_result:
            SQLAgentUI.render_query_preview(last_result)

        # Render current session history
        if active_session_id:
            history = service.get_session_history(active_session_id)
            if history:
                st.markdown('<hr class="ds-section-divider">', unsafe_allow_html=True)
                st.markdown('<div class="ds-section-title">Session History</div>', unsafe_allow_html=True)
                for index, item in enumerate(reversed(history)):
                    st.markdown(f'<div style="font-size:0.85rem;font-weight:600;color:#94A3B8;margin-bottom:4px;">Q{len(history) - index}: {item["question"]}</div>', unsafe_allow_html=True)
                    if item["status"] in ["rejected", "error"]:
                        st.error(f"⚠️ {item['error']}")
                    else:
                        st.write(f"*Answer:* {item['answer']}")
                        with st.expander("Show code & output data", expanded=False):
                            st.code(item["compiled_sql"], language="sql")
                            st.dataframe(item["data"])
                    st.write("---")

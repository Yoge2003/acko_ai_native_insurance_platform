"""
Redesigned Chatbot page renderer using the ACKO Design System.
"""

import uuid
import logging
from datetime import datetime
import streamlit as st
from src.modules.chatbot.ui import ChatbotUI
from src.modules.chatbot.forms import ChatbotForm
from src.modules.chatbot.services import ChatbotService

logger = logging.getLogger(__name__)


def render_chatbot_page() -> None:
    """Premium chatbot page with modern two-column layout."""
    st.markdown(
        """
        <div class="ds-page-header">
            <div class="ds-page-eyebrow">✦ Module 1 &nbsp;·&nbsp; RAG Pipeline &nbsp;·&nbsp; Gemini 2.0 Flash</div>
            <div class="ds-page-title">AI Policy Chatbot</div>
            <div class="ds-page-subtitle">
                Retrieval-Augmented Generation powered by ChromaDB vector search and Google Gemini —
                answers policy coverage questions with source citations, latency tracking, and full conversation persistence.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    service = ChatbotService()
    sessions = service.get_user_sessions()

    col_left, col_right = st.columns([1, 2.5], gap="large")

    with col_left:
        ChatbotUI.render_info_card()

        st.markdown('<div class="ds-section-title" style="margin-top:1rem;">Sessions</div>', unsafe_allow_html=True)

        session_titles = ["+ New Conversation"]
        session_ids = [None]

        for s in sessions:
            try:
                created_str = s["created_at"].strftime("%b %d, %H:%M") if isinstance(s["created_at"], datetime) else str(s["created_at"])[:16]
            except Exception:
                created_str = ""
            session_titles.append(f"{s['title']} ({created_str})")
            session_ids.append(s["session_id"])

        active_idx = 0
        active_sess = st.session_state.get("active_session_id")
        if active_sess in session_ids:
            active_idx = session_ids.index(active_sess)

        selected_session = st.selectbox(
            "Session",
            options=session_titles,
            index=active_idx,
            label_visibility="collapsed",
        )

        target_idx = session_titles.index(selected_session)
        target_session_id = session_ids[target_idx]

        if target_session_id != st.session_state.get("active_session_id"):
            st.session_state["active_session_id"] = target_session_id
            if target_session_id:
                st.session_state["chat_history"] = service.get_chat_history(uuid.UUID(target_session_id))
            else:
                st.session_state["chat_history"] = []
            st.rerun()

        if target_session_id:
            if st.button("Delete Session", use_container_width=True):
                try:
                    service.chat_repo.delete(uuid.UUID(target_session_id))
                    service.db.commit()
                    st.session_state["active_session_id"] = None
                    st.session_state["chat_history"] = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {e}")

        st.markdown('<div class="ds-section-title" style="margin-top:1.5rem;">Retrieval Depth</div>', unsafe_allow_html=True)
        top_k = st.slider(
            "Top-K chunks",
            min_value=1, max_value=10, value=4, step=1,
            label_visibility="collapsed",
            help="Number of policy chunks retrieved from ChromaDB per query.",
        )

    with col_right:
        ChatbotUI.render_chat_log(st.session_state.get("chat_history", []))

        query, submitted = ChatbotForm.render_chat_input()

        if submitted and query:
            active_sess_id = st.session_state.get("active_session_id")
            if not active_sess_id:
                title = query[:30] + ("..." if len(query) > 30 else "")
                try:
                    new_id = service.create_chat_session(title=title)
                    st.session_state["active_session_id"] = str(new_id)
                    active_sess_id = str(new_id)
                except Exception as e:
                    st.error(f"Failed to create session: {e}")
                    st.stop()

            with st.spinner("Searching policy documents…"):
                try:
                    response_payload = service.generate_chat_response(
                        user_query=query,
                        session_id=active_sess_id,
                        k=top_k,
                    )
                    if "chat_history" not in st.session_state:
                        st.session_state["chat_history"] = []

                    st.session_state["chat_history"].append({"role": "user", "content": query, "citations": []})
                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": response_payload["answer"],
                        "citations": response_payload["citations"],
                        "latency_ms": response_payload["latency_ms"],
                        "tokens": response_payload["tokens"],
                    })
                except Exception as err:
                    st.error(f"Query failed: {err}")
                    logger.error(f"RAG error: {err}", exc_info=True)

            st.rerun()

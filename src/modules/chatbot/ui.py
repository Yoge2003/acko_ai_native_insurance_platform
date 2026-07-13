"""
Redesigned Chatbot UI — modern AI chat interface using the ACKO Design System.
"""

import streamlit as st
from typing import List, Dict, Any
from src.modules.chatbot.rag.vector_store import ChromaVectorStore


class ChatbotUI:
    """Renders premium chat bubbles, citations, and diagnostics using the DS."""

    @staticmethod
    def render_info_card() -> None:
        """Renders the RAG pipeline status card."""
        try:
            vector_store = ChromaVectorStore()
            chunk_count = vector_store.collection.count()
            status_html = f'<span class="ds-status-dot online"></span> ChromaDB Online &nbsp;·&nbsp; <strong style="color:#FFFFFF;">{chunk_count:,}</strong> document chunks'
            status_class = "ds-badge-success"
            status_label = "Live"
        except Exception as e:
            status_html = f'<span class="ds-status-dot offline"></span> ChromaDB Offline'
            status_class = "ds-badge-danger"
            status_label = "Offline"

        st.markdown(
            f"""
            <div class="ds-card" style="margin-bottom:1rem;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                    <div style="font-size:0.875rem;font-weight:600;color:#FFFFFF;font-family:'Poppins',sans-serif;">Policy Retrieval Engine</div>
                    <span class="ds-badge {status_class}">{status_label}</span>
                </div>
                <div style="font-size:0.82rem;color:#9CA3AF;line-height:1.6;margin-bottom:12px;font-family:'Poppins',sans-serif;">
                    ChromaDB vector similarity search paired with Gemini for citation-backed policy answers.
                </div>
                <div style="font-size:0.78rem;color:#9CA3AF;padding:10px 12px;background:rgba(0,0,0,0.25);border-radius:8px;border:1px solid rgba(255,255,255,0.07);font-family:'Poppins',sans-serif;">
                    {status_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def render_chat_log(messages: List[Dict[str, Any]]) -> None:
        """Renders the premium chat message thread."""
        st.markdown('<div class="ds-section-title">Conversation</div>', unsafe_allow_html=True)

        if not messages:
            st.markdown(
                """
                <div class="ds-chat-empty">
                    <div class="ds-chat-empty-icon">🤖</div>
                    <div class="ds-chat-empty-title">Policy Assistant Ready</div>
                    <div class="ds-chat-empty-sub">Ask anything about your coverage, claims, or policy terms.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Suggested prompts
            st.markdown('<div class="ds-section-title" style="margin-top:1.5rem;">Suggested Questions</div>', unsafe_allow_html=True)
            suggestions = [
                "What does my car insurance cover?",
                "How do I file a claim?",
                "What is the deductible for bike insurance?",
                "Does my policy cover third-party damage?",
            ]
            cols = st.columns(2)
            for i, s in enumerate(suggestions):
                with cols[i % 2]:
                    st.markdown(
                        f'<div style="padding:11px 16px;background:rgba(124,58,237,0.07);border:1px solid rgba(124,58,237,0.2);border-radius:10px;font-size:0.82rem;color:#D1D5DB;cursor:pointer;margin-bottom:8px;font-family:\'Poppins\',sans-serif;transition:all 0.2s ease;">{s}</div>',
                        unsafe_allow_html=True,
                    )
            return

        # Render messages
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                st.markdown(
                    f"""
                    <div class="ds-chat-user">
                        <div class="ds-chat-user-bubble">{content}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="ds-chat-ai">
                        <div class="ds-chat-ai-avatar">🛡️</div>
                        <div>
                            <div class="ds-chat-ai-bubble">{content}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Citations
                citations = msg.get("citations", [])
                if citations:
                    with st.expander(f"📖 {len(citations)} source{'s' if len(citations)>1 else ''} retrieved", expanded=False):
                        for src in citations:
                            st.markdown(
                                f"""
                                <div class="ds-citation">
                                    <div class="ds-citation-title">[{src.get('source_index')}] {src.get('filename')} — Page {src.get('page')}</div>
                                    <div style="font-size:0.72rem;color:#6366F1;margin-bottom:3px;">{src.get('section_heading','')}</div>
                                    <div class="ds-citation-excerpt">"{src.get('snippet','')}"</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                # Telemetry
                latency = msg.get("latency_ms")
                tokens = msg.get("tokens", {})
                if latency is not None:
                    total_tok = tokens.get("prompt_tokens", 0) + tokens.get("candidates_tokens", 0)
                    tok_str = f" · {total_tok:,} tokens" if total_tok > 0 else ""
                    st.markdown(
                        f'<div class="ds-chat-meta">⏱ {latency} ms{tok_str}</div>',
                        unsafe_allow_html=True,
                    )

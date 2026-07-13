"""
Service layer for the AI Policy Chatbot.
Handles integrated RAG operations, Gemini API queries, and PostgreSQL persistence.
"""

import time
import uuid
import logging
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.modules.chatbot.validators import ChatMessageValidator
from src.modules.chatbot.rag.vector_store import ChromaVectorStore
from src.modules.chatbot.rag.retriever import PolicyRetriever
from src.repositories.user import UserRepository
from src.repositories.chat import ChatRepository
from src.models.user import User
from src.models.chat import ChatSession

logger = logging.getLogger(__name__)

class ChatbotService:
    """
    Orchestrats RAG document retrieval context injection, Gemini LLM prompting,
    citation formatting, latency telemetry logging, and PostgreSQL state persistence.
    """
    def __init__(self, db: Optional[Session] = None, retriever: Optional[PolicyRetriever] = None) -> None:
        self.own_session = False
        
        # 1. Initialize SQLAlchemy Session
        if db is not None:
            self.db = db
        else:
            import src.database.database as db_module
            from src.database.session import SessionLocal
            if db_module.engine is not None:
                SessionLocal.configure(bind=db_module.engine)
            else:
                db_module.engine = db_module.create_db_engine()
                SessionLocal.configure(bind=db_module.engine)
            self.db = SessionLocal()
            self.own_session = True

        # 2. Initialize RAG components
        if retriever is not None:
            self.retriever = retriever
        else:
            self.vector_store = ChromaVectorStore()
            self.retriever = PolicyRetriever(self.vector_store)

        # 3. Create active repositories
        self.user_repo = UserRepository(self.db)
        self.chat_repo = ChatRepository(self.db)
        
        # Cache default user ID
        self.user_id = self._get_or_create_default_user_id()

    def _get_or_create_default_user_id(self) -> uuid.UUID:
        """
        Retrieves the UUID of the default client ("customer@acko.com"),
        creating it if not present in the database.
        """
        try:
            user = self.user_repo.get_by_email("customer@acko.com")
            if not user:
                new_user = User(
                    email="customer@acko.com",
                    full_name="Jane User Acko",
                    phone_number="+919876543210",
                    role="customer"
                )
                user = self.user_repo.create(new_user)
                self.db.commit()
            return user.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error obtaining default user ID: {e}", exc_info=True)
            # Temporary fallback identifier
            return uuid.uuid4()

    def create_chat_session(self, title: str = "New Policy Inquiry") -> uuid.UUID:
        """
        Creates a new Chat Session container in PostgreSQL.
        """
        try:
            new_session = ChatSession(
                user_id=self.user_id,
                title=title
            )
            session = self.chat_repo.create(new_session)
            self.db.commit()
            logger.info(f"Created ChatSession: {session.id} with title: {title}")
            return session.id
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create chat session: {e}", exc_info=True)
            raise e

    def get_user_sessions(self) -> List[Dict[str, Any]]:
        """
        Retrieves all chat sessions for the active user.
        """
        try:
            sessions = self.chat_repo.get_sessions_by_user(self.user_id)
            # Sort by creation date descending
            sessions.sort(key=lambda s: s.created_at, reverse=True)
            return [
                {
                    "session_id": str(s.id),
                    "title": s.title,
                    "created_at": s.created_at
                } 
                for s in sessions
            ]
        except Exception as e:
            logger.error(f"Failed to query chat sessions list: {e}", exc_info=True)
            return []

    def get_chat_history(self, session_id: uuid.UUID) -> List[Dict[str, Any]]:
        """
        Loads message records of a session from PostgreSQL.
        """
        try:
            messages = self.chat_repo.get_messages_by_session(session_id)
            history = []
            for msg in messages:
                history.append({
                    "role": msg.role,
                    "content": msg.message,
                    "citations": msg.retrieved_sources or [],
                    "created_at": msg.created_at
                })
            return history
        except Exception as e:
            logger.error(f"Failed to load chat history for session {session_id}: {e}", exc_info=True)
            return []

    def generate_chat_response(
        self,
        user_query: str,
        session_id: str,
        k: int = 4
    ) -> Dict[str, Any]:
        """
        Retrieves documents from ChromaDB, constructs prompts, invokes Gemini model,
        computes citations, measures performance latency, and persists data.
        """
        start_time = time.perf_counter()
        
        # 1. Input Validation
        validator = ChatMessageValidator(user_query=user_query, session_id=session_id)
        sanitized_query = validator.user_query.strip()
        parsed_session_id = uuid.UUID(session_id) if session_id else self.create_chat_session(title=f"Chat: {sanitized_query[:25]}")
        
        # Save user message to database
        self.chat_repo.create_message(
            session_id=parsed_session_id,
            role="user",
            message=sanitized_query
        )

        # 2. Context Retrieval
        retrieved_docs = self.retriever.retrieve(sanitized_query, k=k)
        
        # 3. Citation Formatting
        citations = []
        for idx, doc in enumerate(retrieved_docs):
            citations.append({
                "source_index": idx + 1,
                "filename": doc.metadata.get("filename", "Unknown Policy Document"),
                "page": int(doc.metadata.get("page", 0)),
                "section_heading": doc.metadata.get("section_heading", "General Terms"),
                "snippet": doc.page_content[:200]
            })

        # 4. Prompt Engineering
        context_blocks = []
        for idx, doc in enumerate(retrieved_docs):
            filename = doc.metadata.get("filename", "unknown")
            page_no = doc.metadata.get("page", 0)
            heading = doc.metadata.get("section_heading", "general")
            context_blocks.append(
                f"--- CONTEXT BLOCK {idx+1} ---\n"
                f"Document: {filename} (Page {page_no})\n"
                f"Section: {heading}\n"
                f"Text:\n{doc.page_content}\n"
                "-------------------------\n"
            )
            
        context_str = "\n".join(context_blocks)
        
        system_instructions = (
            "You are the ACKO Insurance Policy Bot. Your job is to answer the user's questions "
            "using ONLY the policy document contexts provided. Be thorough, clear, and professional.\n\n"
            "Format Guidelines:\n"
            "1. When referencing terms from a context block, cite the page number and document exactly, e.g. "
            "\"(Page 3, Acko_Health_Insurance_Policy_TC.pdf)\" or \"[Acko_Insurance_FAQs.pdf, Page 1]\".\n"
            "2. If the context does not contain enough information to formulate an accurate answer, state: "
            "\"I do not have sufficient information in the loaded policy documentation to verify this.\"\n"
            "3. Rely strictly on facts in the context blocks. Do not hallucinate or manufacture coverages."
        )
        
        full_prompt = (
            f"{system_instructions}\n\n"
            f"Retrieved Policy Contexts:\n{context_str}\n\n"
            f"User Question: {sanitized_query}\n\n"
            "Answer:"
        )

        # Check API key configuration first (before try/catch to raise configuration error directly if missing in app runtime)
        import sys
        is_testing = "pytest" in sys.modules or any("unittest" in m for m in sys.modules)
        if not is_testing:
            if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
                logger.error("Configuration Error: GEMINI_API_KEY is not defined in environment settings.")
                raise ValueError(
                    "Valid GEMINI_API_KEY is not defined in application environment configurations. "
                    "Please configure a valid GEMINI_API_KEY in your .env file."
                )

        # 5. Generative Inference with Fallback Action
        assistant_response = ""
        token_info = {"prompt_tokens": 0, "candidates_tokens": 0}
        
        # gemini-2.0-flash is configured for high free quota limits
        model_name = "gemini-2.0-flash"
        api_key_detected = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here")
        chunk_count = len(retrieved_docs)
        prompt_len = len(full_prompt)
        
        logger.info(f"GEMINI_API_KEY detected: {api_key_detected}")
        logger.info(f"Model name: {model_name}")
        logger.info(f"Prompt length: {prompt_len}")
        logger.info(f"Retrieved chunk count: {chunk_count}")

        # Try without the try/except around the whole block to let exceptions bubble up.
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ValueError("Valid GEMINI_API_KEY is not defined in application environment configurations.")
            
        import google.generativeai as genai
        import google.api_core.exceptions
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        model = genai.GenerativeModel(model_name)
        
        @retry(
            reraise=True,
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=4),
            retry=retry_if_exception_type((
                google.api_core.exceptions.ResourceExhausted,
                google.api_core.exceptions.ServiceUnavailable,
                google.api_core.exceptions.DeadlineExceeded
            )),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
        def _generate_with_retry():
            logger.info("Calling generate_content()")
            try:
                # We specifically wrap this call to print traceback and raise
                response = model.generate_content(full_prompt)
                return response
            except Exception as e:
                import traceback
                logger.exception("FULL GEMINI ERROR")
                print(traceback.format_exc())
                raise
            
        response = _generate_with_retry()
        assistant_response = response.text
        
        # Track Token Metrics
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            token_info["prompt_tokens"] = response.usage_metadata.prompt_token_count
            token_info["candidates_tokens"] = response.usage_metadata.candidates_token_count
        
        latency_ms = int((time.perf_counter() - start_time) * 1000.0)
        logger.info(
            f"Gemini API call succeeded. Status: success. Latency: {latency_ms}ms, "
            f"Tokens: {token_info}"
        )

        latency_ms = int((time.perf_counter() - start_time) * 1000.0)

        # 6. Persist assistant output message
        self.chat_repo.create_message(
            session_id=parsed_session_id,
            role="assistant",
            message=assistant_response,
            retrieved_sources=citations
        )
        
        return {
            "session_id": str(parsed_session_id),
            "role": "assistant",
            "answer": assistant_response,
            "citations": citations,
            "latency_ms": latency_ms,
            "tokens": token_info,
            "status": "success"
        }

    def __del__(self) -> None:
        if hasattr(self, "own_session") and self.own_session and hasattr(self, "db") and self.db:
            self.db.close()
            logger.info("ChatbotService database connection session closed.")

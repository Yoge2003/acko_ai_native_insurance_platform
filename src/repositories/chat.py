"""
ChatRepository handling database query operations for the ChatSession and ChatMessage models.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.chat import ChatMessage, ChatSession
from src.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    """
    Repository for the ChatSession model carrying custom data retrieval routines,
    including handling associated chat messages.
    """

    def __init__(self, db: Session) -> None:
        """
        Initializes ChatRepository.

        Args:
            db: Active SQLAlchemy Database Transaction session.
        """
        super().__init__(ChatSession, db)

    def get_sessions_by_user(self, user_id: uuid.UUID) -> List[ChatSession]:
        """
        Retrieves all Chat Sessions belonging to a User.

        Args:
            user_id: UUID of the User.

        Returns:
            List of matching ChatSession instances.
        """
        try:
            stmt = select(self.model).where(self.model.user_id == user_id)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting ChatSessions for user ID {user_id}: {e}", exc_info=True)
            raise e

    def create_message(
        self,
        session_id: uuid.UUID,
        role: str,
        message: str,
        retrieved_sources: Optional[List[Dict[str, Any]]] = None,
        gemini_response: Optional[str] = None,
    ) -> ChatMessage:
        """
        Creates and persists a new ChatMessage linked to a session ID. Handles transaction.

        Args:
            session_id: UUID of the target ChatSession.
            role: The author role ('user', 'assistant', 'system').
            message: Raw message text sent.
            retrieved_sources: Optional metadata list of query sources retrieved.
            gemini_response: Optional LLM response generated.

        Returns:
            The created ChatMessage model instance.
        """
        try:
            db_msg = ChatMessage(
                session_id=session_id,
                role=role,
                message=message,
                retrieved_sources=retrieved_sources,
                gemini_response=gemini_response
            )
            self.db.add(db_msg)
            self.db.commit()
            self.db.refresh(db_msg)
            self.logger.info(f"Successfully added chat message for Session ID {session_id}.")
            return db_msg
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to create ChatMessage for session ID {session_id}: {e}", exc_info=True)
            raise e

    def get_messages_by_session(self, session_id: uuid.UUID) -> List[ChatMessage]:
        """
        Retrieves all messages inside a ChatSession sorted in ascending order of arrival.

        Args:
            session_id: UUID of the ChatSession.

        Returns:
            List of ChatMessage instances.
        """
        try:
            stmt = select(ChatMessage).where(
                ChatMessage.session_id == session_id
            ).order_by(
                ChatMessage.created_at.asc()
            )
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting Messages for chat session ID {session_id}: {e}", exc_info=True)
            raise e

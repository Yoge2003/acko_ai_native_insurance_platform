"""
ChatService containing business logic for support sessions creation and message additions.
"""

import uuid
from typing import Any, Dict, List, Optional
from src.models.chat import ChatMessage, ChatSession
from src.repositories.chat import ChatRepository
from src.repositories.user import UserRepository
from src.services.base_service import BaseService
from src.services.exceptions import ResourceNotFoundError, ValidationError


class ChatService(BaseService[ChatRepository]):
    """
    ChatService aggregating session configurations, prompt inputs, and history records.
    """

    def __init__(self, repository: ChatRepository, user_repository: UserRepository) -> None:
        """
        Initializes ChatService.

        Args:
            repository: Injected ChatRepository instance.
            user_repository: Injected UserRepository instance.
        """
        super().__init__(repository)
        self.user_repository = user_repository

    def create_session(self, user_id: uuid.UUID, title: str) -> ChatSession:
        """
        Creates and starts a new customer support chat session.

        Args:
            user_id: Owner User ID.
            title: Conversational title or context line.

        Returns:
            The created ChatSession model instance.

        Raises:
            ResourceNotFoundError: If targeted user owner does not exist.
            ValidationError: If title string is unspecified.
        """
        self.logger.info(f"Opening chat session for user ID {user_id} titled: {title}")

        if not title or not title.strip():
            raise ValidationError("Chat session title cannot be empty.")

        # Business validation: Owner verification check
        if not self.user_repository.exists(id=user_id):
            raise ResourceNotFoundError(f"User owner with ID {user_id} does not exist.")

        session = ChatSession(
            user_id=user_id,
            title=title.strip()
        )
        try:
            return self.repository.create(session)
        except Exception as e:
            self.logger.error(f"Error opening ChatSession: {e}", exc_info=True)
            raise e

    def get_session_by_id(self, session_id: uuid.UUID) -> ChatSession:
        """
        Retrieves a specific ChatSession profile by its UUID tracking key.

        Args:
            session_id: UUID of ChatSession.

        Returns:
            The ChatSession instance.

        Raises:
            ResourceNotFoundError: If session ID is not indexed.
        """
        session = self.repository.get_by_id(session_id)
        if session is None:
            self.logger.warning(f"ChatSession not found with ID {session_id}")
            raise ResourceNotFoundError(f"ChatSession with ID {session_id} does not exist.")
        return session

    def get_user_sessions(self, user_id: uuid.UUID) -> List[ChatSession]:
        """
        Lists all chat history modules opened by a specific user.

        Args:
            user_id: Owner User ID.

        Returns:
            List of matching ChatSessions.
        """
        return self.repository.get_sessions_by_user(user_id)

    def add_message(
        self,
        session_id: uuid.UUID,
        role: str,
        message: str,
        retrieved_sources: Optional[List[Dict[str, Any]]] = None,
        gemini_response: Optional[str] = None,
    ) -> ChatMessage:
        """
        Appends and links a new message/response block into an active ChatSession.

        Args:
            session_id: UUID of ChatSession.
            role: Sender role ('user', 'assistant', 'system').
            message: Sent textual payload.
            retrieved_sources: Optional list of document sources.
            gemini_response: Optional system answer generated.

        Returns:
            The created ChatMessage.

        Raises:
            ResourceNotFoundError: If the Session ID is missing.
            ValidationError: If roles or message parameters are invalid.
        """
        self.logger.info(f"Appending chat message role '{role}' to session ID {session_id}")

        # Input validation
        if not message or not message.strip():
            raise ValidationError("ChatMessage text cannot be empty.")
        
        role = role.strip().lower()
        valid_roles = {"user", "assistant", "system"}
        if role not in valid_roles:
            raise ValidationError(f"ChatMessage role must represent one of: {valid_roles}")

        # Business validation: Session existence verified
        if not self.repository.exists(id=session_id):
            raise ResourceNotFoundError(f"Target ChatSession ID {session_id} was not found.")

        try:
            return self.repository.create_message(
                session_id=session_id,
                role=role,
                message=message.strip(),
                retrieved_sources=retrieved_sources,
                gemini_response=gemini_response
            )
        except Exception as e:
            self.logger.error(f"Error saving message block: {e}", exc_info=True)
            raise e

    def get_session_messages(self, session_id: uuid.UUID) -> List[ChatMessage]:
        """
        Extracts clean chronological array of messages belonging to a ChatSession.

        Args:
            session_id: UUID of ChatSession.

        Returns:
            List of ChatMessages sorted in order of creation.

        Raises:
            ResourceNotFoundError: If session ID is not indexed.
        """
        # Ensure session exists
        self.get_session_by_id(session_id)
        return self.repository.get_messages_by_session(session_id)

"""
Validation schemas for the AI Policy Chatbot module.
Defines schemas using Pydantic to validate policy chat queries and session metrics.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ChatMessageValidator(BaseModel):
    """
    Validates structural correctness of user chat queries before routing.
    """
    user_query: str = Field(..., min_length=1, max_length=2000, description="The chatbot input text query submitted by the user")
    session_id: Optional[str] = Field(default=None, description="Optional unique identifier of the chat conversation session")

    @field_validator("user_query")
    @classmethod
    def check_non_empty_content(cls, val: str) -> str:
        """Verifies that the character string doesn't consist of pure whitespace."""
        stripped = val.strip()
        if not stripped:
            raise ValueError("Chat message query cannot be empty or pure whitespace.")
        return stripped

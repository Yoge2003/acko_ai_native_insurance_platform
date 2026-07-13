"""
Validation schemas for the Manager AI module.
Defines schemas using Pydantic to validate Natural Language SQL prompts.
"""

from pydantic import BaseModel, Field, field_validator


class SQLAgentQueryValidator(BaseModel):
    """
    Validates natural language queries target for relational database execution.
    """
    user_prompt: str = Field(..., min_length=5, max_length=1000, description="Natural language database query prompt")

    @field_validator("user_prompt")
    @classmethod
    def check_non_empty_content(cls, val: str) -> str:
        """Verifies query prompt content is not empty."""
        cleaned = val.strip()
        if not cleaned:
            raise ValueError("Prompt query cannot be empty or pure spacing characters.")
        return cleaned

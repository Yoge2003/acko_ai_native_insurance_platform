import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.policy import Policy
    from src.models.image import UploadedImage



class Claim(Base):
    """
    SQLAlchemy ORM model representing an Insurance Claim.
    """
    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    claim_amount: Mapped[float] = mapped_column(Float, nullable=False)
    damage_summary: Mapped[str] = mapped_column(Text, nullable=False)
    gemini_analysis_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )
    predicted_decision: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    approval_probability: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    claim_status: Mapped[str] = mapped_column(String(50), default="pending")
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="claims")
    policy: Mapped["Policy"] = relationship("Policy", back_populates="claims")
    uploaded_images: Mapped[List["UploadedImage"]] = relationship(
        "UploadedImage",
        back_populates="claim",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Claim {self.id} (Status: {self.claim_status}, Amount: {self.claim_amount})>"

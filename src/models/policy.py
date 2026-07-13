import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.claim import Claim



class Policy(Base):
    """
    SQLAlchemy ORM model representing an Insurance Policy.
    """
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    policy_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_make: Mapped[str] = mapped_column(String(100), nullable=False)
    vehicle_model: Mapped[str] = mapped_column(String(100), nullable=False)
    registration_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    idv: Mapped[float] = mapped_column(Float, nullable=False)
    premium: Mapped[float] = mapped_column(Float, nullable=False)
    policy_type: Mapped[str] = mapped_column(String(100), nullable=False)
    coverage_type: Mapped[str] = mapped_column(String(100), nullable=False)
    policy_start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    policy_end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="policies")
    claims: Mapped[List["Claim"]] = relationship(
        "Claim",
        back_populates="policy",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Policy {self.policy_number} ({self.status})>"

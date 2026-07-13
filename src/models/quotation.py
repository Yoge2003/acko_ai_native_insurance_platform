import uuid
from datetime import datetime
from typing import Any, Dict, TYPE_CHECKING
from sqlalchemy import String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.user import User



class Quotation(Base):
    """
    SQLAlchemy ORM model representing a vehicle premium quotation query.
    """
    __tablename__ = "quotations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    quotation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    input_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    predicted_premium: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quotations")

    def __repr__(self) -> str:
        return f"<Quotation {self.id} (Premium: {self.predicted_premium})>"

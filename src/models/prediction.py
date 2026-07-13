import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class PredictionLog(Base):
    """
    SQLAlchemy ORM model representing model prediction logs.
    Used for monitoring, auditing latency, and model drift analysis.
    """
    __tablename__ = "prediction_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    prediction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    input_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )
    output_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<PredictionLog {self.id} ({self.prediction_type} v{self.model_version})>"

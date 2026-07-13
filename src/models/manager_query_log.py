import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Text, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.user import User


class ManagerSession(Base):
    """
    SQLAlchemy ORM model representing a chat/inquiry session for the Manager AI tool.
    """
    __tablename__ = "manager_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    queries: Mapped[list["ManagerQueryLog"]] = relationship(
        "ManagerQueryLog",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<ManagerSession {self.id} (Title: {self.title})>"


class ManagerQueryLog(Base):
    """
    SQLAlchemy ORM model representing an individual executed query log under a ManagerSession.
    """
    __tablename__ = "manager_query_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("manager_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    generated_sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # 'success', 'warning', 'error', 'rejected'
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    # Relationships
    session: Mapped["ManagerSession"] = relationship("ManagerSession", back_populates="queries")

    def __repr__(self) -> str:
        return f"<ManagerQueryLog {self.id} (Status: {self.status})>"

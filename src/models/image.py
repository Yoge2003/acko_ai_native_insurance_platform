import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.claim import Claim



class UploadedImage(Base):
    """
    SQLAlchemy ORM model representing upload attachments supporting insurance Claims.
    """
    __tablename__ = "uploaded_images"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    claim_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    local_path: Mapped[str] = mapped_column(String(512), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(512), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    # Relationships
    claim: Mapped["Claim"] = relationship("Claim", back_populates="uploaded_images")

    def __repr__(self) -> str:
        return f"<UploadedImage {self.id} (Original: {self.original_filename})>"

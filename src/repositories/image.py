"""
UploadedImageRepository handling database query operations for the UploadedImage model.
"""

import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.image import UploadedImage
from src.repositories.base import BaseRepository


class UploadedImageRepository(BaseRepository[UploadedImage]):
    """
    Repository for the UploadedImage model carrying custom data retrieval routines.
    """

    def __init__(self, db: Session) -> None:
        """
        Initializes UploadedImageRepository.

        Args:
            db: Active SQLAlchemy Database Transaction session.
        """
        super().__init__(UploadedImage, db)

    def get_images_by_claim(self, claim_id: uuid.UUID) -> List[UploadedImage]:
        """
        Retrieves all uploaded images linked to a specific Claim ID.

        Args:
            claim_id: UUID of the claim.

        Returns:
            List of matching UploadedImage model instances.
        """
        try:
            stmt = select(self.model).where(self.model.claim_id == claim_id)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting UploadedImages for claim ID {claim_id}: {e}", exc_info=True)
            raise e

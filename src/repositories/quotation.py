"""
QuotationRepository handling database query operations for the Quotation model.
"""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.quotation import Quotation
from src.repositories.base import BaseRepository


class QuotationRepository(BaseRepository[Quotation]):
    """
    Repository for the Quotation model carrying custom data retrieval routines.
    """

    def __init__(self, db: Session) -> None:
        """
        Initializes QuotationRepository.

        Args:
            db: Active SQLAlchemy Database Transaction session.
        """
        super().__init__(Quotation, db)

    def get_by_user_id(self, user_id: uuid.UUID) -> List[Quotation]:
        """
        Retrieves all Quotations associated with a specific User.

        Args:
            user_id: UUID of the requesting User.

        Returns:
            List of matching Quotation instances.
        """
        try:
            stmt = select(self.model).where(self.model.user_id == user_id)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting Quotations for user ID {user_id}: {e}", exc_info=True)
            raise e

    def get_latest_quotation(self, user_id: uuid.UUID) -> Optional[Quotation]:
        """
        Retrieves the latest premium quotation record generated for a specific User.

        Args:
            user_id: UUID of the requesting User.

        Returns:
            The most recent Quotation instance if any exist, otherwise None.
        """
        try:
            stmt = select(self.model).where(
                self.model.user_id == user_id
            ).order_by(
                self.model.prediction_timestamp.desc()
            ).limit(1)
            return self.db.scalars(stmt).first()
        except Exception as e:
            self.logger.error(f"Error getting latest Quotation for user ID {user_id}: {e}", exc_info=True)
            raise e

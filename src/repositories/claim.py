"""
ClaimRepository handling database query operations for the Claim model.
"""

import uuid
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.models.claim import Claim
from src.repositories.base import BaseRepository


class ClaimRepository(BaseRepository[Claim]):
    """
    Repository for the Claim model carrying custom data retrieval routines.
    """

    def __init__(self, db: Session) -> None:
        """
        Initializes ClaimRepository.

        Args:
            db: Active SQLAlchemy Database Transaction session.
        """
        super().__init__(Claim, db)

    def get_by_user_id(self, user_id: uuid.UUID) -> List[Claim]:
        """
        Retrieves all claims submitted by a specific User.

        Args:
            user_id: UUID of the Claimant User.

        Returns:
            List of matching Claim model instances.
        """
        try:
            stmt = select(self.model).where(self.model.user_id == user_id)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting Claims for user ID {user_id}: {e}", exc_info=True)
            raise e

    def get_by_policy_id(self, policy_id: uuid.UUID) -> List[Claim]:
        """
        Retrieves all claims filed against a specific Insurance Policy.

        Args:
            policy_id: UUID of the Policy.

        Returns:
            List of matching Claim instances.
        """
        try:
            stmt = select(self.model).where(self.model.policy_id == policy_id)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting Claims for policy ID {policy_id}: {e}", exc_info=True)
            raise e

    def get_claims_by_status(self, status: str) -> List[Claim]:
        """
        Retrieves claims matching a given status ('pending', 'approved', 'rejected').

        Args:
            status: Targets claim workflow status string.

        Returns:
            List of matching Claim instances.
        """
        try:
            stmt = select(self.model).where(self.model.claim_status == status)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting Claims by status {status}: {e}", exc_info=True)
            raise e

    def get_total_claimed_amount(self, user_id: uuid.UUID) -> float:
        """
        Computes the total sum of claim amounts asked by a specific User ID.

        Args:
            user_id: UUID of the Claimant User.

        Returns:
            The sum total of claim_amount, defaulting to 0.0 if no claims exist.
        """
        try:
            stmt = select(func.sum(self.model.claim_amount)).where(self.model.user_id == user_id)
            total = self.db.scalar(stmt)
            return float(total) if total is not None else 0.0
        except Exception as e:
            self.logger.error(f"Error summing claims for user ID {user_id}: {e}", exc_info=True)
            raise e

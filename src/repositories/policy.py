"""
PolicyRepository handling database query operations for the Policy model.
"""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.policy import Policy
from src.repositories.base import BaseRepository


class PolicyRepository(BaseRepository[Policy]):
    """
    Repository for the Policy model carrying custom data retrieval routines.
    """

    def __init__(self, db: Session) -> None:
        """
        Initializes PolicyRepository.

        Args:
            db: Active SQLAlchemy Database Transaction session.
        """
        super().__init__(Policy, db)

    def get_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """
        Retrieves a Policy using its unique Policy Number.

        Args:
            policy_number: Unique insurance policy number.

        Returns:
            The Policy instance if found, otherwise None.
        """
        try:
            stmt = select(self.model).where(self.model.policy_number == policy_number)
            return self.db.scalars(stmt).first()
        except Exception as e:
            self.logger.error(f"Error getting Policy by policy number {policy_number}: {e}", exc_info=True)
            raise e

    def get_by_user_id(self, user_id: uuid.UUID) -> List[Policy]:
        """
        Retrieves all Policies assigned to a specific User.

        Args:
            user_id: UUID of the User owner.

        Returns:
            List of matching Policy instances.
        """
        try:
            stmt = select(self.model).where(self.model.user_id == user_id)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting Policies for user ID {user_id}: {e}", exc_info=True)
            raise e

    def get_active_policies_by_user(self, user_id: uuid.UUID) -> List[Policy]:
        """
        Retrieves active Policies for a given User.

        Args:
            user_id: UUID of the User owner.

        Returns:
            List of active Policy instances for the user.
        """
        try:
            stmt = select(self.model).where(
                self.model.user_id == user_id,
                self.model.status == "active"
            )
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting active Policies for user ID {user_id}: {e}", exc_info=True)
            raise e

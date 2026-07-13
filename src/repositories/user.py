"""
UserRepository handling database query operations for the User model.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for the User model carrying custom data retrieval routines.
    """

    def __init__(self, db: Session) -> None:
        """
        Initializes UserRepository.

        Args:
            db: Active SQLAlchemy Database Transaction session.
        """
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a User object using their unique registered email address.

        Args:
            email: Registered User email.

        Returns:
            The User instance if matching record exists, otherwise None.
        """
        try:
            stmt = select(self.model).where(self.model.email == email)
            return self.db.scalars(stmt).first()
        except Exception as e:
            self.logger.error(f"Error getting User by email {email}: {e}", exc_info=True)
            raise e

    def get_by_role(self, role: str) -> List[User]:
        """
        Retrieves all Users associated with a specific system role.

        Args:
            role: The targeted role string ('customer', 'admin', etc.).

        Returns:
            List of matching User model instances.
        """
        try:
            stmt = select(self.model).where(self.model.role == role)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting Users by role {role}: {e}", exc_info=True)
            raise e

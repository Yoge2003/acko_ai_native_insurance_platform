"""
UserService containing business logic for User accounts management, registration, and lookups.
"""

import re
import uuid
from typing import List, Optional, Tuple
from src.models.user import User
from src.repositories.user import UserRepository
from src.services.base_service import BaseService
from src.services.exceptions import (
    DuplicateResourceError,
    ResourceNotFoundError,
    ValidationError,
)


class UserService(BaseService[UserRepository]):
    """
    UserService encapsulating business logic rules for user registrations and account management.
    """

    def __init__(self, repository: UserRepository) -> None:
        """
        Initializes the UserService with injected UserRepository.

        Args:
            repository: UserRepository database transaction container.
        """
        super().__init__(repository)

    def register_user(
        self,
        full_name: str,
        email: str,
        phone_number: Optional[str] = None,
        role: str = "customer",
    ) -> User:
        """
        Registers a new user on the insurance platform.

        Args:
            full_name: User's complete legal name.
            email: Unique registered email address.
            phone_number: Optional registry phone number.
            role: Application role ('customer', 'agent', 'admin').

        Returns:
            The created User instance.

        Raises:
            ValidationError: If names, emails, roles, or phone inputs are malformed.
            DuplicateResourceError: If the email has already been registered.
        """
        self.logger.info(f"Attempting to register user with email {email}")

        # Input validation
        if not full_name or not full_name.strip():
            raise ValidationError("User's full name must be specified.")
        
        email = email.strip()
        if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            raise ValidationError(f"Invalid email address provided: {email}")

        valid_roles = {"customer", "agent", "admin", "claims_officer", "underwriter", "manager", "administrator"}
        if role not in valid_roles:
            raise ValidationError(f"Role must be one of {valid_roles}. Received: {role}")

        # Business validation: Unique email check
        existing_user = self.repository.get_by_email(email)
        if existing_user is not None:
            self.logger.warning(f"Registration failed: email {email} is already in use.")
            raise DuplicateResourceError(f"A user with email {email} is already registered.")

        # Creation
        new_user = User(
            full_name=full_name.strip(),
            email=email,
            phone_number=phone_number.strip() if phone_number else None,
            role=role,
        )
        try:
            return self.repository.create(new_user)
        except Exception as e:
            self.logger.error(f"Error executing registration for user {email}: {e}", exc_info=True)
            raise e

    def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """
        Retrieves a user by their unique database UUID.

        Args:
            user_id: UUID of user to retrieve.

        Returns:
            The User instance if found.

        Raises:
            ResourceNotFoundError: If the user ID does not exist in the database.
        """
        user = self.repository.get_by_id(user_id)
        if user is None:
            self.logger.warning(f"User not found with ID {user_id}")
            raise ResourceNotFoundError(f"User with ID {user_id} was not found.")
        return user

    def get_user_by_email(self, email: str) -> User:
        """
        Retrieves a user by their registered email address.

        Args:
            email: Email address of user to view.

        Returns:
            The User instance if found.

        Raises:
            ResourceNotFoundError: If the email does not exist in the database.
        """
        user = self.repository.get_by_email(email.strip())
        if user is None:
            self.logger.warning(f"User not found with email {email}")
            raise ResourceNotFoundError(f"User with email {email} does not exist.")
        return user

    def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        """
        Paginates users with an optional role filter.

        Args:
            page: Pagination page number.
            per_page: Items to return per page.
            role: Optional role string to filter users.

        Returns:
            A tuple of (list of User records, total count).
        """
        filters = {}
        if role:
            filters["role"] = role
        return self.repository.paginate(page=page, per_page=per_page, filters=filters)

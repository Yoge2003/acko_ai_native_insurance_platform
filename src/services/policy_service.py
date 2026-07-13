"""
PolicyService containing business logic for Policy registration, date verification, and status validation.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from src.models.policy import Policy
from src.repositories.policy import PolicyRepository
from src.repositories.user import UserRepository
from src.services.base_service import BaseService
from src.services.exceptions import (
    BusinessRuleViolationError,
    DuplicateResourceError,
    ResourceNotFoundError,
    ValidationError,
)


class PolicyService(BaseService[PolicyRepository]):
    """
    PolicyService wrapping registration logic, dates validation, and active status validation.
    """

    def __init__(self, repository: PolicyRepository, user_repository: UserRepository) -> None:
        """
        Initializes PolicyService.

        Args:
            repository: Injected PolicyRepository instance.
            user_repository: Injected UserRepository instance to verify policy owners.
        """
        super().__init__(repository)
        self.user_repository = user_repository

    def create_policy(
        self,
        user_id: uuid.UUID,
        policy_number: str,
        vehicle_type: str,
        vehicle_make: str,
        vehicle_model: str,
        registration_number: str,
        idv: float,
        premium: float,
        policy_type: str,
        coverage_type: str,
        policy_start_date: datetime,
        policy_end_date: datetime,
        status: str = "active",
    ) -> Policy:
        """
        Registers a new policy for a verified User.

        Args:
            user_id: Owner User ID.
            policy_number: Unique policy alphanumeric code.
            vehicle_type: E.g. 'car' or 'bike'.
            vehicle_make: Brand of the vehicle.
            vehicle_model: Model name.
            registration_number: RTO registration number.
            idv: Insured Declared Value. Must be positive.
            premium: Policy premium amount. Must be positive.
            policy_type: E.g., 'comprehensive'.
            coverage_type: Cover detail classification.
            policy_start_date: Coverage commencement timestamp.
            policy_end_date: Coverage closure timestamp.
            status: Initial status state.

        Returns:
            The created Policy database instance.

        Raises:
            ResourceNotFoundError: If the user ID does not exist in the system.
            ValidationError: If names/amounts/intervals are invalid.
            DuplicateResourceError: If the policy number conflicts with an existing Policy.
        """
        self.logger.info(f"Attempting to create policy key {policy_number} for user ID {user_id}")

        # Input validation
        if not policy_number or not policy_number.strip():
            raise ValidationError("Policy number must be specified.")
        if idv <= 0:
            raise ValidationError("IDV must be a positive value.")
        if premium <= 0:
            raise ValidationError("Premium must be a positive value.")
        if policy_start_date >= policy_end_date:
            raise ValidationError("policy_start_date must occur before policy_end_date.")

        # Business validation: Owner existence check
        if not self.user_repository.exists(id=user_id):
            raise ResourceNotFoundError(f"User owner with ID {user_id} does not exist.")

        # Business validation: policy duplication check
        existing_policy = self.repository.get_by_policy_number(policy_number.strip())
        if existing_policy is not None:
            raise DuplicateResourceError(f"A policy with number {policy_number} already exists.")

        policy = Policy(
            user_id=user_id,
            policy_number=policy_number.strip(),
            vehicle_type=vehicle_type.strip(),
            vehicle_make=vehicle_make.strip(),
            vehicle_model=vehicle_model.strip(),
            registration_number=registration_number.strip(),
            idv=idv,
            premium=premium,
            policy_type=policy_type.strip(),
            coverage_type=coverage_type.strip(),
            policy_start_date=policy_start_date,
            policy_end_date=policy_end_date,
            status=status,
        )
        try:
            return self.repository.create(policy)
        except Exception as e:
            self.logger.error(f"Error registering Policy {policy_number}: {e}", exc_info=True)
            raise e

    def get_policy_by_id(self, policy_id: uuid.UUID) -> Policy:
        """
        Retrieves a policy by its UUID.

        Args:
            policy_id: UUID of policy to retrieve.

        Returns:
            The Policy instance if located.

        Raises:
            ResourceNotFoundError: If the policy ID is not present in the system.
        """
        policy = self.repository.get_by_id(policy_id)
        if policy is None:
            self.logger.warning(f"Policy not found with ID {policy_id}")
            raise ResourceNotFoundError(f"Policy with ID {policy_id} was not found.")
        return policy

    def get_policies_by_user(self, user_id: uuid.UUID) -> List[Policy]:
        """
        Retrieves list of policies belonging to a user owner.

        Args:
            user_id: UUID of Owner User.

        Returns:
            List of matching Policy instances.
        """
        return self.repository.get_by_user_id(user_id)

    def validate_policy_active(self, policy_id: uuid.UUID) -> bool:
        """
        Evaluates whether a Policy is active based on state and current date coverage.
        Updates model status dynamically to 'expired' if the active coverage window has closed.

        Args:
            policy_id: UUID of the policy to check.

        Returns:
            True if Policy status remains active, otherwise False.
        """
        policy = self.get_policy_by_id(policy_id)
        now = datetime.utcnow()

        if policy.status != "active":
            return False

        if now > policy.policy_end_date:
            self.logger.info(f"Policy {policy.policy_number} has elapsed end date. Automatically transitioning to expired.")
            self.repository.update(policy, {"status": "expired"})
            return False

        return True

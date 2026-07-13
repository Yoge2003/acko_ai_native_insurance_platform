"""
QuotationService containing business logic for Quotation verification and storage management.
"""

import uuid
from typing import Any, Dict, List, Tuple
from src.models.quotation import Quotation
from src.repositories.quotation import QuotationRepository
from src.repositories.user import UserRepository
from src.services.base_service import BaseService
from src.services.exceptions import ResourceNotFoundError, ValidationError


class QuotationService(BaseService[QuotationRepository]):
    """
    QuotationService providing validation, creation, and retrieval for Quotation records.
    """

    def __init__(self, repository: QuotationRepository, user_repository: UserRepository) -> None:
        """
        Initializes QuotationService.

        Args:
            repository: Injected QuotationRepository instance.
            user_repository: Injected UserRepository instance.
        """
        super().__init__(repository)
        self.user_repository = user_repository

    def create_quotation(
        self,
        user_id: uuid.UUID,
        quotation_type: str,
        vehicle_type: str,
        input_json: Dict[str, Any],
        predicted_premium: float,
        model_version: str,
    ) -> Quotation:
        """
        Persists a newly generated premium quotation after basic validation bounds checks.

        Args:
            user_id: UUID of requesting User who generated the quote.
            quotation_type: Classification string (e.g. 'car_premium').
            vehicle_type: Type of vehicle.
            input_json: Raw features dictionary passed to inference endpoint.
            predicted_premium: Premium sum calculated. Must be non-negative.
            model_version: The version string of the model.

        Returns:
            The created Quotation.

        Raises:
            ResourceNotFoundError: If requesting user is not registered.
            ValidationError: If input forms or premium amounts are invalid.
        """
        self.logger.info(f"Persisting quotation calculation for user ID {user_id}")

        # Input validation
        if predicted_premium < 0:
            raise ValidationError("predicted_premium cannot be negative.")
        if not input_json:
            raise ValidationError("input_json parameters cannot be empty.")
        if not quotation_type or not quotation_type.strip():
            raise ValidationError("quotation_type must be specified.")
        if not model_version or not model_version.strip():
            raise ValidationError("model_version must be specified.")

        # Business validation: Owner verification check
        if not self.user_repository.exists(id=user_id):
            raise ResourceNotFoundError(f"User creator with ID {user_id} does not exist.")

        quotation = Quotation(
            user_id=user_id,
            quotation_type=quotation_type.strip(),
            vehicle_type=vehicle_type.strip(),
            input_json=input_json,
            predicted_premium=predicted_premium,
            model_version=model_version.strip(),
        )
        try:
            return self.repository.create(quotation)
        except Exception as e:
            self.logger.error(f"Error persisting Quotation: {e}", exc_info=True)
            raise e

    def get_quotation_by_id(self, quotation_id: uuid.UUID) -> Quotation:
        """
        Retrieves a Quotation by its UUID database identifier.

        Args:
            quotation_id: UUID of quotation.

        Returns:
            The Quotation instance if found.

        Raises:
            ResourceNotFoundError: If the quotation ID does not exist.
        """
        q = self.repository.get_by_id(quotation_id)
        if q is None:
            self.logger.warning(f"Quotation not found with ID {quotation_id}")
            raise ResourceNotFoundError(f"Quotation with ID {quotation_id} does not exist.")
        return q

    def get_user_quotations(self, user_id: uuid.UUID) -> List[Quotation]:
        """
        Retrieves all quotation searches linked to a User.

        Args:
            user_id: Owner User ID.

        Returns:
            List of matching Quotations.
        """
        return self.repository.get_by_user_id(user_id)

    def get_latest_quotation_by_user(self, user_id: uuid.UUID) -> Quotation:
        """
        Extracts the most recent premium query run for a specific user ID.

        Args:
            user_id: Owner User ID.

        Returns:
            The latest saved Quotation instance.

        Raises:
            ResourceNotFoundError: If the user has never run a quotation query.
        """
        q = self.repository.get_latest_quotation(user_id)
        if q is None:
            raise ResourceNotFoundError(f"No quotation logs exist for user ID {user_id}.")
        return q

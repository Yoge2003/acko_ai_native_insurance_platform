"""
ClaimService containing business logic for claim registration validations, policy limits checks, and status modifications.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.models.claim import Claim
from src.repositories.claim import ClaimRepository
from src.repositories.policy import PolicyRepository
from src.repositories.user import UserRepository
from src.services.base_service import BaseService
from src.services.exceptions import (
    BusinessRuleViolationError,
    ResourceNotFoundError,
    ValidationError,
)


class ClaimService(BaseService[ClaimRepository]):
    """
    ClaimService providing logic for claim submissions, coverage validation,
    and workflow status transitions.
    """

    def __init__(
        self,
        repository: ClaimRepository,
        policy_repository: PolicyRepository,
        user_repository: UserRepository,
    ) -> None:
        """
        Initializes ClaimService.

        Args:
            repository: ClaimRepository database pipeline.
            policy_repository: PolicyRepository database pipeline.
            user_repository: UserRepository database pipeline.
        """
        super().__init__(repository)
        self.policy_repository = policy_repository
        self.user_repository = user_repository

    def submit_claim(
        self,
        policy_id: uuid.UUID,
        user_id: uuid.UUID,
        claim_amount: float,
        damage_summary: str,
        gemini_analysis_json: Optional[Dict[str, Any]] = None,
        predicted_decision: Optional[str] = None,
        approval_probability: Optional[float] = None,
    ) -> Claim:
        """
        Subscribes a claim against a user policy. Operates full validation rules:
        - Checks containing user existence
        - Checks policy existence
        - Validates that the policy is currently active and end date has not passed
        - Insists that the claim amount does not exceed the policy's IDV limit.

        Args:
            policy_id: In-scope Policy ID.
            user_id: Submitting User ID.
            claim_amount: Claimed financial aggregate. Must be positive.
            damage_summary: Free text details describing the claim.
            gemini_analysis_json: Optional parameters payload from RAG analysis.
            predicted_decision: Optional automated ML decision ('approved', 'rejected').
            approval_probability: Optional automated probability (0.0 to 1.0).

        Returns:
            The created Claim instance.

        Raises:
            ResourceNotFoundError: If the user or policy is missing.
            ValidationError: If amounts or damage reports are empty.
            BusinessRuleViolationError: If policy status is not active, elapsed, or cap limit is exceeded.
        """
        self.logger.info(f"Filing claim submission for policy {policy_id} by user {user_id}")

        # Input validation
        if claim_amount <= 0:
            raise ValidationError("Claim amount must be greater than zero.")
        if not damage_summary or not damage_summary.strip():
            raise ValidationError("A statement of damage summary details must be supplied.")
        if approval_probability is not None and not (0.0 <= approval_probability <= 1.0):
            raise ValidationError("Approval probability must lie between 0.0 and 1.0.")

        # Business validation: Entities existence
        if not self.user_repository.exists(id=user_id):
            raise ResourceNotFoundError(f"Submitting claimant User ID {user_id} does not exist.")

        policy = self.policy_repository.get_by_id(policy_id)
        if policy is None:
            raise ResourceNotFoundError(f"Associated Policy ID {policy_id} was not found.")

        now = datetime.utcnow()
        if policy.policy_end_date.tzinfo is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
        if policy.status != "active":
            raise BusinessRuleViolationError("Cannot submit a claim against an inactive policy.")
        if now > policy.policy_end_date:
            raise BusinessRuleViolationError("Cannot submit a claim against an expired policy.")

        # Business validation: Policy limit bounds
        if claim_amount > policy.idv:
            raise BusinessRuleViolationError(
                f"Claim amount ({claim_amount}) cannot exceed the Policy's Insured Declared Value (IDV = {policy.idv})."
            )

        claim = Claim(
            policy_id=policy_id,
            user_id=user_id,
            claim_amount=claim_amount,
            damage_summary=damage_summary.strip(),
            gemini_analysis_json=gemini_analysis_json,
            predicted_decision=predicted_decision,
            approval_probability=approval_probability,
            claim_status="pending",
            submitted_at=now,
        )
        try:
            return self.repository.create(claim)
        except Exception as e:
            self.logger.error(f"Error submitting claim: {e}", exc_info=True)
            raise e

    def get_claim_by_id(self, claim_id: uuid.UUID) -> Claim:
        """
        Retrieves a claim by its primary UUID tracking number.

        Args:
            claim_id: UUID of the claim.

        Returns:
            The Claim instance.

        Raises:
            ResourceNotFoundError: If the ID does not map in the DB.
        """
        claim = self.repository.get_by_id(claim_id)
        if claim is None:
            self.logger.warning(f"Claim not found with ID {claim_id}")
            raise ResourceNotFoundError(f"Claim with ID {claim_id} does not exist.")
        return claim

    def get_claims_by_user(self, user_id: uuid.UUID) -> List[Claim]:
        """
        Retrieves all claims submitted by a specific user.

        Args:
            user_id: UUID of requesting owner claimant.

        Returns:
            List of matching claims.
        """
        return self.repository.get_by_user_id(user_id)

    def get_claims_by_policy(self, policy_id: uuid.UUID) -> List[Claim]:
        """
        Retrieves all claims submitted under a specific policy index.

        Args:
            policy_id: UUID of specific Policy.

        Returns:
            List of associated Claims.
        """
        return self.repository.get_by_policy_id(policy_id)

    def get_claims_by_status(self, status: str) -> List[Claim]:
        """
        Retrieves list of claims currently matching particular workflow status.

        Args:
            status: E.g., 'pending', 'approved', 'rejected'.

        Returns:
            List of matching Claims.
        """
        return self.repository.get_claims_by_status(status.strip())

    def update_claim_status(self, claim_id: uuid.UUID, status: str) -> Claim:
        """
        Processes claim resolution workflow status update.
        Sets decision timestamp if status transitions out of pending.

        Args:
            claim_id: UUID of targeted claim.
            status: Target status state. Must be in {'pending', 'approved', 'rejected'}.

        Returns:
            The updated Claim database instance.

        Raises:
            ResourceNotFoundError: If targeted claim ID does not exist.
            ValidationError: If invalid status value is passed.
        """
        claim = self.get_claim_by_id(claim_id)
        status = status.strip().lower()

        valid_statuses = {"pending", "approved", "rejected"}
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status value. Must represent one of: {valid_statuses}")

        update_fields: Dict[str, Any] = {"claim_status": status}
        if status in {"approved", "rejected"}:
            update_fields["decided_at"] = datetime.utcnow()
        else:
            update_fields["decided_at"] = None

        return self.repository.update(claim, update_fields)

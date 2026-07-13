"""
ImageService containing business logic for claim attachments metadata validation, retrieval, and deletion.
"""

import uuid
from typing import List, Optional
from src.models.image import UploadedImage
from src.repositories.claim import ClaimRepository
from src.repositories.image import UploadedImageRepository
from src.services.base_service import BaseService
from src.services.exceptions import ResourceNotFoundError, ValidationError


class ImageService(BaseService[UploadedImageRepository]):
    """
    ImageService performing validations regarding claims and storage keys boundaries.
    """

    def __init__(self, repository: UploadedImageRepository, claim_repository: ClaimRepository) -> None:
        """
        Initializes ImageService.

        Args:
            repository: Injected UploadedImageRepository instance.
            claim_repository: Injected ClaimRepository instance.
        """
        super().__init__(repository)
        self.claim_repository = claim_repository

    def register_image(
        self,
        claim_id: uuid.UUID,
        original_filename: str,
        local_path: str,
        s3_key: Optional[str] = None,
    ) -> UploadedImage:
        """
        Registers an upload image attachment supporting an existing Claim.

        Args:
            claim_id: UUID of Claim to attach the image to.
            original_filename: Client uploaded file name (e.g. 'fender.jpg').
            local_path: Absolute disk location saving destination.
            s3_key: Optional cloud storage key path.

        Returns:
            The created UploadedImage metadata instance.

        Raises:
            ResourceNotFoundError: If the associated Claim ID is missing from database records.
            ValidationError: If filename or save path parameters are left empty.
        """
        self.logger.info(f"Registering upload image metadata: {original_filename} under claim ID {claim_id}")

        # Input validation
        if not original_filename or not original_filename.strip():
            raise ValidationError("original_filename cannot be empty.")
        if not local_path or not local_path.strip():
            raise ValidationError("local_path cannot be empty.")

        # Business validation: Claim existence check
        if not self.claim_repository.exists(id=claim_id):
            raise ResourceNotFoundError(f"Associated Claim with ID {claim_id} does not exist.")

        img = UploadedImage(
            claim_id=claim_id,
            original_filename=original_filename.strip(),
            local_path=local_path.strip(),
            s3_key=s3_key.strip() if s3_key else None
        )
        try:
            return self.repository.create(img)
        except Exception as e:
            self.logger.error(f"Error registering UploadedImage: {e}", exc_info=True)
            raise e

    def get_image_by_id(self, image_id: uuid.UUID) -> UploadedImage:
        """
        Retrieves image metadata by its UUID.

        Args:
            image_id: UUID of the upload image.

        Returns:
            The UploadedImage instance.

        Raises:
            ResourceNotFoundError: If image ID does not map in the DB.
        """
        img = self.repository.get_by_id(image_id)
        if img is None:
            self.logger.warning(f"UploadedImage not found with ID {image_id}")
            raise ResourceNotFoundError(f"UploadedImage metadata with ID {image_id} was not found.")
        return img

    def get_claim_images(self, claim_id: uuid.UUID) -> List[UploadedImage]:
        """
        Retrieves all uploaded images linked to a specific Claim ID.

        Args:
            claim_id: UUID of the Claim.

        Returns:
            List of associated UploadedImages.
        """
        return self.repository.get_images_by_claim(claim_id)

    def delete_image(self, image_id: uuid.UUID) -> bool:
        """
        Removes an UploadedImage from database metadata.

        Args:
            image_id: UUID of image.

        Returns:
            True if image was located and deleted, False otherwise.
        """
        try:
            return self.repository.delete(image_id)
        except Exception as e:
            self.logger.error(f"Error deleting image log {image_id}: {e}", exc_info=True)
            raise e

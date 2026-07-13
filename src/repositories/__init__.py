"""
Repositories module for direct database operations using the Repository Pattern.
"""

from src.repositories.base import BaseRepository
from src.repositories.user import UserRepository
from src.repositories.policy import PolicyRepository
from src.repositories.quotation import QuotationRepository
from src.repositories.claim import ClaimRepository
from src.repositories.chat import ChatRepository
from src.repositories.prediction import PredictionRepository
from src.repositories.image import UploadedImageRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "PolicyRepository",
    "QuotationRepository",
    "ClaimRepository",
    "ChatRepository",
    "PredictionRepository",
    "UploadedImageRepository",
]

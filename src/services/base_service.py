"""
Base Service providing shared configurations, logging wrappers, and generic initialization patterns.
"""

import logging
from typing import Generic, TypeVar
from src.repositories.base import BaseRepository

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[RepositoryType]):
    """
    Abstract Base Service wrapping a database repository instance with logging channels.
    """

    def __init__(self, repository: RepositoryType) -> None:
        """
        Initializes the service with dependency injection of its respective repository.

        Args:
            repository: An instance of a repository class that manages DB access.
        """
        self.repository = repository
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

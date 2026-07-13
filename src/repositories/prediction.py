"""
PredictionRepository handling database query operations for the PredictionLog model.
"""

from typing import List
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.models.prediction import PredictionLog
from src.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[PredictionLog]):
    """
    Repository for the PredictionLog model carrying custom data retrieval routines.
    """

    def __init__(self, db: Session) -> None:
        """
        Initializes PredictionRepository.

        Args:
            db: Active SQLAlchemy Database Transaction session.
        """
        super().__init__(PredictionLog, db)

    def get_logs_by_type(self, prediction_type: str) -> List[PredictionLog]:
        """
        Retrieves logs filtered by prediction log type.

        Args:
            prediction_type: Machine learning task identifier (e.g. 'claim_fraud_detection').

        Returns:
            List of matching PredictionLog instances.
        """
        try:
            stmt = select(self.model).where(self.model.prediction_type == prediction_type)
            return list(self.db.scalars(stmt).all())
        except Exception as e:
            self.logger.error(f"Error getting PredictionLogs by type {prediction_type}: {e}", exc_info=True)
            raise e

    def get_average_latency(self, prediction_type: str) -> float:
        """
        Calculates the average inference latency (in ms) for a given prediction type.

        Args:
            prediction_type: Machine learning task identifier.

        Returns:
            The average latency as a float, defaulting to 0.0 if no logs are found.
        """
        try:
            stmt = select(func.avg(self.model.latency_ms)).where(
                self.model.prediction_type == prediction_type
            )
            avg = self.db.scalar(stmt)
            return float(avg) if avg is not None else 0.0
        except Exception as e:
            self.logger.error(f"Error calculating average latency for type {prediction_type}: {e}", exc_info=True)
            raise e

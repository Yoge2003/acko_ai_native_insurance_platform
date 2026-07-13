"""
PredictionService containing business logic for ML inference logs auditing and telemetry queries.
"""

from typing import List, Optional, Tuple
from src.models.prediction import PredictionLog
from src.repositories.prediction import PredictionRepository
from src.services.base_service import BaseService
from src.services.exceptions import ValidationError


class PredictionService(BaseService[PredictionRepository]):
    """
    PredictionService executing latency metrics, hash validations, and bulk auditing logs.
    """

    def __init__(self, repository: PredictionRepository) -> None:
        """
        Initializes PredictionService.

        Args:
            repository: Injected PredictionRepository instance.
        """
        super().__init__(repository)

    def log_prediction(
        self,
        prediction_type: str,
        model_version: str,
        latency_ms: int,
        input_hash: str,
        output_hash: str,
    ) -> PredictionLog:
        """
        Registers a new model prediction log for latency/drift telemetry tracking.

        Args:
            prediction_type: ML model task classification.
            model_version: ML Model semantic version string.
            latency_ms: Roundtrip inference response execution duration size (ms). Must be non-negative.
            input_hash: Hash tracking verification for safety.
            output_hash: Hash tracking output validation.

        Returns:
            The created PredictionLog model profile.

        Raises:
            ValidationError: If inputs are invalid or latency value is negative.
        """
        self.logger.info(f"Logging ML prediction telemetries for type {prediction_type}")

        # Input validation
        if not prediction_type or not prediction_type.strip():
            raise ValidationError("prediction_type name must be specified.")
        if not model_version or not model_version.strip():
            raise ValidationError("model_version details must be supplied.")
        if latency_ms < 0:
            raise ValidationError("latency_ms cannot represent negative durations.")
        if not input_hash or not input_hash.strip():
            raise ValidationError("input_hash must be supplied.")
        if not output_hash or not output_hash.strip():
            raise ValidationError("output_hash must be supplied.")

        log = PredictionLog(
            prediction_type=prediction_type.strip(),
            model_version=model_version.strip(),
            latency_ms=latency_ms,
            input_hash=input_hash.strip(),
            output_hash=output_hash.strip(),
        )
        try:
            return self.repository.create(log)
        except Exception as e:
            self.logger.error(f"Error logging Prediction: {e}", exc_info=True)
            raise e

    def get_average_latency_by_type(self, prediction_type: str) -> float:
        """
        Calculates the average inference latency (in ms) for a given prediction type.

        Args:
            prediction_type: Telemetry task classification.

        Returns:
            Average execution duration (ms) as float. Defaults to 0.0 if empty.
        """
        if not prediction_type or not prediction_type.strip():
            return 0.0
        return self.repository.get_average_latency(prediction_type.strip())

    def list_logs(
        self,
        page: int = 1,
        per_page: int = 20,
        prediction_type: Optional[str] = None,
    ) -> Tuple[List[PredictionLog], int]:
        """
        Lists logs using pagination, optionally filtering by task categorization.

        Args:
            page: Current page query counter.
            per_page: Items count to slice.
            prediction_type: Optional task classification filter.

        Returns:
            A tuple containing (list of logs, total records matching filters).
        """
        filters = {}
        if prediction_type:
            filters["prediction_type"] = prediction_type.strip()
        return self.repository.paginate(page=page, per_page=per_page, filters=filters)

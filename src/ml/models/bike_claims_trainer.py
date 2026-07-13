"""
Bike Claims Trainer.
Provides the trainer class specifically targeted at the Bike Claims dataset.
"""

import logging
from typing import Dict, Any
from src.ml.models.car_claims_trainer import BaseClaimsTrainer

# Set up logger
logger = logging.getLogger(__name__)


class BikeClaimsTrainer(BaseClaimsTrainer):
    """
    Model Trainer subclass specialized for training and evaluating Bike Claims models.
    """

    def __init__(self, data_package: Dict[str, Any]):
        """
        Initializes BikeClaimsTrainer.
        """
        logger.info("Initializing specialized BikeClaimsTrainer.")
        super().__init__(data_package)

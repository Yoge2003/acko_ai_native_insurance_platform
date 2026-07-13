"""
Bike Quotation Trainer.
Provides the trainer class specifically targeted at the Bike Quotation dataset.
"""

import logging
from src.ml.models.base_trainer import BaseTrainer

# Set up logger
logger = logging.getLogger(__name__)


class BikeQuotationTrainer(BaseTrainer):
    """
    Model Trainer subclass specialized for training and evaluating Bike Quotation models.
    """

    def __init__(self, data_package: dict):
        """
        Initializes BikeQuotationTrainer.

        Args:
            data_package: Dictionary containing prepared datasets and metadata.
        """
        logger.info("Initializing specialized BikeQuotationTrainer.")
        super().__init__(data_package)

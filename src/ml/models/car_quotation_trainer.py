"""
Car Quotation Trainer.
Provides the trainer class specifically targeted at the Car Quotation dataset.
"""

import logging
from src.ml.models.base_trainer import BaseTrainer

# Set up logger
logger = logging.getLogger(__name__)


class CarQuotationTrainer(BaseTrainer):
    """
    Model Trainer subclass specialized for training and evaluating Car Quotation models.
    """

    def __init__(self, data_package: dict):
        """
        Initializes CarQuotationTrainer.

        Args:
            data_package: Dictionary containing prepared datasets and metadata.
        """
        logger.info("Initializing specialized CarQuotationTrainer.")
        super().__init__(data_package)

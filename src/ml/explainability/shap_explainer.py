"""
SHAP Explainer Wrapper.
Caches and retrieves SHAP TreeExplainer objects to optimize explanation speeds.
"""

import logging
from typing import Any, Dict
import shap

# Set up logger
logger = logging.getLogger(__name__)


class ShapExplainerWrapper:
    """
    Internal singleton cache manager for SHAP TreeExplainer instances.
    """

    _explainer_cache: Dict[str, Any] = {}

    @classmethod
    def get_explainer(cls, model_id: str, model: Any, background_data: Any = None) -> Any:
        """
        Loads or instantiates a cached TreeExplainer for the specified model.

        Args:
            model_id: Identifier key for caching.
            model: Trained estimator instance.
            background_data: Optional background inputs to format base levels.

        Returns:
            shap.TreeExplainer: Compiled SHAP TreeExplainer.
        """
        if model_id not in cls._explainer_cache:
            logger.info("Initializing and caching SHAP TreeExplainer for model: %s", model_id)
            # UseTreeExplainer directly for Random Forest
            cls._explainer_cache[model_id] = shap.TreeExplainer(model, data=background_data)
        
        return cls._explainer_cache[model_id]

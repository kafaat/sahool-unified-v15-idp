"""
SAHOOL AI Models Module
وحدة نماذج الذكاء الاصطناعي

This module provides AI/ML models for various agricultural tasks.
توفر هذه الوحدة نماذج الذكاء الاصطناعي للمهام الزراعية المختلفة.
"""

# Try importing disease detection model (requires PIL/cv2)
try:
    from .disease_cnn import DiseaseCNNModel, DiseaseConfig
    _disease_available = True
except ImportError:
    _disease_available = False
    DiseaseCNNModel = None
    DiseaseConfig = None

from .crop_parameters import (
    YEMEN_CROPS,
    CropCategory,
    CropParameters,
    GrowthParameters,
    Region,
    RegionalAdjustment,
    Season,
    SoilRequirements,
    get_all_crop_ids,
    get_crop_parameters,
    get_crops_by_category,
    get_crops_by_region,
)
from .yield_ensemble import (
    ConfidenceMetrics,
    FieldData,
    GDDBasedPredictor,
    GrowthStage,
    HistoricalTrendPredictor,
    LimitingFactor,
    NDVIBasedPredictor,
    SoilMoisturePredictor,
    YieldEnsembleModel,
    YieldPrediction,
)

__all__ = [
    # Disease detection - كشف الأمراض
    "DiseaseCNNModel",
    "DiseaseConfig",

    # Crop parameters - معلمات المحاصيل
    "CropParameters",
    "GrowthParameters",
    "SoilRequirements",
    "RegionalAdjustment",
    "Region",
    "Season",
    "CropCategory",
    "get_crop_parameters",
    "get_crops_by_category",
    "get_crops_by_region",
    "get_all_crop_ids",
    "YEMEN_CROPS",

    # Yield prediction ensemble - مجموعة التنبؤ بالإنتاج
    "YieldEnsembleModel",
    "YieldPrediction",
    "FieldData",
    "ConfidenceMetrics",
    "GrowthStage",
    "LimitingFactor",
    "NDVIBasedPredictor",
    "GDDBasedPredictor",
    "SoilMoisturePredictor",
    "HistoricalTrendPredictor",
]

__version__ = "1.0.0"

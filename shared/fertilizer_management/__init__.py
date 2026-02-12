"""
SAHOOL Fertilizer Management Module - وحدة إدارة الأسمدة

Comprehensive fertilizer management for agricultural operations including:
- Fertilizer inventory tracking - تتبع مخزون الأسمدة
- Application recommendations based on soil tests - توصيات التسميد بناءً على تحليل التربة
- Nutrient balance tracking - تتبع توازن العناصر الغذائية
- Cost optimization - تحسين التكاليف
- Environmental compliance - الامتثال البيئي

Features:
- Support for common fertilizers (Urea, DAP, NPK blends, organic)
- Bilingual Arabic/English content
- Integration with soil testing
- Environmental limit enforcement
- Cost analysis and optimization

Version: 1.0.0
"""

from .calculator import (
    # Calculation Results
    ApplicationRateResult,
    BlendCalculation,
    # Calculator
    FertilizerCalculator,
    calculate_blend_for_targets,
    # Helper Functions
    quick_rate_calculation,
)
from .inventory import (
    # Manager
    FertilizerInventoryManager,
    InventoryAlert,
    InventorySummary,
    # Transaction Models
    InventoryTransaction,
    # Helper Functions
    create_inventory_item,
)
from .models import (
    ApplicationMethod,
    ComplianceLevel,
    CostAnalysis,
    EnvironmentalCompliance,
    Fertilizer,
    FertilizerApplication,
    FertilizerForm,
    # Enums
    FertilizerType,
    InventoryItem,
    InventoryStatus,
    # Analysis Models
    NutrientBalance,
    # Core Models
    NutrientComposition,
    NutrientStatus,
    SoilTest,
)
from .recommendations import (
    # Data
    CROP_NUTRIENT_REQUIREMENTS,
    SOIL_NUTRIENT_THRESHOLDS,
    FertilizerRecommendation,
    # Engine
    FertilizerRecommendationEngine,
    # Recommendation Models
    NutrientRecommendation,
    calculate_quick_recommendation,
    # Helper Functions
    get_crop_requirements,
    get_supported_crops,
)

__version__ = "1.0.0"

__all__ = [
    # Version
    "__version__",
    # ===== Enums =====
    "FertilizerType",
    "FertilizerForm",
    "ApplicationMethod",
    "NutrientStatus",
    "InventoryStatus",
    "ComplianceLevel",
    # ===== Core Models =====
    "NutrientComposition",
    "Fertilizer",
    "InventoryItem",
    "FertilizerApplication",
    "SoilTest",
    # ===== Analysis Models =====
    "NutrientBalance",
    "EnvironmentalCompliance",
    "CostAnalysis",
    # ===== Recommendation System =====
    "NutrientRecommendation",
    "FertilizerRecommendation",
    "FertilizerRecommendationEngine",
    "get_crop_requirements",
    "get_supported_crops",
    "calculate_quick_recommendation",
    "CROP_NUTRIENT_REQUIREMENTS",
    "SOIL_NUTRIENT_THRESHOLDS",
    # ===== Inventory Management =====
    "InventoryTransaction",
    "InventoryAlert",
    "InventorySummary",
    "FertilizerInventoryManager",
    "create_inventory_item",
    # ===== Calculator =====
    "ApplicationRateResult",
    "BlendCalculation",
    "FertilizerCalculator",
    "quick_rate_calculation",
    "calculate_blend_for_targets",
]

"""
Fertilizer Advisor Context Engineering Integration
===================================================
وحدة هندسة السياق لخدمة مستشار التسميد

Integrates context compression, memory management, and recommendation evaluation
for the fertilizer advisor service.

المميزات:
- ضغط بيانات التربة والمحاصيل
- تخزين التوصيات في الذاكرة
- تقييم جودة التوصيات
- إدارة السياق للتفاعلات مع الذكاء الاصطناعي

Author: SAHOOL Platform Team
Updated: January 2025
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING, Any

# Add shared modules to path
sys.path.insert(0, "/app")

from shared.ai.context_engineering import (
    CompressionStrategy,
    ContextCompressor,
    EvaluationCriteria,
    FarmMemory,
    MemoryConfig,
    MemoryEntry,
    MemoryType,
    RecommendationEvaluator,
    RecommendationType,
)

# Use TYPE_CHECKING to avoid cyclic imports
if TYPE_CHECKING:
    from main import (
        CropType,
        FertilizationPlan,
        FertilizerRecommendation,
        SoilAnalysis,
    )

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

# Tenant ID for farm memory (defaults to system tenant)
SYSTEM_TENANT_ID = "sahool_system"

# Compression settings
FIELD_CONTEXT_MAX_TOKENS = 1500
SOIL_DATA_MAX_TOKENS = 800


# ─────────────────────────────────────────────────────────────────────────────
# Soil Data Compression
# ─────────────────────────────────────────────────────────────────────────────


def compress_soil_analysis(soil_analysis: SoilAnalysis) -> dict[str, Any]:
    """
    Compress soil analysis data for LLM context.
    ضغط بيانات تحليل التربة لسياق نموذج اللغة

    Removes redundant data and focuses on critical nutrients and constraints.

    Args:
        soil_analysis: SoilAnalysis model to compress

    Returns:
        dict: Compressed soil analysis data
    """
    compressor = ContextCompressor(
        default_strategy=CompressionStrategy.SELECTIVE,
        max_tokens=SOIL_DATA_MAX_TOKENS,
    )

    # Convert soil analysis to dictionary for compression
    soil_dict = {
        "field_id": soil_analysis.field_id,
        "analysis_date": soil_analysis.analysis_date.isoformat(),
        "soil_type": soil_analysis.soil_type.value,
        "critical_metrics": {
            "ph": round(soil_analysis.ph, 1),
            "ec_ds_m": round(soil_analysis.ec_ds_m, 2),
            "organic_matter": round(soil_analysis.organic_matter_percent, 1),
        },
        "nutrients_ppm": {
            "N": round(soil_analysis.nitrogen_ppm, 1),
            "P": round(soil_analysis.phosphorus_ppm, 1),
            "K": round(soil_analysis.potassium_ppm, 1),
        },
        "micronutrients_ppm": {
            "Ca": soil_analysis.calcium_ppm,
            "Mg": soil_analysis.magnesium_ppm,
            "S": soil_analysis.sulfur_ppm,
            "Fe": soil_analysis.iron_ppm,
            "Zn": soil_analysis.zinc_ppm,
        },
    }

    # Compress soil data
    soil_text = json.dumps(soil_dict, ensure_ascii=False)
    compression_result = compressor.compress_text(
        soil_text,
        strategy=CompressionStrategy.SELECTIVE,
    )

    return {
        "compressed": json.loads(compression_result.compressed_text),
        "original_tokens": compression_result.original_tokens,
        "compressed_tokens": compression_result.compressed_tokens,
        "compression_ratio": compression_result.compression_ratio,
        "tokens_saved": compression_result.tokens_saved,
    }


def compress_crop_data(
    crop: CropType, area_hectares: float, target_yield: float | None
) -> dict[str, Any]:
    """
    Compress crop and field data for LLM context.
    ضغط بيانات المحصول والحقل لسياق نموذج اللغة

    Args:
        crop: CropType to compress
        area_hectares: Field area in hectares
        target_yield: Target yield in kg/ha

    Returns:
        dict: Compressed crop and field data
    """
    compressor = ContextCompressor(
        default_strategy=CompressionStrategy.SELECTIVE,
        max_tokens=FIELD_CONTEXT_MAX_TOKENS,
    )

    crop_text = f"""
    Field Information:
    - Crop: {crop.value}
    - Area: {area_hectares} ha
    - Target Yield: {target_yield or 'default'} kg/ha
    """

    compression_result = compressor.compress_text(
        crop_text,
        strategy=CompressionStrategy.SELECTIVE,
    )

    return {
        "crop": crop.value,
        "area_hectares": area_hectares,
        "target_yield": target_yield,
        "original_tokens": compression_result.original_tokens,
        "compressed_tokens": compression_result.compressed_tokens,
        "compression_ratio": compression_result.compression_ratio,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Storage & Retrieval
# ─────────────────────────────────────────────────────────────────────────────


class FertilizerRecommendationMemory:
    """
    In-memory storage for fertilizer recommendations.
    تخزين التوصيات في الذاكرة للمشورة بشأن الأسمدة

    Stores recommendations with metadata for quick retrieval and evaluation.
    """

    def __init__(self, config: MemoryConfig | None = None):
        """
        Initialize recommendation memory.
        تهيئة ذاكرة التوصيات

        Args:
            config: Optional memory configuration
        """
        self.memory = FarmMemory(config=config or MemoryConfig())
        self.tenant_id = os.getenv("TENANT_ID", SYSTEM_TENANT_ID)
        self.recommendation_index: dict[str, str] = {}  # plan_id -> memory_entry_id

    def store_plan(
        self,
        plan: FertilizationPlan,
        compression_metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Store fertilization plan in memory.
        تخزين خطة التسميد في الذاكرة

        Args:
            plan: FertilizationPlan to store
            compression_metadata: Optional metadata about compression

        Returns:
            str: Memory entry ID
        """
        plan_dict = {
            "plan_id": plan.plan_id,
            "field_id": plan.field_id,
            "crop": plan.crop.value,
            "growth_stage": plan.growth_stage.value,
            "recommendations": [
                {
                    "fertilizer": r.fertilizer_type.value,
                    "quantity_kg_ha": r.quantity_kg_per_hectare,
                    "method": r.application_method.value,
                }
                for r in plan.recommendations
            ],
            "total_npk": {
                "N": plan.total_nitrogen_kg,
                "P": plan.total_phosphorus_kg,
                "K": plan.total_potassium_kg,
            },
            "total_cost": plan.total_cost_yer,
            "warnings": plan.warnings_en,
        }

        metadata = {
            "recommendation_count": len(plan.recommendations),
            "area_hectares": plan.area_hectares,
            "cost_per_hectare": plan.total_cost_yer / plan.area_hectares,
        }

        if compression_metadata:
            metadata["compression"] = compression_metadata

        entry_id = self.memory.store(
            tenant_id=self.tenant_id,
            content=plan_dict,
            memory_type=MemoryType.RECOMMENDATION,
            field_id=plan.field_id,
            metadata=metadata,
        )

        self.recommendation_index[plan.plan_id] = entry_id
        logger.info(
            f"Stored recommendation plan {plan.plan_id}",
            extra={"entry_id": entry_id, "field_id": plan.field_id},
        )

        return entry_id

    def retrieve_recent_plans(
        self, field_id: str | None = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        Retrieve recent fertilization plans from memory.
        استرجاع خطط التسميد الأخيرة من الذاكرة

        Args:
            field_id: Optional field ID to filter by
            limit: Maximum number of plans to retrieve

        Returns:
            list: Recent plans
        """
        recall_result = self.memory.recall(
            tenant_id=self.tenant_id,
            field_id=field_id,
            memory_types=[MemoryType.RECOMMENDATION],
            limit=limit,
        )

        plans = []
        for entry in recall_result.entries:
            if isinstance(entry.content, dict):
                plans.append(
                    {
                        **entry.content,
                        "stored_at": entry.timestamp.isoformat(),
                        "memory_entry_id": entry.id,
                    }
                )

        logger.info(
            f"Retrieved {len(plans)} recommendation plans",
            extra={"field_id": field_id},
        )

        return plans


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Evaluation
# ─────────────────────────────────────────────────────────────────────────────


def evaluate_fertilizer_recommendation(
    plan: FertilizationPlan,
) -> dict[str, Any]:
    """
    Evaluate quality of fertilizer recommendation.
    تقييم جودة توصية التسميد

    Uses LLM-as-Judge pattern to evaluate recommendations across multiple criteria:
    - Accuracy: Is the NPK calculation correct?
    - Actionability: Can the farmer implement it?
    - Safety: Are warnings adequate? No toxic levels?
    - Relevance: Does it match the crop and stage?
    - Completeness: Are all nutrients covered?
    - Clarity: Is it understandable in Arabic and English?

    Args:
        plan: FertilizationPlan to evaluate

    Returns:
        dict: Evaluation result with scores and approval status
    """
    evaluator = RecommendationEvaluator()

    # Prepare evaluation input
    recommendation_text = f"""
    Fertilization Plan for {plan.crop.value}:
    - Growth Stage: {plan.growth_stage.value}
    - Area: {plan.area_hectares} ha
    - Total NPK: N={plan.total_nitrogen_kg}kg, P={plan.total_phosphorus_kg}kg, K={plan.total_potassium_kg}kg
    - Cost: {plan.total_cost_yer} YER
    - Number of Recommendations: {len(plan.recommendations)}
    - Warnings: {len(plan.warnings_en)} warnings issued
    """

    # Evaluate the recommendation
    evaluation = evaluator.evaluate(
        recommendation_text=recommendation_text,
        recommendation_type=RecommendationType.FERTILIZATION,
        recommendation_id=plan.plan_id,
        context={
            "crop": plan.crop.value,
            "stage": plan.growth_stage.value,
            "area_hectares": plan.area_hectares,
            "recommendation_count": len(plan.recommendations),
            "has_warnings": len(plan.warnings_en) > 0,
            "cost_per_hectare": plan.total_cost_yer / plan.area_hectares,
        },
    )

    return {
        "evaluation_id": evaluation.id,
        "plan_id": plan.plan_id,
        "grade": evaluation.grade.value,
        "is_approved": evaluation.is_approved,
        "overall_score": evaluation.overall_score,
        "feedback": evaluation.feedback,
        "feedback_ar": evaluation.feedback_ar,
        "improvements": evaluation.improvements,
        "scores": {
            criteria.value: asdict(score)
            for criteria, score in evaluation.scores.items()
        },
        "evaluated_at": evaluation.evaluated_at.isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Factory Functions
# ─────────────────────────────────────────────────────────────────────────────


def create_compressor() -> ContextCompressor:
    """Create a configured context compressor / إنشاء ضاغط سياق مُعد"""
    return ContextCompressor(
        default_strategy=CompressionStrategy.HYBRID,
        max_tokens=FIELD_CONTEXT_MAX_TOKENS + SOIL_DATA_MAX_TOKENS,
        preserve_arabic_diacritics=False,
    )


def create_recommendation_memory() -> FertilizerRecommendationMemory:
    """Create recommendation memory / إنشاء ذاكرة التوصيات"""
    config = MemoryConfig(
        window_size=20,
        max_entries=500,
        ttl_hours=24,
        enable_compression=True,
    )
    return FertilizerRecommendationMemory(config=config)


__all__ = [
    "compress_soil_analysis",
    "compress_crop_data",
    "FertilizerRecommendationMemory",
    "evaluate_fertilizer_recommendation",
    "create_compressor",
    "create_recommendation_memory",
]

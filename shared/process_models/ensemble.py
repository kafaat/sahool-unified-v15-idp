# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Multi-Model Ensemble Framework – AgMIP-Inspired
================================================
إطار الأنسامبل متعدد النماذج – مستوحى من AgMIP

Implements a model-intercomparison and ensemble aggregation framework
inspired by the Agricultural Model Intercomparison and Improvement Project
(AgMIP) and ISIMIP methodologies.

Key capabilities:
  • Register any number of process models under a common interface
  • Run all registered models on the same inputs
  • Compute ensemble statistics (mean, std, percentile range)
  • Rank models against observations (RMSE, bias, correlation)
  • Generate ensemble uncertainty bands for decision support

Reference article section: Chapter 12 (AgMIP / GGCMI / ISIMIP comparisons)

References:
  Rosenzweig C et al. (2013). The Agricultural Model Intercomparison and
  Improvement Project (AgMIP). Agricultural & Forest Meteorology 170:166-182.
  Warszawski L et al. (2014). The Inter-Sectoral Impact Model Intercomparison
  Project (ISIMIP). PNAS 111:3228-3232.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import structlog

from shared.process_models.models import ModelResult, ModelType

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Model registration
# ---------------------------------------------------------------------------


@dataclass
class RegisteredModel:
    """A named model registered in the ensemble. نموذج مسجّل في الأنسامبل."""

    name: str  # Unique model identifier | معرّف النموذج
    name_ar: str  # Arabic name | الاسم بالعربية
    model_type: ModelType  # Category (crop_growth, hydrology, …)
    run_fn: Callable[..., ModelResult]  # callable(**kwargs) → ModelResult
    weight: float = 1.0  # Ensemble weight (for weighted mean) | وزن الأنسامبل
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Ensemble statistics
# ---------------------------------------------------------------------------


@dataclass
class EnsembleStats:
    """Descriptive statistics across ensemble model outputs. إحصاءات الأنسامبل."""

    n_models: int
    mean: float
    std: float
    min_val: float
    max_val: float
    p10: float  # 10th percentile
    p25: float  # 25th percentile (Q1)
    p75: float  # 75th percentile (Q3)
    p90: float  # 90th percentile
    weighted_mean: float
    uncertainty_range: float  # p90 - p10

    def to_dict(self) -> dict[str, float | int]:
        return {
            "n_models": self.n_models,
            "mean": round(self.mean, 3),
            "std": round(self.std, 3),
            "min": round(self.min_val, 3),
            "max": round(self.max_val, 3),
            "p10": round(self.p10, 3),
            "p25": round(self.p25, 3),
            "p75": round(self.p75, 3),
            "p90": round(self.p90, 3),
            "weighted_mean": round(self.weighted_mean, 3),
            "uncertainty_range": round(self.uncertainty_range, 3),
        }


def _percentile(sorted_values: list[float], p: float) -> float:
    """Linear interpolation percentile (no external dependencies)."""
    n = len(sorted_values)
    if n == 0:
        return 0.0
    if n == 1:
        return sorted_values[0]
    idx = (p / 100.0) * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    frac = idx - lo
    return sorted_values[lo] + frac * (sorted_values[hi] - sorted_values[lo])


def compute_ensemble_stats(values: list[float], weights: list[float]) -> EnsembleStats:
    """
    Compute ensemble statistics from a list of model outputs.
    حساب إحصاءات الأنسامبل من قائمة مخرجات النماذج.
    """
    if not values:
        raise ValueError("Empty values list for ensemble statistics")
    sv = sorted(values)
    n = len(sv)
    mean_val = statistics.mean(sv)
    std_val = statistics.stdev(sv) if n > 1 else 0.0
    # Weighted mean
    total_w = sum(weights) or 1.0
    w_mean = sum(v * w for v, w in zip(values, weights)) / total_w

    return EnsembleStats(
        n_models=n,
        mean=mean_val,
        std=std_val,
        min_val=sv[0],
        max_val=sv[-1],
        p10=_percentile(sv, 10),
        p25=_percentile(sv, 25),
        p75=_percentile(sv, 75),
        p90=_percentile(sv, 90),
        weighted_mean=w_mean,
        uncertainty_range=_percentile(sv, 90) - _percentile(sv, 10),
    )


# ---------------------------------------------------------------------------
# Model skill metrics (vs. observation)
# ---------------------------------------------------------------------------


@dataclass
class ModelSkillScore:
    """
    Verification skill metrics for a single model.
    مقاييس مهارة التحقق لنموذج واحد.
    """

    model_name: str
    rmse: float  # Root Mean Square Error
    bias: float  # Mean bias (predicted - observed)
    r_pearson: float  # Pearson correlation coefficient
    d_willmott: float  # Willmott index of agreement (0–1)
    skill_rank: int = 0


def compute_skill_scores(
    model_names: list[str],
    predictions: list[list[float]],
    observations: list[float],
) -> list[ModelSkillScore]:
    """
    Compute skill scores for each model against observations.
    حساب مقاييس المهارة لكل نموذج مقارنةً بالقياسات.
    """
    scores = []
    n = len(observations)
    obs_mean = statistics.mean(observations) if n > 1 else observations[0]

    for name, preds in zip(model_names, predictions):
        if len(preds) != n:
            continue
        bias = statistics.mean([p - o for p, o in zip(preds, observations)])
        rmse = math.sqrt(
            statistics.mean([(p - o) ** 2 for p, o in zip(preds, observations)])
        )

        # Pearson r
        cov = statistics.mean(
            [
                (p - statistics.mean(preds)) * (o - obs_mean)
                for p, o in zip(preds, observations)
            ]
        )
        std_p = statistics.stdev(preds) if n > 1 else 1.0
        std_o = statistics.stdev(observations) if n > 1 else 1.0
        r = cov / (std_p * std_o) if std_p * std_o > 0 else 0.0

        # Willmott d (1981)
        num_d = sum((p - o) ** 2 for p, o in zip(preds, observations))
        den_d = sum(
            (abs(p - obs_mean) + abs(o - obs_mean)) ** 2
            for p, o in zip(preds, observations)
        )
        d = 1.0 - num_d / den_d if den_d > 0 else 0.0

        scores.append(
            ModelSkillScore(
                model_name=name,
                rmse=round(rmse, 4),
                bias=round(bias, 4),
                r_pearson=round(r, 4),
                d_willmott=round(d, 4),
            )
        )

    # Rank by RMSE (ascending = better)
    scores.sort(key=lambda s: s.rmse)
    for rank, s in enumerate(scores, start=1):
        s.skill_rank = rank

    return scores


# ---------------------------------------------------------------------------
# Main framework
# ---------------------------------------------------------------------------


class EnsembleModelFramework:
    """
    AgMIP-inspired multi-model ensemble framework.
    إطار الأنسامبل متعدد النماذج مستوحى من AgMIP.

    Usage::

        framework = EnsembleModelFramework()

        # Register models
        framework.register(RegisteredModel(
            name="CropGrowthEngine", name_ar="محرك نمو المحاصيل",
            model_type=ModelType.CROP_GROWTH,
            run_fn=lambda **kw: crop_engine.simulate(**kw),
        ))

        # Run all models with identical inputs
        result = framework.run_ensemble(
            output_key="grain_yield_t_ha",
            run_kwargs={...},
        )
        print(result.outputs["ensemble_stats"]["mean"])
    """

    def __init__(self) -> None:
        self._models: list[RegisteredModel] = []

    def register(self, model: RegisteredModel) -> None:
        """Register a process model in the ensemble. تسجيل نموذج في الأنسامبل."""
        self._models.append(model)
        logger.info(
            "ensemble_model_registered", name=model.name, model_type=model.model_type
        )

    def list_models(self) -> list[dict[str, str]]:
        """List registered models. قائمة النماذج المسجّلة."""
        return [
            {
                "name": m.name,
                "name_ar": m.name_ar,
                "type": m.model_type,
                "weight": m.weight,
            }
            for m in self._models
        ]

    def run_ensemble(
        self,
        output_key: str,
        run_kwargs: dict[str, Any],
        observations: list[float] | None = None,
    ) -> ModelResult:
        """
        Execute all registered models and compute ensemble statistics.
        تنفيذ جميع النماذج المسجّلة وحساب إحصاءات الأنسامبل.

        Args:
            output_key: The key in ModelResult.outputs to aggregate (e.g. "grain_yield_t_ha").
            run_kwargs: Keyword arguments forwarded to every model's run_fn.
            observations: Optional observed values for skill scoring.

        Returns:
            ModelResult with ensemble_stats, individual_results, and skill_scores.
        """
        if not self._models:
            return ModelResult(
                model_name="EnsembleModelFramework",
                model_type=ModelType.ENSEMBLE,
                success=False,
                message="No models registered",
                message_ar="لا توجد نماذج مسجّلة",
            )

        individual_results = {}
        scalar_values = []
        weights = []
        model_names_with_values = []

        for model in self._models:
            try:
                result = model.run_fn(**run_kwargs)
                val = result.outputs.get(output_key)
                if val is not None and isinstance(val, (int, float)):
                    scalar_values.append(float(val))
                    weights.append(model.weight)
                    model_names_with_values.append(model.name)
                individual_results[model.name] = {
                    "success": result.success,
                    "output_value": val,
                    "model_type": result.model_type,
                }
            except Exception as exc:
                logger.warning("ensemble_model_failed", name=model.name, error=str(exc))
                individual_results[model.name] = {"success": False, "error": str(exc)}

        if not scalar_values:
            return ModelResult(
                model_name="EnsembleModelFramework",
                model_type=ModelType.ENSEMBLE,
                success=False,
                message=f"No models produced a numeric value for key '{output_key}'",
                message_ar=f"لم ينتج أي نموذج قيمة رقمية للمفتاح '{output_key}'",
            )

        stats = compute_ensemble_stats(scalar_values, weights)

        # Optional skill scoring
        skill_scores_out: list[dict] = []
        if observations:
            pred_series = [[v] for v in scalar_values]
            skill_list = compute_skill_scores(
                model_names_with_values, pred_series, observations
            )
            skill_scores_out = [
                {
                    "model": s.model_name,
                    "rmse": s.rmse,
                    "bias": s.bias,
                    "r_pearson": s.r_pearson,
                    "d_willmott": s.d_willmott,
                    "rank": s.skill_rank,
                }
                for s in skill_list
            ]

        logger.info(
            "ensemble_run_complete",
            n_models=len(scalar_values),
            output_key=output_key,
            ensemble_mean=round(stats.mean, 3),
            uncertainty_range=round(stats.uncertainty_range, 3),
        )

        return ModelResult(
            model_name="EnsembleModelFramework (AgMIP-inspired)",
            model_type=ModelType.ENSEMBLE,
            success=True,
            message="Ensemble simulation completed",
            message_ar="اكتملت محاكاة الأنسامبل",
            outputs={
                "output_key": output_key,
                "ensemble_stats": stats.to_dict(),
                "individual_results": individual_results,
                "skill_scores": skill_scores_out,
            },
        )

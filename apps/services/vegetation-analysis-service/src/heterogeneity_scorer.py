"""
Field Heterogeneity Scorer — مقياس تنوع الحقل
Determines if a field has enough spatial variability to benefit from
Variable Rate Application (VRA). Homogeneous fields don't need VRA.

Inspired by OneSoil's heterogeneity scoring algorithm.
"""

import logging
import math
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

# ============================================================================
# Classification types
# ============================================================================

ClassificationEN = Literal[
    "homogeneous",
    "slight",
    "moderate",
    "heterogeneous",
    "highly_heterogeneous",
]

# ============================================================================
# Arabic labels mapping
# ============================================================================

_CLASSIFICATION_AR: dict[ClassificationEN, str] = {
    "homogeneous": "متجانس",
    "slight": "تنوع طفيف",
    "moderate": "تنوع متوسط",
    "heterogeneous": "غير متجانس",
    "highly_heterogeneous": "غير متجانس بشدة",
}

_CLASSIFICATION_DESCRIPTIONS: dict[ClassificationEN, str] = {
    "homogeneous": "الحقل متجانس — لا حاجة للتطبيق المتغير المعدل",
    "slight": "تنوع طفيف — التطبيق المتغير اختياري",
    "moderate": "تنوع متوسط — يُنصح بالتطبيق المتغير المعدل",
    "heterogeneous": "تنوع عالٍ — يُنصح بشدة بالتطبيق المتغير المعدل",
    "highly_heterogeneous": "تنوع شديد — التطبيق المتغير المعدل ضروري",
}


# ============================================================================
# Yemen-specific CV threshold adjustments
# ============================================================================

# Yemen's terraced agriculture and varied microclimates naturally produce
# higher spatial variability. We adjust thresholds upward so that fields
# with inherently higher CV are not over-classified.
_YEMEN_CV_OFFSET: float = 3.0  # percentage points added to each threshold


# ============================================================================
# Data models
# ============================================================================


@dataclass(frozen=True)
class HeterogeneityScore:
    """Result of a field heterogeneity assessment.

    Attributes:
        score: Overall heterogeneity score (0-100).
        classification: English classification label.
        classification_ar: Arabic classification label.
        vra_recommended: Whether VRA is recommended for this field.
        zones_suggested: Optimal number of management zones (1-7).
        coefficient_of_variation: CV of the input values (%).
        spatial_autocorrelation: Moran's I statistic (-1 to 1).
            Positive values indicate spatial clustering; near-zero
            indicates random distribution; negative indicates dispersion.
        description_ar: Arabic description of the recommendation.
    """

    score: float
    classification: ClassificationEN
    classification_ar: str
    vra_recommended: bool
    zones_suggested: int
    coefficient_of_variation: float
    spatial_autocorrelation: float
    description_ar: str = ""


# ============================================================================
# Scorer
# ============================================================================


class HeterogeneityScorer:
    """Scores field spatial variability to decide if VRA is worthwhile.

    The algorithm combines two metrics:
    1. **Coefficient of Variation (CV)** — measures overall value spread.
    2. **Moran's I spatial autocorrelation** — measures whether nearby
       cells are more similar than distant cells. High Moran's I with
       high CV means clear management zones exist.

    The final score (0-100) blends both:
        score = 0.7 * cv_component + 0.3 * spatial_component

    Args:
        yemen_mode: When True, applies Yemen-specific threshold offsets
            to account for naturally higher variability in terraced fields.
    """

    # CV thresholds (upper bound for each class, in %)
    _CV_THRESHOLDS: list[tuple[float, ClassificationEN]] = [
        (5.0, "homogeneous"),
        (10.0, "slight"),
        (20.0, "moderate"),
        (30.0, "heterogeneous"),
    ]
    # Anything above the last threshold is "highly_heterogeneous".

    # Weight for blending CV component vs spatial component
    _CV_WEIGHT: float = 0.7
    _SPATIAL_WEIGHT: float = 0.3

    def __init__(self, *, yemen_mode: bool = False) -> None:
        self._yemen_mode = yemen_mode
        self._cv_offset = _YEMEN_CV_OFFSET if yemen_mode else 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score_from_ndvi_grid(self, ndvi_values: list[list[float]]) -> HeterogeneityScore:
        """Score heterogeneity from a 2-D grid of NDVI values.

        Args:
            ndvi_values: Row-major 2-D grid of NDVI values (each value
                typically in the range -1.0 to 1.0).

        Returns:
            HeterogeneityScore with full spatial analysis.

        Raises:
            ValueError: If the grid is empty or contains fewer than 4 cells.
        """
        flat = self._flatten_grid(ndvi_values)
        if len(flat) < 4:
            raise ValueError("At least 4 NDVI values are required for heterogeneity scoring.")

        cv = self._coefficient_of_variation(flat)
        morans_i = self._morans_i_grid(ndvi_values)

        return self._build_score(cv, morans_i)

    def score_from_observations(self, observations: list[float]) -> HeterogeneityScore:
        """Score heterogeneity from a flat list of NDVI samples.

        This is a simpler interface when spatial arrangement is unknown.
        Moran's I is set to 0.0 (unknown spatial structure).

        Args:
            observations: List of NDVI sample values.

        Returns:
            HeterogeneityScore (spatial_autocorrelation will be 0.0).

        Raises:
            ValueError: If fewer than 2 observations are provided.
        """
        if len(observations) < 2:
            raise ValueError("At least 2 observations are required for heterogeneity scoring.")

        cv = self._coefficient_of_variation(observations)
        morans_i = 0.0  # No spatial structure available

        return self._build_score(cv, morans_i)

    def suggest_zones(self, score: HeterogeneityScore) -> int:
        """Return the optimal number of VRA management zones.

        This is a convenience method; the value is already available
        in ``score.zones_suggested``.
        """
        return score.zones_suggested

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_score(self, cv: float, morans_i: float) -> HeterogeneityScore:
        """Build a HeterogeneityScore from CV and Moran's I."""
        classification = self._classify(cv)
        zones = self._zones_for_classification(classification, cv)

        # Compute composite score (0-100).
        # CV component: map CV 0-40% → 0-100 (capped).
        cv_component = min(cv / 40.0 * 100.0, 100.0)

        # Spatial component: Moran's I ranges from -1 to 1.
        # High positive Moran's I means clear spatial clusters (good for VRA).
        # We map [0, 1] → [0, 100]; negative values contribute 0.
        spatial_component = max(morans_i, 0.0) * 100.0

        raw_score = self._CV_WEIGHT * cv_component + self._SPATIAL_WEIGHT * spatial_component
        final_score = round(min(max(raw_score, 0.0), 100.0), 1)

        vra_recommended = classification in (
            "moderate",
            "heterogeneous",
            "highly_heterogeneous",
        )

        return HeterogeneityScore(
            score=final_score,
            classification=classification,
            classification_ar=_CLASSIFICATION_AR[classification],
            vra_recommended=vra_recommended,
            zones_suggested=zones,
            coefficient_of_variation=round(cv, 2),
            spatial_autocorrelation=round(morans_i, 4),
            description_ar=_CLASSIFICATION_DESCRIPTIONS[classification],
        )

    def _classify(self, cv: float) -> ClassificationEN:
        """Classify CV into a heterogeneity class."""
        for threshold, label in self._CV_THRESHOLDS:
            if cv < (threshold + self._cv_offset):
                return label
        return "highly_heterogeneous"

    def _zones_for_classification(self, classification: ClassificationEN, cv: float) -> int:
        """Determine optimal management zone count."""
        zone_map: dict[ClassificationEN, int] = {
            "homogeneous": 1,
            "slight": 2,
            "moderate": 3 if cv < 15.0 + self._cv_offset else 4,
            "heterogeneous": 5,
            "highly_heterogeneous": 6 if cv < 35.0 + self._cv_offset else 7,
        }
        return zone_map[classification]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @staticmethod
    def _flatten_grid(grid: list[list[float]]) -> list[float]:
        """Flatten a 2-D grid into a 1-D list, filtering NaN values."""
        flat: list[float] = []
        for row in grid:
            for val in row:
                if not math.isnan(val):
                    flat.append(val)
        return flat

    @staticmethod
    def _mean(values: list[float]) -> float:
        return sum(values) / len(values)

    @staticmethod
    def _std(values: list[float], mean: float) -> float:
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(variance)

    def _coefficient_of_variation(self, values: list[float]) -> float:
        """Return CV as a percentage."""
        mean = self._mean(values)
        if abs(mean) < 1e-10:
            # Avoid division by zero; treat as maximum heterogeneity.
            return 100.0
        std = self._std(values, mean)
        return (std / abs(mean)) * 100.0

    def _morans_i_grid(self, grid: list[list[float]]) -> float:
        """Compute Moran's I spatial autocorrelation for a 2-D grid.

        Uses a queen contiguity weight matrix (8-neighbor connectivity).
        NaN cells are excluded.

        Returns:
            Moran's I value in the range [-1, 1].
            Values near +1 indicate strong spatial clustering.
            Values near 0 indicate spatial randomness.
            Values near -1 indicate spatial dispersion.
        """
        rows = len(grid)
        if rows == 0:
            return 0.0
        _cols = len(grid[0])

        # Build index of valid cells
        cells: list[tuple[int, int, float]] = []
        index_map: dict[tuple[int, int], int] = {}
        for r in range(rows):
            for c in range(len(grid[r])):
                val = grid[r][c]
                if not math.isnan(val):
                    idx = len(cells)
                    cells.append((r, c, val))
                    index_map[(r, c)] = idx

        n = len(cells)
        if n < 4:
            return 0.0

        values = [cell[2] for cell in cells]
        mean = self._mean(values)

        # Deviations from mean
        z = [v - mean for v in values]

        # Sum of squared deviations
        sum_z2 = sum(zi * zi for zi in z)
        if sum_z2 < 1e-15:
            return 0.0  # All values identical

        # Queen contiguity: 8-neighbor offsets
        neighbors_offsets = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        # Compute numerator and total weight
        numerator = 0.0
        total_w = 0.0

        for i, (r, c, _) in enumerate(cells):
            for dr, dc in neighbors_offsets:
                nr, nc = r + dr, c + dc
                j = index_map.get((nr, nc))
                if j is not None:
                    numerator += z[i] * z[j]
                    total_w += 1.0

        if total_w < 1e-15:
            return 0.0

        morans_i = (n / total_w) * (numerator / sum_z2)

        # Clamp to valid range
        return max(-1.0, min(1.0, morans_i))

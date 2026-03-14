# ═══════════════════════════════════════════════════════════════════════════════
# Region Relevance Filter (AgriRegion Pattern)
# فلتر الملاءمة الإقليمية (نمط AgriRegion)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Based on AgriRegion (arXiv:2512.10114):
#   - Geospatial metadata injection per chunk
#   - Region-prioritized re-ranking
#   - Spatial-semantic scoring: local knowledge highest, similar ecoregions
#     reduced but not removed, dissimilar regions removed
#
# Uses existing Yemen/GCC regional data:
#   - shared/yemen/climate.py → YEMEN_CLIMATE_ZONES (7 zones)
#   - shared/yemen/crops.py → YEMEN_CROPS (30+ crops with regions)
#   - shared/yemen/soils.py → YEMEN_SOIL_PROFILES
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.ai.knowledge._logging import get_logger

from ..models import BaseKnowledgeDocument

logger = get_logger(__name__)


# ─── Regional Climate Definitions ─────────────────────────────────────────────

CLIMATE_ZONES: dict[str, dict[str, Any]] = {
    "yemen_coastal": {
        "name_ar": "الساحل اليمني (تهامة)",
        "type": "hot_arid",
        "temp_range_c": (25, 42),
        "rainfall_mm": (50, 200),
        "altitude_m": (0, 200),
        "similar_zones": ["saudi_coastal_red_sea", "oman_coastal", "djibouti_coastal"],
    },
    "yemen_highland": {
        "name_ar": "المرتفعات اليمنية",
        "type": "semi_arid_highland",
        "temp_range_c": (10, 28),
        "rainfall_mm": (300, 800),
        "altitude_m": (1500, 3000),
        "similar_zones": ["ethiopia_highland", "saudi_asir"],
    },
    "yemen_eastern_plateau": {
        "name_ar": "الهضبة الشرقية (حضرموت)",
        "type": "arid",
        "temp_range_c": (18, 40),
        "rainfall_mm": (30, 100),
        "altitude_m": (500, 1500),
        "similar_zones": ["oman_interior", "saudi_eastern"],
    },
    "yemen_desert": {
        "name_ar": "الصحراء (الربع الخالي)",
        "type": "hyper_arid",
        "temp_range_c": (15, 50),
        "rainfall_mm": (0, 50),
        "altitude_m": (200, 800),
        "similar_zones": ["saudi_rub_al_khali", "oman_desert"],
    },
    "yemen_islands": {
        "name_ar": "الجزر (سقطرى)",
        "type": "tropical_semi_arid",
        "temp_range_c": (22, 34),
        "rainfall_mm": (100, 300),
        "altitude_m": (0, 1500),
        "similar_zones": ["horn_of_africa_coastal"],
    },
    "saudi_central": {
        "name_ar": "وسط المملكة (الرياض، القصيم)",
        "type": "arid_continental",
        "temp_range_c": (8, 48),
        "rainfall_mm": (50, 150),
        "altitude_m": (500, 1000),
        "similar_zones": ["yemen_eastern_plateau", "uae_interior"],
    },
    "saudi_asir": {
        "name_ar": "عسير والباحة",
        "type": "semi_arid_highland",
        "temp_range_c": (10, 30),
        "rainfall_mm": (200, 500),
        "altitude_m": (1500, 3000),
        "similar_zones": ["yemen_highland"],
    },
    "gcc_coastal": {
        "name_ar": "الساحل الخليجي",
        "type": "hot_humid",
        "temp_range_c": (18, 48),
        "rainfall_mm": (50, 150),
        "altitude_m": (0, 100),
        "similar_zones": ["yemen_coastal", "oman_coastal"],
    },
    # Extended regions from research (ICARDA, Saudi Vision 2030, FAO)
    "egypt_nile_delta": {
        "name_ar": "دلتا النيل",
        "type": "semi_arid",
        "temp_range_c": (10, 38),
        "rainfall_mm": (50, 200),
        "altitude_m": (0, 50),
        "similar_zones": ["gcc_coastal"],
    },
    "egypt_upper": {
        "name_ar": "صعيد مصر",
        "type": "arid",
        "temp_range_c": (8, 44),
        "rainfall_mm": (0, 50),
        "altitude_m": (50, 500),
        "similar_zones": ["yemen_eastern_plateau", "saudi_central"],
    },
    "jordan_valley": {
        "name_ar": "غور الأردن",
        "type": "hot_arid",
        "temp_range_c": (10, 46),
        "rainfall_mm": (50, 200),
        "altitude_m": (-400, 0),
        "similar_zones": ["yemen_coastal"],
    },
    "iraq_central": {
        "name_ar": "وسط العراق",
        "type": "arid_continental",
        "temp_range_c": (5, 50),
        "rainfall_mm": (100, 250),
        "altitude_m": (0, 500),
        "similar_zones": ["saudi_central"],
    },
    "morocco_atlantic": {
        "name_ar": "الساحل الأطلسي المغربي",
        "type": "semi_arid",
        "temp_range_c": (8, 35),
        "rainfall_mm": (200, 600),
        "altitude_m": (0, 500),
        "similar_zones": ["yemen_highland"],
    },
    "sudan_central": {
        "name_ar": "وسط السودان",
        "type": "semi_arid",
        "temp_range_c": (18, 45),
        "rainfall_mm": (200, 600),
        "altitude_m": (300, 700),
        "similar_zones": ["yemen_eastern_plateau"],
    },
    "uae_interior": {
        "name_ar": "داخل الإمارات",
        "type": "hyper_arid",
        "temp_range_c": (12, 52),
        "rainfall_mm": (30, 120),
        "altitude_m": (0, 300),
        "similar_zones": ["saudi_central", "oman_interior"],
    },
}

# Climate type compatibility (how similar two climate types are: 0.0-1.0)
_CLIMATE_COMPATIBILITY: dict[tuple[str, str], float] = {
    ("hot_arid", "arid"): 0.8,
    ("hot_arid", "hyper_arid"): 0.6,
    ("hot_arid", "arid_continental"): 0.7,
    ("hot_arid", "hot_humid"): 0.7,
    ("semi_arid_highland", "semi_arid_highland"): 1.0,
    ("arid", "arid_continental"): 0.8,
    ("arid", "hyper_arid"): 0.6,
    ("hot_humid", "tropical_semi_arid"): 0.6,
    ("semi_arid", "semi_arid_highland"): 0.7,
    ("semi_arid", "arid"): 0.7,
    ("semi_arid", "hot_arid"): 0.6,
    ("arid_continental", "arid"): 0.8,
    ("arid_continental", "hot_arid"): 0.6,
    ("hyper_arid", "arid_continental"): 0.5,
    ("hyper_arid", "arid"): 0.6,
}


@dataclass
class RegionRelevanceResult:
    """Result of region relevance assessment | نتيجة تقييم الملاءمة الإقليمية"""

    overall_score: float = 0.0
    climate_score: float = 0.0
    crop_score: float = 0.0
    soil_score: float = 0.0
    applicable_regions: list[str] = field(default_factory=list)
    adaptations_needed: list[str] = field(default_factory=list)
    adaptations_needed_ar: list[str] = field(default_factory=list)

    @property
    def is_relevant(self) -> bool:
        return self.overall_score >= 0.3

    def to_metadata(self) -> dict[str, Any]:
        """Convert to metadata dict for chunk enrichment."""
        return {
            "region_relevance": {
                "overall_score": round(self.overall_score, 3),
                "climate_score": round(self.climate_score, 3),
                "crop_score": round(self.crop_score, 3),
                "applicable_regions": self.applicable_regions,
                "adaptations": self.adaptations_needed,
            }
        }


class RegionRelevanceFilter:
    """Filters and scores knowledge documents for regional relevance.
    يصفي ويقيم وثائق المعرفة حسب الملاءمة الإقليمية

    Applies the AgriRegion pattern:
    - Local knowledge = highest score
    - Similar ecoregions = reduced but kept
    - Completely dissimilar regions = filtered out"""

    # Default target regions, configurable via SAHOOL_DEFAULT_REGIONS env var
    # Format: comma-separated zone names, e.g. "yemen_highland,saudi_central"
    _DEFAULT_REGIONS = ["yemen_highland", "yemen_coastal"]

    def __init__(
        self,
        target_regions: list[str] | None = None,
        min_relevance: float = 0.3,
    ) -> None:
        import os

        if target_regions is not None:
            self._target_regions = target_regions
        else:
            env_regions = os.environ.get("SAHOOL_DEFAULT_REGIONS", "")
            if env_regions:
                self._target_regions = [r.strip() for r in env_regions.split(",") if r.strip()]
            else:
                self._target_regions = list(self._DEFAULT_REGIONS)
        self._min_relevance = min_relevance

    def assess_relevance(
        self,
        document: BaseKnowledgeDocument,
        target_regions: list[str] | None = None,
    ) -> RegionRelevanceResult:
        """Assess how relevant a document is for target regions.
        تقييم مدى ملاءمة الوثيقة للمناطق المستهدفة"""
        regions = target_regions or self._target_regions
        result = RegionRelevanceResult()

        # 1. Climate compatibility
        result.climate_score = self._check_climate_compatibility(document, regions)

        # 2. Crop availability
        result.crop_score = self._check_crop_relevance(document, regions)

        # 3. Soil compatibility
        soil_score = self._check_soil_compatibility(document, regions)

        # Weighted overall score
        # Climate has highest weight as primary filter
        weights = {"climate": 0.5, "crop": 0.35, "soil": 0.15}
        result.overall_score = (
            weights["climate"] * result.climate_score
            + weights["crop"] * result.crop_score
            + weights["soil"] * soil_score
        )

        # Determine applicable regions
        result.applicable_regions = self._find_applicable_regions(document, regions)

        # Suggest adaptations
        result.adaptations_needed = self._suggest_adaptations(document, regions)
        result.adaptations_needed_ar = self._suggest_adaptations_ar(document, regions)

        logger.debug(
            "region_relevance_assessed",
            document_id=document.id,
            score=result.overall_score,
            regions=result.applicable_regions,
        )

        return result

    def filter_documents(
        self,
        documents: list[BaseKnowledgeDocument],
        target_regions: list[str] | None = None,
    ) -> list[tuple[BaseKnowledgeDocument, RegionRelevanceResult]]:
        """Filter and rank documents by regional relevance.
        تصفية وترتيب الوثائق حسب الملاءمة الإقليمية"""
        scored = []
        for doc in documents:
            relevance = self.assess_relevance(doc, target_regions)
            if relevance.is_relevant:
                scored.append((doc, relevance))

        # Sort by overall score descending
        scored.sort(key=lambda x: x[1].overall_score, reverse=True)
        return scored

    # ─── Scoring Methods ──────────────────────────────────────────────────────

    def _check_climate_compatibility(self, doc: BaseKnowledgeDocument, target_regions: list[str]) -> float:
        """Score climate compatibility between document and target regions."""
        doc_regions = doc.geospatial.applicable_regions
        doc_climates = doc.geospatial.climate_zones

        if not doc_regions and not doc_climates:
            # No geospatial data → assume general (moderate score)
            return 0.5

        # Direct region match
        for dr in doc_regions:
            if dr in target_regions:
                return 1.0

        # Check if doc regions are in similar zones
        max_score = 0.0
        for target in target_regions:
            target_info = CLIMATE_ZONES.get(target)
            if not target_info:
                continue

            for dr in doc_regions:
                dr_info = CLIMATE_ZONES.get(dr)
                if not dr_info:
                    continue

                # Check if they're in each other's similar zones
                if dr in target_info.get("similar_zones", []) or target in dr_info.get("similar_zones", []):
                    max_score = max(max_score, 0.7)
                else:
                    # Compare climate types
                    t_type = target_info.get("type", "")
                    d_type = dr_info.get("type", "")
                    if t_type == d_type:
                        max_score = max(max_score, 0.8)
                    else:
                        compat = _CLIMATE_COMPATIBILITY.get(
                            (t_type, d_type),
                            _CLIMATE_COMPATIBILITY.get((d_type, t_type), 0.2),
                        )
                        max_score = max(max_score, compat * 0.6)

        # Check climate zones directly
        for dc in doc_climates:
            for target in target_regions:
                target_info = CLIMATE_ZONES.get(target)
                if target_info and dc == target_info.get("type"):
                    max_score = max(max_score, 0.8)

        return max_score

    def _check_crop_relevance(self, doc: BaseKnowledgeDocument, target_regions: list[str]) -> float:
        """Score crop relevance for the target regions."""
        # If document has no crop-specific tags, assume general relevance
        crop_tags = [t for t in doc.tags if t.startswith("crop:")]
        if not crop_tags:
            return 0.6  # General content

        # Known crops suitable for MENA/Yemen regions
        mena_crops = {
            "wheat",
            "barley",
            "sorghum",
            "millet",
            "rice",
            "date palm",
            "coffee",
            "qat",
            "tomato",
            "cucumber",
            "potato",
            "onion",
            "okra",
            "citrus",
            "mango",
            "pomegranate",
            "grapes",
            "olive",
            "alfalfa",
            "sesame",
            "corn",
        }

        matched = 0
        for tag in crop_tags:
            crop_name = tag.replace("crop:", "")
            if crop_name in mena_crops:
                matched += 1

        return matched / len(crop_tags)

    def _check_soil_compatibility(self, doc: BaseKnowledgeDocument, target_regions: list[str]) -> float:
        """Score soil compatibility for target regions."""
        doc_soils = doc.geospatial.soil_types
        if not doc_soils:
            return 0.5  # No soil info → moderate

        # Common soil types in Yemen/GCC
        regional_soils = {
            "sandy",
            "sandy loam",
            "loam",
            "clay loam",
            "calcareous",
            "saline",
            "alluvial",
            "aridisol",
            "entisol",
        }

        matched = sum(1 for s in doc_soils if s.lower() in regional_soils)
        return matched / len(doc_soils) if doc_soils else 0.5

    def _find_applicable_regions(self, doc: BaseKnowledgeDocument, target_regions: list[str]) -> list[str]:
        """Find which target regions the document applies to."""
        applicable = []
        for region in target_regions:
            region_info = CLIMATE_ZONES.get(region)
            if not region_info:
                continue

            # Direct match or similar zone
            if region in doc.geospatial.applicable_regions or any(
                r in region_info.get("similar_zones", []) for r in doc.geospatial.applicable_regions
            ):
                applicable.append(region)

        # If no specific regions but document is general
        if not applicable and not doc.geospatial.applicable_regions:
            applicable = list(target_regions)  # General content applies everywhere

        return applicable

    def _suggest_adaptations(self, doc: BaseKnowledgeDocument, target_regions: list[str]) -> list[str]:
        """Suggest adaptations needed for regional application."""
        adaptations = []

        if not doc.geospatial.applicable_regions:
            adaptations.append("Verify applicability to local conditions")

        # Check altitude adaptation
        if doc.geospatial.altitude_range_m:
            doc_lo, doc_hi = doc.geospatial.altitude_range_m
            for region in target_regions:
                region_info = CLIMATE_ZONES.get(region)
                if not region_info:
                    continue
                reg_lo, reg_hi = region_info.get("altitude_m", (0, 3000))
                if doc_hi < reg_lo or doc_lo > reg_hi:
                    adaptations.append(f"Adjust for altitude difference ({region}: {reg_lo}-{reg_hi}m)")

        return adaptations

    def _suggest_adaptations_ar(self, doc: BaseKnowledgeDocument, target_regions: list[str]) -> list[str]:
        """Suggest adaptations in Arabic."""
        adaptations = []

        if not doc.geospatial.applicable_regions:
            adaptations.append("تحقق من ملاءمة المعلومات للظروف المحلية")

        if doc.geospatial.altitude_range_m:
            doc_lo, doc_hi = doc.geospatial.altitude_range_m
            for region in target_regions:
                region_info = CLIMATE_ZONES.get(region)
                if not region_info:
                    continue
                reg_lo, reg_hi = region_info.get("altitude_m", (0, 3000))
                if doc_hi < reg_lo or doc_lo > reg_hi:
                    name_ar = region_info.get("name_ar", region)
                    adaptations.append(f"تكييف لفارق الارتفاع ({name_ar}: {reg_lo}-{reg_hi}م)")

        return adaptations

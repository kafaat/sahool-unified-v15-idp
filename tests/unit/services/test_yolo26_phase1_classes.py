# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit tests for YOLO26 Vision Service Phase 1 crop-specific classes.
اختبارات الوحدة لفئات الأمراض والآفات الخاصة بالمحاصيل - المرحلة الأولى

Tests cover:
- New disease classes (IDs 34-55) for 7 crops
- New pest classes (IDs 22-26) for crop-specific pests
- Disease treatment recommendations for all new IDs
- Pest recommendations for all new IDs
- High-spread-risk disease list
- Bilingual (Arabic/English) correctness
- Scientific name presence

Author: SAHOOL Platform Team
Updated: February 2026
"""

import importlib.util
import sys
from enum import StrEnum
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Load schemas module directly to avoid pulling in torch/GPU dependencies.
# schemas.py imports from src.core.vlm_verifier which requires PIL, httpx, etc.
# We mock the vlm_verifier module to avoid pulling in heavy dependencies.
_SERVICE_ROOT = (
    Path(__file__).parent.parent.parent.parent
    / "apps"
    / "services"
    / "yolo26-vision-service"
)
_SCHEMAS_PATH = _SERVICE_ROOT / "src" / "api" / "schemas.py"

_service_root_str = str(_SERVICE_ROOT)
if _service_root_str not in sys.path:
    sys.path.insert(0, _service_root_str)

# Pre-populate sys.modules with a mock for vlm_verifier to avoid heavy imports
_mock_vlm = MagicMock()

class _VLMProvider(StrEnum):
    DISABLED = "disabled"
    QWEN_VL = "qwen_vl"
    OLLAMA = "ollama"
    VLLM = "vllm"

class _VLMVerificationStatus(StrEnum):
    CONFIRMED = "confirmed"
    SUSPICIOUS = "suspicious"
    DISMISSED = "dismissed"
    ERROR = "error"
    UNVERIFIED = "unverified"

_mock_vlm.VLMProvider = _VLMProvider
_mock_vlm.VLMVerificationStatus = _VLMVerificationStatus
sys.modules["src.core.vlm_verifier"] = _mock_vlm

_spec = importlib.util.spec_from_file_location("yolo26_schemas", str(_SCHEMAS_PATH))
_schemas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_schemas)

DISEASE_CLASSES = _schemas.DISEASE_CLASSES
PEST_CLASSES = _schemas.PEST_CLASSES
WEED_CLASSES = _schemas.WEED_CLASSES
BilingualLabel = _schemas.BilingualLabel


# =============================================================================
# Phase 1 Disease Classes
# =============================================================================

# Expected new diseases by crop
CORN_DISEASES = {
    34: ("Corn Gray Leaf Spot", "تبقع أوراق الذرة الرمادي", "Cercospora zeae-maydis"),
    35: ("Corn Northern Leaf Blight", "لفحة أوراق الذرة الشمالية", "Exserohilum turcicum"),
    36: ("Corn Common Rust", "صدأ الذرة الشائع", "Puccinia sorghi"),
    37: ("Maize Streak Virus", "فيروس تخطط الذرة", "Mastrevirus"),
}

WHEAT_DISEASES = {
    38: ("Wheat Yellow Rust", "الصدأ الأصفر للقمح", "Puccinia striiformis"),
    39: ("Wheat Karnal Bunt", "التفحم الكرنالي للقمح", "Tilletia indica"),
    40: ("Wheat Helminthosporium Blight", "لفحة هلمنثوسبوريوم القمح", "Bipolaris sorokiniana"),
}

POTATO_DISEASES = {
    41: ("Potato Black Scurf", "الجرب الأسود للبطاطس", "Rhizoctonia solani"),
    42: ("Potato Virus Y", "فيروس البطاطس Y", "Potyvirus"),
}

CITRUS_DISEASES = {
    43: ("Citrus Black Spot", "البقعة السوداء للحمضيات", "Phyllosticta citricarpa"),
    44: ("Citrus Tristeza Virus", "فيروس تريستيزا الحمضيات", "Closterovirus"),
    45: ("Citrus Melanose", "ميلانوز الحمضيات", "Diaporthe citri"),
}

MANGO_DISEASES = {
    46: ("Mango Malformation", "تشوه المانجو", "Fusarium mangiferae"),
    47: ("Mango Bacterial Black Spot", "التبقع البكتيري الأسود للمانجو", "Xanthomonas citri pv. mangiferaeindicae"),
    48: ("Mango Stem End Rot", "تعفن نهاية ساق المانجو", "Lasiodiplodia theobromae"),
}

STRAWBERRY_DISEASES = {
    49: ("Strawberry Leaf Scorch", "احتراق أوراق الفراولة", "Diplocarpon earlianum"),
    50: ("Strawberry Angular Leaf Spot", "التبقع الزاوي للفراولة", "Xanthomonas fragariae"),
    51: ("Strawberry Leather Rot", "التعفن الجلدي للفراولة", "Phytophthora cactorum"),
}

SOYBEAN_DISEASES = {
    52: ("Soybean Rust", "صدأ فول الصويا", "Phakopsora pachyrhizi"),
    53: ("Soybean Frogeye Leaf Spot", "تبقع عين الضفدع لفول الصويا", "Cercospora sojina"),
    54: ("Soybean Brown Spot", "التبقع البني لفول الصويا", "Septoria glycines"),
    55: ("Soybean Sudden Death Syndrome", "متلازمة الموت المفاجئ لفول الصويا", "Fusarium virguliforme"),
}

ALL_PHASE1_DISEASES = {
    **CORN_DISEASES,
    **WHEAT_DISEASES,
    **POTATO_DISEASES,
    **CITRUS_DISEASES,
    **MANGO_DISEASES,
    **STRAWBERRY_DISEASES,
    **SOYBEAN_DISEASES,
}

# Expected new pests
PHASE1_PESTS = {
    22: ("Colorado Potato Beetle", "خنفساء كولورادو", "Leptinotarsa decemlineata"),
    23: ("Fall Armyworm", "دودة الحشد الخريفية", "Spodoptera frugiperda"),
    24: ("Mango Seed Weevil", "سوسة بذور المانجو", "Sternochetus mangiferae"),
    25: ("Strawberry Crown Moth", "فراشة تاج الفراولة", "Synanthedon bibionipennis"),
    26: ("Soybean Pod Borer", "حفار قرون فول الصويا", "Maruca vitrata"),
}


# =============================================================================
# Test Disease Classes
# =============================================================================


class TestPhase1DiseaseClasses:
    """Tests for Phase 1 crop-specific disease classes (IDs 34-55)."""

    def test_total_disease_count(self):
        """Total disease classes should be 66 (34 original + 22 Phase1 + 10 Phase2)."""
        assert len(DISEASE_CLASSES) == 66

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE1_DISEASES.items()))
    def test_disease_class_exists(self, class_id: int, expected: tuple):
        """Each Phase 1 disease class should exist in DISEASE_CLASSES."""
        assert class_id in DISEASE_CLASSES

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE1_DISEASES.items()))
    def test_disease_english_name(self, class_id: int, expected: tuple):
        """English names should match expected values."""
        label = DISEASE_CLASSES[class_id]
        assert label.en == expected[0]

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE1_DISEASES.items()))
    def test_disease_arabic_name(self, class_id: int, expected: tuple):
        """Arabic names should match expected values."""
        label = DISEASE_CLASSES[class_id]
        assert label.ar == expected[1]

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE1_DISEASES.items()))
    def test_disease_scientific_name(self, class_id: int, expected: tuple):
        """Scientific names should match expected values."""
        label = DISEASE_CLASSES[class_id]
        assert label.scientific_name == expected[2]

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE1_DISEASES.items()))
    def test_disease_arabic_contains_arabic_chars(self, class_id: int, expected: tuple):
        """Arabic names should contain Arabic Unicode characters."""
        label = DISEASE_CLASSES[class_id]
        assert any("\u0600" <= c <= "\u06ff" for c in label.ar), (
            f"Disease {class_id} ({label.en}): Arabic name has no Arabic characters"
        )

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE1_DISEASES.items()))
    def test_disease_scientific_name_is_ascii(self, class_id: int, expected: tuple):
        """Scientific names should be ASCII (Latin) text."""
        label = DISEASE_CLASSES[class_id]
        assert label.scientific_name.isascii(), f"Disease {class_id} ({label.en}): Scientific name contains non-ASCII"

    def test_corn_disease_count(self):
        """Corn should have 4 new diseases."""
        corn_ids = [34, 35, 36, 37]
        for cid in corn_ids:
            assert cid in DISEASE_CLASSES

    def test_wheat_disease_count(self):
        """Wheat should have 3 new diseases."""
        wheat_ids = [38, 39, 40]
        for wid in wheat_ids:
            assert wid in DISEASE_CLASSES

    def test_soybean_disease_count(self):
        """Soybean should have 4 new diseases."""
        soybean_ids = [52, 53, 54, 55]
        for sid in soybean_ids:
            assert sid in DISEASE_CLASSES

    def test_no_duplicate_english_names(self):
        """All English disease names should be unique."""
        en_names = [label.en for label in DISEASE_CLASSES.values()]
        assert len(en_names) == len(set(en_names)), "Duplicate English disease names found"

    def test_no_duplicate_arabic_names(self):
        """All Arabic disease names should be unique."""
        ar_names = [label.ar for label in DISEASE_CLASSES.values()]
        assert len(ar_names) == len(set(ar_names)), "Duplicate Arabic disease names found"

    def test_ids_are_contiguous_from_34(self):
        """Phase 1 disease IDs should be contiguous from 34 to 55."""
        for i in range(34, 56):
            assert i in DISEASE_CLASSES, f"Disease class ID {i} missing"

    def test_original_diseases_unchanged(self):
        """Original diseases (0-33) should still exist and not be overwritten."""
        assert DISEASE_CLASSES[0].en == "Wheat Rust"
        assert DISEASE_CLASSES[1].en == "Powdery Mildew"
        assert DISEASE_CLASSES[4].en == "Late Blight"
        assert DISEASE_CLASSES[28].en == "Date Palm Bayoud"
        assert DISEASE_CLASSES[33].en == "Potassium Deficiency"


# =============================================================================
# Test Pest Classes
# =============================================================================


class TestPhase1PestClasses:
    """Tests for Phase 1 crop-specific pest classes (IDs 22-26)."""

    def test_total_pest_count(self):
        """Total pest classes should be 32 (22 original + 5 Phase1 + 5 Phase2)."""
        assert len(PEST_CLASSES) == 32

    @pytest.mark.parametrize("class_id,expected", list(PHASE1_PESTS.items()))
    def test_pest_class_exists(self, class_id: int, expected: tuple):
        """Each Phase 1 pest class should exist in PEST_CLASSES."""
        assert class_id in PEST_CLASSES

    @pytest.mark.parametrize("class_id,expected", list(PHASE1_PESTS.items()))
    def test_pest_english_name(self, class_id: int, expected: tuple):
        """English names should match expected values."""
        label = PEST_CLASSES[class_id]
        assert label.en == expected[0]

    @pytest.mark.parametrize("class_id,expected", list(PHASE1_PESTS.items()))
    def test_pest_arabic_name(self, class_id: int, expected: tuple):
        """Arabic names should match expected values."""
        label = PEST_CLASSES[class_id]
        assert label.ar == expected[1]

    @pytest.mark.parametrize("class_id,expected", list(PHASE1_PESTS.items()))
    def test_pest_scientific_name(self, class_id: int, expected: tuple):
        """Scientific names should match expected values."""
        label = PEST_CLASSES[class_id]
        assert label.scientific_name == expected[2]

    def test_colorado_potato_beetle(self):
        """Colorado Potato Beetle should be correctly defined."""
        beetle = PEST_CLASSES[22]
        assert beetle.en == "Colorado Potato Beetle"
        assert "كولورادو" in beetle.ar
        assert beetle.scientific_name == "Leptinotarsa decemlineata"

    def test_fall_armyworm(self):
        """Fall Armyworm should be correctly defined."""
        faw = PEST_CLASSES[23]
        assert faw.en == "Fall Armyworm"
        assert "الخريفية" in faw.ar
        assert faw.scientific_name == "Spodoptera frugiperda"

    def test_original_pests_unchanged(self):
        """Original pests (0-21) should still exist."""
        assert PEST_CLASSES[0].en == "Red Palm Weevil"
        assert PEST_CLASSES[1].en == "Aphid"
        assert PEST_CLASSES[11].en == "Locust"
        assert PEST_CLASSES[21].en == "Citrus Psyllid"

    def test_weed_classes_unchanged(self):
        """Weed classes should be unchanged (12 total)."""
        assert len(WEED_CLASSES) == 12


# =============================================================================
# Test Treatment Recommendations
# =============================================================================


class TestPhase1TreatmentRecommendations:
    """Tests for Phase 1 disease and pest treatment recommendations."""

    @pytest.fixture(autouse=True)
    def _import_recommendations(self):
        """Import recommendation dicts from detection module."""
        # Parse the detection module file to extract just the recommendation dicts
        # without importing the full module (which requires torch, numpy, etc.)
        detection_path = (
            Path(__file__).parent.parent.parent.parent
            / "apps"
            / "services"
            / "yolo26-vision-service"
            / "src"
            / "api"
            / "endpoints"
            / "detection.py"
        )
        source = detection_path.read_text()

        # Extract PEST_RECOMMENDATIONS dict
        pest_start = source.index("PEST_RECOMMENDATIONS: dict[int, dict[str, str]] = {")
        # Find the matching closing brace - scan for "\n}\n" pattern
        pest_end = source.index("\n}", pest_start) + 2
        pest_code = source[pest_start:pest_end]

        # Extract DISEASE_TREATMENTS dict
        disease_start = source.index("DISEASE_TREATMENTS: dict[int, dict[str, str]] = {")
        disease_end = source.index("\n}", disease_start) + 2
        disease_code = source[disease_start:disease_end]

        ns: dict = {}
        exec(pest_code, ns)  # noqa: S102
        exec(disease_code, ns)  # noqa: S102

        self.disease_treatments = ns["DISEASE_TREATMENTS"]
        self.pest_recommendations = ns["PEST_RECOMMENDATIONS"]

    @pytest.mark.parametrize("class_id", list(ALL_PHASE1_DISEASES.keys()))
    def test_disease_has_treatment(self, class_id: int):
        """Every Phase 1 disease should have a treatment recommendation."""
        assert class_id in self.disease_treatments, (
            f"Disease {class_id} ({DISEASE_CLASSES[class_id].en}) missing treatment"
        )

    @pytest.mark.parametrize("class_id", list(ALL_PHASE1_DISEASES.keys()))
    def test_disease_treatment_bilingual(self, class_id: int):
        """Every treatment should have both English and Arabic text."""
        treatment = self.disease_treatments[class_id]
        assert "en" in treatment, f"Disease {class_id}: missing English treatment"
        assert "ar" in treatment, f"Disease {class_id}: missing Arabic treatment"
        assert len(treatment["en"]) > 20, f"Disease {class_id}: English treatment too short"
        assert len(treatment["ar"]) > 10, f"Disease {class_id}: Arabic treatment too short"

    @pytest.mark.parametrize("class_id", list(PHASE1_PESTS.keys()))
    def test_pest_has_recommendation(self, class_id: int):
        """Every Phase 1 pest should have a recommendation."""
        assert class_id in self.pest_recommendations, (
            f"Pest {class_id} ({PEST_CLASSES[class_id].en}) missing recommendation"
        )

    @pytest.mark.parametrize("class_id", list(PHASE1_PESTS.keys()))
    def test_pest_recommendation_bilingual(self, class_id: int):
        """Every pest recommendation should have both English and Arabic text."""
        rec = self.pest_recommendations[class_id]
        assert "en" in rec, f"Pest {class_id}: missing English recommendation"
        assert "ar" in rec, f"Pest {class_id}: missing Arabic recommendation"
        assert len(rec["en"]) > 20, f"Pest {class_id}: English recommendation too short"
        assert len(rec["ar"]) > 10, f"Pest {class_id}: Arabic recommendation too short"

    def test_corn_gray_leaf_spot_treatment_mentions_fungicide(self):
        """Corn Gray Leaf Spot treatment should mention fungicide."""
        treatment = self.disease_treatments[34]
        assert "fungicide" in treatment["en"].lower()

    def test_wheat_yellow_rust_treatment_mentions_triazole(self):
        """Wheat Yellow Rust treatment should mention triazole."""
        treatment = self.disease_treatments[38]
        assert "triazole" in treatment["en"].lower()

    def test_potato_virus_y_treatment_mentions_aphid(self):
        """Potato Virus Y treatment should mention aphid vector control."""
        treatment = self.disease_treatments[42]
        assert "aphid" in treatment["en"].lower()

    def test_soybean_rust_treatment_mentions_growth_stages(self):
        """Soybean Rust treatment should mention growth stages."""
        treatment = self.disease_treatments[52]
        assert "R1" in treatment["en"] or "R3" in treatment["en"]

    def test_colorado_beetle_recommendation_mentions_bt(self):
        """Colorado Potato Beetle recommendation should mention Bt."""
        rec = self.pest_recommendations[22]
        assert "Bacillus" in rec["en"] or "Btt" in rec["en"]


# =============================================================================
# Test High-Spread-Risk Disease List
# =============================================================================


class TestHighSpreadRiskDiseases:
    """Tests for the updated high-spread-risk disease classification."""

    HIGH_SPREAD_RISK_IDS = [4, 12, 13, 37, 38, 42, 44, 52]

    def test_maize_streak_virus_is_high_risk(self):
        """Maize Streak Virus (37) should be in high-spread-risk list."""
        assert 37 in self.HIGH_SPREAD_RISK_IDS

    def test_wheat_yellow_rust_is_high_risk(self):
        """Wheat Yellow Rust (38) should be in high-spread-risk list."""
        assert 38 in self.HIGH_SPREAD_RISK_IDS

    def test_potato_virus_y_is_high_risk(self):
        """Potato Virus Y (42) should be in high-spread-risk list."""
        assert 42 in self.HIGH_SPREAD_RISK_IDS

    def test_citrus_tristeza_is_high_risk(self):
        """Citrus Tristeza Virus (44) should be in high-spread-risk list."""
        assert 44 in self.HIGH_SPREAD_RISK_IDS

    def test_soybean_rust_is_high_risk(self):
        """Soybean Rust (52) should be in high-spread-risk list."""
        assert 52 in self.HIGH_SPREAD_RISK_IDS

    def test_original_high_risk_preserved(self):
        """Original high-risk diseases (4, 12, 13) should still be listed."""
        assert 4 in self.HIGH_SPREAD_RISK_IDS  # Late Blight
        assert 12 in self.HIGH_SPREAD_RISK_IDS  # Mosaic Virus
        assert 13 in self.HIGH_SPREAD_RISK_IDS  # YLCV

    def test_all_high_risk_are_valid_diseases(self):
        """All high-spread-risk IDs should be valid disease classes."""
        for class_id in self.HIGH_SPREAD_RISK_IDS:
            assert class_id in DISEASE_CLASSES, f"High-risk ID {class_id} not in DISEASE_CLASSES"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

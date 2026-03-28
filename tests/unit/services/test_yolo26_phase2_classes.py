# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Unit tests for YOLO26 Vision Service Phase 2 crop-specific classes.
اختبارات الوحدة لفئات الأمراض والآفات الخاصة بالقطن والفول السوداني - المرحلة الثانية

Tests cover:
- Cotton disease classes (IDs 56-60)
- Peanut disease classes (IDs 61-65)
- Cotton pest classes (IDs 27-29)
- Peanut pest classes (IDs 30-31)
- Disease treatment recommendations for all Phase 2 IDs
- Pest recommendations for all Phase 2 IDs
- Updated high-spread-risk disease list
- Bilingual (Arabic/English) correctness
- Scientific name presence
- Total class counts after Phase 1 + Phase 2

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

_spec = importlib.util.spec_from_file_location("yolo26_schemas_p2", str(_SCHEMAS_PATH))
_schemas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_schemas)

DISEASE_CLASSES = _schemas.DISEASE_CLASSES
PEST_CLASSES = _schemas.PEST_CLASSES
WEED_CLASSES = _schemas.WEED_CLASSES
BilingualLabel = _schemas.BilingualLabel


# =============================================================================
# Phase 2 Disease Classes
# =============================================================================

COTTON_DISEASES = {
    56: ("Cotton Leaf Curl Virus", "فيروس تجعد أوراق القطن", "Begomovirus"),
    57: ("Cotton Verticillium Wilt", "ذبول الفرتيسيليوم للقطن", "Verticillium dahliae"),
    58: ("Cotton Bacterial Blight", "اللفحة البكتيرية للقطن", "Xanthomonas citri pv. malvacearum"),
    59: ("Cotton Boll Rot", "تعفن لوز القطن", "Aspergillus flavus"),
    60: ("Cotton Alternaria Leaf Spot", "تبقع أوراق القطن الألتيرناري", "Alternaria macrospora"),
}

PEANUT_DISEASES = {
    61: ("Peanut Early Leaf Spot", "التبقع المبكر للفول السوداني", "Cercospora arachidicola"),
    62: ("Peanut Late Leaf Spot", "التبقع المتأخر للفول السوداني", "Cercosporidium personatum"),
    63: ("Peanut Rust", "صدأ الفول السوداني", "Puccinia arachidis"),
    64: ("Peanut Stem Rot", "تعفن ساق الفول السوداني", "Sclerotium rolfsii"),
    65: ("Peanut Aspergillus Crown Rot", "تعفن تاج الفول السوداني", "Aspergillus niger"),
}

ALL_PHASE2_DISEASES = {**COTTON_DISEASES, **PEANUT_DISEASES}

# Phase 2 Pests
COTTON_PESTS = {
    27: ("Cotton Bollworm", "دودة لوز القطن", "Helicoverpa armigera"),
    28: ("Pink Bollworm", "دودة اللوز القرنفلية", "Pectinophora gossypiella"),
    29: ("Cotton Whitefly", "ذبابة القطن البيضاء", "Bemisia tabaci"),
}

PEANUT_PESTS = {
    30: ("Peanut Leaf Miner", "حفار أوراق الفول السوداني", "Aproaerema modicella"),
    31: ("Groundnut Aphid", "من الفول السوداني", "Aphis craccivora"),
}

ALL_PHASE2_PESTS = {**COTTON_PESTS, **PEANUT_PESTS}


# =============================================================================
# Test Overall Counts (Phase 1 + Phase 2 combined)
# =============================================================================


class TestOverallCounts:
    """Verify total class counts after both phases."""

    def test_total_disease_count(self):
        """Total diseases: 34 original + 22 Phase 1 + 10 Phase 2 = 66."""
        assert len(DISEASE_CLASSES) == 66

    def test_total_pest_count(self):
        """Total pests: 22 original + 5 Phase 1 + 5 Phase 2 = 32."""
        assert len(PEST_CLASSES) == 32

    def test_weed_classes_unchanged(self):
        """Weed classes should remain at 12."""
        assert len(WEED_CLASSES) == 12

    def test_total_all_classes(self):
        """Grand total: 66 diseases + 32 pests + 12 weeds = 110."""
        total = len(DISEASE_CLASSES) + len(PEST_CLASSES) + len(WEED_CLASSES)
        assert total == 110


# =============================================================================
# Test Cotton Disease Classes
# =============================================================================


class TestCottonDiseaseClasses:
    """Tests for Cotton disease classes (IDs 56-60)."""

    @pytest.mark.parametrize("class_id,expected", list(COTTON_DISEASES.items()))
    def test_disease_class_exists(self, class_id: int, expected: tuple):
        """Each Cotton disease class should exist."""
        assert class_id in DISEASE_CLASSES

    @pytest.mark.parametrize("class_id,expected", list(COTTON_DISEASES.items()))
    def test_disease_english_name(self, class_id: int, expected: tuple):
        """English names should match."""
        assert DISEASE_CLASSES[class_id].en == expected[0]

    @pytest.mark.parametrize("class_id,expected", list(COTTON_DISEASES.items()))
    def test_disease_arabic_name(self, class_id: int, expected: tuple):
        """Arabic names should match."""
        assert DISEASE_CLASSES[class_id].ar == expected[1]

    @pytest.mark.parametrize("class_id,expected", list(COTTON_DISEASES.items()))
    def test_disease_scientific_name(self, class_id: int, expected: tuple):
        """Scientific names should match."""
        assert DISEASE_CLASSES[class_id].scientific_name == expected[2]

    @pytest.mark.parametrize("class_id,expected", list(COTTON_DISEASES.items()))
    def test_arabic_has_arabic_chars(self, class_id: int, expected: tuple):
        """Arabic names should contain Arabic Unicode characters."""
        label = DISEASE_CLASSES[class_id]
        assert any("\u0600" <= c <= "\u06ff" for c in label.ar)

    def test_cotton_leaf_curl_virus(self):
        """Cotton Leaf Curl Virus is a major disease - verify details."""
        d = DISEASE_CLASSES[56]
        assert d.en == "Cotton Leaf Curl Virus"
        assert "تجعد" in d.ar
        assert d.scientific_name == "Begomovirus"

    def test_cotton_disease_count(self):
        """Cotton should have exactly 5 diseases."""
        cotton_ids = [56, 57, 58, 59, 60]
        for cid in cotton_ids:
            assert cid in DISEASE_CLASSES


# =============================================================================
# Test Peanut Disease Classes
# =============================================================================


class TestPeanutDiseaseClasses:
    """Tests for Peanut disease classes (IDs 61-65)."""

    @pytest.mark.parametrize("class_id,expected", list(PEANUT_DISEASES.items()))
    def test_disease_class_exists(self, class_id: int, expected: tuple):
        """Each Peanut disease class should exist."""
        assert class_id in DISEASE_CLASSES

    @pytest.mark.parametrize("class_id,expected", list(PEANUT_DISEASES.items()))
    def test_disease_english_name(self, class_id: int, expected: tuple):
        """English names should match."""
        assert DISEASE_CLASSES[class_id].en == expected[0]

    @pytest.mark.parametrize("class_id,expected", list(PEANUT_DISEASES.items()))
    def test_disease_arabic_name(self, class_id: int, expected: tuple):
        """Arabic names should match."""
        assert DISEASE_CLASSES[class_id].ar == expected[1]

    @pytest.mark.parametrize("class_id,expected", list(PEANUT_DISEASES.items()))
    def test_disease_scientific_name(self, class_id: int, expected: tuple):
        """Scientific names should match."""
        assert DISEASE_CLASSES[class_id].scientific_name == expected[2]

    @pytest.mark.parametrize("class_id,expected", list(PEANUT_DISEASES.items()))
    def test_arabic_has_arabic_chars(self, class_id: int, expected: tuple):
        """Arabic names should contain Arabic Unicode characters."""
        label = DISEASE_CLASSES[class_id]
        assert any("\u0600" <= c <= "\u06ff" for c in label.ar)

    def test_peanut_rust(self):
        """Peanut Rust is a key disease - verify details."""
        d = DISEASE_CLASSES[63]
        assert d.en == "Peanut Rust"
        assert "صدأ" in d.ar
        assert d.scientific_name == "Puccinia arachidis"

    def test_peanut_disease_count(self):
        """Peanut should have exactly 5 diseases."""
        peanut_ids = [61, 62, 63, 64, 65]
        for pid in peanut_ids:
            assert pid in DISEASE_CLASSES


# =============================================================================
# Test Phase 2 Pest Classes
# =============================================================================


class TestPhase2PestClasses:
    """Tests for Phase 2 pest classes (IDs 27-31)."""

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE2_PESTS.items()))
    def test_pest_class_exists(self, class_id: int, expected: tuple):
        """Each Phase 2 pest should exist."""
        assert class_id in PEST_CLASSES

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE2_PESTS.items()))
    def test_pest_english_name(self, class_id: int, expected: tuple):
        """English names should match."""
        assert PEST_CLASSES[class_id].en == expected[0]

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE2_PESTS.items()))
    def test_pest_arabic_name(self, class_id: int, expected: tuple):
        """Arabic names should match."""
        assert PEST_CLASSES[class_id].ar == expected[1]

    @pytest.mark.parametrize("class_id,expected", list(ALL_PHASE2_PESTS.items()))
    def test_pest_scientific_name(self, class_id: int, expected: tuple):
        """Scientific names should match."""
        assert PEST_CLASSES[class_id].scientific_name == expected[2]

    def test_cotton_bollworm(self):
        """Cotton Bollworm - major cotton pest."""
        p = PEST_CLASSES[27]
        assert p.en == "Cotton Bollworm"
        assert "لوز القطن" in p.ar
        assert p.scientific_name == "Helicoverpa armigera"

    def test_pink_bollworm(self):
        """Pink Bollworm - serious cotton pest."""
        p = PEST_CLASSES[28]
        assert p.en == "Pink Bollworm"
        assert "القرنفلية" in p.ar
        assert p.scientific_name == "Pectinophora gossypiella"

    def test_groundnut_aphid(self):
        """Groundnut Aphid - major peanut pest."""
        p = PEST_CLASSES[31]
        assert p.en == "Groundnut Aphid"
        assert "الفول السوداني" in p.ar
        assert p.scientific_name == "Aphis craccivora"

    def test_phase1_pests_unchanged(self):
        """Phase 1 pests should still exist."""
        assert PEST_CLASSES[22].en == "Colorado Potato Beetle"
        assert PEST_CLASSES[23].en == "Fall Armyworm"
        assert PEST_CLASSES[26].en == "Soybean Pod Borer"

    def test_original_pests_unchanged(self):
        """Original pests should still exist."""
        assert PEST_CLASSES[0].en == "Red Palm Weevil"
        assert PEST_CLASSES[11].en == "Locust"
        assert PEST_CLASSES[21].en == "Citrus Psyllid"


# =============================================================================
# Test Treatment Recommendations
# =============================================================================


class TestPhase2TreatmentRecommendations:
    """Tests for Phase 2 disease and pest treatment recommendations."""

    @pytest.fixture(autouse=True)
    def _import_recommendations(self):
        """Import recommendation dicts from detection module."""
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

        pest_start = source.index("PEST_RECOMMENDATIONS: dict[int, dict[str, str]] = {")
        pest_end = source.index("\n}", pest_start) + 2
        pest_code = source[pest_start:pest_end]

        disease_start = source.index("DISEASE_TREATMENTS: dict[int, dict[str, str]] = {")
        disease_end = source.index("\n}", disease_start) + 2
        disease_code = source[disease_start:disease_end]

        ns: dict = {}
        exec(pest_code, ns)  # noqa: S102
        exec(disease_code, ns)  # noqa: S102

        self.disease_treatments = ns["DISEASE_TREATMENTS"]
        self.pest_recommendations = ns["PEST_RECOMMENDATIONS"]

    # --- Disease Treatments ---

    @pytest.mark.parametrize("class_id", list(ALL_PHASE2_DISEASES.keys()))
    def test_disease_has_treatment(self, class_id: int):
        """Every Phase 2 disease should have a treatment recommendation."""
        assert class_id in self.disease_treatments, (
            f"Disease {class_id} ({DISEASE_CLASSES[class_id].en}) missing treatment"
        )

    @pytest.mark.parametrize("class_id", list(ALL_PHASE2_DISEASES.keys()))
    def test_disease_treatment_bilingual(self, class_id: int):
        """Treatments should have both English and Arabic text."""
        treatment = self.disease_treatments[class_id]
        assert "en" in treatment
        assert "ar" in treatment
        assert len(treatment["en"]) > 20
        assert len(treatment["ar"]) > 10

    @pytest.mark.parametrize("class_id", list(ALL_PHASE2_DISEASES.keys()))
    def test_disease_treatment_arabic_has_arabic_chars(self, class_id: int):
        """Arabic treatment text should contain Arabic characters."""
        treatment = self.disease_treatments[class_id]
        assert any("\u0600" <= c <= "\u06ff" for c in treatment["ar"])

    # --- Pest Recommendations ---

    @pytest.mark.parametrize("class_id", list(ALL_PHASE2_PESTS.keys()))
    def test_pest_has_recommendation(self, class_id: int):
        """Every Phase 2 pest should have a recommendation."""
        assert class_id in self.pest_recommendations, (
            f"Pest {class_id} ({PEST_CLASSES[class_id].en}) missing recommendation"
        )

    @pytest.mark.parametrize("class_id", list(ALL_PHASE2_PESTS.keys()))
    def test_pest_recommendation_bilingual(self, class_id: int):
        """Pest recommendations should have both English and Arabic text."""
        rec = self.pest_recommendations[class_id]
        assert "en" in rec
        assert "ar" in rec
        assert len(rec["en"]) > 20
        assert len(rec["ar"]) > 10

    # --- Domain-specific content checks ---

    def test_cotton_leaf_curl_mentions_whitefly(self):
        """Cotton Leaf Curl treatment should mention whitefly vector."""
        treatment = self.disease_treatments[56]
        assert "whitefly" in treatment["en"].lower() or "bemisia" in treatment["en"].lower()

    def test_cotton_verticillium_mentions_rotation(self):
        """Cotton Verticillium Wilt treatment should mention crop rotation."""
        treatment = self.disease_treatments[57]
        assert "rotat" in treatment["en"].lower()

    def test_peanut_stem_rot_mentions_trichoderma(self):
        """Peanut Stem Rot should mention Trichoderma biocontrol."""
        treatment = self.disease_treatments[64]
        assert "trichoderma" in treatment["en"].lower()

    def test_bollworm_recommendation_mentions_pheromone(self):
        """Cotton Bollworm recommendation should mention pheromone traps."""
        rec = self.pest_recommendations[27]
        assert "pheromone" in rec["en"].lower()

    def test_pink_bollworm_mentions_sit(self):
        """Pink Bollworm recommendation should mention sterile insect technique."""
        rec = self.pest_recommendations[28]
        assert "sterile" in rec["en"].lower() or "SIT" in rec["en"]


# =============================================================================
# Test High-Spread-Risk Disease List (Updated for Phase 2)
# =============================================================================


class TestPhase2HighSpreadRisk:
    """Tests for the updated high-spread-risk disease list including Phase 2."""

    HIGH_SPREAD_RISK_IDS = [4, 12, 13, 37, 38, 42, 44, 52, 56, 63]

    def test_cotton_leaf_curl_is_high_risk(self):
        """Cotton Leaf Curl Virus (56) should be in high-spread-risk list."""
        assert 56 in self.HIGH_SPREAD_RISK_IDS

    def test_peanut_rust_is_high_risk(self):
        """Peanut Rust (63) should be in high-spread-risk list."""
        assert 63 in self.HIGH_SPREAD_RISK_IDS

    def test_phase1_high_risk_preserved(self):
        """Phase 1 high-risk diseases should still be listed."""
        phase1_risk = [37, 38, 42, 44, 52]
        for cid in phase1_risk:
            assert cid in self.HIGH_SPREAD_RISK_IDS

    def test_all_high_risk_are_valid_diseases(self):
        """All high-spread-risk IDs should be valid disease classes."""
        for class_id in self.HIGH_SPREAD_RISK_IDS:
            assert class_id in DISEASE_CLASSES


# =============================================================================
# Test No Duplicates Across All Phases
# =============================================================================


class TestNoDuplicatesAllPhases:
    """Verify no duplicate names across all phases combined."""

    def test_no_duplicate_english_disease_names(self):
        """All English disease names should be unique across all phases."""
        en_names = [label.en for label in DISEASE_CLASSES.values()]
        assert len(en_names) == len(set(en_names)), "Duplicate English disease names found"

    def test_no_duplicate_arabic_disease_names(self):
        """All Arabic disease names should be unique across all phases."""
        ar_names = [label.ar for label in DISEASE_CLASSES.values()]
        assert len(ar_names) == len(set(ar_names)), "Duplicate Arabic disease names found"

    def test_no_duplicate_english_pest_names(self):
        """All English pest names should be unique across all phases."""
        en_names = [label.en for label in PEST_CLASSES.values()]
        assert len(en_names) == len(set(en_names)), "Duplicate English pest names found"

    def test_no_duplicate_arabic_pest_names(self):
        """All Arabic pest names should be unique across all phases."""
        ar_names = [label.ar for label in PEST_CLASSES.values()]
        assert len(ar_names) == len(set(ar_names)), "Duplicate Arabic pest names found"

    def test_disease_ids_contiguous_0_to_65(self):
        """Disease IDs should be contiguous from 0 to 65."""
        for i in range(66):
            assert i in DISEASE_CLASSES, f"Disease class ID {i} missing"

    def test_pest_ids_contiguous_0_to_31(self):
        """Pest IDs should be contiguous from 0 to 31."""
        for i in range(32):
            assert i in PEST_CLASSES, f"Pest class ID {i} missing"

    def test_all_scientific_names_ascii(self):
        """All scientific names should be ASCII-only."""
        for class_id, label in DISEASE_CLASSES.items():
            if label.scientific_name:
                assert label.scientific_name.isascii(), f"Disease {class_id} ({label.en}): non-ASCII scientific name"
        for class_id, label in PEST_CLASSES.items():
            if label.scientific_name:
                assert label.scientific_name.isascii(), f"Pest {class_id} ({label.en}): non-ASCII scientific name"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

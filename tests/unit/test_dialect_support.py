"""Tests for Arabic dialect support."""
import pytest
from shared.nlp.dialect_support import (
    ArabicDialectProcessor,
    ArabicDialect,
    AGRI_TERMS_DICT,
    DIALECT_VOCABULARY,
)


class TestDialectDetection:
    def setup_method(self):
        self.proc = ArabicDialectProcessor()

    def test_detect_yemeni(self):
        result = self.proc.detect_dialect("الغيل فيه مي كثير والسقي كويس")
        assert result.detected_dialect == ArabicDialect.YEMENI

    def test_detect_saudi(self):
        result = self.proc.detect_dialect("النخل عندنا فيه سوسة والمحور يحتاج صيانة")
        assert result.detected_dialect == ArabicDialect.SAUDI

    def test_detect_iraqi(self):
        result = self.proc.detect_dialect("الحنطة بالشط والتمن بالهور")
        assert result.detected_dialect == ArabicDialect.IRAQI

    def test_detect_egyptian(self):
        result = self.proc.detect_dialect("الغيط محتاج طلمبة والترعة فيها ميه")
        assert result.detected_dialect == ArabicDialect.EGYPTIAN

    def test_detect_msa_default(self):
        result = self.proc.detect_dialect("القمح يحتاج إلى ري منتظم")
        assert result.detected_dialect == ArabicDialect.MSA

    def test_normalize_to_msa(self):
        text = "حنطة"
        normalized = self.proc.normalize_to_msa(text)
        assert normalized == "قمح"


class TestTermTranslation:
    def setup_method(self):
        self.proc = ArabicDialectProcessor()

    def test_translate_ndvi(self):
        result = self.proc.translate_term("ndvi")
        assert result is not None
        assert result.arabic == "مؤشر الغطاء النباتي"

    def test_translate_unknown(self):
        result = self.proc.translate_term("xyz_unknown")
        assert result is None

    def test_all_terms_have_arabic(self):
        for term, info in AGRI_TERMS_DICT.items():
            assert "ar" in info, f"Term {term} missing Arabic"
            assert "en" in info, f"Term {term} missing English"


class TestDialectVocabulary:
    def test_all_dialects_have_vocabulary(self):
        for dialect in [ArabicDialect.YEMENI, ArabicDialect.SAUDI,
                       ArabicDialect.IRAQI, ArabicDialect.EGYPTIAN]:
            assert dialect in DIALECT_VOCABULARY
            assert len(DIALECT_VOCABULARY[dialect]) > 5

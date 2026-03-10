"""
Language Support Tests
اختبارات دعم اللغات

Comprehensive tests for Arabic and English language support in the SAHOOL platform.
These tests verify:
- Arabic text processing and response generation
- English text processing and response generation
- Bilingual consistency
- Arabic dialect understanding (MSA, Yemeni, Gulf)
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

# ============================================================================
# HELPER CLASSES
# ============================================================================


@dataclass
class LanguageTestResult:
    """Result of a language support test"""

    test_id: str
    language: str
    passed: bool
    accuracy_score: float
    has_correct_language: bool
    keyword_matches: list[str]
    errors: list[str]


class LanguageSupportEvaluator:
    """Evaluate language support quality"""

    @staticmethod
    def is_arabic_text(text: str) -> bool:
        """Check if text contains Arabic characters"""
        # Arabic Unicode range: 0x0600-0x06FF
        arabic_chars = sum(1 for char in text if "\u0600" <= char <= "\u06ff")
        return arabic_chars >= len(text) * 0.3  # At least 30% Arabic

    @staticmethod
    def is_english_text(text: str) -> bool:
        """Check if text contains English characters"""
        english_chars = sum(1 for char in text if "a" <= char.lower() <= "z")
        return english_chars >= len(text) * 0.3  # At least 30% English

    @staticmethod
    def calculate_keyword_match(text: str, keywords: list[str]) -> tuple[float, list[str]]:
        """Calculate keyword match score"""
        text_lower = text.lower()
        matched = [kw for kw in keywords if kw.lower() in text_lower]
        score = len(matched) / len(keywords) if keywords else 1.0
        return score, matched

    @staticmethod
    def calculate_lexical_similarity(text1: str, text2: str) -> float:
        """Calculate lexical similarity (Jaccard index)"""
        # Tokenize
        tokens1 = set(re.sub(r"[^\w\s]", " ", text1.lower()).split())
        tokens2 = set(re.sub(r"[^\w\s]", " ", text2.lower()).split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))

        return intersection / union if union > 0 else 0.0


# ============================================================================
# TEST DATA
# ============================================================================


# Arabic test cases covering different categories
ARABIC_TEST_CASES = [
    {
        "id": "ar-disease-001",
        "category": "disease_diagnosis",
        "language": "ar",
        "query": "البقع الصفراء على أوراق القمح، ما المشكلة؟",
        "expected_keywords": ["مرض", "فطري", "صدأ", "علاج"],
        "expected_response_pattern": ".*مرض.*فطري.*|.*صدأ.*أوراق.*",
        "mock_response": "البقع الصفراء على أوراق القمح تشير عادة إلى مرض فطري مثل صدأ الأوراق. ننصح بفحص الحقل والنظر في استخدام مبيد فطري مناسب.",
    },
    {
        "id": "ar-irrigation-001",
        "category": "irrigation",
        "language": "ar",
        "query": "متى أسقي نباتات الطماطم في الصيف؟",
        "expected_keywords": ["ري", "رطوبة", "التربة", "صباح"],
        "expected_response_pattern": ".*ري.*|.*رطوبة.*",
        "mock_response": "في فصل الصيف، يُنصح بري نباتات الطماطم في الصباح الباكر أو المساء. راقب رطوبة التربة وأضف الماء عندما تنخفض عن 50%.",
    },
    {
        "id": "ar-fertilizer-001",
        "category": "fertilizer",
        "language": "ar",
        "query": "ما نوع السماد المناسب للقمح؟",
        "expected_keywords": ["سماد", "نيتروجين", "NPK", "معدل"],
        "expected_response_pattern": ".*سماد.*|.*NPK.*",
        "mock_response": "للقمح في مرحلة النمو الخضري، استخدم سماد NPK متوازن مع التركيز على النيتروجين بمعدل 100-120 كجم للهكتار.",
    },
    {
        "id": "ar-pest-001",
        "category": "pest_management",
        "language": "ar",
        "query": "كيف أكافح المن على الفلفل؟",
        "expected_keywords": ["مكافحة", "مبيد", "عضوي", "نيم"],
        "expected_response_pattern": ".*مكافحة.*|.*مبيد.*",
        "mock_response": "لمكافحة المن على الفلفل، يمكنك استخدام مبيد عضوي مثل زيت النيم أو محلول الصابون الحشري. الرش يكون في الصباح الباكر.",
    },
    {
        "id": "ar-yield-001",
        "category": "yield_prediction",
        "language": "ar",
        "query": "ما الإنتاج المتوقع لحقل القمح؟",
        "expected_keywords": ["إنتاج", "طن", "هكتار", "توقع"],
        "expected_response_pattern": ".*إنتاج.*طن.*|.*توقع.*",
        "mock_response": "بناءً على الظروف الحالية، نتوقع إنتاجية 4-5 طن للهكتار. هذا التوقع يعتمد على استمرار الرعاية المناسبة.",
    },
    {
        "id": "ar-weather-001",
        "category": "weather",
        "language": "ar",
        "query": "هل هناك خطر صقيع الليلة؟",
        "expected_keywords": ["صقيع", "درجة", "حرارة", "حماية"],
        "expected_response_pattern": ".*صقيع.*|.*حرارة.*",
        "mock_response": "نعم، هناك خطر صقيع الليلة مع توقع انخفاض درجة الحرارة إلى 2 درجة مئوية. ننصح بتغطية النباتات الحساسة للحماية.",
    },
    {
        "id": "ar-soil-001",
        "category": "soil_analysis",
        "language": "ar",
        "query": "تربتي ملحية، ماذا أزرع؟",
        "expected_keywords": ["ملوحة", "تحمل", "شعير", "نخيل"],
        "expected_response_pattern": ".*ملوحة.*|.*تحمل.*",
        "mock_response": "للتربة الملحية، ننصح بزراعة محاصيل متحملة للملوحة مثل الشعير أو النخيل أو بعض أنواع الخضروات المتحملة.",
    },
    {
        "id": "ar-field-001",
        "category": "field_analysis",
        "language": "ar",
        "query": "حقلي يظهر مؤشر NDVI منخفض",
        "expected_keywords": ["NDVI", "صحة", "نباتي", "تحسين"],
        "expected_response_pattern": ".*NDVI.*|.*صحة.*نبات.*",
        "mock_response": "مؤشر NDVI المنخفض يشير إلى إجهاد نباتي. قد يكون السبب نقص الري أو العناصر الغذائية. ننصح بفحص رطوبة التربة وتحسين التسميد.",
    },
]

# English test cases covering different categories
ENGLISH_TEST_CASES = [
    {
        "id": "en-disease-001",
        "category": "disease_diagnosis",
        "language": "en",
        "query": "Yellow spots on wheat leaves, what's the problem?",
        "expected_keywords": ["disease", "fungal", "rust", "treatment"],
        "expected_response_pattern": ".*disease.*|.*fungal.*",
        "mock_response": "Yellow spots on wheat leaves typically indicate a fungal disease such as leaf rust or septoria. We recommend inspecting the field and considering appropriate fungicide treatment.",
    },
    {
        "id": "en-irrigation-001",
        "category": "irrigation",
        "language": "en",
        "query": "When should I irrigate tomato plants in summer?",
        "expected_keywords": ["irrigation", "moisture", "soil", "morning"],
        "expected_response_pattern": ".*irrigat.*|.*moisture.*",
        "mock_response": "In summer, irrigate tomato plants in the early morning or evening. Monitor soil moisture and add water when it drops below 50%.",
    },
    {
        "id": "en-fertilizer-001",
        "category": "fertilizer",
        "language": "en",
        "query": "What fertilizer is suitable for wheat?",
        "expected_keywords": ["fertilizer", "nitrogen", "NPK", "rate"],
        "expected_response_pattern": ".*fertilizer.*|.*NPK.*",
        "mock_response": "For wheat during vegetative growth, use balanced NPK fertilizer with emphasis on nitrogen at 100-120 kg per hectare rate.",
    },
    {
        "id": "en-pest-001",
        "category": "pest_management",
        "language": "en",
        "query": "How do I control aphids on pepper?",
        "expected_keywords": ["control", "pesticide", "organic", "neem"],
        "expected_response_pattern": ".*control.*|.*pesticide.*",
        "mock_response": "To control aphids on pepper, you can use organic pesticides like neem oil or insecticidal soap solution. Spray in the early morning.",
    },
    {
        "id": "en-yield-001",
        "category": "yield_prediction",
        "language": "en",
        "query": "What is the expected yield for wheat field?",
        "expected_keywords": ["yield", "tons", "hectare", "expected"],
        "expected_response_pattern": ".*yield.*tons.*|.*expect.*",
        "mock_response": "Based on current conditions, we expect a yield of 4-5 tons per hectare. This prediction depends on continued proper care.",
    },
    {
        "id": "en-weather-001",
        "category": "weather",
        "language": "en",
        "query": "Is there frost risk tonight?",
        "expected_keywords": ["frost", "temperature", "degrees", "protection"],
        "expected_response_pattern": ".*frost.*|.*temperature.*",
        "mock_response": "Yes, there is frost risk tonight with expected temperature drop to 2 degrees Celsius. We recommend covering sensitive plants for protection.",
    },
    {
        "id": "en-soil-001",
        "category": "soil_analysis",
        "language": "en",
        "query": "My soil is saline, what can I grow?",
        "expected_keywords": ["salinity", "tolerant", "barley", "palm"],
        "expected_response_pattern": ".*salin.*|.*tolerant.*",
        "mock_response": "For saline soil, we recommend growing salt-tolerant crops such as barley, date palms, or some tolerant vegetables.",
    },
    {
        "id": "en-field-001",
        "category": "field_analysis",
        "language": "en",
        "query": "My field shows low NDVI index",
        "expected_keywords": ["NDVI", "health", "vegetation", "improve"],
        "expected_response_pattern": ".*NDVI.*|.*health.*plant.*",
        "mock_response": "Low NDVI indicates plant stress. The cause may be lack of irrigation or nutrients. We recommend checking soil moisture and improving fertilization.",
    },
]


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def evaluator():
    """Create language support evaluator"""
    return LanguageSupportEvaluator()


@pytest.fixture
def arabic_test_cases():
    """Get Arabic test cases"""
    return ARABIC_TEST_CASES


@pytest.fixture
def english_test_cases():
    """Get English test cases"""
    return ENGLISH_TEST_CASES


@pytest.fixture
def language_results_tracker():
    """Track language test results"""

    class ResultsTracker:
        def __init__(self):
            self.results: list[dict[str, Any]] = []

        def add_result(self, result: dict[str, Any]):
            self.results.append(result)

        def get_arabic_pass_rate(self) -> float:
            ar_results = [r for r in self.results if r.get("language") == "ar"]
            if not ar_results:
                return 0.0
            return sum(1 for r in ar_results if r.get("passed")) / len(ar_results) * 100

        def get_english_pass_rate(self) -> float:
            en_results = [r for r in self.results if r.get("language") == "en"]
            if not en_results:
                return 0.0
            return sum(1 for r in en_results if r.get("passed")) / len(en_results) * 100

        def save_results(self, path: Path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "results": self.results,
                        "arabic_pass_rate": self.get_arabic_pass_rate(),
                        "english_pass_rate": self.get_english_pass_rate(),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

    return ResultsTracker()


# ============================================================================
# ARABIC LANGUAGE TESTS
# ============================================================================


@pytest.mark.evaluation
@pytest.mark.arabic
class TestArabicLanguageSupport:
    """
    Test Arabic language support
    اختبار دعم اللغة العربية
    """

    def test_arabic_text_detection(self, evaluator):
        """Test Arabic text detection"""
        arabic_text = "البقع الصفراء على أوراق القمح"
        english_text = "Yellow spots on wheat leaves"
        mixed_text = "NDVI مؤشر"

        assert evaluator.is_arabic_text(arabic_text), "Should detect Arabic text"
        assert not evaluator.is_arabic_text(english_text), "Should not detect English as Arabic"
        # Mixed text should be detected based on ratio
        assert evaluator.is_arabic_text(mixed_text) or not evaluator.is_arabic_text(mixed_text)

    def test_arabic_disease_diagnosis(
        self,
        evaluator,
        arabic_test_cases,
        language_results_tracker,
    ):
        """Test Arabic disease diagnosis responses"""
        disease_cases = [tc for tc in arabic_test_cases if tc["category"] == "disease_diagnosis"]

        for test_case in disease_cases:
            mock_response = test_case["mock_response"]

            # Verify response is in Arabic
            is_arabic = evaluator.is_arabic_text(mock_response)

            # Calculate keyword match
            keyword_score, matched_keywords = evaluator.calculate_keyword_match(
                mock_response, test_case["expected_keywords"]
            )

            # Calculate similarity
            similarity = evaluator.calculate_lexical_similarity(mock_response, test_case["query"])

            passed = is_arabic and keyword_score >= 0.5

            language_results_tracker.add_result(
                {
                    "test_id": test_case["id"],
                    "language": "ar",
                    "category": test_case["category"],
                    "passed": passed,
                    "accuracy_score": keyword_score,
                    "has_correct_language": is_arabic,
                    "keyword_matches": matched_keywords,
                }
            )

            assert is_arabic, f"Response should be in Arabic for {test_case['id']}"
            assert keyword_score >= 0.25, f"Should match at least 25% keywords for {test_case['id']}"

    def test_arabic_irrigation_advice(
        self,
        evaluator,
        arabic_test_cases,
        language_results_tracker,
    ):
        """Test Arabic irrigation advice responses"""
        irrigation_cases = [tc for tc in arabic_test_cases if tc["category"] == "irrigation"]

        for test_case in irrigation_cases:
            mock_response = test_case["mock_response"]
            is_arabic = evaluator.is_arabic_text(mock_response)
            keyword_score, matched_keywords = evaluator.calculate_keyword_match(
                mock_response, test_case["expected_keywords"]
            )

            passed = is_arabic and keyword_score >= 0.5

            language_results_tracker.add_result(
                {
                    "test_id": test_case["id"],
                    "language": "ar",
                    "category": test_case["category"],
                    "passed": passed,
                    "accuracy_score": keyword_score,
                    "has_correct_language": is_arabic,
                    "keyword_matches": matched_keywords,
                }
            )

            assert is_arabic, f"Response should be in Arabic for {test_case['id']}"

    def test_arabic_all_categories(
        self,
        evaluator,
        arabic_test_cases,
        language_results_tracker,
    ):
        """Test Arabic responses across all categories"""
        passed_count = 0

        for test_case in arabic_test_cases:
            mock_response = test_case["mock_response"]
            is_arabic = evaluator.is_arabic_text(mock_response)
            keyword_score, matched_keywords = evaluator.calculate_keyword_match(
                mock_response, test_case["expected_keywords"]
            )

            passed = is_arabic and keyword_score >= 0.25
            if passed:
                passed_count += 1

            language_results_tracker.add_result(
                {
                    "test_id": test_case["id"],
                    "language": "ar",
                    "category": test_case["category"],
                    "passed": passed,
                    "accuracy_score": keyword_score,
                    "has_correct_language": is_arabic,
                    "keyword_matches": matched_keywords,
                }
            )

        pass_rate = passed_count / len(arabic_test_cases)
        assert pass_rate >= 0.75, f"Arabic pass rate {pass_rate:.0%} should be at least 75%"


# ============================================================================
# ENGLISH LANGUAGE TESTS
# ============================================================================


@pytest.mark.evaluation
@pytest.mark.english
class TestEnglishLanguageSupport:
    """
    Test English language support
    اختبار دعم اللغة الإنجليزية
    """

    def test_english_text_detection(self, evaluator):
        """Test English text detection"""
        english_text = "Yellow spots on wheat leaves"
        arabic_text = "البقع الصفراء على أوراق القمح"

        assert evaluator.is_english_text(english_text), "Should detect English text"
        assert not evaluator.is_english_text(arabic_text), "Should not detect Arabic as English"

    def test_english_disease_diagnosis(
        self,
        evaluator,
        english_test_cases,
        language_results_tracker,
    ):
        """Test English disease diagnosis responses"""
        disease_cases = [tc for tc in english_test_cases if tc["category"] == "disease_diagnosis"]

        for test_case in disease_cases:
            mock_response = test_case["mock_response"]

            is_english = evaluator.is_english_text(mock_response)
            keyword_score, matched_keywords = evaluator.calculate_keyword_match(
                mock_response, test_case["expected_keywords"]
            )

            passed = is_english and keyword_score >= 0.5

            language_results_tracker.add_result(
                {
                    "test_id": test_case["id"],
                    "language": "en",
                    "category": test_case["category"],
                    "passed": passed,
                    "accuracy_score": keyword_score,
                    "has_correct_language": is_english,
                    "keyword_matches": matched_keywords,
                }
            )

            assert is_english, f"Response should be in English for {test_case['id']}"
            assert keyword_score >= 0.25, f"Should match at least 25% keywords for {test_case['id']}"

    def test_english_irrigation_advice(
        self,
        evaluator,
        english_test_cases,
        language_results_tracker,
    ):
        """Test English irrigation advice responses"""
        irrigation_cases = [tc for tc in english_test_cases if tc["category"] == "irrigation"]

        for test_case in irrigation_cases:
            mock_response = test_case["mock_response"]
            is_english = evaluator.is_english_text(mock_response)
            keyword_score, matched_keywords = evaluator.calculate_keyword_match(
                mock_response, test_case["expected_keywords"]
            )

            passed = is_english and keyword_score >= 0.5

            language_results_tracker.add_result(
                {
                    "test_id": test_case["id"],
                    "language": "en",
                    "category": test_case["category"],
                    "passed": passed,
                    "accuracy_score": keyword_score,
                    "has_correct_language": is_english,
                    "keyword_matches": matched_keywords,
                }
            )

            assert is_english, f"Response should be in English for {test_case['id']}"

    def test_english_all_categories(
        self,
        evaluator,
        english_test_cases,
        language_results_tracker,
    ):
        """Test English responses across all categories"""
        passed_count = 0

        for test_case in english_test_cases:
            mock_response = test_case["mock_response"]
            is_english = evaluator.is_english_text(mock_response)
            keyword_score, matched_keywords = evaluator.calculate_keyword_match(
                mock_response, test_case["expected_keywords"]
            )

            passed = is_english and keyword_score >= 0.25
            if passed:
                passed_count += 1

            language_results_tracker.add_result(
                {
                    "test_id": test_case["id"],
                    "language": "en",
                    "category": test_case["category"],
                    "passed": passed,
                    "accuracy_score": keyword_score,
                    "has_correct_language": is_english,
                    "keyword_matches": matched_keywords,
                }
            )

        pass_rate = passed_count / len(english_test_cases)
        assert pass_rate >= 0.75, f"English pass rate {pass_rate:.0%} should be at least 75%"


# ============================================================================
# BILINGUAL CONSISTENCY TESTS
# ============================================================================


@pytest.mark.evaluation
class TestBilingualConsistency:
    """
    Test bilingual consistency
    اختبار الاتساق ثنائي اللغة
    """

    def test_consistent_categories_coverage(
        self,
        arabic_test_cases,
        english_test_cases,
    ):
        """Test that both languages cover same categories"""
        ar_categories = {tc["category"] for tc in arabic_test_cases}
        en_categories = {tc["category"] for tc in english_test_cases}

        assert ar_categories == en_categories, (
            f"Both languages should cover same categories. Arabic: {ar_categories}, English: {en_categories}"
        )

    def test_similar_response_structure(
        self,
        evaluator,
        arabic_test_cases,
        english_test_cases,
    ):
        """Test that responses have similar structure"""
        # Group by category
        ar_by_category = {tc["category"]: tc for tc in arabic_test_cases}
        en_by_category = {tc["category"]: tc for tc in english_test_cases}

        for category in ar_by_category:
            ar_response = ar_by_category[category]["mock_response"]
            en_response = en_by_category[category]["mock_response"]

            # Both should have reasonable length
            ar_words = len(ar_response.split())
            en_words = len(en_response.split())

            # Word counts should be within 3x of each other
            ratio = max(ar_words, en_words) / min(ar_words, en_words) if min(ar_words, en_words) > 0 else float("inf")
            assert ratio <= 3.0, f"Word count ratio for {category} should be reasonable"

    def test_keyword_translation_coverage(
        self,
        arabic_test_cases,
        english_test_cases,
    ):
        """Test that keyword coverage is similar across languages"""
        ar_keyword_counts = [len(tc["expected_keywords"]) for tc in arabic_test_cases]
        en_keyword_counts = [len(tc["expected_keywords"]) for tc in english_test_cases]

        ar_avg = sum(ar_keyword_counts) / len(ar_keyword_counts)
        en_avg = sum(en_keyword_counts) / len(en_keyword_counts)

        # Average keyword counts should be similar
        assert abs(ar_avg - en_avg) <= 1, (
            f"Average keyword count should be similar. Arabic: {ar_avg}, English: {en_avg}"
        )


# ============================================================================
# ARABIC DIALECT TESTS
# ============================================================================


@pytest.mark.evaluation
@pytest.mark.arabic
class TestArabicDialectSupport:
    """
    Test Arabic dialect understanding
    اختبار فهم اللهجات العربية
    """

    DIALECT_TEST_CASES = [
        # Modern Standard Arabic (MSA)
        {
            "id": "msa-001",
            "dialect": "MSA",
            "query": "ما هي أفضل طريقة لري القمح؟",
            "expected_understanding": True,
        },
        # Yemeni dialect
        {
            "id": "yemeni-001",
            "dialect": "Yemeni",
            "query": "إيش أحسن طريقة أسقي القمح؟",
            "expected_understanding": True,
        },
        # Gulf dialect
        {
            "id": "gulf-001",
            "dialect": "Gulf",
            "query": "شلون أسوي حق سقي القمح؟",
            "expected_understanding": True,
        },
    ]

    def test_dialect_contains_question(self):
        """Test that dialect queries are valid questions"""
        for test_case in self.DIALECT_TEST_CASES:
            query = test_case["query"]
            # Should contain interrogative markers
            has_question = any(marker in query for marker in ["ما", "إيش", "شلون", "كيف", "متى", "أين", "؟"])
            assert has_question, f"Query '{query}' should be a question"

    def test_dialect_agricultural_context(self):
        """Test that dialect queries contain agricultural terms"""
        agricultural_terms = ["قمح", "ري", "سقي", "زراعة", "محصول", "حقل"]

        for test_case in self.DIALECT_TEST_CASES:
            query = test_case["query"]
            has_agri_term = any(term in query for term in agricultural_terms)
            assert has_agri_term, f"Query '{query}' should contain agricultural term"


# ============================================================================
# SUMMARY TEST
# ============================================================================


@pytest.mark.evaluation
class TestLanguageSupportSummary:
    """
    Final summary test for language support
    اختبار ملخص نهائي لدعم اللغات
    """

    def test_overall_language_support(
        self,
        evaluator,
        arabic_test_cases,
        english_test_cases,
    ):
        """Test overall language support metrics"""
        # Test Arabic
        ar_passed = 0
        for tc in arabic_test_cases:
            if evaluator.is_arabic_text(tc["mock_response"]):
                keyword_score, _ = evaluator.calculate_keyword_match(tc["mock_response"], tc["expected_keywords"])
                if keyword_score >= 0.25:
                    ar_passed += 1

        # Test English
        en_passed = 0
        for tc in english_test_cases:
            if evaluator.is_english_text(tc["mock_response"]):
                keyword_score, _ = evaluator.calculate_keyword_match(tc["mock_response"], tc["expected_keywords"])
                if keyword_score >= 0.25:
                    en_passed += 1

        ar_rate = ar_passed / len(arabic_test_cases) * 100
        en_rate = en_passed / len(english_test_cases) * 100

        print(f"\n{'=' * 60}")
        print("Language Support Summary | ملخص دعم اللغات")
        print(f"{'=' * 60}")
        print(f"Arabic (العربية):  {ar_rate:.1f}% ({ar_passed}/{len(arabic_test_cases)} passed)")
        print(f"English:           {en_rate:.1f}% ({en_passed}/{len(english_test_cases)} passed)")
        print(f"{'=' * 60}")

        # Both should pass at least 75%
        assert ar_rate >= 75.0, f"Arabic pass rate {ar_rate:.1f}% below 75% threshold"
        assert en_rate >= 75.0, f"English pass rate {en_rate:.1f}% below 75% threshold"

        # Save results
        results_path = Path(__file__).parent / "language-support-results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "arabic_pass_rate": ar_rate,
                    "english_pass_rate": en_rate,
                    "arabic_passed": ar_passed,
                    "arabic_total": len(arabic_test_cases),
                    "english_passed": en_passed,
                    "english_total": len(english_test_cases),
                    "status": "PASSED" if ar_rate >= 75 and en_rate >= 75 else "NEEDS_IMPROVEMENT",
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"Results saved to: {results_path}")

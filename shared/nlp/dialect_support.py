"""
Arabic Dialect Support for Agricultural NLP | دعم اللهجات العربية للمعالجة اللغوية الزراعية

Supports regional dialects: Yemeni, Saudi, Iraqi, Egyptian
Provides agricultural vocabulary translation and normalization.

This is a SAHOOL-exclusive feature - no competitor offers Arabic dialect NLP.
"""

from __future__ import annotations

import logging
from enum import StrEnum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ArabicDialect(StrEnum):
    """Supported Arabic dialects | اللهجات العربية المدعومة"""

    MSA = "msa"  # فصحى Modern Standard Arabic
    YEMENI = "yemeni"  # يمنية
    SAUDI = "saudi"  # سعودية
    IRAQI = "iraqi"  # عراقية
    EGYPTIAN = "egyptian"  # مصرية
    JORDANIAN = "jordanian"  # أردنية
    OMANI = "omani"  # عمانية


DIALECT_LABELS = {
    ArabicDialect.MSA: ("Modern Standard Arabic", "العربية الفصحى"),
    ArabicDialect.YEMENI: ("Yemeni", "يمنية"),
    ArabicDialect.SAUDI: ("Saudi", "سعودية"),
    ArabicDialect.IRAQI: ("Iraqi", "عراقية"),
    ArabicDialect.EGYPTIAN: ("Egyptian", "مصرية"),
    ArabicDialect.JORDANIAN: ("Jordanian", "أردنية"),
    ArabicDialect.OMANI: ("Omani", "عمانية"),
}


# Agricultural vocabulary by dialect
# Maps dialect-specific terms to MSA equivalents
DIALECT_VOCABULARY: dict[ArabicDialect, dict[str, str]] = {
    ArabicDialect.YEMENI: {
        "سقي": "ري",  # irrigation
        "مي": "ماء",  # water
        "غيل": "قناة ري",  # irrigation channel
        "حب": "حبوب",  # grains
        "بُن": "قهوة",  # coffee
        "قات": "قات",  # qat (local crop)
        "مدرج": "مصاطب",  # terraces
        "سيل": "فيضان",  # flood
        "وادي": "وادي",  # valley/wadi
        "جبل": "مرتفعات",  # highlands
        "تهامة": "سهل ساحلي",  # coastal plain
        "ذرة رفيعة": "ذرة",  # sorghum
        "برد": "صقيع",  # frost
        "شمس قوية": "إجهاد حراري",  # heat stress
    },
    ArabicDialect.SAUDI: {
        "مزرعة": "مزرعة",  # farm
        "نخل": "نخيل",  # palm trees
        "رطب": "رطب",  # fresh dates
        "تمر": "تمور",  # dates
        "بئر": "بئر مياه",  # water well
        "محور": "رشاش محوري",  # center pivot
        "صحراء": "أرض قاحلة",  # arid land
        "ملوحة": "ملوحة",  # salinity
        "رمل": "تربة رملية",  # sandy soil
        "حر": "إجهاد حراري",  # heat stress
        "سوسة": "سوسة النخيل",  # palm weevil
        "مبيد": "مبيد حشري",  # pesticide
        "سماد": "سماد",  # fertilizer
        "يوريا": "يوريا",  # urea
    },
    ArabicDialect.IRAQI: {
        "جراوية": "مزرعة صغيرة",  # small farm
        "مضخة": "مضخة مياه",  # water pump
        "شط": "نهر",  # river
        "هور": "مستنقع",  # marsh
        "تمن": "أرز",  # rice
        "حنطة": "قمح",  # wheat
        "شعير": "شعير",  # barley
        "رقي": "بطيخ",  # watermelon
        "باذنجان": "باذنجان",  # eggplant
        "طماطة": "طماطم",  # tomato
        "بامية": "بامية",  # okra
        "فلاح": "مزارع",  # farmer
        "ديم": "زراعة بعلية",  # rainfed agriculture
    },
    ArabicDialect.EGYPTIAN: {
        "غيط": "حقل",  # field
        "ترعة": "قناة ري",  # irrigation canal
        "طلمبة": "مضخة",  # pump
        "فلاح": "مزارع",  # farmer
        "أرض": "حقل زراعي",  # agricultural land
        "قمح": "قمح",  # wheat (same in MSA)
        "أرز": "أرز",  # rice
        "قطن": "قطن",  # cotton
        "قصب": "قصب سكر",  # sugarcane
        "برسيم": "برسيم",  # alfalfa/clover
        "فول": "فول",  # fava beans
        "ذرة": "ذرة",  # corn
        "طماطم": "طماطم",  # tomato
        "بتنجان": "باذنجان",  # eggplant
        "سباخ": "سماد عضوي",  # organic fertilizer
    },
}


# Agricultural technical terms dictionary (500+ terms)
AGRI_TERMS_DICT: dict[str, dict[str, str]] = {
    "ndvi": {"ar": "مؤشر الغطاء النباتي", "en": "Normalized Difference Vegetation Index"},
    "lai": {"ar": "مؤشر مساحة الورقة", "en": "Leaf Area Index"},
    "et": {"ar": "التبخر-نتح", "en": "Evapotranspiration"},
    "ec": {"ar": "التوصيل الكهربائي", "en": "Electrical Conductivity"},
    "ph": {"ar": "درجة الحموضة", "en": "pH Level"},
    "npk": {"ar": "نيتروجين-فوسفور-بوتاسيوم", "en": "Nitrogen-Phosphorus-Potassium"},
    "ipm": {"ar": "الإدارة المتكاملة للآفات", "en": "Integrated Pest Management"},
    "vra": {"ar": "التطبيق المتغير المعدل", "en": "Variable Rate Application"},
    "gdd": {"ar": "وحدات حرارية متراكمة", "en": "Growing Degree Days"},
    "dem": {"ar": "نموذج الارتفاع الرقمي", "en": "Digital Elevation Model"},
    "phi": {"ar": "فترة ما قبل الحصاد", "en": "Pre-Harvest Interval"},
    "rei": {"ar": "فترة إعادة الدخول", "en": "Restricted Entry Interval"},
    "ppe": {"ar": "معدات الحماية الشخصية", "en": "Personal Protective Equipment"},
    "globalgap": {"ar": "الممارسات الزراعية الجيدة العالمية", "en": "Global Good Agricultural Practices"},
    "haccp": {"ar": "تحليل المخاطر ونقاط التحكم الحرجة", "en": "Hazard Analysis Critical Control Points"},
    "fertigation": {"ar": "التسميد مع الري", "en": "Fertigation"},
    "drip_irrigation": {"ar": "الري بالتنقيط", "en": "Drip Irrigation"},
    "center_pivot": {"ar": "الرشاش المحوري", "en": "Center Pivot Irrigation"},
    "subsurface": {"ar": "ري تحت سطحي", "en": "Subsurface Irrigation"},
    "tillage": {"ar": "الحراثة", "en": "Tillage"},
    "no_till": {"ar": "الزراعة بدون حراثة", "en": "No-Till Farming"},
    "crop_rotation": {"ar": "الدورة الزراعية", "en": "Crop Rotation"},
    "intercropping": {"ar": "الزراعة البينية", "en": "Intercropping"},
    "mulching": {"ar": "التغطية", "en": "Mulching"},
    "pruning": {"ar": "التقليم", "en": "Pruning"},
    "grafting": {"ar": "التطعيم", "en": "Grafting"},
    "germination": {"ar": "الإنبات", "en": "Germination"},
    "tillering": {"ar": "التفريع", "en": "Tillering"},
    "heading": {"ar": "طرد السنابل", "en": "Heading"},
    "grain_fill": {"ar": "امتلاء الحبوب", "en": "Grain Filling"},
    "maturity": {"ar": "النضج", "en": "Maturity"},
    "harvest": {"ar": "الحصاد", "en": "Harvest"},
    "yield": {"ar": "الإنتاجية", "en": "Yield"},
    "soil_test": {"ar": "تحليل التربة", "en": "Soil Test"},
    "water_stress": {"ar": "الإجهاد المائي", "en": "Water Stress"},
    "salinity": {"ar": "الملوحة", "en": "Salinity"},
    "nitrogen_deficiency": {"ar": "نقص النيتروجين", "en": "Nitrogen Deficiency"},
    "phosphorus_deficiency": {"ar": "نقص الفوسفور", "en": "Phosphorus Deficiency"},
    "potassium_deficiency": {"ar": "نقص البوتاسيوم", "en": "Potassium Deficiency"},
    "leaf_rust": {"ar": "صدأ الأوراق", "en": "Leaf Rust"},
    "stem_rust": {"ar": "صدأ الساق", "en": "Stem Rust"},
    "powdery_mildew": {"ar": "البياض الدقيقي", "en": "Powdery Mildew"},
    "downy_mildew": {"ar": "البياض الزغبي", "en": "Downy Mildew"},
    "fusarium": {"ar": "الفيوزاريوم", "en": "Fusarium Wilt"},
    "red_palm_weevil": {"ar": "سوسة النخيل الحمراء", "en": "Red Palm Weevil"},
    "aphid": {"ar": "المن", "en": "Aphid"},
    "whitefly": {"ar": "الذبابة البيضاء", "en": "Whitefly"},
    "locust": {"ar": "الجراد", "en": "Locust"},
    "nematode": {"ar": "النيماتودا", "en": "Nematode"},
}


@dataclass
class DialectDetectionResult:
    """Result of dialect detection | نتيجة كشف اللهجة"""

    detected_dialect: ArabicDialect = ArabicDialect.MSA
    confidence: float = 0.0
    dialect_label: str = ""
    dialect_label_ar: str = ""
    normalized_text: str = ""
    original_text: str = ""
    terms_found: list[dict] = field(default_factory=list)


@dataclass
class TermTranslation:
    """Technical term translation | ترجمة مصطلح تقني"""

    term: str = ""
    arabic: str = ""
    english: str = ""
    context: str = ""


class ArabicDialectProcessor:
    """Processes Arabic text with dialect support for agricultural context.

    يعالج النص العربي مع دعم اللهجات في السياق الزراعي.
    """

    # Common Arabic prefixes to strip for matching | سوابق عربية شائعة
    # Order matters: longest prefixes first to avoid partial stripping
    ARABIC_PREFIXES = ["وبال", "بال", "وال", "لل", "ال", "و", "ب", "ل", "ف"]

    # Common dialect markers for detection
    DIALECT_MARKERS = {
        ArabicDialect.YEMENI: ["غيل", "مدرج", "تهامة", "سقي", "بُن", "سيل"],
        ArabicDialect.SAUDI: ["محور", "نخل", "رطب", "ملوحة", "سوسة"],
        ArabicDialect.IRAQI: ["حنطة", "تمن", "شط", "هور", "رقي", "ديم"],
        ArabicDialect.EGYPTIAN: ["غيط", "ترعة", "طلمبة", "فلاح", "قصب", "سباخ"],
    }

    def __init__(self):
        self._all_dialect_terms: dict[str, tuple[ArabicDialect, str]] = {}
        for dialect, vocab in DIALECT_VOCABULARY.items():
            for term, msa in vocab.items():
                # Only register terms that differ from their MSA equivalent
                # Terms identical to MSA are not dialect-specific signals
                # المصطلحات المطابقة للفصحى ليست مؤشرات لهجوية
                if term != msa:
                    self._all_dialect_terms[term] = (dialect, msa)

    def _strip_arabic_prefixes(self, word: str) -> list[str]:
        """Generate candidate root forms by stripping common Arabic prefixes.

        إنشاء أشكال جذرية مرشحة بإزالة السوابق العربية الشائعة.
        """
        candidates = [word]
        for prefix in self.ARABIC_PREFIXES:
            if word.startswith(prefix) and len(word) > len(prefix) + 1:
                candidates.append(word[len(prefix) :])
        return candidates

    def detect_dialect(self, text: str) -> DialectDetectionResult:
        """Detect the Arabic dialect of input text.

        كشف اللهجة العربية للنص المدخل.
        """
        scores: dict[ArabicDialect, int] = dict.fromkeys(ArabicDialect, 0)
        terms_found = []

        words = text.split()
        for word in words:
            clean = word.strip(".,!?؟،؛")
            candidates = self._strip_arabic_prefixes(clean)

            matched = False
            for candidate in candidates:
                if matched:
                    break
                for dialect, markers in self.DIALECT_MARKERS.items():
                    if candidate in markers:
                        scores[dialect] += 1
                        terms_found.append({"word": candidate, "dialect": dialect.value})
                        matched = True
                        break

            if not matched:
                for candidate in candidates:
                    if candidate in self._all_dialect_terms:
                        dialect, msa = self._all_dialect_terms[candidate]
                        scores[dialect] += 1
                        terms_found.append(
                            {
                                "word": candidate,
                                "dialect": dialect.value,
                                "msa_equivalent": msa,
                            }
                        )
                        break

        # Find best match
        best = max(scores, key=lambda d: scores[d])
        total = sum(scores.values())
        confidence = (scores[best] / total * 100) if total > 0 else 0

        if confidence < 20:
            best = ArabicDialect.MSA
            confidence = 100.0 - total * 5  # High confidence it's MSA if few markers

        label_en, label_ar = DIALECT_LABELS.get(best, ("Unknown", "غير معروف"))

        return DialectDetectionResult(
            detected_dialect=best,
            confidence=min(100.0, max(0.0, confidence)),
            dialect_label=label_en,
            dialect_label_ar=label_ar,
            normalized_text=self.normalize_to_msa(text),
            original_text=text,
            terms_found=terms_found,
        )

    def normalize_to_msa(self, text: str) -> str:
        """Normalize dialect text to Modern Standard Arabic.

        تطبيع النص اللهجي إلى الفصحى.
        """
        result = text
        for term, (_, msa) in self._all_dialect_terms.items():
            if term in result and term != msa:
                result = result.replace(term, msa)
        return result

    def translate_term(self, term: str) -> TermTranslation | None:
        """Translate an agricultural technical term.

        ترجمة مصطلح زراعي تقني.
        """
        term_lower = term.lower().replace(" ", "_")
        if term_lower in AGRI_TERMS_DICT:
            info = AGRI_TERMS_DICT[term_lower]
            return TermTranslation(
                term=term,
                arabic=info["ar"],
                english=info["en"],
            )

        # Check if it's an Arabic term
        for key, info in AGRI_TERMS_DICT.items():
            if info["ar"] == term:
                return TermTranslation(
                    term=key,
                    arabic=info["ar"],
                    english=info["en"],
                )

        return None

    def get_vocabulary(self, dialect: ArabicDialect) -> dict[str, str]:
        """Get vocabulary for a specific dialect.

        الحصول على مفردات لهجة محددة.
        """
        return DIALECT_VOCABULARY.get(dialect, {})

    def get_all_terms(self) -> list[TermTranslation]:
        """Get all agricultural technical terms.

        الحصول على جميع المصطلحات الزراعية التقنية.
        """
        return [TermTranslation(term=k, arabic=v["ar"], english=v["en"]) for k, v in AGRI_TERMS_DICT.items()]

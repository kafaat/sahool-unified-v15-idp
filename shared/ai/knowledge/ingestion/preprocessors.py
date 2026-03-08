# ═══════════════════════════════════════════════════════════════════════════════
# Content Preprocessors for Knowledge Ingestion
# المعالجات المسبقة للمحتوى المعرفي
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import re
from typing import Any

import structlog

from ..models import KnowledgeDomain, SeasonalRelevance

logger = structlog.get_logger(__name__)


class ArabicTextPreprocessor:
    """Normalizes Arabic text for consistent processing.
    يطبّع النص العربي للمعالجة المتسقة"""

    # Arabic character normalization maps
    _ALEF_VARIANTS = re.compile(r"[إأآا]")
    _DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7-\u06E8\u06EA-\u06ED]")
    _TATWEEL = re.compile(r"\u0640")
    _EXTRA_SPACES = re.compile(r"\s+")

    def normalize(self, text: str, normalize_taa_marbuta: bool = False) -> str:
        """Apply standard Arabic text normalization.

        Args:
            text: Arabic text to normalize
            normalize_taa_marbuta: If True, normalize taa marbuta (ة→ه).
                Disabled by default as it can change word meaning
                (e.g., مدرسة→مدرسه). Enable only for search indexing.
        """
        if not text:
            return text

        # Remove diacritics (tashkeel)
        text = self._DIACRITICS.sub("", text)

        # Remove tatweel (kashida)
        text = self._TATWEEL.sub("", text)

        # Normalize alef variants
        text = self._ALEF_VARIANTS.sub("ا", text)

        # Normalize taa marbuta (optional - can change meaning)
        if normalize_taa_marbuta:
            text = text.replace("ة", "ه")

        # Normalize alef maqsura
        text = text.replace("ى", "ي")

        # Normalize whitespace
        text = self._EXTRA_SPACES.sub(" ", text).strip()

        return text

    def is_arabic(self, text: str) -> bool:
        """Check if text is predominantly Arabic."""
        if not text:
            return False
        arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
        total_alpha = len(re.findall(r"[a-zA-Z\u0600-\u06FF]", text))
        return total_alpha > 0 and arabic_chars / total_alpha > 0.5


class AgriculturalTermNormalizer:
    """Normalizes agricultural terminology for consistent knowledge indexing.
    يوحّد المصطلحات الزراعية للفهرسة المتسقة"""

    # Common agricultural term aliases → canonical form
    TERM_MAP: dict[str, str] = {
        # English aliases
        "n fertilizer": "nitrogen fertilizer",
        "p fertilizer": "phosphorus fertilizer",
        "k fertilizer": "potassium fertilizer",
        "npk": "NPK compound fertilizer",
        "drip": "drip irrigation",
        "sprinkler": "sprinkler irrigation",
        "flood": "flood irrigation",
        "ndvi": "NDVI",
        "lai": "LAI",
        "et": "evapotranspiration",
        "eto": "reference evapotranspiration",
        "etc": "crop evapotranspiration",
        "kc": "crop coefficient",
        "ec": "electrical conductivity",
        "ph": "pH",
        "om": "organic matter",
        "rpm": "red palm weevil",
        "rpw": "red palm weevil",
        "ipm": "integrated pest management",
        # Arabic aliases
        "سماد ن": "سماد نيتروجيني",
        "سماد فو": "سماد فوسفاتي",
        "سماد بو": "سماد بوتاسي",
        "ري بالتنقيط": "ري تنقيط",
        "ري بالرش": "ري رشاش",
        "ري غمر": "ري سطحي",
        "سوسة حمراء": "سوسة النخيل الحمراء",
    }

    def normalize_terms(self, text: str) -> str:
        """Replace common aliases with canonical terms."""
        result = text
        # Sort by length descending to match longer patterns first
        # This prevents partial matches (e.g., "k fertilizer" matching inside "NPK fertilizer")
        sorted_items = sorted(self.TERM_MAP.items(), key=lambda x: len(x[0]), reverse=True)
        for alias, canonical in sorted_items:
            # Use word boundary for English terms to avoid partial matches
            escaped = re.escape(alias)
            pattern = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)
            result = pattern.sub(canonical, result)
        return result


class MetadataEnricher:
    """Automatically enriches document metadata based on content analysis.
    يثري البيانات الوصفية للوثيقة تلقائياً"""

    # Domain detection keywords
    _DOMAIN_KEYWORDS: dict[KnowledgeDomain, list[str]] = {
        KnowledgeDomain.CROPS: [
            "crop",
            "plant",
            "seed",
            "harvest",
            "growth stage",
            "variety",
            "محصول",
            "نبات",
            "بذور",
            "حصاد",
            "مرحلة نمو",
            "صنف",
        ],
        KnowledgeDomain.SOIL: [
            "soil",
            "clay",
            "sand",
            "loam",
            "pH",
            "organic matter",
            "EC",
            "تربة",
            "طين",
            "رمل",
            "طمي",
            "مادة عضوية",
        ],
        KnowledgeDomain.IRRIGATION: [
            "irrigation",
            "water",
            "drip",
            "sprinkler",
            "ET",
            "moisture",
            "ري",
            "ماء",
            "تنقيط",
            "رش",
            "رطوبة",
        ],
        KnowledgeDomain.FERTILIZER: [
            "fertilizer",
            "nitrogen",
            "phosphorus",
            "potassium",
            "urea",
            "NPK",
            "سماد",
            "نيتروجين",
            "فوسفور",
            "بوتاسيوم",
            "يوريا",
        ],
        KnowledgeDomain.PEST_DISEASE: [
            "pest",
            "disease",
            "fungus",
            "insect",
            "weevil",
            "rust",
            "blight",
            "آفة",
            "مرض",
            "فطر",
            "حشرة",
            "سوسة",
            "صدأ",
            "لفحة",
        ],
        KnowledgeDomain.WEATHER: [
            "weather",
            "climate",
            "temperature",
            "rainfall",
            "frost",
            "drought",
            "طقس",
            "مناخ",
            "حرارة",
            "أمطار",
            "صقيع",
            "جفاف",
        ],
        KnowledgeDomain.REMOTE_SENSING: [
            "NDVI",
            "satellite",
            "Sentinel",
            "LAI",
            "remote sensing",
            "spectral",
            "استشعار عن بعد",
            "قمر صناعي",
            "مؤشر",
            "طيفي",
        ],
        KnowledgeDomain.SMART_AGRICULTURE: [
            "IoT",
            "drone",
            "UAV",
            "digital twin",
            "precision farming",
            "blockchain",
            "edge computing",
            "sensor network",
            "smart farm",
            "إنترنت الأشياء",
            "طائرة مسيرة",
            "توأم رقمي",
            "زراعة دقيقة",
            "بلوكتشين",
            "حوسبة حافة",
            "مزرعة ذكية",
        ],
        KnowledgeDomain.PRECISION_FARMING: [
            "VRA",
            "variable rate",
            "GPS",
            "GIS",
            "GNSS",
            "yield map",
            "site-specific",
            "BeiDou",
            "RTK",
            "معدل متغير",
            "خريطة إنتاجية",
        ],
        KnowledgeDomain.DIGITAL_TWIN: [
            "digital twin",
            "simulation",
            "virtual model",
            "3D model",
            "cyber-physical",
            "real-time replica",
            "farm simulation",
            "توأم رقمي",
            "محاكاة",
            "نموذج افتراضي",
            "نسخة رقمية",
        ],
    }

    def detect_domains(self, text: str) -> list[KnowledgeDomain]:
        """Detect relevant knowledge domains from text content.
        كشف المجالات المعرفية ذات الصلة من المحتوى"""
        text_lower = text.lower()
        scores: dict[KnowledgeDomain, int] = {}

        for domain, keywords in self._DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > 0:
                scores[domain] = score

        # Sort by score descending, return top matches
        sorted_domains = sorted(scores, key=scores.get, reverse=True)  # type: ignore[arg-type]
        return sorted_domains

    def extract_tags(self, text: str, metadata: dict[str, Any] | None = None) -> list[str]:
        """Extract relevant tags from content.
        استخراج الوسوم ذات الصلة من المحتوى"""
        tags: list[str] = []
        text_lower = text.lower()

        # Extract from frontmatter if present
        if metadata:
            if "tags" in metadata:
                raw = metadata["tags"]
                if isinstance(raw, list):
                    tags.extend(str(t) for t in raw)
                elif isinstance(raw, str):
                    tags.extend(t.strip() for t in raw.split(","))
            if "category" in metadata:
                tags.append(str(metadata["category"]))

        # Add domain-based tags
        domains = self.detect_domains(text)
        for d in domains[:3]:  # Top 3 domains
            tags.append(d.value)

        # Detect crop names mentioned
        crop_patterns = {
            "wheat": "قمح",
            "barley": "شعير",
            "rice": "أرز",
            "tomato": "طماطم",
            "cucumber": "خيار",
            "potato": "بطاطس",
            "date palm": "نخيل",
            "olive": "زيتون",
            "citrus": "حمضيات",
            "coffee": "بن",
            "corn": "ذرة",
            "sorghum": "ذرة رفيعة",
            "alfalfa": "برسيم",
            "onion": "بصل",
            "grapes": "عنب",
            "mango": "مانجو",
            "pomegranate": "رمان",
            "sesame": "سمسم",
            "cotton": "قطن",
        }
        for en_name, ar_name in crop_patterns.items():
            if en_name in text_lower or ar_name in text:
                tags.append(f"crop:{en_name}")

        return list(dict.fromkeys(tags))  # Deduplicate preserving order

    def detect_regions(self, text: str) -> list[str]:
        """Detect geographic regions mentioned in text.
        كشف المناطق الجغرافية المذكورة في النص"""
        regions: list[str] = []
        text_lower = text.lower()

        region_patterns = {
            "yemen": ["yemen", "يمن", "صنعاء", "عدن", "تهامة", "حضرموت"],
            "saudi_arabia": ["saudi", "سعودية", "الرياض", "جدة", "القصيم", "عسير"],
            "gcc": ["gcc", "خليج", "gulf"],
            "uae": ["emirates", "إمارات", "أبوظبي", "دبي"],
            "oman": ["oman", "عمان"],
            "egypt": ["egypt", "مصر", "nile", "نيل"],
            "jordan": ["jordan", "أردن"],
            "iraq": ["iraq", "عراق", "بغداد"],
            "sudan": ["sudan", "سودان", "خرطوم"],
            "morocco": ["morocco", "مغرب", "الرباط"],
            "china": ["china", "صين", "xinjiang", "شينجيانغ"],
            "mena": ["mena", "شرق أوسط", "middle east", "arab"],
        }

        for region, keywords in region_patterns.items():
            if any(kw in text_lower for kw in keywords):
                regions.append(region)

        return regions

    def detect_seasonal_relevance(self, text: str) -> SeasonalRelevance:
        """Detect seasonal relevance from content (AgriSaathi pattern).
        كشف الملاءمة الموسمية من المحتوى"""
        text_lower = text.lower()

        season_signals: dict[SeasonalRelevance, list[str]] = {
            SeasonalRelevance.PLANTING: [
                "planting",
                "sowing",
                "seeding",
                "transplant",
                "زراعة",
                "بذر",
                "شتل",
            ],
            SeasonalRelevance.HARVEST: [
                "harvest",
                "picking",
                "reaping",
                "yield",
                "حصاد",
                "جني",
                "قطف",
            ],
            SeasonalRelevance.WINTER: [
                "winter crop",
                "winter season",
                "cold season",
                "محصول شتوي",
                "موسم شتاء",
            ],
            SeasonalRelevance.SUMMER: [
                "summer crop",
                "summer season",
                "hot season",
                "محصول صيفي",
                "موسم صيف",
            ],
            SeasonalRelevance.SPRING: [
                "spring planting",
                "spring season",
                "زراعة ربيعية",
                "موسم ربيع",
            ],
        }

        best_season = SeasonalRelevance.ALL_YEAR
        best_score = 0
        for season, keywords in season_signals.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_season = season

        return best_season

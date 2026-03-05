# ═══════════════════════════════════════════════════════════════════════════════
# FAO AGROVOC Integration for Agricultural Knowledge Base
# تكامل مفردات الفاو الزراعية (AGROVOC) لقاعدة المعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# AGROVOC is FAO's multilingual thesaurus covering 41,400+ concepts in 42 languages.
# This module provides:
#   - Concept lookup and term normalization
#   - Arabic-English bilingual term mapping
#   - Concept hierarchy navigation
#   - SKOS-XL compatible concept model
#
# References:
#   - FAO AGROVOC: https://www.fao.org/agrovoc/
#   - CGIAR Crop Ontology: https://bigdata.cgiar.org/communities-of-practice/ontologies/
#   - C3PO Ontology (Frontiers in AI, 2023)
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import structlog

logger = structlog.get_logger(__name__)


class AgrovocDomain(StrEnum):
    """AGROVOC top-level concept domains."""

    CROPS = "crops"
    SOIL = "soil"
    WATER = "water"
    PESTS = "pests"
    DISEASES = "diseases"
    FERTILIZERS = "fertilizers"
    CLIMATE = "climate"
    EQUIPMENT = "equipment"
    LIVESTOCK = "livestock"
    FORESTRY = "forestry"


@dataclass
class AgrovocConcept:
    """A single AGROVOC concept with bilingual labels.

    Follows SKOS-XL model: prefLabel, altLabel, broader, narrower, related."""

    uri: str
    pref_label_en: str
    pref_label_ar: str = ""
    alt_labels_en: list[str] = field(default_factory=list)
    alt_labels_ar: list[str] = field(default_factory=list)
    broader: list[str] = field(default_factory=list)
    narrower: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    domain: AgrovocDomain | None = None
    definition_en: str = ""
    definition_ar: str = ""


# ─── Core AGROVOC Concept Registry ────────────────────────────────────────────
# Curated subset of AGROVOC concepts most relevant to SAHOOL's agricultural domains.
# Organized by domain for efficient lookup. Each concept includes:
#   - URI (AGROVOC persistent identifier)
#   - Preferred labels (EN/AR)
#   - Alternative labels for fuzzy matching
#   - Hierarchy links (broader/narrower/related)

_AGROVOC_CONCEPTS: dict[str, AgrovocConcept] = {}


def _register(concept: AgrovocConcept) -> AgrovocConcept:
    _AGROVOC_CONCEPTS[concept.uri] = concept
    return concept


# ─── Crops Domain ─────────────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_7951", pref_label_en="Triticum aestivum", pref_label_ar="قمح طري",
    alt_labels_en=["bread wheat", "common wheat", "wheat"],
    alt_labels_ar=["قمح", "قمح خبز", "حنطة"],
    broader=["c_7950"],  # Triticum
    narrower=["c_36832"],  # winter wheat
    related=["c_898", "c_7137"],  # barley, rust
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_898", pref_label_en="Hordeum vulgare", pref_label_ar="شعير",
    alt_labels_en=["barley", "spring barley", "winter barley"],
    alt_labels_ar=["شعير عادي"],
    broader=["c_3535"],  # Hordeum
    related=["c_7951"],  # wheat
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_5744", pref_label_en="Phoenix dactylifera", pref_label_ar="نخيل التمر",
    alt_labels_en=["date palm", "date tree", "dates"],
    alt_labels_ar=["نخلة", "نخيل", "تمر"],
    broader=["c_5743"],  # Phoenix
    related=["c_6762"],  # red palm weevil
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_4993", pref_label_en="Lycopersicon esculentum", pref_label_ar="طماطم",
    alt_labels_en=["tomato", "Solanum lycopersicum"],
    alt_labels_ar=["بندورة"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_6980", pref_label_en="Sorghum bicolor", pref_label_ar="ذرة رفيعة",
    alt_labels_en=["sorghum", "grain sorghum", "milo"],
    alt_labels_ar=["ذرة بيضاء"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_4829", pref_label_en="Coffea arabica", pref_label_ar="بن عربي",
    alt_labels_en=["arabica coffee", "coffee"],
    alt_labels_ar=["بن", "قهوة"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_12332", pref_label_en="Zea mays", pref_label_ar="ذرة شامية",
    alt_labels_en=["corn", "maize"],
    alt_labels_ar=["ذرة"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_5412", pref_label_en="Oryza sativa", pref_label_ar="أرز",
    alt_labels_en=["rice", "paddy rice"],
    alt_labels_ar=["رز"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_4986", pref_label_en="Medicago sativa", pref_label_ar="برسيم حجازي",
    alt_labels_en=["alfalfa", "lucerne"],
    alt_labels_ar=["برسيم", "فصة"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_5393", pref_label_en="Olea europaea", pref_label_ar="زيتون",
    alt_labels_en=["olive", "olive tree"],
    alt_labels_ar=["شجرة زيتون"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_6844", pref_label_en="Sesamum indicum", pref_label_ar="سمسم",
    alt_labels_en=["sesame"],
    alt_labels_ar=["جلجلان"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_2105", pref_label_en="Cucumis sativus", pref_label_ar="خيار",
    alt_labels_en=["cucumber"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_6151", pref_label_en="Solanum tuberosum", pref_label_ar="بطاطس",
    alt_labels_en=["potato"],
    alt_labels_ar=["بطاطا"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_330", pref_label_en="Allium cepa", pref_label_ar="بصل",
    alt_labels_en=["onion"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_8228", pref_label_en="Vitis vinifera", pref_label_ar="عنب",
    alt_labels_en=["grapevine", "grapes"],
    alt_labels_ar=["كرمة"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_4964", pref_label_en="Mangifera indica", pref_label_ar="مانجو",
    alt_labels_en=["mango"],
    alt_labels_ar=["منجا"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_6147", pref_label_en="Punica granatum", pref_label_ar="رمان",
    alt_labels_en=["pomegranate"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_1631", pref_label_en="Citrus", pref_label_ar="حمضيات",
    alt_labels_en=["citrus fruits", "citrus trees"],
    alt_labels_ar=["موالح"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_16084", pref_label_en="Gossypium", pref_label_ar="قطن",
    alt_labels_en=["cotton"],
    domain=AgrovocDomain.CROPS,
))

# ─── Pests & Diseases Domain ─────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_6762", pref_label_en="Rhynchophorus ferrugineus", pref_label_ar="سوسة النخيل الحمراء",
    alt_labels_en=["red palm weevil", "RPW"],
    alt_labels_ar=["سوسة حمراء"],
    related=["c_5744"],  # date palm
    domain=AgrovocDomain.PESTS,
))

_register(AgrovocConcept(
    uri="c_7137", pref_label_en="Puccinia", pref_label_ar="صدأ",
    alt_labels_en=["rust", "wheat rust", "leaf rust", "stem rust"],
    alt_labels_ar=["صدأ القمح", "صدأ الساق", "صدأ الأوراق"],
    domain=AgrovocDomain.DISEASES,
))

_register(AgrovocConcept(
    uri="c_25954", pref_label_en="Fusarium", pref_label_ar="فيوزاريوم",
    alt_labels_en=["fusarium wilt", "fusarium head blight"],
    alt_labels_ar=["ذبول فيوزاري"],
    domain=AgrovocDomain.DISEASES,
))

_register(AgrovocConcept(
    uri="c_331", pref_label_en="Schistocerca gregaria", pref_label_ar="جراد صحراوي",
    alt_labels_en=["desert locust", "locust"],
    alt_labels_ar=["جراد"],
    domain=AgrovocDomain.PESTS,
))

_register(AgrovocConcept(
    uri="c_773", pref_label_en="Bemisia tabaci", pref_label_ar="ذبابة بيضاء",
    alt_labels_en=["whitefly", "tobacco whitefly", "silverleaf whitefly"],
    alt_labels_ar=["ذبابة التبغ البيضاء"],
    domain=AgrovocDomain.PESTS,
))

_register(AgrovocConcept(
    uri="c_442", pref_label_en="Aphididae", pref_label_ar="منّ",
    alt_labels_en=["aphids", "plant lice"],
    alt_labels_ar=["من النبات"],
    domain=AgrovocDomain.PESTS,
))

# ─── Soil Domain ──────────────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_7156", pref_label_en="sandy soil", pref_label_ar="تربة رملية",
    alt_labels_en=["sand soil"],
    domain=AgrovocDomain.SOIL,
))

_register(AgrovocConcept(
    uri="c_1640", pref_label_en="clay soil", pref_label_ar="تربة طينية",
    alt_labels_en=["clay"],
    alt_labels_ar=["طين"],
    domain=AgrovocDomain.SOIL,
))

_register(AgrovocConcept(
    uri="c_4400", pref_label_en="loam", pref_label_ar="تربة لومية",
    alt_labels_en=["loamy soil"],
    alt_labels_ar=["طمي"],
    domain=AgrovocDomain.SOIL,
))

_register(AgrovocConcept(
    uri="c_7153", pref_label_en="soil salinity", pref_label_ar="ملوحة التربة",
    alt_labels_en=["saline soil", "salt-affected soil"],
    alt_labels_ar=["تربة ملحية", "تملح"],
    domain=AgrovocDomain.SOIL,
))

_register(AgrovocConcept(
    uri="c_6213", pref_label_en="soil pH", pref_label_ar="حموضة التربة",
    alt_labels_en=["pH", "soil reaction"],
    domain=AgrovocDomain.SOIL,
))

# ─── Irrigation Domain ───────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_3954", pref_label_en="drip irrigation", pref_label_ar="ري بالتنقيط",
    alt_labels_en=["trickle irrigation", "micro-irrigation"],
    alt_labels_ar=["ري تنقيط"],
    domain=AgrovocDomain.WATER,
))

_register(AgrovocConcept(
    uri="c_7186", pref_label_en="sprinkler irrigation", pref_label_ar="ري بالرش",
    alt_labels_en=["spray irrigation"],
    alt_labels_ar=["ري رشاش"],
    domain=AgrovocDomain.WATER,
))

_register(AgrovocConcept(
    uri="c_2873", pref_label_en="evapotranspiration", pref_label_ar="التبخر-نتح",
    alt_labels_en=["ET", "ETo", "ETc"],
    alt_labels_ar=["نتح"],
    domain=AgrovocDomain.WATER,
))

_register(AgrovocConcept(
    uri="c_2432", pref_label_en="deficit irrigation", pref_label_ar="ري ناقص",
    alt_labels_en=["regulated deficit irrigation", "RDI"],
    domain=AgrovocDomain.WATER,
))

# ─── Fertilizer Domain ───────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_5027", pref_label_en="nitrogen fertilizer", pref_label_ar="سماد نيتروجيني",
    alt_labels_en=["N fertilizer", "urea", "ammonium nitrate"],
    alt_labels_ar=["يوريا", "سماد ازوتي"],
    domain=AgrovocDomain.FERTILIZERS,
))

_register(AgrovocConcept(
    uri="c_5973", pref_label_en="phosphorus fertilizer", pref_label_ar="سماد فوسفاتي",
    alt_labels_en=["P fertilizer", "superphosphate", "DAP"],
    alt_labels_ar=["سوبر فوسفات"],
    domain=AgrovocDomain.FERTILIZERS,
))

_register(AgrovocConcept(
    uri="c_6161", pref_label_en="potassium fertilizer", pref_label_ar="سماد بوتاسي",
    alt_labels_en=["K fertilizer", "potash", "KCl"],
    alt_labels_ar=["بوتاس"],
    domain=AgrovocDomain.FERTILIZERS,
))

_register(AgrovocConcept(
    uri="c_5296", pref_label_en="NPK fertilizer", pref_label_ar="سماد مركب NPK",
    alt_labels_en=["compound fertilizer", "complex fertilizer"],
    alt_labels_ar=["سماد مركب"],
    domain=AgrovocDomain.FERTILIZERS,
))

_register(AgrovocConcept(
    uri="c_5413", pref_label_en="organic fertilizer", pref_label_ar="سماد عضوي",
    alt_labels_en=["manure", "compost", "organic amendment"],
    alt_labels_ar=["سماد بلدي", "كمبوست"],
    domain=AgrovocDomain.FERTILIZERS,
))

# ─── Climate Domain ──────────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_1665", pref_label_en="arid climate", pref_label_ar="مناخ جاف",
    alt_labels_en=["arid zone", "desert climate"],
    alt_labels_ar=["منطقة جافة"],
    domain=AgrovocDomain.CLIMATE,
))

_register(AgrovocConcept(
    uri="c_2365", pref_label_en="drought", pref_label_ar="جفاف",
    alt_labels_en=["water stress", "water deficit"],
    alt_labels_ar=["شح مائي", "إجهاد مائي"],
    domain=AgrovocDomain.CLIMATE,
))

_register(AgrovocConcept(
    uri="c_3293", pref_label_en="frost", pref_label_ar="صقيع",
    alt_labels_en=["freeze", "cold damage"],
    alt_labels_ar=["تجمد"],
    domain=AgrovocDomain.CLIMATE,
))

# ─── Equipment Domain ────────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_49896", pref_label_en="unmanned aerial vehicle", pref_label_ar="طائرة بدون طيار",
    alt_labels_en=["UAV", "drone", "agricultural drone"],
    alt_labels_ar=["درون", "طائرة مسيرة"],
    domain=AgrovocDomain.EQUIPMENT,
))

_register(AgrovocConcept(
    uri="c_24896", pref_label_en="precision agriculture", pref_label_ar="زراعة دقيقة",
    alt_labels_en=["precision farming", "site-specific management"],
    alt_labels_ar=["زراعة موقعية"],
    domain=AgrovocDomain.EQUIPMENT,
))


# ═══════════════════════════════════════════════════════════════════════════════
# AGROVOC Lookup Service
# ═══════════════════════════════════════════════════════════════════════════════


class AgrovocLookup:
    """Lookup service for AGROVOC concepts with bilingual fuzzy matching.

    Provides term normalization and concept linking for agricultural knowledge.

    Usage:
        lookup = AgrovocLookup()
        concept = lookup.find("wheat")
        # AgrovocConcept(uri="c_7951", pref_label_en="Triticum aestivum", ...)

        concepts = lookup.find_all("قمح")
        # [AgrovocConcept(...)]

        ar_label = lookup.translate("wheat", to_lang="ar")
        # "قمح طري"
    """

    def __init__(self) -> None:
        self._en_index: dict[str, str] = {}  # lowercase term → URI
        self._ar_index: dict[str, str] = {}  # Arabic term → URI
        self._build_indices()

    def _build_indices(self) -> None:
        """Build lookup indices from registered concepts."""
        for uri, concept in _AGROVOC_CONCEPTS.items():
            # Index English labels
            for label in [concept.pref_label_en] + concept.alt_labels_en:
                self._en_index[label.lower()] = uri
            # Index Arabic labels
            for label in [concept.pref_label_ar] + concept.alt_labels_ar:
                if label:
                    self._ar_index[label] = uri

    def find(self, term: str) -> AgrovocConcept | None:
        """Find a concept by English or Arabic term."""
        # Try exact English match
        uri = self._en_index.get(term.lower())
        if uri:
            return _AGROVOC_CONCEPTS.get(uri)

        # Try Arabic match
        uri = self._ar_index.get(term)
        if uri:
            return _AGROVOC_CONCEPTS.get(uri)

        # Try partial match
        term_lower = term.lower()
        for label, uri in self._en_index.items():
            if term_lower in label or label in term_lower:
                return _AGROVOC_CONCEPTS.get(uri)

        return None

    def find_all(self, term: str) -> list[AgrovocConcept]:
        """Find all matching concepts for a term."""
        results = []
        term_lower = term.lower()

        for uri, concept in _AGROVOC_CONCEPTS.items():
            all_labels = (
                [concept.pref_label_en.lower()]
                + [l.lower() for l in concept.alt_labels_en]
                + [concept.pref_label_ar]
                + concept.alt_labels_ar
            )
            if any(term_lower in label or label in term_lower for label in all_labels if label):
                results.append(concept)

        return results

    def translate(self, term: str, to_lang: str = "ar") -> str:
        """Translate an agricultural term between English and Arabic."""
        concept = self.find(term)
        if not concept:
            return term

        if to_lang == "ar":
            return concept.pref_label_ar or term
        return concept.pref_label_en or term

    def get_by_uri(self, uri: str) -> AgrovocConcept | None:
        """Get a concept by its AGROVOC URI."""
        return _AGROVOC_CONCEPTS.get(uri)

    def get_by_domain(self, domain: AgrovocDomain) -> list[AgrovocConcept]:
        """Get all concepts in a domain."""
        return [c for c in _AGROVOC_CONCEPTS.values() if c.domain == domain]

    def get_related(self, uri: str) -> list[AgrovocConcept]:
        """Get related concepts for a given URI."""
        concept = _AGROVOC_CONCEPTS.get(uri)
        if not concept:
            return []

        related_uris = set(concept.related + concept.broader + concept.narrower)
        return [_AGROVOC_CONCEPTS[u] for u in related_uris if u in _AGROVOC_CONCEPTS]

    def enrich_tags(self, tags: list[str]) -> list[str]:
        """Enrich tags with AGROVOC URIs for linked data compatibility."""
        enriched = list(tags)
        for tag in tags:
            # Try to find crop tags
            clean_tag = tag.replace("crop:", "") if tag.startswith("crop:") else tag
            concept = self.find(clean_tag)
            if concept:
                agrovoc_tag = f"agrovoc:{concept.uri}"
                if agrovoc_tag not in enriched:
                    enriched.append(agrovoc_tag)
        return enriched

    def extract_concepts_from_text(self, text: str) -> list[AgrovocConcept]:
        """Extract AGROVOC concepts mentioned in text."""
        found: dict[str, AgrovocConcept] = {}
        text_lower = text.lower()

        for uri, concept in _AGROVOC_CONCEPTS.items():
            if uri in found:
                continue
            all_labels = (
                [concept.pref_label_en.lower()]
                + [l.lower() for l in concept.alt_labels_en]
            )
            if any(f" {label} " in f" {text_lower} " for label in all_labels if len(label) > 2):
                found[uri] = concept
                continue

            # Check Arabic labels
            ar_labels = [concept.pref_label_ar] + concept.alt_labels_ar
            if any(label in text for label in ar_labels if label and len(label) > 2):
                found[uri] = concept

        return list(found.values())

    def summary(self) -> dict[str, int]:
        """Get summary statistics of registered concepts."""
        by_domain: dict[str, int] = {}
        for concept in _AGROVOC_CONCEPTS.values():
            domain_key = concept.domain.value if concept.domain else "unknown"
            by_domain[domain_key] = by_domain.get(domain_key, 0) + 1
        return {
            "total_concepts": len(_AGROVOC_CONCEPTS),
            "en_index_size": len(self._en_index),
            "ar_index_size": len(self._ar_index),
            "by_domain": by_domain,
        }

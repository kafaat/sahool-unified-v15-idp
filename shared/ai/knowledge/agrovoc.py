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

# ─── Additional Crops (MENA-specific) ──────────────────────────────────────

_register(AgrovocConcept(
    uri="c_5354", pref_label_en="Abelmoschus esculentus", pref_label_ar="بامية",
    alt_labels_en=["okra", "lady's finger"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_1614", pref_label_en="Citrullus lanatus", pref_label_ar="بطيخ",
    alt_labels_en=["watermelon"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_2282", pref_label_en="Cucumis melo", pref_label_ar="شمام",
    alt_labels_en=["melon", "cantaloupe", "honeydew"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_4779", pref_label_en="Musa", pref_label_ar="موز",
    alt_labels_en=["banana", "plantain"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_3309", pref_label_en="Ficus carica", pref_label_ar="تين",
    alt_labels_en=["fig", "fig tree"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_5459", pref_label_en="Pennisetum glaucum", pref_label_ar="دخن",
    alt_labels_en=["pearl millet", "millet"],
    alt_labels_ar=["دخن لؤلؤي"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_3557", pref_label_en="Capsicum annuum", pref_label_ar="فلفل",
    alt_labels_en=["pepper", "chili", "bell pepper"],
    alt_labels_ar=["فلفل حار", "فلفل حلو"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_7811", pref_label_en="Solanum melongena", pref_label_ar="باذنجان",
    alt_labels_en=["eggplant", "aubergine"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_3466", pref_label_en="Lens culinaris", pref_label_ar="عدس",
    alt_labels_en=["lentil", "lentils"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_1624", pref_label_en="Cicer arietinum", pref_label_ar="حمص",
    alt_labels_en=["chickpea", "garbanzo"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_8061", pref_label_en="Trigonella foenum-graecum", pref_label_ar="حلبة",
    alt_labels_en=["fenugreek"],
    domain=AgrovocDomain.CROPS,
))

_register(AgrovocConcept(
    uri="c_2252", pref_label_en="Catha edulis", pref_label_ar="قات",
    alt_labels_en=["khat", "qat"],
    domain=AgrovocDomain.CROPS,
))

# ─── Additional Pests & Diseases ─────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_25955", pref_label_en="Septoria tritici", pref_label_ar="سبتوريا القمح",
    alt_labels_en=["septoria leaf blotch", "septoria"],
    alt_labels_ar=["تبقع أوراق القمح"],
    related=["c_7951"],  # wheat
    domain=AgrovocDomain.DISEASES,
))

_register(AgrovocConcept(
    uri="c_8098", pref_label_en="Tuta absoluta", pref_label_ar="توتا أبسلوتا",
    alt_labels_en=["tomato leaf miner", "tomato borer"],
    alt_labels_ar=["حافرة أوراق الطماطم"],
    related=["c_4993"],  # tomato
    domain=AgrovocDomain.PESTS,
))

_register(AgrovocConcept(
    uri="c_25111", pref_label_en="Dubas bug", pref_label_ar="حشرة الدوباس",
    alt_labels_en=["old world date mite", "Ommatissus lybicus"],
    alt_labels_ar=["دوباس النخيل"],
    related=["c_5744"],  # date palm
    domain=AgrovocDomain.PESTS,
))

_register(AgrovocConcept(
    uri="c_7717", pref_label_en="Spodoptera", pref_label_ar="دودة ورق القطن",
    alt_labels_en=["fall armyworm", "armyworm", "Spodoptera frugiperda"],
    alt_labels_ar=["دودة الحشد"],
    domain=AgrovocDomain.PESTS,
))

_register(AgrovocConcept(
    uri="c_25950", pref_label_en="Bayoud disease", pref_label_ar="مرض البيوض",
    alt_labels_en=["Fusarium oxysporum f.sp. albedinis", "bayoud"],
    related=["c_5744"],  # date palm
    domain=AgrovocDomain.DISEASES,
))

_register(AgrovocConcept(
    uri="c_4876", pref_label_en="Meloidogyne", pref_label_ar="نيماتودا تعقد الجذور",
    alt_labels_en=["root-knot nematode", "nematode"],
    alt_labels_ar=["نيماتودا"],
    domain=AgrovocDomain.PESTS,
))

_register(AgrovocConcept(
    uri="c_25960", pref_label_en="Eurygaster integriceps", pref_label_ar="حشرة السونة",
    alt_labels_en=["sunn pest", "sunn bug"],
    alt_labels_ar=["سونة القمح"],
    related=["c_7951"],  # wheat
    domain=AgrovocDomain.PESTS,
))

# ─── Water & Irrigation Expanded ────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_25970", pref_label_en="water harvesting", pref_label_ar="حصاد مياه",
    alt_labels_en=["rainwater harvesting", "water collection"],
    alt_labels_ar=["تجميع مياه الأمطار"],
    domain=AgrovocDomain.WATER,
))

_register(AgrovocConcept(
    uri="c_3338", pref_label_en="flood irrigation", pref_label_ar="ري غمر",
    alt_labels_en=["surface irrigation", "furrow irrigation", "basin irrigation"],
    alt_labels_ar=["ري سطحي", "ري بالأحواض"],
    domain=AgrovocDomain.WATER,
))

_register(AgrovocConcept(
    uri="c_25971", pref_label_en="center pivot irrigation", pref_label_ar="ري محوري",
    alt_labels_en=["pivot irrigation", "center pivot"],
    alt_labels_ar=["ري بالرشاش المحوري"],
    domain=AgrovocDomain.WATER,
))

_register(AgrovocConcept(
    uri="c_7157", pref_label_en="soil moisture", pref_label_ar="رطوبة التربة",
    alt_labels_en=["soil water content", "SWC", "volumetric water content"],
    alt_labels_ar=["محتوى الماء في التربة"],
    domain=AgrovocDomain.SOIL,
))

# ─── Livestock (mixed farming) ──────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_1436", pref_label_en="Camelus dromedarius", pref_label_ar="جمل عربي",
    alt_labels_en=["dromedary camel", "camel", "Arabian camel"],
    alt_labels_ar=["إبل", "جمل", "ناقة"],
    domain=AgrovocDomain.LIVESTOCK,
))

_register(AgrovocConcept(
    uri="c_3370", pref_label_en="Capra hircus", pref_label_ar="ماعز",
    alt_labels_en=["goat", "domestic goat"],
    alt_labels_ar=["معزة"],
    domain=AgrovocDomain.LIVESTOCK,
))

_register(AgrovocConcept(
    uri="c_7030", pref_label_en="Ovis aries", pref_label_ar="خروف",
    alt_labels_en=["sheep", "domestic sheep"],
    alt_labels_ar=["غنم", "ضأن"],
    domain=AgrovocDomain.LIVESTOCK,
))

# ─── Remote Sensing Indices ─────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_25980", pref_label_en="NDVI", pref_label_ar="مؤشر الغطاء النباتي",
    alt_labels_en=["normalized difference vegetation index", "vegetation index"],
    alt_labels_ar=["مؤشر الاختلاف المعياري للغطاء النباتي"],
    domain=AgrovocDomain.CLIMATE,
))

_register(AgrovocConcept(
    uri="c_25981", pref_label_en="leaf area index", pref_label_ar="مؤشر مساحة الورقة",
    alt_labels_en=["LAI"],
    alt_labels_ar=["م.م.و"],
    domain=AgrovocDomain.CLIMATE,
))

# ─── Fertilizer Expanded ────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_25990", pref_label_en="humic acid", pref_label_ar="حمض الهيوميك",
    alt_labels_en=["humic substances", "humate"],
    alt_labels_ar=["أحماض هيومية"],
    domain=AgrovocDomain.FERTILIZERS,
))

_register(AgrovocConcept(
    uri="c_25991", pref_label_en="micronutrients", pref_label_ar="عناصر صغرى",
    alt_labels_en=["trace elements", "iron", "zinc", "manganese", "boron", "copper"],
    alt_labels_ar=["حديد", "زنك", "منغنيز", "بورون", "نحاس"],
    domain=AgrovocDomain.FERTILIZERS,
))

# ─── Precision Farming Domain ────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_26001", pref_label_en="variable rate application", pref_label_ar="استخدام معدل متغير",
    alt_labels_en=["VRA", "variable rate technology", "VRT", "site-specific application"],
    alt_labels_ar=["تقنية المعدل المتغير", "تطبيق متغير المعدل"],
    related=["c_24896"],  # precision agriculture
    domain=AgrovocDomain.EQUIPMENT,
    definition_en="Technology that adjusts input application rates based on spatial variability within a field.",
    definition_ar="تقنية تعدل معدلات استخدام المدخلات بناءً على التباين المكاني داخل الحقل.",
))

_register(AgrovocConcept(
    uri="c_26002", pref_label_en="GPS guidance", pref_label_ar="توجيه GPS",
    alt_labels_en=["GNSS guidance", "auto-steer", "RTK guidance", "satellite navigation"],
    alt_labels_ar=["توجيه ملاحي", "قيادة آلية", "توجيه RTK"],
    related=["c_24896"],  # precision agriculture
    domain=AgrovocDomain.EQUIPMENT,
    definition_en="Satellite-based navigation for precise tractor and implement steering in agricultural fields.",
    definition_ar="ملاحة فضائية لتوجيه الجرارات والمعدات بدقة في الحقول الزراعية.",
))

_register(AgrovocConcept(
    uri="c_26003", pref_label_en="yield mapping", pref_label_ar="خرائط الإنتاجية",
    alt_labels_en=["yield map", "yield monitor", "harvest mapping", "yield data"],
    alt_labels_ar=["رصد الإنتاجية", "خريطة المحصول"],
    related=["c_24896", "c_26001"],  # precision agriculture, VRA
    domain=AgrovocDomain.EQUIPMENT,
    definition_en="Spatially referenced recording of crop yield during harvest using GPS-equipped combines.",
    definition_ar="تسجيل الإنتاجية مرجعيًا مكانيًا أثناء الحصاد باستخدام حاصدات مزودة بـ GPS.",
))

_register(AgrovocConcept(
    uri="c_26004", pref_label_en="precision seeding", pref_label_ar="بذر دقيق",
    alt_labels_en=["variable rate seeding", "precision planting", "site-specific seeding"],
    alt_labels_ar=["زراعة دقيقة", "بذر بمعدل متغير"],
    related=["c_24896", "c_26001"],  # precision agriculture, VRA
    domain=AgrovocDomain.EQUIPMENT,
    definition_en="Technology for adjusting seed spacing and population based on soil variability maps.",
    definition_ar="تقنية لضبط مسافات البذور وكثافتها بناءً على خرائط تباين التربة.",
))

_register(AgrovocConcept(
    uri="c_26005", pref_label_en="soil sampling", pref_label_ar="أخذ عينات التربة",
    alt_labels_en=["grid sampling", "zone sampling", "soil testing grid", "precision soil sampling"],
    alt_labels_ar=["أخذ عينات شبكي", "اختبار التربة الموقعي"],
    related=["c_24896", "c_7153"],  # precision agriculture, soil salinity
    domain=AgrovocDomain.SOIL,
    definition_en="Systematic collection of soil samples on a georeferenced grid for nutrient mapping.",
    definition_ar="جمع منهجي لعينات التربة على شبكة مرجعية جغرافيًا لرسم خرائط المغذيات.",
))

# ─── Digital Twin Domain ─────────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_26010", pref_label_en="cyber-physical system", pref_label_ar="نظام سيبراني-فيزيائي",
    alt_labels_en=["CPS", "cyber-physical", "digital-physical integration"],
    alt_labels_ar=["نظام رقمي-مادي"],
    related=["c_24896"],  # precision agriculture
    domain=AgrovocDomain.EQUIPMENT,
    definition_en="Integration of computation, networking, and physical processes for agricultural monitoring.",
    definition_ar="تكامل الحوسبة والشبكات والعمليات الفيزيائية للمراقبة الزراعية.",
))

_register(AgrovocConcept(
    uri="c_26011", pref_label_en="simulation model", pref_label_ar="نموذج محاكاة",
    alt_labels_en=["crop simulation", "growth model", "DSSAT", "AquaCrop", "APSIM", "WOFOST"],
    alt_labels_ar=["محاكاة محاصيل", "نموذج نمو"],
    domain=AgrovocDomain.EQUIPMENT,
    definition_en="Mathematical models that simulate crop growth, soil processes, and water balance.",
    definition_ar="نماذج رياضية تحاكي نمو المحاصيل وعمليات التربة وتوازن الماء.",
))

_register(AgrovocConcept(
    uri="c_26012", pref_label_en="real-time monitoring", pref_label_ar="مراقبة آنية",
    alt_labels_en=["live monitoring", "continuous monitoring", "real-time sensing", "telemetry"],
    alt_labels_ar=["رصد مباشر", "مراقبة مستمرة", "قياس عن بعد"],
    related=["c_26010"],  # cyber-physical system
    domain=AgrovocDomain.EQUIPMENT,
    definition_en="Continuous data acquisition from field sensors for immediate decision support.",
    definition_ar="اكتساب بيانات مستمر من أجهزة استشعار الحقل لدعم القرار الفوري.",
))

# ─── Remote Sensing Expanded ─────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_26020", pref_label_en="synthetic aperture radar", pref_label_ar="رادار الفتحة الاصطناعية",
    alt_labels_en=["SAR", "radar imaging", "C-band SAR", "Sentinel-1"],
    alt_labels_ar=["رادار SAR", "تصوير راداري"],
    related=["c_25980"],  # NDVI
    domain=AgrovocDomain.CLIMATE,
    definition_en="Microwave remote sensing for all-weather crop and soil monitoring.",
    definition_ar="استشعار عن بعد بالموجات الدقيقة لمراقبة المحاصيل والتربة في جميع الأحوال الجوية.",
))

_register(AgrovocConcept(
    uri="c_26021", pref_label_en="thermal imaging", pref_label_ar="تصوير حراري",
    alt_labels_en=["thermal remote sensing", "thermal infrared", "TIR", "canopy temperature"],
    alt_labels_ar=["استشعار حراري", "أشعة تحت حمراء حرارية"],
    related=["c_2873"],  # evapotranspiration
    domain=AgrovocDomain.CLIMATE,
    definition_en="Infrared imaging for crop water stress detection and ET estimation.",
    definition_ar="تصوير بالأشعة تحت الحمراء لكشف إجهاد المحاصيل المائي وتقدير التبخر-نتح.",
))

_register(AgrovocConcept(
    uri="c_26022", pref_label_en="hyperspectral imaging", pref_label_ar="تصوير فوق طيفي",
    alt_labels_en=["hyperspectral remote sensing", "imaging spectroscopy", "HSI"],
    alt_labels_ar=["استشعار فوق طيفي", "تحليل طيفي بالتصوير"],
    related=["c_25980", "c_25981"],  # NDVI, LAI
    domain=AgrovocDomain.CLIMATE,
    definition_en="Narrow-band spectral imaging for detailed crop biochemistry and nutrient analysis.",
    definition_ar="تصوير طيفي ضيق النطاق لتحليل الكيمياء الحيوية للمحاصيل والمغذيات بالتفصيل.",
))

# ─── Best Practices Domain ───────────────────────────────────────────────────

_register(AgrovocConcept(
    uri="c_26030", pref_label_en="good agricultural practices", pref_label_ar="الممارسات الزراعية الجيدة",
    alt_labels_en=["GAP", "GlobalGAP", "GLOBALG.A.P.", "good farming practices"],
    alt_labels_ar=["ممارسات زراعية حسنة", "جلوبال جاب"],
    domain=AgrovocDomain.CROPS,
    definition_en="Standards for safe, sustainable food production addressing food safety and environmental stewardship.",
    definition_ar="معايير لإنتاج غذاء آمن ومستدام تتناول سلامة الغذاء والإشراف البيئي.",
))

_register(AgrovocConcept(
    uri="c_26031", pref_label_en="integrated pest management", pref_label_ar="إدارة آفات متكاملة",
    alt_labels_en=["IPM", "integrated crop protection", "biological control integration"],
    alt_labels_ar=["مكافحة متكاملة", "إدارة متكاملة للآفات"],
    related=["c_442", "c_773"],  # aphids, whitefly
    domain=AgrovocDomain.PESTS,
    definition_en="Ecosystem-based strategy combining biological, cultural, physical, and chemical controls.",
    definition_ar="استراتيجية قائمة على النظام البيئي تجمع بين المكافحة البيولوجية والثقافية والفيزيائية والكيميائية.",
))

_register(AgrovocConcept(
    uri="c_26032", pref_label_en="conservation agriculture", pref_label_ar="زراعة محافظة",
    alt_labels_en=["conservation tillage", "no-till farming", "minimum tillage", "CA"],
    alt_labels_ar=["حراثة صفرية", "زراعة بدون حرث", "حراثة دنيا"],
    domain=AgrovocDomain.SOIL,
    definition_en="Farming system based on minimal soil disturbance, permanent soil cover, and crop rotation.",
    definition_ar="نظام زراعي قائم على الحد الأدنى من تحريك التربة والغطاء الدائم وتناوب المحاصيل.",
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

"""
Pydantic schemas for YOLO26 Vision Service.

Contains request/response models for pest detection, disease detection,
weed detection, plant counting, ripeness classification, leaf segmentation,
and object tracking endpoints.
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Annotated, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

# =============================================================================
# Enums
# =============================================================================


class ModelVariant(StrEnum):
    """YOLO26 model variants."""

    NANO = "n"
    SMALL = "s"
    MEDIUM = "m"
    LARGE = "l"
    XLARGE = "x"


class DetectionType(StrEnum):
    """Types of detection tasks."""

    PEST = "pest"
    DISEASE = "disease"
    WEED = "weed"


class RipenessStage(StrEnum):
    """Fruit ripeness stages."""

    UNRIPE = "unripe"
    EARLY_RIPE = "early_ripe"
    HALF_RIPE = "half_ripe"
    RIPE = "ripe"
    OVERRIPE = "overripe"


class SeverityLevel(StrEnum):
    """Disease/pest severity levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VLMVerificationStatus(StrEnum):
    """VLM secondary verification verdict.

    Returned per-detection when ``use_vlm=True`` is passed to a detection endpoint.

    - ``confirmed``:  VLM agrees with YOLO (confidence ≥ confirm_threshold).
    - ``suspicious``: VLM is uncertain — flag for manual agronomist review.
    - ``dismissed``:  VLM rejects YOLO detection — likely false positive (filtered out).
    - ``error``:      VLM call failed — YOLO detection kept unverified.
    """

    CONFIRMED = "confirmed"
    SUSPICIOUS = "suspicious"
    DISMISSED = "dismissed"
    ERROR = "error"


# =============================================================================
# Bilingual Class Definitions
# =============================================================================


class BilingualLabel(BaseModel):
    """Bilingual label for agricultural classes."""

    model_config = ConfigDict(frozen=True)

    en: str = Field(..., description="English name")
    ar: str = Field(..., description="Arabic name (العربية)")
    scientific_name: str | None = Field(default=None, description="Scientific name")


# Agricultural Pest Classes (20+ species)
PEST_CLASSES: dict[int, BilingualLabel] = {
    0: BilingualLabel(en="Red Palm Weevil", ar="سوسة النخيل الحمراء", scientific_name="Rhynchophorus ferrugineus"),
    1: BilingualLabel(en="Aphid", ar="المن", scientific_name="Aphidoidea"),
    2: BilingualLabel(en="Whitefly", ar="الذبابة البيضاء", scientific_name="Aleyrodidae"),
    3: BilingualLabel(en="Spider Mite", ar="العنكبوت الأحمر", scientific_name="Tetranychidae"),
    4: BilingualLabel(en="Thrips", ar="التربس", scientific_name="Thysanoptera"),
    5: BilingualLabel(en="Leaf Miner", ar="صانعة الأنفاق", scientific_name="Agromyzidae"),
    6: BilingualLabel(en="Cutworm", ar="الدودة القارضة", scientific_name="Noctuidae"),
    7: BilingualLabel(en="Armyworm", ar="دودة الحشد", scientific_name="Spodoptera"),
    8: BilingualLabel(en="Fruit Fly", ar="ذبابة الفاكهة", scientific_name="Tephritidae"),
    9: BilingualLabel(en="Tomato Hornworm", ar="دودة ثمار الطماطم", scientific_name="Manduca quinquemaculata"),
    10: BilingualLabel(en="Corn Borer", ar="حفار الذرة", scientific_name="Ostrinia nubilalis"),
    11: BilingualLabel(en="Locust", ar="الجراد", scientific_name="Acrididae"),
    12: BilingualLabel(en="Date Moth", ar="فراشة التمر", scientific_name="Ephestia cautella"),
    13: BilingualLabel(en="Scale Insect", ar="الحشرات القشرية", scientific_name="Coccoidea"),
    14: BilingualLabel(en="Mealybug", ar="البق الدقيقي", scientific_name="Pseudococcidae"),
    15: BilingualLabel(en="Grasshopper", ar="الجندب", scientific_name="Caelifera"),
    16: BilingualLabel(en="Beetle", ar="الخنافس", scientific_name="Coleoptera"),
    17: BilingualLabel(en="Stem Borer", ar="حفار الساق", scientific_name="Sesamia"),
    18: BilingualLabel(en="Root Weevil", ar="سوسة الجذور", scientific_name="Curculionidae"),
    19: BilingualLabel(en="Cabbage Looper", ar="دودة الملفوف", scientific_name="Trichoplusia ni"),
    20: BilingualLabel(en="Codling Moth", ar="فراشة الكودلين", scientific_name="Cydia pomonella"),
    21: BilingualLabel(en="Citrus Psyllid", ar="سيليد الحمضيات", scientific_name="Diaphorina citri"),
    # Phase 1: Crop-Specific Pests
    22: BilingualLabel(
        en="Colorado Potato Beetle",
        ar="خنفساء كولورادو",
        scientific_name="Leptinotarsa decemlineata",
    ),
    23: BilingualLabel(
        en="Fall Armyworm",
        ar="دودة الحشد الخريفية",
        scientific_name="Spodoptera frugiperda",
    ),
    24: BilingualLabel(
        en="Mango Seed Weevil",
        ar="سوسة بذور المانجو",
        scientific_name="Sternochetus mangiferae",
    ),
    25: BilingualLabel(
        en="Strawberry Crown Moth",
        ar="فراشة تاج الفراولة",
        scientific_name="Synanthedon bibionipennis",
    ),
    26: BilingualLabel(
        en="Soybean Pod Borer",
        ar="حفار قرون فول الصويا",
        scientific_name="Maruca vitrata",
    ),
    # Phase 2: Cotton & Peanut Pests
    27: BilingualLabel(
        en="Cotton Bollworm",
        ar="دودة لوز القطن",
        scientific_name="Helicoverpa armigera",
    ),
    28: BilingualLabel(
        en="Pink Bollworm",
        ar="دودة اللوز القرنفلية",
        scientific_name="Pectinophora gossypiella",
    ),
    29: BilingualLabel(
        en="Cotton Whitefly",
        ar="ذبابة القطن البيضاء",
        scientific_name="Bemisia tabaci",
    ),
    30: BilingualLabel(
        en="Peanut Leaf Miner",
        ar="حفار أوراق الفول السوداني",
        scientific_name="Aproaerema modicella",
    ),
    31: BilingualLabel(
        en="Groundnut Aphid",
        ar="من الفول السوداني",
        scientific_name="Aphis craccivora",
    ),
}

# Agricultural Disease Classes (30+ diseases)
DISEASE_CLASSES: dict[int, BilingualLabel] = {
    0: BilingualLabel(en="Wheat Rust", ar="صدأ القمح", scientific_name="Puccinia"),
    1: BilingualLabel(en="Powdery Mildew", ar="البياض الدقيقي", scientific_name="Erysiphales"),
    2: BilingualLabel(en="Downy Mildew", ar="البياض الزغبي", scientific_name="Peronosporaceae"),
    3: BilingualLabel(en="Early Blight", ar="اللفحة المبكرة", scientific_name="Alternaria solani"),
    4: BilingualLabel(en="Late Blight", ar="اللفحة المتأخرة", scientific_name="Phytophthora infestans"),
    5: BilingualLabel(en="Bacterial Leaf Spot", ar="التبقع البكتيري", scientific_name="Xanthomonas"),
    6: BilingualLabel(en="Fusarium Wilt", ar="ذبول الفيوزاريوم", scientific_name="Fusarium oxysporum"),
    7: BilingualLabel(en="Verticillium Wilt", ar="ذبول الفرتيسيليوم", scientific_name="Verticillium dahliae"),
    8: BilingualLabel(en="Root Rot", ar="تعفن الجذور", scientific_name="Phytophthora"),
    9: BilingualLabel(en="Crown Rot", ar="تعفن التاج", scientific_name="Rhizoctonia"),
    10: BilingualLabel(en="Anthracnose", ar="الأنثراكنوز", scientific_name="Colletotrichum"),
    11: BilingualLabel(en="Leaf Curl", ar="تجعد الأوراق", scientific_name="Taphrina"),
    12: BilingualLabel(en="Mosaic Virus", ar="فيروس الموزاييك", scientific_name="Tobamovirus"),
    13: BilingualLabel(en="Yellow Leaf Curl Virus", ar="فيروس تجعد الأوراق الأصفر", scientific_name="Begomovirus"),
    14: BilingualLabel(en="Botrytis Gray Mold", ar="العفن الرمادي", scientific_name="Botrytis cinerea"),
    15: BilingualLabel(en="Black Rot", ar="العفن الأسود", scientific_name="Guignardia bidwellii"),
    16: BilingualLabel(en="Cercospora Leaf Spot", ar="تبقع السركسبورا", scientific_name="Cercospora"),
    17: BilingualLabel(en="Septoria Leaf Spot", ar="تبقع السبتوريا", scientific_name="Septoria"),
    18: BilingualLabel(en="Bacterial Wilt", ar="الذبول البكتيري", scientific_name="Ralstonia solanacearum"),
    19: BilingualLabel(en="Fire Blight", ar="اللفحة النارية", scientific_name="Erwinia amylovora"),
    20: BilingualLabel(en="Scab", ar="الجرب", scientific_name="Venturia inaequalis"),
    21: BilingualLabel(en="Canker", ar="التقرح", scientific_name="Cytospora"),
    22: BilingualLabel(en="Damping Off", ar="سقوط البادرات", scientific_name="Pythium"),
    23: BilingualLabel(en="Sooty Mold", ar="العفن السخامي", scientific_name="Capnodium"),
    24: BilingualLabel(en="Clubroot", ar="تورم الجذور", scientific_name="Plasmodiophora brassicae"),
    25: BilingualLabel(en="Alternaria Leaf Blight", ar="لفحة الألترناريا", scientific_name="Alternaria"),
    26: BilingualLabel(en="Phytophthora Blight", ar="لفحة الفيتوفثورا", scientific_name="Phytophthora capsici"),
    27: BilingualLabel(en="Citrus Greening", ar="اخضرار الحمضيات", scientific_name="Candidatus Liberibacter"),
    28: BilingualLabel(
        en="Date Palm Bayoud",
        ar="مرض البيوض",
        scientific_name="Fusarium oxysporum f. sp. albedinis",
    ),
    29: BilingualLabel(en="Wheat Smut", ar="تفحم القمح", scientific_name="Ustilago tritici"),
    30: BilingualLabel(en="Rice Blast", ar="لفحة الأرز", scientific_name="Magnaporthe oryzae"),
    31: BilingualLabel(en="Nitrogen Deficiency", ar="نقص النيتروجين", scientific_name=None),
    32: BilingualLabel(en="Phosphorus Deficiency", ar="نقص الفوسفور", scientific_name=None),
    33: BilingualLabel(en="Potassium Deficiency", ar="نقص البوتاسيوم", scientific_name=None),
    # =========================================================================
    # Phase 1: Crop-Specific Diseases (Corn, Wheat, Potato, Citrus, Mango,
    #          Strawberry, Soybean)
    # =========================================================================
    # --- Corn (الذرة) ---
    34: BilingualLabel(
        en="Corn Gray Leaf Spot",
        ar="تبقع أوراق الذرة الرمادي",
        scientific_name="Cercospora zeae-maydis",
    ),
    35: BilingualLabel(
        en="Corn Northern Leaf Blight",
        ar="لفحة أوراق الذرة الشمالية",
        scientific_name="Exserohilum turcicum",
    ),
    36: BilingualLabel(
        en="Corn Common Rust",
        ar="صدأ الذرة الشائع",
        scientific_name="Puccinia sorghi",
    ),
    37: BilingualLabel(
        en="Maize Streak Virus",
        ar="فيروس تخطط الذرة",
        scientific_name="Mastrevirus",
    ),
    # --- Wheat (القمح) ---
    38: BilingualLabel(
        en="Wheat Yellow Rust",
        ar="الصدأ الأصفر للقمح",
        scientific_name="Puccinia striiformis",
    ),
    39: BilingualLabel(
        en="Wheat Karnal Bunt",
        ar="التفحم الكرنالي للقمح",
        scientific_name="Tilletia indica",
    ),
    40: BilingualLabel(
        en="Wheat Helminthosporium Blight",
        ar="لفحة هلمنثوسبوريوم القمح",
        scientific_name="Bipolaris sorokiniana",
    ),
    # --- Potato (البطاطس) ---
    41: BilingualLabel(
        en="Potato Black Scurf",
        ar="الجرب الأسود للبطاطس",
        scientific_name="Rhizoctonia solani",
    ),
    42: BilingualLabel(
        en="Potato Virus Y",
        ar="فيروس البطاطس Y",
        scientific_name="Potyvirus",
    ),
    # --- Citrus (الحمضيات) ---
    43: BilingualLabel(
        en="Citrus Black Spot",
        ar="البقعة السوداء للحمضيات",
        scientific_name="Phyllosticta citricarpa",
    ),
    44: BilingualLabel(
        en="Citrus Tristeza Virus",
        ar="فيروس تريستيزا الحمضيات",
        scientific_name="Closterovirus",
    ),
    45: BilingualLabel(
        en="Citrus Melanose",
        ar="ميلانوز الحمضيات",
        scientific_name="Diaporthe citri",
    ),
    # --- Mango (المانجو) ---
    46: BilingualLabel(
        en="Mango Malformation",
        ar="تشوه المانجو",
        scientific_name="Fusarium mangiferae",
    ),
    47: BilingualLabel(
        en="Mango Bacterial Black Spot",
        ar="التبقع البكتيري الأسود للمانجو",
        scientific_name="Xanthomonas citri pv. mangiferaeindicae",
    ),
    48: BilingualLabel(
        en="Mango Stem End Rot",
        ar="تعفن نهاية ساق المانجو",
        scientific_name="Lasiodiplodia theobromae",
    ),
    # --- Strawberry (الفراولة) ---
    49: BilingualLabel(
        en="Strawberry Leaf Scorch",
        ar="احتراق أوراق الفراولة",
        scientific_name="Diplocarpon earlianum",
    ),
    50: BilingualLabel(
        en="Strawberry Angular Leaf Spot",
        ar="التبقع الزاوي للفراولة",
        scientific_name="Xanthomonas fragariae",
    ),
    51: BilingualLabel(
        en="Strawberry Leather Rot",
        ar="التعفن الجلدي للفراولة",
        scientific_name="Phytophthora cactorum",
    ),
    # --- Soybean (فول الصويا) ---
    52: BilingualLabel(
        en="Soybean Rust",
        ar="صدأ فول الصويا",
        scientific_name="Phakopsora pachyrhizi",
    ),
    53: BilingualLabel(
        en="Soybean Frogeye Leaf Spot",
        ar="تبقع عين الضفدع لفول الصويا",
        scientific_name="Cercospora sojina",
    ),
    54: BilingualLabel(
        en="Soybean Brown Spot",
        ar="التبقع البني لفول الصويا",
        scientific_name="Septoria glycines",
    ),
    55: BilingualLabel(
        en="Soybean Sudden Death Syndrome",
        ar="متلازمة الموت المفاجئ لفول الصويا",
        scientific_name="Fusarium virguliforme",
    ),
    # =========================================================================
    # Phase 2: Cotton & Peanut Diseases (القطن والفول السوداني)
    # =========================================================================
    # --- Cotton (القطن) ---
    56: BilingualLabel(
        en="Cotton Leaf Curl Virus",
        ar="فيروس تجعد أوراق القطن",
        scientific_name="Begomovirus",
    ),
    57: BilingualLabel(
        en="Cotton Verticillium Wilt",
        ar="ذبول الفرتيسيليوم للقطن",
        scientific_name="Verticillium dahliae",
    ),
    58: BilingualLabel(
        en="Cotton Bacterial Blight",
        ar="اللفحة البكتيرية للقطن",
        scientific_name="Xanthomonas citri pv. malvacearum",
    ),
    59: BilingualLabel(
        en="Cotton Boll Rot",
        ar="تعفن لوز القطن",
        scientific_name="Aspergillus flavus",
    ),
    60: BilingualLabel(
        en="Cotton Alternaria Leaf Spot",
        ar="تبقع أوراق القطن الألتيرناري",
        scientific_name="Alternaria macrospora",
    ),
    # --- Peanut (الفول السوداني) ---
    61: BilingualLabel(
        en="Peanut Early Leaf Spot",
        ar="التبقع المبكر للفول السوداني",
        scientific_name="Cercospora arachidicola",
    ),
    62: BilingualLabel(
        en="Peanut Late Leaf Spot",
        ar="التبقع المتأخر للفول السوداني",
        scientific_name="Cercosporidium personatum",
    ),
    63: BilingualLabel(
        en="Peanut Rust",
        ar="صدأ الفول السوداني",
        scientific_name="Puccinia arachidis",
    ),
    64: BilingualLabel(
        en="Peanut Stem Rot",
        ar="تعفن ساق الفول السوداني",
        scientific_name="Sclerotium rolfsii",
    ),
    65: BilingualLabel(
        en="Peanut Aspergillus Crown Rot",
        ar="تعفن تاج الفول السوداني",
        scientific_name="Aspergillus niger",
    ),
}

# Weed Classes
WEED_CLASSES: dict[int, BilingualLabel] = {
    0: BilingualLabel(en="Wild Oat", ar="الشوفان البري", scientific_name="Avena fatua"),
    1: BilingualLabel(en="Bermuda Grass", ar="النجيل", scientific_name="Cynodon dactylon"),
    2: BilingualLabel(en="Johnson Grass", ar="حشيشة جونسون", scientific_name="Sorghum halepense"),
    3: BilingualLabel(en="Pigweed", ar="عرف الديك", scientific_name="Amaranthus"),
    4: BilingualLabel(en="Lambsquarters", ar="السرمق", scientific_name="Chenopodium album"),
    5: BilingualLabel(en="Bindweed", ar="العليق", scientific_name="Convolvulus arvensis"),
    6: BilingualLabel(en="Nutsedge", ar="السعد", scientific_name="Cyperus"),
    7: BilingualLabel(en="Purslane", ar="الرجلة", scientific_name="Portulaca oleracea"),
    8: BilingualLabel(en="Dandelion", ar="الهندباء البرية", scientific_name="Taraxacum"),
    9: BilingualLabel(en="Ryegrass", ar="الزوان", scientific_name="Lolium"),
    10: BilingualLabel(en="Foxtail", ar="ذيل الثعلب", scientific_name="Setaria"),
    11: BilingualLabel(en="Crabgrass", ar="حشيشة السرطان", scientific_name="Digitaria"),
}

# Ripeness Stage Labels
RIPENESS_LABELS: dict[RipenessStage, BilingualLabel] = {
    RipenessStage.UNRIPE: BilingualLabel(en="Unripe", ar="غير ناضج"),
    RipenessStage.EARLY_RIPE: BilingualLabel(en="Early Ripe", ar="بداية النضج"),
    RipenessStage.HALF_RIPE: BilingualLabel(en="Half Ripe", ar="نصف ناضج"),
    RipenessStage.RIPE: BilingualLabel(en="Ripe", ar="ناضج"),
    RipenessStage.OVERRIPE: BilingualLabel(en="Overripe", ar="مفرط النضج"),
}


# =============================================================================
# Base Schemas
# =============================================================================


class BoundingBox(BaseModel):
    """Bounding box coordinates (normalized 0-1 or pixel coordinates)."""

    model_config = ConfigDict(frozen=True)

    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")

    @property
    def width(self) -> float:
        """Calculate bounding box width."""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """Calculate bounding box height."""
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        """Calculate bounding box area."""
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        """Calculate center point."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)


class ImageMetadata(BaseModel):
    """Metadata about the processed image."""

    width: int = Field(..., ge=1, description="Image width in pixels")
    height: int = Field(..., ge=1, description="Image height in pixels")
    channels: int = Field(default=3, ge=1, le=4, description="Number of color channels")
    format: str | None = Field(default=None, description="Image format (jpg, png, etc.)")


# =============================================================================
# Detection Schemas
# =============================================================================


class VLMVerification(BaseModel):
    """Secondary verification result from a Vision-Language Model (Qwen-VL / Ollama).

    Attached to each detection when ``use_vlm=True`` is requested.
    Detections with status ``dismissed`` are filtered from the response.
    """

    model_config = ConfigDict(frozen=True)

    status: VLMVerificationStatus = Field(..., description="VLM verification verdict")
    has_pest: bool = Field(..., description="Whether the VLM found a pest or disease")
    confidence: float = Field(..., ge=0.0, le=1.0, description="VLM confidence (0.0–1.0)")
    pest_type: str | None = Field(default=None, description="VLM-identified pest/disease name (English)")
    pest_type_ar: str | None = Field(default=None, description="VLM-identified pest/disease name (Arabic)")
    severity: str | None = Field(default=None, description="VLM-assessed severity (mild/moderate/severe)")
    diagnosis_en: str | None = Field(default=None, description="One-sentence VLM diagnosis (English)")
    diagnosis_ar: str | None = Field(default=None, description="One-sentence VLM diagnosis (Arabic)")
    provider: str = Field(default="disabled", description="VLM provider used (qwen_vl, ollama, disabled)")
    latency_ms: float = Field(default=0.0, ge=0.0, description="VLM API call latency in ms")
    error: str | None = Field(default=None, description="Error message when status is 'error'")


class DetectionBase(BaseModel):
    """Base detection result."""

    model_config = ConfigDict(frozen=True)

    class_id: int = Field(..., ge=0, description="Class ID")
    class_name_en: str = Field(..., description="Class name in English")
    class_name_ar: str = Field(..., description="Class name in Arabic")
    scientific_name: str | None = Field(default=None, description="Scientific name")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, description="Detection confidence")]
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")


class PestDetection(DetectionBase):
    """Pest detection result with additional attributes."""

    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="Pest severity level")
    life_stage: str | None = Field(default=None, description="Life stage (egg, larva, adult)")
    recommended_action_en: str | None = Field(default=None, description="Recommended action (English)")
    recommended_action_ar: str | None = Field(default=None, description="Recommended action (Arabic)")
    vlm_verification: VLMVerification | None = Field(
        default=None, description="VLM secondary verification result (present only when use_vlm=True)"
    )


class DiseaseDetection(DetectionBase):
    """Disease detection result with additional attributes."""

    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="Disease severity level")
    affected_area_percent: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Percentage of affected area"
    )
    spread_risk: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="Risk of spread")
    recommended_treatment_en: str | None = Field(default=None, description="Recommended treatment (English)")
    recommended_treatment_ar: str | None = Field(default=None, description="Recommended treatment (Arabic)")
    vlm_verification: VLMVerification | None = Field(
        default=None, description="VLM secondary verification result (present only when use_vlm=True)"
    )


class WeedDetection(DetectionBase):
    """Weed detection result with additional attributes."""

    coverage_percent: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Weed coverage percentage in detected area"
    )
    growth_stage: str | None = Field(default=None, description="Weed growth stage")
    vlm_verification: VLMVerification | None = Field(
        default=None, description="VLM secondary verification result (present only when use_vlm=True)"
    )


# =============================================================================
# Request Schemas
# =============================================================================


class DetectionRequest(BaseModel):
    """Base request for detection endpoints."""

    model_config = ConfigDict(extra="forbid")

    confidence_threshold: float = Field(default=0.25, ge=0.0, le=1.0, description="Minimum confidence threshold")
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0, description="IoU threshold for NMS")
    model_variant: ModelVariant = Field(default=ModelVariant.MEDIUM, description="Model variant to use")
    max_detections: int = Field(default=300, ge=1, le=1000, description="Maximum number of detections")
    image_size: int = Field(default=640, ge=320, le=1280, description="Input image size")
    return_visualization: bool = Field(default=False, description="Return annotated image with bounding boxes")

    @field_validator("image_size")
    @classmethod
    def validate_image_size(cls, v: int) -> int:
        """Ensure image size is multiple of 32."""
        if v % 32 != 0:
            return (v // 32 + 1) * 32
        return v


class PestDetectionRequest(DetectionRequest):
    """Request for pest detection."""

    include_life_stage: bool = Field(default=True, description="Include pest life stage in results")
    include_recommendations: bool = Field(default=True, description="Include recommended actions")
    use_vlm: bool = Field(
        default=False,
        description=(
            "Enable VLM secondary verification (Qwen-VL / Ollama). "
            "Reduces false positives ~40%%. Requires vlm_provider to be configured."
        ),
    )


class DiseaseDetectionRequest(DetectionRequest):
    """Request for disease detection."""

    calculate_affected_area: bool = Field(default=True, description="Calculate affected area percentage")
    include_treatments: bool = Field(default=True, description="Include treatment recommendations")
    use_vlm: bool = Field(
        default=False,
        description=(
            "Enable VLM secondary verification (Qwen-VL / Ollama). "
            "Reduces false positives ~40%%. Requires vlm_provider to be configured."
        ),
    )


class WeedDetectionRequest(DetectionRequest):
    """Request for weed detection."""

    calculate_coverage: bool = Field(default=True, description="Calculate weed coverage percentage")
    use_vlm: bool = Field(
        default=False,
        description=(
            "Enable VLM secondary verification (Qwen-VL / Ollama). "
            "Reduces false positives ~40%%. Requires vlm_provider to be configured."
        ),
    )


class PlantCountRequest(BaseModel):
    """Request for plant counting."""

    model_config = ConfigDict(extra="forbid")

    confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Confidence threshold")
    model_variant: ModelVariant = Field(default=ModelVariant.MEDIUM, description="Model variant")
    generate_density_map: bool = Field(default=True, description="Generate density heatmap")
    grid_size: int = Field(default=32, ge=8, le=128, description="Grid size for density map")
    count_per_unit_area: bool = Field(default=True, description="Calculate plants per square meter")
    gsd_meters: float | None = Field(default=None, gt=0.0, description="Ground sampling distance in meters/pixel")


class RipenessClassificationRequest(BaseModel):
    """Request for ripeness classification."""

    model_config = ConfigDict(extra="forbid")

    confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Confidence threshold")
    model_variant: ModelVariant = Field(default=ModelVariant.MEDIUM, description="Model variant")
    fruit_type: str | None = Field(default=None, description="Type of fruit (tomato, date, grape, etc.)")
    return_stage_distribution: bool = Field(default=True, description="Return distribution across stages")


class LeafSegmentationRequest(BaseModel):
    """Request for leaf segmentation."""

    model_config = ConfigDict(extra="forbid")

    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence threshold")
    model_variant: ModelVariant = Field(default=ModelVariant.MEDIUM, description="Model variant")
    return_mask: bool = Field(default=True, description="Return segmentation mask")
    calculate_area: bool = Field(default=True, description="Calculate leaf area in pixels/sq meters")
    gsd_meters: float | None = Field(default=None, gt=0.0, description="Ground sampling distance for area calculation")


class ObjectTrackingRequest(BaseModel):
    """Request for object tracking."""

    model_config = ConfigDict(extra="forbid")

    confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Confidence threshold")
    model_variant: ModelVariant = Field(default=ModelVariant.MEDIUM, description="Model variant")
    tracking_method: str = Field(default="bytetrack", description="Tracking algorithm (bytetrack, botsort)")
    persist_ids: bool = Field(default=True, description="Persist object IDs across frames")
    track_buffer: int = Field(default=30, ge=1, le=300, description="Frames to keep lost tracks")


# =============================================================================
# Response Schemas
# =============================================================================


class DetectionResponse(BaseModel):
    """Base response for detection endpoints."""

    model_config = ConfigDict(from_attributes=True)

    request_id: UUID = Field(default_factory=uuid4, description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: float = Field(..., ge=0.0, description="Processing time in milliseconds")
    model_variant: ModelVariant = Field(..., description="Model variant used")
    image_metadata: ImageMetadata = Field(..., description="Input image metadata")


class PestDetectionResponse(DetectionResponse):
    """Response for pest detection."""

    detections: list[PestDetection] = Field(default_factory=list, description="List of pest detections")
    total_count: int = Field(default=0, ge=0, description="Total number of pests detected")
    severity_summary: dict[str, int] = Field(default_factory=dict, description="Count by severity level")
    visualization_base64: str | None = Field(default=None, description="Base64 encoded visualization")
    vlm_stats: dict[str, int] | None = Field(
        default=None,
        description=(
            "VLM verification counts (confirmed/suspicious/dismissed/error). "
            "Present only when use_vlm=True."
        ),
    )


class DiseaseDetectionResponse(DetectionResponse):
    """Response for disease detection."""

    detections: list[DiseaseDetection] = Field(default_factory=list, description="List of disease detections")
    total_count: int = Field(default=0, ge=0, description="Total number of diseases detected")
    overall_health_score: float = Field(
        default=100.0, ge=0.0, le=100.0, description="Overall plant health score (0-100)"
    )
    severity_summary: dict[str, int] = Field(default_factory=dict, description="Count by severity level")
    visualization_base64: str | None = Field(default=None, description="Base64 encoded visualization")
    vlm_stats: dict[str, int] | None = Field(
        default=None,
        description=(
            "VLM verification counts (confirmed/suspicious/dismissed/error). "
            "Present only when use_vlm=True."
        ),
    )


class WeedDetectionResponse(DetectionResponse):
    """Response for weed detection."""

    detections: list[WeedDetection] = Field(default_factory=list, description="List of weed detections")
    total_count: int = Field(default=0, ge=0, description="Total number of weeds detected")
    total_coverage_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Total weed coverage percentage")
    species_distribution: dict[str, int] = Field(default_factory=dict, description="Count by species")
    visualization_base64: str | None = Field(default=None, description="Base64 encoded visualization")
    vlm_stats: dict[str, int] | None = Field(
        default=None,
        description=(
            "VLM verification counts (confirmed/suspicious/dismissed/error). "
            "Present only when use_vlm=True."
        ),
    )


class PlantCountResponse(DetectionResponse):
    """Response for plant counting."""

    total_count: int = Field(..., ge=0, description="Total number of plants")
    density_per_sqm: float | None = Field(default=None, ge=0.0, description="Plants per square meter")
    density_map_base64: str | None = Field(default=None, description="Base64 encoded density heatmap")
    grid_counts: list[list[int]] | None = Field(default=None, description="Grid-based plant counts")
    average_spacing_m: float | None = Field(default=None, description="Average plant spacing in meters")


class RipenessResult(BaseModel):
    """Individual ripeness classification result."""

    model_config = ConfigDict(frozen=True)

    bbox: BoundingBox = Field(..., description="Fruit location")
    stage: RipenessStage = Field(..., description="Ripeness stage")
    stage_label_en: str = Field(..., description="Stage label in English")
    stage_label_ar: str = Field(..., description="Stage label in Arabic")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    days_to_optimal: int | None = Field(default=None, description="Estimated days to optimal ripeness")


class RipenessClassificationResponse(DetectionResponse):
    """Response for ripeness classification."""

    results: list[RipenessResult] = Field(default_factory=list, description="Individual classifications")
    total_count: int = Field(default=0, ge=0, description="Total fruits classified")
    stage_distribution: dict[str, int] = Field(default_factory=dict, description="Count by ripeness stage")
    average_ripeness_score: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Average ripeness (0=unripe, 100=overripe)"
    )
    harvest_readiness_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage ready for harvest")
    visualization_base64: str | None = Field(default=None, description="Base64 encoded visualization")


class LeafSegment(BaseModel):
    """Individual leaf segment result."""

    model_config = ConfigDict(frozen=True)

    segment_id: int = Field(..., ge=0, description="Segment identifier")
    bbox: BoundingBox = Field(..., description="Leaf bounding box")
    area_pixels: int = Field(..., ge=0, description="Leaf area in pixels")
    area_sqm: float | None = Field(default=None, ge=0.0, description="Leaf area in square meters")
    perimeter_pixels: int | None = Field(default=None, ge=0, description="Leaf perimeter in pixels")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Segmentation confidence")
    health_indicator: float | None = Field(default=None, ge=0.0, le=1.0, description="Leaf health indicator (0-1)")


class LeafSegmentationResponse(DetectionResponse):
    """Response for leaf segmentation."""

    segments: list[LeafSegment] = Field(default_factory=list, description="Individual leaf segments")
    total_leaves: int = Field(default=0, ge=0, description="Total leaves detected")
    total_leaf_area_pixels: int = Field(default=0, ge=0, description="Total leaf area in pixels")
    total_leaf_area_sqm: float | None = Field(default=None, ge=0.0, description="Total leaf area in sq meters")
    leaf_area_index: float | None = Field(default=None, ge=0.0, description="Estimated LAI")
    mask_base64: str | None = Field(default=None, description="Base64 encoded segmentation mask")
    visualization_base64: str | None = Field(default=None, description="Base64 encoded visualization")


class TrackedObject(BaseModel):
    """Individual tracked object."""

    model_config = ConfigDict(frozen=True)

    track_id: int = Field(..., ge=0, description="Persistent track ID")
    class_id: int = Field(..., ge=0, description="Object class ID")
    class_name: str = Field(..., description="Object class name")
    bbox: BoundingBox = Field(..., description="Current bounding box")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    velocity: tuple[float, float] | None = Field(default=None, description="Velocity (vx, vy) pixels/frame")
    track_length: int = Field(default=1, ge=1, description="Number of frames tracked")
    is_new: bool = Field(default=False, description="Whether this is a newly detected object")


class ObjectTrackingResponse(DetectionResponse):
    """Response for object tracking."""

    frame_number: int = Field(..., ge=0, description="Current frame number")
    tracked_objects: list[TrackedObject] = Field(default_factory=list, description="Currently tracked objects")
    active_tracks: int = Field(default=0, ge=0, description="Number of active tracks")
    new_tracks: int = Field(default=0, ge=0, description="Number of new tracks this frame")
    lost_tracks: int = Field(default=0, ge=0, description="Number of lost tracks this frame")
    total_unique_objects: int = Field(default=0, ge=0, description="Total unique objects seen")
    visualization_base64: str | None = Field(default=None, description="Base64 encoded visualization")


# =============================================================================
# Error Schemas
# =============================================================================


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message in English")
    message_ar: str | None = Field(default=None, description="Error message in Arabic")
    field: str | None = Field(default=None, description="Field that caused the error")
    details: dict[str, Any] | None = Field(default=None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Standard error response."""

    request_id: UUID = Field(default_factory=uuid4, description="Request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    status_code: int = Field(..., ge=400, le=599, description="HTTP status code")
    error: str = Field(..., description="Error type")
    errors: list[ErrorDetail] = Field(default_factory=list, description="List of error details")


# =============================================================================
# Health Check Schemas
# =============================================================================


class HealthStatus(BaseModel):
    """Health check status."""

    status: str = Field(..., description="Health status (ok, degraded, unhealthy)")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class ReadinessStatus(BaseModel):
    """Readiness check status with component details."""

    status: str = Field(..., description="Overall status (ok, degraded, unhealthy)")
    database: bool = Field(..., description="Database connection status")
    nats: bool = Field(..., description="NATS connection status")
    redis: bool = Field(..., description="Redis connection status")
    models_loaded: bool = Field(..., description="Model loading status")
    gpu_available: bool = Field(..., description="GPU availability status")
    models: dict[str, bool] = Field(default_factory=dict, description="Individual model status")
    agricultural_models_loaded: bool = Field(
        default=True,
        description="Whether agricultural-trained models are loaded (False = using generic fallback)",
    )
    degraded_tasks: list[str] = Field(
        default_factory=list,
        description="List of tasks running with generic fallback models instead of agricultural models",
    )
    degraded_message: str | None = Field(
        default=None,
        description="Human-readable degradation message (English)",
    )
    degraded_message_ar: str | None = Field(
        default=None,
        description="Human-readable degradation message (Arabic)",
    )

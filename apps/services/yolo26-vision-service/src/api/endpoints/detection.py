"""
Detection endpoints for YOLO26 Vision Service.

Provides endpoints for pest detection, disease detection, and weed detection
with bilingual (Arabic/English) class names.
"""

import base64
import io
import time
from typing import Annotated
from uuid import uuid4

import numpy as np
import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from PIL import Image

from src.api.schemas import (
    DISEASE_CLASSES,
    PEST_CLASSES,
    WEED_CLASSES,
    BilingualLabel,
    BoundingBox,
    DiseaseDetection,
    DiseaseDetectionRequest,
    DiseaseDetectionResponse,
    ImageMetadata,
    ModelVariant,
    PestDetection,
    PestDetectionRequest,
    PestDetectionResponse,
    SeverityLevel,
    WeedDetection,
    WeedDetectionRequest,
    WeedDetectionResponse,
)
from src.core.config import settings
from src.events import VisionEventPublisher
from src.models.yolo26_manager import (
    InferenceResult,
    ModelTask,
    YOLO26ModelManager,
    get_model_manager,
)

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")

logger = structlog.get_logger(__name__)


def _get_event_publisher(request) -> VisionEventPublisher | None:
    """Get event publisher from app state if NATS is connected."""
    nc = getattr(request.app.state, "nc", None)
    nats_connected = getattr(request.app.state, "nats_connected", False)
    if nc and nats_connected:
        return VisionEventPublisher(nc)
    return None


router = APIRouter(prefix="/api/v1", tags=["detection"])


# =============================================================================
# Dependencies
# =============================================================================


async def get_manager() -> YOLO26ModelManager:
    """Get the model manager instance."""
    return get_model_manager()


async def validate_image(file: UploadFile) -> bytes:
    """Validate and read uploaded image."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid file type",
                "message": "File must be an image (JPEG, PNG, WebP, etc.)",
                "message_ar": "يجب أن يكون الملف صورة (JPEG، PNG، WebP، إلخ)",
            },
        )

    content = await file.read()

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "File too large",
                "message": f"Maximum file size is {settings.max_upload_size_mb}MB",
                "message_ar": f"الحد الأقصى لحجم الملف هو {settings.max_upload_size_mb} ميجابايت",
            },
        )

    return content


def get_image_metadata(image_bytes: bytes) -> ImageMetadata:
    """Extract image metadata from bytes."""
    img = Image.open(io.BytesIO(image_bytes))
    return ImageMetadata(
        width=img.width,
        height=img.height,
        channels=len(img.getbands()),
        format=img.format,
    )


def calculate_severity(confidence: float, area_ratio: float = 0.0) -> SeverityLevel:
    """Calculate severity level based on confidence and affected area."""
    score = confidence * 0.6 + area_ratio * 0.4

    if score >= 0.8:
        return SeverityLevel.CRITICAL
    elif score >= 0.6:
        return SeverityLevel.HIGH
    elif score >= 0.4:
        return SeverityLevel.MEDIUM
    elif score >= 0.2:
        return SeverityLevel.LOW
    else:
        return SeverityLevel.NONE


def create_visualization(
    image_bytes: bytes,
    detections: list[dict],
    class_labels: dict[int, BilingualLabel],
) -> str:
    """Create visualization with bounding boxes and return as base64."""
    try:
        from PIL import ImageDraw, ImageFont

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Try to load a font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except Exception:
            font = ImageFont.load_default()

        colors = {
            SeverityLevel.CRITICAL: "#FF0000",
            SeverityLevel.HIGH: "#FF6600",
            SeverityLevel.MEDIUM: "#FFCC00",
            SeverityLevel.LOW: "#00CC00",
            SeverityLevel.NONE: "#0066FF",
        }

        for det in detections:
            bbox = det["bbox"]
            severity = det.get("severity", SeverityLevel.MEDIUM)
            color = colors.get(severity, "#00FF00")
            class_id = det["class_id"]
            confidence = det["confidence"]

            # Draw bounding box
            draw.rectangle(
                [bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]],
                outline=color,
                width=2,
            )

            # Draw label
            label = class_labels.get(class_id)
            if label:
                text = f"{label.en} ({confidence:.0%})"
                text_bbox = draw.textbbox((bbox["x1"], bbox["y1"] - 20), text, font=font)
                draw.rectangle(text_bbox, fill=color)
                draw.text((bbox["x1"], bbox["y1"] - 20), text, fill="white", font=font)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        logger.warning("visualization_failed", error=str(e))
        return ""


# =============================================================================
# Pest Detection Recommendations
# =============================================================================

PEST_RECOMMENDATIONS: dict[int, dict[str, str]] = {
    0: {  # Red Palm Weevil
        "en": "Immediately report to agricultural authorities. Apply trunk injection with imidacloprid. Install pheromone traps.",
        "ar": "أبلغ السلطات الزراعية فورًا. قم بحقن الجذع بمادة الإيميداكلوبريد. ثبّت مصائد الفرمونات.",
    },
    1: {  # Aphid
        "en": "Apply neem oil or insecticidal soap. Introduce beneficial insects like ladybugs. Remove heavily infested leaves.",
        "ar": "استخدم زيت النيم أو الصابون الحشري. أدخل حشرات نافعة مثل الدعسوقة. أزل الأوراق المصابة بشدة.",
    },
    2: {  # Whitefly
        "en": "Use yellow sticky traps. Apply insecticidal soap or neem oil. Introduce parasitic wasps (Encarsia formosa).",
        "ar": "استخدم المصائد اللاصقة الصفراء. طبق الصابون الحشري أو زيت النيم. أدخل الدبابير الطفيلية.",
    },
    3: {  # Spider Mite
        "en": "Increase humidity. Apply miticide or neem oil. Introduce predatory mites (Phytoseiulus persimilis).",
        "ar": "زد الرطوبة. طبق المبيد العنكبوتي أو زيت النيم. أدخل العث المفترس.",
    },
    4: {  # Thrips
        "en": "Use blue sticky traps. Apply spinosad or neem oil. Remove plant debris.",
        "ar": "استخدم المصائد اللاصقة الزرقاء. طبق السبينوساد أو زيت النيم. أزل بقايا النباتات.",
    },
    5: {  # Leaf Miner
        "en": "Remove and destroy affected leaves. Apply systemic insecticide. Use yellow sticky traps for adults.",
        "ar": "أزل الأوراق المصابة ودمرها. طبق مبيدًا جهازيًا. استخدم المصائد اللاصقة الصفراء للحشرات البالغة.",
    },
    6: {  # Cutworm
        "en": "Apply Bacillus thuringiensis (Bt). Create barriers around seedlings. Hand-pick at night.",
        "ar": "طبق باسيلوس ثورنجينسيس. أنشئ حواجز حول الشتلات. اجمعها يدويًا ليلًا.",
    },
    7: {  # Armyworm
        "en": "Apply Bacillus thuringiensis (Bt) or spinosad. Scout fields early morning. Remove egg masses.",
        "ar": "طبق باسيلوس ثورنجينسيس أو السبينوساد. تفقد الحقول في الصباح الباكر. أزل كتل البيض.",
    },
    11: {  # Locust
        "en": "Report to agricultural authorities immediately. Apply recommended insecticides. Coordinate with regional control programs.",
        "ar": "أبلغ السلطات الزراعية فورًا. طبق المبيدات الموصى بها. نسق مع برامج المكافحة الإقليمية.",
    },
    # Phase 1: Crop-Specific Pest Recommendations
    22: {  # Colorado Potato Beetle
        "en": "Hand-pick adults and larvae. Apply Bacillus thuringiensis var. tenebrionis (Btt) for larvae. Rotate crops annually. Use neem oil for early infestations.",
        "ar": "اجمع الحشرات البالغة واليرقات يدويًا. طبق باسيلوس ثورنجينسيس (Btt) لليرقات. قم بالدورة الزراعية سنويًا. استخدم زيت النيم للإصابات المبكرة.",
    },
    23: {  # Fall Armyworm
        "en": "Apply chlorantraniliprole or emamectin benzoate at early instar stages. Scout fields at dawn/dusk. Use pheromone traps for monitoring.",
        "ar": "طبق كلورانترانيليبرول أو إمامكتين بنزوات في مراحل اليرقات المبكرة. تفقد الحقول عند الفجر/الغسق. استخدم مصائد الفرمونات للمراقبة.",
    },
    24: {  # Mango Seed Weevil
        "en": "Collect and destroy fallen fruits. Apply trunk banding with sticky traps. Use hot water treatment (46°C for 60 min) for post-harvest control.",
        "ar": "اجمع الثمار المتساقطة ودمرها. طبق أشرطة لاصقة على الجذوع. استخدم المعالجة بالماء الساخن (46 درجة لمدة 60 دقيقة) بعد الحصاد.",
    },
    25: {  # Strawberry Crown Moth
        "en": "Remove and destroy infested crowns. Apply entomopathogenic nematodes. Maintain field sanitation and remove plant debris.",
        "ar": "أزل التيجان المصابة ودمرها. طبق النيماتودا الممرضة للحشرات. حافظ على نظافة الحقل وأزل بقايا النباتات.",
    },
    26: {  # Soybean Pod Borer
        "en": "Apply Bacillus thuringiensis (Bt) or lambda-cyhalothrin at flowering stage. Use pheromone traps. Practice early planting to avoid peak infestation.",
        "ar": "طبق باسيلوس ثورنجينسيس أو لامبدا سيهالوثرين في مرحلة الإزهار. استخدم مصائد الفرمونات. مارس الزراعة المبكرة لتجنب ذروة الإصابة.",
    },
    # Phase 2: Cotton & Peanut Pest Recommendations
    27: {  # Cotton Bollworm
        "en": "Apply chlorantraniliprole or emamectin benzoate at early boll stage. Use pheromone traps for monitoring. Release Trichogramma parasitoids. Scout at dusk when moths are active.",
        "ar": "طبق كلورانترانيليبرول أو إمامكتين بنزوات في مرحلة اللوز المبكرة. استخدم مصائد الفرمونات للمراقبة. أطلق طفيل التريكوجراما. تفقد عند الغسق عندما تنشط الفراشات.",
    },
    28: {  # Pink Bollworm
        "en": "Use sterile insect technique (SIT) where available. Apply Bt cotton varieties. Install pheromone traps (5/ha). Destroy crop residues after harvest immediately.",
        "ar": "استخدم تقنية الحشرات العقيمة حيث تتوفر. ازرع أصناف القطن Bt. ثبّت مصائد فرمونات (5/هكتار). دمر بقايا المحصول بعد الحصاد فورًا.",
    },
    29: {  # Cotton Whitefly (Bemisia tabaci)
        "en": "Apply neem oil or spiromesifen at nymph stage. Use yellow sticky traps. Introduce Eretmocerus parasitoids. Avoid excessive nitrogen which promotes whitefly.",
        "ar": "طبق زيت النيم أو سبيروميسيفين في مرحلة الحورية. استخدم المصائد اللاصقة الصفراء. أدخل طفيل إريتموسيروس. تجنب الإفراط في النيتروجين الذي يعزز الذبابة البيضاء.",
    },
    30: {  # Peanut Leaf Miner
        "en": "Apply triazophos or profenofos at early infestation. Use neem-based pesticides. Remove and destroy infested leaves. Maintain field hygiene.",
        "ar": "طبق ترايازوفوس أو بروفينوفوس عند الإصابة المبكرة. استخدم مبيدات النيم. أزل الأوراق المصابة ودمرها. حافظ على نظافة الحقل.",
    },
    31: {  # Groundnut Aphid
        "en": "Apply imidacloprid seed treatment. Use neem oil or dimethoate foliar spray. Introduce ladybird beetles and lacewings. Remove volunteer plants.",
        "ar": "طبق معاملة البذور بالإيميداكلوبريد. استخدم رش ورقي بزيت النيم أو الدايمثويت. أدخل خنافس الدعسوقة وأسد المن. أزل النباتات التطوعية.",
    },
}

# =============================================================================
# Disease Treatment Recommendations
# =============================================================================

DISEASE_TREATMENTS: dict[int, dict[str, str]] = {
    0: {  # Wheat Rust
        "en": "Apply fungicide (propiconazole or tebuconazole). Remove infected plant debris. Use resistant varieties.",
        "ar": "طبق مبيدًا فطريًا (بروبيكونازول أو تيبوكونازول). أزل بقايا النباتات المصابة. استخدم أصنافًا مقاومة.",
    },
    1: {  # Powdery Mildew
        "en": "Apply sulfur-based fungicide or potassium bicarbonate. Improve air circulation. Avoid overhead watering.",
        "ar": "طبق مبيدًا فطريًا كبريتيًا أو بيكربونات البوتاسيوم. حسّن دوران الهواء. تجنب الري العلوي.",
    },
    2: {  # Downy Mildew
        "en": "Apply copper-based fungicide. Remove infected leaves. Ensure good drainage and air circulation.",
        "ar": "طبق مبيدًا فطريًا نحاسيًا. أزل الأوراق المصابة. تأكد من الصرف الجيد ودوران الهواء.",
    },
    3: {  # Early Blight
        "en": "Apply chlorothalonil or mancozeb. Remove lower infected leaves. Mulch to prevent soil splash.",
        "ar": "طبق كلوروثالونيل أو مانكوزيب. أزل الأوراق السفلية المصابة. ضع نشارة لمنع تناثر التربة.",
    },
    4: {  # Late Blight
        "en": "Apply systemic fungicide immediately (metalaxyl). Remove and destroy infected plants. Avoid overhead irrigation.",
        "ar": "طبق مبيدًا فطريًا جهازيًا فورًا (ميتالاكسيل). أزل النباتات المصابة ودمرها. تجنب الري العلوي.",
    },
    6: {  # Fusarium Wilt
        "en": "Remove infected plants. Solarize soil. Use resistant varieties. Rotate crops for 4+ years.",
        "ar": "أزل النباتات المصابة. شمّس التربة. استخدم أصنافًا مقاومة. قم بالدورة الزراعية لأكثر من 4 سنوات.",
    },
    8: {  # Root Rot
        "en": "Improve drainage. Apply phosphonate fungicide. Avoid overwatering. Remove severely affected plants.",
        "ar": "حسّن الصرف. طبق مبيد فوسفونات فطري. تجنب الإفراط في الري. أزل النباتات المصابة بشدة.",
    },
    12: {  # Mosaic Virus
        "en": "Remove infected plants immediately. Control aphid vectors. Use virus-free seeds. Disinfect tools.",
        "ar": "أزل النباتات المصابة فورًا. كافح ناقلات المن. استخدم بذورًا خالية من الفيروس. عقم الأدوات.",
    },
    28: {  # Date Palm Bayoud
        "en": "Remove and burn infected palms. Do not replant in infected areas for 5+ years. Use resistant cultivars.",
        "ar": "أزل النخيل المصاب واحرقه. لا تعد الزراعة في المناطق المصابة لأكثر من 5 سنوات. استخدم أصنافًا مقاومة.",
    },
    # =========================================================================
    # Phase 1: Crop-Specific Disease Treatments
    # =========================================================================
    # --- Corn (الذرة) ---
    34: {  # Corn Gray Leaf Spot
        "en": "Apply strobilurin or triazole fungicide at VT-R1 stage. Rotate with non-host crops (soybean). Reduce tillage to limit inoculum. Use resistant hybrids.",
        "ar": "طبق مبيدًا فطريًا ستروبيلورين أو تريازول في مرحلة VT-R1. قم بالدورة الزراعية مع محاصيل غير مضيفة (فول الصويا). قلل الحرث للحد من اللقاح. استخدم هجنًا مقاومة.",
    },
    35: {  # Corn Northern Leaf Blight
        "en": "Apply foliar fungicide (azoxystrobin or propiconazole) at first symptoms. Plant resistant hybrids with Ht genes. Rotate crops and manage residue.",
        "ar": "طبق مبيدًا فطريًا ورقيًا (أزوكسيستروبين أو بروبيكونازول) عند أول الأعراض. ازرع هجنًا مقاومة بجينات Ht. قم بالدورة الزراعية وأدِر بقايا المحصول.",
    },
    36: {  # Corn Common Rust
        "en": "Apply fungicide (pyraclostrobin or triazole) if pustules appear before tasseling. Plant resistant hybrids. Monitor fields regularly during humid conditions.",
        "ar": "طبق مبيدًا فطريًا (بيراكلوستروبين أو تريازول) إذا ظهرت البثرات قبل التزهير. ازرع هجنًا مقاومة. راقب الحقول بانتظام في الظروف الرطبة.",
    },
    37: {  # Maize Streak Virus
        "en": "Control leafhopper vectors with imidacloprid seed treatment. Plant resistant varieties. Remove infected plants early. Eliminate grass weeds near fields.",
        "ar": "كافح نطاطات الأوراق بمعاملة البذور بالإيميداكلوبريد. ازرع أصنافًا مقاومة. أزل النباتات المصابة مبكرًا. أزل الحشائش النجيلية قرب الحقول.",
    },
    # --- Wheat (القمح) ---
    38: {  # Wheat Yellow Rust
        "en": "Apply triazole fungicide (tebuconazole) immediately upon detection. Use resistant varieties (Yr genes). Scout fields from tillering to heading stage.",
        "ar": "طبق مبيدًا فطريًا تريازول (تيبوكونازول) فور الكشف. استخدم أصنافًا مقاومة (جينات Yr). تفقد الحقول من مرحلة التفريع إلى التسبيل.",
    },
    39: {  # Wheat Karnal Bunt
        "en": "Use certified disease-free seed. Apply propiconazole at heading. Avoid late planting. Report to plant quarantine authorities if detected.",
        "ar": "استخدم بذورًا معتمدة خالية من المرض. طبق بروبيكونازول عند التسبيل. تجنب الزراعة المتأخرة. أبلغ سلطات الحجر الزراعي عند الكشف.",
    },
    40: {  # Wheat Helminthosporium Blight
        "en": "Apply mancozeb or propiconazole at flag leaf emergence. Use resistant varieties. Practice crop rotation with non-cereal crops.",
        "ar": "طبق مانكوزيب أو بروبيكونازول عند ظهور ورقة العلم. استخدم أصنافًا مقاومة. مارس الدورة الزراعية مع محاصيل غير نجيلية.",
    },
    # --- Potato (البطاطس) ---
    41: {  # Potato Black Scurf
        "en": "Treat seed tubers with flutolanil or pencycuron before planting. Ensure proper soil drainage. Avoid planting in cold, wet soils. Rotate with non-host crops for 3+ years.",
        "ar": "عالج درنات البذور بالفلوتولانيل أو بنسيكورون قبل الزراعة. تأكد من الصرف الجيد. تجنب الزراعة في التربة الباردة الرطبة. قم بالدورة الزراعية لأكثر من 3 سنوات.",
    },
    42: {  # Potato Virus Y
        "en": "Use certified virus-free seed potatoes. Control aphid vectors with mineral oil sprays. Remove infected plants immediately. Plant resistant varieties.",
        "ar": "استخدم بطاطس بذرية معتمدة خالية من الفيروس. كافح المن الناقل برش الزيوت المعدنية. أزل النباتات المصابة فورًا. ازرع أصنافًا مقاومة.",
    },
    # --- Citrus (الحمضيات) ---
    43: {  # Citrus Black Spot
        "en": "Apply copper-based fungicide or strobilurins from fruit set to harvest. Remove fallen leaves. Prune for better air circulation. Use disease-free nursery stock.",
        "ar": "طبق مبيدًا فطريًا نحاسيًا أو ستروبيلورين من عقد الثمار حتى الحصاد. أزل الأوراق المتساقطة. قلّم لتحسين دوران الهواء. استخدم شتلات خالية من المرض.",
    },
    44: {  # Citrus Tristeza Virus
        "en": "Use CTV-tolerant rootstocks (Volkameriana, Citrumelo). Remove infected trees in young orchards. Control aphid vectors. Use certified budwood from clean sources.",
        "ar": "استخدم أصولًا متحملة لفيروس تريستيزا. أزل الأشجار المصابة في البساتين الصغيرة. كافح المن الناقل. استخدم طعومًا معتمدة من مصادر نظيفة.",
    },
    45: {  # Citrus Melanose
        "en": "Apply copper fungicide during spring flush. Prune dead twigs and branches. Ensure good air circulation. Collect and destroy fallen debris.",
        "ar": "طبق مبيدًا فطريًا نحاسيًا أثناء نمو الربيع. قلّم الأغصان والفروع الميتة. تأكد من دوران الهواء الجيد. اجمع الحطام المتساقط ودمره.",
    },
    # --- Mango (المانجو) ---
    46: {  # Mango Malformation
        "en": "Prune and burn affected panicles and vegetative shoots. Apply naphthalene acetic acid (NAA) to inhibit malformed tissue. Avoid excessive nitrogen fertilization.",
        "ar": "قلّم واحرق العناقيد الزهرية والنموات الخضرية المصابة. طبق حمض النفثالين أسيتيك لتثبيط النسيج المشوه. تجنب الإفراط في التسميد النيتروجيني.",
    },
    47: {  # Mango Bacterial Black Spot
        "en": "Apply copper-based bactericide during wet weather. Avoid overhead irrigation. Use windbreaks to reduce injury. Plant resistant cultivars.",
        "ar": "طبق مبيدًا بكتيريًا نحاسيًا أثناء الطقس الرطب. تجنب الري العلوي. استخدم مصدات الرياح لتقليل الإصابة. ازرع أصنافًا مقاومة.",
    },
    48: {  # Mango Stem End Rot
        "en": "Apply hot water treatment (52°C for 5 min) post-harvest. Use fungicide dip (prochloraz). Maintain cold chain. Handle fruits carefully to avoid wounds.",
        "ar": "طبق المعالجة بالماء الساخن (52 درجة لمدة 5 دقائق) بعد الحصاد. استخدم غمس بالمبيد الفطري (بروكلوراز). حافظ على سلسلة التبريد. تعامل مع الثمار بحذر لتجنب الجروح.",
    },
    # --- Strawberry (الفراولة) ---
    49: {  # Strawberry Leaf Scorch
        "en": "Remove and destroy infected leaves. Apply captan or myclobutanil fungicide. Improve air circulation between rows. Use disease-free transplants.",
        "ar": "أزل الأوراق المصابة ودمرها. طبق مبيد كابتان أو مايكلوبيوتانيل. حسّن دوران الهواء بين الصفوف. استخدم شتلات خالية من المرض.",
    },
    50: {  # Strawberry Angular Leaf Spot
        "en": "Avoid overhead irrigation. Apply copper hydroxide during cool wet periods. Use pathogen-free transplants. Remove and destroy infected plant debris.",
        "ar": "تجنب الري العلوي. طبق هيدروكسيد النحاس خلال الفترات الباردة الرطبة. استخدم شتلات خالية من المسبب المرضي. أزل بقايا النباتات المصابة ودمرها.",
    },
    51: {  # Strawberry Leather Rot
        "en": "Improve drainage and use raised beds. Apply mefenoxam or phosphonate fungicide. Use straw mulch to prevent soil splash. Harvest frequently.",
        "ar": "حسّن الصرف واستخدم الأحواض المرتفعة. طبق مبيد ميفينوكسام أو فوسفونات. استخدم نشارة القش لمنع تناثر التربة. احصد بشكل متكرر.",
    },
    # --- Soybean (فول الصويا) ---
    52: {  # Soybean Rust
        "en": "Apply triazole or strobilurin fungicide at R1-R3 growth stages. Scout lower canopy for early symptoms. Plant early-maturing varieties. Avoid late planting.",
        "ar": "طبق مبيدًا فطريًا تريازول أو ستروبيلورين في مراحل النمو R1-R3. تفقد المظلة السفلية للأعراض المبكرة. ازرع أصنافًا مبكرة النضج. تجنب الزراعة المتأخرة.",
    },
    53: {  # Soybean Frogeye Leaf Spot
        "en": "Apply strobilurin fungicide at R3 stage. Rotate with non-host crops for 2+ years. Use resistant varieties. Manage crop residue through tillage.",
        "ar": "طبق مبيدًا فطريًا ستروبيلورين في مرحلة R3. قم بالدورة الزراعية مع محاصيل غير مضيفة لأكثر من سنتين. استخدم أصنافًا مقاومة. أدِر بقايا المحصول بالحرث.",
    },
    54: {  # Soybean Brown Spot
        "en": "Rotate with non-host crops. Apply fungicide if disease is severe at pod fill. Improve potassium fertility. Use tillage to bury infected residue.",
        "ar": "قم بالدورة الزراعية مع محاصيل غير مضيفة. طبق مبيدًا فطريًا إذا كان المرض شديدًا عند امتلاء القرون. حسّن خصوبة البوتاسيوم. احرث لدفن البقايا المصابة.",
    },
    55: {  # Soybean Sudden Death Syndrome
        "en": "Plant resistant varieties. Improve soil drainage. Delay planting until soil warms. Manage soybean cyst nematode which worsens SDS. Avoid soil compaction.",
        "ar": "ازرع أصنافًا مقاومة. حسّن صرف التربة. أخّر الزراعة حتى تسخن التربة. كافح نيماتودا كيس فول الصويا التي تفاقم المرض. تجنب ضغط التربة.",
    },
    # =========================================================================
    # Phase 2: Cotton & Peanut Disease Treatments
    # =========================================================================
    # --- Cotton (القطن) ---
    56: {  # Cotton Leaf Curl Virus
        "en": "Control whitefly vectors (Bemisia tabaci) with imidacloprid or spiromesifen. Use virus-resistant Bt cotton varieties. Remove infected plants early. Destroy alternate weed hosts.",
        "ar": "كافح ذباب القطن الأبيض الناقل بالإيميداكلوبريد أو سبيروميسيفين. استخدم أصناف قطن Bt المقاومة للفيروس. أزل النباتات المصابة مبكرًا. دمر الحشائش المضيفة البديلة.",
    },
    57: {  # Cotton Verticillium Wilt
        "en": "Rotate with non-host crops (cereals) for 3+ years. Use tolerant varieties. Improve soil drainage. Avoid excessive irrigation. Soil fumigation in severe cases.",
        "ar": "قم بالدورة الزراعية مع محاصيل غير مضيفة (حبوب) لأكثر من 3 سنوات. استخدم أصنافًا متحملة. حسّن صرف التربة. تجنب الإفراط في الري. تعقيم التربة في الحالات الشديدة.",
    },
    58: {  # Cotton Bacterial Blight
        "en": "Use acid-delinted treated seed. Apply copper hydroxide at first symptoms. Plant resistant varieties. Avoid working in wet fields. Destroy crop residues after harvest.",
        "ar": "استخدم بذورًا منزوعة الزغب ومعالجة. طبق هيدروكسيد النحاس عند أول الأعراض. ازرع أصنافًا مقاومة. تجنب العمل في الحقول الرطبة. دمر بقايا المحصول بعد الحصاد.",
    },
    59: {  # Cotton Boll Rot
        "en": "Ensure proper plant spacing for air circulation. Apply copper-based fungicide. Avoid late-season irrigation. Control bollworm which creates entry wounds. Pick bolls promptly.",
        "ar": "تأكد من التباعد المناسب بين النباتات لدوران الهواء. طبق مبيدًا فطريًا نحاسيًا. تجنب الري المتأخر في الموسم. كافح دودة اللوز التي تسبب جروح الدخول. اجنِ اللوز فورًا.",
    },
    60: {  # Cotton Alternaria Leaf Spot
        "en": "Apply mancozeb or chlorothalonil fungicide. Maintain balanced fertilization. Remove infected leaves. Rotate crops. Use resistant varieties where available.",
        "ar": "طبق مبيد مانكوزيب أو كلوروثالونيل. حافظ على التسميد المتوازن. أزل الأوراق المصابة. قم بالدورة الزراعية. استخدم أصنافًا مقاومة حيث تتوفر.",
    },
    # --- Peanut (الفول السوداني) ---
    61: {  # Peanut Early Leaf Spot
        "en": "Apply chlorothalonil or tebuconazole at 30-35 days after planting. Rotate with cereals for 2+ years. Use resistant varieties. Maintain proper plant spacing.",
        "ar": "طبق كلوروثالونيل أو تيبوكونازول بعد 30-35 يومًا من الزراعة. قم بالدورة مع الحبوب لأكثر من سنتين. استخدم أصنافًا مقاومة. حافظ على التباعد المناسب.",
    },
    62: {  # Peanut Late Leaf Spot
        "en": "Apply mancozeb or propiconazole at first symptoms. Remove crop debris after harvest. Avoid planting in previously infected fields. Use certified disease-free seed.",
        "ar": "طبق مانكوزيب أو بروبيكونازول عند أول الأعراض. أزل بقايا المحصول بعد الحصاد. تجنب الزراعة في الحقول المصابة سابقًا. استخدم بذورًا معتمدة خالية من المرض.",
    },
    63: {  # Peanut Rust
        "en": "Apply triazole fungicide (hexaconazole or propiconazole) at first appearance. Scout regularly from 50 days after planting. Use early-maturing resistant varieties.",
        "ar": "طبق مبيدًا فطريًا تريازول (هيكساكونازول أو بروبيكونازول) عند أول ظهور. تفقد بانتظام من 50 يومًا بعد الزراعة. استخدم أصنافًا مقاومة مبكرة النضج.",
    },
    64: {  # Peanut Stem Rot
        "en": "Treat seed with carboxin + thiram before planting. Apply Trichoderma viride as biocontrol. Deep plowing to bury sclerotia. Avoid excess moisture at soil level.",
        "ar": "عالج البذور بالكاربوكسين + ثيرام قبل الزراعة. طبق تريكوديرما كمكافحة حيوية. احرث عميقًا لدفن الأجسام الحجرية. تجنب الرطوبة الزائدة عند مستوى التربة.",
    },
    65: {  # Peanut Aspergillus Crown Rot
        "en": "Treat seed with mancozeb or thiram. Ensure proper drainage. Avoid injury to crown area during weeding. Maintain soil calcium levels. Apply gypsum at pegging.",
        "ar": "عالج البذور بالمانكوزيب أو ثيرام. تأكد من الصرف الجيد. تجنب إصابة منطقة التاج أثناء التعشيب. حافظ على مستويات الكالسيوم في التربة. طبق الجبس عند التوتيد.",
    },
}


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/detect/pest",
    response_model=PestDetectionResponse,
    summary="Detect pests in agricultural images",
    description="Detect and classify agricultural pests (20+ species) with bilingual labels and treatment recommendations.",
)
async def detect_pests(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    return_visualization: bool = False,
    include_recommendations: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> PestDetectionResponse:
    """
    Detect pests in agricultural images.

    Supports detection of 20+ pest species including:
    - Red Palm Weevil (سوسة النخيل الحمراء)
    - Aphids (المن)
    - Whitefly (الذبابة البيضاء)
    - Spider Mites (العنكبوت الأحمر)
    - Thrips (التربس)
    - And many more...

    Returns bilingual (Arabic/English) class names, severity levels,
    and optional treatment recommendations.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "pest_detection_request",
        request_id=str(request_id),
        filename=file.filename,
        model_variant=model_variant.value,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Ensure image size is multiple of 32
        if image_size % 32 != 0:
            image_size = (image_size // 32 + 1) * 32

        # Run inference
        result: InferenceResult = await manager.predict(
            task=ModelTask.PEST_DETECTION,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=iou_threshold,
            max_det=max_detections,
            imgsz=image_size,
        )

        # Process detections
        detections: list[PestDetection] = []
        severity_counts: dict[str, int] = {s.value: 0 for s in SeverityLevel}
        visualization_data = []

        for i in range(result.count):
            class_id = int(result.class_ids[i])
            confidence = float(result.scores[i])
            box = result.boxes[i]

            # Get bilingual label
            label = PEST_CLASSES.get(class_id, BilingualLabel(en="Unknown Pest", ar="آفة غير معروفة"))

            # Calculate severity
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            image_area = image_metadata.width * image_metadata.height
            area_ratio = box_area / image_area if image_area > 0 else 0
            severity = calculate_severity(confidence, area_ratio)
            severity_counts[severity.value] += 1

            # Get recommendations
            rec = PEST_RECOMMENDATIONS.get(class_id, {})

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            detection = PestDetection(
                class_id=class_id,
                class_name_en=label.en,
                class_name_ar=label.ar,
                scientific_name=label.scientific_name,
                confidence=confidence,
                bbox=bbox,
                severity=severity,
                life_stage=None,  # Would require additional model
                recommended_action_en=rec.get("en") if include_recommendations else None,
                recommended_action_ar=rec.get("ar") if include_recommendations else None,
            )
            detections.append(detection)

            visualization_data.append(
                {
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
                    "severity": severity,
                }
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Generate visualization if requested
        visualization_base64 = None
        if return_visualization and detections:
            visualization_base64 = create_visualization(image_bytes, visualization_data, PEST_CLASSES)

        logger.info(
            "pest_detection_complete",
            request_id=str(request_id),
            detections=len(detections),
            processing_time_ms=round(processing_time, 2),
        )

        # Publish NATS event
        publisher = _get_event_publisher(request)
        if publisher and detections:
            await publisher.publish_pest_detected(
                request_id=request_id,
                detections=[
                    {
                        "class_id": d.class_id,
                        "class_name_en": d.class_name_en,
                        "class_name_ar": d.class_name_ar,
                        "confidence": d.confidence,
                        "severity": d.severity.value if d.severity else None,
                        "bbox": {"x1": d.bbox.x1, "y1": d.bbox.y1, "x2": d.bbox.x2, "y2": d.bbox.y2},
                    }
                    for d in detections
                ],
                processing_time_ms=processing_time,
                model_variant=model_variant.value,
            )

        return PestDetectionResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            detections=detections,
            total_count=len(detections),
            severity_summary=severity_counts,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("pest_detection_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف",
            },
        )


@router.post(
    "/detect/disease",
    response_model=DiseaseDetectionResponse,
    summary="Detect plant diseases in agricultural images",
    description="Detect and classify plant diseases (30+ diseases) with bilingual labels and treatment recommendations.",
)
async def detect_diseases(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    return_visualization: bool = False,
    include_treatments: bool = True,
    calculate_affected_area: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> DiseaseDetectionResponse:
    """
    Detect plant diseases in agricultural images.

    Supports detection of 30+ diseases including:
    - Wheat Rust (صدأ القمح)
    - Powdery Mildew (البياض الدقيقي)
    - Early/Late Blight (اللفحة المبكرة/المتأخرة)
    - Fusarium Wilt (ذبول الفيوزاريوم)
    - Mosaic Virus (فيروس الموزاييك)
    - Date Palm Bayoud (مرض البيوض)
    - And many more...

    Returns bilingual (Arabic/English) class names, severity levels,
    affected area estimation, and optional treatment recommendations.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "disease_detection_request",
        request_id=str(request_id),
        filename=file.filename,
        model_variant=model_variant.value,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Ensure image size is multiple of 32
        if image_size % 32 != 0:
            image_size = (image_size // 32 + 1) * 32

        # Run inference
        result: InferenceResult = await manager.predict(
            task=ModelTask.DISEASE_DETECTION,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=iou_threshold,
            max_det=max_detections,
            imgsz=image_size,
        )

        # Process detections
        detections: list[DiseaseDetection] = []
        severity_counts: dict[str, int] = {s.value: 0 for s in SeverityLevel}
        total_affected_area = 0.0
        visualization_data = []

        image_area = image_metadata.width * image_metadata.height

        for i in range(result.count):
            class_id = int(result.class_ids[i])
            confidence = float(result.scores[i])
            box = result.boxes[i]

            # Get bilingual label
            label = DISEASE_CLASSES.get(class_id, BilingualLabel(en="Unknown Disease", ar="مرض غير معروف"))

            # Calculate affected area
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            area_percent = (box_area / image_area * 100) if image_area > 0 and calculate_affected_area else None
            if area_percent:
                total_affected_area += area_percent

            # Calculate severity
            area_ratio = box_area / image_area if image_area > 0 else 0
            severity = calculate_severity(confidence, area_ratio)
            severity_counts[severity.value] += 1

            # Estimate spread risk based on disease type and severity
            spread_risk = severity
            # Late Blight, Mosaic Virus, YLCV, Maize Streak Virus, Wheat Yellow Rust,
            # Potato Virus Y, Citrus Tristeza, Soybean Rust, Cotton Leaf Curl Virus,
            # Peanut Rust - high spread risk
            if class_id in [4, 12, 13, 37, 38, 42, 44, 52, 56, 63]:
                spread_risk = SeverityLevel.HIGH if severity != SeverityLevel.CRITICAL else SeverityLevel.CRITICAL

            # Get treatment recommendations
            treatment = DISEASE_TREATMENTS.get(class_id, {})

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            detection = DiseaseDetection(
                class_id=class_id,
                class_name_en=label.en,
                class_name_ar=label.ar,
                scientific_name=label.scientific_name,
                confidence=confidence,
                bbox=bbox,
                severity=severity,
                affected_area_percent=area_percent,
                spread_risk=spread_risk,
                recommended_treatment_en=treatment.get("en") if include_treatments else None,
                recommended_treatment_ar=treatment.get("ar") if include_treatments else None,
            )
            detections.append(detection)

            visualization_data.append(
                {
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
                    "severity": severity,
                }
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Calculate overall health score (100 = healthy, 0 = severely diseased)
        health_score = max(0.0, 100.0 - total_affected_area)
        if len(detections) > 0:
            avg_severity = sum(
                [
                    1
                    if d.severity == SeverityLevel.LOW
                    else 2
                    if d.severity == SeverityLevel.MEDIUM
                    else 3
                    if d.severity == SeverityLevel.HIGH
                    else 4
                    if d.severity == SeverityLevel.CRITICAL
                    else 0
                    for d in detections
                ]
            ) / len(detections)
            health_score = max(0.0, health_score - (avg_severity * 10))

        # Generate visualization if requested
        visualization_base64 = None
        if return_visualization and detections:
            visualization_base64 = create_visualization(image_bytes, visualization_data, DISEASE_CLASSES)

        logger.info(
            "disease_detection_complete",
            request_id=str(request_id),
            detections=len(detections),
            health_score=round(health_score, 1),
            processing_time_ms=round(processing_time, 2),
        )

        # Publish NATS event
        publisher = _get_event_publisher(request)
        if publisher and detections:
            await publisher.publish_disease_detected(
                request_id=request_id,
                detections=[
                    {
                        "class_id": d.class_id,
                        "class_name_en": d.class_name_en,
                        "class_name_ar": d.class_name_ar,
                        "confidence": d.confidence,
                        "severity": d.severity.value if d.severity else None,
                        "affected_area_percent": d.affected_area_percent,
                        "spread_risk": d.spread_risk.value if d.spread_risk else None,
                        "bbox": {"x1": d.bbox.x1, "y1": d.bbox.y1, "x2": d.bbox.x2, "y2": d.bbox.y2},
                    }
                    for d in detections
                ],
                processing_time_ms=processing_time,
                model_variant=model_variant.value,
                health_score=health_score,
            )

        return DiseaseDetectionResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            detections=detections,
            total_count=len(detections),
            overall_health_score=round(health_score, 1),
            severity_summary=severity_counts,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("disease_detection_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف",
            },
        )


@router.post(
    "/detect/weed",
    response_model=WeedDetectionResponse,
    summary="Detect weeds in agricultural images",
    description="Detect and classify weeds with bilingual labels and coverage estimation.",
)
async def detect_weeds(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    return_visualization: bool = False,
    calculate_coverage: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> WeedDetectionResponse:
    """
    Detect weeds in agricultural images.

    Supports detection of common agricultural weeds including:
    - Wild Oat (الشوفان البري)
    - Bermuda Grass (النجيل)
    - Johnson Grass (حشيشة جونسون)
    - Pigweed (عرف الديك)
    - Bindweed (العليق)
    - And more...

    Returns bilingual (Arabic/English) class names, coverage percentage,
    and species distribution.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "weed_detection_request",
        request_id=str(request_id),
        filename=file.filename,
        model_variant=model_variant.value,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Ensure image size is multiple of 32
        if image_size % 32 != 0:
            image_size = (image_size // 32 + 1) * 32

        # Run inference
        result: InferenceResult = await manager.predict(
            task=ModelTask.WEED_DETECTION,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=iou_threshold,
            max_det=max_detections,
            imgsz=image_size,
        )

        # Process detections
        detections: list[WeedDetection] = []
        species_distribution: dict[str, int] = {}
        total_coverage = 0.0
        visualization_data = []

        image_area = image_metadata.width * image_metadata.height

        for i in range(result.count):
            class_id = int(result.class_ids[i])
            confidence = float(result.scores[i])
            box = result.boxes[i]

            # Get bilingual label
            label = WEED_CLASSES.get(class_id, BilingualLabel(en="Unknown Weed", ar="عشبة غير معروفة"))

            # Update species distribution
            species_distribution[label.en] = species_distribution.get(label.en, 0) + 1

            # Calculate coverage
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            coverage_percent = (box_area / image_area * 100) if image_area > 0 and calculate_coverage else None
            if coverage_percent:
                total_coverage += coverage_percent

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            detection = WeedDetection(
                class_id=class_id,
                class_name_en=label.en,
                class_name_ar=label.ar,
                scientific_name=label.scientific_name,
                confidence=confidence,
                bbox=bbox,
                coverage_percent=coverage_percent,
                growth_stage=None,  # Would require additional model
            )
            detections.append(detection)

            visualization_data.append(
                {
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
                    "severity": SeverityLevel.MEDIUM,  # Default for visualization
                }
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Cap total coverage at 100%
        total_coverage = min(total_coverage, 100.0)

        # Generate visualization if requested
        visualization_base64 = None
        if return_visualization and detections:
            visualization_base64 = create_visualization(image_bytes, visualization_data, WEED_CLASSES)

        logger.info(
            "weed_detection_complete",
            request_id=str(request_id),
            detections=len(detections),
            total_coverage=round(total_coverage, 1),
            processing_time_ms=round(processing_time, 2),
        )

        # Publish NATS event
        publisher = _get_event_publisher(request)
        if publisher and detections:
            await publisher.publish_weed_detected(
                request_id=request_id,
                detections=[
                    {
                        "class_id": d.class_id,
                        "class_name_en": d.class_name_en,
                        "class_name_ar": d.class_name_ar,
                        "confidence": d.confidence,
                        "coverage_percent": d.coverage_percent,
                        "bbox": {"x1": d.bbox.x1, "y1": d.bbox.y1, "x2": d.bbox.x2, "y2": d.bbox.y2},
                    }
                    for d in detections
                ],
                processing_time_ms=processing_time,
                model_variant=model_variant.value,
                total_coverage_percent=total_coverage,
            )

        return WeedDetectionResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            detections=detections,
            total_count=len(detections),
            total_coverage_percent=round(total_coverage, 1),
            species_distribution=species_distribution,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("weed_detection_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف",
            },
        )

"""
Pest Detection API
واجهة برمجة كشف الآفات

Endpoints for pest identification, database queries, and AI detection.
"""

import json
from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Optional
from uuid import uuid4

import httpx
import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, Field

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    _bearer_scheme = HTTPBearer(auto_error=False)
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# Enums
# ============================================================================


class PestCategory(StrEnum):
    """Pest categories."""

    INSECT = "insect"
    MITE = "mite"
    NEMATODE = "nematode"
    RODENT = "rodent"
    BIRD = "bird"
    MOLLUSK = "mollusk"


class SeverityLevel(StrEnum):
    """Infestation severity levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LifeStage(StrEnum):
    """Pest life stages."""

    EGG = "egg"
    LARVA = "larva"
    PUPA = "pupa"
    NYMPH = "nymph"
    ADULT = "adult"


# ============================================================================
# ML Feature Schema for pest detection pipeline
# ============================================================================

feature_schema = {
    "detection_output": {
        "confidence": {"type": "float", "range": [0, 1], "description": "Detection confidence score"},
        "severity": {"type": "enum", "values": ["none", "low", "medium", "high", "critical"]},
        "life_stage": {"type": "enum", "values": ["egg", "larva", "pupa", "nymph", "adult"]},
        "bounding_box": {"type": "dict", "keys": ["x", "y", "width", "height"]},
    },
    "input_features": {
        "image_size": {"type": "int", "range": [64, 4096], "description": "Input image dimension"},
        "crop_type": {"type": "str", "description": "Target crop for detection context"},
        "region": {"type": "str", "description": "Geographic region for pest filtering"},
    },
}


# ============================================================================
# Models
# ============================================================================


class Pest(BaseModel):
    """Pest information model."""

    id: str
    name_en: str = Field(..., description="English name")
    name_ar: str = Field(..., description="Arabic name")
    scientific_name: str
    category: PestCategory
    description_en: str
    description_ar: str
    affected_crops: list[str]
    symptoms_en: list[str]
    symptoms_ar: list[str]
    is_quarantine: bool = False
    image_url: str | None = None


class DetectionResult(BaseModel):
    """AI pest detection result."""

    pest_id: str
    pest_name_en: str
    pest_name_ar: str
    confidence: float = Field(..., ge=0, le=1)
    severity: SeverityLevel
    life_stage: LifeStage | None = None
    bounding_box: dict | None = None
    recommendations_en: list[str]
    recommendations_ar: list[str]


class IdentifyRequest(BaseModel):
    """Request for symptom-based identification."""

    crop: str = Field(..., min_length=1, max_length=100, description="Crop type for pest context")
    symptoms: list[str] = Field(..., min_length=1, max_length=20, description="Observed symptoms")
    region: str | None = Field("middle_east", max_length=50, description="Geographic region")


# ============================================================================
# Pest Database (In-memory for demo, would be PostgreSQL in production)
# ============================================================================

PEST_DATABASE: dict[str, Pest] = {
    "rpw": Pest(
        id="rpw",
        name_en="Red Palm Weevil",
        name_ar="سوسة النخيل الحمراء",
        scientific_name="Rhynchophorus ferrugineus",
        category=PestCategory.INSECT,
        description_en="Most destructive pest of palm trees. Adults are reddish-brown, 2-5cm long.",
        description_ar="أخطر آفة تصيب أشجار النخيل. الحشرة البالغة بنية محمرة بطول 2-5 سم.",
        affected_crops=["date_palm", "coconut_palm", "oil_palm"],
        symptoms_en=[
            "Yellowing and wilting of fronds",
            "Holes in trunk with oozing sap",
            "Fermented odor from trunk",
            "Presence of cocoons at leaf bases",
        ],
        symptoms_ar=[
            "اصفرار وذبول السعف",
            "ثقوب في الجذع مع تسرب النسغ",
            "رائحة تخمر من الجذع",
            "وجود شرانق عند قواعد الأوراق",
        ],
        is_quarantine=True,
    ),
    "dubas": Pest(
        id="dubas",
        name_en="Dubas Bug",
        name_ar="دوباس النخيل",
        scientific_name="Ommatissus lybicus",
        category=PestCategory.INSECT,
        description_en="Sap-sucking pest of date palms. Secretes honeydew causing sooty mold.",
        description_ar="آفة ماصة للعصارة تصيب النخيل. تفرز ندوة عسلية تسبب العفن الأسود.",
        affected_crops=["date_palm"],
        symptoms_en=[
            "Honeydew secretion on fronds",
            "Sooty mold on leaves and fruits",
            "Yellowing of leaflets",
            "Reduced fruit quality",
        ],
        symptoms_ar=[
            "إفراز ندوة عسلية على السعف",
            "عفن أسود على الأوراق والثمار",
            "اصفرار الوريقات",
            "انخفاض جودة الثمار",
        ],
        is_quarantine=False,
    ),
    "aphids": Pest(
        id="aphids",
        name_en="Aphids",
        name_ar="المن",
        scientific_name="Aphididae family",
        category=PestCategory.INSECT,
        description_en="Small soft-bodied insects that suck plant sap. Often found in colonies.",
        description_ar="حشرات صغيرة رخوة الجسم تمتص عصارة النبات. توجد غالباً في مستعمرات.",
        affected_crops=["wheat", "barley", "vegetables", "fruits"],
        symptoms_en=[
            "Curled or distorted leaves",
            "Sticky honeydew on leaves",
            "Presence of ants (farming aphids)",
            "Yellowing and stunted growth",
        ],
        symptoms_ar=[
            "تجعد أو تشوه الأوراق",
            "ندوة عسلية لزجة على الأوراق",
            "وجود النمل (يرعى المن)",
            "اصفرار وتقزم النمو",
        ],
        is_quarantine=False,
    ),
    "whitefly": Pest(
        id="whitefly",
        name_en="Whitefly",
        name_ar="الذبابة البيضاء",
        scientific_name="Bemisia tabaci",
        category=PestCategory.INSECT,
        description_en="Tiny white flying insects. Major vector for plant viruses.",
        description_ar="حشرات طائرة بيضاء صغيرة. ناقل رئيسي للفيروسات النباتية.",
        affected_crops=["tomato", "cucumber", "pepper", "cotton"],
        symptoms_en=[
            "White insects on leaf undersides",
            "Yellowing leaves",
            "Honeydew and sooty mold",
            "Virus symptoms (leaf curl, mosaic)",
        ],
        symptoms_ar=[
            "حشرات بيضاء أسفل الأوراق",
            "اصفرار الأوراق",
            "ندوة عسلية وعفن أسود",
            "أعراض فيروسية (تجعد، موزاييك)",
        ],
        is_quarantine=False,
    ),
    "spider_mite": Pest(
        id="spider_mite",
        name_en="Spider Mite",
        name_ar="العنكبوت الأحمر",
        scientific_name="Tetranychus urticae",
        category=PestCategory.MITE,
        description_en="Tiny mites that feed on plant cells. Thrive in hot, dry conditions.",
        description_ar="عث صغير يتغذى على خلايا النبات. ينتشر في الظروف الحارة والجافة.",
        affected_crops=["cucumber", "tomato", "strawberry", "citrus"],
        symptoms_en=[
            "Fine webbing on leaves",
            "Stippled or bronzed leaves",
            "Leaf drop in severe cases",
            "Tiny moving dots on leaf undersides",
        ],
        symptoms_ar=[
            "خيوط عنكبوتية دقيقة على الأوراق",
            "نقاط أو لون برونزي على الأوراق",
            "سقوط الأوراق في الحالات الشديدة",
            "نقاط صغيرة متحركة أسفل الأوراق",
        ],
        is_quarantine=False,
    ),
    "locust": Pest(
        id="locust",
        name_en="Desert Locust",
        name_ar="الجراد الصحراوي",
        scientific_name="Schistocerca gregaria",
        category=PestCategory.INSECT,
        description_en="Highly destructive migratory pest. Swarms can devastate crops.",
        description_ar="آفة مهاجرة شديدة التدمير. الأسراب يمكن أن تدمر المحاصيل.",
        affected_crops=["wheat", "barley", "vegetables", "fruits", "pastures"],
        symptoms_en=[
            "Complete defoliation",
            "Swarm sightings",
            "Stripped plants",
            "Damage to bark and fruits",
        ],
        symptoms_ar=[
            "تعرية كاملة للأوراق",
            "مشاهدة أسراب",
            "نباتات مجردة",
            "تلف اللحاء والثمار",
        ],
        is_quarantine=True,
    ),
    "tuta": Pest(
        id="tuta",
        name_en="Tomato Leafminer",
        name_ar="حافرة أنفاق الطماطم",
        scientific_name="Tuta absoluta",
        category=PestCategory.INSECT,
        description_en="Devastating pest of tomatoes. Larvae mine leaves and fruits.",
        description_ar="آفة مدمرة للطماطم. اليرقات تحفر أنفاقاً في الأوراق والثمار.",
        affected_crops=["tomato", "potato", "eggplant", "pepper"],
        symptoms_en=[
            "Irregular mines in leaves",
            "Holes in fruits",
            "Wilting of terminal shoots",
            "Galleries in stems",
        ],
        symptoms_ar=[
            "أنفاق غير منتظمة في الأوراق",
            "ثقوب في الثمار",
            "ذبول القمم النامية",
            "أنفاق في السيقان",
        ],
        is_quarantine=True,
    ),
    "thrips": Pest(
        id="thrips",
        name_en="Thrips",
        name_ar="التربس",
        scientific_name="Thysanoptera order",
        category=PestCategory.INSECT,
        description_en="Tiny slender insects. Damage flowers and transmit viruses.",
        description_ar="حشرات صغيرة نحيلة. تتلف الأزهار وتنقل الفيروسات.",
        affected_crops=["onion", "pepper", "cucumber", "flowers"],
        symptoms_en=[
            "Silvery streaks on leaves",
            "Distorted flowers",
            "Scarred fruits",
            "Virus symptoms",
        ],
        symptoms_ar=[
            "خطوط فضية على الأوراق",
            "تشوه الأزهار",
            "ندبات على الثمار",
            "أعراض فيروسية",
        ],
        is_quarantine=False,
    ),
    "fruit_fly": Pest(
        id="fruit_fly",
        name_en="Mediterranean Fruit Fly",
        name_ar="ذبابة الفاكهة",
        scientific_name="Ceratitis capitata",
        category=PestCategory.INSECT,
        description_en="Major pest of fruits. Larvae develop inside fruits.",
        description_ar="آفة رئيسية للفواكه. اليرقات تتطور داخل الثمار.",
        affected_crops=["citrus", "peach", "apple", "mango", "fig"],
        symptoms_en=[
            "Sting marks on fruits",
            "Premature fruit drop",
            "Larvae inside fruits",
            "Rotting fruits",
        ],
        symptoms_ar=[
            "علامات وخز على الثمار",
            "سقوط الثمار المبكر",
            "يرقات داخل الثمار",
            "تعفن الثمار",
        ],
        is_quarantine=True,
    ),
    "date_moth": Pest(
        id="date_moth",
        name_en="Date Moth",
        name_ar="فراشة التمر",
        scientific_name="Ephestia cautella",
        category=PestCategory.INSECT,
        description_en="Pest of stored dates. Larvae feed on fruits in storage.",
        description_ar="آفة التمور المخزنة. اليرقات تتغذى على الثمار في المخازن.",
        affected_crops=["date_palm"],
        symptoms_en=[
            "Webbing on stored dates",
            "Frass (insect waste) in dates",
            "Larvae in fruits",
            "Damaged fruit texture",
        ],
        symptoms_ar=[
            "خيوط على التمور المخزنة",
            "فضلات الحشرات في التمور",
            "يرقات في الثمار",
            "تلف قوام الثمار",
        ],
        is_quarantine=False,
    ),
}


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/pests", response_model=list[Pest])
async def list_pests(
    category: PestCategory | None = None,
    crop: str | None = None,
    quarantine_only: bool = False,
    _user=Depends(get_current_user),
):
    """
    List all pests in database.
    قائمة جميع الآفات في قاعدة البيانات.
    """
    pests = list(PEST_DATABASE.values())

    if category:
        pests = [p for p in pests if p.category == category]

    if crop:
        pests = [p for p in pests if crop.lower() in [c.lower() for c in p.affected_crops]]

    if quarantine_only:
        pests = [p for p in pests if p.is_quarantine]

    return pests


@router.get("/pests/search")
async def search_pests(
    q: str = Query(..., min_length=2, description="Search query"),
):
    """
    Search pests by name.
    البحث عن الآفات بالاسم.
    """
    q_lower = q.lower()
    results = []

    for pest in PEST_DATABASE.values():
        if (
            q_lower in pest.name_en.lower()
            or q_lower in pest.name_ar
            or q_lower in pest.scientific_name.lower()
        ):
            results.append(pest)

    return results


@router.get("/pests/crop/{crop}")
async def get_pests_by_crop(crop: str):
    """
    Get pests that affect a specific crop.
    الحصول على الآفات التي تصيب محصولاً معيناً.
    """
    pests = [
        p for p in PEST_DATABASE.values() if crop.lower() in [c.lower() for c in p.affected_crops]
    ]
    return pests


@router.post("/pests/identify", response_model=DetectionResult)
async def identify_pest_from_image(
    request: Request,
    file: UploadFile = File(..., description="Image file (JPG, PNG)"),
):
    """
    Identify pest from image using AI.
    تحديد الآفة من الصورة باستخدام الذكاء الاصطناعي.
    """
    logger.info("pest_identification_request", filename=file.filename)

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read image
    image_data = await file.read()

    # Call vision service
    try:
        vision_client = request.app.state.vision_client
        response = await vision_client.post(
            "/api/v1/detect/pest",
            files={"file": (file.filename, image_data, file.content_type)},
        )

        if response.status_code != 200:
            logger.error("vision_service_error", status=response.status_code)
            raise HTTPException(
                status_code=503,
                detail="Vision service unavailable",
            )

        vision_result = response.json()

        # Enrich with pest database info
        detections = vision_result.get("detections", [])
        if not detections:
            return DetectionResult(
                pest_id="unknown",
                pest_name_en="No pest detected",
                pest_name_ar="لم يتم اكتشاف آفة",
                confidence=0.0,
                severity=SeverityLevel.NONE,
                recommendations_en=["Continue regular monitoring"],
                recommendations_ar=["استمر في المراقبة المنتظمة"],
            )

        # Get top detection
        top = detections[0]
        pest_id = top.get("class_name", "unknown").lower().replace(" ", "_")
        pest_info = PEST_DATABASE.get(pest_id)

        if pest_info:
            result = DetectionResult(
                pest_id=pest_id,
                pest_name_en=pest_info.name_en,
                pest_name_ar=pest_info.name_ar,
                confidence=top.get("confidence", 0.0),
                severity=SeverityLevel(top.get("severity", "medium").lower()),
                life_stage=LifeStage(top["life_stage"]) if top.get("life_stage") else None,
                bounding_box=top.get("bbox"),
                recommendations_en=[
                    "Confirm identification with manual inspection",
                    "Check neighboring plants for spread",
                    "Consult treatment recommendations",
                ],
                recommendations_ar=[
                    "تأكد من التعريف بالفحص اليدوي",
                    "افحص النباتات المجاورة للانتشار",
                    "راجع توصيات العلاج",
                ],
            )
        else:
            result = DetectionResult(
                pest_id=pest_id,
                pest_name_en=top.get("class_name", "Unknown pest"),
                pest_name_ar="آفة غير معروفة",
                confidence=top.get("confidence", 0.0),
                severity=SeverityLevel.MEDIUM,
                recommendations_en=["Manual identification recommended"],
                recommendations_ar=["يُنصح بالتعريف اليدوي"],
            )

        # Publish pest detection event to NATS
        nc = getattr(request.app.state, "nc", None)
        if nc:
            try:
                event_payload = json.dumps({
                    "event_type": "pest_detected",
                    "pest_id": result.pest_id,
                    "pest_name_en": result.pest_name_en,
                    "pest_name_ar": result.pest_name_ar,
                    "confidence": result.confidence,
                    "severity": result.severity.value,
                    "is_quarantine": pest_info.is_quarantine if pest_info else False,
                    "detection_id": str(uuid4()),
                    "source": "pest-detection-service",
                    "timestamp": datetime.now(UTC).isoformat(),
                }, default=str).encode()
                await nc.publish("sahool.health.pest_detected", event_payload)
                logger.info("nats_event_published", subject="sahool.health.pest_detected", pest_id=result.pest_id)
            except Exception as pub_err:
                logger.warning("nats_publish_failed", error=str(pub_err))

        return result

    except httpx.RequestError as e:
        logger.error("vision_service_connection_error", error=str(e))
        raise HTTPException(
            status_code=503,
            detail="Could not connect to vision service",
        )


@router.post("/pests/identify/symptoms")
async def identify_by_symptoms(request_body: IdentifyRequest):
    """
    Identify pest by symptoms.
    تحديد الآفة من خلال الأعراض.
    """
    matches = []

    for pest in PEST_DATABASE.values():
        # Check if crop matches
        if request_body.crop.lower() not in [c.lower() for c in pest.affected_crops]:
            continue

        # Count symptom matches
        symptom_matches = 0
        all_symptoms = pest.symptoms_en + pest.symptoms_ar

        for symptom in request_body.symptoms:
            symptom_lower = symptom.lower()
            for pest_symptom in all_symptoms:
                if symptom_lower in pest_symptom.lower():
                    symptom_matches += 1
                    break

        if symptom_matches > 0:
            confidence = min(symptom_matches / len(request_body.symptoms), 1.0)
            matches.append(
                {
                    "pest": pest,
                    "confidence": confidence,
                    "matched_symptoms": symptom_matches,
                }
            )

    # Sort by confidence
    matches.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "crop": request_body.crop,
        "input_symptoms": request_body.symptoms,
        "matches": matches[:5],  # Top 5 matches
    }


@router.get("/pests/quarantine")
async def list_quarantine_pests():
    """
    List quarantine pests requiring immediate reporting.
    قائمة آفات الحجر الزراعي التي تتطلب إبلاغاً فورياً.
    """
    return [p for p in PEST_DATABASE.values() if p.is_quarantine]


@router.get("/pests/seasonal")
async def get_seasonal_predictions(
    crop: str | None = None,
    month: int | None = Query(None, ge=1, le=12),
):
    """
    Get seasonal pest predictions.
    الحصول على توقعات الآفات الموسمية.
    """
    # Simplified seasonal logic - would use ML model in production
    seasonal_risks = {
        "spring": ["aphids", "thrips", "whitefly"],
        "summer": ["spider_mite", "whitefly", "fruit_fly", "locust"],
        "fall": ["dubas", "date_moth"],
        "winter": ["aphids", "rpw"],
    }

    if month:
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "fall"
        else:
            season = "winter"
    else:
        season = "summer"  # Default

    predicted_pests = [PEST_DATABASE[pid] for pid in seasonal_risks[season] if pid in PEST_DATABASE]

    if crop:
        predicted_pests = [
            p for p in predicted_pests if crop.lower() in [c.lower() for c in p.affected_crops]
        ]

    return {
        "season": season,
        "season_ar": {
            "spring": "الربيع",
            "summer": "الصيف",
            "fall": "الخريف",
            "winter": "الشتاء",
        }[season],
        "predicted_pests": predicted_pests,
        "risk_level": "high" if len(predicted_pests) > 2 else "medium",
    }


@router.get("/pests/{pest_id}", response_model=Pest)
async def get_pest(pest_id: str):
    """
    Get pest details by ID.
    الحصول على تفاصيل الآفة بواسطة المعرف.
    """
    pest = PEST_DATABASE.get(pest_id)
    if not pest:
        raise HTTPException(status_code=404, detail=f"Pest not found: {pest_id}")
    return pest

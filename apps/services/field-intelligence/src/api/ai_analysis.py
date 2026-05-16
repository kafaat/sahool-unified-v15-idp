"""
Field AI Analysis — Multi-Agent Agricultural Intelligence
تحليل الحقول بالذكاء الاصطناعي — وكلاء متعددون متوازيون

Runs three agents in parallel via OpenRouter (OpenAI-compatible API):
  1. مؤشر الغطاء النباتي  — Qwen3.5-122B — يفسر قيم مؤشر CDSE المختار
  2. محلل الطقس          — Qwen3.5-122B — يفسر بيانات OpenWeather + OpenMeteo الحية
  3. التوصيات الزراعية   — Qwen3.5-122B — يُجمّع كل البيانات في توصيات قابلة للتنفيذ

Returns structured bullet-point analysis fully in Arabic.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re

from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

ai_router = APIRouter()

# ── OpenRouter client (lazy, shared) ─────────────────────────────────────────

_openrouter_client: AsyncOpenAI | None = None

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

MODEL_FAST = os.environ.get("OPENROUTER_MODEL_FAST", "qwen/qwen3.5-122b-a10b")
MODEL_PRIMARY = os.environ.get("OPENROUTER_MODEL_PRIMARY", "qwen/qwen3.5-122b-a10b")


def _get_client() -> AsyncOpenAI:
    global _openrouter_client
    if _openrouter_client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set in environment")
        _openrouter_client = AsyncOpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://sahool.app",
                "X-Title": "SAHOOL Field Intelligence",
            },
        )
    return _openrouter_client


# ── Request / Response schemas ────────────────────────────────────────────────


class CdseStats(BaseModel):
    indice: str
    value: float | None = None
    minValue: float | None = None
    maxValue: float | None = None
    stdDev: float | None = None
    date: str = ""
    cloudCover: float | None = None


class WeatherData(BaseModel):
    temperature: float | None = None
    feelsLike: float | None = None
    humidity: float | None = None
    windSpeed: float | None = None
    windDirection: float | None = None
    precipitation: float | None = None
    description: str = ""
    pressure: float | None = None
    cloudCover: float | None = None
    visibility: float | None = None


class MeteoData(BaseModel):
    temperature2m: float | None = None
    relativeHumidity2m: float | None = None
    precipitation: float | None = None
    windSpeed10m: float | None = None
    soilMoisture0to1cm: float | None = None
    et0FaoEvapotranspiration: float | None = None
    surfacePressure: float | None = None
    cloudCover: float | None = None
    shortwaveRadiation: float | None = None


class FieldInfo(BaseModel):
    id: str
    name: str
    nameAr: str | None = None
    lat: float
    lng: float
    areaHa: float | None = None
    cropType: str | None = None
    soilType: str | None = None


class AnalyzeFieldRequest(BaseModel):
    field: FieldInfo
    cdse: CdseStats
    weather: WeatherData | None = None
    meteo: MeteoData | None = None
    indice: str = "NDVI"
    fetchedAt: str = ""


class AnalyzeFieldResponse(BaseModel):
    field_id: str
    indice: str
    current_status: list[str] = Field(description="Bullet-point current field status in Arabic")
    recommendations: list[str] = Field(description="Bullet-point actionable recommendations in Arabic")
    analyzed_at: str


# ── Agricultural specialist persona ──────────────────────────────────────────

SYSTEM_PERSONA = """أنت الدكتور خالد الرشيدي، متخصص زراعي أول بخبرة 25 عامًا في الزراعة الدقيقة والاستشعار عن بُعد وإدارة المحاصيل في منطقة الشرق الأوسط وشمال أفريقيا. حصلت على الدكتوراه في علم الزراعة من جامعة العلوم والتكنولوجيا الأردنية، وعملت مع المزارعين في اليمن والسعودية ومصر والأردن.

━━ مجالات خبرتك ━━

▸ مؤشرات الاستشعار عن بُعد وتفسيرها الزراعي:
  • NDVI  (مؤشر الغطاء النباتي)          — صحة النبات العامة، الكثافة الخضرية
  • EVI   (مؤشر الغطاء المُحسَّن)        — دقة أعلى في المناطق الكثيفة
  • NDWI  (مؤشر محتوى الماء)             — محتوى الماء في النبات والغطاء المائي
  • NDMI  (مؤشر رطوبة النبات)            — إجهاد مائي في الأوراق والسيقان
  • SAVI  (مؤشر النبات مع تعديل التربة)  — مناسب للمناطق متفرقة النبات
  • NDRE  (مؤشر الحافة الحمراء)          — محتوى الكلوروفيل والنيتروجين
  • NBR   (نسبة الحرق المُعيَّرة)         — تقييم الحرائق والتلف
  • BSI   (مؤشر التربة العارية)           — الكشف عن التعرية وانكشاف التربة
  • MSAVI (مؤشر النبات المُعدَّل للتربة) — تحسين دقة المناطق الجافة
  • GNDVI (مؤشر الغطاء الأخضر)          — كثافة الكلوروفيل، نقص النيتروجين
  • LAI   (مؤشر مساحة الأوراق)          — كثافة الغطاء وكفاءة الضوء

▸ الكشف عن إجهاد المحاصيل: إجهاد مائي، نقص غذائي، آفات وأمراض، ملوحة، شيخوخة
▸ تفاعل الطقس مع المحاصيل: التبخر-النتح، الإجهاد الحراري، الصقيع، كفاءة الأمطار
▸ ديناميكيات رطوبة التربة وجدولة الري وكفاءة استخدام المياه
▸ الزراعة الذكية مناخيًا في المناطق الجافة وشبه الجافة

━━ قواعد الرد ━━
• **جميع إجاباتك باللغة العربية حصرًا — لا تكتب أي كلمة أو جملة بالإنجليزية في متن ردودك**
• اذكر الأرقام والقيم الكمية دائمًا مع وحداتها
• صنِّف الحالات بمستويات الخطورة: حرج / مجهد / متوسط / صحي / ممتاز
• أبرز المخاطر الحرجة بوضوح واقترح إجراءات فورية"""


# ── Prompt helpers ────────────────────────────────────────────────────────────

# Arabic names for each index — shown in prompts for clarity
_INDICE_AR: dict[str, str] = {
    "NDVI":  "مؤشر الغطاء النباتي الطبيعي (NDVI)",
    "EVI":   "مؤشر الغطاء النباتي المُحسَّن (EVI)",
    "NDWI":  "مؤشر محتوى الماء في النبات (NDWI)",
    "NDMI":  "مؤشر رطوبة النبات (NDMI)",
    "SAVI":  "مؤشر الغطاء مع تعديل التربة (SAVI)",
    "NDRE":  "مؤشر الحافة الحمراء للكلوروفيل (NDRE)",
    "NBR":   "نسبة الحرق المُعيَّرة (NBR)",
    "BSI":   "مؤشر التربة العارية (BSI)",
    "MSAVI": "مؤشر النبات المُعدَّل للتربة (MSAVI)",
    "GNDVI": "مؤشر الغطاء النباتي الأخضر (GNDVI)",
    "LAI":   "مؤشر مساحة الأوراق (LAI)",
}


def _indice_ar(indice: str) -> str:
    return _INDICE_AR.get(indice.upper(), f"مؤشر {indice}")


def _build_vegetation_prompt(req: AnalyzeFieldRequest) -> str:
    cdse = req.cdse
    field = req.field
    indice_label = _indice_ar(req.indice)
    val_str = f"{cdse.value:.4f}" if cdse.value is not None else "غير متوفر"
    range_str = (
        f" (الحد الأدنى={cdse.minValue:.4f}، الحد الأقصى={cdse.maxValue:.4f}، الانحراف المعياري σ={cdse.stdDev:.4f})"
        if cdse.value is not None and cdse.minValue is not None
        else ""
    )

    return f"""<مهمة>
أنت الدكتور خالد الرشيدي. حلّل بيانات المؤشر الساتلي للحقل الزراعي التالي وأنتج تقريرًا موجزًا عن حالة الغطاء النباتي.

<بيانات_الحقل>
اسم الحقل : {field.nameAr or field.name}
الموقع    : {field.lat:.4f}° شمالًا، {field.lng:.4f}° شرقًا
المساحة   : {field.areaHa or 'غير محدد'} هكتار
نوع المحصول: {field.cropType or 'غير محدد'}
نوع التربة : {field.soilType or 'غير محدد'}
</بيانات_الحقل>

<بيانات_المؤشر_الساتلي>
المؤشر المحدد  : {indice_label}
القيمة المتوسطة: {val_str}{range_str}
تاريخ الصورة  : {cdse.date or 'غير محدد'}
الغطاء السحابي: {f"{cdse.cloudCover:.1f}%" if cdse.cloudCover is not None else "غير محدد"}
</بيانات_المؤشر_الساتلي>

أنتج بالضبط 4–6 نقاط موجزة باللغة العربية تتناول:
١. ماذا تعني قيمة {indice_label} ({val_str}) زراعيًا لهذا الحقل الآن
٢. تصنيف صحة النبات (حرج / مجهد / متوسط / صحي / ممتاز) مع المبرر الكمي
٣. إشارات الإجهاد أو الشذوذات المكتشفة (مائية، غذائية، أمراض، شيخوخة)
٤. تحليل التباين المكاني من نطاق الحد الأدنى/الأقصى إن توفر
٥. مستوى الثقة في التقييم مع مراعاة الغطاء السحابي وعمر البيانات

التنسيق: نقاط تبدأ بـ "•". أرقام ووحدات دائمًا. بدون عناوين. باللغة العربية حصرًا. الحد الأقصى 120 كلمة لكل نقطة.
</مهمة>"""


def _build_weather_prompt(req: AnalyzeFieldRequest) -> str:
    w = req.weather
    m = req.meteo
    field = req.field
    indice_label = _indice_ar(req.indice)

    weather_block = ""
    if w:
        weather_block = f"""
بيانات OpenWeather (الآن):
  درجة الحرارة    : {w.temperature}°م (تبدو كـ {w.feelsLike}°م)
  الرطوبة النسبية : {w.humidity}%
  سرعة الرياح    : {w.windSpeed} م/ث باتجاه {w.windDirection}°
  هطول الأمطار   : {w.precipitation} مم (الساعة الأخيرة)
  الغطاء السحابي : {w.cloudCover}%
  الضغط الجوي    : {w.pressure} هكتوباسكال
  مدى الرؤية     : {w.visibility} كم
  الحالة الجوية  : {w.description}"""

    meteo_block = ""
    if m:
        meteo_block = f"""
بيانات OpenMeteo (الآن):
  درجة الحرارة (2م)        : {m.temperature2m}°م
  الرطوبة النسبية (2م)      : {m.relativeHumidity2m}%
  هطول الأمطار              : {m.precipitation} مم
  سرعة الرياح (10م)         : {m.windSpeed10m} م/ث
  رطوبة التربة (0–1 سم)     : {m.soilMoisture0to1cm} م³/م³
  التبخر-النتح ET₀ (FAO-56) : {m.et0FaoEvapotranspiration} مم/يوم
  ضغط السطح                 : {m.surfacePressure} هكتوباسكال
  الغطاء السحابي             : {m.cloudCover}%
  الإشعاع الشمسي القصير     : {m.shortwaveRadiation} واط/م²"""

    return f"""<مهمة>
أنت الدكتور خالد الرشيدي. حلّل الظروف الجوية والأرصاد الزراعية الحالية للحقل التالي (بيانات مباشرة الآن).

<بيانات_الحقل>
الحقل   : {field.nameAr or field.name}
المحصول : {field.cropType or 'غير محدد'}
المساحة : {field.areaHa or '؟'} هكتار
الموقع  : {field.lat:.4f}° شمالًا، {field.lng:.4f}° شرقًا
المؤشر الساتلي المحدد: {indice_label}
</بيانات_الحقل>

<بيانات_الطقس_الحالية>{weather_block or chr(10) + '  لا تتوفر بيانات OpenWeather'}{meteo_block or chr(10) + '  لا تتوفر بيانات OpenMeteo'}
</بيانات_الطقس_الحالية>

أنتج بالضبط 4–6 نقاط موجزة باللغة العربية تغطي:
١. مدى ملاءمة الطقس الحالي للعمليات الزراعية (رش، ري، حصاد، خدمة التربة)
٢. حِمل التبخر-النتح ET₀ وإلحاحية الري بناءً على القيمة الحالية
٣. حالة رطوبة التربة وتداعياتها على امتصاص الجذور للماء والعناصر
٤. مخاطر الإجهاد الحراري أو البرودي أو الريحي على المحصول
٥. مدى كفاية الأمطار مقارنةً باحتياجات المحصول المائية
٦. مخاطر الآفات والأمراض المرتبطة بالطقس (رطوبة وحرارة ملائمة للفطريات والبكتيريا)

التنسيق: نقاط تبدأ بـ "•". أرقام ووحدات دائمًا. بدون عناوين. باللغة العربية حصرًا. الحد الأقصى 120 كلمة لكل نقطة.
</مهمة>"""


def _build_recommendations_prompt(req: AnalyzeFieldRequest) -> str:
    cdse = req.cdse
    w = req.weather
    m = req.meteo
    field = req.field
    indice_label = _indice_ar(req.indice)

    val_str = f"{cdse.value:.4f}" if cdse.value is not None else "غير متوفر"
    range_str = (
        f" (الأدنى={cdse.minValue:.4f}، الأقصى={cdse.maxValue:.4f}، σ={cdse.stdDev:.4f})"
        if cdse.value is not None and cdse.minValue is not None
        else ""
    )

    weather_lines = ""
    if w:
        weather_lines = f"""
  ── بيانات OpenWeather الحالية ──
  درجة الحرارة      : {w.temperature}°م (تبدو كـ {w.feelsLike}°م)
  الرطوبة النسبية   : {w.humidity}%
  سرعة الرياح       : {w.windSpeed} م/ث | اتجاه {w.windDirection}°
  هطول الأمطار      : {w.precipitation} مم/ساعة
  الغطاء السحابي    : {w.cloudCover}%
  الضغط الجوي       : {w.pressure} هكتوباسكال
  مدى الرؤية        : {w.visibility} كم
  الحالة الجوية     : {w.description}"""

    meteo_lines = ""
    if m:
        meteo_lines = f"""
  ── بيانات OpenMeteo الحالية ──
  درجة الحرارة (2م)         : {m.temperature2m}°م
  الرطوبة النسبية (2م)       : {m.relativeHumidity2m}%
  هطول الأمطار               : {m.precipitation} مم
  سرعة الرياح (10م)          : {m.windSpeed10m} م/ث
  رطوبة التربة (0–1 سم)      : {m.soilMoisture0to1cm} م³/م³
  التبخر-النتح ET₀ (FAO-56)  : {m.et0FaoEvapotranspiration} مم/يوم
  ضغط السطح                  : {m.surfacePressure} هكتوباسكال
  الغطاء السحابي              : {m.cloudCover}%
  الإشعاع الشمسي القصير      : {m.shortwaveRadiation} واط/م²"""

    return f"""<مهمة>
أنت الدكتور خالد الرشيدي. بناءً على بيانات المؤشر الساتلي والطقس الحالية أدناه، قدّم توصيات زراعية فورية وعملية للمزارع.

<بيانات_الحقل_الكاملة>
  ── معلومات الحقل ──
  اسم الحقل        : {field.nameAr or field.name}
  المحصول           : {field.cropType or 'غير محدد'}
  المساحة           : {field.areaHa or '؟'} هكتار
  نوع التربة        : {field.soilType or 'غير محدد'}
  الموقع            : {field.lat:.4f}° شمالًا، {field.lng:.4f}° شرقًا

  ── المؤشر الساتلي CDSE (تاريخ: {cdse.date or 'غير محدد'}) ──
  المؤشر المحدد     : {indice_label}
  القيمة المتوسطة   : {val_str}{range_str}
  الغطاء السحابي    : {f"{cdse.cloudCover:.1f}%" if cdse.cloudCover is not None else "غير محدد"}
{weather_lines}
{meteo_lines}
</بيانات_الحقل_الكاملة>

أنتج بالضبط 5–7 نقاط توصية قابلة للتطبيق الفوري باللغة العربية. كل توصية يجب أن:
- تكون محددة وقابلة للتنفيذ (24–72 ساعة للحالات الحرجة، 1–2 أسبوع للتخطيط)
- ترتبط مباشرةً برقم أو قيمة من البيانات أعلاه
- تتضمن التوقيت والكمية/المعدل أو الطريقة حيثما أمكن
- تحمل تصنيف الأولوية: [عاجل] أو [عالٍ] أو [متوسط] أو [منخفض]

تغطي كحد أدنى: قرار الري، التسميد والتغذية، الوقاية من الآفات، توقيت العمليات الميدانية، إجراءات المراقبة.

التنسيق: نقاط تبدأ بـ "•". بدون عناوين. باللغة العربية حصرًا. الحد الأقصى 150 كلمة لكل نقطة.
</مهمة>"""


# ── Agent runners ─────────────────────────────────────────────────────────────


async def _run_agent(
    system: str,
    user_prompt: str,
    max_tokens: int = 800,
    model: str | None = None,
) -> str:
    """Call LLM via OpenRouter (OpenAI-compatible). Returns raw text."""
    client = _get_client()
    _model = model or MODEL_FAST
    try:
        response = await client.chat.completions.create(
            model=_model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        logger.error("OpenRouter API call failed [model=%s]: %s", _model, exc)
        raise


def _parse_bullets(text: str) -> list[str]:
    """Extract bullet-point lines. Strips <think> blocks from reasoning models."""
    # Strip reasoning model thinking blocks (Qwen3.5, DeepSeek-R1, etc.)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    bullets = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("•"):
            bullet = stripped[1:].strip()
            if bullet:
                bullets.append(bullet)
        elif stripped.startswith(("-", "*")):
            bullet = stripped[1:].strip()
            if bullet and len(bullet) > 15:
                bullets.append(bullet)

    # Fallback: paragraph split when model doesn't use bullet chars
    if not bullets:
        for para in text.split("\n\n"):
            para = para.strip()
            if para and len(para) > 20:
                bullets.append(para)

    return bullets[:8]


# ── Endpoint ─────────────────────────────────────────────────────────────────


@ai_router.post(
    "/analyze/field",
    response_model=AnalyzeFieldResponse,
    summary="تحليل الحقل بالذكاء الاصطناعي",
    description="ثلاثة وكلاء متوازيون: صحة الغطاء النباتي + تأثير الطقس + التوصيات",
    tags=["AI Analysis"],
)
async def analyze_field(req: AnalyzeFieldRequest) -> AnalyzeFieldResponse:
    """
    Three agents run in parallel:
    - Agent 1: CDSE index analysis (selected index) → current_status
    - Agent 2: Weather (OpenWeather + OpenMeteo live) → current_status
    - Agent 3: Actionable recommendations from all data → recommendations
    """
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="AI analysis service not configured: OPENROUTER_API_KEY missing",
        )

    veg_prompt = _build_vegetation_prompt(req)
    weather_prompt = _build_weather_prompt(req)
    reco_prompt = _build_recommendations_prompt(req)

    logger.info(
        "AI analysis started — field=%s indice=%s model=%s",
        req.field.id,
        req.indice,
        MODEL_FAST,
    )

    try:
        veg_task     = _run_agent(SYSTEM_PERSONA, veg_prompt,     max_tokens=700, model=MODEL_FAST)
        weather_task = _run_agent(SYSTEM_PERSONA, weather_prompt, max_tokens=700, model=MODEL_FAST)
        reco_task    = _run_agent(SYSTEM_PERSONA, reco_prompt,    max_tokens=1000, model=MODEL_PRIMARY)

        veg_text, weather_text, reco_text = await asyncio.gather(
            veg_task, weather_task, reco_task
        )

    except Exception as exc:
        logger.error("Multi-agent analysis failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {exc}",
        )

    current_status_bullets = _parse_bullets(veg_text) + _parse_bullets(weather_text)
    recommendation_bullets = _parse_bullets(reco_text)

    from datetime import datetime, timezone

    return AnalyzeFieldResponse(
        field_id=req.field.id,
        indice=req.indice,
        current_status=current_status_bullets,
        recommendations=recommendation_bullets,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )

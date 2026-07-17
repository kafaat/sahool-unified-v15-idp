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

from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

ai_router = APIRouter()

# ── OpenRouter client (lazy, shared) ─────────────────────────────────────────

_openrouter_client: AsyncOpenAI | None = None

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

MODEL_FAST = os.environ.get("OPENROUTER_MODEL_FAST", "qwen/qwen3-next-80b-a3b-instruct:free")
MODEL_PRIMARY = os.environ.get("OPENROUTER_MODEL_PRIMARY", "anthropic/claude-sonnet-4-20250514")


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

# Arabic names for each index
_INDICE_AR: dict[str, str] = {
    "NDVI": "مؤشر الغطاء النباتي الطبيعي (NDVI)",
    "EVI": "مؤشر الغطاء النباتي المُحسَّن (EVI)",
    "EVI2": "مؤشر الغطاء النباتي ثنائي النطاق (EVI2)",
    "NDWI": "مؤشر محتوى الماء في النبات (NDWI)",
    "NDMI": "مؤشر رطوبة النبات (NDMI)",
    "NDMI_STRESS": "مؤشر إجهاد رطوبة النبات (NDMI Stress)",
    "SAVI": "مؤشر الغطاء مع تعديل التربة (SAVI)",
    "NDRE": "مؤشر الحافة الحمراء للكلوروفيل (NDRE)",
    "NBR": "نسبة الحرق المُعيَّرة (NBR)",
    "BAIS2": "مؤشر المناطق المحروقة (BAIS2)",
    "BSI": "مؤشر التربة العارية (BSI)",
    "MSAVI": "مؤشر النبات المُعدَّل للتربة (MSAVI)",
    "GNDVI": "مؤشر الغطاء النباتي الأخضر (GNDVI)",
    "LAI": "مؤشر مساحة الأوراق (LAI)",
    "FAPAR": "جزء الإشعاع الضوئي الممتص (FAPAR)",
    "FCOVER": "كسر الغطاء النباتي (FCOVER)",
    "ARVI": "مؤشر مقاومة الغلاف الجوي (ARVI)",
    "PSRI": "مؤشر شيخوخة النبات (PSRI)",
    "RECI": "مؤشر كلوروفيل الحافة الحمراء (RECI)",
    "NDCI": "مؤشر الكلوروفيل المعياري (NDCI)",
    "MCARI": "مؤشر امتصاص الكلوروفيل (MCARI)",
    "NDSI": "مؤشر الثلج المعياري (NDSI)",
    "KNDVI": "مؤشر NDVI النواة (kNDVI)",
    "NDYI": "مؤشر الاصفرار (NDYI)",
    "MSI": "مؤشر إجهاد الرطوبة (MSI)",
}

# Per-index interpretation context: ranges + what it measures + key thresholds
_INDICE_CONTEXT: dict[str, str] = {
    "NDVI": "النطاق −1 إلى +1. < 0.2 = تربة/غطاء حرج | 0.2–0.4 = نبات مجهد | 0.4–0.6 = نبات متوسط | > 0.6 = نبات صحي. يقيس الكثافة الخضرية العامة.",
    "EVI": "النطاق −1 إلى +1. أكثر دقة من NDVI في المناطق الكثيفة وعند تشبع الإشارة. < 0.2 = حرج | 0.2–0.4 = مجهد | > 0.5 = صحي.",
    "EVI2": "مشابه لـ EVI لكن بدون نطاق أزرق. الحدود ذاتها.",
    "GNDVI": "النطاق −1 إلى +1. حساس لنقص النيتروجين أكثر من NDVI. < 0.25 = نقص شديد | 0.25–0.45 = نقص متوسط | > 0.5 = كافٍ.",
    "NDRE": "النطاق −1 إلى +1. مؤشر الكلوروفيل ومحتوى النيتروجين. < 0.1 = نقص حاد | 0.1–0.2 = نقص | > 0.2 = مقبول.",
    "SAVI": "النطاق −1 إلى +1. مُحسَّن للمناطق متفرقة النبات (جفاف، رعي). < 0.2 = غطاء ضعيف | 0.2–0.5 = متوسط | > 0.5 = جيد.",
    "MSAVI": "مشابه لـ SAVI مع تكيف ذاتي. مناسب للمناطق الجافة. نفس نطاقات SAVI.",
    "NDWI": "النطاق −1 إلى +1. يقيس محتوى الماء في النبات. < −0.1 = إجهاد مائي حاد | −0.1–0.1 = جفاف معتدل | > 0.2 = محتوى مائي كافٍ.",
    "NDMI": "النطاق −1 إلى +1. يقيس رطوبة الأوراق. < −0.2 = إجهاد مائي شديد | −0.2–0.0 = مجهد | > 0.0 = رطوبة مناسبة.",
    "NDMI_STRESS": "نفس NDMI مع تركيز على قيم الإجهاد السلبية.",
    "MSI": "النطاق 0 إلى +3. عكسي: الأعلى = جفاف أشد. < 0.4 = رطوبة عالية | 0.4–1.0 = طبيعي | > 1.0 = إجهاد مائي.",
    "LAI": "النطاق 0 إلى 8+ م²/م². 0–1 = غطاء ضعيف | 1–3 = متوسط | 3–6 = جيد | > 6 = كثيف جدًا.",
    "FAPAR": "النطاق 0–1. نسبة الإشعاع الممتص. < 0.3 = غطاء ضعيف | > 0.6 = غطاء جيد.",
    "FCOVER": "النطاق 0–1. نسبة تغطية الأرض. < 0.3 = تغطية ضعيفة | > 0.6 = تغطية جيدة.",
    "NBR": "النطاق −1 إلى +1. يقيس الحرق والتلف. > 0.1 = نبات سليم | −0.1–0.1 = تلف خفيف | < −0.1 = حريق/تلف شديد.",
    "BAIS2": "النطاق 0–5+. مؤشر المساحات المحروقة. > 1.0 = حريق مؤكد.",
    "BSI": "النطاق −1 إلى +1. يكشف التربة العارية. > 0 = تربة مكشوفة | < 0 = غطاء نباتي.",
    "ARVI": "مشابه لـ NDVI لكن مُصحَّح للغلاف الجوي. نفس نطاقات NDVI.",
    "PSRI": "النطاق −1 إلى +1. يقيس شيخوخة النبات. > 0.2 = شيخوخة/نضج متقدم | < 0 = نبات خضراء.",
    "NDYI": "يقيس الاصفرار. > 0.2 = اصفرار واضح ← نقص N أو مرض.",
    "RECI": "النطاق 0–15+. يقيس الكلوروفيل الكلي. < 2 = نقص | 2–5 = طبيعي | > 5 = وفير.",
    "NDCI": "النطاق −1 إلى +1. كلوروفيل في المسطحات المائية. > 0.2 = تركيز عالٍ.",
    "MCARI": "مشابه لـ RECI للكلوروفيل. القيم الأعلى = كلوروفيل أوفر.",
    "NDSI": "النطاق −1 إلى +1. يكشف الثلج. > 0.4 = غطاء ثلجي.",
    "KNDVI": "نسخة منقحة من NDVI. نفس نطاقات NDVI لكن أكثر استقرارًا مع الغطاء الكثيف.",
}


def _indice_ar(indice: str) -> str:
    return _INDICE_AR.get(indice.upper(), f"مؤشر {indice}")


def _indice_context(indice: str) -> str:
    return _INDICE_CONTEXT.get(indice.upper(), f"يُرجى تفسير قيمة {indice} وفق معرفتك الزراعية.")


def _fmt(val: float | None, decimals: int = 2, unit: str = "") -> str:
    """Format a numeric value for prompt, replacing None with Arabic 'unavailable'."""
    if val is None:
        return "غير متوفر"
    formatted = f"{val:.{decimals}f}"
    return f"{formatted} {unit}".strip() if unit else formatted


def _build_vegetation_prompt(req: AnalyzeFieldRequest) -> str:
    cdse = req.cdse
    field = req.field
    m = req.meteo
    w = req.weather
    indice_label = _indice_ar(req.indice)
    ctx = _indice_context(req.indice)
    has_value = cdse.value is not None

    val_str = f"{cdse.value:.4f}" if has_value else "غير متوفر (تعذّر استرداد صورة الأقمار الاصطناعية)"
    range_str = (
        f"\nالحد الأدنى      : {cdse.minValue:.4f}"
        f"\nالحد الأقصى      : {cdse.maxValue:.4f}"
        f"\nالانحراف المعياري: σ={cdse.stdDev:.4f}"
        if has_value and cdse.minValue is not None
        else ""
    )

    # Build environmental block from all available sources (always include)
    env_lines: list[str] = []
    if m:
        env_lines += [
            f"  رطوبة التربة (0–1 سم)    : {_fmt(m.soilMoisture0to1cm, 3, 'م³/م³')}",
            f"  التبخر-النتح ET₀ (FAO-56): {_fmt(m.et0FaoEvapotranspiration, 2, 'مم/يوم')}",
            f"  درجة الحرارة (2م)          : {_fmt(m.temperature2m, 1, '°م')}",
            f"  الرطوبة النسبية (2م)        : {_fmt(m.relativeHumidity2m, 0, '%')}",
            f"  الإشعاع الشمسي القصير      : {_fmt(m.shortwaveRadiation, 1, 'واط/م²')}",
            f"  الغطاء السحابي              : {_fmt(m.cloudCover, 0, '%')}",
            f"  هطول الأمطار               : {_fmt(m.precipitation, 2, 'مم')}",
            f"  سرعة الرياح (10م)          : {_fmt(m.windSpeed10m, 1, 'م/ث')}",
        ]
    if w:
        env_lines += [
            f"  الحالة الجوية (OpenWeather): {w.description or 'غير متوفر'}",
            f"  درجة الحرارة الظاهرة       : {_fmt(w.feelsLike, 1, '°م')}",
            f"  الرطوبة (OpenWeather)       : {_fmt(w.humidity, 0, '%')}",
        ]

    env_block = "\n".join(env_lines) if env_lines else "  لا تتوفر بيانات بيئية"

    if not has_value:
        return f"""أنت الدكتور خالد الرشيدي. صورة {indice_label} غير متوفرة حاليًا لهذا الحقل (الأرجح بسبب الغيوم أو عدم اكتمال المعالجة). لديك بيانات بيئية وأرصاد زراعية كاملة — استخدمها لتحليل صحة المحصول وأنتج 4 نقاط دقيقة.

<بيانات_الحقل>
الحقل   : {field.nameAr or field.name}
الموقع  : {field.lat:.4f}°ش، {field.lng:.4f}°ش
المحصول : {field.cropType or "غير محدد"} | المساحة: {_fmt(field.areaHa, 1, "هـ")} | التربة: {field.soilType or "غير محدد"}
</بيانات_الحقل>

<البيانات_البيئية_المتاحة>
{env_block}
</البيانات_البيئية_المتاحة>

<المؤشر_المطلوب>
المؤشر: {indice_label}
مرجع التفسير: {ctx}
قيمة المؤشر: {val_str}
</المؤشر_المطلوب>

اكتب 4 نقاط فقط تبدأ كل منها بـ (•):
• نقطة 1: وضِّح أن صورة {indice_label} غير متاحة الآن مع ذكر السبب المرجح، ومتى يمكن إعادة المحاولة.
• نقطة 2: قيّم الإجهاد المائي للمحصول بناءً على رطوبة التربة وET₀ — اذكر الأرقام واتخذ قرارًا.
• نقطة 3: قيّم الإجهاد الحراري والضوئي بناءً على درجة الحرارة والإشعاع الشمسي والرطوبة.
• نقطة 4: أعطِ تصنيفًا إجماليًا لصحة المحصول (حرج/مجهد/متوسط/صحي) مع التوصية الميدانية الأعلى أولوية.

⚠️ 4 نقاط فقط — لا أكثر ولا أقل. أرقام ووحدات في كل نقطة. بدون عناوين. باللغة العربية حصرًا."""

    return f"""أنت الدكتور خالد الرشيدي. حلِّل مؤشر {indice_label} للحقل أدناه وأنتج 4 نقاط ساتلية دقيقة.

<بيانات_الحقل>
الحقل   : {field.nameAr or field.name}
الموقع  : {field.lat:.4f}°ش، {field.lng:.4f}°ش
المحصول : {field.cropType or "غير محدد"} | المساحة: {_fmt(field.areaHa, 1, "هـ")} | التربة: {field.soilType or "غير محدد"}
</بيانات_الحقل>

<قراءة_{req.indice}>
القيمة المتوسطة : {val_str}{range_str}
تاريخ الصورة   : {cdse.date or "غير محدد"}
الغطاء السحابي : {_fmt(cdse.cloudCover, 1, "%")}
</قراءة_{req.indice}>

<مرجع_التفسير>
{ctx}
</مرجع_التفسير>

<البيانات_البيئية_المصاحبة>
{env_block}
</البيانات_البيئية_المصاحبة>

اكتب 4 نقاط فقط تبدأ كل منها بـ (•):
• نقطة 1: فسِّر قيمة {val_str} لـ {indice_label} زراعيًا بالنسبة للمحصول، مع ذكر الرقم صراحةً وتصنيفه وفق مرجع التفسير.
• نقطة 2: صنِّف صحة النبات (حرج/مجهد/متوسط/صحي/ممتاز) مستندًا إلى الأرقام والنطاقات المرجعية.
• نقطة 3: حدِّد إشارات الإجهاد أو الشذوذات (مائية/غذائية/أمراض/شيخوخة) مقارنةً بالبيانات البيئية.
• نقطة 4: اذكر تباين القيم (أدنى/أقصى) إن توفر، ومستوى الثقة في التقييم مع توصية فورية واحدة.

⚠️ 4 نقاط فقط — لا أكثر. أرقام ووحدات في كل نقطة. بدون عناوين. باللغة العربية حصرًا."""


def _build_weather_prompt(req: AnalyzeFieldRequest) -> str:
    w = req.weather
    m = req.meteo
    field = req.field
    indice_label = _indice_ar(req.indice)
    cdse = req.cdse

    val_str = f"{cdse.value:.4f}" if cdse.value is not None else "غير متوفر"

    weather_block = "  ── OpenWeather: غير متوفر (مفتاح API غير مُهيَّأ) ──"
    if w:
        weather_block = f"""  ── بيانات OpenWeather الحالية ──
  درجة الحرارة    : {_fmt(w.temperature, 1, "°م")} (تبدو كـ {_fmt(w.feelsLike, 1, "°م")})
  الرطوبة النسبية : {_fmt(w.humidity, 0, "%")}
  سرعة الرياح    : {_fmt(w.windSpeed, 1, "م/ث")} باتجاه {_fmt(w.windDirection, 0, "°")}
  هطول الأمطار   : {_fmt(w.precipitation, 2, "مم")} (الساعة الأخيرة)
  الغطاء السحابي : {_fmt(w.cloudCover, 0, "%")}
  الضغط الجوي    : {_fmt(w.pressure, 0, "هكتوباسكال")}
  مدى الرؤية     : {_fmt(w.visibility, 0, "كم")}
  الحالة الجوية  : {w.description or "غير متوفر"}"""

    meteo_block = "  ── OpenMeteo: غير متوفر ──"
    if m:
        meteo_block = f"""  ── بيانات OpenMeteo الحالية ──
  درجة الحرارة (2م)        : {_fmt(m.temperature2m, 1, "°م")}
  الرطوبة النسبية (2م)      : {_fmt(m.relativeHumidity2m, 0, "%")}
  هطول الأمطار              : {_fmt(m.precipitation, 2, "مم")}
  سرعة الرياح (10م)         : {_fmt(m.windSpeed10m, 1, "م/ث")}
  رطوبة التربة (0–1 سم)     : {_fmt(m.soilMoisture0to1cm, 3, "م³/م³")}
  التبخر-النتح ET₀ (FAO-56) : {_fmt(m.et0FaoEvapotranspiration, 2, "مم/يوم")}
  ضغط السطح                 : {_fmt(m.surfacePressure, 0, "هكتوباسكال")}
  الغطاء السحابي             : {_fmt(m.cloudCover, 0, "%")}
  الإشعاع الشمسي القصير     : {_fmt(m.shortwaveRadiation, 1, "واط/م²")}"""

    return f"""أنت الدكتور خالد الرشيدي. حلِّل الطقس والأرصاد الزراعية لهذا الحقل وأنتج 4 نقاط طقسية دقيقة.

<بيانات_الحقل>
الحقل: {field.nameAr or field.name} | المحصول: {field.cropType or "غير محدد"} | {_fmt(field.areaHa, 1, "هـ")}
الموقع: {field.lat:.4f}°ش، {field.lng:.4f}°ش | المؤشر الساتلي: {indice_label} = {val_str}
</بيانات_الحقل>

<الطقس_الحالي>
{weather_block}
{meteo_block}
</الطقس_الحالي>

اكتب 4 نقاط فقط تبدأ كل منها بـ (•):
• نقطة 1: ملاءمة الطقس الحالي للعمليات الزراعية (رش، ري، حصاد) بناءً على الأرقام الفعلية المذكورة أعلاه.
• نقطة 2: إلحاحية الري بناءً على ET₀ ورطوبة التربة — اذكر الأرقام صراحةً واتخذ قرارًا واضحًا (ري الآن / تأجيل N يوم).
• نقطة 3: مخاطر الإجهاد الحراري أو الريحي على المحصول بناءً على درجة الحرارة والرطوبة والإشعاع.
• نقطة 4: مخاطر الآفات والأمراض المرتبطة بالظروف الجوية الحالية مع توصية وقائية محددة.

⚠️ 4 نقاط فقط — لا أكثر. أرقام ووحدات في كل نقطة. بدون عناوين. باللغة العربية حصرًا."""


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

    weather_lines = "  ── OpenWeather: غير متوفر (مفتاح API غير مُهيَّأ) ──"
    if w:
        weather_lines = f"""  ── بيانات OpenWeather الحالية ──
  درجة الحرارة      : {_fmt(w.temperature, 1, "°م")} (تبدو كـ {_fmt(w.feelsLike, 1, "°م")})
  الرطوبة النسبية   : {_fmt(w.humidity, 0, "%")}
  سرعة الرياح       : {_fmt(w.windSpeed, 1, "م/ث")} | اتجاه {_fmt(w.windDirection, 0, "°")}
  هطول الأمطار      : {_fmt(w.precipitation, 2, "مم/ساعة")}
  الغطاء السحابي    : {_fmt(w.cloudCover, 0, "%")}
  الضغط الجوي       : {_fmt(w.pressure, 0, "هكتوباسكال")}
  مدى الرؤية        : {_fmt(w.visibility, 0, "كم")}
  الحالة الجوية     : {w.description or "غير متوفر"}"""

    meteo_lines = "  ── OpenMeteo: غير متوفر ──"
    if m:
        meteo_lines = f"""  ── بيانات OpenMeteo الحالية ──
  درجة الحرارة (2م)         : {_fmt(m.temperature2m, 1, "°م")}
  الرطوبة النسبية (2م)       : {_fmt(m.relativeHumidity2m, 0, "%")}
  هطول الأمطار               : {_fmt(m.precipitation, 2, "مم")}
  سرعة الرياح (10م)          : {_fmt(m.windSpeed10m, 1, "م/ث")}
  رطوبة التربة (0–1 سم)      : {_fmt(m.soilMoisture0to1cm, 3, "م³/م³")}
  التبخر-النتح ET₀ (FAO-56)  : {_fmt(m.et0FaoEvapotranspiration, 2, "مم/يوم")}
  ضغط السطح                  : {_fmt(m.surfacePressure, 0, "هكتوباسكال")}
  الغطاء السحابي              : {_fmt(m.cloudCover, 0, "%")}
  الإشعاع الشمسي القصير      : {_fmt(m.shortwaveRadiation, 1, "واط/م²")}"""

    ctx = _indice_context(req.indice)

    return f"""أنت الدكتور خالد الرشيدي. بناءً على جميع البيانات أدناه، أنتج 5 توصيات زراعية فورية قابلة للتنفيذ.

<بيانات_الحقل_الكاملة>
الحقل: {field.nameAr or field.name} | المحصول: {field.cropType or "غير محدد"} | {_fmt(field.areaHa, 1, "هـ")} | التربة: {field.soilType or "غير محدد"}
الموقع: {field.lat:.4f}°ش، {field.lng:.4f}°ش

── {indice_label} (تاريخ: {cdse.date or "غير محدد"}) ──
القيمة: {val_str}{range_str}
مرجع التفسير: {ctx}

{weather_lines}

{meteo_lines}
</بيانات_الحقل_الكاملة>

اكتب 5 توصيات فقط تبدأ كل منها بـ (•) وتحمل تصنيف الأولوية في البداية:
• [عاجل/عالٍ/متوسط/منخفض] التوصية 1: قرار الري — هل يجب الري الآن؟ متى؟ كم مم؟ استند للأرقام الفعلية.
• [عاجل/عالٍ/متوسط/منخفض] التوصية 2: التسميد والتغذية — ما العنصر المطلوب؟ الكمية؟ التوقيت الأمثل؟
• [عاجل/عالٍ/متوسط/منخفض] التوصية 3: مكافحة الآفات والأمراض — ما المخاطر بناءً على الطقس؟ ما الإجراء؟
• [عاجل/عالٍ/متوسط/منخفض] التوصية 4: توقيت العمليات الميدانية — ما الذي يجب تأجيله أو تسريعه بناءً على الظروف؟
• [عاجل/عالٍ/متوسط/منخفض] التوصية 5: مراقبة {indice_label} — ما الإجراء التالي لتتبع هذا المؤشر تحديدًا؟

⚠️ 5 نقاط فقط — لا أكثر. كل نقطة تحتوي أرقامًا وتوقيتًا ومعدلًا حيثما أمكن. بدون عناوين إضافية. باللغة العربية حصرًا."""


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


def _parse_bullets(text: str, max_bullets: int = 8) -> list[str]:
    """Extract bullet-point lines. Strips <think> blocks from reasoning models."""
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

    return bullets[:max_bullets]


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

    has_cdse = req.cdse.value is not None
    has_weather = req.weather is not None
    has_meteo = req.meteo is not None
    logger.info(
        "AI analysis started — field=%s indice=%s cdse_value=%s weather=%s meteo=%s model=%s",
        req.field.id,
        req.indice,
        f"{req.cdse.value:.4f}" if has_cdse else "null",
        "yes" if has_weather else "null",
        "yes" if has_meteo else "null",
        MODEL_FAST,
    )

    try:
        veg_task = _run_agent(SYSTEM_PERSONA, veg_prompt, max_tokens=700, model=MODEL_FAST)
        weather_task = _run_agent(SYSTEM_PERSONA, weather_prompt, max_tokens=700, model=MODEL_FAST)
        reco_task = _run_agent(SYSTEM_PERSONA, reco_prompt, max_tokens=1000, model=MODEL_PRIMARY)

        veg_text, weather_text, reco_text = await asyncio.gather(veg_task, weather_task, reco_task)

    except Exception as exc:
        logger.error("Multi-agent analysis failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {exc}",
        )

    # Vegetation: 4 bullets always (even when CDSE null — prompt uses meteo data).
    # Weather: 4. Recommendations: 5.
    current_status_bullets = _parse_bullets(veg_text, 4) + _parse_bullets(weather_text, 4)
    recommendation_bullets = _parse_bullets(reco_text, 5)

    from datetime import UTC, datetime

    return AnalyzeFieldResponse(
        field_id=req.field.id,
        indice=req.indice,
        current_status=current_status_bullets,
        recommendations=recommendation_bullets,
        analyzed_at=datetime.now(UTC).isoformat(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Comprehensive Unified 13-Section Field Analysis
# التحليل الشامل الموحد (13 قسماً)
# ═══════════════════════════════════════════════════════════════════════════════

import json
import os as _os

# Import schemas at module level so FastAPI can resolve them for body injection
from ..models.analysis_schemas import (  # noqa: E402
    ActionItem,
    AllIndicesPayload,
    AnalysisSections,
    ComprehensiveAnalysisRequest,
    FieldAnalysisResponse,
    ImageryPayload,
    MeteoPayload,
    SectionContent,
    WeatherPayload,
)

try:
    import redis.asyncio as aioredis

    _REDIS_URL = _os.environ.get("REDIS_URL", "redis://redis:6379")
    _redis_client: aioredis.Redis | None = None

    async def _get_redis() -> aioredis.Redis | None:
        global _redis_client
        if _redis_client is None:
            try:
                _redis_client = aioredis.from_url(_REDIS_URL, decode_responses=True)
            except Exception:
                _redis_client = None
        return _redis_client

except ImportError:

    async def _get_redis():
        return None


_CACHE_TTL_SECONDS = 3 * 3600  # 3 hours


def _fmt_val(v: float | None, dec: int = 3) -> str:
    return f"{v:.{dec}f}" if v is not None else "غير متوفر"


def _build_indices_block(indices: AllIndicesPayload) -> str:
    """Format all 37 indices into a structured Arabic text block."""
    _LABELS = {
        "NDVI": "NDVI (الغطاء النباتي)",
        "EVI": "EVI (الغطاء المُحسَّن)",
        "EVI2": "EVI2 (ثنائي النطاق)",
        "GNDVI": "GNDVI (الكلوروفيل الأخضر)",
        "WDRVI": "WDRVI (النطاق الديناميكي)",
        "ARVI": "ARVI (تصحيح جوي)",
        "DVI": "DVI (فرق الغطاء)",
        "RVI": "RVI (نسبة الغطاء)",
        "RDVI": "RDVI (معياري محسّن)",
        "NIRv": "NIRv (إنتاجية أولية)",
        "NDRE": "NDRE (كلوروفيل/نيتروجين)",
        "NDRE1": "NDRE1 (حافة حمراء 1)",
        "NDRE2": "NDRE2 (حافة حمراء 2)",
        "S2REP": "S2REP (موضع الحافة الحمراء)",
        "IRECI": "IRECI (كلوروفيل معكوس)",
        "CIre": "CIre (مؤشر كلوروفيل)",
        "CIgreen": "CIgreen (كلوروفيل أخضر)",
        "MCARI": "MCARI (امتصاص الكلوروفيل)",
        "SAVI": "SAVI (تعديل التربة)",
        "OSAVI": "OSAVI (تعديل محسّن)",
        "MSAVI": "MSAVI (تعديل ذاتي)",
        "TSAVI": "TSAVI (تعديل محوّل)",
        "NDWI": "NDWI (محتوى الماء)",
        "NDMI": "NDMI (رطوبة النبات)",
        "MNDWI": "MNDWI (ماء معدّل)",
        "MSI": "MSI (إجهاد الرطوبة)",
        "LSWI": "LSWI (رطوبة السطح)",
        "DSWI": "DSWI (مرض-إجهاد مائي)",
        "LAI": "LAI (مساحة الأوراق م²/م²)",
        "FAPAR": "FAPAR (الإشعاع الممتص)",
        "SeLI": "SeLI (مؤشر LAI)",
        "PSRI": "PSRI (شيخوخة النبات)",
        "SIPI": "SIPI (نسبة الأصباغ)",
        "ARI": "ARI (أنثوسيانين)",
        "BSI": "BSI (التربة العارية)",
        "BI": "BI (سطوع التربة)",
        "NDPI": "NDPI (المرحلة الفينولوجية)",
    }
    lines = []
    for key, label in _LABELS.items():
        stats = getattr(indices, key, None)
        val = stats.value if stats else None
        lines.append(f"  {label}: {_fmt_val(val)}")
    return "\n".join(lines)


def _build_meteo_block(meteo: MeteoPayload | None, weather: WeatherPayload | None) -> str:
    """Format all weather + soil + forecast data into Arabic text block."""
    lines = []
    if weather:
        lines.append("── بيانات الطقس الحالية (OpenWeather) ──")
        lines.append(
            f"  درجة الحرارة: {_fmt_val(weather.temperature, 1)}°م | الرطوبة: {_fmt_val(weather.humidity, 0)}%"
        )
        lines.append(f"  الرياح: {_fmt_val(weather.wind_speed, 1)} كم/س | هطول: {_fmt_val(weather.precipitation)} مم")
        lines.append(
            f"  الغيوم: {_fmt_val(weather.cloud_cover, 0)}% | الضغط: {_fmt_val(weather.pressure, 0)} هكتوباسكال"
        )
        lines.append(f"  الحالة: {weather.description or 'غير متوفر'}")
    if meteo:
        lines.append("── بيانات الأرصاد الزراعية (Open-Meteo) ──")
        lines.append(
            f"  الحرارة: {_fmt_val(meteo.temperature_2m, 1)}°م | الظاهرية: {_fmt_val(meteo.apparent_temperature, 1)}°م"
        )
        lines.append(
            f"  الرطوبة: {_fmt_val(meteo.relative_humidity_2m, 0)}% | VPD: {_fmt_val(meteo.vapour_pressure_deficit, 2)} كيلوباسكال"
        )
        lines.append(f"  ET₀ (FAO-56): {_fmt_val(meteo.et0_fao_evapotranspiration, 2)} مم/يوم")
        lines.append(f"  الإشعاع الشمسي: {_fmt_val(meteo.shortwave_radiation, 1)} واط/م²")
        lines.append(
            f"  إشعاع مباشر: {_fmt_val(meteo.direct_radiation, 1)} واط/م² | منتشر: {_fmt_val(meteo.diffuse_radiation, 1)} واط/م²"
        )
        lines.append(f"  مدة سطوع الشمس: {_fmt_val(meteo.sunshine_duration, 0)} ثانية")
        # Soil moisture
        sm = meteo.soil_moisture
        if sm:
            lines.append("── رطوبة التربة (م³/م³) ──")
            lines.append(
                f"  0-1سم: {_fmt_val(sm.depth_0_1cm, 3)} | 1-3سم: {_fmt_val(sm.depth_1_3cm, 3)} | 3-9سم: {_fmt_val(sm.depth_3_9cm, 3)}"
            )
            lines.append(f"  9-27سم: {_fmt_val(sm.depth_9_27cm, 3)} | 27-81سم: {_fmt_val(sm.depth_27_81cm, 3)}")
        elif meteo.soil_moisture_0to1cm is not None:
            lines.append(f"  رطوبة التربة (0-1سم): {_fmt_val(meteo.soil_moisture_0to1cm, 3)} م³/م³")
        # Soil temperature
        st = meteo.soil_temperature
        if st:
            lines.append("── حرارة التربة (°م) ──")
            lines.append(
                f"  سطح: {_fmt_val(st.surface, 1)} | 6سم: {_fmt_val(st.depth_6cm, 1)} | 18سم: {_fmt_val(st.depth_18cm, 1)} | 54سم: {_fmt_val(st.depth_54cm, 1)}"
            )
        # 7-day forecast summary
        if meteo.forecast_7day:
            lines.append("── توقعات 7 أيام ──")
            for day in meteo.forecast_7day[:7]:
                if day and day.date:
                    lines.append(
                        f"  {day.date}: {_fmt_val(day.temp_min, 0)}-{_fmt_val(day.temp_max, 0)}°م | هطول: {_fmt_val(day.precipitation_sum)} مم | ET₀: {_fmt_val(day.et0)} مم | أشعة: {_fmt_val(day.uv_index_max, 1)}"
                    )
    return "\n".join(lines) if lines else "  لا تتوفر بيانات بيئية"


def _calc_growth_stage(seeding_date: str | None) -> str:
    """Derive approximate growth stage from seeding date."""
    if not seeding_date:
        return "غير محدد"
    try:
        from datetime import date as _date

        seeded = _date.fromisoformat(seeding_date[:10])
        days = (_date.today() - seeded).days
        if days < 0:
            return "قبل الزراعة"
        elif days <= 20:
            return "إنبات (Emergence)"
        elif days <= 60:
            return "نمو خضري (Vegetative)"
        elif days <= 100:
            return "إزهار (Reproductive)"
        elif days <= 140:
            return "نضج (Maturation)"
        else:
            return "استعداد للحصاد (Pre-Harvest)"
    except Exception:
        return "غير محدد"


def _safe_parse_tier(text: str, default_label: str = "غير متاح") -> dict:
    """Parse LLM JSON output, returning a safe default on failure."""
    # Strip reasoning blocks from models like QwQ / DeepSeek-R1
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    text = re.sub(r"^```[a-z]*\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\s*```$", "", text).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Greedy: find the last } and the matching { to extract outermost JSON object
    last_brace = text.rfind("}")
    if last_brace != -1:
        # Walk backwards to find a matching {
        depth = 0
        for i in range(last_brace, -1, -1):
            if text[i] == "}":
                depth += 1
            elif text[i] == "{":
                depth -= 1
                if depth == 0:
                    candidate = text[i : last_brace + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break

    # Fallback: surface raw text as summary so the UI is never blank
    summary_fallback = text[:500].strip() if text else "التحليل غير متاح حالياً"
    logger.warning("_safe_parse_tier: JSON parse failed, using raw text (%d chars)", len(text))
    return {
        "status_label": default_label,
        "status_color": "yellow",
        "summary": summary_fallback,
        "observations": [],
        "actions": [],
    }


@ai_router.post(
    "/analyze/field/comprehensive",
    summary="تحليل شامل موحد للحقل - 13 قسم",
    description="يستخدم جميع المؤشرات الطيفية الـ37 + الطقس الكامل + بيانات الحقل. يُخزَّن 3 ساعات في Redis.",
    tags=["AI Analysis"],
)
async def analyze_field_comprehensive(
    req: ComprehensiveAnalysisRequest,
) -> FieldAnalysisResponse:
    """
    Unified 13-section field analysis using Claude Sonnet via OpenRouter.
    Single LLM call with comprehensive agriculture prompt.
    """

    if not _os.environ.get("OPENROUTER_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="AI analysis not configured: OPENROUTER_API_KEY missing",
        )

    # ── 1. Redis cache ─────────────────────────────────────────────────────────
    from datetime import UTC, datetime

    today_str = datetime.now(UTC).strftime("%Y%m%d")
    cache_key = f"field_ai_v2:{req.field.id}:{today_str}"

    redis = await _get_redis()
    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached:
                logger.info("cache_hit field=%s", req.field.id)
                data = json.loads(cached)
                data["cached"] = True
                return FieldAnalysisResponse(**data)
        except Exception as _ce:
            logger.warning("Redis read failed: %s", _ce)

    # ── 2. AgriGuard health scoring ────────────────────────────────────────────
    from ..services.model_loader import get_agri_scorer

    scorer = get_agri_scorer()
    health_class, health_confidence = scorer.score(
        ndvi=req.indices.NDVI.value,
        ndre=req.indices.NDRE.value,
        ndmi=req.indices.NDMI.value,
        evi2=req.indices.EVI2.value,
        temperature=req.weather.temperature if req.weather else None,
        humidity=req.weather.humidity if req.weather else None,
    )

    # Convert to 0-100 score
    health_score_map = {"healthy": 85, "stressed": 50, "diseased": 20, "moderate": 65}
    health_score = int(health_score_map.get(health_class, 50) * health_confidence + (1 - health_confidence) * 50)

    # ── 3. Build indices summary ───────────────────────────────────────────────
    indices_summary = {}
    for name in req.indices.model_fields:
        stats = getattr(req.indices, name, None)
        indices_summary[name] = stats.value if stats else None

    # ── 4. Build unified prompt ────────────────────────────────────────────────
    f = req.field
    growth = _calc_growth_stage(f.seeding_date)
    hier = f.farm_hierarchy
    loc_str = f"{hier.governorate or ''} - {hier.district or ''}" if hier else "غير محدد"

    indices_block = _build_indices_block(req.indices)
    meteo_block = _build_meteo_block(req.meteo, req.weather)

    health_ar = {"healthy": "صحي", "stressed": "مجهد", "diseased": "حرج", "moderate": "متوسط"}.get(
        health_class, "غير محدد"
    )

    unified_prompt = f"""أنت الدكتور خالد الرشيدي، خبير زراعي أول متخصص في الزراعة الذكية بخبرة تزيد عن 20 عامًا في منطقة الشرق الأوسط.
خبرتك تشمل: إدارة المحاصيل في المناطق الجافة وشبه الجافة (قمح، شعير، نخيل، خضروات)، تفسير صور الأقمار الصناعية Sentinel-2، تحسين الري تحت ظروف شح المياه، الآفات والأمراض المحلية (سوسة النخيل الحمراء، صدأ القمح، المن)، أنواع التربة في الشرق الأوسط (كلسية، ملحية، رملية).

حلّل الحقل التالي وأنتج تقريراً موحداً شاملاً من 13 قسماً.

<بيانات_الحقل>
الحقل: {f.name_ar or f.name} | المعرف: {f.id}
الموقع: {f.lat:.4f}°ش، {f.lng:.4f}°ش | الموقع الإداري: {loc_str}
المحصول: {f.crop_type or "غير محدد"} | المحصول السابق: {f.previous_crop or "غير محدد"}
المساحة: {_fmt_val(f.area_ha, 1)} هكتار | نوع التربة: {f.soil_type or "غير محدد"} | نوع الري: {f.irrigation_type or "غير محدد"}
تاريخ الزراعة: {f.seeding_date or "غير محدد"} | تاريخ الحصاد المتوقع: {f.harvest_date or "غير محدد"}
مرحلة النمو التقريبية: {growth}
التصنيف الصحي (AgriGuard): {health_ar} (ثقة: {health_confidence:.0%})
</بيانات_الحقل>

<المؤشرات_الطيفية_37>
{indices_block}
</المؤشرات_الطيفية_37>

<مصفوفة_التفسير_المشترك>
NDVI منخفض + NDWI/NDMI منخفض + NDRE منخفض = إجهاد مائي
NDVI منخفض + NDWI طبيعي + NDRE منخفض = نقص نيتروجين
NDVI منخفض + NDWI طبيعي + NDRE طبيعي = ضرر فيزيائي (بَرَد/رياح)
NDVI طبيعي + NDWI منخفض + NDRE طبيعي = إجهاد مائي مبكر
NDVI متراجع + NDWI طبيعي + NDRE متراجع = بداية مرض
NDVI متقطع منخفض + متغير + متغير = إصابة آفات
</مصفوفة_التفسير_المشترك>

<البيانات_الجوية_والأرصادية>
{meteo_block}
</البيانات_الجوية_والأرصادية>

أنتج التقرير بصيغة JSON التالية. اكتب التحليل بالعربية مع ذكر المصطلحات التقنية بالإنجليزية بين قوسين عند أول استخدام.

استند فقط إلى البيانات المقدمة. لا تفترض أو تخترع بيانات غير موجودة. عندما تكون البيانات غير كافية لتقييم واثق، اذكر ذلك بوضوح.

{{
  "health_overview": {{
    "title": "نظرة عامة على الصحة",
    "title_en": "Health Overview",
    "status": "good|moderate|warning|critical",
    "status_color": "green|yellow|orange|red",
    "summary": "ملخص عام 1-2 جملة عن حالة الحقل الصحية",
    "details": ["نقطة 1 عن الدرجة الصحية الإجمالية", "نقطة 2 عن أهم المؤشرات"],
    "metrics": {{"health_score": {health_score}, "confidence": {health_confidence:.2f}}},
    "confidence": 0.0
  }},
  "vegetation_health": {{
    "title": "صحة الغطاء النباتي",
    "title_en": "Vegetation Health",
    "status": "...", "status_color": "...",
    "summary": "تحليل متعدد المؤشرات باستخدام NDVI و EVI و GNDVI و RVI",
    "details": ["تفسير NDVI", "تفسير EVI/EVI2", "تفسير GNDVI", "التباين المكاني"],
    "metrics": {{"ndvi": ..., "evi": ..., "gndvi": ...}},
    "confidence": 0.0
  }},
  "water_stress": {{
    "title": "الإجهاد المائي والرطوبة",
    "title_en": "Water Stress & Moisture",
    "status": "...", "status_color": "...",
    "summary": "تحليل الإجهاد المائي من NDMI و NDWI و MSI ورطوبة التربة",
    "details": ["تفسير NDMI/NDWI", "تفسير MSI/LSWI", "رطوبة التربة بالأعماق", "توصية"],
    "metrics": {{"ndmi": ..., "soil_moisture_surface": ...}},
    "confidence": 0.0
  }},
  "growth_stage": {{
    "title": "مرحلة النمو",
    "title_en": "Growth Stage",
    "status": "...", "status_color": "...",
    "summary": "تقييم المرحلة الفينولوجية من NDPI وتاريخ الزراعة",
    "details": ["المرحلة الحالية", "مقارنة بالمتوقع", "مؤشرات النضج"],
    "metrics": {{"days_since_seeding": ..., "estimated_stage": "..."}},
    "confidence": 0.0
  }},
  "nutrient_status": {{
    "title": "حالة العناصر الغذائية",
    "title_en": "Nutrient Status",
    "status": "...", "status_color": "...",
    "summary": "تقدير حالة النيتروجين من NDRE و CIre و MCARI",
    "details": ["تقييم النيتروجين", "تقييم الكلوروفيل", "توصية التسميد"],
    "metrics": {{"ndre": ..., "cire": ...}},
    "confidence": 0.0
  }},
  "pest_disease_risk": {{
    "title": "مخاطر الآفات والأمراض",
    "title_en": "Pest & Disease Risk",
    "status": "...", "status_color": "...",
    "summary": "تقييم المخاطر من DSWI والظروف الجوية",
    "details": ["مستوى الخطر", "التهديدات المحتملة", "إجراء وقائي"],
    "metrics": {{"risk_level": "..."}},
    "confidence": 0.0
  }},
  "irrigation_recommendation": {{
    "title": "توصيات الري",
    "title_en": "Irrigation Recommendations",
    "status": "...", "status_color": "...",
    "summary": "توصية ري محددة بناءً على ET₀ و VPD ورطوبة التربة",
    "details": ["الكمية المقترحة بالمم", "التوقيت الأمثل", "طريقة الري المناسبة"],
    "metrics": {{"et0": ..., "vpd": ..., "recommended_mm": ...}},
    "confidence": 0.0
  }},
  "weather_impact": {{
    "title": "تأثير الطقس",
    "title_en": "Weather Impact",
    "status": "...", "status_color": "...",
    "summary": "تفسير تأثير الطقس الحالي وتوقعات 7 أيام على المحصول",
    "details": ["الظروف الحالية", "توقعات الأسبوع", "نوافذ الرش", "تحذيرات"],
    "metrics": {{"current_temp": ..., "rain_forecast_7d": ...}},
    "confidence": 0.0
  }},
  "yield_prediction": {{
    "title": "تقدير الإنتاجية",
    "title_en": "Yield Prediction",
    "status": "...", "status_color": "...",
    "summary": "تقدير سردي للإنتاجية المتوقعة بناءً على LAI و FAPAR والطقس",
    "details": ["التقدير", "العوامل المؤثرة", "مقارنة بالمتوسط"],
    "metrics": {{"lai": ..., "fapar": ...}},
    "confidence": 0.0
  }},
  "soil_health": {{
    "title": "صحة التربة",
    "title_en": "Soil Health",
    "status": "...", "status_color": "...",
    "summary": "تقييم التربة من BSI وحرارة التربة ورطوبتها",
    "details": ["حالة التربة", "الرطوبة", "الحرارة"],
    "metrics": {{"bsi": ..., "soil_temp_surface": ...}},
    "confidence": 0.0
  }},
  "historical_trends": {{
    "title": "الاتجاهات التاريخية",
    "title_en": "Historical Trends",
    "status": "...", "status_color": "...",
    "summary": "مقارنة القيم الحالية بالمتوقع لمرحلة النمو (ملاحظة: لا تتوفر بيانات تاريخية فعلية)",
    "details": ["تقييم بناءً على القيم الحالية مقارنة بالنطاقات المرجعية"],
    "metrics": {{}},
    "confidence": 0.0
  }},
  "action_plan": {{
    "title": "خطة العمل",
    "title_en": "Action Plan",
    "status": "...", "status_color": "...",
    "summary": "أهم الإجراءات المطلوبة مرتبة حسب الأولوية",
    "details": ["[عاجل] إجراء 1", "[هذا الأسبوع] إجراء 2", "[هذا الشهر] إجراء 3"],
    "metrics": {{"urgent_count": ..., "total_actions": ...}},
    "confidence": 0.0
  }},
  "economic_impact": {{
    "title": "الأثر الاقتصادي",
    "title_en": "Economic Impact",
    "status": "...", "status_color": "...",
    "summary": "تقدير تكلفة التدخلات مقابل القيمة المعرضة للخطر",
    "details": ["تكلفة التدخل التقديرية", "العائد المتوقع"],
    "metrics": {{}},
    "confidence": 0.0
  }}
}}

⚠️ أعد JSON فقط بدون أي نص قبله أو بعده. جميع القيم النصية بالعربية مع المصطلحات التقنية بالإنجليزية بين قوسين. استبدل القيم ... بأرقام فعلية من البيانات المقدمة. اضبط confidence بين 0 و1 حسب اكتمال البيانات."""

    logger.info(
        "comprehensive_unified_analysis field=%s health=%s score=%d model=%s",
        req.field.id,
        health_class,
        health_score,
        MODEL_PRIMARY,
    )

    try:
        raw_text = await _run_agent(
            SYSTEM_PERSONA,
            unified_prompt,
            max_tokens=4000,
            model=MODEL_PRIMARY,
        )
    except Exception as exc:
        logger.error("Unified analysis LLM failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {exc}")

    # ── Parse JSON response ────────────────────────────────────────────────────
    parsed = _safe_parse_tier(raw_text, default_label="غير متاح")

    # Build sections from parsed dict
    def _section(key: str, default_title: str, default_title_en: str) -> SectionContent:
        s = parsed.get(key, {})
        if not isinstance(s, dict):
            s = {}
        return SectionContent(
            title=s.get("title", default_title),
            title_en=s.get("title_en", default_title_en),
            status=s.get("status", "moderate"),
            status_color=s.get("status_color", "yellow"),
            summary=s.get("summary", "التحليل غير متاح"),
            details=[d for d in s.get("details", []) if d] or [],
            metrics=s.get("metrics"),
            confidence=float(s.get("confidence", 0.5)),
        )

    sections = AnalysisSections(
        health_overview=_section("health_overview", "نظرة عامة على الصحة", "Health Overview"),
        vegetation_health=_section("vegetation_health", "صحة الغطاء النباتي", "Vegetation Health"),
        water_stress=_section("water_stress", "الإجهاد المائي والرطوبة", "Water Stress & Moisture"),
        growth_stage=_section("growth_stage", "مرحلة النمو", "Growth Stage"),
        nutrient_status=_section("nutrient_status", "حالة العناصر الغذائية", "Nutrient Status"),
        pest_disease_risk=_section("pest_disease_risk", "مخاطر الآفات والأمراض", "Pest & Disease Risk"),
        irrigation_recommendation=_section("irrigation_recommendation", "توصيات الري", "Irrigation Recommendations"),
        weather_impact=_section("weather_impact", "تأثير الطقس", "Weather Impact"),
        yield_prediction=_section("yield_prediction", "تقدير الإنتاجية", "Yield Prediction"),
        soil_health=_section("soil_health", "صحة التربة", "Soil Health"),
        historical_trends=_section("historical_trends", "الاتجاهات التاريخية", "Historical Trends"),
        action_plan=_section("action_plan", "خطة العمل", "Action Plan"),
        economic_impact=_section("economic_impact", "الأثر الاقتصادي", "Economic Impact"),
    )

    # Backward compat
    compat_status = sections.health_overview.details[:4]
    compat_recs = sections.action_plan.details[:5]

    # ── Assemble response ──────────────────────────────────────────────────────
    now_iso = datetime.now(UTC).isoformat()
    response = FieldAnalysisResponse(
        field_id=req.field.id,
        analyzed_at=now_iso,
        cached=False,
        health_score=health_score,
        health_class=health_class,
        health_confidence=health_confidence,
        imagery=req.imagery,
        sections=sections,
        indices_summary=indices_summary,
        satellite_date=req.satellite_date,
        cloud_cover_pct=req.cloud_cover_pct,
        data_sources=[
            s
            for s in [req.data_source, "openweather" if req.weather else None, "open-meteo" if req.meteo else None]
            if s
        ],
        indice=req.primary_indice,
        current_status=compat_status,
        recommendations=compat_recs,
    )

    # ── Store in Redis ─────────────────────────────────────────────────────────
    if redis:
        try:
            await redis.setex(cache_key, _CACHE_TTL_SECONDS, response.model_dump_json())
        except Exception as _se:
            logger.warning("Redis write failed: %s", _se)

    return response

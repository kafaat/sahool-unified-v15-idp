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

MODEL_FAST = os.environ.get("OPENROUTER_MODEL_FAST", "qwen/qwen3-next-80b-a3b-instruct:free")
MODEL_PRIMARY = os.environ.get("OPENROUTER_MODEL_PRIMARY", "qwen/qwen3-next-80b-a3b-instruct:free")


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
    "NDVI":        "مؤشر الغطاء النباتي الطبيعي (NDVI)",
    "EVI":         "مؤشر الغطاء النباتي المُحسَّن (EVI)",
    "EVI2":        "مؤشر الغطاء النباتي ثنائي النطاق (EVI2)",
    "NDWI":        "مؤشر محتوى الماء في النبات (NDWI)",
    "NDMI":        "مؤشر رطوبة النبات (NDMI)",
    "NDMI_STRESS": "مؤشر إجهاد رطوبة النبات (NDMI Stress)",
    "SAVI":        "مؤشر الغطاء مع تعديل التربة (SAVI)",
    "NDRE":        "مؤشر الحافة الحمراء للكلوروفيل (NDRE)",
    "NBR":         "نسبة الحرق المُعيَّرة (NBR)",
    "BAIS2":       "مؤشر المناطق المحروقة (BAIS2)",
    "BSI":         "مؤشر التربة العارية (BSI)",
    "MSAVI":       "مؤشر النبات المُعدَّل للتربة (MSAVI)",
    "GNDVI":       "مؤشر الغطاء النباتي الأخضر (GNDVI)",
    "LAI":         "مؤشر مساحة الأوراق (LAI)",
    "FAPAR":       "جزء الإشعاع الضوئي الممتص (FAPAR)",
    "FCOVER":      "كسر الغطاء النباتي (FCOVER)",
    "ARVI":        "مؤشر مقاومة الغلاف الجوي (ARVI)",
    "PSRI":        "مؤشر شيخوخة النبات (PSRI)",
    "RECI":        "مؤشر كلوروفيل الحافة الحمراء (RECI)",
    "NDCI":        "مؤشر الكلوروفيل المعياري (NDCI)",
    "MCARI":       "مؤشر امتصاص الكلوروفيل (MCARI)",
    "NDSI":        "مؤشر الثلج المعياري (NDSI)",
    "KNDVI":       "مؤشر NDVI النواة (kNDVI)",
    "NDYI":        "مؤشر الاصفرار (NDYI)",
    "MSI":         "مؤشر إجهاد الرطوبة (MSI)",
}

# Per-index interpretation context: ranges + what it measures + key thresholds
_INDICE_CONTEXT: dict[str, str] = {
    "NDVI": "النطاق −1 إلى +1. < 0.2 = تربة/غطاء حرج | 0.2–0.4 = نبات مجهد | 0.4–0.6 = نبات متوسط | > 0.6 = نبات صحي. يقيس الكثافة الخضرية العامة.",
    "EVI":  "النطاق −1 إلى +1. أكثر دقة من NDVI في المناطق الكثيفة وعند تشبع الإشارة. < 0.2 = حرج | 0.2–0.4 = مجهد | > 0.5 = صحي.",
    "EVI2": "مشابه لـ EVI لكن بدون نطاق أزرق. الحدود ذاتها.",
    "GNDVI":"النطاق −1 إلى +1. حساس لنقص النيتروجين أكثر من NDVI. < 0.25 = نقص شديد | 0.25–0.45 = نقص متوسط | > 0.5 = كافٍ.",
    "NDRE": "النطاق −1 إلى +1. مؤشر الكلوروفيل ومحتوى النيتروجين. < 0.1 = نقص حاد | 0.1–0.2 = نقص | > 0.2 = مقبول.",
    "SAVI": "النطاق −1 إلى +1. مُحسَّن للمناطق متفرقة النبات (جفاف، رعي). < 0.2 = غطاء ضعيف | 0.2–0.5 = متوسط | > 0.5 = جيد.",
    "MSAVI":"مشابه لـ SAVI مع تكيف ذاتي. مناسب للمناطق الجافة. نفس نطاقات SAVI.",
    "NDWI": "النطاق −1 إلى +1. يقيس محتوى الماء في النبات. < −0.1 = إجهاد مائي حاد | −0.1–0.1 = جفاف معتدل | > 0.2 = محتوى مائي كافٍ.",
    "NDMI": "النطاق −1 إلى +1. يقيس رطوبة الأوراق. < −0.2 = إجهاد مائي شديد | −0.2–0.0 = مجهد | > 0.0 = رطوبة مناسبة.",
    "NDMI_STRESS": "نفس NDMI مع تركيز على قيم الإجهاد السلبية.",
    "MSI":  "النطاق 0 إلى +3. عكسي: الأعلى = جفاف أشد. < 0.4 = رطوبة عالية | 0.4–1.0 = طبيعي | > 1.0 = إجهاد مائي.",
    "LAI":  "النطاق 0 إلى 8+ م²/م². 0–1 = غطاء ضعيف | 1–3 = متوسط | 3–6 = جيد | > 6 = كثيف جدًا.",
    "FAPAR":"النطاق 0–1. نسبة الإشعاع الممتص. < 0.3 = غطاء ضعيف | > 0.6 = غطاء جيد.",
    "FCOVER":"النطاق 0–1. نسبة تغطية الأرض. < 0.3 = تغطية ضعيفة | > 0.6 = تغطية جيدة.",
    "NBR":  "النطاق −1 إلى +1. يقيس الحرق والتلف. > 0.1 = نبات سليم | −0.1–0.1 = تلف خفيف | < −0.1 = حريق/تلف شديد.",
    "BAIS2":"النطاق 0–5+. مؤشر المساحات المحروقة. > 1.0 = حريق مؤكد.",
    "BSI":  "النطاق −1 إلى +1. يكشف التربة العارية. > 0 = تربة مكشوفة | < 0 = غطاء نباتي.",
    "ARVI": "مشابه لـ NDVI لكن مُصحَّح للغلاف الجوي. نفس نطاقات NDVI.",
    "PSRI": "النطاق −1 إلى +1. يقيس شيخوخة النبات. > 0.2 = شيخوخة/نضج متقدم | < 0 = نبات خضراء.",
    "NDYI": "يقيس الاصفرار. > 0.2 = اصفرار واضح ← نقص N أو مرض.",
    "RECI": "النطاق 0–15+. يقيس الكلوروفيل الكلي. < 2 = نقص | 2–5 = طبيعي | > 5 = وفير.",
    "NDCI": "النطاق −1 إلى +1. كلوروفيل في المسطحات المائية. > 0.2 = تركيز عالٍ.",
    "MCARI":"مشابه لـ RECI للكلوروفيل. القيم الأعلى = كلوروفيل أوفر.",
    "NDSI": "النطاق −1 إلى +1. يكشف الثلج. > 0.4 = غطاء ثلجي.",
    "KNDVI":"نسخة منقحة من NDVI. نفس نطاقات NDVI لكن أكثر استقرارًا مع الغطاء الكثيف.",
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
        return f"""أنت الدكتور خالد الرشيدي. حلِّل صحة المحصول لهذا الحقل بناءً على بيانات الأرصاد الزراعية الكاملة المتاحة وأنتج 4 نقاط دقيقة.

<بيانات_الحقل>
الحقل   : {field.nameAr or field.name}
الموقع  : {field.lat:.4f}°ش، {field.lng:.4f}°ش
المحصول : {field.cropType or 'غير محدد'} | المساحة: {_fmt(field.areaHa, 1, 'هـ')} | التربة: {field.soilType or 'غير محدد'}
</بيانات_الحقل>

<البيانات_البيئية_المتاحة>
{env_block}
</البيانات_البيئية_المتاحة>

<المؤشر_المطلوب>
المؤشر: {indice_label}
مرجع التفسير: {ctx}
</المؤشر_المطلوب>

اكتب 4 نقاط فقط تبدأ كل منها بـ (•):
• نقطة 1: قيّم الإجهاد المائي للمحصول بناءً على رطوبة التربة وET₀ — اذكر الأرقام واتخذ قرارًا واضحًا (يحتاج ري/لا يحتاج).
• نقطة 2: قيّم الإجهاد الحراري والضوئي بناءً على درجة الحرارة والإشعاع الشمسي والرطوبة النسبية.
• نقطة 3: استنتج الحالة المحتملة لـ {indice_label} تقديريًا من المؤشرات البيئية مع بيان نطاق القيمة المتوقعة.
• نقطة 4: أعطِ تصنيفًا إجماليًا لصحة المحصول (حرج/مجهد/متوسط/صحي) مع التوصية الميدانية الأعلى أولوية.

⚠️ 4 نقاط فقط — لا أكثر ولا أقل. أرقام ووحدات في كل نقطة. بدون عناوين. باللغة العربية حصرًا."""

    return f"""أنت الدكتور خالد الرشيدي. حلِّل مؤشر {indice_label} للحقل أدناه وأنتج 4 نقاط ساتلية دقيقة.

<بيانات_الحقل>
الحقل   : {field.nameAr or field.name}
الموقع  : {field.lat:.4f}°ش، {field.lng:.4f}°ش
المحصول : {field.cropType or 'غير محدد'} | المساحة: {_fmt(field.areaHa, 1, 'هـ')} | التربة: {field.soilType or 'غير محدد'}
</بيانات_الحقل>

<قراءة_{req.indice}>
القيمة المتوسطة : {val_str}{range_str}
تاريخ الصورة   : {cdse.date or 'غير محدد'}
الغطاء السحابي : {_fmt(cdse.cloudCover, 1, '%')}
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
  درجة الحرارة    : {_fmt(w.temperature, 1, '°م')} (تبدو كـ {_fmt(w.feelsLike, 1, '°م')})
  الرطوبة النسبية : {_fmt(w.humidity, 0, '%')}
  سرعة الرياح    : {_fmt(w.windSpeed, 1, 'م/ث')} باتجاه {_fmt(w.windDirection, 0, '°')}
  هطول الأمطار   : {_fmt(w.precipitation, 2, 'مم')} (الساعة الأخيرة)
  الغطاء السحابي : {_fmt(w.cloudCover, 0, '%')}
  الضغط الجوي    : {_fmt(w.pressure, 0, 'هكتوباسكال')}
  مدى الرؤية     : {_fmt(w.visibility, 0, 'كم')}
  الحالة الجوية  : {w.description or 'غير متوفر'}"""

    meteo_block = "  ── OpenMeteo: غير متوفر ──"
    if m:
        meteo_block = f"""  ── بيانات OpenMeteo الحالية ──
  درجة الحرارة (2م)        : {_fmt(m.temperature2m, 1, '°م')}
  الرطوبة النسبية (2م)      : {_fmt(m.relativeHumidity2m, 0, '%')}
  هطول الأمطار              : {_fmt(m.precipitation, 2, 'مم')}
  سرعة الرياح (10م)         : {_fmt(m.windSpeed10m, 1, 'م/ث')}
  رطوبة التربة (0–1 سم)     : {_fmt(m.soilMoisture0to1cm, 3, 'م³/م³')}
  التبخر-النتح ET₀ (FAO-56) : {_fmt(m.et0FaoEvapotranspiration, 2, 'مم/يوم')}
  ضغط السطح                 : {_fmt(m.surfacePressure, 0, 'هكتوباسكال')}
  الغطاء السحابي             : {_fmt(m.cloudCover, 0, '%')}
  الإشعاع الشمسي القصير     : {_fmt(m.shortwaveRadiation, 1, 'واط/م²')}"""

    return f"""أنت الدكتور خالد الرشيدي. حلِّل الطقس والأرصاد الزراعية لهذا الحقل وأنتج 4 نقاط طقسية دقيقة.

<بيانات_الحقل>
الحقل: {field.nameAr or field.name} | المحصول: {field.cropType or 'غير محدد'} | {_fmt(field.areaHa, 1, 'هـ')}
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
  درجة الحرارة      : {_fmt(w.temperature, 1, '°م')} (تبدو كـ {_fmt(w.feelsLike, 1, '°م')})
  الرطوبة النسبية   : {_fmt(w.humidity, 0, '%')}
  سرعة الرياح       : {_fmt(w.windSpeed, 1, 'م/ث')} | اتجاه {_fmt(w.windDirection, 0, '°')}
  هطول الأمطار      : {_fmt(w.precipitation, 2, 'مم/ساعة')}
  الغطاء السحابي    : {_fmt(w.cloudCover, 0, '%')}
  الضغط الجوي       : {_fmt(w.pressure, 0, 'هكتوباسكال')}
  مدى الرؤية        : {_fmt(w.visibility, 0, 'كم')}
  الحالة الجوية     : {w.description or 'غير متوفر'}"""

    meteo_lines = "  ── OpenMeteo: غير متوفر ──"
    if m:
        meteo_lines = f"""  ── بيانات OpenMeteo الحالية ──
  درجة الحرارة (2م)         : {_fmt(m.temperature2m, 1, '°م')}
  الرطوبة النسبية (2م)       : {_fmt(m.relativeHumidity2m, 0, '%')}
  هطول الأمطار               : {_fmt(m.precipitation, 2, 'مم')}
  سرعة الرياح (10م)          : {_fmt(m.windSpeed10m, 1, 'م/ث')}
  رطوبة التربة (0–1 سم)      : {_fmt(m.soilMoisture0to1cm, 3, 'م³/م³')}
  التبخر-النتح ET₀ (FAO-56)  : {_fmt(m.et0FaoEvapotranspiration, 2, 'مم/يوم')}
  ضغط السطح                  : {_fmt(m.surfacePressure, 0, 'هكتوباسكال')}
  الغطاء السحابي              : {_fmt(m.cloudCover, 0, '%')}
  الإشعاع الشمسي القصير      : {_fmt(m.shortwaveRadiation, 1, 'واط/م²')}"""

    ctx = _indice_context(req.indice)

    return f"""أنت الدكتور خالد الرشيدي. بناءً على جميع البيانات أدناه، أنتج 5 توصيات زراعية فورية قابلة للتنفيذ.

<بيانات_الحقل_الكاملة>
الحقل: {field.nameAr or field.name} | المحصول: {field.cropType or 'غير محدد'} | {_fmt(field.areaHa, 1, 'هـ')} | التربة: {field.soilType or 'غير محدد'}
الموقع: {field.lat:.4f}°ش، {field.lng:.4f}°ش

── {indice_label} (تاريخ: {cdse.date or 'غير محدد'}) ──
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

    # Launch all three agents as concurrent tasks immediately
    tasks = [
        asyncio.create_task(
            _run_agent(SYSTEM_PERSONA, veg_prompt,     max_tokens=700,  model=MODEL_FAST),
            name="vegetation",
        ),
        asyncio.create_task(
            _run_agent(SYSTEM_PERSONA, weather_prompt, max_tokens=700,  model=MODEL_FAST),
            name="weather",
        ),
        asyncio.create_task(
            _run_agent(SYSTEM_PERSONA, reco_prompt,    max_tokens=1000, model=MODEL_PRIMARY),
            name="recommendations",
        ),
    ]
    try:
        veg_text, weather_text, reco_text = await asyncio.gather(*tasks)
    except Exception as exc:
        for t in tasks:
            if not t.done():
                t.cancel()
        logger.error("Multi-agent analysis failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {exc}",
        )

    # Vegetation: 4 bullets always (even when CDSE null — prompt uses meteo data).
    # Weather: 4. Recommendations: 5.
    current_status_bullets = _parse_bullets(veg_text, 4) + _parse_bullets(weather_text, 4)
    recommendation_bullets = _parse_bullets(reco_text, 5)

    from datetime import datetime, timezone

    return AnalyzeFieldResponse(
        field_id=req.field.id,
        indice=req.indice,
        current_status=current_status_bullets,
        recommendations=recommendation_bullets,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )

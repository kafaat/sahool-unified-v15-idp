#!/usr/bin/env python3
"""
SAHOOL Astronomical Calendar Service
خدمة التقويم الفلكي الزراعي - سهول

التقويم الفلكي التقليدي اليمني للزراعة يجمع بين:
- حسابات فلكية دقيقة (مراحل القمر)
- منازل النجوم (المنازل القمرية الـ 28)
- التقويم الهجري
- توقيتات الزراعة التقليدية
- الأبراج الزراعية

Port: 8111
Version: 16.0.0
"""

# Version constant - use this throughout the application
VERSION = "16.0.0"

import math
import os
import sys
from datetime import UTC, datetime, timedelta

import httpx
from fastapi import FastAPI, HTTPException, Query

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# التطبيق الرئيسي
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="SAHOOL Astronomical Calendar Service",
    description="""
    خدمة التقويم الفلكي الزراعي التقليدي اليمني

    ## المميزات:
    - 🌙 حساب مراحل القمر بدقة عالية
    - ⭐ منازل النجوم الـ 28 (المنازل القمرية)
    - 📅 التقويم الهجري
    - 🌱 توقيتات الزراعة التقليدية
    - ♈ الأبراج الزراعية
    - 🔗 تكامل مع خدمة الطقس

    ## الاستخدام:
    يستخدم المزارعون اليمنيون هذا التقويم منذ آلاف السنين
    لتحديد أفضل أوقات الزراعة والحصاد.
    """,
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass  # Shared module not available in standalone mode

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    _has_tenant_middleware = True
except ImportError:
    _has_tenant_middleware = False

# CORS middleware - secure origins from environment
CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:8080",
).split(",")

# Weather service URL - configurable via environment variable
WEATHER_SERVICE_URL = os.getenv(
    "WEATHER_SERVICE_URL",
    "http://weather-service:8092",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

if _has_tenant_middleware:
    app.add_middleware(TenantContextMiddleware)


# ═══════════════════════════════════════════════════════════════════════════════
# الثوابت الفلكية
# ═══════════════════════════════════════════════════════════════════════════════

# الأشهر الهجرية
HIJRI_MONTHS = {
    1: {"name": "محرم", "name_en": "Muharram", "days": 30},
    2: {"name": "صفر", "name_en": "Safar", "days": 29},
    3: {"name": "ربيع الأول", "name_en": "Rabi al-Awwal", "days": 30},
    4: {"name": "ربيع الثاني", "name_en": "Rabi al-Thani", "days": 29},
    5: {"name": "جمادى الأولى", "name_en": "Jumada al-Awwal", "days": 30},
    6: {"name": "جمادى الآخرة", "name_en": "Jumada al-Thani", "days": 29},
    7: {"name": "رجب", "name_en": "Rajab", "days": 30},
    8: {"name": "شعبان", "name_en": "Shaban", "days": 29},
    9: {"name": "رمضان", "name_en": "Ramadan", "days": 30},
    10: {"name": "شوال", "name_en": "Shawwal", "days": 29},
    11: {"name": "ذو القعدة", "name_en": "Dhu al-Qadah", "days": 30},
    12: {
        "name": "ذو الحجة",
        "name_en": "Dhu al-Hijjah",
        "days": 29,
    },  # 30 في السنة الكبيسة
}

# المنازل القمرية الـ 28 (منازل النجوم)
LUNAR_MANSIONS = {
    1: {
        "name": "الشرطين",
        "name_en": "Al-Sharatain",
        "constellation": "الحمل",
        "constellation_en": "Aries",
        "element": "نار",
        "farming": "زراعة ممتازة",
        "farming_score": 9,
        "crops": ["قمح", "شعير", "ذرة"],
        "activities": ["زراعة", "تطعيم"],
        "avoid": [],
        "description": "منزلة خصبة جداً، مناسبة لزراعة الحبوب",
    },
    2: {
        "name": "البطين",
        "name_en": "Al-Butain",
        "constellation": "الحمل",
        "constellation_en": "Aries",
        "element": "نار",
        "farming": "زراعة جيدة",
        "farming_score": 7,
        "crops": ["خضروات", "بقوليات"],
        "activities": ["زراعة", "ري"],
        "avoid": ["حصاد"],
        "description": "مناسبة للخضروات الورقية",
    },
    3: {
        "name": "الثريا",
        "name_en": "Al-Thuraya",
        "constellation": "الثور",
        "constellation_en": "Taurus",
        "element": "أرض",
        "farming": "ممتازة للزراعة",
        "farming_score": 10,
        "crops": ["جميع المحاصيل"],
        "activities": ["زراعة", "غرس", "تطعيم", "تقليم"],
        "avoid": [],
        "description": "أفضل المنازل للزراعة على الإطلاق - نجم الثريا المبارك",
    },
    4: {
        "name": "الدبران",
        "name_en": "Al-Dabaran",
        "constellation": "الثور",
        "constellation_en": "Taurus",
        "element": "أرض",
        "farming": "جيدة جداً",
        "farming_score": 8,
        "crops": ["فواكه", "أشجار"],
        "activities": ["غرس الأشجار", "تطعيم"],
        "avoid": ["حصاد الحبوب"],
        "description": "مثالية لغرس الأشجار المثمرة",
    },
    5: {
        "name": "الهقعة",
        "name_en": "Al-Haq'ah",
        "constellation": "الجوزاء",
        "constellation_en": "Gemini",
        "element": "هواء",
        "farming": "متوسطة",
        "farming_score": 5,
        "crops": ["زهور", "نباتات عطرية"],
        "activities": ["جمع البذور"],
        "avoid": ["زراعة", "ري"],
        "description": "مناسبة للنباتات العطرية فقط",
    },
    6: {
        "name": "الهنعة",
        "name_en": "Al-Han'ah",
        "constellation": "الجوزاء",
        "constellation_en": "Gemini",
        "element": "هواء",
        "farming": "ضعيفة",
        "farming_score": 3,
        "crops": [],
        "activities": ["مكافحة آفات"],
        "avoid": ["زراعة", "غرس"],
        "description": "غير مناسبة للزراعة - مناسبة للراحة",
    },
    7: {
        "name": "الذراع",
        "name_en": "Al-Dhira",
        "constellation": "السرطان",
        "constellation_en": "Cancer",
        "element": "ماء",
        "farming": "ممتازة للري",
        "farming_score": 8,
        "crops": ["خيار", "بطيخ", "شمام"],
        "activities": ["ري", "زراعة القرعيات"],
        "avoid": ["حصاد"],
        "description": "ممتازة لزراعة المحاصيل التي تحتاج ماء كثير",
    },
    8: {
        "name": "النثرة",
        "name_en": "Al-Nathrah",
        "constellation": "السرطان",
        "constellation_en": "Cancer",
        "element": "ماء",
        "farming": "جيدة",
        "farming_score": 7,
        "crops": ["خضروات مائية"],
        "activities": ["ري", "تسميد"],
        "avoid": ["حصاد الحبوب"],
        "description": "مناسبة للتسميد والري",
    },
    9: {
        "name": "الطرف",
        "name_en": "Al-Tarf",
        "constellation": "الأسد",
        "constellation_en": "Leo",
        "element": "نار",
        "farming": "ضعيفة",
        "farming_score": 2,
        "crops": [],
        "activities": ["مكافحة حشرات"],
        "avoid": ["زراعة", "ري", "غرس"],
        "description": "منزلة حارة - تجنب الزراعة",
    },
    10: {
        "name": "الجبهة",
        "name_en": "Al-Jabhah",
        "constellation": "الأسد",
        "constellation_en": "Leo",
        "element": "نار",
        "farming": "ضعيفة",
        "farming_score": 2,
        "crops": [],
        "activities": ["حصاد"],
        "avoid": ["زراعة", "ري"],
        "description": "مناسبة للحصاد فقط",
    },
    11: {
        "name": "الزبرة",
        "name_en": "Al-Zubrah",
        "constellation": "الأسد",
        "constellation_en": "Leo",
        "element": "نار",
        "farming": "ضعيفة",
        "farming_score": 3,
        "crops": ["فلفل", "بهارات"],
        "activities": ["حصاد", "تجفيف"],
        "avoid": ["زراعة"],
        "description": "مناسبة للتجفيف والتخزين",
    },
    12: {
        "name": "الصرفة",
        "name_en": "Al-Sarfah",
        "constellation": "الأسد",
        "constellation_en": "Leo",
        "element": "نار",
        "farming": "متوسطة",
        "farming_score": 5,
        "crops": ["طماطم", "باذنجان"],
        "activities": ["تقليم"],
        "avoid": ["غرس أشجار"],
        "description": "بداية تحسن الظروف",
    },
    13: {
        "name": "العواء",
        "name_en": "Al-Awwa",
        "constellation": "العذراء",
        "constellation_en": "Virgo",
        "element": "أرض",
        "farming": "جيدة جداً",
        "farming_score": 8,
        "crops": ["حبوب", "بقوليات"],
        "activities": ["زراعة", "حرث"],
        "avoid": [],
        "description": "ممتازة لتحضير الأرض والزراعة",
    },
    14: {
        "name": "السماك",
        "name_en": "Al-Simak",
        "constellation": "العذراء",
        "constellation_en": "Virgo",
        "element": "أرض",
        "farming": "ممتازة",
        "farming_score": 9,
        "crops": ["جميع المحاصيل"],
        "activities": ["زراعة", "غرس", "تطعيم"],
        "avoid": [],
        "description": "من أفضل المنازل للزراعة",
    },
    15: {
        "name": "الغفر",
        "name_en": "Al-Ghafr",
        "constellation": "الميزان",
        "constellation_en": "Libra",
        "element": "هواء",
        "farming": "جيدة",
        "farming_score": 6,
        "crops": ["زهور", "نباتات زينة"],
        "activities": ["زراعة الزهور"],
        "avoid": ["غرس أشجار"],
        "description": "مناسبة للنباتات الجمالية",
    },
    16: {
        "name": "الزبانا",
        "name_en": "Al-Zubana",
        "constellation": "الميزان",
        "constellation_en": "Libra",
        "element": "هواء",
        "farming": "متوسطة",
        "farming_score": 5,
        "crops": ["خضروات ورقية"],
        "activities": ["ري خفيف"],
        "avoid": ["زراعة ثقيلة"],
        "description": "مناسبة للخضروات الورقية",
    },
    17: {
        "name": "الإكليل",
        "name_en": "Al-Iklil",
        "constellation": "العقرب",
        "constellation_en": "Scorpio",
        "element": "ماء",
        "farming": "جيدة للري",
        "farming_score": 7,
        "crops": ["جذريات", "بطاطس"],
        "activities": ["ري", "زراعة الجذور"],
        "avoid": ["حصاد"],
        "description": "مثالية لزراعة المحاصيل الجذرية",
    },
    18: {
        "name": "القلب",
        "name_en": "Al-Qalb",
        "constellation": "العقرب",
        "constellation_en": "Scorpio",
        "element": "ماء",
        "farming": "ضعيفة",
        "farming_score": 3,
        "crops": [],
        "activities": ["مكافحة آفات"],
        "avoid": ["زراعة", "غرس"],
        "description": "قلب العقرب - تجنب الزراعة",
    },
    19: {
        "name": "الشولة",
        "name_en": "Al-Shaulah",
        "constellation": "العقرب",
        "constellation_en": "Scorpio",
        "element": "ماء",
        "farming": "ضعيفة",
        "farming_score": 2,
        "crops": [],
        "activities": ["راحة"],
        "avoid": ["جميع الأنشطة الزراعية"],
        "description": "ذنب العقرب - أسوأ المنازل للزراعة",
    },
    20: {
        "name": "النعائم",
        "name_en": "Al-Na'aim",
        "constellation": "القوس",
        "constellation_en": "Sagittarius",
        "element": "نار",
        "farming": "متوسطة",
        "farming_score": 5,
        "crops": ["علف"],
        "activities": ["حرث"],
        "avoid": ["زراعة دقيقة"],
        "description": "مناسبة لتحضير الأرض",
    },
    21: {
        "name": "البلدة",
        "name_en": "Al-Baldah",
        "constellation": "القوس",
        "constellation_en": "Sagittarius",
        "element": "نار",
        "farming": "جيدة",
        "farming_score": 6,
        "crops": ["حبوب"],
        "activities": ["بذر"],
        "avoid": [],
        "description": "مناسبة للبذر والتحضير",
    },
    22: {
        "name": "سعد الذابح",
        "name_en": "Sa'd al-Dhabih",
        "constellation": "الجدي",
        "constellation_en": "Capricorn",
        "element": "أرض",
        "farming": "جيدة",
        "farming_score": 7,
        "crops": ["جذريات", "بصل", "ثوم"],
        "activities": ["زراعة", "حصاد"],
        "avoid": [],
        "description": "مناسبة للمحاصيل تحت الأرض",
    },
    23: {
        "name": "سعد بلع",
        "name_en": "Sa'd Bula",
        "constellation": "الجدي",
        "constellation_en": "Capricorn",
        "element": "أرض",
        "farming": "جيدة جداً",
        "farming_score": 8,
        "crops": ["أشجار", "فواكه"],
        "activities": ["غرس", "تطعيم"],
        "avoid": [],
        "description": "ممتازة لغرس الأشجار",
    },
    24: {
        "name": "سعد السعود",
        "name_en": "Sa'd al-Su'ud",
        "constellation": "الدلو",
        "constellation_en": "Aquarius",
        "element": "هواء",
        "farming": "ممتازة",
        "farming_score": 10,
        "crops": ["جميع المحاصيل"],
        "activities": ["جميع الأنشطة"],
        "avoid": [],
        "description": "أسعد المنازل - مباركة لجميع الأعمال",
    },
    25: {
        "name": "سعد الأخبية",
        "name_en": "Sa'd al-Akhbiyah",
        "constellation": "الدلو",
        "constellation_en": "Aquarius",
        "element": "هواء",
        "farming": "جيدة",
        "farming_score": 7,
        "crops": ["خضروات", "زهور"],
        "activities": ["زراعة", "ري"],
        "avoid": [],
        "description": "مناسبة للزراعة والتجميل",
    },
    26: {
        "name": "المقدم",
        "name_en": "Al-Muqaddam",
        "constellation": "الحوت",
        "constellation_en": "Pisces",
        "element": "ماء",
        "farming": "جيدة للري",
        "farming_score": 7,
        "crops": ["أرز", "قصب"],
        "activities": ["ري", "زراعة مائية"],
        "avoid": ["حصاد"],
        "description": "ممتازة للمحاصيل المائية",
    },
    27: {
        "name": "المؤخر",
        "name_en": "Al-Mu'akhkhar",
        "constellation": "الحوت",
        "constellation_en": "Pisces",
        "element": "ماء",
        "farming": "جيدة",
        "farming_score": 6,
        "crops": ["سمك", "طحالب"],
        "activities": ["استزراع مائي"],
        "avoid": ["زراعة برية"],
        "description": "للاستزراع المائي",
    },
    28: {
        "name": "الرشاء",
        "name_en": "Al-Risha",
        "constellation": "الحوت",
        "constellation_en": "Pisces",
        "element": "ماء",
        "farming": "جيدة",
        "farming_score": 7,
        "crops": ["خضروات مائية"],
        "activities": ["ري", "تحضير"],
        "avoid": [],
        "description": "انتهاء الدورة - تحضير للموسم الجديد",
    },
}

# مراحل القمر
MOON_PHASES = {
    "new_moon": {
        "name": "المحاق",
        "name_en": "New Moon",
        "icon": "🌑",
        "farming_good": False,
    },
    "waxing_crescent": {
        "name": "الهلال المتزايد",
        "name_en": "Waxing Crescent",
        "icon": "🌒",
        "farming_good": True,
    },
    "first_quarter": {
        "name": "التربيع الأول",
        "name_en": "First Quarter",
        "icon": "🌓",
        "farming_good": True,
    },
    "waxing_gibbous": {
        "name": "الأحدب المتزايد",
        "name_en": "Waxing Gibbous",
        "icon": "🌔",
        "farming_good": True,
    },
    "full_moon": {
        "name": "البدر",
        "name_en": "Full Moon",
        "icon": "🌕",
        "farming_good": True,
    },
    "waning_gibbous": {
        "name": "الأحدب المتناقص",
        "name_en": "Waning Gibbous",
        "icon": "🌖",
        "farming_good": False,
    },
    "last_quarter": {
        "name": "التربيع الأخير",
        "name_en": "Last Quarter",
        "icon": "🌗",
        "farming_good": False,
    },
    "waning_crescent": {
        "name": "الهلال المتناقص",
        "name_en": "Waning Crescent",
        "icon": "🌘",
        "farming_good": False,
    },
}

# الأمثال الزراعية اليمنية التقليدية
YEMENI_FARMING_PROVERBS = {
    "general": [
        {
            "proverb": "إذا طلعت الثريا عشاءً، فاكفِ يدك من الماء",
            "meaning": "عند طلوع نجم الثريا مساءً، ينتهي موسم الري الصيفي",
            "application": "توقيت الري",
            "mansion": "الثريا",
        },
        {
            "proverb": "الزرع في الثريا، والحصاد في الجوزاء",
            "meaning": "أفضل وقت للزراعة في منزلة الثريا، والحصاد في الجوزاء",
            "application": "توقيت الزراعة والحصاد",
            "mansion": "الثريا",
        },
        {
            "proverb": "اللي يزرع في القمر المتزايد، محصوله متزايد",
            "meaning": "الزراعة في فترة تزايد القمر تعطي محصولاً أفضل",
            "application": "توقيت الزراعة",
            "mansion": None,
        },
        {
            "proverb": "من زرع في المحاق، حصد البواق",
            "meaning": "تجنب الزراعة في وقت المحاق (اختفاء القمر)",
            "application": "تجنب الزراعة",
            "mansion": None,
        },
        {
            "proverb": "سعد السعود، يخرج البرد من العود",
            "meaning": "في منزلة سعد السعود ينتهي البرد ويبدأ الدفء",
            "application": "توقيت الموسم",
            "mansion": "سعد السعود",
        },
        {
            "proverb": "إذا طلع سهيل، برد الليل وأقبل السيل",
            "meaning": "طلوع نجم سهيل يعلن بداية موسم الأمطار",
            "application": "توقيت الأمطار",
            "mansion": None,
        },
        {
            "proverb": "في الشولة لا تزرع ولا تحول",
            "meaning": "تجنب الزراعة والتطعيم في منزلة الشولة",
            "application": "تجنب الزراعة",
            "mansion": "الشولة",
        },
        {
            "proverb": "العواء خير ما طلعت على الزراعة والبناء",
            "meaning": "منزلة العواء ممتازة للزراعة والبناء",
            "application": "أفضلية الزراعة",
            "mansion": "العواء",
        },
        {
            "proverb": "إذا اشتد الحر، فاستعن بالسحر",
            "meaning": "في الحر الشديد، قم بالعمل الزراعي في الفجر",
            "application": "توقيت العمل",
            "mansion": None,
        },
        {
            "proverb": "الزرع يريد أربعين يوماً للجذر، وأربعين للساق",
            "meaning": "المحصول يحتاج 40 يوماً لتكوين الجذور و40 للساق",
            "application": "دورة النمو",
            "mansion": None,
        },
        {
            "proverb": "الأرض تحب من يحبها",
            "meaning": "العناية بالأرض تعود بالخير",
            "application": "العناية بالتربة",
            "mansion": None,
        },
        {
            "proverb": "زرعة الصبر تثمر العسل",
            "meaning": "الصبر في الزراعة يؤتي ثماره",
            "application": "الصبر",
            "mansion": None,
        },
        {
            "proverb": "إذا غاب المطر، فالدعاء والصبر",
            "meaning": "التوكل في أوقات الجفاف",
            "application": "الجفاف",
            "mansion": None,
        },
        {
            "proverb": "العين على الغيث، واليد في الأرض",
            "meaning": "الاستعداد للمطر مع العمل",
            "application": "التحضير",
            "mansion": None,
        },
        {
            "proverb": "ما كل بذرة تنبت، ولا كل زرعة تثمر",
            "meaning": "تقبل الخسائر الطبيعية",
            "application": "الواقعية",
            "mansion": None,
        },
        {
            "proverb": "الماء الكثير يغرق الزرع، والماء القليل يحرقه",
            "meaning": "الاعتدال في الري ضروري",
            "application": "إدارة الري",
            "mansion": None,
        },
        {
            "proverb": "أول الزرع نية، وآخره عناية",
            "meaning": "النية الصالحة والعناية المستمرة أساس النجاح",
            "application": "الإخلاص في العمل",
            "mansion": None,
        },
        {
            "proverb": "الأرض السوداء كنز، والأرض الحمراء فخر",
            "meaning": "كل نوع تربة له ميزته الخاصة",
            "application": "معرفة التربة",
            "mansion": None,
        },
        {
            "proverb": "اسقِ زرعك قبل الظهيرة، أو بعد العصر",
            "meaning": "تجنب الري في حرارة النهار",
            "application": "أوقات الري",
            "mansion": None,
        },
        {
            "proverb": "البذرة الطيبة في الأرض الطيبة، خير من ألف في الأرض الرديئة",
            "meaning": "جودة التربة أهم من كمية البذور",
            "application": "اختيار الأرض",
            "mansion": None,
        },
        {
            "proverb": "من أراد الثمر، فليصبر على الشجر",
            "meaning": "الأشجار تحتاج صبراً وانتظاراً",
            "application": "زراعة الأشجار",
            "mansion": None,
        },
        {
            "proverb": "الشمس والتراب والماء، أركان الزراعة الثلاثة",
            "meaning": "العناصر الأساسية للنمو",
            "application": "أساسيات الزراعة",
            "mansion": None,
        },
        {
            "proverb": "من حرث في الدبران، جنى الخير والأمان",
            "meaning": "منزلة الدبران مباركة للحراثة",
            "application": "توقيت الحراثة",
            "mansion": "الدبران",
        },
        {
            "proverb": "السماد للأرض كالغذاء للبدن",
            "meaning": "التسميد ضروري لخصوبة التربة",
            "application": "التسميد",
            "mansion": None,
        },
        {
            "proverb": "الحرث العميق يخرج الخير الدفين",
            "meaning": "الحراثة الجيدة تحسن الإنتاج",
            "application": "عمق الحراثة",
            "mansion": None,
        },
    ],
    "by_crop": {
        "قمح": [
            {
                "proverb": "القمح يُزرع في صفر، ويُحصد في جمادى",
                "meaning": "أفضل وقت لزراعة القمح شهر صفر الهجري",
                "application": "توقيت زراعة القمح",
            },
            {
                "proverb": "لا تزرع القمح إلا والقمر متزايد",
                "meaning": "زراعة القمح في القمر المتزايد لمحصول أفضل",
                "application": "مرحلة القمر المناسبة",
            },
        ],
        "بن": [
            {
                "proverb": "البن يحب الظل والندى",
                "meaning": "شجرة البن تحتاج الظل والرطوبة العالية",
                "application": "متطلبات النمو",
            },
            {
                "proverb": "قطف البن في الثريا، وجففه في الجوزاء",
                "meaning": "أفضل وقت لقطف البن في منزلة الثريا",
                "application": "توقيت الحصاد",
            },
            {
                "proverb": "البن ثلاث سنين صبر، وسبعين سنة خير",
                "meaning": "شجرة البن تحتاج صبراً ولكنها تعطي لسنوات طويلة",
                "application": "الاستثمار طويل الأمد",
            },
        ],
        "ذرة": [
            {
                "proverb": "الذرة تُزرع مع السيل، وتُحصد قبل الويل",
                "meaning": "زراعة الذرة مع بداية الأمطار وحصادها قبل السيول الكبيرة",
                "application": "توقيت الزراعة والحصاد",
            },
            {
                "proverb": "الذرة بنت الماء والشمس",
                "meaning": "الذرة تحتاج ماء وفير وشمس قوية",
                "application": "متطلبات النمو",
            },
        ],
        "بصل": [
            {
                "proverb": "البصل والثوم في القمر المتناقص",
                "meaning": "المحاصيل الجذرية تُزرع في القمر المتناقص",
                "application": "مرحلة القمر المناسبة",
            },
            {
                "proverb": "البصل يُزرع في برد، ويُحصد في حر",
                "meaning": "البصل يزرع شتاءً ويحصد صيفاً",
                "application": "توقيت الزراعة",
            },
        ],
        "عنب": [
            {
                "proverb": "العنب في الربيع يُغرس، وفي الصيف يُقطف",
                "meaning": "غرس الكروم في الربيع وحصاد العنب في الصيف",
                "application": "دورة العنب السنوية",
            },
            {
                "proverb": "التقليم في الشتاء، والحصاد في الحر",
                "meaning": "تقليم الكروم شتاءً لحصاد وفير صيفاً",
                "application": "التقليم",
            },
            {
                "proverb": "الكرمة تحب التراب الأحمر والماء المعتدل",
                "meaning": "العنب ينمو جيداً في التربة الحمراء مع ري متوازن",
                "application": "اختيار الموقع",
            },
        ],
        "نخيل": [
            {
                "proverb": "النخلة رأسها في النار ورجلها في الماء",
                "meaning": "النخل يحتاج حرارة عالية في الأعلى ورطوبة في الجذور",
                "application": "متطلبات النخيل",
            },
            {
                "proverb": "التلقيح في الربيع، والجداد في الصيف",
                "meaning": "تلقيح النخل ربيعاً وحصاد التمر صيفاً",
                "application": "توقيت العمليات",
            },
            {
                "proverb": "النخلة بنت العناية والسقاية",
                "meaning": "النخل يحتاج رعاية مستمرة وري منتظم",
                "application": "العناية بالنخيل",
            },
        ],
        "قات": [
            {
                "proverb": "القات يحب الماء الدائم والظل الخفيف",
                "meaning": "القات يحتاج ري مستمر وظل جزئي",
                "application": "متطلبات القات",
            },
            {
                "proverb": "قطاف القات في الفجر أطيب وأنضر",
                "meaning": "أفضل وقت لقطف القات الفجر",
                "application": "وقت القطف",
            },
            {
                "proverb": "القات في الأرض السوداء أخضر وأحلى",
                "meaning": "التربة الخصبة تنتج قات أفضل",
                "application": "اختيار التربة",
            },
        ],
        "طماطم": [
            {
                "proverb": "الطماطم تحب الشمس ولا تحب الصقيع",
                "meaning": "الطماطم محصول صيفي يخشى البرد",
                "application": "توقيت الزراعة",
            },
            {
                "proverb": "زرع الطماطم في الربيع، واقطفها في الصيف",
                "meaning": "الطماطم تزرع ربيعاً وتحصد صيفاً",
                "application": "دورة الزراعة",
            },
        ],
        "بطاطس": [
            {
                "proverb": "البطاطس تُزرع في القمر المتناقص لدرنات أكبر",
                "meaning": "زراعة البطاطس في القمر المتناقص تعطي درنات أفضل",
                "application": "توقيت الزراعة",
            },
            {
                "proverb": "البطاطس بنت البرد والتراب الهش",
                "meaning": "البطاطس تنمو جيداً في الجو البارد والتربة الخفيفة",
                "application": "الظروف المثالية",
            },
        ],
        "موز": [
            {
                "proverb": "الموز يحب الماء الكثير والجو الدافئ",
                "meaning": "الموز يحتاج ري غزير ودفء مستمر",
                "application": "متطلبات الموز",
            },
            {
                "proverb": "شجرة الموز مرة واحدة، ثم يأتي الخلف",
                "meaning": "الموز يثمر مرة واحدة ثم تنمو خلفات جديدة",
                "application": "دورة الإنتاج",
            },
        ],
    },
    "by_season": {
        "الصيف": [
            {
                "proverb": "صيف الحاجة، وشتاء الزراعة",
                "meaning": "الصيف للاحتياج والشتاء للزراعة",
                "application": "تخطيط المواسم",
            },
        ],
        "الخريف": [
            {
                "proverb": "في الخريف اجمع وفي الشتاء ازرع",
                "meaning": "الخريف للحصاد والتجميع",
                "application": "تخطيط المواسم",
            },
        ],
        "الشتاء": [
            {
                "proverb": "المطر في شتاء، خير من ألف دعاء",
                "meaning": "أمطار الشتاء ضرورية للزراعة",
                "application": "أهمية الأمطار",
            },
        ],
        "الربيع": [
            {
                "proverb": "في الربيع اغرس الشجر، تحصد الثمر",
                "meaning": "الربيع أفضل وقت لغرس الأشجار",
                "application": "توقيت الغرس",
            },
        ],
    },
    "by_region": {
        "تهامة": [
            {
                "proverb": "في تهامة الصبر على الحر والعطش",
                "meaning": "مناخ تهامة حار ويحتاج صبراً",
                "application": "التكيف مع المناخ",
            },
            {
                "proverb": "تهامة أرض الموز والنخيل",
                "meaning": "تهامة مناسبة للمحاصيل الاستوائية",
                "application": "اختيار المحاصيل",
            },
            {
                "proverb": "ماء تهامة قليل، فاحرص على كل قطرة",
                "meaning": "المياه نادرة في تهامة فيجب الحفاظ عليها",
                "application": "ترشيد المياه",
            },
            {
                "proverb": "في تهامة الزرع مع أول مطر",
                "meaning": "استغلال الأمطار النادرة فوراً",
                "application": "التوقيت",
            },
        ],
        "المرتفعات": [
            {
                "proverb": "في الجبال البن والبرد والضباب",
                "meaning": "المرتفعات مناسبة لزراعة البن",
                "application": "المحاصيل الجبلية",
            },
            {
                "proverb": "المدرجات الجبلية كنز الأجداد",
                "meaning": "المدرجات الزراعية إرث ثمين",
                "application": "الحفاظ على المدرجات",
            },
            {
                "proverb": "في الجبال القمح والشعير والعدس",
                "meaning": "الحبوب تنمو جيداً في المرتفعات",
                "application": "المحاصيل المناسبة",
            },
            {
                "proverb": "السحاب في الجبال ري وبركة",
                "meaning": "الضباب يوفر رطوبة إضافية",
                "application": "الاستفادة من الرطوبة",
            },
            {
                "proverb": "برد الجبال يحلي الفاكهة",
                "meaning": "البرودة تحسن جودة الفواكه",
                "application": "جودة المحصول",
            },
        ],
        "حضرموت": [
            {
                "proverb": "في حضرموت النخل والسدر والعسل",
                "meaning": "حضرموت مشهورة بالنخيل والعسل",
                "application": "المحاصيل المحلية",
            },
            {
                "proverb": "وادي حضرموت جنة في الصحراء",
                "meaning": "الوديان الخصبة وسط الجفاف",
                "application": "الاستفادة من الوديان",
            },
            {
                "proverb": "ماء السيل في حضرموت ذهب سائل",
                "meaning": "مياه السيول ثمينة ويجب تخزينها",
                "application": "حصاد المياه",
            },
        ],
    },
    "by_activity": {
        "الحراثة": [
            {
                "proverb": "الحرث الجيد نصف الزرع",
                "meaning": "تحضير الأرض جيداً أساس النجاح",
                "application": "أهمية الحراثة",
            },
            {
                "proverb": "احرث مرتين تحصد ضعفين",
                "meaning": "الحراثة المتكررة تحسن الإنتاج",
                "application": "عدد مرات الحراثة",
            },
            {
                "proverb": "احرث في الرطب ولا تحرث في اليابس",
                "meaning": "الحراثة بعد المطر أسهل وأفضل",
                "application": "توقيت الحراثة",
            },
        ],
        "البذر": [
            {
                "proverb": "البذرة الطيبة أساس الحصاد الوفير",
                "meaning": "جودة البذور تحدد جودة المحصول",
                "application": "اختيار البذور",
            },
            {
                "proverb": "لا تبذر في الريح ولا في الحر الشديد",
                "meaning": "تجنب البذر في ظروف صعبة",
                "application": "ظروف البذر",
            },
            {
                "proverb": "البذر المبكر يدرك الخير",
                "meaning": "البذر في الوقت المناسب يضمن محصولاً جيداً",
                "application": "التوقيت",
            },
            {
                "proverb": "ابذر في القمر المتزايد تنبت البذرة سريعاً",
                "meaning": "القمر المتزايد يساعد على الإنبات",
                "application": "مرحلة القمر",
            },
        ],
        "الري": [
            {
                "proverb": "الري بالعلم لا بالعشوائية",
                "meaning": "الري يحتاج معرفة وتخطيط",
                "application": "إدارة الري",
            },
            {
                "proverb": "قطرة ماء في وقتها خير من سيل في غير وقته",
                "meaning": "الري المنتظم أفضل من الإفراط",
                "application": "انتظام الري",
            },
            {
                "proverb": "اسقِ الجذر ولا تسقِ الساق",
                "meaning": "الري عند الجذور أكثر فعالية",
                "application": "طريقة الري",
            },
        ],
        "الحصاد": [
            {
                "proverb": "احصد في اليابس ولا تحصد في الرطب",
                "meaning": "الحصاد في الجو الجاف يحفظ المحصول",
                "application": "توقيت الحصاد",
            },
            {
                "proverb": "الحصاد في القمر المتناقص يطول التخزين",
                "meaning": "المحصول المقطوف في القمر المتناقص يُخزن أفضل",
                "application": "مرحلة القمر",
            },
            {
                "proverb": "من عجّل الحصاد فاته الخير",
                "meaning": "الصبر حتى النضج الكامل ضروري",
                "application": "وقت النضج",
            },
            {
                "proverb": "احصد في الصباح قبل الحر",
                "meaning": "الحصاد الصباحي أفضل للجودة",
                "application": "وقت الحصاد",
            },
        ],
        "التخزين": [
            {
                "proverb": "التخزين الجيد يحفظ تعب السنة",
                "meaning": "التخزين السليم يحمي المحصول",
                "application": "أهمية التخزين",
            },
            {
                "proverb": "جفّف قبل أن تخزّن",
                "meaning": "التجفيف ضروري قبل التخزين",
                "application": "التحضير للتخزين",
            },
            {
                "proverb": "المخزن البارد والجاف يطيل العمر",
                "meaning": "ظروف التخزين الجيدة تحفظ المحصول",
                "application": "ظروف التخزين",
            },
        ],
    },
}

# التقنيات الزراعية اليمنية التقليدية
TRADITIONAL_TECHNIQUES = {
    "plowing": {
        "الحراثة بالثيران": {
            "name": "الحراثة بالثيران",
            "name_en": "Ox Plowing",
            "description": "استخدام الثيران لحراثة الأرض قبل الزراعة",
            "tools": ["المحراث الخشبي", "النير", "السكة"],
            "best_time": "قبل موسم الأمطار",
            "lunar_phase": "القمر المتناقص",
            "regions": ["المرتفعات", "السهول"],
            "depth_cm": 20,
            "passes": 2,
            "tips_ar": ["ابدأ من الأطراف نحو الوسط", "اترك الأرض يومين قبل الزراعة"],
            "benefits": ["تهوية التربة", "تفكيك الطبقات الصلبة", "دمج المخلفات العضوية"],
            "difficulty": "متوسطة",
            "traditional_saying": "الحرث الجيد نصف الزرع",
        },
        "الحراثة اليدوية": {
            "name": "الحراثة اليدوية",
            "name_en": "Manual Plowing",
            "description": "حراثة الأرض باستخدام المعزقة اليدوية للمساحات الصغيرة",
            "tools": ["المعزقة", "الفأس", "المنجل"],
            "best_time": "الصباح الباكر أو المساء",
            "lunar_phase": "أي مرحلة",
            "regions": ["المدرجات الجبلية", "الحدائق المنزلية"],
            "depth_cm": 15,
            "passes": 1,
            "tips_ar": [
                "استخدم المعزقة بزاوية 45 درجة",
                "احرث في اتجاه واحد أولاً ثم عمودياً",
                "ارتدِ القفازات لحماية اليدين",
            ],
            "benefits": ["دقة عالية", "مناسب للمساحات الضيقة", "لا يحتاج طاقة حيوانية"],
            "difficulty": "سهلة",
            "traditional_saying": "يد واحدة بالعمل خير من ألف باللسان",
        },
        "الحراثة بالمحراث الحديدي": {
            "name": "الحراثة بالمحراث الحديدي",
            "name_en": "Iron Plow Plowing",
            "description": "استخدام المحراث الحديدي التقليدي مع الثيران",
            "tools": ["المحراث الحديدي", "النير الخشبي", "السكة الحديدية"],
            "best_time": "بعد المطر مباشرة",
            "lunar_phase": "القمر المتزايد",
            "regions": ["السهول", "الوديان"],
            "depth_cm": 25,
            "passes": 3,
            "tips_ar": [
                "اضبط عمق السكة قبل البدء",
                "نظف المحراث من الأعشاب كل ساعة",
                "راعِ راحة الثيران كل ساعتين",
            ],
            "benefits": ["عمق أفضل", "قوة حراثة أكبر", "مناسب للأراضي الطينية"],
            "difficulty": "متقدمة",
            "traditional_saying": "الحديد بالحديد يُفلح، والأرض بالحرث تُصلح",
        },
    },
    "irrigation": {
        "الري بالسواقي": {
            "name": "الري بالسواقي",
            "name_en": "Channel Irrigation",
            "description": "نقل المياه عبر قنوات ترابية من المصدر إلى الحقول",
            "water_source": "آبار أو غيول",
            "efficiency_percent": 60,
            "best_time": "الفجر أو المغرب",
            "technique": "فتح وإغلاق البوابات بالتناوب",
            "tools": ["الفأس لحفر القنوات", "بوابات خشبية", "أحجار لتوجيه الماء"],
            "regions": ["المرتفعات", "الوديان"],
            "water_distribution": "تناوبي حسب الحقول",
            "maintenance": "تنظيف القنوات كل شهر",
            "tips_ar": [
                "اجعل الساقية بميل خفيف 1-2%",
                "ضع أحجاراً في الانحناءات لمنع التآكل",
                "أغلق الساقية بعد الري مباشرة",
            ],
            "traditional_saying": "الماء حياة، والساقية شريانها",
        },
        "الري بالغمر": {
            "name": "الري بالغمر",
            "name_en": "Flood Irrigation",
            "description": "غمر الحقل بالماء بالكامل لفترة محددة",
            "water_source": "سدود، آبار كبيرة",
            "efficiency_percent": 50,
            "best_time": "الليل لتقليل التبخر",
            "technique": "إغراق الحقل بالكامل لمدة 2-4 ساعات",
            "tools": ["قنوات رئيسية", "حواجز ترابية", "بوابات"],
            "regions": ["السهول المنبسطة", "حقول الأرز"],
            "water_distribution": "متساوي على كامل المساحة",
            "maintenance": "تسوية الأرض سنوياً",
            "tips_ar": [
                "تأكد من استواء الأرض قبل الري",
                "اصنع حواجز ترابية بارتفاع 20-30 سم",
                "صرّف الماء الزائد خلال 6 ساعات",
            ],
            "traditional_saying": "الأرض المستوية ماؤها متساوي",
            "suitable_crops": ["أرز", "قمح", "شعير"],
        },
        "الري بالتنقيط التقليدي": {
            "name": "الري بالتنقيط التقليدي",
            "name_en": "Traditional Drip Irrigation",
            "description": "استخدام أوانٍ فخارية مسامية مدفونة بجانب النباتات",
            "water_source": "أوانٍ فخارية مملوءة بالماء",
            "efficiency_percent": 85,
            "best_time": "يومياً في الصباح",
            "technique": "دفن أواني فخارية بجانب النباتات تتسرب منها المياه ببطء",
            "tools": ["أوانٍ فخارية مسامية", "أغطية للأوانٍ", "حصى صغيرة"],
            "regions": ["الحدائق المنزلية", "زراعة الخضروات"],
            "water_distribution": "مباشر لجذور النبات",
            "maintenance": "تنظيف الأوانٍ كل أسبوعين",
            "tips_ar": [
                "ادفن الإناء بحيث يظهر الفوهة فقط",
                "ضع حصى صغيرة حول الإناء",
                "املأ الأوانٍ يومياً أو كل يومين",
            ],
            "traditional_saying": "الماء القليل الدائم خير من الكثير المنقطع",
            "suitable_crops": ["طماطم", "فلفل", "باذنجان", "أشجار صغيرة"],
            "benefits": ["توفير الماء", "نمو جذري قوي", "منع الأعشاب"],
        },
        "الري بالدلو والرشاش": {
            "name": "الري بالدلو والرشاش",
            "name_en": "Bucket and Spray Irrigation",
            "description": "الري اليدوي باستخدام الدلو ورش الماء بالمغرفة",
            "water_source": "بئر، خزان",
            "efficiency_percent": 70,
            "best_time": "الفجر قبل شروق الشمس",
            "technique": "رش الماء بالتساوي على النباتات باستخدام مغرفة مثقبة",
            "tools": ["دلو", "مغرفة مثقبة", "حبل للسحب"],
            "regions": ["جميع المناطق"],
            "water_distribution": "رش يدوي متساوي",
            "maintenance": "تنظيف المغرفة أسبوعياً",
            "tips_ar": [
                "اغرف من البئر برفق لتجنب تعكير الماء",
                "رش الماء من ارتفاع متر واحد",
                "تجنب رش الأوراق في الشمس الحارة",
            ],
            "traditional_saying": "رية واحدة صباحية تساوي عشر ليلية",
            "suitable_crops": ["خضروات", "زهور", "شتلات"],
        },
    },
    "fertilization": {
        "التسميد بالسماد البلدي": {
            "name": "السماد البلدي",
            "name_en": "Traditional Organic Fertilizer",
            "description": "استخدام روث الحيوانات والمخلفات العضوية كسماد طبيعي",
            "sources": ["روث الأبقار", "روث الأغنام", "روث الدجاج", "مخلفات المنزل العضوية"],
            "composting_days": 60,
            "application_kg_per_hectare": 5000,
            "best_moon_phase": "القمر المتزايد",
            "application_time": "قبل الزراعة بأسبوعين",
            "benefits": [
                "يحسن بنية التربة",
                "بطيء التحلل يغذي طويلاً",
                "آمن بيئياً",
                "يزيد احتفاظ التربة بالماء",
            ],
            "preparation": [
                "اجمع الروث في مكان مظلل",
                "اخلطه مع القش والمخلفات",
                "رش الماء للترطيب",
                "قلّب الكومة كل أسبوعين",
                "انتظر 60 يوماً حتى النضج",
            ],
            "application_method": "نثر على الأرض قبل الحرث أو خلط مع التربة",
            "tips_ar": [
                "روث الأغنام أقوى من روث الأبقار",
                "لا تستخدم روثاً طازجاً - قد يحرق النباتات",
                "أضف رماد الخشب للسماد لزيادة البوتاسيوم",
            ],
            "traditional_saying": "السماد البلدي أبو الخصوبة",
        },
        "الرماد": {
            "name": "الرماد",
            "name_en": "Wood Ash Fertilizer",
            "description": "استخدام رماد الحطب كسماد غني بالبوتاسيوم والمعادن",
            "sources": ["رماد حطب البلوط", "رماد السدر", "رماد الحطب العادي"],
            "composting_days": 0,
            "application_kg_per_hectare": 500,
            "best_moon_phase": "القمر المتناقص",
            "application_time": "مباشرة عند الحاجة",
            "benefits": [
                "غني بالبوتاسيوم",
                "يرفع حموضة التربة (قلوي)",
                "يطرد بعض الحشرات",
                "يحسن طعم الثمار",
            ],
            "preparation": [
                "اجمع الرماد البارد من المواقد",
                "نخّله لإزالة القطع الكبيرة",
                "احفظه في مكان جاف",
            ],
            "application_method": "نثر خفيف حول النباتات أو خلط مع ماء الري",
            "tips_ar": [
                "لا تستخدم رماد الفحم - مضر",
                "الرماد قلوي - لا تكثر منه",
                "مفيد جداً للطماطم والبطاطس",
            ],
            "traditional_saying": "الرماد للثمر حلاوة، وللتربة قلوية",
            "suitable_crops": ["طماطم", "بطاطس", "بصل", "فواكه"],
            "cautions": ["تجنب الاستخدام المفرط", "لا يناسب النباتات المحبة للحموضة"],
        },
        "مخلفات البن": {
            "name": "مخلفات البن",
            "name_en": "Coffee Grounds Fertilizer",
            "description": "استخدام قشور البن المجففة وبقايا القهوة كسماد عضوي",
            "sources": ["قشور البن", "بقايا القهوة المطحونة"],
            "composting_days": 30,
            "application_kg_per_hectare": 2000,
            "best_moon_phase": "القمر المتزايد",
            "application_time": "خلال موسم النمو",
            "benefits": [
                "غني بالنيتروجين",
                "يحسن تركيب التربة",
                "حمضي - مناسب لبعض النباتات",
                "يطرد بعض الحشرات",
            ],
            "preparation": [
                "اجمع قشور البن بعد التجفيف",
                "جففها تماماً في الشمس",
                "اطحنها أو اتركها كما هي",
                "يمكن خلطها مع السماد البلدي",
            ],
            "application_method": "نثر حول النباتات أو خلط مع التربة العلوية",
            "tips_ar": [
                "ممتاز لنباتات البن نفسها",
                "لا تكثر - قد يزيد حموضة التربة",
                "اخلطه مع الرماد لتعديل الحموضة",
            ],
            "traditional_saying": "البن يغذي البن - دورة الطبيعة",
            "suitable_crops": ["بن", "ورود", "طماطم", "جزر"],
            "nitrogen_content": "حوالي 2%",
        },
        "السماد الأخضر": {
            "name": "السماد الأخضر",
            "name_en": "Green Manure",
            "description": "زراعة نباتات بقولية ودفنها في التربة كسماد",
            "sources": ["الفول", "البرسيم", "الحلبة", "العدس"],
            "composting_days": 14,
            "application_kg_per_hectare": 10000,
            "best_moon_phase": "القمر المتزايد للزراعة",
            "application_time": "قبل الموسم الرئيسي بـ 3 أشهر",
            "benefits": [
                "يثبت النيتروجين من الجو",
                "يحسن بنية التربة بسرعة",
                "يكافح الأعشاب",
                "متجدد ومجاني",
            ],
            "preparation": [
                "ازرع البقوليات في الأرض",
                "دعها تنمو 60-90 يوماً",
                "احرثها في التربة قبل الإزهار",
                "انتظر أسبوعين قبل الزراعة الرئيسية",
            ],
            "application_method": "حراثة النباتات الخضراء في التربة",
            "tips_ar": [
                "اقطع النباتات قبل الإزهار - أقصى نيتروجين",
                "البرسيم أفضل سماد أخضر",
                "رش قليلاً من الماء بعد الحراثة",
            ],
            "traditional_saying": "ما أكل الحيوان خير، وما دفن في الأرض أخير",
            "suitable_green_crops": ["برسيم", "فول", "حلبة", "بازيلاء"],
        },
    },
    "harvesting": {
        "حصاد الحبوب يدوياً": {
            "name": "حصاد الحبوب يدوياً",
            "name_en": "Manual Grain Harvesting",
            "description": "قطف سنابل القمح والشعير باستخدام المنجل التقليدي",
            "tools": ["المنجل", "حبال للربط", "بسط للتجفيف"],
            "best_time": "الصباح الباكر بعد جفاف الندى",
            "lunar_phase": "القمر المتناقص",
            "best_season": "الصيف - يونيو/يوليو",
            "technique": "القطع بزاوية 45 درجة فوق الأرض بـ 10-15 سم",
            "drying_days": 7,
            "storage": "أكياس قماشية في مكان جاف",
            "tips_ar": [
                "احصد عندما تكون السنابل ذهبية وجافة",
                "اربط الحزم مباشرة بعد القطع",
                "اضرب السنابل برفق لفصل الحبوب",
                "نظف الحبوب بالغربلة",
            ],
            "traditional_saying": "الحصاد في المحاق، والحبوب في الأجراب",
            "moisture_content": "12-14% للتخزين الآمن",
        },
        "قطف البن": {
            "name": "قطف البن",
            "name_en": "Coffee Harvesting",
            "description": "قطف حبات البن الناضجة يدوياً - الطريقة اليمنية التقليدية",
            "tools": ["سلال خوصية", "سلالم خشبية", "مفارش للتجفيف"],
            "best_time": "الصباح الباكر",
            "lunar_phase": "القمر المتناقص",
            "best_season": "الخريف - أكتوبر/نوفمبر/ديسمبر",
            "technique": "قطف انتقائي - الحبات الحمراء الناضجة فقط",
            "drying_days": 21,
            "storage": "في مكان جاف بعيداً عن الرطوبة",
            "tips_ar": [
                "اقطف الحبات الحمراء فقط",
                "مرر على الشجرة عدة مرات",
                "جفف على الأسطح أو الحصير",
                "قلّب الحبات مرتين يومياً",
            ],
            "traditional_saying": "قطف البن في الثريا، وجففه في الجوزاء",
            "processing_method": "التجفيف الطبيعي على الأسطح",
            "quality_indicator": "اللون الأحمر الداكن للحبة",
        },
        "جني العسل التقليدي": {
            "name": "جني العسل التقليدي",
            "name_en": "Traditional Honey Harvesting",
            "description": "استخراج العسل من خلايا النحل الجبلية التقليدية",
            "tools": ["المدخن", "سكين العسل", "أوعية فخارية", "قفازات"],
            "best_time": "الصباح الباكر أو المساء",
            "lunar_phase": "القمر المتناقص",
            "best_season": "الخريف بعد موسم الأزهار",
            "technique": "التدخين لتهدئة النحل ثم قطع الأقراص برفق",
            "processing": "العصر اليدوي أو بالثقل",
            "storage": "في أوانٍ فخارية مغلقة",
            "tips_ar": [
                "استخدم الدخان برفق - لا تخيف النحل",
                "اترك ثلث الأقراص للنحل",
                "اجنِ في الأيام الجافة فقط",
                "صفِّ العسل بقطعة قماش نظيفة",
            ],
            "traditional_saying": "العسل في القمر المتناقص أصفى وأحلى",
            "smoke_source": "قشور البن المجففة أو أعشاب عطرية",
            "yield_kg_per_hive": "5-15 كجم سنوياً",
        },
        "قطاف التمور": {
            "name": "قطاف التمور",
            "name_en": "Date Harvesting",
            "description": "قطف التمر من النخيل في مراحل النضج المختلفة",
            "tools": ["سلم طويل", "سلال", "مقص", "حبال"],
            "best_time": "الصباح قبل الحر الشديد",
            "lunar_phase": "أي مرحلة",
            "best_season": "الصيف - يوليو/أغسطس/سبتمبر",
            "technique": "القطف التدريجي حسب النضج",
            "drying_days": "حسب النوع: 0-14 يوم",
            "storage": "في سلال مهواة أو أوعية",
            "tips_ar": [
                "اقطف التمر في مرحلة الرطب للأكل الطازج",
                "اترك البعض ليجف على الشجرة",
                "افرز التمر حسب الجودة",
                "خزن في مكان بارد وجاف",
            ],
            "traditional_saying": "التمر في الصيف ذهب، وفي الشتاء غذاء",
            "ripeness_stages": ["خلال", "بسر", "رطب", "تمر"],
        },
    },
    "processing": {
        "تجفيف البن": {
            "name": "تجفيف البن على السطوح",
            "name_en": "Rooftop Coffee Drying",
            "description": "تجفيف حبات البن على أسطح المنازل والحصير - الطريقة اليمنية الأصيلة",
            "method": "نشر الثمار على أسطح المنازل أو حصير القش",
            "duration_days": 21,
            "turning_frequency": "مرتين يومياً - الصباح والظهر",
            "best_season": "الخريف - أكتوبر/نوفمبر",
            "ideal_temperature": "25-30 درجة مئوية",
            "humidity_limit": "أقل من 60%",
            "final_moisture": "10-12%",
            "tips_ar": [
                "انشر طبقة رقيقة - سماكة حبتين فقط",
                "قلّب الحبات بانتظام للتجفيف المتساوي",
                "اجمع الحبات عند غروب الشمس",
                "غطها ليلاً لمنع الرطوبة",
            ],
            "quality_indicators": [
                "اللون البني الداكن",
                "صوت طقطقة عند الهز",
                "سهولة فصل القشرة",
            ],
            "traditional_saying": "البن الجبلي يجفف بالشمس والهواء - طعمه الأصيل",
        },
        "طحن الحبوب": {
            "name": "طحن الحبوب",
            "name_en": "Grain Milling",
            "description": "طحن القمح والشعير باستخدام الرحى الحجرية التقليدية",
            "method": "الطحن بين حجري الرحى بالدوران",
            "tools": ["الرحى الحجرية", "القادوس", "أكياس قماشية"],
            "best_time": "في أي وقت حسب الحاجة",
            "lunar_phase": "القمر المتناقص - الطحين يدوم أكثر",
            "processing_kg_per_hour": 10,
            "tips_ar": [
                "نظف الحبوب جيداً قبل الطحن",
                "اضبط المسافة بين الحجرين حسب النعومة المطلوبة",
                "دع الرحى تبرد كل ساعة",
                "احفظ الدقيق في مكان جاف ومظلم",
            ],
            "flour_types": ["دقيق ناعم", "دقيق خشن", "بليلة (حب مكسور)"],
            "traditional_saying": "الرحى تطحن ببطء لكن بإتقان",
            "shelf_life_days": 90,
        },
        "تخزين الحبوب": {
            "name": "تخزين الحبوب",
            "name_en": "Grain Storage",
            "description": "حفظ الحبوب في صوامع طينية أو أكياس قماشية تقليدية",
            "method": "التخزين في صوامع طينية محكمة أو أكياس قماش",
            "containers": ["الصوامع الطينية", "أكياس القماش", "براميل خشبية"],
            "best_time": "بعد التجفيف الكامل",
            "lunar_phase": "القمر المتناقص",
            "ideal_temperature": "15-20 درجة مئوية",
            "humidity_limit": "أقل من 13%",
            "pest_prevention": [
                "إضافة أوراق النعناع الجافة",
                "وضع حبات الثوم",
                "رش طبقة رماد خفيفة",
            ],
            "tips_ar": [
                "جفف الحبوب تماماً قبل التخزين",
                "افحص المخزون شهرياً",
                "ضع الحبوب الجديدة في قاع الصومعة",
                "تجنب التخزين بجانب جدران رطبة",
            ],
            "shelf_life_months": 12,
            "traditional_saying": "الحبوب المخزونة في القمر الأسود تدوم سنة",
        },
        "تجفيف الفواكه": {
            "name": "تجفيف الفواكه",
            "name_en": "Fruit Drying",
            "description": "تجفيف العنب والتين والمشمش بالشمس للحفظ",
            "method": "التجفيف الشمسي على حصير أو صواني",
            "tools": ["حصير", "شبك", "غطاء شفاف"],
            "duration_days": "5-14 حسب النوع",
            "turning_frequency": "مرة يومياً",
            "best_season": "الصيف - الحرارة العالية",
            "ideal_temperature": "30-40 درجة مئوية",
            "final_moisture": "15-20%",
            "fruits_suitable": ["عنب (زبيب)", "تين", "مشمش", "تمر"],
            "tips_ar": [
                "اغسل الفواكه وجففها قبل النشر",
                "قطّع الفواكه الكبيرة لنصفين",
                "غطها بشبك لحمايتها من الحشرات",
                "اجمعها ليلاً في مكان جاف",
            ],
            "traditional_saying": "الفاكهة المجففة زاد الشتاء",
        },
    },
    "pest_control": {
        "المكافحة بالرماد": {
            "name": "المكافحة بالرماد",
            "name_en": "Ash Pest Control",
            "description": "استخدام رماد الخشب لمكافحة الحشرات والآفات",
            "method": "نثر الرماد حول النباتات أو على الأوراق",
            "pests_controlled": ["الحلزون", "الديدان", "النمل", "المن"],
            "application_frequency": "كل أسبوعين أو بعد المطر",
            "best_time": "الصباح الباكر على الأوراق المبللة بالندى",
            "tools": ["غربال ناعم", "قفازات", "قناع"],
            "preparation": "نخل الرماد البارد لإزالة القطع الكبيرة",
            "tips_ar": [
                "انثر طبقة خفيفة حول النبات",
                "كرر بعد كل مطر",
                "لا تكثر - قد يرفع قلوية التربة",
                "اخلط مع الماء للرش على الأوراق",
            ],
            "effectiveness_percent": 70,
            "traditional_saying": "الرماد سيف النبات ضد الحشرات",
        },
        "التبخير بالأعشاب": {
            "name": "التبخير بالأعشاب",
            "name_en": "Herbal Fumigation",
            "description": "حرق أعشاب عطرية لطرد الحشرات من الحقول والمخازن",
            "method": "حرق الأعشاب الجافة وتوجيه الدخان نحو النباتات",
            "herbs_used": ["الشيح", "الحبق", "النعناع البري", "الزعتر", "قشور البن"],
            "pests_controlled": ["الذباب", "البعوض", "العث", "الفراشات الضارة"],
            "application_frequency": "مرة أسبوعياً أو عند الحاجة",
            "best_time": "المساء قبل الغروب",
            "tools": ["مبخرة معدنية", "أعشاب جافة", "منفاخ"],
            "tips_ar": [
                "استخدم أعشاباً جافة تماماً",
                "بخر في اتجاه الريح",
                "كرر بعد الأمطار",
                "احفظ الأعشاب المجففة في مكان جاف",
            ],
            "effectiveness_percent": 60,
            "traditional_saying": "دخان الأعشاب يطرد الشر والحشرات",
            "side_benefits": ["رائحة طيبة", "تطهير الهواء"],
        },
        "الفزاعات التقليدية": {
            "name": "الفزاعات التقليدية",
            "name_en": "Traditional Scarecrows",
            "description": "نصب أشكال بشرية أو عاكسة لطرد الطيور من الحقول",
            "method": "صنع دمى من القماش والقش أو تعليق أقراص لامعة",
            "materials": [
                "عصي خشبية",
                "ملابس قديمة",
                "قش",
                "أقراص معدنية لامعة",
                "أجراس صغيرة",
            ],
            "pests_controlled": ["الطيور", "الغربان", "الحمام"],
            "effectiveness_duration": "2-3 أشهر (ثم تعتاد الطيور)",
            "best_time": "قبل نضج المحاصيل",
            "tips_ar": [
                "غيّر موقع الفزاعة كل أسبوع",
                "أضف عناصر متحركة (أقمشة ترفرف)",
                "علق أقراص معدنية تعكس الضوء",
                "استخدم عدة فزاعات بأشكال مختلفة",
            ],
            "effectiveness_percent": 50,
            "traditional_saying": "الفزاعة الساكنة تخيف أسبوعاً، والمتحركة شهراً",
            "enhancement": "إضافة أجراس أو شرائط صوتية",
        },
        "المصائد الفخارية": {
            "name": "المصائد الفخارية",
            "name_en": "Clay Pot Traps",
            "description": "استخدام أوانٍ فخارية كمصائد للحشرات",
            "method": "دفن أوانٍ فخارية مملوءة بسائل جاذب للحشرات",
            "trap_liquid": ["ماء + سكر + خل", "عصير فواكه متخمر", "ماء صابوني"],
            "pests_controlled": ["الخنافس", "الديدان", "النمل الطائر"],
            "application_frequency": "تفريغ وتنظيف كل 3 أيام",
            "best_time": "بداية الموسم قبل تكاثر الحشرات",
            "tools": ["أوانٍ فخارية صغيرة", "غطاء مثقب", "سوائل جاذبة"],
            "tips_ar": [
                "ادفن الإناء بحيث تكون الفوهة بمستوى الأرض",
                "ضع 4-6 مصائد لكل 100 متر مربع",
                "غيّر السائل كل 3 أيام",
                "أضف قطرتي صابون لمنع الهروب",
            ],
            "effectiveness_percent": 65,
            "traditional_saying": "الفخار يصيد ما لا تراه العين",
        },
    },
}


# النجوم المهمة للزراعة اليمنية
IMPORTANT_STARS = {
    "سهيل": {
        "name": "سهيل",
        "name_en": "Canopus",
        "rising_month": 8,  # أغسطس
        "significance": "بداية موسم الأمطار والبرودة",
        "farming_impact": "إشارة لبدء الزراعة الصيفية",
        "proverb": "إذا طلع سهيل، برد الليل وأقبل السيل",
    },
    "الثريا": {
        "name": "الثريا",
        "name_en": "Pleiades",
        "rising_month": 5,  # مايو (صباحاً)
        "significance": "أهم نجم في التقويم الزراعي اليمني",
        "farming_impact": "أفضل وقت للزراعة عند طلوعها",
        "proverb": "الزرع في الثريا، والحصاد في الجوزاء",
    },
    "السماك": {
        "name": "السماك الأعزل",
        "name_en": "Spica",
        "rising_month": 4,  # أبريل
        "significance": "نجم الربيع والخصوبة",
        "farming_impact": "مناسب لجميع أنواع الزراعة",
        "proverb": "في السماك ازرع ولا تخف",
    },
}

# المعالم الزراعية اليمنية التاريخية
YEMENI_AGRICULTURAL_LANDMARKS = {
    "terraces": {
        "المدرجات الجبلية": {
            "name": "المدرجات الجبلية",
            "name_en": "Mountain Terraces",
            "locations": ["حراز", "إب", "المحويت", "صعدة", "ريمة"],
            "description": "تقنية زراعية عريقة لاستغلال المنحدرات الجبلية في زراعة المحاصيل المختلفة",
            "crops": ["بن", "قات", "ذرة", "قمح"],
            "altitude_range": "1500-2800م",
            "heritage_status": "تراث إنساني - UNESCO",
            "age_years": 3000,
            "techniques": ["حجارة جافة", "قنوات تصريف", "جدران احتفاظ"],
            "image_url": None,
            "significance": "تمثل إنجازاً هندسياً فريداً يعكس ذكاء المزارع اليمني في التعامل مع التضاريس الصعبة",
        },
        "مدرجات حراز": {
            "name": "مدرجات حراز",
            "name_en": "Haraz Terraces",
            "locations": ["حراز", "المحويت"],
            "coordinates": {"lat": 15.3667, "lng": 43.8},
            "description": "مدرجات جبلية شهيرة بزراعة البن اليمني الفاخر",
            "crops": ["بن", "قات", "فواكه"],
            "altitude_range": "1800-2500م",
            "heritage_status": "محمية وطنية",
            "age_years": 2500,
            "techniques": ["بناء حجري متقن", "نظام ري بالغيول", "تربة محسنة"],
            "image_url": None,
            "significance": "موطن أجود أنواع البن اليمني",
        },
        "مدرجات ريمة": {
            "name": "مدرجات ريمة",
            "name_en": "Raymah Terraces",
            "locations": ["ريمة"],
            "coordinates": {"lat": 14.6167, "lng": 43.7167},
            "description": "مدرجات خضراء تشتهر بزراعة القات والبن في بيئة جبلية رطبة",
            "crops": ["قات", "بن", "ذرة", "خضروات"],
            "altitude_range": "1500-2400م",
            "heritage_status": "محمية طبيعية",
            "age_years": 2000,
            "techniques": ["تدريج دقيق", "استغلال الأمطار", "تنوع بيولوجي"],
            "image_url": None,
            "significance": "تجمع بين الزراعة والحفاظ على التنوع البيولوجي",
        },
        "مدرجات صعدة": {
            "name": "مدرجات صعدة",
            "name_en": "Saada Terraces",
            "locations": ["صعدة"],
            "coordinates": {"lat": 16.9167, "lng": 43.7667},
            "description": "مدرجات زراعية في المرتفعات الشمالية تشتهر بزراعة الحبوب",
            "crops": ["قمح", "شعير", "عدس", "ذرة"],
            "altitude_range": "1600-2600م",
            "heritage_status": "تراث محلي",
            "age_years": 2200,
            "techniques": ["زراعة موسمية", "استغلال مياه الأمطار", "تخزين التربة"],
            "image_url": None,
            "significance": "تمثل النمط الزراعي التقليدي في المرتفعات الشمالية",
        },
    },
    "dams": {
        "سد مأرب": {
            "name": "سد مأرب القديم",
            "name_en": "Ancient Marib Dam",
            "location": "مأرب",
            "coordinates": {"lat": 15.4167, "lng": 45.35},
            "built_era": "القرن الثامن قبل الميلاد",
            "description": "أعظم إنجاز هندسي في العالم القديم، بناه سبأيون وكان معجزة هندسية لعصره",
            "irrigated_area_hectares": 9600,
            "crops_historical": ["قمح", "شعير", "نخيل", "فواكه", "عنب"],
            "current_status": "أثري - السد الجديد يعمل منذ 1986",
            "length_meters": 650,
            "height_meters": 16,
            "capacity_cubic_meters": 30000000,
            "engineering_features": ["سدتان جانبيتان", "قنوات توزيع", "بوابات تحكم"],
            "historical_significance": "ذُكر في القرآن الكريم وكان سبب ازدهار حضارة سبأ",
        },
        "سد أذينة": {
            "name": "سد أذينة",
            "name_en": "Adhanah Dam",
            "location": "ذمار",
            "coordinates": {"lat": 14.5, "lng": 44.3},
            "built_era": "القرن الأول الميلادي",
            "description": "سد تاريخي من العصر الحميري يروي أراضي زراعية واسعة",
            "irrigated_area_hectares": 1200,
            "crops_historical": ["قمح", "ذرة", "بقوليات"],
            "current_status": "آثار متبقية",
            "length_meters": 120,
            "height_meters": 8,
            "capacity_cubic_meters": 500000,
            "engineering_features": ["بناء حجري", "قنوات فرعية"],
            "historical_significance": "يعكس تطور تقنيات الري في الحضارة الحميرية",
        },
        "سد الخانق": {
            "name": "سد الخانق",
            "name_en": "Al-Khaniq Dam",
            "location": "تعز",
            "coordinates": {"lat": 13.5833, "lng": 44.0167},
            "built_era": "العصر الإسلامي المبكر",
            "description": "سد صخري يستغل مضيق طبيعي لحجز مياه الأمطار",
            "irrigated_area_hectares": 800,
            "crops_historical": ["بن", "ذرة", "فواكه"],
            "current_status": "مستخدم جزئياً",
            "length_meters": 85,
            "height_meters": 12,
            "capacity_cubic_meters": 350000,
            "engineering_features": ["استغلال التضاريس", "قنوات طبيعية"],
            "historical_significance": "نموذج للهندسة المائية الذكية",
        },
        "سد جفينة": {
            "name": "سد جفينة",
            "name_en": "Jufainah Dam",
            "location": "أبين",
            "coordinates": {"lat": 13.8, "lng": 45.5},
            "built_era": "القرن الثالث قبل الميلاد",
            "description": "سد قديم في منطقة أبين كان يروي وادي بناء الخصب",
            "irrigated_area_hectares": 1500,
            "crops_historical": ["نخيل", "حبوب", "خضروات"],
            "current_status": "أطلال أثرية",
            "length_meters": 180,
            "height_meters": 10,
            "capacity_cubic_meters": 800000,
            "engineering_features": ["نظام ري متطور", "بوابات خشبية"],
            "historical_significance": "شاهد على ازدهار الزراعة في الجنوب اليمني",
        },
    },
    "water_systems": {
        "الغيول": {
            "name": "نظام الغيول",
            "name_en": "Ghayl System",
            "description": "قنوات ري تقليدية تنقل المياه من الينابيع الجبلية إلى المدرجات الزراعية بالاعتماد على الانسياب الطبيعي",
            "regions": ["وادي ضهر", "صنعاء", "تعز", "إب"],
            "technique": "انسياب طبيعي بالجاذبية",
            "construction": "حفر في الصخر أو قنوات حجرية مبطنة",
            "average_length_km": 5,
            "age_years": 1500,
            "water_source": "ينابيع جبلية، عيون طبيعية",
            "distribution_method": "توزيع عادل حسب الأوقات المحددة",
            "maintenance": "صيانة جماعية موسمية",
            "social_aspect": "نظام إدارة مجتمعي تقليدي",
        },
        "الآبار الارتوازية": {
            "name": "الآبار الارتوازية التقليدية",
            "name_en": "Traditional Artesian Wells",
            "description": "آبار عميقة تصل للمياه الجوفية، محفورة يدوياً بتقنيات تقليدية",
            "regions": ["مأرب", "الجوف", "صعدة", "حضرموت"],
            "technique": "حفر يدوي عميق",
            "construction": "جدران حجرية محكمة، غطاء خشبي",
            "average_depth_meters": 40,
            "age_years": 1000,
            "water_source": "المياه الجوفية",
            "distribution_method": "رفع بالدلو أو البكرة",
            "maintenance": "تنظيف دوري، إصلاح الجدران",
            "social_aspect": "ملكية مشتركة أو عامة",
        },
        "السواقي": {
            "name": "السواقي",
            "name_en": "Water Wheels (Saqiya)",
            "description": "عجلات مائية تدار بالحيوانات أو الماء لرفع المياه من الآبار والوديان",
            "regions": ["تهامة", "وادي زبيد", "أبين"],
            "technique": "دوران ميكانيكي",
            "construction": "عجلة خشبية، أوعية فخارية أو معدنية",
            "average_capacity_liters_hour": 3000,
            "age_years": 800,
            "water_source": "آبار، أنهار",
            "distribution_method": "قنوات صغيرة متفرعة",
            "maintenance": "تشحيم، تبديل الأجزاء الخشبية",
            "social_aspect": "ملكية فردية أو عائلية",
        },
        "الأحواض والبرك": {
            "name": "أحواض تجميع المياه",
            "name_en": "Water Collection Pools",
            "description": "أحواض صخرية أو إسمنتية لتجميع مياه الأمطار والينابيع",
            "regions": ["المرتفعات الوسطى", "صنعاء", "ذمار"],
            "technique": "تجميع وتخزين",
            "construction": "حوض محفور في الصخر أو مبني بالحجر",
            "average_capacity_cubic_meters": 200,
            "age_years": 1200,
            "water_source": "مياه أمطار، فائض الغيول",
            "distribution_method": "استخدام مباشر أو توزيع بالجرار",
            "maintenance": "تنظيف سنوي قبل موسم الأمطار",
            "social_aspect": "ملكية مشتركة للقرية",
        },
    },
    "storage": {
        "المخازن الحجرية": {
            "name": "المخازن الحجرية",
            "name_en": "Stone Storage Houses",
            "description": "مخازن تقليدية مبنية من الحجر لتخزين الحبوب والمحاصيل في ظروف باردة وجافة",
            "regions": ["صنعاء", "شبام", "حضرموت"],
            "construction": "جدران حجرية سميكة، أسقف طينية",
            "capacity_tons": 10,
            "crops_stored": ["قمح", "شعير", "ذرة", "عدس"],
            "preservation_method": "التهوية الطبيعية، العزل الحراري",
            "age_years": 800,
            "design_features": ["فتحات تهوية علوية", "أرضيات مرتفعة", "جدران عازلة"],
            "cultural_significance": "جزء من العمارة اليمنية التقليدية",
        },
        "الصوامع التقليدية": {
            "name": "الصوامع الطينية",
            "name_en": "Traditional Mud Silos",
            "description": "صوامع أسطوانية من الطين المحروق لتخزين الحبوب بشكل آمن",
            "regions": ["تهامة", "حضرموت", "الجوف"],
            "construction": "طين محروق، قش مضغوط",
            "capacity_tons": 5,
            "crops_stored": ["ذرة", "دخن", "سمسم"],
            "preservation_method": "العزل الطبيعي، التجفيف الشمسي",
            "age_years": 600,
            "design_features": ["شكل أسطواني", "غطاء محكم", "قاعدة مرتفعة"],
            "cultural_significance": "تكنولوجيا تخزين تقليدية فعالة",
        },
        "القمريات": {
            "name": "القمريات",
            "name_en": "Al-Qamariat (Attic Storage)",
            "description": "غرف علوية في البيوت اليمنية التقليدية مخصصة لتخزين المؤن والحبوب",
            "regions": ["صنعاء القديمة", "شبام", "صعدة"],
            "construction": "جزء من العمارة السكنية، طوابق عليا",
            "capacity_tons": 3,
            "crops_stored": ["قمح", "قات مجفف", "بهارات", "قهوة"],
            "preservation_method": "التهوية المتقاطعة، الارتفاع",
            "age_years": 500,
            "design_features": ["نوافذ قمرية للتهوية", "أرضيات خشبية", "عزل طبيعي"],
            "cultural_significance": "جزء من التراث المعماري اليمني",
        },
        "الكهوف التخزينية": {
            "name": "كهوف التخزين",
            "name_en": "Storage Caves",
            "description": "كهوف طبيعية أو محفورة في الجبال لتخزين التمور والعسل والحبوب",
            "regions": ["حضرموت", "شبوة", "مأرب"],
            "construction": "كهوف طبيعية أو محفورة يدوياً",
            "capacity_tons": 8,
            "crops_stored": ["تمور", "عسل", "قمح", "سمن"],
            "preservation_method": "حرارة ثابتة، رطوبة منخفضة",
            "age_years": 2000,
            "design_features": ["درجة حرارة ثابتة", "رطوبة منخفضة", "حماية من الحشرات"],
            "cultural_significance": "أقدم طرق التخزين في اليمن",
        },
    },
}

# المواسم الزراعية اليمنية التقليدية
YEMENI_SEASONS = {
    "sayf": {
        "name": "الصيف",
        "name_en": "Sayf (Summer)",
        "months": [6, 7, 8],
        "description": "موسم الأمطار الموسمية - زراعة الذرة والدخن",
        "main_crops": ["ذرة", "دخن", "سمسم"],
        "activities": ["زراعة الحبوب", "حصاد القات"],
    },
    "kharif": {
        "name": "الخريف",
        "name_en": "Kharif (Autumn)",
        "months": [9, 10, 11],
        "description": "موسم الحصاد والتجفيف",
        "main_crops": ["بن", "عنب"],
        "activities": ["حصاد", "تجفيف", "تخزين"],
    },
    "shita": {
        "name": "الشتاء",
        "name_en": "Shita (Winter)",
        "months": [12, 1, 2],
        "description": "موسم زراعة الخضروات الشتوية",
        "main_crops": ["قمح", "شعير", "خضروات"],
        "activities": ["زراعة القمح", "ري"],
    },
    "rabi": {
        "name": "الربيع",
        "name_en": "Rabi (Spring)",
        "months": [3, 4, 5],
        "description": "موسم الأزهار وغرس الأشجار",
        "main_crops": ["فواكه", "بن"],
        "activities": ["غرس الأشجار", "تطعيم", "تقليم"],
    },
}

# المناطق الزراعية اليمنية
YEMENI_AGRICULTURAL_REGIONS = {
    "tihama": {
        "name": "سهل تهامة",
        "name_en": "Tihama Coastal Plain",
        "governorates": ["الحديدة", "تعز", "لحج"],
        "climate": {
            "type": "حار رطب",
            "type_en": "Hot Humid",
            "avg_temp_summer": 38,
            "avg_temp_winter": 25,
            "rainfall_mm": 150,
            "humidity_percent": 70,
        },
        "altitude": "0-200م",
        "altitude_en": "0-200m",
        "soil_type": "طميية رملية",
        "soil_type_en": "Sandy Loam",
        "water_sources": ["أودية موسمية", "آبار", "مياه جوفية"],
        "water_sources_en": ["Seasonal Wadis", "Wells", "Groundwater"],
        "main_crops": ["ذرة", "دخن", "سمسم", "موز", "مانجو", "بطيخ", "قطن", "تبغ"],
        "main_crops_en": [
            "Sorghum",
            "Millet",
            "Sesame",
            "Banana",
            "Mango",
            "Watermelon",
            "Cotton",
            "Tobacco",
        ],
        "planting_seasons": {
            "صيفي": {
                "months": ["يونيو", "يوليو"],
                "months_en": ["June", "July"],
                "crops": ["ذرة", "دخن", "سمسم"],
            },
            "شتوي": {
                "months": ["نوفمبر", "ديسمبر"],
                "months_en": ["November", "December"],
                "crops": ["خضروات", "طماطم", "بطاطس"],
            },
        },
        "challenges": ["شح المياه", "ملوحة التربة", "الحرارة العالية", "التصحر"],
        "challenges_en": [
            "Water Scarcity",
            "Soil Salinity",
            "High Temperature",
            "Desertification",
        ],
        "famous_products": ["موز تهامة", "مانجو الحديدة", "بطيخ زبيد"],
        "famous_products_en": [
            "Tihama Bananas",
            "Hodeidah Mangoes",
            "Zabid Watermelons",
        ],
        "traditional_irrigation": ["سقيا بالغيل", "آبار تقليدية", "سيول الأودية"],
        "traditional_irrigation_en": [
            "Spate Irrigation",
            "Traditional Wells",
            "Wadi Floods",
        ],
        "description": "سهل ساحلي خصب يمتد على البحر الأحمر، يتميز بمناخه الحار الرطب وإنتاجه الوفير من الفواكه الاستوائية",
        "description_en": "A fertile coastal plain extending along the Red Sea, characterized by hot humid climate and abundant tropical fruit production",
    },
    "central_highlands": {
        "name": "المرتفعات الوسطى",
        "name_en": "Central Highlands",
        "governorates": ["صنعاء", "ذمار", "إب", "تعز", "البيضاء"],
        "climate": {
            "type": "معتدل صيفاً بارد شتاءً",
            "type_en": "Moderate Summer, Cold Winter",
            "avg_temp_summer": 26,
            "avg_temp_winter": 12,
            "rainfall_mm": 500,
            "humidity_percent": 45,
        },
        "altitude": "2000-3600م",
        "altitude_en": "2000-3600m",
        "soil_type": "بركانية خصبة",
        "soil_type_en": "Fertile Volcanic",
        "water_sources": ["أمطار موسمية", "ينابيع", "آبار", "سدود"],
        "water_sources_en": ["Seasonal Rainfall", "Springs", "Wells", "Dams"],
        "main_crops": [
            "بن",
            "قات",
            "عنب",
            "تفاح",
            "خوخ",
            "رمان",
            "لوز",
            "قمح",
            "شعير",
            "ذرة",
        ],
        "main_crops_en": [
            "Coffee",
            "Qat",
            "Grapes",
            "Apples",
            "Peaches",
            "Pomegranates",
            "Almonds",
            "Wheat",
            "Barley",
            "Sorghum",
        ],
        "planting_seasons": {
            "ربيعي": {
                "months": ["مارس", "أبريل"],
                "months_en": ["March", "April"],
                "crops": ["بن", "عنب", "فواكه"],
            },
            "صيفي": {
                "months": ["يونيو", "يوليو"],
                "months_en": ["June", "July"],
                "crops": ["ذرة", "قمح"],
            },
            "خريفي": {
                "months": ["سبتمبر", "أكتوبر"],
                "months_en": ["September", "October"],
                "crops": ["خضروات", "بقوليات"],
            },
        },
        "challenges": [
            "تآكل التربة",
            "الجفاف الموسمي",
            "تناقص المياه الجوفية",
            "الزراعة العشوائية",
        ],
        "challenges_en": [
            "Soil Erosion",
            "Seasonal Drought",
            "Groundwater Depletion",
            "Random Cultivation",
        ],
        "famous_products": [
            "بن يافعي",
            "بن حرازي",
            "عنب رازح",
            "رمان ذمار",
            "تفاح جبل صبر",
        ],
        "famous_products_en": [
            "Yafei Coffee",
            "Haraz Coffee",
            "Razeh Grapes",
            "Dhamar Pomegranates",
            "Jabal Sabir Apples",
        ],
        "traditional_irrigation": [
            "مدرجات زراعية",
            "قنوات تقليدية",
            "سدود جبلية",
            "حصاد مياه الأمطار",
        ],
        "traditional_irrigation_en": [
            "Agricultural Terraces",
            "Traditional Channels",
            "Mountain Dams",
            "Rainwater Harvesting",
        ],
        "description": "أكثر المناطق الزراعية خصوبة في اليمن، تشتهر بإنتاج البن اليمني عالي الجودة والفواكه المعتدلة",
        "description_en": "The most fertile agricultural region in Yemen, famous for high-quality Yemeni coffee and temperate fruits",
    },
    "eastern_plateau": {
        "name": "الهضبة الشرقية",
        "name_en": "Eastern Plateau",
        "governorates": ["حضرموت", "المهرة", "شبوة"],
        "climate": {
            "type": "صحراوي جاف",
            "type_en": "Desert Arid",
            "avg_temp_summer": 42,
            "avg_temp_winter": 22,
            "rainfall_mm": 50,
            "humidity_percent": 25,
        },
        "altitude": "500-1500م",
        "altitude_en": "500-1500m",
        "soil_type": "رملية صحراوية",
        "soil_type_en": "Sandy Desert",
        "water_sources": ["سيول الأودية", "آبار عميقة", "عيون جوفية"],
        "water_sources_en": ["Wadi Floods", "Deep Wells", "Underground Springs"],
        "main_crops": ["نخيل التمر", "دخن", "ذرة", "خضروات", "علف"],
        "main_crops_en": ["Date Palms", "Millet", "Sorghum", "Vegetables", "Fodder"],
        "planting_seasons": {
            "صيفي": {
                "months": ["مايو", "يونيو"],
                "months_en": ["May", "June"],
                "crops": ["دخن", "ذرة"],
            },
            "شتوي": {
                "months": ["نوفمبر", "ديسمبر"],
                "months_en": ["November", "December"],
                "crops": ["خضروات", "برسيم"],
            },
        },
        "challenges": [
            "ندرة المياه الشديدة",
            "العواصف الرملية",
            "التصحر المتقدم",
            "ملوحة عالية",
        ],
        "challenges_en": [
            "Severe Water Scarcity",
            "Sandstorms",
            "Advanced Desertification",
            "High Salinity",
        ],
        "famous_products": [
            "تمور حضرموت",
            "عسل حضرموت",
            "تمر دوعني",
            "تمر صيحوت",
        ],
        "famous_products_en": [
            "Hadramawt Dates",
            "Hadramawt Honey",
            "Do'ani Dates",
            "Sayhut Dates",
        ],
        "traditional_irrigation": [
            "زراعة الواحات",
            "سيول الأودية",
            "آبار ارتوازية",
            "نظام الغيل",
        ],
        "traditional_irrigation_en": [
            "Oasis Farming",
            "Wadi Spate",
            "Artesian Wells",
            "Ghayl System",
        ],
        "description": "منطقة صحراوية واسعة تعتمد على زراعة النخيل والزراعة في الوديان، تشتهر بإنتاج أجود أنواع التمور",
        "description_en": "A vast desert region relying on palm cultivation and wadi farming, famous for producing the finest dates",
    },
    "northern_highlands": {
        "name": "المرتفعات الشمالية",
        "name_en": "Northern Highlands",
        "governorates": ["صعدة", "عمران", "حجة", "الجوف", "مأرب"],
        "climate": {
            "type": "جاف بارد شتاءً",
            "type_en": "Dry Cold Winter",
            "avg_temp_summer": 30,
            "avg_temp_winter": 8,
            "rainfall_mm": 300,
            "humidity_percent": 35,
        },
        "altitude": "1800-3000م",
        "altitude_en": "1800-3000m",
        "soil_type": "طينية جبلية",
        "soil_type_en": "Mountainous Clay",
        "water_sources": ["أمطار موسمية", "ينابيع جبلية", "سدود", "آبار"],
        "water_sources_en": ["Seasonal Rainfall", "Mountain Springs", "Dams", "Wells"],
        "main_crops": [
            "قمح",
            "شعير",
            "ذرة",
            "عدس",
            "حمص",
            "عنب",
            "لوز",
            "رمان",
            "تين",
        ],
        "main_crops_en": [
            "Wheat",
            "Barley",
            "Sorghum",
            "Lentils",
            "Chickpeas",
            "Grapes",
            "Almonds",
            "Pomegranates",
            "Figs",
        ],
        "planting_seasons": {
            "ربيعي": {
                "months": ["فبراير", "مارس"],
                "months_en": ["February", "March"],
                "crops": ["قمح", "شعير"],
            },
            "صيفي": {
                "months": ["يونيو", "يوليو"],
                "months_en": ["June", "July"],
                "crops": ["ذرة", "دخن"],
            },
        },
        "challenges": [
            "الصقيع الشتوي",
            "نقص الأمطار",
            "وعورة التضاريس",
            "تآكل التربة",
        ],
        "challenges_en": [
            "Winter Frost",
            "Rainfall Shortage",
            "Rugged Terrain",
            "Soil Erosion",
        ],
        "famous_products": [
            "عنب صعدة",
            "رمان حجة",
            "لوز الجوف",
            "عسل البن الشمالي",
            "قمح عمران",
        ],
        "famous_products_en": [
            "Sa'dah Grapes",
            "Hajjah Pomegranates",
            "Al-Jawf Almonds",
            "Northern Honey",
            "Amran Wheat",
        ],
        "traditional_irrigation": [
            "مدرجات حجرية",
            "قنوات محفورة",
            "برك تجميع",
            "نظام الحوضين",
        ],
        "traditional_irrigation_en": [
            "Stone Terraces",
            "Carved Channels",
            "Collection Ponds",
            "Double Basin System",
        ],
        "description": "منطقة جبلية باردة تعتمد على الزراعة البعلية والحبوب، تشتهر بالمدرجات الزراعية الأثرية",
        "description_en": "A cold mountainous region relying on rainfed agriculture and grains, famous for ancient agricultural terraces",
    },
    "southern_coast": {
        "name": "الساحل الجنوبي",
        "name_en": "Southern Coast",
        "governorates": ["عدن", "أبين", "لحج", "حضرموت الساحلية"],
        "climate": {
            "type": "حار رطب استوائي",
            "type_en": "Hot Humid Tropical",
            "avg_temp_summer": 36,
            "avg_temp_winter": 26,
            "rainfall_mm": 100,
            "humidity_percent": 75,
        },
        "altitude": "0-300م",
        "altitude_en": "0-300m",
        "soil_type": "رملية ساحلية",
        "soil_type_en": "Coastal Sandy",
        "water_sources": ["آبار ساحلية", "سيول موسمية", "تحلية مياه"],
        "water_sources_en": ["Coastal Wells", "Seasonal Floods", "Water Desalination"],
        "main_crops": [
            "جوز الهند",
            "موز",
            "بابايا",
            "أسماك",
            "خضروات",
            "قطن",
            "تبغ",
        ],
        "main_crops_en": [
            "Coconut",
            "Banana",
            "Papaya",
            "Fish",
            "Vegetables",
            "Cotton",
            "Tobacco",
        ],
        "planting_seasons": {
            "صيفي": {
                "months": ["مايو", "يونيو", "يوليو"],
                "months_en": ["May", "June", "July"],
                "crops": ["موز", "جوز الهند", "خضروات"],
            },
            "شتوي": {
                "months": ["أكتوبر", "نوفمبر"],
                "months_en": ["October", "November"],
                "crops": ["طماطم", "خيار", "فلفل"],
            },
        },
        "challenges": [
            "ارتفاع درجات الحرارة",
            "ملوحة المياه",
            "الرطوبة العالية",
            "الأعاصير",
        ],
        "challenges_en": [
            "High Temperatures",
            "Water Salinity",
            "High Humidity",
            "Cyclones",
        ],
        "famous_products": [
            "موز عدن",
            "جوز الهند الساحلي",
            "أسماك المحيط",
            "ملح البحر",
        ],
        "famous_products_en": [
            "Aden Bananas",
            "Coastal Coconuts",
            "Ocean Fish",
            "Sea Salt",
        ],
        "traditional_irrigation": [
            "آبار ساحلية",
            "ري بالتنقيط",
            "حصاد مياه الأمطار",
            "زراعة ساحلية",
        ],
        "traditional_irrigation_en": [
            "Coastal Wells",
            "Drip Irrigation",
            "Rainwater Harvesting",
            "Coastal Farming",
        ],
        "description": "ساحل استوائي يطل على خليج عدن والمحيط الهندي، يعتمد على صيد الأسماك والزراعة الاستوائية",
        "description_en": "A tropical coast overlooking the Gulf of Aden and Indian Ocean, relying on fishing and tropical agriculture",
    },
}

# تقويم المحاصيل التفصيلي
DETAILED_CROP_CALENDAR = {
    "بن_يمني": {
        "name": "البن اليمني",
        "name_en": "Yemeni Coffee",
        "varieties": ["حرازي", "يافعي", "مطري", "برعي", "إسماعيلي"],
        "regions": ["حراز", "يافع", "برع", "بني مطر"],
        "altitude_range": "1400-2400م",
        "lifecycle_years": 30,
        "first_harvest_year": 3,
        "peak_production_year": "7-15",
        "planting": {
            "hijri_months": ["ربيع الأول", "ربيع الثاني"],
            "gregorian_months": [3, 4],
            "lunar_mansions": [3, 4, 14, 23],  # الثريا، الدبران، السماك، سعد بلع
            "moon_phase": "متزايد",
            "method": "شتلات عمرها 6-12 شهر",
            "spacing_m": 2.5,
            "shade_requirement": "50-70%",
        },
        "care": {
            "irrigation": "أسبوعياً في الصيف",
            "fertilization": "مرتين سنوياً - ربيع وخريف",
            "pruning": "بعد الحصاد - القمر المتناقص",
            "pests": ["حفار الساق", "المن"],
            "diseases": ["صدأ الأوراق", "التبقع"],
        },
        "harvest": {
            "hijri_months": ["شوال", "ذو القعدة"],
            "gregorian_months": [10, 11],
            "lunar_mansions": [3, 13],  # الثريا، العواء
            "signs_of_ripeness": ["لون أحمر قانٍ", "سهولة الانفصال"],
            "method": "قطف يدوي انتقائي",
            "yield_kg_per_tree": 3,
        },
        "processing": {
            "drying_method": "تجفيف شمسي على السطوح",
            "drying_days": 21,
            "moisture_target_percent": 11,
            "storage": "أكياس خيش في مكان جاف",
        },
        "proverbs": ["قطف البن في الثريا، وجففه في الجوزاء", "البن يحب الظل والندى"],
        "market_price_yer_kg": 15000,
    },
    "قمح_يمني": {
        "name": "القمح اليمني",
        "name_en": "Yemeni Wheat",
        "varieties": ["بلدي", "كاما", "مصري"],
        "regions": ["صعدة", "ذمار", "إب", "تعز"],
        "altitude_range": "1500-2800م",
        "lifecycle_years": 1,
        "first_harvest_year": 1,
        "peak_production_year": "1",
        "planting": {
            "hijri_months": ["صفر", "ربيع الأول"],
            "gregorian_months": [10, 11, 12],
            "lunar_mansions": [1, 3, 13, 14, 22],  # الشرطين، الثريا، العواء، السماك
            "moon_phase": "متزايد",
            "method": "بذر مباشر - 140 كجم/هكتار",
            "spacing_m": 0.15,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "3-5 مرات خلال الموسم",
            "fertilization": "عند الزراعة وعند التفريع",
            "pruning": "لا يحتاج",
            "pests": ["المن", "الحفار"],
            "diseases": ["الصدأ الأصفر", "التفحم"],
        },
        "harvest": {
            "hijri_months": ["جمادى الأولى", "جمادى الآخرة"],
            "gregorian_months": [5, 6],
            "lunar_mansions": [10, 11, 12],  # الجبهة، الزبرة، الصرفة
            "signs_of_ripeness": ["اصفرار السنابل", "صلابة الحبة"],
            "method": "حصاد يدوي أو ميكانيكي",
            "yield_kg_per_tree": 2500,  # كجم/هكتار
        },
        "processing": {
            "drying_method": "تجفيف شمسي في الحقل",
            "drying_days": 7,
            "moisture_target_percent": 13,
            "storage": "مخازن جافة - صوامع",
        },
        "proverbs": [
            "القمح يُزرع في صفر، ويُحصد في جمادى",
            "لا تزرع القمح إلا والقمر متزايد",
        ],
        "market_price_yer_kg": 280,
    },
    "ذرة_رفيعة": {
        "name": "الذرة الرفيعة",
        "name_en": "Sorghum",
        "varieties": ["الصفراء", "البيضاء", "الحمراء", "السودانية"],
        "regions": ["تهامة", "الجوف", "مأرب", "حضرموت"],
        "altitude_range": "0-1800م",
        "lifecycle_years": 1,
        "first_harvest_year": 1,
        "peak_production_year": "1",
        "planting": {
            "hijri_months": ["رجب", "شعبان"],
            "gregorian_months": [6, 7, 8],
            "lunar_mansions": [1, 3, 7, 13, 14],  # الشرطين، الثريا، الذراع، العواء، السماك
            "moon_phase": "متزايد",
            "method": "بذر مباشر - 15-20 كجم/هكتار",
            "spacing_m": 0.4,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "حسب الأمطار - ري تكميلي",
            "fertilization": "سماد عضوي عند الزراعة",
            "pruning": "إزالة التفريعات الجانبية",
            "pests": ["دودة الساق", "المن", "الجراد"],
            "diseases": ["التفحم", "اللفحة"],
        },
        "harvest": {
            "hijri_months": ["ذو القعدة", "ذو الحجة"],
            "gregorian_months": [10, 11],
            "lunar_mansions": [10, 11, 12],  # الجبهة، الزبرة، الصرفة
            "signs_of_ripeness": ["صلابة الحبوب", "جفاف الأوراق"],
            "method": "قطع الرؤوس يدوياً",
            "yield_kg_per_tree": 3000,  # كجم/هكتار
        },
        "processing": {
            "drying_method": "تجفيف شمسي معلق",
            "drying_days": 14,
            "moisture_target_percent": 12,
            "storage": "أكياس في مخازن مرتفعة",
        },
        "proverbs": [
            "الذرة تُزرع مع السيل، وتُحصد قبل الويل",
            "إذا طلع سهيل زرع الذرة في السهل",
        ],
        "market_price_yer_kg": 200,
    },
    "عنب_يمني": {
        "name": "العنب اليمني",
        "name_en": "Yemeni Grapes",
        "varieties": ["العاصمي", "الرازقي", "البياض", "الأحمر"],
        "regions": ["صنعاء", "صعدة", "عمران", "ريمة"],
        "altitude_range": "1800-2400م",
        "lifecycle_years": 25,
        "first_harvest_year": 2,
        "peak_production_year": "5-15",
        "planting": {
            "hijri_months": ["صفر", "ربيع الأول", "ربيع الثاني"],
            "gregorian_months": [2, 3, 4],
            "lunar_mansions": [3, 4, 23, 24],  # الثريا، الدبران، سعد بلع، سعد السعود
            "moon_phase": "متزايد",
            "method": "عقل أو شتلات مطعمة",
            "spacing_m": 2.0,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "مرة كل أسبوعين",
            "fertilization": "سماد عضوي في الشتاء، كيماوي في الربيع",
            "pruning": "تقليم شتوي - القمر المتناقص",
            "pests": ["حشرة البق الدقيقي", "العنكبوت الأحمر"],
            "diseases": ["البياض الدقيقي", "العفن الرمادي"],
        },
        "harvest": {
            "hijri_months": ["شعبان", "رمضان"],
            "gregorian_months": [7, 8, 9],
            "lunar_mansions": [3, 13, 14],  # الثريا، العواء، السماك
            "signs_of_ripeness": ["تلون العناقيد", "حلاوة الطعم"],
            "method": "قطف يدوي للعناقيد",
            "yield_kg_per_tree": 40,
        },
        "processing": {
            "drying_method": "تجفيف شمسي للزبيب",
            "drying_days": 21,
            "moisture_target_percent": 15,
            "storage": "غرف تبريد للطازج - أكياس للزبيب",
        },
        "proverbs": ["العنب في الصيف زاد، وفي الشتاء مراد", "قلّم عنبك في المحاق يجيك العنقود راق"],
        "market_price_yer_kg": 800,
    },
    "نخيل_تمر": {
        "name": "نخيل التمر",
        "name_en": "Date Palm",
        "varieties": ["البرحي", "الصفري", "السكري", "المجهولي", "الصعيدي"],
        "regions": ["حضرموت", "مأرب", "الجوف", "تهامة"],
        "altitude_range": "0-1200م",
        "lifecycle_years": 80,
        "first_harvest_year": 4,
        "peak_production_year": "10-60",
        "planting": {
            "hijri_months": ["صفر", "ربيع الأول", "ربيع الثاني"],
            "gregorian_months": [2, 3, 4],
            "lunar_mansions": [3, 4, 14, 23, 24],  # الثريا، الدبران، السماك
            "moon_phase": "متزايد",
            "method": "فسائل عمرها 3-4 سنوات",
            "spacing_m": 8.0,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "كل أسبوعين - يتحمل الجفاف",
            "fertilization": "3 مرات سنوياً - سماد عضوي",
            "pruning": "إزالة السعف الجاف - القمر المتناقص",
            "pests": ["حفار ساق النخيل", "سوسة النخيل الحمراء", "دودة الطلع"],
            "diseases": ["تعفن الطلع", "الخامج"],
        },
        "harvest": {
            "hijri_months": ["رجب", "شعبان", "رمضان"],
            "gregorian_months": [7, 8, 9],
            "lunar_mansions": [3, 11, 13],  # الثريا، الزبرة، العواء
            "signs_of_ripeness": ["تغير اللون", "ليونة الثمرة"],
            "method": "قطف يدوي أو تسلق الشجرة",
            "yield_kg_per_tree": 100,
        },
        "processing": {
            "drying_method": "تجفيف شمسي أو على الشجرة",
            "drying_days": 30,
            "moisture_target_percent": 20,
            "storage": "غرف تبريد - صناديق خشبية",
        },
        "proverbs": [
            "النخلة تغرس في الربيع وتثمر في الصيف",
            "نخلتك اللي بالبيت، خير من نخل بالغيط",
        ],
        "market_price_yer_kg": 1200,
    },
    "موز_تهامة": {
        "name": "الموز التهامي",
        "name_en": "Tihama Banana",
        "varieties": ["موز السكري", "الهندي", "البلدي"],
        "regions": ["تهامة", "الحديدة", "حجة", "المحويت"],
        "altitude_range": "0-800م",
        "lifecycle_years": 10,
        "first_harvest_year": 1,
        "peak_production_year": "2-8",
        "planting": {
            "hijri_months": ["صفر", "ربيع الأول", "رجب"],
            "gregorian_months": [2, 3, 4, 7, 8],
            "lunar_mansions": [7, 8, 17, 26, 27],  # الذراع، النثرة، الإكليل، المقدم، المؤخر
            "moon_phase": "متزايد",
            "method": "خلفات من الأمهات",
            "spacing_m": 3.0,
            "shade_requirement": "لا يحتاج - يفضل الشمس",
        },
        "care": {
            "irrigation": "كل 3-5 أيام - يحتاج ماء كثير",
            "fertilization": "شهرياً - سماد عضوي وكيماوي",
            "pruning": "إزالة الأوراق الجافة والخلفات الزائدة",
            "pests": ["سوسة الموز", "التربس"],
            "diseases": ["مرض بنما", "تعفن القمة"],
        },
        "harvest": {
            "hijri_months": ["طوال العام"],
            "gregorian_months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "lunar_mansions": [7, 8, 17],  # المنازل المائية
            "signs_of_ripeness": ["امتلاء السباطة", "اصفرار خفيف"],
            "method": "قطع السباطة كاملة",
            "yield_kg_per_tree": 30,
        },
        "processing": {
            "drying_method": "استهلاك طازج - لا يجفف",
            "drying_days": 0,
            "moisture_target_percent": 75,
            "storage": "غرف تبريد 13-15 درجة",
        },
        "proverbs": [
            "الموز يحب الماي والطين",
            "موز تهامة في الصيف، مثل الذهب في الخريف",
        ],
        "market_price_yer_kg": 400,
    },
    "مانجو": {
        "name": "المانجو",
        "name_en": "Mango",
        "varieties": ["الفونس", "السندي", "السكري", "الكيت"],
        "regions": ["تهامة", "الحديدة", "أبين", "لحج"],
        "altitude_range": "0-600م",
        "lifecycle_years": 40,
        "first_harvest_year": 3,
        "peak_production_year": "8-30",
        "planting": {
            "hijri_months": ["صفر", "ربيع الأول", "ربيع الثاني"],
            "gregorian_months": [2, 3, 4],
            "lunar_mansions": [3, 4, 14, 23, 24],  # الثريا، الدبران، السماك، سعد بلع
            "moon_phase": "متزايد",
            "method": "شتلات مطعمة عمرها سنة",
            "spacing_m": 8.0,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "أسبوعياً - توقف قبل الإزهار",
            "fertilization": "3 مرات سنوياً",
            "pruning": "تقليم تشكيلي بعد الحصاد",
            "pests": ["ذبابة الفاكهة", "البق الدقيقي"],
            "diseases": ["البياض الدقيقي", "تعفن الثمار"],
        },
        "harvest": {
            "hijri_months": ["جمادى الأولى", "جمادى الآخرة", "رجب"],
            "gregorian_months": [5, 6, 7],
            "lunar_mansions": [3, 13, 14],  # الثريا، العواء، السماك
            "signs_of_ripeness": ["تغير اللون", "ليونة خفيفة"],
            "method": "قطف يدوي بترك عنق",
            "yield_kg_per_tree": 80,
        },
        "processing": {
            "drying_method": "استهلاك طازج أو تصنيع",
            "drying_days": 0,
            "moisture_target_percent": 80,
            "storage": "غرف تبريد 10-13 درجة",
        },
        "proverbs": [
            "المانجو شجرة مباركة، ظلها بارد وثمرها حلو",
            "مانجو الصيف تنسي الهم",
        ],
        "market_price_yer_kg": 600,
    },
    "رمان": {
        "name": "الرمان",
        "name_en": "Pomegranate",
        "varieties": ["الوندرفول", "البلدي", "الشامي", "المنفلوطي"],
        "regions": ["صنعاء", "ذمار", "إب", "تعز", "صعدة"],
        "altitude_range": "1200-2400م",
        "lifecycle_years": 30,
        "first_harvest_year": 2,
        "peak_production_year": "5-20",
        "planting": {
            "hijri_months": ["صفر", "ربيع الأول"],
            "gregorian_months": [2, 3],
            "lunar_mansions": [3, 4, 14, 23, 24],  # الثريا، الدبران، السماك
            "moon_phase": "متزايد",
            "method": "عقل أو شتلات",
            "spacing_m": 4.0,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "كل 10 أيام - تقليل عند النضج",
            "fertilization": "مرتين سنوياً - ربيع وخريف",
            "pruning": "إزالة الأفرع الجافة - القمر المتناقص",
            "pests": ["حفار الساق", "المن"],
            "diseases": ["تعفن الثمار", "البياض الدقيقي"],
        },
        "harvest": {
            "hijri_months": ["شعبان", "رمضان", "شوال"],
            "gregorian_months": [8, 9, 10],
            "lunar_mansions": [11, 12, 13],  # الزبرة، الصرفة، العواء
            "signs_of_ripeness": ["اللون الأحمر القاني", "صوت رنان عند النقر"],
            "method": "قطف يدوي بمقص",
            "yield_kg_per_tree": 50,
        },
        "processing": {
            "drying_method": "استهلاك طازج أو عصير",
            "drying_days": 0,
            "moisture_target_percent": 78,
            "storage": "غرف تبريد 5 درجات - 3 أشهر",
        },
        "proverbs": [
            "الرمان في الخريف تاج",
            "رمانة واحدة أحسن من عنقود فاسد",
        ],
        "market_price_yer_kg": 700,
    },
    "بصل_يمني": {
        "name": "البصل اليمني",
        "name_en": "Yemeni Onion",
        "varieties": ["الأحمر", "الأصفر", "الأبيض"],
        "regions": ["ذمار", "إب", "تعز", "الضالع"],
        "altitude_range": "1500-2600م",
        "lifecycle_years": 1,
        "first_harvest_year": 1,
        "peak_production_year": "1",
        "planting": {
            "hijri_months": ["ذو القعدة", "ذو الحجة", "محرم"],
            "gregorian_months": [10, 11, 12],
            "lunar_mansions": [17, 22, 23],  # الإكليل، سعد الذابح، سعد بلع
            "moon_phase": "متناقص",
            "method": "بذور أو شتل - 4 كجم بذور/هكتار",
            "spacing_m": 0.15,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "أسبوعياً - توقف قبل الحصاد بأسبوعين",
            "fertilization": "سماد عضوي عند الزراعة",
            "pruning": "لا يحتاج",
            "pests": ["ذبابة البصل", "التربس"],
            "diseases": ["البياض الزغبي", "العفن الأبيض"],
        },
        "harvest": {
            "hijri_months": ["ربيع الثاني", "جمادى الأولى"],
            "gregorian_months": [4, 5],
            "lunar_mansions": [17, 22],  # الإكليل، سعد الذابح
            "signs_of_ripeness": ["اصفرار الأوراق", "سقوط العرش"],
            "method": "قلع يدوي",
            "yield_kg_per_tree": 25000,  # كجم/هكتار
        },
        "processing": {
            "drying_method": "تجفيف هوائي في الظل",
            "drying_days": 14,
            "moisture_target_percent": 20,
            "storage": "معلق في مكان جاف وجيد التهوية",
        },
        "proverbs": [
            "البصل والثوم في القمر المتناقص",
            "بصل ذمار يشفي من الأمراض",
        ],
        "market_price_yer_kg": 250,
    },
    "ثوم_يمني": {
        "name": "الثوم اليمني",
        "name_en": "Yemeni Garlic",
        "varieties": ["البلدي", "الصيني", "المصري"],
        "regions": ["ذمار", "إب", "تعز", "البيضاء"],
        "altitude_range": "1500-2600م",
        "lifecycle_years": 1,
        "first_harvest_year": 1,
        "peak_production_year": "1",
        "planting": {
            "hijri_months": ["ذو القعدة", "ذو الحجة"],
            "gregorian_months": [10, 11],
            "lunar_mansions": [17, 22, 23],  # الإكليل، سعد الذابح، سعد بلع
            "moon_phase": "متناقص",
            "method": "فصوص - 800 كجم/هكتار",
            "spacing_m": 0.15,
            "shade_requirement": "لا يحتاج",
        },
        "care": {
            "irrigation": "كل 10 أيام - توقف قبل الحصاد",
            "fertilization": "سماد عضوي متخمر",
            "pruning": "إزالة الشماريخ الزهرية",
            "pests": ["التربس", "الديدان الخيطية"],
            "diseases": ["العفن الأبيض", "الصدأ"],
        },
        "harvest": {
            "hijri_months": ["ربيع الثاني", "جمادى الأولى", "جمادى الآخرة"],
            "gregorian_months": [5, 6],
            "lunar_mansions": [17, 22],  # الإكليل، سعد الذابح
            "signs_of_ripeness": ["اصفرار الأوراق", "جفاف العرش"],
            "method": "قلع يدوي كامل",
            "yield_kg_per_tree": 8000,  # كجم/هكتار
        },
        "processing": {
            "drying_method": "تجفيف هوائي معلق",
            "drying_days": 21,
            "moisture_target_percent": 35,
            "storage": "معلق في ضفائر - مكان جاف",
        },
        "proverbs": [
            "الثوم دواء وغذاء",
            "يُزرع في القمر المتناقص لتقوية الجذور",
        ],
        "market_price_yer_kg": 800,
    },
}


# الأبراج الزراعية
ZODIAC_FARMING = {
    "aries": {"name": "الحمل", "element": "نار", "fertility": "جافة", "score": 4},
    "taurus": {"name": "الثور", "element": "أرض", "fertility": "خصبة جداً", "score": 9},
    "gemini": {"name": "الجوزاء", "element": "هواء", "fertility": "جافة", "score": 3},
    "cancer": {
        "name": "السرطان",
        "element": "ماء",
        "fertility": "خصبة جداً",
        "score": 10,
    },
    "leo": {"name": "الأسد", "element": "نار", "fertility": "جافة جداً", "score": 2},
    "virgo": {"name": "العذراء", "element": "أرض", "fertility": "جافة", "score": 5},
    "libra": {"name": "الميزان", "element": "هواء", "fertility": "متوسطة", "score": 6},
    "scorpio": {
        "name": "العقرب",
        "element": "ماء",
        "fertility": "خصبة جداً",
        "score": 9,
    },
    "sagittarius": {"name": "القوس", "element": "نار", "fertility": "جافة", "score": 3},
    "capricorn": {"name": "الجدي", "element": "أرض", "fertility": "خصبة", "score": 7},
    "aquarius": {"name": "الدلو", "element": "هواء", "fertility": "جافة", "score": 4},
    "pisces": {"name": "الحوت", "element": "ماء", "fertility": "خصبة جداً", "score": 9},
}


# ═══════════════════════════════════════════════════════════════════════════════
# نماذج البيانات (Pydantic Models)
# ═══════════════════════════════════════════════════════════════════════════════


class MoonPhase(BaseModel):
    """مرحلة القمر"""

    phase_key: str = Field(..., description="مفتاح المرحلة")
    name: str = Field(..., description="اسم المرحلة بالعربية")
    name_en: str = Field(..., description="اسم المرحلة بالإنجليزية")
    icon: str = Field(..., description="أيقونة المرحلة")
    illumination: float = Field(..., ge=0, le=100, description="نسبة الإضاءة")
    age_days: float = Field(..., description="عمر القمر بالأيام")
    is_waxing: bool = Field(..., description="هل القمر متزايد")
    farming_good: bool = Field(..., description="هل مناسب للزراعة")


class LunarMansion(BaseModel):
    """منزلة قمرية"""

    number: int = Field(..., ge=1, le=28, description="رقم المنزلة")
    name: str = Field(..., description="اسم المنزلة بالعربية")
    name_en: str = Field(..., description="اسم المنزلة بالإنجليزية")
    constellation: str = Field(..., description="البرج")
    constellation_en: str = Field(..., description="البرج بالإنجليزية")
    element: str = Field(..., description="العنصر")
    farming: str = Field(..., description="حالة الزراعة")
    farming_score: int = Field(..., ge=1, le=10, description="درجة ملاءمة الزراعة")
    crops: list[str] = Field(..., description="المحاصيل الموصى بها")
    activities: list[str] = Field(..., description="الأنشطة الموصى بها")
    avoid: list[str] = Field(..., description="الأنشطة التي يجب تجنبها")
    description: str = Field(..., description="وصف المنزلة")


class HijriDate(BaseModel):
    """التاريخ الهجري"""

    year: int = Field(..., description="السنة الهجرية")
    month: int = Field(..., ge=1, le=12, description="الشهر")
    day: int = Field(..., ge=1, le=30, description="اليوم")
    month_name: str = Field(..., description="اسم الشهر بالعربية")
    month_name_en: str = Field(..., description="اسم الشهر بالإنجليزية")
    weekday: str = Field(..., description="اليوم من الأسبوع")


class ZodiacInfo(BaseModel):
    """معلومات البرج"""

    name: str = Field(..., description="اسم البرج بالعربية")
    name_en: str = Field(..., description="اسم البرج بالإنجليزية")
    element: str = Field(..., description="العنصر")
    fertility: str = Field(..., description="الخصوبة")
    score: int = Field(..., ge=1, le=10, description="درجة ملاءمة الزراعة")


class SeasonInfo(BaseModel):
    """معلومات الموسم"""

    name: str = Field(..., description="اسم الموسم بالعربية")
    name_en: str = Field(..., description="اسم الموسم بالإنجليزية")
    description: str = Field(..., description="وصف الموسم")
    main_crops: list[str] = Field(..., description="المحاصيل الرئيسية")
    activities: list[str] = Field(..., description="الأنشطة الموصى بها")


class FarmingRecommendation(BaseModel):
    """توصية زراعية"""

    activity: str = Field(..., description="النشاط")
    suitability: str = Field(..., description="مدى الملاءمة")
    suitability_score: int = Field(..., ge=1, le=10, description="درجة الملاءمة")
    reason: str = Field(..., description="السبب")
    best_time: str | None = Field(None, description="أفضل وقت")


class DailyAstronomicalData(BaseModel):
    """البيانات الفلكية اليومية"""

    date_gregorian: str = Field(..., description="التاريخ الميلادي")
    date_hijri: HijriDate = Field(..., description="التاريخ الهجري")
    moon_phase: MoonPhase = Field(..., description="مرحلة القمر")
    lunar_mansion: LunarMansion = Field(..., description="المنزلة القمرية")
    zodiac: ZodiacInfo = Field(..., description="البرج")
    season: SeasonInfo = Field(..., description="الموسم")
    overall_farming_score: int = Field(..., ge=1, le=10, description="درجة الزراعة الإجمالية")
    recommendations: list[FarmingRecommendation] = Field(..., description="التوصيات الزراعية")


class WeeklyForecast(BaseModel):
    """التوقعات الأسبوعية"""

    start_date: str
    end_date: str
    days: list[DailyAstronomicalData]
    best_planting_days: list[str]
    best_harvesting_days: list[str]
    avoid_days: list[str]


class CropCalendar(BaseModel):
    """تقويم المحصول"""

    crop_name: str
    crop_name_en: str
    best_planting_mansions: list[int]
    best_moon_phases: list[str]
    best_zodiac_signs: list[str]
    optimal_months: list[int]
    planting_guide: str
    current_suitability: int


# ═══════════════════════════════════════════════════════════════════════════════
# الحسابات الفلكية
# ═══════════════════════════════════════════════════════════════════════════════


def calculate_julian_day(year: int, month: int, day: int) -> float:
    """حساب اليوم اليولياني"""
    if month <= 2:
        year -= 1
        month += 12

    A = int(year / 100)
    B = 2 - A + int(A / 4)

    JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    return JD


def calculate_moon_phase(dt: datetime) -> dict:
    """حساب مرحلة القمر بدقة"""
    # القمر الجديد المرجعي: 6 يناير 2000
    reference_new_moon = datetime(2000, 1, 6, 18, 14)
    synodic_month = 29.530588853  # الشهر القمري بالأيام

    days_since_reference = (dt - reference_new_moon).total_seconds() / 86400
    moon_age = days_since_reference % synodic_month

    # نسبة الإضاءة
    illumination = (1 - math.cos(2 * math.pi * moon_age / synodic_month)) / 2 * 100

    # تحديد المرحلة
    phase_index = int((moon_age / synodic_month) * 8) % 8
    phase_keys = list(MOON_PHASES.keys())
    phase_key = phase_keys[phase_index]
    phase_data = MOON_PHASES[phase_key]

    is_waxing = moon_age < synodic_month / 2

    return MoonPhase(
        phase_key=phase_key,
        name=phase_data["name"],
        name_en=phase_data["name_en"],
        icon=phase_data["icon"],
        illumination=round(illumination, 1),
        age_days=round(moon_age, 2),
        is_waxing=is_waxing,
        farming_good=phase_data["farming_good"],
    )


def calculate_lunar_mansion(dt: datetime) -> LunarMansion:
    """حساب المنزلة القمرية"""
    # المنزلة المرجعية: 1 يناير 2000 = المنزلة 1 (الشرطين)
    reference_date = datetime(2000, 1, 1)
    days_since_reference = (dt - reference_date).days

    # كل منزلة ≈ 13 يوم تقريباً (365.25 / 28)
    mansion_period = 365.25 / 28

    mansion_number = int((days_since_reference % 365.25) / mansion_period) + 1
    if mansion_number > 28:
        mansion_number = 1

    mansion_data = LUNAR_MANSIONS[mansion_number]

    return LunarMansion(
        number=mansion_number,
        name=mansion_data["name"],
        name_en=mansion_data["name_en"],
        constellation=mansion_data["constellation"],
        constellation_en=mansion_data["constellation_en"],
        element=mansion_data["element"],
        farming=mansion_data["farming"],
        farming_score=mansion_data["farming_score"],
        crops=mansion_data["crops"],
        activities=mansion_data["activities"],
        avoid=mansion_data["avoid"],
        description=mansion_data["description"],
    )


def gregorian_to_hijri(year: int, month: int, day: int) -> HijriDate:
    """تحويل من ميلادي إلى هجري (خوارزمية تقريبية)"""
    # حساب اليوم اليولياني
    jd = calculate_julian_day(year, month, day)

    # تحويل إلى هجري
    # نقطة المرجع: 1 محرم 1 هـ = 16 يوليو 622 م = JD 1948439.5
    epoch = 1948439.5

    days_since_epoch = jd - epoch

    # السنة الهجرية (تقريبي)
    hijri_year = int(days_since_epoch / 354.36667) + 1

    # حساب بداية السنة
    days_in_year = days_since_epoch - int((hijri_year - 1) * 354.36667)

    # الشهر واليوم
    hijri_month = 1
    remaining_days = days_in_year

    for m in range(1, 13):
        month_days = HIJRI_MONTHS[m]["days"]
        if remaining_days <= month_days:
            hijri_month = m
            break
        remaining_days -= month_days

    hijri_day = max(1, min(30, int(remaining_days) + 1))

    # اليوم من الأسبوع
    weekdays = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    weekday = weekdays[int(jd + 1.5) % 7]

    return HijriDate(
        year=hijri_year,
        month=hijri_month,
        day=hijri_day,
        month_name=HIJRI_MONTHS[hijri_month]["name"],
        month_name_en=HIJRI_MONTHS[hijri_month]["name_en"],
        weekday=weekday,
    )


def get_zodiac_sign(dt: datetime) -> ZodiacInfo:
    """الحصول على البرج الشمسي"""
    # تواريخ الأبراج التقريبية
    zodiac_dates = [
        (1, 20, "aquarius"),
        (2, 19, "pisces"),
        (3, 21, "aries"),
        (4, 20, "taurus"),
        (5, 21, "gemini"),
        (6, 21, "cancer"),
        (7, 23, "leo"),
        (8, 23, "virgo"),
        (9, 23, "libra"),
        (10, 23, "scorpio"),
        (11, 22, "sagittarius"),
        (12, 22, "capricorn"),
    ]

    month, day = dt.month, dt.day

    sign_key = "capricorn"  # افتراضي
    for zd in zodiac_dates:
        if (month == zd[0] and day >= zd[1]) or (
            month == zd[0] + 1 and day < zodiac_dates[(zodiac_dates.index(zd) + 1) % 12][1]
        ):
            sign_key = zd[2]
            break

    if month == 12 and day >= 22 or month == 1 and day < 20:
        sign_key = "capricorn"

    # تحديد البرج بناءً على الشهر والتاريخ
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        sign_key = "aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        sign_key = "taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        sign_key = "gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        sign_key = "cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        sign_key = "leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        sign_key = "virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        sign_key = "libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        sign_key = "scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        sign_key = "sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        sign_key = "capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        sign_key = "aquarius"
    else:
        sign_key = "pisces"

    zodiac_data = ZODIAC_FARMING[sign_key]

    return ZodiacInfo(
        name=zodiac_data["name"],
        name_en=sign_key.capitalize(),
        element=zodiac_data["element"],
        fertility=zodiac_data["fertility"],
        score=zodiac_data["score"],
    )


def get_current_season(month: int) -> SeasonInfo:
    """الحصول على الموسم الحالي"""
    for _season_key, season_data in YEMENI_SEASONS.items():
        if month in season_data["months"]:
            return SeasonInfo(
                name=season_data["name"],
                name_en=season_data["name_en"],
                description=season_data["description"],
                main_crops=season_data["main_crops"],
                activities=season_data["activities"],
            )

    # افتراضي
    return SeasonInfo(
        name="غير محدد", name_en="Unknown", description="", main_crops=[], activities=[]
    )


def calculate_farming_recommendations(
    moon_phase: MoonPhase, lunar_mansion: LunarMansion, zodiac: ZodiacInfo
) -> list[FarmingRecommendation]:
    """حساب التوصيات الزراعية"""
    recommendations = []

    # توصية الزراعة
    planting_score = (lunar_mansion.farming_score + zodiac.score) // 2
    if moon_phase.is_waxing:
        planting_score = min(10, planting_score + 2)

    planting_suitability = (
        "ممتازة"
        if planting_score >= 8
        else ("جيدة" if planting_score >= 6 else "متوسطة" if planting_score >= 4 else "ضعيفة")
    )

    recommendations.append(
        FarmingRecommendation(
            activity="زراعة",
            suitability=planting_suitability,
            suitability_score=planting_score,
            reason=f"المنزلة: {lunar_mansion.name} ({lunar_mansion.farming}), القمر: {moon_phase.name}",
            best_time="الصباح الباكر" if planting_score >= 6 else None,
        )
    )

    # توصية الري
    irrigation_score = 5
    if zodiac.element == "ماء":
        irrigation_score += 3
    if lunar_mansion.element == "ماء":
        irrigation_score += 2
    irrigation_score = min(10, irrigation_score)

    recommendations.append(
        FarmingRecommendation(
            activity="ري",
            suitability=(
                "ممتازة" if irrigation_score >= 8 else "جيدة" if irrigation_score >= 6 else "متوسطة"
            ),
            suitability_score=irrigation_score,
            reason=f"عنصر البرج: {zodiac.element}, عنصر المنزلة: {lunar_mansion.element}",
            best_time="الفجر أو المغرب",
        )
    )

    # توصية الحصاد
    harvest_score = 5
    if not moon_phase.is_waxing:  # القمر المتناقص أفضل للحصاد
        harvest_score += 3
    if zodiac.element in ["أرض", "نار"]:
        harvest_score += 2
    harvest_score = min(10, harvest_score)

    recommendations.append(
        FarmingRecommendation(
            activity="حصاد",
            suitability=(
                "ممتازة" if harvest_score >= 8 else "جيدة" if harvest_score >= 6 else "متوسطة"
            ),
            suitability_score=harvest_score,
            reason=f"القمر {'متناقص' if not moon_phase.is_waxing else 'متزايد'} - {'مناسب' if not moon_phase.is_waxing else 'غير مثالي'} للحصاد",
            best_time="منتصف النهار" if harvest_score >= 6 else None,
        )
    )

    # توصية التقليم
    pruning_score = 5
    if not moon_phase.is_waxing:
        pruning_score += 2
    if zodiac.element == "هواء":
        pruning_score += 2
    pruning_score = min(10, pruning_score)

    recommendations.append(
        FarmingRecommendation(
            activity="تقليم",
            suitability=(
                "ممتازة" if pruning_score >= 8 else "جيدة" if pruning_score >= 6 else "متوسطة"
            ),
            suitability_score=pruning_score,
            reason="القمر المتناقص أفضل للتقليم",
            best_time="الصباح",
        )
    )

    return recommendations


def calculate_overall_score(
    moon_phase: MoonPhase, lunar_mansion: LunarMansion, zodiac: ZodiacInfo
) -> int:
    """حساب الدرجة الإجمالية للزراعة"""
    base_score = lunar_mansion.farming_score

    # تأثير مرحلة القمر
    if moon_phase.farming_good:
        base_score += 1
    else:
        base_score -= 1

    # تأثير البرج
    base_score = (base_score + zodiac.score) // 2

    return max(1, min(10, base_score))


def get_daily_astronomical_data(dt: datetime) -> DailyAstronomicalData:
    """الحصول على البيانات الفلكية اليومية"""
    moon_phase = calculate_moon_phase(dt)
    lunar_mansion = calculate_lunar_mansion(dt)
    zodiac = get_zodiac_sign(dt)
    season = get_current_season(dt.month)
    hijri = gregorian_to_hijri(dt.year, dt.month, dt.day)

    recommendations = calculate_farming_recommendations(moon_phase, lunar_mansion, zodiac)
    overall_score = calculate_overall_score(moon_phase, lunar_mansion, zodiac)

    return DailyAstronomicalData(
        date_gregorian=dt.strftime("%Y-%m-%d"),
        date_hijri=hijri,
        moon_phase=moon_phase,
        lunar_mansion=lunar_mansion,
        zodiac=zodiac,
        season=season,
        overall_farming_score=overall_score,
        recommendations=recommendations,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# نقاط النهاية (API Endpoints)
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/healthz", tags=["Health"])
def health_check():
    """التحقق من صحة الخدمة"""
    return {
        "status": "healthy",
        "service": "astronomical-calendar",
        "version": VERSION,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    return {
        "status": "ready",
        "service": "astronomical-calendar",
        "version": VERSION,
        "checks": {
            "service": "ready",
        },
    }


@app.get("/v1/today", response_model=DailyAstronomicalData, tags=["Calendar"])
def get_today():
    """
    الحصول على البيانات الفلكية لليوم الحالي

    يرجع:
    - التاريخ الهجري
    - مرحلة القمر
    - المنزلة القمرية
    - البرج
    - الموسم الزراعي
    - التوصيات الزراعية
    """
    return get_daily_astronomical_data(datetime.now(UTC))


@app.get("/v1/date/{date_str}", response_model=DailyAstronomicalData, tags=["Calendar"])
def get_date(date_str: str):
    """
    الحصول على البيانات الفلكية لتاريخ محدد

    المعطيات:
    - date_str: التاريخ بصيغة YYYY-MM-DD
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return get_daily_astronomical_data(dt)
    except ValueError:
        raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD")


@app.get("/v1/week", response_model=WeeklyForecast, tags=["Calendar"])
def get_weekly_forecast(
    start_date: str | None = Query(None, description="تاريخ البداية (YYYY-MM-DD)"),
):
    """
    الحصول على التوقعات الفلكية الأسبوعية

    يرجع أفضل أيام الزراعة والحصاد والأيام التي يجب تجنبها
    """
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        start = datetime.now(UTC)

    days = []
    best_planting = []
    best_harvesting = []
    avoid_days = []

    for i in range(7):
        dt = start + timedelta(days=i)
        data = get_daily_astronomical_data(dt)
        days.append(data)

        date_str = dt.strftime("%Y-%m-%d")

        if data.overall_farming_score >= 7:
            best_planting.append(date_str)

        # أفضل أيام الحصاد: القمر متناقص + درجة جيدة
        harvest_rec = next((r for r in data.recommendations if r.activity == "حصاد"), None)
        if harvest_rec and harvest_rec.suitability_score >= 7:
            best_harvesting.append(date_str)

        if data.overall_farming_score <= 3:
            avoid_days.append(date_str)

    end = start + timedelta(days=6)

    return WeeklyForecast(
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        days=days,
        best_planting_days=best_planting,
        best_harvesting_days=best_harvesting,
        avoid_days=avoid_days,
    )


@app.get("/v1/moon-phase", response_model=MoonPhase, tags=["Astronomy"])
def get_moon_phase(date_str: str | None = Query(None, description="التاريخ (YYYY-MM-DD)")):
    """الحصول على مرحلة القمر"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.now(UTC)

    return calculate_moon_phase(dt)


@app.get("/v1/lunar-mansion", response_model=LunarMansion, tags=["Astronomy"])
def get_lunar_mansion(date_str: str | None = Query(None, description="التاريخ (YYYY-MM-DD)")):
    """الحصول على المنزلة القمرية الحالية"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.now(UTC)

    return calculate_lunar_mansion(dt)


@app.get("/v1/lunar-mansions", tags=["Reference"])
def list_lunar_mansions():
    """قائمة جميع المنازل القمرية الـ 28"""
    mansions = []
    for num, data in LUNAR_MANSIONS.items():
        mansions.append(
            {
                "number": num,
                "name": data["name"],
                "name_en": data["name_en"],
                "constellation": data["constellation"],
                "element": data["element"],
                "farming_score": data["farming_score"],
                "crops": data["crops"],
            }
        )
    return {"mansions": mansions, "total": 28}


@app.get("/v1/hijri", response_model=HijriDate, tags=["Calendar"])
def get_hijri_date(date_str: str | None = Query(None, description="التاريخ الميلادي (YYYY-MM-DD)")):
    """تحويل تاريخ ميلادي إلى هجري"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.now(UTC)

    return gregorian_to_hijri(dt.year, dt.month, dt.day)


@app.get("/v1/hijri-months", tags=["Reference"])
def list_hijri_months():
    """قائمة الأشهر الهجرية"""
    return {"months": HIJRI_MONTHS}


@app.get("/v1/zodiac", response_model=ZodiacInfo, tags=["Astronomy"])
def get_zodiac(date_str: str | None = Query(None, description="التاريخ (YYYY-MM-DD)")):
    """الحصول على البرج الشمسي"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.now(UTC)

    return get_zodiac_sign(dt)


@app.get("/v1/zodiac-farming", tags=["Reference"])
def list_zodiac_farming():
    """قائمة الأبراج مع معلومات الخصوبة الزراعية"""
    return {"zodiac_signs": ZODIAC_FARMING}


@app.get("/v1/seasons", tags=["Reference"])
def list_seasons():
    """قائمة المواسم الزراعية اليمنية"""
    return {"seasons": YEMENI_SEASONS}


@app.get("/v1/current-season", response_model=SeasonInfo, tags=["Calendar"])
def get_current_season_info():
    """الحصول على الموسم الزراعي الحالي"""
    return get_current_season(datetime.now(UTC).month)


@app.get("/v1/crop-calendar/{crop_name}", response_model=CropCalendar, tags=["Crops"])
def get_crop_calendar(crop_name: str):
    """
    الحصول على التقويم الفلكي لمحصول معين

    المحاصيل المدعومة: قمح، شعير، ذرة، طماطم، بن، موز، بصل، ثوم
    """
    crop_calendars = {
        "قمح": {
            "crop_name": "قمح",
            "crop_name_en": "Wheat",
            "best_planting_mansions": [1, 3, 4, 13, 14, 22, 23],
            "best_moon_phases": ["waxing_crescent", "first_quarter", "waxing_gibbous"],
            "best_zodiac_signs": ["taurus", "cancer", "scorpio", "pisces"],
            "optimal_months": [10, 11, 12],
            "planting_guide": "يُزرع في منازل الثريا والدبران والسماك، في القمر المتزايد، خلال أشهر الخريف",
        },
        "wheat": {
            "crop_name": "قمح",
            "crop_name_en": "Wheat",
            "best_planting_mansions": [1, 3, 4, 13, 14, 22, 23],
            "best_moon_phases": ["waxing_crescent", "first_quarter", "waxing_gibbous"],
            "best_zodiac_signs": ["taurus", "cancer", "scorpio", "pisces"],
            "optimal_months": [10, 11, 12],
            "planting_guide": "Plant during Thuraya, Dabaran, Simak mansions, in waxing moon, during autumn",
        },
        "طماطم": {
            "crop_name": "طماطم",
            "crop_name_en": "Tomato",
            "best_planting_mansions": [3, 7, 8, 14, 24],
            "best_moon_phases": ["waxing_crescent", "first_quarter"],
            "best_zodiac_signs": ["cancer", "scorpio", "pisces", "taurus"],
            "optimal_months": [2, 3, 9, 10],
            "planting_guide": "تُزرع في منزلة الثريا والذراع، في القمر المتزايد، في الربيع أو الخريف",
        },
        "tomato": {
            "crop_name": "طماطم",
            "crop_name_en": "Tomato",
            "best_planting_mansions": [3, 7, 8, 14, 24],
            "best_moon_phases": ["waxing_crescent", "first_quarter"],
            "best_zodiac_signs": ["cancer", "scorpio", "pisces", "taurus"],
            "optimal_months": [2, 3, 9, 10],
            "planting_guide": "Plant during Thuraya, Dhira mansions, in waxing moon, in spring or autumn",
        },
        "بن": {
            "crop_name": "بن",
            "crop_name_en": "Coffee",
            "best_planting_mansions": [3, 4, 14, 23, 24],
            "best_moon_phases": ["first_quarter", "waxing_gibbous"],
            "best_zodiac_signs": ["taurus", "cancer", "capricorn"],
            "optimal_months": [3, 4],
            "planting_guide": "يُغرس في منازل الثريا وسعد بلع، في الربيع، القمر المتزايد",
        },
        "coffee": {
            "crop_name": "بن",
            "crop_name_en": "Coffee",
            "best_planting_mansions": [3, 4, 14, 23, 24],
            "best_moon_phases": ["first_quarter", "waxing_gibbous"],
            "best_zodiac_signs": ["taurus", "cancer", "capricorn"],
            "optimal_months": [3, 4],
            "planting_guide": "Plant during Thuraya, Sa'd Bula mansions, in spring, waxing moon",
        },
        "موز": {
            "crop_name": "موز",
            "crop_name_en": "Banana",
            "best_planting_mansions": [7, 8, 17, 26, 27],
            "best_moon_phases": ["first_quarter", "full_moon"],
            "best_zodiac_signs": ["cancer", "scorpio", "pisces"],
            "optimal_months": [2, 3, 4],
            "planting_guide": "يُغرس في المنازل المائية، في القمر المتزايد، في الربيع",
        },
        "بصل": {
            "crop_name": "بصل",
            "crop_name_en": "Onion",
            "best_planting_mansions": [17, 22, 23],
            "best_moon_phases": ["waning_gibbous", "last_quarter"],
            "best_zodiac_signs": ["capricorn", "taurus", "virgo"],
            "optimal_months": [10, 11],
            "planting_guide": "يُزرع في القمر المتناقص لتقوية الجذور، في الخريف",
        },
        "ثوم": {
            "crop_name": "ثوم",
            "crop_name_en": "Garlic",
            "best_planting_mansions": [17, 22, 23],
            "best_moon_phases": ["waning_gibbous", "last_quarter"],
            "best_zodiac_signs": ["capricorn", "taurus", "scorpio"],
            "optimal_months": [10, 11],
            "planting_guide": "يُزرع في القمر المتناقص، في منازل الإكليل وسعد الذابح",
        },
        "ذرة": {
            "crop_name": "ذرة",
            "crop_name_en": "Corn/Maize",
            "best_planting_mansions": [1, 3, 13, 14, 24],
            "best_moon_phases": ["waxing_crescent", "first_quarter"],
            "best_zodiac_signs": ["cancer", "scorpio", "pisces", "taurus"],
            "optimal_months": [6, 7],
            "planting_guide": "تُزرع مع بداية الأمطار الموسمية، في منزلة الثريا أو السماك",
        },
    }

    crop_key = crop_name.lower()
    if crop_key not in crop_calendars:
        raise HTTPException(
            status_code=404,
            detail=f"المحصول '{crop_name}' غير موجود. المحاصيل المدعومة: قمح، طماطم، بن، موز، بصل، ثوم، ذرة",
        )

    crop_data = crop_calendars[crop_key]

    # حساب ملاءمة اليوم الحالي
    today = get_daily_astronomical_data(datetime.now(UTC))
    current_suitability = 5

    if today.lunar_mansion.number in crop_data["best_planting_mansions"]:
        current_suitability += 2
    if today.moon_phase.phase_key in crop_data["best_moon_phases"]:
        current_suitability += 2
    if datetime.now(UTC).month in crop_data["optimal_months"]:
        current_suitability += 1

    current_suitability = min(10, current_suitability)

    return CropCalendar(
        crop_name=crop_data["crop_name"],
        crop_name_en=crop_data["crop_name_en"],
        best_planting_mansions=crop_data["best_planting_mansions"],
        best_moon_phases=crop_data["best_moon_phases"],
        best_zodiac_signs=crop_data["best_zodiac_signs"],
        optimal_months=crop_data["optimal_months"],
        planting_guide=crop_data["planting_guide"],
        current_suitability=current_suitability,
    )


@app.get("/v1/crops", tags=["Crops"])
def list_supported_crops():
    """قائمة المحاصيل المدعومة"""
    return {
        "crops": [
            {"name": "قمح", "name_en": "Wheat"},
            {"name": "شعير", "name_en": "Barley"},
            {"name": "ذرة", "name_en": "Corn/Maize"},
            {"name": "طماطم", "name_en": "Tomato"},
            {"name": "بن", "name_en": "Coffee"},
            {"name": "موز", "name_en": "Banana"},
            {"name": "بصل", "name_en": "Onion"},
            {"name": "ثوم", "name_en": "Garlic"},
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# المناطق الزراعية اليمنية - Yemeni Agricultural Regions
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/regions", tags=["Yemeni Heritage"])
def get_regions():
    """
    المناطق الزراعية اليمنية

    يرجع قائمة بجميع المناطق الزراعية الرئيسية في اليمن مع معلومات أساسية عن كل منطقة:
    - سهل تهامة
    - المرتفعات الوسطى
    - الهضبة الشرقية
    - المرتفعات الشمالية
    - الساحل الجنوبي
    """
    regions_summary = []
    for region_id, region_data in YEMENI_AGRICULTURAL_REGIONS.items():
        regions_summary.append(
            {
                "id": region_id,
                "name": region_data["name"],
                "name_en": region_data["name_en"],
                "governorates": region_data["governorates"],
                "climate_type": region_data["climate"]["type"],
                "altitude": region_data["altitude"],
                "main_crops_count": len(region_data["main_crops"]),
                "famous_products": region_data["famous_products"][:3],  # Top 3
                "description": region_data["description"],
            }
        )

    return {
        "regions": regions_summary,
        "total": len(regions_summary),
        "note": "استخدم /v1/regions/{region_id} للحصول على تفاصيل كاملة لمنطقة معينة",
    }


@app.get("/v1/regions/{region_id}", tags=["Yemeni Heritage"])
def get_region(region_id: str):
    """
    تفاصيل منطقة زراعية

    يرجع معلومات تفصيلية عن منطقة زراعية محددة تشمل:
    - المعلومات الجغرافية والمناخية
    - المحاصيل الرئيسية
    - مواسم الزراعة
    - التحديات الزراعية
    - المنتجات الشهيرة
    - أنظمة الري التقليدية

    المناطق المتاحة: tihama, central_highlands, eastern_plateau, northern_highlands, southern_coast
    """
    if region_id not in YEMENI_AGRICULTURAL_REGIONS:
        available_regions = list(YEMENI_AGRICULTURAL_REGIONS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"المنطقة '{region_id}' غير موجودة. المناطق المتاحة: {', '.join(available_regions)}",
        )

    region_data = YEMENI_AGRICULTURAL_REGIONS[region_id]

    # حساب أفضل وقت للزراعة حالياً
    current_month = datetime.now(UTC).month
    current_season = None
    recommended_crops = []

    # تحديد الموسم الحالي
    month_names_ar = {
        1: "يناير",
        2: "فبراير",
        3: "مارس",
        4: "أبريل",
        5: "مايو",
        6: "يونيو",
        7: "يوليو",
        8: "أغسطس",
        9: "سبتمبر",
        10: "أكتوبر",
        11: "نوفمبر",
        12: "ديسمبر",
    }

    current_month_name = month_names_ar[current_month]

    # البحث عن الموسم الحالي
    for season_name, season_info in region_data["planting_seasons"].items():
        if current_month_name in season_info["months"]:
            current_season = season_name
            recommended_crops = season_info["crops"]
            break

    return {
        "id": region_id,
        "basic_info": {
            "name": region_data["name"],
            "name_en": region_data["name_en"],
            "governorates": region_data["governorates"],
            "description": region_data["description"],
            "description_en": region_data["description_en"],
        },
        "geography": {
            "altitude": region_data["altitude"],
            "altitude_en": region_data["altitude_en"],
            "soil_type": region_data["soil_type"],
            "soil_type_en": region_data["soil_type_en"],
        },
        "climate": region_data["climate"],
        "water": {
            "sources": region_data["water_sources"],
            "sources_en": region_data["water_sources_en"],
            "traditional_irrigation": region_data["traditional_irrigation"],
            "traditional_irrigation_en": region_data["traditional_irrigation_en"],
        },
        "agriculture": {
            "main_crops": region_data["main_crops"],
            "main_crops_en": region_data["main_crops_en"],
            "planting_seasons": region_data["planting_seasons"],
            "famous_products": region_data["famous_products"],
            "famous_products_en": region_data["famous_products_en"],
        },
        "challenges": {
            "list": region_data["challenges"],
            "list_en": region_data["challenges_en"],
        },
        "current_recommendations": {
            "month": current_month_name,
            "season": current_season if current_season else "غير محدد",
            "recommended_crops": recommended_crops
            if recommended_crops
            else ["لا توجد توصيات لهذا الشهر"],
            "note": f"الموسم الحالي: {current_season}"
            if current_season
            else "خارج المواسم الرئيسية",
        },
    }


@app.get("/v1/regions/{region_id}/crops", tags=["Yemeni Heritage"])
def get_region_crops(region_id: str):
    """
    محاصيل منطقة معينة

    يرجع قائمة مفصلة بالمحاصيل التي تُزرع في منطقة معينة مع معلومات عن:
    - المحاصيل الرئيسية
    - مواسم الزراعة لكل محصول
    - المنتجات الشهيرة من المنطقة

    المناطق المتاحة: tihama, central_highlands, eastern_plateau, northern_highlands, southern_coast
    """
    if region_id not in YEMENI_AGRICULTURAL_REGIONS:
        available_regions = list(YEMENI_AGRICULTURAL_REGIONS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"المنطقة '{region_id}' غير موجودة. المناطق المتاحة: {', '.join(available_regions)}",
        )

    region_data = YEMENI_AGRICULTURAL_REGIONS[region_id]

    # تنظيم المحاصيل حسب الموسم
    crops_by_season = {}
    for season_name, season_info in region_data["planting_seasons"].items():
        crops_by_season[season_name] = {
            "name": season_name,
            "months": season_info["months"],
            "months_en": season_info["months_en"],
            "crops": season_info["crops"],
        }

    # إحصائيات
    total_crops = len(region_data["main_crops"])
    total_famous_products = len(region_data["famous_products"])

    return {
        "region_id": region_id,
        "region_name": region_data["name"],
        "region_name_en": region_data["name_en"],
        "all_crops": {
            "arabic": region_data["main_crops"],
            "english": region_data["main_crops_en"],
            "total": total_crops,
        },
        "crops_by_season": crops_by_season,
        "famous_products": {
            "arabic": region_data["famous_products"],
            "english": region_data["famous_products_en"],
            "total": total_famous_products,
        },
        "climate_suitability": {
            "climate_type": region_data["climate"]["type"],
            "avg_temp_summer": region_data["climate"]["avg_temp_summer"],
            "avg_temp_winter": region_data["climate"]["avg_temp_winter"],
            "rainfall_mm": region_data["climate"]["rainfall_mm"],
            "note": f"المنطقة مناسبة لـ {total_crops} نوع من المحاصيل",
        },
        "agricultural_heritage": {
            "traditional_irrigation": region_data["traditional_irrigation"],
            "soil_type": region_data["soil_type"],
            "water_sources": region_data["water_sources"],
        },
    }


@app.get("/v1/best-days", tags=["Calendar"])
def get_best_farming_days(
    activity: str = Query("زراعة", description="النشاط: زراعة، حصاد، ري، تقليم"),
    days: int = Query(30, ge=7, le=90, description="عدد الأيام للبحث"),
):
    """
    البحث عن أفضل الأيام لنشاط زراعي معين

    الأنشطة المدعومة: زراعة، حصاد، ري، تقليم، غرس، تطعيم
    """
    start = datetime.now(UTC)
    best_days = []

    for i in range(days):
        dt = start + timedelta(days=i)
        data = get_daily_astronomical_data(dt)

        # البحث عن التوصية المطلوبة
        for rec in data.recommendations:
            if rec.activity == activity and rec.suitability_score >= 7:
                best_days.append(
                    {
                        "date": dt.strftime("%Y-%m-%d"),
                        "hijri_date": f"{data.date_hijri.day} {data.date_hijri.month_name}",
                        "moon_phase": data.moon_phase.name,
                        "lunar_mansion": data.lunar_mansion.name,
                        "score": rec.suitability_score,
                        "reason": rec.reason,
                    }
                )
                break

    return {
        "activity": activity,
        "search_period_days": days,
        "best_days": best_days,
        "total_found": len(best_days),
    }


@app.get("/v1/integration/weather", tags=["Integration"])
async def get_integrated_data(
    location_id: str = Query("sanaa", description="معرف الموقع"),
    date_str: str | None = Query(None, description="التاريخ (YYYY-MM-DD)"),
):
    """
    دمج البيانات الفلكية مع بيانات الطقس

    يتصل بخدمة الطقس للحصول على بيانات متكاملة
    """
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.now(UTC)

    # البيانات الفلكية
    astro_data = get_daily_astronomical_data(dt)

    # محاولة جلب بيانات الطقس
    weather_data = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{WEATHER_SERVICE_URL}/v1/current/{location_id}",
                timeout=5.0,
            )
            if response.status_code == 200:
                weather_data = response.json()
    except httpx.TimeoutException:
        weather_data = {"error": "timeout", "note": "انتهت مهلة الاتصال بخدمة الطقس"}
    except httpx.ConnectError:
        weather_data = {"error": "connection_error", "note": "لا يمكن الاتصال بخدمة الطقس"}
    except Exception:
        weather_data = {"error": "unknown", "note": "خدمة الطقس غير متاحة حالياً"}

    # دمج التوصيات
    integrated_recommendations = []
    for rec in astro_data.recommendations:
        integrated_rec = rec.dict()

        # تعديل التوصية بناءً على الطقس إذا توفرت البيانات
        if weather_data and "temperature" in weather_data:
            temp = weather_data.get("temperature", 25)
            if rec.activity == "ري" and temp > 35:
                integrated_rec["weather_note"] = (
                    "⚠️ درجة الحرارة مرتفعة - يُنصح بالري في الصباح الباكر أو المساء"
                )
            elif rec.activity == "زراعة" and temp < 10:
                integrated_rec["weather_note"] = "⚠️ درجة الحرارة منخفضة - قد تؤثر على الإنبات"

        integrated_recommendations.append(integrated_rec)

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "location_id": location_id,
        "astronomical": {
            "hijri_date": astro_data.date_hijri.dict(),
            "moon_phase": astro_data.moon_phase.dict(),
            "lunar_mansion": astro_data.lunar_mansion.dict(),
            "zodiac": astro_data.zodiac.dict(),
            "season": astro_data.season.dict(),
            "overall_score": astro_data.overall_farming_score,
        },
        "weather": weather_data,
        "integrated_recommendations": integrated_recommendations,
        "summary_ar": f"اليوم في منزلة {astro_data.lunar_mansion.name}، والقمر {astro_data.moon_phase.name}. درجة ملاءمة الزراعة: {astro_data.overall_farming_score}/10",
    }


# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# نقاط نهاية المحاصيل التفصيلية
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/crop-details", tags=["Crops"])
def list_detailed_crops():
    """
    قائمة المحاصيل مع التفاصيل الكاملة

    يرجع معلومات موجزة عن جميع المحاصيل في التقويم التفصيلي
    """
    crops_summary = []
    for crop_id, crop_data in DETAILED_CROP_CALENDAR.items():
        crops_summary.append(
            {
                "crop_id": crop_id,
                "name": crop_data["name"],
                "name_en": crop_data["name_en"],
                "regions": crop_data["regions"],
                "altitude_range": crop_data["altitude_range"],
                "lifecycle_years": crop_data["lifecycle_years"],
                "market_price_yer_kg": crop_data["market_price_yer_kg"],
            }
        )

    return {
        "total_crops": len(crops_summary),
        "crops": crops_summary,
    }


@app.get("/v1/crop-details/{crop_id}", tags=["Crops"])
def get_crop_details(crop_id: str):
    """
    تفاصيل محصول كاملة

    يرجع جميع المعلومات عن محصول معين بما في ذلك:
    - الأصناف والمناطق
    - معلومات الزراعة التفصيلية
    - العناية والري والتسميد
    - الحصاد والمعالجة
    - الأمثال الشعبية
    """
    if crop_id not in DETAILED_CROP_CALENDAR:
        raise HTTPException(
            status_code=404, detail=f"المحصول '{crop_id}' غير موجود في التقويم التفصيلي"
        )

    crop_data = DETAILED_CROP_CALENDAR[crop_id]

    # حساب ملاءمة اليوم الحالي للزراعة
    today = get_daily_astronomical_data(datetime.now(UTC))
    current_month = datetime.now(UTC).month

    planting_suitability = {
        "score": 5,
        "suitable_now": False,
        "reason": [],
    }

    # Check if current month is in optimal planting months
    if current_month in crop_data["planting"]["gregorian_months"]:
        planting_suitability["score"] += 2
        planting_suitability["suitable_now"] = True
        planting_suitability["reason"].append("الشهر الحالي مناسب للزراعة")

    # Check if current lunar mansion is optimal
    if today.lunar_mansion.number in crop_data["planting"]["lunar_mansions"]:
        planting_suitability["score"] += 2
        planting_suitability["suitable_now"] = True
        planting_suitability["reason"].append(
            f"المنزلة الحالية ({today.lunar_mansion.name}) مناسبة"
        )

    # Check moon phase
    required_phase = crop_data["planting"]["moon_phase"]
    if (required_phase == "متزايد" and today.moon_phase.is_waxing) or (
        required_phase == "متناقص" and not today.moon_phase.is_waxing
    ):
        planting_suitability["score"] += 1
        planting_suitability["reason"].append(f"مرحلة القمر مناسبة ({today.moon_phase.name})")

    planting_suitability["score"] = min(10, planting_suitability["score"])

    if not planting_suitability["reason"]:
        planting_suitability["reason"].append("الوقت الحالي غير مثالي للزراعة")

    return {
        **crop_data,
        "crop_id": crop_id,
        "current_planting_suitability": planting_suitability,
        "current_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        "current_lunar_mansion": today.lunar_mansion.name,
        "current_moon_phase": today.moon_phase.name,
    }


@app.get("/v1/crop-details/{crop_id}/planting-guide", tags=["Crops"])
def get_planting_guide(crop_id: str):
    """
    دليل زراعة المحصول المفصل

    يرجع دليل خطوة بخطوة لزراعة المحصول المحدد
    """
    if crop_id not in DETAILED_CROP_CALENDAR:
        raise HTTPException(
            status_code=404, detail=f"المحصول '{crop_id}' غير موجود في التقويم التفصيلي"
        )

    crop_data = DETAILED_CROP_CALENDAR[crop_id]

    # Build comprehensive planting guide
    guide = {
        "crop_id": crop_id,
        "crop_name": crop_data["name"],
        "crop_name_en": crop_data["name_en"],
        "overview": {
            "best_regions": crop_data["regions"],
            "altitude_range": crop_data["altitude_range"],
            "lifecycle_years": crop_data["lifecycle_years"],
            "first_harvest_year": crop_data["first_harvest_year"],
            "peak_production_years": crop_data["peak_production_year"],
        },
        "timing": {
            "best_hijri_months": crop_data["planting"]["hijri_months"],
            "best_gregorian_months": crop_data["planting"]["gregorian_months"],
            "best_lunar_mansions": [
                LUNAR_MANSIONS[m]["name"] for m in crop_data["planting"]["lunar_mansions"]
            ],
            "required_moon_phase": crop_data["planting"]["moon_phase"],
        },
        "planting": {
            "method": crop_data["planting"]["method"],
            "spacing_meters": crop_data["planting"]["spacing_m"],
            "shade_requirement": crop_data["planting"]["shade_requirement"],
        },
        "care_schedule": {
            "irrigation": crop_data["care"]["irrigation"],
            "fertilization": crop_data["care"]["fertilization"],
            "pruning": crop_data["care"]["pruning"],
        },
        "pest_disease_management": {
            "common_pests": crop_data["care"]["pests"],
            "common_diseases": crop_data["care"]["diseases"],
        },
        "harvest": {
            "best_hijri_months": crop_data["harvest"]["hijri_months"],
            "best_gregorian_months": crop_data["harvest"]["gregorian_months"],
            "signs_of_ripeness": crop_data["harvest"]["signs_of_ripeness"],
            "method": crop_data["harvest"]["method"],
            "expected_yield": crop_data["harvest"]["yield_kg_per_tree"],
        },
        "post_harvest": {
            "drying_method": crop_data["processing"]["drying_method"],
            "drying_days": crop_data["processing"]["drying_days"],
            "target_moisture": crop_data["processing"]["moisture_target_percent"],
            "storage": crop_data["processing"]["storage"],
        },
        "traditional_wisdom": {
            "proverbs": crop_data["proverbs"],
        },
        "economics": {
            "market_price_yer_per_kg": crop_data["market_price_yer_kg"],
        },
    }

    return guide


@app.get("/v1/what-to-plant", tags=["Crops"])
def what_to_plant_now(
    region: str = Query(None, description="المنطقة (اختياري): حراز، صنعاء، تهامة، إلخ"),
    altitude_min: int = Query(None, description="الارتفاع الأدنى بالمتر"),
    altitude_max: int = Query(None, description="الارتفاع الأعلى بالمتر"),
):
    """
    ماذا أزرع الآن؟

    يوصي بالمحاصيل المناسبة للزراعة في الوقت الحالي بناءً على:
    - التاريخ الحالي (الشهر الميلادي والهجري)
    - المنزلة القمرية
    - مرحلة القمر
    - المنطقة (اختياري)
    - الارتفاع (اختياري)
    """
    today = get_daily_astronomical_data(datetime.now(UTC))
    current_month = datetime.now(UTC).month
    current_hijri_month = today.date_hijri.month_name

    recommendations = []

    for crop_id, crop_data in DETAILED_CROP_CALENDAR.items():
        score = 0
        reasons = []

        # Check if current month is suitable
        if current_month in crop_data["planting"]["gregorian_months"]:
            score += 3
            reasons.append(f"الشهر الحالي ({current_month}) مناسب للزراعة")

        # Check if current lunar mansion is suitable
        if today.lunar_mansion.number in crop_data["planting"]["lunar_mansions"]:
            score += 3
            reasons.append(f"المنزلة القمرية ({today.lunar_mansion.name}) مناسبة")

        # Check moon phase
        required_phase = crop_data["planting"]["moon_phase"]
        if (required_phase == "متزايد" and today.moon_phase.is_waxing) or (
            required_phase == "متناقص" and not today.moon_phase.is_waxing
        ):
            score += 2
            reasons.append(f"مرحلة القمر ({today.moon_phase.name}) مناسبة")

        # Filter by region if specified
        if region:
            if region in crop_data["regions"] or any(
                region.lower() in r.lower() for r in crop_data["regions"]
            ):
                score += 2
                reasons.append(f"مناسب لمنطقة {region}")
            else:
                # Significantly reduce score if region doesn't match
                score -= 5

        # Filter by altitude if specified
        if altitude_min is not None or altitude_max is not None:
            # Parse altitude range from crop data (format: "1400-2400م")
            alt_range = crop_data["altitude_range"].replace("م", "").split("-")
            try:
                crop_alt_min = int(alt_range[0])
                crop_alt_max = int(alt_range[1])

                user_alt_min = altitude_min if altitude_min is not None else 0
                user_alt_max = altitude_max if altitude_max is not None else 10000

                # Check if there's overlap
                if crop_alt_min <= user_alt_max and crop_alt_max >= user_alt_min:
                    score += 2
                    reasons.append("مناسب للارتفاع المطلوب")
                else:
                    score -= 5
            except (ValueError, IndexError):
                pass

        # Only include if score is positive
        if score > 0:
            recommendations.append(
                {
                    "crop_id": crop_id,
                    "name": crop_data["name"],
                    "name_en": crop_data["name_en"],
                    "suitability_score": min(10, score),
                    "reasons": reasons,
                    "planting_method": crop_data["planting"]["method"],
                    "spacing_m": crop_data["planting"]["spacing_m"],
                    "regions": crop_data["regions"],
                    "altitude_range": crop_data["altitude_range"],
                    "first_harvest_in_years": crop_data["first_harvest_year"],
                    "expected_yield": crop_data["harvest"]["yield_kg_per_tree"],
                    "market_price_yer_kg": crop_data["market_price_yer_kg"],
                }
            )

    # Sort by suitability score
    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)

    return {
        "query_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        "hijri_date": f"{today.date_hijri.day} {current_hijri_month} {today.date_hijri.year}هـ",
        "lunar_mansion": today.lunar_mansion.name,
        "moon_phase": today.moon_phase.name,
        "moon_is_waxing": today.moon_phase.is_waxing,
        "filters": {
            "region": region,
            "altitude_min": altitude_min,
            "altitude_max": altitude_max,
        },
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "advice": (
            f"اليوم نحن في منزلة {today.lunar_mansion.name} والقمر {today.moon_phase.name}. "
            f"{'القمر متزايد - مناسب لزراعة المحاصيل الورقية والثمرية' if today.moon_phase.is_waxing else 'القمر متناقص - مناسب لزراعة الجذور والدرنات'}"
        ),
    }


# الأمثال الزراعية والنجوم
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/proverbs", tags=["Yemeni Wisdom"])
def get_all_proverbs():
    """
    الحصول على جميع الأمثال الزراعية اليمنية

    تشمل:
    - الأمثال العامة
    - أمثال حسب المحصول
    - أمثال حسب الموسم
    """
    return {
        "general": YEMENI_FARMING_PROVERBS["general"],
        "by_crop": YEMENI_FARMING_PROVERBS["by_crop"],
        "by_season": YEMENI_FARMING_PROVERBS["by_season"],
        "total_proverbs": len(YEMENI_FARMING_PROVERBS["general"])
        + sum(len(v) for v in YEMENI_FARMING_PROVERBS["by_crop"].values())
        + sum(len(v) for v in YEMENI_FARMING_PROVERBS["by_season"].values()),
    }


@app.get("/v1/proverbs/today", tags=["Yemeni Wisdom"])
def get_proverb_of_the_day():
    """
    الحصول على مثل اليوم مع تفسيره

    يختار مثلاً مناسباً بناءً على:
    - المنزلة القمرية الحالية
    - الموسم الحالي
    - مرحلة القمر
    """
    now = datetime.now(UTC)
    lunar_mansion = calculate_lunar_mansion(now)
    moon_phase = calculate_moon_phase(now)
    season = get_current_season(now.month)

    # البحث عن مثل مناسب للمنزلة الحالية
    matching_proverb = None
    for proverb in YEMENI_FARMING_PROVERBS["general"]:
        if proverb.get("mansion") == lunar_mansion.name:
            matching_proverb = proverb
            break

    # إذا لم نجد، نختار واحداً عاماً بناءً على اليوم
    if not matching_proverb:
        day_of_year = now.timetuple().tm_yday
        proverb_index = day_of_year % len(YEMENI_FARMING_PROVERBS["general"])
        matching_proverb = YEMENI_FARMING_PROVERBS["general"][proverb_index]

    # إضافة أمثال الموسم
    season_proverbs = YEMENI_FARMING_PROVERBS["by_season"].get(season.name, [])

    return {
        "date": now.strftime("%Y-%m-%d"),
        "proverb_of_the_day": matching_proverb,
        "current_mansion": lunar_mansion.name,
        "current_moon_phase": moon_phase.name,
        "current_season": season.name,
        "season_proverbs": season_proverbs,
        "context": f"اليوم نحن في منزلة {lunar_mansion.name} والقمر {moon_phase.name}",
    }


@app.get("/v1/proverbs/crop/{crop_name}", tags=["Yemeni Wisdom"])
def get_crop_proverbs(crop_name: str):
    """
    الحصول على الأمثال الخاصة بمحصول معين

    المحاصيل المدعومة: قمح، بن، ذرة، بصل
    """
    proverbs = YEMENI_FARMING_PROVERBS["by_crop"].get(crop_name, [])

    if not proverbs:
        available_crops = list(YEMENI_FARMING_PROVERBS["by_crop"].keys())
        return {
            "crop": crop_name,
            "proverbs": [],
            "note": f"لا توجد أمثال مسجلة لهذا المحصول. المحاصيل المتاحة: {', '.join(available_crops)}",
        }

    return {"crop": crop_name, "proverbs": proverbs, "count": len(proverbs)}


@app.get("/v1/proverbs/mansion/{mansion_name}", tags=["Yemeni Wisdom"])
def get_mansion_proverbs(mansion_name: str):
    """
    الحصول على الأمثال المرتبطة بمنزلة قمرية معينة
    """
    matching_proverbs = [
        p for p in YEMENI_FARMING_PROVERBS["general"] if p.get("mansion") == mansion_name
    ]

    # البحث في المنازل للحصول على معلومات إضافية
    mansion_info = None
    for num, data in LUNAR_MANSIONS.items():
        if data["name"] == mansion_name:
            mansion_info = {
                "number": num,
                "name": data["name"],
                "farming_score": data["farming_score"],
                "description": data["description"],
            }
            break

    return {
        "mansion": mansion_name,
        "mansion_info": mansion_info,
        "proverbs": matching_proverbs,
        "count": len(matching_proverbs),
    }


@app.get("/v1/stars", tags=["Yemeni Wisdom"])
def get_important_stars():
    """
    الحصول على النجوم المهمة في التقويم الزراعي اليمني

    تشمل:
    - سهيل (Canopus)
    - الثريا (Pleiades)
    - السماك (Spica)
    """
    return {
        "stars": IMPORTANT_STARS,
        "total": len(IMPORTANT_STARS),
        "note": "هذه النجوم يستخدمها المزارعون اليمنيون منذ آلاف السنين لتحديد مواعيد الزراعة",
    }


@app.get("/v1/stars/{star_name}", tags=["Yemeni Wisdom"])
def get_star_info(star_name: str):
    """
    الحصول على معلومات نجم معين
    """
    star = IMPORTANT_STARS.get(star_name)

    if not star:
        available_stars = list(IMPORTANT_STARS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"النجم '{star_name}' غير موجود. النجوم المتاحة: {', '.join(available_stars)}",
        )

    # هل النجم طالع حالياً؟
    current_month = datetime.now(UTC).month
    is_rising = current_month == star["rising_month"]

    return {
        "star": star,
        "is_currently_rising": is_rising,
        "rising_month_name": HIJRI_MONTHS.get(star["rising_month"], {}).get("name", ""),
        "advice": (
            star["farming_impact"]
            if is_rising
            else f"سيطلع هذا النجم في شهر {star['rising_month']}"
        ),
    }


@app.get("/v1/landmarks", tags=["Yemeni Heritage"])
def get_landmarks():
    """
    قائمة المعالم الزراعية اليمنية التاريخية

    تشمل:
    - المدرجات الجبلية
    - السدود التاريخية
    - أنظمة الري التقليدية
    - مخازن الحبوب والمحاصيل

    هذه المعالم تمثل التراث الزراعي اليمني العريق
    """
    # حساب إحصائيات
    stats = {
        "total_terraces": len(YEMENI_AGRICULTURAL_LANDMARKS["terraces"]),
        "total_dams": len(YEMENI_AGRICULTURAL_LANDMARKS["dams"]),
        "total_water_systems": len(YEMENI_AGRICULTURAL_LANDMARKS["water_systems"]),
        "total_storage_systems": len(YEMENI_AGRICULTURAL_LANDMARKS["storage"]),
        "total_landmarks": (
            len(YEMENI_AGRICULTURAL_LANDMARKS["terraces"])
            + len(YEMENI_AGRICULTURAL_LANDMARKS["dams"])
            + len(YEMENI_AGRICULTURAL_LANDMARKS["water_systems"])
            + len(YEMENI_AGRICULTURAL_LANDMARKS["storage"])
        ),
    }

    return {
        "landmarks": YEMENI_AGRICULTURAL_LANDMARKS,
        "statistics": stats,
        "categories": ["terraces", "dams", "water_systems", "storage"],
        "description": "التراث الزراعي اليمني - تقنيات عمرها آلاف السنين ما زالت مستخدمة حتى اليوم",
    }


@app.get("/v1/landmarks/{category}", tags=["Yemeni Heritage"])
def get_landmarks_by_category(category: str):
    """
    المعالم حسب الفئة

    الفئات المتاحة:
    - terraces: المدرجات الجبلية
    - dams: السدود التاريخية
    - water_systems: أنظمة الري التقليدية
    - storage: أنظمة التخزين
    """
    valid_categories = ["terraces", "dams", "water_systems", "storage"]

    if category not in valid_categories:
        raise HTTPException(
            status_code=404,
            detail=f"الفئة '{category}' غير موجودة. الفئات المتاحة: {', '.join(valid_categories)}",
        )

    category_data = YEMENI_AGRICULTURAL_LANDMARKS[category]

    # أسماء الفئات بالعربية
    category_names = {
        "terraces": "المدرجات الجبلية",
        "dams": "السدود التاريخية",
        "water_systems": "أنظمة الري التقليدية",
        "storage": "أنظمة التخزين",
    }

    category_descriptions = {
        "terraces": "المدرجات الجبلية اليمنية تمثل إحدى أعظم الإنجازات الهندسية الزراعية في التاريخ",
        "dams": "السدود اليمنية القديمة شاهدة على عظمة الحضارات اليمنية القديمة",
        "water_systems": "أنظمة الري التقليدية تعكس الحكمة اليمنية في إدارة الموارد المائية",
        "storage": "أنظمة التخزين التقليدية تحافظ على المحاصيل بطرق طبيعية وفعالة",
    }

    return {
        "category": category,
        "category_name_ar": category_names[category],
        "description": category_descriptions[category],
        "landmarks": category_data,
        "count": len(category_data),
        "items": list(category_data.keys()),
    }


@app.get("/v1/landmarks/{category}/{landmark_name}", tags=["Yemeni Heritage"])
def get_specific_landmark(category: str, landmark_name: str):
    """
    الحصول على معلومات معلم محدد

    مثال: /v1/landmarks/dams/سد مأرب
    """
    valid_categories = ["terraces", "dams", "water_systems", "storage"]

    if category not in valid_categories:
        raise HTTPException(status_code=404, detail=f"الفئة '{category}' غير موجودة")

    category_data = YEMENI_AGRICULTURAL_LANDMARKS[category]

    if landmark_name not in category_data:
        available_landmarks = list(category_data.keys())
        raise HTTPException(
            status_code=404,
            detail=f"المعلم '{landmark_name}' غير موجود في هذه الفئة. المعالم المتاحة: {', '.join(available_landmarks)}",
        )

    landmark = category_data[landmark_name]

    # إضافة معلومات إضافية
    return {
        "category": category,
        "landmark": landmark,
        "related_categories": valid_categories,
        "preservation_note": "هذه المعالم تحتاج للحماية والصيانة للحفاظ على التراث الزراعي اليمني",
    }


@app.get("/v1/wisdom/today", tags=["Yemeni Wisdom"])
def get_daily_wisdom():
    """
    الحكمة الزراعية اليومية الشاملة

    تجمع بين:
    - مثل اليوم
    - نصيحة المنزلة
    - توقعات النجوم
    - توصيات الموسم
    """
    now = datetime.now(UTC)
    astro_data = get_daily_astronomical_data(now)

    # مثل اليوم
    day_of_year = now.timetuple().tm_yday
    proverb_index = day_of_year % len(YEMENI_FARMING_PROVERBS["general"])
    proverb = YEMENI_FARMING_PROVERBS["general"][proverb_index]

    # نجم الشهر
    current_star = None
    for _star_name, star_data in IMPORTANT_STARS.items():
        if star_data["rising_month"] == now.month:
            current_star = star_data
            break

    # نصائح المنزلة
    mansion_tips = []
    if astro_data.lunar_mansion.farming_score >= 7:
        mansion_tips.append(
            f"🌟 اليوم مناسب للزراعة - درجة الملاءمة: {astro_data.lunar_mansion.farming_score}/10"
        )
        mansion_tips.append(f"المحاصيل المقترحة: {', '.join(astro_data.lunar_mansion.crops[:3])}")
    else:
        mansion_tips.append(
            f"⚠️ اليوم غير مثالي للزراعة - درجة الملاءمة: {astro_data.lunar_mansion.farming_score}/10"
        )
        if astro_data.lunar_mansion.avoid:
            mansion_tips.append(f"تجنب: {', '.join(astro_data.lunar_mansion.avoid)}")

    # نصائح القمر
    moon_tips = []
    if astro_data.moon_phase.is_waxing:
        moon_tips.append("🌙 القمر متزايد - مناسب لزراعة المحاصيل الورقية والثمرية")
    else:
        moon_tips.append("🌙 القمر متناقص - مناسب لزراعة الجذور والتقليم")

    return {
        "date": now.strftime("%Y-%m-%d"),
        "hijri_date": astro_data.date_hijri.formatted,
        "proverb_of_the_day": {
            "text": proverb["proverb"],
            "meaning": proverb["meaning"],
            "application": proverb["application"],
        },
        "current_mansion": {
            "name": astro_data.lunar_mansion.name,
            "description": astro_data.lunar_mansion.description,
            "tips": mansion_tips,
        },
        "moon_phase": {
            "name": astro_data.moon_phase.name,
            "icon": astro_data.moon_phase.icon,
            "illumination": f"{astro_data.moon_phase.illumination:.0f}%",
            "tips": moon_tips,
        },
        "current_star": current_star,
        "season": {
            "name": astro_data.season.name,
            "crops": astro_data.season.main_crops,
            "activities": astro_data.season.activities,
        },
        "overall_score": astro_data.overall_farming_score,
        "summary": f"""
📅 اليوم {astro_data.date_hijri.weekday} {astro_data.date_hijri.formatted}
{astro_data.moon_phase.icon} القمر: {astro_data.moon_phase.name} ({astro_data.moon_phase.illumination:.0f}%)
⭐ المنزلة: {astro_data.lunar_mansion.name} ({astro_data.lunar_mansion.farming})
{astro_data.zodiac.zodiac_icon} البرج: {astro_data.zodiac.name}
🌾 درجة الزراعة: {astro_data.overall_farming_score}/10

📜 مثل اليوم:
"{proverb["proverb"]}"
- {proverb["meaning"]}
        """.strip(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# التقنيات الزراعية التقليدية (API Endpoints)
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/techniques", tags=["Yemeni Heritage"])
def get_all_techniques():
    """
    الحصول على جميع التقنيات الزراعية اليمنية التقليدية

    يرجع:
    - جميع الفئات والتقنيات
    - عدد التقنيات في كل فئة
    - قائمة الفئات المتاحة
    """
    categories_summary = {}
    total_techniques = 0

    for category_key, category_data in TRADITIONAL_TECHNIQUES.items():
        technique_count = len(category_data)
        total_techniques += technique_count
        categories_summary[category_key] = {
            "count": technique_count,
            "techniques": list(category_data.keys()),
        }

    return {
        "categories": categories_summary,
        "total_categories": len(TRADITIONAL_TECHNIQUES),
        "total_techniques": total_techniques,
        "available_categories": list(TRADITIONAL_TECHNIQUES.keys()),
        "description": "مكتبة شاملة للتقنيات الزراعية اليمنية التقليدية - من الحراثة إلى الحصاد",
    }


@app.get("/v1/techniques/{category}", tags=["Yemeni Heritage"])
def get_techniques_by_category(category: str):
    """
    الحصول على جميع التقنيات في فئة معينة

    الفئات المتاحة:
    - plowing: تقنيات الحراثة
    - irrigation: تقنيات الري
    - fertilization: تقنيات التسميد
    - harvesting: تقنيات الحصاد
    - processing: تقنيات المعالجة والتخزين
    - pest_control: تقنيات مكافحة الآفات
    """
    if category not in TRADITIONAL_TECHNIQUES:
        available_categories = list(TRADITIONAL_TECHNIQUES.keys())
        raise HTTPException(
            status_code=404,
            detail=f"الفئة '{category}' غير موجودة. الفئات المتاحة: {', '.join(available_categories)}",
        )

    category_data = TRADITIONAL_TECHNIQUES[category]

    # تصنيف الفئة بالعربية
    category_names = {
        "plowing": "الحراثة",
        "irrigation": "الري",
        "fertilization": "التسميد",
        "harvesting": "الحصاد",
        "processing": "المعالجة والتخزين",
        "pest_control": "مكافحة الآفات",
    }

    return {
        "category": category,
        "category_name_ar": category_names.get(category, category),
        "techniques": category_data,
        "count": len(category_data),
        "technique_ids": list(category_data.keys()),
    }


@app.get("/v1/techniques/{category}/{technique_id}", tags=["Yemeni Heritage"])
def get_technique_details(category: str, technique_id: str):
    """
    الحصول على تفاصيل تقنية زراعية محددة

    يرجع معلومات شاملة عن التقنية:
    - الوصف والاسم بالعربية والإنجليزية
    - الأدوات المستخدمة
    - أفضل الأوقات للتطبيق
    - نصائح عملية
    - الأقوال الشعبية المرتبطة
    """
    if category not in TRADITIONAL_TECHNIQUES:
        available_categories = list(TRADITIONAL_TECHNIQUES.keys())
        raise HTTPException(
            status_code=404,
            detail=f"الفئة '{category}' غير موجودة. الفئات المتاحة: {', '.join(available_categories)}",
        )

    category_data = TRADITIONAL_TECHNIQUES[category]

    if technique_id not in category_data:
        available_techniques = list(category_data.keys())
        raise HTTPException(
            status_code=404,
            detail=f"التقنية '{technique_id}' غير موجودة في فئة '{category}'. التقنيات المتاحة: {', '.join(available_techniques)}",
        )

    technique = category_data[technique_id]

    # إضافة معلومات سياقية
    current_data = get_daily_astronomical_data(datetime.now(UTC))

    # تقييم مدى ملاءمة اليوم الحالي لهذه التقنية
    suitability_score = 5
    suitability_notes = []

    # فحص مرحلة القمر إذا كانت التقنية تتطلبها
    if "lunar_phase" in technique:
        required_phase = technique["lunar_phase"]
        if required_phase == "القمر المتزايد" and current_data.moon_phase.is_waxing:
            suitability_score += 3
            suitability_notes.append("القمر متزايد - مناسب لهذه التقنية")
        elif required_phase == "القمر المتناقص" and not current_data.moon_phase.is_waxing:
            suitability_score += 3
            suitability_notes.append("القمر متناقص - مناسب لهذه التقنية")
        elif required_phase != "أي مرحلة":
            suitability_score -= 1
            suitability_notes.append(f"الأفضل تطبيقها في: {required_phase}")

    # فحص المنزلة القمرية
    mansion_appropriate = False
    if (
        category == "plowing"
        and current_data.lunar_mansion.farming_score >= 6
        or category == "irrigation"
        and current_data.lunar_mansion.element == "ماء"
        or category == "fertilization"
        and current_data.moon_phase.is_waxing
    ):
        mansion_appropriate = True

    if mansion_appropriate:
        suitability_score += 2
        suitability_notes.append(f"المنزلة الحالية ({current_data.lunar_mansion.name}) مناسبة")

    suitability_score = max(1, min(10, suitability_score))

    return {
        "technique": technique,
        "category": category,
        "technique_id": technique_id,
        "current_day_suitability": {
            "score": suitability_score,
            "date": datetime.now(UTC).strftime("%Y-%m-%d"),
            "lunar_mansion": current_data.lunar_mansion.name,
            "moon_phase": current_data.moon_phase.name,
            "notes": suitability_notes,
            "recommendation": (
                "ممتاز - طبق هذه التقنية اليوم"
                if suitability_score >= 8
                else (
                    "جيد - يمكن التطبيق"
                    if suitability_score >= 6
                    else "متوسط - انتظر وقتاً أفضل"
                    if suitability_score >= 4
                    else "غير مناسب اليوم"
                )
            ),
        },
        "heritage_note": "هذه التقنيات ورثها المزارعون اليمنيون جيلاً بعد جيل لآلاف السنين",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# نقطة الدخول
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8111))
    uvicorn.run(app, host="0.0.0.0", port=port)

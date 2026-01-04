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
Version: 15.5.0
"""

import math
import os
from datetime import datetime, timedelta

import httpx
from fastapi import FastAPI, HTTPException, Query
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
    version="15.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - secure origins from environment
CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:8080",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


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
        ],
        "ذرة": [
            {
                "proverb": "الذرة تُزرع مع السيل، وتُحصد قبل الويل",
                "meaning": "زراعة الذرة مع بداية الأمطار وحصادها قبل السيول الكبيرة",
                "application": "توقيت الزراعة والحصاد",
            },
        ],
        "بصل": [
            {
                "proverb": "البصل والثوم في القمر المتناقص",
                "meaning": "المحاصيل الجذرية تُزرع في القمر المتناقص",
                "application": "مرحلة القمر المناسبة",
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
    overall_farming_score: int = Field(
        ..., ge=1, le=10, description="درجة الزراعة الإجمالية"
    )
    recommendations: list[FarmingRecommendation] = Field(
        ..., description="التوصيات الزراعية"
    )


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
            month == zd[0] + 1
            and day < zodiac_dates[(zodiac_dates.index(zd) + 1) % 12][1]
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
    for season_key, season_data in YEMENI_SEASONS.items():
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
        else (
            "جيدة"
            if planting_score >= 6
            else "متوسطة" if planting_score >= 4 else "ضعيفة"
        )
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
                "ممتازة"
                if irrigation_score >= 8
                else "جيدة" if irrigation_score >= 6 else "متوسطة"
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
                "ممتازة"
                if harvest_score >= 8
                else "جيدة" if harvest_score >= 6 else "متوسطة"
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
                "ممتازة"
                if pruning_score >= 8
                else "جيدة" if pruning_score >= 6 else "متوسطة"
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

    recommendations = calculate_farming_recommendations(
        moon_phase, lunar_mansion, zodiac
    )
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
        "version": "15.5.0",
        "timestamp": datetime.utcnow().isoformat(),
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
    return get_daily_astronomical_data(datetime.utcnow())


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
        raise HTTPException(
            status_code=400, detail="صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD"
        )


@app.get("/v1/week", response_model=WeeklyForecast, tags=["Calendar"])
def get_weekly_forecast(
    start_date: str | None = Query(None, description="تاريخ البداية (YYYY-MM-DD)")
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
        start = datetime.utcnow()

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
        harvest_rec = next(
            (r for r in data.recommendations if r.activity == "حصاد"), None
        )
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
def get_moon_phase(
    date_str: str | None = Query(None, description="التاريخ (YYYY-MM-DD)")
):
    """الحصول على مرحلة القمر"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.utcnow()

    return calculate_moon_phase(dt)


@app.get("/v1/lunar-mansion", response_model=LunarMansion, tags=["Astronomy"])
def get_lunar_mansion(
    date_str: str | None = Query(None, description="التاريخ (YYYY-MM-DD)")
):
    """الحصول على المنزلة القمرية الحالية"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.utcnow()

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
def get_hijri_date(
    date_str: str | None = Query(None, description="التاريخ الميلادي (YYYY-MM-DD)")
):
    """تحويل تاريخ ميلادي إلى هجري"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.utcnow()

    return gregorian_to_hijri(dt.year, dt.month, dt.day)


@app.get("/v1/hijri-months", tags=["Reference"])
def list_hijri_months():
    """قائمة الأشهر الهجرية"""
    return {"months": HIJRI_MONTHS}


@app.get("/v1/zodiac", response_model=ZodiacInfo, tags=["Astronomy"])
def get_zodiac(
    date_str: str | None = Query(None, description="التاريخ (YYYY-MM-DD)")
):
    """الحصول على البرج الشمسي"""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="صيغة التاريخ غير صحيحة")
    else:
        dt = datetime.utcnow()

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
    return get_current_season(datetime.utcnow().month)


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
    today = get_daily_astronomical_data(datetime.utcnow())
    current_suitability = 5

    if today.lunar_mansion.number in crop_data["best_planting_mansions"]:
        current_suitability += 2
    if today.moon_phase.phase_key in crop_data["best_moon_phases"]:
        current_suitability += 2
    if datetime.utcnow().month in crop_data["optimal_months"]:
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


@app.get("/v1/best-days", tags=["Calendar"])
def get_best_farming_days(
    activity: str = Query("زراعة", description="النشاط: زراعة، حصاد، ري، تقليم"),
    days: int = Query(30, ge=7, le=90, description="عدد الأيام للبحث"),
):
    """
    البحث عن أفضل الأيام لنشاط زراعي معين

    الأنشطة المدعومة: زراعة، حصاد، ري، تقليم، غرس، تطعيم
    """
    start = datetime.utcnow()
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
        dt = datetime.utcnow()

    # البيانات الفلكية
    astro_data = get_daily_astronomical_data(dt)

    # محاولة جلب بيانات الطقس
    weather_data = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://sahool-weather-advanced:8092/v1/current/{location_id}",
                timeout=5.0,
            )
            if response.status_code == 200:
                weather_data = response.json()
    except Exception:
        weather_data = {"note": "خدمة الطقس غير متاحة حالياً"}

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
                integrated_rec["weather_note"] = (
                    "⚠️ درجة الحرارة منخفضة - قد تؤثر على الإنبات"
                )

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
    now = datetime.utcnow()
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
        p
        for p in YEMENI_FARMING_PROVERBS["general"]
        if p.get("mansion") == mansion_name
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
    current_month = datetime.utcnow().month
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
    now = datetime.utcnow()
    astro_data = get_daily_astronomical_data(now)

    # مثل اليوم
    day_of_year = now.timetuple().tm_yday
    proverb_index = day_of_year % len(YEMENI_FARMING_PROVERBS["general"])
    proverb = YEMENI_FARMING_PROVERBS["general"][proverb_index]

    # نجم الشهر
    current_star = None
    for star_name, star_data in IMPORTANT_STARS.items():
        if star_data["rising_month"] == now.month:
            current_star = star_data
            break

    # نصائح المنزلة
    mansion_tips = []
    if astro_data.lunar_mansion.farming_score >= 7:
        mansion_tips.append(
            f"🌟 اليوم مناسب للزراعة - درجة الملاءمة: {astro_data.lunar_mansion.farming_score}/10"
        )
        mansion_tips.append(
            f"المحاصيل المقترحة: {', '.join(astro_data.lunar_mansion.crops[:3])}"
        )
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
"{proverb['proverb']}"
- {proverb['meaning']}
        """.strip(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# نقطة الدخول
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8111)

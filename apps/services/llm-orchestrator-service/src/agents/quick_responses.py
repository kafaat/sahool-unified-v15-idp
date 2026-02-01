# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Quick Responses for common queries.

Pre-defined responses for frequently asked questions.
No LLM needed - saves API costs and reduces latency.

الردود السريعة للاستفسارات الشائعة.
ردود محددة مسبقاً للأسئلة المتكررة.
لا حاجة لنماذج لغوية - توفر التكاليف وتقلل زمن الاستجابة.
"""

from dataclasses import dataclass


@dataclass
class QuickResponse:
    """
    A pre-defined quick response.
    رد سريع محدد مسبقاً.
    """

    response_en: str
    response_ar: str
    category: str = "general"
    confidence: float = 1.0


# Quick responses database
# Keys are normalized patterns (lowercase, stripped)
QUICK_RESPONSES: dict[str, QuickResponse] = {
    # Platform Information
    "what is sahool": QuickResponse(
        response_en=(
            "SAHOOL is the National Agricultural Intelligence Platform - an offline-first "
            "agricultural operating system designed for low-connectivity environments. "
            "It provides real-time advisory, irrigation management, crop health monitoring (NDVI), "
            "and field operations management for smallholder farmers in the Middle East."
        ),
        response_ar=(
            "سهول هو المنصة الوطنية للذكاء الزراعي - نظام تشغيل زراعي يعمل بدون اتصال "
            "مصمم للبيئات ذات الاتصال المحدود. "
            "يوفر استشارات فورية، وإدارة الري، ومراقبة صحة المحاصيل (NDVI)، "
            "وإدارة العمليات الميدانية للمزارعين أصحاب الحيازات الصغيرة في الشرق الأوسط."
        ),
        category="platform",
    ),
    "ما هو سهول": QuickResponse(
        response_en=(
            "SAHOOL is the National Agricultural Intelligence Platform - an offline-first "
            "agricultural operating system designed for low-connectivity environments."
        ),
        response_ar=(
            "سهول هو المنصة الوطنية للذكاء الزراعي - نظام تشغيل زراعي يعمل بدون اتصال "
            "مصمم للبيئات ذات الاتصال المحدود. "
            "يوفر استشارات فورية، وإدارة الري، ومراقبة صحة المحاصيل (NDVI)، "
            "وإدارة العمليات الميدانية للمزارعين أصحاب الحيازات الصغيرة في الشرق الأوسط."
        ),
        category="platform",
    ),
    # Greetings
    "hello": QuickResponse(
        response_en="Hello! How can I help you with your farm today?",
        response_ar="أهلاً! كيف يمكنني مساعدتك في مزرعتك اليوم؟",
        category="greeting",
    ),
    "hi": QuickResponse(
        response_en="Hi! I'm here to help with agricultural advice. What do you need?",
        response_ar="مرحباً! أنا هنا لمساعدتك بالنصائح الزراعية. ماذا تحتاج؟",
        category="greeting",
    ),
    "مرحبا": QuickResponse(
        response_en="Hello! How can I help you with your farm today?",
        response_ar="مرحباً! كيف يمكنني مساعدتك في مزرعتك اليوم؟",
        category="greeting",
    ),
    "أهلا": QuickResponse(
        response_en="Hello! How can I help you with your farm today?",
        response_ar="أهلاً وسهلاً! كيف يمكنني خدمتك اليوم؟",
        category="greeting",
    ),
    "السلام عليكم": QuickResponse(
        response_en="Peace be upon you! How can I help you with your farm?",
        response_ar="وعليكم السلام ورحمة الله وبركاته! كيف يمكنني مساعدتك في شؤون مزرعتك؟",
        category="greeting",
    ),
    # Help
    "help": QuickResponse(
        response_en=(
            "I can help you with:\n"
            "- Crop disease diagnosis (send an image)\n"
            "- Pest identification\n"
            "- Irrigation scheduling\n"
            "- Fertilizer recommendations\n"
            "- Weather forecasts\n"
            "- Yield predictions\n"
            "- Field analysis\n\n"
            "What would you like to know?"
        ),
        response_ar=(
            "يمكنني مساعدتك في:\n"
            "- تشخيص أمراض المحاصيل (أرسل صورة)\n"
            "- تحديد الآفات\n"
            "- جدولة الري\n"
            "- توصيات الأسمدة\n"
            "- توقعات الطقس\n"
            "- تنبؤات المحصول\n"
            "- تحليل الحقل\n\n"
            "ماذا تريد أن تعرف؟"
        ),
        category="help",
    ),
    "مساعدة": QuickResponse(
        response_en=(
            "I can help you with: crop disease diagnosis, pest identification, "
            "irrigation scheduling, fertilizer recommendations, weather forecasts, "
            "yield predictions, and field analysis."
        ),
        response_ar=(
            "يمكنني مساعدتك في:\n"
            "- تشخيص أمراض المحاصيل (أرسل صورة)\n"
            "- تحديد الآفات\n"
            "- جدولة الري\n"
            "- توصيات الأسمدة\n"
            "- توقعات الطقس\n"
            "- تنبؤات المحصول\n"
            "- تحليل الحقل\n\n"
            "ماذا تريد أن تعرف؟"
        ),
        category="help",
    ),
    # Common NDVI Questions
    "what is ndvi": QuickResponse(
        response_en=(
            "NDVI (Normalized Difference Vegetation Index) is a measure of plant health "
            "derived from satellite imagery. Values range from -1 to 1:\n"
            "- 0.6 to 0.9: Dense, healthy vegetation\n"
            "- 0.3 to 0.6: Moderate vegetation\n"
            "- 0.2 to 0.3: Sparse vegetation\n"
            "- Below 0.2: Bare soil, water, or stressed crops"
        ),
        response_ar=(
            "NDVI (مؤشر الاختلاف النباتي الطبيعي) هو مقياس لصحة النبات "
            "مشتق من صور الأقمار الصناعية. تتراوح القيم من -1 إلى 1:\n"
            "- 0.6 إلى 0.9: غطاء نباتي كثيف وصحي\n"
            "- 0.3 إلى 0.6: غطاء نباتي متوسط\n"
            "- 0.2 إلى 0.3: غطاء نباتي متفرق\n"
            "- أقل من 0.2: تربة عارية أو ماء أو محاصيل متضررة"
        ),
        category="education",
    ),
    "ما هو ndvi": QuickResponse(
        response_en=(
            "NDVI measures plant health from satellite imagery. "
            "Higher values (0.6-0.9) indicate healthy crops."
        ),
        response_ar=(
            "NDVI (مؤشر الاختلاف النباتي الطبيعي) هو مقياس لصحة النبات "
            "مشتق من صور الأقمار الصناعية. تتراوح القيم من -1 إلى 1:\n"
            "- 0.6 إلى 0.9: غطاء نباتي كثيف وصحي\n"
            "- 0.3 إلى 0.6: غطاء نباتي متوسط\n"
            "- 0.2 إلى 0.3: غطاء نباتي متفرق\n"
            "- أقل من 0.2: تربة عارية أو ماء أو محاصيل متضررة"
        ),
        category="education",
    ),
    # Common Crop Questions
    "when to plant wheat": QuickResponse(
        response_en=(
            "Wheat planting times depend on your region:\n"
            "- Winter wheat: October to November (Middle East)\n"
            "- Spring wheat: March to April\n\n"
            "Optimal soil temperature: 12-25°C\n"
            "For personalized advice, provide your field location."
        ),
        response_ar=(
            "أوقات زراعة القمح تعتمد على منطقتك:\n"
            "- القمح الشتوي: أكتوبر إلى نوفمبر (الشرق الأوسط)\n"
            "- القمح الربيعي: مارس إلى أبريل\n\n"
            "درجة حرارة التربة المثلى: 12-25 درجة مئوية\n"
            "للحصول على نصيحة مخصصة، أرسل موقع حقلك."
        ),
        category="planting",
    ),
    "متى أزرع القمح": QuickResponse(
        response_en="Wheat planting: October-November for winter wheat, March-April for spring wheat.",
        response_ar=(
            "أوقات زراعة القمح تعتمد على منطقتك:\n"
            "- القمح الشتوي: أكتوبر إلى نوفمبر\n"
            "- القمح الربيعي: مارس إلى أبريل\n\n"
            "درجة حرارة التربة المثلى: 12-25 درجة مئوية\n"
            "للحصول على نصيحة مخصصة، حدد موقع حقلك."
        ),
        category="planting",
    ),
    "when to water": QuickResponse(
        response_en=(
            "Optimal irrigation timing:\n"
            "- Best time: Early morning (6-8 AM) or evening (after 6 PM)\n"
            "- Avoid: Midday heat (water evaporates quickly)\n"
            "- Check soil moisture before watering\n\n"
            "For personalized scheduling, provide your field ID."
        ),
        response_ar=(
            "أفضل وقت للري:\n"
            "- الوقت المثالي: الصباح الباكر (6-8 صباحاً) أو المساء (بعد 6 مساءً)\n"
            "- تجنب: حرارة الظهيرة (الماء يتبخر بسرعة)\n"
            "- افحص رطوبة التربة قبل الري\n\n"
            "للحصول على جدول مخصص، حدد معرف حقلك."
        ),
        category="irrigation",
    ),
    "متى أسقي": QuickResponse(
        response_en="Best irrigation time: Early morning (6-8 AM) or evening (after 6 PM).",
        response_ar=(
            "أفضل وقت للري:\n"
            "- الوقت المثالي: الصباح الباكر (6-8 صباحاً) أو المساء (بعد 6 مساءً)\n"
            "- تجنب: حرارة الظهيرة (الماء يتبخر بسرعة)\n"
            "- افحص رطوبة التربة قبل الري\n\n"
            "للحصول على جدول مخصص، حدد معرف حقلك."
        ),
        category="irrigation",
    ),
    # Thanks
    "thank you": QuickResponse(
        response_en="You're welcome! Feel free to ask if you have more questions about your farm.",
        response_ar="على الرحب والسعة! لا تتردد في السؤال إذا كانت لديك أسئلة أخرى عن مزرعتك.",
        category="closing",
    ),
    "thanks": QuickResponse(
        response_en="You're welcome! Happy farming!",
        response_ar="على الرحب والسعة! زراعة موفقة!",
        category="closing",
    ),
    "شكرا": QuickResponse(
        response_en="You're welcome! Feel free to ask more questions.",
        response_ar="على الرحب والسعة! لا تتردد في السؤال إذا كانت لديك أسئلة أخرى.",
        category="closing",
    ),
    "شكراً": QuickResponse(
        response_en="You're welcome! Feel free to ask more questions.",
        response_ar="عفواً! سعيد بمساعدتك في أي وقت.",
        category="closing",
    ),
}

# Fuzzy matching patterns for common questions
# These are patterns that might have variations
PATTERN_MATCHERS: list[tuple[list[str], str]] = [
    # Platform info
    (["what", "sahool"], "what is sahool"),
    (["ما", "سهول"], "ما هو سهول"),
    # NDVI
    (["what", "ndvi"], "what is ndvi"),
    (["ما", "ndvi"], "ما هو ndvi"),
    # Wheat planting
    (["when", "plant", "wheat"], "when to plant wheat"),
    (["متى", "زرع", "قمح"], "متى أزرع القمح"),
    (["متى", "أزرع", "قمح"], "متى أزرع القمح"),
    # Watering
    (["when", "water"], "when to water"),
    (["when", "irrigate"], "when to water"),
    (["متى", "سقي"], "متى أسقي"),
    (["متى", "ري"], "متى أسقي"),
]


def normalize_query(query: str) -> str:
    """
    Normalize a query for matching.
    تطبيع الاستعلام للمطابقة.
    """
    # Lowercase and strip
    normalized = query.lower().strip()

    # Remove common punctuation
    for char in ["?", "!", ".", ",", "؟", "،"]:
        normalized = normalized.replace(char, "")

    return normalized


def get_quick_response(query: str) -> QuickResponse | None:
    """
    Get a quick response for a query if available.
    الحصول على رد سريع للاستعلام إذا كان متاحاً.

    Args:
        query: User's query text

    Returns:
        QuickResponse if found, None otherwise
    """
    normalized = normalize_query(query)

    # Direct match
    if normalized in QUICK_RESPONSES:
        return QUICK_RESPONSES[normalized]

    # Pattern matching
    words = set(normalized.split())
    for patterns, response_key in PATTERN_MATCHERS:
        if all(p in normalized or p in words for p in patterns):
            return QUICK_RESPONSES.get(response_key)

    return None


def is_quick_query(query: str) -> bool:
    """
    Check if a query can be answered with a quick response.
    التحقق مما إذا كان يمكن الإجابة على الاستعلام برد سريع.
    """
    return get_quick_response(query) is not None


def get_all_quick_patterns() -> list[str]:
    """
    Get all available quick response patterns.
    الحصول على جميع أنماط الردود السريعة المتاحة.
    """
    return list(QUICK_RESPONSES.keys())


def get_quick_responses_by_category(category: str) -> list[tuple[str, QuickResponse]]:
    """
    Get quick responses filtered by category.
    الحصول على الردود السريعة مفلترة حسب الفئة.
    """
    return [
        (key, resp)
        for key, resp in QUICK_RESPONSES.items()
        if resp.category == category
    ]


def get_categories() -> list[str]:
    """
    Get all available categories.
    الحصول على جميع الفئات المتاحة.
    """
    return list(set(r.category for r in QUICK_RESPONSES.values()))

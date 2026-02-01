"""
Agricultural Prompt Templates
=============================
قوالب المطالبات الزراعية

Bilingual (Arabic/English) prompt templates for agricultural AI applications.
Includes crop advisory, disease diagnosis, irrigation advice, and more.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PromptLanguage(str, Enum):
    """Supported languages."""

    ENGLISH = "en"
    ARABIC = "ar"
    BILINGUAL = "both"


class PromptCategory(str, Enum):
    """Prompt categories."""

    CROP_ADVISORY = "crop_advisory"
    DISEASE_DIAGNOSIS = "disease_diagnosis"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PEST_CONTROL = "pest_control"
    HARVEST = "harvest"
    GENERAL = "general"


@dataclass
class PromptTemplate:
    """
    Bilingual prompt template.

    قالب مطالبة ثنائي اللغة
    """

    name: str
    name_ar: str
    category: PromptCategory
    system_en: str
    system_ar: str
    user_template_en: str
    user_template_ar: str
    description: str = ""
    description_ar: str = ""

    def get_system_prompt(self, language: PromptLanguage = PromptLanguage.ENGLISH) -> str:
        """Get system prompt in specified language."""
        if language == PromptLanguage.ARABIC:
            return self.system_ar
        elif language == PromptLanguage.BILINGUAL:
            return f"{self.system_en}\n\n{self.system_ar}"
        return self.system_en

    def get_user_prompt(
        self,
        language: PromptLanguage = PromptLanguage.ENGLISH,
        **kwargs: Any,
    ) -> str:
        """
        Get formatted user prompt.

        Args:
            language: Output language
            **kwargs: Template variables

        Returns:
            Formatted prompt string
        """
        if language == PromptLanguage.ARABIC:
            template = self.user_template_ar
        elif language == PromptLanguage.BILINGUAL:
            template = f"{self.user_template_en}\n\n{self.user_template_ar}"
        else:
            template = self.user_template_en

        return template.format(**kwargs)

    def format(
        self,
        language: PromptLanguage = PromptLanguage.ENGLISH,
        **kwargs: Any,
    ) -> tuple[str, str]:
        """
        Get both system and user prompts.

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        return (
            self.get_system_prompt(language),
            self.get_user_prompt(language, **kwargs),
        )


# ============================================================================
# CROP ADVISORY PROMPTS
# ============================================================================

CROP_ADVISOR_TEMPLATE = PromptTemplate(
    name="Crop Advisor",
    name_ar="مستشار المحاصيل",
    category=PromptCategory.CROP_ADVISORY,
    description="General crop advisory and recommendations",
    description_ar="استشارات وتوصيات زراعية عامة",
    system_en="""You are an expert agricultural advisor for the SAHOOL platform, \
specializing in Middle Eastern agriculture. Provide practical, actionable advice \
for farmers based on local conditions, crop types, and best practices.

Guidelines:
- Consider local climate conditions (arid/semi-arid)
- Factor in water scarcity and efficient irrigation
- Use metric units (hectares, kg, mm)
- Provide cost-effective solutions suitable for smallholder farmers
- Include timing recommendations based on crop growth stages
- Mention any safety precautions when recommending chemicals""",
    system_ar="""أنت مستشار زراعي خبير لمنصة سهول، متخصص في الزراعة في الشرق الأوسط. \
قدم نصائح عملية وقابلة للتنفيذ للمزارعين بناءً على الظروف المحلية وأنواع المحاصيل \
وأفضل الممارسات.

إرشادات:
- ضع في الاعتبار الظروف المناخية المحلية (جافة/شبه جافة)
- راعِ ندرة المياه والري الفعال
- استخدم الوحدات المترية (هكتار، كجم، مم)
- قدم حلولاً فعالة من حيث التكلفة مناسبة لصغار المزارعين
- أضف توصيات التوقيت بناءً على مراحل نمو المحصول
- اذكر احتياطات السلامة عند التوصية بالمواد الكيميائية""",
    user_template_en="""Crop: {crop_type}
Field Area: {area_hectares} hectares
Current Growth Stage: {growth_stage}
Location: {location}
Current Conditions: {conditions}

Question: {question}

Please provide detailed agricultural advice.""",
    user_template_ar="""المحصول: {crop_type}
مساحة الحقل: {area_hectares} هكتار
مرحلة النمو الحالية: {growth_stage}
الموقع: {location}
الظروف الحالية: {conditions}

السؤال: {question}

يرجى تقديم نصيحة زراعية مفصلة.""",
)


# ============================================================================
# DISEASE DIAGNOSIS PROMPTS
# ============================================================================

DISEASE_DIAGNOSIS_TEMPLATE = PromptTemplate(
    name="Disease Diagnosis",
    name_ar="تشخيص الأمراض",
    category=PromptCategory.DISEASE_DIAGNOSIS,
    description="Diagnose crop diseases from symptoms",
    description_ar="تشخيص أمراض المحاصيل من الأعراض",
    system_en="""You are a plant pathologist expert specializing in crop diseases \
common in the Middle East. Analyze the symptoms described and provide:
1. Most likely disease diagnosis
2. Confidence level (high/medium/low)
3. Contributing factors
4. Immediate actions to take
5. Treatment recommendations (chemical and organic options)
6. Prevention measures for future

Consider common diseases for the crop type mentioned and local environmental conditions.""",
    system_ar="""أنت خبير في أمراض النباتات متخصص في أمراض المحاصيل الشائعة في \
الشرق الأوسط. حلل الأعراض الموصوفة وقدم:
1. التشخيص الأكثر احتمالاً للمرض
2. مستوى الثقة (عالي/متوسط/منخفض)
3. العوامل المساهمة
4. الإجراءات الفورية الواجب اتخاذها
5. توصيات العلاج (خيارات كيميائية وعضوية)
6. تدابير الوقاية للمستقبل

ضع في الاعتبار الأمراض الشائعة لنوع المحصول المذكور والظروف البيئية المحلية.""",
    user_template_en="""Crop: {crop_type}
Growth Stage: {growth_stage}
Symptoms Observed:
{symptoms}

Environmental Conditions:
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Recent Weather: {recent_weather}

Please diagnose the issue and provide treatment recommendations.""",
    user_template_ar="""المحصول: {crop_type}
مرحلة النمو: {growth_stage}
الأعراض الملاحظة:
{symptoms}

الظروف البيئية:
- درجة الحرارة: {temperature} درجة مئوية
- الرطوبة: {humidity}%
- الطقس الأخير: {recent_weather}

يرجى تشخيص المشكلة وتقديم توصيات العلاج.""",
)


# ============================================================================
# IRRIGATION ADVICE PROMPTS
# ============================================================================

IRRIGATION_ADVICE_TEMPLATE = PromptTemplate(
    name="Irrigation Advice",
    name_ar="نصيحة الري",
    category=PromptCategory.IRRIGATION,
    description="Smart irrigation recommendations",
    description_ar="توصيات الري الذكي",
    system_en="""You are an irrigation specialist for arid and semi-arid regions. \
Provide precise irrigation recommendations based on:
- Crop water requirements (ETc)
- Soil moisture levels
- Weather forecasts
- Growth stage needs
- Available water resources

Always prioritize water efficiency and consider:
- Drip vs sprinkler vs flood irrigation suitability
- Best time of day for irrigation
- Signs of over/under-watering
- Salinity management if applicable""",
    system_ar="""أنت متخصص في الري للمناطق الجافة وشبه الجافة. قدم توصيات ري \
دقيقة بناءً على:
- متطلبات المياه للمحصول (ETc)
- مستويات رطوبة التربة
- توقعات الطقس
- احتياجات مرحلة النمو
- الموارد المائية المتاحة

أعطِ الأولوية دائماً لكفاءة المياه وضع في الاعتبار:
- مدى ملاءمة الري بالتنقيط مقابل الرش مقابل الغمر
- أفضل وقت في اليوم للري
- علامات الإفراط/نقص الري
- إدارة الملوحة إن وجدت""",
    user_template_en="""Crop: {crop_type}
Field Area: {area_hectares} hectares
Growth Stage: {growth_stage}
Irrigation System: {irrigation_type}

Current Conditions:
- Soil Moisture: {soil_moisture}%
- Soil Type: {soil_type}
- Last Irrigation: {last_irrigation}

Weather Forecast (next 7 days):
- Temperature: {temp_forecast}
- Rain Expected: {rain_forecast}
- ET₀: {eto} mm/day

Water Available: {water_available}

Please provide irrigation schedule and volume recommendations.""",
    user_template_ar="""المحصول: {crop_type}
مساحة الحقل: {area_hectares} هكتار
مرحلة النمو: {growth_stage}
نظام الري: {irrigation_type}

الظروف الحالية:
- رطوبة التربة: {soil_moisture}%
- نوع التربة: {soil_type}
- آخر ري: {last_irrigation}

توقعات الطقس (الأيام السبعة القادمة):
- درجة الحرارة: {temp_forecast}
- هطول متوقع: {rain_forecast}
- التبخر النتحي المرجعي: {eto} مم/يوم

المياه المتاحة: {water_available}

يرجى تقديم جدول الري وتوصيات الكمية.""",
)


# ============================================================================
# FERTILIZER RECOMMENDATION PROMPTS
# ============================================================================

FERTILIZER_RECOMMENDATION_TEMPLATE = PromptTemplate(
    name="Fertilizer Recommendation",
    name_ar="توصية التسميد",
    category=PromptCategory.FERTILIZER,
    description="Fertilizer application recommendations",
    description_ar="توصيات تطبيق الأسمدة",
    system_en="""You are a soil fertility and plant nutrition expert. Provide \
fertilizer recommendations based on:
- Soil test results (N, P, K, pH, EC, organic matter)
- Crop nutrient requirements at current growth stage
- Target yield
- Economic considerations

Include:
- Specific fertilizer products and application rates
- Application timing and method
- Split application schedules if needed
- Micronutrient recommendations if deficiencies suspected
- Organic alternatives where suitable
- Cost estimates per hectare""",
    system_ar="""أنت خبير في خصوبة التربة وتغذية النبات. قدم توصيات التسميد بناءً على:
- نتائج تحليل التربة (النيتروجين، الفوسفور، البوتاسيوم، الأس الهيدروجيني، \
الموصلية الكهربائية، المادة العضوية)
- متطلبات المحصول من العناصر الغذائية في مرحلة النمو الحالية
- الإنتاجية المستهدفة
- الاعتبارات الاقتصادية

أضمن:
- منتجات أسمدة محددة ومعدلات التطبيق
- توقيت وطريقة التطبيق
- جداول التطبيق المقسمة إذا لزم الأمر
- توصيات العناصر الصغرى إذا كان هناك نقص مشتبه به
- البدائل العضوية حيثما كان ذلك مناسباً
- تقديرات التكلفة لكل هكتار""",
    user_template_en="""Crop: {crop_type}
Variety: {variety}
Field Area: {area_hectares} hectares
Growth Stage: {growth_stage}
Target Yield: {target_yield} tons/ha

Soil Test Results:
- Nitrogen (N): {nitrogen} ppm
- Phosphorus (P): {phosphorus} ppm
- Potassium (K): {potassium} ppm
- pH: {ph}
- EC: {ec} dS/m
- Organic Matter: {organic_matter}%

Previous Crop: {previous_crop}
Previous Fertilizer Applied: {previous_fertilizer}

Please provide fertilizer recommendations with application schedule.""",
    user_template_ar="""المحصول: {crop_type}
الصنف: {variety}
مساحة الحقل: {area_hectares} هكتار
مرحلة النمو: {growth_stage}
الإنتاجية المستهدفة: {target_yield} طن/هكتار

نتائج تحليل التربة:
- النيتروجين (N): {nitrogen} جزء في المليون
- الفوسفور (P): {phosphorus} جزء في المليون
- البوتاسيوم (K): {potassium} جزء في المليون
- الأس الهيدروجيني: {ph}
- الموصلية الكهربائية: {ec} ديسي سيمنز/متر
- المادة العضوية: {organic_matter}%

المحصول السابق: {previous_crop}
الأسمدة المطبقة سابقاً: {previous_fertilizer}

يرجى تقديم توصيات التسميد مع جدول التطبيق.""",
)


# ============================================================================
# PEST CONTROL PROMPTS
# ============================================================================

PEST_CONTROL_TEMPLATE = PromptTemplate(
    name="Pest Control",
    name_ar="مكافحة الآفات",
    category=PromptCategory.PEST_CONTROL,
    description="Integrated pest management recommendations",
    description_ar="توصيات الإدارة المتكاملة للآفات",
    system_en="""You are an entomologist and IPM (Integrated Pest Management) \
specialist. Provide pest control recommendations following IPM principles:

1. Identification: Confirm pest identity
2. Monitoring: Economic threshold levels
3. Prevention: Cultural and biological controls first
4. Chemical control: Only when thresholds exceeded

Always include:
- Safety precautions and PHI (Pre-Harvest Interval)
- Impact on beneficial insects
- Resistance management (rotate active ingredients)
- Application timing for maximum effectiveness
- Environmental considerations""",
    system_ar="""أنت عالم حشرات ومتخصص في الإدارة المتكاملة للآفات (IPM). \
قدم توصيات مكافحة الآفات وفقاً لمبادئ الإدارة المتكاملة:

1. التعريف: تأكيد هوية الآفة
2. الرصد: مستويات العتبة الاقتصادية
3. الوقاية: المكافحة الثقافية والبيولوجية أولاً
4. المكافحة الكيميائية: فقط عند تجاوز العتبات

أضمن دائماً:
- احتياطات السلامة وفترة ما قبل الحصاد (PHI)
- التأثير على الحشرات المفيدة
- إدارة المقاومة (تدوير المواد الفعالة)
- توقيت التطبيق لأقصى فعالية
- الاعتبارات البيئية""",
    user_template_en="""Crop: {crop_type}
Growth Stage: {growth_stage}
Field Area: {area_hectares} hectares

Pest Observed: {pest_description}
Infestation Level: {infestation_level}
Affected Area: {affected_percentage}% of field

Previous Control Measures: {previous_measures}

Please provide IPM-based control recommendations.""",
    user_template_ar="""المحصول: {crop_type}
مرحلة النمو: {growth_stage}
مساحة الحقل: {area_hectares} هكتار

الآفة الملاحظة: {pest_description}
مستوى الإصابة: {infestation_level}
المنطقة المتأثرة: {affected_percentage}% من الحقل

إجراءات المكافحة السابقة: {previous_measures}

يرجى تقديم توصيات مكافحة مبنية على الإدارة المتكاملة للآفات.""",
)


# ============================================================================
# HARVEST TIMING PROMPTS
# ============================================================================

HARVEST_TIMING_TEMPLATE = PromptTemplate(
    name="Harvest Timing",
    name_ar="توقيت الحصاد",
    category=PromptCategory.HARVEST,
    description="Optimal harvest timing recommendations",
    description_ar="توصيات التوقيت الأمثل للحصاد",
    system_en="""You are a post-harvest specialist. Provide harvest timing \
recommendations based on:
- Crop maturity indicators
- Quality parameters
- Market conditions
- Weather forecasts
- Storage requirements

Include:
- Visual and measurable maturity indicators
- Optimal moisture content for harvest
- Equipment requirements
- Post-harvest handling recommendations
- Storage conditions""",
    system_ar="""أنت متخصص في ما بعد الحصاد. قدم توصيات توقيت الحصاد بناءً على:
- مؤشرات نضج المحصول
- معايير الجودة
- ظروف السوق
- توقعات الطقس
- متطلبات التخزين

أضمن:
- مؤشرات النضج المرئية والقابلة للقياس
- المحتوى الرطوبي الأمثل للحصاد
- متطلبات المعدات
- توصيات التعامل بعد الحصاد
- ظروف التخزين""",
    user_template_en="""Crop: {crop_type}
Variety: {variety}
Planting Date: {planting_date}
Current Growth Stage: {growth_stage}

Current Observations:
{observations}

Weather Forecast:
{weather_forecast}

Market Timing Preference: {market_preference}

Please advise on optimal harvest timing and procedures.""",
    user_template_ar="""المحصول: {crop_type}
الصنف: {variety}
تاريخ الزراعة: {planting_date}
مرحلة النمو الحالية: {growth_stage}

الملاحظات الحالية:
{observations}

توقعات الطقس:
{weather_forecast}

تفضيل توقيت السوق: {market_preference}

يرجى تقديم المشورة بشأن التوقيت الأمثل للحصاد والإجراءات.""",
)


# ============================================================================
# GENERAL AGRICULTURAL QUESTION PROMPT
# ============================================================================

GENERAL_AGRICULTURAL_TEMPLATE = PromptTemplate(
    name="General Agricultural Question",
    name_ar="سؤال زراعي عام",
    category=PromptCategory.GENERAL,
    description="General agricultural questions",
    description_ar="أسئلة زراعية عامة",
    system_en="""You are a knowledgeable agricultural expert for the SAHOOL \
platform. Answer questions about farming, crops, livestock, and agricultural \
practices in the Middle East region.

Be helpful, accurate, and practical. If you're uncertain about something, \
say so and suggest consulting a local agricultural extension officer.

Always consider:
- Local climate and conditions
- Water scarcity
- Cost-effectiveness for smallholder farmers
- Sustainable practices""",
    system_ar="""أنت خبير زراعي على دراية بمنصة سهول. أجب عن الأسئلة حول \
الزراعة والمحاصيل والثروة الحيوانية والممارسات الزراعية في منطقة الشرق الأوسط.

كن مفيداً ودقيقاً وعملياً. إذا كنت غير متأكد من شيء ما، قل ذلك واقترح \
استشارة مرشد زراعي محلي.

ضع في الاعتبار دائماً:
- المناخ والظروف المحلية
- ندرة المياه
- فعالية التكلفة لصغار المزارعين
- الممارسات المستدامة""",
    user_template_en="""{question}""",
    user_template_ar="""{question}""",
)


# ============================================================================
# PROMPT REGISTRY
# ============================================================================

PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    "crop_advisor": CROP_ADVISOR_TEMPLATE,
    "disease_diagnosis": DISEASE_DIAGNOSIS_TEMPLATE,
    "irrigation_advice": IRRIGATION_ADVICE_TEMPLATE,
    "fertilizer_recommendation": FERTILIZER_RECOMMENDATION_TEMPLATE,
    "pest_control": PEST_CONTROL_TEMPLATE,
    "harvest_timing": HARVEST_TIMING_TEMPLATE,
    "general": GENERAL_AGRICULTURAL_TEMPLATE,
}


def get_prompt_template(name: str) -> PromptTemplate | None:
    """
    Get a prompt template by name.

    الحصول على قالب مطالبة بالاسم
    """
    return PROMPT_TEMPLATES.get(name)


def list_prompt_templates() -> list[dict[str, str]]:
    """
    List all available prompt templates.

    قائمة جميع قوالب المطالبات المتاحة
    """
    return [
        {
            "name": name,
            "name_ar": template.name_ar,
            "category": template.category.value,
            "description": template.description,
            "description_ar": template.description_ar,
        }
        for name, template in PROMPT_TEMPLATES.items()
    ]


def get_prompts_by_category(category: PromptCategory) -> list[PromptTemplate]:
    """
    Get all prompts in a category.

    الحصول على جميع المطالبات في فئة
    """
    return [t for t in PROMPT_TEMPLATES.values() if t.category == category]


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def format_crop_advisory(
    crop_type: str,
    question: str,
    area_hectares: float = 1.0,
    growth_stage: str = "vegetative",
    location: str = "Middle East",
    conditions: str = "",
    language: PromptLanguage = PromptLanguage.ENGLISH,
) -> tuple[str, str]:
    """
    Format a crop advisory prompt.

    تنسيق مطالبة استشارة المحاصيل

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    return CROP_ADVISOR_TEMPLATE.format(
        language=language,
        crop_type=crop_type,
        area_hectares=area_hectares,
        growth_stage=growth_stage,
        location=location,
        conditions=conditions,
        question=question,
    )


def format_disease_diagnosis(
    crop_type: str,
    symptoms: str,
    growth_stage: str = "vegetative",
    temperature: float = 25.0,
    humidity: float = 60.0,
    recent_weather: str = "normal",
    language: PromptLanguage = PromptLanguage.ENGLISH,
) -> tuple[str, str]:
    """
    Format a disease diagnosis prompt.

    تنسيق مطالبة تشخيص الأمراض
    """
    return DISEASE_DIAGNOSIS_TEMPLATE.format(
        language=language,
        crop_type=crop_type,
        growth_stage=growth_stage,
        symptoms=symptoms,
        temperature=temperature,
        humidity=humidity,
        recent_weather=recent_weather,
    )


def format_irrigation_advice(
    crop_type: str,
    area_hectares: float,
    soil_moisture: float,
    soil_type: str = "loam",
    irrigation_type: str = "drip",
    growth_stage: str = "vegetative",
    last_irrigation: str = "2 days ago",
    temp_forecast: str = "25-30°C",
    rain_forecast: str = "No rain expected",
    eto: float = 5.0,
    water_available: str = "Sufficient",
    language: PromptLanguage = PromptLanguage.ENGLISH,
) -> tuple[str, str]:
    """
    Format an irrigation advice prompt.

    تنسيق مطالبة نصيحة الري
    """
    return IRRIGATION_ADVICE_TEMPLATE.format(
        language=language,
        crop_type=crop_type,
        area_hectares=area_hectares,
        growth_stage=growth_stage,
        irrigation_type=irrigation_type,
        soil_moisture=soil_moisture,
        soil_type=soil_type,
        last_irrigation=last_irrigation,
        temp_forecast=temp_forecast,
        rain_forecast=rain_forecast,
        eto=eto,
        water_available=water_available,
    )


def format_general_question(
    question: str,
    language: PromptLanguage = PromptLanguage.ENGLISH,
) -> tuple[str, str]:
    """
    Format a general agricultural question.

    تنسيق سؤال زراعي عام
    """
    return GENERAL_AGRICULTURAL_TEMPLATE.format(
        language=language,
        question=question,
    )

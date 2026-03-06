"""
Arabic AI Models for Agricultural Registry
============================================
نماذج الذكاء الاصطناعي العربية لسجل النماذج الزراعية

Arabic-first and Arabic-supporting AI models from organizations across
the Arab world, designed for or adapted to Arabic language understanding,
generation, and agricultural domain applications.

النماذج العربية الأولى والداعمة للعربية من مؤسسات في العالم العربي،
مصممة أو مكيفة لفهم وتوليد اللغة العربية وتطبيقات المجال الزراعي.

Models included:
- Jais (جيس) - Inception/G42, UAE
- AceGPT - MBZUAI/FlagOpen
- ALLaM (علام) - SDAIA, Saudi Arabia
- SILMA (سلمى) - Silma AI
- AraGPT2 - AUBMINDLAB (AUB)

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

from .models import (
    AIModelCategory,
    AIModelInfo,
    DeveloperInfo,
    LanguageSupport,
    ModelArchitecture,
    ModelCapability,
    ModelLicense,
    ModelPerformance,
    ModelStatus,
)


def get_arabic_models() -> list[AIModelInfo]:
    """
    Get all Arabic AI models for registration.
    الحصول على جميع نماذج الذكاء الاصطناعي العربية للتسجيل.

    Returns:
        List of AIModelInfo instances for Arabic models
    """
    return [
        _create_jais(),
        _create_jais_adapted(),
        _create_acegpt(),
        _create_allam(),
        _create_silma(),
        _create_aragpt2(),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Jais - Inception/G42 (UAE)
# جيس - إنسبشن/جي42 (الإمارات)
# ═══════════════════════════════════════════════════════════════════════════════


def _create_jais() -> AIModelInfo:
    """Jais - Arabic-centric bilingual LLM by Inception/G42 (UAE)."""
    return AIModelInfo(
        model_id="jais-30b",
        name="Jais 30B",
        name_ar="جيس 30 مليار",
        category=AIModelCategory.GENERAL_AGRICULTURE,
        capabilities=[
            ModelCapability.QA,
            ModelCapability.DECISION_SUPPORT,
            ModelCapability.EXPERT_CONSULTATION,
        ],
        architecture=ModelArchitecture.LLM,
        developer=DeveloperInfo(
            name="Inception / G42 (Core42)",
            name_ar="إنسبشن / جي42 (كور42)",
            organization_type="commercial",
            country="UAE",
            website="https://www.inceptioniai.org/jais",
        ),
        url="https://huggingface.co/inceptioniai/jais-30b-chat-v3",
        huggingface_url="https://huggingface.co/inceptioniai/jais-30b-chat-v3",
        paper_url="https://arxiv.org/abs/2308.16149",
        status=ModelStatus.ACTIVE,
        license=ModelLicense.OPEN_SOURCE,
        version="3.0",
        release_date="2024-03",
        language_support=LanguageSupport(
            arabic=True,
            english=True,
        ),
        base_model="Custom GPT Architecture",
        parameter_count="30B",
        context_length=8192,
        performance=ModelPerformance(
            accuracy=0.82,
            benchmark_dataset="Arabic MMLU, ACVA",
            benchmark_date="2024-03",
            notes=(
                "State-of-the-art Arabic LLM. Outperforms LLaMA-2 and Falcon "
                "on Arabic benchmarks. Trained on balanced Arabic-English corpus."
            ),
        ),
        description=(
            "Jais is the world's most advanced Arabic large language model, "
            "developed by Inception (a G42 company) in the UAE. Built from scratch "
            "with a balanced Arabic-English training corpus, it excels at Arabic "
            "understanding, generation, and instruction-following. Suitable for "
            "agricultural advisory in Arabic-speaking regions."
        ),
        description_ar=(
            "جيس هو أكثر نماذج اللغة العربية الكبيرة تقدماً في العالم، "
            "طُوِّر بواسطة إنسبشن (إحدى شركات جي42) في الإمارات. "
            "بُني من الصفر بمجموعة بيانات متوازنة عربية-إنجليزية، ويتفوق "
            "في فهم وتوليد واتباع التعليمات بالعربية. مناسب للاستشارات "
            "الزراعية في المناطق الناطقة بالعربية."
        ),
        use_cases=[
            "Arabic agricultural advisory",
            "Bilingual crop management Q&A",
            "Farmer support chatbot",
            "Agricultural knowledge extraction",
        ],
        use_cases_ar=[
            "الاستشارات الزراعية بالعربية",
            "أسئلة وأجوبة إدارة المحاصيل ثنائية اللغة",
            "روبوت دعم المزارعين",
            "استخراج المعرفة الزراعية",
        ],
        tags=["arabic", "llm", "bilingual", "uae", "jais", "foundation", "chat"],
    )


def _create_jais_adapted() -> AIModelInfo:
    """Jais-adapted - Jais fine-tuned for agriculture."""
    return AIModelInfo(
        model_id="jais-agri",
        name="Jais Agriculture",
        name_ar="جيس الزراعة",
        category=AIModelCategory.GENERAL_AGRICULTURE,
        capabilities=[
            ModelCapability.QA,
            ModelCapability.DECISION_SUPPORT,
            ModelCapability.EXPERT_CONSULTATION,
            ModelCapability.CROP_MONITORING,
            ModelCapability.PEST_DETECTION,
        ],
        architecture=ModelArchitecture.LLM,
        developer=DeveloperInfo(
            name="SAHOOL Platform (fine-tuned from Jais)",
            name_ar="منصة سهول (مضبوط من جيس)",
            organization_type="commercial",
            country="UAE",
        ),
        status=ModelStatus.COMING_SOON,
        license=ModelLicense.PROPRIETARY,
        version="1.0",
        language_support=LanguageSupport(arabic=True, english=True),
        base_model="Jais-30B",
        parameter_count="30B",
        context_length=8192,
        description=(
            "Jais model fine-tuned on SAHOOL agricultural knowledge base for "
            "Arabic-first crop advisory, pest diagnosis, and irrigation planning. "
            "Integrates regional agricultural knowledge from Middle East and "
            "North Africa (MENA) sources."
        ),
        description_ar=(
            "نموذج جيس مضبوط على قاعدة المعرفة الزراعية لسهول "
            "للاستشارات الزراعية بالعربية أولاً، وتشخيص الآفات، "
            "وتخطيط الري. يدمج المعرفة الزراعية الإقليمية من مصادر "
            "الشرق الأوسط وشمال أفريقيا."
        ),
        use_cases=[
            "MENA crop advisory",
            "Arabic pest diagnosis",
            "Regional irrigation planning",
        ],
        use_cases_ar=[
            "استشارات محاصيل الشرق الأوسط وشمال أفريقيا",
            "تشخيص الآفات بالعربية",
            "تخطيط الري الإقليمي",
        ],
        tags=["arabic", "agriculture", "fine-tuned", "jais", "mena", "advisory"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AceGPT - MBZUAI / FlagOpen
# ═══════════════════════════════════════════════════════════════════════════════


def _create_acegpt() -> AIModelInfo:
    """AceGPT - Arabic LLM by MBZUAI and FlagOpen."""
    return AIModelInfo(
        model_id="acegpt",
        name="AceGPT",
        name_ar="إيس جي بي تي",
        category=AIModelCategory.GENERAL_AGRICULTURE,
        capabilities=[
            ModelCapability.QA,
            ModelCapability.DECISION_SUPPORT,
            ModelCapability.EXPERT_CONSULTATION,
        ],
        architecture=ModelArchitecture.LLM,
        developer=DeveloperInfo(
            name="MBZUAI / FlagOpen (BAAI)",
            name_ar="جامعة محمد بن زايد للذكاء الاصطناعي / فلاغ أوبن",
            organization_type="academic",
            country="UAE",
            website="https://www.mbzuai.ac.ae/",
        ),
        url="https://huggingface.co/FlagOpen/AceGPT-v2-70B-Chat",
        huggingface_url="https://huggingface.co/FlagOpen/AceGPT-v2-70B-Chat",
        paper_url="https://arxiv.org/abs/2309.12053",
        github_url="https://github.com/FlagOpen/AceGPT",
        status=ModelStatus.ACTIVE,
        license=ModelLicense.OPEN_SOURCE,
        version="2.0",
        release_date="2024-06",
        language_support=LanguageSupport(
            arabic=True,
            english=True,
        ),
        base_model="LLaMA-2",
        parameter_count="70B",
        context_length=4096,
        performance=ModelPerformance(
            accuracy=0.79,
            benchmark_dataset="Arabic MMLU, ACVA, EXAMS",
            benchmark_date="2024-06",
            notes=(
                "Localized Arabic LLM using vocabulary expansion and "
                "pre-training on Arabic data. Strong performance on Arabic "
                "NLU and cultural alignment benchmarks."
            ),
        ),
        description=(
            "AceGPT is an Arabic-centric LLM developed by MBZUAI and FlagOpen (BAAI). "
            "Built by adapting LLaMA-2 with Arabic vocabulary expansion, continued "
            "pre-training on Arabic corpora, and cultural-aware alignment. "
            "Supports agricultural Q&A and culturally appropriate advisory for "
            "Arabic-speaking farmers."
        ),
        description_ar=(
            "إيس جي بي تي هو نموذج لغوي كبير مركز على العربية طوره "
            "جامعة محمد بن زايد للذكاء الاصطناعي وفلاغ أوبن. "
            "بُني بتكييف LLaMA-2 مع توسيع المفردات العربية والتدريب "
            "المستمر على مجموعات بيانات عربية. يدعم الأسئلة والأجوبة "
            "الزراعية والاستشارات المناسبة ثقافياً للمزارعين."
        ),
        use_cases=[
            "Arabic agricultural Q&A",
            "Cultural advisory alignment",
            "Farmer education in Arabic",
            "Agricultural text generation",
        ],
        use_cases_ar=[
            "أسئلة وأجوبة زراعية بالعربية",
            "محاذاة الاستشارات الثقافية",
            "تعليم المزارعين بالعربية",
            "توليد نصوص زراعية",
        ],
        tags=["arabic", "llm", "mbzuai", "uae", "llama", "cultural", "chat"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ALLaM - SDAIA (Saudi Arabia)
# علام - الهيئة السعودية للبيانات والذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════════


def _create_allam() -> AIModelInfo:
    """ALLaM - Arabic LLM by SDAIA (Saudi Arabia)."""
    return AIModelInfo(
        model_id="allam",
        name="ALLaM",
        name_ar="علّام",
        category=AIModelCategory.GENERAL_AGRICULTURE,
        capabilities=[
            ModelCapability.QA,
            ModelCapability.DECISION_SUPPORT,
            ModelCapability.EXPERT_CONSULTATION,
            ModelCapability.KNOWLEDGE_GRAPH,
        ],
        architecture=ModelArchitecture.LLM,
        developer=DeveloperInfo(
            name="SDAIA (Saudi Data & AI Authority) / IBM",
            name_ar="سدايا (الهيئة السعودية للبيانات والذكاء الاصطناعي) / آي بي إم",
            organization_type="government",
            country="Saudi Arabia",
            website="https://sdaia.gov.sa/",
        ),
        url="https://huggingface.co/sdaia/allam-1-13b-instruct",
        huggingface_url="https://huggingface.co/sdaia/allam-1-13b-instruct",
        status=ModelStatus.ACTIVE,
        license=ModelLicense.OPEN_SOURCE,
        version="1.0",
        release_date="2024-12",
        language_support=LanguageSupport(
            arabic=True,
            english=True,
        ),
        base_model="IBM Granite",
        parameter_count="13B",
        context_length=8192,
        performance=ModelPerformance(
            accuracy=0.78,
            benchmark_dataset="Arabic MMLU, ArabicBench",
            benchmark_date="2024-12",
            notes=(
                "Saudi government-backed Arabic LLM. Strong on Arabic dialects "
                "and Modern Standard Arabic. Trained with emphasis on Saudi and "
                "Gulf Arabic language patterns."
            ),
        ),
        description=(
            "ALLaM is a large Arabic language model developed by the Saudi Data "
            "and AI Authority (SDAIA) in collaboration with IBM. Named after the "
            "Arabic word for 'the knowledgeable one', it is designed for Arabic "
            "natural language understanding and generation. Particularly strong "
            "in Gulf Arabic dialects and agricultural terminology common in the "
            "Saudi agricultural sector."
        ),
        description_ar=(
            "علّام هو نموذج لغوي عربي كبير طورته الهيئة السعودية للبيانات "
            "والذكاء الاصطناعي (سدايا) بالتعاون مع آي بي إم. "
            "سُمّي بالعربية تيمناً بـ'العلّام' أي كثير العلم، "
            "وهو مصمم لفهم وتوليد اللغة العربية. قوي بشكل خاص "
            "في اللهجات الخليجية والمصطلحات الزراعية الشائعة "
            "في القطاع الزراعي السعودي."
        ),
        use_cases=[
            "Saudi agricultural advisory",
            "Gulf Arabic farmer support",
            "Agricultural policy analysis",
            "Arabic knowledge extraction",
            "Agricultural document understanding",
        ],
        use_cases_ar=[
            "الاستشارات الزراعية السعودية",
            "دعم المزارعين باللهجة الخليجية",
            "تحليل السياسات الزراعية",
            "استخراج المعرفة بالعربية",
            "فهم الوثائق الزراعية",
        ],
        tags=["arabic", "llm", "saudi", "sdaia", "gulf", "government", "ibm"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SILMA - Silma AI
# سلمى - سلمى للذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════════


def _create_silma() -> AIModelInfo:
    """SILMA - Arabic language model by Silma AI."""
    return AIModelInfo(
        model_id="silma",
        name="SILMA",
        name_ar="سِلما",
        category=AIModelCategory.GENERAL_AGRICULTURE,
        capabilities=[
            ModelCapability.QA,
            ModelCapability.DECISION_SUPPORT,
            ModelCapability.EXPERT_CONSULTATION,
        ],
        architecture=ModelArchitecture.LLM,
        developer=DeveloperInfo(
            name="Silma AI",
            name_ar="سلمى للذكاء الاصطناعي",
            organization_type="commercial",
            country="Saudi Arabia",
            website="https://huggingface.co/silma-ai",
        ),
        url="https://huggingface.co/silma-ai/SILMA-9B-Instruct-v1.0",
        huggingface_url="https://huggingface.co/silma-ai/SILMA-9B-Instruct-v1.0",
        status=ModelStatus.ACTIVE,
        license=ModelLicense.OPEN_SOURCE,
        version="1.0",
        release_date="2024-10",
        language_support=LanguageSupport(
            arabic=True,
            english=True,
        ),
        base_model="Gemma-2",
        parameter_count="9B",
        context_length=8192,
        performance=ModelPerformance(
            accuracy=0.75,
            benchmark_dataset="Arabic MMLU, ArabicBench",
            benchmark_date="2024-10",
            notes=(
                "Efficient Arabic model built on Gemma-2 architecture. "
                "Competitive performance with larger models on Arabic tasks. "
                "Small enough for edge deployment in low-connectivity environments."
            ),
        ),
        description=(
            "SILMA is an Arabic language model built on the Gemma-2 architecture "
            "by Silma AI. At 9B parameters, it provides strong Arabic language "
            "capabilities in a compact form factor suitable for deployment in "
            "resource-constrained environments. Ideal for offline-first agricultural "
            "applications where larger models cannot be hosted locally."
        ),
        description_ar=(
            "سِلما هو نموذج لغوي عربي مبني على بنية Gemma-2 "
            "بواسطة سلمى للذكاء الاصطناعي. بحجم 9 مليار معامل، "
            "يوفر قدرات عربية قوية في شكل مدمج مناسب للنشر "
            "في البيئات محدودة الموارد. مثالي للتطبيقات الزراعية "
            "العاملة بدون اتصال حيث لا يمكن استضافة نماذج أكبر محلياً."
        ),
        use_cases=[
            "Offline Arabic agricultural advisory",
            "Edge deployment for farmer support",
            "Mobile agricultural assistant",
            "Low-resource Arabic NLU",
        ],
        use_cases_ar=[
            "استشارات زراعية عربية بدون اتصال",
            "نشر على الأجهزة الطرفية لدعم المزارعين",
            "مساعد زراعي متنقل",
            "فهم اللغة العربية بموارد محدودة",
        ],
        tags=["arabic", "llm", "edge", "offline", "compact", "gemma", "saudi"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AraGPT2 - AUBMINDLAB (American University of Beirut)
# ═══════════════════════════════════════════════════════════════════════════════


def _create_aragpt2() -> AIModelInfo:
    """AraGPT2 - Arabic GPT-2 model by AUBMINDLAB."""
    return AIModelInfo(
        model_id="aragpt2",
        name="AraGPT2",
        name_ar="عربي جي بي تي 2",
        category=AIModelCategory.GENERAL_AGRICULTURE,
        capabilities=[
            ModelCapability.QA,
            ModelCapability.DECISION_SUPPORT,
        ],
        architecture=ModelArchitecture.LLM,
        developer=DeveloperInfo(
            name="AUBMINDLAB (American University of Beirut)",
            name_ar="مختبر العقل في الجامعة الأمريكية في بيروت",
            organization_type="academic",
            country="Lebanon",
            website="https://github.com/aub-mind",
        ),
        url="https://huggingface.co/aubmindlab/aragpt2-mega",
        huggingface_url="https://huggingface.co/aubmindlab/aragpt2-mega",
        github_url="https://github.com/aub-mind/arabert",
        paper_url="https://arxiv.org/abs/2012.15520",
        status=ModelStatus.ACTIVE,
        license=ModelLicense.OPEN_SOURCE,
        version="2.0",
        release_date="2021-06",
        language_support=LanguageSupport(
            arabic=True,
            english=False,
        ),
        base_model="GPT-2",
        parameter_count="1.46B",
        context_length=1024,
        performance=ModelPerformance(
            accuracy=0.72,
            benchmark_dataset="Arabic Perplexity Benchmark",
            benchmark_date="2021-06",
            notes=(
                "Pioneering Arabic generative model. AraGPT2-mega (1.46B) "
                "is the largest variant. Trained on 77GB of Arabic text. "
                "Lower perplexity than multilingual GPT-2 on Arabic text."
            ),
        ),
        description=(
            "AraGPT2 is one of the first large-scale Arabic text generation "
            "models, developed by AUBMINDLAB at the American University of Beirut. "
            "Built on the GPT-2 architecture and trained exclusively on Arabic text, "
            "it excels at Arabic text completion and generation. Part of the same "
            "ecosystem as AraBERT, the foundational Arabic NLP model. Suitable for "
            "generating agricultural reports and advisory text in Arabic."
        ),
        description_ar=(
            "عربي جي بي تي 2 هو أحد أوائل نماذج توليد النصوص العربية واسعة النطاق، "
            "طُوِّر بواسطة مختبر العقل في الجامعة الأمريكية في بيروت. "
            "بُني على بنية GPT-2 وتم تدريبه حصرياً على نصوص عربية. "
            "يتفوق في إكمال وتوليد النصوص العربية. جزء من نفس نظام "
            "AraBERT النموذج التأسيسي لمعالجة اللغة العربية. "
            "مناسب لتوليد التقارير الزراعية والنصوص الاستشارية بالعربية."
        ),
        use_cases=[
            "Arabic agricultural report generation",
            "Arabic text completion for farm docs",
            "Advisory text generation",
            "Arabic content creation",
        ],
        use_cases_ar=[
            "توليد تقارير زراعية بالعربية",
            "إكمال النصوص العربية لوثائق المزرعة",
            "توليد نصوص استشارية",
            "إنشاء محتوى بالعربية",
        ],
        tags=["arabic", "gpt2", "generation", "aub", "lebanon", "text", "arabert"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Registration Helper
# ═══════════════════════════════════════════════════════════════════════════════


def register_arabic_models(registry: Any) -> int:
    """
    Register all Arabic AI models into the given registry.
    تسجيل جميع نماذج الذكاء الاصطناعي العربية في السجل المحدد.

    Args:
        registry: AgriculturalAIRegistry instance with _register method

    Returns:
        Number of models registered
    """
    models = get_arabic_models()
    count = 0
    for model in models:
        if model.model_id not in registry:
            registry._register(model)
            count += 1
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# Quick Reference Constants
# ═══════════════════════════════════════════════════════════════════════════════

ARABIC_MODEL_IDS = [
    "jais-30b",
    "jais-agri",
    "acegpt",
    "allam",
    "silma",
    "aragpt2",
]
"""List of all Arabic model IDs | قائمة جميع معرفات النماذج العربية"""

ARABIC_MODELS_BY_COUNTRY: dict[str, list[str]] = {
    "UAE": ["jais-30b", "jais-agri", "acegpt"],
    "Saudi Arabia": ["allam", "silma"],
    "Lebanon": ["aragpt2"],
}
"""Arabic models organized by country | النماذج العربية مرتبة حسب الدولة"""

ARABIC_MODELS_FOR_AGRICULTURE: list[str] = [
    "jais-agri",  # Fine-tuned for agriculture (coming soon)
    "jais-30b",  # Strong general Arabic + English
    "allam",  # Saudi agricultural context
    "silma",  # Compact, good for edge/offline
    "acegpt",  # Cultural alignment
    "aragpt2",  # Arabic text generation
]
"""Arabic models ranked by agricultural suitability | النماذج العربية مرتبة حسب الملاءمة الزراعية"""

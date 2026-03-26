"""
Agricultural AI Models Registry
================================
سجل نماذج الذكاء الاصطناعي الزراعي

Comprehensive registry of 50+ agricultural AI models from academic institutions,
research laboratories, and commercial organizations worldwide.

Based on the survey article covering major agricultural AI innovations.

Categories:
1. General Agriculture Decision (通用农业决策) - 20+ models
2. Breeding & Bioscience (育种与生物科学) - 10+ models
3. Livestock & Veterinary (畜牧兽医) - 10+ models
4. Remote Sensing & Geo (遥感地理) - 10+ models
5. Specialty (专业垂直) - 10+ models

Philosophy:
- "让知识流动" (Let Knowledge Flow) - LLM consultants democratize expertise
- "让计算创造" (Let Computation Create) - Bio/remote sensing enables precision
- Future: From "advice" to "Agent execution"

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .models import (
    AIModelCategory,
    AIModelInfo,
    DeveloperInfo,
    LanguageSupport,
    ModelArchitecture,
    ModelCapability,
    ModelDiscoveryResult,
    ModelLicense,
    ModelStatus,
)


class AgriculturalAIRegistry:
    """Registry of Agricultural AI Models.

    سجل نماذج الذكاء الاصطناعي الزراعي
    农业AI模型注册表

    A comprehensive registry containing information about 50+ agricultural
    AI models from around the world, organized by category and capability.
    """

    def __init__(self):
        """Initialize the registry with all known models."""
        self._models: dict[str, AIModelInfo] = {}
        self._load_all_models()

    def _load_all_models(self) -> None:
        """Load all agricultural AI models into the registry."""
        # Load models by category
        self._load_general_agriculture_models()
        self._load_breeding_bioscience_models()
        self._load_livestock_veterinary_models()
        self._load_remote_sensing_models()
        self._load_specialty_models()

    # ========================================================================
    # Category 1: General Agriculture Decision (通用农业决策)
    # ========================================================================

    def _load_general_agriculture_models(self) -> None:
        """Load general agriculture decision support models."""

        # 1. Sinong (思农) - Nanjing Agricultural University
        self._register(
            AIModelInfo(
                model_id="sinong",
                name="Sinong",
                name_ar="سينونغ",
                name_cn="思农",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.EXPERT_CONSULTATION,
                    ModelCapability.PEST_DETECTION,
                    ModelCapability.DISEASE_DETECTION,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Nanjing Agricultural University",
                    name_ar="جامعة نانجينغ الزراعية",
                    name_cn="南京农业大学",
                    organization_type="academic",
                    country="China",
                ),
                url="https://github.com/njauzzx/Sinong",
                github_url="https://github.com/njauzzx/Sinong",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(chinese=True, english=True),
                base_model="LLaMA",
                description="Agricultural LLM for crop management and pest/disease identification",
                description_ar="نموذج لغوي كبير للزراعة لإدارة المحاصيل وتحديد الآفات/الأمراض",
                description_cn="用于作物管理和病虫害识别的农业大语言模型",
                use_cases=["Crop advisory", "Pest identification", "Disease diagnosis"],
                use_cases_ar=["استشارات المحاصيل", "تحديد الآفات", "تشخيص الأمراض"],
                tags=["llm", "crop", "pest", "disease", "chinese"],
            )
        )

        # 2. Qiwen/Enlightenment (启文) - Harbin Institute of Technology
        self._register(
            AIModelInfo(
                model_id="qiwen",
                name="Qiwen (Enlightenment)",
                name_ar="تشيوين (التنوير)",
                name_cn="启文",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.KNOWLEDGE_GRAPH,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Harbin Institute of Technology",
                    name_ar="معهد هاربين للتكنولوجيا",
                    name_cn="哈尔滨工业大学",
                    organization_type="academic",
                    country="China",
                ),
                url="https://www.tgkwai.com/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Agricultural knowledge enlightenment system with Q&A capabilities",
                description_ar="نظام تنوير المعرفة الزراعية مع قدرات الأسئلة والأجوبة",
                description_cn="具有问答能力的农业知识启蒙系统",
                tags=["llm", "knowledge", "qa", "chinese"],
            )
        )

        # 3. ShengNong 3.0 (神农) - China Agricultural University
        self._register(
            AIModelInfo(
                model_id="shengnong",
                name="ShengNong 3.0",
                name_ar="شينونغ 3.0",
                name_cn="神农3.0",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.EXPERT_CONSULTATION,
                    ModelCapability.PEST_DETECTION,
                    ModelCapability.DISEASE_DETECTION,
                    ModelCapability.YIELD_PREDICTION,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="China Agricultural University",
                    name_ar="جامعة الصين الزراعية",
                    name_cn="中国农业大学",
                    organization_type="academic",
                    country="China",
                    website="https://shennong.cau.edu.cn/",
                ),
                url="https://shennong.cau.edu.cn/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                version="3.0",
                language_support=LanguageSupport(chinese=True, english=True),
                base_model="Qwen-VL",
                description="Multimodal agricultural AI named after legendary Chinese agricultural deity",
                description_ar="ذكاء اصطناعي زراعي متعدد الوسائط سمي على اسم الإله الزراعي الصيني الأسطوري",
                description_cn="以中国传说农业神命名的多模态农业AI",
                use_cases=["Crop diagnosis", "Yield prediction", "Expert consultation"],
                tags=["vlm", "multimodal", "chinese", "flagship"],
            )
        )

        # 4. Guiyang Yunshen Agriculture (贵阳云深农业) - Northwest A&F University
        self._register(
            AIModelInfo(
                model_id="guiyang_yunshen",
                name="Guiyang Yunshen Agriculture",
                name_ar="قويانغ يونشين للزراعة",
                name_cn="贵阳云深农业",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Northwest A&F University",
                    name_ar="جامعة الشمال الغربي للزراعة والغابات",
                    name_cn="西北农林科技大学",
                    organization_type="academic",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True),
                description="Deep learning agriculture model from Northwest China",
                description_cn="来自西北农林的深度学习农业模型",
                tags=["llm", "chinese", "regional"],
            )
        )

        # 5. Qeeiji (齐耕集) - Beijing University of Agriculture
        self._register(
            AIModelInfo(
                model_id="qeeiji",
                name="Qeeiji",
                name_ar="تشيجي",
                name_cn="齐耕集",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.KNOWLEDGE_GRAPH,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Beijing University of Agriculture",
                    name_ar="جامعة بكين للزراعة",
                    name_cn="北京农学院",
                    organization_type="academic",
                    country="China",
                ),
                url="http://www.qeeg.org.cn/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True),
                description="Agricultural knowledge platform with collaborative features",
                description_cn="具有协作功能的农业知识平台",
                tags=["llm", "knowledge", "collaborative", "chinese"],
            )
        )

        # 6. Fentian Agriculture (丰田农业) - China Mobile
        self._register(
            AIModelInfo(
                model_id="fentian",
                name="Fentian Agriculture",
                name_ar="فنتيان للزراعة",
                name_cn="丰田农业",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.CROP_MONITORING,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="China Mobile",
                    name_ar="تشاينا موبايل",
                    name_cn="中国移动",
                    organization_type="commercial",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.PROPRIETARY,
                language_support=LanguageSupport(chinese=True),
                description="Enterprise agricultural AI from China's largest telecom",
                description_cn="来自中国最大电信公司的企业农业AI",
                tags=["llm", "enterprise", "commercial", "chinese"],
            )
        )

        # 7. AgriGPT - Zhejiang University
        self._register(
            AIModelInfo(
                model_id="agrigpt_zju",
                name="AgriGPT",
                name_ar="أجري جي بي تي",
                name_cn="AgriGPT",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.EXPERT_CONSULTATION,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Zhejiang University",
                    name_ar="جامعة تشجيانغ",
                    name_cn="浙江大学",
                    organization_type="academic",
                    country="China",
                ),
                url="https://arxiv.org/abs/2508.08632",
                paper_url="https://arxiv.org/abs/2508.08632",
                status=ModelStatus.RESEARCH,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Agricultural GPT from Zhejiang University",
                description_cn="来自浙江大学的农业GPT",
                tags=["llm", "gpt", "academic", "chinese"],
            )
        )

        # 8. AgroGPT - MBZUAI (Mohamed bin Zayed University of AI)
        self._register(
            AIModelInfo(
                model_id="agrogpt",
                name="AgroGPT",
                name_ar="أجرو جي بي تي",
                name_cn="AgroGPT",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.PEST_DETECTION,
                    ModelCapability.DISEASE_DETECTION,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Mohamed bin Zayed University of AI (MBZUAI)",
                    name_ar="جامعة محمد بن زايد للذكاء الاصطناعي",
                    name_cn="穆罕默德·本·扎耶德人工智能大学",
                    organization_type="academic",
                    country="UAE",
                    website="https://mbzuai.ac.ae/",
                ),
                url="https://github.com/awaisrauf/agroGPT",
                github_url="https://github.com/awaisrauf/agroGPT",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True, arabic=True),
                description="Vision-language model for agricultural applications from UAE",
                description_ar="نموذج رؤية-لغة للتطبيقات الزراعية من الإمارات",
                description_cn="来自阿联酋的农业视觉语言模型",
                use_cases=["Crop disease detection", "Agricultural Q&A"],
                use_cases_ar=["كشف أمراض المحاصيل", "أسئلة وأجوبة زراعية"],
                tags=["vlm", "arabic", "uae", "open-source"],
            )
        )

        # 9. AgroLLM - University of Pittsburgh
        self._register(
            AIModelInfo(
                model_id="agrollm",
                name="AgroLLM",
                name_ar="أجرو إل إل إم",
                name_cn="AgroLLM",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.YIELD_PREDICTION,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="University of Pittsburgh",
                    name_ar="جامعة بيتسبرغ",
                    name_cn="匹兹堡大学",
                    organization_type="academic",
                    country="USA",
                ),
                url="https://arxiv.org/abs/2503.04788",
                paper_url="https://arxiv.org/abs/2503.04788",
                status=ModelStatus.RESEARCH,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(english=True),
                description="Agricultural LLM for yield prediction and decision support",
                description_ar="نموذج لغوي كبير للزراعة للتنبؤ بالإنتاج ودعم القرار",
                description_cn="用于产量预测和决策支持的农业大语言模型",
                tags=["llm", "yield", "usa", "academic"],
            )
        )

        # 10. CropWizard - NCSA/UIUC
        self._register(
            AIModelInfo(
                model_id="cropwizard",
                name="CropWizard",
                name_ar="ويزارد المحاصيل",
                name_cn="CropWizard",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.EXPERT_CONSULTATION,
                    ModelCapability.KNOWLEDGE_GRAPH,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="National Center for Supercomputing Applications (NCSA)",
                    name_ar="المركز الوطني لتطبيقات الحوسبة الفائقة",
                    name_cn="国家超级计算应用中心",
                    organization_type="research",
                    country="USA",
                    website="https://www.ncsa.illinois.edu/",
                ),
                url="https://uiuc.chat/cropwizard-1.5/chat",
                version="1.5",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.FREEMIUM,
                language_support=LanguageSupport(english=True),
                base_model="GPT-4",
                description="Agricultural expert system powered by NCSA supercomputing",
                description_ar="نظام خبير زراعي مدعوم بالحوسبة الفائقة من NCSA",
                description_cn="由NCSA超级计算支持的农业专家系统",
                use_cases=["Crop advisory", "Agricultural Q&A", "Expert consultation"],
                tags=["llm", "expert-system", "usa", "ncsa"],
            )
        )

        # 11. Taranis AI Assistant
        self._register(
            AIModelInfo(
                model_id="taranis_ai",
                name="Taranis AI Assistant",
                name_ar="مساعد تارانيس الذكي",
                name_cn="Taranis AI助手",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.PEST_DETECTION,
                    ModelCapability.DISEASE_DETECTION,
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Taranis",
                    name_ar="تارانيس",
                    name_cn="Taranis",
                    organization_type="commercial",
                    country="Israel",
                    website="https://www.taranis.com/",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.COMMERCIAL,
                language_support=LanguageSupport(english=True, spanish=True),
                description="AI-powered crop intelligence platform",
                description_ar="منصة ذكاء المحاصيل المدعومة بالذكاء الاصطناعي",
                description_cn="AI驱动的作物智能平台",
                tags=["commercial", "precision-ag", "israel"],
            )
        )

        # 12. Bayer E.L.Y.
        self._register(
            AIModelInfo(
                model_id="bayer_ely",
                name="Bayer E.L.Y.",
                name_ar="باير إي.إل.واي",
                name_cn="Bayer E.L.Y.",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.PEST_DETECTION,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Bayer Crop Science",
                    name_ar="باير لعلوم المحاصيل",
                    name_cn="拜耳作物科学",
                    organization_type="commercial",
                    country="Germany",
                    website="https://www.bayer.com/",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.PROPRIETARY,
                language_support=LanguageSupport(english=True, spanish=True, french=True),
                description="Enterprise agricultural assistant from Bayer",
                description_ar="مساعد زراعي مؤسسي من باير",
                description_cn="来自拜耳的企业农业助手",
                tags=["commercial", "enterprise", "germany"],
            )
        )

        # 13. Corteva Carl
        self._register(
            AIModelInfo(
                model_id="corteva_carl",
                name="Corteva Carl",
                name_ar="كورتيفا كارل",
                name_cn="Corteva Carl",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.YIELD_PREDICTION,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Corteva Agriscience",
                    name_ar="كورتيفا للعلوم الزراعية",
                    name_cn="科迪华农业科技",
                    organization_type="commercial",
                    country="USA",
                    website="https://www.corteva.com/",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.PROPRIETARY,
                language_support=LanguageSupport(english=True, spanish=True),
                description="Corteva's agricultural AI assistant",
                description_ar="مساعد كورتيفا للذكاء الاصطناعي الزراعي",
                description_cn="科迪华农业AI助手",
                tags=["commercial", "enterprise", "usa"],
            )
        )

        # 14. AgriBot (Generic/Open Implementation)
        self._register(
            AIModelInfo(
                model_id="agribot",
                name="AgriBot",
                name_ar="أجري بوت",
                name_cn="AgriBot",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Open Source Community",
                    name_ar="مجتمع المصدر المفتوح",
                    name_cn="开源社区",
                    organization_type="research",
                    country="International",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True),
                description="Open source agricultural chatbot framework",
                description_ar="إطار روبوت محادثة زراعي مفتوح المصدر",
                description_cn="开源农业聊天机器人框架",
                tags=["open-source", "chatbot", "framework"],
            )
        )

        # 15. FarmVibes.AI - Microsoft
        self._register(
            AIModelInfo(
                model_id="farmvibes_ai",
                name="FarmVibes.AI",
                name_ar="فارم فايبز إيه آي",
                name_cn="FarmVibes.AI",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.YIELD_PREDICTION,
                    ModelCapability.DECISION_SUPPORT,
                    ModelCapability.CLIMATE_MODELING,
                ],
                architecture=ModelArchitecture.HYBRID,
                developer=DeveloperInfo(
                    name="Microsoft Research",
                    name_ar="أبحاث مايكروسوفت",
                    name_cn="微软研究院",
                    organization_type="commercial",
                    country="USA",
                    website="https://www.microsoft.com/research/project/farmvibes-ai/",
                ),
                github_url="https://github.com/microsoft/farmvibes-ai",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True),
                description="Microsoft's agricultural AI toolkit for precision farming",
                description_ar="مجموعة أدوات مايكروسوفت للذكاء الاصطناعي الزراعي للزراعة الدقيقة",
                description_cn="微软用于精准农业的农业AI工具包",
                tags=["microsoft", "precision-ag", "satellite", "open-source"],
            )
        )

        # Additional general agriculture models...
        self._register(
            AIModelInfo(
                model_id="nongxin",
                name="NongXin (Agricultural Heart)",
                name_ar="نونغشين",
                name_cn="农芯",
                category=AIModelCategory.GENERAL_AGRICULTURE,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Chinese Academy of Agricultural Sciences",
                    name_ar="الأكاديمية الصينية للعلوم الزراعية",
                    name_cn="中国农业科学院",
                    organization_type="government",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.GOVERNMENT,
                language_support=LanguageSupport(chinese=True),
                description="Agricultural AI from CAAS",
                description_cn="来自中国农科院的农业AI",
                tags=["llm", "government", "chinese"],
            )
        )

    # ========================================================================
    # Category 2: Breeding & Bioscience (育种与生物科学)
    # ========================================================================

    def _load_breeding_bioscience_models(self) -> None:
        """Load breeding and bioscience models."""

        # 1. PlantGPT - South China Agricultural University
        self._register(
            AIModelInfo(
                model_id="plantgpt",
                name="PlantGPT",
                name_ar="بلانت جي بي تي",
                name_cn="PlantGPT",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.GENOMICS,
                    ModelCapability.BREEDING,
                    ModelCapability.PHENOTYPE_PREDICTION,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="South China Agricultural University",
                    name_ar="جامعة جنوب الصين الزراعية",
                    name_cn="华南农业大学",
                    organization_type="academic",
                    country="China",
                ),
                url="https://www.plantgpt.icu",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Plant genomics and breeding AI assistant",
                description_ar="مساعد ذكاء اصطناعي لجينوم النبات والتربية",
                description_cn="植物基因组学和育种AI助手",
                use_cases=[
                    "Gene function analysis",
                    "Breeding recommendations",
                    "Phenotype prediction",
                ],
                tags=["genomics", "breeding", "plant-science"],
            )
        )

        # 2. SeedLLM - Yaguu National Laboratory
        self._register(
            AIModelInfo(
                model_id="seedllm",
                name="SeedLLM",
                name_ar="سيد إل إل إم",
                name_cn="SeedLLM",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.GENOMICS,
                    ModelCapability.BREEDING,
                    ModelCapability.MOLECULAR_DESIGN,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Yaguu National Laboratory (Shenzhen)",
                    name_ar="مختبر ياغو الوطني (شنتشن)",
                    name_cn="崖谷国家实验室（深圳）",
                    organization_type="government",
                    country="China",
                ),
                url="https://seedllm.org.cn/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.GOVERNMENT,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Seed genetics and breeding language model",
                description_ar="نموذج لغوي لجينات البذور والتربية",
                description_cn="种子遗传学和育种大语言模型",
                tags=["genomics", "seed", "breeding", "national-lab"],
            )
        )

        # 3. BreedingGPT - Peking University
        self._register(
            AIModelInfo(
                model_id="breedinggpt",
                name="BreedingGPT",
                name_ar="بريدنغ جي بي تي",
                name_cn="BreedingGPT",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.BREEDING,
                    ModelCapability.GENOMICS,
                    ModelCapability.PHENOTYPE_PREDICTION,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Peking University (Institute of Agricultural AI Sciences)",
                    name_ar="جامعة بكين (معهد علوم الذكاء الاصطناعي الزراعي)",
                    name_cn="北京大学（农业人工智能科学研究院）",
                    organization_type="academic",
                    country="China",
                ),
                url="http://ai4b.pku-iaas.edu.cn",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="AI for breeding optimization from Peking University",
                description_ar="ذكاء اصطناعي لتحسين التربية من جامعة بكين",
                description_cn="来自北京大学的育种优化AI",
                tags=["breeding", "genomics", "pku", "academic"],
            )
        )

        # 4. AgroNT - InstaDeep
        self._register(
            AIModelInfo(
                model_id="agront",
                name="AgroNT (Agro Nucleotide Transformer)",
                name_ar="أجرو إن تي",
                name_cn="AgroNT",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.GENOMICS,
                    ModelCapability.GENE_EDITING,
                    ModelCapability.PHENOTYPE_PREDICTION,
                ],
                architecture=ModelArchitecture.TRANSFORMER,
                developer=DeveloperInfo(
                    name="InstaDeep",
                    name_ar="إنستاديب",
                    name_cn="InstaDeep",
                    organization_type="commercial",
                    country="UK",
                    website="https://www.instadeep.com/",
                ),
                url="https://huggingface.co/InstaDeepAI/agro-nucleotide-transformer-1b",
                huggingface_url="https://huggingface.co/InstaDeepAI/agro-nucleotide-transformer-1b",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                parameter_count="1B",
                language_support=LanguageSupport(english=True),
                description="1B parameter nucleotide transformer for agricultural genomics",
                description_ar="محول نيوكليوتيد بمليار معامل للجينوم الزراعي",
                description_cn="用于农业基因组学的10亿参数核苷酸转换器",
                tags=["genomics", "transformer", "huggingface", "dna"],
            )
        )

        # 5. Evo2 - Arc Institute
        self._register(
            AIModelInfo(
                model_id="evo2",
                name="Evo2",
                name_ar="إيفو 2",
                name_cn="Evo2",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.GENOMICS,
                    ModelCapability.GENE_EDITING,
                    ModelCapability.MOLECULAR_DESIGN,
                ],
                architecture=ModelArchitecture.FOUNDATION,
                developer=DeveloperInfo(
                    name="Arc Institute",
                    name_ar="معهد آرك",
                    name_cn="Arc研究所",
                    organization_type="research",
                    country="USA",
                    website="https://arcinstitute.org/",
                ),
                url="https://arcinstitute.org/tools/evo",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True),
                description="Foundation model for biological sequence design",
                description_ar="نموذج أساسي لتصميم التسلسل الحيوي",
                description_cn="用于生物序列设计的基础模型",
                tags=["genomics", "foundation-model", "sequence-design"],
            )
        )

        # 6. PLLaMa - Plant LLaMA
        self._register(
            AIModelInfo(
                model_id="pllama",
                name="PLLaMa (Plant LLaMA)",
                name_ar="بي إل لاما",
                name_cn="PLLaMa",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.GENOMICS,
                    ModelCapability.QA,
                    ModelCapability.PHENOTYPE_PREDICTION,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Research Community",
                    name_ar="مجتمع البحث",
                    name_cn="研究社区",
                    organization_type="academic",
                    country="International",
                ),
                url="https://github.com/Xianjun-Yang/PLLaMa",
                github_url="https://github.com/Xianjun-Yang/PLLaMa",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                base_model="LLaMA",
                language_support=LanguageSupport(english=True),
                description="LLaMA-based model fine-tuned for plant biology",
                description_ar="نموذج قائم على لاما مضبوط لعلم أحياء النبات",
                description_cn="针对植物生物学微调的LLaMA模型",
                tags=["llama", "plant-biology", "open-source"],
            )
        )

        # 7. CropGPT
        self._register(
            AIModelInfo(
                model_id="cropgpt",
                name="CropGPT",
                name_ar="كروب جي بي تي",
                name_cn="CropGPT",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.GENOMICS,
                    ModelCapability.BREEDING,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Agricultural Genomics Institute (AGI)",
                    name_ar="معهد الجينوم الزراعي",
                    name_cn="农业基因组研究所",
                    organization_type="research",
                    country="China",
                ),
                status=ModelStatus.RESEARCH,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Crop genomics specialized GPT model",
                description_cn="作物基因组学专用GPT模型",
                tags=["genomics", "crop", "chinese"],
            )
        )

        # 8. GeneFormer-Agri
        self._register(
            AIModelInfo(
                model_id="geneformer_agri",
                name="GeneFormer-Agri",
                name_ar="جين فورمر زراعي",
                name_cn="GeneFormer-Agri",
                category=AIModelCategory.BREEDING_BIOSCIENCE,
                capabilities=[
                    ModelCapability.GENOMICS,
                    ModelCapability.GENE_EDITING,
                ],
                architecture=ModelArchitecture.TRANSFORMER,
                developer=DeveloperInfo(
                    name="Broad Institute (Agricultural Extension)",
                    name_ar="معهد برود (امتداد زراعي)",
                    name_cn="Broad研究所（农业扩展）",
                    organization_type="research",
                    country="USA",
                ),
                status=ModelStatus.RESEARCH,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(english=True),
                description="Gene expression transformer adapted for agricultural species",
                description_ar="محول تعبير الجينات مكيف للأنواع الزراعية",
                description_cn="适用于农业物种的基因表达转换器",
                tags=["genomics", "transformer", "gene-expression"],
            )
        )

    # ========================================================================
    # Category 3: Livestock & Veterinary (畜牧兽医)
    # ========================================================================

    def _load_livestock_veterinary_models(self) -> None:
        """Load livestock and veterinary models."""

        # 1. AI4DLLM - China Agricultural University (Dairy)
        self._register(
            AIModelInfo(
                model_id="ai4dllm",
                name="AI4DLLM (AI for Dairy)",
                name_ar="إيه آي فور دي إل إل إم",
                name_cn="AI4DLLM",
                category=AIModelCategory.LIVESTOCK_VETERINARY,
                capabilities=[
                    ModelCapability.ANIMAL_HEALTH,
                    ModelCapability.MILK_PRODUCTION,
                    ModelCapability.FEED_OPTIMIZATION,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="China Agricultural University (Dairy Science)",
                    name_ar="جامعة الصين الزراعية (علوم الألبان)",
                    name_cn="中国农业大学（奶牛科学）",
                    organization_type="academic",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="AI assistant for dairy farm management",
                description_ar="مساعد ذكاء اصطناعي لإدارة مزارع الألبان",
                description_cn="奶牛场管理AI助手",
                use_cases=[
                    "Milk production optimization",
                    "Dairy cattle health",
                    "Feed management",
                ],
                tags=["dairy", "livestock", "chinese"],
            )
        )

        # 2. VetCloud - Beijing University of Agriculture
        self._register(
            AIModelInfo(
                model_id="vetcloud",
                name="VetCloud",
                name_ar="فيت كلاود",
                name_cn="兽医云",
                category=AIModelCategory.LIVESTOCK_VETERINARY,
                capabilities=[
                    ModelCapability.VETERINARY_QA,
                    ModelCapability.ANIMAL_HEALTH,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Beijing University of Agriculture (Veterinary)",
                    name_ar="جامعة بكين للزراعة (البيطرية)",
                    name_cn="北京农学院（兽医）",
                    organization_type="academic",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True),
                description="Cloud-based veterinary consultation system",
                description_ar="نظام استشارات بيطرية قائم على السحابة",
                description_cn="基于云的兽医咨询系统",
                tags=["veterinary", "cloud", "chinese"],
            )
        )

        # 3. PigGPT - National Pig Data Center
        self._register(
            AIModelInfo(
                model_id="piggpt",
                name="PigGPT",
                name_ar="بيغ جي بي تي",
                name_cn="PigGPT",
                category=AIModelCategory.LIVESTOCK_VETERINARY,
                capabilities=[
                    ModelCapability.ANIMAL_HEALTH,
                    ModelCapability.BREEDING_MANAGEMENT,
                    ModelCapability.FEED_OPTIMIZATION,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="National Pig Data Center of China",
                    name_ar="المركز الوطني الصيني لبيانات الخنازير",
                    name_cn="国家生猪数据中心",
                    organization_type="government",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.GOVERNMENT,
                language_support=LanguageSupport(chinese=True),
                description="Specialized AI for swine industry management",
                description_ar="ذكاء اصطناعي متخصص لإدارة صناعة الخنازير",
                description_cn="生猪产业管理专用AI",
                tags=["pig", "swine", "livestock", "chinese"],
            )
        )

        # 4. VetGPT - International
        self._register(
            AIModelInfo(
                model_id="vetgpt",
                name="VetGPT",
                name_ar="فيت جي بي تي",
                name_cn="VetGPT",
                category=AIModelCategory.LIVESTOCK_VETERINARY,
                capabilities=[
                    ModelCapability.VETERINARY_QA,
                    ModelCapability.ANIMAL_HEALTH,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="VetGPT Team",
                    name_ar="فريق فيت جي بي تي",
                    name_cn="VetGPT团队",
                    organization_type="commercial",
                    country="USA",
                    website="https://www.vetgpt.com/",
                ),
                url="https://www.vetgpt.com/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.FREEMIUM,
                language_support=LanguageSupport(english=True, spanish=True),
                description="AI veterinary assistant for pet and livestock care",
                description_ar="مساعد بيطري بالذكاء الاصطناعي لرعاية الحيوانات الأليفة والماشية",
                description_cn="用于宠物和牲畜护理的AI兽医助手",
                tags=["veterinary", "pet", "livestock"],
            )
        )

        # 5. PoultryAI
        self._register(
            AIModelInfo(
                model_id="poultryai",
                name="PoultryAI",
                name_ar="بولتري إيه آي",
                name_cn="家禽AI",
                category=AIModelCategory.LIVESTOCK_VETERINARY,
                capabilities=[
                    ModelCapability.ANIMAL_HEALTH,
                    ModelCapability.FEED_OPTIMIZATION,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.HYBRID,
                developer=DeveloperInfo(
                    name="Poultry Research Institute",
                    name_ar="معهد أبحاث الدواجن",
                    name_cn="家禽研究所",
                    organization_type="research",
                    country="International",
                ),
                status=ModelStatus.RESEARCH,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(english=True, chinese=True),
                description="AI system for poultry farm optimization",
                description_ar="نظام ذكاء اصطناعي لتحسين مزارع الدواجن",
                description_cn="家禽养殖场优化AI系统",
                tags=["poultry", "chicken", "livestock"],
            )
        )

        # 6. LivestockLLM
        self._register(
            AIModelInfo(
                model_id="livestockllm",
                name="LivestockLLM",
                name_ar="لايفستوك إل إل إم",
                name_cn="畜牧LLM",
                category=AIModelCategory.LIVESTOCK_VETERINARY,
                capabilities=[
                    ModelCapability.ANIMAL_HEALTH,
                    ModelCapability.BREEDING_MANAGEMENT,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="International Livestock Research Institute (ILRI)",
                    name_ar="المعهد الدولي لأبحاث الثروة الحيوانية",
                    name_cn="国际畜牧研究所",
                    organization_type="research",
                    country="Kenya",
                    website="https://www.ilri.org/",
                ),
                status=ModelStatus.RESEARCH,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(english=True, french=True),
                description="LLM for livestock management in developing regions",
                description_ar="نموذج لغوي كبير لإدارة الثروة الحيوانية في المناطق النامية",
                description_cn="用于发展中地区畜牧管理的大语言模型",
                tags=["livestock", "developing-regions", "ilri"],
            )
        )

        # 7. AquaVet
        self._register(
            AIModelInfo(
                model_id="aquavet",
                name="AquaVet",
                name_ar="أكوا فيت",
                name_cn="水产兽医",
                category=AIModelCategory.LIVESTOCK_VETERINARY,
                capabilities=[
                    ModelCapability.AQUACULTURE,
                    ModelCapability.ANIMAL_HEALTH,
                    ModelCapability.DISEASE_DETECTION,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Ocean University of China",
                    name_ar="جامعة المحيط الصينية",
                    name_cn="中国海洋大学",
                    organization_type="academic",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="AI for aquaculture health management",
                description_ar="ذكاء اصطناعي لإدارة صحة الاستزراع المائي",
                description_cn="水产养殖健康管理AI",
                tags=["aquaculture", "fish", "veterinary"],
            )
        )

    # ========================================================================
    # Category 4: Remote Sensing & Geo (遥感地理)
    # ========================================================================

    def _load_remote_sensing_models(self) -> None:
        """Load remote sensing and geospatial models."""

        # 1. EarthGPT - Beijing Jiaotong University
        self._register(
            AIModelInfo(
                model_id="earthgpt",
                name="EarthGPT",
                name_ar="إيرث جي بي تي",
                name_cn="EarthGPT",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.LAND_USE,
                    ModelCapability.CHANGE_DETECTION,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Beijing Jiaotong University",
                    name_ar="جامعة بكين جياوتونغ",
                    name_cn="北京交通大学",
                    organization_type="academic",
                    country="China",
                ),
                url="https://github.com/wivizhang/EarthGPT",
                github_url="https://github.com/wivizhang/EarthGPT",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Multimodal model for Earth observation and geospatial analysis",
                description_ar="نموذج متعدد الوسائط لمراقبة الأرض والتحليل الجغرافي المكاني",
                description_cn="用于地球观测和地理空间分析的多模态模型",
                tags=["earth-observation", "satellite", "multimodal"],
            )
        )

        # 2. GeoGPT - River Lab
        self._register(
            AIModelInfo(
                model_id="geogpt",
                name="GeoGPT",
                name_ar="جيو جي بي تي",
                name_cn="GeoGPT",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.LAND_USE,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="River Lab (Henan University)",
                    name_ar="مختبر النهر (جامعة خنان)",
                    name_cn="河流实验室（河南大学）",
                    organization_type="academic",
                    country="China",
                ),
                url="https://geogpt.zero2x.org.cn/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Geospatial GPT for geographic information processing",
                description_ar="جي بي تي جغرافي مكاني لمعالجة المعلومات الجغرافية",
                description_cn="用于地理信息处理的地理空间GPT",
                tags=["geospatial", "gis", "chinese"],
            )
        )

        # 3. SkySense - Wuhan University
        self._register(
            AIModelInfo(
                model_id="skysense",
                name="SkySense",
                name_ar="سكاي سينس",
                name_cn="SkySense",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.NDVI_ANALYSIS,
                    ModelCapability.CHANGE_DETECTION,
                ],
                architecture=ModelArchitecture.FOUNDATION,
                developer=DeveloperInfo(
                    name="Wuhan University (Remote Sensing)",
                    name_ar="جامعة ووهان (الاستشعار عن بعد)",
                    name_cn="武汉大学（遥感）",
                    organization_type="academic",
                    country="China",
                ),
                url="https://github.com/Jack-bo1220/SkySense",
                github_url="https://github.com/Jack-bo1220/SkySense",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Foundation model for remote sensing image understanding",
                description_ar="نموذج أساسي لفهم صور الاستشعار عن بعد",
                description_cn="用于遥感图像理解的基础模型",
                tags=["remote-sensing", "foundation-model", "satellite"],
            )
        )

        # 4. GeoChat - MBZUAI
        self._register(
            AIModelInfo(
                model_id="geochat",
                name="GeoChat",
                name_ar="جيو شات",
                name_cn="GeoChat",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.QA,
                    ModelCapability.LAND_USE,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Mohamed bin Zayed University of AI (MBZUAI)",
                    name_ar="جامعة محمد بن زايد للذكاء الاصطناعي",
                    name_cn="穆罕默德·本·扎耶德人工智能大学",
                    organization_type="academic",
                    country="UAE",
                ),
                url="https://mbzuai-oryx.github.io/GeoChat/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True, arabic=True),
                description="Vision-language model for geospatial chat and analysis",
                description_ar="نموذج رؤية-لغة للمحادثة والتحليل الجغرافي المكاني",
                description_cn="用于地理空间聊天和分析的视觉语言模型",
                tags=["geospatial", "chat", "arabic", "uae"],
            )
        )

        # 5. AgroMind - Sun Yat-sen University
        self._register(
            AIModelInfo(
                model_id="agromind",
                name="AgroMind",
                name_ar="أجرو مايند",
                name_cn="AgroMind",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.NDVI_ANALYSIS,
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.YIELD_PREDICTION,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Sun Yat-sen University (Remote Sensing)",
                    name_ar="جامعة صن يات صن (الاستشعار عن بعد)",
                    name_cn="中山大学（遥感）",
                    organization_type="academic",
                    country="China",
                ),
                url="https://rssysu.github.io/AgroMind/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Agricultural remote sensing intelligence system",
                description_ar="نظام ذكاء الاستشعار عن بعد الزراعي",
                description_cn="农业遥感智能系统",
                tags=["remote-sensing", "agriculture", "ndvi"],
            )
        )

        # 6. Prithvi - NASA/IBM
        self._register(
            AIModelInfo(
                model_id="prithvi",
                name="Prithvi",
                name_ar="بريثفي",
                name_cn="Prithvi",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.LAND_USE,
                    ModelCapability.CHANGE_DETECTION,
                    ModelCapability.CLIMATE_MODELING,
                ],
                architecture=ModelArchitecture.FOUNDATION,
                developer=DeveloperInfo(
                    name="NASA & IBM",
                    name_ar="ناسا وآي بي إم",
                    name_cn="NASA与IBM",
                    organization_type="government",
                    country="USA",
                    website="https://www.ibm.com/",
                ),
                url="https://huggingface.co/ibm-nasa-geospatial",
                huggingface_url="https://huggingface.co/ibm-nasa-geospatial",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True),
                description="Geospatial foundation model from NASA-IBM collaboration",
                description_ar="نموذج أساسي جغرافي مكاني من تعاون ناسا-آي بي إم",
                description_cn="NASA-IBM合作的地理空间基础模型",
                use_cases=["Land use classification", "Climate analysis", "Flood mapping"],
                tags=["nasa", "ibm", "foundation-model", "geospatial"],
            )
        )

        # 7. ClimateGPT
        self._register(
            AIModelInfo(
                model_id="climategpt",
                name="ClimateGPT",
                name_ar="كلايميت جي بي تي",
                name_cn="ClimateGPT",
                category=AIModelCategory.CLIMATE_WEATHER,
                capabilities=[
                    ModelCapability.CLIMATE_MODELING,
                    ModelCapability.WEATHER_FORECAST,
                    ModelCapability.DISASTER_WARNING,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Erasmus AI",
                    name_ar="إيراسموس إيه آي",
                    name_cn="Erasmus AI",
                    organization_type="commercial",
                    country="International",
                    website="https://climategpt.ai/",
                ),
                url="https://climategpt.ai/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.FREEMIUM,
                language_support=LanguageSupport(english=True),
                description="AI assistant for climate science and sustainability",
                description_ar="مساعد ذكاء اصطناعي لعلوم المناخ والاستدامة",
                description_cn="气候科学和可持续发展AI助手",
                tags=["climate", "sustainability", "weather"],
            )
        )

        # 8. SatCLIP
        self._register(
            AIModelInfo(
                model_id="satclip",
                name="SatCLIP",
                name_ar="سات كليب",
                name_cn="SatCLIP",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.LAND_USE,
                ],
                architecture=ModelArchitecture.FOUNDATION,
                developer=DeveloperInfo(
                    name="Microsoft Research",
                    name_ar="أبحاث مايكروسوفت",
                    name_cn="微软研究院",
                    organization_type="commercial",
                    country="USA",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True),
                description="CLIP-style model for satellite imagery understanding",
                description_ar="نموذج بأسلوب CLIP لفهم صور الأقمار الصناعية",
                description_cn="用于卫星图像理解的CLIP风格模型",
                tags=["satellite", "clip", "foundation-model"],
            )
        )

        # 9. RSPrompter
        self._register(
            AIModelInfo(
                model_id="rsprompter",
                name="RSPrompter",
                name_ar="آر إس برومبتر",
                name_cn="RSPrompter",
                category=AIModelCategory.REMOTE_SENSING_GEO,
                capabilities=[
                    ModelCapability.SATELLITE_ANALYSIS,
                    ModelCapability.CHANGE_DETECTION,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Chinese Academy of Sciences",
                    name_ar="الأكاديمية الصينية للعلوم",
                    name_cn="中国科学院",
                    organization_type="government",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Prompt-based remote sensing image analysis",
                description_ar="تحليل صور الاستشعار عن بعد القائم على المطالبات",
                description_cn="基于提示的遥感图像分析",
                tags=["remote-sensing", "prompt-based", "chinese"],
            )
        )

    # ========================================================================
    # Category 5: Specialty (专业垂直)
    # ========================================================================

    def _load_specialty_models(self) -> None:
        """Load specialty/vertical domain models."""

        # 1. LinLong (林龙) - Forestry
        self._register(
            AIModelInfo(
                model_id="linlong",
                name="LinLong",
                name_ar="لين لونغ",
                name_cn="林龙",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.FORESTRY,
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Beijing Forestry University",
                    name_ar="جامعة بكين للغابات",
                    name_cn="北京林业大学",
                    organization_type="academic",
                    country="China",
                ),
                url="https://www.linloong.com/",
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True),
                description="AI assistant for forestry management and tree species identification",
                description_ar="مساعد ذكاء اصطناعي لإدارة الغابات وتحديد أنواع الأشجار",
                description_cn="用于林业管理和树种识别的AI助手",
                use_cases=["Tree species ID", "Forest management", "Pest detection"],
                tags=["forestry", "trees", "chinese"],
            )
        )

        # 2. LuYu (庐羽) - Tea
        self._register(
            AIModelInfo(
                model_id="luyu",
                name="LuYu",
                name_ar="لو يو",
                name_cn="庐羽",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.TEA_CULTIVATION,
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Tea Research Institute of CAAS",
                    name_ar="معهد أبحاث الشاي",
                    name_cn="中国农科院茶叶研究所",
                    organization_type="government",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True),
                description="AI for tea cultivation and processing named after the Tea Sage",
                description_ar="ذكاء اصطناعي لزراعة الشاي ومعالجته سمي على اسم حكيم الشاي",
                description_cn="以茶圣命名的茶叶种植和加工AI",
                tags=["tea", "specialty-crop", "chinese"],
            )
        )

        # 3. AgriLaw - Agricultural Law Q&A
        self._register(
            AIModelInfo(
                model_id="agrilaw",
                name="AgriLaw",
                name_ar="أجري لو",
                name_cn="农业法律",
                category=AIModelCategory.AGRICULTURAL_LAW,
                capabilities=[
                    ModelCapability.LEGAL_QA,
                    ModelCapability.QA,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="China University of Political Science and Law",
                    name_ar="جامعة الصين للعلوم السياسية والقانون",
                    name_cn="中国政法大学",
                    organization_type="academic",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True),
                description="Legal Q&A system for agricultural regulations",
                description_ar="نظام أسئلة وأجوبة قانونية للأنظمة الزراعية",
                description_cn="农业法规法律问答系统",
                tags=["legal", "regulations", "chinese"],
            )
        )

        # 4. FoodSafe
        self._register(
            AIModelInfo(
                model_id="foodsafe",
                name="FoodSafe",
                name_ar="فود سيف",
                name_cn="食品安全",
                category=AIModelCategory.FOOD_SAFETY,
                capabilities=[
                    ModelCapability.QA,
                    ModelCapability.DECISION_SUPPORT,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="China National Center for Food Safety Risk Assessment",
                    name_ar="المركز الوطني الصيني لتقييم مخاطر سلامة الغذاء",
                    name_cn="国家食品安全风险评估中心",
                    organization_type="government",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.GOVERNMENT,
                language_support=LanguageSupport(chinese=True),
                description="AI for food safety risk assessment",
                description_ar="ذكاء اصطناعي لتقييم مخاطر سلامة الغذاء",
                description_cn="食品安全风险评估AI",
                tags=["food-safety", "risk", "chinese"],
            )
        )

        # 5. CottonAI
        self._register(
            AIModelInfo(
                model_id="cottonai",
                name="CottonAI",
                name_ar="كوتن إيه آي",
                name_cn="棉花AI",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.DISEASE_DETECTION,
                    ModelCapability.YIELD_PREDICTION,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Cotton Research Institute of CAAS",
                    name_ar="معهد أبحاث القطن",
                    name_cn="中国农科院棉花研究所",
                    organization_type="government",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="Specialized AI for cotton cultivation",
                description_ar="ذكاء اصطناعي متخصص لزراعة القطن",
                description_cn="棉花种植专用AI",
                tags=["cotton", "specialty-crop", "chinese"],
            )
        )

        # 6. RiceAI
        self._register(
            AIModelInfo(
                model_id="riceai",
                name="RiceAI",
                name_ar="رايس إيه آي",
                name_cn="水稻AI",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.DISEASE_DETECTION,
                    ModelCapability.YIELD_PREDICTION,
                    ModelCapability.BREEDING,
                ],
                architecture=ModelArchitecture.HYBRID,
                developer=DeveloperInfo(
                    name="China National Rice Research Institute",
                    name_ar="معهد الصين الوطني لأبحاث الأرز",
                    name_cn="中国水稻研究所",
                    organization_type="government",
                    country="China",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(chinese=True, english=True),
                description="AI for rice breeding and cultivation",
                description_ar="ذكاء اصطناعي لتربية الأرز وزراعته",
                description_cn="用于水稻育种和栽培的AI",
                tags=["rice", "breeding", "chinese"],
            )
        )

        # 7. VineAI
        self._register(
            AIModelInfo(
                model_id="vineai",
                name="VineAI",
                name_ar="فاين إيه آي",
                name_cn="葡萄AI",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.DISEASE_DETECTION,
                    ModelCapability.GROWTH_STAGE,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Viticulture Research Community",
                    name_ar="مجتمع أبحاث زراعة الكروم",
                    name_cn="葡萄种植研究社区",
                    organization_type="research",
                    country="International",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.OPEN_SOURCE,
                language_support=LanguageSupport(english=True, french=True, spanish=True),
                description="AI for vineyard management and wine grape cultivation",
                description_ar="ذكاء اصطناعي لإدارة الكروم وزراعة عنب النبيذ",
                description_cn="用于葡萄园管理和酿酒葡萄种植的AI",
                tags=["vine", "grape", "wine", "viticulture"],
            )
        )

        # 8. DatePalmAI
        self._register(
            AIModelInfo(
                model_id="datepalmAI",
                name="DatePalmAI",
                name_ar="نخيل إيه آي",
                name_cn="椰枣AI",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.PEST_DETECTION,
                    ModelCapability.DISEASE_DETECTION,
                    ModelCapability.YIELD_PREDICTION,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Date Palm Research Centers (MENA)",
                    name_ar="مراكز أبحاث النخيل (الشرق الأوسط)",
                    name_cn="椰枣研究中心（中东北非）",
                    organization_type="research",
                    country="UAE",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(arabic=True, english=True),
                description="AI for date palm cultivation and Red Palm Weevil detection",
                description_ar="ذكاء اصطناعي لزراعة النخيل وكشف سوسة النخيل الحمراء",
                description_cn="用于椰枣种植和红棕象甲检测的AI",
                use_cases=["RPW detection", "Irrigation optimization", "Yield estimation"],
                use_cases_ar=["كشف سوسة النخيل الحمراء", "تحسين الري", "تقدير الإنتاج"],
                tags=["date-palm", "rpw", "arabic", "mena"],
            )
        )

        # 9. OliveAI
        self._register(
            AIModelInfo(
                model_id="oliveai",
                name="OliveAI",
                name_ar="أوليف إيه آي",
                name_cn="橄榄AI",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.DISEASE_DETECTION,
                    ModelCapability.YIELD_PREDICTION,
                ],
                architecture=ModelArchitecture.VLM,
                developer=DeveloperInfo(
                    name="Mediterranean Agricultural Research",
                    name_ar="أبحاث زراعة البحر المتوسط",
                    name_cn="地中海农业研究",
                    organization_type="research",
                    country="Spain",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(spanish=True, english=True, arabic=True),
                description="AI for olive cultivation and oil production optimization",
                description_ar="ذكاء اصطناعي لزراعة الزيتون وتحسين إنتاج الزيت",
                description_cn="用于橄榄种植和油生产优化的AI",
                tags=["olive", "mediterranean", "oil"],
            )
        )

        # 10. SoybeanGPT
        self._register(
            AIModelInfo(
                model_id="soybeangpt",
                name="SoybeanGPT",
                name_ar="صويا جي بي تي",
                name_cn="大豆GPT",
                category=AIModelCategory.SPECIALTY,
                capabilities=[
                    ModelCapability.CROP_MONITORING,
                    ModelCapability.YIELD_PREDICTION,
                    ModelCapability.BREEDING,
                ],
                architecture=ModelArchitecture.LLM,
                developer=DeveloperInfo(
                    name="Soybean Research Institute",
                    name_ar="معهد أبحاث فول الصويا",
                    name_cn="大豆研究所",
                    organization_type="research",
                    country="Brazil",
                ),
                status=ModelStatus.ACTIVE,
                license=ModelLicense.ACADEMIC,
                language_support=LanguageSupport(english=True, spanish=True, chinese=True),
                description="AI for soybean cultivation and breeding",
                description_ar="ذكاء اصطناعي لزراعة فول الصويا وتربيته",
                description_cn="用于大豆种植和育种的AI",
                tags=["soybean", "breeding", "brazil"],
            )
        )

    # ========================================================================
    # Registry Operations
    # ========================================================================

    def _register(self, model: AIModelInfo) -> None:
        """Register a model in the registry."""
        self._models[model.model_id] = model

    def get(self, model_id: str) -> AIModelInfo | None:
        """Get a model by ID."""
        return self._models.get(model_id)

    def get_all(self) -> list[AIModelInfo]:
        """Get all registered models."""
        return list(self._models.values())

    def count(self) -> int:
        """Get the total number of registered models."""
        return len(self._models)

    def __iter__(self) -> Iterator[AIModelInfo]:
        """Iterate over all models."""
        return iter(self._models.values())

    def __contains__(self, model_id: str) -> bool:
        """Check if a model exists."""
        return model_id in self._models

    def __len__(self) -> int:
        """Get the number of models."""
        return len(self._models)

    # ========================================================================
    # Discovery & Search
    # ========================================================================

    def discover_by_category(self, category: AIModelCategory) -> ModelDiscoveryResult:
        """Discover models by category."""
        import time

        start = time.time()

        models = [m for m in self._models.values() if m.category == category]

        return ModelDiscoveryResult(
            models=models,
            total_count=len(models),
            filter_criteria={"category": category.value},
            search_duration_ms=(time.time() - start) * 1000,
        )

    def discover_by_capability(self, capability: ModelCapability) -> ModelDiscoveryResult:
        """Discover models by capability."""
        import time

        start = time.time()

        models = [m for m in self._models.values() if capability in m.capabilities]

        return ModelDiscoveryResult(
            models=models,
            total_count=len(models),
            filter_criteria={"capability": capability.value},
            search_duration_ms=(time.time() - start) * 1000,
        )

    def discover_by_language(self, language: str) -> ModelDiscoveryResult:
        """Discover models by supported language."""
        import time

        start = time.time()

        models = [m for m in self._models.values() if m.supports_language(language)]

        return ModelDiscoveryResult(
            models=models,
            total_count=len(models),
            filter_criteria={"language": language},
            search_duration_ms=(time.time() - start) * 1000,
        )

    def discover_available(self) -> ModelDiscoveryResult:
        """Discover all currently available models."""
        import time

        start = time.time()

        models = [m for m in self._models.values() if m.is_available()]

        return ModelDiscoveryResult(
            models=models,
            total_count=len(models),
            filter_criteria={"status": "available"},
            search_duration_ms=(time.time() - start) * 1000,
        )

    def discover_open_source(self) -> ModelDiscoveryResult:
        """Discover open source models."""
        import time

        start = time.time()

        models = [m for m in self._models.values() if m.license == ModelLicense.OPEN_SOURCE]

        return ModelDiscoveryResult(
            models=models,
            total_count=len(models),
            filter_criteria={"license": "open_source"},
            search_duration_ms=(time.time() - start) * 1000,
        )

    def search(
        self,
        query: str | None = None,
        category: AIModelCategory | None = None,
        capabilities: list[ModelCapability] | None = None,
        language: str | None = None,
        status: ModelStatus | None = None,
        license_type: ModelLicense | None = None,
        country: str | None = None,
    ) -> ModelDiscoveryResult:
        """Advanced search with multiple filters."""
        import time

        start = time.time()

        models = list(self._models.values())

        # Apply filters
        if category:
            models = [m for m in models if m.category == category]

        if capabilities:
            models = [m for m in models if all(cap in m.capabilities for cap in capabilities)]

        if language:
            models = [m for m in models if m.supports_language(language)]

        if status:
            models = [m for m in models if m.status == status]

        if license_type:
            models = [m for m in models if m.license == license_type]

        if country and any(m.developer for m in models):
            models = [m for m in models if m.developer and m.developer.country.lower() == country.lower()]

        if query:
            query_lower = query.lower()
            models = [
                m
                for m in models
                if (
                    query_lower in m.name.lower()
                    or query_lower in m.description.lower()
                    or query_lower in m.name_cn.lower()
                    or query_lower in m.name_ar.lower()
                    or any(query_lower in tag for tag in m.tags)
                )
            ]

        filter_criteria = {
            k: v
            for k, v in {
                "query": query,
                "category": category.value if category else None,
                "capabilities": [c.value for c in capabilities] if capabilities else None,
                "language": language,
                "status": status.value if status else None,
                "license": license_type.value if license_type else None,
                "country": country,
            }.items()
            if v is not None
        }

        return ModelDiscoveryResult(
            models=models,
            total_count=len(models),
            filter_criteria=filter_criteria,
            search_duration_ms=(time.time() - start) * 1000,
        )

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics."""
        models = list(self._models.values())

        # Count by category
        by_category = {}
        for cat in AIModelCategory:
            count = sum(1 for m in models if m.category == cat)
            if count > 0:
                by_category[cat.value] = count

        # Count by status
        by_status = {}
        for status in ModelStatus:
            count = sum(1 for m in models if m.status == status)
            if count > 0:
                by_status[status.value] = count

        # Count by license
        by_license = {}
        for lic in ModelLicense:
            count = sum(1 for m in models if m.license == lic)
            if count > 0:
                by_license[lic.value] = count

        # Count by country
        by_country: dict[str, int] = {}
        for m in models:
            if m.developer:
                country = m.developer.country
                by_country[country] = by_country.get(country, 0) + 1

        # Language support
        arabic_support = sum(1 for m in models if m.supports_language("ar"))
        chinese_support = sum(1 for m in models if m.supports_language("zh"))
        english_support = sum(1 for m in models if m.supports_language("en"))

        return {
            "total_models": len(models),
            "by_category": by_category,
            "by_status": by_status,
            "by_license": by_license,
            "by_country": by_country,
            "language_support": {
                "arabic": arabic_support,
                "chinese": chinese_support,
                "english": english_support,
            },
            "open_source_count": sum(1 for m in models if m.license == ModelLicense.OPEN_SOURCE),
            "available_count": sum(1 for m in models if m.is_available()),
        }


# Singleton instance
_registry: AgriculturalAIRegistry | None = None


def get_registry() -> AgriculturalAIRegistry:
    """Get the singleton registry instance."""
    global _registry
    if _registry is None:
        _registry = AgriculturalAIRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the singleton registry (mainly for testing)."""
    global _registry
    _registry = None

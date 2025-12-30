"""
سجل الوكلاء - Agent Registry
Agent Registration and Discovery System

يدير تسجيل واكتشاف الوكلاء المتاحين
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Type
from enum import Enum
import inspect


class AgentCapability(Enum):
    """قدرات الوكلاء"""
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    EXECUTE_CODE = "execute_code"
    WEB_SEARCH = "web_search"
    WEB_FETCH = "web_fetch"
    DATABASE_ACCESS = "database_access"
    API_CALLS = "api_calls"
    IMAGE_ANALYSIS = "image_analysis"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


@dataclass
class AgentDefinition:
    """تعريف وكيل"""
    name: str
    description: str
    description_ar: str
    agent_class: Type
    capabilities: list[AgentCapability]
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    tools: list[dict] = field(default_factory=list)
    system_prompt: str = ""
    examples: list[dict] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    priority: int = 0  # أولوية الاختيار عند التطابق

    def matches_request(self, request: str, required_capabilities: list[AgentCapability] = None) -> float:
        """حساب مدى تطابق الوكيل مع الطلب"""
        score = 0.0

        # تطابق الكلمات المفتاحية
        request_lower = request.lower()
        for tag in self.tags:
            if tag.lower() in request_lower:
                score += 0.2

        # تطابق القدرات
        if required_capabilities:
            matched = set(self.capabilities) & set(required_capabilities)
            score += len(matched) / len(required_capabilities) * 0.5

        # إضافة الأولوية
        score += self.priority * 0.1

        return min(score, 1.0)


class AgentRegistry:
    """
    سجل مركزي للوكلاء

    الميزات:
    - تسجيل وكلاء جدد
    - اكتشاف الوكيل المناسب
    - إدارة التبعيات
    - التحقق من القدرات
    """

    _instance = None
    _agents: dict[str, AgentDefinition] = {}

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._agents = {}
        return cls._instance

    @classmethod
    def register(
        cls,
        name: str,
        description: str,
        description_ar: str,
        capabilities: list[AgentCapability],
        **kwargs
    ) -> Callable:
        """
        Decorator لتسجيل وكيل

        الاستخدام:
        @AgentRegistry.register(
            name="code-writer",
            description="Writes clean code",
            description_ar="يكتب كود نظيف",
            capabilities=[AgentCapability.CODE_GENERATION]
        )
        class CodeWriterAgent:
            ...
        """
        def decorator(agent_class: Type) -> Type:
            definition = AgentDefinition(
                name=name,
                description=description,
                description_ar=description_ar,
                agent_class=agent_class,
                capabilities=capabilities,
                **kwargs
            )
            cls._agents[name] = definition
            return agent_class

        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[AgentDefinition]:
        """الحصول على تعريف وكيل"""
        return cls._agents.get(name)

    @classmethod
    def get_all(cls) -> dict[str, AgentDefinition]:
        """الحصول على جميع الوكلاء"""
        return cls._agents.copy()

    @classmethod
    def find_best_agent(
        cls,
        request: str,
        required_capabilities: list[AgentCapability] = None
    ) -> Optional[AgentDefinition]:
        """
        البحث عن أفضل وكيل للطلب
        """
        best_agent = None
        best_score = 0.0

        for agent in cls._agents.values():
            score = agent.matches_request(request, required_capabilities)
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent

    @classmethod
    def find_agents_by_capability(
        cls,
        capability: AgentCapability
    ) -> list[AgentDefinition]:
        """البحث عن وكلاء بقدرة معينة"""
        return [
            agent for agent in cls._agents.values()
            if capability in agent.capabilities
        ]

    @classmethod
    def list_agents(cls) -> list[dict]:
        """قائمة الوكلاء المتاحة"""
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "description_ar": agent.description_ar,
                "capabilities": [c.value for c in agent.capabilities],
                "tags": agent.tags
            }
            for agent in cls._agents.values()
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# تسجيل الوكلاء الأساسية
# ═══════════════════════════════════════════════════════════════════════════════

@AgentRegistry.register(
    name="general-purpose",
    description="General purpose agent for various tasks",
    description_ar="وكيل متعدد الأغراض للمهام المختلفة",
    capabilities=[
        AgentCapability.READ_FILES,
        AgentCapability.WRITE_FILES,
        AgentCapability.CODE_GENERATION,
    ],
    tags=["general", "عام", "multi-purpose"],
    priority=0,
    system_prompt="""
    أنت وكيل متعدد الأغراض. قم بتنفيذ المهمة المطلوبة بدقة وكفاءة.
    """
)
class GeneralPurposeAgent:
    """وكيل متعدد الأغراض"""
    pass


@AgentRegistry.register(
    name="code-writer",
    description="Expert code writer following best practices",
    description_ar="مطور خبير يكتب كود نظيف",
    capabilities=[
        AgentCapability.CODE_GENERATION,
        AgentCapability.READ_FILES,
        AgentCapability.WRITE_FILES,
    ],
    tags=["code", "write", "develop", "كود", "برمجة", "تطوير"],
    priority=2,
    system_prompt="""
    أنت مطور برمجيات خبير. اكتب كود نظيف وموثق يتبع أفضل الممارسات.
    - استخدم أسماء واضحة ومعبرة
    - أضف تعليقات توضيحية
    - اتبع مبادئ SOLID
    - تأكد من معالجة الأخطاء
    """
)
class CodeWriterAgent:
    """وكيل كتابة الكود"""
    pass


@AgentRegistry.register(
    name="code-reviewer",
    description="Expert code reviewer for quality assurance",
    description_ar="مراجع كود خبير لضمان الجودة",
    capabilities=[
        AgentCapability.CODE_REVIEW,
        AgentCapability.READ_FILES,
    ],
    tags=["review", "quality", "مراجعة", "جودة", "security", "أمان"],
    priority=2,
    system_prompt="""
    أنت مراجع كود خبير. راجع الكود وأعط ملاحظات بناءة.
    - ابحث عن الأخطاء المنطقية
    - تحقق من الأمان
    - اقترح تحسينات الأداء
    - تأكد من اتباع أفضل الممارسات
    """
)
class CodeReviewerAgent:
    """وكيل مراجعة الكود"""
    pass


@AgentRegistry.register(
    name="test-writer",
    description="Expert test writer for comprehensive coverage",
    description_ar="كاتب اختبارات خبير لتغطية شاملة",
    capabilities=[
        AgentCapability.TESTING,
        AgentCapability.CODE_GENERATION,
        AgentCapability.READ_FILES,
        AgentCapability.WRITE_FILES,
    ],
    tags=["test", "testing", "unit", "اختبار", "فحص"],
    priority=2,
    system_prompt="""
    أنت خبير في كتابة الاختبارات. اكتب اختبارات شاملة وموثوقة.
    - غطي جميع الحالات العادية
    - اختبر الحالات الحدية
    - استخدم mocks عند الحاجة
    - تأكد من قابلية الصيانة
    """
)
class TestWriterAgent:
    """وكيل كتابة الاختبارات"""
    pass


@AgentRegistry.register(
    name="explorer",
    description="Fast codebase explorer and analyzer",
    description_ar="مستكشف سريع لقواعد الكود",
    capabilities=[
        AgentCapability.READ_FILES,
    ],
    tags=["explore", "search", "find", "استكشاف", "بحث"],
    priority=1,
    system_prompt="""
    أنت مستكشف أكواد سريع. ابحث وحلل الكود بكفاءة.
    - اعثر على الملفات المطلوبة
    - افهم بنية المشروع
    - لخص النتائج بوضوح
    """
)
class ExplorerAgent:
    """وكيل استكشاف الكود"""
    pass


@AgentRegistry.register(
    name="documentation",
    description="Professional documentation writer",
    description_ar="كاتب توثيق محترف",
    capabilities=[
        AgentCapability.DOCUMENTATION,
        AgentCapability.READ_FILES,
        AgentCapability.WRITE_FILES,
    ],
    tags=["docs", "documentation", "readme", "توثيق", "شرح"],
    priority=1,
    system_prompt="""
    أنت كاتب توثيق محترف. اكتب توثيقاً واضحاً ومفيداً.
    - استخدم لغة بسيطة ومباشرة
    - أضف أمثلة عملية
    - نظم المحتوى بشكل منطقي
    - اشرح المفاهيم الصعبة
    """
)
class DocumentationAgent:
    """وكيل كتابة التوثيق"""
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# مثال الاستخدام
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """مثال على استخدام سجل الوكلاء"""

    registry = AgentRegistry()

    # عرض الوكلاء المتاحة
    print("🤖 الوكلاء المتاحة:")
    for agent in registry.list_agents():
        print(f"  - {agent['name']}: {agent['description_ar']}")

    print("\n" + "="*50)

    # البحث عن أفضل وكيل لطلب
    requests = [
        "اكتب دالة لحساب المتوسط",
        "راجع هذا الكود وأعطني ملاحظات",
        "اكتب اختبارات للوحدة",
        "ابحث عن ملفات التكوين",
        "اكتب توثيقاً للـ API",
    ]

    print("🔍 اختيار الوكيل المناسب:")
    for request in requests:
        best = registry.find_best_agent(request)
        print(f"  '{request[:30]}...' → {best.name if best else 'لا يوجد'}")

    print("\n" + "="*50)

    # البحث بالقدرات
    print("📋 وكلاء بقدرة كتابة الكود:")
    code_agents = registry.find_agents_by_capability(AgentCapability.CODE_GENERATION)
    for agent in code_agents:
        print(f"  - {agent.name}")


if __name__ == "__main__":
    main()

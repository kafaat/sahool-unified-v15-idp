"""
نظام الوكلاء المتعددين - الوكيل المركزي (Orchestrator)
Multi-Agent System - Central Orchestrator

هذا المثال يوضح كيفية بناء نظام وكلاء مشابه لـ Claude Code
"""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from datetime import datetime
import anthropic


# ═══════════════════════════════════════════════════════════════════════════════
# 1. تعريف أنواع الوكلاء | Agent Types Definition
# ═══════════════════════════════════════════════════════════════════════════════

class AgentType(Enum):
    """أنواع الوكلاء المتاحة"""
    GENERAL_PURPOSE = "general-purpose"
    CODE_WRITER = "code-writer"
    CODE_REVIEWER = "code-reviewer"
    TEST_WRITER = "test-writer"
    DOCUMENTATION = "documentation"
    EXPLORER = "explorer"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. نماذج البيانات | Data Models
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Task:
    """مهمة يتم تنفيذها بواسطة وكيل"""
    id: str
    description: str
    prompt: str
    agent_type: AgentType
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AgentResult:
    """نتيجة تنفيذ وكيل"""
    task_id: str
    success: bool
    output: str
    error: Optional[str] = None
    tokens_used: int = 0
    execution_time: float = 0.0


@dataclass
class OrchestratorState:
    """حالة الـ Orchestrator"""
    tasks: dict[str, Task] = field(default_factory=dict)
    results: dict[str, AgentResult] = field(default_factory=dict)
    conversation_history: list[dict] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. الوكيل الفرعي | Sub-Agent
# ═══════════════════════════════════════════════════════════════════════════════

class SubAgent:
    """
    وكيل فرعي لتنفيذ مهمة محددة
    - Stateless: لا يحتفظ بحالة بين الاستدعاءات
    - Isolated: معزول عن الوكلاء الآخرين
    - Single Response: يعطي رد واحد فقط
    """

    def __init__(
        self,
        client: anthropic.Anthropic,
        agent_type: AgentType,
        model: str = "claude-sonnet-4-20250514",
        tools: list[dict] = None
    ):
        self.client = client
        self.agent_type = agent_type
        self.model = model
        self.tools = tools or []
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """الحصول على System Prompt حسب نوع الوكيل"""
        prompts = {
            AgentType.GENERAL_PURPOSE: """
                أنت وكيل متعدد الأغراض. قم بتنفيذ المهمة المطلوبة بدقة.
                - اقرأ التعليمات بعناية
                - نفذ المطلوب فقط
                - أعط نتيجة واضحة ومختصرة
            """,
            AgentType.CODE_WRITER: """
                أنت مطور برمجيات خبير. اكتب كود نظيف وموثق.
                - اتبع أفضل الممارسات
                - أضف تعليقات توضيحية
                - تأكد من عدم وجود أخطاء
            """,
            AgentType.CODE_REVIEWER: """
                أنت مراجع كود خبير. راجع الكود وأعط ملاحظات.
                - ابحث عن الأخطاء والمشاكل
                - اقترح تحسينات
                - تحقق من الأمان
            """,
            AgentType.TEST_WRITER: """
                أنت خبير في كتابة الاختبارات. اكتب اختبارات شاملة.
                - غطي جميع الحالات
                - اختبر الحالات الحدية
                - استخدم mocks عند الحاجة
            """,
            AgentType.DOCUMENTATION: """
                أنت كاتب توثيق محترف. اكتب توثيقاً واضحاً.
                - استخدم لغة بسيطة
                - أضف أمثلة
                - نظم المحتوى بشكل منطقي
            """,
            AgentType.EXPLORER: """
                أنت مستكشف أكواد. ابحث وحلل الكود.
                - اعثر على الملفات المطلوبة
                - افهم البنية
                - لخص النتائج
            """,
        }
        return prompts.get(self.agent_type, prompts[AgentType.GENERAL_PURPOSE])

    async def execute(self, task: Task) -> AgentResult:
        """تنفيذ المهمة"""
        start_time = asyncio.get_event_loop().time()

        try:
            # استدعاء Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=[{"role": "user", "content": task.prompt}],
                tools=self.tools if self.tools else None,
            )

            # استخراج النتيجة
            output = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    output += block.text

            execution_time = asyncio.get_event_loop().time() - start_time

            return AgentResult(
                task_id=task.id,
                success=True,
                output=output,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                execution_time=execution_time
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                success=False,
                output="",
                error=str(e),
                execution_time=asyncio.get_event_loop().time() - start_time
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. الوكيل المركزي | Orchestrator
# ═══════════════════════════════════════════════════════════════════════════════

class Orchestrator:
    """
    الوكيل المركزي لإدارة الوكلاء الفرعيين

    المسؤوليات:
    1. تحليل طلب المستخدم
    2. تقسيم العمل إلى مهام
    3. توزيع المهام على الوكلاء
    4. تجميع النتائج
    5. التكامل والرد النهائي
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_parallel_agents: int = 5
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_parallel_agents = max_parallel_agents
        self.state = OrchestratorState()
        self.agents: dict[AgentType, SubAgent] = {}

        # إنشاء الوكلاء
        self._initialize_agents()

    def _initialize_agents(self):
        """إنشاء جميع أنواع الوكلاء"""
        for agent_type in AgentType:
            self.agents[agent_type] = SubAgent(
                client=self.client,
                agent_type=agent_type,
                model=self.model
            )

    async def analyze_request(self, user_request: str) -> list[Task]:
        """
        تحليل طلب المستخدم وتقسيمه إلى مهام
        """
        analysis_prompt = f"""
        حلل الطلب التالي وقسمه إلى مهام منفصلة:

        الطلب: {user_request}

        أعد قائمة JSON بالمهام بالتنسيق التالي:
        {{
            "tasks": [
                {{
                    "id": "task_1",
                    "description": "وصف المهمة",
                    "prompt": "التعليمات التفصيلية للوكيل",
                    "agent_type": "code-writer|code-reviewer|test-writer|documentation|explorer|general-purpose",
                    "dependencies": ["task_id"] // المهام التي يجب أن تكتمل أولاً
                }}
            ],
            "execution_strategy": "parallel|sequential|mixed"
        }}
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        # استخراج JSON من الرد
        response_text = response.content[0].text

        # تحليل JSON (مع معالجة الأخطاء)
        try:
            # البحث عن JSON في الرد
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
                tasks = []
                for t in data.get("tasks", []):
                    task = Task(
                        id=t["id"],
                        description=t["description"],
                        prompt=t["prompt"],
                        agent_type=AgentType(t["agent_type"]),
                        dependencies=t.get("dependencies", [])
                    )
                    tasks.append(task)
                    self.state.tasks[task.id] = task
                return tasks
        except (json.JSONDecodeError, KeyError) as e:
            # إذا فشل التحليل، أنشئ مهمة واحدة
            task = Task(
                id="task_1",
                description="تنفيذ الطلب",
                prompt=user_request,
                agent_type=AgentType.GENERAL_PURPOSE
            )
            self.state.tasks[task.id] = task
            return [task]

        return []

    def _get_ready_tasks(self, tasks: list[Task]) -> list[Task]:
        """الحصول على المهام الجاهزة للتنفيذ (بدون تبعيات معلقة)"""
        ready = []
        for task in tasks:
            if task.status != "pending":
                continue

            # تحقق من اكتمال التبعيات
            dependencies_met = all(
                self.state.tasks.get(dep_id, Task(id="", description="", prompt="", agent_type=AgentType.GENERAL_PURPOSE)).status == "completed"
                for dep_id in task.dependencies
            )

            if dependencies_met:
                ready.append(task)

        return ready[:self.max_parallel_agents]

    async def execute_tasks(self, tasks: list[Task]) -> list[AgentResult]:
        """تنفيذ المهام بالتوازي"""
        results = []

        while any(t.status in ["pending", "running"] for t in tasks):
            # الحصول على المهام الجاهزة
            ready_tasks = self._get_ready_tasks(tasks)

            if not ready_tasks:
                await asyncio.sleep(0.1)
                continue

            # تنفيذ المهام بالتوازي
            async def run_task(task: Task) -> AgentResult:
                task.status = "running"
                task.started_at = datetime.now()

                agent = self.agents[task.agent_type]
                result = await agent.execute(task)

                task.status = "completed" if result.success else "failed"
                task.completed_at = datetime.now()
                task.result = result.output
                task.error = result.error

                self.state.results[task.id] = result
                return result

            # تشغيل المهام الجاهزة بالتوازي
            batch_results = await asyncio.gather(
                *[run_task(task) for task in ready_tasks]
            )
            results.extend(batch_results)

        return results

    async def integrate_results(self, results: list[AgentResult]) -> str:
        """تجميع وتكامل النتائج"""
        # تجميع كل النتائج
        results_summary = "\n\n".join([
            f"## نتيجة المهمة {r.task_id}:\n{r.output}"
            for r in results if r.success
        ])

        errors_summary = "\n".join([
            f"- خطأ في {r.task_id}: {r.error}"
            for r in results if not r.success
        ])

        # طلب من Claude تلخيص وتكامل النتائج
        integration_prompt = f"""
        قم بتجميع وتلخيص النتائج التالية في رد متماسك للمستخدم:

        النتائج:
        {results_summary}

        {"الأخطاء:" + errors_summary if errors_summary else ""}

        أعط ملخصاً واضحاً ومنظماً.
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": integration_prompt}]
        )

        return response.content[0].text

    async def process_request(self, user_request: str) -> str:
        """
        معالجة طلب المستخدم الكامل

        الخطوات:
        1. تحليل الطلب
        2. تقسيم إلى مهام
        3. تنفيذ المهام
        4. تجميع النتائج
        5. إرجاع الرد النهائي
        """
        print(f"📥 استلام الطلب: {user_request[:50]}...")

        # 1. تحليل وتقسيم
        print("🔍 تحليل الطلب...")
        tasks = await self.analyze_request(user_request)
        print(f"📋 تم تحديد {len(tasks)} مهمة")

        # 2. تنفيذ المهام
        print("🚀 بدء التنفيذ...")
        results = await self.execute_tasks(tasks)

        successful = sum(1 for r in results if r.success)
        print(f"✅ اكتمل {successful}/{len(results)} مهمة")

        # 3. تجميع النتائج
        print("🔄 تجميع النتائج...")
        final_response = await self.integrate_results(results)

        # 4. حفظ في التاريخ
        self.state.conversation_history.append({
            "role": "user",
            "content": user_request
        })
        self.state.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })

        print("✨ اكتمل!")
        return final_response


# ═══════════════════════════════════════════════════════════════════════════════
# 5. مثال الاستخدام | Usage Example
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """مثال على استخدام النظام"""

    # إنشاء Orchestrator
    orchestrator = Orchestrator(
        api_key="your-api-key",
        max_parallel_agents=5
    )

    # طلب المستخدم
    user_request = """
    أريد إنشاء نظام تسجيل دخول:
    1. إنشاء نموذج المستخدم
    2. إنشاء API للتسجيل
    3. كتابة الاختبارات
    4. كتابة التوثيق
    """

    # معالجة الطلب
    response = await orchestrator.process_request(user_request)

    print("\n" + "="*50)
    print("الرد النهائي:")
    print("="*50)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())

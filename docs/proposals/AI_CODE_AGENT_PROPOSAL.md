# مقترح وكيل الذكاء الاصطناعي لإصلاح وتنفيذ الأكواد

# AI Code Agent Proposal for SAHOOL Platform

**التاريخ**: يناير 2026
**الإصدار**: 1.0.0
**المؤلف**: AI Architecture Team
**الحالة**: مقترح للمراجعة

---

## 1. ملخص تنفيذي / Executive Summary

يقدم هذا المقترح تصميم وكيل ذكاء اصطناعي متخصص لإصلاح وتنفيذ الأكواد داخل منصة سهول، يتبع أحدث الممارسات في تصميم وكلاء الذكاء الاصطناعي وفقاً لإطار عمل Claude Agent SDK ومعايير A2A Protocol.

---

## 2. مراجعة الهيكل الحالي / Current Architecture Review

### 2.1 هيكل الوكلاء الحالي

المشروع يتضمن بنية تحتية متقدمة للوكلاء تشمل:

```
apps/services/
├── ai-agents-core/          # النواة الأساسية للوكلاء
│   └── src/agents/
│       ├── base_agent.py    # الفئة الأساسية (5 أنواع وكلاء)
│       ├── coordinator/     # منسق الوكلاء
│       ├── specialist/      # الوكلاء المتخصصين
│       ├── edge/            # وكلاء الحافة
│       └── learning/        # وكلاء التعلم
├── ai-advisor/              # خدمة الاستشارات
└── agent-registry/          # سجل الوكلاء
```

### 2.2 أنواع الوكلاء المطبقة (base_agent.py)

| النوع           | الوصف                       | الاستخدام      |
| --------------- | --------------------------- | -------------- |
| `SIMPLE_REFLEX` | إذا كان الشرط → نفذ الإجراء | ردود فعل سريعة |
| `MODEL_BASED`   | نموذج داخلي للبيئة          | تتبع الحالة    |
| `GOAL_BASED`    | قرارات بناءً على الأهداف    | تخطيط          |
| `UTILITY_BASED` | اختيار أفضل النتائج         | تحسين          |
| `LEARNING`      | يتعلم من التجربة            | تحسين مستمر    |

### 2.3 طبقات الوكلاء (Agent Layers)

```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING LAYER                            │
│  (Model Updater, Feedback Learner, Knowledge Miner)         │
├─────────────────────────────────────────────────────────────┤
│                   COORDINATOR LAYER                          │
│  (Master Coordinator - حل النزاعات وتوزيع الموارد)          │
├─────────────────────────────────────────────────────────────┤
│                   SPECIALIST LAYER                           │
│  (Disease Expert, Yield Predictor, Irrigation Advisor...)   │
├─────────────────────────────────────────────────────────────┤
│                      EDGE LAYER                              │
│  (Mobile Agent, IoT Agent, Drone Agent) - < 100ms           │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 نقاط القوة في التصميم الحالي

✅ **بروتوكول A2A متكامل** - تعريفات موحدة في `governance/agents.yaml`
✅ **نظام تقييم شامل** - `tests/evaluation/evaluator.py` مع:

- تحليل التشابه الدلالي (Semantic Similarity)
- فحص السلامة (Safety Checker)
- تقييم زمن الاستجابة (Latency Evaluation)
  ✅ **بروتوكول MCP** - تكامل مع Model Context Protocol
  ✅ **نظام حل النزاعات** - في Master Coordinator
  ✅ **دعم ثنائي اللغة** - عربي/إنجليزي

### 2.5 الفجوات المحددة

⚠️ **لا يوجد وكيل متخصص لإصلاح/تنفيذ الكود**
⚠️ **محدودية التكامل مع أدوات التطوير (IDE, Git)**
⚠️ **غياب آلية تنفيذ آمنة للكود (Sandboxing)**
⚠️ **نقص في آليات التحقق والاختبار التلقائي**

---

## 3. مقترح وكيل إصلاح الكود / Code Fix Agent Proposal

### 3.1 نظرة عامة

```
┌─────────────────────────────────────────────────────────────────┐
│                    CODE FIX AGENT                                │
│                 وكيل إصلاح وتنفيذ الكود                          │
├─────────────────────────────────────────────────────────────────┤
│  Type: UTILITY_BASED + LEARNING                                 │
│  Layer: SPECIALIST                                              │
│  Response Time: < 5s for analysis, < 30s for fixes              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 القدرات الأساسية (Capabilities)

```yaml
code-fix-agent:
  name: "Code Fix Agent"
  name_ar: "وكيل إصلاح الكود"
  version: "1.0.0"
  category: intelligence

  capabilities:
    - name: "analyze_code"
      description: "تحليل الكود واكتشاف المشاكل"
      input_schema:
        type: object
        required: ["code_snippet", "language"]
        properties:
          code_snippet: { type: string }
          language: { type: string, enum: ["python", "typescript", "dart"] }
          file_path: { type: string }
          context: { type: object }
      output_schema:
        type: object
        properties:
          issues: { type: array }
          severity: { type: string }
          suggestions: { type: array }

    - name: "fix_code"
      description: "إصلاح الكود تلقائياً"
      input_schema:
        type: object
        required: ["code_snippet", "issue_type"]
        properties:
          code_snippet: { type: string }
          issue_type: { type: string }
          fix_strategy: { type: string }
      output_schema:
        type: object
        properties:
          fixed_code: { type: string }
          changes_made: { type: array }
          confidence: { type: number }

    - name: "implement_feature"
      description: "تنفيذ ميزة جديدة"
      input_schema:
        type: object
        required: ["specification", "target_files"]
        properties:
          specification: { type: string }
          target_files: { type: array }
          design_patterns: { type: array }
      output_schema:
        type: object
        properties:
          implementation: { type: object }
          tests: { type: array }
          documentation: { type: string }

    - name: "refactor_code"
      description: "إعادة هيكلة الكود"
      input_schema:
        type: object
        required: ["code_snippet", "refactor_type"]
        properties:
          code_snippet: { type: string }
          refactor_type: { type: string }
          target_pattern: { type: string }
      output_schema:
        type: object
        properties:
          refactored_code: { type: string }
          improvements: { type: array }

    - name: "generate_tests"
      description: "توليد اختبارات تلقائية"
      input_schema:
        type: object
        required: ["code_snippet"]
        properties:
          code_snippet: { type: string }
          test_framework: { type: string }
          coverage_target: { type: number }
      output_schema:
        type: object
        properties:
          tests: { type: array }
          coverage_estimate: { type: number }

    - name: "review_pr"
      description: "مراجعة طلب السحب"
      input_schema:
        type: object
        required: ["pr_diff"]
        properties:
          pr_diff: { type: string }
          context_files: { type: array }
      output_schema:
        type: object
        properties:
          review_comments: { type: array }
          approval_status: { type: string }
          suggestions: { type: array }
```

### 3.3 الهيكل التقني المقترح

```
apps/services/code-fix-agent/
├── Dockerfile
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── code_fix_agent.py      # Main agent class
│   │   ├── analyzers/
│   │   │   ├── python_analyzer.py
│   │   │   ├── typescript_analyzer.py
│   │   │   └── dart_analyzer.py
│   │   ├── fixers/
│   │   │   ├── bug_fixer.py
│   │   │   ├── security_fixer.py
│   │   │   └── performance_fixer.py
│   │   └── generators/
│   │       ├── code_generator.py
│   │       ├── test_generator.py
│   │       └── doc_generator.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── ast_tools.py           # Abstract Syntax Tree utilities
│   │   ├── git_tools.py           # Git integration
│   │   ├── sandbox.py             # Safe code execution
│   │   └── lsp_client.py          # Language Server Protocol
│   ├── knowledge/
│   │   ├── patterns.py            # Design patterns database
│   │   ├── best_practices.py      # SAHOOL best practices
│   │   └── codebase_context.py    # Project-specific knowledge
│   └── api/
│       └── v1/
│           ├── analyze.py
│           ├── fix.py
│           └── implement.py
└── tests/
    ├── unit/
    ├── integration/
    └── golden_dataset/
```

### 3.4 تصميم الفئة الأساسية

```python
"""
SAHOOL Code Fix Agent
وكيل إصلاح وتنفيذ الكود

Implements a Learning + Utility-Based agent for:
- Code analysis and bug detection
- Automated code fixes
- Feature implementation
- Code refactoring
- Test generation
- PR review
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from apps.services.ai_agents_core.src.agents.base_agent import (
    AgentAction,
    AgentContext,
    AgentLayer,
    AgentPercept,
    AgentType,
    BaseAgent,
)


class IssueType(Enum):
    """أنواع مشاكل الكود"""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    TYPE_ERROR = "type_error"
    LOGIC_ERROR = "logic_error"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"


class FixStrategy(Enum):
    """استراتيجيات الإصلاح"""
    MINIMAL = "minimal"          # أقل تغيير ممكن
    COMPREHENSIVE = "comprehensive"  # إصلاح شامل
    REFACTOR = "refactor"        # إعادة هيكلة


@dataclass
class CodeIssue:
    """مشكلة في الكود"""
    issue_type: IssueType
    severity: str  # critical, high, medium, low
    line_start: int
    line_end: int
    description: str
    description_ar: str
    suggestion: str
    confidence: float


@dataclass
class CodeFix:
    """إصلاح الكود"""
    original_code: str
    fixed_code: str
    changes: list[dict[str, Any]]
    confidence: float
    tests_needed: list[str]


class CodeFixAgent(BaseAgent):
    """
    وكيل إصلاح وتنفيذ الكود
    Code Fix and Implementation Agent

    Combines Utility-Based decision making with Learning capabilities
    for intelligent code analysis and fixes.
    """

    # Priority weights for different issue types
    ISSUE_PRIORITIES = {
        IssueType.SECURITY: 100,
        IssueType.MEMORY_LEAK: 90,
        IssueType.RACE_CONDITION: 85,
        IssueType.BUG: 80,
        IssueType.TYPE_ERROR: 70,
        IssueType.LOGIC_ERROR: 75,
        IssueType.PERFORMANCE: 50,
        IssueType.STYLE: 20,
    }

    def __init__(self, agent_id: str = "code_fix_agent_001"):
        super().__init__(
            agent_id=agent_id,
            name="Code Fix Agent",
            name_ar="وكيل إصلاح الكود",
            agent_type=AgentType.LEARNING,  # Learning agent for continuous improvement
            layer=AgentLayer.SPECIALIST,
            description="AI agent for code analysis, fixes, and implementation",
            description_ar="وكيل ذكاء اصطناعي لتحليل وإصلاح وتنفيذ الكود",
        )

        # Initialize analyzers and tools
        self._init_analyzers()
        self._init_knowledge_base()

        # Set utility function for fix selection
        self.set_utility_function(self._fix_utility)

        # Track fix history for learning
        self.fix_history: list[dict[str, Any]] = []
        self.success_patterns: dict[str, float] = {}

    def _fix_utility(self, action: AgentAction, context: AgentContext) -> float:
        """
        دالة المنفعة لتقييم خيارات الإصلاح
        Utility function to evaluate fix options

        Considers:
        - Issue severity and priority
        - Fix confidence
        - Code change size (minimal preferred)
        - Historical success rate
        - Test coverage impact
        """
        if action.action_type != "apply_fix":
            return 0.0

        params = action.parameters

        # Severity factor (higher priority = higher utility)
        issue_type = params.get("issue_type")
        severity_score = self.ISSUE_PRIORITIES.get(
            IssueType(issue_type), 50
        ) / 100

        # Confidence factor
        confidence = params.get("confidence", 0.5)

        # Change size factor (smaller changes preferred)
        change_size = params.get("change_size", 100)
        size_factor = max(0, 1 - (change_size / 500))

        # Historical success factor
        pattern_key = f"{issue_type}_{params.get('fix_pattern', 'default')}"
        success_rate = self.success_patterns.get(pattern_key, 0.7)

        # Calculate combined utility
        utility = (
            0.30 * severity_score +
            0.25 * confidence +
            0.20 * size_factor +
            0.25 * success_rate
        )

        return utility

    async def perceive(self, percept: AgentPercept) -> None:
        """
        استقبال المدخلات للتحليل
        Receive inputs for analysis
        """
        if percept.percept_type == "code_snippet":
            self.state.beliefs["code"] = percept.data

        elif percept.percept_type == "file_context":
            self.state.beliefs["context"] = percept.data

        elif percept.percept_type == "error_log":
            self.state.beliefs["errors"] = percept.data

        elif percept.percept_type == "pr_diff":
            self.state.beliefs["diff"] = percept.data

        elif percept.percept_type == "specification":
            self.state.beliefs["spec"] = percept.data

    async def think(self) -> AgentAction | None:
        """
        تحليل الكود واتخاذ القرار
        Analyze code and decide on action
        """
        # Determine task type
        if "errors" in self.state.beliefs:
            return await self._handle_error_fix()

        elif "diff" in self.state.beliefs:
            return await self._handle_pr_review()

        elif "spec" in self.state.beliefs:
            return await self._handle_implementation()

        elif "code" in self.state.beliefs:
            return await self._handle_code_analysis()

        return None

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """
        تنفيذ الإجراء
        Execute the action
        """
        # Implementation details...
        pass

    async def learn(self, feedback: dict[str, Any]) -> None:
        """
        التعلم من نتائج الإصلاحات
        Learn from fix results
        """
        await super().learn(feedback)

        # Update success patterns
        if feedback.get("fix_successful"):
            pattern_key = feedback.get("pattern_key")
            current_rate = self.success_patterns.get(pattern_key, 0.7)
            # Exponential moving average
            self.success_patterns[pattern_key] = (
                0.9 * current_rate + 0.1 * 1.0
            )
        else:
            pattern_key = feedback.get("pattern_key")
            current_rate = self.success_patterns.get(pattern_key, 0.7)
            self.success_patterns[pattern_key] = (
                0.9 * current_rate + 0.1 * 0.0
            )
```

### 3.5 تكامل MCP (Model Context Protocol)

```python
# إضافة أدوات جديدة لـ shared/mcp/tools.py

class CodeFixMCPTools:
    """MCP Tools for Code Fix Agent"""

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "analyze_code",
                "description": "Analyze code for bugs, security issues, and improvements. Returns detailed analysis with suggestions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code snippet to analyze"
                        },
                        "language": {
                            "type": "string",
                            "enum": ["python", "typescript", "dart"],
                            "description": "Programming language"
                        },
                        "analysis_depth": {
                            "type": "string",
                            "enum": ["quick", "standard", "deep"],
                            "default": "standard"
                        }
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "fix_bug",
                "description": "Automatically fix detected bug in code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "bug_description": {"type": "string"},
                        "fix_strategy": {
                            "type": "string",
                            "enum": ["minimal", "comprehensive", "refactor"]
                        }
                    },
                    "required": ["code", "bug_description"]
                }
            },
            {
                "name": "generate_tests",
                "description": "Generate unit tests for code",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                        "framework": {
                            "type": "string",
                            "description": "Test framework (pytest, vitest, flutter_test)"
                        },
                        "coverage_target": {
                            "type": "number",
                            "default": 80
                        }
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "review_changes",
                "description": "Review code changes and provide feedback",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "diff": {"type": "string"},
                        "context": {"type": "string"},
                        "review_focus": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Focus areas: security, performance, style, logic"
                        }
                    },
                    "required": ["diff"]
                }
            }
        ]
```

### 3.6 نظام التقييم (Evaluation System)

```python
# إضافة لـ tests/evaluation/

class CodeFixEvaluator:
    """
    تقييم أداء وكيل إصلاح الكود
    Evaluate Code Fix Agent Performance
    """

    METRICS = {
        "fix_accuracy": {
            "description": "نسبة الإصلاحات الصحيحة",
            "weight": 0.35,
            "threshold": 0.85
        },
        "time_to_fix": {
            "description": "متوسط وقت الإصلاح",
            "weight": 0.15,
            "threshold_ms": 5000
        },
        "regression_rate": {
            "description": "معدل الأخطاء الناتجة عن الإصلاح",
            "weight": 0.25,
            "threshold": 0.05  # Max 5%
        },
        "test_pass_rate": {
            "description": "نسبة نجاح الاختبارات بعد الإصلاح",
            "weight": 0.25,
            "threshold": 0.95
        }
    }

    def evaluate(self, results: list[dict]) -> dict:
        """تقييم شامل"""
        scores = {}

        # Fix accuracy
        successful_fixes = sum(1 for r in results if r["fix_correct"])
        scores["fix_accuracy"] = successful_fixes / len(results)

        # Time to fix
        avg_time = sum(r["time_ms"] for r in results) / len(results)
        scores["time_to_fix"] = max(0, 1 - (avg_time / 10000))

        # Regression rate
        regressions = sum(1 for r in results if r.get("caused_regression"))
        scores["regression_rate"] = 1 - (regressions / len(results))

        # Test pass rate
        tests_passed = sum(r.get("tests_passed", 0) for r in results)
        tests_total = sum(r.get("tests_total", 1) for r in results)
        scores["test_pass_rate"] = tests_passed / tests_total

        # Weighted overall score
        overall = sum(
            scores[metric] * info["weight"]
            for metric, info in self.METRICS.items()
        )

        return {
            "scores": scores,
            "overall": overall,
            "passed": all(
                scores[m] >= self.METRICS[m].get("threshold", 0)
                for m in scores
            )
        }
```

---

## 4. خطة التنفيذ / Implementation Plan

### المرحلة 1: الأساس (Phase 1: Foundation)

| المهمة                         | الأولوية | المتطلبات                     |
| ------------------------------ | -------- | ----------------------------- |
| إنشاء هيكل خدمة code-fix-agent | عالية    | Python, FastAPI               |
| تنفيذ CodeFixAgent base class  | عالية    | ai-agents-core                |
| تكامل مع AST analyzers         | عالية    | Python AST, typescript-parser |
| Sandbox للتنفيذ الآمن          | عالية    | Docker, seccomp               |

### المرحلة 2: التحليل (Phase 2: Analysis)

| المهمة              | الأولوية | المتطلبات                   |
| ------------------- | -------- | --------------------------- |
| Python Analyzer     | عالية    | pylint, mypy, bandit        |
| TypeScript Analyzer | عالية    | ESLint, TypeScript compiler |
| Dart Analyzer       | متوسطة   | dart analyze                |
| Security Scanner    | عالية    | semgrep, CodeQL             |

### المرحلة 3: الإصلاح (Phase 3: Fixing)

| المهمة                | الأولوية | المتطلبات                |
| --------------------- | -------- | ------------------------ |
| Bug Fixer             | عالية    | Pattern matching, LLM    |
| Security Fixer        | عالية    | OWASP guidelines         |
| Performance Optimizer | متوسطة   | Profiling integration    |
| Test Generator        | عالية    | pytest, vitest templates |

### المرحلة 4: التكامل (Phase 4: Integration)

| المهمة                    | الأولوية | المتطلبات              |
| ------------------------- | -------- | ---------------------- |
| Git Integration           | عالية    | GitPython              |
| CI/CD Integration         | عالية    | GitHub Actions         |
| IDE Plugin Support        | منخفضة   | LSP                    |
| A2A Protocol Registration | عالية    | governance/agents.yaml |

---

## 5. أفضل الممارسات المتبعة / Best Practices Applied

### 5.1 تصميم الوكيل (Agent Design)

✅ **ReAct Pattern** - Reasoning + Acting
✅ **Tool Use** - استخدام أدوات محددة
✅ **Memory Management** - ذاكرة قصيرة وطويلة المدى
✅ **Self-Reflection** - تقييم ذاتي للنتائج

### 5.2 السلامة (Safety)

✅ **Sandboxed Execution** - تنفيذ معزول
✅ **Input Validation** - التحقق من المدخلات
✅ **Rate Limiting** - تحديد معدل الطلبات
✅ **Audit Logging** - تسجيل كامل

### 5.3 القابلية للتوسع (Scalability)

✅ **Horizontal Scaling** - توسع أفقي
✅ **Async Processing** - معالجة غير متزامنة
✅ **Caching** - تخزين مؤقت للنتائج
✅ **Queue-based** - معالجة عبر الطوابير

---

## 6. تعريف A2A Protocol

```yaml
# إضافة لـ governance/agents.yaml

code-fix-agent:
  name: "Code Fix Agent"
  name_ar: "وكيل إصلاح الكود"
  version: "1.0.0"
  category: intelligence
  description: "AI agent for automated code analysis, bug fixing, and implementation"
  description_ar: "وكيل ذكاء اصطناعي لتحليل وإصلاح وتنفيذ الكود تلقائياً"

  capabilities:
    - name: "analyze_code"
      description: "Comprehensive code analysis"
      input_schema:
        type: object
        required: ["code", "language"]
        properties:
          code: { type: string }
          language: { type: string, enum: ["python", "typescript", "dart"] }
      output_schema:
        type: object
        properties:
          issues: { type: array }
          suggestions: { type: array }

    - name: "fix_code"
      description: "Automated bug fixing"
      input_schema:
        type: object
        required: ["code", "issue"]
      output_schema:
        type: object
        properties:
          fixed_code: { type: string }
          confidence: { type: number }

    - name: "implement_feature"
      description: "Feature implementation from specification"
      input_schema:
        type: object
        required: ["specification"]
      output_schema:
        type: object
        properties:
          implementation: { type: object }
          tests: { type: array }

    - name: "generate_tests"
      description: "Automated test generation"
      input_schema:
        type: object
        required: ["code"]
      output_schema:
        type: object
        properties:
          tests: { type: array }
          coverage: { type: number }

    - name: "review_pr"
      description: "Pull request review"
      input_schema:
        type: object
        required: ["diff"]
      output_schema:
        type: object
        properties:
          comments: { type: array }
          approval: { type: string }

  skills:
    - skill_id: "code_analysis"
      name: "Code Analysis"
      name_ar: "تحليل الكود"
      level: "expert"
      keywords: ["analysis", "bugs", "security", "performance"]

    - skill_id: "code_generation"
      name: "Code Generation"
      name_ar: "توليد الكود"
      level: "expert"
      keywords: ["generation", "implementation", "refactoring"]

    - skill_id: "testing"
      name: "Test Generation"
      name_ar: "توليد الاختبارات"
      level: "advanced"
      keywords: ["testing", "unit-tests", "coverage"]

  dependencies:
    - git-service
    - ci-cd-pipeline
    - sandbox-service

  endpoint:
    url: "https://api.sahool.app/agents/code-fix/invoke"
    method: "POST"

  health_endpoint: "https://api.sahool.app/agents/code-fix/health"

  security:
    scheme: "bearer"
    requires_authentication: true
    requires_developer_role: true

  metadata:
    tags: ["code", "development", "ai", "automation", "testing"]
    organization: "SAHOOL"
    license: "MIT"

  status: "proposed"
```

---

## 7. الخلاصة / Conclusion

هذا المقترح يقدم وكيل ذكاء اصطناعي متكامل لإصلاح وتنفيذ الكود يتوافق مع:

1. ✅ البنية التحتية الحالية لوكلاء سهول
2. ✅ بروتوكول A2A المعتمد
3. ✅ معايير MCP للتكامل
4. ✅ أفضل ممارسات Claude Agent SDK
5. ✅ متطلبات الأمان والسلامة

### الخطوات التالية

1. مراجعة المقترح من فريق التطوير
2. الموافقة على خطة التنفيذ
3. تخصيص الموارد
4. بدء التنفيذ المرحلي

---

**التوقيع**: AI Architecture Team
**التاريخ**: يناير 2026

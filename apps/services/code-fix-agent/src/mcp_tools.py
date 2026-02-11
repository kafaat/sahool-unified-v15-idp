"""
SAHOOL Code Fix Agent - MCP Tools
أدوات بروتوكول سياق النموذج

Model Context Protocol tools for code operations.
Integrates with Claude and other AI models.
"""

from dataclasses import dataclass
from typing import Any

import structlog

from .agent.code_fix_agent import AgentPercept, CodeFixAgent
from .tools.sandbox import CodeSandbox, SandboxConfig

logger = structlog.get_logger(__name__)


@dataclass
class MCPToolDefinition:
    """تعريف أداة MCP"""

    name: str
    description: str
    description_ar: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None


class CodeFixMCPTools:
    """
    أدوات MCP لوكيل إصلاح الكود
    MCP Tools for Code Fix Agent

    Provides Model Context Protocol compatible tools for:
    - Code analysis
    - Bug fixing
    - Test generation
    - Code review
    - Safe code execution
    """

    def __init__(self, agent: CodeFixAgent | None = None):
        """
        تهيئة أدوات MCP

        Args:
            agent: وكيل إصلاح الكود (اختياري)
        """
        self.agent = agent or CodeFixAgent()
        self.sandbox = CodeSandbox(
            SandboxConfig(
                timeout_seconds=30,
                memory_limit_mb=256,
            )
        )

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        الحصول على تعريفات الأدوات
        Get tool definitions for MCP protocol
        """
        return [
            {
                "name": "analyze_code",
                "description": "Analyze code for bugs, security issues, and improvements. Supports Python, TypeScript, and Dart.",
                "description_ar": "تحليل الكود للبحث عن الأخطاء ومشاكل الأمان والتحسينات",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Source code to analyze"},
                        "language": {
                            "type": "string",
                            "enum": ["python", "typescript", "javascript", "dart"],
                            "default": "python",
                            "description": "Programming language",
                        },
                        "analysis_depth": {
                            "type": "string",
                            "enum": ["quick", "standard", "deep"],
                            "default": "standard",
                            "description": "Depth of analysis",
                        },
                        "check_security": {
                            "type": "boolean",
                            "default": True,
                            "description": "Check for security vulnerabilities",
                        },
                        "check_style": {
                            "type": "boolean",
                            "default": False,
                            "description": "Check code style",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "fix_bug",
                "description": "Automatically fix detected bug in code. Returns fixed code with explanation.",
                "description_ar": "إصلاح الخطأ المكتشف في الكود تلقائياً",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code with bug to fix"},
                        "bug_description": {
                            "type": "string",
                            "description": "Description of the bug",
                        },
                        "error_message": {
                            "type": "string",
                            "description": "Error message if available",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["python", "typescript", "javascript", "dart"],
                            "default": "python",
                        },
                        "fix_strategy": {
                            "type": "string",
                            "enum": ["minimal", "comprehensive", "refactor", "safe"],
                            "default": "minimal",
                            "description": "Strategy for fixing",
                        },
                    },
                    "required": ["code", "bug_description"],
                },
            },
            {
                "name": "generate_tests",
                "description": "Generate unit tests for the provided code.",
                "description_ar": "توليد اختبارات الوحدة للكود المقدم",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to generate tests for"},
                        "language": {
                            "type": "string",
                            "enum": ["python", "typescript", "javascript", "dart"],
                            "default": "python",
                        },
                        "framework": {
                            "type": "string",
                            "description": "Test framework (pytest, vitest, flutter_test)",
                        },
                        "coverage_target": {
                            "type": "number",
                            "default": 80,
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Target code coverage percentage",
                        },
                        "test_style": {
                            "type": "string",
                            "enum": ["unit", "integration", "both"],
                            "default": "unit",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "review_changes",
                "description": "Review code changes (diff) and provide feedback.",
                "description_ar": "مراجعة تغييرات الكود وتقديم التغذية الراجعة",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "diff": {"type": "string", "description": "Git diff or code changes"},
                        "context": {
                            "type": "string",
                            "description": "Additional context about the changes",
                        },
                        "review_focus": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Focus areas: security, performance, style, logic",
                        },
                        "severity_threshold": {
                            "type": "string",
                            "enum": ["all", "warnings", "errors"],
                            "default": "warnings",
                        },
                    },
                    "required": ["diff"],
                },
            },
            {
                "name": "execute_code",
                "description": "Safely execute code in a sandboxed environment.",
                "description_ar": "تنفيذ الكود بأمان في بيئة معزولة",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to execute"},
                        "language": {
                            "type": "string",
                            "enum": ["python"],
                            "default": "python",
                            "description": "Programming language (currently only Python)",
                        },
                        "inputs": {"type": "object", "description": "Input variables for the code"},
                        "timeout_seconds": {
                            "type": "number",
                            "default": 30,
                            "maximum": 60,
                            "description": "Execution timeout",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "refactor_code",
                "description": "Refactor code to improve quality without changing behavior.",
                "description_ar": "إعادة هيكلة الكود لتحسين الجودة",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to refactor"},
                        "language": {
                            "type": "string",
                            "enum": ["python", "typescript", "javascript", "dart"],
                            "default": "python",
                        },
                        "refactor_type": {
                            "type": "string",
                            "enum": [
                                "extract_function",
                                "extract_variable",
                                "rename",
                                "simplify",
                                "optimize",
                                "modernize",
                            ],
                            "description": "Type of refactoring",
                        },
                        "target": {
                            "type": "string",
                            "description": "Specific target for refactoring (function name, line range)",
                        },
                    },
                    "required": ["code", "refactor_type"],
                },
            },
            {
                "name": "explain_code",
                "description": "Explain what a piece of code does in natural language.",
                "description_ar": "شرح ما يفعله الكود باللغة الطبيعية",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to explain"},
                        "language": {
                            "type": "string",
                            "enum": ["python", "typescript", "javascript", "dart"],
                            "default": "python",
                        },
                        "detail_level": {
                            "type": "string",
                            "enum": ["brief", "detailed", "comprehensive"],
                            "default": "detailed",
                        },
                        "output_language": {
                            "type": "string",
                            "enum": ["en", "ar"],
                            "default": "en",
                            "description": "Language for explanation",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "get_code_metrics",
                "description": "Calculate code quality metrics.",
                "description_ar": "حساب مقاييس جودة الكود",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to analyze"},
                        "language": {
                            "type": "string",
                            "enum": ["python", "typescript", "javascript", "dart"],
                            "default": "python",
                        },
                    },
                    "required": ["code"],
                },
            },
        ]

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        تنفيذ أداة MCP
        Execute MCP tool

        Args:
            tool_name: اسم الأداة
            arguments: معطيات الأداة

        Returns:
            نتيجة التنفيذ
        """
        logger.info("mcp_tool_execute", tool=tool_name, args_keys=list(arguments.keys()))

        try:
            if tool_name == "analyze_code":
                return await self._analyze_code(arguments)

            elif tool_name == "fix_bug":
                return await self._fix_bug(arguments)

            elif tool_name == "generate_tests":
                return await self._generate_tests(arguments)

            elif tool_name == "review_changes":
                return await self._review_changes(arguments)

            elif tool_name == "execute_code":
                return await self._execute_code(arguments)

            elif tool_name == "refactor_code":
                return await self._refactor_code(arguments)

            elif tool_name == "explain_code":
                return await self._explain_code(arguments)

            elif tool_name == "get_code_metrics":
                return await self._get_code_metrics(arguments)

            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                }

        except Exception as e:
            logger.error("mcp_tool_error", tool=tool_name, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }

    async def _analyze_code(self, args: dict[str, Any]) -> dict[str, Any]:
        """تحليل الكود"""
        percept = AgentPercept(
            percept_type="code_snippet",
            data={
                "code": args["code"],
                "language": args.get("language", "python"),
            },
            source="mcp",
        )

        result = await self.agent.run(percept)

        return {
            "success": result.get("success", False),
            "analysis": result.get("action", {}).get("parameters", {}).get("analysis_result"),
            "response_time_ms": result.get("total_time_ms"),
        }

    async def _fix_bug(self, args: dict[str, Any]) -> dict[str, Any]:
        """إصلاح الخطأ"""
        # First perceive the code
        await self.agent.perceive(
            AgentPercept(
                percept_type="code_snippet",
                data={
                    "code": args["code"],
                    "language": args.get("language", "python"),
                },
                source="mcp",
            )
        )

        # Then perceive the error
        percept = AgentPercept(
            percept_type="error_log",
            data=[
                {
                    "type": "bug",
                    "message": args["bug_description"],
                    "error_message": args.get("error_message", ""),
                }
            ],
            source="mcp",
        )

        result = await self.agent.run(percept)

        return {
            "success": result.get("success", False),
            "fix": result.get("action", {}).get("parameters", {}).get("fix"),
            "confidence": result.get("action", {}).get("confidence"),
            "response_time_ms": result.get("total_time_ms"),
        }

    async def _generate_tests(self, args: dict[str, Any]) -> dict[str, Any]:
        """توليد الاختبارات"""
        # This would integrate with test generation logic
        return {
            "success": True,
            "tests": [],
            "coverage_estimate": 0,
            "message": "Test generation requires LLM integration",
        }

    async def _review_changes(self, args: dict[str, Any]) -> dict[str, Any]:
        """مراجعة التغييرات"""
        percept = AgentPercept(
            percept_type="pr_diff",
            data=args["diff"],
            source="mcp",
        )

        result = await self.agent.run(percept)

        return {
            "success": result.get("success", False),
            "review": result.get("action", {}).get("parameters", {}).get("review"),
            "response_time_ms": result.get("total_time_ms"),
        }

    async def _execute_code(self, args: dict[str, Any]) -> dict[str, Any]:
        """تنفيذ الكود"""
        result = await self.sandbox.execute_python(
            code=args["code"],
            inputs=args.get("inputs"),
        )

        return {
            "success": result.status.value == "success",
            "status": result.status.value,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_value": result.return_value,
            "execution_time_ms": result.execution_time_ms,
            "error": result.error_message,
        }

    async def _refactor_code(self, args: dict[str, Any]) -> dict[str, Any]:
        """إعادة هيكلة الكود"""
        return {
            "success": True,
            "refactored_code": args["code"],
            "changes": [],
            "message": "Refactoring requires LLM integration",
        }

    async def _explain_code(self, args: dict[str, Any]) -> dict[str, Any]:
        """شرح الكود"""
        return {
            "success": True,
            "explanation": "Code explanation requires LLM integration",
            "explanation_ar": "شرح الكود يتطلب تكامل LLM",
        }

    async def _get_code_metrics(self, args: dict[str, Any]) -> dict[str, Any]:
        """حساب المقاييس"""
        from .agent.analyzers.dart_analyzer import DartAnalyzer
        from .agent.analyzers.python_analyzer import PythonAnalyzer
        from .agent.analyzers.typescript_analyzer import TypeScriptAnalyzer

        language = args.get("language", "python")
        code = args["code"]

        if language == "python":
            analyzer = PythonAnalyzer()
        elif language in ["typescript", "javascript"]:
            analyzer = TypeScriptAnalyzer()
        elif language == "dart":
            analyzer = DartAnalyzer()
        else:
            return {"success": False, "error": f"Unsupported language: {language}"}

        result = await analyzer.analyze(code)

        return {
            "success": result.success,
            "metrics": result.metrics,
            "issue_count": len(result.issues),
        }


def get_mcp_server_config() -> dict[str, Any]:
    """
    الحصول على إعدادات خادم MCP
    Get MCP server configuration
    """
    tools = CodeFixMCPTools()

    return {
        "name": "code-fix-agent",
        "version": "1.0.0",
        "description": "AI-powered code analysis and fixing tools",
        "description_ar": "أدوات تحليل وإصلاح الكود المدعومة بالذكاء الاصطناعي",
        "tools": tools.get_tool_definitions(),
        "capabilities": {
            "analysis": True,
            "fixing": True,
            "testing": True,
            "execution": True,
            "review": True,
        },
        "supported_languages": ["python", "typescript", "javascript", "dart"],
    }

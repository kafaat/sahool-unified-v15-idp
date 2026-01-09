"""
Unit Tests for Code Fix Agent
اختبارات الوحدة لوكيل إصلاح الكود
"""

import sys
from pathlib import Path

import pytest

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent.code_fix_agent import (
    AgentPercept,
    AgentStatus,
    CodeFixAgent,
    CodeIssue,
    IssueSeverity,
    IssueType,
    SupportedLanguage,
)


class TestCodeFixAgent:
    """اختبارات وكيل إصلاح الكود"""

    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return CodeFixAgent(agent_id="test_agent_001")

    def test_agent_initialization(self, agent):
        """اختبار تهيئة الوكيل"""
        assert agent.agent_id == "test_agent_001"
        assert agent.name == "Code Fix Agent"
        assert agent.name_ar == "وكيل إصلاح الكود"
        assert agent.status == AgentStatus.IDLE
        assert len(agent.state.goals) == 5

    def test_agent_metrics_initial(self, agent):
        """اختبار المقاييس الأولية"""
        metrics = agent.get_metrics()
        assert metrics["total_requests"] == 0
        assert metrics["success_rate_percent"] == 0
        assert metrics["patterns_learned"] == 0

    def test_agent_to_dict(self, agent):
        """اختبار تحويل الوكيل إلى قاموس"""
        data = agent.to_dict()
        assert data["agent_id"] == "test_agent_001"
        assert data["name"] == "Code Fix Agent"
        assert data["name_ar"] == "وكيل إصلاح الكود"
        assert "metrics" in data

    @pytest.mark.asyncio
    async def test_perceive_code_snippet(self, agent):
        """اختبار استقبال مقطع كود"""
        percept = AgentPercept(
            percept_type="code_snippet",
            data={
                "code": "def hello():\n    print('hello')",
                "language": "python",
                "file_path": "test.py",
            },
            source="test",
        )

        await agent.perceive(percept)

        assert "code" in agent.state.beliefs
        assert agent.state.beliefs["language"] == "python"

    @pytest.mark.asyncio
    async def test_analyze_clean_code(self, agent):
        """اختبار تحليل كود نظيف"""
        percept = AgentPercept(
            percept_type="code_snippet",
            data={
                "code": "def add(a, b):\n    return a + b\n",
                "language": "python",
            },
            source="test",
        )

        result = await agent.run(percept)

        assert result["success"]
        assert result["action"]["action_type"] == "analyze_code"

    @pytest.mark.asyncio
    async def test_analyze_code_with_syntax_error(self, agent):
        """اختبار تحليل كود مع خطأ نحوي"""
        percept = AgentPercept(
            percept_type="code_snippet",
            data={
                "code": "def broken(\n    return",  # Syntax error
                "language": "python",
            },
            source="test",
        )

        result = await agent.run(percept)

        assert result["success"]
        # Should detect syntax error
        params = result["action"]["parameters"]
        if "analysis_result" in params:
            issues = params["analysis_result"].get("issues", [])
            assert any(i["type"] == "syntax_error" for i in issues)

    @pytest.mark.asyncio
    async def test_analyze_code_with_security_issue(self, agent):
        """اختبار اكتشاف مشاكل الأمان"""
        percept = AgentPercept(
            percept_type="code_snippet",
            data={
                "code": "user_input = input()\neval(user_input)",  # Security issue
                "language": "python",
            },
            source="test",
        )

        result = await agent.run(percept)

        assert result["success"]
        params = result["action"]["parameters"]
        if "analysis_result" in params:
            issues = params["analysis_result"].get("issues", [])
            assert any(i["type"] == "security" for i in issues)


class TestCodeIssue:
    """اختبارات مشاكل الكود"""

    def test_code_issue_creation(self):
        """اختبار إنشاء مشكلة كود"""
        issue = CodeIssue(
            issue_id="test_001",
            issue_type=IssueType.BUG,
            severity=IssueSeverity.HIGH,
            file_path="test.py",
            line_start=10,
            line_end=10,
            description="Test bug",
            description_ar="خطأ اختبار",
        )

        assert issue.issue_id == "test_001"
        assert issue.issue_type == IssueType.BUG
        assert issue.severity == IssueSeverity.HIGH


class TestUtilityFunction:
    """اختبارات دالة المنفعة"""

    @pytest.fixture
    def agent(self):
        return CodeFixAgent()

    def test_issue_priority_order(self, agent):
        """اختبار ترتيب أولويات المشاكل"""
        # Security should be highest priority
        assert agent.ISSUE_PRIORITIES[IssueType.SECURITY] > agent.ISSUE_PRIORITIES[IssueType.BUG]
        assert agent.ISSUE_PRIORITIES[IssueType.BUG] > agent.ISSUE_PRIORITIES[IssueType.STYLE]

    def test_severity_multipliers(self, agent):
        """اختبار مضاعفات الشدة"""
        assert (
            agent.SEVERITY_MULTIPLIERS[IssueSeverity.CRITICAL]
            > agent.SEVERITY_MULTIPLIERS[IssueSeverity.HIGH]
        )
        assert (
            agent.SEVERITY_MULTIPLIERS[IssueSeverity.HIGH]
            > agent.SEVERITY_MULTIPLIERS[IssueSeverity.LOW]
        )


class TestLearning:
    """اختبارات التعلم"""

    @pytest.fixture
    def agent(self):
        return CodeFixAgent()

    @pytest.mark.asyncio
    async def test_learn_from_feedback(self, agent):
        """اختبار التعلم من التغذية الراجعة"""
        feedback = {
            "fix_successful": True,
            "pattern_key": "bug_minimal",
            "reward": 1.0,
        }

        await agent.learn(feedback)

        assert len(agent.feedback_history) == 1
        assert len(agent.reward_history) == 1
        assert "bug_minimal" in agent.success_patterns

    @pytest.mark.asyncio
    async def test_learn_updates_patterns(self, agent):
        """اختبار تحديث الأنماط"""
        # Initial pattern rate
        agent.success_patterns["test_pattern"] = 0.5

        # Successful feedback
        await agent.learn(
            {
                "fix_successful": True,
                "pattern_key": "test_pattern",
            }
        )

        # Rate should increase
        assert agent.success_patterns["test_pattern"] > 0.5


class TestAnalyzers:
    """اختبارات المحللات"""

    @pytest.fixture
    def agent(self):
        return CodeFixAgent()

    @pytest.mark.asyncio
    async def test_check_syntax_valid(self, agent):
        """اختبار فحص نحو صالح"""
        code = "def foo():\n    return 42\n"
        issues = await agent._check_syntax(code, SupportedLanguage.PYTHON)
        assert len(issues) == 0

    @pytest.mark.asyncio
    async def test_check_syntax_invalid(self, agent):
        """اختبار فحص نحو غير صالح"""
        code = "def foo(\n    return"
        issues = await agent._check_syntax(code, SupportedLanguage.PYTHON)
        assert len(issues) > 0
        assert issues[0].issue_type == IssueType.SYNTAX_ERROR

    @pytest.mark.asyncio
    async def test_check_security_eval(self, agent):
        """اختبار اكتشاف eval"""
        code = "result = eval(user_input)"
        issues = await agent._check_security(code, SupportedLanguage.PYTHON)
        assert len(issues) > 0
        assert issues[0].issue_type == IssueType.SECURITY

    @pytest.mark.asyncio
    async def test_check_style_long_line(self, agent):
        """اختبار اكتشاف سطر طويل"""
        code = "x = " + "a" * 150  # Line > 120 chars
        issues = await agent._check_style(code, SupportedLanguage.PYTHON)
        assert any(i.issue_type == IssueType.STYLE for i in issues)

    def test_calculate_code_metrics(self, agent):
        """اختبار حساب مقاييس الكود"""
        code = """def foo():
    # Comment
    return 42

def bar():
    return 0
"""
        metrics = agent._calculate_code_metrics(code)
        assert metrics["total_lines"] == 7
        assert metrics["comment_lines"] == 1
        assert metrics["blank_lines"] == 2  # One between functions + trailing newline

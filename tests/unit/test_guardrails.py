"""
Tool Guardrails Test Suite
===========================
مجموعة اختبارات حواجز الحماية للأدوات

Tests for:
- Tool Guard functionality
- Allowlists and blocklists
- Policy management
- Security validations

Author: SAHOOL Platform Team
Updated: January 2026
"""

import json
import tempfile
from pathlib import Path

import pytest

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.guardrails]


class TestAllowlists:
    """Test allowlists configuration."""

    def test_tool_allowlist_has_essential_tools(self):
        """Test essential tools are in allowlist."""
        from shared.ai.guardrails.allowlists import TOOL_ALLOWLIST

        essential_tools = [
            "code.analyze",
            "code.fix",
            "rag.search",
            "field.list",
            "advisory.irrigation",
        ]

        for tool in essential_tools:
            assert tool in TOOL_ALLOWLIST, f"Missing essential tool: {tool}"

    def test_domain_allowlist_has_sahool_domains(self):
        """Test SAHOOL domains are allowed."""
        from shared.ai.guardrails.allowlists import DOMAIN_ALLOWLIST

        assert "sahool.app" in DOMAIN_ALLOWLIST
        assert "api.sahool.app" in DOMAIN_ALLOWLIST
        assert "localhost" in DOMAIN_ALLOWLIST

    def test_blocked_patterns_cover_secrets(self):
        """Test blocked patterns include secret patterns."""
        from shared.ai.guardrails.allowlists import BLOCKED_PATTERNS

        assert len(BLOCKED_PATTERNS) > 0

        # Check pattern structure
        for pattern in BLOCKED_PATTERNS:
            assert isinstance(pattern, str)

    def test_dangerous_commands_are_blocked(self):
        """Test dangerous commands are in blocklist."""
        from shared.ai.guardrails.allowlists import DANGEROUS_COMMANDS

        dangerous = [
            "rm -rf",
            "DROP TABLE",
            "DELETE FROM",
            "git push --force",
        ]

        for cmd in dangerous:
            assert cmd in DANGEROUS_COMMANDS, f"Missing dangerous command: {cmd}"


class TestToolGuard:
    """Test ToolGuard functionality."""

    def test_guard_initialization(self):
        """Test guard initializes correctly."""
        from shared.ai.guardrails.tool_guard import ToolGuard

        guard = ToolGuard()
        assert guard is not None

    def test_guard_allows_safe_tool(self):
        """Test guard allows safe tools."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="code.analyze",
            args={"path": "/safe/path/file.txt"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is True

    def test_guard_blocks_dangerous_tool(self):
        """Test guard blocks tools not in allowlist."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="execute_arbitrary_code",
            args={"code": "import os; os.system('rm -rf /')"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False

    def test_guard_blocks_large_output(self):
        """Test guard blocks excessively large arguments."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        # Create args larger than MAX_ARGS_SIZE (default 20000)
        large_content = "x" * 25000
        context = ToolCallContext(
            tool="code.analyze",
            args={"content": large_content},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False
        assert "large" in decision.reason.lower() or "size" in decision.reason.lower()

    def test_guard_blocks_secret_patterns(self):
        """Test guard blocks content with secret patterns."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="code.fix",
            args={
                "file_path": "/some/credentials.json",
            },
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False

    def test_guard_blocks_external_domain(self):
        """Test guard blocks external domains."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="code.analyze",
            args={"url": "https://malicious-site.com/api"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False

    def test_guard_allows_internal_domain(self):
        """Test guard allows internal domains."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="code.analyze",
            args={"url": "https://api.sahool.app/v1/fields"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is True

    def test_guard_decision_includes_metadata(self):
        """Test guard decision includes proper metadata."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="code.analyze",
            args={"path": "/test/file.txt"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)

        assert hasattr(decision, "allowed")
        assert hasattr(decision, "reason")
        assert hasattr(decision, "timestamp")


class TestPolicy:
    """Test policy management."""

    def test_policy_rule_creation(self):
        """Test policy rule creation."""
        from shared.ai.guardrails.policy import PolicyRule

        rule = PolicyRule(
            id="rule-001",
            name="Block shell commands",
            name_ar="حظر أوامر Shell",
            type="deny",
            target="*",
            conditions={"pattern": r"rm\s+-rf"},
            priority=1,
        )

        assert rule.id == "rule-001"
        assert rule.type == "deny"

    def test_guard_policy_creation(self):
        """Test guard policy creation."""
        from shared.ai.guardrails.policy import GuardPolicy, PolicyRule

        rules = [
            PolicyRule(
                id="rule-001",
                name="Block shell",
                name_ar="حظر Shell",
                type="deny",
                target="*",
                priority=1,
            ),
        ]

        policy = GuardPolicy(
            name="Test Policy",
            version="1.0",
            rules=rules,
        )

        assert policy.name == "Test Policy"
        assert len(policy.rules) == 1

    def test_save_and_load_policy(self):
        """Test saving and loading policy."""
        from shared.ai.guardrails.policy import (
            GuardPolicy,
            PolicyRule,
            load_policy,
            save_policy,
        )

        rules = [
            PolicyRule(
                id="rule-001",
                name="Test Rule",
                name_ar="قاعدة اختبار",
                type="allow",
                target="code.*",
                priority=1,
            ),
        ]

        policy = GuardPolicy(
            name="Test Policy",
            version="1.0",
            rules=rules,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "test_policy.json"

            # Save
            save_policy(policy, policy_path)
            assert policy_path.exists()

            # Load
            loaded = load_policy(policy_path)
            assert loaded.name == "Test Policy"
            assert len(loaded.rules) == 1


class TestSecurityValidations:
    """Test security validations."""

    def test_sql_injection_blocked(self):
        """Test SQL injection patterns are blocked via dangerous commands."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="code.analyze",
            args={"query": "SELECT * FROM users; DROP TABLE users;--"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False

    def test_path_traversal_blocked(self):
        """Test path traversal to /etc/passwd is blocked."""
        from shared.ai.guardrails.tool_guard import ToolCallContext, ToolGuard

        guard = ToolGuard()

        context = ToolCallContext(
            tool="code.analyze",
            args={"file_path": "/etc/passwd"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False


class TestGuardDecorator:
    """Test guard_tool_call function."""

    def test_decorator_allows_safe_call(self):
        """Test guard_tool_call allows safe function calls."""
        from shared.ai.guardrails.tool_guard import guard_tool_call

        decision = guard_tool_call(
            tool="code.analyze",
            args={"path": "/safe/path/file.txt"},
            session_id="test-session",
        )
        assert decision.allowed is True

    def test_decorator_blocks_dangerous_call(self):
        """Test guard_tool_call blocks dangerous function calls."""
        from shared.ai.guardrails.tool_guard import guard_tool_call

        decision = guard_tool_call(
            tool="code.analyze",
            args={"command": "rm -rf /"},
            session_id="test-session",
        )
        assert decision.allowed is False


# Fixtures
@pytest.fixture
def temp_policy_dir():
    """Create temporary directory for policy files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

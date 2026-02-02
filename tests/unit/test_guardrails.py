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

import pytest
import tempfile
import json
from pathlib import Path

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.guardrails]


class TestAllowlists:
    """Test allowlists configuration."""

    def test_tool_allowlist_has_essential_tools(self):
        """Test essential tools are in allowlist."""
        from shared.ai.guardrails.allowlists import TOOL_ALLOWLIST

        essential_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "search_code",
            "run_tests",
        ]

        for tool in essential_tools:
            assert tool in TOOL_ALLOWLIST, f"Missing essential tool: {tool}"

    def test_domain_allowlist_has_sahool_domains(self):
        """Test SAHOOL domains are allowed."""
        from shared.ai.guardrails.allowlists import DOMAIN_ALLOWLIST

        assert "sahool.com" in DOMAIN_ALLOWLIST
        assert "api.sahool.com" in DOMAIN_ALLOWLIST
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
            ":(){:|:&};:",  # Fork bomb
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
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="read_file",
            arguments={"path": "/safe/path/file.txt"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is True

    def test_guard_blocks_dangerous_tool(self):
        """Test guard blocks dangerous tools."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="execute_arbitrary_code",
            arguments={"code": "import os; os.system('rm -rf /')"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False

    def test_guard_blocks_large_output(self):
        """Test guard blocks excessively large outputs."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard(max_output_size=1000)

        context = ToolCallContext(
            tool_name="read_file",
            arguments={"path": "/some/file.txt"},
            output_size=10000,  # Exceeds limit
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False
        assert "size" in decision.reason.lower()

    def test_guard_blocks_secret_patterns(self):
        """Test guard blocks content with secret patterns."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="write_file",
            arguments={
                "path": "/some/config.txt",
                "content": "api_key=sk-secret123456",
            },
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False
        assert "secret" in decision.reason.lower() or "blocked" in decision.reason.lower()

    def test_guard_blocks_external_domain(self):
        """Test guard blocks external domains."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="http_request",
            arguments={"url": "https://malicious-site.com/api"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False

    def test_guard_allows_internal_domain(self):
        """Test guard allows internal domains."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="http_request",
            arguments={"url": "https://api.sahool.com/v1/fields"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is True

    def test_guard_decision_includes_metadata(self):
        """Test guard decision includes proper metadata."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="read_file",
            arguments={"path": "/test/file.txt"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)

        assert hasattr(decision, 'allowed')
        assert hasattr(decision, 'reason')
        assert hasattr(decision, 'checked_at')


class TestPolicy:
    """Test policy management."""

    def test_policy_rule_creation(self):
        """Test policy rule creation."""
        from shared.ai.guardrails.policy import PolicyRule

        rule = PolicyRule(
            id="rule-001",
            name="Block shell commands",
            pattern=r"rm\s+-rf",
            action="block",
            priority=1,
        )

        assert rule.id == "rule-001"
        assert rule.action == "block"

    def test_guard_policy_creation(self):
        """Test guard policy creation."""
        from shared.ai.guardrails.policy import GuardPolicy, PolicyRule

        rules = [
            PolicyRule(
                id="rule-001",
                name="Block shell",
                pattern=r"rm\s+-rf",
                action="block",
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
            save_policy,
            load_policy,
        )

        rules = [
            PolicyRule(
                id="rule-001",
                name="Test Rule",
                pattern=r"test",
                action="warn",
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
        """Test SQL injection patterns are blocked."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="database_query",
            arguments={"query": "SELECT * FROM users; DROP TABLE users;--"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False

    def test_path_traversal_blocked(self):
        """Test path traversal is blocked."""
        from shared.ai.guardrails.tool_guard import ToolGuard, ToolCallContext

        guard = ToolGuard()

        context = ToolCallContext(
            tool_name="read_file",
            arguments={"path": "../../../etc/passwd"},
            user_id="test-user",
            session_id="test-session",
        )

        decision = guard.check(context)
        assert decision.allowed is False


class TestGuardDecorator:
    """Test guard_tool_call decorator."""

    def test_decorator_allows_safe_call(self):
        """Test decorator allows safe function calls."""
        from shared.ai.guardrails.tool_guard import guard_tool_call

        @guard_tool_call(tool_name="read_file")
        def read_file(path: str) -> str:
            return f"Content of {path}"

        # This should not raise
        result = read_file("/safe/path/file.txt")
        assert "Content" in result

    def test_decorator_blocks_dangerous_call(self):
        """Test decorator blocks dangerous function calls."""
        from shared.ai.guardrails.tool_guard import guard_tool_call, GuardDecision

        @guard_tool_call(tool_name="execute_shell")
        def execute_shell(command: str) -> str:
            return f"Executed: {command}"

        # This should be blocked
        with pytest.raises(Exception):
            execute_shell("rm -rf /")


# Fixtures
@pytest.fixture
def temp_policy_dir():
    """Create temporary directory for policy files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_policy(temp_policy_dir):
    """Create sample policy file."""
    from shared.ai.guardrails.policy import GuardPolicy, PolicyRule, save_policy

    rules = [
        PolicyRule(
            id="rule-001",
            name="Block dangerous commands",
            pattern=r"rm\s+-rf",
            action="block",
            priority=1,
        ),
        PolicyRule(
            id="rule-002",
            name="Warn on shell access",
            pattern=r"os\.system",
            action="warn",
            priority=2,
        ),
    ]

    policy = GuardPolicy(
        name="Sample Policy",
        version="1.0",
        rules=rules,
    )

    policy_path = temp_policy_dir / "sample_policy.json"
    save_policy(policy, policy_path)

    return policy_path

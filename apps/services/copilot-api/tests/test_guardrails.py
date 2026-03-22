"""
Tests for Tool Guardrails (security/guardrails.py) and Allowlists (security/allowlists.py)
"""

import pytest

pytestmark = [pytest.mark.unit]
class TestAllowlists:
    def test_rag_tools_in_allowlist(self):
        from src.security.allowlists import TOOL_ALLOWLIST

        for tool in ("rag.search", "rag.add", "rag.list", "rag.delete"):
            assert tool in TOOL_ALLOWLIST

    def test_code_tools_in_allowlist(self):
        from src.security.allowlists import TOOL_ALLOWLIST

        assert "code.analyze" in TOOL_ALLOWLIST
        assert "code.fix" in TOOL_ALLOWLIST
        assert "code.review" in TOOL_ALLOWLIST

    def test_deploy_tools_in_allowlist(self):
        from src.security.allowlists import TOOL_ALLOWLIST

        assert "deploy.plan" in TOOL_ALLOWLIST
        assert "deploy.status" in TOOL_ALLOWLIST

    def test_unknown_tool_not_in_allowlist(self):
        from src.security.allowlists import TOOL_ALLOWLIST

        assert "exec.shell" not in TOOL_ALLOWLIST
        assert "system.rm" not in TOOL_ALLOWLIST

    def test_dangerous_commands(self):
        from src.security.allowlists import DANGEROUS_COMMANDS

        assert "rm -rf" in DANGEROUS_COMMANDS
        assert "DROP TABLE" in DANGEROUS_COMMANDS
        assert "git push --force" in DANGEROUS_COMMANDS
        assert "docker rm -f" in DANGEROUS_COMMANDS

    def test_blocked_patterns_contain_secrets(self):
        from src.security.allowlists import BLOCKED_PATTERNS

        assert ".env" in BLOCKED_PATTERNS
        assert "*.key" in BLOCKED_PATTERNS
        assert "*.pem" in BLOCKED_PATTERNS
        assert "credentials.json" in BLOCKED_PATTERNS

    def test_domain_allowlist_contains_localhost(self):
        from src.security.allowlists import DOMAIN_ALLOWLIST

        assert "localhost" in DOMAIN_ALLOWLIST

    def test_domain_allowlist_contains_sahool(self):
        from src.security.allowlists import DOMAIN_ALLOWLIST

        assert "api.sahool.app" in DOMAIN_ALLOWLIST

    def test_max_args_size_is_positive(self):
        from src.security.allowlists import MAX_ARGS_SIZE

        assert MAX_ARGS_SIZE > 0

    def test_max_prompt_chars_is_positive(self):
        from src.security.allowlists import MAX_PROMPT_CHARS

        assert MAX_PROMPT_CHARS > 0
class TestGuardDecision:
    def test_to_dict(self):
        from src.security.guardrails import GuardDecision

        d = GuardDecision(
            allowed=True,
            reason="OK",
            reason_ar="موافق",
            layer="test",
            details={"key": "val"},
        )
        result = d.to_dict()
        assert result["allowed"] is True
        assert result["reason"] == "OK"
        assert result["reason_ar"] == "موافق"
        assert result["layer"] == "test"
        assert "timestamp" in result
class TestToolGuard:
    def test_allows_safe_tool(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard()
        ctx = ToolCallContext(tool="rag.search", args={"query": "test"})
        decision = guard.check(ctx)
        assert decision.allowed is True

    def test_blocks_unknown_tool(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard()
        ctx = ToolCallContext(tool="exec.shell", args={"cmd": "ls"})
        decision = guard.check(ctx)
        assert decision.allowed is False
        assert decision.layer == "tool_allowlist"

    def test_blocks_oversized_args(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard()
        ctx = ToolCallContext(tool="rag.add", args={"text": "x" * 100000})
        decision = guard.check(ctx)
        assert decision.allowed is False
        assert decision.layer == "size_limits"

    def test_blocks_dangerous_command(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard()
        ctx = ToolCallContext(tool="code.fix", args={"command": "rm -rf /"})
        decision = guard.check(ctx)
        assert decision.allowed is False
        assert decision.layer == "dangerous_commands"

    def test_blocks_external_tool_when_disabled(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard(
            tool_allowlist=frozenset({"external.api"}),
            enable_external=False,
        )
        ctx = ToolCallContext(tool="external.api", args={})
        decision = guard.check(ctx)
        assert decision.allowed is False
        assert decision.layer == "external_access"

    def test_blocks_disallowed_domain(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard(
            tool_allowlist=frozenset({"http.get"}),
        )
        ctx = ToolCallContext(tool="http.get", args={"url": "https://evil.com/data"})
        decision = guard.check(ctx)
        assert decision.allowed is False
        assert decision.layer == "external_access"

    def test_allows_allowed_domain(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard(
            tool_allowlist=frozenset({"http.get"}),
            domain_allowlist=frozenset({"api.sahool.app"}),
        )
        ctx = ToolCallContext(tool="http.get", args={"url": "https://api.sahool.app/v1/fields"})
        decision = guard.check(ctx)
        assert decision.allowed is True

    def test_stats_tracking(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard()
        guard.check(ToolCallContext(tool="rag.search", args={}))
        guard.check(ToolCallContext(tool="exec.shell", args={}))

        stats = guard.get_stats()
        assert stats["total_checks"] == 2
        assert stats["allowed"] == 1
        assert stats["blocked"] == 1

    def test_custom_validator_blocks(self):
        from src.security.guardrails import GuardDecision, ToolCallContext, ToolGuard

        def custom_block(ctx):
            if "forbidden" in str(ctx.args):
                return GuardDecision(allowed=False, reason="Custom block", layer="custom")
            return None

        guard = ToolGuard(custom_validators=[custom_block])
        ctx = ToolCallContext(tool="rag.search", args={"query": "forbidden content"})
        decision = guard.check(ctx)
        assert decision.allowed is False

    def test_audit_callback_invoked_on_allow(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        audit_log = []

        def audit_cb(ctx, decision):
            audit_log.append((ctx.tool, decision.allowed))

        guard = ToolGuard(audit_callback=audit_cb)
        guard.check(ToolCallContext(tool="rag.search", args={}))
        assert len(audit_log) == 1
        assert audit_log[0] == ("rag.search", True)

    def test_wildcard_tool_match(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        # code.* is not literally in the allowlist, but code.analyze is
        guard = ToolGuard()
        ctx = ToolCallContext(tool="code.analyze", args={})
        decision = guard.check(ctx)
        assert decision.allowed is True

    def test_blocked_env_pattern(self):
        from src.security.guardrails import ToolCallContext, ToolGuard

        guard = ToolGuard()
        ctx = ToolCallContext(tool="rag.search", args={"file_path": ".env"})
        decision = guard.check(ctx)
        assert decision.allowed is False
        assert decision.layer == "blocked_patterns"
class TestConvenienceFunctions:
    def test_guard_tool_call(self):
        from src.security.guardrails import guard_tool_call

        decision = guard_tool_call(tool="rag.search", args={"query": "test"})
        assert decision.allowed is True

    def test_is_tool_allowed(self):
        from src.security.guardrails import is_tool_allowed

        assert is_tool_allowed("rag.search") is True
        assert is_tool_allowed("exec.shell") is False

    def test_is_domain_allowed(self):
        from src.security.guardrails import is_domain_allowed

        assert is_domain_allowed("localhost") is True
        assert is_domain_allowed("evil.com") is False

    def test_is_domain_allowed_localhost_ip(self):
        from src.security.guardrails import is_domain_allowed

        assert is_domain_allowed("127.0.0.1") is True

    def test_get_guard_singleton(self):
        import src.security.guardrails as gmod
        from src.security.guardrails import get_guard

        gmod._global_guard = None
        g1 = get_guard()
        g2 = get_guard()
        assert g1 is g2
        gmod._global_guard = None

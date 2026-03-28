"""
Infrastructure Security Configuration Tests
=============================================

Deep tests that verify ACTUAL configuration files enforce security best
practices. No mocks -- every assertion parses real files from the repository.

Covers:
    - Redis hardening (ACL, bind, dangerous commands)
    - NATS gateway reject_unknown
    - Kong TRUSTED_IPS RFC-1918 only
    - Vault localhost binding
    - Docker Compose secret hygiene
    - Prometheus admin API disabled
    - OTLP TLS defaults
    - .env.example placeholder safety
    - Helm chart security contexts
    - Prisma migration safety (no CONCURRENTLY)
"""

from __future__ import annotations

import ipaddress
import os
import re
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]  # repo root


def _read(relpath: str) -> str:
    """Read a file relative to the repo root."""
    path = ROOT / relpath
    assert path.exists(), f"Expected file not found: {path}"
    return path.read_text(encoding="utf-8")


# RFC-1918 private address ranges
_RFC1918_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


def _is_rfc1918(cidr: str) -> bool:
    """Return True if *cidr* falls entirely within an RFC-1918 range."""
    net = ipaddress.ip_network(cidr.strip(), strict=False)
    return any(
        parent.supernet_of(net) or parent == net for parent in _RFC1918_NETWORKS
    )


# ═══════════════════════════════════════════════════════════════════════════
# 1. Redis -- no active ACL users in dev
# ═══════════════════════════════════════════════════════════════════════════

class TestRedisConfig:
    """Tests for infrastructure/redis/redis-secure.conf."""

    REDIS_CONF = "infrastructure/redis/redis-secure.conf"

    def test_no_active_acl_users(self):
        """All ACL `user` lines must be commented out so dev mode is safe."""
        content = _read(self.REDIS_CONF)
        active_acl_lines: list[str] = []
        for line in content.splitlines():
            stripped = line.strip()
            # Active ACL user directive: starts with "user " (not "# user")
            if stripped.startswith("user ") and not stripped.startswith("#"):
                active_acl_lines.append(stripped)
        assert active_acl_lines == [], (
            f"Found uncommented ACL user lines in {self.REDIS_CONF} "
            f"(unsafe for dev): {active_acl_lines}"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # 2. Redis -- bind localhost
    # ═══════════════════════════════════════════════════════════════════════

    def test_bind_localhost(self):
        """Redis must bind to 127.0.0.1, NOT 0.0.0.0."""
        content = _read(self.REDIS_CONF)
        bind_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("bind ") and not line.strip().startswith("#")
        ]
        assert bind_lines, "No active 'bind' directive found in redis config"
        for bind_line in bind_lines:
            assert "0.0.0.0" not in bind_line, (
                f"Redis binds to 0.0.0.0 (world-accessible): {bind_line}"
            )
            assert "127.0.0.1" in bind_line, (
                f"Redis bind does not include 127.0.0.1: {bind_line}"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # 3. Redis -- dangerous commands renamed
    # ═══════════════════════════════════════════════════════════════════════

    @pytest.mark.parametrize("cmd", ["FLUSHDB", "FLUSHALL", "CONFIG", "DEBUG"])
    def test_dangerous_commands_renamed(self, cmd: str):
        """FLUSHDB, FLUSHALL, CONFIG, and DEBUG must be renamed or disabled."""
        content = _read(self.REDIS_CONF)
        # Look for an active rename-command line for this command
        pattern = re.compile(
            rf'^rename-command\s+{cmd}\s+', re.MULTILINE
        )
        match = pattern.search(content)
        assert match is not None, (
            f"Dangerous command {cmd} is NOT renamed in {self.REDIS_CONF}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 4. NATS gateway -- reject_unknown: true
# ═══════════════════════════════════════════════════════════════════════════

class TestNATSConfig:
    """Tests for config/nats/nats-cluster-node1.conf."""

    NATS_CONF = "config/nats/nats-cluster-node1.conf"

    def test_gateway_reject_unknown(self):
        """NATS gateway section must contain reject_unknown: true."""
        content = _read(self.NATS_CONF)
        # Find the gateway block and verify reject_unknown
        in_gateway = False
        brace_depth = 0
        found = False
        for line in content.splitlines():
            stripped = line.strip()
            # Detect start of top-level gateway block
            if re.match(r'^gateway\s*\{', stripped):
                in_gateway = True
                brace_depth = 1
                continue
            if in_gateway:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth <= 0:
                    break  # exited gateway block
                if re.match(r'reject_unknown\s*:\s*true', stripped):
                    found = True
                    break
        assert found, (
            f"gateway.reject_unknown is not set to true in {self.NATS_CONF}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5. Kong -- TRUSTED_IPS private only (RFC-1918)
# ═══════════════════════════════════════════════════════════════════════════

class TestKongConfig:
    """Tests for infrastructure/gateway/kong/docker-compose.yml."""

    KONG_COMPOSE = "infrastructure/gateway/kong/docker-compose.yml"

    def test_trusted_ips_private_only(self):
        """KONG_TRUSTED_IPS must contain only RFC-1918 CIDR ranges."""
        content = _read(self.KONG_COMPOSE)
        data = yaml.safe_load(content)
        services = data.get("services", {})

        trusted_ips_found = False
        for svc_name, svc in services.items():
            env = svc.get("environment", {})
            if isinstance(env, dict):
                tip = env.get("KONG_TRUSTED_IPS")
            elif isinstance(env, list):
                tip = None
                for item in env:
                    if isinstance(item, str) and item.startswith("KONG_TRUSTED_IPS="):
                        tip = item.split("=", 1)[1]
                        break
            else:
                continue

            if tip is None:
                continue

            trusted_ips_found = True
            cidrs = [c.strip() for c in str(tip).split(",")]
            for cidr in cidrs:
                assert _is_rfc1918(cidr), (
                    f"KONG_TRUSTED_IPS in service '{svc_name}' contains non-RFC1918 "
                    f"range: {cidr}"
                )

        assert trusted_ips_found, (
            "No KONG_TRUSTED_IPS found in any service in Kong docker-compose"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 6. Docker Compose -- Vault localhost bind
# ═══════════════════════════════════════════════════════════════════════════

class TestDockerCompose:
    """Tests for the main docker-compose.yml."""

    DC_FILE = "docker-compose.yml"

    def test_vault_dev_listen_localhost(self):
        """VAULT_DEV_LISTEN_ADDRESS must bind to 127.0.0.1, not 0.0.0.0."""
        content = _read(self.DC_FILE)
        data = yaml.safe_load(content)
        vault_svc = data.get("services", {}).get("vault")
        assert vault_svc is not None, "No 'vault' service in docker-compose.yml"

        env = vault_svc.get("environment", {})
        listen_addr = None
        if isinstance(env, dict):
            listen_addr = env.get("VAULT_DEV_LISTEN_ADDRESS")
        elif isinstance(env, list):
            for item in env:
                if isinstance(item, str) and "VAULT_DEV_LISTEN_ADDRESS" in item:
                    listen_addr = item.split("=", 1)[1]
                    break

        assert listen_addr is not None, (
            "VAULT_DEV_LISTEN_ADDRESS not set in vault service"
        )
        listen_str = str(listen_addr)
        assert "127.0.0.1" in listen_str, (
            f"Vault dev listen address is not localhost: {listen_str}"
        )
        assert "0.0.0.0" not in listen_str, (
            f"Vault dev listen address binds to 0.0.0.0 (world-accessible): {listen_str}"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # 7. Docker Compose -- no exposed (hardcoded) secrets
    # ═══════════════════════════════════════════════════════════════════════

    def test_no_hardcoded_passwords(self):
        """docker-compose.yml must not contain hardcoded plaintext passwords.

        Passwords must be sourced from env vars (``${VAR}`` or ``$VAR`` syntax),
        not written literally.  We scan every ``environment:`` value for keys
        containing PASSWORD/SECRET and ensure their values use env-var interpolation.
        """
        content = _read(self.DC_FILE)
        data = yaml.safe_load(content)
        violations: list[str] = []

        sensitive_keys = re.compile(
            r"(PASSWORD|SECRET_KEY|SECRET_ID)", re.IGNORECASE
        )

        for svc_name, svc in data.get("services", {}).items():
            env = svc.get("environment", {})
            items: list[tuple[str, str]] = []
            if isinstance(env, dict):
                items = list(env.items())
            elif isinstance(env, list):
                for entry in env:
                    if isinstance(entry, str) and "=" in entry:
                        k, v = entry.split("=", 1)
                        items.append((k, v))

            for key, value in items:
                if not sensitive_keys.search(key):
                    continue
                val_str = str(value)
                # Values that use env-var interpolation are OK
                if "${" in val_str or val_str == "":
                    continue
                # Bare $VAR references are also OK
                if val_str.startswith("$") and not val_str.startswith("$$"):
                    continue
                violations.append(
                    f"  service={svc_name}, key={key}, value={val_str!r}"
                )

        assert violations == [], (
            "Hardcoded sensitive values found in docker-compose.yml:\n"
            + "\n".join(violations)
        )


# ═══════════════════════════════════════════════════════════════════════════
# 8. Prometheus -- admin API disabled in monitoring stack
# ═══════════════════════════════════════════════════════════════════════════

class TestPrometheusConfig:
    """Verify Prometheus is not started with the dangerous admin API flag."""

    MONITORING_COMPOSE = "infrastructure/monitoring/docker-compose.monitoring.yml"

    def test_admin_api_disabled_in_monitoring(self):
        """The main monitoring Prometheus must NOT enable --web.enable-admin-api.

        The admin API exposes endpoints to delete data and create snapshots,
        which is dangerous in production.
        """
        content = _read(self.MONITORING_COMPOSE)
        data = yaml.safe_load(content)
        prom_svc = data.get("services", {}).get("prometheus")
        assert prom_svc is not None, "No prometheus service found"

        command = prom_svc.get("command", [])
        if isinstance(command, str):
            command = command.split()

        for arg in command:
            assert "--web.enable-admin-api" not in arg, (
                "Prometheus in monitoring stack has --web.enable-admin-api enabled. "
                "This exposes dangerous endpoints (snapshot, delete series)."
            )


# ═══════════════════════════════════════════════════════════════════════════
# 9. OTLP -- TLS by default (insecure=false)
# ═══════════════════════════════════════════════════════════════════════════

class TestOTLPDefaults:
    """Tests for shared/telemetry/tracing.py default security."""

    TRACING_PY = "shared/telemetry/tracing.py"

    def test_otlp_insecure_defaults_false(self):
        """The OTLP exporter must default to secure (TLS) connections.

        The env var OTLP_INSECURE should default to "false", meaning TLS
        is on unless explicitly opted out.
        """
        content = _read(self.TRACING_PY)
        # Find the line that reads the env var
        match = re.search(
            r'''os\.getenv\(\s*["']OTLP_INSECURE["']\s*,\s*["'](\w+)["']\s*\)''',
            content,
        )
        assert match is not None, (
            "Could not find OTLP_INSECURE env var default in tracing.py"
        )
        default_value = match.group(1)
        assert default_value == "false", (
            f"OTLP_INSECURE defaults to '{default_value}' -- must be 'false' for TLS"
        )

    def test_otlp_insecure_env_example(self):
        """The .env.example must also set OTLP_INSECURE=false."""
        content = _read(".env.example")
        match = re.search(r"^OTLP_INSECURE\s*=\s*(.+)$", content, re.MULTILINE)
        assert match is not None, "OTLP_INSECURE not found in .env.example"
        value = match.group(1).strip().split("#")[0].strip()
        assert value == "false", (
            f"OTLP_INSECURE in .env.example is '{value}', expected 'false'"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 10. .env.example -- no real passwords
# ═══════════════════════════════════════════════════════════════════════════

class TestEnvExample:
    """.env.example must use safe placeholder values."""

    ENV_EXAMPLE = ".env.example"

    # Keywords in the KEY part that indicate a sensitive credential
    _SENSITIVE_KEY = re.compile(
        r"(PASSWORD|_SECRET_KEY|_SECRET$)", re.IGNORECASE
    )

    def test_passwords_are_placeholders(self):
        """Every PASSWORD / SECRET_KEY / SECRET value must be a placeholder
        (contain 'change' case-insensitively) or be empty.
        """
        content = _read(self.ENV_EXAMPLE)
        violations: list[str] = []

        for line in content.splitlines():
            stripped = line.strip()
            # Skip comments and blank lines
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue

            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip()

            if not self._SENSITIVE_KEY.search(key):
                continue

            # Strip inline comments
            value_clean = value.split("#")[0].strip()

            # Empty values are fine (means "user must fill in")
            if not value_clean:
                continue

            # Env-var references are fine
            if "${" in value_clean:
                continue

            # Must contain the word 'change' to signal placeholder
            if "change" not in value_clean.lower():
                violations.append(f"  {key}={value_clean}")

        assert violations == [], (
            "Found PASSWORD/SECRET values in .env.example that are not "
            "placeholder values (must contain 'change' or be empty):\n"
            + "\n".join(violations)
        )


# ═══════════════════════════════════════════════════════════════════════════
# 11. Helm charts -- security context enforcement
# ═══════════════════════════════════════════════════════════════════════════

class TestHelmSecurityContext:
    """Verify Helm chart values and helpers enforce container security."""

    VALUES = "helm/sahool/values.yaml"
    HELPERS = "helm/sahool/templates/_helpers.tpl"

    def test_values_run_as_non_root(self):
        """values.yaml podSecurityContext must set runAsNonRoot: true."""
        content = _read(self.VALUES)
        data = yaml.safe_load(content)
        psc = data.get("podSecurityContext", {})
        assert psc.get("runAsNonRoot") is True, (
            "podSecurityContext.runAsNonRoot is not true in values.yaml"
        )

    def test_values_read_only_root_filesystem(self):
        """values.yaml securityContext must set readOnlyRootFilesystem: true."""
        content = _read(self.VALUES)
        data = yaml.safe_load(content)
        sc = data.get("securityContext", {})
        assert sc.get("readOnlyRootFilesystem") is True, (
            "securityContext.readOnlyRootFilesystem not true in values.yaml"
        )

    def test_values_drop_all_capabilities(self):
        """values.yaml securityContext must drop ALL capabilities."""
        content = _read(self.VALUES)
        data = yaml.safe_load(content)
        sc = data.get("securityContext", {})
        caps = sc.get("capabilities", {})
        drop_list = caps.get("drop", [])
        assert "ALL" in drop_list, (
            f"securityContext.capabilities.drop does not include ALL: {drop_list}"
        )

    def test_helpers_pod_security_context(self):
        """_helpers.tpl sahool.podSecurityContext must enforce runAsNonRoot."""
        content = _read(self.HELPERS)
        # Extract the define block
        match = re.search(
            r'define\s+"sahool\.podSecurityContext".*?end',
            content,
            re.DOTALL,
        )
        assert match is not None, "sahool.podSecurityContext not found in _helpers.tpl"
        block = match.group(0)
        assert "runAsNonRoot: true" in block, (
            "sahool.podSecurityContext helper does not set runAsNonRoot: true"
        )

    def test_helpers_container_security_context(self):
        """_helpers.tpl sahool.securityContext must drop ALL and enforce readOnly."""
        content = _read(self.HELPERS)
        match = re.search(
            r'define\s+"sahool\.securityContext".*?end',
            content,
            re.DOTALL,
        )
        assert match is not None, "sahool.securityContext not found in _helpers.tpl"
        block = match.group(0)
        assert "readOnlyRootFilesystem: true" in block, (
            "sahool.securityContext does not set readOnlyRootFilesystem: true"
        )
        assert "- ALL" in block, (
            "sahool.securityContext does not drop ALL capabilities"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 12. Prisma migrations -- no CONCURRENTLY in active services
# ═══════════════════════════════════════════════════════════════════════════

class TestPrismaMigrations:
    """Prisma migrations must not use CREATE INDEX CONCURRENTLY.

    CONCURRENTLY cannot run inside the transaction that Prisma wraps each
    migration in, so it will cause migration failures.
    """

    MIGRATIONS_ROOT = ROOT / "apps" / "services"

    def test_no_concurrent_indexes(self):
        """Scan all active-service migration SQL files for CONCURRENTLY."""
        violations: list[str] = []
        sql_files = list(self.MIGRATIONS_ROOT.rglob("prisma/migrations/**/*.sql"))
        assert sql_files, "No Prisma migration SQL files found"

        for sql_file in sql_files:
            content = sql_file.read_text(encoding="utf-8")
            for lineno, line in enumerate(content.splitlines(), start=1):
                if "CONCURRENTLY" in line.upper() and not line.strip().startswith("--"):
                    rel = sql_file.relative_to(ROOT)
                    violations.append(f"  {rel}:{lineno}: {line.strip()}")

        assert violations == [], (
            "CREATE INDEX CONCURRENTLY found in active Prisma migrations "
            "(incompatible with Prisma transaction wrapper):\n"
            + "\n".join(violations)
        )

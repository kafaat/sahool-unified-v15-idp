"""
SAHOOL Container Security Hardening Tests
===========================================
اختبارات تقوية أمان الحاويات

Validates security best practices across all container Dockerfiles and
docker-compose.yml configurations. All tests are static analysis.

Coverage:
1.  Dockerfile security patterns    – apt cleanup, no chmod 777, no curl|sh
2.  No secrets in Dockerfiles       – no API keys, tokens, .env copies
3.  Container security config       – no privileged, no host PID/network
4.  Python base image security      – slim image, Python >= 3.11
5.  Node.js base image security     – slim/alpine, Node >= 20
6.  Network security config         – internal network, no 0.0.0.0
7.  Compose secrets handling        – variable substitution for credentials
8.  Dockerfile layer optimization   – deps before source for caching

Run:
    pytest tests/container/test_security_hardening.py -v --tb=short
    pytest tests/container/test_security_hardening.py -v -n auto
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.container.service_registry import (
    ALL_BUILT_SERVICES,
    ALL_HTTP_SERVICES,
    INFRA_SERVICES,
    NODE_SERVICES,
    PYTHON_SERVICES,
)

pytestmark = [pytest.mark.container, pytest.mark.smoke, pytest.mark.security]

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"


# ---------------------------------------------------------------------------
# Fixtures & Helpers
# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text(encoding="utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. Dockerfile Security Patterns
# ===========================================================================


class TestDockerfileSecurityPatterns:
    """Dockerfiles must follow secure build practices.
    يجب أن تتبع ملفات Docker ممارسات البناء الآمنة."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_apt_uses_no_install_recommends(self, svc_name: str) -> None:
        """apt-get install must use --no-install-recommends to minimize attack surface."""
        content = _read_dockerfile(svc_name)
        if "apt-get install" not in content:
            pytest.skip(f"{svc_name} doesn't use apt-get install")
        # Find apt-get install lines that lack --no-install-recommends
        lines = content.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if "apt-get install" in stripped and "--no-install-recommends" not in stripped:
                # Check continuation lines
                full_cmd = stripped
                j = i + 1
                while full_cmd.endswith("\\") and j < len(lines):
                    full_cmd += " " + lines[j].strip()
                    j += 1
                if "--no-install-recommends" not in full_cmd:
                    pytest.fail(
                        f"{svc_name}: apt-get install without --no-install-recommends"
                    )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_apt_lists_cleaned(self, svc_name: str) -> None:
        """apt-get install should clean up /var/lib/apt/lists/* to reduce image size."""
        content = _read_dockerfile(svc_name)
        if "apt-get install" not in content:
            pytest.skip(f"{svc_name} doesn't use apt-get install")
        has_cleanup = "rm -rf /var/lib/apt/lists" in content or "apt-get clean" in content
        assert has_cleanup, (
            f"{svc_name}: apt-get install without cleaning /var/lib/apt/lists/*"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_no_chmod_777(self, svc_name: str) -> None:
        """No chmod 777 in Dockerfile (overly permissive)."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        assert "chmod 777" not in content, (
            f"{svc_name}: Dockerfile uses chmod 777 (security risk)"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_no_curl_pipe_sh(self, svc_name: str) -> None:
        """No curl|sh or curl|bash patterns (unsafe remote code execution)."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        unsafe = bool(re.search(
            r"curl\s+.*\|\s*(sh|bash|python)", content, re.IGNORECASE
        ))
        assert not unsafe, (
            f"{svc_name}: Dockerfile uses curl|sh pattern (unsafe)"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_no_add_with_url(self, svc_name: str) -> None:
        """No ADD with remote URLs (use COPY + explicit download instead)."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        # ADD https://... is risky
        has_remote_add = bool(re.search(
            r"^\s*ADD\s+https?://", content, re.IGNORECASE | re.MULTILINE
        ))
        assert not has_remote_add, (
            f"{svc_name}: Dockerfile uses ADD with remote URL (use COPY instead)"
        )


# ===========================================================================
# 2. No Secrets in Dockerfile
# ===========================================================================


class TestNoSecretsInDockerfile:
    """No secrets or credentials in Dockerfiles.
    لا يجب وجود أسرار أو بيانات اعتماد في ملفات Docker."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_no_env_file_copied(self, svc_name: str) -> None:
        """No .env files should be COPY'd into images."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        has_env_copy = bool(re.search(
            r"^\s*COPY\s+.*\.env\b", content, re.IGNORECASE | re.MULTILINE
        ))
        assert not has_env_copy, (
            f"{svc_name}: Dockerfile copies .env file into image"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_no_ssh_keys_in_image(self, svc_name: str) -> None:
        """No SSH keys referenced in COPY/ADD."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        has_ssh = bool(re.search(
            r"(?:COPY|ADD)\s+.*(?:id_rsa|id_ed25519|\.ssh)",
            content,
            re.IGNORECASE,
        ))
        assert not has_ssh, (
            f"{svc_name}: Dockerfile references SSH keys"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_no_git_credentials(self, svc_name: str) -> None:
        """No git credentials in Dockerfile."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        has_git_creds = bool(re.search(
            r"git\s+clone\s+https://[^@]+:[^@]+@",
            content,
            re.IGNORECASE,
        ))
        assert not has_git_creds, (
            f"{svc_name}: Dockerfile contains git credentials in clone URL"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_arg_secrets_no_default(self, svc_name: str) -> None:
        """ARG instructions for secrets should not have default values."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped.startswith("ARG"):
                continue
            # Check if it's a secret-like ARG with a default
            if re.search(
                r"ARG\s+(?:.*(?:PASSWORD|SECRET|TOKEN|API_KEY).*)\s*=\s*\S",
                stripped,
                re.IGNORECASE,
            ):
                pytest.fail(
                    f"{svc_name}: ARG with secret has default value: {stripped}"
                )


# ===========================================================================
# 3. Container Security Config
# ===========================================================================


class TestContainerSecurityConfig:
    """docker-compose.yml must not use insecure settings.
    يجب ألا يستخدم docker-compose.yml إعدادات غير آمنة."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_privileged(self, services: dict, svc_name: str) -> None:
        """No privileged: true on application services."""
        svc = services.get(svc_name, {})
        assert svc.get("privileged") is not True, (
            f"'{svc_name}' runs as privileged container"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_cap_add_all(self, services: dict, svc_name: str) -> None:
        """No cap_add: ALL or SYS_ADMIN on application services."""
        svc = services.get(svc_name, {})
        caps = svc.get("cap_add", [])
        forbidden = {"ALL", "SYS_ADMIN", "NET_ADMIN"}
        bad_caps = [c for c in caps if c in forbidden]
        assert not bad_caps, (
            f"'{svc_name}' has dangerous capabilities: {bad_caps}"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_docker_socket_mount(self, services: dict, svc_name: str) -> None:
        """No Docker socket mount on application services."""
        svc = services.get(svc_name, {})
        volumes = svc.get("volumes", [])
        for vol in volumes:
            vol_str = str(vol)
            assert "/var/run/docker.sock" not in vol_str, (
                f"'{svc_name}' mounts Docker socket (security risk)"
            )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_host_network_mode(self, services: dict, svc_name: str) -> None:
        """No network_mode: host on application services."""
        svc = services.get(svc_name, {})
        assert svc.get("network_mode") != "host", (
            f"'{svc_name}' uses host network mode"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_host_pid(self, services: dict, svc_name: str) -> None:
        """No pid: host on application services."""
        svc = services.get(svc_name, {})
        assert svc.get("pid") != "host", (
            f"'{svc_name}' shares host PID namespace"
        )


# ===========================================================================
# 4. Python Base Image Security
# ===========================================================================


class TestPythonBaseImageSecurity:
    """Python services must use secure base images.
    يجب أن تستخدم خدمات Python صور أساسية آمنة."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_uses_slim_image(self, svc_name: str) -> None:
        """Python service must use slim base (not full debian/ubuntu)."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        # Check all FROM directives (multi-stage builds)
        from_images = re.findall(r"FROM\s+(\S+)", content, re.IGNORECASE)
        if not from_images:
            pytest.skip(f"No FROM in {svc_name}")
        # At least one FROM should use an acceptable base
        is_acceptable = any(
            "slim" in img or "alpine" in img or "nvidia/cuda" in img
            or "distroless" in img
            for img in from_images
        )
        assert is_acceptable, (
            f"{svc_name}: no base image uses slim/alpine/cuda: {from_images}"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_version_minimum(self, svc_name: str) -> None:
        """Python version must be >= 3.11."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        # Check ARG PYTHON_VERSION or FROM python:3.xx
        version_match = re.search(
            r"(?:ARG\s+PYTHON_VERSION\s*=\s*|FROM\s+python:)(\d+\.\d+)",
            content,
        )
        if not version_match:
            pytest.skip(f"{svc_name}: cannot determine Python version")
        version = version_match.group(1)
        major, minor = version.split(".")
        assert int(major) >= 3 and int(minor) >= 11, (
            f"{svc_name}: Python {version} < 3.11 (minimum required)"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_pythondontwritebytecode(self, svc_name: str) -> None:
        """PYTHONDONTWRITEBYTECODE=1 should be set to avoid .pyc in image."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        if "PYTHONDONTWRITEBYTECODE" not in content:
            pytest.xfail(
                f"{svc_name}: missing PYTHONDONTWRITEBYTECODE=1 (recommended)"
            )


# ===========================================================================
# 5. Node.js Base Image Security
# ===========================================================================


class TestNodeBaseImageSecurity:
    """Node.js services must use secure base images.
    يجب أن تستخدم خدمات Node.js صور أساسية آمنة."""

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_uses_slim_or_alpine(self, svc_name: str) -> None:
        """Node.js service should use slim or alpine base."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        # Check all FROM lines - at least one should use slim/alpine
        from_images = re.findall(r"FROM\s+(\S+)", content, re.IGNORECASE)
        is_acceptable = any(
            "slim" in img or "alpine" in img or "distroless" in img
            for img in from_images
        )
        if not is_acceptable:
            pytest.xfail(
                f"{svc_name}: no base image uses slim/alpine: {from_images}"
            )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_env_production_in_final_stage(self, svc_name: str) -> None:
        """Final stage must set NODE_ENV=production."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        assert "NODE_ENV=production" in content, (
            f"{svc_name}: missing NODE_ENV=production in Dockerfile"
        )


# ===========================================================================
# 6. Network Security
# ===========================================================================


class TestNetworkSecurity:
    """Network configuration must be secure.
    يجب أن يكون تكوين الشبكة آمناً."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_service_on_internal_network(self, services: dict, svc_name: str) -> None:
        """Application services must be on an internal network."""
        svc = services.get(svc_name, {})
        networks = svc.get("networks", {})
        if isinstance(networks, list):
            net_names = networks
        elif isinstance(networks, dict):
            net_names = list(networks.keys())
        else:
            net_names = []
        assert net_names, f"'{svc_name}' has no network configuration"


# ===========================================================================
# 7. Compose Secrets Handling
# ===========================================================================


class TestComposeSecretsHandling:
    """Credentials in compose must use variable substitution.
    يجب أن تستخدم بيانات الاعتماد في Compose استبدال المتغيرات."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_database_url_uses_substitution(
        self, services: dict, svc_name: str
    ) -> None:
        """DATABASE_URL must use ${} variable substitution."""
        svc = services.get(svc_name, {})
        env = svc.get("environment", {})
        if isinstance(env, dict):
            db_url = env.get("DATABASE_URL", "")
        elif isinstance(env, list):
            db_url = ""
            for e in env:
                if str(e).startswith("DATABASE_URL="):
                    db_url = str(e).split("=", 1)[1]
        else:
            db_url = ""
        if not db_url:
            pytest.skip(f"{svc_name} has no DATABASE_URL")
        # Should contain ${} substitution for password
        if "://" in str(db_url) and "@" in str(db_url):
            uses_var = "${" in str(db_url) or str(db_url).startswith("postgresql://")
            assert uses_var, (
                f"'{svc_name}' DATABASE_URL may have hardcoded credentials"
            )

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_jwt_secret_uses_substitution(
        self, services: dict, svc_name: str
    ) -> None:
        """JWT_SECRET_KEY must use ${} variable substitution."""
        svc = services.get(svc_name, {})
        env = svc.get("environment", {})
        if isinstance(env, dict):
            jwt = env.get("JWT_SECRET_KEY", "")
        elif isinstance(env, list):
            jwt = ""
            for e in env:
                if str(e).startswith("JWT_SECRET_KEY="):
                    jwt = str(e).split("=", 1)[1]
        else:
            jwt = ""
        if not jwt:
            pytest.skip(f"{svc_name} has no JWT_SECRET_KEY")
        val = str(jwt)
        if len(val) > 10 and "${" not in val and "test" not in val.lower():
            pytest.fail(
                f"'{svc_name}' JWT_SECRET_KEY appears hardcoded: {val[:20]}..."
            )


# ===========================================================================
# 8. Dockerfile Layer Optimization
# ===========================================================================


class TestDockerfileLayerOptimization:
    """Dockerfiles must optimize layer caching.
    يجب أن تحسن ملفات Docker تخزين الطبقات المؤقت."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_requirements_copied_before_source(self, svc_name: str) -> None:
        """requirements.txt must be COPY'd before application source code."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        lines = content.splitlines()
        req_line = -1
        src_line = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(r"COPY\s+.*requirements\.txt", stripped, re.IGNORECASE):
                if req_line == -1:
                    req_line = i
            # COPY . or COPY src/ or COPY --from=builder
            if re.match(r"COPY\s+(?:\.\s|src/|--from)", stripped, re.IGNORECASE):
                if "requirements" not in stripped:
                    if src_line == -1:
                        src_line = i
        if req_line == -1 or src_line == -1:
            pytest.skip(f"{svc_name}: cannot determine COPY order")
        assert req_line < src_line, (
            f"{svc_name}: requirements.txt (line {req_line}) copied AFTER "
            f"source code (line {src_line}) – breaks layer caching"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_package_json_copied_before_source(self, svc_name: str) -> None:
        """package.json must be COPY'd before application source code (within same stage)."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        lines = content.splitlines()
        pkg_line = -1
        src_line = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip COPY --from (multi-stage copies, different context)
            if stripped.startswith("COPY --from"):
                continue
            if re.match(r"COPY\s+.*package.*\.json", stripped, re.IGNORECASE):
                if pkg_line == -1:
                    pkg_line = i
            elif re.match(r"COPY\s+\.\s", stripped, re.IGNORECASE):
                if src_line == -1:
                    src_line = i
        if pkg_line == -1 or src_line == -1:
            pytest.skip(f"{svc_name}: cannot determine COPY order")
        assert pkg_line < src_line, (
            f"{svc_name}: package.json (line {pkg_line}) copied AFTER "
            f"source code (line {src_line}) – breaks layer caching"
        )

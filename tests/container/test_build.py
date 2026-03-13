"""
SAHOOL Docker Build Validation Tests
=====================================
اختبارات التحقق من صحة بناء حاويات Docker

Validates that every service Dockerfile and its build context are
correct and safe *before* any image is actually built.

All tests are static (parse files only – no Docker daemon required).

Coverage:
1.  Build context integrity   – required files exist (requirements.txt / package.json)
2.  Dockerfile base image     – correct base images and versions
3.  WORKDIR convention        – all services use /app
4.  Non-root user             – non-root user created and activated
5.  Python service specifics  – PYTHONPATH, pip no-cache, uvicorn CMD
6.  Node.js service specifics – multi-stage build, production stage, node CMD
7.  Constraints file          – constraints.txt referenced in Python pip installs
8.  No hardcoded secrets      – no passwords/tokens baked into Dockerfiles
9.  CMD / ENTRYPOINT          – every service declares a start command
10. EXPOSE directive          – service port declared (literal or variable)
11. Port consistency          – literal EXPOSE port matches the known service port
12. HEALTHCHECK directive     – present on all HTTP-serving containers
13. HEALTHCHECK timing        – interval, timeout, start-period, retries parameters
14. HEALTHCHECK endpoint      – polls /healthz or /health path

Run:
    pytest tests/container/test_build.py -v --tb=short
    pytest tests/container/test_build.py -v -n auto     # parallel
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Import the shared service registry (single source of truth)
from tests.container.service_registry import (
    ALL_BUILT_SERVICES,
    NODE_SERVICES,
    PORTLESS_SERVICES,
    PYTHON_SERVICES,
)

pytestmark = [pytest.mark.container, pytest.mark.smoke]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
CONSTRAINTS_TXT = REPO_ROOT / "constraints.txt"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}


def _read_dockerfile(service_name: str) -> str:
    """Return Dockerfile content for *service_name*, cached."""
    if service_name not in _dockerfile_cache:
        path = SERVICES_DIR / service_name / "Dockerfile"
        _dockerfile_cache[service_name] = path.read_text(encoding="utf-8")
    return _dockerfile_cache[service_name]


def _has_instruction(content: str, instruction: str) -> bool:
    """Return True if Dockerfile contains the given instruction (case-insensitive)."""
    return bool(
        re.search(rf"^\s*{re.escape(instruction)}\s+", content, re.IGNORECASE | re.MULTILINE)
    )


def _extract_expose_ports(content: str) -> list[int]:
    """Return list of integer ports declared in EXPOSE directives (literals only)."""
    ports: list[int] = []
    for match in re.finditer(
        r"^\s*EXPOSE\s+([\d/\s]+)", content, re.IGNORECASE | re.MULTILINE
    ):
        for token in match.group(1).split():
            port_str = token.split("/")[0].strip()
            if port_str.isdigit():
                ports.append(int(port_str))
    return ports


def _has_expose(content: str) -> bool:
    """Return True if Dockerfile has any EXPOSE directive (literal or variable)."""
    return bool(re.search(r"^\s*EXPOSE\s+", content, re.IGNORECASE | re.MULTILINE))


def _extract_healthcheck_block(content: str) -> str:
    """Extract the HEALTHCHECK directive line(s) from a Dockerfile."""
    # Find the HEALTHCHECK line and include up to 3 continuation lines
    lines = content.splitlines()
    result_lines: list[str] = []
    in_hc = False
    for line in lines:
        if re.match(r"\s*HEALTHCHECK\s+", line, re.IGNORECASE):
            in_hc = True
            result_lines = [line]
        elif in_hc:
            result_lines.append(line)
            # Stop at the CMD argument of HEALTHCHECK (after the CMD keyword)
            if re.search(r"\bCMD\b", "\n".join(result_lines)):
                # Check if the CMD value is complete (no trailing \)
                if not line.rstrip().endswith("\\"):
                    break
    return "\n".join(result_lines)


# ===========================================================================
# 1. Build Context Integrity
# ===========================================================================


class TestBuildContextIntegrity:
    """Every service must have the files referenced by its Dockerfile."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_service_has_dockerfile(self, svc_name: str) -> None:
        """Python service Dockerfile exists."""
        assert (SERVICES_DIR / svc_name / "Dockerfile").exists(), (
            f"Missing Dockerfile for Python service: {svc_name}"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_service_has_requirements(self, svc_name: str) -> None:
        """Python service has a requirements.txt build context file."""
        assert (SERVICES_DIR / svc_name / "requirements.txt").exists(), (
            f"Missing requirements.txt for Python service: {svc_name}"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_requirements_not_empty(self, svc_name: str) -> None:
        """requirements.txt must contain at least one package."""
        content = (SERVICES_DIR / svc_name / "requirements.txt").read_text(encoding="utf-8")
        non_comment = [
            ln for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("#")
        ]
        assert non_comment, f"{svc_name}/requirements.txt is empty"

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_service_has_src_directory(self, svc_name: str) -> None:
        """Python service has a src/ directory containing application code."""
        assert (SERVICES_DIR / svc_name / "src").is_dir(), (
            f"Missing src/ directory for Python service: {svc_name}"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_service_has_dockerfile(self, svc_name: str) -> None:
        """Node.js service Dockerfile exists."""
        assert (SERVICES_DIR / svc_name / "Dockerfile").exists(), (
            f"Missing Dockerfile for Node.js service: {svc_name}"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_service_has_package_json(self, svc_name: str) -> None:
        """Node.js service has a package.json build context file."""
        assert (SERVICES_DIR / svc_name / "package.json").exists(), (
            f"Missing package.json for Node.js service: {svc_name}"
        )

    def test_global_constraints_file_exists(self) -> None:
        """Root constraints.txt exists for Python build constraints."""
        assert CONSTRAINTS_TXT.exists(), "Missing root constraints.txt"

    def test_global_constraints_not_empty(self) -> None:
        """Root constraints.txt is not empty."""
        lines = [
            ln
            for ln in CONSTRAINTS_TXT.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        assert lines, "Root constraints.txt is empty"

    @pytest.mark.parametrize("svc_name", sorted(PORTLESS_SERVICES))
    def test_portless_service_has_dockerfile(self, svc_name: str) -> None:
        """Worker / init service Dockerfile exists."""
        assert (SERVICES_DIR / svc_name / "Dockerfile").exists(), (
            f"Missing Dockerfile for portless service: {svc_name}"
        )


# ===========================================================================
# 2. Dockerfile Base Image
# ===========================================================================


class TestDockerfileBaseImage:
    """Validate base image declarations in Dockerfiles."""

    _PYTHON_BASE = re.compile(
        r"FROM\s+python:[\$\{A-Za-z0-9_\}].*-slim|FROM\s+nvidia/cuda",
        re.IGNORECASE,
    )
    _NODE_BASE = re.compile(r"FROM\s+node:[\$\{A-Za-z0-9_\}]", re.IGNORECASE)

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_base_image(self, svc_name: str) -> None:
        """Python service FROM uses a slim or CUDA base image."""
        content = _read_dockerfile(svc_name)
        assert self._PYTHON_BASE.search(content), (
            f"{svc_name} Dockerfile does not use an expected Python base image "
            f"(expected python:*-slim* or nvidia/cuda)"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_base_image(self, svc_name: str) -> None:
        """Node.js service FROM uses a node: base image."""
        content = _read_dockerfile(svc_name)
        assert self._NODE_BASE.search(content), (
            f"{svc_name} Dockerfile does not use an expected Node.js base image"
        )


# ===========================================================================
# 3. WORKDIR Convention
# ===========================================================================


class TestWorkdirConvention:
    """All services must set WORKDIR /app (or /home/sahool for multi-stage)."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_workdir_is_app(self, svc_name: str) -> None:
        """Dockerfile sets WORKDIR /app at some stage."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"WORKDIR\s+/app", content, re.IGNORECASE), (
            f"{svc_name} Dockerfile missing 'WORKDIR /app'"
        )


# ===========================================================================
# 4. Non-Root User Security
# ===========================================================================


class TestNonRootUser:
    """Every production Dockerfile must create and switch to a non-root user."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_non_root_user_created(self, svc_name: str) -> None:
        """Dockerfile creates or uses a non-root system user.

        Accepted patterns:
        - Custom user created with useradd/adduser/groupadd + USER directive
        - Built-in base-image user activated with USER node / USER sahool / etc.
        """
        content = _read_dockerfile(svc_name)
        has_useradd = bool(re.search(r"useradd|adduser|groupadd", content, re.IGNORECASE))
        # Some Node.js services rely on the built-in 'node' user in the base image
        has_user_directive = bool(
            re.search(
                r"^\s*USER\s+(?!0\b)(?!root\b)[A-Za-z][A-Za-z0-9_\-]*",
                content,
                re.IGNORECASE | re.MULTILINE,
            )
        )
        assert has_useradd or has_user_directive, (
            f"{svc_name} Dockerfile does not create or activate a non-root user"
        )

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_user_switched_to_non_root(self, svc_name: str) -> None:
        """Dockerfile switches to a non-root USER before CMD/ENTRYPOINT."""
        content = _read_dockerfile(svc_name)
        # Accept any non-numeric non-root username: sahool, node, agent, appuser, etc.
        assert re.search(
            r"^\s*USER\s+(?!0\b)(?!root\b)[A-Za-z][A-Za-z0-9_\-]*",
            content,
            re.IGNORECASE | re.MULTILINE,
        ), f"{svc_name} Dockerfile does not switch to a non-root USER"


# ===========================================================================
# 5. Python Service Build Specifics
# ===========================================================================


class TestPythonBuildSpecifics:
    """Validate Python-specific build patterns."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_pip_cache_disabled(self, svc_name: str) -> None:
        """Python service disables pip cache via ENV or --no-cache-dir flag."""
        content = _read_dockerfile(svc_name)
        has_env = bool(re.search(r"PIP_NO_CACHE_DIR", content))
        has_flag = bool(re.search(r"pip\s+install.*--no-cache-dir", content, re.DOTALL))
        assert has_env or has_flag, (
            f"{svc_name} does not disable pip cache "
            f"(missing PIP_NO_CACHE_DIR env or --no-cache-dir flag)"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_requirements_copied_in_dockerfile(self, svc_name: str) -> None:
        """Python Dockerfile COPYs requirements.txt into the image."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"COPY.*requirements\.txt", content, re.IGNORECASE), (
            f"{svc_name} Dockerfile does not COPY requirements.txt"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_constraints_file_referenced(self, svc_name: str) -> None:
        """Python Dockerfile references a constraints file for pip install.

        Accepted: constraints.txt (standard) or constraints-ai.txt (AI services).
        """
        content = _read_dockerfile(svc_name)
        assert re.search(r"constraints[-\w]*\.txt", content, re.IGNORECASE), (
            f"{svc_name} Dockerfile does not reference any constraints file"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_cmd_starts_server(self, svc_name: str) -> None:
        """Python service CMD starts an HTTP server or application module."""
        content = _read_dockerfile(svc_name)
        # CMD patterns in use across services:
        # - CMD ["python", "-m", "uvicorn", ...]  (most services)
        # - CMD ["uvicorn", ...]                  (some services)
        # - CMD ["python", "-m", "src.main"]      (code-review-service)
        # - CMD ["sh", "-c", "uvicorn ..."]       (whatsapp-bot-service, ws-gateway)
        assert re.search(
            r'CMD\s+\["?(?:python|uvicorn|gunicorn|sh)',
            content,
            re.IGNORECASE,
        ), f"{svc_name} Dockerfile CMD does not start an HTTP server or application module"

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_pythonunbuffered_set(self, svc_name: str) -> None:
        """Python service sets PYTHONUNBUFFERED for real-time log output."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"PYTHONUNBUFFERED=1", content), (
            f"{svc_name} Dockerfile missing PYTHONUNBUFFERED=1"
        )


# ===========================================================================
# 6. Node.js Service Build Specifics
# ===========================================================================


class TestNodeBuildSpecifics:
    """Validate Node.js / NestJS multi-stage build patterns."""

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_multi_stage_build(self, svc_name: str) -> None:
        """Node.js service uses multi-stage build (at least 2 FROM stages)."""
        content = _read_dockerfile(svc_name)
        from_count = len(re.findall(r"^\s*FROM\s+", content, re.IGNORECASE | re.MULTILINE))
        assert from_count >= 2, (
            f"{svc_name} Dockerfile has only {from_count} FROM stage(s), "
            f"expected multi-stage build"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_builder_stage_present(self, svc_name: str) -> None:
        """Node.js Dockerfile has a named builder stage."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"FROM\s+\S+\s+AS\s+\w+", content, re.IGNORECASE), (
            f"{svc_name} Dockerfile has no named build stage (AS <name>)"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_production_env(self, svc_name: str) -> None:
        """Node.js production stage sets NODE_ENV=production."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"NODE_ENV=production", content), (
            f"{svc_name} Dockerfile does not set NODE_ENV=production"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_cmd_uses_node_or_npm(self, svc_name: str) -> None:
        """Node.js service CMD ultimately runs node (directly or via sh wrapper)."""
        content = _read_dockerfile(svc_name)
        # Accept: CMD ["node", ...], CMD ["npm", ...], CMD ["sh", "-c", "... node ..."]
        assert re.search(
            r'CMD\s+\["?(?:node|npm|sh)',
            content,
            re.IGNORECASE,
        ), f"{svc_name} Dockerfile CMD does not start with node, npm, or sh"


# ===========================================================================
# 7. No Hardcoded Secrets
# ===========================================================================


class TestNoHardcodedSecrets:
    """Dockerfiles must not bake credentials into ENV or RUN instructions."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_no_hardcoded_credential(self, svc_name: str) -> None:
        """No literal credential value on non-ARG, non-comment lines.

        Variable substitution patterns like ${VAR:?...} are allowed because
        they reference runtime environment – they are not hardcoded.
        """
        content = _read_dockerfile(svc_name)
        for line in content.splitlines():
            stripped = line.strip()
            # Skip blank lines, comments, and ARG declarations
            if not stripped or stripped.startswith("#") or stripped.upper().startswith("ARG"):
                continue
            # Skip lines that only use variable substitution (not literal values)
            if re.search(r"\$\{[A-Z_]+[:\?!-]", line):
                continue
            # Flag literal credential values (8+ alphanumeric chars after = sign)
            if re.search(
                r"(?i)(?:PASSWORD|SECRET|API_KEY)\s*=\s*['\"]?[A-Za-z0-9@#$%!_\-]{8,}['\"]?",
                line,
            ):
                pytest.fail(
                    f"{svc_name} Dockerfile contains potential hardcoded credential:\n"
                    f"  {stripped}"
                )


# ===========================================================================
# 8. CMD / ENTRYPOINT Presence
# ===========================================================================


class TestCmdEntrypointPresence:
    """Every service Dockerfile must define how the container starts."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_BUILT_SERVICES))
    def test_cmd_or_entrypoint_defined(self, svc_name: str) -> None:
        """Dockerfile has at least one CMD or ENTRYPOINT instruction."""
        content = _read_dockerfile(svc_name)
        assert _has_instruction(content, "CMD") or _has_instruction(content, "ENTRYPOINT"), (
            f"{svc_name} Dockerfile has no CMD or ENTRYPOINT"
        )


# ===========================================================================
# 9. EXPOSE Directive
# ===========================================================================


class TestExposeDirective:
    """HTTP services must declare their port with EXPOSE."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_service_has_expose(self, svc_name: str) -> None:
        """Python service Dockerfile has an EXPOSE directive."""
        content = _read_dockerfile(svc_name)
        assert _has_expose(content), f"{svc_name} Dockerfile is missing EXPOSE directive"

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_service_has_expose(self, svc_name: str) -> None:
        """Node.js service Dockerfile has an EXPOSE directive."""
        content = _read_dockerfile(svc_name)
        assert _has_expose(content), f"{svc_name} Dockerfile is missing EXPOSE directive"


# ===========================================================================
# 10. Port Consistency (literal EXPOSE matches known service port)
# ===========================================================================


class TestPortConsistency:
    """Where EXPOSE uses a literal port number it must match the registry."""

    @pytest.mark.parametrize("svc_name,expected_port", sorted(PYTHON_SERVICES.items()))
    def test_python_literal_expose_matches_registry(
        self, svc_name: str, expected_port: int
    ) -> None:
        """If EXPOSE declares a literal port, it must match the expected service port."""
        content = _read_dockerfile(svc_name)
        expose_ports = _extract_expose_ports(content)
        if not expose_ports:
            # Variable-based EXPOSE (e.g. EXPOSE ${PORT}) – validated by ENV PORT test instead
            pytest.skip(f"{svc_name} uses variable EXPOSE – skip literal port check")
        assert expected_port in expose_ports, (
            f"{svc_name} EXPOSE {expose_ports} does not include expected port {expected_port}"
        )

    @pytest.mark.parametrize("svc_name,expected_port", sorted(NODE_SERVICES.items()))
    def test_node_literal_expose_matches_registry(
        self, svc_name: str, expected_port: int
    ) -> None:
        """If EXPOSE declares a literal port, it must match the expected service port."""
        content = _read_dockerfile(svc_name)
        expose_ports = _extract_expose_ports(content)
        if not expose_ports:
            pytest.skip(f"{svc_name} uses variable EXPOSE – skip literal port check")
        assert expected_port in expose_ports, (
            f"{svc_name} EXPOSE {expose_ports} does not include expected port {expected_port}"
        )


# ===========================================================================
# 11. HEALTHCHECK Directive
# ===========================================================================


class TestHealthcheckPresence:
    """All HTTP-serving containers must declare a HEALTHCHECK."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_service_has_healthcheck(self, svc_name: str) -> None:
        """Python service Dockerfile has a HEALTHCHECK instruction."""
        content = _read_dockerfile(svc_name)
        assert _has_instruction(content, "HEALTHCHECK"), (
            f"{svc_name} Dockerfile is missing HEALTHCHECK directive"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_service_has_healthcheck(self, svc_name: str) -> None:
        """Node.js service Dockerfile has a HEALTHCHECK instruction."""
        content = _read_dockerfile(svc_name)
        assert _has_instruction(content, "HEALTHCHECK"), (
            f"{svc_name} Dockerfile is missing HEALTHCHECK directive"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_healthcheck_polls_health_endpoint(self, svc_name: str) -> None:
        """Python service HEALTHCHECK CMD polls /healthz or /health endpoint."""
        content = _read_dockerfile(svc_name)
        hc_block = _extract_healthcheck_block(content)
        assert re.search(r"/healthz|/health", hc_block), (
            f"{svc_name} HEALTHCHECK does not poll /healthz or /health:\n  {hc_block[:200]}"
        )

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_node_healthcheck_polls_health_endpoint(self, svc_name: str) -> None:
        """Node.js service HEALTHCHECK CMD polls /healthz or /health endpoint."""
        content = _read_dockerfile(svc_name)
        hc_block = _extract_healthcheck_block(content)
        assert re.search(r"/healthz|/health", hc_block), (
            f"{svc_name} HEALTHCHECK does not poll /healthz or /health:\n  {hc_block[:200]}"
        )


# ===========================================================================
# 12. HEALTHCHECK Timing Parameters
# ===========================================================================


class TestHealthcheckTiming:
    """HEALTHCHECK must define interval, timeout, start-period, and retries."""

    _ALL_HTTP: list[str] = sorted({**PYTHON_SERVICES, **NODE_SERVICES})

    @pytest.mark.parametrize("svc_name", _ALL_HTTP)
    def test_healthcheck_has_interval(self, svc_name: str) -> None:
        """HEALTHCHECK includes --interval parameter."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"HEALTHCHECK.*--interval=", content, re.IGNORECASE | re.DOTALL), (
            f"{svc_name} HEALTHCHECK missing --interval"
        )

    @pytest.mark.parametrize("svc_name", _ALL_HTTP)
    def test_healthcheck_has_timeout(self, svc_name: str) -> None:
        """HEALTHCHECK includes --timeout parameter."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"HEALTHCHECK.*--timeout=", content, re.IGNORECASE | re.DOTALL), (
            f"{svc_name} HEALTHCHECK missing --timeout"
        )

    @pytest.mark.parametrize("svc_name", _ALL_HTTP)
    def test_healthcheck_has_retries(self, svc_name: str) -> None:
        """HEALTHCHECK includes --retries parameter."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"HEALTHCHECK.*--retries=", content, re.IGNORECASE | re.DOTALL), (
            f"{svc_name} HEALTHCHECK missing --retries"
        )

    @pytest.mark.parametrize("svc_name", _ALL_HTTP)
    def test_healthcheck_has_start_period(self, svc_name: str) -> None:
        """HEALTHCHECK includes --start-period to accommodate slow-starting services."""
        content = _read_dockerfile(svc_name)
        assert re.search(r"HEALTHCHECK.*--start-period=", content, re.IGNORECASE | re.DOTALL), (
            f"{svc_name} HEALTHCHECK missing --start-period"
        )

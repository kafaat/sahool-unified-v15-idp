"""
SAHOOL Cross-Service Contract Validation Tests
================================================
اختبارات التحقق من اتساق العقود بين الخدمات

Static analysis tests that validate consistency of ports, events, API
contracts, health endpoints, and service registry entries across all
microservices. No Docker daemon or running services required.

Coverage:
1.  Port consistency       – ports match across compose, Dockerfile, registry, governance
2.  NATS event conventions – subject naming, no hardcoded tenants, constant usage
3.  Health endpoints       – /healthz and /readyz present, patterns correct
4.  API version consistency – /api/v1/ convention, no mixed versions
5.  Service registry       – governance/services.yaml completeness vs service_registry.py
6.  Docker Compose files   – consistency across yml, test, prod compose files

Run:
    pytest tests/container/test_cross_service_contracts.py -v --tb=short
    pytest tests/container/test_cross_service_contracts.py -v -n auto   # parallel
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.container.service_registry import (
    ALL_BUILT_SERVICES,
    ALL_HTTP_SERVICES,
    INFRA_SERVICES,
    NODE_SERVICES,
    PORTLESS_SERVICES,
    PYTHON_SERVICES,
)

pytestmark = [pytest.mark.container, pytest.mark.smoke]

# ---------------------------------------------------------------------------
# Paths - المسارات
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"
TEST_COMPOSE = REPO_ROOT / "docker-compose.test.yml"
PROD_COMPOSE = REPO_ROOT / "docker-compose.prod.yml"
SERVICES_DIR = REPO_ROOT / "apps" / "services"
GOVERNANCE_YAML = REPO_ROOT / "governance" / "services.yaml"
SERVICE_PORTS_TS = (
    REPO_ROOT / "packages" / "shared-types" / "src" / "contracts" / "service-ports.ts"
)
EVENTS_SUBJECTS_PY = REPO_ROOT / "shared" / "events" / "subjects.py"

# ---------------------------------------------------------------------------
# Caches - ذاكرة التخزين المؤقت
# ---------------------------------------------------------------------------

_compose_cache: dict[str, dict[str, Any]] = {}
_dockerfile_cache: dict[str, str] = {}
_governance_cache: dict[str, Any] | None = None


def _load_compose(path: Path) -> dict[str, Any]:
    """Load a docker-compose YAML file, cached.
    تحميل ملف docker-compose مع التخزين المؤقت."""
    key = str(path)
    if key not in _compose_cache:
        if not path.exists():
            _compose_cache[key] = {}
        else:
            with open(path, encoding="utf-8") as fh:
                _compose_cache[key] = yaml.safe_load(fh) or {}
    return _compose_cache[key]


def _read_dockerfile(service_name: str) -> str | None:
    """Return Dockerfile content for a service, or None if missing.
    قراءة محتوى Dockerfile للخدمة أو إرجاع None."""
    if service_name not in _dockerfile_cache:
        path = SERVICES_DIR / service_name / "Dockerfile"
        if path.exists():
            _dockerfile_cache[service_name] = path.read_text(encoding="utf-8")
        else:
            _dockerfile_cache[service_name] = ""
    content = _dockerfile_cache[service_name]
    return content if content else None


def _load_governance() -> dict[str, Any]:
    """Load governance/services.yaml, cached.
    تحميل ملف سجل الخدمات المعتمدة."""
    global _governance_cache  # noqa: PLW0603
    if _governance_cache is None:
        if GOVERNANCE_YAML.exists():
            with open(GOVERNANCE_YAML, encoding="utf-8") as fh:
                _governance_cache = yaml.safe_load(fh) or {}
        else:
            _governance_cache = {}
    return _governance_cache


def _extract_expose_ports(content: str) -> list[int]:
    """Extract literal integer ports from EXPOSE directives.
    استخراج أرقام المنافذ من تعليمات EXPOSE."""
    ports: list[int] = []
    for match in re.finditer(
        r"^\s*EXPOSE\s+(.+)", content, re.MULTILINE | re.IGNORECASE
    ):
        for token in match.group(1).split():
            token = token.strip()
            if token.isdigit():
                ports.append(int(token))
    return ports


def _extract_env_port(content: str) -> int | None:
    """Extract PORT=XXXX from ENV directives in a Dockerfile.
    استخراج قيمة PORT من متغيرات البيئة في Dockerfile."""
    for match in re.finditer(
        r"^\s*ENV\s+.*?\bPORT[=\s]+(\d+)", content, re.MULTILINE | re.IGNORECASE
    ):
        return int(match.group(1))
    return None


def _extract_compose_container_port(service_cfg: dict) -> int | None:
    """Extract the container-side port from a compose service's ports list.
    استخراج منفذ الحاوية من تعريف ports في docker-compose."""
    for port_entry in service_cfg.get("ports", []):
        port_str = str(port_entry)
        parts = port_str.split(":")
        container_part = parts[-1]
        var_match = re.search(r"\$\{[^}]*:-(\d+)\}", container_part)
        if var_match:
            return int(var_match.group(1))
        if container_part.strip().isdigit():
            return int(container_part.strip())
    return None


def _extract_compose_env_port(service_cfg: dict) -> int | None:
    """Extract PORT= value from compose environment list/dict.
    استخراج قيمة PORT من متغيرات البيئة في docker-compose."""
    env = service_cfg.get("environment", [])
    if isinstance(env, dict):
        val = env.get("PORT")
        if val is not None:
            val_str = str(val)
            if val_str.isdigit():
                return int(val_str)
        return None
    if isinstance(env, list):
        for entry in env:
            entry_str = str(entry)
            match = re.match(r"^PORT=(\d+)$", entry_str)
            if match:
                return int(match.group(1))
    return None


def _get_python_src_files(service_name: str) -> list[Path]:
    """Return all .py files under a service's src/ directory.
    إرجاع جميع ملفات Python في مجلد src/ للخدمة."""
    src_dir = SERVICES_DIR / service_name / "src"
    if not src_dir.exists():
        return []
    return list(src_dir.rglob("*.py"))


def _extract_healthcheck_path(content: str) -> str | None:
    """Extract the health endpoint path from a Dockerfile HEALTHCHECK directive.
    استخراج مسار نقطة فحص الصحة من Dockerfile.

    Handles multi-line HEALTHCHECK directives where the CMD is on a
    continuation line (backslash + newline)."""
    collapsed = content.replace("\\\n", " ")
    match = re.search(
        r"HEALTHCHECK\s+.*?(?:curl|wget)\s+.*?https?://[^/\s]+((?:/[\w.-]+)+)",
        collapsed,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)
    return None


# ===========================================================================
# 1. TestPortConsistencyAcrossFiles
#    التحقق من اتساق المنافذ عبر جميع الملفات
# ===========================================================================


class TestPortConsistencyAcrossFiles:
    """Validate port number consistency across all configuration files.
    التحقق من اتساق أرقام المنافذ عبر جميع ملفات التكوين."""

    @pytest.mark.parametrize("service,expected_port", sorted(ALL_HTTP_SERVICES.items()))
    def test_compose_port_matches_registry(
        self, service: str, expected_port: int
    ) -> None:
        """Port in docker-compose.yml must match service_registry.py.
        يجب أن يتطابق المنفذ في docker-compose.yml مع سجل الخدمات."""
        compose = _load_compose(MAIN_COMPOSE)
        compose_services = compose.get("services", {})
        if service not in compose_services:
            pytest.skip(f"{service} not in docker-compose.yml")

        container_port = _extract_compose_container_port(compose_services[service])
        if container_port is None:
            pytest.skip(f"{service} has no port mapping in compose")

        assert container_port == expected_port, (
            f"{service}: compose container port {container_port} "
            f"!= registry port {expected_port}"
        )

    @pytest.mark.parametrize("service,expected_port", sorted(ALL_HTTP_SERVICES.items()))
    def test_dockerfile_expose_matches_compose(
        self, service: str, expected_port: int
    ) -> None:
        """Dockerfile EXPOSE must match docker-compose.yml port mapping.
        يجب أن يتطابق EXPOSE في Dockerfile مع تعيين المنفذ في docker-compose."""
        content = _read_dockerfile(service)
        if content is None:
            pytest.skip(f"No Dockerfile for {service}")

        exposed = _extract_expose_ports(content)
        if not exposed:
            pytest.skip(f"{service} uses variable EXPOSE (not literal)")

        assert expected_port in exposed, (
            f"{service}: expected port {expected_port} not in "
            f"EXPOSE ports {exposed}"
        )

    @pytest.mark.parametrize("service,expected_port", sorted(ALL_HTTP_SERVICES.items()))
    def test_dockerfile_env_port_matches_expose(
        self, service: str, expected_port: int
    ) -> None:
        """PORT env var in Dockerfile must match EXPOSE directive.
        يجب أن يتطابق متغير PORT في Dockerfile مع تعليمة EXPOSE."""
        content = _read_dockerfile(service)
        if content is None:
            pytest.skip(f"No Dockerfile for {service}")

        env_port = _extract_env_port(content)
        if env_port is None:
            pytest.skip(f"{service} has no ENV PORT in Dockerfile")

        exposed = _extract_expose_ports(content)
        if not exposed:
            assert env_port == expected_port, (
                f"{service}: ENV PORT={env_port} != registry port {expected_port}"
            )
        else:
            assert env_port in exposed, (
                f"{service}: ENV PORT={env_port} not in EXPOSE {exposed}"
            )

    def test_no_duplicate_ports_in_registry(self) -> None:
        """No two services may share the same port number.
        لا يجوز لخدمتين مشاركة نفس رقم المنفذ."""
        port_counts = Counter(ALL_HTTP_SERVICES.values())
        duplicates = {
            port: count for port, count in port_counts.items() if count > 1
        }
        if duplicates:
            details: dict[int, list[str]] = {}
            for svc, port in ALL_HTTP_SERVICES.items():
                if port in duplicates:
                    details.setdefault(port, []).append(svc)
            pytest.fail(f"Duplicate ports detected: {details}")

    @pytest.mark.parametrize("service,expected_port", sorted(ALL_HTTP_SERVICES.items()))
    def test_governance_port_matches_registry(
        self, service: str, expected_port: int
    ) -> None:
        """Port in governance/services.yaml must match service_registry.py.
        يجب أن يتطابق المنفذ في سجل الحوكمة مع سجل الخدمات."""
        gov = _load_governance()
        gov_services = gov.get("services", {})
        if service not in gov_services:
            pytest.skip(f"{service} not in governance/services.yaml")

        gov_info = gov_services[service]
        if not isinstance(gov_info, dict):
            pytest.skip(f"{service} has no structured entry in governance")

        gov_port = gov_info.get("port")
        if gov_port is None:
            pytest.skip(f"{service} has port=null in governance")

        assert int(gov_port) == expected_port, (
            f"{service}: governance port {gov_port} "
            f"!= registry port {expected_port}"
        )

    @pytest.mark.parametrize("service,expected_port", sorted(ALL_HTTP_SERVICES.items()))
    def test_compose_env_port_matches_container_port(
        self, service: str, expected_port: int
    ) -> None:
        """PORT env var in docker-compose.yml must match its port mapping.
        يجب أن يتطابق متغير PORT في docker-compose مع تعيين المنفذ."""
        compose = _load_compose(MAIN_COMPOSE)
        compose_services = compose.get("services", {})
        if service not in compose_services:
            pytest.skip(f"{service} not in docker-compose.yml")

        env_port = _extract_compose_env_port(compose_services[service])
        if env_port is None:
            pytest.skip(f"{service} has no PORT= in compose environment")

        assert env_port == expected_port, (
            f"{service}: compose ENV PORT={env_port} "
            f"!= registry port {expected_port}"
        )


# ===========================================================================
# 2. TestNATSEventSubjectConventions
#    التحقق من اتفاقيات تسمية موضوعات أحداث NATS
# ===========================================================================


class TestNATSEventSubjectConventions:
    """Validate NATS event subject naming conventions across services.
    التحقق من اتفاقيات تسمية موضوعات أحداث NATS عبر الخدمات."""

    HARDCODED_UUID_RE = re.compile(
        r'sahool\.[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\.'
    )

    PUBLISH_INLINE_RE = re.compile(
        r'\.(?:publish|subscribe|request)\(\s*f?["\']([^"\']+)["\']'
    )

    def test_shared_events_subjects_file_exists(self) -> None:
        """shared/events/subjects.py must exist and define subject constants.
        يجب أن يوجد ملف ثوابت الموضوعات ويحتوي على تعريفات."""
        assert EVENTS_SUBJECTS_PY.exists(), (
            f"Missing {EVENTS_SUBJECTS_PY.relative_to(REPO_ROOT)} - "
            "event subjects must be centralized"
        )
        content = EVENTS_SUBJECTS_PY.read_text(encoding="utf-8")
        assert "SAHOOL_" in content, (
            "subjects.py must define SAHOOL_* constants"
        )

    def test_subject_constants_follow_naming_pattern(self) -> None:
        """Subject values in subjects.py must follow sahool.{domain}.{action}.
        يجب أن تتبع قيم الموضوعات نمط sahool.{domain}.{action}."""
        if not EVENTS_SUBJECTS_PY.exists():
            pytest.skip("subjects.py not found")

        content = EVENTS_SUBJECTS_PY.read_text(encoding="utf-8")
        assignments = re.findall(
            r'^(SAHOOL_\w+)\s*=\s*["\']([^"\']+)["\']',
            content,
            re.MULTILINE,
        )
        assert len(assignments) > 0, "No SAHOOL_* constants found in subjects.py"

        # Allow versioned subjects (.v1), NATS wildcards (*, >), multi-segment
        base_pattern = re.compile(r'^sahool\.[a-z_]+(?:\.[a-z0-9_*>]+){1,5}$')
        invalid: list[tuple[str, str]] = []
        for name, value in assignments:
            if not base_pattern.match(value):
                invalid.append((name, value))

        assert not invalid, (
            f"Subject constants with invalid format: {invalid}. "
            f"Expected pattern: sahool.{{domain}}.{{action}}"
        )

    @pytest.mark.parametrize(
        "service",
        [s for s in sorted(PYTHON_SERVICES) if (SERVICES_DIR / s / "src").is_dir()],
    )
    def test_no_hardcoded_tenant_ids_in_subjects(self, service: str) -> None:
        """No hardcoded tenant UUIDs in NATS subject strings.
        لا يجوز كتابة معرفات المستأجرين مباشرة في موضوعات NATS."""
        src_files = _get_python_src_files(service)
        if not src_files:
            pytest.skip(f"{service} has no src/ Python files")

        violations: list[str] = []
        for py_file in src_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for line_no, line in enumerate(content.splitlines(), 1):
                if self.HARDCODED_UUID_RE.search(line):
                    rel = py_file.relative_to(REPO_ROOT)
                    violations.append(f"{rel}:{line_no}")

        assert not violations, (
            f"{service}: hardcoded tenant UUID in subject at: {violations}"
        )

    @pytest.mark.parametrize(
        "service",
        [s for s in sorted(PYTHON_SERVICES) if (SERVICES_DIR / s / "src").is_dir()],
    )
    def test_event_subjects_prefer_constants(self, service: str) -> None:
        """NATS publish/subscribe should use constants, not inline strings.
        يفضل استخدام الثوابت بدلا من النصوص المباشرة في النشر والاشتراك."""
        src_files = _get_python_src_files(service)
        if not src_files:
            pytest.skip(f"{service} has no src/ Python files")

        inline_subjects: list[str] = []
        for py_file in src_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for line_no, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                matches = self.PUBLISH_INLINE_RE.findall(line)
                for subject in matches:
                    if subject.startswith("sahool.") and not subject.startswith("sahool.{"):
                        rel = py_file.relative_to(REPO_ROOT)
                        inline_subjects.append(f"{rel}:{line_no} -> '{subject}'")

        if inline_subjects:
            pytest.xfail(
                f"{service}: {len(inline_subjects)} inline subject string(s) found "
                f"(prefer constants from shared.events.subjects): "
                f"{inline_subjects[:5]}"
            )


# ===========================================================================
# 3. TestHealthEndpointConsistency
#    التحقق من وجود واتساق نقاط فحص الصحة
# ===========================================================================


class TestHealthEndpointConsistency:
    """Validate health endpoint presence and consistency for all services.
    التحقق من وجود واتساق نقاط فحص الصحة لجميع الخدمات."""

    HEALTHZ_PATTERNS = [
        re.compile(r"""['"]/?healthz['"]""", re.IGNORECASE),
        re.compile(r"""['"]/?health['"]""", re.IGNORECASE),
    ]

    READYZ_PATTERNS = [
        re.compile(r"""['"]/?readyz['"]""", re.IGNORECASE),
    ]

    # Matches various status patterns used across services
    STATUS_OK_PATTERN = re.compile(
        r"""(?:["']status["']\s*:\s*["']|status\s*=\s*["'])"""
        r"""(?:ok|healthy|up|running|available)["']"""
        r"""|return\s*\{[^}]*["'](?:status|ok|healthy)["']"""
        r"""|["'](?:ok|healthy)["']""",
        re.IGNORECASE,
    )

    def _all_py_files(self, service: str) -> list[Path]:
        """Get all Python files for a service (src/ and root main.py).
        الحصول على جميع ملفات Python للخدمة."""
        files = _get_python_src_files(service)
        root_main = SERVICES_DIR / service / "main.py"
        if root_main.exists():
            files.append(root_main)
        return files

    @pytest.mark.parametrize("service", sorted(PYTHON_SERVICES))
    def test_python_service_has_healthz(self, service: str) -> None:
        """Every Python service must define a /healthz endpoint.
        يجب أن تعرف كل خدمة Python نقطة /healthz."""
        all_files = self._all_py_files(service)
        if not all_files:
            pytest.skip(f"{service} has no Python source files")

        found = False
        for py_file in all_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if any(p.search(content) for p in self.HEALTHZ_PATTERNS):
                found = True
                break

        assert found, f"{service}: no /healthz or /health endpoint found in source files"

    @pytest.mark.parametrize("service", sorted(PYTHON_SERVICES))
    def test_python_service_has_readyz(self, service: str) -> None:
        """Every Python service should define a /readyz endpoint.
        يجب أن تعرف كل خدمة Python نقطة /readyz."""
        all_files = self._all_py_files(service)
        if not all_files:
            pytest.skip(f"{service} has no Python source files")

        found = False
        for py_file in all_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if any(p.search(content) for p in self.READYZ_PATTERNS):
                found = True
                break

        if not found:
            pytest.xfail(f"{service}: no /readyz endpoint found (recommended)")

    @pytest.mark.parametrize("service", sorted(PYTHON_SERVICES))
    def test_health_returns_status_ok(self, service: str) -> None:
        """Health endpoint must return status ok or healthy pattern.
        يجب أن ترجع نقطة الصحة نمط status ok او healthy."""
        all_files = self._all_py_files(service)
        if not all_files:
            pytest.skip(f"{service} has no Python source files")

        has_healthz = False
        has_status_ok = False
        for py_file in all_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if any(p.search(content) for p in self.HEALTHZ_PATTERNS):
                has_healthz = True
                if self.STATUS_OK_PATTERN.search(content):
                    has_status_ok = True
                    break

        if not has_healthz:
            pytest.skip(f"{service} has no healthz endpoint to check")

        assert has_status_ok, (
            f"{service}: health endpoint does not return "
            f"status ok/healthy pattern"
        )

    @pytest.mark.parametrize("service", sorted(PYTHON_SERVICES))
    def test_healthcheck_path_matches_dockerfile(self, service: str) -> None:
        """HEALTHCHECK path in Dockerfile must match health endpoint in code.
        يجب أن يتطابق مسار HEALTHCHECK في Dockerfile مع نقطة الصحة في الكود."""
        content = _read_dockerfile(service)
        if content is None:
            pytest.skip(f"No Dockerfile for {service}")

        if "HEALTHCHECK" not in content.upper():
            pytest.skip(f"{service} Dockerfile has no HEALTHCHECK")

        hc_path = _extract_healthcheck_path(content)
        if hc_path is None:
            pytest.skip(f"{service}: could not parse HEALTHCHECK path")

        valid_health_paths = {"/healthz", "/readyz", "/health", "/api/health"}
        assert hc_path in valid_health_paths, (
            f"{service}: HEALTHCHECK path '{hc_path}' is not a standard "
            f"health endpoint. Expected one of: {valid_health_paths}"
        )


# ===========================================================================
# 4. TestAPIVersionConsistency
#    التحقق من اتفاقيات تسمية اصدارات واجهة برمجة التطبيقات
# ===========================================================================


class TestAPIVersionConsistency:
    """Validate API version naming conventions across services.
    التحقق من اتفاقيات تسمية اصدارات واجهة برمجة التطبيقات."""

    API_ROUTE_RE = re.compile(
        r"""(?:prefix|path)\s*=\s*['"](/api/v\d+[^"']*)['"]""",
        re.IGNORECASE,
    )

    ROUTER_PREFIX_RE = re.compile(
        r"""(?:prefix|Router\()\s*.*?['"]/?api/v(\d+)""",
        re.IGNORECASE,
    )

    @pytest.mark.parametrize(
        "service",
        [s for s in sorted(PYTHON_SERVICES) if (SERVICES_DIR / s / "src").is_dir()],
    )
    def test_api_routes_follow_versioning_pattern(self, service: str) -> None:
        """API routes must use /api/v1/ or /api/v2/ pattern.
        يجب أن تتبع مسارات API نمط /api/v1/ او /api/v2/."""
        src_files = _get_python_src_files(service)
        if not src_files:
            pytest.skip(f"{service} has no src/ Python files")

        invalid_routes: list[str] = []
        for py_file in src_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for match in self.API_ROUTE_RE.finditer(content):
                route = match.group(1)
                if not re.match(r"^/api/v\d+", route):
                    rel = py_file.relative_to(REPO_ROOT)
                    invalid_routes.append(f"{rel}: {route}")

        if invalid_routes:
            pytest.xfail(
                f"{service}: non-standard API routes: {invalid_routes[:5]}"
            )

    @pytest.mark.parametrize(
        "service",
        [s for s in sorted(PYTHON_SERVICES) if (SERVICES_DIR / s / "src").is_dir()],
    )
    def test_no_mixed_api_versions_in_service(self, service: str) -> None:
        """A single service should not mix /api/v1/ and /api/v2/ routes.
        لا يجوز لخدمة واحدة خلط اصدارات API المختلفة."""
        src_files = _get_python_src_files(service)
        if not src_files:
            pytest.skip(f"{service} has no src/ Python files")

        versions_found: set[int] = set()
        for py_file in src_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for match in self.ROUTER_PREFIX_RE.finditer(content):
                versions_found.add(int(match.group(1)))

        if len(versions_found) <= 1:
            return

        pytest.xfail(
            f"{service}: multiple API versions in use: "
            f"{sorted(versions_found)} (verify intentional migration)"
        )

    @pytest.mark.parametrize(
        "service",
        [s for s in sorted(PYTHON_SERVICES) if (SERVICES_DIR / s / "src").is_dir()],
    )
    def test_router_prefixes_use_api_v1(self, service: str) -> None:
        """Router prefixes should use /api/v1 pattern.
        يجب أن تستخدم بادئات الموجه نمط /api/v1."""
        src_files = _get_python_src_files(service)
        if not src_files:
            pytest.skip(f"{service} has no src/ Python files")

        router_prefix_re = re.compile(
            r"""(?:APIRouter|include_router)\s*\(.*?prefix\s*=\s*['"](/?[^"']+)['"]""",
            re.IGNORECASE | re.DOTALL,
        )
        non_api_prefixes: list[str] = []
        for py_file in src_files:
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for match in router_prefix_re.finditer(content):
                prefix = match.group(1)
                if prefix in ("/", "/healthz", "/readyz", "/metrics", "/health"):
                    continue
                if not prefix.startswith("/api/v") and not prefix.startswith("api/v"):
                    rel = py_file.relative_to(REPO_ROOT)
                    non_api_prefixes.append(f"{rel}: prefix='{prefix}'")

        if non_api_prefixes:
            pytest.xfail(
                f"{service}: router prefixes not using /api/v pattern: "
                f"{non_api_prefixes[:5]}"
            )


# ===========================================================================
# 5. TestServiceRegistryCompleteness
#    التحقق من اكتمال سجل الخدمات
# ===========================================================================


class TestServiceRegistryCompleteness:
    """Validate that governance/services.yaml, service_registry.py, and
    docker-compose.yml are all in sync.
    التحقق من تزامن سجل الحوكمة وسجل الخدمات وملف docker-compose."""

    def _governance_active_services(self) -> dict[str, dict]:
        """Return active (non-archived) services from governance.
        ارجاع الخدمات النشطة من سجل الحوكمة."""
        gov = _load_governance()
        result: dict[str, dict] = {}
        for name, info in gov.get("services", {}).items():
            if not isinstance(info, dict):
                continue
            status = info.get("status", "active")
            if status in ("active", "deprecated"):
                result[name] = info
        return result

    def _compose_app_services(self) -> set[str]:
        """Return application service names from compose (excluding infra).
        ارجاع اسماء خدمات التطبيقات من docker-compose."""
        compose = _load_compose(MAIN_COMPOSE)
        compose_services = set(compose.get("services", {}).keys())
        excluded = INFRA_SERVICES | {
            "ollama-model-loader",
            "etcd-init",
            "vllm-deepseek",
        }
        return compose_services - excluded

    @pytest.mark.parametrize("service", sorted(ALL_HTTP_SERVICES.keys()))
    def test_registry_service_in_governance(self, service: str) -> None:
        """Every service in service_registry.py must be listed in governance.
        يجب أن تكون كل خدمة في سجل الخدمات مدرجة في سجل الحوكمة."""
        gov = _load_governance()
        gov_services = gov.get("services", {})
        assert service in gov_services, (
            f"{service} is in service_registry.py but missing from "
            f"governance/services.yaml"
        )

    @pytest.mark.parametrize("service", sorted(ALL_HTTP_SERVICES.keys()))
    def test_registry_service_in_compose(self, service: str) -> None:
        """Every service in service_registry.py should exist in docker-compose.yml.
        يجب أن تكون كل خدمة في سجل الخدمات موجودة في docker-compose.yml."""
        compose = _load_compose(MAIN_COMPOSE)
        compose_services = set(compose.get("services", {}).keys())
        if service not in compose_services:
            pytest.xfail(
                f"{service} is in service_registry.py but not in "
                f"docker-compose.yml (may use profiles)"
            )

    def test_no_orphan_services_in_governance(self) -> None:
        """Active governance services with ports should exist in service_registry.py.
        يجب الا توجد خدمات يتيمة في سجل الحوكمة."""
        gov_active = self._governance_active_services()
        registry_all = set(ALL_HTTP_SERVICES.keys()) | PORTLESS_SERVICES

        orphans: list[str] = []
        for svc_name, info in gov_active.items():
            if svc_name not in registry_all:
                port = info.get("port")
                if port is None:
                    continue
                orphans.append(f"{svc_name} (port={port})")

        if orphans:
            pytest.xfail(
                f"Governance has active services not in service_registry.py: {orphans}"
            )

    def test_no_ghost_services_in_compose(self) -> None:
        """App services in compose should exist in service_registry.py.
        يجب الا توجد خدمات شبحية في docker-compose غير مسجلة."""
        compose_apps = self._compose_app_services()
        registry_all = set(ALL_BUILT_SERVICES.keys())

        ghosts = compose_apps - registry_all
        if ghosts:
            pytest.xfail(
                f"Compose has services not in service_registry.py: "
                f"{sorted(ghosts)}"
            )

    def test_governance_lists_all_event_layers(self) -> None:
        """governance/services.yaml must define all 4 event architecture layers.
        يجب أن يحدد سجل الحوكمة جميع طبقات هندسة الاحداث الاربع."""
        gov = _load_governance()
        event_arch = gov.get("event_architecture", {})
        layers = event_arch.get("layers", {})
        expected_layers = {"acquisition", "intelligence", "decision", "business"}
        actual_layers = set(layers.keys())
        missing = expected_layers - actual_layers
        assert not missing, f"Missing event layers in governance: {missing}"

    @pytest.mark.parametrize("service", sorted(ALL_HTTP_SERVICES.keys()))
    def test_governance_service_has_required_fields(self, service: str) -> None:
        """Each governance service entry must have type and status fields.
        يجب أن يحتوي كل ادخال خدمة في الحوكمة على الحقول المطلوبة."""
        gov = _load_governance()
        gov_services = gov.get("services", {})
        if service not in gov_services:
            pytest.skip(f"{service} not in governance/services.yaml")

        info = gov_services[service]
        if not isinstance(info, dict):
            pytest.fail(f"{service} has no structured entry")

        required_fields = {"type", "status"}
        missing = required_fields - set(info.keys())
        assert not missing, (
            f"{service}: missing required fields in governance: {missing}"
        )


# ===========================================================================
# 6. TestDockerComposeConsistencyAcrossFiles
#    التحقق من اتساق ملفات docker-compose المختلفة
# ===========================================================================


class TestDockerComposeConsistencyAcrossFiles:
    """Validate consistency across docker-compose.yml, test, and prod files.
    التحقق من اتساق ملفات docker-compose المختلفة."""

    def test_main_compose_exists(self) -> None:
        """Main docker-compose.yml must exist.
        يجب أن يوجد ملف docker-compose.yml الرئيسي."""
        assert MAIN_COMPOSE.exists(), (
            f"docker-compose.yml not found at {MAIN_COMPOSE}"
        )

    def test_test_compose_exists(self) -> None:
        """docker-compose.test.yml must exist.
        يجب أن يوجد ملف docker-compose.test.yml."""
        assert TEST_COMPOSE.exists(), (
            f"docker-compose.test.yml not found at {TEST_COMPOSE}"
        )

    def test_prod_compose_exists(self) -> None:
        """docker-compose.prod.yml must exist.
        يجب أن يوجد ملف docker-compose.prod.yml."""
        assert PROD_COMPOSE.exists(), (
            f"docker-compose.prod.yml not found at {PROD_COMPOSE}"
        )

    def test_test_compose_services_subset_of_main(self) -> None:
        """Services in docker-compose.test.yml should reference services that
        exist in docker-compose.yml or are test-only infrastructure.
        يجب أن تكون خدمات ملف الاختبار موجودة في الملف الرئيسي."""
        main = _load_compose(MAIN_COMPOSE)
        test = _load_compose(TEST_COMPOSE)
        if not test:
            pytest.skip("docker-compose.test.yml is empty or missing")

        main_services = set(main.get("services", {}).keys())
        test_services = set(test.get("services", {}).keys())

        test_only_pattern = re.compile(r"(?:test_runner|.*_test$)")
        test_specific = {s for s in test_services if test_only_pattern.match(s)}
        app_test_services = test_services - test_specific

        not_in_main: set[str] = set()
        for svc in app_test_services:
            base = svc.removesuffix("_test")
            if base not in main_services and svc not in main_services:
                not_in_main.add(svc)

        if not_in_main:
            pytest.xfail(
                f"Test compose services not found in main compose: "
                f"{sorted(not_in_main)}"
            )

    def test_prod_compose_services_subset_of_main(self) -> None:
        """Services in docker-compose.prod.yml should be a subset of main.
        يجب أن تكون خدمات ملف الانتاج مجموعة فرعية من الملف الرئيسي."""
        main = _load_compose(MAIN_COMPOSE)
        prod = _load_compose(PROD_COMPOSE)
        if not prod:
            pytest.skip("docker-compose.prod.yml is empty or missing")

        main_services = set(main.get("services", {}).keys())
        prod_services = set(prod.get("services", {}).keys())

        not_in_main = prod_services - main_services
        if not_in_main:
            pytest.xfail(
                f"Prod compose has services not in main compose: "
                f"{sorted(not_in_main)}"
            )

    def test_main_compose_defines_network(self) -> None:
        """Main docker-compose.yml must define the sahool-network.
        يجب أن يعرف الملف الرئيسي شبكة sahool-network."""
        main = _load_compose(MAIN_COMPOSE)
        networks = main.get("networks", {})
        assert "sahool-network" in networks, (
            f"Main compose missing 'sahool-network'. "
            f"Found networks: {list(networks.keys())}"
        )

    def test_network_names_consistent(self) -> None:
        """Network naming should be consistent across compose files.
        يجب أن تكون اسماء الشبكات متسقة عبر ملفات docker-compose."""
        compose_files = [
            ("main", MAIN_COMPOSE),
            ("test", TEST_COMPOSE),
            ("prod", PROD_COMPOSE),
        ]

        all_networks: dict[str, list[str]] = {}
        for label, path in compose_files:
            data = _load_compose(path)
            if not data:
                continue
            networks = list(data.get("networks", {}).keys())
            for net in networks:
                all_networks.setdefault(net, []).append(label)

        non_standard: list[str] = []
        for net_name in all_networks:
            if not net_name.startswith("sahool"):
                non_standard.append(net_name)

        if non_standard:
            pytest.xfail(
                f"Non-standard network names: {non_standard} "
                f"(expected sahool-* prefix)"
            )

    @pytest.mark.parametrize(
        "service,expected_port",
        sorted(ALL_HTTP_SERVICES.items()),
    )
    def test_compose_port_mapping_format(
        self, service: str, expected_port: int
    ) -> None:
        """Port mappings in compose should bind to 127.0.0.1 (localhost).
        يجب أن تربط تعيينات المنافذ بعنوان 127.0.0.1 للامان."""
        compose = _load_compose(MAIN_COMPOSE)
        compose_services = compose.get("services", {})
        if service not in compose_services:
            pytest.skip(f"{service} not in docker-compose.yml")

        ports = compose_services[service].get("ports", [])
        if not ports:
            pytest.skip(f"{service} has no port mappings")

        for port_entry in ports:
            port_str = str(port_entry)
            if ":" in port_str and not port_str.startswith("127.0.0.1:"):
                if "${" in port_str:
                    continue
                pytest.xfail(
                    f"{service}: port mapping '{port_str}' does not bind "
                    f"to 127.0.0.1 (security best practice)"
                )

    def test_main_compose_has_logging_config(self) -> None:
        """Main compose should define default logging configuration.
        يجب أن يعرف الملف الرئيسي تكوين التسجيل الافتراضي."""
        raw_content = MAIN_COMPOSE.read_text(encoding="utf-8")
        assert "x-logging" in raw_content or "logging:" in raw_content, (
            "Main compose should define logging configuration "
            "(x-logging anchor or per-service logging)"
        )

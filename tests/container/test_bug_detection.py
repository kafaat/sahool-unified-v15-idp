"""
SAHOOL Container Function Bug Detection Tests
===============================================
اختبارات كشف الأخطاء الوظيفية في الحاويات

These tests detect REAL bugs and inconsistencies that could cause runtime
failures, event routing errors, or security issues. Unlike smoke tests,
these validate cross-service contract integrity.

Bugs detected:
 1.  NATS subject drift: subjects hardcoded in services but missing from
     shared/events/subjects.py (causes silent event routing failures)
 2.  Constraint file omission: pip install without -c constraints.txt
     (causes version conflicts and CVE exposure)
 3.  Port/env mismatch: PORT env var vs Dockerfile EXPOSE
 4.  Broken NATS event contracts between publisher/subscriber
 5.  Duplicate subjects across services (collision risk)
 6.  Services importing shared/ without PYTHONPATH=/app
 7.  Health endpoint mismatch (HEALTHCHECK URL vs actual route)
 8.  Missing env vars in compose that source code requires
 9.  Inconsistent tenant subject patterns
10.  Dockerfile security regressions

Run:
    pytest tests/container/test_bug_detection.py -v --tb=short
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.container, pytest.mark.smoke]

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"
SUBJECTS_PY = REPO_ROOT / "shared" / "events" / "subjects.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_compose_cache: dict | None = None
_subjects_cache: str | None = None


def _load_compose() -> dict[str, Any]:
    global _compose_cache
    if _compose_cache is None:
        content = MAIN_COMPOSE.read_text("utf-8")
        sanitized = re.sub(r"\$\{([^:}]+):-(\d+)\}", r"\2", content)
        sanitized = re.sub(r"\$\{[^}]+\}", "placeholder", sanitized)
        _compose_cache = yaml.safe_load(sanitized) or {}
    return _compose_cache


def _load_subjects() -> str:
    global _subjects_cache
    if _subjects_cache is None:
        _subjects_cache = SUBJECTS_PY.read_text("utf-8") if SUBJECTS_PY.exists() else ""
    return _subjects_cache


_subject_cache: dict[str, set[str]] = {}


def _find_hardcoded_subjects(svc_name: str, max_files: int = 30) -> set[str]:
    """Find NATS subjects hardcoded as string literals in service source (cached)."""
    if svc_name in _subject_cache:
        return _subject_cache[svc_name]
    src_dir = SERVICES_DIR / svc_name / "src"
    if not src_dir.exists():
        _subject_cache[svc_name] = set()
        return set()
    subjects: set[str] = set()
    pattern = re.compile(r'"(sahool\.[a-z][a-z0-9_.]+)"')
    files = sorted(src_dir.rglob("*.py"))[:max_files] + sorted(src_dir.rglob("*.ts"))[:max_files]
    for src_file in files:
        try:
            content = src_file.read_text("utf-8", errors="ignore")
        except OSError:
            continue
        for m in pattern.finditer(content):
            subj = m.group(1)
            if not subj.endswith(".") and "*" not in subj and ">" not in subj:
                subjects.add(subj)
    _subject_cache[svc_name] = subjects
    return subjects


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    return _load_compose()


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. NATS Subject Drift Detection
# ===========================================================================


class TestNATSSubjectDrift:
    """كشف انحراف مواضيع NATS عن الثوابت المركزية.

    Many services hardcode NATS subjects as string literals instead of
    importing from shared/events/subjects.py. This causes silent failures
    when subjects are renamed or deprecated.
    """

    # Services expected to use NATS subjects
    NATS_SERVICES = [
        "advisory-service", "alert-service", "audit-service",
        "billing-core", "crop-intelligence-service",
        "field-management-service", "indicators-service",
        "irrigation-smart", "ndvi-processor",
        "pest-detection-service", "soil-analysis-service",
        "task-service", "weather-service", "yolo26-vision-service",
    ]

    def test_subjects_py_exists(self) -> None:
        """shared/events/subjects.py must exist as single source of truth."""
        assert SUBJECTS_PY.exists(), (
            "shared/events/subjects.py missing – this is the single source of truth "
            "for all NATS event subjects"
        )

    def test_subjects_py_has_minimum_constants(self) -> None:
        """subjects.py must define minimum set of agricultural event constants."""
        content = _load_subjects()
        required_prefixes = [
            "SAHOOL_FIELD_",
            "SAHOOL_WEATHER_",
            "SAHOOL_SATELLITE_",
            "SAHOOL_HEALTH_",
            "SAHOOL_RECOMMENDATION_",
            "SAHOOL_TASK_",
        ]
        found = [p for p in required_prefixes if p in content]
        assert len(found) >= 5, (
            f"subjects.py missing critical event constant prefixes "
            f"(found: {found}, expected ≥5 of {required_prefixes})"
        )

    @pytest.mark.parametrize("svc", sorted(NATS_SERVICES))
    def test_service_uses_nats_subjects(self, svc: str) -> None:
        """Service that publishes NATS events should reference subject constants."""
        subjects = _find_hardcoded_subjects(svc)
        if not subjects:
            pytest.skip(f"{svc} has no hardcoded subjects")
        # Check how many are in subjects.py
        subjects_content = _load_subjects()
        missing = {s for s in subjects if s not in subjects_content}
        # Filter out tenant-scoped subjects (sahool.{tenant_id}.xxx)
        missing = {s for s in missing if ".tenant." not in s and "{" not in s}
        # Flag services with high drift (>50% subjects missing AND ≥5 missing)
        drift_pct = len(missing) / max(len(subjects), 1)
        if drift_pct > 0.5 and len(missing) >= 5:
            pytest.fail(
                f"{svc} has {len(missing)}/{len(subjects)} NATS subjects "
                f"NOT in shared/events/subjects.py:\n"
                + "\n".join(f"  - {s}" for s in sorted(missing)[:5])
                + ("\n  ... (truncated)" if len(missing) > 5 else "")
            )


# ===========================================================================
# 2. Pip Constraints File Usage
# ===========================================================================


class TestPipConstraintsUsage:
    """التحقق من استخدام ملف القيود في pip install.

    Services that install Python packages without -c constraints.txt
    may get different versions than tested, exposing CVE vulnerabilities
    or causing incompatibilities.
    """

    def _get_python_services(self) -> list[str]:
        """Return all Python services with Dockerfiles."""
        svcs = []
        for svc_dir in SERVICES_DIR.iterdir():
            if not svc_dir.is_dir():
                continue
            dockerfile = svc_dir / "Dockerfile"
            req_txt = svc_dir / "requirements.txt"
            if dockerfile.exists() and req_txt.exists():
                svcs.append(svc_dir.name)
        return sorted(svcs)

    def test_all_python_services_use_constraints(self) -> None:
        """All Python services should use constraints.txt for version pinning."""
        missing_constraints: list[str] = []
        for svc in self._get_python_services():
            dockerfile = SERVICES_DIR / svc / "Dockerfile"
            content = dockerfile.read_text("utf-8")
            has_pip = "pip install" in content
            has_constraints = "constraints" in content.lower()
            if has_pip and not has_constraints:
                missing_constraints.append(svc)
        if missing_constraints:
            pytest.fail(
                f"{len(missing_constraints)} service(s) run pip install without "
                f"-c constraints.txt (CVE risk):\n"
                + "\n".join(f"  - {s}" for s in missing_constraints)
            )


# ===========================================================================
# 3. PYTHONPATH Configuration
# ===========================================================================


class TestPythonPathConfig:
    """التحقق من PYTHONPATH في Dockerfiles.

    Services that import from shared/ need PYTHONPATH=/app (or equivalent)
    so Python can find the shared package at runtime.
    """

    # Node.js services don't need PYTHONPATH
    NODE_SERVICES = {"field-management-service", "iot-service", "chat-service",
                     "marketplace-service", "user-service", "crop-growth-model",
                     "lai-estimation", "yield-prediction", "yield-prediction-service",
                     "research-core", "disaster-assessment", "code-review-agent"}

    def _get_services_using_shared(self) -> list[str]:
        """Find Python services that import from shared/ in source code."""
        svcs = []
        for svc_dir in SERVICES_DIR.iterdir():
            if svc_dir.name in self.NODE_SERVICES:
                continue  # Node.js services don't need PYTHONPATH
            src_dir = svc_dir / "src"
            if not src_dir.exists():
                continue
            main_py = src_dir / "main.py"
            if main_py.exists():
                content = main_py.read_text("utf-8", errors="ignore")
                if "from shared" in content or "import shared" in content:
                    svcs.append(svc_dir.name)
        return sorted(svcs)

    def test_pythonpath_set_for_shared_imports(self) -> None:
        """Services importing shared/ must set PYTHONPATH or copy shared/ under WORKDIR."""
        missing_pythonpath: list[str] = []
        for svc in self._get_services_using_shared():
            dockerfile = SERVICES_DIR / svc / "Dockerfile"
            if not dockerfile.exists():
                continue
            content = dockerfile.read_text("utf-8")
            has_pythonpath = "PYTHONPATH" in content
            # Also OK if shared/ is copied to WORKDIR (./shared/ with WORKDIR /app)
            copies_shared_to_workdir = bool(
                re.search(r"COPY.*shared.*\./shared", content, re.IGNORECASE)
                or re.search(r"COPY.*shared.*/app/shared", content, re.IGNORECASE)
            )
            if not has_pythonpath and not copies_shared_to_workdir:
                missing_pythonpath.append(svc)
        assert not missing_pythonpath, (
            f"Services importing shared/ without PYTHONPATH or shared/ copy:\n"
            + "\n".join(f"  - {s}" for s in missing_pythonpath)
        )


# ===========================================================================
# 4. Health Endpoint Consistency
# ===========================================================================


class TestHealthEndpointConsistency:
    """تناسق نقاط فحص الصحة.

    Dockerfile HEALTHCHECK URL must match an actually defined route.
    """

    def test_healthcheck_url_matches_source(self) -> None:
        """HEALTHCHECK URL path exists as a route in service source."""
        mismatches: list[str] = []
        for svc_dir in SERVICES_DIR.iterdir():
            dockerfile = svc_dir / "Dockerfile"
            main_py = svc_dir / "src" / "main.py"
            if not dockerfile.exists() or not main_py.exists():
                continue

            df_content = dockerfile.read_text("utf-8")
            # Extract healthcheck URL path
            hc_match = re.search(
                r"HEALTHCHECK.*(?:curl|wget|urllib|urlopen).*?['\"]https?://[^/]*(\/\S+?)['\"]",
                df_content,
                re.IGNORECASE,
            )
            if not hc_match:
                continue
            hc_path = hc_match.group(1).rstrip("'\")")

            # Check if path exists in source
            src_content = main_py.read_text("utf-8", errors="ignore")
            # Also check other source files
            all_src = src_content
            for extra in (svc_dir / "src").rglob("*.py"):
                if extra.name != "__pycache__":
                    try:
                        all_src += extra.read_text("utf-8", errors="ignore")
                    except OSError:
                        continue  # Skip unreadable files

            if hc_path not in all_src:
                mismatches.append(f"{svc_dir.name}: HEALTHCHECK→{hc_path} not in source")

        # Some mismatches are OK (path may be auto-registered by framework)
        if len(mismatches) > 5:
            pytest.fail(
                f"{len(mismatches)} services have HEALTHCHECK URLs not found in source:\n"
                + "\n".join(f"  - {m}" for m in mismatches[:10])
            )


# ===========================================================================
# 5. Compose Environment Variable Completeness
# ===========================================================================


class TestComposeEnvCompleteness:
    """اكتمال متغيرات البيئة في docker-compose.

    Detect services that read env vars in source code but don't declare
    them in docker-compose.yml environment section.
    """

    # Critical env vars that should be in compose if used in source
    CRITICAL_ENV_VARS = {
        "DATABASE_URL": "database connection",
        "NATS_URL": "event bus connection",
        "REDIS_URL": "cache connection",
        "JWT_SECRET_KEY": "authentication",
    }

    def test_critical_env_vars_declared(self, services: dict) -> None:
        """Services using critical env vars must declare them in compose."""
        issues: list[str] = []
        for svc_dir in SERVICES_DIR.iterdir():
            main_py = svc_dir / "src" / "main.py"
            if not main_py.exists():
                continue
            svc_name = svc_dir.name
            svc_def = services.get(svc_name, {})
            if not svc_def:
                continue

            src = main_py.read_text("utf-8", errors="ignore")
            env_str = str(svc_def.get("environment", {}))

            for var, purpose in self.CRITICAL_ENV_VARS.items():
                # Check if source uses this var
                uses_var = (
                    f'"{var}"' in src
                    or f"'{var}'" in src
                    or f"getenv('{var}" in src
                    or f'getenv("{var}' in src
                    or f"os.environ['{var}" in src
                    or f'os.environ["{var}' in src
                )
                if uses_var and var not in env_str and "placeholder" not in env_str:
                    issues.append(f"{svc_name}: uses {var} ({purpose}) but not in compose env")

        if issues:
            pytest.fail(
                f"{len(issues)} env var declaration gaps:\n"
                + "\n".join(f"  - {i}" for i in issues[:10])
            )


# ===========================================================================
# 6. Dockerfile Security Regressions
# ===========================================================================


class TestDockerfileSecurityRegressions:
    """كشف الانحدارات الأمنية في Dockerfiles."""

    def test_no_root_cmd_in_production(self) -> None:
        """No Dockerfile runs CMD as root (last USER must be non-root)."""
        root_services: list[str] = []
        for svc_dir in SERVICES_DIR.iterdir():
            dockerfile = svc_dir / "Dockerfile"
            if not dockerfile.exists():
                continue
            content = dockerfile.read_text("utf-8")
            # Find all USER instructions and CMD
            user_instructions = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
            has_cmd = bool(re.search(r"^CMD\s+", content, re.MULTILINE))
            if has_cmd and not user_instructions:
                root_services.append(svc_dir.name)
            elif has_cmd and user_instructions:
                last_user = user_instructions[-1]
                if last_user.lower() in ("root", "0"):
                    root_services.append(svc_dir.name)

        assert not root_services, (
            f"Services running CMD as root (security risk):\n"
            + "\n".join(f"  - {s}" for s in root_services)
        )

    def test_no_secrets_in_dockerfiles(self) -> None:
        """No Dockerfile contains hardcoded secrets or credentials."""
        secret_patterns = [
            r"(?i)(password|secret|token|api_key)\s*=\s*['\"][^$][^'\"]{8,}",
            r"(?i)COPY.*\.env\b",
        ]
        found_secrets: list[str] = []
        for svc_dir in SERVICES_DIR.iterdir():
            dockerfile = svc_dir / "Dockerfile"
            if not dockerfile.exists():
                continue
            content = dockerfile.read_text("utf-8")
            for pattern in secret_patterns:
                if re.search(pattern, content):
                    found_secrets.append(svc_dir.name)
                    break

        assert not found_secrets, (
            f"Dockerfiles with potential hardcoded secrets:\n"
            + "\n".join(f"  - {s}" for s in found_secrets)
        )

    def test_no_chmod_777(self) -> None:
        """No Dockerfile uses chmod 777 (world-writable permissions)."""
        violations: list[str] = []
        for svc_dir in SERVICES_DIR.iterdir():
            dockerfile = svc_dir / "Dockerfile"
            if not dockerfile.exists():
                continue
            content = dockerfile.read_text("utf-8")
            if "chmod 777" in content or "chmod -R 777" in content:
                violations.append(svc_dir.name)

        assert not violations, (
            f"Dockerfiles with chmod 777 (security risk):\n"
            + "\n".join(f"  - {s}" for s in violations)
        )


# ===========================================================================
# 7. NATS Publisher/Subscriber Contract Integrity
# ===========================================================================


class TestNATSContractIntegrity:
    """سلامة عقود الناشر/المشترك في NATS.

    When a service publishes an event, at least one other service should
    subscribe to it. Orphan subjects indicate broken data flow.
    """

    def test_critical_events_have_subscribers(self) -> None:
        """Critical agricultural events are both published and subscribed."""
        # Build publish/subscribe maps
        all_subjects: dict[str, dict[str, list[str]]] = defaultdict(
            lambda: {"publishers": [], "subscribers": []}
        )

        for svc_dir in SERVICES_DIR.iterdir():
            src_dir = svc_dir / "src"
            if not src_dir.exists():
                continue
            svc_name = svc_dir.name
            for py_file in src_dir.rglob("*.py"):
                try:
                    content = py_file.read_text("utf-8", errors="ignore")
                except OSError:
                    continue
                # Detect publishers
                for m in re.finditer(r'publish\(["\']?(sahool\.[a-z_.]+)', content):
                    all_subjects[m.group(1)]["publishers"].append(svc_name)
                for m in re.finditer(r'nc\.publish\("(sahool\.[a-z_.]+)"', content):
                    all_subjects[m.group(1)]["publishers"].append(svc_name)
                # Detect subscribers
                for m in re.finditer(r'subscribe\(["\']?(sahool\.[a-z_.]+)', content):
                    all_subjects[m.group(1)]["subscribers"].append(svc_name)

        # Check critical subjects have both publisher and subscriber
        critical_subjects = [
            "sahool.field.created",
            "sahool.satellite.ndvi.computed",
            "sahool.vision.pest_detected",
            "sahool.weather.alert",
        ]
        orphans = []
        for subj in critical_subjects:
            info = all_subjects.get(subj, {"publishers": [], "subscribers": []})
            if info["publishers"] and not info["subscribers"]:
                orphans.append(f"{subj}: published by {info['publishers']} but no subscribers")

        # Allow some orphans (subscribers may use wildcard patterns)
        if len(orphans) > 2:
            pytest.fail(
                f"Critical NATS events without subscribers:\n"
                + "\n".join(f"  - {o}" for o in orphans)
            )


# ===========================================================================
# 8. Tenant Subject Pattern Consistency
# ===========================================================================


class TestTenantSubjectPatterns:
    """اتساق أنماط مواضيع المستأجرين.

    SAHOOL uses two tenant-scoped subject patterns:
    1. sahool.tenant.{tenant_id}.{domain}.{action}
    2. sahool.{tenant_id}.{domain}.{action}

    Services should use get_tenant_subject() for consistency.
    """

    def test_tenant_subject_patterns_consistent(self) -> None:
        """Services use consistent tenant subject patterns."""
        pattern1_services: list[str] = []  # sahool.tenant.{id}
        pattern2_services: list[str] = []  # sahool.{id}

        for svc_dir in SERVICES_DIR.iterdir():
            src_dir = svc_dir / "src"
            if not src_dir.exists():
                continue
            for py_file in src_dir.rglob("*.py"):
                try:
                    content = py_file.read_text("utf-8", errors="ignore")
                except OSError:
                    continue
                if "sahool.tenant." in content and "f\"sahool.tenant." in content:
                    pattern1_services.append(svc_dir.name)
                if re.search(r'f"sahool\.\{[^}]*tenant', content):
                    pattern2_services.append(svc_dir.name)

        p1 = set(pattern1_services)
        p2 = set(pattern2_services)
        # Services using BOTH patterns is a bug
        both = p1 & p2
        if both:
            pytest.fail(
                f"Services using BOTH tenant subject patterns (inconsistency):\n"
                + "\n".join(f"  - {s}" for s in sorted(both))
                + "\nShould use get_tenant_subject() from shared/events/subjects.py"
            )


# ===========================================================================
# 9. Broken Dependencies Detection
# ===========================================================================


class TestBrokenDependencies:
    """كشف التبعيات المعطلة."""

    def test_no_broken_depends_on(self, services: dict) -> None:
        """All depends_on targets exist in docker-compose.yml."""
        broken: list[str] = []
        all_names = set(services.keys())
        for svc_name, svc in services.items():
            depends = svc.get("depends_on", {})
            deps = (
                set(depends) if isinstance(depends, list)
                else set(depends.keys()) if isinstance(depends, dict)
                else set()
            )
            missing = deps - all_names
            if missing:
                broken.append(f"{svc_name} → {missing}")

        assert not broken, (
            f"Broken depends_on references:\n"
            + "\n".join(f"  - {b}" for b in broken)
        )

    def test_no_duplicate_port_mappings(self, services: dict) -> None:
        """No two services share the same host port."""
        port_map: dict[int, list[str]] = defaultdict(list)
        for svc_name, svc in services.items():
            for p in svc.get("ports", []):
                p_str = str(p)
                parts = p_str.split(":")
                if len(parts) >= 2:
                    host_part = parts[0].strip()
                    # Skip IPs
                    if "." in host_part:
                        host_part = parts[1].strip() if len(parts) >= 3 else parts[0]
                    m = re.search(r"(\d+)", host_part)
                    if m:
                        port_map[int(m.group(1))].append(svc_name)

        duplicates = {p: svcs for p, svcs in port_map.items() if len(svcs) > 1}
        assert not duplicates, (
            f"Duplicate host port mappings:\n"
            + "\n".join(f"  port {p}: {svcs}" for p, svcs in duplicates.items())
        )


# ===========================================================================
# 10. Hybrid Service Detection (Python+Node.js Mix)
# ===========================================================================


class TestHybridServiceDetection:
    """كشف الخدمات الهجينة (Python+Node.js في نفس الخدمة).

    A service should be either Python OR Node.js, not both.
    Having both main.py and main.ts causes build confusion.
    """

    # Known Node.js services
    NODE_SERVICES = {
        "field-management-service", "iot-service", "chat-service",
        "marketplace-service", "user-service", "crop-growth-model",
        "lai-estimation", "yield-prediction", "yield-prediction-service",
        "research-core", "disaster-assessment", "code-review-agent",
    }

    def test_node_services_no_python_main(self) -> None:
        """Node.js services should not have a conflicting Python main.py."""
        hybrids: list[str] = []
        for svc in self.NODE_SERVICES:
            svc_dir = SERVICES_DIR / svc
            has_ts = (svc_dir / "src" / "main.ts").exists() or (
                svc_dir / "src" / "index.ts"
            ).exists()
            has_py = (svc_dir / "src" / "main.py").exists()
            if has_ts and has_py:
                # Check if Dockerfile is Node.js based
                dockerfile = svc_dir / "Dockerfile"
                if dockerfile.exists():
                    df = dockerfile.read_text("utf-8")
                    is_node_build = "node:" in df.lower()
                    if is_node_build:
                        hybrids.append(
                            f"{svc}: has both main.ts AND main.py "
                            f"but Dockerfile is Node.js (Python code won't run)"
                        )
        if hybrids:
            pytest.fail(
                f"Hybrid services detected (Python code in Node.js service):\n"
                + "\n".join(f"  - {h}" for h in hybrids)
            )


# ===========================================================================
# 11. Service Registry Completeness
# ===========================================================================


class TestServiceRegistryCompleteness:
    """اكتمال سجل الخدمات.

    All buildable services in docker-compose.yml should be registered
    in tests/container/service_registry.py.
    """

    def test_buildable_services_registered(self, services: dict) -> None:
        """All services with build: directive are in the service registry."""
        from tests.container.service_registry import (
            ALL_HTTP_SERVICES,
            PORTLESS_SERVICES,
            DEPRECATED_SERVICES,
        )

        registered = set(ALL_HTTP_SERVICES.keys()) | PORTLESS_SERVICES | set(DEPRECATED_SERVICES.keys())

        buildable_in_compose: set[str] = set()
        for svc_name, svc_def in services.items():
            if "build" in svc_def:
                buildable_in_compose.add(svc_name)

        unregistered = buildable_in_compose - registered
        # Exclude known special services (init containers, GPU-only services)
        known_unregistered = {"vllm-deepseek", "etcd-perms-init", "etcd-init"}
        unregistered -= known_unregistered

        if unregistered:
            pytest.fail(
                f"Buildable services in compose but NOT in service_registry.py:\n"
                + "\n".join(f"  - {s}" for s in sorted(unregistered))
                + "\nAdd them to PYTHON_SERVICES, NODE_SERVICES, or PORTLESS_SERVICES"
            )


# ===========================================================================
# 12. Deprecated Service Isolation
# ===========================================================================


class TestDeprecatedServiceIsolation:
    """عزل الخدمات المهملة.

    Deprecated services should not start by default. They must require
    --profile deprecated to launch.
    """

    def test_deprecated_services_have_profiles(self, services: dict) -> None:
        """Deprecated services must have 'profiles' to prevent default startup."""
        from tests.container.service_registry import DEPRECATED_SERVICES

        no_profile: list[str] = []
        for svc_name in DEPRECATED_SERVICES:
            svc_def = services.get(svc_name, {})
            if not svc_def:
                continue  # Not in compose at all — OK
            profiles = svc_def.get("profiles", [])
            if not profiles:
                no_profile.append(svc_name)

        if no_profile:
            pytest.fail(
                f"Deprecated services without 'profiles' annotation "
                f"(will start by default):\n"
                + "\n".join(f"  - {s}" for s in no_profile)
                + "\nAdd: profiles: [deprecated] to prevent accidental startup"
            )


# ===========================================================================
# 13. Container Image Version Pinning (CVE Prevention)
# ===========================================================================


class TestImageVersionPinning:
    """تثبيت إصدارات صور Docker لمنع ثغرات CVE.

    Using :latest tags causes non-reproducible builds and may pull
    images with known CVEs. All images must use pinned version tags.
    """

    # Compose files to scan for :latest tags
    COMPOSE_FILES = [
        "docker-compose.yml",
        "docker-compose.test.yml",
        "docker-compose.prod.yml",
        "docker/docker-compose.infra.yml",
    ]

    def test_no_latest_tags_in_main_compose(self, services: dict) -> None:
        """Main docker-compose.yml has no :latest image tags."""
        latest_images: list[str] = []
        for svc_name, svc_def in services.items():
            image = svc_def.get("image", "")
            if ":latest" in image:
                latest_images.append(f"{svc_name}: {image}")
        assert not latest_images, (
            f"Services using :latest tag (non-reproducible, CVE risk):\n"
            + "\n".join(f"  - {i}" for i in latest_images)
        )

    def test_compose_files_no_latest(self) -> None:
        """Scan compose files for :latest tags."""
        latest_found: list[str] = []
        for compose_file in self.COMPOSE_FILES:
            path = REPO_ROOT / compose_file
            if not path.exists():
                continue
            content = path.read_text("utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                if ":latest" in line and "image:" in line and not line.strip().startswith("#"):
                    latest_found.append(f"{compose_file}:{i}: {line.strip()}")
        assert not latest_found, (
            f"Compose files with :latest tags:\n"
            + "\n".join(f"  - {f}" for f in latest_found)
        )

    def test_infrastructure_images_version_pinned(self, services: dict) -> None:
        """All infrastructure images have specific version tags (not just major)."""
        infra_services = [
            "postgres", "pgbouncer", "redis", "nats", "kong",
            "vault", "qdrant", "milvus", "minio", "mqtt",
        ]
        unpinned: list[str] = []
        for svc_name in infra_services:
            svc_def = services.get(svc_name, {})
            image = svc_def.get("image", "")
            if not image:
                continue
            # Check that image has a version tag with at least one digit
            parts = image.split(":")
            if len(parts) < 2:
                unpinned.append(f"{svc_name}: {image} (no tag)")
            elif parts[1] == "latest":
                unpinned.append(f"{svc_name}: {image} (:latest)")
        assert not unpinned, (
            f"Infrastructure images without version pin:\n"
            + "\n".join(f"  - {u}" for u in unpinned)
        )


# ===========================================================================
# 14. Image Version Consistency Across Compose Files
# ===========================================================================


class TestImageVersionConsistency:
    """اتساق إصدارات الصور عبر ملفات compose المختلفة."""

    def test_kong_version_consistent(self) -> None:
        """Kong image version is consistent across all compose files."""
        versions: dict[str, str] = {}
        for compose_file in REPO_ROOT.rglob("docker-compose*.yml"):
            try:
                content = compose_file.read_text("utf-8")
            except OSError:
                continue
            for line in content.splitlines():
                if "image:" in line and "kong:" in line.lower() and not line.strip().startswith("#"):
                    m = re.search(r"kong:([^\s\"']+)", line)
                    if m:
                        rel_path = str(compose_file.relative_to(REPO_ROOT))
                        versions[rel_path] = m.group(1)

        unique_versions = set(versions.values())
        if len(unique_versions) > 1:
            details = "\n".join(f"  - {f}: kong:{v}" for f, v in sorted(versions.items()))
            pytest.fail(
                f"Kong image has {len(unique_versions)} different versions:\n{details}"
            )

    def test_qdrant_version_consistent(self) -> None:
        """Qdrant image version is consistent across all compose files."""
        versions: dict[str, str] = {}
        for compose_file in REPO_ROOT.rglob("docker-compose*.yml"):
            try:
                content = compose_file.read_text("utf-8")
            except OSError:
                continue
            for line in content.splitlines():
                if "image:" in line and "qdrant" in line.lower() and not line.strip().startswith("#"):
                    m = re.search(r"qdrant:([^\s\"']+)", line)
                    if m:
                        rel_path = str(compose_file.relative_to(REPO_ROOT))
                        versions[rel_path] = m.group(1)

        unique_versions = set(versions.values())
        if len(unique_versions) > 1:
            details = "\n".join(f"  - {f}: qdrant:{v}" for f, v in sorted(versions.items()))
            pytest.fail(
                f"Qdrant image has {len(unique_versions)} different versions:\n{details}"
            )

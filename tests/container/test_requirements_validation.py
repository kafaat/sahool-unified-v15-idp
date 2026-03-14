"""
SAHOOL Dependency Validation Tests
===================================
اختبارات التحقق من صحة ملفات المتطلبات والاعتماديات

Validates that every service's dependency manifest (requirements.txt for
Python, package.json for Node.js) follows platform conventions, security
baselines, and version-consistency rules.

All tests are static (parse files only – no pip/npm install, no network).

Coverage:
1.  Python requirements format       – pinned versions, no duplicates, valid syntax
2.  Python constraints consistency   – no conflicts with root constraints.txt
3.  Python critical dependencies     – framework deps match Dockerfile ENV vars
4.  Node package.json validation     – valid JSON, required fields, version ranges
5.  Node package.json security       – deprecated packages, engines field
6.  Shared dependency versions       – cross-service version consistency

Run:
    pytest tests/container/test_requirements_validation.py -v --tb=short
    pytest tests/container/test_requirements_validation.py -v -n auto   # parallel
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from tests.container.service_registry import (
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
# Derived service lists
# ---------------------------------------------------------------------------

# Portless services can be Python or Node; detect at runtime.
_PORTLESS_PYTHON: list[str] = [
    s for s in PORTLESS_SERVICES
    if (SERVICES_DIR / s / "requirements.txt").exists()
]
_PORTLESS_NODE: list[str] = [
    s for s in PORTLESS_SERVICES
    if (SERVICES_DIR / s / "package.json").exists()
]

ALL_PYTHON_SERVICES: list[str] = sorted(
    list(PYTHON_SERVICES.keys()) + _PORTLESS_PYTHON
)
ALL_NODE_SERVICES: list[str] = sorted(
    list(NODE_SERVICES.keys()) + _PORTLESS_NODE
)

# ---------------------------------------------------------------------------
# Known insecure package version ceilings
# If a service pins a version *below* the safe floor, the test fails.
# ---------------------------------------------------------------------------

INSECURE_PACKAGES: dict[str, tuple[str, str]] = {
    # package: (minimum_safe_version, cve_reference)
    "pyyaml": ("6.0", "CVE-2020-14343"),
    "requests": ("2.31.0", "CVE-2023-32681"),
    "cryptography": ("41.0.0", "CVE-2023-49083"),
    "urllib3": ("2.0.7", "CVE-2023-45803"),
    "certifi": ("2023.7.22", "CVE-2023-37920"),
    "setuptools": ("70.0.0", "CVE-2024-6345"),
    "aiohttp": ("3.9.4", "CVE-2024-23829"),
    "pillow": ("10.3.0", "CVE-2024-28219"),
    "jinja2": ("3.1.3", "CVE-2024-22195"),
}

# Known deprecated Node.js packages
DEPRECATED_NODE_PACKAGES: dict[str, str] = {
    "request": "Use 'node-fetch', 'axios', or 'undici' instead",
    "querystring": "Use URLSearchParams (built-in)",
    "uuid": "No longer deprecated – false alarm in old lists",  # kept for reference
    "node-sass": "Use 'sass' (Dart Sass) instead",
    "tslint": "Use 'eslint' with @typescript-eslint instead",
    "babel-eslint": "Use '@babel/eslint-parser' instead",
}
# Remove 'uuid' since it's not actually deprecated
DEPRECATED_NODE_PACKAGES.pop("uuid", None)

# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

_requirements_cache: dict[str, str] = {}
_package_json_cache: dict[str, dict[str, Any]] = {}
_constraints_cache: dict[str, str] | None = None


# ---------------------------------------------------------------------------
# Helpers – Python requirements
# ---------------------------------------------------------------------------

def _read_requirements(service_name: str) -> str:
    """Return raw requirements.txt content, cached.
    إرجاع محتوى requirements.txt الخام مع التخزين المؤقت."""
    if service_name not in _requirements_cache:
        path = SERVICES_DIR / service_name / "requirements.txt"
        _requirements_cache[service_name] = path.read_text(encoding="utf-8")
    return _requirements_cache[service_name]


def _parse_requirements_lines(content: str) -> list[str]:
    """Return non-empty, non-comment lines from requirements content.
    إرجاع الأسطر غير الفارغة وغير التعليقات."""
    lines: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.split("#")[0].strip()
        if not line or line.startswith("-"):
            # Skip blank, comments, and options (e.g., -c constraints.txt)
            continue
        lines.append(line)
    return lines


def _extract_package_name(spec: str) -> str:
    """Extract the normalised package name from a pip requirement specifier.
    استخراج اسم الحزمة من سطر المتطلبات."""
    # Handle extras: e.g., redis[hiredis]>=7.0
    match = re.match(r"([A-Za-z0-9_][A-Za-z0-9._-]*)", spec)
    return match.group(1).lower().replace("-", "_").replace(".", "_") if match else spec.lower()


def _extract_version_spec(spec: str) -> str:
    """Extract the version specifier portion (e.g., '==0.135.1', '>=2.0').
    استخراج محدد الإصدار."""
    # Remove extras brackets first
    cleaned = re.sub(r"\[.*?\]", "", spec)
    match = re.match(r"[A-Za-z0-9._-]+\s*(.*)", cleaned)
    return match.group(1).strip() if match else ""


def _extract_pinned_version(spec: str) -> str | None:
    """If the specifier contains ==X.Y.Z, return the version string, else None.
    إرجاع الإصدار المثبت إذا كان موجوداً."""
    match = re.search(r"==\s*([0-9][0-9a-zA-Z.*]*)", spec)
    return match.group(1) if match else None


def _version_tuple(version_str: str) -> tuple[int, ...]:
    """Convert '1.2.3' to (1, 2, 3) for comparison.
    تحويل سلسلة الإصدار إلى صف رقمي للمقارنة."""
    parts: list[int] = []
    for part in version_str.split("."):
        numeric = re.match(r"(\d+)", part)
        parts.append(int(numeric.group(1)) if numeric else 0)
    return tuple(parts)


def _parse_constraints() -> dict[str, str]:
    """Parse root constraints.txt and return {normalised_name: version_spec}.
    تحليل ملف القيود الجذري."""
    global _constraints_cache
    if _constraints_cache is not None:
        return _constraints_cache

    result: dict[str, str] = {}
    if not CONSTRAINTS_TXT.exists():
        _constraints_cache = result
        return result

    for raw_line in CONSTRAINTS_TXT.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        pkg_name = _extract_package_name(line)
        ver_spec = _extract_version_spec(line)
        if pkg_name and ver_spec:
            result[pkg_name] = ver_spec
    _constraints_cache = result
    return result


def _read_dockerfile(service_name: str) -> str:
    """Return Dockerfile content for the service, or empty string.
    إرجاع محتوى Dockerfile للخدمة."""
    path = SERVICES_DIR / service_name / "Dockerfile"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Helpers – Node.js package.json
# ---------------------------------------------------------------------------

def _read_package_json(service_name: str) -> dict[str, Any]:
    """Return parsed package.json, cached.
    إرجاع package.json المُحلَّل مع التخزين المؤقت."""
    if service_name not in _package_json_cache:
        path = SERVICES_DIR / service_name / "package.json"
        _package_json_cache[service_name] = json.loads(
            path.read_text(encoding="utf-8")
        )
    return _package_json_cache[service_name]


# ═══════════════════════════════════════════════════════════════════════════
# 1. TestPythonRequirementsFormat
# التحقق من تنسيق ملفات المتطلبات للخدمات بايثون
# ═══════════════════════════════════════════════════════════════════════════


class TestPythonRequirementsFormat:
    """Validate format and hygiene of Python requirements.txt files.
    التحقق من تنسيق ونظافة ملفات requirements.txt لخدمات بايثون."""

    @pytest.mark.parametrize("service", ALL_PYTHON_SERVICES)
    def test_pinned_versions(self, service: str) -> None:
        """Production requirements must have version specifiers (not bare package names).
        يجب أن تحتوي متطلبات الإنتاج على محددات إصدار."""
        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        unpinned: list[str] = []

        for line in lines:
            ver_spec = _extract_version_spec(line)
            if not ver_spec:
                # No version specifier at all — completely unpinned
                unpinned.append(line)

        assert not unpinned, (
            f"[{service}] requirements.txt has completely unpinned dependencies "
            f"(add at least a minimum version with >=X.Y.Z):\n"
            + "\n".join(f"  - {p}" for p in unpinned)
        )

    @pytest.mark.parametrize("service", ALL_PYTHON_SERVICES)
    def test_no_duplicate_packages(self, service: str) -> None:
        """No duplicate package names in requirements.txt.
        عدم وجود حزم مكررة في ملف المتطلبات."""
        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        names = [_extract_package_name(line) for line in lines]
        counts = Counter(names)
        duplicates = {name: cnt for name, cnt in counts.items() if cnt > 1}

        assert not duplicates, (
            f"[{service}] requirements.txt has duplicate packages:\n"
            + "\n".join(f"  - {name} (appears {cnt} times)" for name, cnt in duplicates.items())
        )

    @pytest.mark.parametrize("service", ALL_PYTHON_SERVICES)
    def test_no_commented_out_dependencies(self, service: str) -> None:
        """No commented-out lines that look like active dependency specifiers.
        عدم وجود حزم معلقة تبدو كأنها اعتماديات فعالة.

        Catches patterns like:
            # fastapi==0.115.0
            # nats-py>=2.6.0
        but ignores normal prose comments and CVE notes.
        """
        content = _read_requirements(service)
        suspicious: list[str] = []

        for lineno, raw_line in enumerate(content.splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped.startswith("#"):
                continue
            # Remove the leading # and whitespace
            after_hash = stripped.lstrip("#").strip()
            # Check if it looks like a pip specifier: package==X.Y.Z or package>=X
            if re.match(r"^[a-zA-Z][a-zA-Z0-9_.-]*\s*(==|>=|<=|~=|!=)\s*[0-9]", after_hash):
                suspicious.append(f"  line {lineno}: {stripped}")

        # Allow up to 10 commented-out deps (dev deps, optional deps, etc.)
        assert len(suspicious) <= 10, (
            f"[{service}] requirements.txt has {len(suspicious)} commented-out dependency "
            f"specifiers (remove or uncomment):\n" + "\n".join(suspicious)
        )

    @pytest.mark.parametrize("service", ALL_PYTHON_SERVICES)
    def test_valid_pip_format(self, service: str) -> None:
        """Requirements.txt must be valid pip format (no syntax errors).
        يجب أن يكون ملف المتطلبات بتنسيق pip صالح بدون أخطاء نحوية."""
        content = _read_requirements(service)
        errors: list[str] = []

        for lineno, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.split("#")[0].strip()
            if not line:
                continue

            # Valid lines: options (-c, -r, --...), or package specifiers
            if line.startswith("-"):
                # Options line, skip validation
                continue

            # Must start with a letter or digit (package name)
            if not re.match(r"^[A-Za-z0-9]", line):
                errors.append(f"  line {lineno}: invalid syntax: {raw_line.strip()}")
                continue

            # Validate specifier format: name[extras]<version_spec>
            if not re.match(
                r"^[A-Za-z0-9][A-Za-z0-9._-]*"   # package name
                r"(\[[\w,.-]+\])?"                  # optional extras
                r"\s*"                              # optional whitespace
                r"("                                # version spec group (optional)
                r"(==|>=|<=|~=|!=|>|<)"            # operator
                r"\s*[0-9]"                         # version starts with digit
                r")?"
                r".*$",
                line,
            ):
                errors.append(f"  line {lineno}: possibly malformed: {raw_line.strip()}")

        assert not errors, (
            f"[{service}] requirements.txt has syntax issues:\n" + "\n".join(errors)
        )

    @pytest.mark.parametrize("service", ALL_PYTHON_SERVICES)
    def test_no_insecure_packages(self, service: str) -> None:
        """Requirements must not pin known-insecure package versions.
        يجب ألا تثبت المتطلبات إصدارات معروفة بأنها غير آمنة."""
        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        violations: list[str] = []

        for line in lines:
            pkg_name = _extract_package_name(line)
            if pkg_name not in INSECURE_PACKAGES:
                continue

            min_safe_str, cve = INSECURE_PACKAGES[pkg_name]
            min_safe = _version_tuple(min_safe_str)
            pinned = _extract_pinned_version(line)

            if pinned:
                if _version_tuple(pinned) < min_safe:
                    violations.append(
                        f"  - {line.strip()} (minimum safe: {min_safe_str}, {cve})"
                    )
            else:
                # Check for upper-bounded ranges like <6.0 that exclude safe versions
                upper_match = re.search(r"<\s*([0-9][0-9a-zA-Z.]*)", line)
                if upper_match:
                    upper = _version_tuple(upper_match.group(1))
                    if upper <= min_safe:
                        violations.append(
                            f"  - {line.strip()} (upper bound excludes safe {min_safe_str}, {cve})"
                        )

        assert not violations, (
            f"[{service}] requirements.txt pins insecure package versions:\n"
            + "\n".join(violations)
        )


# ═══════════════════════════════════════════════════════════════════════════
# 2. TestPythonConstraintsConsistency
# التحقق من اتساق القيود بين المتطلبات المحلية والقيود المركزية
# ═══════════════════════════════════════════════════════════════════════════


class TestPythonConstraintsConsistency:
    """Packages in service requirements.txt must not conflict with root constraints.txt.
    يجب ألا تتعارض الحزم في ملف المتطلبات مع ملف القيود الجذري."""

    @pytest.mark.parametrize("service", ALL_PYTHON_SERVICES)
    def test_no_constraint_conflicts(self, service: str) -> None:
        """Service-pinned versions must not differ from constraints.txt pins.
        يجب ألا تختلف الإصدارات المثبتة في الخدمة عن إصدارات ملف القيود.

        If constraints.txt says fastapi==0.135.1, a service must not pin
        fastapi==0.120.0 (a different version). Range specifiers that are
        compatible with the constraint are allowed.
        """
        constraints = _parse_constraints()
        if not constraints:
            pytest.skip("constraints.txt not found or empty")

        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        conflicts: list[str] = []

        for line in lines:
            pkg_name = _extract_package_name(line)
            if pkg_name not in constraints:
                continue

            constraint_spec = constraints[pkg_name]
            service_pinned = _extract_pinned_version(line)
            constraint_pinned = _extract_pinned_version(f"{pkg_name}{constraint_spec}")

            # Only flag when BOTH are exact pins and they disagree
            if service_pinned and constraint_pinned and service_pinned != constraint_pinned:
                conflicts.append(
                    f"  - {pkg_name}: service pins =={service_pinned}, "
                    f"constraints.txt pins =={constraint_pinned}"
                )

        assert not conflicts, (
            f"[{service}] requirements.txt conflicts with constraints.txt:\n"
            + "\n".join(conflicts)
        )


# ═══════════════════════════════════════════════════════════════════════════
# 3. TestPythonCriticalDependencies
# التحقق من وجود الاعتماديات الحرجة بناءً على إعدادات Dockerfile
# ═══════════════════════════════════════════════════════════════════════════


class TestPythonCriticalDependencies:
    """FastAPI services must declare framework dependencies matching their Dockerfile.
    يجب أن تُعلن خدمات FastAPI عن الاعتماديات الحرجة المطابقة لإعدادات Dockerfile."""

    @pytest.mark.parametrize("service", list(PYTHON_SERVICES.keys()))
    def test_fastapi_in_requirements(self, service: str) -> None:
        """Python HTTP services must list fastapi in requirements.txt.
        يجب أن تحتوي خدمات بايثون ذات المنافذ على fastapi في المتطلبات."""
        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        pkg_names = {_extract_package_name(l) for l in lines}

        assert "fastapi" in pkg_names, (
            f"[{service}] is a Python HTTP service (port {PYTHON_SERVICES[service]}) "
            f"but requirements.txt does not list 'fastapi'"
        )

    @pytest.mark.parametrize("service", list(PYTHON_SERVICES.keys()))
    def test_database_driver_present(self, service: str) -> None:
        """Services with DATABASE_URL in Dockerfile must have a database driver.
        الخدمات التي تحتوي على DATABASE_URL يجب أن تتضمن برنامج تشغيل قاعدة البيانات."""
        dockerfile = _read_dockerfile(service)
        if "DATABASE_URL" not in dockerfile:
            pytest.skip(f"{service} Dockerfile does not reference DATABASE_URL")

        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        pkg_names = {_extract_package_name(l) for l in lines}

        db_drivers = {"asyncpg", "tortoise_orm", "sqlalchemy", "psycopg2_binary", "psycopg2"}
        found = pkg_names & db_drivers

        assert found, (
            f"[{service}] Dockerfile references DATABASE_URL but requirements.txt "
            f"has no database driver (expected one of: {', '.join(sorted(db_drivers))})"
        )

    @pytest.mark.parametrize("service", list(PYTHON_SERVICES.keys()))
    def test_nats_driver_present(self, service: str) -> None:
        """Services with NATS_URL in Dockerfile must have nats-py.
        الخدمات التي تحتوي على NATS_URL يجب أن تتضمن مكتبة nats-py."""
        dockerfile = _read_dockerfile(service)
        if "NATS_URL" not in dockerfile:
            pytest.skip(f"{service} Dockerfile does not reference NATS_URL")

        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        pkg_names = {_extract_package_name(l) for l in lines}

        assert "nats_py" in pkg_names or "nats" in pkg_names, (
            f"[{service}] Dockerfile references NATS_URL but requirements.txt "
            f"does not list 'nats-py'"
        )

    @pytest.mark.parametrize("service", list(PYTHON_SERVICES.keys()))
    def test_redis_driver_present(self, service: str) -> None:
        """Services with REDIS_URL in Dockerfile must have a Redis client.
        الخدمات التي تحتوي على REDIS_URL يجب أن تتضمن مكتبة Redis."""
        dockerfile = _read_dockerfile(service)
        if "REDIS_URL" not in dockerfile:
            pytest.skip(f"{service} Dockerfile does not reference REDIS_URL")

        content = _read_requirements(service)
        lines = _parse_requirements_lines(content)
        pkg_names = {_extract_package_name(l) for l in lines}

        redis_clients = {"redis", "aioredis", "redis_py"}
        found = pkg_names & redis_clients

        assert found, (
            f"[{service}] Dockerfile references REDIS_URL but requirements.txt "
            f"has no Redis client (expected one of: {', '.join(sorted(redis_clients))})"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 4. TestNodePackageJsonValidation
# التحقق من صحة ملفات package.json لخدمات Node.js
# ═══════════════════════════════════════════════════════════════════════════


class TestNodePackageJsonValidation:
    """Validate Node.js package.json structure and conventions.
    التحقق من بنية واتفاقيات ملفات package.json لخدمات Node.js."""

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_valid_json(self, service: str) -> None:
        """package.json must be valid JSON.
        يجب أن يكون package.json بتنسيق JSON صالح."""
        path = SERVICES_DIR / service / "package.json"
        raw = path.read_text(encoding="utf-8")
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            pytest.fail(
                f"[{service}] package.json is not valid JSON: {exc}"
            )

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_has_name_field(self, service: str) -> None:
        """package.json must have a 'name' field.
        يجب أن يحتوي package.json على حقل 'name'."""
        pkg = _read_package_json(service)
        assert "name" in pkg and pkg["name"], (
            f"[{service}] package.json is missing the 'name' field"
        )

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_has_scripts(self, service: str) -> None:
        """package.json must have a 'scripts' section with 'start' or 'build'.
        يجب أن يحتوي package.json على قسم 'scripts' مع 'start' أو 'build'."""
        pkg = _read_package_json(service)
        scripts = pkg.get("scripts", {})

        assert scripts, (
            f"[{service}] package.json is missing the 'scripts' section"
        )
        assert "start" in scripts or "build" in scripts, (
            f"[{service}] package.json 'scripts' must contain 'start' or 'build' "
            f"(found: {', '.join(sorted(scripts.keys()))})"
        )

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_dependency_version_ranges(self, service: str) -> None:
        """Dependencies should use ^ or ~ prefixes, not * or 'latest'.
        يجب أن تستخدم الاعتماديات بادئات ^ أو ~ وليس * أو 'latest'."""
        pkg = _read_package_json(service)
        deps = pkg.get("dependencies", {})
        violations: list[str] = []

        for name, version in deps.items():
            if isinstance(version, str):
                # Skip workspace/file references
                if version.startswith(("file:", "workspace:", "link:")):
                    continue
                if version in ("*", "latest"):
                    violations.append(f"  - {name}: {version}")

        assert not violations, (
            f"[{service}] package.json has wildcard/latest dependencies "
            f"(use ^ or ~ ranges):\n" + "\n".join(violations)
        )

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_nestjs_core_present(self, service: str) -> None:
        """NestJS services must list @nestjs/core in dependencies.
        يجب أن تحتوي خدمات NestJS على @nestjs/core في الاعتماديات."""
        pkg = _read_package_json(service)
        deps = pkg.get("dependencies", {})
        dev_deps = pkg.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}

        # Check if this is a NestJS service by looking for nest references
        is_nestjs = (
            "@nestjs/core" in all_deps
            or "@nestjs/common" in all_deps
            or any("nest" in str(v) for v in pkg.get("scripts", {}).values())
        )

        if not is_nestjs:
            pytest.skip(f"{service} is not a NestJS service")

        assert "@nestjs/core" in deps, (
            f"[{service}] appears to be a NestJS service but @nestjs/core "
            f"is not in 'dependencies'"
        )

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_no_duplicate_deps(self, service: str) -> None:
        """No package should appear in both dependencies and devDependencies.
        يجب ألا تظهر أي حزمة في كل من dependencies و devDependencies."""
        pkg = _read_package_json(service)
        deps = set(pkg.get("dependencies", {}).keys())
        dev_deps = set(pkg.get("devDependencies", {}).keys())
        overlap = deps & dev_deps

        assert not overlap, (
            f"[{service}] package.json has packages in both dependencies and "
            f"devDependencies:\n"
            + "\n".join(f"  - {p}" for p in sorted(overlap))
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5. TestNodePackageJsonSecurity
# التحقق الأمني لملفات package.json
# ═══════════════════════════════════════════════════════════════════════════


class TestNodePackageJsonSecurity:
    """Security checks for Node.js package.json.
    فحوصات أمنية لملفات package.json لخدمات Node.js."""

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_no_deprecated_packages(self, service: str) -> None:
        """Dependencies must not include known deprecated packages.
        يجب ألا تتضمن الاعتماديات حزماً معروفة بأنها مهملة."""
        pkg = _read_package_json(service)
        deps = pkg.get("dependencies", {})
        dev_deps = pkg.get("devDependencies", {})
        all_dep_names = set(deps.keys()) | set(dev_deps.keys())
        found: list[str] = []

        for dep_name in all_dep_names:
            if dep_name in DEPRECATED_NODE_PACKAGES:
                found.append(
                    f"  - {dep_name}: {DEPRECATED_NODE_PACKAGES[dep_name]}"
                )

        assert not found, (
            f"[{service}] package.json includes deprecated packages:\n"
            + "\n".join(found)
        )

    @pytest.mark.parametrize("service", ALL_NODE_SERVICES)
    def test_engines_node_version(self, service: str) -> None:
        """The 'engines' field should specify Node.js >= 20.
        يجب أن يحدد حقل 'engines' إصدار Node.js >= 20."""
        pkg = _read_package_json(service)
        engines = pkg.get("engines", {})

        if not engines:
            pytest.skip(
                f"{service} package.json has no 'engines' field "
                f"(recommended to add: engines.node >= 20)"
            )

        node_spec = engines.get("node", "")
        if not node_spec:
            pytest.skip(f"{service} package.json engines has no 'node' field")

        # Extract the minimum version from the node spec
        # Handles: ">=20.0.0", "^20", ">=20", "20.x", etc.
        version_match = re.search(r"(\d+)", node_spec)
        if version_match:
            min_major = int(version_match.group(1))
            assert min_major >= 20, (
                f"[{service}] engines.node specifies {node_spec} "
                f"(minimum major version {min_major} < 20). "
                f"Platform requires Node.js >= 20."
            )


# ═══════════════════════════════════════════════════════════════════════════
# 6. TestSharedDependencyVersions
# التحقق من اتساق إصدارات الاعتماديات المشتركة عبر الخدمات
# ═══════════════════════════════════════════════════════════════════════════


class TestSharedDependencyVersions:
    """Cross-service version consistency checks.
    فحوصات اتساق الإصدارات عبر الخدمات."""

    def test_fastapi_version_consistency(self) -> None:
        """All Python services using fastapi should use compatible versions.
        يجب أن تستخدم جميع خدمات بايثون إصدارات متوافقة من fastapi."""
        versions: dict[str, str] = {}

        for service in ALL_PYTHON_SERVICES:
            try:
                content = _read_requirements(service)
            except FileNotFoundError:
                continue
            lines = _parse_requirements_lines(content)
            for line in lines:
                if _extract_package_name(line) == "fastapi":
                    pinned = _extract_pinned_version(line)
                    if pinned:
                        versions[service] = pinned
                    break

        if len(versions) < 2:
            pytest.skip("Fewer than 2 services pin fastapi with ==")

        unique_versions = set(versions.values())
        if len(unique_versions) > 1:
            version_groups: dict[str, list[str]] = {}
            for svc, ver in versions.items():
                version_groups.setdefault(ver, []).append(svc)

            report = "\n".join(
                f"  fastapi=={ver}: {', '.join(sorted(svcs))}"
                for ver, svcs in sorted(version_groups.items())
            )
            pytest.fail(
                f"Python services use {len(unique_versions)} different fastapi "
                f"versions (expected 1):\n{report}"
            )

    def test_pydantic_v2_required(self) -> None:
        """All Python services using pydantic should use v2 (>=2.0).
        يجب أن تستخدم جميع خدمات بايثون الإصدار الثاني من pydantic (>=2.0)."""
        v1_services: list[str] = []

        for service in ALL_PYTHON_SERVICES:
            try:
                content = _read_requirements(service)
            except FileNotFoundError:
                continue
            lines = _parse_requirements_lines(content)
            for line in lines:
                if _extract_package_name(line) == "pydantic":
                    pinned = _extract_pinned_version(line)
                    if pinned and _version_tuple(pinned) < (2, 0):
                        v1_services.append(f"{service} (pydantic=={pinned})")
                    elif not pinned:
                        # Check for explicit <2 upper bound
                        if re.search(r"<\s*2(\.0)?", line):
                            v1_services.append(f"{service} ({line.strip()})")
                    break

        assert not v1_services, (
            "The following services still use Pydantic v1 (platform requires v2):\n"
            + "\n".join(f"  - {s}" for s in v1_services)
        )

    def test_nestjs_core_version_consistency(self) -> None:
        """All Node services using @nestjs/core should use the same major version.
        يجب أن تستخدم جميع خدمات Node.js نفس الإصدار الرئيسي من @nestjs/core."""
        versions: dict[str, str] = {}

        for service in ALL_NODE_SERVICES:
            try:
                pkg = _read_package_json(service)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
            deps = pkg.get("dependencies", {})
            if "@nestjs/core" in deps:
                versions[service] = deps["@nestjs/core"]

        if len(versions) < 2:
            pytest.skip("Fewer than 2 Node services use @nestjs/core")

        # Extract major versions
        major_versions: dict[str, set[str]] = {}
        for svc, ver_spec in versions.items():
            match = re.search(r"(\d+)", ver_spec)
            if match:
                major = match.group(1)
                major_versions.setdefault(major, set()).add(svc)

        if len(major_versions) > 1:
            report = "\n".join(
                f"  v{major}.x: {', '.join(sorted(svcs))}"
                for major, svcs in sorted(major_versions.items())
            )
            pytest.fail(
                f"Node services use {len(major_versions)} different @nestjs/core "
                f"major versions (expected 1):\n{report}"
            )

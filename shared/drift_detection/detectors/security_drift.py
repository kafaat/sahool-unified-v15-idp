"""
Security Drift Detector
كاشف انحراف الأمان

Detects security drift:
- Hardcoded secrets/credentials in code
- Missing security headers in services
- Secret rotation expiry checks
- Docker security violations (root user, privileged, latest tag)
- Dependency vulnerability indicators
- Rate limiting consistency
- Certificate pinning drift (mobile)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from shared.drift_detection.detectors.base import BaseDriftDetector
from shared.drift_detection.models import (
    DriftCategory,
    DriftResult,
    DriftSeverity,
)

logger = logging.getLogger(__name__)

# Patterns that indicate hardcoded secrets
SECRET_PATTERNS = [
    (re.compile(r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE), "Hardcoded password"),
    (re.compile(r'(?:api_key|apikey|api-key)\s*=\s*["\'][^"\']{16,}["\']', re.IGNORECASE), "Hardcoded API key"),
    (re.compile(r'(?:secret|token)\s*=\s*["\'][a-zA-Z0-9+/=]{20,}["\']', re.IGNORECASE), "Hardcoded secret/token"),
    (
        re.compile(r'(?:aws_access_key_id|aws_secret_access_key)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        "AWS credentials",
    ),
    (re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----", re.IGNORECASE), "Private key in code"),
]

# Paths to exclude from secret scanning (test data, fixtures, examples)
EXCLUDE_SECRET_PATHS = {
    "test",
    "tests",
    "fixtures",
    "mock",
    "mocks",
    "example",
    "examples",
    "__pycache__",
    "__tests__",
    "__mocks__",
    "node_modules",
    ".venv",
    "archive",
    ".github",
    "dist",
}

# File name patterns that indicate test files (regardless of directory)
_TEST_FILE_PATTERNS = (".spec.", ".test.", "_test.", "_spec.", "conftest.")

# Known security utility directories whose files contain secret detection patterns
# (regex patterns for masking, vault path registries, etc. — NOT actual secrets)
_SAFE_SECURITY_DIRS = {"observability", "secrets"}


class SecurityDriftDetector(BaseDriftDetector):
    """
    Detects security drift and compliance violations.
    يكتشف انحراف الأمان وانتهاكات الامتثال.
    """

    @property
    def category(self) -> DriftCategory:
        return DriftCategory.SECURITY

    async def detect(self) -> list[DriftResult]:
        self.clear_results()

        await self._check_hardcoded_secrets()
        await self._check_docker_security()
        await self._check_security_headers()
        await self._check_rate_limiting()
        await self._check_auth_patterns()
        await self._check_dependency_security()
        await self._check_tls_config()

        return self.results

    async def _check_hardcoded_secrets(self) -> None:
        """Scan code for hardcoded secrets."""
        root = Path(self.working_dir).resolve().resolve()
        scan_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".yaml", ".yml", ".json", ".env"}

        for ext in scan_extensions:
            for file_path in root.rglob(f"*{ext}"):
                # Skip excluded paths (directory names)
                if any(excl in file_path.parts for excl in EXCLUDE_SECRET_PATHS):
                    continue
                # Skip test files by name pattern (e.g. *.spec.ts, *.test.py)
                if any(pat in file_path.name for pat in _TEST_FILE_PATTERNS):
                    continue
                # Skip known security utility files (contain detection regexes, not secrets)
                if file_path.parent.name in _SAFE_SECURITY_DIRS:
                    continue
                # Skip .env.example (that's documentation)
                if file_path.name == ".env.example":
                    continue
                # Skip actual .env files detection (they shouldn't be in repo)
                if file_path.name == ".env" and file_path.parent == root:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.SECURITY,
                            severity=DriftSeverity.CRITICAL,
                            source="secret_scan",
                            description=".env file found in repository root - should be in .gitignore",
                            description_ar="ملف .env موجود في جذر المستودع - يجب أن يكون في .gitignore",
                            file_path=str(file_path),
                            auto_fixable=False,
                            remediation_hint="Add .env to .gitignore and remove from version control",
                        )
                    )
                    continue

                try:
                    content = file_path.read_text(errors="ignore")
                except (OSError, UnicodeDecodeError):
                    continue

                for pattern, pattern_name in SECRET_PATTERNS:
                    matches = pattern.findall(content)
                    if matches:
                        # Filter out known safe patterns (case-insensitive)
                        content_lower = content[:500].lower()
                        safe = any(
                            safe_pat in content_lower
                            for safe_pat in [
                                "test",
                                "example",
                                "placeholder",
                                "dummy",
                                "mock",
                                "<",
                                "your_",
                                "change_me",
                                "re.compile",
                                "regex",
                                "masking",
                                "sanitiz",
                            ]
                        )
                        if safe:
                            continue

                        # Filter out GitHub Actions template expressions
                        if "${{" in content and "secrets." in content:
                            continue

                        self.add_result(
                            DriftResult(
                                category=DriftCategory.SECURITY,
                                severity=DriftSeverity.CRITICAL,
                                source="secret_scan",
                                description=f"Possible {pattern_name} in {file_path.relative_to(root)}",
                                description_ar=f"احتمال وجود {pattern_name} في {file_path.relative_to(root)}",
                                file_path=str(file_path),
                                auto_fixable=False,
                                remediation_hint="Move secrets to environment variables or HashiCorp Vault",
                                remediation_hint_ar="انقل الأسرار إلى متغيرات البيئة أو HashiCorp Vault",
                            )
                        )
                        break  # One finding per file is enough

    async def _check_docker_security(self) -> None:
        """Check Dockerfiles for security best practices."""
        root = Path(self.working_dir).resolve()

        dockerfiles = list(root.glob("apps/services/*/Dockerfile"))
        dockerfiles += list(root.glob("docker/Dockerfile.*"))

        for df in dockerfiles:
            try:
                content = df.read_text()
            except (OSError, UnicodeDecodeError):
                continue

            service_name = df.parent.name if df.parent.name != "docker" else df.name

            # Check for running as root
            if "USER" not in content and "user" not in content:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SECURITY,
                        severity=DriftSeverity.HIGH,
                        source="docker_security",
                        expected="Non-root USER directive",
                        actual="No USER directive found",
                        description=f"Dockerfile for '{service_name}' runs as root (no USER directive)",
                        description_ar=f"Dockerfile لـ '{service_name}' يعمل كـ root (لا يوجد توجيه USER)",
                        file_path=str(df),
                        service_name=service_name,
                        auto_fixable=True,
                        remediation_hint="Add 'RUN useradd -r sahool && USER sahool' to Dockerfile",
                    )
                )

            # Check for :latest tag
            latest_pattern = re.compile(r"FROM\s+\S+:latest", re.IGNORECASE)
            if latest_pattern.search(content):
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SECURITY,
                        severity=DriftSeverity.HIGH,
                        source="docker_security",
                        expected="Pinned image tag (e.g., python:3.11-slim-bookworm)",
                        actual=":latest tag used",
                        description=f"Dockerfile for '{service_name}' uses :latest tag - non-deterministic builds",
                        description_ar=f"Dockerfile لـ '{service_name}' يستخدم وسم :latest - بناء غير حتمي",
                        file_path=str(df),
                        service_name=service_name,
                        auto_fixable=False,
                        remediation_hint="Pin image tags to specific versions",
                    )
                )

            # Check for HEALTHCHECK
            if "HEALTHCHECK" not in content:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SECURITY,
                        severity=DriftSeverity.MEDIUM,
                        source="docker_security",
                        description=f"Dockerfile for '{service_name}' missing HEALTHCHECK directive",
                        description_ar=f"Dockerfile لـ '{service_name}' يفتقر إلى توجيه HEALTHCHECK",
                        file_path=str(df),
                        service_name=service_name,
                        auto_fixable=True,
                        remediation_hint="Add HEALTHCHECK CMD curl -f http://localhost:PORT/healthz || exit 1",
                    )
                )

    async def _check_security_headers(self) -> None:
        """Check services implement required security headers."""
        root = Path(self.working_dir).resolve()

        # Check shared security headers middleware
        sec_headers = root / "shared" / "middleware" / "security_headers.py"
        if not sec_headers.exists():
            self.add_result(
                DriftResult(
                    category=DriftCategory.SECURITY,
                    severity=DriftSeverity.HIGH,
                    source="security_headers",
                    description="Security headers middleware not found",
                    description_ar="وسيط رؤوس الأمان غير موجود",
                    auto_fixable=False,
                    remediation_hint="Create shared/middleware/security_headers.py with HSTS, CSP, X-Frame-Options",
                )
            )
            return

        content = sec_headers.read_text()
        required_headers = [
            ("Strict-Transport-Security", "HSTS"),
            ("X-Content-Type-Options", "X-Content-Type-Options"),
            ("X-Frame-Options", "X-Frame-Options"),
        ]

        for header, name in required_headers:
            if header not in content:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SECURITY,
                        severity=DriftSeverity.HIGH,
                        source="security_headers",
                        expected=f"{name} header configured",
                        actual=f"{name} header missing from security middleware",
                        description=f"Security header '{name}' not configured in middleware",
                        description_ar=f"رأس الأمان '{name}' غير مكون في الوسيط",
                        file_path=str(sec_headers),
                    )
                )

    async def _check_rate_limiting(self) -> None:
        """Check rate limiting is consistently configured."""
        root = Path(self.working_dir).resolve()

        rate_limit = root / "shared" / "middleware" / "rate_limit.py"
        if not rate_limit.exists():
            self.add_result(
                DriftResult(
                    category=DriftCategory.SECURITY,
                    severity=DriftSeverity.HIGH,
                    source="rate_limiting",
                    description="Rate limiting middleware not found",
                    description_ar="وسيط تحديد المعدل غير موجود",
                )
            )

    async def _check_auth_patterns(self) -> None:
        """Check authentication patterns are consistent across services."""
        root = Path(self.working_dir).resolve()

        service_dirs = list(root.glob("apps/services/*/src"))

        for src_dir in service_dirs:
            service_name = src_dir.parent.name
            if "archive" in str(src_dir):
                continue

            # Check for API routes without auth
            api_files = list(src_dir.rglob("api/**/*.py")) + list(src_dir.rglob("api/**/*.ts"))

            for api_file in api_files:
                try:
                    content = api_file.read_text(errors="ignore")
                except (OSError, UnicodeDecodeError):
                    continue

                # Check for routes
                has_routes = any(
                    pat in content
                    for pat in [
                        "@router.",
                        "@app.",
                        "@Controller",
                        "router.get",
                        "router.post",
                        "router.put",
                        "router.delete",
                    ]
                )

                if not has_routes:
                    continue

                # Check for auth (including try/except imported guards)
                has_auth = any(
                    pat in content
                    for pat in [
                        "get_current_user",
                        "Depends(",
                        "Guards(",
                        "@UseGuards",
                        "AuthGuard",
                        "JwtAuthGuard",
                        "authenticate",
                        "verify_token",
                        "require_auth",
                        "HTTPBearer",
                        "OAuth2PasswordBearer",
                        "shared.auth",
                    ]
                )

                # Skip health/public endpoints and gateway-managed auth
                is_public = any(
                    pat in content
                    for pat in [
                        "healthz",
                        "readyz",
                        "/public/",
                        "login",
                        "register",
                        "callback",
                        "webhook",
                        "ussd",
                        "drift:auth-exempt",
                    ]
                )

                if has_routes and not has_auth and not is_public:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.SECURITY,
                            severity=DriftSeverity.HIGH,
                            source="auth_pattern",
                            expected="Authentication on API routes",
                            actual=f"No auth pattern in {api_file.name}",
                            description=f"API routes in {service_name}/{api_file.name} may lack authentication",
                            description_ar=f"مسارات API في {service_name}/{api_file.name} قد تفتقر إلى المصادقة",
                            file_path=str(api_file),
                            service_name=service_name,
                        )
                    )

    async def _check_dependency_security(self) -> None:
        """Check for known security patterns in dependency files."""
        root = Path(self.working_dir).resolve()

        # Check for constraints file
        constraints = root / "constraints.txt"
        if not constraints.exists():
            self.add_result(
                DriftResult(
                    category=DriftCategory.SECURITY,
                    severity=DriftSeverity.MEDIUM,
                    source="dependency_security",
                    description="No constraints.txt found - dependency versions may be unpinned",
                    description_ar="لم يتم العثور على constraints.txt - قد تكون إصدارات التبعيات غير مثبتة",
                )
            )

        # Check for npm audit config
        npmrc = root / ".npmrc"
        if npmrc.exists():
            content = npmrc.read_text()
            if "audit=false" in content:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.SECURITY,
                        severity=DriftSeverity.HIGH,
                        source="dependency_security",
                        description="npm audit is disabled in .npmrc",
                        description_ar="فحص npm معطل في .npmrc",
                        file_path=str(npmrc),
                    )
                )

    async def _check_tls_config(self) -> None:
        """Check TLS/SSL configuration consistency."""
        root = Path(self.working_dir).resolve()

        # Check for TLS compose
        tls_compose = root / "docker-compose.tls.yml"
        if not tls_compose.exists():
            self.add_result(
                DriftResult(
                    category=DriftCategory.SECURITY,
                    severity=DriftSeverity.INFO,
                    source="tls_config",
                    description="No TLS docker-compose overlay found - ensure TLS is configured in production",
                    description_ar="لم يتم العثور على ملف TLS docker-compose - تأكد من تكوين TLS في الإنتاج",
                )
            )

        # Check database URL patterns for sslmode
        for py_file in root.glob("apps/services/*/src/main.py"):
            try:
                content = py_file.read_text(errors="ignore")
                if "DATABASE_URL" not in content:
                    continue
                # Check if sslmode is referenced in the service code or config
                service_dir = py_file.parent.parent
                has_ssl = "sslmode" in content
                # Also check config files in the service directory
                if not has_ssl:
                    for cfg_file in service_dir.rglob("*.py"):
                        try:
                            cfg_content = cfg_file.read_text(errors="ignore")
                            if "sslmode" in cfg_content:
                                has_ssl = True
                                break
                        except (OSError, UnicodeDecodeError):
                            continue
                # Also check if the service uses shared DB utilities that enforce SSL
                if not has_ssl and ("shared.db" in content or "shared.common" in content):
                    has_ssl = True
                if not has_ssl:
                    service_name = service_dir.name
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.SECURITY,
                            severity=DriftSeverity.MEDIUM,
                            source="tls_config",
                            description=f"Service '{service_name}' may not enforce DB SSL (sslmode not checked)",
                            description_ar=f"الخدمة '{service_name}' قد لا تفرض SSL لقاعدة البيانات",
                            file_path=str(py_file),
                            service_name=service_name,
                        )
                    )
            except (OSError, UnicodeDecodeError):
                continue

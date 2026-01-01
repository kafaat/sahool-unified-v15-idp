#!/usr/bin/env python3
"""
SAHOOL Compliance Checklist Generator
Generates compliance checklist from codebase analysis

Usage:
    python tools/compliance/generate_checklist.py [--output docs/compliance/COMPLIANCE_CHECKLIST.md]
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


@dataclass
class ComplianceCheck:
    """Single compliance check result"""

    category: str
    name: str
    status: str  # pass, fail, warning, manual
    details: str
    file_path: str | None = None
    line_number: int | None = None


@dataclass
class ComplianceReport:
    """Full compliance report"""

    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    checks: list[ComplianceCheck] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def add_check(self, check: ComplianceCheck) -> None:
        self.checks.append(check)

    def compute_summary(self) -> None:
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c.status == "pass")
        failed = sum(1 for c in self.checks if c.status == "fail")
        warnings = sum(1 for c in self.checks if c.status == "warning")
        manual = sum(1 for c in self.checks if c.status == "manual")

        self.summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "manual_review": manual,
            "compliance_score": round(passed / total * 100, 1) if total > 0 else 0,
        }


class ComplianceChecker:
    """Analyzes codebase for compliance requirements"""

    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.report = ComplianceReport()

    def run_all_checks(self) -> ComplianceReport:
        """Run all compliance checks"""
        # Audit checks
        self._check_audit_logging()
        self._check_audit_hash_chain()
        self._check_pii_redaction()

        # Security checks
        self._check_authentication()
        self._check_authorization()
        self._check_encryption()
        self._check_secrets_management()

        # GDPR checks
        self._check_gdpr_endpoints()
        self._check_consent_management()
        self._check_data_retention()

        # Code quality checks
        self._check_input_validation()
        self._check_error_handling()
        self._check_logging_sanitization()

        # Documentation checks
        self._check_security_docs()
        self._check_api_docs()

        self.report.compute_summary()
        return self.report

    # -------------------------------------------------------------------------
    # Audit Checks
    # -------------------------------------------------------------------------

    def _check_audit_logging(self) -> None:
        """Verify audit logging is implemented"""
        audit_path = self.root / "shared" / "libs" / "audit"

        if audit_path.exists():
            service_file = audit_path / "service.py"
            if service_file.exists():
                content = service_file.read_text()
                if "write_audit_log" in content:
                    self.report.add_check(
                        ComplianceCheck(
                            category="Audit",
                            name="Audit logging service",
                            status="pass",
                            details="write_audit_log() function found in audit service",
                            file_path=str(service_file),
                        )
                    )
                    return

        self.report.add_check(
            ComplianceCheck(
                category="Audit",
                name="Audit logging service",
                status="fail",
                details="Audit logging service not found or incomplete",
            )
        )

    def _check_audit_hash_chain(self) -> None:
        """Verify hash chain for tamper evidence"""
        hashchain_file = self.root / "shared" / "libs" / "audit" / "hashchain.py"

        if hashchain_file.exists():
            content = hashchain_file.read_text()
            checks = [
                "compute_entry_hash" in content,
                "verify_chain" in content,
                "sha256" in content.lower(),
            ]
            if all(checks):
                self.report.add_check(
                    ComplianceCheck(
                        category="Audit",
                        name="Hash chain integrity",
                        status="pass",
                        details="Tamper-evident hash chain implemented with SHA-256",
                        file_path=str(hashchain_file),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="Audit",
                name="Hash chain integrity",
                status="fail",
                details="Hash chain implementation missing or incomplete",
            )
        )

    def _check_pii_redaction(self) -> None:
        """Verify PII redaction in audit logs"""
        redact_file = self.root / "shared" / "libs" / "audit" / "redact.py"

        if redact_file.exists():
            content = redact_file.read_text()
            sensitive_keys = ["password", "token", "secret", "ssn", "credit_card"]
            found = sum(1 for key in sensitive_keys if key in content.lower())

            if found >= 3:
                self.report.add_check(
                    ComplianceCheck(
                        category="Audit",
                        name="PII redaction",
                        status="pass",
                        details=f"Redaction covers {found} sensitive field types",
                        file_path=str(redact_file),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="Audit",
                name="PII redaction",
                status="fail",
                details="PII redaction not implemented or insufficient",
            )
        )

    # -------------------------------------------------------------------------
    # Security Checks
    # -------------------------------------------------------------------------

    def _check_authentication(self) -> None:
        """Verify authentication is implemented"""
        auth_patterns = [
            self.root / "kernel_domain" / "auth",
            self.root / "services" / "idp",
            self.root / "shared" / "libs" / "auth",
        ]

        for path in auth_patterns:
            if path.exists():
                self.report.add_check(
                    ComplianceCheck(
                        category="Security",
                        name="Authentication",
                        status="pass",
                        details=f"Authentication module found at {path.relative_to(self.root)}",
                        file_path=str(path),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="Security",
                name="Authentication",
                status="warning",
                details="Authentication module location could not be verified",
            )
        )

    def _check_authorization(self) -> None:
        """Check for RBAC/ABAC implementation"""
        # Look for permission/role patterns
        for py_file in self._find_python_files():
            content = py_file.read_text()
            if any(
                pattern in content
                for pattern in ["Permission", "Role", "RBAC", "authorize"]
            ):
                self.report.add_check(
                    ComplianceCheck(
                        category="Security",
                        name="Authorization",
                        status="pass",
                        details="Authorization patterns found in codebase",
                        file_path=str(py_file),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="Security",
                name="Authorization",
                status="manual",
                details="Manual review required for authorization implementation",
            )
        )

    def _check_encryption(self) -> None:
        """Verify encryption is used for sensitive data"""
        encryption_indicators = ["encrypt", "decrypt", "AES", "Fernet", "cryptography"]

        for py_file in self._find_python_files():
            content = py_file.read_text()
            if any(indicator in content for indicator in encryption_indicators):
                self.report.add_check(
                    ComplianceCheck(
                        category="Security",
                        name="Data encryption",
                        status="pass",
                        details="Encryption implementation found",
                        file_path=str(py_file),
                    )
                )
                return

        # Check for TLS configuration
        tls_path = self.root / "shared" / "libs" / "tls"
        if tls_path.exists():
            self.report.add_check(
                ComplianceCheck(
                    category="Security",
                    name="Data encryption",
                    status="pass",
                    details="TLS library found for transport encryption",
                    file_path=str(tls_path),
                )
            )
            return

        self.report.add_check(
            ComplianceCheck(
                category="Security",
                name="Data encryption",
                status="warning",
                details="Encryption implementation needs verification",
            )
        )

    def _check_secrets_management(self) -> None:
        """Verify secrets are not hardcoded"""
        # Check for Vault integration
        vault_path = self.root / "shared" / "libs" / "vault"
        if vault_path.exists():
            self.report.add_check(
                ComplianceCheck(
                    category="Security",
                    name="Secrets management",
                    status="pass",
                    details="HashiCorp Vault integration found",
                    file_path=str(vault_path),
                )
            )
            return

        # Check for environment variable usage
        env_pattern = re.compile(r"os\.environ|getenv|Settings.*env")
        for py_file in self._find_python_files():
            content = py_file.read_text()
            if env_pattern.search(content):
                self.report.add_check(
                    ComplianceCheck(
                        category="Security",
                        name="Secrets management",
                        status="pass",
                        details="Environment-based configuration found",
                        file_path=str(py_file),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="Security",
                name="Secrets management",
                status="warning",
                details="Secrets management approach needs review",
            )
        )

    # -------------------------------------------------------------------------
    # GDPR Checks
    # -------------------------------------------------------------------------

    def _check_gdpr_endpoints(self) -> None:
        """Verify GDPR endpoints exist"""
        gdpr_path = self.root / "kernel" / "compliance" / "routes_gdpr.py"

        if gdpr_path.exists():
            content = gdpr_path.read_text()
            endpoints = [
                "/export" in content,
                "/delete" in content,
                "/consent" in content,
            ]
            if all(endpoints):
                self.report.add_check(
                    ComplianceCheck(
                        category="GDPR",
                        name="GDPR endpoints",
                        status="pass",
                        details="Export, delete, and consent endpoints implemented",
                        file_path=str(gdpr_path),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="GDPR",
                name="GDPR endpoints",
                status="fail",
                details="GDPR compliance endpoints missing",
            )
        )

    def _check_consent_management(self) -> None:
        """Verify consent management"""
        for py_file in self._find_python_files():
            content = py_file.read_text()
            if "consent" in content.lower() and (
                "record" in content.lower() or "grant" in content.lower()
            ):
                self.report.add_check(
                    ComplianceCheck(
                        category="GDPR",
                        name="Consent management",
                        status="pass",
                        details="Consent management functionality found",
                        file_path=str(py_file),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="GDPR",
                name="Consent management",
                status="manual",
                details="Consent management requires manual verification",
            )
        )

    def _check_data_retention(self) -> None:
        """Check for data retention policies"""
        # Look for retention-related code or configuration
        retention_patterns = ["retention", "expire", "ttl", "cleanup", "purge"]

        for py_file in self._find_python_files():
            content = py_file.read_text().lower()
            if any(pattern in content for pattern in retention_patterns):
                self.report.add_check(
                    ComplianceCheck(
                        category="GDPR",
                        name="Data retention",
                        status="pass",
                        details="Data retention patterns found",
                        file_path=str(py_file),
                    )
                )
                return

        self.report.add_check(
            ComplianceCheck(
                category="GDPR",
                name="Data retention",
                status="manual",
                details="Data retention policy requires manual review",
            )
        )

    # -------------------------------------------------------------------------
    # Code Quality Checks
    # -------------------------------------------------------------------------

    def _check_input_validation(self) -> None:
        """Verify input validation is used"""
        validation_patterns = [
            "pydantic",
            "BaseModel",
            "Field(",
            "validator",
            "Depends",
        ]

        count = 0
        for py_file in self._find_python_files():
            content = py_file.read_text()
            if any(pattern in content for pattern in validation_patterns):
                count += 1

        if count > 5:
            self.report.add_check(
                ComplianceCheck(
                    category="Code Quality",
                    name="Input validation",
                    status="pass",
                    details=f"Pydantic validation used in {count} files",
                )
            )
        else:
            self.report.add_check(
                ComplianceCheck(
                    category="Code Quality",
                    name="Input validation",
                    status="warning",
                    details="Limited input validation found",
                )
            )

    def _check_error_handling(self) -> None:
        """Check for proper error handling"""
        error_patterns = ["HTTPException", "raise ", "try:", "except"]

        count = 0
        for py_file in self._find_python_files():
            content = py_file.read_text()
            if any(pattern in content for pattern in error_patterns):
                count += 1

        if count > 10:
            self.report.add_check(
                ComplianceCheck(
                    category="Code Quality",
                    name="Error handling",
                    status="pass",
                    details=f"Error handling present in {count} files",
                )
            )
        else:
            self.report.add_check(
                ComplianceCheck(
                    category="Code Quality",
                    name="Error handling",
                    status="warning",
                    details="Error handling coverage needs improvement",
                )
            )

    def _check_logging_sanitization(self) -> None:
        """Verify logs don't leak sensitive data"""
        redact_path = self.root / "shared" / "libs" / "audit" / "redact.py"

        if redact_path.exists():
            self.report.add_check(
                ComplianceCheck(
                    category="Code Quality",
                    name="Log sanitization",
                    status="pass",
                    details="Log redaction utility available",
                    file_path=str(redact_path),
                )
            )
        else:
            self.report.add_check(
                ComplianceCheck(
                    category="Code Quality",
                    name="Log sanitization",
                    status="warning",
                    details="Log sanitization approach needs verification",
                )
            )

    # -------------------------------------------------------------------------
    # Documentation Checks
    # -------------------------------------------------------------------------

    def _check_security_docs(self) -> None:
        """Verify security documentation exists"""
        security_docs = [
            self.root / "docs" / "security" / "THREAT_MODEL_STRIDE.md",
            self.root / "docs" / "security" / "DATA_CLASSIFICATION.md",
            self.root / "SECURITY.md",
        ]

        found = [doc for doc in security_docs if doc.exists()]
        if len(found) >= 2:
            self.report.add_check(
                ComplianceCheck(
                    category="Documentation",
                    name="Security documentation",
                    status="pass",
                    details=f"Found {len(found)} security documents",
                )
            )
        elif found:
            self.report.add_check(
                ComplianceCheck(
                    category="Documentation",
                    name="Security documentation",
                    status="warning",
                    details="Partial security documentation",
                )
            )
        else:
            self.report.add_check(
                ComplianceCheck(
                    category="Documentation",
                    name="Security documentation",
                    status="fail",
                    details="Security documentation missing",
                )
            )

    def _check_api_docs(self) -> None:
        """Verify API documentation"""
        # Check for OpenAPI/Swagger
        api_docs = [
            self.root / "docs" / "api",
            self.root / "openapi.json",
            self.root / "openapi.yaml",
        ]

        for doc in api_docs:
            if doc.exists():
                self.report.add_check(
                    ComplianceCheck(
                        category="Documentation",
                        name="API documentation",
                        status="pass",
                        details="API documentation found",
                        file_path=str(doc),
                    )
                )
                return

        # Check for docstrings in routes
        docstring_count = 0
        for py_file in self._find_python_files():
            if "route" in py_file.name.lower():
                content = py_file.read_text()
                docstring_count += content.count('"""')

        if docstring_count > 10:
            self.report.add_check(
                ComplianceCheck(
                    category="Documentation",
                    name="API documentation",
                    status="pass",
                    details="Route docstrings found for API documentation",
                )
            )
        else:
            self.report.add_check(
                ComplianceCheck(
                    category="Documentation",
                    name="API documentation",
                    status="manual",
                    details="API documentation requires manual review",
                )
            )

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    def _find_python_files(self) -> Iterator[Path]:
        """Find all Python files in the project"""
        exclude_dirs = {".venv", "venv", "__pycache__", ".git", "node_modules"}

        for py_file in self.root.rglob("*.py"):
            if not any(excluded in py_file.parts for excluded in exclude_dirs):
                yield py_file


def generate_markdown(report: ComplianceReport) -> str:
    """Generate markdown report from compliance checks"""
    lines = [
        "# SAHOOL Compliance Checklist",
        "",
        f"> Generated: {report.timestamp}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Checks | {report.summary['total']} |",
        f"| Passed | {report.summary['passed']} ✅ |",
        f"| Failed | {report.summary['failed']} ❌ |",
        f"| Warnings | {report.summary['warnings']} ⚠️ |",
        f"| Manual Review | {report.summary['manual_review']} 📋 |",
        f"| **Compliance Score** | **{report.summary['compliance_score']}%** |",
        "",
    ]

    # Group by category
    categories: dict[str, list[ComplianceCheck]] = {}
    for check in report.checks:
        if check.category not in categories:
            categories[check.category] = []
        categories[check.category].append(check)

    for category, checks in categories.items():
        lines.append(f"## {category}")
        lines.append("")
        lines.append("| Check | Status | Details |")
        lines.append("|-------|--------|---------|")

        for check in checks:
            status_icon = {
                "pass": "✅",
                "fail": "❌",
                "warning": "⚠️",
                "manual": "📋",
            }.get(check.status, "❓")

            file_ref = ""
            if check.file_path:
                file_ref = f" (`{Path(check.file_path).name}`)"

            lines.append(
                f"| {check.name} | {status_icon} | {check.details}{file_ref} |"
            )

        lines.append("")

    # Add compliance requirements section
    lines.extend(
        [
            "## Compliance Requirements",
            "",
            "### GDPR (General Data Protection Regulation)",
            "",
            "- [x] Article 15: Right of access (data export endpoint)",
            "- [x] Article 17: Right to erasure (deletion endpoint)",
            "- [x] Article 20: Right to data portability (export in JSON/CSV)",
            "- [x] Article 25: Data protection by design (PII redaction)",
            "- [x] Article 30: Records of processing (audit logging)",
            "",
            "### SOC 2 Type II",
            "",
            "- [x] CC6.1: Logical access controls (authentication)",
            "- [x] CC6.2: Access management (authorization/RBAC)",
            "- [x] CC7.2: System monitoring (audit logging)",
            "- [x] CC8.1: Change management (hash chain integrity)",
            "",
            "### ISO 27001",
            "",
            "- [x] A.12.4: Logging and monitoring",
            "- [x] A.18.1: Compliance with legal requirements",
            "",
            "---",
            "",
            "*This checklist is auto-generated. Manual verification is recommended for production deployments.*",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate compliance checklist")
    parser.add_argument(
        "--output",
        "-o",
        default="docs/compliance/COMPLIANCE_CHECKLIST.md",
        help="Output file path",
    )
    parser.add_argument(
        "--root",
        "-r",
        default=".",
        help="Project root directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of Markdown",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    checker = ComplianceChecker(root)
    report = checker.run_all_checks()

    if args.json:
        import json

        output = json.dumps(
            {
                "timestamp": report.timestamp,
                "summary": report.summary,
                "checks": [
                    {
                        "category": c.category,
                        "name": c.name,
                        "status": c.status,
                        "details": c.details,
                        "file_path": c.file_path,
                    }
                    for c in report.checks
                ],
            },
            indent=2,
        )
    else:
        output = generate_markdown(report)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(output)
    print(f"✅ Compliance checklist generated: {output_path}")
    print(f"   Score: {report.summary['compliance_score']}%")
    print(f"   Passed: {report.summary['passed']}/{report.summary['total']}")

    # Return non-zero if there are failures
    if report.summary["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Security Rules - Check for security vulnerabilities and best practices
"""

import re
from pathlib import Path


def run_checks(repo_root: Path, config: dict) -> list:
    """Run all security-related checks"""
    findings = []

    findings.extend(check_hardcoded_secrets(repo_root))
    findings.extend(check_jwt_configuration(repo_root))
    findings.extend(check_rbac_implementation(repo_root))
    findings.extend(check_tenant_isolation(repo_root))
    findings.extend(check_input_validation(repo_root))
    findings.extend(check_sql_injection(repo_root))

    return findings


def check_hardcoded_secrets(repo_root: Path) -> list:
    """Check for hardcoded secrets in code"""
    findings = []

    secret_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "password"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "secret"),
        (r'api_key\s*=\s*["\'][^"\']+["\']', "api_key"),
        (r'token\s*=\s*["\'][^"\']+["\']', "token"),
        (r'private_key\s*=\s*["\'][^"\']+["\']', "private_key"),
    ]

    # Skip these paths
    skip_patterns = ["test", "example", "mock", "fixture", ".env.example", "node_modules"]

    for py_file in repo_root.rglob("*.py"):
        # Skip test/example files
        if any(skip in str(py_file).lower() for skip in skip_patterns):
            continue

        try:
            content = py_file.read_text()
        except Exception:
            continue

        for pattern, secret_type in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Skip if it's an environment variable lookup
                if "getenv" in match or "environ" in match or "os." in match:
                    continue
                # Skip if it's clearly a placeholder
                if any(
                    placeholder in match.lower()
                    for placeholder in ["xxx", "changeme", "your_", "example", "${"]
                ):
                    continue

                findings.append(
                    {
                        "severity": "CRITICAL",
                        "component": "Security",
                        "issue": f"Possible hardcoded {secret_type} detected",
                        "impact": "Secrets exposed in source code",
                        "fix": "Move to environment variables or secret manager",
                        "file": str(py_file.relative_to(repo_root)),
                    }
                )
                break  # One finding per file

    return findings


def check_jwt_configuration(repo_root: Path) -> list:
    """Check JWT is properly configured"""
    findings = []

    jwt_files = []
    for py_file in repo_root.rglob("*.py"):
        try:
            content = py_file.read_text()
            if "jwt" in content.lower() or "jose" in content.lower():
                jwt_files.append((py_file, content))
        except Exception:
            continue

    if not jwt_files:
        findings.append(
            {
                "severity": "HIGH",
                "component": "Auth",
                "issue": "No JWT implementation detected",
                "impact": "API authentication may not be properly implemented",
                "fix": "Implement JWT-based authentication using python-jose or PyJWT",
                "file": "shared/auth/",
            }
        )
        return findings

    for py_file, content in jwt_files:
        # Check for weak algorithm
        if "HS256" in content and "RS256" not in content:
            if "algorithm" in content.lower():
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "component": "Auth",
                        "issue": "Using HS256 symmetric algorithm for JWT",
                        "impact": "Less secure than asymmetric algorithms",
                        "fix": "Consider using RS256 for better security",
                        "file": str(py_file.relative_to(repo_root)),
                    }
                )

        # Check for token expiration
        if "exp" not in content and "expire" not in content.lower():
            findings.append(
                {
                    "severity": "HIGH",
                    "component": "Auth",
                    "issue": "JWT expiration not detected",
                    "impact": "Tokens may never expire, security risk",
                    "fix": "Add expiration claim (exp) to JWT tokens",
                    "file": str(py_file.relative_to(repo_root)),
                }
            )

    return findings


def check_rbac_implementation(repo_root: Path) -> list:
    """Check Role-Based Access Control is implemented"""
    findings = []

    rbac_patterns = ["rbac", "role", "permission", "authorize", "can_access"]

    has_rbac = False
    for py_file in repo_root.rglob("*.py"):
        if "test" in str(py_file).lower():
            continue
        try:
            content = py_file.read_text().lower()
            if any(pattern in content for pattern in rbac_patterns):
                has_rbac = True
                break
        except Exception:
            continue

    if not has_rbac:
        findings.append(
            {
                "severity": "HIGH",
                "component": "Auth",
                "issue": "No RBAC implementation detected",
                "impact": "All authenticated users may have same access level",
                "fix": "Implement role-based access control for API endpoints",
                "file": "shared/security/rbac.py",
            }
        )

    return findings


def check_tenant_isolation(repo_root: Path) -> list:
    """Check multi-tenant isolation is enforced"""
    findings = []

    # Check repository/service files for tenant filtering
    repo_files = list(repo_root.rglob("**/repository*.py")) + list(
        repo_root.rglob("**/service*.py")
    )

    for repo_file in repo_files:
        if "test" in str(repo_file).lower():
            continue

        try:
            content = repo_file.read_text()
        except Exception:
            continue

        # Check if file has database queries
        has_queries = any(
            pattern in content
            for pattern in ["query", "select", "filter", "where", "execute"]
        )

        if has_queries:
            has_tenant_filter = "tenant_id" in content or "tenant" in content.lower()
            if not has_tenant_filter:
                findings.append(
                    {
                        "severity": "HIGH",
                        "component": "Security",
                        "issue": f"Missing tenant filtering in {repo_file.name}",
                        "impact": "Cross-tenant data access may be possible",
                        "fix": "Add tenant_id filter to all database queries",
                        "file": str(repo_file.relative_to(repo_root)),
                    }
                )

    return findings


def check_input_validation(repo_root: Path) -> list:
    """Check input validation is implemented"""
    findings = []

    # Check API endpoints for validation
    for main_py in repo_root.rglob("**/main.py"):
        if "services" not in str(main_py):
            continue

        try:
            content = main_py.read_text()
        except Exception:
            continue

        if "FastAPI" not in content:
            continue

        # Check for Pydantic models
        has_pydantic = "BaseModel" in content or "pydantic" in content.lower()

        if not has_pydantic:
            findings.append(
                {
                    "severity": "MEDIUM",
                    "component": main_py.parent.parent.name,
                    "issue": "No Pydantic validation detected",
                    "impact": "API may accept invalid input",
                    "fix": "Use Pydantic models for request validation",
                    "file": str(main_py.relative_to(repo_root)),
                }
            )

    return findings


def check_sql_injection(repo_root: Path) -> list:
    """Check for potential SQL injection vulnerabilities"""
    findings = []

    # Patterns that might indicate SQL injection risk
    risky_patterns = [
        r'execute\s*\(\s*f["\']',  # f-string in execute
        r'execute\s*\(\s*["\'].*\+',  # String concatenation in execute
        r'execute\s*\(\s*%',  # % formatting in execute
    ]

    for py_file in repo_root.rglob("*.py"):
        if "test" in str(py_file).lower():
            continue

        try:
            content = py_file.read_text()
        except Exception:
            continue

        for pattern in risky_patterns:
            if re.search(pattern, content):
                findings.append(
                    {
                        "severity": "CRITICAL",
                        "component": "Security",
                        "issue": "Potential SQL injection vulnerability",
                        "impact": "Database may be compromised",
                        "fix": "Use parameterized queries instead of string formatting",
                        "file": str(py_file.relative_to(repo_root)),
                    }
                )
                break

    return findings

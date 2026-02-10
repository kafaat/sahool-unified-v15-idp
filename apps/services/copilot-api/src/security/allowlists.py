"""
Security Allowlists Configuration
إعدادات قوائم السماح الأمنية

Defines allowed tools, domains, and security constraints.
"""

from __future__ import annotations

import os
from typing import Final

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL ALLOWLIST - قائمة الأدوات المسموحة
# ═══════════════════════════════════════════════════════════════════════════════

# Default tools that are always safe
DEFAULT_TOOL_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        # RAG Operations
        "rag.search",
        "rag.add",
        "rag.list",
        "rag.delete",
        # Code Analysis (read-only)
        "code.analyze",
        "code.lint",
        "code.metrics",
        "code.review",
        # Code Fixing (with safeguards)
        "code.fix",
        "code.format",
        "code.suggest",
        # Deployment (planning only)
        "deploy.plan",
        "deploy.status",
        "deploy.validate",
        # Field Operations (SAHOOL domain)
        "field.list",
        "field.get",
        "field.analyze",
        "field.ndvi",
        # Weather Operations
        "weather.forecast",
        "weather.current",
        "weather.historical",
        # Advisory Operations
        "advisory.irrigation",
        "advisory.fertilizer",
        "advisory.crop",
        # Inventory Operations (read-only)
        "inventory.list",
        "inventory.check",
        # Audit Operations (read-only)
        "audit.list",
        "audit.search",
    }
)

# Load additional tools from environment
_env_tools = os.getenv("COPILOT_TOOL_ALLOWLIST", "")
TOOL_ALLOWLIST: frozenset[str] = DEFAULT_TOOL_ALLOWLIST | frozenset(
    t.strip() for t in _env_tools.split(",") if t.strip()
)

# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN ALLOWLIST - قائمة النطاقات المسموحة
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_DOMAIN_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        # Internal services
        "localhost",
        "127.0.0.1",
        "api.sahool.app",
        "api.sahool.local",
        # SAHOOL microservices (internal docker network)
        "field_core",
        "weather_core",
        "agro_advisor",
        "ai_advisor",
        "notification_service",
        "qdrant",
        "redis",
        "postgres",
        "nats",
        # Ollama for local LLM
        "ollama",
        "ollama.local",
        # GitHub (for code operations)
        "github.com",
        "api.github.com",
        "raw.githubusercontent.com",
    }
)

# Load additional domains from environment
_env_domains = os.getenv("COPILOT_DOMAIN_ALLOWLIST", "")
DOMAIN_ALLOWLIST: frozenset[str] = DEFAULT_DOMAIN_ALLOWLIST | frozenset(
    d.strip().lower() for d in _env_domains.split(",") if d.strip()
)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKED PATTERNS - الأنماط المحظورة
# ═══════════════════════════════════════════════════════════════════════════════

BLOCKED_PATTERNS: Final[frozenset[str]] = frozenset(
    {
        # File patterns that should never be accessed
        "*.key",
        "*.pem",
        "*.crt",
        "*.p12",
        "*.pfx",
        ".env",
        ".env.*",
        "*.env",
        "credentials.json",
        "secrets.yaml",
        "secrets.yml",
        ".git/config",
        ".ssh/*",
        "id_rsa*",
        "*.secret",
        # Database patterns
        "*.sql",
        "*.dump",
        "*.bak",
        # Sensitive directories
        "/etc/passwd",
        "/etc/shadow",
        "/root/*",
    }
)

# ═══════════════════════════════════════════════════════════════════════════════
# SIZE LIMITS - حدود الأحجام
# ═══════════════════════════════════════════════════════════════════════════════

# Maximum size for tool arguments (bytes)
MAX_ARGS_SIZE: Final[int] = int(os.getenv("COPILOT_MAX_ARGS_SIZE", "20000"))

# Maximum characters in prompt
MAX_PROMPT_CHARS: Final[int] = int(os.getenv("COPILOT_MAX_PROMPT_CHARS", "12000"))

# Maximum files that can be changed in one operation
MAX_FILES_CHANGED: Final[int] = int(os.getenv("COPILOT_MAX_FILES_CHANGED", "20"))

# Request timeout in seconds
REQUEST_TIMEOUT_S: Final[float] = float(os.getenv("COPILOT_REQUEST_TIMEOUT_S", "30.0"))

# ═══════════════════════════════════════════════════════════════════════════════
# EXTERNAL ACCESS CONTROL - التحكم في الوصول الخارجي
# ═══════════════════════════════════════════════════════════════════════════════

# Enable external network access (default: offline)
ENABLE_EXTERNAL: Final[bool] = os.getenv("COPILOT_ENABLE_EXTERNAL", "false").lower() == "true"

# External LLM configuration
EXTERNAL_LLM_BASE_URL: Final[str | None] = os.getenv("EXTERNAL_LLM_BASE_URL")
EXTERNAL_LLM_API_KEY: Final[str | None] = os.getenv("EXTERNAL_LLM_API_KEY")
EXTERNAL_LLM_MODEL: Final[str] = os.getenv("EXTERNAL_LLM_MODEL", "gpt-4o-mini")
EXTERNAL_LLM_TEMPERATURE: Final[float] = float(os.getenv("EXTERNAL_LLM_TEMPERATURE", "0.2"))

# ═══════════════════════════════════════════════════════════════════════════════
# DANGEROUS COMMANDS - الأوامر الخطرة
# ═══════════════════════════════════════════════════════════════════════════════

DANGEROUS_COMMANDS: Final[frozenset[str]] = frozenset(
    {
        # Destructive file operations
        "rm -rf",
        "rm -r",
        "rmdir",
        "del /f",
        "format",
        # Database destructive operations
        "DROP TABLE",
        "DROP DATABASE",
        "DELETE FROM",
        "TRUNCATE",
        # Git destructive operations
        "git push --force",
        "git reset --hard",
        "git clean -fd",
        "git checkout .",
        # System operations
        "shutdown",
        "reboot",
        "kill -9",
        "pkill",
        # Docker destructive operations
        "docker rm -f",
        "docker system prune",
        "docker volume rm",
    }
)

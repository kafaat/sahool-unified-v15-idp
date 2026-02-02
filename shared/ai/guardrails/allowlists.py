"""
Shared Security Allowlists
قوائم السماح الأمنية المشتركة

Centralized allowlists for all SAHOOL AI services.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import os
from typing import Final

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL ALLOWLIST - قائمة الأدوات المسموحة
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_TOOL_ALLOWLIST: Final[frozenset[str]] = frozenset({
    # RAG Operations
    "rag.search",
    "rag.add",
    "rag.list",
    "rag.delete",
    "rag.index",

    # Code Analysis (read-only)
    "code.analyze",
    "code.lint",
    "code.metrics",
    "code.review",
    "code.search",
    "code.explain",

    # Code Fixing (with safeguards)
    "code.fix",
    "code.format",
    "code.suggest",
    "code.refactor",
    "code.generate_tests",

    # Deployment (planning only)
    "deploy.plan",
    "deploy.status",
    "deploy.validate",
    "deploy.rollback_plan",

    # Field Operations (SAHOOL domain)
    "field.list",
    "field.get",
    "field.analyze",
    "field.ndvi",
    "field.history",
    "field.recommendations",

    # Weather Operations
    "weather.forecast",
    "weather.current",
    "weather.historical",
    "weather.alerts",

    # Advisory Operations
    "advisory.irrigation",
    "advisory.fertilizer",
    "advisory.crop",
    "advisory.pest",
    "advisory.harvest",

    # Inventory Operations (read-only by default)
    "inventory.list",
    "inventory.check",
    "inventory.forecast",

    # Audit Operations (read-only)
    "audit.list",
    "audit.search",
    "audit.export",

    # Agent Operations
    "agent.status",
    "agent.list",
    "agent.invoke",

    # Utility Operations
    "util.translate",
    "util.summarize",
    "util.format",
})

# Load additional tools from environment
_env_tools = os.getenv("SAHOOL_TOOL_ALLOWLIST", "")
TOOL_ALLOWLIST: frozenset[str] = DEFAULT_TOOL_ALLOWLIST | frozenset(
    t.strip() for t in _env_tools.split(",") if t.strip()
)

# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN ALLOWLIST - قائمة النطاقات المسموحة
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_DOMAIN_ALLOWLIST: Final[frozenset[str]] = frozenset({
    # Internal services
    "localhost",
    "127.0.0.1",
    "::1",
    "api.sahool.app",
    "api.sahool.local",
    "sahool.app",

    # SAHOOL microservices (Docker network)
    "postgres",
    "redis",
    "nats",
    "qdrant",
    "mqtt",
    "field_core",
    "weather_core",
    "agro_advisor",
    "ai_advisor",
    "copilot_api",
    "code_fix_agent",
    "notification_service",
    "satellite_service",
    "ndvi_engine",

    # Local LLM services
    "ollama",
    "ollama.local",
    "localhost:11434",

    # Trusted external (optional)
    "github.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "huggingface.co",
    "cdn-lfs.huggingface.co",
})

_env_domains = os.getenv("SAHOOL_DOMAIN_ALLOWLIST", "")
DOMAIN_ALLOWLIST: frozenset[str] = DEFAULT_DOMAIN_ALLOWLIST | frozenset(
    d.strip().lower() for d in _env_domains.split(",") if d.strip()
)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKED PATTERNS - الأنماط المحظورة
# ═══════════════════════════════════════════════════════════════════════════════

BLOCKED_PATTERNS: Final[frozenset[str]] = frozenset({
    # Secrets and credentials
    "*.key",
    "*.pem",
    "*.crt",
    "*.p12",
    "*.pfx",
    ".env",
    ".env.*",
    "*.env",
    "credentials.json",
    "credentials.yaml",
    "secrets.yaml",
    "secrets.yml",
    "*.secret",
    "*password*",
    "*api_key*",
    "*apikey*",
    "*secret_key*",

    # Git sensitive
    ".git/config",
    ".gitconfig",

    # SSH
    ".ssh/*",
    "id_rsa*",
    "id_ed25519*",
    "authorized_keys",
    "known_hosts",

    # Database
    "*.sql",
    "*.dump",
    "*.bak",
    "*.backup",

    # System
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers",
    "/root/*",
    "~/*",

    # Docker secrets
    "/run/secrets/*",

    # Kubernetes
    "kubeconfig",
    "*.kubeconfig",
})

# ═══════════════════════════════════════════════════════════════════════════════
# DANGEROUS COMMANDS - الأوامر الخطرة
# ═══════════════════════════════════════════════════════════════════════════════

DANGEROUS_COMMANDS: Final[frozenset[str]] = frozenset({
    # File destruction
    "rm -rf",
    "rm -r /",
    "rm -rf /",
    "rmdir",
    "del /f /s",
    "format",
    "mkfs",
    "> /dev/sda",

    # Database destruction
    "DROP TABLE",
    "DROP DATABASE",
    "DELETE FROM",
    "TRUNCATE TABLE",
    "DROP SCHEMA",

    # Git destructive
    "git push --force",
    "git push -f",
    "git reset --hard",
    "git clean -fd",
    "git checkout .",
    "git rebase -i",

    # System
    "shutdown",
    "reboot",
    "halt",
    "init 0",
    "kill -9",
    "pkill -9",
    "killall",

    # Docker destructive
    "docker rm -f",
    "docker system prune -a",
    "docker volume rm",
    "docker rmi -f",

    # Kubernetes destructive
    "kubectl delete --all",
    "kubectl delete namespace",

    # Network
    "iptables -F",
    "ip route flush",

    # Permission escalation
    "chmod 777",
    "chown root",
    "sudo rm",
    "sudo dd",
})

# ═══════════════════════════════════════════════════════════════════════════════
# SIZE LIMITS - حدود الأحجام
# ═══════════════════════════════════════════════════════════════════════════════

MAX_ARGS_SIZE: Final[int] = int(os.getenv("SAHOOL_MAX_ARGS_SIZE", "20000"))
MAX_PROMPT_CHARS: Final[int] = int(os.getenv("SAHOOL_MAX_PROMPT_CHARS", "12000"))
MAX_FILES_CHANGED: Final[int] = int(os.getenv("SAHOOL_MAX_FILES_CHANGED", "20"))
MAX_OUTPUT_SIZE: Final[int] = int(os.getenv("SAHOOL_MAX_OUTPUT_SIZE", "100000"))
REQUEST_TIMEOUT_S: Final[float] = float(os.getenv("SAHOOL_REQUEST_TIMEOUT_S", "30.0"))

# ═══════════════════════════════════════════════════════════════════════════════
# EXTERNAL ACCESS CONTROL
# ═══════════════════════════════════════════════════════════════════════════════

ENABLE_EXTERNAL: Final[bool] = os.getenv("SAHOOL_ENABLE_EXTERNAL", "false").lower() == "true"

"""
Auto-Fix Configuration
======================
تكوين محرك الإصلاح التلقائي

Centralized configuration for the SAHOOL Auto-Fix engine,
quality orchestration, and diagnostic tooling.

Author: SAHOOL Platform Team
Created: March 2026
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .models import FixStrategy, QualityLayer, ToolType


@dataclass
class DiagnosticToolConfig:
    """Configuration for a single diagnostic tool.
    تكوين أداة تشخيص واحدة"""

    enabled: bool = True
    timeout_seconds: int = 30
    max_retries: int = 2
    extra_args: list[str] = field(default_factory=list)


@dataclass
class AutoFixConfig:
    """Central configuration for the Auto-Fix engine.
    التكوين المركزي لمحرك الإصلاح التلقائي

    Environment variables override defaults when present.

    Example:
        config = AutoFixConfig.from_env()
        engine = AutoFixEngine(config=config)
    """

    # ── Fix Strategy Settings ─────────────────────────
    default_strategy: FixStrategy = FixStrategy.SAFE
    dry_run: bool = True
    max_files_per_run: int = 50
    max_fixes_per_file: int = 20
    backup_enabled: bool = True
    backup_dir: str = ".sahool_backups"

    # ── Diagnostic Settings ───────────────────────────
    diagnostic_timeout: int = 60
    parallel_diagnostics: bool = True
    max_concurrent_tools: int = 4

    # ── Quality Layer Settings ────────────────────────
    enabled_layers: list[QualityLayer] = field(
        default_factory=lambda: list(QualityLayer),
    )
    fail_on_security: bool = True
    fail_on_type_errors: bool = False
    complexity_threshold: int = 20

    # ── Tool-specific Configuration ───────────────────
    tool_configs: dict[ToolType, DiagnosticToolConfig] = field(default_factory=dict)

    # ── Ruff Settings ─────────────────────────────────
    ruff_line_length: int = 120
    ruff_target_version: str = "py311"
    ruff_select_rules: list[str] = field(
        default_factory=lambda: ["E", "F", "I", "UP", "B", "SIM", "N", "W", "C4", "C90"],
    )

    # ── Audit Settings ────────────────────────────────
    audit_enabled: bool = True
    audit_dir: str = ".sahool_audit"

    # ── Paths ─────────────────────────────────────────
    working_dir: str = "."
    python_paths: list[str] = field(default_factory=lambda: ["apps/", "shared/"])
    typescript_paths: list[str] = field(default_factory=lambda: ["apps/web/", "apps/admin/", "packages/"])
    dart_paths: list[str] = field(default_factory=lambda: ["apps/mobile/"])
    exclude_paths: list[str] = field(
        default_factory=lambda: [
            "archive/",
            "idp/templates/",
            ".git",
            ".venv",
            "__pycache__",
            "node_modules",
        ],
    )

    @classmethod
    def from_env(cls) -> AutoFixConfig:
        """Create configuration from environment variables.
        إنشاء التكوين من متغيرات البيئة

        Reads AUTO_FIX_* prefixed environment variables.
        """
        config = cls()

        # Override from environment
        if strategy := os.getenv("AUTO_FIX_STRATEGY"):
            try:
                config.default_strategy = FixStrategy(strategy)
            except ValueError:
                pass  # Keep default if invalid

        if os.getenv("AUTO_FIX_DRY_RUN", "").lower() in ("0", "false", "no"):
            config.dry_run = False

        if max_files := os.getenv("AUTO_FIX_MAX_FILES"):
            try:
                config.max_files_per_run = int(max_files)
            except ValueError:
                pass  # Keep default if env var is not a valid integer

        if timeout := os.getenv("AUTO_FIX_TIMEOUT"):
            try:
                config.diagnostic_timeout = int(timeout)
            except ValueError:
                pass  # Keep default if env var is not a valid integer

        if os.getenv("AUTO_FIX_AUDIT_ENABLED", "").lower() in ("0", "false", "no"):
            config.audit_enabled = False

        if line_length := os.getenv("RUFF_LINE_LENGTH"):
            try:
                config.ruff_line_length = int(line_length)
            except ValueError:
                pass  # Keep default if env var is not a valid integer

        if complexity := os.getenv("AUTO_FIX_COMPLEXITY_THRESHOLD"):
            try:
                config.complexity_threshold = int(complexity)
            except ValueError:
                pass  # Keep default if env var is not a valid integer

        if working_dir := os.getenv("AUTO_FIX_WORKING_DIR"):
            config.working_dir = working_dir

        return config

    def get_tool_config(self, tool: ToolType) -> DiagnosticToolConfig:
        """Get configuration for a specific tool, with defaults.
        الحصول على تكوين أداة محددة مع القيم الافتراضية"""
        return self.tool_configs.get(tool, DiagnosticToolConfig())

    def is_layer_enabled(self, layer: QualityLayer) -> bool:
        """Check if a quality layer is enabled.
        التحقق مما إذا كانت طبقة الجودة مفعلة"""
        return layer in self.enabled_layers


# ── Default Configurations ────────────────────────────

DEFAULT_CONFIG = AutoFixConfig()

SAFE_CONFIG = AutoFixConfig(
    default_strategy=FixStrategy.SAFE,
    dry_run=False,
    fail_on_security=True,
    fail_on_type_errors=False,
)

STRICT_CONFIG = AutoFixConfig(
    default_strategy=FixStrategy.COMPREHENSIVE,
    dry_run=False,
    fail_on_security=True,
    fail_on_type_errors=True,
    complexity_threshold=15,
)

CI_CONFIG = AutoFixConfig(
    default_strategy=FixStrategy.SAFE,
    dry_run=True,
    audit_enabled=True,
    parallel_diagnostics=True,
    max_concurrent_tools=6,
)

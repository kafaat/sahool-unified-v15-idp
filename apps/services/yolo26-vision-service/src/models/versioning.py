"""
Model Versioning System for YOLO26 Vision Service.

Provides version tracking, rollback capabilities, and model metadata management
for agricultural AI models in the SAHOOL platform.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ModelStatus(StrEnum):
    """Model deployment status."""

    ACTIVE = "active"  # Currently in use
    DEPRECATED = "deprecated"  # Marked for removal
    TESTING = "testing"  # In testing phase
    ROLLBACK = "rollback"  # Available for rollback


class ModelStage(StrEnum):
    """Model lifecycle stage."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelMetrics:
    """Model performance metrics."""

    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    map50: float = 0.0  # mAP@0.5
    map50_95: float = 0.0  # mAP@0.5:0.95
    inference_time_ms: float = 0.0
    memory_mb: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "map50": self.map50,
            "map50_95": self.map50_95,
            "inference_time_ms": self.inference_time_ms,
            "memory_mb": self.memory_mb,
        }


@dataclass
class ModelVersion:
    """Model version information."""

    version: str
    task: str
    variant: str
    created_at: datetime
    status: ModelStatus = ModelStatus.ACTIVE
    stage: ModelStage = ModelStage.DEVELOPMENT
    file_path: str = ""
    file_hash: str = ""
    file_size_mb: float = 0.0
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    training_config: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    description_ar: str = ""
    changelog: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @property
    def model_key(self) -> str:
        """Generate unique model key."""
        return f"{self.task}_{self.variant}_{self.version}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "task": self.task,
            "variant": self.variant,
            "model_key": self.model_key,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "stage": self.stage.value,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "file_size_mb": self.file_size_mb,
            "metrics": self.metrics.to_dict(),
            "training_config": self.training_config,
            "description": self.description,
            "description_ar": self.description_ar,
            "changelog": self.changelog,
            "tags": self.tags,
        }


class ModelVersionRegistry:
    """
    Model version registry for tracking and managing model versions.

    Supports:
    - Version tracking with semantic versioning
    - Rollback capabilities
    - A/B testing support
    - Performance metrics tracking
    """

    def __init__(
        self,
        registry_path: str | Path = "/models/registry",
        max_versions_per_model: int = 10,
    ):
        self.registry_path = Path(registry_path)
        self.max_versions_per_model = max_versions_per_model
        self._versions: dict[str, list[ModelVersion]] = {}
        self._active_versions: dict[str, ModelVersion] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Load registry from disk if exists."""
        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file) as f:
                    data = json.load(f)
                    self._parse_registry_data(data)
                logger.info("model_registry_loaded", count=len(self._versions))
            except Exception as e:
                logger.warning("registry_load_failed", error=str(e))
        else:
            logger.info("model_registry_initialized_empty")

    def _parse_registry_data(self, data: dict[str, Any]) -> None:
        """Parse registry data from JSON."""
        for task_variant, versions in data.get("versions", {}).items():
            self._versions[task_variant] = []
            for v_data in versions:
                version = ModelVersion(
                    version=v_data["version"],
                    task=v_data["task"],
                    variant=v_data["variant"],
                    created_at=datetime.fromisoformat(v_data["created_at"]),
                    status=ModelStatus(v_data.get("status", "active")),
                    stage=ModelStage(v_data.get("stage", "production")),
                    file_path=v_data.get("file_path", ""),
                    file_hash=v_data.get("file_hash", ""),
                    file_size_mb=v_data.get("file_size_mb", 0.0),
                    metrics=ModelMetrics(**v_data.get("metrics", {})),
                    training_config=v_data.get("training_config", {}),
                    description=v_data.get("description", ""),
                    description_ar=v_data.get("description_ar", ""),
                    changelog=v_data.get("changelog", []),
                    tags=v_data.get("tags", []),
                )
                self._versions[task_variant].append(version)
                if version.status == ModelStatus.ACTIVE:
                    self._active_versions[task_variant] = version

    def _save_registry(self) -> None:
        """Save registry to disk."""
        self.registry_path.mkdir(parents=True, exist_ok=True)
        registry_file = self.registry_path / "registry.json"

        data = {
            "versions": {},
            "updated_at": datetime.now(UTC).isoformat(),
        }

        for task_variant, versions in self._versions.items():
            data["versions"][task_variant] = [v.to_dict() for v in versions]

        try:
            with open(registry_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug("registry_saved")
        except Exception as e:
            logger.error("registry_save_failed", error=str(e))

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of model file."""
        if not file_path.exists():
            return ""

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]

    def register_version(
        self,
        task: str,
        variant: str,
        version: str,
        file_path: str | Path,
        metrics: ModelMetrics | None = None,
        training_config: dict[str, Any] | None = None,
        description: str = "",
        description_ar: str = "",
        changelog: list[str] | None = None,
        tags: list[str] | None = None,
        stage: ModelStage = ModelStage.DEVELOPMENT,
        activate: bool = False,
    ) -> ModelVersion:
        """
        Register a new model version.

        Args:
            task: Model task (e.g., pest_detection, disease_detection)
            variant: Model variant (n, s, m, l, x)
            version: Semantic version string (e.g., 1.0.0)
            file_path: Path to model file
            metrics: Model performance metrics
            training_config: Training configuration
            description: Version description
            description_ar: Arabic description
            changelog: List of changes
            tags: Version tags
            stage: Deployment stage
            activate: Set as active version

        Returns:
            Registered ModelVersion
        """
        task_variant = f"{task}_{variant}"
        path = Path(file_path)

        # Compute file info
        file_hash = self._compute_file_hash(path)
        file_size_mb = path.stat().st_size / (1024 * 1024) if path.exists() else 0.0

        model_version = ModelVersion(
            version=version,
            task=task,
            variant=variant,
            created_at=datetime.now(UTC),
            status=ModelStatus.ACTIVE if activate else ModelStatus.TESTING,
            stage=stage,
            file_path=str(path),
            file_hash=file_hash,
            file_size_mb=round(file_size_mb, 2),
            metrics=metrics or ModelMetrics(),
            training_config=training_config or {},
            description=description,
            description_ar=description_ar,
            changelog=changelog or [],
            tags=tags or [],
        )

        # Initialize version list if needed
        if task_variant not in self._versions:
            self._versions[task_variant] = []

        # Add to versions
        self._versions[task_variant].insert(0, model_version)

        # Trim old versions
        if len(self._versions[task_variant]) > self.max_versions_per_model:
            old_versions = self._versions[task_variant][self.max_versions_per_model :]
            self._versions[task_variant] = self._versions[task_variant][: self.max_versions_per_model]
            for old in old_versions:
                logger.info("model_version_archived", model_key=old.model_key)

        # Activate if requested
        if activate:
            self.activate_version(task, variant, version)

        self._save_registry()

        logger.info(
            "model_version_registered",
            model_key=model_version.model_key,
            stage=stage.value,
            activated=activate,
        )

        return model_version

    def activate_version(self, task: str, variant: str, version: str) -> bool:
        """
        Activate a specific model version.

        Args:
            task: Model task
            variant: Model variant
            version: Version to activate

        Returns:
            True if activated successfully
        """
        task_variant = f"{task}_{variant}"

        if task_variant not in self._versions:
            logger.warning("task_variant_not_found", task_variant=task_variant)
            return False

        # Find and activate the version
        for v in self._versions[task_variant]:
            if v.version == version:
                # Deactivate current active
                if task_variant in self._active_versions:
                    self._active_versions[task_variant].status = ModelStatus.ROLLBACK

                # Activate new version
                v.status = ModelStatus.ACTIVE
                self._active_versions[task_variant] = v
                self._save_registry()

                logger.info(
                    "model_version_activated",
                    task_variant=task_variant,
                    version=version,
                )
                return True

        logger.warning("version_not_found", task_variant=task_variant, version=version)
        return False

    def rollback(self, task: str, variant: str, to_version: str | None = None) -> ModelVersion | None:
        """
        Rollback to a previous model version.

        Args:
            task: Model task
            variant: Model variant
            to_version: Specific version to rollback to (or None for previous)

        Returns:
            Rolled back ModelVersion or None
        """
        task_variant = f"{task}_{variant}"

        if task_variant not in self._versions:
            return None

        versions = self._versions[task_variant]

        if to_version:
            # Rollback to specific version
            for v in versions:
                if v.version == to_version and v.status == ModelStatus.ROLLBACK:
                    self.activate_version(task, variant, to_version)
                    logger.info(
                        "model_rollback",
                        task_variant=task_variant,
                        to_version=to_version,
                    )
                    return v
        else:
            # Rollback to previous version
            for v in versions:
                if v.status == ModelStatus.ROLLBACK:
                    self.activate_version(task, variant, v.version)
                    logger.info(
                        "model_rollback",
                        task_variant=task_variant,
                        to_version=v.version,
                    )
                    return v

        return None

    def get_active_version(self, task: str, variant: str) -> ModelVersion | None:
        """Get the currently active version for a task/variant."""
        task_variant = f"{task}_{variant}"
        return self._active_versions.get(task_variant)

    def get_version(self, task: str, variant: str, version: str) -> ModelVersion | None:
        """Get a specific version."""
        task_variant = f"{task}_{variant}"
        if task_variant not in self._versions:
            return None

        for v in self._versions[task_variant]:
            if v.version == version:
                return v
        return None

    def get_version_history(self, task: str, variant: str) -> list[ModelVersion]:
        """Get version history for a task/variant."""
        task_variant = f"{task}_{variant}"
        return self._versions.get(task_variant, [])

    def compare_versions(
        self,
        task: str,
        variant: str,
        version_a: str,
        version_b: str,
    ) -> dict[str, Any]:
        """Compare two model versions."""
        v_a = self.get_version(task, variant, version_a)
        v_b = self.get_version(task, variant, version_b)

        if not v_a or not v_b:
            return {"error": "Version not found"}

        return {
            "version_a": v_a.to_dict(),
            "version_b": v_b.to_dict(),
            "metrics_comparison": {
                "accuracy_diff": v_b.metrics.accuracy - v_a.metrics.accuracy,
                "precision_diff": v_b.metrics.precision - v_a.metrics.precision,
                "recall_diff": v_b.metrics.recall - v_a.metrics.recall,
                "f1_diff": v_b.metrics.f1_score - v_a.metrics.f1_score,
                "map50_diff": v_b.metrics.map50 - v_a.metrics.map50,
                "inference_time_diff": v_b.metrics.inference_time_ms - v_a.metrics.inference_time_ms,
            },
            "improved": v_b.metrics.map50 > v_a.metrics.map50,
        }

    def deprecate_version(self, task: str, variant: str, version: str) -> bool:
        """Mark a version as deprecated."""
        v = self.get_version(task, variant, version)
        if v:
            v.status = ModelStatus.DEPRECATED
            self._save_registry()
            logger.info("model_version_deprecated", model_key=v.model_key)
            return True
        return False

    def get_all_versions(self) -> dict[str, list[dict[str, Any]]]:
        """Get all registered versions."""
        result = {}
        for task_variant, versions in self._versions.items():
            result[task_variant] = [v.to_dict() for v in versions]
        return result

    def update_metrics(
        self,
        task: str,
        variant: str,
        version: str,
        metrics: ModelMetrics,
    ) -> bool:
        """Update metrics for a specific version."""
        v = self.get_version(task, variant, version)
        if v:
            v.metrics = metrics
            self._save_registry()
            logger.info(
                "model_metrics_updated",
                model_key=v.model_key,
                map50=metrics.map50,
            )
            return True
        return False

    def promote_to_production(self, task: str, variant: str, version: str) -> bool:
        """Promote a version to production stage."""
        v = self.get_version(task, variant, version)
        if v:
            v.stage = ModelStage.PRODUCTION
            self._save_registry()
            logger.info("model_promoted_to_production", model_key=v.model_key)
            return True
        return False


# Singleton instance
_registry_instance: ModelVersionRegistry | None = None


def get_version_registry(registry_path: str = "/models/registry") -> ModelVersionRegistry:
    """Get the singleton version registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ModelVersionRegistry(registry_path=registry_path)
    return _registry_instance

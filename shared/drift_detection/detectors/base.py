"""
Base Drift Detector
قاعدة كاشف الانحراف

Abstract base class for all drift detectors.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from shared.drift_detection.models import DriftCategory, DriftResult

logger = logging.getLogger(__name__)


class BaseDriftDetector(ABC):
    """
    Abstract base class for drift detectors.
    الفئة الأساسية المجردة لكواشف الانحراف.

    Each detector must implement:
    - category: The drift category it handles
    - detect(): Run detection and return results
    """

    def __init__(self, working_dir: str = ".", config: dict[str, Any] | None = None):
        self.working_dir = working_dir
        self.config = config or {}
        self._results: list[DriftResult] = []

    @property
    @abstractmethod
    def category(self) -> DriftCategory:
        """The drift category this detector handles."""
        ...

    @abstractmethod
    async def detect(self) -> list[DriftResult]:
        """
        Run drift detection and return results.
        تشغيل كشف الانحراف وإرجاع النتائج.
        """
        ...

    def add_result(self, result: DriftResult) -> None:
        """Add a drift result to the collection."""
        self._results.append(result)

    def clear_results(self) -> None:
        """Clear previous results before a new run."""
        self._results.clear()

    @property
    def results(self) -> list[DriftResult]:
        return list(self._results)

    @property
    def has_drift(self) -> bool:
        return len(self._results) > 0

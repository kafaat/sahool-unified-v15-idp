# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
ML Service Integration
تكامل خدمة التعلم الآلي

Wraps the shared AgML module for use in the orchestrator.
"""

import os
import sys
from typing import Any

import structlog

# Add shared module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

logger = structlog.get_logger()


class MLService:
    """
    Machine Learning service for agricultural AI.
    خدمة التعلم الآلي للذكاء الاصطناعي الزراعي
    """

    def __init__(self):
        self._manager = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the ML manager."""
        if self._initialized:
            return True

        try:
            from shared.ml import AgMLDatasetManager

            self._manager = AgMLDatasetManager()
            await self._manager.initialize()
            self._initialized = True
            logger.info("ML service initialized")
            return True

        except ImportError as e:
            logger.warning("shared.ml not available", error=str(e))
            # Initialize without AgML (use built-in catalog)
            try:
                from shared.ml import AgMLDatasetManager

                self._manager = AgMLDatasetManager()
                self._initialized = True
                return True
            except Exception:
                return False
        except Exception as e:
            logger.error("Failed to initialize ML service", error=str(e))
            return False

    def list_datasets(
        self,
        dataset_type: str | None = None,
        crop_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        List available agricultural ML datasets.
        عرض مجموعات بيانات التعلم الآلي الزراعية المتاحة
        """
        if not self._manager:
            return []

        try:
            from shared.ml import CropType, DatasetType

            dt = DatasetType(dataset_type) if dataset_type else None
            ct = CropType(crop_type) if crop_type else None

            datasets = self._manager.list_datasets(dt, ct)

            return [
                {
                    "name": d.name,
                    "name_ar": d.name_ar,
                    "type": d.dataset_type.value,
                    "crop": d.crop_type.value,
                    "num_classes": d.num_classes,
                    "num_images": d.num_images,
                    "source": d.source,
                    "license": d.license,
                    "description": d.description,
                    "description_ar": d.description_ar,
                }
                for d in datasets
            ]

        except Exception as e:
            logger.error("Failed to list datasets", error=str(e))
            return []

    def get_disease_classes(self, crop: str) -> list[dict[str, str]]:
        """
        Get disease classes for a crop.
        الحصول على فئات الأمراض لمحصول
        """
        if not self._manager:
            return []

        try:
            from shared.ml import CropType

            ct = CropType(crop)
            return self._manager.get_disease_classes(ct)

        except Exception as e:
            logger.error("Failed to get disease classes", error=str(e))
            return []

    def get_yield_features(self) -> list[dict[str, str]]:
        """
        Get features used for yield prediction.
        الحصول على الميزات المستخدمة للتنبؤ بالإنتاجية
        """
        if not self._manager:
            return []

        return self._manager.get_yield_features()

    def get_recommended_datasets(self, region: str = "middle_east") -> list[str]:
        """
        Get recommended datasets for a region.
        الحصول على مجموعات البيانات الموصى بها لمنطقة
        """
        if not self._manager:
            return [
                "wheat_rust",
                "date_palm_disease",
                "tomato_disease",
            ]

        return self._manager.get_recommended_datasets(region)

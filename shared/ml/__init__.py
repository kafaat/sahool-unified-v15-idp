# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Agricultural Machine Learning Module
وحدة التعلم الآلي الزراعي

Provides ML capabilities using AgML and other agricultural ML frameworks.
"""

from .agml_integration import (
    AgMLDatasetManager,
    CropDataset,
    DiseaseDataset,
    YieldDataset,
    DatasetType,
)

__all__ = [
    "AgMLDatasetManager",
    "CropDataset",
    "DiseaseDataset",
    "YieldDataset",
    "DatasetType",
]

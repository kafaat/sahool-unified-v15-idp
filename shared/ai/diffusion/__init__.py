"""
Diffusion Language Models Module
================================
وحدة نماذج اللغة الانتشارية

Provides diffusion-based language generation for SAHOOL,
including advisory generation with parallel decoding and
template infilling capabilities.

Based on:
- LLaDA (Large Language Diffusion Adapter)
- Dream 7B
- dLLM library

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .advisory import (
    DiffusionAdvisoryGenerator,
    DiffusionConfig,
    DiffusionSamplerConfig,
    EditOperation,
    EditType,
    GenerationResult,
)

__all__ = [
    "DiffusionAdvisoryGenerator",
    "DiffusionConfig",
    "DiffusionSamplerConfig",
    "GenerationResult",
    "EditOperation",
    "EditType",
]

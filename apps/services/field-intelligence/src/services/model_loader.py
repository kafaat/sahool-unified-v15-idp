"""
Singleton model loader for agricultural AI models.
منفذ نموذج مفرد للنماذج الزراعية

Provides lazy-loaded singletons for:
- AgriGuardScorer   (rules-based, always available)
- HFAdvisorModel    (optional, requires CROP_ADVISOR_MODEL env + transformers)
- NLLBTranslator    (optional, requires TRANSLATION_MODEL env + transformers)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.agricultural_models import AgriGuardScorer, HFAdvisorModel, NLLBTranslator

logger = logging.getLogger(__name__)

# ── Singletons (initialised once on first use) ─────────────────────────────────

_agri_scorer: AgriGuardScorer | None = None
_hf_advisor: HFAdvisorModel | None = None
_nllb_translator: NLLBTranslator | None = None


def get_agri_scorer():
    """Return the singleton AgriGuardScorer (no download required)."""
    global _agri_scorer
    if _agri_scorer is None:
        from ..models.agricultural_models import AgriGuardScorer
        _agri_scorer = AgriGuardScorer()
        logger.info("AgriGuardScorer initialised")
    return _agri_scorer


def get_hf_advisor():
    """Return the singleton HFAdvisorModel (loads on first call if configured)."""
    global _hf_advisor
    if _hf_advisor is None:
        from ..models.agricultural_models import HFAdvisorModel
        _hf_advisor = HFAdvisorModel()
        if _hf_advisor.load():
            logger.info("HFAdvisorModel ready")
        else:
            logger.info("HFAdvisorModel not configured — will use OpenRouter fallback")
    return _hf_advisor


def get_nllb_translator():
    """Return the singleton NLLBTranslator (loads on first call if configured)."""
    global _nllb_translator
    if _nllb_translator is None:
        from ..models.agricultural_models import NLLBTranslator
        _nllb_translator = NLLBTranslator()
        if _nllb_translator.load():
            logger.info("NLLBTranslator ready")
        else:
            logger.info("NLLBTranslator not configured — Arabic generated directly by LLM")
    return _nllb_translator

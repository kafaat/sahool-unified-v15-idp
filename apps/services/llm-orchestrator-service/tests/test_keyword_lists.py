# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Invariant tests for INTENT_KEYWORDS.

The scorer in `calculate_intent_score()` matches keywords with plain
substring (`kw in text_lower`), so two keywords inside the *same* category
where one is a substring of the other would both fire on a single token —
double-counting it and inflating confidence. This module guards against
that drift by asserting the lists are overlap-free.

اختبارات ثابتة لقوائم الكلمات المفتاحية، تمنع تداخل جذر/اشتقاق داخل الفئة
نفسها من رفع درجة الثقة بشكل مصطنع.
"""

from __future__ import annotations

import pytest

try:
    from src.utils.intent_classifier import INTENT_KEYWORDS
except ImportError:
    pytest.skip("llm-orchestrator-service dependencies not installed", allow_module_level=True)


def test_no_intra_category_substring_overlap():
    """
    Inside a single (intent, language) list no keyword may be a substring of
    another. If it is, both fire on the same token and the flat per-match
    score in `calculate_intent_score` becomes misleading.
    """
    offenders: list[str] = []
    for intent, langs in INTENT_KEYWORDS.items():
        for lang, kws in langs.items():
            for shorter in kws:
                for longer in kws:
                    if shorter != longer and shorter in longer:
                        offenders.append(
                            f"{intent.value} ({lang}): '{shorter}' ⊂ '{longer}'"
                        )
    assert not offenders, (
        "INTENT_KEYWORDS contains overlapping keywords within a single "
        "category — substring matching will double-count a single token. "
        "Remove the longer form; the shorter one already covers it via "
        "prefix match:\n  - " + "\n  - ".join(offenders)
    )


def test_no_empty_keyword_lists():
    """Every intent must define at least one keyword per supported language."""
    for intent, langs in INTENT_KEYWORDS.items():
        for lang, kws in langs.items():
            assert kws, f"{intent.value} has no keywords for language '{lang}'"


def test_no_duplicate_keywords_in_category():
    """Duplicates within the same list would also double-score a match."""
    for intent, langs in INTENT_KEYWORDS.items():
        for lang, kws in langs.items():
            assert len(kws) == len(set(kws)), (
                f"{intent.value} ({lang}) has duplicate keywords: {kws}"
            )

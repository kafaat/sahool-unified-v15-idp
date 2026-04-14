"""Phase 1 scoring — simple, explainable, no ML.

Iteration 1 P0: zero-floor rule — no trigger match means no result.
"""

from __future__ import annotations

from app.models import Skill


EXTERNAL_PENALTY = 0.7
TRIGGER_WEIGHT = 2.0
DESC_WORD_WEIGHT = 0.2


def score_skill(query: str, skill: Skill) -> float:
    """Score a single skill against a query.

    Iteration 1 P0 semantics:
      - Trigger match contributes TRIGGER_WEIGHT per hit.
      - Description word match contributes DESC_WORD_WEIGHT per hit,
        BUT only counts if at least one trigger already matched
        (zero floor — prevents false positives on common words).
      - External skills (bundled plugins) down-ranked by EXTERNAL_PENALTY.

    Skills with zero trigger matches return 0 and are filtered out.
    """
    q = query.lower()

    trigger_score = 0.0
    for t in skill.triggers:
        if t.lower() in q:
            trigger_score += TRIGGER_WEIGHT

    # Zero floor: no trigger match → no score. Prevents description-noise
    # false positives (ADR-010 Iteration 1 P0 fix).
    if trigger_score == 0.0:
        return 0.0

    desc_score = 0.0
    for word in (skill.description or "").lower().split():
        if len(word) >= 4 and word in q:
            desc_score += DESC_WORD_WEIGHT

    score = trigger_score + desc_score

    if skill.external:
        score *= EXTERNAL_PENALTY

    return score


def filter_skills(skills: list[Skill], tenant_id: str) -> list[Skill]:
    """Exclude deprecated skills and enforce tenant scoping."""
    return [
        s
        for s in skills
        if not s.deprecated and (s.tenant_id == "*" or s.tenant_id == tenant_id)
    ]

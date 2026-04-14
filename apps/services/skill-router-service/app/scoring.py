"""Phase 1 scoring — simple, explainable, no ML."""

from __future__ import annotations

from app.models import Skill


EXTERNAL_PENALTY = 0.7


def score_skill(query: str, skill: Skill) -> float:
    """Score a single skill against a query.

    - Trigger match: +2.0 per trigger found (strong signal)
    - Description word match: +0.2 per word overlap (weak signal)
    - External skills (bundled plugins) are down-ranked by EXTERNAL_PENALTY
      so they don't dominate SAHOOL-native results.

    This is deliberately naive. The Router's job in v0 is to surface
    the ambiguity, not to resolve it perfectly.
    """
    q = query.lower()
    score = 0.0

    for t in skill.triggers:
        if t.lower() in q:
            score += 2.0

    for word in (skill.description or "").lower().split():
        if word in q:
            score += 0.2

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

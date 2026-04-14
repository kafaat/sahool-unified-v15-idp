"""Load the Skill Registry from index.yaml at startup."""

from __future__ import annotations

import yaml

from app.config import settings
from app.models import Skill


def load_skills() -> list[Skill]:
    """Read index.yaml and coerce each entry into a Skill model.

    Invalid entries are silently skipped (intentional for v0 — registry is
    generated, not hand-curated, so strict validation would fail the service
    on upstream data issues).
    """
    with open(settings.SKILLS_INDEX_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    skills: list[Skill] = []
    for s in data.get("skills", []) if data else []:
        try:
            skills.append(Skill(**s))
        except Exception:
            continue
    return skills

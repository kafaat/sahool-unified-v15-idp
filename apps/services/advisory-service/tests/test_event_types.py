"""
Tests for Event Types - advisory-service
"""

import pytest
from src.events.types import (
    DISEASE_DETECTED,
    FERTILIZER_PLAN_ISSUED,
    NUTRIENT_ASSESSMENT_ISSUED,
    RECOMMENDATION_ISSUED,
    SUBJECT_PREFIX,
    SUBJECTS,
    VERSIONS,
    get_subject,
    get_version,
)


class TestEventConstants:
    """Tests for event type constants"""

    def test_subject_prefix(self):
        assert SUBJECT_PREFIX == "sahool.advisory"

    def test_all_subjects_prefixed(self):
        for event_type, subject in SUBJECTS.items():
            assert subject.startswith(SUBJECT_PREFIX), f"{event_type} subject not prefixed"

    def test_all_versions_positive(self):
        for event_type, version in VERSIONS.items():
            assert version >= 1, f"{event_type} version < 1"


class TestGetSubject:
    """Tests for get_subject function"""

    def test_known_event_type(self):
        subject = get_subject(RECOMMENDATION_ISSUED)
        assert subject == "sahool.advisory.recommendation_issued"

    def test_fertilizer_plan_subject(self):
        subject = get_subject(FERTILIZER_PLAN_ISSUED)
        assert subject == "sahool.advisory.fertilizer_plan_issued"

    def test_nutrient_assessment_subject(self):
        subject = get_subject(NUTRIENT_ASSESSMENT_ISSUED)
        assert subject == "sahool.advisory.nutrient_assessment_issued"

    def test_disease_detected_subject(self):
        subject = get_subject(DISEASE_DETECTED)
        assert subject == "sahool.advisory.disease_detected"

    def test_unknown_event_type_fallback(self):
        subject = get_subject("unknown_event")
        assert subject == "sahool.advisory.unknown_event"


class TestGetVersion:
    """Tests for get_version function"""

    def test_known_version(self):
        v = get_version(RECOMMENDATION_ISSUED)
        assert v == 1

    def test_unknown_event_default_version(self):
        v = get_version("unknown_event")
        assert v == 1

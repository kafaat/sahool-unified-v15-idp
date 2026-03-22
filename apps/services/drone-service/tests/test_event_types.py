"""
Tests for event types module - اختبارات وحدة أنواع الأحداث
"""

from src.events.types import (
    DRONE_DEREGISTERED,
    DRONE_REGISTERED,
    DRONE_STATUS_CHANGED,
    DRONE_UPDATED,
    FLIGHT_PLANNED,
    FLIGHT_WEATHER_CHECKED,
    MISSION_ABORTED,
    MISSION_COMPLETED,
    MISSION_CREATED,
    MISSION_PAUSED,
    MISSION_RESUMED,
    MISSION_STARTED,
    SUBJECT_PREFIX,
    SUBJECTS,
    VERSIONS,
    VISION_DISEASE_DETECTED,
    VISION_PEST_DETECTED,
    VISION_WEED_DETECTED,
    VRA_PRESCRIPTION_CREATED,
    VRA_SPOT_SPRAY_CREATED,
    WEATHER_ALERT,
    get_subject,
    get_version,
)


class TestEventTypeConstants:
    """Test event type constant values."""

    def test_drone_lifecycle_constants(self):
        assert DRONE_REGISTERED == "drone_registered"
        assert DRONE_UPDATED == "drone_updated"
        assert DRONE_DEREGISTERED == "drone_deregistered"
        assert DRONE_STATUS_CHANGED == "drone_status_changed"

    def test_flight_planning_constants(self):
        assert FLIGHT_PLANNED == "flight_planned"
        assert FLIGHT_WEATHER_CHECKED == "weather_checked"

    def test_mission_lifecycle_constants(self):
        assert MISSION_CREATED == "mission_created"
        assert MISSION_STARTED == "mission_started"
        assert MISSION_PAUSED == "mission_paused"
        assert MISSION_RESUMED == "mission_resumed"
        assert MISSION_COMPLETED == "mission_completed"
        assert MISSION_ABORTED == "mission_aborted"

    def test_vra_constants(self):
        assert VRA_PRESCRIPTION_CREATED == "vra_prescription_created"
        assert VRA_SPOT_SPRAY_CREATED == "vra_spot_spray_created"

    def test_cross_service_constants(self):
        assert VISION_PEST_DETECTED == "sahool.vision.pest_detected"
        assert VISION_DISEASE_DETECTED == "sahool.vision.disease_detected"
        assert VISION_WEED_DETECTED == "sahool.vision.weed_detected"
        assert WEATHER_ALERT == "sahool.weather.alert"

    def test_subject_prefix(self):
        assert SUBJECT_PREFIX == "sahool.drone"
class TestSubjectsMapping:
    """Test NATS subjects mapping."""

    def test_all_event_types_have_subjects(self):
        expected_types = [
            DRONE_REGISTERED, DRONE_UPDATED, DRONE_DEREGISTERED,
            DRONE_STATUS_CHANGED, FLIGHT_PLANNED, FLIGHT_WEATHER_CHECKED,
            MISSION_CREATED, MISSION_STARTED, MISSION_PAUSED,
            MISSION_RESUMED, MISSION_COMPLETED, MISSION_ABORTED,
            VRA_PRESCRIPTION_CREATED, VRA_SPOT_SPRAY_CREATED,
        ]
        for et in expected_types:
            assert et in SUBJECTS, f"Missing subject for {et}"

    def test_subjects_use_correct_prefix(self):
        for subject in SUBJECTS.values():
            assert subject.startswith("sahool.drone."), f"Bad prefix: {subject}"

    def test_subject_drone_registered(self):
        assert SUBJECTS[DRONE_REGISTERED] == "sahool.drone.registered"

    def test_subject_mission_completed(self):
        assert SUBJECTS[MISSION_COMPLETED] == "sahool.drone.mission_completed"
class TestVersionsMapping:
    """Test event versions."""

    def test_all_event_types_have_versions(self):
        for et in SUBJECTS:
            assert et in VERSIONS

    def test_all_versions_are_positive_integers(self):
        for v in VERSIONS.values():
            assert isinstance(v, int)
            assert v >= 1
class TestGetSubject:
    """Test get_subject helper."""

    def test_known_event_type(self):
        assert get_subject(DRONE_REGISTERED) == "sahool.drone.registered"

    def test_unknown_event_type_fallback(self):
        result = get_subject("unknown_event")
        assert result == "sahool.drone.unknown_event"
class TestGetVersion:
    """Test get_version helper."""

    def test_known_event_type(self):
        assert get_version(DRONE_REGISTERED) == 1

    def test_unknown_event_type_defaults_to_1(self):
        assert get_version("nonexistent") == 1

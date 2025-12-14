"""
Tests for Field Chat API
"""

from src.models import ScopeType


class TestScopeType:
    """Test ScopeType enum"""

    def test_scope_types(self):
        """Test all scope types are defined"""
        assert ScopeType.FIELD == "field"
        assert ScopeType.TASK == "task"
        assert ScopeType.INCIDENT == "incident"

    def test_scope_type_values(self):
        """Test scope type string values"""
        assert ScopeType.FIELD.value == "field"
        assert ScopeType.TASK.value == "task"
        assert ScopeType.INCIDENT.value == "incident"


class TestEventTypes:
    """Test event type constants"""

    def test_event_types_defined(self):
        """Test all event types are defined"""
        from src.events.types import (
            CHAT_THREAD_CREATED,
            CHAT_MESSAGE_SENT,
            CHAT_MESSAGE_EDITED,
            CHAT_PARTICIPANT_JOINED,
            CHAT_PARTICIPANT_LEFT,
        )

        assert CHAT_THREAD_CREATED == "chat_thread_created"
        assert CHAT_MESSAGE_SENT == "chat_message_sent"
        assert CHAT_MESSAGE_EDITED == "chat_message_edited"
        assert CHAT_PARTICIPANT_JOINED == "chat_participant_joined"
        assert CHAT_PARTICIPANT_LEFT == "chat_participant_left"

    def test_subjects_defined(self):
        """Test all subjects are defined"""
        from src.events.types import SUBJECTS, CHAT_MESSAGE_SENT

        assert CHAT_MESSAGE_SENT in SUBJECTS
        assert SUBJECTS[CHAT_MESSAGE_SENT] == "chat.chat_message_sent"


class TestPublisher:
    """Test event publisher"""

    def test_event_envelope_creation(self):
        """Test creating event envelope"""
        from src.events.publish import EventEnvelope

        envelope = EventEnvelope.create(
            event_type="test_event",
            version=1,
            aggregate_id="agg-123",
            tenant_id="tenant-1",
            correlation_id="corr-456",
            payload={"key": "value"},
        )

        assert envelope.event_type == "test_event"
        assert envelope.version == 1
        assert envelope.aggregate_id == "agg-123"
        assert envelope.tenant_id == "tenant-1"
        assert envelope.correlation_id == "corr-456"
        assert envelope.payload == {"key": "value"}
        assert envelope.event_id is not None
        assert envelope.timestamp is not None


class TestRepository:
    """Test repository helper methods"""

    def test_generate_title_field(self):
        """Test title generation for field scope"""
        from src.repository import ChatRepository

        repo = ChatRepository()
        title = repo._generate_title("field", "field-123")

        assert "محادثة" in title or "Chat" in title

    def test_generate_title_task(self):
        """Test title generation for task scope"""
        from src.repository import ChatRepository

        repo = ChatRepository()
        title = repo._generate_title("task", "task-456")

        assert "محادثة" in title or "Chat" in title

    def test_generate_title_incident(self):
        """Test title generation for incident scope"""
        from src.repository import ChatRepository

        repo = ChatRepository()
        title = repo._generate_title("incident", "incident-789")

        assert "محادثة" in title or "Chat" in title


class TestProjectionWorker:
    """Test projection worker"""

    def test_truncate_short_text(self):
        """Test truncate with short text"""
        from src.projections.worker import ChatProjectionWorker

        worker = ChatProjectionWorker()
        result = worker._truncate("Hello", 10)

        assert result == "Hello"

    def test_truncate_long_text(self):
        """Test truncate with long text"""
        from src.projections.worker import ChatProjectionWorker

        worker = ChatProjectionWorker()
        result = worker._truncate("Hello World, this is a long message", 15)

        assert len(result) == 15
        assert result.endswith("...")

    def test_truncate_exact_length(self):
        """Test truncate with exact length"""
        from src.projections.worker import ChatProjectionWorker

        worker = ChatProjectionWorker()
        result = worker._truncate("1234567890", 10)

        assert result == "1234567890"

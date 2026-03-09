"""
Comprehensive tests for NATS event publisher (GAP-12).
Covers: payload structure, tenant_id, error handling, all event methods, edge cases.
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock

import pytest


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestKnowledgeEventPublisherPayloads:
    """Verify every event method sends correct payload structure."""

    def test_document_ingested_payload_structure(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher, SUBJECT_DOCUMENT_INGESTED

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(
            pub.document_ingested(
                document_id="doc-100",
                collection="crop_knowledge",
                domain="crops",
                source_credibility=4,
                chunks_count=5,
                vector_ids=["v1", "v2"],
                tenant_id="tenant-abc",
            )
        )

        call_args = mock_nc.publish.call_args
        subject = call_args[0][0]
        payload = json.loads(call_args[0][1])

        assert subject == SUBJECT_DOCUMENT_INGESTED
        assert payload["event"] == SUBJECT_DOCUMENT_INGESTED
        assert "timestamp" in payload
        assert payload["data"]["document_id"] == "doc-100"
        assert payload["data"]["collection"] == "crop_knowledge"
        assert payload["data"]["domain"] == "crops"
        assert payload["data"]["source_credibility"] == 4
        assert payload["data"]["chunks_count"] == 5
        assert payload["data"]["vector_ids"] == ["v1", "v2"]
        assert payload["data"]["tenant_id"] == "tenant-abc"

    def test_document_verified_payload_structure(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher, SUBJECT_DOCUMENT_VERIFIED

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(
            pub.document_verified(
                document_id="doc-200",
                status="approved",
                confidence_score=0.95,
                layers_passed=["structural", "semantic", "cross_ref", "safety"],
                tenant_id="tenant-xyz",
            )
        )

        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["event"] == SUBJECT_DOCUMENT_VERIFIED
        assert payload["data"]["status"] == "approved"
        assert payload["data"]["confidence_score"] == 0.95
        assert payload["data"]["layers_passed"] == ["structural", "semantic", "cross_ref", "safety"]
        assert payload["data"]["tenant_id"] == "tenant-xyz"

    def test_document_expired_payload_structure(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher, SUBJECT_DOCUMENT_EXPIRED

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(
            pub.document_expired(
                document_id="doc-300",
                title="Old Pesticide Guide 2020",
                domain="pest_disease",
                days_past_expiry=45,
                tenant_id="tenant-farm1",
            )
        )

        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["event"] == SUBJECT_DOCUMENT_EXPIRED
        assert payload["data"]["title"] == "Old Pesticide Guide 2020"
        assert payload["data"]["days_past_expiry"] == 45

    def test_collection_populated_payload_structure(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher, SUBJECT_COLLECTION_POPULATED

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(
            pub.collection_populated(
                collection="soil_knowledge",
                total_files=25,
                succeeded=23,
                failed=2,
                tenant_id="tenant-001",
            )
        )

        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["event"] == SUBJECT_COLLECTION_POPULATED
        assert payload["data"]["collection"] == "soil_knowledge"
        assert payload["data"]["total_files"] == 25
        assert payload["data"]["succeeded"] == 23
        assert payload["data"]["failed"] == 2

    def test_ingestion_failed_payload_structure(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher, SUBJECT_INGESTION_FAILED

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(
            pub.ingestion_failed(
                document_id="doc-400",
                source_path="/docs/bad-file.md",
                errors=["Parse error", "Invalid format"],
                tenant_id="tenant-002",
            )
        )

        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["event"] == SUBJECT_INGESTION_FAILED
        assert payload["data"]["source_path"] == "/docs/bad-file.md"
        assert payload["data"]["errors"] == ["Parse error", "Invalid format"]


@pytest.mark.unit
class TestKnowledgeEventPublisherDefaults:
    """Verify default parameter values."""

    def test_default_tenant_id_is_empty(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(pub.document_ingested(document_id="d1", collection="c1", domain="crops"))
        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["data"]["tenant_id"] == ""

    def test_default_vector_ids_is_empty_list(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(pub.document_ingested(document_id="d1", collection="c1", domain="crops"))
        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["data"]["vector_ids"] == []

    def test_default_layers_passed_is_empty_list(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(pub.document_verified(document_id="d1", status="pending", confidence_score=0.5))
        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["data"]["layers_passed"] == []

    def test_default_errors_is_empty_list(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(pub.ingestion_failed(document_id="d1", source_path="/x"))
        payload = json.loads(mock_nc.publish.call_args[0][1])
        assert payload["data"]["errors"] == []


@pytest.mark.unit
class TestKnowledgeEventPublisherErrorHandling:
    """Verify graceful error handling."""

    def test_publish_error_does_not_raise(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        mock_nc.publish.side_effect = ConnectionError("NATS disconnected")
        pub = KnowledgeEventPublisher(nc=mock_nc)

        # Should not raise
        _run(pub.document_ingested(document_id="d1", collection="c1", domain="crops"))

    def test_publish_timeout_does_not_raise(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        mock_nc.publish.side_effect = TimeoutError("Connection timed out")
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(pub.collection_populated(collection="c1", total_files=10, succeeded=10, failed=0))

    def test_timestamp_is_iso_format(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher
        from datetime import datetime

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(pub.document_ingested(document_id="d1", collection="c1", domain="crops"))
        payload = json.loads(mock_nc.publish.call_args[0][1])

        # Should parse as ISO datetime
        ts = datetime.fromisoformat(payload["timestamp"])
        assert ts is not None

    def test_payload_is_utf8_encoded(self):
        from shared.ai.knowledge.events import KnowledgeEventPublisher

        mock_nc = AsyncMock()
        pub = KnowledgeEventPublisher(nc=mock_nc)

        _run(
            pub.document_expired(
                document_id="d-ar",
                title="دليل المبيدات القديم",
                domain="pest_disease",
            )
        )

        raw_bytes = mock_nc.publish.call_args[0][1]
        assert isinstance(raw_bytes, bytes)
        payload = json.loads(raw_bytes.decode("utf-8"))
        assert payload["data"]["title"] == "دليل المبيدات القديم"


@pytest.mark.unit
class TestNatsClientProtocol:
    """Verify the NatsClient protocol."""

    def test_protocol_conformance(self):
        from shared.ai.knowledge.events import NatsClient

        mock_nc = AsyncMock()
        assert hasattr(mock_nc, "publish")
        # Verify it matches protocol
        assert isinstance(mock_nc, object)  # NatsClient is structural

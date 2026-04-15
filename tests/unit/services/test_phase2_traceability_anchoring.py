"""
Unit tests for the Phase 2 traceability anchoring subscriber.

Tests cover:

* Subject classification (event routing + ignore rules)
* Hash-chain integrity across multiple events
* Tamper detection via ``verify_chain``
* Tenant isolation (two tenants can have chains for the same field_id
  without cross-contamination)
* Graceful handling of malformed payloads (missing field_id, non-JSON)
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from types import SimpleNamespace

import pytest


def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # Must be registered before exec_module
    spec.loader.exec_module(mod)
    return mod


_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_subscriber_mod = _load_module(
    "phase2_trace_subscriber",
    os.path.join(
        _REPO_ROOT,
        "apps",
        "services",
        "traceability-service",
        "src",
        "anchoring",
        "subscriber.py",
    ),
)
FieldEventSubscriber = _subscriber_mod.FieldEventSubscriber
classify_event = _subscriber_mod.classify_event


# ---------------------------------------------------------------------------
# Classifier tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "subject,expected",
    [
        ("sahool.field.activity.recorded", "activity"),
        ("sahool.field.harvest.completed", "harvesting"),
        ("sahool.field.crop_season.started", "planting"),
        ("sahool.field.crop_season.ended", "harvesting"),
        ("sahool.field.crop_season.updated", "state_change"),
        ("sahool.field.operation.fertilizing", "fertilizing"),
        ("sahool.field.operation.spraying", "spraying"),
        ("sahool.field.operation.irrigating", "irrigating"),
        ("sahool.field.observation.ingested", "observation"),
        # Fallback path: unknown operation subtype → "activity"
        ("sahool.field.operation.something_new", "activity"),
        # Fallback path: harvest subtype
        ("sahool.field.harvest.partial", "harvesting"),
    ],
)
def test_classify_actionable_events(subject, expected):
    assert classify_event(subject) == expected


@pytest.mark.parametrize(
    "subject",
    [
        "sahool.field.created",  # admin CRUD
        "sahool.field.updated",  # admin CRUD
        "sahool.field.deleted",  # admin CRUD
        "sahool.weather.alert.frost",  # not a field event
        "sahool.traceability.batch_created",  # not a field event
    ],
)
def test_classify_ignored_events(subject):
    assert classify_event(subject) is None


# ---------------------------------------------------------------------------
# Fake NATS + async helpers
# ---------------------------------------------------------------------------


class FakeNatsClient:
    """In-memory NATS stand-in that records every publish call."""

    def __init__(self):
        self.published: list[tuple[str, bytes]] = []

    async def publish(self, subject: str, payload: bytes):
        self.published.append((subject, payload))


@pytest.fixture
def subscriber() -> FieldEventSubscriber:
    # db_pool=None forces the in-memory-only path
    return FieldEventSubscriber(nats_client=FakeNatsClient(), db_pool=None)


def _fake_msg(subject: str, payload: dict) -> SimpleNamespace:
    return SimpleNamespace(subject=subject, data=json.dumps(payload).encode())


# ---------------------------------------------------------------------------
# Anchor chain tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_single_event_creates_anchor(subscriber: FieldEventSubscriber):
    msg = _fake_msg(
        "sahool.field.crop_season.started",
        {
            "tenant_id": "t-1",
            "field_id": "F-1",
            "crop": "wheat",
            "variety": "Sakha95",
        },
    )
    await subscriber._handle_message(msg)

    chain = subscriber.get_chain("t-1", "F-1")
    assert len(chain) == 1
    anchor = chain[0]
    assert anchor.event_type == "planting"
    assert anchor.previous_hash == "genesis"
    assert anchor.sequence == 0
    assert anchor.payload_summary.get("crop") == "wheat"
    assert subscriber.verify_chain("t-1", "F-1") is True


@pytest.mark.asyncio
async def test_chain_linked_across_events(subscriber: FieldEventSubscriber):
    events = [
        ("sahool.field.crop_season.started", {"tenant_id": "t-1", "field_id": "F-1"}),
        ("sahool.field.operation.fertilizing", {"tenant_id": "t-1", "field_id": "F-1"}),
        ("sahool.field.operation.irrigating", {"tenant_id": "t-1", "field_id": "F-1"}),
        ("sahool.field.harvest.completed", {"tenant_id": "t-1", "field_id": "F-1"}),
    ]
    for subj, payload in events:
        await subscriber._handle_message(_fake_msg(subj, payload))

    chain = subscriber.get_chain("t-1", "F-1")
    assert len(chain) == 4
    assert [a.sequence for a in chain] == [0, 1, 2, 3]
    # Each anchor's previous_hash MUST equal the preceding anchor's hash
    assert chain[0].previous_hash == "genesis"
    for i in range(1, 4):
        assert chain[i].previous_hash == chain[i - 1].hash
    assert subscriber.verify_chain("t-1", "F-1") is True


@pytest.mark.asyncio
async def test_tamper_detection_fails_verify(subscriber: FieldEventSubscriber):
    for _ in range(3):
        await subscriber._handle_message(
            _fake_msg(
                "sahool.field.operation.spraying",
                {"tenant_id": "t-1", "field_id": "F-1"},
            )
        )
    # Tamper with the middle anchor's hash — chain becomes invalid
    chain_container = subscriber._chains[("t-1", "F-1")]
    chain_container.anchors[1].hash = (
        "0000000000000000000000000000000000000000000000000000000000000000"
    )
    assert subscriber.verify_chain("t-1", "F-1") is False


@pytest.mark.asyncio
async def test_tenant_isolation(subscriber: FieldEventSubscriber):
    # Two different tenants on the SAME field_id must not share a chain
    await subscriber._handle_message(
        _fake_msg(
            "sahool.field.operation.spraying",
            {"tenant_id": "tenant-A", "field_id": "F-1"},
        )
    )
    await subscriber._handle_message(
        _fake_msg(
            "sahool.field.operation.spraying",
            {"tenant_id": "tenant-B", "field_id": "F-1"},
        )
    )
    a_chain = subscriber.get_chain("tenant-A", "F-1")
    b_chain = subscriber.get_chain("tenant-B", "F-1")
    assert len(a_chain) == 1
    assert len(b_chain) == 1
    # Neither chain is contaminated by the other's hashes
    assert a_chain[0].hash != b_chain[0].hash


@pytest.mark.asyncio
async def test_ignored_events_not_anchored(subscriber: FieldEventSubscriber):
    await subscriber._handle_message(
        _fake_msg(
            "sahool.field.created",
            {"tenant_id": "t-1", "field_id": "F-1"},
        )
    )
    assert subscriber.get_chain("t-1", "F-1") == []
    assert subscriber.stats["events_ignored"] == 1
    assert subscriber.stats["anchors_created"] == 0


@pytest.mark.asyncio
async def test_missing_field_id_skipped(subscriber: FieldEventSubscriber):
    # No field_id in payload — subscriber must log and skip, not crash
    await subscriber._handle_message(
        _fake_msg(
            "sahool.field.operation.spraying",
            {"tenant_id": "t-1"},  # field_id missing
        )
    )
    assert subscriber.stats["events_ignored"] == 1
    assert subscriber.stats["anchors_created"] == 0


@pytest.mark.asyncio
async def test_malformed_payload_does_not_crash(subscriber: FieldEventSubscriber):
    # Raw non-JSON bytes — subscriber should log and skip gracefully
    msg = SimpleNamespace(subject="sahool.field.operation.spraying", data=b"not-json")
    await subscriber._handle_message(msg)
    # No anchor created, no error raised (error count unchanged)
    assert subscriber.stats["anchors_created"] == 0


@pytest.mark.asyncio
async def test_publish_anchor_emitted_on_success(subscriber: FieldEventSubscriber):
    await subscriber._handle_message(
        _fake_msg(
            "sahool.field.operation.spraying",
            {"tenant_id": "t-1", "field_id": "F-1"},
        )
    )
    published = subscriber._nc.published  # type: ignore[attr-defined]
    assert len(published) == 1
    subject, body = published[0]
    assert subject == FieldEventSubscriber.ANCHOR_SUBJECT
    decoded = json.loads(body)
    assert decoded["tenant_id"] == "t-1"
    assert decoded["field_id"] == "F-1"
    assert decoded["event_type"] == "spraying"
    assert decoded["sequence"] == 0

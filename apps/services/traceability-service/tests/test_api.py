"""API endpoint tests for traceability-service with mocked DB."""

import json
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest


class FakeRecord(dict):
    """Fake asyncpg Record that supports both dict and attribute access."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)


def _make_batch_record(**overrides):
    """Create a fake batch DB record."""
    defaults = {
        "id": uuid.uuid4(),
        "tenant_id": "TENANT-001",
        "farm_id": "FARM-001",
        "field_id": "FIELD-001",
        "batch_code": "WH-26-001",
        "product_name_en": "Organic Wheat",
        "product_name_ar": "قمح عضوي",
        "variety": "Sakha 95",
        "quantity": 1000.0,
        "unit": "kg",
        "quality_grade": "A",
        "status": "created",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return FakeRecord(defaults)


def _make_event_record(event_type="harvest", **overrides):
    """Create a fake supply chain event DB record."""
    defaults = {
        "id": uuid.uuid4(),
        "batch_id": uuid.uuid4(),
        "event_type": event_type,
        "timestamp": datetime.now(UTC),
        "location": "Field A",
        "location_ar": "الحقل أ",
        "crop_type": "wheat" if event_type == "harvest" else None,
        "harvest_method": "mechanical" if event_type == "harvest" else None,
        "quality_grade": "A" if event_type == "harvest" else None,
        "facility_name": "Packing House" if event_type == "processing" else None,
        "process_type": "sorting" if event_type == "processing" else None,
        "temperature_c": 4.0 if event_type == "storage" else None,
        "humidity_percent": 85.0 if event_type == "storage" else None,
        "origin": "Farm A" if event_type == "transport" else None,
        "destination": "Market B" if event_type == "transport" else None,
        "transport_mode": "truck" if event_type == "transport" else None,
        "vehicle_id": None,
        "notes": None,
        "notes_ar": None,
        "metadata": "{}",
        "created_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return FakeRecord(defaults)


class TestBatchEndpoints:
    """Test batch CRUD endpoints."""

    def test_create_batch(self, db_client, mock_db_pool):
        """Test creating a produce batch."""
        from src.api.v1.batches import get_current_user
        from src.main import app

        # Override auth dependency for testing
        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}

        try:
            batch_record = _make_batch_record()
            mock_db_pool.fetchval.return_value = 0  # count for sequence
            mock_db_pool.fetchrow.return_value = batch_record

            response = db_client.post(
                "/api/v1/traceability/batches",
                json={
                    "farm_id": "FARM-001",
                    "field_id": "FIELD-001",
                    "product_name_en": "Organic Wheat",
                    "product_name_ar": "قمح عضوي",
                    "quantity": 1000.0,
                    "unit": "kg",
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data["product_name_en"] == "Organic Wheat"
            assert data["product_name_ar"] == "قمح عضوي"
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_get_batch(self, db_client, mock_db_pool):
        """Test getting a batch by ID."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.return_value = _make_batch_record(id=batch_id)

        response = db_client.get(f"/api/v1/traceability/batches/{batch_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["batch_code"] == "WH-26-001"

    def test_get_batch_not_found(self, db_client, mock_db_pool):
        """Test 404 for non-existent batch."""
        mock_db_pool.fetchrow.return_value = None

        response = db_client.get(f"/api/v1/traceability/batches/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_list_batches(self, db_client, mock_db_pool):
        """Test listing batches."""
        mock_db_pool.fetch.return_value = [_make_batch_record(), _make_batch_record()]

        response = db_client.get("/api/v1/traceability/batches")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2

    def test_list_batches_with_filters(self, db_client, mock_db_pool):
        """Test listing batches with farm filter (tenant from header)."""
        mock_db_pool.fetch.return_value = [_make_batch_record()]

        response = db_client.get("/api/v1/traceability/batches?farm_id=F1")
        assert response.status_code == 200

    def test_no_database_returns_503(self):
        """Test that missing DB pool returns 503."""
        from src.main import app

        # Ensure no db_pool is set
        if hasattr(app.state, "db_pool"):
            saved = app.state.db_pool
            app.state.db_pool = None
        else:
            saved = None
        try:
            from fastapi.testclient import TestClient

            c = TestClient(app)
            c.headers["X-Tenant-Id"] = "00000000-0000-0000-0000-000000000001"
            response = c.get("/api/v1/traceability/batches")
            assert response.status_code == 503
        finally:
            app.state.db_pool = saved


class TestSupplyChainEvents:
    """Test supply chain event recording."""

    def test_record_harvest_event(self, db_client, mock_db_pool):
        """Test recording a harvest event."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_batch_record(id=batch_id),
            _make_event_record("harvest", batch_id=batch_id),
        ]

        response = db_client.post(
            f"/api/v1/traceability/batches/{batch_id}/events/harvest",
            json={
                "field_name_en": "Field A",
                "field_name_ar": "الحقل أ",
                "crop_type": "wheat",
                "harvest_method_en": "Mechanical",
                "harvest_method_ar": "آلي",
                "quality_grade": "A",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "recorded"

    def test_record_processing_event(self, db_client, mock_db_pool):
        """Test recording a processing event."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_batch_record(id=batch_id),
            _make_event_record("processing", batch_id=batch_id),
        ]

        response = db_client.post(
            f"/api/v1/traceability/batches/{batch_id}/events/processing",
            json={"facility_name": "Packing House", "process_type": "sorting"},
        )
        assert response.status_code == 200

    def test_record_storage_event(self, db_client, mock_db_pool):
        """Test recording a storage event."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_batch_record(id=batch_id),
            _make_event_record("storage", batch_id=batch_id),
        ]

        response = db_client.post(
            f"/api/v1/traceability/batches/{batch_id}/events/storage",
            json={"location": "Cold Storage A", "temperature_c": 4.0, "humidity_percent": 85.0},
        )
        assert response.status_code == 200

    def test_record_transport_event(self, db_client, mock_db_pool):
        """Test recording a transport event."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_batch_record(id=batch_id),
            _make_event_record("transport", batch_id=batch_id),
        ]

        response = db_client.post(
            f"/api/v1/traceability/batches/{batch_id}/events/transport",
            json={"origin": "Farm A", "destination": "Market B", "transport_mode": "truck", "distance_km": 150.0},
        )
        assert response.status_code == 200

    def test_list_events(self, db_client, mock_db_pool):
        """Test listing events for a batch."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.return_value = _make_batch_record(id=batch_id)
        mock_db_pool.fetch.return_value = [
            _make_event_record("harvest"),
            _make_event_record("transport"),
        ]

        response = db_client.get(f"/api/v1/traceability/batches/{batch_id}/events")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2


class TestBatchSplit:
    """Test batch split functionality."""

    def test_split_batch(self, db_client, mock_db_pool):
        """Test splitting a batch into sub-batches."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_batch_record(id=batch_id, quantity=1000.0),
            _make_batch_record(batch_code="WH-26-001-S1", quantity=400.0),
            _make_batch_record(batch_code="WH-26-001-S2", quantity=600.0),
        ]

        response = db_client.post(
            f"/api/v1/traceability/batches/{batch_id}/split",
            json={"quantities": [400.0, 600.0]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["remaining_quantity"] == 0.0
        assert len(data["child_batches"]) == 2

    def test_split_exceeds_quantity(self, db_client, mock_db_pool):
        """Test that split total exceeding quantity returns 400."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.return_value = _make_batch_record(id=batch_id, quantity=100.0)

        response = db_client.post(
            f"/api/v1/traceability/batches/{batch_id}/split",
            json={"quantities": [60.0, 60.0]},
        )
        assert response.status_code == 400


class TestBatchCodes:
    """Test batch code generation and verification."""

    def test_generate_code(self, db_client):
        """Test batch code generation."""
        response = db_client.post(
            "/api/v1/traceability/batches/generate-code",
            json={"product_code": "WH", "sequence": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert "batch_code" in data
        assert "WH" in data["batch_code"]

    def test_verify_code(self, db_client, mock_db_pool):
        """Test batch code verification."""
        mock_db_pool.fetchval.return_value = True

        response = db_client.get("/api/v1/traceability/batches/verify-code/WH-26-001")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "WH-26-001"
        assert data["exists"] is True


class TestProductJourney:
    """Test consumer product journey endpoint."""

    def test_get_journey(self, db_client, mock_db_pool):
        """Test getting product journey by batch code."""
        from src.api.v1.batches import get_current_user
        from src.main import app

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}

        try:
            batch_id = uuid.uuid4()
            mock_db_pool.fetchrow.return_value = _make_batch_record(id=batch_id, batch_code="WH-26-001")
            mock_db_pool.fetch.side_effect = [
                [_make_event_record("harvest", batch_id=batch_id)],
                [],  # certifications
            ]

            response = db_client.get("/api/v1/traceability/journey/WH-26-001")
            assert response.status_code == 200
            data = response.json()
            assert data["batch_code"] == "WH-26-001"
            assert data["product_name_en"] == "Organic Wheat"
            assert len(data["journey"]) == 1
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_journey_not_found(self, db_client, mock_db_pool):
        """Test 404 for non-existent batch code."""
        from src.api.v1.batches import get_current_user
        from src.main import app

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}

        try:
            mock_db_pool.fetchrow.return_value = None

            response = db_client.get("/api/v1/traceability/journey/INVALID-CODE")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestRecallManagement:
    """Test recall management endpoints (GS1 EPCIS compliance)."""

    def test_initiate_recall(self, db_client, mock_db_pool):
        """Test initiating a product recall."""
        from src.api.v1.batches import get_current_user
        from src.main import app

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}

        try:
            batch_id = uuid.uuid4()
            recall_event = _make_event_record("recall", batch_id=batch_id)

            mock_db_pool.fetchrow.side_effect = [
                _make_batch_record(id=batch_id, status="in_transit"),  # get batch
                recall_event,  # insert recall event
            ]
            mock_db_pool.fetch.return_value = []  # no child batches
            mock_db_pool.execute.return_value = None

            response = db_client.post(
                f"/api/v1/traceability/batches/{batch_id}/recall",
                json={
                    "reason_en": "Contamination detected",
                    "reason_ar": "تم اكتشاف تلوث",
                    "severity": "critical",
                    "affected_regions": ["Riyadh", "Jeddah"],
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "recalled"
            assert data["severity"] == "critical"
            assert data["reason_en"] == "Contamination detected"
            assert data["reason_ar"] == "تم اكتشاف تلوث"
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_recall_already_recalled_batch(self, db_client, mock_db_pool):
        """Test that recalling an already recalled batch returns 400."""
        from src.api.v1.batches import get_current_user
        from src.main import app

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}

        try:
            batch_id = uuid.uuid4()
            mock_db_pool.fetchrow.return_value = _make_batch_record(id=batch_id, status="recalled")

            response = db_client.post(
                f"/api/v1/traceability/batches/{batch_id}/recall",
                json={"reason_en": "Test", "reason_ar": "اختبار"},
            )
            assert response.status_code == 400
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_recall_with_child_batches(self, db_client, mock_db_pool):
        """Test recall propagates to child batches."""
        from src.api.v1.batches import get_current_user
        from src.main import app

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}

        try:
            batch_id = uuid.uuid4()
            child1_id = uuid.uuid4()
            child2_id = uuid.uuid4()

            mock_db_pool.fetchrow.side_effect = [
                _make_batch_record(id=batch_id, batch_code="WH-26-001", status="in_transit"),
                _make_event_record("recall", batch_id=batch_id),
            ]
            mock_db_pool.fetch.return_value = [
                FakeRecord({"id": child1_id, "batch_code": "WH-26-001-S1", "status": "in_transit"}),
                FakeRecord({"id": child2_id, "batch_code": "WH-26-001-S2", "status": "in_storage"}),
            ]
            mock_db_pool.execute.return_value = None

            response = db_client.post(
                f"/api/v1/traceability/batches/{batch_id}/recall",
                json={"reason_en": "Quality issue", "reason_ar": "مشكلة في الجودة", "severity": "high"},
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["affected_children"]) == 2
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestNATSEventPublishing:
    """Test that NATS events are published correctly."""

    def test_create_batch_publishes_event(self, db_client, mock_db_pool, mock_nats):
        """Test batch creation publishes NATS event."""
        from src.api.v1.batches import get_current_user
        from src.main import app

        app.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}

        try:
            mock_db_pool.fetchval.return_value = 0
            mock_db_pool.fetchrow.return_value = _make_batch_record()

            db_client.post(
                "/api/v1/traceability/batches",
                json={
                    "farm_id": "F1",
                    "field_id": "FLD1",
                    "product_name_en": "Wheat",
                    "product_name_ar": "قمح",
                    "quantity": 100.0,
                },
            )

            # Verify NATS publish was called with correct subject
            assert mock_nats.publish.called
            call_args = mock_nats.publish.call_args_list
            subjects = [c.args[0] for c in call_args]
            assert "sahool.traceability.batch_created" in subjects
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_harvest_publishes_event(self, db_client, mock_db_pool, mock_nats):
        """Test harvest event publishes NATS event."""
        batch_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_batch_record(id=batch_id),
            _make_event_record("harvest", batch_id=batch_id),
        ]

        db_client.post(
            f"/api/v1/traceability/batches/{batch_id}/events/harvest",
            json={
                "field_name_en": "Field A",
                "field_name_ar": "الحقل أ",
                "crop_type": "wheat",
            },
        )

        assert mock_nats.publish.called
        subjects = [c.args[0] for c in mock_nats.publish.call_args_list]
        assert "sahool.traceability.harvest_recorded" in subjects

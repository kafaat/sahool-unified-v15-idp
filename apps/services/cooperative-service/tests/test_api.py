"""API endpoint tests for cooperative-service with mocked DB."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest


class FakeRecord(dict):
    """Fake asyncpg Record that supports both dict and attribute access."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)


def _make_coop_record(**overrides):
    """Create a fake cooperative DB record."""
    defaults = {
        "id": uuid.uuid4(),
        "tenant_id": "TENANT-001",
        "name": "Al-Falah Cooperative",
        "name_ar": "تعاونية الفلاح",
        "type": "multi_purpose",
        "description": "Test cooperative",
        "description_ar": "تعاونية تجريبية",
        "region": "Riyadh",
        "status": "active",
        "member_count": 0,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return FakeRecord(defaults)


def _make_member_record(**overrides):
    """Create a fake member DB record."""
    defaults = {
        "id": uuid.uuid4(),
        "cooperative_id": uuid.uuid4(),
        "farmer_id": "FARMER-001",
        "name": "Ahmed",
        "name_ar": "أحمد",
        "phone": "+966500000001",
        "role": "member",
        "share_count": 1,
        "land_area_ha": 5.0,
        "status": "active",
        "joined_at": datetime.now(UTC),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return FakeRecord(defaults)


def _make_resource_record(**overrides):
    """Create a fake resource DB record."""
    defaults = {
        "id": uuid.uuid4(),
        "cooperative_id": uuid.uuid4(),
        "name": "Tractor",
        "name_ar": "جرار",
        "type": "equipment",
        "model": "John Deere 5050D",
        "capacity": 50.0,
        "capacity_unit": "hp",
        "hourly_rate": 100.0,
        "status": "available",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return FakeRecord(defaults)


class TestCooperativeEndpoints:
    """Test cooperative CRUD endpoints."""

    def test_create_cooperative(self, db_client, mock_db_pool):
        """Test creating a cooperative."""
        coop_record = _make_coop_record()
        mock_db_pool.fetchrow.return_value = coop_record

        response = db_client.post(
            "/api/v1/cooperatives/",
            json={
                "name": "Al-Falah Cooperative",
                "name_ar": "تعاونية الفلاح",
                "type": "multi_purpose",
                "region": "Riyadh",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Al-Falah Cooperative"
        assert data["name_ar"] == "تعاونية الفلاح"

    def test_list_cooperatives(self, db_client, mock_db_pool):
        """Test listing cooperatives."""
        mock_db_pool.fetch.return_value = [_make_coop_record(), _make_coop_record()]

        response = db_client.get("/api/v1/cooperatives/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["cooperatives"]) == 2

    def test_list_cooperatives_filtered_by_tenant_header(self, db_client, mock_db_pool):
        """Test listing cooperatives filtered by tenant from X-Tenant-Id header."""
        mock_db_pool.fetch.return_value = [_make_coop_record(tenant_id="00000000-0000-0000-0000-000000000001")]

        response = db_client.get("/api/v1/cooperatives/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1

    def test_get_cooperative(self, db_client, mock_db_pool):
        """Test getting a cooperative with members and resources."""
        coop_id = uuid.uuid4()
        mock_db_pool.fetchrow.return_value = _make_coop_record(id=coop_id)
        mock_db_pool.fetch.return_value = []

        response = db_client.get(f"/api/v1/cooperatives/{coop_id}")
        assert response.status_code == 200
        data = response.json()
        assert "members" in data
        assert "resources" in data

    def test_get_cooperative_not_found(self, db_client, mock_db_pool):
        """Test 404 for non-existent cooperative."""
        mock_db_pool.fetchrow.return_value = None

        response = db_client.get(f"/api/v1/cooperatives/{uuid.uuid4()}")
        assert response.status_code == 404

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
            response = c.get("/api/v1/cooperatives/")
            assert response.status_code == 503
        finally:
            app.state.db_pool = saved


class TestMemberEndpoints:
    """Test member management endpoints."""

    def test_add_member(self, db_client, mock_db_pool):
        """Test adding a member to a cooperative."""
        coop_id = uuid.uuid4()
        member_record = _make_member_record(cooperative_id=coop_id)

        # First call: _get_coop_or_404, Second call: INSERT member
        mock_db_pool.fetchrow.side_effect = [
            _make_coop_record(id=coop_id),
            member_record,
        ]

        response = db_client.post(
            f"/api/v1/cooperatives/{coop_id}/members",
            json={
                "farmer_id": "FARMER-001",
                "name": "Ahmed",
                "name_ar": "أحمد",
                "phone": "+966500000001",
                "role": "member",
                "share_count": 1,
                "land_area_ha": 5.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Ahmed"
        assert data["name_ar"] == "أحمد"

    def test_list_members(self, db_client, mock_db_pool):
        """Test listing cooperative members."""
        coop_id = uuid.uuid4()
        mock_db_pool.fetchrow.return_value = _make_coop_record(id=coop_id)
        mock_db_pool.fetch.return_value = [_make_member_record(cooperative_id=coop_id)]

        response = db_client.get(f"/api/v1/cooperatives/{coop_id}/members")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1


class TestResourceEndpoints:
    """Test resource management endpoints."""

    def test_register_resource(self, db_client, mock_db_pool):
        """Test registering a shared resource."""
        coop_id = uuid.uuid4()
        resource_record = _make_resource_record(cooperative_id=coop_id)

        mock_db_pool.fetchrow.side_effect = [
            _make_coop_record(id=coop_id),
            resource_record,
        ]

        response = db_client.post(
            f"/api/v1/cooperatives/{coop_id}/resources",
            json={
                "name": "Tractor",
                "name_ar": "جرار",
                "type": "equipment",
                "hourly_rate": 100.0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tractor"
        assert data["type"] == "equipment"

    def test_list_resources(self, db_client, mock_db_pool):
        """Test listing cooperative resources."""
        coop_id = uuid.uuid4()
        mock_db_pool.fetchrow.return_value = _make_coop_record(id=coop_id)
        mock_db_pool.fetch.return_value = [_make_resource_record()]

        response = db_client.get(f"/api/v1/cooperatives/{coop_id}/resources")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1


class TestRevenueDistribution:
    """Test revenue distribution endpoints."""

    def test_distribute_revenue_equal(self, db_client, mock_db_pool):
        """Test equal revenue distribution."""
        coop_id = uuid.uuid4()
        members = [
            _make_member_record(cooperative_id=coop_id, name="Ahmed", name_ar="أحمد"),
            _make_member_record(cooperative_id=coop_id, name="Hassan", name_ar="حسن"),
        ]

        mock_db_pool.fetchrow.return_value = _make_coop_record(id=coop_id)
        mock_db_pool.fetch.return_value = members

        response = db_client.post(
            f"/api/v1/cooperatives/{coop_id}/revenue/distribute",
            json={"total_revenue": 10000.0, "method": "production"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] == 10000.0
        assert len(data["distributions"]) == 2
        assert data["distributions"][0]["amount"] == 5000.0


class TestStatistics:
    """Test statistics endpoint."""

    def test_get_stats(self, db_client, mock_db_pool):
        """Test cooperative statistics."""
        coop_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_coop_record(id=coop_id),
            FakeRecord(
                {
                    "member_count": 5,
                    "resource_count": 3,
                    "total_land_area_ha": 25.0,
                    "total_shares": 10,
                    "active_bookings": 2,
                    "total_booking_revenue": 1500.0,
                }
            ),
        ]

        response = db_client.get(f"/api/v1/cooperatives/{coop_id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["member_count"] == 5
        assert data["resource_count"] == 3
        assert data["total_land_area_ha"] == 25.0


class TestNATSEventPublishing:
    """Test that NATS events are published correctly."""

    def test_create_cooperative_publishes_event(self, db_client, mock_db_pool, mock_nats):
        """Test cooperative creation publishes NATS event."""
        mock_db_pool.fetchrow.return_value = _make_coop_record()

        db_client.post(
            "/api/v1/cooperatives/",
            json={
                "name": "Test Coop",
                "name_ar": "تعاونية تجربة",
            },
        )

        assert mock_nats.publish.called
        subjects = [c.args[0] for c in mock_nats.publish.call_args_list]
        assert "sahool.cooperative.created" in subjects

    def test_add_member_publishes_event(self, db_client, mock_db_pool, mock_nats):
        """Test adding member publishes NATS event."""
        coop_id = uuid.uuid4()
        mock_db_pool.fetchrow.side_effect = [
            _make_coop_record(id=coop_id),  # _get_coop_or_404
            _make_member_record(cooperative_id=coop_id),  # INSERT RETURNING
        ]

        db_client.post(
            f"/api/v1/cooperatives/{coop_id}/members",
            json={"farmer_id": "F1", "name": "Ahmed", "name_ar": "أحمد"},
        )

        assert mock_nats.publish.called
        subjects = [c.args[0] for c in mock_nats.publish.call_args_list]
        assert "sahool.cooperative.member_added" in subjects

    def test_revenue_distribution_publishes_event_and_notification(self, db_client, mock_db_pool, mock_nats):
        """Test revenue distribution publishes event + notification."""
        coop_id = uuid.uuid4()
        mock_db_pool.fetchrow.return_value = _make_coop_record(id=coop_id)
        mock_db_pool.fetch.return_value = [
            _make_member_record(cooperative_id=coop_id, name="Ahmed", name_ar="أحمد"),
        ]

        db_client.post(
            f"/api/v1/cooperatives/{coop_id}/revenue/distribute",
            json={"total_revenue": 5000.0, "method": "production"},
        )

        assert mock_nats.publish.called
        subjects = [c.args[0] for c in mock_nats.publish.call_args_list]
        assert "sahool.cooperative.revenue_distributed" in subjects
        assert "sahool.notification.send" in subjects

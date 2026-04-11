"""Tests for the cooperative booking approve/reject workflow (Wave 2)."""

import uuid
from datetime import UTC, datetime, timedelta


class FakeRecord(dict):
    """Fake asyncpg Record that supports dict and attribute access."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)


def _make_booking_record(**overrides):
    """Create a fake cooperative_booking DB record."""
    defaults = {
        "id": uuid.uuid4(),
        "tenant_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "cooperative_id": uuid.uuid4(),
        "resource_id": uuid.uuid4(),
        "requested_by": uuid.uuid4(),
        "booking_date": datetime.now(UTC) + timedelta(days=1),
        "duration_hours": 4.0,
        "status": "pending",
        "approved_by": None,
        "approved_at": None,
        "notes": None,
        "created_at": datetime.now(UTC),
        "version": 1,
    }
    defaults.update(overrides)
    return FakeRecord(defaults)


class TestCooperativeBookingWorkflow:
    """Happy-path tests for booking create → approve flow."""

    def test_create_booking_returns_pending(self, db_client, mock_db_pool):
        """POST /api/v1/cooperatives/bookings creates a pending booking."""
        booking = _make_booking_record(status="pending")
        mock_db_pool.fetchrow.return_value = booking

        response = db_client.post(
            "/api/v1/cooperatives/bookings",
            json={
                "cooperative_id": str(uuid.uuid4()),
                "resource_id": str(uuid.uuid4()),
                "booking_date": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "duration_hours": 4.0,
                "notes": "Tractor for field prep",
            },
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["status"] == "pending"
        assert data["version"] == 1
        assert data["duration_hours"] == 4.0

    def test_approve_booking_transitions_to_approved(self, db_client, mock_db_pool):
        """POST /bookings/{id}/approve transitions pending → approved with bumped version."""
        booking_id = uuid.uuid4()
        pending = _make_booking_record(id=booking_id, status="pending", version=1)
        approved = _make_booking_record(
            id=booking_id,
            status="approved",
            version=2,
            approved_by=uuid.uuid4(),
            approved_at=datetime.now(UTC),
            notes="Approved by chairman",
        )
        # 1st fetchrow: _get_booking_or_404, 2nd fetchrow: UPDATE RETURNING
        mock_db_pool.fetchrow.side_effect = [pending, approved]

        response = db_client.post(
            f"/api/v1/cooperatives/bookings/{booking_id}/approve",
            json={"notes": "Approved by chairman", "version": 1},
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["status"] == "approved"
        assert data["version"] == 2
        assert data["approved_at"] is not None

    def test_approve_rejects_non_pending(self, db_client, mock_db_pool):
        """Cannot approve a booking that is already approved."""
        booking_id = uuid.uuid4()
        already_approved = _make_booking_record(id=booking_id, status="approved", version=2)
        mock_db_pool.fetchrow.return_value = already_approved

        response = db_client.post(
            f"/api/v1/cooperatives/bookings/{booking_id}/approve",
            json={},
        )

        assert response.status_code == 409
        detail = response.json()["detail"]
        assert "cannot be approved" in detail["error"]

    def test_reject_booking_transitions_to_rejected(self, db_client, mock_db_pool):
        """POST /bookings/{id}/reject transitions pending → rejected with reason in notes."""
        booking_id = uuid.uuid4()
        pending = _make_booking_record(id=booking_id, status="pending", version=1)
        rejected = _make_booking_record(
            id=booking_id,
            status="rejected",
            version=2,
            approved_by=uuid.uuid4(),
            approved_at=datetime.now(UTC),
            notes="REJECTED: resource under maintenance",
        )
        mock_db_pool.fetchrow.side_effect = [pending, rejected]

        response = db_client.post(
            f"/api/v1/cooperatives/bookings/{booking_id}/reject",
            json={"reason": "resource under maintenance", "version": 1},
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["status"] == "rejected"
        assert "resource under maintenance" in (data.get("notes") or "")

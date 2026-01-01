"""
SAHOOL Field Operations Unit Tests
Tests for field operations logic without I/O
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

# Import from the service
import sys

sys.path.insert(0, "archive/kernel-legacy/kernel/services/field_ops/src")

from main import FieldCreate, FieldUpdate, FieldResponse, OperationCreate


class TestFieldCreateModel:
    """Tests for FieldCreate Pydantic model"""

    def test_valid_field_create(self, test_tenant_id):
        """Valid field data should create model successfully"""
        field = FieldCreate(
            tenant_id=test_tenant_id,
            name="Test Field",
            area_hectares=25.5,
        )

        assert field.tenant_id == test_tenant_id
        assert field.name == "Test Field"
        assert field.area_hectares == 25.5

    def test_field_with_arabic_name(self, test_tenant_id):
        """Field should accept Arabic name"""
        field = FieldCreate(
            tenant_id=test_tenant_id,
            name="Test Field",
            name_ar="حقل اختبار",
            area_hectares=10.0,
        )

        assert field.name_ar == "حقل اختبار"

    def test_field_with_geometry(self, test_tenant_id):
        """Field should accept GeoJSON geometry"""
        geometry = {
            "type": "Polygon",
            "coordinates": [
                [[45.0, 15.0], [45.1, 15.0], [45.1, 15.1], [45.0, 15.1], [45.0, 15.0]]
            ],
        }

        field = FieldCreate(
            tenant_id=test_tenant_id,
            name="Geo Field",
            area_hectares=50.0,
            geometry=geometry,
        )

        assert field.geometry == geometry

    def test_field_area_must_be_positive(self, test_tenant_id):
        """Field area must be greater than 0"""
        with pytest.raises(ValidationError) as exc:
            FieldCreate(
                tenant_id=test_tenant_id,
                name="Invalid Field",
                area_hectares=0,
            )

        assert "greater than" in str(exc.value).lower()

    def test_field_area_cannot_be_negative(self, test_tenant_id):
        """Field area cannot be negative"""
        with pytest.raises(ValidationError):
            FieldCreate(
                tenant_id=test_tenant_id,
                name="Invalid Field",
                area_hectares=-5.0,
            )

    def test_field_requires_tenant_id(self):
        """Field must have tenant_id"""
        with pytest.raises(ValidationError):
            FieldCreate(
                name="No Tenant Field",
                area_hectares=10.0,
            )

    def test_field_requires_name(self, test_tenant_id):
        """Field must have name"""
        with pytest.raises(ValidationError):
            FieldCreate(
                tenant_id=test_tenant_id,
                area_hectares=10.0,
            )


class TestFieldUpdateModel:
    """Tests for FieldUpdate Pydantic model"""

    def test_partial_update_name_only(self):
        """Update should allow partial fields"""
        update = FieldUpdate(name="Updated Name")

        assert update.name == "Updated Name"
        assert update.area_hectares is None

    def test_partial_update_area_only(self):
        """Update should allow just area"""
        update = FieldUpdate(area_hectares=30.0)

        assert update.name is None
        assert update.area_hectares == 30.0

    def test_update_area_must_be_positive_if_provided(self):
        """Update area must be positive if provided"""
        with pytest.raises(ValidationError):
            FieldUpdate(area_hectares=0)

    def test_empty_update_allowed(self):
        """Empty update should be allowed"""
        update = FieldUpdate()

        assert update.name is None
        assert update.area_hectares is None


class TestOperationCreateModel:
    """Tests for OperationCreate Pydantic model"""

    def test_valid_operation_create(self, test_tenant_id):
        """Valid operation data should create model"""
        op = OperationCreate(
            tenant_id=test_tenant_id,
            field_id="field-123",
            operation_type="irrigation",
        )

        assert op.tenant_id == test_tenant_id
        assert op.field_id == "field-123"
        assert op.operation_type == "irrigation"

    def test_operation_with_schedule(self, test_tenant_id):
        """Operation should accept scheduled date"""
        scheduled = datetime.now(timezone.utc).isoformat()

        op = OperationCreate(
            tenant_id=test_tenant_id,
            field_id="field-123",
            operation_type="planting",
            scheduled_date=scheduled,
        )

        assert op.scheduled_date == scheduled

    def test_operation_with_notes(self, test_tenant_id):
        """Operation should accept notes"""
        op = OperationCreate(
            tenant_id=test_tenant_id,
            field_id="field-123",
            operation_type="fertilizing",
            notes="Apply NPK 20-10-10",
        )

        assert op.notes == "Apply NPK 20-10-10"

    def test_operation_requires_field_id(self, test_tenant_id):
        """Operation must have field_id"""
        with pytest.raises(ValidationError):
            OperationCreate(
                tenant_id=test_tenant_id,
                operation_type="irrigation",
            )

    def test_operation_requires_type(self, test_tenant_id):
        """Operation must have operation_type"""
        with pytest.raises(ValidationError):
            OperationCreate(
                tenant_id=test_tenant_id,
                field_id="field-123",
            )


class TestFieldResponse:
    """Tests for FieldResponse model"""

    def test_field_response_from_dict(self, test_tenant_id):
        """FieldResponse should create from dictionary"""
        data = {
            "id": "field-123",
            "tenant_id": test_tenant_id,
            "name": "Response Field",
            "name_ar": None,
            "area_hectares": 25.0,
            "crop_type": "wheat",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        response = FieldResponse(**data)

        assert response.id == "field-123"
        assert response.name == "Response Field"
        assert response.area_hectares == 25.0

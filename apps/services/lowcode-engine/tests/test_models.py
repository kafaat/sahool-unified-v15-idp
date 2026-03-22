"""
Tests for lowcode-engine Pydantic models.
"""

import os
import sys
from datetime import datetime

# Add project root and src path
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
sys.path.insert(0, project_root)
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set test environment variables
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")

# Mock shared.auth (required by main.py) - shared.lowcode is real and available
from unittest.mock import MagicMock

if "shared.auth.dependencies" not in sys.modules:
    mock_auth = MagicMock()
    mock_auth.get_current_user = MagicMock()
    sys.modules["shared.auth.dependencies"] = mock_auth
    sys.modules["shared.auth.models"] = MagicMock()
    sys.modules["shared.auth.models"].User = MagicMock


# ============================================================================
# Import Models After Environment Setup
# ============================================================================

# Import the request/response models from main.py
from main import (
    AISuggestionRequest,
    AISuggestionResponse,
    ComponentResponse,
    DataModelCreateRequest,
    DataModelResponse,
    PageCreateRequest,
    PageRenderResponse,
    PageResponse,
)

# ============================================================================
# Test DataModel Validation
# ============================================================================


class TestDataModelValidation:
    """Tests for DataModel related Pydantic models."""

    def test_data_model_create_request_valid(self):
        """Test creating a valid DataModelCreateRequest."""
        request = DataModelCreateRequest(
            name="TestModel",
            name_ar="نموذج اختباري",
            description="A test model",
            description_ar="نموذج للاختبار",
            fields=[
                {"name": "field1", "field_type": "string", "required": True},
                {"name": "field2", "field_type": "number"},
            ],
            tenant_id="test-tenant",
        )

        assert request.name == "TestModel"
        assert request.name_ar == "نموذج اختباري"
        assert len(request.fields) == 2
        assert request.tenant_id == "test-tenant"

    def test_data_model_create_request_minimal(self):
        """Test creating DataModelCreateRequest with minimal fields."""
        request = DataModelCreateRequest(
            name="Minimal",
            fields=[{"name": "id"}],
            tenant_id="test",
        )

        assert request.name == "Minimal"
        assert request.name_ar is None
        assert request.description is None

    def test_data_model_create_request_empty_name_fails(self):
        """Test that empty name fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            DataModelCreateRequest(
                name="",
                fields=[],
                tenant_id="test",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_data_model_create_request_long_name_fails(self):
        """Test that name exceeding max length fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            DataModelCreateRequest(
                name="x" * 101,  # Exceeds max_length=100
                fields=[],
                tenant_id="test",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_data_model_response_valid(self):
        """Test creating a valid DataModelResponse."""
        now = datetime.utcnow()
        response = DataModelResponse(
            id="model-123",
            name="TestModel",
            name_ar="نموذج",
            description="Test description",
            description_ar="وصف الاختبار",
            fields=[{"name": "field1", "type": "string"}],
            created_at=now,
            updated_at=now,
        )

        assert response.id == "model-123"
        assert response.name == "TestModel"
        assert len(response.fields) == 1

    def test_data_model_response_nullable_fields(self):
        """Test DataModelResponse with nullable fields."""
        now = datetime.utcnow()
        response = DataModelResponse(
            id="model-123",
            name="TestModel",
            name_ar=None,
            description=None,
            description_ar=None,
            fields=[],
            created_at=now,
            updated_at=now,
        )

        assert response.name_ar is None
        assert response.description is None


# ============================================================================
# Test PageDefinition Validation
# ============================================================================


class TestPageDefinitionValidation:
    """Tests for PageDefinition related Pydantic models."""

    def test_page_create_request_valid(self):
        """Test creating a valid PageCreateRequest."""
        request = PageCreateRequest(
            name="Dashboard",
            name_ar="لوحة التحكم",
            description="Main dashboard",
            route="/dashboard",
            blocks=[
                {"component_name": "container", "props": {"padding": "16px"}},
            ],
            tenant_id="test-tenant",
        )

        assert request.name == "Dashboard"
        assert request.route == "/dashboard"
        assert len(request.blocks) == 1

    def test_page_create_request_minimal(self):
        """Test creating PageCreateRequest with minimal fields."""
        request = PageCreateRequest(
            name="MinPage",
            route="/min",
            tenant_id="test",
        )

        assert request.name == "MinPage"
        assert request.blocks == []
        assert request.data_model_id is None

    def test_page_create_request_route_validation_valid(self):
        """Test that valid routes pass validation."""
        valid_routes = [
            "/",
            "/dashboard",
            "/fields/list",
            "/api/v1/test",
            "/a-b-c/d-e-f",
            "/123/456",
        ]

        for route in valid_routes:
            request = PageCreateRequest(
                name="Test",
                route=route,
                tenant_id="test",
            )
            assert request.route == route

    def test_page_create_request_route_validation_invalid(self):
        """Test that invalid routes fail validation."""
        invalid_routes = [
            "no-slash",
            "/UPPERCASE",
            "/space here",
            "/special@char",
            "/under_score",
        ]

        for route in invalid_routes:
            with pytest.raises(ValidationError):
                PageCreateRequest(
                    name="Test",
                    route=route,
                    tenant_id="test",
                )

    def test_page_create_request_empty_name_fails(self):
        """Test that empty page name fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            PageCreateRequest(
                name="",
                route="/test",
                tenant_id="test",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_page_response_valid(self):
        """Test creating a valid PageResponse."""
        now = datetime.utcnow()
        response = PageResponse(
            id="page-123",
            name="Test Page",
            name_ar="صفحة اختبار",
            description="A test page",
            route="/test",
            blocks=[],
            data_model_id=None,
            is_published=False,
            version=1,
            created_at=now,
            updated_at=now,
        )

        assert response.id == "page-123"
        assert response.is_published is False
        assert response.version == 1

    def test_page_response_with_blocks(self):
        """Test PageResponse with blocks."""
        now = datetime.utcnow()
        response = PageResponse(
            id="page-123",
            name="Test Page",
            name_ar=None,
            description=None,
            route="/test",
            blocks=[
                {"id": "block-1", "component_name": "container"},
                {"id": "block-2", "component_name": "text_input"},
            ],
            data_model_id="model-456",
            is_published=True,
            version=3,
            created_at=now,
            updated_at=now,
        )

        assert len(response.blocks) == 2
        assert response.data_model_id == "model-456"
        assert response.version == 3

    def test_page_render_response_valid(self):
        """Test creating a valid PageRenderResponse."""
        response = PageRenderResponse(
            page_id="page-123",
            name="Test Page",
            route="/test",
            rendered_blocks=[
                {"id": "block-1", "component_name": "container", "props": {}},
            ],
            data={"field1": "value1"},
        )

        assert response.page_id == "page-123"
        assert len(response.rendered_blocks) == 1
        assert response.data == {"field1": "value1"}

    def test_page_render_response_null_data(self):
        """Test PageRenderResponse with null data."""
        response = PageRenderResponse(
            page_id="page-123",
            name="Test Page",
            route="/test",
            rendered_blocks=[],
            data=None,
        )

        assert response.data is None


# ============================================================================
# Test FieldDefinition Validation
# ============================================================================


class TestFieldDefinitionValidation:
    """Tests for field definition validation."""

    def test_field_definition_in_request(self):
        """Test field definitions within DataModelCreateRequest."""
        request = DataModelCreateRequest(
            name="FieldTest",
            fields=[
                {
                    "name": "string_field",
                    "name_ar": "حقل نصي",
                    "field_type": "string",
                    "required": True,
                    "default_value": "default",
                },
                {
                    "name": "number_field",
                    "name_ar": "حقل رقمي",
                    "field_type": "number",
                    "required": False,
                    "validation": {"min": 0, "max": 100},
                },
                {
                    "name": "enum_field",
                    "field_type": "enum",
                    "options": ["option1", "option2", "option3"],
                },
            ],
            tenant_id="test",
        )

        assert len(request.fields) == 3
        assert request.fields[0]["name"] == "string_field"
        assert request.fields[0]["required"] is True
        assert request.fields[1]["validation"] == {"min": 0, "max": 100}
        assert request.fields[2]["options"] == ["option1", "option2", "option3"]

    def test_field_definition_all_types(self):
        """Test various field type definitions."""
        field_types = [
            "string",
            "number",
            "boolean",
            "date",
            "datetime",
            "enum",
            "array",
            "object",
            "geojson",
            "image",
            "file",
            "relation",
        ]

        fields = [{"name": f"field_{ft}", "field_type": ft} for ft in field_types]

        request = DataModelCreateRequest(
            name="AllTypesModel",
            fields=fields,
            tenant_id="test",
        )

        assert len(request.fields) == len(field_types)


# ============================================================================
# Test BlockConfig Validation
# ============================================================================


class TestBlockConfigValidation:
    """Tests for block configuration validation."""

    def test_block_config_in_page_request(self):
        """Test block configurations within PageCreateRequest."""
        request = PageCreateRequest(
            name="BlockTest",
            route="/blocks",
            blocks=[
                {
                    "id": "block-1",
                    "component_name": "container",
                    "props": {"padding": "16px", "direction": "column"},
                    "children": [
                        {
                            "id": "block-2",
                            "component_name": "text_input",
                            "props": {"label": "Name"},
                        },
                    ],
                },
            ],
            tenant_id="test",
        )

        assert len(request.blocks) == 1
        block = request.blocks[0]
        assert block["component_name"] == "container"
        assert len(block["children"]) == 1

    def test_block_config_with_conditions(self):
        """Test block configurations with conditions."""
        request = PageCreateRequest(
            name="ConditionalPage",
            route="/conditional",
            blocks=[
                {
                    "component_name": "container",
                    "props": {},
                    "conditions": {"visible": "data.showContainer == true"},
                },
            ],
            tenant_id="test",
        )

        assert request.blocks[0]["conditions"] is not None

    def test_block_config_with_loop(self):
        """Test block configurations with loop directive."""
        request = PageCreateRequest(
            name="LoopPage",
            route="/loop",
            blocks=[
                {
                    "component_name": "field_card",
                    "props": {},
                    "loop": {"items": "data.fields", "item": "field"},
                },
            ],
            tenant_id="test",
        )

        assert request.blocks[0]["loop"] is not None
        assert request.blocks[0]["loop"]["items"] == "data.fields"

    def test_nested_blocks_deep_hierarchy(self):
        """Test deeply nested block hierarchy."""
        request = PageCreateRequest(
            name="DeepNestingPage",
            route="/deep",
            blocks=[
                {
                    "component_name": "container",
                    "children": [
                        {
                            "component_name": "grid",
                            "children": [
                                {
                                    "component_name": "container",
                                    "children": [
                                        {
                                            "component_name": "text_input",
                                            "props": {"label": "Deep Input"},
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
            tenant_id="test",
        )

        # Navigate through nesting
        level1 = request.blocks[0]
        level2 = level1["children"][0]
        level3 = level2["children"][0]
        level4 = level3["children"][0]

        assert level4["component_name"] == "text_input"


# ============================================================================
# Test Component Response Validation
# ============================================================================


class TestComponentResponseValidation:
    """Tests for ComponentResponse model validation."""

    def test_component_response_valid(self):
        """Test creating a valid ComponentResponse."""
        response = ComponentResponse(
            component_id="test_component",
            name="Test Component",
            name_ar="مكون اختباري",
            category="form",
            description="A test component",
            description_ar="مكون للاختبار",
            props=[
                {"name": "label", "type": "string", "default": "Label"},
            ],
            slots=[
                {"name": "content", "title": "Content Slot"},
            ],
            events=[
                {"name": "onClick", "description": "Click event"},
            ],
            is_container=False,
            icon="test-icon",
        )

        assert response.component_id == "test_component"
        assert len(response.props) == 1
        assert len(response.slots) == 1
        assert len(response.events) == 1

    def test_component_response_minimal(self):
        """Test ComponentResponse with minimal fields."""
        response = ComponentResponse(
            component_id="minimal",
            name="Minimal",
            name_ar=None,
            category="form",
            description=None,
            description_ar=None,
            props=[],
            slots=[],
            events=[],
            is_container=False,
        )

        assert response.name_ar is None
        assert response.props == []


# ============================================================================
# Test AI Suggestion Models
# ============================================================================


class TestAISuggestionValidation:
    """Tests for AI suggestion related models."""

    def test_ai_suggestion_request_valid(self):
        """Test creating a valid AISuggestionRequest."""
        request = AISuggestionRequest(
            description="Create a field dashboard with irrigation controls",
            description_ar="إنشاء لوحة حقل مع عناصر تحكم الري",
            context={"crop_type": "wheat", "region": "central"},
        )

        assert len(request.description) >= 10
        assert request.context is not None

    def test_ai_suggestion_request_minimal(self):
        """Test AISuggestionRequest with minimal fields."""
        request = AISuggestionRequest(
            description="A page with maps and charts for analysis",
        )

        assert request.description_ar is None
        assert request.context is None

    def test_ai_suggestion_request_short_description_fails(self):
        """Test that description too short fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            AISuggestionRequest(
                description="short",  # Less than min_length=10
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("description",) for e in errors)

    def test_ai_suggestion_response_valid(self):
        """Test creating a valid AISuggestionResponse."""
        response = AISuggestionResponse(
            suggestions=[
                {
                    "component_id": "field_map",
                    "component_name": "Field Map",
                    "confidence": 0.9,
                },
                {
                    "component_id": "irrigation_scheduler",
                    "component_name": "Irrigation Scheduler",
                    "confidence": 0.8,
                },
            ],
            reasoning="Based on your description, I recommend these components.",
            reasoning_ar="بناءً على وصفك، أوصي بهذه المكونات.",
            confidence=0.85,
        )

        assert len(response.suggestions) == 2
        assert 0 <= response.confidence <= 1

    def test_ai_suggestion_response_empty_suggestions(self):
        """Test AISuggestionResponse with empty suggestions."""
        response = AISuggestionResponse(
            suggestions=[],
            reasoning="No matching components found.",
            reasoning_ar=None,
            confidence=0.0,
        )

        assert len(response.suggestions) == 0
        assert response.confidence == 0.0


# ============================================================================
# Test Model Serialization
# ============================================================================


class TestModelSerialization:
    """Tests for model serialization."""

    def test_data_model_response_json_serialization(self):
        """Test DataModelResponse JSON serialization."""
        now = datetime.utcnow()
        response = DataModelResponse(
            id="model-123",
            name="Test",
            name_ar="اختبار",
            description="Desc",
            description_ar="وصف",
            fields=[{"name": "f1", "type": "string"}],
            created_at=now,
            updated_at=now,
        )

        json_data = response.model_dump_json()
        assert "model-123" in json_data
        assert "Test" in json_data

    def test_page_response_json_serialization(self):
        """Test PageResponse JSON serialization."""
        now = datetime.utcnow()
        response = PageResponse(
            id="page-123",
            name="Test Page",
            name_ar="صفحة",
            description=None,
            route="/test",
            blocks=[{"id": "b1", "component": "container"}],
            data_model_id=None,
            is_published=True,
            version=2,
            created_at=now,
            updated_at=now,
        )

        json_data = response.model_dump_json()
        assert "page-123" in json_data
        assert '"is_published":true' in json_data

    def test_component_response_dict_conversion(self):
        """Test ComponentResponse conversion to dict."""
        response = ComponentResponse(
            component_id="test",
            name="Test",
            name_ar="اختبار",
            category="form",
            description="Desc",
            description_ar="وصف",
            props=[],
            slots=[],
            events=[],
            is_container=False,
        )

        data = response.model_dump()
        assert isinstance(data, dict)
        assert data["component_id"] == "test"
        assert data["is_container"] is False


# ============================================================================
# Test Edge Cases
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_unicode_in_arabic_fields(self):
        """Test Unicode Arabic characters in fields."""
        request = DataModelCreateRequest(
            name="UnicodeTest",
            name_ar="اختبار يونيكود مع أحرف خاصة: ء أ إ آ",
            description="Test Unicode",
            description_ar="اختبار: 1. الأول 2. الثاني 3. الثالث",
            fields=[
                {
                    "name": "arabic_text",
                    "name_ar": "نص عربي متعدد الأسطر\nمع سطر جديد",
                    "field_type": "string",
                },
            ],
            tenant_id="test",
        )

        assert "يونيكود" in request.name_ar
        assert "\n" in request.fields[0]["name_ar"]

    def test_special_characters_in_props(self):
        """Test special characters in block props."""
        request = PageCreateRequest(
            name="SpecialCharsPage",
            route="/special",
            blocks=[
                {
                    "component_name": "text_display",
                    "props": {
                        "text": 'Quote: "Hello" & <World>',
                        "json_string": '{"key": "value"}',
                        "regex": r"^\d+$",
                    },
                },
            ],
            tenant_id="test",
        )

        props = request.blocks[0]["props"]
        assert '"' in props["text"]
        assert "&" in props["text"]

    def test_large_blocks_array(self):
        """Test page with many blocks."""
        blocks = [{"component_name": f"component_{i}", "props": {"index": i}} for i in range(100)]

        request = PageCreateRequest(
            name="ManyBlocksPage",
            route="/many-blocks",
            blocks=blocks,
            tenant_id="test",
        )

        assert len(request.blocks) == 100

    def test_empty_strings_vs_none(self):
        """Test distinction between empty strings and None."""
        # Empty string should be preserved
        request1 = DataModelCreateRequest(
            name="EmptyDesc",
            description="",  # Explicit empty string
            fields=[],
            tenant_id="test",
        )
        assert request1.description == ""

        # None should be preserved
        request2 = DataModelCreateRequest(
            name="NoneDesc",
            description=None,  # Explicit None
            fields=[],
            tenant_id="test",
        )
        assert request2.description is None

    def test_numeric_field_boundaries(self):
        """Test numeric values in field definitions."""
        request = DataModelCreateRequest(
            name="NumericBoundaries",
            fields=[
                {
                    "name": "float_field",
                    "field_type": "number",
                    "validation": {
                        "min": -999999.999,
                        "max": 999999.999,
                    },
                },
                {
                    "name": "int_field",
                    "field_type": "number",
                    "validation": {
                        "min": 0,
                        "max": 2147483647,
                    },
                },
            ],
            tenant_id="test",
        )

        assert request.fields[0]["validation"]["min"] == -999999.999
        assert request.fields[1]["validation"]["max"] == 2147483647

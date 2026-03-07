"""
Shared fixtures for lowcode-engine tests.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

# Add project root to path FIRST
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
sys.path.insert(0, project_root)

# Add src path for importing main module
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set test environment variables before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""


# ============================================================================
# Mock shared.auth module (required because the app imports it)
# ============================================================================

# Mock shared.auth.dependencies
mock_user = MagicMock()
mock_user.id = "test-user-123"
mock_user.username = "testuser"
mock_user.email = "test@sahool.com"
mock_user.tenant_id = "test-tenant"
mock_user.roles = ["admin"]

mock_auth = MagicMock()
mock_auth.get_current_user = MagicMock(return_value=mock_user)

sys.modules["shared.auth.dependencies"] = mock_auth
sys.modules["shared.auth.models"] = MagicMock()
sys.modules["shared.auth.models"].User = MagicMock


# ============================================================================
# Import real shared.lowcode module (it exists and works)
# ============================================================================

from shared.lowcode import (
    AIComponentSuggester,
    BlockConfig,
    ComponentCategory,
    ComponentMaterial,
    DataModel,
    EventDefinition,
    FieldDefinition,
    FieldType,
    LowCodeEngine,
    PageDefinition,
    PropDefinition,
    SlotDefinition,
)

# ============================================================================
# Engine Fixtures
# ============================================================================


@pytest.fixture
def lowcode_engine() -> LowCodeEngine:
    """Provide a real LowCodeEngine instance."""
    return LowCodeEngine(tenant_id="test-tenant")


@pytest.fixture
def ai_suggester(lowcode_engine: LowCodeEngine) -> AIComponentSuggester:
    """Provide an AI suggester instance."""
    return AIComponentSuggester(lowcode_engine)


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_component() -> ComponentMaterial:
    """Provide a sample component."""
    return ComponentMaterial(
        component_id="test_component",
        name="Test Component",
        name_ar="مكون اختباري",
        category=ComponentCategory.FORM,
        description="A test component",
        description_ar="مكون للاختبار",
        props=[
            PropDefinition(name="label", name_ar="التسمية", type="string", default="Default Label"),
            PropDefinition(name="required", name_ar="مطلوب", type="boolean", default=False),
        ],
        slots=[SlotDefinition(name="content", name_ar="المحتوى", description="Content slot")],
        events=[EventDefinition(name="onClick", name_ar="عند النقر", description="Triggered on click")],
        is_container=False,
        icon="test-icon",
    )


@pytest.fixture
def sample_data_model() -> DataModel:
    """Provide a sample data model."""
    return DataModel(
        model_id=str(uuid4()),
        name="TestModel",
        name_ar="نموذج اختباري",
        description="A test data model",
        description_ar="نموذج بيانات للاختبار",
        fields=[
            FieldDefinition(
                name="field1",
                name_ar="حقل 1",
                type=FieldType.STRING,
                required=True,
            ),
            FieldDefinition(
                name="field2",
                name_ar="حقل 2",
                type=FieldType.NUMBER,
                required=False,
            ),
        ],
    )


@pytest.fixture
def sample_field_definition() -> FieldDefinition:
    """Provide a sample field definition."""
    return FieldDefinition(
        name="test_field",
        name_ar="حقل اختباري",
        type=FieldType.STRING,
        required=True,
        default="default",
    )


# ============================================================================
# HTTP Client Fixtures
# ============================================================================


@pytest.fixture
def app():
    """Provide the FastAPI application instance."""
    from main import app as fastapi_app

    return fastapi_app


@pytest.fixture
async def async_client(app) -> AsyncClient:
    """Provide an async HTTP client for testing endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_tenant_id() -> str:
    """Provide a test tenant ID."""
    return "test-tenant-123"


@pytest.fixture
def test_user_id() -> str:
    """Provide a test user ID."""
    return "test-user-123"


# ============================================================================
# Data Fixtures for API Tests
# ============================================================================


@pytest.fixture
def data_model_create_request() -> dict:
    """Provide a valid data model creation request."""
    return {
        "name": "Field",
        "name_ar": "حقل",
        "description": "Agricultural field model",
        "description_ar": "نموذج الحقل الزراعي",
        "fields": [
            {
                "name": "name",
                "name_ar": "الاسم",
                "field_type": "string",
                "required": True,
            },
            {
                "name": "area_ha",
                "name_ar": "المساحة",
                "field_type": "number",
                "required": True,
            },
            {
                "name": "boundary",
                "name_ar": "الحدود",
                "field_type": "geojson",
                "required": False,
            },
        ],
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def page_create_request() -> dict:
    """Provide a valid page creation request."""
    return {
        "name": "Field Dashboard",
        "name_ar": "لوحة الحقل",
        "description": "Dashboard for field management",
        "route": "/fields/dashboard",
        "blocks": [
            {
                "component_name": "container",
                "props": {"padding": "20px"},
                "children": [],
            },
        ],
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def ai_suggestion_request() -> dict:
    """Provide a valid AI suggestion request."""
    return {
        "description": "Create a dashboard showing field map with irrigation controls",
        "description_ar": "إنشاء لوحة تحكم تعرض خريطة الحقل مع عناصر التحكم في الري",
        "context": {"crop_type": "wheat", "region": "central"},
    }

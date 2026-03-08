"""
Tests for LowCodeEngine class.
"""

import os
import sys
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
sys.path.insert(0, project_root)

# Import from shared.lowcode
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
    PluginBase,
    PropDefinition,
    SlotDefinition,
)

# ============================================================================
# Test Component Registration
# ============================================================================


class TestComponentRegistration:
    """Tests for component registration functionality."""

    def test_component_registration_basic(self):
        """Test basic component registration."""
        engine = LowCodeEngine(tenant_id="test")

        component = ComponentMaterial(
            component_id="custom_input",
            name="Custom Input",
            name_ar="حقل مخصص",
            category=ComponentCategory.FORM,
        )

        engine.register_component(component)

        registered = engine.get_component("custom_input")
        assert registered is not None
        assert registered.component_id == "custom_input"
        assert registered.name == "Custom Input"

    def test_component_registration_with_props(self):
        """Test component registration with properties."""
        engine = LowCodeEngine(tenant_id="test")

        component = ComponentMaterial(
            component_id="prop_component",
            name="Prop Component",
            name_ar="مكون بخصائص",
            category=ComponentCategory.FORM,
            props=[
                PropDefinition(
                    name="label",
                    name_ar="التسمية",
                    type="string",
                    default="Default Label",
                    required=True,
                ),
                PropDefinition(
                    name="value",
                    name_ar="القيمة",
                    type="number",
                    default=0,
                ),
            ],
        )

        engine.register_component(component)

        registered = engine.get_component("prop_component")
        assert len(registered.props) == 2
        assert registered.props[0].name == "label"
        assert registered.props[0].required is True
        assert registered.props[1].default == 0

    def test_component_registration_with_events(self):
        """Test component registration with events."""
        engine = LowCodeEngine(tenant_id="test")

        component = ComponentMaterial(
            component_id="event_component",
            name="Event Component",
            name_ar="مكون بأحداث",
            category=ComponentCategory.ACTION,
            events=[
                EventDefinition(
                    name="onClick",
                    name_ar="عند النقر",
                    description="Triggered when clicked",
                ),
                EventDefinition(
                    name="onHover",
                    name_ar="عند التمرير",
                    description="Triggered on mouse hover",
                ),
            ],
        )

        engine.register_component(component)

        registered = engine.get_component("event_component")
        assert len(registered.events) == 2
        assert registered.events[0].name == "onClick"

    def test_component_registration_container(self):
        """Test registration of container component."""
        engine = LowCodeEngine(tenant_id="test")

        component = ComponentMaterial(
            component_id="custom_container",
            name="Custom Container",
            name_ar="حاوية مخصصة",
            category=ComponentCategory.LAYOUT,
            is_container=True,
            slots=[
                SlotDefinition(
                    name="content",
                    name_ar="المحتوى",
                    description="Main content area",
                ),
                SlotDefinition(
                    name="footer",
                    name_ar="التذييل",
                    description="Footer area",
                ),
            ],
        )

        engine.register_component(component)

        registered = engine.get_component("custom_container")
        assert registered.is_container is True
        assert len(registered.slots) == 2

    def test_component_override(self):
        """Test that registering a component with same ID overrides."""
        engine = LowCodeEngine(tenant_id="test")

        # Register first version
        component_v1 = ComponentMaterial(
            component_id="override_test",
            name="Version 1",
            name_ar="الإصدار 1",
            category=ComponentCategory.FORM,
        )
        engine.register_component(component_v1)

        # Register second version with same ID
        component_v2 = ComponentMaterial(
            component_id="override_test",
            name="Version 2",
            name_ar="الإصدار 2",
            category=ComponentCategory.FORM,
        )
        engine.register_component(component_v2)

        registered = engine.get_component("override_test")
        assert registered.name == "Version 2"

    def test_get_nonexistent_component(self):
        """Test getting a component that doesn't exist returns None."""
        engine = LowCodeEngine(tenant_id="test")

        result = engine.get_component("nonexistent")
        assert result is None


# ============================================================================
# Test Component Listing by Category
# ============================================================================


class TestComponentListingByCategory:
    """Tests for listing components by category."""

    def test_list_all_components(self):
        """Test listing all registered components."""
        engine = LowCodeEngine(tenant_id="test")

        components = engine.list_components()

        assert isinstance(components, list)
        assert len(components) > 0  # Built-in components should be registered

    def test_list_components_by_layout_category(self):
        """Test listing components filtered by LAYOUT category."""
        engine = LowCodeEngine(tenant_id="test")

        components = engine.list_components(category=ComponentCategory.LAYOUT)

        assert all(c.category == ComponentCategory.LAYOUT for c in components)
        # Should have container and grid at minimum
        component_ids = [c.component_id for c in components]
        assert "container" in component_ids or "grid" in component_ids

    def test_list_components_by_form_category(self):
        """Test listing components filtered by FORM category."""
        engine = LowCodeEngine(tenant_id="test")

        components = engine.list_components(category=ComponentCategory.FORM)

        assert all(c.category == ComponentCategory.FORM for c in components)

    def test_list_components_by_agriculture_category(self):
        """Test listing components filtered by AGRICULTURE category."""
        engine = LowCodeEngine(tenant_id="test")

        components = engine.list_components(category=ComponentCategory.AGRICULTURE)

        assert all(c.category == ComponentCategory.AGRICULTURE for c in components)

    def test_list_components_by_map_category(self):
        """Test listing components filtered by MAP category."""
        engine = LowCodeEngine(tenant_id="test")

        components = engine.list_components(category=ComponentCategory.MAP)

        assert all(c.category == ComponentCategory.MAP for c in components)
        # field_map should be present
        component_ids = [c.component_id for c in components]
        assert "field_map" in component_ids

    def test_list_components_empty_category(self):
        """Test listing components for a category with no components."""
        engine = LowCodeEngine(tenant_id="test")

        # ACTION category might be empty
        components = engine.list_components(category=ComponentCategory.ACTION)

        assert isinstance(components, list)
        # All returned components should match the category (even if empty)
        for c in components:
            assert c.category == ComponentCategory.ACTION

    def test_list_components_includes_custom(self):
        """Test that custom registered components are included in listing."""
        engine = LowCodeEngine(tenant_id="test")

        # Register a custom component
        custom = ComponentMaterial(
            component_id="my_custom_form",
            name="My Custom Form",
            name_ar="نموذجي المخصص",
            category=ComponentCategory.FORM,
        )
        engine.register_component(custom)

        # List form components
        components = engine.list_components(category=ComponentCategory.FORM)

        component_ids = [c.component_id for c in components]
        assert "my_custom_form" in component_ids


# ============================================================================
# Test Page Rendering
# ============================================================================


class TestPageRendering:
    """Tests for page rendering functionality."""

    def test_create_page_basic(self):
        """Test basic page creation."""
        engine = LowCodeEngine(tenant_id="test")

        page = engine.create_page(
            name="Test Page",
            name_ar="صفحة اختبار",
            path="/test",
        )

        assert page is not None
        assert page.page_id.startswith("page-")
        assert page.name == "Test Page"
        assert page.name_ar == "صفحة اختبار"
        assert page.path == "/test"
        assert page.layout == "default"
        assert page.blocks == []

    def test_create_page_with_layout(self):
        """Test page creation with custom layout."""
        engine = LowCodeEngine(tenant_id="test")

        page = engine.create_page(
            name="Full Width Page",
            name_ar="صفحة بعرض كامل",
            path="/full",
            layout="full-width",
        )

        assert page.layout == "full-width"

    def test_add_block_to_page(self):
        """Test adding a block to a page."""
        engine = LowCodeEngine(tenant_id="test")

        page = engine.create_page(
            name="Block Test",
            name_ar="اختبار الكتل",
            path="/blocks",
        )

        block = engine.add_block_to_page(
            page_id=page.page_id,
            component_id="container",
            props={"padding": "16px"},
        )

        assert block is not None
        assert block.block_id.startswith("block-")
        assert block.component_id == "container"
        assert block.props == {"padding": "16px"}

        # Verify block is in page
        updated_page = engine._pages.get(page.page_id)
        assert len(updated_page.blocks) == 1

    def test_add_nested_block(self):
        """Test adding a nested block to a parent block."""
        engine = LowCodeEngine(tenant_id="test")

        page = engine.create_page(
            name="Nested Test",
            name_ar="اختبار متداخل",
            path="/nested",
        )

        # Add parent block
        parent_block = engine.add_block_to_page(
            page_id=page.page_id,
            component_id="container",
        )

        # Add child block to parent
        child_block = engine.add_block_to_page(
            page_id=page.page_id,
            component_id="text_input",
            props={"label": "Name"},
            parent_block_id=parent_block.block_id,
        )

        assert child_block is not None
        assert len(parent_block.children) == 1
        assert parent_block.children[0].component_id == "text_input"

    def test_add_block_to_nonexistent_page(self):
        """Test adding block to non-existent page returns None."""
        engine = LowCodeEngine(tenant_id="test")

        result = engine.add_block_to_page(
            page_id="nonexistent-page",
            component_id="container",
        )

        assert result is None

    def test_page_to_json(self):
        """Test page serialization to JSON."""
        engine = LowCodeEngine(tenant_id="test")

        page = engine.create_page(
            name="JSON Test",
            name_ar="اختبار JSON",
            path="/json",
        )

        engine.add_block_to_page(
            page_id=page.page_id,
            component_id="container",
            props={"padding": "20px"},
        )

        json_str = page.to_json()

        assert isinstance(json_str, str)
        assert "JSON Test" in json_str
        assert "اختبار JSON" in json_str
        assert "/json" in json_str

    def test_page_updated_at_on_block_add(self):
        """Test that page updated_at is modified when adding block."""
        engine = LowCodeEngine(tenant_id="test")

        page = engine.create_page(
            name="Update Test",
            name_ar="اختبار التحديث",
            path="/update",
        )

        original_updated = page.updated_at

        # Small delay to ensure different timestamp
        import time

        time.sleep(0.01)

        engine.add_block_to_page(
            page_id=page.page_id,
            component_id="container",
        )

        assert page.updated_at > original_updated


# ============================================================================
# Test Data Model Field Types
# ============================================================================


class TestDataModelFieldTypes:
    """Tests for data model field types."""

    def test_register_data_model(self):
        """Test registering a data model."""
        engine = LowCodeEngine(tenant_id="test")

        model = DataModel(
            model_id="field",
            name="Field",
            name_ar="حقل",
            fields=[
                FieldDefinition(
                    name="name",
                    name_ar="الاسم",
                    type=FieldType.STRING,
                    required=True,
                ),
            ],
        )

        engine.register_model(model)

        registered = engine.get_model("field")
        assert registered is not None
        assert registered.name == "Field"

    def test_data_model_all_field_types(self):
        """Test data model with all field types."""
        engine = LowCodeEngine(tenant_id="test")

        model = DataModel(
            model_id="all_types",
            name="All Types Model",
            name_ar="نموذج جميع الأنواع",
            fields=[
                FieldDefinition(name="str_field", name_ar="نص", type=FieldType.STRING),
                FieldDefinition(name="num_field", name_ar="رقم", type=FieldType.NUMBER),
                FieldDefinition(name="bool_field", name_ar="منطقي", type=FieldType.BOOLEAN),
                FieldDefinition(name="date_field", name_ar="تاريخ", type=FieldType.DATE),
                FieldDefinition(name="datetime_field", name_ar="وقت تاريخ", type=FieldType.DATETIME),
                FieldDefinition(name="enum_field", name_ar="قائمة", type=FieldType.ENUM),
                FieldDefinition(name="array_field", name_ar="مصفوفة", type=FieldType.ARRAY),
                FieldDefinition(name="object_field", name_ar="كائن", type=FieldType.OBJECT),
                FieldDefinition(name="geo_field", name_ar="جغرافي", type=FieldType.GEOJSON),
                FieldDefinition(name="img_field", name_ar="صورة", type=FieldType.IMAGE),
                FieldDefinition(name="file_field", name_ar="ملف", type=FieldType.FILE),
                FieldDefinition(name="rel_field", name_ar="علاقة", type=FieldType.RELATION),
            ],
        )

        engine.register_model(model)

        registered = engine.get_model("all_types")
        assert len(registered.fields) == 12

        # Verify each field type
        field_types = {f.name: f.type for f in registered.fields}
        assert field_types["str_field"] == FieldType.STRING
        assert field_types["geo_field"] == FieldType.GEOJSON
        assert field_types["rel_field"] == FieldType.RELATION

    def test_data_model_get_field(self):
        """Test getting a field from a data model."""
        model = DataModel(
            model_id="test_model",
            name="Test",
            name_ar="اختبار",
            fields=[
                FieldDefinition(name="field1", name_ar="حقل 1", type=FieldType.STRING),
                FieldDefinition(name="field2", name_ar="حقل 2", type=FieldType.NUMBER),
            ],
        )

        field = model.get_field("field1")
        assert field is not None
        assert field.name == "field1"
        assert field.type == FieldType.STRING

        # Test non-existent field
        assert model.get_field("nonexistent") is None

    def test_data_model_field_validation(self):
        """Test field definition validation properties."""
        field = FieldDefinition(
            name="validated_field",
            name_ar="حقل موثق",
            type=FieldType.STRING,
            required=True,
            min_length=1,
            max_length=100,
            pattern=r"^[a-zA-Z]+$",
        )

        assert field.required is True
        assert field.min_length == 1
        assert field.max_length == 100
        assert field.pattern == r"^[a-zA-Z]+$"

    def test_data_model_numeric_field_validation(self):
        """Test numeric field validation properties."""
        field = FieldDefinition(
            name="numeric_field",
            name_ar="حقل رقمي",
            type=FieldType.NUMBER,
            min_value=0,
            max_value=100,
        )

        assert field.min_value == 0
        assert field.max_value == 100

    def test_data_model_relation_field(self):
        """Test relation field properties."""
        field = FieldDefinition(
            name="farmer_id",
            name_ar="معرف المزارع",
            type=FieldType.RELATION,
            relation_model="farmer",
            relation_type="many-to-one",
        )

        assert field.relation_model == "farmer"
        assert field.relation_type == "many-to-one"

    def test_get_nonexistent_model(self):
        """Test getting a model that doesn't exist returns None."""
        engine = LowCodeEngine(tenant_id="test")

        result = engine.get_model("nonexistent")
        assert result is None


# ============================================================================
# Test Plugin System
# ============================================================================


class TestPluginSystem:
    """Tests for the plugin system."""

    def test_install_plugin(self):
        """Test installing a plugin."""
        engine = LowCodeEngine(tenant_id="test")

        class TestPlugin(PluginBase):
            @property
            def plugin_id(self) -> str:
                return "test-plugin"

            @property
            def name(self) -> str:
                return "Test Plugin"

            def on_install(self, engine: LowCodeEngine) -> None:
                pass

            def on_activate(self, engine: LowCodeEngine) -> None:
                pass

        plugin = TestPlugin()
        engine.install_plugin(plugin)

        assert "test-plugin" in engine._plugins

    def test_plugin_registers_components(self):
        """Test that plugin can register components."""
        engine = LowCodeEngine(tenant_id="test")

        class ComponentPlugin(PluginBase):
            @property
            def plugin_id(self) -> str:
                return "component-plugin"

            @property
            def name(self) -> str:
                return "Component Plugin"

            def on_install(self, engine: LowCodeEngine) -> None:
                pass

            def on_activate(self, engine: LowCodeEngine) -> None:
                pass

            def register_components(self) -> list[ComponentMaterial]:
                return [
                    ComponentMaterial(
                        component_id="plugin_component",
                        name="Plugin Component",
                        name_ar="مكون إضافة",
                        category=ComponentCategory.FORM,
                    )
                ]

        plugin = ComponentPlugin()
        engine.install_plugin(plugin)

        # Component should be registered
        component = engine.get_component("plugin_component")
        assert component is not None
        assert component.name == "Plugin Component"

    def test_plugin_registers_models(self):
        """Test that plugin can register data models."""
        engine = LowCodeEngine(tenant_id="test")

        class ModelPlugin(PluginBase):
            @property
            def plugin_id(self) -> str:
                return "model-plugin"

            @property
            def name(self) -> str:
                return "Model Plugin"

            def on_install(self, engine: LowCodeEngine) -> None:
                pass

            def on_activate(self, engine: LowCodeEngine) -> None:
                pass

            def register_data_models(self) -> list[DataModel]:
                return [
                    DataModel(
                        model_id="plugin_model",
                        name="Plugin Model",
                        name_ar="نموذج إضافة",
                        fields=[],
                    )
                ]

        plugin = ModelPlugin()
        engine.install_plugin(plugin)

        # Model should be registered
        model = engine.get_model("plugin_model")
        assert model is not None
        assert model.name == "Plugin Model"


# ============================================================================
# Test Event System
# ============================================================================


class TestEventSystem:
    """Tests for the event system."""

    def test_event_handler_registration(self):
        """Test registering an event handler."""
        engine = LowCodeEngine(tenant_id="test")
        events_received = []

        def handler(data):
            events_received.append(data)

        engine.on("component:registered", handler)

        # Register a component to trigger event
        component = ComponentMaterial(
            component_id="event_test",
            name="Event Test",
            name_ar="اختبار الحدث",
            category=ComponentCategory.FORM,
        )
        engine.register_component(component)

        assert len(events_received) == 1
        assert events_received[0].component_id == "event_test"

    def test_multiple_event_handlers(self):
        """Test multiple handlers for same event."""
        engine = LowCodeEngine(tenant_id="test")
        handler1_calls = []
        handler2_calls = []

        engine.on("page:created", lambda d: handler1_calls.append(d))
        engine.on("page:created", lambda d: handler2_calls.append(d))

        engine.create_page(
            name="Multi Handler Test",
            name_ar="اختبار معالجات متعددة",
            path="/multi",
        )

        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1

    def test_event_handler_exception_isolation(self):
        """Test that exception in one handler doesn't affect others."""
        engine = LowCodeEngine(tenant_id="test")
        handler2_called = []

        def failing_handler(data):
            raise ValueError("Test error")

        def successful_handler(data):
            handler2_called.append(data)

        engine.on("model:registered", failing_handler)
        engine.on("model:registered", successful_handler)

        # Register model - should not raise
        model = DataModel(
            model_id="exception_test",
            name="Exception Test",
            name_ar="اختبار استثناء",
            fields=[],
        )
        engine.register_model(model)

        # Second handler should still be called
        assert len(handler2_called) == 1


# ============================================================================
# Test Schema Export
# ============================================================================


class TestSchemaExport:
    """Tests for schema export functionality."""

    def test_export_schema_basic(self):
        """Test basic schema export."""
        engine = LowCodeEngine(tenant_id="test-export")

        schema = engine.export_schema()

        assert schema["version"] == "1.0.0"
        assert schema["tenant_id"] == "test-export"
        assert "components" in schema
        assert "models" in schema
        assert "pages" in schema
        assert "plugins" in schema

    def test_export_schema_with_custom_content(self):
        """Test schema export includes custom content."""
        engine = LowCodeEngine(tenant_id="test-export")

        # Add custom component
        engine.register_component(
            ComponentMaterial(
                component_id="export_component",
                name="Export Test Component",
                name_ar="مكون تصدير",
                category=ComponentCategory.FORM,
            )
        )

        # Add custom model
        engine.register_model(
            DataModel(
                model_id="export_model",
                name="Export Test Model",
                name_ar="نموذج تصدير",
                fields=[
                    FieldDefinition(name="field1", name_ar="حقل", type=FieldType.STRING),
                ],
            )
        )

        # Create page
        engine.create_page(
            name="Export Test Page",
            name_ar="صفحة تصدير",
            path="/export",
        )

        schema = engine.export_schema()

        # Check components include custom
        component_ids = [c["componentId"] for c in schema["components"]]
        assert "export_component" in component_ids

        # Check models include custom
        model_ids = [m["modelId"] for m in schema["models"]]
        assert "export_model" in model_ids

        # Check pages include custom
        page_paths = [p["path"] for p in schema["pages"]]
        assert "/export" in page_paths


# ============================================================================
# Test AI Component Suggester
# ============================================================================


class TestAIComponentSuggester:
    """Tests for the AI component suggester."""

    def test_suggester_initialization(self):
        """Test AI suggester initialization."""
        engine = LowCodeEngine(tenant_id="test")
        suggester = AIComponentSuggester(engine)

        assert suggester.engine is engine

    def test_suggest_components_for_model(self):
        """Test suggesting components for a data model."""
        engine = LowCodeEngine(tenant_id="test")
        suggester = AIComponentSuggester(engine)

        model = DataModel(
            model_id="suggestion_test",
            name="Suggestion Test",
            name_ar="اختبار الاقتراحات",
            fields=[
                FieldDefinition(name="name", name_ar="الاسم", type=FieldType.STRING),
                FieldDefinition(name="area", name_ar="المساحة", type=FieldType.NUMBER),
                FieldDefinition(name="date", name_ar="التاريخ", type=FieldType.DATE),
                FieldDefinition(name="boundary", name_ar="الحدود", type=FieldType.GEOJSON),
            ],
        )

        suggestions = suggester.suggest_components_for_model(model)

        assert isinstance(suggestions, list)
        # Should have suggestions for each field
        assert len(suggestions) >= 1

    def test_suggest_layout_for_fields(self):
        """Test suggesting layout for fields."""
        engine = LowCodeEngine(tenant_id="test")
        suggester = AIComponentSuggester(engine)

        fields = [FieldDefinition(name=f"field_{i}", name_ar=f"حقل {i}", type=FieldType.STRING) for i in range(5)]

        layout = suggester.suggest_layout_for_fields(fields)

        assert layout["layout"] == "grid"
        assert layout["columns"] == 2
        assert "groups" in layout

    def test_suggest_layout_grouping(self):
        """Test that fields are grouped correctly."""
        engine = LowCodeEngine(tenant_id="test")
        suggester = AIComponentSuggester(engine)

        # Create 7 fields - should result in 3 groups (3+3+1)
        fields = [FieldDefinition(name=f"field_{i}", name_ar=f"حقل {i}", type=FieldType.STRING) for i in range(7)]

        layout = suggester.suggest_layout_for_fields(fields)

        # Should have multiple groups
        assert len(layout["groups"]) >= 2


# ============================================================================
# Test Built-in Components
# ============================================================================


class TestBuiltinComponents:
    """Tests for built-in components."""

    def test_container_component_exists(self):
        """Test container component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("container")
        assert component is not None
        assert component.is_container is True
        assert component.category == ComponentCategory.LAYOUT

    def test_grid_component_exists(self):
        """Test grid component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("grid")
        assert component is not None
        assert component.is_container is True

    def test_text_input_component_exists(self):
        """Test text input component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("text_input")
        assert component is not None
        assert component.category == ComponentCategory.FORM

    def test_field_map_component_exists(self):
        """Test field map component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("field_map")
        assert component is not None
        assert component.category == ComponentCategory.MAP
        assert "field_id" in [p.name for p in component.props]

    def test_crop_selector_component_exists(self):
        """Test crop selector component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("crop_selector")
        assert component is not None
        assert component.category == ComponentCategory.AGRICULTURE

    def test_irrigation_scheduler_component_exists(self):
        """Test irrigation scheduler component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("irrigation_scheduler")
        assert component is not None

    def test_sensor_display_component_exists(self):
        """Test sensor display component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("sensor_display")
        assert component is not None

    def test_ai_advisor_component_exists(self):
        """Test AI advisor component is registered."""
        engine = LowCodeEngine(tenant_id="test")

        component = engine.get_component("ai_advisor")
        assert component is not None
        assert component.category == ComponentCategory.AI


# ============================================================================
# Test Component Material Methods
# ============================================================================


class TestComponentMaterialMethods:
    """Tests for ComponentMaterial methods."""

    def test_component_to_dict(self):
        """Test ComponentMaterial to_dict method."""
        component = ComponentMaterial(
            component_id="test_dict",
            name="Test Dict",
            name_ar="اختبار قاموس",
            category=ComponentCategory.FORM,
            props=[
                PropDefinition(name="prop1", name_ar="خاصية", type="string", default="val"),
            ],
        )

        result = component.to_dict()

        assert result["componentId"] == "test_dict"
        assert result["name"] == "Test Dict"
        assert result["nameAr"] == "اختبار قاموس"
        assert result["category"] == "form"
        assert result["isContainer"] is False
        assert len(result["props"]) == 1
        assert result["props"][0]["name"] == "prop1"

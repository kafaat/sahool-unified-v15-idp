"""
SAHOOL Low-Code Engine
======================
محرك سهول للتطوير منخفض الكود

Enterprise-grade low-code platform for agricultural applications.
Inspired by Alibaba LowCode Engine and NocoBase.

Architecture:
- Microkernel design with plugin system
- Data model-driven (not form-centric)
- Material protocol for component interoperability
- AI-powered suggestions and automation

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Callable

# ═══════════════════════════════════════════════════════════════════════════════
# Core Types & Enums
# ═══════════════════════════════════════════════════════════════════════════════


class ComponentCategory(StrEnum):
    """Component categories for the material system."""

    LAYOUT = "layout"  # تخطيط - Grid, Flex, Container
    FORM = "form"  # نموذج - Input, Select, Date
    DATA = "data"  # بيانات - Table, List, Cards
    CHART = "chart"  # رسم بياني - Line, Bar, Pie
    MAP = "map"  # خريطة - Field Map, Satellite
    AGRICULTURE = "agriculture"  # زراعي - Crop, Field, Sensor
    AI = "ai"  # ذكاء اصطناعي - Advisor, Predictor
    ACTION = "action"  # إجراء - Button, Link, Modal


class DataSourceType(StrEnum):
    """Data source types."""

    DATABASE = "database"  # قاعدة بيانات
    API = "api"  # واجهة برمجية
    STATIC = "static"  # ثابت
    COMPUTED = "computed"  # محسوب
    AI_GENERATED = "ai_generated"  # مولد بالذكاء الاصطناعي


class FieldType(StrEnum):
    """Field types for data models."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    ARRAY = "array"
    OBJECT = "object"
    GEOJSON = "geojson"  # For field boundaries
    IMAGE = "image"
    FILE = "file"
    RELATION = "relation"  # Foreign key


# ═══════════════════════════════════════════════════════════════════════════════
# Material Protocol (Component System)
# نظام المواد (البروتوكول المكوني)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PropDefinition:
    """Property definition for a component."""

    name: str
    name_ar: str
    type: str  # string, number, boolean, enum, etc.
    default: Any = None
    required: bool = False
    description: str = ""
    description_ar: str = ""
    enum_values: list[str] | None = None
    setter: str | None = None  # Custom setter component


@dataclass
class SlotDefinition:
    """Slot definition for nested components."""

    name: str
    name_ar: str
    description: str = ""
    allowed_components: list[str] = field(default_factory=list)
    max_items: int | None = None


@dataclass
class EventDefinition:
    """Event definition for component interactions."""

    name: str
    name_ar: str
    description: str = ""
    payload_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentMaterial:
    """
    Component Material Definition (following Alibaba's Material Protocol).
    تعريف مادة المكون (وفقاً لبروتوكول المواد)

    This defines how a component appears and behaves in the low-code editor.
    """

    # Identity
    component_id: str
    name: str
    name_ar: str
    version: str = "1.0.0"

    # Classification
    category: ComponentCategory = ComponentCategory.FORM
    tags: list[str] = field(default_factory=list)

    # Visual
    icon: str = "📦"
    thumbnail: str | None = None
    description: str = ""
    description_ar: str = ""

    # Schema
    props: list[PropDefinition] = field(default_factory=list)
    slots: list[SlotDefinition] = field(default_factory=list)
    events: list[EventDefinition] = field(default_factory=list)

    # Behavior
    is_container: bool = False
    is_draggable: bool = True
    is_resizable: bool = True
    default_size: dict[str, Any] = field(default_factory=lambda: {"width": "100%", "height": "auto"})

    # Data binding
    supports_data_binding: bool = True
    data_schema: dict[str, Any] = field(default_factory=dict)

    # Metadata
    author: str = "SAHOOL"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "componentId": self.component_id,
            "name": self.name,
            "nameAr": self.name_ar,
            "category": self.category.value,
            "icon": self.icon,
            "props": [{"name": p.name, "type": p.type, "default": p.default} for p in self.props],
            "isContainer": self.is_container,
            "supportsDataBinding": self.supports_data_binding,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Data Model System (NocoBase-inspired)
# نظام نموذج البيانات
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class FieldDefinition:
    """Field definition in a data model."""

    name: str
    name_ar: str
    type: FieldType
    required: bool = False
    unique: bool = False
    indexed: bool = False
    default: Any = None
    description: str = ""

    # Validation
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None  # Regex

    # Relations
    relation_model: str | None = None
    relation_type: str | None = None  # one-to-one, one-to-many, many-to-many

    # Display
    display_format: str | None = None
    hidden: bool = False
    read_only: bool = False


@dataclass
class DataModel:
    """
    Data Model Definition (NocoBase-inspired).
    تعريف نموذج البيانات

    Represents a collection/table structure.
    """

    model_id: str
    name: str
    name_ar: str
    description: str = ""
    description_ar: str = ""

    # Schema
    fields: list[FieldDefinition] = field(default_factory=list)
    primary_key: str = "id"

    # Behavior
    timestamps: bool = True  # created_at, updated_at
    soft_delete: bool = False
    auditable: bool = False

    # Display
    title_field: str | None = None
    icon: str = "📄"
    color: str = "#3B82F6"

    # Permissions
    permissions: dict[str, list[str]] = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_field(self, name: str) -> FieldDefinition | None:
        return next((f for f in self.fields if f.name == name), None)


# ═══════════════════════════════════════════════════════════════════════════════
# Page & Block System
# نظام الصفحات والكتل
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class BlockConfig:
    """Configuration for a page block."""

    block_id: str
    component_id: str
    props: dict[str, Any] = field(default_factory=dict)
    styles: dict[str, Any] = field(default_factory=dict)
    data_source: dict[str, Any] | None = None
    children: list[BlockConfig] = field(default_factory=list)
    events: dict[str, str] = field(default_factory=dict)  # event_name -> action_id
    position: dict[str, Any] = field(default_factory=lambda: {"x": 0, "y": 0})
    size: dict[str, Any] = field(default_factory=lambda: {"width": "100%", "height": "auto"})
    visible: bool = True
    condition: str | None = None  # Visibility condition expression


@dataclass
class PageDefinition:
    """
    Page Definition.
    تعريف الصفحة

    A page is a composition of blocks.
    """

    page_id: str
    name: str
    name_ar: str
    path: str  # URL path

    # Content
    blocks: list[BlockConfig] = field(default_factory=list)

    # Layout
    layout: str = "default"  # default, full-width, sidebar
    background: str = "#F5F5F5"

    # Permissions
    requires_auth: bool = False
    allowed_roles: list[str] = field(default_factory=list)

    # SEO
    title: str | None = None
    description: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None

    def to_json(self) -> str:
        """Export page as JSON schema."""
        return json.dumps(
            {
                "pageId": self.page_id,
                "name": self.name,
                "nameAr": self.name_ar,
                "path": self.path,
                "layout": self.layout,
                "blocks": self._blocks_to_dict(self.blocks),
            },
            ensure_ascii=False,
            indent=2,
        )

    def _blocks_to_dict(self, blocks: list[BlockConfig]) -> list[dict]:
        result = []
        for block in blocks:
            result.append(
                {
                    "blockId": block.block_id,
                    "componentId": block.component_id,
                    "props": block.props,
                    "children": self._blocks_to_dict(block.children),
                }
            )
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# Plugin System (WordPress-style, NocoBase-inspired)
# نظام الإضافات
# ═══════════════════════════════════════════════════════════════════════════════


class PluginBase(ABC):
    """
    Base class for Low-Code plugins.
    الفئة الأساسية لإضافات Low-Code
    """

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique plugin identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    def name_ar(self) -> str:
        """Plugin name in Arabic."""
        return self.name

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return ""

    @abstractmethod
    def on_install(self, engine: LowCodeEngine) -> None:
        """Called when plugin is installed."""
        pass

    @abstractmethod
    def on_activate(self, engine: LowCodeEngine) -> None:
        """Called when plugin is activated."""
        pass

    def on_deactivate(self, engine: LowCodeEngine) -> None:
        """Called when plugin is deactivated."""
        pass

    def register_components(self) -> list[ComponentMaterial]:
        """Register custom components."""
        return []

    def register_data_models(self) -> list[DataModel]:
        """Register data models."""
        return []

    def register_pages(self) -> list[PageDefinition]:
        """Register pages."""
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# Low-Code Engine Core
# نواة محرك Low-Code
# ═══════════════════════════════════════════════════════════════════════════════


class LowCodeEngine:
    """
    SAHOOL Low-Code Engine.
    محرك سهول للتطوير منخفض الكود

    Microkernel architecture with plugin system.
    Based on Alibaba LowCode Engine and NocoBase patterns.

    Example:
        engine = LowCodeEngine(tenant_id="farm_001")

        # Register agricultural components
        engine.register_component(field_map_component)
        engine.register_component(crop_selector_component)

        # Create a data model
        field_model = DataModel(
            model_id="field",
            name="Field",
            name_ar="حقل",
            fields=[
                FieldDefinition(name="name", name_ar="الاسم", type=FieldType.STRING),
                FieldDefinition(name="area_ha", name_ar="المساحة", type=FieldType.NUMBER),
                FieldDefinition(name="boundary", name_ar="الحدود", type=FieldType.GEOJSON),
            ]
        )
        engine.register_model(field_model)

        # Create a page
        page = engine.create_page(
            name="Field Dashboard",
            name_ar="لوحة الحقول",
            path="/fields"
        )
    """

    def __init__(self, tenant_id: str = "sahool"):
        self.tenant_id = tenant_id

        # Registries
        self._components: dict[str, ComponentMaterial] = {}
        self._models: dict[str, DataModel] = {}
        self._pages: dict[str, PageDefinition] = {}
        self._plugins: dict[str, PluginBase] = {}
        self._actions: dict[str, Callable] = {}

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

        # Initialize built-in components
        self._register_builtin_components()

    def _register_builtin_components(self) -> None:
        """Register built-in components."""
        # Layout components
        self.register_component(
            ComponentMaterial(
                component_id="container",
                name="Container",
                name_ar="حاوية",
                category=ComponentCategory.LAYOUT,
                icon="📦",
                is_container=True,
                props=[
                    PropDefinition(name="padding", name_ar="الحشو", type="string", default="16px"),
                    PropDefinition(
                        name="direction",
                        name_ar="الاتجاه",
                        type="enum",
                        enum_values=["row", "column"],
                        default="column",
                    ),
                ],
            )
        )

        self.register_component(
            ComponentMaterial(
                component_id="grid",
                name="Grid",
                name_ar="شبكة",
                category=ComponentCategory.LAYOUT,
                icon="⊞",
                is_container=True,
                props=[
                    PropDefinition(name="columns", name_ar="الأعمدة", type="number", default=2),
                    PropDefinition(name="gap", name_ar="الفجوة", type="string", default="16px"),
                ],
            )
        )

        # Form components
        self.register_component(
            ComponentMaterial(
                component_id="text_input",
                name="Text Input",
                name_ar="حقل نصي",
                category=ComponentCategory.FORM,
                icon="✏️",
                props=[
                    PropDefinition(name="label", name_ar="التسمية", type="string"),
                    PropDefinition(name="placeholder", name_ar="نص توضيحي", type="string"),
                    PropDefinition(name="required", name_ar="مطلوب", type="boolean", default=False),
                ],
                events=[
                    EventDefinition(name="onChange", name_ar="عند التغيير"),
                    EventDefinition(name="onBlur", name_ar="عند فقد التركيز"),
                ],
            )
        )

        self.register_component(
            ComponentMaterial(
                component_id="number_input",
                name="Number Input",
                name_ar="حقل رقمي",
                category=ComponentCategory.FORM,
                icon="🔢",
                props=[
                    PropDefinition(name="label", name_ar="التسمية", type="string"),
                    PropDefinition(name="min", name_ar="الحد الأدنى", type="number"),
                    PropDefinition(name="max", name_ar="الحد الأقصى", type="number"),
                    PropDefinition(name="unit", name_ar="الوحدة", type="string"),
                ],
            )
        )

        self.register_component(
            ComponentMaterial(
                component_id="select",
                name="Select",
                name_ar="قائمة منسدلة",
                category=ComponentCategory.FORM,
                icon="📋",
                props=[
                    PropDefinition(name="label", name_ar="التسمية", type="string"),
                    PropDefinition(name="options", name_ar="الخيارات", type="array"),
                    PropDefinition(name="multiple", name_ar="متعدد", type="boolean", default=False),
                ],
            )
        )

        self.register_component(
            ComponentMaterial(
                component_id="date_picker",
                name="Date Picker",
                name_ar="منتقي التاريخ",
                category=ComponentCategory.FORM,
                icon="📅",
                props=[
                    PropDefinition(name="label", name_ar="التسمية", type="string"),
                    PropDefinition(name="format", name_ar="التنسيق", type="string", default="YYYY-MM-DD"),
                    PropDefinition(name="use_hijri", name_ar="استخدام الهجري", type="boolean", default=False),
                ],
            )
        )

        # Data components
        self.register_component(
            ComponentMaterial(
                component_id="data_table",
                name="Data Table",
                name_ar="جدول البيانات",
                category=ComponentCategory.DATA,
                icon="📊",
                props=[
                    PropDefinition(name="columns", name_ar="الأعمدة", type="array"),
                    PropDefinition(name="pagination", name_ar="ترقيم الصفحات", type="boolean", default=True),
                    PropDefinition(name="page_size", name_ar="حجم الصفحة", type="number", default=10),
                    PropDefinition(name="sortable", name_ar="قابل للفرز", type="boolean", default=True),
                ],
                supports_data_binding=True,
            )
        )

        # Chart components
        self.register_component(
            ComponentMaterial(
                component_id="line_chart",
                name="Line Chart",
                name_ar="رسم بياني خطي",
                category=ComponentCategory.CHART,
                icon="📈",
                props=[
                    PropDefinition(name="title", name_ar="العنوان", type="string"),
                    PropDefinition(name="x_axis", name_ar="المحور السيني", type="string"),
                    PropDefinition(name="y_axis", name_ar="المحور الصادي", type="string"),
                ],
            )
        )

        # Agricultural components
        self._register_agricultural_components()

    def _register_agricultural_components(self) -> None:
        """Register SAHOOL-specific agricultural components."""

        # Field Map
        self.register_component(
            ComponentMaterial(
                component_id="field_map",
                name="Field Map",
                name_ar="خريطة الحقل",
                category=ComponentCategory.MAP,
                icon="🗺️",
                description="Interactive map showing field boundaries and health",
                description_ar="خريطة تفاعلية تظهر حدود الحقل وصحته",
                props=[
                    PropDefinition(name="field_id", name_ar="معرف الحقل", type="string"),
                    PropDefinition(name="show_ndvi", name_ar="إظهار NDVI", type="boolean", default=True),
                    PropDefinition(
                        name="show_sensors",
                        name_ar="إظهار المستشعرات",
                        type="boolean",
                        default=True,
                    ),
                    PropDefinition(
                        name="satellite_layer",
                        name_ar="طبقة الأقمار",
                        type="enum",
                        enum_values=["satellite", "ndvi", "moisture"],
                        default="satellite",
                    ),
                ],
                events=[
                    EventDefinition(name="onFieldClick", name_ar="عند النقر على الحقل"),
                    EventDefinition(name="onZoneSelect", name_ar="عند اختيار منطقة"),
                ],
            )
        )

        # Crop Selector
        self.register_component(
            ComponentMaterial(
                component_id="crop_selector",
                name="Crop Selector",
                name_ar="منتقي المحصول",
                category=ComponentCategory.AGRICULTURE,
                icon="🌾",
                props=[
                    PropDefinition(name="label", name_ar="التسمية", type="string"),
                    PropDefinition(name="region", name_ar="المنطقة", type="string"),
                    PropDefinition(
                        name="season",
                        name_ar="الموسم",
                        type="enum",
                        enum_values=["winter", "summer", "spring"],
                        default="winter",
                    ),
                    PropDefinition(
                        name="show_recommendations",
                        name_ar="إظهار التوصيات",
                        type="boolean",
                        default=True,
                    ),
                ],
            )
        )

        # Irrigation Scheduler
        self.register_component(
            ComponentMaterial(
                component_id="irrigation_scheduler",
                name="Irrigation Scheduler",
                name_ar="جدولة الري",
                category=ComponentCategory.AGRICULTURE,
                icon="💧",
                props=[
                    PropDefinition(name="field_id", name_ar="معرف الحقل", type="string"),
                    PropDefinition(name="auto_schedule", name_ar="جدولة تلقائية", type="boolean", default=False),
                    PropDefinition(name="show_forecast", name_ar="إظهار التوقعات", type="boolean", default=True),
                ],
                events=[
                    EventDefinition(name="onScheduleCreate", name_ar="عند إنشاء جدول"),
                    EventDefinition(name="onIrrigationStart", name_ar="عند بدء الري"),
                ],
            )
        )

        # Sensor Display
        self.register_component(
            ComponentMaterial(
                component_id="sensor_display",
                name="Sensor Display",
                name_ar="عرض المستشعر",
                category=ComponentCategory.AGRICULTURE,
                icon="📡",
                props=[
                    PropDefinition(name="sensor_id", name_ar="معرف المستشعر", type="string"),
                    PropDefinition(
                        name="sensor_type",
                        name_ar="نوع المستشعر",
                        type="enum",
                        enum_values=["soil_moisture", "temperature", "humidity", "ec"],
                    ),
                    PropDefinition(name="show_history", name_ar="إظهار السجل", type="boolean", default=True),
                    PropDefinition(name="alert_threshold", name_ar="حد التنبيه", type="number"),
                ],
            )
        )

        # Crop Health Card
        self.register_component(
            ComponentMaterial(
                component_id="crop_health_card",
                name="Crop Health Card",
                name_ar="بطاقة صحة المحصول",
                category=ComponentCategory.AGRICULTURE,
                icon="🌱",
                props=[
                    PropDefinition(name="field_id", name_ar="معرف الحقل", type="string"),
                    PropDefinition(name="show_score", name_ar="إظهار الدرجة", type="boolean", default=True),
                    PropDefinition(
                        name="show_recommendations",
                        name_ar="إظهار التوصيات",
                        type="boolean",
                        default=True,
                    ),
                ],
            )
        )

        # AI Advisor Widget
        self.register_component(
            ComponentMaterial(
                component_id="ai_advisor",
                name="AI Advisor",
                name_ar="مستشار الذكاء الاصطناعي",
                category=ComponentCategory.AI,
                icon="🤖",
                description="AI-powered agricultural advisor",
                description_ar="مستشار زراعي مدعوم بالذكاء الاصطناعي",
                props=[
                    PropDefinition(name="context", name_ar="السياق", type="object"),
                    PropDefinition(
                        name="language",
                        name_ar="اللغة",
                        type="enum",
                        enum_values=["ar", "en"],
                        default="ar",
                    ),
                    PropDefinition(
                        name="agent_type",
                        name_ar="نوع الوكيل",
                        type="enum",
                        enum_values=["research", "advisor", "planner"],
                        default="advisor",
                    ),
                ],
                events=[
                    EventDefinition(name="onRecommendation", name_ar="عند التوصية"),
                    EventDefinition(name="onQuery", name_ar="عند الاستعلام"),
                ],
            )
        )

    def register_component(self, component: ComponentMaterial) -> None:
        """Register a component in the material system."""
        self._components[component.component_id] = component
        self._emit("component:registered", component)

    def get_component(self, component_id: str) -> ComponentMaterial | None:
        """Get component by ID."""
        return self._components.get(component_id)

    def list_components(self, category: ComponentCategory | None = None) -> list[ComponentMaterial]:
        """List all components, optionally filtered by category."""
        components = list(self._components.values())
        if category:
            components = [c for c in components if c.category == category]
        return components

    def register_model(self, model: DataModel) -> None:
        """Register a data model."""
        self._models[model.model_id] = model
        self._emit("model:registered", model)

    def get_model(self, model_id: str) -> DataModel | None:
        """Get data model by ID."""
        return self._models.get(model_id)

    def create_page(
        self,
        name: str,
        name_ar: str,
        path: str,
        layout: str = "default",
    ) -> PageDefinition:
        """Create a new page."""
        page = PageDefinition(
            page_id=f"page-{uuid.uuid4().hex[:8]}",
            name=name,
            name_ar=name_ar,
            path=path,
            layout=layout,
        )
        self._pages[page.page_id] = page
        self._emit("page:created", page)
        return page

    def add_block_to_page(
        self,
        page_id: str,
        component_id: str,
        props: dict[str, Any] | None = None,
        parent_block_id: str | None = None,
    ) -> BlockConfig | None:
        """Add a block to a page."""
        page = self._pages.get(page_id)
        if not page:
            return None

        block = BlockConfig(
            block_id=f"block-{uuid.uuid4().hex[:8]}",
            component_id=component_id,
            props=props or {},
        )

        if parent_block_id:
            # Find parent and add as child
            parent = self._find_block(page.blocks, parent_block_id)
            if parent:
                parent.children.append(block)
        else:
            page.blocks.append(block)

        page.updated_at = datetime.now(UTC)
        self._emit("block:added", {"page_id": page_id, "block": block})
        return block

    def _find_block(self, blocks: list[BlockConfig], block_id: str) -> BlockConfig | None:
        """Recursively find a block by ID."""
        for block in blocks:
            if block.block_id == block_id:
                return block
            found = self._find_block(block.children, block_id)
            if found:
                return found
        return None

    def install_plugin(self, plugin: PluginBase) -> None:
        """Install a plugin."""
        plugin.on_install(self)
        self._plugins[plugin.plugin_id] = plugin

        # Register plugin's components, models, and pages
        for component in plugin.register_components():
            self.register_component(component)

        for model in plugin.register_data_models():
            self.register_model(model)

        for page in plugin.register_pages():
            self._pages[page.page_id] = page

        plugin.on_activate(self)
        self._emit("plugin:installed", plugin)

    def _emit(self, event: str, data: Any) -> None:
        """Emit an event to handlers."""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                pass

    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def export_schema(self) -> dict[str, Any]:
        """Export the entire schema as JSON."""
        return {
            "version": "1.0.0",
            "tenant_id": self.tenant_id,
            "components": [c.to_dict() for c in self._components.values()],
            "models": [
                {
                    "modelId": m.model_id,
                    "name": m.name,
                    "nameAr": m.name_ar,
                    "fields": [{"name": f.name, "type": f.type.value} for f in m.fields],
                }
                for m in self._models.values()
            ],
            "pages": [
                {
                    "pageId": p.page_id,
                    "name": p.name,
                    "path": p.path,
                    "blocksCount": len(p.blocks),
                }
                for p in self._pages.values()
            ],
            "plugins": list(self._plugins.keys()),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AI-Powered Features
# ميزات مدعومة بالذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════════


class AIComponentSuggester:
    """
    AI-powered component suggester.
    مقترح المكونات المدعوم بالذكاء الاصطناعي

    Suggests components based on context and data model.
    """

    def __init__(self, engine: LowCodeEngine):
        self.engine = engine

    def suggest_components_for_model(
        self,
        model: DataModel,
        purpose: str = "form",
    ) -> list[dict[str, Any]]:
        """
        Suggest components for a data model.
        اقتراح مكونات لنموذج البيانات
        """
        suggestions = []

        for field in model.fields:
            suggestion = self._suggest_for_field(field, purpose)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def _suggest_for_field(
        self,
        field: FieldDefinition,
        purpose: str,
    ) -> dict[str, Any] | None:
        """Suggest a component for a field."""
        # Map field types to components
        type_mapping = {
            FieldType.STRING: "text_input",
            FieldType.NUMBER: "number_input",
            FieldType.BOOLEAN: "checkbox",
            FieldType.DATE: "date_picker",
            FieldType.DATETIME: "date_picker",
            FieldType.ENUM: "select",
            FieldType.GEOJSON: "field_map",
            FieldType.IMAGE: "image_upload",
        }

        component_id = type_mapping.get(field.type)
        if not component_id:
            return None

        component = self.engine.get_component(component_id)
        if not component:
            return None

        return {
            "field": field.name,
            "field_ar": field.name_ar,
            "component_id": component_id,
            "component_name": component.name,
            "component_name_ar": component.name_ar,
            "suggested_props": {
                "label": field.name_ar,
                "required": field.required,
            },
            "confidence": 0.9,
        }

    def suggest_layout_for_fields(
        self,
        fields: list[FieldDefinition],
    ) -> dict[str, Any]:
        """
        Suggest a layout structure for fields.
        اقتراح هيكل تخطيط للحقول
        """
        # Simple heuristic: group related fields
        groups = []
        current_group = []

        for i, field in enumerate(fields):
            current_group.append(field)

            # Start new group every 3 fields or on type change
            if len(current_group) >= 3:
                groups.append(current_group)
                current_group = []

        if current_group:
            groups.append(current_group)

        return {
            "layout": "grid",
            "columns": 2,
            "groups": [
                {
                    "fields": [f.name for f in group],
                    "columns": min(len(group), 2),
                }
                for group in groups
            ],
        }

# shared/lowcode - Low-Code Workflow Automation Engine

وحدة سهول للتطوير منخفض الكود

Enterprise-grade low-code platform for building agricultural management applications without manual frontend development. Inspired by Alibaba LowCode Engine and NocoBase. Uses a microkernel architecture with a plugin system, data model-driven page composition, and a material protocol for component interoperability.

## File Structure

```
shared/lowcode/
├── __init__.py   # Package exports
└── engine.py     # All types, models, engine, and AI suggester
```

## Architecture

```
LowCodeEngine (microkernel)
├── Component Registry      # ComponentMaterial definitions
├── Data Model Registry     # DataModel + FieldDefinition schemas
├── Page Registry           # PageDefinition + BlockConfig compositions
├── Plugin System           # PluginBase lifecycle hooks
└── Event Bus               # on(event, handler) / _emit(event, data)
```

## Key Components

### Enums

| Enum | Values | Purpose |
|------|--------|---------|
| `ComponentCategory` | layout, form, data, chart, map, agriculture, ai, action | UI component grouping |
| `DataSourceType` | database, api, static, computed, ai_generated | Data binding source |
| `FieldType` | string, number, boolean, date, datetime, enum, array, object, geojson, image, file, relation | Data model field types |

### Core Classes

**`ComponentMaterial`** - Component definition following Alibaba's Material Protocol:
- Identity: `component_id`, `name`, `name_ar`, `version`
- Schema: `props` (PropDefinition list), `slots`, `events`
- Behavior: `is_container`, `is_draggable`, `is_resizable`, `supports_data_binding`

**`DataModel`** - NocoBase-inspired collection schema:
- Fields: list of `FieldDefinition` with validation rules and relation support
- Behavior flags: `timestamps`, `soft_delete`, `auditable`
- Role-based `permissions` dict

**`PageDefinition`** - Composable page from nested `BlockConfig` blocks:
- Export as JSON schema via `to_json()`
- Role-based access with `requires_auth`, `allowed_roles`

**`LowCodeEngine`** - Main orchestrator:
- `register_component(material)` - Add to component registry
- `register_model(model)` - Add data model
- `create_page(name, name_ar, path)` - Scaffold new page
- `add_block_to_page(page_id, component_id, props, parent_block_id)` - Compose UI
- `install_plugin(plugin)` - Install and activate plugin
- `export_schema()` - Full JSON export for renderer
- `on(event, handler)` - Subscribe to engine events

**`AIComponentSuggester`** - Maps data model fields to appropriate components:
- `suggest_components_for_model(model, purpose)` - Auto-suggests form/display components
- `suggest_layout_for_fields(fields)` - Grid grouping heuristic

### Built-in Agricultural Components

| Component ID | Category | Description |
|-------------|----------|-------------|
| `field_map` | map | Interactive field boundary map with NDVI/sensor layers |
| `crop_selector` | agriculture | Crop picker with regional and seasonal filtering |
| `irrigation_scheduler` | agriculture | Irrigation scheduling with auto-schedule option |
| `sensor_display` | agriculture | IoT sensor readings with alert thresholds |
| `crop_health_card` | agriculture | NDVI-based crop health summary |
| `ai_advisor` | ai | Embedded AI advisory widget (ar/en, research/advisor/planner modes) |

Standard components also included: `container`, `grid`, `text_input`, `number_input`, `select`, `date_picker`, `data_table`, `line_chart`.

## Usage Example

```python
from shared.lowcode import LowCodeEngine, DataModel, FieldDefinition, FieldType

engine = LowCodeEngine(tenant_id="farm_001")

# Define a data model
field_model = DataModel(
    model_id="field",
    name="Field",
    name_ar="حقل",
    fields=[
        FieldDefinition(name="name", name_ar="الاسم", type=FieldType.STRING, required=True),
        FieldDefinition(name="area_ha", name_ar="المساحة (هكتار)", type=FieldType.NUMBER),
        FieldDefinition(name="boundary", name_ar="الحدود", type=FieldType.GEOJSON),
        FieldDefinition(name="crop_type", name_ar="نوع المحصول", type=FieldType.ENUM),
    ],
    timestamps=True,
    auditable=True,
)
engine.register_model(field_model)

# Build a page
page = engine.create_page("Field Dashboard", "لوحة الحقول", path="/fields")
engine.add_block_to_page(page.page_id, "field_map", props={"show_ndvi": True})
engine.add_block_to_page(page.page_id, "crop_health_card")

# AI component suggestions for the model
from shared.lowcode import AIComponentSuggester
suggester = AIComponentSuggester(engine)
suggestions = suggester.suggest_components_for_model(field_model, purpose="form")
# [{"field": "name", "component_id": "text_input", "confidence": 0.9}, ...]

# Export for frontend renderer
schema = engine.export_schema()
```

## Plugin System

```python
from shared.lowcode import PluginBase, LowCodeEngine

class IrrigationPlugin(PluginBase):
    @property
    def plugin_id(self): return "irrigation"

    @property
    def name(self): return "Smart Irrigation"

    def on_install(self, engine): pass
    def on_activate(self, engine): pass

    def register_components(self):
        return [...]   # Custom ComponentMaterial list

engine.install_plugin(IrrigationPlugin())
```

## Notes

- The `lowcode-engine` service (port 8132) exposes this module via REST API.
- Pages are exported as JSON and rendered by the web/admin frontend via a compatible renderer.
- The `date_picker` component supports Hijri (Islamic) calendar via `use_hijri: true`.
- The `geojson` field type auto-suggests the `field_map` component, enabling zero-config map integration.

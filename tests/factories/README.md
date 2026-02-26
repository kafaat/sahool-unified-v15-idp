# Test Data Factories

Reusable factory functions and dataclasses that generate consistent, realistic test data for the SAHOOL platform. Factories eliminate boilerplate in test files and ensure test data matches production domain shapes.

## Usage

```python
from tests.factories.user_factory import make_user, make_admin_user
from tests.factories.field_factory import make_field, make_field_with_geometry
from tests.factories.farm_factory import make_farm, FarmData
from tests.factories.crop_factory import make_crop, CropData

# Create with defaults
user = make_user()
field = make_field()

# Override specific attributes
admin = make_user(roles=["admin", "super_admin"])
wheat_field = make_field(crop_type="wheat", area_hectares=20.5)
```

## Factory Files

### `user_factory.py`

Generates `TestUser` dataclass instances:

- `make_user(**overrides)` — standard farmer user
- `make_admin_user(**overrides)` — admin role user
- Default values: unique UUID ID, unique email, tenant ID, roles `["farmer"]`, Arabic name
- `.to_dict()` method for API payload conversion

### `field_factory.py`

Generates `TestField` dataclass instances:

- `make_field(**overrides)` — field with GeoJSON polygon geometry
- `make_field_with_geometry(**overrides)` — field with realistic Saudi Arabia coordinates
- Default values: unique ID, 10 ha area, wheat crop type, Arabic and English names
- `.to_dict()` — full representation including timestamps
- `.to_create_dict()` — creation payload (no ID or timestamps)

### `farm_factory.py`

Generates `FarmData` dataclass instances:

- `make_farm(**overrides)` — farm with Riyadh location defaults
- `make_large_farm(**overrides)` — 500+ ha enterprise farm
- Default values: Saudi Arabia coordinates (24.7136°N, 46.6753°E), 100 ha, active status
- Arabic and English bilingual name fields

### `crop_factory.py`

Generates `CropData` dataclass instances:

- `make_crop(**overrides)` — wheat crop in vegetative stage
- `make_crop_batch(n, **overrides)` — list of N crop records
- Default values: Sakha 95 variety, 120-day harvest timeline, 10 ha, 5 t/ha yield
- Growth stages: `vegetative`, `tillering`, `heading`, `ripening`, `harvest`

## Conventions

- All factory functions return typed dataclasses with a `.to_dict()` method.
- UUIDs are generated with `uuid4()` to ensure uniqueness per test.
- Timestamps use `datetime.now(UTC)` for timezone-aware values.
- Arabic translations are included for all bilingual fields.
- Override any field via `**overrides` keyword arguments.

## Adding New Factories

Create a new `{domain}_factory.py` file in this directory following the pattern:

```python
@dataclass
class ThingData:
    id: str = field(default_factory=lambda: f"thing-{uuid4().hex[:8]}")
    # ... other fields ...

def make_thing(**overrides) -> ThingData:
    defaults = { ... }
    defaults.update(overrides)
    return ThingData(**defaults)
```

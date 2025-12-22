# SAHOOL Development Tools

## Overview

أدوات التطوير والفحص والمحاكاة لمنصة سهول.

---

## Structure

```
tools/
├── arch/                   # Architecture tools
│   └── check_imports.py    # Import dependency checker
│
├── compliance/             # Compliance tools
│   └── generate_checklist.py  # Compliance checklist generator
│
├── env/                    # Environment tools
│   ├── check_env_drift.py  # Environment drift detection
│   ├── migrate.sh          # Environment migration
│   ├── required_env.json   # Required env variables
│   ├── scan_env_usage.py   # Scan env usage
│   └── validate_env.py     # Validate env files
│
├── events/                 # Event tools
│   └── generate_catalog.py # Event catalog generator
│
├── release/                # Release tools
│   ├── release_v15_3_2.sh  # Release script
│   └── smoke_test.sh       # Smoke test runner
│
├── security/               # Security tools
│   └── certs/              # Certificate storage
│
└── sensor-simulator/       # IoT simulator
    ├── requirements.txt
    └── simulator.py        # Sensor data simulator
```

---

## Tools

### arch/check_imports.py

Check import dependencies and detect violations.

```bash
# Check all imports
python tools/arch/check_imports.py

# Check specific service
python tools/arch/check_imports.py apps/services/field-service

# With JSON output
python tools/arch/check_imports.py --format json
```

**Checks:**
- Circular dependencies
- Cross-layer imports
- Forbidden imports

---

### compliance/generate_checklist.py

Generate compliance checklists.

```bash
# Generate all checklists
python tools/compliance/generate_checklist.py

# Specific standard
python tools/compliance/generate_checklist.py --standard gdpr
python tools/compliance/generate_checklist.py --standard soc2
```

**Output:**
- GDPR compliance checklist
- SOC2 compliance checklist
- Security audit checklist

---

### env/

Environment management tools:

#### check_env_drift.py

```bash
# Check for environment drift
python tools/env/check_env_drift.py

# Compare environments
python tools/env/check_env_drift.py --compare staging production
```

#### validate_env.py

```bash
# Validate environment file
python tools/env/validate_env.py config/prod.env

# Against required list
python tools/env/validate_env.py --required tools/env/required_env.json
```

#### scan_env_usage.py

```bash
# Scan env usage in code
python tools/env/scan_env_usage.py

# Find unused variables
python tools/env/scan_env_usage.py --unused
```

#### migrate.sh

```bash
# Migrate environment
./tools/env/migrate.sh --from local --to staging
```

---

### events/generate_catalog.py

Generate event catalog documentation.

```bash
# Generate catalog
python tools/events/generate_catalog.py

# Output to file
python tools/events/generate_catalog.py --output docs/EVENT_CATALOG.md

# JSON format
python tools/events/generate_catalog.py --format json
```

**Output:**
- Event types list
- Event schemas
- Publisher/consumer mapping

---

### release/

Release management tools:

#### release_v15_3_2.sh

```bash
# Run release process
./tools/release/release_v15_3_2.sh

# Dry run
./tools/release/release_v15_3_2.sh --dry-run
```

#### smoke_test.sh

```bash
# Run smoke tests
./tools/release/smoke_test.sh

# Specific environment
./tools/release/smoke_test.sh --env staging

# With timeout
./tools/release/smoke_test.sh --timeout 60
```

---

### sensor-simulator/

IoT sensor data simulator.

```bash
# Install dependencies
pip install -r tools/sensor-simulator/requirements.txt

# Run simulator
python tools/sensor-simulator/simulator.py

# With options
python tools/sensor-simulator/simulator.py \
  --mqtt-host localhost \
  --interval 5 \
  --devices 10
```

**Simulates:**
- Soil moisture sensors
- Temperature sensors
- Humidity sensors
- Weather stations

**Configuration:**
```python
# In simulator.py
DEVICES = [
    {"type": "soil_moisture", "field_id": "field-1"},
    {"type": "temperature", "field_id": "field-1"},
    {"type": "weather", "location": "25.0,45.0"}
]
```

---

## Usage Examples

### Pre-release Checks

```bash
# 1. Check architecture
python tools/arch/check_imports.py

# 2. Validate environments
python tools/env/validate_env.py config/prod.env

# 3. Run smoke tests
./tools/release/smoke_test.sh
```

### Development

```bash
# 1. Start sensor simulator
python tools/sensor-simulator/simulator.py --interval 1

# 2. Check env usage
python tools/env/scan_env_usage.py
```

### Documentation

```bash
# Generate event catalog
python tools/events/generate_catalog.py --output docs/EVENTS.md

# Generate compliance checklist
python tools/compliance/generate_checklist.py
```

---

## Related Documentation

- [Scripts](../scripts/README.md)
- [Tests](../tests/README.md)
- [Infrastructure](../infra/README.md)

---

<p align="center">
  <sub>SAHOOL Development Tools</sub>
  <br>
  <sub>December 2025</sub>
</p>

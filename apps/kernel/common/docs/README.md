# SAHOOL API Documentation Generator

# مولد توثيق واجهة برمجة تطبيقات سحول

Automatically generate comprehensive API documentation for the SAHOOL platform from FastAPI services.

يقوم تلقائيًا بإنشاء توثيق شامل لواجهة برمجة التطبيقات لمنصة سحول من خدمات FastAPI.

## Features | المميزات

- **Automatic Service Scanning**: Scans all FastAPI services and extracts endpoints
- **OpenAPI 3.0 Specification**: Generates standard OpenAPI spec
- **Markdown Documentation**: Creates detailed docs in English and Arabic
- **Postman Collection**: Generates ready-to-use Postman collection
- **Multi-language Support**: Documentation in both English and Arabic
- **Categorized APIs**: Automatically categorizes endpoints by functionality

## Installation | التثبيت

The generator is part of the SAHOOL kernel and requires no additional installation.

```bash
# Ensure you're in the project root
cd /home/user/sahool-unified-v15-idp
```

## Usage | الاستخدام

### Basic Usage

Generate all documentation:

```bash
python apps/kernel/common/docs/api_docs_generator.py
```

This will:

1. Scan all services in `apps/services/`
2. Generate OpenAPI spec at `docs/api/openapi.json`
3. Generate Markdown documentation in `docs/api/`
4. Generate Postman collection at `docs/api/SAHOOL.postman_collection.json`

### Advanced Usage

```bash
# Specify custom directories
python apps/kernel/common/docs/api_docs_generator.py \
  --services-dir /path/to/services \
  --output-dir /path/to/output

# Skip service scanning (faster for regeneration)
python apps/kernel/common/docs/api_docs_generator.py --skip-scan
```

### Arguments

| Argument         | Description                | Default         |
| ---------------- | -------------------------- | --------------- |
| `--services-dir` | Path to services directory | `apps/services` |
| `--output-dir`   | Path to output directory   | `docs/api`      |
| `--skip-scan`    | Skip scanning services     | `False`         |

## Output Files | ملفات الإخراج

After running the generator, you'll find:

### Markdown Documentation

| File                | Description                           |
| ------------------- | ------------------------------------- |
| `README.md`         | Main API documentation index          |
| `authentication.md` | Authentication and authorization docs |
| `fields.md`         | Field management API docs             |
| `sensors.md`        | IoT and sensor API docs               |
| `weather.md`        | Weather API docs                      |
| `ai.md`             | AI and analysis API docs              |

### API Specifications

| File                             | Description               |
| -------------------------------- | ------------------------- |
| `openapi.json`                   | OpenAPI 3.0 specification |
| `SAHOOL.postman_collection.json` | Postman collection        |

## Programmatic Usage | الاستخدام البرمجي

You can also use the generator in your Python code:

```python
from apps.kernel.common.docs.api_docs_generator import APIDocsGenerator

# Initialize generator
generator = APIDocsGenerator(
    services_dir="/path/to/services",
    output_dir="/path/to/output"
)

# Scan services
generator.scan_all_services()

# Generate documentation
generator.generate_openapi_spec()
generator.generate_markdown_docs()
generator.generate_postman_collection()

# Access scanned data
print(f"Found {len(generator.services)} services")
for category, endpoints in generator.endpoints_by_category.items():
    print(f"{category}: {len(endpoints)} endpoints")
```

## API Categories | تصنيفات API

The generator automatically categorizes endpoints:

- **Authentication**: Login, registration, token management
- **Field Management**: Field CRUD, profitability analysis
- **Sensors**: IoT gateway, virtual sensors
- **Weather**: Current conditions, forecasts, alerts
- **Satellite**: NDVI, vegetation analysis
- **AI/Analysis**: AI advisor, crop health, yield prediction
- **Notifications**: Alerts and notifications
- **Crop Health**: Disease detection, health monitoring
- **Irrigation**: Irrigation optimization
- **Equipment**: Equipment management
- **Inventory**: Inventory tracking
- **Billing**: Billing and payments
- **Tasks**: Task management
- **Misc**: Other endpoints

## Customization | التخصيص

### Adding New Categories

Edit `APICategory` enum in `api_docs_generator.py`:

```python
class APICategory(str, Enum):
    # ... existing categories ...
    MY_CATEGORY = "my_category"
```

Update `_determine_category` method to classify endpoints:

```python
def _determine_category(self, service_name: str, path: str) -> APICategory:
    # ... existing logic ...
    if 'my-keyword' in service_lower:
        return APICategory.MY_CATEGORY
```

### Custom Documentation Templates

Override the markdown generation methods:

```python
class MyDocsGenerator(APIDocsGenerator):
    def _generate_main_readme(self):
        # Custom README generation
        pass
```

## Integration with CI/CD | التكامل مع CI/CD

Add to your CI/CD pipeline:

```yaml
# .github/workflows/docs.yml
name: Generate API Docs

on:
  push:
    branches: [main]
    paths:
      - "apps/services/*/src/main.py"

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate Documentation
        run: |
          python apps/kernel/common/docs/api_docs_generator.py
      - name: Commit Documentation
        run: |
          git config --global user.name 'API Docs Bot'
          git config --global user.email 'bot@sahool.com'
          git add docs/api/
          git commit -m "Update API documentation"
          git push
```

## Development | التطوير

### Running Tests

```bash
# Test the generator
python -m pytest apps/kernel/common/docs/tests/

# Manual testing
python apps/kernel/common/docs/api_docs_generator.py
```

### Adding Features

1. Add new methods to `APIDocsGenerator` class
2. Update the `main()` function to call new methods
3. Test with sample services
4. Update this README

## Troubleshooting | استكشاف الأخطاء

### No services found

**Problem**: "Scanned 0 services"

**Solution**:

- Check `--services-dir` path is correct
- Ensure services have `src/main.py` files
- Verify FastAPI app is defined in main.py

### Missing endpoints

**Problem**: Some endpoints not appearing in docs

**Solution**:

- Ensure endpoints use `@app.get`, `@app.post`, etc. decorators
- Check endpoint paths are quoted strings
- Verify docstrings are properly formatted

### Arabic text not showing

**Problem**: Arabic descriptions not appearing

**Solution**:

- Ensure source files are UTF-8 encoded
- Add Arabic descriptions in docstrings
- Use Arabic characters in service descriptions

## Examples | أمثلة

### Example 1: Generate docs for specific service

```python
from pathlib import Path
from api_docs_generator import APIDocsGenerator

generator = APIDocsGenerator()
service = generator._scan_service(
    "weather-service",
    Path("apps/services/weather-service/src/main.py")
)

print(f"Service: {service.title}")
print(f"Endpoints: {len(service.endpoints)}")
for endpoint in service.endpoints:
    print(f"  {endpoint.method} {endpoint.path}")
```

### Example 2: Export to different formats

```python
from api_docs_generator import APIDocsGenerator

generator = APIDocsGenerator()
generator.scan_all_services()

# Generate OpenAPI spec
openapi_path = generator.generate_openapi_spec("custom_openapi.json")

# Generate Postman collection
postman_path = generator.generate_postman_collection("custom.postman_collection.json")

print(f"OpenAPI: {openapi_path}")
print(f"Postman: {postman_path}")
```

## Contributing | المساهمة

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License | الترخيص

Copyright © 2024 SAHOOL Platform

---

**Author**: SAHOOL Development Team
**Version**: 1.0.0
**Last Updated**: 2026-01-02

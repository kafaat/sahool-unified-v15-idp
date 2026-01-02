"""
SAHOOL API Documentation Generator
مولد توثيق واجهة برمجة تطبيقات سحول

This tool automatically generates API documentation from FastAPI applications.
يقوم هذا البرنامج بإنشاء توثيق API تلقائيًا من تطبيقات FastAPI.

Features:
- Scan endpoints from FastAPI apps
- Generate OpenAPI 3.0 specifications
- Generate Markdown documentation (English + Arabic)
- Generate Postman collections
- Support for multiple services

Usage:
    from api_docs_generator import APIDocsGenerator

    generator = APIDocsGenerator(services_dir="/path/to/services")
    generator.scan_all_services()
    generator.generate_openapi_spec()
    generator.generate_markdown_docs()
    generator.generate_postman_collection()
"""

import os
import sys
import json
import re
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import inspect


@dataclass
class Parameter:
    """API parameter definition"""
    name: str
    type: str
    required: bool = False
    description: str = ""
    description_ar: str = ""
    default: Any = None
    location: str = "query"  # query, path, header, body


@dataclass
class RequestBody:
    """Request body schema"""
    schema: Dict[str, Any]
    required: bool = True
    description: str = ""
    description_ar: str = ""
    content_type: str = "application/json"
    example: Optional[Dict[str, Any]] = None


@dataclass
class Response:
    """API response definition"""
    status_code: int
    description: str = ""
    description_ar: str = ""
    schema: Optional[Dict[str, Any]] = None
    example: Optional[Dict[str, Any]] = None


@dataclass
class Endpoint:
    """API endpoint definition"""
    path: str
    method: str
    summary: str = ""
    summary_ar: str = ""
    description: str = ""
    description_ar: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: List[Response] = field(default_factory=list)
    auth_required: bool = True
    deprecated: bool = False
    service_name: str = ""
    service_port: int = 0


@dataclass
class Service:
    """Service definition"""
    name: str
    title: str
    description: str = ""
    description_ar: str = ""
    version: str = "1.0.0"
    port: int = 8000
    base_path: str = ""
    endpoints: List[Endpoint] = field(default_factory=list)


class APICategory(str, Enum):
    """API categories for documentation"""
    AUTHENTICATION = "authentication"
    FIELD_MANAGEMENT = "field_management"
    SENSORS = "sensors"
    WEATHER = "weather"
    AI_ANALYSIS = "ai_analysis"
    NOTIFICATIONS = "notifications"
    CROP_HEALTH = "crop_health"
    IRRIGATION = "irrigation"
    SATELLITE = "satellite"
    MARKET = "market"
    TASKS = "tasks"
    EQUIPMENT = "equipment"
    INVENTORY = "inventory"
    BILLING = "billing"
    MISC = "misc"


class APIDocsGenerator:
    """
    API Documentation Generator for SAHOOL Platform
    مولد توثيق API لمنصة سحول
    """

    def __init__(self, services_dir: str = None, output_dir: str = None):
        """
        Initialize the documentation generator

        Args:
            services_dir: Path to services directory
            output_dir: Path to output documentation
        """
        if services_dir is None:
            # Default to apps/services
            project_root = Path(__file__).parent.parent.parent.parent.parent
            services_dir = project_root / "apps" / "services"

        if output_dir is None:
            # Default to docs/api
            project_root = Path(__file__).parent.parent.parent.parent.parent
            output_dir = project_root / "docs" / "api"

        self.services_dir = Path(services_dir)
        self.output_dir = Path(output_dir)
        self.services: Dict[str, Service] = {}
        self.endpoints_by_category: Dict[APICategory, List[Endpoint]] = {
            category: [] for category in APICategory
        }

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_all_services(self):
        """
        Scan all services in the services directory
        فحص جميع الخدمات في دليل الخدمات
        """
        print(f"🔍 Scanning services in {self.services_dir}")

        if not self.services_dir.exists():
            print(f"❌ Services directory not found: {self.services_dir}")
            return

        # Find all service directories
        service_dirs = [d for d in self.services_dir.iterdir() if d.is_dir()]

        for service_dir in service_dirs:
            service_name = service_dir.name
            main_py = service_dir / "src" / "main.py"

            if main_py.exists():
                print(f"  📦 Found service: {service_name}")
                try:
                    service = self._scan_service(service_name, main_py)
                    if service:
                        self.services[service_name] = service
                        self._categorize_endpoints(service)
                except Exception as e:
                    print(f"  ⚠️  Error scanning {service_name}: {e}")

        print(f"\n✅ Scanned {len(self.services)} services")

    def _scan_service(self, service_name: str, main_file: Path) -> Optional[Service]:
        """
        Scan a single service and extract API endpoints

        Args:
            service_name: Name of the service
            main_file: Path to main.py file

        Returns:
            Service object with endpoints
        """
        try:
            # Read the main.py file
            content = main_file.read_text()

            # Extract service metadata
            title = self._extract_title(content, service_name)
            description = self._extract_description(content)
            description_ar = self._extract_description_ar(content)
            version = self._extract_version(content)
            port = self._extract_port(content)

            service = Service(
                name=service_name,
                title=title,
                description=description,
                description_ar=description_ar,
                version=version,
                port=port
            )

            # Extract endpoints
            endpoints = self._extract_endpoints(content, service_name, port)
            service.endpoints = endpoints

            return service

        except Exception as e:
            print(f"    Error reading {main_file}: {e}")
            return None

    def _extract_title(self, content: str, default: str) -> str:
        """Extract service title from FastAPI app definition"""
        match = re.search(r'title\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return default.replace('-', ' ').title()

    def _extract_description(self, content: str) -> str:
        """Extract service description"""
        match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if match:
            return match.group(1)

        # Try to get from docstring
        match = re.search(r'"""([^"]+)"""', content)
        if match:
            lines = match.group(1).strip().split('\n')
            if lines:
                return lines[0].strip()
        return ""

    def _extract_description_ar(self, content: str) -> str:
        """Extract Arabic description from docstring"""
        match = re.search(r'"""[^"]*\n([^\n]*[\u0600-\u06FF][^\n]*)', content)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_version(self, content: str) -> str:
        """Extract version from FastAPI app"""
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else "1.0.0"

    def _extract_port(self, content: str) -> int:
        """Extract port number from main file"""
        # Look for Port: comment
        match = re.search(r'Port:\s*(\d+)', content)
        if match:
            return int(match.group(1))

        # Look for uvicorn.run port
        match = re.search(r'port\s*=\s*(?:int\(os\.getenv\(["\']PORT["\']\s*,\s*["\']?(\d+)["\']?\)\)|(\d+))', content)
        if match:
            return int(match.group(1) or match.group(2))
        return 8000

    def _extract_endpoints(self, content: str, service_name: str, port: int) -> List[Endpoint]:
        """
        Extract all endpoints from the content

        Args:
            content: Source code content
            service_name: Name of the service
            port: Service port number

        Returns:
            List of Endpoint objects
        """
        endpoints = []

        # Pattern to match FastAPI route decorators
        pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'

        for match in re.finditer(pattern, content):
            method = match.group(1).upper()
            path = match.group(2)

            # Get the function that follows
            func_start = match.end()
            func_match = re.search(r'(?:async\s+)?def\s+(\w+)\s*\([^)]*\):', content[func_start:])

            if func_match:
                func_name = func_match.group(1)
                func_def_start = func_start + func_match.start()

                # Extract function docstring
                docstring_match = re.search(
                    r'def\s+\w+[^:]+:\s*"""([^"]+)"""',
                    content[func_def_start:func_def_start + 500],
                    re.DOTALL
                )

                summary = ""
                summary_ar = ""
                description = ""
                description_ar = ""

                if docstring_match:
                    docstring = docstring_match.group(1).strip()
                    lines = [l.strip() for l in docstring.split('\n') if l.strip()]

                    if lines:
                        # First line is summary
                        summary = lines[0]

                        # Look for Arabic summary
                        for line in lines:
                            if self._contains_arabic(line):
                                summary_ar = line
                                break

                        # Rest is description
                        if len(lines) > 1:
                            description = '\n'.join(lines[1:])

                # Extract parameters
                parameters = self._extract_parameters(content[func_def_start:func_def_start + 1000])

                # Create endpoint
                endpoint = Endpoint(
                    path=path,
                    method=method,
                    summary=summary or func_name.replace('_', ' ').title(),
                    summary_ar=summary_ar,
                    description=description,
                    description_ar=description_ar,
                    tags=[service_name],
                    parameters=parameters,
                    service_name=service_name,
                    service_port=port
                )

                endpoints.append(endpoint)

        return endpoints

    def _extract_parameters(self, func_content: str) -> List[Parameter]:
        """Extract parameters from function definition"""
        parameters = []

        # Look for Query parameters
        query_pattern = r'(\w+)\s*:\s*\w+\s*=\s*Query\s*\([^)]*\)'
        for match in re.finditer(query_pattern, func_content):
            param_name = match.group(1)
            param_def = match.group(0)

            # Extract description
            desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', param_def)
            description = desc_match.group(1) if desc_match else ""

            # Check if required (has ... or no default)
            required = '...' in param_def

            parameters.append(Parameter(
                name=param_name,
                type="string",
                required=required,
                description=description,
                location="query"
            ))

        # Look for Path parameters
        path_pattern = r'(\w+)\s*:\s*(\w+)\s*(?:,|\))'
        for match in re.finditer(path_pattern, func_content):
            param_name = match.group(1)
            if param_name not in ['request', 'response', 'background_tasks', 'db']:
                param_type = match.group(2)
                parameters.append(Parameter(
                    name=param_name,
                    type=param_type.lower(),
                    required=True,
                    location="path"
                ))

        return parameters

    def _contains_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        return bool(re.search(r'[\u0600-\u06FF]', text))

    def _categorize_endpoints(self, service: Service):
        """Categorize endpoints by their purpose"""
        for endpoint in service.endpoints:
            category = self._determine_category(service.name, endpoint.path)
            self.endpoints_by_category[category].append(endpoint)

    def _determine_category(self, service_name: str, path: str) -> APICategory:
        """Determine the category of an endpoint"""
        service_lower = service_name.lower()
        path_lower = path.lower()

        # Authentication
        if 'auth' in service_lower or 'login' in path_lower or 'register' in path_lower:
            return APICategory.AUTHENTICATION

        # Field Management
        if 'field' in service_lower and 'chat' not in service_lower:
            return APICategory.FIELD_MANAGEMENT

        # Sensors/IoT
        if 'iot' in service_lower or 'sensor' in service_lower or 'virtual-sensor' in service_lower:
            return APICategory.SENSORS

        # Weather
        if 'weather' in service_lower:
            return APICategory.WEATHER

        # Satellite
        if 'satellite' in service_lower or 'ndvi' in service_lower or 'vegetation' in service_lower:
            return APICategory.SATELLITE

        # AI/Analysis
        if any(x in service_lower for x in ['ai', 'advisor', 'intelligence', 'crop-health-ai']):
            return APICategory.AI_ANALYSIS

        # Notifications
        if 'notification' in service_lower or 'alert' in service_lower:
            return APICategory.NOTIFICATIONS

        # Crop Health
        if 'crop' in service_lower and 'health' in service_lower:
            return APICategory.CROP_HEALTH

        # Irrigation
        if 'irrigation' in service_lower:
            return APICategory.IRRIGATION

        # Equipment
        if 'equipment' in service_lower:
            return APICategory.EQUIPMENT

        # Inventory
        if 'inventory' in service_lower:
            return APICategory.INVENTORY

        # Billing
        if 'billing' in service_lower:
            return APICategory.BILLING

        # Tasks
        if 'task' in service_lower:
            return APICategory.TASKS

        return APICategory.MISC

    def generate_openapi_spec(self, output_file: str = "openapi.json") -> str:
        """
        Generate OpenAPI 3.0 specification
        إنشاء مواصفات OpenAPI 3.0

        Returns:
            Path to generated file
        """
        print("\n📝 Generating OpenAPI specification...")

        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "SAHOOL Platform API",
                "description": "Agricultural Intelligence Platform - منصة الذكاء الزراعي",
                "version": "15.3.0",
                "contact": {
                    "name": "SAHOOL Support",
                    "email": "support@sahool.com"
                }
            },
            "servers": [],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT authentication token"
                    },
                    "apiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key for service-to-service communication"
                    }
                },
                "schemas": {}
            },
            "security": [
                {"bearerAuth": []}
            ],
            "tags": []
        }

        # Add servers
        for service_name, service in self.services.items():
            spec["servers"].append({
                "url": f"http://localhost:{service.port}",
                "description": f"{service.title} - {service.description}"
            })

            # Add tag
            spec["tags"].append({
                "name": service_name,
                "description": service.description,
                "x-description-ar": service.description_ar
            })

        # Add endpoints
        for service_name, service in self.services.items():
            for endpoint in service.endpoints:
                if endpoint.path not in spec["paths"]:
                    spec["paths"][endpoint.path] = {}

                method_lower = endpoint.method.lower()

                operation = {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "x-summary-ar": endpoint.summary_ar,
                    "x-description-ar": endpoint.description_ar,
                    "parameters": [],
                    "responses": {
                        "200": {
                            "description": "Successful response"
                        },
                        "401": {
                            "description": "Unauthorized - Invalid or missing token"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    }
                }

                # Add parameters
                for param in endpoint.parameters:
                    operation["parameters"].append({
                        "name": param.name,
                        "in": param.location,
                        "required": param.required,
                        "description": param.description,
                        "schema": {
                            "type": param.type
                        }
                    })

                spec["paths"][endpoint.path][method_lower] = operation

        # Write to file
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)

        print(f"✅ OpenAPI spec written to: {output_path}")
        return str(output_path)

    def generate_markdown_docs(self):
        """
        Generate Markdown documentation files
        إنشاء ملفات توثيق Markdown
        """
        print("\n📝 Generating Markdown documentation...")

        # Generate main README
        self._generate_main_readme()

        # Generate category-specific docs
        self._generate_authentication_docs()
        self._generate_fields_docs()
        self._generate_sensors_docs()
        self._generate_weather_docs()
        self._generate_ai_docs()

        print("✅ Markdown documentation generated")

    def _generate_main_readme(self):
        """Generate main README.md"""
        content = f"""# SAHOOL API Documentation
# توثيق واجهة برمجة تطبيقات سحول

**Version:** 15.3.0
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}

## Overview | نظرة عامة

SAHOOL is an Agricultural Intelligence Platform that provides comprehensive APIs for:
- Field management and crop monitoring
- Weather forecasting and alerts
- Satellite imagery and NDVI analysis
- AI-powered agricultural advisory
- IoT sensor integration
- Market intelligence

منصة سحول هي منصة ذكاء زراعي توفر واجهات برمجية شاملة لـ:
- إدارة الحقول ومراقبة المحاصيل
- التنبؤ بالطقس والتنبيهات
- صور الأقمار الصناعية وتحليل NDVI
- الاستشارات الزراعية بالذكاء الاصطناعي
- تكامل أجهزة استشعار إنترنت الأشياء
- معلومات السوق

## Quick Start | البدء السريع

### Authentication | المصادقة

All API requests require authentication using JWT tokens:

```bash
# Login to get access token
curl -X POST http://localhost:8000/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "user@example.com", "password": "password"}}'

# Use token in requests
curl -X GET http://localhost:8090/v1/crops/list \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Base URLs | عناوين URL الأساسية

| Service | Port | Base URL |
|---------|------|----------|
"""

        # Add services
        for service_name, service in sorted(self.services.items(), key=lambda x: x[1].port):
            content += f"| {service.title} | {service.port} | http://localhost:{service.port} |\n"

        content += f"""
## API Categories | تصنيفات API

### 1. [Authentication APIs](./authentication.md) | واجهات المصادقة
- User login and registration
- Token management
- Password reset

### 2. [Field Management APIs](./fields.md) | واجهات إدارة الحقول
- Field CRUD operations
- Crop profitability analysis
- Field boundaries and mapping

### 3. [Sensor/IoT APIs](./sensors.md) | واجهات أجهزة الاستشعار
- IoT gateway integration
- Virtual sensors
- Sensor data retrieval

### 4. [Weather APIs](./weather.md) | واجهات الطقس
- Current weather conditions
- Weather forecasts
- Weather alerts and warnings

### 5. [AI/Analysis APIs](./ai.md) | واجهات الذكاء الاصطناعي
- AI advisor and recommendations
- Crop health analysis
- Disease detection
- Yield prediction

### 6. [Satellite APIs](./satellite.md) | واجهات الأقمار الصناعية
- NDVI analysis
- Vegetation indices
- Field boundary detection
- Growing Degree Days (GDD)

## Common Patterns | الأنماط الشائعة

### Error Responses | استجابات الخطأ

All errors follow a consistent format:

```json
{{
  "error": "error_code",
  "message": "Human readable error message",
  "message_ar": "رسالة خطأ بالعربية",
  "details": {{}}
}}
```

### Pagination | التصفح

List endpoints support pagination:

```
GET /api/v1/resource?page=1&limit=20
```

Response includes:
```json
{{
  "items": [],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}}
```

### Rate Limiting | حدود المعدل

Rate limits are enforced per user/IP:
- Standard endpoints: 60 requests/minute
- Authentication endpoints: 5 requests/minute
- Heavy operations: 10 requests/minute

Headers:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## Services Overview | نظرة عامة على الخدمات

Total Services: {len(self.services)}
Total Endpoints: {sum(len(s.endpoints) for s in self.services.values())}

"""

        # Add services by category
        for category in APICategory:
            endpoints = self.endpoints_by_category[category]
            if endpoints:
                category_name = category.value.replace('_', ' ').title()
                content += f"\n### {category_name}\n\n"
                content += f"Endpoints: {len(endpoints)}\n\n"

        content += """
## OpenAPI Specification | مواصفات OpenAPI

Full OpenAPI 3.0 specification: [openapi.json](./openapi.json)

Import into:
- Swagger UI
- Postman
- Insomnia
- Any OpenAPI-compatible tool

## Postman Collection | مجموعة Postman

Download: [SAHOOL.postman_collection.json](./SAHOOL.postman_collection.json)

Includes:
- Pre-configured requests for all endpoints
- Environment variables
- Authentication setup
- Example requests and responses

## Support | الدعم

For API support or questions:
- Email: api-support@sahool.com
- Documentation: https://docs.sahool.com
- Issues: https://github.com/sahool/api/issues

---

*Generated automatically by SAHOOL API Documentation Generator*
*تم إنشاؤه تلقائيًا بواسطة مولد توثيق SAHOOL API*
"""

        # Write file
        readme_path = self.output_dir / "README.md"
        readme_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Created {readme_path}")

    def _generate_authentication_docs(self):
        """Generate authentication.md"""
        content = """# Authentication APIs
# واجهات برمجة تطبيقات المصادقة

## Overview | نظرة عامة

SAHOOL uses JWT (JSON Web Tokens) for authentication. All API requests (except authentication endpoints) require a valid JWT token in the Authorization header.

تستخدم منصة سحول JWT للمصادقة. جميع طلبات API (باستثناء نقاط المصادقة) تتطلب رمز JWT صالح في رأس التفويض.

## Authentication Flow | تدفق المصادقة

```mermaid
sequenceDiagram
    Client->>API: POST /auth/login (email, password)
    API->>Client: {access_token, refresh_token}
    Client->>API: GET /api/resource (Authorization: Bearer token)
    API->>Client: Resource data
    Client->>API: POST /auth/refresh (refresh_token)
    API->>Client: {new_access_token}
```

## Token Types | أنواع الرموز

### Access Token
- **Purpose:** Authenticate API requests
- **Lifetime:** 1 hour (3600 seconds)
- **Format:** JWT
- **Usage:** Include in `Authorization: Bearer <token>` header

### Refresh Token
- **Purpose:** Obtain new access tokens
- **Lifetime:** 7 days
- **Format:** JWT
- **Usage:** POST to `/auth/refresh` endpoint

## Endpoints | نقاط النهاية

### 1. Login | تسجيل الدخول

**Endpoint:** `POST /auth/login`
**Rate Limit:** 5 requests/minute
**Authentication:** Not required

#### Request Body

```json
{
  "email": "farmer@example.com",
  "password": "secure_password"
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-123",
    "email": "farmer@example.com",
    "name": "Ahmed Al-Farmer",
    "tenant_id": "tenant-456",
    "roles": ["farmer"]
  }
}
```

#### Error Responses

| Status | Error Code | Description |
|--------|------------|-------------|
| 401 | `invalid_credentials` | Invalid email or password |
| 429 | `rate_limit_exceeded` | Too many login attempts |
| 400 | `invalid_request` | Missing or invalid fields |

#### Example

```bash
curl -X POST http://localhost:8000/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "farmer@example.com",
    "password": "secure_password"
  }'
```

### 2. Register | التسجيل

**Endpoint:** `POST /auth/register`
**Rate Limit:** 10 requests/minute
**Authentication:** Not required

#### Request Body

```json
{
  "email": "newfarmer@example.com",
  "password": "secure_password",
  "full_name": "محمد المزارع",
  "phone": "+967777123456",
  "governorate": "sanaa",
  "farm_size_hectares": 5.5
}
```

#### Response

```json
{
  "message": "Registration successful. Please check your email for verification.",
  "message_ar": "تم التسجيل بنجاح. يرجى التحقق من بريدك الإلكتروني للتحقق.",
  "user_id": "user-789"
}
```

### 3. Refresh Token | تحديث الرمز

**Endpoint:** `POST /auth/refresh`
**Rate Limit:** 10 requests/minute
**Authentication:** Refresh token required

#### Request Body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 4. Logout | تسجيل الخروج

**Endpoint:** `POST /auth/logout`
**Authentication:** Required

Invalidates the current refresh token and optionally blacklists the access token.

#### Request Headers

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response

```json
{
  "message": "Logout successful",
  "message_ar": "تم تسجيل الخروج بنجاح"
}
```

### 5. Forgot Password | نسيت كلمة المرور

**Endpoint:** `POST /auth/forgot-password`
**Rate Limit:** 3 requests/minute
**Authentication:** Not required

#### Request Body

```json
{
  "email": "farmer@example.com"
}
```

#### Response

```json
{
  "message": "If the email exists, a password reset link has been sent.",
  "message_ar": "إذا كان البريد الإلكتروني موجودًا، فقد تم إرسال رابط إعادة تعيين كلمة المرور."
}
```

### 6. Reset Password | إعادة تعيين كلمة المرور

**Endpoint:** `POST /auth/reset-password`
**Rate Limit:** 5 requests/minute
**Authentication:** Reset token required

#### Request Body

```json
{
  "token": "reset-token-from-email",
  "new_password": "new_secure_password"
}
```

## JWT Token Structure | هيكل رمز JWT

### Access Token Payload

```json
{
  "sub": "user-123",
  "type": "access",
  "email": "farmer@example.com",
  "tenant_id": "tenant-456",
  "roles": ["farmer"],
  "permissions": ["read:fields", "write:fields"],
  "iat": 1640000000,
  "exp": 1640003600,
  "iss": "sahool-auth",
  "aud": "sahool-api"
}
```

### Token Claims

| Claim | Description |
|-------|-------------|
| `sub` | User ID (subject) |
| `type` | Token type (access/refresh) |
| `email` | User email |
| `tenant_id` | Organization/tenant ID |
| `roles` | User roles array |
| `permissions` | User permissions array |
| `iat` | Issued at timestamp |
| `exp` | Expiration timestamp |
| `iss` | Issuer (sahool-auth) |
| `aud` | Audience (sahool-api) |

## Using Tokens | استخدام الرموز

### In HTTP Headers

```bash
curl -X GET http://localhost:8090/v1/fields \\
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### In JavaScript/TypeScript

```typescript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8090/v1/fields', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### In Python

```python
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

response = requests.get(
    "http://localhost:8090/v1/fields",
    headers={"Authorization": f"Bearer {token}"}
)
```

## API Keys | مفاتيح API

For service-to-service communication, use API keys:

### Request Header

```
X-API-Key: sahool_sk_live_abc123def456
```

### Example

```bash
curl -X GET http://localhost:8090/v1/internal/metrics \\
  -H "X-API-Key: sahool_sk_live_abc123def456"
```

## Security Best Practices | أفضل ممارسات الأمان

1. **Store tokens securely**
   - Use httpOnly cookies for web applications
   - Use secure storage for mobile apps
   - Never store tokens in localStorage for sensitive data

2. **Refresh tokens proactively**
   - Refresh access token before expiration
   - Implement automatic token refresh

3. **Handle token expiration**
   - Catch 401 errors
   - Redirect to login or refresh token
   - Clear invalid tokens

4. **Protect API keys**
   - Never commit API keys to version control
   - Rotate keys periodically
   - Use different keys for different environments

5. **Use HTTPS**
   - Always use HTTPS in production
   - Never send tokens over HTTP

## Rate Limiting | حدود المعدل

Authentication endpoints have strict rate limits:

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| `/auth/login` | 5 requests | 1 minute |
| `/auth/register` | 10 requests | 1 minute |
| `/auth/forgot-password` | 3 requests | 1 minute |
| `/auth/reset-password` | 5 requests | 1 minute |
| `/auth/refresh` | 10 requests | 1 minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 45
```

### Rate Limit Exceeded Response

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many login attempts. Please try again later.",
  "message_ar": "عدد كبير جدًا من محاولات تسجيل الدخول. يرجى المحاولة مرة أخرى لاحقًا.",
  "retry_after": 45
}
```

## Roles and Permissions | الأدوار والصلاحيات

### Roles

| Role | Description |
|------|-------------|
| `farmer` | Regular farmer user |
| `agronomist` | Agricultural expert |
| `admin` | Platform administrator |
| `service` | Service account for integrations |

### Permissions

Permissions follow the pattern: `action:resource`

Examples:
- `read:fields` - View field information
- `write:fields` - Create/update fields
- `delete:fields` - Delete fields
- `manage:users` - Manage user accounts
- `view:analytics` - Access analytics data

---

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        auth_path = self.output_dir / "authentication.md"
        auth_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Created {auth_path}")

    def _generate_fields_docs(self):
        """Generate fields.md"""
        endpoints = self.endpoints_by_category[APICategory.FIELD_MANAGEMENT]

        content = """# Field Management APIs
# واجهات برمجة تطبيقات إدارة الحقول

## Overview | نظرة عامة

Field Management APIs provide comprehensive tools for managing agricultural fields, including:
- Field registration and boundaries
- Crop profitability analysis
- Cost and revenue tracking
- Historical data and trends
- Regional benchmarks

توفر واجهات إدارة الحقول أدوات شاملة لإدارة الحقول الزراعية، بما في ذلك:
- تسجيل الحقول والحدود
- تحليل ربحية المحاصيل
- تتبع التكاليف والإيرادات
- البيانات التاريخية والاتجاهات
- المقاييس الإقليمية

## Base URL

**Field Management Service:** `http://localhost:8090`

## Authentication | المصادقة

All endpoints require JWT authentication:

```
Authorization: Bearer <access_token>
```

## Endpoints | نقاط النهاية

"""

        # Add discovered endpoints
        if endpoints:
            for endpoint in sorted(endpoints, key=lambda x: (x.service_port, x.path)):
                content += f"\n### {endpoint.method} {endpoint.path}\n\n"
                content += f"**Service:** {endpoint.service_name} (Port: {endpoint.service_port})\n\n"

                if endpoint.summary:
                    content += f"**Summary:** {endpoint.summary}\n\n"
                if endpoint.summary_ar:
                    content += f"**الملخص:** {endpoint.summary_ar}\n\n"

                if endpoint.description:
                    content += f"{endpoint.description}\n\n"
                if endpoint.description_ar:
                    content += f"{endpoint.description_ar}\n\n"

                # Parameters
                if endpoint.parameters:
                    content += "#### Parameters | المعاملات\n\n"
                    content += "| Name | Type | Required | Location | Description |\n"
                    content += "|------|------|----------|----------|-------------|\n"
                    for param in endpoint.parameters:
                        required = "✓" if param.required else ""
                        content += f"| `{param.name}` | {param.type} | {required} | {param.location} | {param.description} |\n"
                    content += "\n"

                # Example
                content += "#### Example Request\n\n"
                content += "```bash\n"
                content += f"curl -X {endpoint.method} http://localhost:{endpoint.service_port}{endpoint.path} \\\n"
                content += '  -H "Authorization: Bearer YOUR_TOKEN"\n'
                content += "```\n\n"

        else:
            content += """
### GET /v1/fields

List all fields for the authenticated user.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Results per page (default: 20)
- `crop_type` (string, optional): Filter by crop type

**Response:**

```json
{
  "items": [
    {
      "id": "field-123",
      "name": "North Field",
      "name_ar": "الحقل الشمالي",
      "area_hectares": 5.5,
      "location": {
        "lat": 15.3694,
        "lon": 44.1910
      },
      "crop_type": "wheat",
      "planting_date": "2024-01-15",
      "status": "active"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

### GET /v1/profitability/crop/{crop_season_id}

Get profitability analysis for a specific crop season.

**Path Parameters:**
- `crop_season_id` (string, required): Crop season identifier

**Query Parameters:**
- `field_id` (string, required): Field ID
- `crop_code` (string, required): Crop code
- `area_ha` (number, required): Area in hectares

**Response:**

```json
{
  "crop_season_id": "season-123",
  "crop_code": "wheat",
  "crop_name_en": "Wheat",
  "crop_name_ar": "قمح",
  "area_ha": 5.5,
  "total_costs": 825000,
  "total_revenue": 1100000,
  "net_profit": 275000,
  "profit_margin_pct": 25,
  "roi_pct": 33.3,
  "cost_per_ha": 150000,
  "revenue_per_ha": 200000,
  "break_even_yield_kg": 2750,
  "estimated_yield_kg": 16500,
  "cost_breakdown": {
    "seeds": 82500,
    "fertilizer": 165000,
    "irrigation": 247500,
    "labor": 220000,
    "other": 110000
  }
}
```

### POST /v1/profitability/analyze

Analyze crop profitability with custom costs and revenues.

**Request Body:**

```json
{
  "field_id": "field-123",
  "crop_season_id": "season-456",
  "crop_code": "wheat",
  "area_ha": 5.5,
  "costs": [
    {
      "category": "seeds",
      "description": "Premium wheat seeds",
      "amount": 90000,
      "unit": "YER",
      "quantity": 300,
      "unit_cost": 300
    }
  ],
  "revenues": [
    {
      "description": "Wheat harvest - Grade A",
      "quantity": 16500,
      "unit": "kg",
      "unit_price": 65,
      "grade": "A"
    }
  ]
}
```

**Response:**

```json
{
  "analysis": {
    "net_profit": 275000,
    "roi_pct": 33.3,
    "profit_margin_pct": 25
  },
  "recommendations": [
    {
      "type": "cost_optimization",
      "priority": "high",
      "message": "Consider bulk purchasing seeds to reduce costs by 15%",
      "message_ar": "فكر في شراء البذور بالجملة لتقليل التكاليف بنسبة 15٪"
    }
  ]
}
```

### GET /v1/profitability/compare

Compare profitability of different crops.

**Query Parameters:**
- `crops` (string, required): Comma-separated crop codes
- `area_ha` (number, optional): Area in hectares (default: 1.0)
- `region` (string, optional): Region for benchmarks (default: "sanaa")

**Example Request:**

```bash
curl "http://localhost:8090/v1/profitability/compare?crops=wheat,corn,tomato&area_ha=5" \\
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "region": "sanaa",
  "area_ha": 5.0,
  "crops": [
    {
      "crop_code": "tomato",
      "crop_name_en": "Tomato",
      "crop_name_ar": "طماطم",
      "estimated_profit": 450000,
      "roi_pct": 65.2,
      "rank": 1
    },
    {
      "crop_code": "wheat",
      "crop_name_en": "Wheat",
      "crop_name_ar": "قمح",
      "estimated_profit": 275000,
      "roi_pct": 33.3,
      "rank": 2
    }
  ],
  "best_crop": {
    "crop_code": "tomato",
    "estimated_profit": 450000
  }
}
```

### GET /v1/crops/list

List all crops with available profitability data.

**Response:**

```json
{
  "total": 15,
  "crops": [
    {
      "crop_code": "wheat",
      "name_en": "Wheat",
      "name_ar": "قمح",
      "has_regional_data": true,
      "regional_yield_kg_ha": 3000,
      "regional_price_yer_kg": 60
    }
  ]
}
```
"""

        content += """
## Data Models | نماذج البيانات

### Field

```typescript
interface Field {
  id: string;
  tenant_id: string;
  name: string;
  name_ar?: string;
  area_hectares: number;
  location: {
    lat: number;
    lon: number;
  };
  boundary?: GeoJSON.Polygon;
  crop_type: string;
  planting_date?: string;
  harvest_date?: string;
  status: 'active' | 'inactive' | 'fallow';
  created_at: string;
  updated_at: string;
}
```

### Crop Profitability

```typescript
interface CropProfitability {
  crop_season_id: string;
  field_id: string;
  crop_code: string;
  crop_name_en: string;
  crop_name_ar: string;
  area_ha: number;
  total_costs: number;
  total_revenue: number;
  net_profit: number;
  profit_margin_pct: number;
  roi_pct: number;
  cost_per_ha: number;
  revenue_per_ha: number;
  cost_breakdown: {
    seeds: number;
    fertilizer: number;
    pesticides: number;
    irrigation: number;
    labor: number;
    machinery: number;
    other: number;
  };
}
```

## Error Codes | رموز الخطأ

| Code | Message | Description |
|------|---------|-------------|
| `field_not_found` | Field not found | The specified field does not exist |
| `invalid_area` | Invalid area | Area must be greater than 0 |
| `invalid_crop_code` | Invalid crop code | The crop code is not recognized |
| `no_benchmark_data` | No benchmark data available | Regional data not available for this crop |

---

*Last updated: """ + datetime.now().strftime('%Y-%m-%d') + "*\n"

        fields_path = self.output_dir / "fields.md"
        fields_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Created {fields_path}")

    def _generate_sensors_docs(self):
        """Generate sensors.md"""
        content = f"""# Sensor/IoT APIs
# واجهات برمجة تطبيقات أجهزة الاستشعار

## Overview | نظرة عامة

IoT and Sensor APIs enable integration with agricultural sensors and IoT devices:
- Real-time sensor data ingestion
- Virtual sensors for calculated metrics
- Sensor configuration and management
- Historical sensor data retrieval

تتيح واجهات إنترنت الأشياء والاستشعار التكامل مع أجهزة الاستشعار الزراعية:
- استقبال بيانات الاستشعار في الوقت الفعلي
- أجهزة استشعار افتراضية للمقاييس المحسوبة
- تكوين وإدارة أجهزة الاستشعار
- استرجاع البيانات التاريخية

## Base URLs

**IoT Gateway:** `http://localhost:8081`
**Virtual Sensors:** `http://localhost:8107`

## Sensor Types | أنواع أجهزة الاستشعار

| Type | Description | Units |
|------|-------------|-------|
| `soil_moisture` | Soil moisture sensor | % |
| `soil_temperature` | Soil temperature | °C |
| `air_temperature` | Air temperature | °C |
| `air_humidity` | Air humidity | % |
| `rainfall` | Rain gauge | mm |
| `wind_speed` | Wind speed | km/h |
| `light_intensity` | Light sensor | lux |
| `ph_sensor` | Soil pH | pH |
| `ec_sensor` | Electrical conductivity | dS/m |

## Endpoints | نقاط النهاية

### POST /api/v1/sensor-data

Ingest sensor data from IoT devices.

**Request Body:**

```json
{{
  "device_id": "device-123",
  "sensor_type": "soil_moisture",
  "value": 45.5,
  "unit": "%",
  "field_id": "field-456",
  "timestamp": "2024-01-15T12:30:00Z",
  "metadata": {{
    "depth_cm": 30,
    "location": "zone-A"
  }}
}}
```

**Response:**

```json
{{
  "id": "reading-789",
  "device_id": "device-123",
  "received_at": "2024-01-15T12:30:01Z",
  "status": "processed"
}}
```

### GET /api/v1/sensors/{{device_id}}/data

Get sensor data for a specific device.

**Query Parameters:**
- `start_date` (string, optional): Start date (ISO 8601)
- `end_date` (string, optional): End date (ISO 8601)
- `limit` (integer, optional): Number of readings (default: 100)

**Response:**

```json
{{
  "device_id": "device-123",
  "sensor_type": "soil_moisture",
  "readings": [
    {{
      "timestamp": "2024-01-15T12:30:00Z",
      "value": 45.5,
      "unit": "%"
    }}
  ],
  "total": 100
}}
```

### GET /api/v1/virtual-sensors/et0

Calculate reference evapotranspiration (ET0).

**Query Parameters:**
- `lat` (number, required): Latitude
- `lon` (number, required): Longitude
- `date` (string, optional): Date (ISO 8601)

**Response:**

```json
{{
  "et0_mm": 5.2,
  "date": "2024-01-15",
  "location": {{
    "lat": 15.3694,
    "lon": 44.1910
  }},
  "method": "penman_monteith",
  "weather_data": {{
    "temp_max_c": 32,
    "temp_min_c": 18,
    "humidity_pct": 45,
    "wind_speed_kmh": 15
  }}
}}
```

---

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        sensors_path = self.output_dir / "sensors.md"
        sensors_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Created {sensors_path}")

    def _generate_weather_docs(self):
        """Generate weather.md"""
        content = f"""# Weather APIs
# واجهات برمجة تطبيقات الطقس

## Overview | نظرة عامة

Weather APIs provide comprehensive weather data and forecasts for agricultural decision-making:
- Current weather conditions
- Multi-day forecasts
- Weather alerts and warnings
- Irrigation recommendations based on weather
- Multi-provider support with automatic fallback

توفر واجهات الطقس بيانات وتوقعات شاملة للطقس لاتخاذ القرارات الزراعية:
- ظروف الطقس الحالية
- توقعات متعددة الأيام
- تنبيهات وتحذيرات الطقس
- توصيات الري بناءً على الطقس
- دعم متعدد المزودين مع احتياطي تلقائي

## Base URLs

**Weather Core:** `http://localhost:8108`
**Weather Advanced:** `http://localhost:8109`
**Weather Service:** `http://localhost:8110`

## Weather Providers | مزودو الطقس

The system supports multiple weather data providers with automatic fallback:

1. **Open-Meteo** (Free, no API key required)
2. **OpenWeatherMap** (Requires: `OPENWEATHERMAP_API_KEY`)
3. **WeatherAPI** (Requires: `WEATHERAPI_KEY`)

## Endpoints | نقاط النهاية

### POST /weather/current

Get current weather conditions for a location.

**Request Body:**

```json
{{
  "tenant_id": "tenant-123",
  "field_id": "field-456",
  "lat": 15.3694,
  "lon": 44.1910
}}
```

**Response:**

```json
{{
  "field_id": "field-456",
  "location": {{
    "lat": 15.3694,
    "lon": 44.1910
  }},
  "provider": "Open-Meteo",
  "current": {{
    "temperature_c": 28.5,
    "humidity_pct": 45,
    "wind_speed_kmh": 15.2,
    "wind_direction_deg": 180,
    "wind_direction": "S",
    "precipitation_mm": 0,
    "cloud_cover_pct": 20,
    "pressure_hpa": 1013,
    "uv_index": 7.5,
    "condition": "Partly Cloudy",
    "condition_ar": "غائم جزئياً",
    "timestamp": "2024-01-15T12:30:00Z"
  }},
  "alerts": [
    {{
      "alert_type": "heat_stress",
      "severity": "medium",
      "title_en": "High Temperature Alert",
      "title_ar": "تنبيه درجة حرارة عالية",
      "window_hours": 6
    }}
  ]
}}
```

### POST /weather/forecast

Get weather forecast for a location.

**Request Body:**

```json
{{
  "tenant_id": "tenant-123",
  "field_id": "field-456",
  "lat": 15.3694,
  "lon": 44.1910
}}
```

**Query Parameters:**
- `days` (integer, optional): Number of forecast days (1-16, default: 7)

**Response:**

```json
{{
  "field_id": "field-456",
  "location": {{
    "lat": 15.3694,
    "lon": 44.1910
  }},
  "provider": "Open-Meteo",
  "forecast": [
    {{
      "date": "2024-01-16",
      "temp_max_c": 32,
      "temp_min_c": 18,
      "precipitation_mm": 0,
      "precipitation_probability_pct": 10,
      "wind_speed_max_kmh": 20,
      "uv_index_max": 9,
      "condition": "Sunny",
      "condition_ar": "مشمس",
      "sunrise": "06:15",
      "sunset": "18:30"
    }}
  ],
  "days": 7
}}
```

### POST /weather/irrigation

Get irrigation adjustment recommendations based on weather.

**Request Body:**

```json
{{
  "tenant_id": "tenant-123",
  "field_id": "field-456",
  "temp_c": 32,
  "humidity_pct": 40,
  "wind_speed_kmh": 18,
  "precipitation_mm": 0
}}
```

**Response:**

```json
{{
  "field_id": "field-456",
  "weather_input": {{
    "temp_c": 32,
    "humidity_pct": 40,
    "wind_speed_kmh": 18,
    "precipitation_mm": 0
  }},
  "adjustment_factor": 1.3,
  "recommendation_en": "Increase irrigation by 30% due to high evapotranspiration",
  "recommendation_ar": "زيادة الري بنسبة 30٪ بسبب التبخر العالي",
  "factors": {{
    "temperature": "high",
    "humidity": "low",
    "wind": "moderate",
    "precipitation": "none"
  }}
}}
```

### GET /weather/heat-stress/{{temp_c}}

Quick heat stress assessment for a temperature.

**Path Parameters:**
- `temp_c` (number, required): Temperature in Celsius

**Response:**

```json
{{
  "temperature_c": 38,
  "alert_type": "heat_stress",
  "severity": "high",
  "at_risk": true
}}
```

### GET /weather/providers

Get list of available weather providers.

**Response:**

```json
{{
  "multi_provider_enabled": true,
  "providers": [
    {{
      "name": "Open-Meteo",
      "configured": true,
      "type": "OpenMeteoProvider",
      "requires_api_key": false
    }},
    {{
      "name": "OpenWeatherMap",
      "configured": true,
      "type": "OpenWeatherMapProvider",
      "requires_api_key": true
    }},
    {{
      "name": "WeatherAPI",
      "configured": false,
      "type": "WeatherAPIProvider",
      "requires_api_key": true
    }}
  ],
  "total": 3,
  "configured": 2
}}
```

## Weather Alerts | تنبيهات الطقس

### Alert Types

| Type | Description |
|------|-------------|
| `heat_stress` | High temperature warning |
| `frost_risk` | Frost warning |
| `high_wind` | Strong wind warning |
| `heavy_rain` | Heavy precipitation warning |
| `low_humidity` | Low humidity alert |

### Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| `none` | No risk | No action needed |
| `low` | Minor risk | Monitor conditions |
| `medium` | Moderate risk | Take preventive measures |
| `high` | High risk | Immediate action required |
| `critical` | Extreme risk | Emergency measures |

## Data Models | نماذج البيانات

### Current Weather

```typescript
interface CurrentWeather {{
  temperature_c: number;
  humidity_pct: number;
  wind_speed_kmh: number;
  wind_direction_deg: number;
  wind_direction: string;
  precipitation_mm: number;
  cloud_cover_pct: number;
  pressure_hpa: number;
  uv_index: number;
  condition: string;
  condition_ar: string;
  timestamp: string;
}}
```

### Weather Forecast

```typescript
interface DailyForecast {{
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  precipitation_mm: number;
  precipitation_probability_pct: number;
  wind_speed_max_kmh: number;
  uv_index_max: number;
  condition: string;
  condition_ar: string;
  sunrise: string;
  sunset: string;
}}
```

---

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        weather_path = self.output_dir / "weather.md"
        weather_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Created {weather_path}")

    def _generate_ai_docs(self):
        """Generate ai.md"""
        content = f"""# AI/Analysis APIs
# واجهات برمجة تطبيقات الذكاء الاصطناعي

## Overview | نظرة عامة

AI and Analysis APIs provide intelligent agricultural advisory and analysis:
- Multi-agent AI system for agricultural questions
- Crop health analysis and disease detection
- Yield prediction
- Irrigation optimization
- Fertilizer recommendations
- RAG-based knowledge retrieval

توفر واجهات الذكاء الاصطناعي والتحليل استشارات وتحليلات زراعية ذكية:
- نظام ذكاء اصطناعي متعدد الوكلاء للأسئلة الزراعية
- تحليل صحة المحاصيل واكتشاف الأمراض
- التنبؤ بالمحصول
- تحسين الري
- توصيات الأسمدة
- استرجاع المعرفة القائم على RAG

## Base URLs

**AI Advisor:** `http://localhost:8083`
**Crop Health AI:** `http://localhost:8089`
**Agro Advisor:** `http://localhost:8084`

## AI Advisor | المستشار الذكي

Multi-agent system for comprehensive agricultural advisory.

### POST /api/v1/ask

Ask a general agricultural question.

**Request Body:**

```json
{{
  "question": "What is the best time to plant wheat in Sanaa?",
  "language": "en",
  "context": {{
    "field_id": "field-123",
    "location": "sanaa",
    "current_season": "winter"
  }}
}}
```

**Response:**

```json
{{
  "answer": "The best time to plant wheat in Sanaa is from mid-October to mid-November. This timing allows the crop to benefit from winter rains and cooler temperatures during the growing season.",
  "answer_ar": "أفضل وقت لزراعة القمح في صنعاء هو من منتصف أكتوبر إلى منتصف نوفمبر...",
  "confidence": 0.92,
  "sources": [
    "Yemen Agricultural Research",
    "Local Farming Practices Database"
  ],
  "agent": "field_analyst",
  "follow_up_questions": [
    "What wheat variety is recommended for Sanaa?",
    "How much irrigation does wheat need?"
  ]
}}
```

### POST /api/v1/diagnose

Diagnose crop diseases from symptoms or images.

**Request Body:**

```json
{{
  "crop_type": "wheat",
  "symptoms": {{
    "leaf_color": "yellow_spots",
    "leaf_texture": "powdery_coating",
    "stem_condition": "normal",
    "severity": "moderate"
  }},
  "image_path": "/uploads/crop-image-123.jpg",
  "location": "sanaa"
}}
```

**Response:**

```json
{{
  "diagnosis": {{
    "disease": "powdery_mildew",
    "disease_name_en": "Powdery Mildew",
    "disease_name_ar": "البياض الدقيقي",
    "confidence": 0.87,
    "severity": "moderate",
    "description": "Fungal disease causing white powdery growth on leaves",
    "description_ar": "مرض فطري يسبب نموًا أبيض مسحوقيًا على الأوراق"
  }},
  "treatment": {{
    "immediate_actions": [
      "Remove heavily infected leaves",
      "Improve air circulation"
    ],
    "chemical_treatment": {{
      "fungicide": "Sulfur-based fungicide",
      "dosage": "3 g/L water",
      "frequency": "Every 7-10 days",
      "duration": "2-3 applications"
    }},
    "organic_treatment": {{
      "method": "Neem oil spray",
      "dosage": "5 ml/L water",
      "frequency": "Weekly"
    }},
    "preventive_measures": [
      "Avoid overhead irrigation",
      "Plant resistant varieties",
      "Maintain proper spacing"
    ]
  }},
  "estimated_yield_impact": {{
    "if_treated": -5,
    "if_untreated": -25,
    "unit": "percent"
  }}
}}
```

### POST /api/v1/recommend

Get recommendations for irrigation, fertilization, or pest management.

**Request Body:**

```json
{{
  "crop_type": "wheat",
  "growth_stage": "tillering",
  "recommendation_type": "fertilizer",
  "field_data": {{
    "soil_type": "loamy",
    "soil_ph": 7.2,
    "area_hectares": 5.5,
    "last_fertilization": "2024-01-01"
  }}
}}
```

**Response:**

```json
{{
  "recommendations": [
    {{
      "type": "nitrogen_application",
      "priority": "high",
      "timing": "now",
      "details": {{
        "fertilizer": "Urea (46-0-0)",
        "rate_kg_ha": 80,
        "total_amount_kg": 440,
        "application_method": "broadcast",
        "timing_note": "Apply during tillering stage for optimal uptake"
      }},
      "rationale": "Wheat requires high nitrogen during tillering for strong stem development",
      "rationale_ar": "يحتاج القمح إلى نيتروجين عالي أثناء مرحلة التفريع لتطوير ساق قوي",
      "expected_benefit": "15-20% yield increase",
      "cost_estimate_yer": 26400
    }}
  ]
}}
```

### POST /api/v1/analyze-field

Comprehensive field analysis combining multiple data sources.

**Request Body:**

```json
{{
  "field_id": "field-123",
  "crop_type": "wheat",
  "analysis_types": [
    "crop_health",
    "yield_prediction",
    "irrigation_needs",
    "pest_risk"
  ]
}}
```

**Response:**

```json
{{
  "field_id": "field-123",
  "analysis_date": "2024-01-15",
  "crop_health": {{
    "overall_score": 78,
    "status": "good",
    "issues": [
      {{
        "type": "minor_stress",
        "location": "northwest_corner",
        "severity": "low"
      }}
    ]
  }},
  "yield_prediction": {{
    "predicted_yield_kg_ha": 3200,
    "confidence": 0.84,
    "factors": {{
      "weather": "favorable",
      "soil_health": "good",
      "management": "optimal"
    }}
  }},
  "irrigation_needs": {{
    "next_irrigation": "2024-01-17",
    "amount_mm": 25,
    "frequency_days": 7
  }},
  "pest_risk": {{
    "overall_risk": "low",
    "pests": [
      {{
        "pest": "aphids",
        "risk_level": "low",
        "monitoring_recommended": true
      }}
    ]
  }}
}}
```

## Crop Health Analysis | تحليل صحة المحاصيل

### POST /api/v1/health/analyze

Analyze crop health from satellite imagery or field data.

**Request Body:**

```json
{{
  "field_id": "field-123",
  "analysis_date": "2024-01-15",
  "data_sources": [
    "ndvi",
    "field_sensors",
    "visual_inspection"
  ]
}}
```

**Response:**

```json
{{
  "field_id": "field-123",
  "analysis_date": "2024-01-15",
  "overall_health_score": 82,
  "health_status": "good",
  "ndvi_analysis": {{
    "average_ndvi": 0.72,
    "healthy_area_pct": 85,
    "stressed_area_pct": 10,
    "bare_soil_pct": 5,
    "zones": [
      {{
        "zone_id": "zone-1",
        "ndvi": 0.75,
        "health": "excellent"
      }}
    ]
  }},
  "recommendations": [
    {{
      "action": "Investigate zone-3 for water stress",
      "priority": "medium",
      "details": "NDVI below 0.4 indicates potential irrigation issues"
    }}
  ]
}}
```

## Yield Prediction | التنبؤ بالمحصول

### POST /api/v1/yield/predict

Predict crop yield based on current conditions.

**Request Body:**

```json
{{
  "field_id": "field-123",
  "crop_type": "wheat",
  "planting_date": "2023-11-15",
  "area_hectares": 5.5,
  "current_growth_stage": "grain_filling",
  "weather_data": {{
    "avg_temperature_c": 25,
    "total_precipitation_mm": 250,
    "sunny_days": 45
  }}
}}
```

**Response:**

```json
{{
  "field_id": "field-123",
  "predicted_yield_kg": 17600,
  "predicted_yield_kg_ha": 3200,
  "confidence_interval": {{
    "lower_kg": 15840,
    "upper_kg": 19360,
    "confidence_pct": 90
  }},
  "factors": {{
    "weather_impact": 0.95,
    "soil_health_impact": 0.88,
    "management_impact": 0.92
  }},
  "harvest_date_estimate": "2024-04-20",
  "quality_prediction": {{
    "grade": "A",
    "protein_content_pct": 12.5
  }}
}}
```

## Data Models | نماذج البيانات

### AI Question Request

```typescript
interface QuestionRequest {{
  question: string;
  language: 'en' | 'ar';
  context?: {{
    field_id?: string;
    location?: string;
    crop_type?: string;
    [key: string]: any;
  }};
}}
```

### Disease Diagnosis

```typescript
interface DiagnosisResult {{
  diagnosis: {{
    disease: string;
    disease_name_en: string;
    disease_name_ar: string;
    confidence: number;
    severity: 'low' | 'moderate' | 'high' | 'critical';
  }};
  treatment: {{
    immediate_actions: string[];
    chemical_treatment?: TreatmentDetails;
    organic_treatment?: TreatmentDetails;
    preventive_measures: string[];
  }};
  estimated_yield_impact: {{
    if_treated: number;
    if_untreated: number;
  }};
}}
```

---

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""

        ai_path = self.output_dir / "ai.md"
        ai_path.write_text(content, encoding='utf-8')
        print(f"  ✓ Created {ai_path}")

    def generate_postman_collection(self, output_file: str = "SAHOOL.postman_collection.json") -> str:
        """
        Generate Postman collection
        إنشاء مجموعة Postman

        Returns:
            Path to generated file
        """
        print("\n📦 Generating Postman collection...")

        collection = {
            "info": {
                "name": "SAHOOL Platform API",
                "description": "Agricultural Intelligence Platform - منصة الذكاء الزراعي",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{access_token}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "http://localhost",
                    "type": "string"
                },
                {
                    "key": "access_token",
                    "value": "",
                    "type": "string"
                },
                {
                    "key": "tenant_id",
                    "value": "tenant-123",
                    "type": "string"
                }
            ],
            "item": []
        }

        # Add services as folders
        for service_name, service in sorted(self.services.items(), key=lambda x: x[0]):
            folder = {
                "name": f"{service.title} (Port {service.port})",
                "description": f"{service.description}\n{service.description_ar}",
                "item": []
            }

            # Add endpoints
            for endpoint in service.endpoints:
                request_item = {
                    "name": f"{endpoint.method} {endpoint.path}",
                    "request": {
                        "method": endpoint.method,
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}:{service.port}{endpoint.path}",
                            "host": ["{{base_url}}"],
                            "port": str(service.port),
                            "path": [p for p in endpoint.path.split('/') if p]
                        },
                        "description": f"{endpoint.summary}\n{endpoint.summary_ar}"
                    },
                    "response": []
                }

                # Add query parameters
                if endpoint.parameters:
                    query_params = [p for p in endpoint.parameters if p.location == "query"]
                    if query_params:
                        request_item["request"]["url"]["query"] = [
                            {
                                "key": p.name,
                                "value": "",
                                "description": p.description
                            }
                            for p in query_params
                        ]

                folder["item"].append(request_item)

            if folder["item"]:
                collection["item"].append(folder)

        # Add authentication folder at the beginning
        auth_folder = {
            "name": "Authentication",
            "description": "Authentication endpoints for login, registration, and token management",
            "item": [
                {
                    "name": "Login",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "const response = pm.response.json();",
                                    "if (response.access_token) {",
                                    "    pm.environment.set('access_token', response.access_token);",
                                    "    pm.environment.set('refresh_token', response.refresh_token);",
                                    "}"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "email": "farmer@example.com",
                                "password": "password123"
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{base_url}}:8000/auth/login",
                            "host": ["{{base_url}}"],
                            "port": "8000",
                            "path": ["auth", "login"]
                        }
                    }
                },
                {
                    "name": "Refresh Token",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "const response = pm.response.json();",
                                    "if (response.access_token) {",
                                    "    pm.environment.set('access_token', response.access_token);",
                                    "}"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "POST",
                        "header": [],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "refresh_token": "{{refresh_token}}"
                            }, indent=2),
                            "options": {
                                "raw": {
                                    "language": "json"
                                }
                            }
                        },
                        "url": {
                            "raw": "{{base_url}}:8000/auth/refresh",
                            "host": ["{{base_url}}"],
                            "port": "8000",
                            "path": ["auth", "refresh"]
                        }
                    }
                }
            ]
        }

        collection["item"].insert(0, auth_folder)

        # Write to file
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)

        print(f"✅ Postman collection written to: {output_path}")
        return str(output_path)


def main():
    """Main function to generate all documentation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate API documentation for SAHOOL platform"
    )
    parser.add_argument(
        "--services-dir",
        help="Path to services directory",
        default=None
    )
    parser.add_argument(
        "--output-dir",
        help="Path to output directory",
        default=None
    )
    parser.add_argument(
        "--skip-scan",
        action="store_true",
        help="Skip scanning services (use for quick regeneration)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("SAHOOL API Documentation Generator")
    print("مولد توثيق واجهة برمجة تطبيقات سحول")
    print("=" * 60)

    generator = APIDocsGenerator(
        services_dir=args.services_dir,
        output_dir=args.output_dir
    )

    if not args.skip_scan:
        generator.scan_all_services()

    generator.generate_openapi_spec()
    generator.generate_markdown_docs()
    generator.generate_postman_collection()

    print("\n" + "=" * 60)
    print("✅ Documentation generation complete!")
    print(f"📁 Output directory: {{generator.output_dir}}")
    print("=" * 60)


if __name__ == "__main__":
    main()

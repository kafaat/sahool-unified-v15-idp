# خطة العمل للتحسينات والترقيات

# Action Plan for Improvements and Upgrades

**المشروع:** SAHOOL Unified Platform v15.3.2  
**التاريخ:** ديسمبر 2024  
**الحالة:** خطة تنفيذ جاهزة

---

## نظرة عامة | Overview

هذا المستند يحدد **خطة عمل تنفيذية** لتحسين منصة سهول بناءً على نتائج المراجعة الشاملة. الخطة مقسمة إلى **4 مراحل** حسب الأولوية والوقت المطلوب.

---

## المرحلة 1: إصلاحات عاجلة (أسبوع واحد) 🔴

### الأولوية القصوى: الأمان

#### 1.1 إصلاح CORS Wildcard في جميع الخدمات

**المشكلة:**

```python
# في 3+ خدمات:
allow_origins=["*"]  # خطر أمني!
```

**الحل:**

**الملفات المتأثرة:**

- `kernel-services-v15.3/crop-health-ai/src/main.py`
- `kernel-services-v15.3/yield-engine/src/main.py`
- `kernel-services-v15.3/virtual-sensors/src/main.py`
- جميع الخدمات الأخرى (فحص شامل)

**الكود الجديد:**

```python
# shared/config/cors_config.py
from typing import List
from pydantic_settings import BaseSettings

class CORSSettings(BaseSettings):
    """Centralized CORS configuration"""

    allowed_origins: List[str] = [
        "https://admin.sahool.io",
        "https://app.sahool.io",
        "https://dashboard.sahool.io",
    ]

    # Development only
    dev_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
    ]

    @property
    def all_origins(self) -> List[str]:
        """Get all allowed origins based on environment"""
        import os
        if os.getenv("ENVIRONMENT") == "development":
            return self.allowed_origins + self.dev_origins
        return self.allowed_origins

# في كل خدمة:
from shared.config.cors_config import CORSSettings

cors_settings = CORSSettings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.all_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

**خطوات التنفيذ:**

```bash
# 1. إنشاء ملف التهيئة المشترك
mkdir -p shared/config
cat > shared/config/cors_config.py << 'EOF'
[الكود أعلاه]
EOF

# 2. تحديث جميع الخدمات
./scripts/security/update-cors-all-services.sh

# 3. الاختبار
pytest tests/security/test_cors.py

# 4. النشر
git add .
git commit -m "Security: Fix CORS wildcard in all services"
git push
```

**التحقق:**

```bash
# اختبار CORS
curl -H "Origin: https://malicious-site.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://api.sahool.io/v1/diagnose

# يجب أن يرفض الطلب
```

---

#### 1.2 إزالة كلمات المرور الافتراضية

**المشكلة:**

```yaml
# docker-compose.yml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-sahool} # قيمة افتراضية خطيرة!
REDIS_PASSWORD: ${REDIS_PASSWORD:-changeme}
```

**الحل:**

**1. تحديث docker-compose.yml:**

```yaml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Error: POSTGRES_PASSWORD not set}

  redis:
    command: redis-server --requirepass ${REDIS_PASSWORD:?Error: REDIS_PASSWORD not set}
```

**2. إنشاء .env.template:**

```bash
# .env.template
# ═══════════════════════════════════════════════════════════════
# SAHOOL Platform - Environment Variables Template
# ═══════════════════════════════════════════════════════════════

# Database Configuration
POSTGRES_USER=sahool
POSTGRES_PASSWORD=GENERATE_SECURE_PASSWORD_HERE
POSTGRES_DB=sahool
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PASSWORD=GENERATE_SECURE_PASSWORD_HERE
REDIS_HOST=redis
REDIS_PORT=6379

# JWT Configuration
JWT_SECRET=GENERATE_SECURE_JWT_SECRET_HERE_MIN_32_CHARS
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60

# API Configuration
API_BASE_URL=http://localhost:8000
ENVIRONMENT=development

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# NATS Configuration
NATS_URL=nats://nats:4222

# ═══════════════════════════════════════════════════════════════
# NEVER COMMIT THE ACTUAL .env FILE!
# Copy this template to .env and fill in secure values
# ═══════════════════════════════════════════════════════════════
```

**3. إنشاء سكربت لتوليد كلمات مرور آمنة:**

```bash
#!/bin/bash
# scripts/security/generate-env.sh

echo "═══════════════════════════════════════════════════════"
echo "SAHOOL Platform - Secure Environment Generator"
echo "═══════════════════════════════════════════════════════"
echo ""

# Generate random secure passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 48)

# Create .env file
cat > .env << EOF
# Generated on $(date)
POSTGRES_USER=sahool
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=sahool

REDIS_PASSWORD=${REDIS_PASSWORD}

JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60

ENVIRONMENT=production
EOF

echo "✅ .env file created successfully!"
echo ""
echo "⚠️  IMPORTANT: Keep this file secure!"
echo "⚠️  Add to .gitignore to prevent committing"
echo ""
echo "Generated credentials:"
echo "  - PostgreSQL Password: ${POSTGRES_PASSWORD:0:8}..."
echo "  - Redis Password: ${REDIS_PASSWORD:0:8}..."
echo "  - JWT Secret: ${JWT_SECRET:0:8}..."
```

**خطوات التنفيذ:**

```bash
# 1. إنشاء سكربت التوليد
chmod +x scripts/security/generate-env.sh

# 2. توليد .env للبيئات المختلفة
./scripts/security/generate-env.sh

# 3. التحقق من .gitignore
grep -q "^.env$" .gitignore || echo ".env" >> .gitignore

# 4. الاختبار
docker-compose config  # يجب أن يفشل بدون .env
docker-compose --env-file .env config  # يجب أن ينجح

# 5. النشر
git add docker-compose.yml .env.template scripts/security/generate-env.sh
git commit -m "Security: Remove default passwords, add secure env generation"
```

---

#### 1.3 تحسين مصادقة WebSocket

**المشكلة:**

```python
# kernel/services/ws_gateway/src/main.py
# TODO: Implement proper JWT validation
```

**الحل:**

**1. إنشاء وحدة مصادقة JWT:**

```python
# shared/auth/jwt_validator.py
from typing import Optional, Dict
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi import WebSocketDisconnect
from pydantic_settings import BaseSettings

class JWTSettings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"

class JWTValidator:
    """Centralized JWT validation for all services"""

    def __init__(self):
        self.settings = JWTSettings()

    async def validate_token(self, token: str) -> Dict:
        """
        Validate JWT token and return payload

        Args:
            token: JWT token string

        Returns:
            Dict with user information

        Raises:
            WebSocketDisconnect: If token is invalid
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                }
            )

            # Validate required fields
            required_fields = ["user_id", "role", "tenant_id"]
            for field in required_fields:
                if field not in payload:
                    raise WebSocketDisconnect(
                        code=4002,
                        reason=f"Missing required field: {field}"
                    )

            return payload

        except ExpiredSignatureError:
            raise WebSocketDisconnect(
                code=4001,
                reason="Token has expired"
            )
        except InvalidTokenError as e:
            raise WebSocketDisconnect(
                code=4003,
                reason=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise WebSocketDisconnect(
                code=4000,
                reason=f"Authentication error: {str(e)}"
            )

    def extract_token_from_query(self, query_params: str) -> Optional[str]:
        """Extract token from WebSocket query parameters"""
        from urllib.parse import parse_qs

        params = parse_qs(query_params)
        token = params.get("token", [None])[0]

        if not token:
            raise WebSocketDisconnect(
                code=4004,
                reason="Missing authentication token"
            )

        return token
```

**2. تحديث ws_gateway:**

```python
# kernel/services/ws_gateway/src/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from shared.auth.jwt_validator import JWTValidator
import logging

app = FastAPI(title="SAHOOL WebSocket Gateway")
jwt_validator = JWTValidator()
logger = logging.getLogger(__name__)

# Active connections with user context
connections: Dict[str, Dict] = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint with JWT authentication

    Usage: ws://localhost:8089/ws?token=<jwt_token>
    """
    try:
        # 1. Extract token from query params
        token = jwt_validator.extract_token_from_query(
            websocket.scope.get("query_string", b"").decode()
        )

        # 2. Validate token before accepting connection
        user_context = await jwt_validator.validate_token(token)

        # 3. Accept WebSocket connection
        await websocket.accept()

        # 4. Store connection with user context
        connection_id = f"{user_context['user_id']}_{user_context['tenant_id']}"
        connections[connection_id] = {
            "websocket": websocket,
            "user_id": user_context["user_id"],
            "role": user_context["role"],
            "tenant_id": user_context["tenant_id"],
        }

        logger.info(
            f"WebSocket connected: {connection_id} "
            f"(role={user_context['role']})"
        )

        # 5. Handle messages
        try:
            while True:
                data = await websocket.receive_json()

                # Validate tenant isolation
                if data.get("tenant_id") != user_context["tenant_id"]:
                    await websocket.send_json({
                        "error": "Tenant mismatch",
                        "code": "TENANT_MISMATCH"
                    })
                    continue

                # Process message
                await process_message(data, user_context)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {connection_id}")
        finally:
            # Cleanup
            if connection_id in connections:
                del connections[connection_id]

    except WebSocketDisconnect as e:
        logger.warning(f"WebSocket authentication failed: {e.reason}")
        await websocket.close(code=e.code, reason=e.reason)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason="Internal server error")

async def process_message(data: Dict, user_context: Dict):
    """Process incoming WebSocket message"""
    # Add user context to message
    data["_user_id"] = user_context["user_id"]
    data["_tenant_id"] = user_context["tenant_id"]

    # Publish to NATS for processing
    await nats_client.publish(
        subject=f"ws.{data['type']}.{user_context['tenant_id']}",
        data=data
    )
```

**3. اختبارات الوحدة:**

```python
# tests/security/test_jwt_validation.py
import pytest
from datetime import datetime, timedelta
import jwt
from shared.auth.jwt_validator import JWTValidator
from fastapi import WebSocketDisconnect

@pytest.fixture
def jwt_validator():
    return JWTValidator()

@pytest.fixture
def valid_token():
    payload = {
        "user_id": "user123",
        "role": "farmer",
        "tenant_id": "tenant456",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, "test_secret", algorithm="HS256")

@pytest.mark.asyncio
async def test_valid_token(jwt_validator, valid_token):
    """Test validation of valid token"""
    payload = await jwt_validator.validate_token(valid_token)
    assert payload["user_id"] == "user123"
    assert payload["role"] == "farmer"

@pytest.mark.asyncio
async def test_expired_token(jwt_validator):
    """Test validation of expired token"""
    expired_payload = {
        "user_id": "user123",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
    }
    expired_token = jwt.encode(expired_payload, "test_secret", algorithm="HS256")

    with pytest.raises(WebSocketDisconnect) as exc_info:
        await jwt_validator.validate_token(expired_token)

    assert exc_info.value.code == 4001
    assert "expired" in exc_info.value.reason.lower()

@pytest.mark.asyncio
async def test_invalid_signature(jwt_validator):
    """Test validation of token with invalid signature"""
    payload = {"user_id": "user123"}
    invalid_token = jwt.encode(payload, "wrong_secret", algorithm="HS256")

    with pytest.raises(WebSocketDisconnect) as exc_info:
        await jwt_validator.validate_token(invalid_token)

    assert exc_info.value.code == 4003
```

**خطوات التنفيذ:**

```bash
# 1. إنشاء الوحدات
mkdir -p shared/auth tests/security
# [إضافة الملفات أعلاه]

# 2. تشغيل الاختبارات
pytest tests/security/test_jwt_validation.py -v

# 3. تحديث ws_gateway
# [تطبيق التغييرات]

# 4. اختبار التكامل
python scripts/test/test_ws_auth.py

# 5. النشر
git add .
git commit -m "Security: Implement proper JWT validation for WebSocket"
```

---

### 1.4 فحص أمني شامل

**أدوات الفحص:**

```bash
#!/bin/bash
# scripts/security/comprehensive-security-scan.sh

echo "═══════════════════════════════════════════════════════"
echo "SAHOOL Security Scan"
echo "═══════════════════════════════════════════════════════"

# 1. Scan Python dependencies
echo "📦 Scanning Python dependencies..."
pip install safety
safety check --json > reports/security/python-deps.json

# 2. Scan Node.js dependencies
echo "📦 Scanning Node.js dependencies..."
cd web_admin && npm audit --json > ../reports/security/npm-audit.json
cd ../kernel/services/field_core && npm audit --json > ../../../reports/security/field-core-audit.json

# 3. Scan Docker images
echo "🐳 Scanning Docker images..."
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image sahool-field-ops:latest \
    --format json > reports/security/trivy-scan.json

# 4. Scan for secrets in code
echo "🔐 Scanning for hardcoded secrets..."
docker run --rm -v "$PWD:/path" trufflesecurity/trufflehog:latest \
    filesystem /path --json > reports/security/secrets-scan.json

# 5. OWASP ZAP scan (if services are running)
echo "🛡️ Running OWASP ZAP scan..."
docker run --rm -v $(pwd)/reports/security:/zap/wrk/:rw \
    -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8000 -J zap-report.json

echo "✅ Security scan complete!"
echo "📊 Reports available in reports/security/"
```

---

## المرحلة 2: تحسينات قصيرة الأجل (2-4 أسابيع) 🟠

### 2.1 زيادة التغطية الاختبارية

#### هدف: 70%+ للخدمات الحرجة

**1. إعداد بنية الاختبارات:**

```bash
# إنشاء بنية موحدة للاختبارات
mkdir -p tests/{unit,integration,e2e,performance}
```

**2. اختبارات Python Services:**

```python
# tests/unit/test_field_ops.py
import pytest
from httpx import AsyncClient
from kernel.services.field_ops.src.main import app

@pytest.mark.asyncio
async def test_create_field():
    """Test field creation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/fields",
            json={
                "name": "Test Field",
                "crop_type": "wheat",
                "area": 1000,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            }
        )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Field"

@pytest.mark.asyncio
async def test_get_field():
    """Test field retrieval"""
    # Test implementation

@pytest.mark.asyncio
async def test_update_field():
    """Test field update"""
    # Test implementation
```

**3. اختبارات Flutter (Mobile App):**

```dart
// mobile/sahool_field_app/test/features/field/field_repository_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:sahool_field_app/features/field/data/repo/field_repository.dart';

void main() {
  late FieldRepository repository;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    repository = FieldRepository(dio: mockDio);
  });

  group('FieldRepository', () {
    test('should fetch fields successfully', () async {
      // Arrange
      when(mockDio.get('/api/v1/fields'))
          .thenAnswer((_) async => Response(
                data: {'fields': []},
                statusCode: 200,
              ));

      // Act
      final result = await repository.getFields();

      // Assert
      expect(result.isSuccess, true);
      verify(mockDio.get('/api/v1/fields')).called(1);
    });

    test('should handle network errors', () async {
      // Test implementation
    });
  });
}
```

**4. اختبارات Web Admin (Jest):**

```bash
# إعداد Jest لـ web_admin
cd web_admin
npm install -D jest @testing-library/react @testing-library/jest-dom \
    @testing-library/user-event jest-environment-jsdom
```

```javascript
// web_admin/src/__tests__/components/Dashboard.test.tsx
import { render, screen } from "@testing-library/react";
import Dashboard from "@/components/Dashboard";

describe("Dashboard", () => {
  it("renders dashboard heading", () => {
    render(<Dashboard />);
    const heading = screen.getByRole("heading", { name: /dashboard/i });
    expect(heading).toBeInTheDocument();
  });

  it("displays field statistics", async () => {
    render(<Dashboard />);
    expect(await screen.findByText(/total fields/i)).toBeInTheDocument();
  });
});
```

**5. CI/CD Integration:**

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-cov
      - name: Run tests with coverage
        run: pytest --cov=kernel --cov-report=xml --cov-report=html
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  flutter-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: "3.27.0"
      - name: Run tests
        run: cd mobile/sahool_field_app && flutter test --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  web-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "20"
      - name: Run tests
        run: cd web_admin && npm ci && npm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

### 2.2 إكمال ميزات Mobile App

#### قائمة المهام (24 TODO)

**1. Wallet Screen - حوارات السحب والقرض:**

```dart
// mobile/sahool_field_app/lib/features/wallet/ui/dialogs/withdraw_dialog.dart
import 'package:flutter/material.dart';

class WithdrawDialog extends StatefulWidget {
  final double availableBalance;

  const WithdrawDialog({required this.availableBalance});

  @override
  State<WithdrawDialog> createState() => _WithdrawDialogState();
}

class _WithdrawDialogState extends State<WithdrawDialog> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  String? _selectedMethod;

  final List<String> _withdrawMethods = [
    'Bank Transfer',
    'Mobile Money',
    'Cash Pickup',
  ];

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Withdraw Funds'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Available Balance: \$${widget.availableBalance.toStringAsFixed(2)}'),
            const SizedBox(height: 16),
            TextFormField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Amount',
                prefixText: '\$',
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter amount';
                }
                final amount = double.tryParse(value);
                if (amount == null || amount <= 0) {
                  return 'Invalid amount';
                }
                if (amount > widget.availableBalance) {
                  return 'Insufficient balance';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _selectedMethod,
              decoration: const InputDecoration(
                labelText: 'Withdrawal Method',
              ),
              items: _withdrawMethods.map((method) {
                return DropdownMenuItem(
                  value: method,
                  child: Text(method),
                );
              }).toList(),
              onChanged: (value) {
                setState(() => _selectedMethod = value);
              },
              validator: (value) {
                if (value == null) {
                  return 'Please select withdrawal method';
                }
                return null;
              },
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _handleWithdraw,
          child: const Text('Withdraw'),
        ),
      ],
    );
  }

  void _handleWithdraw() {
    if (_formKey.currentState!.validate()) {
      final amount = double.parse(_amountController.text);
      Navigator.pop(context, {
        'amount': amount,
        'method': _selectedMethod,
      });
    }
  }
}
```

**2. Profile Screen - تسجيل الخروج:**

```dart
// mobile/sahool_field_app/lib/features/profile/ui/profile_screen.dart

Future<void> _handleLogout(BuildContext context) async {
  // Show confirmation dialog
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text('Logout'),
      content: const Text('Are you sure you want to logout?'),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () => Navigator.pop(context, true),
          child: const Text('Logout'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
          ),
        ),
      ],
    ),
  );

  if (confirmed == true) {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    try {
      // 1. Clear local database
      await ref.read(databaseProvider).deleteAll();

      // 2. Clear secure storage (tokens)
      final storage = FlutterSecureStorage();
      await storage.deleteAll();

      // 3. Clear shared preferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.clear();

      // 4. Cancel background sync
      await Workmanager().cancelAll();

      // 5. Navigate to login
      if (context.mounted) {
        Navigator.pop(context); // Close loading
        Navigator.pushNamedAndRemoveUntil(
          context,
          '/login',
          (route) => false,
        );
      }
    } catch (e) {
      // Handle error
      if (context.mounted) {
        Navigator.pop(context); // Close loading
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Logout failed: $e')),
        );
      }
    }
  }
}
```

**[المزيد من التطبيقات للميزات الأخرى...]**

---

## المرحلة 3: تحسينات متوسطة الأجل (1-3 أشهر) 🟡

### 3.1 نظام المراقبة الشامل (Observability)

**1. Prometheus + Grafana Stack:**

```yaml
# observability/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "sahool-services"
    static_configs:
      - targets:
          - field_ops:8080
          - ndvi_engine:8107
          - weather_core:8108
    metrics_path: /metrics

  - job_name: "postgres"
    static_configs:
      - targets: ["postgres-exporter:9187"]

  - job_name: "redis"
    static_configs:
      - targets: ["redis-exporter:9121"]
```

**2. Grafana Dashboards:**

```json
// observability/grafana/dashboards/sahool-overview.json
{
  "dashboard": {
    "title": "SAHOOL Platform Overview",
    "panels": [
      {
        "title": "API Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time P95",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

**3. Alerting Rules:**

```yaml
# observability/prometheus/alerts.yml
groups:
  - name: sahool_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} requests/sec"

      - alert: SlowResponses
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow API responses"
          description: "P95 response time is {{ $value }}s"
```

---

### 3.2 تحسينات الأداء

**1. Redis Caching Strategy:**

```python
# shared/cache/caching_strategy.py
from redis import Redis
from typing import Optional, Callable, Any
from functools import wraps
import json
import hashlib

class CacheStrategy:
    """Unified caching strategy for all services"""

    # TTL configurations (in seconds)
    TTL_CONFIGS = {
        "weather_current": 900,      # 15 minutes
        "weather_forecast": 3600,    # 1 hour
        "ndvi_data": 86400,          # 24 hours
        "field_data": 300,           # 5 minutes
        "user_profile": 3600,        # 1 hour
        "crop_recommendations": 7200, # 2 hours
    }

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def cache(
        self,
        key_prefix: str,
        ttl: Optional[int] = None,
        invalidate_on: Optional[list] = None
    ):
        """
        Decorator for caching function results

        Usage:
            @cache_strategy.cache(key_prefix="weather", ttl=900)
            async def get_weather(lat: float, lon: float):
                # expensive operation
                return weather_data
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                cache_key = self._generate_key(
                    key_prefix, func.__name__, args, kwargs
                )

                # Try to get from cache
                cached = await self._get(cache_key)
                if cached is not None:
                    return cached

                # Execute function
                result = await func(*args, **kwargs)

                # Store in cache
                await self._set(
                    cache_key,
                    result,
                    ttl or self.TTL_CONFIGS.get(key_prefix, 3600)
                )

                return result

            return wrapper
        return decorator

    def _generate_key(
        self,
        prefix: str,
        func_name: str,
        args: tuple,
        kwargs: dict
    ) -> str:
        """Generate unique cache key"""
        # Create hash of arguments
        args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]

        return f"sahool:{prefix}:{func_name}:{args_hash}"

    async def _get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def _set(self, key: str, value: Any, ttl: int):
        """Set value in cache"""
        self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def invalidate(self, pattern: str):
        """Invalidate cache by pattern"""
        keys = self.redis.keys(f"sahool:{pattern}:*")
        if keys:
            self.redis.delete(*keys)

# Usage example:
cache_strategy = CacheStrategy(redis_client)

@cache_strategy.cache(key_prefix="weather_current", ttl=900)
async def get_current_weather(lat: float, lon: float):
    # Expensive API call
    response = await weather_api.get_current(lat, lon)
    return response.json()
```

---

## المرحلة 4: رؤية طويلة الأجل (3-12 شهر) 🟢

### 4.1 Service Mesh (Istio)

**الفوائد:**

- mTLS تلقائي بين الخدمات
- Circuit Breaking
- Retry Policies
- Traffic Management
- Observability المتقدم

**التطبيق:**

```yaml
# infra/istio/install.sh
#!/bin/bash

# Install Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install Istio operator
istioctl install --set profile=production -y

# Enable sidecar injection for sahool namespace
kubectl label namespace sahool istio-injection=enabled

# Apply gateway
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: sahool-gateway
  namespace: sahool
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: sahool-tls-cert
    hosts:
    - "*.sahool.io"
EOF
```

---

### 4.2 GraphQL Gateway

**الفوائد:**

- Single query لبيانات متعددة
- Reduced over-fetching
- Better mobile performance

```graphql
# graphql/schema.graphql
type Query {
  field(id: ID!): Field
  fields(tenantId: ID!, limit: Int, offset: Int): [Field!]!
  fieldWithHealth(id: ID!): FieldWithHealth
}

type Field {
  id: ID!
  name: String!
  area: Float!
  cropType: String!
  geometry: GeoJSON!
  tenant: Tenant!
  tasks: [Task!]!
  health: HealthData
}

type FieldWithHealth {
  field: Field!
  ndvi: NDVIData!
  weather: WeatherData!
  recommendations: [Recommendation!]!
}

type NDVIData {
  value: Float!
  timestamp: DateTime!
  trend: String!
}

type WeatherData {
  temperature: Float!
  humidity: Float!
  rainfall: Float!
  forecast: [WeatherForecast!]!
}

type Recommendation {
  id: ID!
  type: String!
  priority: String!
  action: String!
  description: String!
}
```

---

## ملخص الجدول الزمني | Timeline Summary

```
الأسبوع 1: إصلاحات الأمان العاجلة
├── يوم 1-2: إصلاح CORS
├── يوم 3: إزالة كلمات المرور الافتراضية
├── يوم 4-5: تحسين WebSocket Auth
└── يوم 6-7: فحص أمني شامل

الأسبوع 2-4: تحسينات قصيرة الأجل
├── الأسبوع 2: زيادة التغطية الاختبارية (Python + Flutter)
├── الأسبوع 3: اختبارات Web Admin + CI/CD
└── الأسبوع 4: إكمال ميزات Mobile App

الشهر 2-3: تحسينات متوسطة الأجل
├── الشهر 2: نظام المراقبة الشامل (Prometheus + Grafana)
├── الشهر 2.5: تحسينات الأداء (Redis Caching)
└── الشهر 3: Database Optimization + Connection Pooling

الشهر 4-12: رؤية طويلة الأجل
├── الشهر 4-6: Service Mesh (Istio)
├── الشهر 7-9: GraphQL Gateway
└── الشهر 10-12: ML Pipeline Enhancement + Multi-Region
```

---

## المتابعة والتقييم | Monitoring & Evaluation

### مؤشرات الأداء الرئيسية (KPIs)

```yaml
Technical KPIs:
  Security:
    - Critical Vulnerabilities: 0
    - Security Scan Frequency: Weekly
    - Incident Response Time: < 15 minutes

  Quality:
    - Test Coverage: > 70%
    - Code Review: 100% of PRs
    - Build Success Rate: > 95%

  Performance:
    - API Response Time P95: < 300ms
    - Uptime: > 99.9%
    - Error Rate: < 0.1%

Business KPIs:
  - Active Users: +50% MoM
  - User Satisfaction: > 4.5/5
  - Feature Adoption: > 60%
```

### تقارير التقدم

```markdown
Weekly Report Template:

- ✅ Completed Tasks
- 🔄 In Progress
- 🚧 Blockers
- 📊 Metrics Update
- 🎯 Next Week Goals
```

---

## الخلاصة | Conclusion

هذه الخطة توفر **مسار واضح ومنظم** لتحسين منصة سهول من حالتها الحالية (8.1/10) إلى **مستوى الإنتاج الكامل (9.5/10+)**.

### الأولويات:

1. 🔴 **الأمان** - إصلاحات فورية (أسبوع 1)
2. 🟠 **الجودة** - زيادة الاختبارات (أسبوع 2-4)
3. 🟡 **الأداء** - تحسينات متوسطة (شهر 2-3)
4. 🟢 **التوسع** - رؤية طويلة الأجل (شهر 4-12)

**نتوقع بعد 4 أسابيع:**

- ✅ منصة آمنة تماماً
- ✅ تغطية اختبارية > 70%
- ✅ جميع الميزات الأساسية مكتملة
- ✅ جاهزة للإنتاج 100%

---

**آخر تحديث:** ديسمبر 2024  
**الحالة:** جاهز للتنفيذ  
**الملاك:** فريق تطوير سهول

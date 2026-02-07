# Contributing to SAHOOL

# المساهمة في سهول

Thank you for your interest in contributing to the SAHOOL National Agricultural Intelligence Platform.

شكرًا لاهتمامك بالمساهمة في منصة سهول للذكاء الزراعي الوطني.

---

## Table of Contents | جدول المحتويات

1. [Code of Conduct](#code-of-conduct--قواعد-السلوك)
2. [Getting Started](#getting-started--البدء)
3. [Development Workflow](#development-workflow--سير-العمل-التطويري)
4. [Coding Standards](#coding-standards--معايير-الترميز)
5. [Commit Guidelines](#commit-guidelines--إرشادات-الالتزام)
6. [Pull Request Process](#pull-request-process--عملية-طلب-السحب)
7. [Testing Requirements](#testing-requirements--متطلبات-الاختبار)
8. [Documentation](#documentation--التوثيق)
9. [Security](#security--الأمان)
10. [Getting Help](#getting-help--الحصول-على-المساعدة)

---

## Code of Conduct | قواعد السلوك

All contributors must adhere to professional standards and treat others with respect. Key principles:

يجب على جميع المساهمين الالتزام بالمعايير المهنية ومعاملة الآخرين باحترام. المبادئ الأساسية:

- Be respectful and inclusive | كن محترمًا وشاملاً
- Provide constructive feedback | قدم ملاحظات بناءة
- Focus on the best outcome for the project | ركز على أفضل نتيجة للمشروع
- Accept responsibility for mistakes | تحمل مسؤولية الأخطاء

---

## Getting Started | البدء

### Prerequisites | المتطلبات الأساسية

Before contributing, ensure you have:

قبل المساهمة، تأكد من وجود:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker & Docker Compose | 24+ | Container runtime |
| Python | 3.11+ | Backend services |
| Node.js | 18+ | Node.js services |
| Flutter | 3.27+ | Mobile development |
| Git | 2.x | Version control |

### Environment Setup | إعداد البيئة

```bash
# 1. Clone the repository | استنساخ المستودع
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp

# 2. Copy environment template | نسخ قالب البيئة
cp .env.example .env

# 3. Install dependencies | تثبيت التبعيات
npm install                    # Node.js packages
pip install -r requirements.txt # Python packages (if applicable)

# 4. Start development environment | بدء بيئة التطوير
make dev

# 5. Run tests to verify setup | تشغيل الاختبارات للتحقق
make test
```

### Quick Start Commands | أوامر البدء السريع

```bash
make quickstart     # Interactive setup guide
make dev            # Start all development services
make test           # Run all tests
make lint           # Check code quality
make fmt            # Format code
```

---

## Development Workflow | سير العمل التطويري

### Branch Strategy | استراتيجية الفروع

We follow a structured branching model:

نتبع نموذج فروع منظم:

| Branch Pattern | Purpose | Example |
|----------------|---------|---------|
| `main` | Production-ready code | - |
| `develop` | Development integration | - |
| `feature/**` | New features | `feature/ndvi-enhancement` |
| `fix/**` | Bug fixes | `fix/auth-token-refresh` |
| `docs/**` | Documentation updates | `docs/api-reference` |
| `refactor/**` | Code refactoring | `refactor/service-structure` |
| `test/**` | Test improvements | `test/integration-coverage` |
| `release/**` | Release preparation | `release/16.1.0` |

### Creating a Branch | إنشاء فرع

```bash
# Start from the latest develop branch
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature-name

# Work on your changes...
# Commit regularly with meaningful messages
```

---

## Coding Standards | معايير الترميز

### Python Services

We use **Ruff** for linting and formatting:

```bash
# Check code quality
ruff check apps/ shared/

# Auto-fix issues
ruff check --fix apps/ shared/

# Format code
ruff format .
```

**Key Standards:**

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use `structlog` for logging
- Use `Pydantic v2` for data validation

**Example:**

```python
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

class FieldCreate(BaseModel):
    """Create a new agricultural field."""
    name: str
    area_hectares: float
    crop_type: str | None = None

async def create_field(data: FieldCreate, tenant_id: str) -> dict:
    """Create a new field for the given tenant."""
    logger.info("creating_field", name=data.name, tenant_id=tenant_id)
    # Implementation...
    return {"id": "field-123", "name": data.name}
```

### Node.js / TypeScript Services

We use **ESLint** and **Prettier**:

```bash
# Check code quality
npm run lint

# Fix issues
npm run lint:fix

# Type checking
npm run typecheck
```

**Key Standards:**

- Use TypeScript with strict mode
- Follow ESLint configuration
- Use Prisma for database access
- Use NestJS patterns for services

### Flutter / Dart

We use the Dart analyzer:

```bash
# Analyze code
flutter analyze

# Auto-fix issues
dart fix --apply
```

**Key Standards:**

- Follow Effective Dart guidelines
- Use Riverpod for state management
- Use Drift for local database
- Support offline-first patterns

---

## Commit Guidelines | إرشادات الالتزام

### Commit Message Format | تنسيق رسالة الالتزام

We follow **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types | الأنواع

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(irrigation): add smart scheduling` |
| `fix` | Bug fix | `fix(auth): resolve token refresh issue` |
| `docs` | Documentation | `docs(api): update endpoint reference` |
| `style` | Formatting (no logic change) | `style: fix indentation` |
| `refactor` | Code restructuring | `refactor(services): extract common logic` |
| `test` | Add/update tests | `test(field): add integration tests` |
| `chore` | Maintenance tasks | `chore: update dependencies` |
| `perf` | Performance improvement | `perf(db): optimize query indexes` |
| `security` | Security fix | `security: fix SQL injection vulnerability` |
| `ci` | CI/CD changes | `ci: add parallel test execution` |

### Scopes | النطاقات

Common scopes include:

| Scope | Description |
|-------|-------------|
| `auth` | Authentication/authorization |
| `api` | API endpoints |
| `mobile` | Flutter mobile app |
| `web` | Web dashboard |
| `admin` | Admin portal |
| `db` | Database |
| `ci` | CI/CD pipeline |
| `docs` | Documentation |
| `irrigation` | Irrigation service |
| `ndvi` | NDVI processing |
| `weather` | Weather service |
| `iot` | IoT gateway |

### Good Commit Examples | أمثلة جيدة

```bash
# Feature
git commit -m "feat(irrigation): add soil moisture threshold alerts"

# Bug fix with issue reference
git commit -m "fix(auth): resolve JWT expiration handling

Fixes #234"

# Documentation
git commit -m "docs(api): add hydrology service endpoint reference"

# Breaking change
git commit -m "feat(api)!: update field response schema

BREAKING CHANGE: field.coordinates is now GeoJSON format"
```

---

## Pull Request Process | عملية طلب السحب

### Before Submitting | قبل التقديم

1. **Update from develop** | تحديث من develop
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Run all checks** | تشغيل جميع الفحوصات
   ```bash
   make lint
   make test
   make typecheck  # For TypeScript
   ```

3. **Self-review your code** | راجع كودك بنفسك

### PR Template | قالب طلب السحب

```markdown
## Summary | الملخص
Brief description of the changes.

## Type of Change | نوع التغيير
- [ ] New feature (non-breaking)
- [ ] Bug fix (non-breaking)
- [ ] Breaking change
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Changes Made | التغييرات المنفذة
- Change 1
- Change 2

## Testing | الاختبار
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed

## Checklist | قائمة التحقق
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
- [ ] No secrets or credentials committed
- [ ] Tests added/updated for changes
```

### Review Process | عملية المراجعة

1. Create PR against `develop` branch
2. Request review from team members
3. Address feedback promptly
4. Ensure CI checks pass
5. Squash commits if requested
6. Merge after approval

---

## Testing Requirements | متطلبات الاختبار

### Minimum Coverage | التغطية الأدنى

- **Overall**: 60% code coverage (enforced in CI)
- **New code**: 80% coverage recommended

### Test Categories | فئات الاختبار

| Category | Location | Command |
|----------|----------|---------|
| Unit | `tests/unit/` | `make test-unit` |
| Integration | `tests/integration/` | `make test-integration` |
| Smoke | `tests/smoke/` | `make test-smoke` |
| E2E | `tests/e2e/` | `make test-e2e` |
| Load | `tests/load/` | `make test-load` |

### Writing Tests | كتابة الاختبارات

**Python (pytest):**

```python
import pytest
from apps.services.irrigation_smart.src.api.v1 import irrigation

@pytest.mark.unit
async def test_calculate_irrigation_amount():
    """Test irrigation amount calculation."""
    result = await irrigation.calculate_amount(
        soil_moisture=35.0,
        crop_type="wheat",
        temperature=28.0
    )
    assert result.amount_mm > 0
    assert result.confidence >= 0.8

@pytest.mark.integration
async def test_irrigation_recommendation_api(client):
    """Test irrigation recommendation API endpoint."""
    response = await client.post(
        "/api/v1/irrigation/recommend",
        json={"field_id": "FIELD-001", "crop_type": "wheat"}
    )
    assert response.status_code == 200
    assert "recommendation" in response.json()
```

**Node.js (Vitest):**

```typescript
import { describe, it, expect } from 'vitest';
import { FieldService } from './field.service';

describe('FieldService', () => {
  it('should create a new field', async () => {
    const service = new FieldService();
    const field = await service.create({
      name: 'Test Field',
      area: 10.5,
    });

    expect(field.id).toBeDefined();
    expect(field.name).toBe('Test Field');
  });
});
```

---

## Documentation | التوثيق

### When to Document | متى توثق

- New API endpoints
- Configuration changes
- Architecture decisions
- Breaking changes
- Complex algorithms

### Documentation Standards | معايير التوثيق

1. **Bilingual**: Include both English and Arabic where possible
2. **Examples**: Provide code examples and usage scenarios
3. **Current**: Keep documentation in sync with code
4. **Linked**: Update `docs/README.md` index for new docs

### Adding Documentation | إضافة التوثيق

```bash
# Create documentation
vim docs/NEW_FEATURE.md

# Update index
vim docs/README.md

# Commit
git add docs/
git commit -m "docs: add NEW_FEATURE documentation"
```

---

## Security | الأمان

### Security Guidelines | إرشادات الأمان

**DO NOT commit:**
- Secrets, API keys, or credentials
- `.env` files with real values
- Private keys or certificates
- Database connection strings with passwords

**DO:**
- Use environment variables for secrets
- Follow secure coding practices
- Report security issues privately
- Use parameterized queries (no SQL injection)

### Reporting Security Issues | الإبلاغ عن مشاكل الأمان

For security vulnerabilities, please **do not** open a public issue. Instead:

1. Email security concerns to the development team
2. Include detailed description of the vulnerability
3. Provide steps to reproduce if possible
4. Allow time for a fix before public disclosure

---

## Getting Help | الحصول على المساعدة

### Resources | الموارد

| Resource | Location |
|----------|----------|
| Documentation | `docs/` directory |
| API Reference | `docs/api/` |
| Architecture | `docs/architecture/` |
| Runbooks | `docs/RUNBOOKS.md` |
| Troubleshooting | `docs/TROUBLESHOOTING.md` |

### Common Commands | الأوامر الشائعة

```bash
# Development
make dev                 # Start all services
make logs               # View all logs
make status             # Check service status

# Testing
make test               # Run all tests
make test-coverage      # With coverage report

# Code Quality
make lint               # Check code quality
make fmt                # Format code
make ci                 # Run full CI checks

# Database
make db-shell           # Connect to PostgreSQL
make db-migrate         # Run migrations
make db-seed            # Seed sample data
```

### Support Channels | قنوات الدعم

- Check existing documentation in `docs/`
- Search closed issues for similar problems
- Contact the development team for project-specific questions

---

## Recognition | التقدير

Contributors who make significant improvements will be recognized in the project's release notes and documentation.

سيتم تقدير المساهمين الذين يقدمون تحسينات كبيرة في ملاحظات الإصدار والتوثيق.

---

Thank you for contributing to SAHOOL!

شكرًا لمساهمتك في سهول!

---

_Last Updated | آخر تحديث: February 2026_

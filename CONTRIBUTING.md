# Contributing to SAHOOL Platform
# المساهمة في منصة سهول

Thank you for your interest in contributing to SAHOOL! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Security](#security)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- **Be respectful:** Treat everyone with respect and professionalism
- **Be collaborative:** Work together to achieve common goals
- **Be inclusive:** Welcome and support people of all backgrounds
- **Be constructive:** Focus on what is best for the community

## Getting Started

### Prerequisites

- **Node.js:** v18+ (for web admin and field_core service)
- **Python:** 3.11+ (for backend services)
- **Flutter:** 3.2+ (for mobile app)
- **Docker:** 20.10+ (for containerized development)
- **Git:** Latest version

### First Time Setup

1. **Fork the repository:**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/sahool-unified-v15-idp.git
   cd sahool-unified-v15-idp
   ```

2. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/kafaat/sahool-unified-v15-idp.git
   ```

3. **Generate secure environment:**
   ```bash
   ./scripts/security/generate-env.sh
   ```

4. **Start development environment:**
   ```bash
   docker-compose up -d
   ```

## Development Setup

### Python Services

```bash
cd kernel-services-v15.3/crop-health-ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### Node.js Services

```bash
cd web_admin
npm install
npm run dev
```

### Flutter Mobile App

```bash
cd mobile/sahool_field_app
flutter pub get
flutter run
```

## How to Contribute

### Types of Contributions

We welcome contributions in the following areas:

1. **Bug Fixes:** Fix existing issues
2. **New Features:** Implement new functionality
3. **Documentation:** Improve or add documentation
4. **Tests:** Add or improve test coverage
5. **Performance:** Optimize existing code
6. **Security:** Fix security vulnerabilities

### Before You Start

1. **Check existing issues:** Look for related issues or discussions
2. **Create an issue:** For new features, create an issue first to discuss
3. **Get assigned:** Wait for maintainers to approve/assign the issue
4. **Create a branch:** Work on a feature branch, not main

### Branch Naming Convention

```
feature/short-description       # For new features
bugfix/issue-number-description # For bug fixes
security/vulnerability-fix      # For security fixes
docs/what-you-are-documenting  # For documentation
test/what-you-are-testing      # For tests
```

Examples:
```bash
git checkout -b feature/wallet-withdraw-dialog
git checkout -b bugfix/123-cors-issue
git checkout -b security/sql-injection-fix
git checkout -b docs/api-documentation
```

## Coding Standards

### General Principles

- **KISS:** Keep It Simple, Stupid
- **DRY:** Don't Repeat Yourself
- **SOLID:** Follow SOLID principles
- **Clean Code:** Write self-documenting code

### Python

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Maximum line length: **88 characters** (Black formatter)
- Use **docstrings** for classes and functions

```python
from typing import List, Optional

def calculate_yield(
    area_hectares: float,
    crop_type: str,
    weather_data: Optional[dict] = None
) -> float:
    """
    Calculate crop yield prediction.
    
    Args:
        area_hectares: Field area in hectares
        crop_type: Type of crop (wheat, corn, etc.)
        weather_data: Optional weather data dictionary
        
    Returns:
        Predicted yield in tons
        
    Raises:
        ValueError: If area is negative or crop_type is invalid
    """
    pass
```

### JavaScript/TypeScript

- Follow **Airbnb Style Guide**
- Use **TypeScript** for type safety
- Use **async/await** instead of promises
- Maximum line length: **100 characters**

```typescript
interface FieldData {
  id: string;
  name: string;
  area: number;
  cropType: string;
}

async function getFieldData(fieldId: string): Promise<FieldData> {
  try {
    const response = await api.get(`/fields/${fieldId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch field data:', error);
    throw error;
  }
}
```

### Dart/Flutter

- Follow **Effective Dart** guidelines
- Use **riverpod** for state management
- Maximum line length: **80 characters**
- Use **named parameters** for clarity

```dart
class FieldRepository {
  final Dio _dio;
  
  FieldRepository({required Dio dio}) : _dio = dio;
  
  Future<List<Field>> getFields({
    required String tenantId,
    int page = 1,
    int perPage = 20,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/fields',
        queryParameters: {
          'tenant_id': tenantId,
          'page': page,
          'per_page': perPage,
        },
      );
      
      return (response.data['fields'] as List)
          .map((json) => Field.fromJson(json))
          .toList();
    } catch (e) {
      throw FieldException('Failed to fetch fields: $e');
    }
  }
}
```

### Code Formatting

We use automated formatters:

- **Python:** Black + Ruff
- **JavaScript/TypeScript:** Prettier + ESLint
- **Dart:** dart format

```bash
# Python
black .
ruff check --fix .

# JavaScript/TypeScript
npm run format
npm run lint:fix

# Dart
dart format .
flutter analyze
```

## Security

### Security-First Mindset

- **Never commit secrets:** Use .env files (already in .gitignore)
- **Validate all inputs:** Sanitize user input to prevent injection
- **Use parameterized queries:** Prevent SQL injection
- **Implement rate limiting:** Prevent abuse
- **Follow principle of least privilege:** Minimize permissions

### Security Checklist Before PR

- [ ] No hardcoded secrets or credentials
- [ ] Input validation on all user inputs
- [ ] Proper error handling (don't expose stack traces)
- [ ] Authentication/authorization checks
- [ ] CORS configured correctly (no wildcards in production)
- [ ] SQL queries use parameterized statements
- [ ] Dependencies are up to date
- [ ] Run security scan: `npm audit` / `pip-audit` / `flutter pub audit`

### Reporting Security Vulnerabilities

**DO NOT** open a public issue for security vulnerabilities.

Instead:
1. Email: security@sahool.io
2. Or create a **Private Security Advisory** on GitHub

## Testing

### Test Coverage Requirements

- **New features:** Must include tests
- **Bug fixes:** Must include regression tests
- **Minimum coverage:** 70% for critical paths

### Running Tests

```bash
# Python services
cd kernel-services-v15.3/crop-health-ai
pytest tests/ -v --cov=src --cov-report=html

# Node.js services
cd web_admin
npm test
npm run test:coverage

# Flutter app
cd mobile/sahool_field_app
flutter test --coverage
```

### Test Structure

```
tests/
├── unit/           # Unit tests (fast, isolated)
├── integration/    # Integration tests (multiple components)
├── e2e/           # End-to-end tests (full user flows)
└── fixtures/      # Test data and mocks
```

### Writing Good Tests

```python
# Python example
import pytest
from src.services.yield_service import calculate_yield

def test_calculate_yield_with_valid_data():
    """Test yield calculation with valid inputs."""
    # Arrange
    area = 10.0
    crop_type = "wheat"
    
    # Act
    result = calculate_yield(area, crop_type)
    
    # Assert
    assert result > 0
    assert isinstance(result, float)

def test_calculate_yield_with_negative_area():
    """Test yield calculation raises error for negative area."""
    with pytest.raises(ValueError, match="Area must be positive"):
        calculate_yield(-5.0, "wheat")
```

## Pull Request Process

### Before Submitting

1. **Update from upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all tests:**
   ```bash
   # Ensure all tests pass
   pytest
   npm test
   flutter test
   ```

3. **Run linters and formatters:**
   ```bash
   black .
   ruff check .
   npm run lint
   flutter analyze
   ```

4. **Update documentation:** If you changed APIs or behavior

5. **Write clear commit messages:**
   ```
   type(scope): Brief description
   
   Detailed explanation if needed.
   
   Fixes #123
   ```
   
   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Submitting the PR

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub:**
   - Use a clear, descriptive title
   - Reference related issues
   - Provide detailed description
   - Add screenshots for UI changes
   - Check the boxes in PR template

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed
   
   ## Screenshots (if applicable)
   
   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests pass locally
   - [ ] Security considerations addressed
   ```

### Review Process

1. **Automated checks:** CI/CD runs tests and security scans
2. **Code review:** At least one maintainer reviews
3. **Address feedback:** Make requested changes
4. **Approval:** Once approved, maintainer will merge

### After Merge

1. **Delete your branch:**
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update local main:**
   ```bash
   git checkout main
   git pull upstream main
   ```

## Development Workflow

### Daily Development

```bash
# 1. Start your day - update from upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/new-awesome-feature

# 3. Make changes, commit frequently
git add .
git commit -m "feat: add awesome feature"

# 4. Keep up to date with upstream
git fetch upstream
git rebase upstream/main

# 5. Push and create PR
git push origin feature/new-awesome-feature
```

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(wallet): add withdrawal dialog

Implements the wallet withdrawal functionality with:
- Amount validation
- Method selection (bank, mobile money, cash)
- Confirmation dialog

Closes #42

fix(auth): resolve token expiration issue

The JWT tokens were expiring too quickly causing
users to be logged out frequently.

- Increased token expiry to 60 minutes
- Added token refresh mechanism

Fixes #156

docs(api): update OpenAPI specs for field endpoints

Added missing request/response schemas for:
- GET /api/v1/fields
- POST /api/v1/fields
- PUT /api/v1/fields/{id}
```

## Questions or Need Help?

- **Documentation:** Check `/docs` folder
- **Discussions:** Use GitHub Discussions
- **Chat:** Join our Slack channel (request invite)
- **Email:** dev@sahool.io

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to SAHOOL! 🌾**

Together, we're building the future of smart agriculture. 🚀

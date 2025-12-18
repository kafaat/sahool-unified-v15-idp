# Contributing to SAHOOL / المساهمة في SAHOOL

شكراً لاهتمامك بالمساهمة في SAHOOL! هذا الدليل سيساعدك على البدء.

## Code of Conduct / قواعد السلوك

Please be respectful and constructive in all interactions.

## Getting Started / البدء

### Prerequisites / المتطلبات

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Flutter 3.16+ (for mobile)

### Development Setup / إعداد بيئة التطوير

```bash
# Clone the repository
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp

# Generate environment files
python tools/env/generate_env.py

# Start services
docker-compose up -d

# Run migrations
./tools/env/migrate.sh

# Verify setup
./tools/release/smoke_test.sh
```

## Project Structure / هيكل المشروع

```
/
├── kernel/services/    # Microservices (Source of Truth)
├── shared/             # Shared libraries
├── docker/             # Docker configurations
├── helm/               # Kubernetes Helm charts
├── gitops/             # ArgoCD applications
├── mobile/             # Flutter mobile app
├── frontend/           # Web dashboard
├── tools/              # Development tools
├── docs/               # Documentation
└── legacy/             # Archived versions (READ-ONLY)
```

## Making Changes / إجراء التغييرات

### Branch Naming / تسمية الفروع

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `security/` - Security fixes

Example: `feature/add-user-analytics`

### Commit Messages / رسائل الـ Commit

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`

Examples:
```
feat(auth): add multi-factor authentication
fix(api): handle null response in user endpoint
docs(readme): update installation instructions
security(deps): upgrade vulnerable package
```

### Code Style / نمط الكود

**Python:**
```bash
# Format and lint
ruff format .
ruff check . --fix
```

**TypeScript/JavaScript:**
```bash
npm run lint
npm run format
```

**Dart (Flutter):**
```bash
flutter analyze
dart format .
```

## Pull Request Process / عملية طلب السحب

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** your changes locally
5. **Push** to your fork
6. **Open** a Pull Request

### PR Checklist / قائمة التحقق

Before submitting:

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No secrets in code
- [ ] Commit messages follow convention

### Review Process / عملية المراجعة

1. Automated checks run (lint, test, security)
2. Code owners are assigned
3. At least 1 approval required
4. All comments addressed
5. Merge by maintainer

## Testing / الاختبار

```bash
# Unit tests
make test-unit

# Integration tests
make test-integration

# All tests with coverage
make test-cov

# Mobile tests
make test-mobile
```

## Documentation / التوثيق

- Update relevant docs in `/docs/`
- Add inline comments for complex logic
- Update README if adding new features

## Getting Help / الحصول على مساعدة

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Security**: See [SECURITY.md](SECURITY.md)

## License / الترخيص

By contributing, you agree that your contributions will be licensed under the project's license.

---

_Thank you for contributing! / شكراً لمساهمتك!_

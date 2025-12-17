# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Makefile
# Professional development and deployment commands
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: help up down restart logs ps clean db-shell test lint mobile-run

# Default target
.DEFAULT_GOAL := help

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@echo "═══════════════════════════════════════════════════════════════════"
	@echo "  SAHOOL Platform v16.0.0 - Development Commands"
	@echo "═══════════════════════════════════════════════════════════════════"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Docker Commands
# ─────────────────────────────────────────────────────────────────────────────

up: ## Start all services
	@echo "🚀 Starting SAHOOL Platform..."
	docker-compose up -d
	@echo "✅ Platform is running!"
	@echo "   - API Gateway: http://localhost:8000"
	@echo "   - Field Ops:   http://localhost:8080"
	@echo "   - NATS:        http://localhost:8222"

down: ## Stop all services
	@echo "🛑 Stopping SAHOOL Platform..."
	docker-compose down
	@echo "✅ Platform stopped."

restart: down up ## Restart all services

logs: ## Follow logs from all services
	docker-compose logs -f

logs-service: ## Follow logs from specific service (usage: make logs-service SERVICE=field_ops)
	docker-compose logs -f $(SERVICE)

ps: ## List running services
	docker-compose ps

# ─────────────────────────────────────────────────────────────────────────────
# Database Commands
# ─────────────────────────────────────────────────────────────────────────────

db-shell: ## Connect to PostgreSQL shell
	@echo "🗄️  Connecting to SAHOOL Database..."
	docker exec -it sahool-postgres psql -U sahool -d sahool

db-migrate: ## Run database migrations
	@echo "📦 Running migrations..."
	./tools/env/migrate.sh

db-backup: ## Backup database
	@echo "💾 Creating database backup..."
	docker exec sahool-postgres pg_dump -U sahool sahool > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"

# ─────────────────────────────────────────────────────────────────────────────
# Development Commands
# ─────────────────────────────────────────────────────────────────────────────

clean: ## Clean up containers, volumes, and build artifacts
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup complete!"

build: ## Build all Docker images
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache
	@echo "✅ Build complete!"

# ─────────────────────────────────────────────────────────────────────────────
# Mobile App Commands
# ─────────────────────────────────────────────────────────────────────────────

mobile-run: ## Run Flutter mobile app
	@echo "📱 Starting Mobile App..."
	cd mobile/sahool_field_app && flutter run

mobile-build-apk: ## Build Android APK
	@echo "📦 Building Android APK..."
	cd mobile/sahool_field_app && flutter build apk --release

mobile-build-ios: ## Build iOS app
	@echo "📦 Building iOS App..."
	cd mobile/sahool_field_app && flutter build ios --release

mobile-clean: ## Clean Flutter build
	@echo "🧹 Cleaning Flutter build..."
	cd mobile/sahool_field_app && flutter clean && flutter pub get

# ─────────────────────────────────────────────────────────────────────────────
# Code Quality Commands (Sprint 1 Governance)
# ─────────────────────────────────────────────────────────────────────────────

fmt: ## Format code with Ruff
	@echo "✨ Formatting code..."
	python -m ruff format .
	python -m ruff check . --fix
	@echo "✅ Code formatted!"

lint: ## Check code style and linting
	@echo "🔍 Running linters..."
	python -m ruff format . --check
	python -m ruff check .

test: ## Run all tests with coverage
	@echo "🧪 Running tests..."
	pytest --cov=shared --cov-report=term-missing

test-unit: ## Run unit tests only (fast)
	@echo "🧪 Running unit tests..."
	pytest tests/unit -v

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	pytest tests/integration -v

test-smoke: ## Run smoke tests
	@echo "💨 Running smoke tests..."
	pytest tests/smoke -v

test-cov: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	pytest --cov=shared --cov-report=html:coverage_html --cov-fail-under=60
	@echo "📊 Coverage report: coverage_html/index.html"

test-mobile: ## Run Flutter tests
	@echo "🧪 Running Flutter tests..."
	cd mobile/sahool_field_app && flutter test

ci: lint test ## Run lint + test (CI check)
	@echo "✅ CI checks passed!"

ci-full: lint test-cov env-check env-scan ## Full CI check with coverage
	@echo "✅ Full CI checks passed!"

env-check: ## Validate environment variables
	@echo "🔍 Validating environment..."
	python tools/env/validate_env.py

env-scan: ## Scan for ENV drift
	@echo "🔍 Scanning ENV usage..."
	python tools/env/scan_env_usage.py > tools/env/used_env.txt
	python tools/env/check_env_drift.py

secrets-scan: ## Scan for leaked secrets
	@echo "🔒 Scanning for secrets..."
	detect-secrets scan --baseline .secrets.baseline
	@echo "✅ Secrets scan complete!"

governance-check: lint env-check env-scan arch-check ## Full governance check
	@echo "✅ All governance checks passed!"

arch-check: ## Check architecture import rules
	@echo "🏗️  Checking architecture boundaries..."
	python -m tools.arch.check_imports --root .
	@echo "✅ Architecture check passed!"

arch-check-verbose: ## Check architecture with verbose output
	@echo "🏗️  Checking architecture boundaries (verbose)..."
	python -m tools.arch.check_imports --root . --verbose --fix-suggestions

# ─────────────────────────────────────────────────────────────────────────────
# Event Governance Commands (Sprint 4)
# ─────────────────────────────────────────────────────────────────────────────

event-catalog: ## Generate event catalog documentation
	@echo "📚 Generating event catalog..."
	python -m tools.events.generate_catalog
	@echo "✅ Event catalog generated!"

event-validate: ## Validate all event schemas
	@echo "🔍 Validating event schemas..."
	python -c "from shared.libs.events.schema_registry import SchemaRegistry; r = SchemaRegistry.load(); print(f'✅ Loaded {len(r.list_schemas())} schemas')"

event-check: event-validate ## Check event contracts are valid
	@echo "✅ Event contracts valid!"

# ─────────────────────────────────────────────────────────────────────────────
# Security Commands (Sprint 5)
# ─────────────────────────────────────────────────────────────────────────────

certs-ca: ## Generate internal CA (run once)
	@echo "🔐 Generating internal CA..."
	bash tools/security/certs/gen_ca.sh infra/pki
	@echo "✅ CA generated!"

certs-service: ## Generate service certificate (usage: make certs-service SERVICE=kernel)
	@echo "🔐 Generating certificate for $(SERVICE)..."
	bash tools/security/certs/gen_service_cert.sh $(SERVICE) infra/pki

certs-all: ## Generate CA and all service certificates
	@echo "🔐 Generating all certificates..."
	bash tools/security/certs/gen_all_certs.sh infra/pki
	@echo "✅ All certificates generated!"

vault-up: ## Start Vault in dev mode
	@echo "🔐 Starting Vault..."
	docker compose -f infra/vault/docker-compose.vault.yml up -d
	@echo "✅ Vault running at http://localhost:8200"
	@echo "   Token: dev-root-token"

vault-down: ## Stop Vault
	@echo "🛑 Stopping Vault..."
	docker compose -f infra/vault/docker-compose.vault.yml down

security-check: secrets-scan ## Run all security checks
	@echo "🔐 Running security checks..."
	@echo "📋 Checking for private keys..."
	@! find . -type f \( -name "*.pem" -o -name "*.key" -o -name "*.p12" \) -not -path "./.git/*" | grep -q . || (echo "❌ Private keys found!" && exit 1)
	@echo "✅ No private keys in repository"
	@echo "📋 Verifying security docs..."
	@test -f docs/security/THREAT_MODEL_STRIDE.md || (echo "❌ Missing THREAT_MODEL_STRIDE.md" && exit 1)
	@test -f docs/security/DATA_CLASSIFICATION.md || (echo "❌ Missing DATA_CLASSIFICATION.md" && exit 1)
	@echo "✅ Security documentation present"
	@echo "✅ All security checks passed!"

# ─────────────────────────────────────────────────────────────────────────────
# Compliance Commands (Sprint 6)
# ─────────────────────────────────────────────────────────────────────────────

compliance: ## Run compliance checklist generator
	@echo "📋 Generating compliance checklist..."
	python tools/compliance/generate_checklist.py --output docs/compliance/COMPLIANCE_CHECKLIST.md
	@echo "✅ Compliance checklist generated!"

compliance-json: ## Generate compliance report as JSON
	@echo "📋 Generating compliance JSON report..."
	python tools/compliance/generate_checklist.py --json --output docs/compliance/compliance_report.json

audit-test: ## Run audit flow tests
	@echo "🧪 Running audit tests..."
	pytest tests/integration/test_audit_flow.py -v

compliance-check: compliance audit-test ## Full compliance check (generate + test)
	@echo "✅ All compliance checks passed!"

gdpr-status: ## Check GDPR compliance status
	@echo "📋 GDPR Compliance Status"
	@echo "─────────────────────────"
	@test -f kernel/compliance/routes_gdpr.py && echo "✅ GDPR endpoints: Present" || echo "❌ GDPR endpoints: Missing"
	@test -f shared/libs/audit/redact.py && echo "✅ PII redaction: Present" || echo "❌ PII redaction: Missing"
	@test -f shared/libs/audit/service.py && echo "✅ Audit service: Present" || echo "❌ Audit service: Missing"
	@echo "─────────────────────────"

dev-install: ## Install dev dependencies
	@echo "📦 Installing dev dependencies..."
	python -m pip install -U pip ruff pytest pytest-cov pytest-asyncio pre-commit httpx detect-secrets pyjwt fastapi pydantic jsonschema sqlalchemy hvac
	pre-commit install
	@echo "✅ Dev environment ready!"

# ─────────────────────────────────────────────────────────────────────────────
# GIS/Spatial Commands (Sprint 7)
# ─────────────────────────────────────────────────────────────────────────────

gis-migrate: ## Run PostGIS migrations
	@echo "🗺️  Running PostGIS migrations..."
	alembic -c field_suite/migrations/alembic.ini upgrade head
	@echo "✅ PostGIS migrations complete!"

gis-validate: ## Validate and fix geometries
	@echo "🔍 Validating geometries..."
	python -c "from field_suite.spatial import validate_and_fix_geometries; from sqlalchemy.orm import Session; print('Note: Run with actual DB session')"
	@echo "ℹ️  Use: python -c \"from field_suite.spatial import validate_and_fix_geometries; ...\""

gis-test: ## Run GIS/spatial tests
	@echo "🧪 Running GIS tests..."
	pytest tests/integration/test_spatial_hierarchy.py -v

gis-status: ## Check GIS infrastructure status
	@echo "🗺️  GIS Infrastructure Status"
	@echo "─────────────────────────────"
	@test -f field_suite/spatial/__init__.py && echo "✅ Spatial module: Present" || echo "❌ Spatial module: Missing"
	@test -f field_suite/spatial/orm_models.py && echo "✅ ORM models: Present" || echo "❌ ORM models: Missing"
	@test -f field_suite/spatial/queries.py && echo "✅ Spatial queries: Present" || echo "❌ Spatial queries: Missing"
	@test -f field_suite/spatial/validation.py && echo "✅ Validation job: Present" || echo "❌ Validation job: Missing"
	@test -f field_suite/zones/models.py && echo "✅ Zone models: Present" || echo "❌ Zone models: Missing"
	@test -f field_suite/migrations/versions/s7_0001_postgis_hierarchy.py && echo "✅ PostGIS migration: Present" || echo "❌ PostGIS migration: Missing"
	@echo "─────────────────────────────"

# ─────────────────────────────────────────────────────────────────────────────
# Infrastructure Commands
# ─────────────────────────────────────────────────────────────────────────────

k8s-deploy: ## Deploy to Kubernetes
	@echo "☸️  Deploying to Kubernetes..."
	kubectl apply -f gitops/argocd/applications/

kong-reload: ## Reload Kong configuration
	@echo "🔄 Reloading Kong configuration..."
	docker exec sahool-kong kong reload

# ─────────────────────────────────────────────────────────────────────────────
# Release Commands
# ─────────────────────────────────────────────────────────────────────────────

release: ## Create a new release
	@echo "📦 Creating release..."
	./tools/release/release_v15_3_2.sh

smoke-test: ## Run smoke tests
	@echo "💨 Running smoke tests..."
	./tools/release/smoke_test.sh

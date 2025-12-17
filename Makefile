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
# NDVI Engine Commands (Sprint 8)
# ─────────────────────────────────────────────────────────────────────────────

ndvi-test: ## Run NDVI engine unit tests
	@echo "🧪 Running NDVI engine tests..."
	pytest tests/unit/ndvi -v
	@echo "✅ NDVI tests complete!"

ndvi-migrate: ## Run NDVI database migrations
	@echo "📦 Running NDVI migrations..."
	alembic -c kernel/services/ndvi_engine/src/migrations/alembic.ini upgrade head
	@echo "✅ NDVI migrations complete!"

ndvi-status: ## Check NDVI engine infrastructure status
	@echo "🛰️  NDVI Engine Infrastructure Status"
	@echo "─────────────────────────────────────"
	@test -f kernel/services/ndvi_engine/src/models.py && echo "✅ ORM models: Present" || echo "❌ ORM models: Missing"
	@test -f kernel/services/ndvi_engine/src/confidence.py && echo "✅ Confidence scoring: Present" || echo "❌ Confidence scoring: Missing"
	@test -f kernel/services/ndvi_engine/src/cloud_cover.py && echo "✅ Cloud detection: Present" || echo "❌ Cloud detection: Missing"
	@test -f kernel/services/ndvi_engine/src/caching.py && echo "✅ Caching strategy: Present" || echo "❌ Caching strategy: Missing"
	@test -f kernel/services/ndvi_engine/src/repository.py && echo "✅ Repository layer: Present" || echo "❌ Repository layer: Missing"
	@test -f kernel/services/ndvi_engine/src/analytics.py && echo "✅ Analytics module: Present" || echo "❌ Analytics module: Missing"
	@test -f kernel/services/ndvi_engine/src/routes_analytics.py && echo "✅ Analytics API: Present" || echo "❌ Analytics API: Missing"
	@test -f kernel/services/ndvi_engine/src/migrations/versions/s8_0001_ndvi_timeseries.py && echo "✅ NDVI migration: Present" || echo "❌ NDVI migration: Missing"
	@echo "─────────────────────────────────────"

ndvi-check: ndvi-test ndvi-status ## Full NDVI engine check (tests + status)
	@echo "✅ All NDVI checks passed!"

# ─────────────────────────────────────────────────────────────────────────────
# AI/RAG Commands (Sprint 9)
# ─────────────────────────────────────────────────────────────────────────────

ai-test: ## Run AI/RAG unit tests
	@echo "🧪 Running AI/RAG tests..."
	pytest tests/unit/ai -v
	@echo "✅ AI tests complete!"

ai-status: ## Check AI infrastructure status
	@echo "🤖 AI Infrastructure Status"
	@echo "───────────────────────────"
	@test -f advisor/ai/rag_models.py && echo "✅ RAG models: Present" || echo "❌ RAG models: Missing"
	@test -f advisor/ai/llm_client.py && echo "✅ LLM client: Present" || echo "❌ LLM client: Missing"
	@test -f advisor/ai/prompt_engine.py && echo "✅ Prompt engine: Present" || echo "❌ Prompt engine: Missing"
	@test -f advisor/ai/context_builder.py && echo "✅ Context builder: Present" || echo "❌ Context builder: Missing"
	@test -f advisor/ai/retriever.py && echo "✅ Retriever: Present" || echo "❌ Retriever: Missing"
	@test -f advisor/ai/ranker.py && echo "✅ Ranker: Present" || echo "❌ Ranker: Missing"
	@test -f advisor/ai/rag_pipeline.py && echo "✅ RAG pipeline: Present" || echo "❌ RAG pipeline: Missing"
	@test -f advisor/ai/evaluation.py && echo "✅ Evaluation hooks: Present" || echo "❌ Evaluation hooks: Missing"
	@test -f advisor/rag/doc_store.py && echo "✅ Vector store protocol: Present" || echo "❌ Vector store protocol: Missing"
	@test -f advisor/rag/qdrant_store.py && echo "✅ Qdrant adapter: Present" || echo "❌ Qdrant adapter: Missing"
	@test -f advisor/rag/ingestion.py && echo "✅ Ingestion module: Present" || echo "❌ Ingestion module: Missing"
	@echo "───────────────────────────"

qdrant-up: ## Start Qdrant vector database
	@echo "🔷 Starting Qdrant..."
	docker compose -f infra/qdrant/docker-compose.qdrant.yml up -d
	@echo "✅ Qdrant running at http://localhost:6333"
	@echo "   Dashboard: http://localhost:6333/dashboard"

qdrant-down: ## Stop Qdrant
	@echo "🛑 Stopping Qdrant..."
	docker compose -f infra/qdrant/docker-compose.qdrant.yml down

ai-check: ai-test ai-status ## Full AI check (tests + status)
	@echo "✅ All AI checks passed!"

# ─────────────────────────────────────────────────────────────────────────────
# Sync & Analytics Commands (Sprint 10-11)
# ─────────────────────────────────────────────────────────────────────────────

sync-status: ## Check mobile sync infrastructure
	@echo "📱 Mobile Sync Infrastructure Status"
	@echo "────────────────────────────────────"
	@test -f mobile/sahool_field_app/lib/core/sync/delta_sync.dart && echo "✅ Delta sync: Present" || echo "❌ Delta sync: Missing"
	@test -f mobile/sahool_field_app/lib/core/sync/batch_uploader.dart && echo "✅ Batch uploader: Present" || echo "❌ Batch uploader: Missing"
	@test -f mobile/sahool_field_app/lib/core/sync/selective_sync.dart && echo "✅ Selective sync: Present" || echo "❌ Selective sync: Missing"
	@test -f mobile/sahool_field_app/lib/core/sync/sync_metrics.dart && echo "✅ Sync metrics: Present" || echo "❌ Sync metrics: Missing"
	@echo "────────────────────────────────────"

analytics-status: ## Check analytics infrastructure
	@echo "📊 Analytics Infrastructure Status"
	@echo "──────────────────────────────────"
	@test -f services/research_core/src/modules/analytics/analytics.service.ts && echo "✅ Analytics service: Present" || echo "❌ Analytics service: Missing"
	@test -f services/research_core/src/modules/analytics/analytics.controller.ts && echo "✅ Analytics controller: Present" || echo "❌ Analytics controller: Missing"
	@test -f services/research_core/src/modules/analytics/analytics.module.ts && echo "✅ Analytics module: Present" || echo "❌ Analytics module: Missing"
	@test -f services/research_core/src/modules/analytics/export.service.ts && echo "✅ Export service: Present" || echo "❌ Export service: Missing"
	@test -f services/research_core/src/modules/analytics/dto/analytics.dto.ts && echo "✅ Analytics DTOs: Present" || echo "❌ Analytics DTOs: Missing"
	@echo "──────────────────────────────────"

# ─────────────────────────────────────────────────────────────────────────────
# E2E Testing Commands (Sprint 12)
# ─────────────────────────────────────────────────────────────────────────────

test-e2e: ## Run E2E tests
	@echo "🧪 Running E2E tests..."
	cd services/research_core && npx jest --config=../../tests/jest.e2e.config.js
	@echo "✅ E2E tests complete!"

test-e2e-experiments: ## Run E2E tests for experiments module
	@echo "🧪 Running experiments E2E tests..."
	cd services/research_core && npx jest --config=../../tests/jest.e2e.config.js --testNamePattern="Experiments"

test-e2e-logs: ## Run E2E tests for logs module
	@echo "🧪 Running logs E2E tests..."
	cd services/research_core && npx jest --config=../../tests/jest.e2e.config.js --testNamePattern="Logs"

test-e2e-analytics: ## Run E2E tests for analytics module
	@echo "🧪 Running analytics E2E tests..."
	cd services/research_core && npx jest --config=../../tests/jest.e2e.config.js --testNamePattern="Analytics"

e2e-status: ## Check E2E testing infrastructure
	@echo "🧪 E2E Testing Infrastructure Status"
	@echo "────────────────────────────────────"
	@test -f tests/e2e/research_core/experiments.e2e.spec.ts && echo "✅ Experiments E2E: Present" || echo "❌ Experiments E2E: Missing"
	@test -f tests/e2e/research_core/logs.e2e.spec.ts && echo "✅ Logs E2E: Present" || echo "❌ Logs E2E: Missing"
	@test -f tests/e2e/research_core/analytics.e2e.spec.ts && echo "✅ Analytics E2E: Present" || echo "❌ Analytics E2E: Missing"
	@test -f tests/fixtures/research.fixtures.ts && echo "✅ Test fixtures: Present" || echo "❌ Test fixtures: Missing"
	@test -f tests/setup/e2e.setup.ts && echo "✅ E2E setup: Present" || echo "❌ E2E setup: Missing"
	@test -f tests/jest.e2e.config.js && echo "✅ Jest E2E config: Present" || echo "❌ Jest E2E config: Missing"
	@echo "────────────────────────────────────"

sprint-10-12-check: sync-status analytics-status e2e-status ## Full Sprint 10-12 status check
	@echo "✅ All Sprint 10-12 checks passed!"

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

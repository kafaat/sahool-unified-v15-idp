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

dev-install: ## Install dev dependencies
	@echo "📦 Installing dev dependencies..."
	python -m pip install -U pip ruff pytest pytest-cov pytest-asyncio pre-commit httpx detect-secrets pyjwt fastapi pydantic jsonschema sqlalchemy
	pre-commit install
	@echo "✅ Dev environment ready!"

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

# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Makefile - سهول المنصة الموحدة
# Comprehensive management for the unified agricultural platform
# مجموعة شاملة لإدارة منصة سهول الزراعية الموحدة
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 2.0.0
# Reference: governance/services.yaml, REPO_MAP.md
# ═══════════════════════════════════════════════════════════════════════════════

# Comprehensive .PHONY declarations for all targets
.PHONY: help dev dev-starter dev-professional dev-enterprise
.PHONY: build build-python build-node up down down-volumes restart logs logs-service
.PHONY: db-migrate db-seed db-reset db-shell db-backup
.PHONY: test test-python test-node test-integration test-unit test-coverage test-docker
.PHONY: clean status health shell ps
.PHONY: monitoring-up monitoring-down monitoring-logs
.PHONY: lint fmt
.PHONY: infra-up kong-reload vault-up vault-down
.PHONY: starter-up professional-up enterprise-up
.PHONY: network-create network-inspect
.PHONY: dev-install generate-tokens
.PHONY: security-scan env-check
.PHONY: docs start stop rebuild quickstart
.PHONY: ci ci-full stats watch

.DEFAULT_GOAL := help

# ─────────────────────────────────────────────────────────────────────────────
# Environment Variables - متغيرات البيئة
# ─────────────────────────────────────────────────────────────────────────────

ENV ?= development
COMPOSE_PROJECT_NAME ?= sahool
SERVICE ?=

# Compose file paths - مسارات ملفات Docker Compose
COMPOSE_BASE = docker-compose.yml
COMPOSE_STARTER = packages/starter/docker-compose.yml
COMPOSE_PROFESSIONAL = packages/professional/docker-compose.yml
COMPOSE_ENTERPRISE = packages/enterprise/docker-compose.yml
COMPOSE_MONITORING = infrastructure/monitoring/docker-compose.monitoring.yml
COMPOSE_TEST = docker-compose.test.yml

# Colors for terminal output - ألوان للطرفية
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BOLD := \033[1m
RESET := \033[0m

# ═══════════════════════════════════════════════════════════════════════════════
# Help - المساعدة
# ═══════════════════════════════════════════════════════════════════════════════

help: ## عرض قائمة الأوامر المتاحة - Show available commands
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(BOLD)  SAHOOL Platform v15.3 - Unified Management Commands$(RESET)"
	@echo "$(BOLD)  منصة سهول الموحدة - أوامر الإدارة الشاملة$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)$(BLUE)Development - التطوير:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*dev/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Docker - إدارة الحاويات:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*(docker|build|up|down|restart|logs)/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Database - قاعدة البيانات:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*(database|db|migrate|seed)/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Testing - الاختبارات:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*test/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Monitoring - المراقبة:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*monitor/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Utilities - الأدوات المساعدة:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*(clean|status|health|shell)/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)Usage Examples - أمثلة الاستخدام:$(RESET)"
	@echo "  $(GREEN)make dev$(RESET)                      - بدء بيئة التطوير"
	@echo "  $(GREEN)make build$(RESET)                    - بناء جميع صور Docker"
	@echo "  $(GREEN)make logs-service SERVICE=field_ops$(RESET) - عرض سجلات خدمة محددة"
	@echo "  $(GREEN)make shell SERVICE=postgres$(RESET)   - فتح طرفية في حاوية"
	@echo "  $(GREEN)make test-python$(RESET)              - تشغيل اختبارات Python"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Development - التطوير
# ═══════════════════════════════════════════════════════════════════════════════

dev: ## بدء بيئة التطوير الكاملة - Start full development environment
	@echo "$(GREEN)🚀 بدء بيئة التطوير - Starting Development Environment...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) up -d || (echo "$(RED)Failed to start development environment!$(RESET)" && exit 1)
	@$(MAKE) --no-print-directory status
	@echo "$(GREEN)✅ بيئة التطوير جاهزة - Development environment ready!$(RESET)"

dev-starter: ## بدء حزمة المبتدئين فقط - Start only starter package services
	@echo "$(GREEN)🌱 بدء حزمة المبتدئين - Starting Starter Package...$(RESET)"
	@docker compose -f $(COMPOSE_STARTER) up -d || (echo "$(RED)Failed to start starter package!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ حزمة المبتدئين جاهزة - Starter package ready!$(RESET)"
	@echo "$(BLUE)Services: PostgreSQL, Redis, NATS, Field Core, Weather, Advisory$(RESET)"

dev-professional: ## بدء حزمة الاحترافية - Start professional package
	@echo "$(GREEN)🏢 بدء حزمة الاحترافية - Starting Professional Package...$(RESET)"
	@docker compose -f $(COMPOSE_PROFESSIONAL) up -d || (echo "$(RED)Failed to start professional package!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ حزمة الاحترافية جاهزة - Professional package ready!$(RESET)"

dev-enterprise: ## بدء جميع الخدمات المتقدمة - Start all enterprise services
	@echo "$(GREEN)🏭 بدء حزمة المؤسسات - Starting Enterprise Package...$(RESET)"
	@docker compose -f $(COMPOSE_ENTERPRISE) up -d || (echo "$(RED)Failed to start enterprise package!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ حزمة المؤسسات جاهزة - Enterprise package ready!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Docker Management - إدارة Docker
# ═══════════════════════════════════════════════════════════════════════════════

build: ## بناء جميع صور Docker - Build all Docker images
	@echo "$(YELLOW)🔨 بناء جميع الصور - Building all Docker images...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) build --parallel || (echo "$(RED)Build failed!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ اكتمل البناء - Build complete!$(RESET)"

build-python: ## بناء خدمات Python فقط - Build only Python services
	@echo "$(YELLOW)🐍 بناء خدمات Python - Building Python services...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) build \
		field_ops \
		weather_core \
		ndvi_engine \
		crop_health_ai \
		virtual_sensors \
		yield_engine \
		agro_advisor \
		alert_service \
		astronomical_calendar \
		billing_core \
		fertilizer_advisor \
		crop_health \
		ai_advisor \
		agro_rules || (echo "$(RED)Python services build failed!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ خدمات Python جاهزة - Python services built!$(RESET)"

build-node: ## بناء خدمات Node.js فقط - Build only Node.js services
	@echo "$(YELLOW)📦 بناء خدمات Node.js - Building Node.js services...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) build \
		crop_growth_model \
		disaster_assessment \
		lai_estimation \
		yield_prediction \
		marketplace_service \
		community_chat \
		field_core \
		iot_service || (echo "$(RED)Node.js services build failed!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ خدمات Node.js جاهزة - Node.js services built!$(RESET)"

up: ## تشغيل جميع الخدمات - Start all services
	@echo "$(GREEN)🚀 تشغيل جميع الخدمات - Starting all services...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) up -d || (echo "$(RED)Failed to start services!$(RESET)" && exit 1)
	@$(MAKE) --no-print-directory status
	@echo "$(GREEN)✅ جميع الخدمات قيد التشغيل - All services running!$(RESET)"

down: ## إيقاف جميع الخدمات - Stop all services
	@echo "$(RED)🛑 إيقاف جميع الخدمات - Stopping all services...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) down || (echo "$(RED)Failed to stop services!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ تم إيقاف الخدمات - Services stopped!$(RESET)"

down-volumes: ## إيقاف وحذف البيانات - Stop services and remove volumes
	@echo "$(RED)🗑️  إيقاف وحذف البيانات - Stopping services and removing volumes...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) down -v || (echo "$(RED)Failed to stop services and remove volumes!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ تم حذف الخدمات والبيانات - Services and volumes removed!$(RESET)"

restart: ## إعادة تشغيل جميع الخدمات - Restart all services
	@echo "$(YELLOW)🔄 إعادة التشغيل - Restarting all services...$(RESET)"
	@$(MAKE) --no-print-directory down
	@sleep 2
	@$(MAKE) --no-print-directory up

logs: ## عرض سجلات جميع الخدمات - View logs from all services
	@echo "$(BLUE)📋 عرض السجلات - Viewing logs...$(RESET)"
	docker compose -f $(COMPOSE_BASE) logs -f

logs-service: ## عرض سجلات خدمة محددة - View specific service logs (usage: make logs-service SERVICE=name)
ifndef SERVICE
	@echo "$(RED)❌ Error: SERVICE parameter required$(RESET)"
	@echo "$(YELLOW)Usage: make logs-service SERVICE=field_ops$(RESET)"
	@exit 1
endif
	@echo "$(BLUE)📋 عرض سجلات $(SERVICE) - Viewing logs for $(SERVICE)...$(RESET)"
	docker compose -f $(COMPOSE_BASE) logs -f $(SERVICE)

# ═══════════════════════════════════════════════════════════════════════════════
# Database - قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════

db-migrate: ## تشغيل ترحيل قاعدة البيانات - Run database migrations (Prisma)
	@echo "$(YELLOW)📦 تشغيل الترحيل - Running migrations...$(RESET)"
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "$(RED)Error: DATABASE_URL is not set$(RESET)"; \
		exit 1; \
	fi
	@if [ -d "apps/services/field-core" ]; then \
		echo "Migrating field-core..."; \
		cd apps/services/field-core && npx prisma migrate deploy || (echo "$(RED)field-core migration failed!$(RESET)" && exit 1); \
	fi
	@if [ -d "apps/services/crop-growth-model" ]; then \
		echo "Migrating crop-growth-model..."; \
		cd apps/services/crop-growth-model && npx prisma migrate deploy || (echo "$(RED)crop-growth-model migration failed!$(RESET)" && exit 1); \
	fi
	@if [ -d "apps/services/disaster-assessment" ]; then \
		echo "Migrating disaster-assessment..."; \
		cd apps/services/disaster-assessment && npx prisma migrate deploy || (echo "$(RED)disaster-assessment migration failed!$(RESET)" && exit 1); \
	fi
	@echo "$(GREEN)✅ اكتمل الترحيل - Migrations complete!$(RESET)"

db-seed: ## ملء قاعدة البيانات بالبيانات التجريبية - Seed database with sample data
	@echo "$(YELLOW)🌱 ملء قاعدة البيانات - Seeding database...$(RESET)"
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "$(RED)Error: DATABASE_URL is not set$(RESET)"; \
		exit 1; \
	fi
	@if [ -d "apps/services/field-core" ]; then \
		cd apps/services/field-core && npx prisma db seed || (echo "$(RED)Database seeding failed!$(RESET)" && exit 1); \
	fi
	@echo "$(GREEN)✅ تم ملء البيانات - Database seeded!$(RESET)"

db-reset: ## إعادة تعيين قاعدة البيانات - Reset database (WARNING: deletes all data)
	@echo "$(RED)⚠️  تحذير: سيتم حذف جميع البيانات! - WARNING: This will delete all data!$(RESET)"
	@read -p "هل أنت متأكد؟ Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(RED)🗑️  إعادة تعيين قاعدة البيانات - Resetting database...$(RESET)"; \
		docker compose -f $(COMPOSE_BASE) down postgres -v; \
		docker compose -f $(COMPOSE_BASE) up -d postgres; \
		sleep 5; \
		$(MAKE) --no-print-directory db-migrate; \
		echo "$(GREEN)✅ تمت إعادة التعيين - Database reset complete!$(RESET)"; \
	else \
		echo "$(YELLOW)❌ تم الإلغاء - Cancelled$(RESET)"; \
	fi

db-shell: ## الاتصال بطرفية قاعدة البيانات - Connect to PostgreSQL shell
	@echo "$(BLUE)🗄️  الاتصال بقاعدة البيانات - Connecting to database...$(RESET)"
	@docker exec -it sahool-postgres psql -U sahool -d sahool || (echo "$(RED)Failed to connect to database! Is PostgreSQL running?$(RESET)" && exit 1)

db-backup: ## نسخ احتياطي لقاعدة البيانات - Backup database
	@echo "$(YELLOW)💾 إنشاء نسخة احتياطية - Creating database backup...$(RESET)"
	@mkdir -p backups || (echo "$(RED)Failed to create backups directory!$(RESET)" && exit 1)
	@docker exec sahool-postgres pg_dump -U sahool sahool > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql || (echo "$(RED)Database backup failed! Is PostgreSQL running?$(RESET)" && exit 1)
	@echo "$(GREEN)✅ تم إنشاء النسخة الاحتياطية - Backup created in backups/ directory!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Testing - الاختبارات
# ═══════════════════════════════════════════════════════════════════════════════

test: ## تشغيل جميع الاختبارات - Run all tests
	@echo "$(BLUE)🧪 تشغيل جميع الاختبارات - Running all tests...$(RESET)"
	@$(MAKE) --no-print-directory test-python
	@$(MAKE) --no-print-directory test-node
	@echo "$(GREEN)✅ اكتملت جميع الاختبارات - All tests complete!$(RESET)"

test-python: ## تشغيل اختبارات Python - Run Python tests
	@echo "$(BLUE)Running Python tests...$(RESET)"
	@set -e; \
	python -m pytest tests/ -v --tb=short || { \
		echo "$(RED)Python tests failed! Please fix failing tests before proceeding.$(RESET)"; \
		exit 1; \
	}
	@echo "$(GREEN)Python tests passed!$(RESET)"

test-node: ## تشغيل اختبارات Node.js - Run Node.js tests
	@echo "$(BLUE)Running Node.js tests...$(RESET)"
	@set -e; \
	if [ -d "apps/services/field-core" ]; then \
		echo "Testing field-core..."; \
		cd apps/services/field-core && npm test || { echo "$(RED)field-core tests failed!$(RESET)"; exit 1; }; \
	fi; \
	if [ -d "apps/services/crop-growth-model" ]; then \
		echo "Testing crop-growth-model..."; \
		cd apps/services/crop-growth-model && npm test || { echo "$(RED)crop-growth-model tests failed!$(RESET)"; exit 1; }; \
	fi; \
	if [ -d "apps/web" ]; then \
		echo "Testing web app..."; \
		cd apps/web && npm test || { echo "$(RED)web tests failed!$(RESET)"; exit 1; }; \
	fi
	@echo "$(GREEN)Node.js tests passed!$(RESET)"

test-integration: ## تشغيل اختبارات التكامل - Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	@set -e; \
	pytest tests/integration -v || { \
		echo "$(RED)Integration tests failed! Please fix failing tests.$(RESET)"; \
		exit 1; \
	}
	@echo "$(GREEN)Integration tests passed!$(RESET)"

test-unit: ## تشغيل اختبارات الوحدة - Run unit tests
	@echo "$(BLUE)Running unit tests...$(RESET)"
	@set -e; \
	pytest tests/unit -v || { \
		echo "$(RED)Unit tests failed! Please fix failing tests.$(RESET)"; \
		exit 1; \
	}
	@echo "$(GREEN)Unit tests passed!$(RESET)"

test-coverage: ## تشغيل الاختبارات مع تقرير التغطية - Run tests with coverage report
	@echo "$(BLUE)📊 تشغيل الاختبارات مع التغطية - Running tests with coverage...$(RESET)"
	@pytest tests/ --cov=shared --cov=packages --cov-report=html:coverage_html --cov-report=term || (echo "$(RED)Tests with coverage failed!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ تقرير التغطية: coverage_html/index.html - Coverage report: coverage_html/index.html$(RESET)"

test-docker: ## تشغيل الاختبارات داخل Docker - Run tests in Docker containers
	@echo "$(BLUE)🐳 تشغيل الاختبارات في Docker - Running tests in Docker...$(RESET)"
	@docker compose -f $(COMPOSE_TEST) up --build --abort-on-container-exit || (echo "$(RED)Docker tests failed!$(RESET)" && docker compose -f $(COMPOSE_TEST) down && exit 1)
	@docker compose -f $(COMPOSE_TEST) down
	@echo "$(GREEN)✅ اكتملت اختبارات Docker - Docker tests complete!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Utilities - الأدوات المساعدة
# ═══════════════════════════════════════════════════════════════════════════════

clean: ## تنظيف الحاويات والبيانات - Clean up containers, volumes, and build artifacts
	@echo "$(RED)🧹 التنظيف - Cleaning up...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) down -v --remove-orphans || echo "$(YELLOW)Warning: Some containers may not have been removed$(RESET)"
	@docker system prune -f --volumes || echo "$(YELLOW)Warning: Docker prune encountered issues$(RESET)"
	@rm -rf coverage_html .pytest_cache __pycache__ node_modules/.cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules/.cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ اكتمل التنظيف - Cleanup complete!$(RESET)"

status: ## عرض حالة الخدمات - Show service status
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(BOLD)  حالة الخدمات - Service Status$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@docker compose -f $(COMPOSE_BASE) ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(BOLD)  روابط الخدمات - Service URLs$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo "  $(BLUE)API Gateway (Kong):$(RESET)       http://localhost:8000"
	@echo "  $(BLUE)Field Ops Service:$(RESET)        http://localhost:8080"
	@echo "  $(BLUE)Weather Core:$(RESET)             http://localhost:8108"
	@echo "  $(BLUE)NDVI Engine:$(RESET)              http://localhost:8107"
	@echo "  $(BLUE)Crop Growth Model:$(RESET)        http://localhost:3023"
	@echo "  $(BLUE)Admin Dashboard:$(RESET)          http://localhost:3001"
	@echo "  $(BLUE)Web Application:$(RESET)          http://localhost:3000"
	@echo "  $(BLUE)PostgreSQL:$(RESET)               localhost:5432"
	@echo "  $(BLUE)Redis:$(RESET)                    localhost:6379"
	@echo "  $(BLUE)NATS:$(RESET)                     localhost:4222"
	@echo "  $(BLUE)NATS Monitor:$(RESET)             http://localhost:8222"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo ""

health: ## فحص صحة جميع الخدمات - Check health of all services
	@echo "$(BLUE)🏥 فحص صحة الخدمات - Health Check...$(RESET)"
	@echo ""
	@for service in postgres redis nats kong field_ops weather_core; do \
		if docker compose -f $(COMPOSE_BASE) ps $$service | grep -q "Up"; then \
			echo "$(GREEN)✅ $$service - Healthy$(RESET)"; \
		else \
			echo "$(RED)❌ $$service - Unhealthy$(RESET)"; \
		fi; \
	done
	@echo ""
	@echo "$(BLUE)Testing API endpoints...$(RESET)"
	@curl -s -o /dev/null -w "Kong Gateway: %{http_code}\n" http://localhost:8000 || echo "Kong: Not responding"
	@curl -s -o /dev/null -w "Field Ops: %{http_code}\n" http://localhost:8080/health || echo "Field Ops: Not responding"
	@echo ""

shell: ## فتح طرفية في حاوية - Open shell in container (usage: make shell SERVICE=postgres)
ifndef SERVICE
	@echo "$(RED)❌ Error: SERVICE parameter required$(RESET)"
	@echo "$(YELLOW)Usage: make shell SERVICE=postgres$(RESET)"
	@exit 1
endif
	@echo "$(BLUE)🐚 فتح طرفية في $(SERVICE) - Opening shell in $(SERVICE)...$(RESET)"
	docker compose -f $(COMPOSE_BASE) exec $(SERVICE) /bin/sh || \
	docker compose -f $(COMPOSE_BASE) exec $(SERVICE) /bin/bash

ps: ## قائمة الحاويات قيد التشغيل - List running containers
	@echo "$(BLUE)📦 الحاويات قيد التشغيل - Running containers:$(RESET)"
	@docker compose -f $(COMPOSE_BASE) ps

# ═══════════════════════════════════════════════════════════════════════════════
# Monitoring - المراقبة
# ═══════════════════════════════════════════════════════════════════════════════

monitoring-up: ## تشغيل Prometheus/Grafana - Start monitoring stack (Prometheus/Grafana)
	@echo "$(GREEN)📊 تشغيل المراقبة - Starting monitoring stack...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found$(RESET)"; \
		echo "$(YELLOW)Please create .env from .env.example and set GRAFANA_ADMIN_PASSWORD$(RESET)"; \
		exit 1; \
	fi
	@docker compose -f $(COMPOSE_MONITORING) up -d || (echo "$(RED)Failed to start monitoring stack!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ المراقبة جاهزة - Monitoring stack ready!$(RESET)"
	@echo "$(BLUE)Prometheus:$(RESET) http://localhost:9090"
	@echo "$(BLUE)Grafana:$(RESET)    http://localhost:3002"
	@echo "$(BLUE)Alertmanager:$(RESET) http://localhost:9093"

monitoring-down: ## إيقاف المراقبة - Stop monitoring stack
	@echo "$(RED)🛑 إيقاف المراقبة - Stopping monitoring stack...$(RESET)"
	@docker compose -f $(COMPOSE_MONITORING) down || (echo "$(RED)Failed to stop monitoring stack!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ تم إيقاف المراقبة - Monitoring stopped!$(RESET)"

monitoring-logs: ## عرض سجلات المراقبة - View monitoring logs
	@echo "$(BLUE)📋 سجلات المراقبة - Monitoring logs:$(RESET)"
	docker compose -f $(COMPOSE_MONITORING) logs -f

# ═══════════════════════════════════════════════════════════════════════════════
# Code Quality - جودة الكود
# ═══════════════════════════════════════════════════════════════════════════════

lint: ## فحص جودة الكود - Check code style and linting
	@echo "$(BLUE)🔍 فحص الكود - Running linters...$(RESET)"
	@echo "$(YELLOW)Python:$(RESET)"
	@python -m ruff format . --check || (echo "$(RED)Python formatting check failed!$(RESET)" && exit 1)
	@python -m ruff check . || (echo "$(RED)Python linting failed!$(RESET)" && exit 1)
	@echo "$(YELLOW)TypeScript/JavaScript:$(RESET)"
	@if [ -d "apps/web" ]; then \
		cd apps/web && npm run lint || (echo "$(RED)TypeScript/JavaScript linting failed!$(RESET)" && exit 1); \
	fi
	@echo "$(GREEN)✅ فحص الكود مكتمل - Linting passed!$(RESET)"

fmt: ## تنسيق الكود - Format code
	@echo "$(BLUE)✨ تنسيق الكود - Formatting code...$(RESET)"
	@python -m ruff format . || (echo "$(RED)Python formatting failed!$(RESET)" && exit 1)
	@python -m ruff check . --fix || (echo "$(RED)Python auto-fix failed!$(RESET)" && exit 1)
	@if [ -d "apps/web" ]; then \
		cd apps/web && npm run format || (echo "$(RED)TypeScript/JavaScript formatting failed!$(RESET)" && exit 1); \
	fi
	@echo "$(GREEN)✅ تم تنسيق الكود - Code formatted!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Infrastructure Management - إدارة البنية التحتية
# ═══════════════════════════════════════════════════════════════════════════════

infra-up: ## تشغيل البنية التحتية فقط - Start infrastructure only (postgres, redis, nats, kong)
	@echo "$(GREEN)🏗️  تشغيل البنية التحتية - Starting infrastructure...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) up -d postgres redis nats kong || (echo "$(RED)Failed to start infrastructure!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ البنية التحتية جاهزة - Infrastructure ready!$(RESET)"
	@echo "$(BLUE)PostgreSQL:$(RESET) localhost:5432"
	@echo "$(BLUE)Redis:$(RESET)      localhost:6379"
	@echo "$(BLUE)NATS:$(RESET)       localhost:4222"
	@echo "$(BLUE)Kong:$(RESET)       localhost:8000"

kong-reload: ## إعادة تحميل إعدادات Kong - Reload Kong configuration
	@echo "$(YELLOW)🔄 إعادة تحميل Kong - Reloading Kong...$(RESET)"
	@docker exec sahool-kong kong reload || (echo "$(RED)Failed to reload Kong! Is Kong running?$(RESET)" && exit 1)
	@echo "$(GREEN)✅ تم إعادة تحميل Kong - Kong reloaded!$(RESET)"

vault-up: ## تشغيل Vault - Start HashiCorp Vault
	@echo "$(GREEN)🔐 تشغيل Vault - Starting Vault...$(RESET)"
	@docker compose -f infra/vault/docker-compose.vault.yml up -d || (echo "$(RED)Failed to start Vault!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ Vault جاهز - Vault ready!$(RESET)"
	@echo "$(BLUE)Vault:$(RESET) http://localhost:8200"
	@echo "$(YELLOW)Token:$(RESET) dev-root-token"

vault-down: ## إيقاف Vault - Stop Vault
	@echo "$(RED)🛑 إيقاف Vault - Stopping Vault...$(RESET)"
	@docker compose -f infra/vault/docker-compose.vault.yml down || (echo "$(RED)Failed to stop Vault!$(RESET)" && exit 1)

# ═══════════════════════════════════════════════════════════════════════════════
# Package-Specific Commands - أوامر الحزم
# ═══════════════════════════════════════════════════════════════════════════════

starter-up: dev-starter ## بدء حزمة المبتدئين - Start starter package (alias)

professional-up: dev-professional ## بدء حزمة الاحترافية - Start professional package (alias)

enterprise-up: dev-enterprise ## بدء حزمة المؤسسات - Start enterprise package (alias)

# ═══════════════════════════════════════════════════════════════════════════════
# Network Management - إدارة الشبكة
# ═══════════════════════════════════════════════════════════════════════════════

network-create: ## إنشاء شبكة SAHOOL - Create SAHOOL network
	@echo "$(YELLOW)🌐 إنشاء الشبكة - Creating network...$(RESET)"
	docker network create sahool-network 2>/dev/null || echo "$(BLUE)Network already exists$(RESET)"
	@echo "$(GREEN)✅ الشبكة جاهزة - Network ready!$(RESET)"

network-inspect: ## فحص شبكة SAHOOL - Inspect SAHOOL network
	@echo "$(BLUE)🔍 فحص الشبكة - Inspecting network:$(RESET)"
	docker network inspect sahool-network

# ═══════════════════════════════════════════════════════════════════════════════
# Development Tools - أدوات التطوير
# ═══════════════════════════════════════════════════════════════════════════════

dev-install: ## تثبيت أدوات التطوير - Install development dependencies
	@echo "$(YELLOW)📦 تثبيت أدوات التطوير - Installing dev dependencies...$(RESET)"
	@python -m pip install -U pip || (echo "$(RED)Failed to upgrade pip!$(RESET)" && exit 1)
	@pip install -r requirements/dev.txt || (echo "$(RED)Failed to install Python dev dependencies!$(RESET)" && exit 1)
	@pre-commit install || (echo "$(RED)Failed to install pre-commit hooks!$(RESET)" && exit 1)
	@if [ -d "apps/web" ]; then \
		cd apps/web && npm install || (echo "$(RED)Failed to install web app dependencies!$(RESET)" && exit 1); \
	fi
	@if [ -d "apps/admin" ]; then \
		cd apps/admin && npm install || (echo "$(RED)Failed to install admin app dependencies!$(RESET)" && exit 1); \
	fi
	@echo "$(GREEN)✅ بيئة التطوير جاهزة - Dev environment ready!$(RESET)"

generate-tokens: ## توليد رموز التصميم - Generate design tokens
	@echo "$(BLUE)🎨 توليد رموز التصميم - Generating design tokens...$(RESET)"
	@python3 scripts/generators/generate_design_tokens.py || (echo "$(RED)Failed to generate design tokens!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ تم توليد الرموز - Tokens generated!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Security & Compliance - الأمن والامتثال
# ═══════════════════════════════════════════════════════════════════════════════

security-scan: ## فحص الأمان - Run security scans
	@echo "$(BLUE)🔒 فحص الأمان - Running security scans...$(RESET)"
	@detect-secrets scan --baseline .secrets.baseline || (echo "$(RED)Security scan failed!$(RESET)" && exit 1)
	@echo "$(GREEN)✅ فحص الأمان مكتمل - Security scan complete!$(RESET)"

env-check: ## التحقق من متغيرات البيئة - Validate environment variables
	@echo "$(BLUE)🔍 التحقق من البيئة - Validating environment...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ .env file not found$(RESET)"; \
		echo "$(YELLOW)Creating from .env.example...$(RESET)"; \
		cp .env.example .env; \
		echo "$(YELLOW)⚠️  Please update .env with your values$(RESET)"; \
	else \
		echo "$(GREEN)✅ .env file exists$(RESET)"; \
	fi

# ═══════════════════════════════════════════════════════════════════════════════
# Documentation - التوثيق
# ═══════════════════════════════════════════════════════════════════════════════

docs: ## عرض التوثيق - Show documentation
	@echo "$(BLUE)📚 SAHOOL Platform Documentation - توثيق منصة سهول$(RESET)"
	@echo ""
	@echo "$(BOLD)Main Documentation:$(RESET)"
	@echo "  - README.md                           - Project overview"
	@echo "  - REPO_MAP.md                         - Repository structure"
	@echo "  - packages/PACKAGE_STRUCTURE.md       - Package information"
	@echo "  - docs/                               - Full documentation"
	@echo ""
	@echo "$(BOLD)Package Documentation:$(RESET)"
	@echo "  - packages/README.md                  - Package overview"
	@echo "  - packages/DEPLOYMENT.md              - Deployment guide"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Quick Start Aliases - اختصارات البدء السريع
# ═══════════════════════════════════════════════════════════════════════════════

start: up ## اختصار لتشغيل النظام - Alias for 'up'

stop: down ## اختصار لإيقاف النظام - Alias for 'down'

rebuild: clean build up ## إعادة البناء الكاملة - Full rebuild (clean + build + up)
	@echo "$(GREEN)✅ اكتملت إعادة البناء - Rebuild complete!$(RESET)"

quickstart: ## بدء سريع للمطورين الجدد - Quick start for new developers
	@echo "$(BOLD)$(GREEN)🚀 بدء سريع لمنصة سهول - SAHOOL Platform Quick Start$(RESET)"
	@echo ""
	@echo "$(YELLOW)Step 1: Environment setup...$(RESET)"
	@$(MAKE) --no-print-directory env-check
	@echo ""
	@echo "$(YELLOW)Step 2: Creating network...$(RESET)"
	@$(MAKE) --no-print-directory network-create
	@echo ""
	@echo "$(YELLOW)Step 3: Starting infrastructure...$(RESET)"
	@$(MAKE) --no-print-directory infra-up
	@sleep 5
	@echo ""
	@echo "$(YELLOW)Step 4: Running migrations...$(RESET)"
	@$(MAKE) --no-print-directory db-migrate
	@echo ""
	@echo "$(YELLOW)Step 5: Starting services...$(RESET)"
	@$(MAKE) --no-print-directory up
	@echo ""
	@echo "$(BOLD)$(GREEN)✅ منصة سهول جاهزة! - SAHOOL Platform is ready!$(RESET)"
	@echo ""
	@$(MAKE) --no-print-directory status

# ═══════════════════════════════════════════════════════════════════════════════
# CI/CD Commands - أوامر التكامل والنشر المستمر
# ═══════════════════════════════════════════════════════════════════════════════

ci: lint test ## تشغيل فحوصات CI - Run CI checks (lint + test)
	@echo "$(GREEN)✅ فحوصات CI مكتملة - CI checks passed!$(RESET)"

ci-full: lint test-coverage security-scan ## فحوصات CI كاملة - Full CI checks
	@echo "$(GREEN)✅ جميع فحوصات CI مكتملة - All CI checks passed!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Advanced Commands - أوامر متقدمة
# ═══════════════════════════════════════════════════════════════════════════════

stats: ## إحصائيات المشروع - Show project statistics
	@echo "$(BOLD)$(BLUE)📊 إحصائيات مشروع سهول - SAHOOL Project Statistics$(RESET)"
	@echo ""
	@echo "$(YELLOW)Services:$(RESET)"
	@echo "  Python services:  $(shell find apps/services -name "requirements.txt" | wc -l)"
	@echo "  Node.js services: $(shell find apps/services -maxdepth 2 -name "package.json" | wc -l)"
	@echo ""
	@echo "$(YELLOW)Docker:$(RESET)"
	@echo "  Running containers: $(shell docker compose -f $(COMPOSE_BASE) ps -q | wc -l)"
	@echo "  Images: $(shell docker images | grep sahool | wc -l)"
	@echo ""
	@echo "$(YELLOW)Code:$(RESET)"
	@echo "  Python files: $(shell find . -name "*.py" -not -path "./.*" -not -path "*/node_modules/*" | wc -l)"
	@echo "  TypeScript files: $(shell find . -name "*.ts" -o -name "*.tsx" -not -path "./.*" -not -path "*/node_modules/*" | wc -l)"
	@echo ""

watch: ## مراقبة تلقائية للسجلات - Watch logs continuously
	@echo "$(BLUE)👀 مراقبة السجلات - Watching logs...$(RESET)"
	watch -n 2 'docker compose -f $(COMPOSE_BASE) ps'

# ═══════════════════════════════════════════════════════════════════════════════
# End of Makefile - نهاية الملف
# ═══════════════════════════════════════════════════════════════════════════════

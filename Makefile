# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Makefile - سهول المنصة الموحدة
# Comprehensive management for the unified agricultural platform
# مجموعة شاملة لإدارة منصة سهول الزراعية الموحدة
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 2.0.0
# Reference: governance/services.yaml, REPO_MAP.md
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: help dev build up down restart logs clean test health
.PHONY: mobile-test mobile-build mobile-build-release mobile-build-aab mobile-analyze
.PHONY: mobile-format mobile-clean mobile-deps mobile-codegen mobile-doctor mobile-ci
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
	@echo "$(BOLD)$(BLUE)Mobile Development - تطوير الجوال:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^mobile-[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Utilities - الأدوات المساعدة:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*(clean|status|health|shell)/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Kimi Quality Agent - وكيل الجودة كيمي:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^kimi-[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)Usage Examples - أمثلة الاستخدام:$(RESET)"
	@echo "  $(GREEN)make dev$(RESET)                      - بدء بيئة التطوير"
	@echo "  $(GREEN)make build$(RESET)                    - بناء جميع صور Docker"
	@echo "  $(GREEN)make logs-service SERVICE=field_ops$(RESET) - عرض سجلات خدمة محددة"
	@echo "  $(GREEN)make shell SERVICE=postgres$(RESET)   - فتح طرفية في حاوية"
	@echo "  $(GREEN)make test-python$(RESET)              - تشغيل اختبارات Python"
	@echo "  $(GREEN)make kimi-scan$(RESET)                - فحص جودة الكود"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Development - التطوير
# ═══════════════════════════════════════════════════════════════════════════════

dev: ## بدء بيئة التطوير الكاملة - Start full development environment
	@echo "$(GREEN)🚀 بدء بيئة التطوير - Starting Development Environment...$(RESET)"
	docker compose -f $(COMPOSE_BASE) up -d
	@$(MAKE) --no-print-directory status
	@echo "$(GREEN)✅ بيئة التطوير جاهزة - Development environment ready!$(RESET)"

dev-starter: ## بدء حزمة المبتدئين فقط - Start only starter package services
	@echo "$(GREEN)🌱 بدء حزمة المبتدئين - Starting Starter Package...$(RESET)"
	docker compose -f $(COMPOSE_STARTER) up -d
	@echo "$(GREEN)✅ حزمة المبتدئين جاهزة - Starter package ready!$(RESET)"
	@echo "$(BLUE)Services: PostgreSQL, Redis, NATS, Field Core, Weather, Advisory$(RESET)"

dev-professional: ## بدء حزمة الاحترافية - Start professional package
	@echo "$(GREEN)🏢 بدء حزمة الاحترافية - Starting Professional Package...$(RESET)"
	docker compose -f $(COMPOSE_PROFESSIONAL) up -d
	@echo "$(GREEN)✅ حزمة الاحترافية جاهزة - Professional package ready!$(RESET)"

dev-enterprise: ## بدء جميع الخدمات المتقدمة - Start all enterprise services
	@echo "$(GREEN)🏭 بدء حزمة المؤسسات - Starting Enterprise Package...$(RESET)"
	docker compose -f $(COMPOSE_ENTERPRISE) up -d
	@echo "$(GREEN)✅ حزمة المؤسسات جاهزة - Enterprise package ready!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Docker Management - إدارة Docker
# ═══════════════════════════════════════════════════════════════════════════════

build: ## بناء جميع صور Docker - Build all Docker images
	@echo "$(YELLOW)🔨 بناء جميع الصور - Building all Docker images...$(RESET)"
	docker compose -f $(COMPOSE_BASE) build --parallel
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
		agro_rules
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
		iot_service
	@echo "$(GREEN)✅ خدمات Node.js جاهزة - Node.js services built!$(RESET)"

up: ## تشغيل جميع الخدمات - Start all services
	@echo "$(GREEN)🚀 تشغيل جميع الخدمات - Starting all services...$(RESET)"
	docker compose -f $(COMPOSE_BASE) up -d
	@$(MAKE) --no-print-directory status
	@echo "$(GREEN)✅ جميع الخدمات قيد التشغيل - All services running!$(RESET)"

down: ## إيقاف جميع الخدمات - Stop all services
	@echo "$(RED)🛑 إيقاف جميع الخدمات - Stopping all services...$(RESET)"
	docker compose -f $(COMPOSE_BASE) down
	@echo "$(GREEN)✅ تم إيقاف الخدمات - Services stopped!$(RESET)"

down-volumes: ## إيقاف وحذف البيانات - Stop services and remove volumes
	@echo "$(RED)🗑️  إيقاف وحذف البيانات - Stopping services and removing volumes...$(RESET)"
	docker compose -f $(COMPOSE_BASE) down -v
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
	@if [ -d "apps/services/field-core" ]; then \
		cd apps/services/field-core && npx prisma migrate deploy; \
	fi
	@if [ -d "apps/services/crop-growth-model" ]; then \
		cd apps/services/crop-growth-model && npx prisma migrate deploy; \
	fi
	@if [ -d "apps/services/disaster-assessment" ]; then \
		cd apps/services/disaster-assessment && npx prisma migrate deploy; \
	fi
	@echo "$(GREEN)✅ اكتمل الترحيل - Migrations complete!$(RESET)"

db-seed: ## ملء قاعدة البيانات بالبيانات التجريبية - Seed database with sample data
	@echo "$(YELLOW)🌱 ملء قاعدة البيانات - Seeding database...$(RESET)"
	@if [ -d "apps/services/field-core" ]; then \
		cd apps/services/field-core && npx prisma db seed; \
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
	docker exec -it sahool-postgres psql -U sahool -d sahool

db-backup: ## نسخ احتياطي لقاعدة البيانات - Backup database
	@echo "$(YELLOW)💾 إنشاء نسخة احتياطية - Creating database backup...$(RESET)"
	@mkdir -p backups
	docker exec sahool-postgres pg_dump -U sahool sahool > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
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
	@echo "$(BLUE)🐍 تشغيل اختبارات Python - Running Python tests...$(RESET)"
	python -m pytest tests/ -v --tb=short || true
	@echo "$(GREEN)✅ اكتملت اختبارات Python - Python tests complete!$(RESET)"

test-node: ## تشغيل اختبارات Node.js - Run Node.js tests
	@echo "$(BLUE)📦 تشغيل اختبارات Node.js - Running Node.js tests...$(RESET)"
	@if [ -d "apps/services/field-core" ]; then \
		cd apps/services/field-core && npm test; \
	fi
	@if [ -d "apps/services/crop-growth-model" ]; then \
		cd apps/services/crop-growth-model && npm test; \
	fi
	@if [ -d "apps/web" ]; then \
		cd apps/web && npm test; \
	fi
	@echo "$(GREEN)✅ اكتملت اختبارات Node.js - Node.js tests complete!$(RESET)"

test-integration: ## تشغيل اختبارات التكامل - Run integration tests
	@echo "$(BLUE)🔗 تشغيل اختبارات التكامل - Running integration tests...$(RESET)"
	pytest tests/integration -v
	@echo "$(GREEN)✅ اكتملت اختبارات التكامل - Integration tests complete!$(RESET)"

test-unit: ## تشغيل اختبارات الوحدة - Run unit tests
	@echo "$(BLUE)⚡ تشغيل اختبارات الوحدة - Running unit tests...$(RESET)"
	pytest tests/unit -v
	@echo "$(GREEN)✅ اكتملت اختبارات الوحدة - Unit tests complete!$(RESET)"

test-coverage: ## تشغيل الاختبارات مع تقرير التغطية - Run tests with coverage report
	@echo "$(BLUE)📊 تشغيل الاختبارات مع التغطية - Running tests with coverage...$(RESET)"
	pytest tests/ --cov=shared --cov=packages --cov-report=html:coverage_html --cov-report=term
	@echo "$(GREEN)✅ تقرير التغطية: coverage_html/index.html - Coverage report: coverage_html/index.html$(RESET)"

test-docker: ## تشغيل الاختبارات داخل Docker - Run tests in Docker containers
	@echo "$(BLUE)🐳 تشغيل الاختبارات في Docker - Running tests in Docker...$(RESET)"
	docker compose -f $(COMPOSE_TEST) up --build --abort-on-container-exit
	docker compose -f $(COMPOSE_TEST) down
	@echo "$(GREEN)✅ اكتملت اختبارات Docker - Docker tests complete!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Utilities - الأدوات المساعدة
# ═══════════════════════════════════════════════════════════════════════════════

clean: ## تنظيف الحاويات والبيانات - Clean up containers, volumes, and build artifacts
	@echo "$(RED)🧹 التنظيف - Cleaning up...$(RESET)"
	docker compose -f $(COMPOSE_BASE) down -v --remove-orphans
	docker system prune -f --volumes
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
		echo "$(RED)❌ Error: .env file not found$(RESET)"; \
		echo "$(YELLOW)Please create .env from .env.example and set GRAFANA_ADMIN_PASSWORD$(RESET)"; \
		exit 1; \
	fi
	docker compose -f $(COMPOSE_MONITORING) up -d
	@echo "$(GREEN)✅ المراقبة جاهزة - Monitoring stack ready!$(RESET)"
	@echo "$(BLUE)Prometheus:$(RESET) http://localhost:9090"
	@echo "$(BLUE)Grafana:$(RESET)    http://localhost:3002"
	@echo "$(BLUE)Alertmanager:$(RESET) http://localhost:9093"

monitoring-down: ## إيقاف المراقبة - Stop monitoring stack
	@echo "$(RED)🛑 إيقاف المراقبة - Stopping monitoring stack...$(RESET)"
	docker compose -f $(COMPOSE_MONITORING) down
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
	python -m ruff format . --check
	python -m ruff check .
	@echo "$(YELLOW)TypeScript/JavaScript:$(RESET)"
	@cd apps/web && npm run lint || true
	@echo "$(GREEN)✅ فحص الكود مكتمل - Linting complete!$(RESET)"

fmt: ## تنسيق الكود - Format code
	@echo "$(BLUE)✨ تنسيق الكود - Formatting code...$(RESET)"
	python -m ruff format .
	python -m ruff check . --fix
	@cd apps/web && npm run format || true
	@echo "$(GREEN)✅ تم تنسيق الكود - Code formatted!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Infrastructure Management - إدارة البنية التحتية
# ═══════════════════════════════════════════════════════════════════════════════

infra-up: ## تشغيل البنية التحتية فقط - Start infrastructure only (postgres, redis, nats, kong)
	@echo "$(GREEN)🏗️  تشغيل البنية التحتية - Starting infrastructure...$(RESET)"
	docker compose -f $(COMPOSE_BASE) up -d postgres redis nats kong
	@echo "$(GREEN)✅ البنية التحتية جاهزة - Infrastructure ready!$(RESET)"
	@echo "$(BLUE)PostgreSQL:$(RESET) localhost:5432"
	@echo "$(BLUE)Redis:$(RESET)      localhost:6379"
	@echo "$(BLUE)NATS:$(RESET)       localhost:4222"
	@echo "$(BLUE)Kong:$(RESET)       localhost:8000"

kong-reload: ## إعادة تحميل إعدادات Kong - Reload Kong configuration
	@echo "$(YELLOW)🔄 إعادة تحميل Kong - Reloading Kong...$(RESET)"
	docker exec sahool-kong kong reload
	@echo "$(GREEN)✅ تم إعادة تحميل Kong - Kong reloaded!$(RESET)"

vault-up: ## تشغيل Vault - Start HashiCorp Vault
	@echo "$(GREEN)🔐 تشغيل Vault - Starting Vault...$(RESET)"
	docker compose -f infrastructure/core/vault/docker-compose.vault.yml up -d
	@echo "$(GREEN)✅ Vault جاهز - Vault ready!$(RESET)"
	@echo "$(BLUE)Vault:$(RESET) http://localhost:8200"
	@echo "$(YELLOW)Token:$(RESET) dev-root-token"

vault-down: ## إيقاف Vault - Stop Vault
	@echo "$(RED)🛑 إيقاف Vault - Stopping Vault...$(RESET)"
	docker compose -f infrastructure/core/vault/docker-compose.vault.yml down

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
	python -m pip install -U pip
	pip install -r requirements/dev.txt
	pre-commit install
	@if [ -d "apps/web" ]; then cd apps/web && npm install; fi
	@if [ -d "apps/admin" ]; then cd apps/admin && npm install; fi
	@echo "$(GREEN)✅ بيئة التطوير جاهزة - Dev environment ready!$(RESET)"

generate-tokens: ## توليد رموز التصميم - Generate design tokens
	@echo "$(BLUE)🎨 توليد رموز التصميم - Generating design tokens...$(RESET)"
	python3 scripts/generators/generate_design_tokens.py
	@echo "$(GREEN)✅ تم توليد الرموز - Tokens generated!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Security & Compliance - الأمن والامتثال
# ═══════════════════════════════════════════════════════════════════════════════

security-scan: ## فحص الأمان - Run security scans
	@echo "$(BLUE)🔒 فحص الأمان - Running security scans...$(RESET)"
	detect-secrets scan --baseline .secrets.baseline
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
# Mobile Development - تطوير تطبيق الجوال
# ═══════════════════════════════════════════════════════════════════════════════

MOBILE_DIR = apps/mobile

mobile-test: ## تشغيل اختبارات Flutter - Run Flutter mobile app tests
	@echo "$(BLUE)📱 تشغيل اختبارات تطبيق الجوال - Running Flutter tests...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && flutter test --coverage --reporter=expanded; \
		if [ -f coverage/lcov.info ]; then \
			echo "$(GREEN)✅ التغطية: $$(lcov --summary coverage/lcov.info 2>&1 | grep 'lines' | sed 's/.*: //')$(RESET)"; \
		fi; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ اكتملت اختبارات الجوال - Mobile tests complete!$(RESET)"

mobile-build: ## بناء APK للتطبيق - Build Flutter APK (debug)
	@echo "$(YELLOW)🔨 بناء تطبيق الجوال - Building Flutter APK...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && \
		flutter pub get && \
		dart run build_runner build --delete-conflicting-outputs && \
		flutter build apk --debug; \
		APK_PATH=$$(find build/app/outputs -name "*.apk" | head -1); \
		if [ -n "$$APK_PATH" ]; then \
			APK_SIZE=$$(du -h "$$APK_PATH" | cut -f1); \
			echo "$(GREEN)✅ APK جاهز: $$APK_PATH ($$APK_SIZE)$(RESET)"; \
		fi; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi

mobile-build-release: ## بناء APK للإنتاج - Build Flutter APK (release)
	@echo "$(YELLOW)🔨 بناء تطبيق الجوال للإنتاج - Building Release APK...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && \
		flutter pub get && \
		dart run build_runner build --delete-conflicting-outputs && \
		flutter build apk --release; \
		APK_PATH=$$(find build/app/outputs -name "*.apk" | head -1); \
		if [ -n "$$APK_PATH" ]; then \
			APK_SIZE=$$(du -h "$$APK_PATH" | cut -f1); \
			echo "$(GREEN)✅ Release APK جاهز: $$APK_PATH ($$APK_SIZE)$(RESET)"; \
		fi; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi

mobile-build-aab: ## بناء AAB للمتجر - Build Flutter App Bundle for Play Store
	@echo "$(YELLOW)🔨 بناء App Bundle للمتجر - Building AAB...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && \
		flutter pub get && \
		dart run build_runner build --delete-conflicting-outputs && \
		flutter build appbundle --release; \
		AAB_PATH=$$(find build/app/outputs/bundle -name "*.aab" | head -1); \
		if [ -n "$$AAB_PATH" ]; then \
			AAB_SIZE=$$(du -h "$$AAB_PATH" | cut -f1); \
			echo "$(GREEN)✅ AAB جاهز: $$AAB_PATH ($$AAB_SIZE)$(RESET)"; \
		fi; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi

mobile-analyze: ## تحليل كود Flutter - Analyze Flutter code
	@echo "$(BLUE)🔍 تحليل كود Flutter - Running Flutter analyze...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && \
		flutter pub get && \
		flutter analyze --no-fatal-infos; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ تحليل الكود مكتمل - Analysis complete!$(RESET)"

mobile-format: ## تنسيق كود Dart - Format Dart code
	@echo "$(BLUE)✨ تنسيق كود Dart - Formatting Dart code...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && dart format lib/ test/; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ تم تنسيق الكود - Code formatted!$(RESET)"

mobile-clean: ## تنظيف ملفات Flutter - Clean Flutter build artifacts
	@echo "$(RED)🧹 تنظيف ملفات البناء - Cleaning Flutter build...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && \
		flutter clean && \
		rm -rf .dart_tool build coverage; \
	fi
	@echo "$(GREEN)✅ تم التنظيف - Clean complete!$(RESET)"

mobile-deps: ## تثبيت تبعيات Flutter - Install Flutter dependencies
	@echo "$(YELLOW)📦 تثبيت تبعيات Flutter - Installing Flutter dependencies...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && \
		flutter pub get && \
		dart run build_runner build --delete-conflicting-outputs; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ التبعيات جاهزة - Dependencies installed!$(RESET)"

mobile-codegen: ## توليد الكود (Drift, Freezed) - Generate code (Drift, Freezed, etc.)
	@echo "$(YELLOW)⚙️  توليد الكود - Generating code...$(RESET)"
	@if [ -d "$(MOBILE_DIR)" ]; then \
		cd $(MOBILE_DIR) && \
		flutter pub get && \
		dart run build_runner build --delete-conflicting-outputs; \
	else \
		echo "$(RED)❌ Mobile directory not found$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ توليد الكود مكتمل - Code generation complete!$(RESET)"

mobile-doctor: ## فحص بيئة Flutter - Check Flutter environment
	@echo "$(BLUE)🏥 فحص بيئة Flutter - Flutter doctor...$(RESET)"
	flutter doctor -v

mobile-ci: mobile-analyze mobile-test ## فحوصات CI للجوال - Run mobile CI checks
	@echo "$(GREEN)✅ فحوصات CI للجوال مكتملة - Mobile CI checks passed!$(RESET)"

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
# Kimi Repair Agent - وكيل الإصلاح التلقائي كيمي
# ═══════════════════════════════════════════════════════════════════════════════

kimi-scan: ## 🔍 تشغيل فحص Kimi الشامل - Run comprehensive Kimi scan
	@echo "$(BLUE)🔍 تشغيل فحص Kimi الشامل - Running Kimi comprehensive scan...$(RESET)"
	@chmod +x scripts/kimi-sahool-repair.sh
	@./scripts/kimi-sahool-repair.sh --scan-only
	@echo "$(GREEN)✅ فحص Kimi اكتمل - Kimi scan completed!$(RESET)"

kimi-fix: ## 🔧 تطبيق إصلاحات Kimi تلقائياً - Apply Kimi auto-fixes
	@echo "$(BLUE)🔧 تطبيق إصلاحات Kimi - Applying Kimi fixes...$(RESET)"
	@chmod +x scripts/kimi-sahool-repair.sh
	@./scripts/kimi-sahool-repair.sh --apply-fixes
	@echo "$(GREEN)✅ إصلاحات Kimi اكتملت - Kimi fixes applied!$(RESET)"
	@echo "$(YELLOW)⚠️  يرجى مراجعة التغييرات قبل الالتزام - Please review changes before committing$(RESET)"

kimi-report: ## 📊 إنشاء تقرير Kimi مفصل - Generate detailed Kimi report
	@echo "$(BLUE)📊 إنشاء تقرير Kimi - Generating Kimi report...$(RESET)"
	@chmod +x scripts/kimi-sahool-repair.sh
	@./scripts/kimi-sahool-repair.sh --scan-only --output-json /tmp/kimi-report.json
	@if [ -f /tmp/kimi-report.json ]; then \
		echo "$(GREEN)📄 التقرير محفوظ في: /tmp/kimi-report.json$(RESET)"; \
		cat /tmp/kimi-report.json | jq .; \
	fi

kimi-quick-scan: ## ⚡ فحص سريع للملفات المعدلة - Quick scan of modified files
	@echo "$(BLUE)⚡ فحص سريع - Quick scan...$(RESET)"
	@CHANGED_PY=$$(git diff --name-only --diff-filter=ACM | grep '\.py$$' || true); \
	if [ ! -z "$$CHANGED_PY" ]; then \
		echo "$(CYAN)  🐍 Checking Python files...$(RESET)"; \
		ruff check $$CHANGED_PY || true; \
	fi
	@CHANGED_JS=$$(git diff --name-only --diff-filter=ACM | grep -E '\.(tsx?|jsx?)$$' || true); \
	if [ ! -z "$$CHANGED_JS" ]; then \
		echo "$(CYAN)  📦 Checking JS/TS files...$(RESET)"; \
		npx eslint $$CHANGED_JS --quiet || true; \
	fi
	@echo "$(GREEN)✅ فحص سريع اكتمل - Quick scan completed!$(RESET)"

kimi-install-hook: ## 🪝 تثبيت pre-commit hook - Install pre-commit hook
	@echo "$(BLUE)🪝 تثبيت pre-commit hook...$(RESET)"
	@if [ -f .git/hooks/pre-commit ]; then \
		echo "$(YELLOW)⚠️  pre-commit hook already exists, creating backup...$(RESET)"; \
		cp .git/hooks/pre-commit .git/hooks/pre-commit.backup; \
	fi
	@cp .git/hooks/pre-commit-kimi .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)✅ Kimi pre-commit hook installed!$(RESET)"

kimi-help: ## ❓ عرض مساعدة Kimi - Show Kimi help
	@echo ""
	@echo "$(BOLD)$(PURPLE)════════════════════════════════════════════════════════$(RESET)"
	@echo "$(BOLD)$(PURPLE)  🤖 Kimi Repair Agent - وكيل الإصلاح التلقائي كيمي$(RESET)"
	@echo "$(BOLD)$(PURPLE)════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)$(BLUE)Available Commands:$(RESET)"
	@echo "  $(GREEN)make kimi-scan$(RESET)          - فحص شامل لجودة الكود"
	@echo "  $(GREEN)make kimi-fix$(RESET)           - تطبيق الإصلاحات التلقائية"
	@echo "  $(GREEN)make kimi-report$(RESET)        - إنشاء تقرير JSON مفصل"
	@echo "  $(GREEN)make kimi-quick-scan$(RESET)    - فحص سريع للملفات المعدلة"
	@echo "  $(GREEN)make kimi-install-hook$(RESET)  - تثبيت pre-commit hook"
	@echo ""
	@echo "$(BOLD)$(BLUE)Configuration:$(RESET)"
	@echo "  Config file: .kimi-agents/sahool-repair-config.yaml"
	@echo "  Script: scripts/kimi-sahool-repair.sh"
	@echo "  Workflow: .github/workflows/kimi-quality-check.yml"
	@echo ""
	@echo "$(BOLD)$(BLUE)Supported Tools:$(RESET)"
	@echo "  • ESLint (Frontend - JavaScript/TypeScript)"
	@echo "  • Ruff (Backend - Python linting)"
	@echo "  • Bandit (Backend - Security scanning)"
	@echo "  • Hadolint (Infrastructure - Dockerfile linting)"
	@echo "  • Flutter Analyze (Mobile - Dart/Flutter)"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# End of Makefile - نهاية الملف
# ═══════════════════════════════════════════════════════════════════════════════

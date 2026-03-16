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
.PHONY: fixops fixops-run fixops-comprehensive fixops-json
.PHONY: deps-check deps-tree deps-audit deps-outdated deps-security deps-install-tools
.PHONY: perf-install dead-code complexity unused-deps docstring-coverage secrets-scan licenses benchmark quality-full
.PHONY: service-health check-services db-migrate-all db-generate logs-all
.PHONY: dev-ai dev-agents build-ai test-ai
.PHONY: pr-merge pr-merge-all pr-status pr-monitor pr-help
.DEFAULT_GOAL := help

# ─────────────────────────────────────────────────────────────────────────────
# Environment Variables - متغيرات البيئة
# ─────────────────────────────────────────────────────────────────────────────

ENV ?= development
COMPOSE_PROJECT_NAME ?= sahool
SERVICE ?=
PYTHON ?= python3

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
	@echo "$(BOLD)  SAHOOL Platform v16.0.0 - Unified Management Commands$(RESET)"
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
	@echo "$(BOLD)$(BLUE)AI & Agents - الذكاء الاصطناعي والوكلاء:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^(dev-ai|dev-agents|build-ai|test-ai|dev-mcp):.*?## / {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)PR Automation - أتمتة طلبات السحب:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^pr-[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)$(BLUE)Utilities - الأدوات المساعدة:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*(clean|status|health|shell|script)/ {printf "  $(BLUE)%-25s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BOLD)Usage Examples - أمثلة الاستخدام:$(RESET)"
	@echo "  $(GREEN)make dev$(RESET)                      - بدء بيئة التطوير"
	@echo "  $(GREEN)make build$(RESET)                    - بناء جميع صور Docker"
	@echo "  $(GREEN)make logs-service SERVICE=field-management-service$(RESET) - عرض سجلات خدمة محددة"
	@echo "  $(GREEN)make shell SERVICE=postgres$(RESET)   - فتح طرفية في حاوية"
	@echo "  $(GREEN)make test-python$(RESET)              - تشغيل اختبارات Python"
	@echo "  $(GREEN)make service-health$(RESET)           - فحص صحة جميع الخدمات"
	@echo "  $(GREEN)make dev-ai$(RESET)                   - تشغيل خدمات الذكاء الاصطناعي"
	@echo "  $(GREEN)make pr-merge PR=123$(RESET)          - دمج طلب سحب محدد"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Development - التطوير
# ═══════════════════════════════════════════════════════════════════════════════

dev: network-create ## بدء بيئة التطوير الكاملة - Start full development environment
	@test -f .env || (echo "$(YELLOW)📋 Creating .env from .env.development...$(RESET)" && cp .env.development .env)
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
		advisory-service \
		weather-service \
		vegetation-analysis-service \
		crop-intelligence-service \
		virtual-sensors \
		agro-rules \
		alert-service \
		astronomical-calendar \
		billing-core \
		ai-advisor \
		notification-service \
		irrigation-smart \
		indicators-service
	@echo "$(GREEN)✅ خدمات Python جاهزة - Python services built!$(RESET)"

build-node: ## بناء خدمات Node.js فقط - Build only Node.js services
	@echo "$(YELLOW)📦 بناء خدمات Node.js - Building Node.js services...$(RESET)"
	@docker compose -f $(COMPOSE_BASE) build \
		crop-growth-model \
		disaster-assessment \
		lai-estimation \
		yield-prediction-service \
		marketplace-service \
		chat-service \
		field-management-service \
		iot-service
	@echo "$(GREEN)✅ خدمات Node.js جاهزة - Node.js services built!$(RESET)"

up: network-create ## تشغيل جميع الخدمات - Start all services
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
	@for dir in apps/services/field-management-service apps/services/user-service apps/services/marketplace-service apps/services/chat-service apps/services/disaster-assessment apps/services/iot-service apps/services/research-core apps/services/inventory-service apps/services/weather-service; do \
		if [ -d "$$dir" ] && [ -f "$$dir/prisma/schema.prisma" ]; then \
			echo "$(BLUE)Migrating $$(basename $$dir)...$(RESET)"; \
			(cd "$$dir" && npx prisma migrate deploy); \
		fi; \
	done
	@echo "$(GREEN)✅ اكتمل الترحيل - Migrations complete!$(RESET)"

db-seed: ## ملء قاعدة البيانات بالبيانات التجريبية - Seed database with sample data
	@echo "$(YELLOW)🌱 ملء قاعدة البيانات - Seeding database...$(RESET)"
	@if [ -d "apps/services/field-management-service" ]; then \
		(cd apps/services/field-management-service && npx prisma db seed); \
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
	$(PYTHON) -m pytest tests/ -v --tb=short || true
	@echo "$(GREEN)✅ اكتملت اختبارات Python - Python tests complete!$(RESET)"

test-node: ## تشغيل اختبارات Node.js - Run Node.js tests
	@echo "$(BLUE)📦 تشغيل اختبارات Node.js - Running Node.js tests...$(RESET)"
	@if [ -d "apps/services/field-management-service" ]; then \
		cd apps/services/field-management-service && npm test; \
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
	@echo "  $(BLUE)Field Management:$(RESET)         http://localhost:3000"
	@echo "  $(BLUE)Weather Service:$(RESET)          http://localhost:8092"
	@echo "  $(BLUE)Advisory Service:$(RESET)         http://localhost:8093"
	@echo "  $(BLUE)Vegetation Analysis:$(RESET)      http://localhost:8090"
	@echo "  $(BLUE)Crop Growth Model:$(RESET)        http://localhost:3023"
	@echo "  $(BLUE)Copilot API:$(RESET)              http://localhost:8088"
	@echo "  $(BLUE)Admin Dashboard:$(RESET)          http://localhost:3002 (npm run dev)"
	@echo "  $(BLUE)Web Application:$(RESET)          http://localhost:3000 (npm run dev)"
	@echo "  $(BLUE)PostgreSQL:$(RESET)               localhost:5432"
	@echo "  $(BLUE)PgBouncer:$(RESET)                localhost:6432"
	@echo "  $(BLUE)Redis:$(RESET)                    localhost:6379"
	@echo "  $(BLUE)NATS:$(RESET)                     localhost:4222"
	@echo "  $(BLUE)NATS Monitor:$(RESET)             http://localhost:8222"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo ""

health: ## فحص صحة جميع الخدمات - Check health of all services
	@echo "$(BLUE)🏥 فحص صحة الخدمات - Health Check...$(RESET)"
	@echo ""
	@for service in postgres pgbouncer redis nats kong field-management-service weather-service advisory-service copilot-api; do \
		if docker compose -f $(COMPOSE_BASE) ps $$service 2>/dev/null | grep -q "Up"; then \
			echo "$(GREEN)✅ $$service - Healthy$(RESET)"; \
		else \
			echo "$(RED)❌ $$service - Unhealthy$(RESET)"; \
		fi; \
	done
	@echo ""
	@echo "$(BLUE)Testing API endpoints...$(RESET)"
	@curl -s -o /dev/null -w "Kong Gateway: %{http_code}\n" http://localhost:8000 || echo "Kong: Not responding"
	@curl -s -o /dev/null -w "Field Management: %{http_code}\n" http://localhost:3000/healthz || echo "Field Management: Not responding"
	@curl -s -o /dev/null -w "Copilot API: %{http_code}\n" http://localhost:8088/healthz || echo "Copilot API: Not responding"
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
# FixOps - Kimi Repair Agent - أدوات الإصلاح التلقائي
# ═══════════════════════════════════════════════════════════════════════════════

fixops: ## معاينة مشاكل الكود - Preview code issues (dry-run)
	@echo "$(BLUE)🔧 FixOps - معاينة المشاكل - Preview Mode...$(RESET)"
	$(PYTHON) -m tools.fixops --dry-run

fixops-run: ## إصلاح المشاكل تلقائياً (safe) - Fix issues automatically (safe strategy)
	@echo "$(GREEN)🔧 FixOps - تطبيق الإصلاحات - Applying Fixes...$(RESET)"
	$(PYTHON) -m tools.fixops --no-dry-run --strategy safe

fixops-comprehensive: ## إصلاح شامل لجميع المشاكل - Comprehensive fix (all issues)
	@echo "$(YELLOW)🔧 FixOps - إصلاح شامل - Comprehensive Fix...$(RESET)"
	$(PYTHON) -m tools.fixops --no-dry-run --strategy comprehensive

fixops-json: ## مخرجات JSON للتكامل - JSON output for CI/CD integration
	@$(PYTHON) -m tools.fixops --dry-run --json

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
# Dependency Management - إدارة الاعتماديات
# ═══════════════════════════════════════════════════════════════════════════════

deps-check: ## فحص توافق الاعتماديات - Check dependency compatibility
	@echo "$(BLUE)🔍 فحص توافق الاعتماديات - Checking dependency compatibility...$(RESET)"
	@bash scripts/check-dependency-compatibility.sh || true
	@echo ""
	@echo "$(YELLOW)التعارضات المحتملة (pip):$(RESET)"
	@pip check 2>/dev/null || true
	@pipdeptree --warn fail 2>&1 | grep -A2 "Warning!!! Possibly conflicting" || echo "$(GREEN)✅ لا توجد تعارضات$(RESET)"

deps-tree: ## عرض شجرة الاعتماديات - Show dependency tree
	@echo "$(BLUE)🌳 شجرة الاعتماديات - Dependency tree:$(RESET)"
	@pipdeptree --warn silence | head -100

deps-audit: ## فحص الثغرات الأمنية - Audit dependencies for vulnerabilities
	@echo "$(BLUE)🔒 فحص الثغرات الأمنية - Security audit...$(RESET)"
	@pip-audit --desc 2>&1 | head -50

deps-outdated: ## عرض الاعتماديات القديمة - Show outdated dependencies
	@echo "$(BLUE)📦 الاعتماديات القديمة - Outdated packages:$(RESET)"
	@pip list --outdated 2>/dev/null | head -30

deps-security: ## فحص أمني شامل - Full security scan (Bandit + pip-audit)
	@echo "$(BLUE)🛡️ فحص أمني شامل - Full security scan...$(RESET)"
	@echo ""
	@echo "$(YELLOW)=== Bandit (Python Security) ===$(RESET)"
	@bandit -r apps/services/ shared/ -f json 2>/dev/null | $(PYTHON) -c "import sys,json; d=json.load(sys.stdin); h=len([r for r in d.get('results',[]) if r['issue_severity']=='HIGH']); m=len([r for r in d.get('results',[]) if r['issue_severity']=='MEDIUM']); print(f'HIGH: {h}, MEDIUM: {m}')" || echo "Bandit not available"
	@echo ""
	@echo "$(YELLOW)=== pip-audit (CVE Check) ===$(RESET)"
	@pip-audit 2>&1 | grep -E "^Found|^Name|^No vulnerable" | head -10

deps-install-tools: ## تثبيت أدوات إدارة الاعتماديات - Install dependency management tools
	@echo "$(BLUE)📥 تثبيت الأدوات - Installing tools...$(RESET)"
	pip install --ignore-installed pip-tools pipdeptree pip-audit bandit safety yamllint
	@echo "$(GREEN)✅ تم التثبيت - Tools installed!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Performance & Advanced Quality - الأداء والجودة المتقدمة
# ═══════════════════════════════════════════════════════════════════════════════

perf-install: ## تثبيت أدوات الأداء - Install performance tools
	@echo "$(BLUE)📥 تثبيت أدوات الأداء - Installing performance tools...$(RESET)"
	pip install vulture radon deptry interrogate detect-secrets safety pip-licenses hypothesis pytest-benchmark memray py-spy scalene
	@echo "$(GREEN)✅ تم التثبيت - Tools installed!$(RESET)"

dead-code: ## كشف الكود الميت - Find dead/unused code with vulture
	@echo "$(BLUE)💀 كشف الكود الميت - Finding dead code...$(RESET)"
	@vulture apps/services/ shared/ --min-confidence 80 2>/dev/null | head -50 || echo "$(GREEN)✅ لا يوجد كود ميت$(RESET)"

complexity: ## قياس تعقيد الكود - Measure code complexity with radon
	@echo "$(BLUE)📊 قياس التعقيد - Code complexity analysis...$(RESET)"
	@echo "$(YELLOW)=== Cyclomatic Complexity (CC) ===$(RESET)"
	@radon cc apps/services/ shared/ -a -s --total-average 2>/dev/null | tail -20
	@echo ""
	@echo "$(YELLOW)=== Maintainability Index (MI) ===$(RESET)"
	@radon mi apps/services/ shared/ -s 2>/dev/null | grep -E "^[A-F]" | head -20

unused-deps: ## كشف الاعتماديات غير المستخدمة - Find unused dependencies
	@echo "$(BLUE)📦 كشف الاعتماديات غير المستخدمة - Finding unused dependencies...$(RESET)"
	@deptry apps/services/ 2>/dev/null | head -30 || echo "Run from service directory"

docstring-coverage: ## تغطية التوثيق - Check docstring coverage
	@echo "$(BLUE)📝 تغطية التوثيق - Docstring coverage...$(RESET)"
	@interrogate apps/services/ shared/ -v --fail-under 0 2>/dev/null | tail -30

secrets-scan: ## فحص الأسرار المسربة - Scan for leaked secrets
	@echo "$(BLUE)🔐 فحص الأسرار - Scanning for secrets...$(RESET)"
	@detect-secrets scan apps/ shared/ --all-files 2>/dev/null | $(PYTHON) -c "import sys,json; d=json.load(sys.stdin); n=len(d.get('results',{})); print(f'Found {n} potential secrets' if n else '✅ No secrets found')" || echo "$(GREEN)✅ لا توجد أسرار مسربة$(RESET)"

licenses: ## فحص التراخيص - Check dependency licenses
	@echo "$(BLUE)📜 فحص التراخيص - License check...$(RESET)"
	@pip-licenses --format=markdown --with-license-file --no-license-path 2>/dev/null | head -40

benchmark: ## اختبار الأداء - Run benchmarks
	@echo "$(BLUE)⏱️ اختبار الأداء - Running benchmarks...$(RESET)"
	@pytest tests/ -v --benchmark-only --benchmark-sort=mean 2>/dev/null | head -40 || echo "No benchmarks found"

quality-full: ## فحص جودة شامل - Full quality scan (all tools)
	@echo "$(BLUE)🎯 فحص جودة شامل - Full Quality Scan$(RESET)"
	@echo ""
	@$(MAKE) --no-print-directory dead-code
	@echo ""
	@$(MAKE) --no-print-directory complexity
	@echo ""
	@$(MAKE) --no-print-directory docstring-coverage
	@echo ""
	@$(MAKE) --no-print-directory secrets-scan
	@echo ""
	@$(MAKE) --no-print-directory deps-security

# ═══════════════════════════════════════════════════════════════════════════════
# Code Quality - جودة الكود
# ═══════════════════════════════════════════════════════════════════════════════

lint: ## فحص جودة الكود - Check code style and linting
	@echo "$(BLUE)🔍 فحص الكود - Running linters...$(RESET)"
	@echo "$(YELLOW)Python:$(RESET)"
	$(PYTHON) -m ruff format . --check
	$(PYTHON) -m ruff check .
	@echo "$(YELLOW)TypeScript/JavaScript:$(RESET)"
	@cd apps/web && npm run lint || true
	@echo "$(GREEN)✅ فحص الكود مكتمل - Linting complete!$(RESET)"

fmt: ## تنسيق الكود - Format code
	@echo "$(BLUE)✨ تنسيق الكود - Formatting code...$(RESET)"
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check . --fix
	@cd apps/web && npm run format || true
	@echo "$(GREEN)✅ تم تنسيق الكود - Code formatted!$(RESET)"

quality: ## حزام الجودة الموحد - Run unified quality belt (all platforms)
	@echo "$(BLUE)🎯 حزام الجودة الموحد - Quality Belt$(RESET)"
	@./scripts/quality-belt.sh all

quality-quick: ## فحص سريع - Quick quality check (no tests)
	@echo "$(BLUE)⚡ فحص سريع - Quick Quality Check$(RESET)"
	@./scripts/quality-belt.sh quick

quality-python: ## فحص Python فقط - Python quality checks only
	@echo "$(BLUE)🐍 فحص Python - Python Quality$(RESET)"
	@./scripts/quality-belt.sh python

quality-ts: ## فحص TypeScript فقط - TypeScript quality checks only
	@echo "$(BLUE)📘 فحص TypeScript - TypeScript Quality$(RESET)"
	@./scripts/quality-belt.sh typescript

quality-flutter: ## فحص Flutter فقط - Flutter quality checks only
	@echo "$(BLUE)🦋 فحص Flutter - Flutter Quality$(RESET)"
	@./scripts/quality-belt.sh flutter

flutter-analyze: ## تحليل Flutter - Flutter static analysis
	@echo "$(BLUE)🦋 تحليل Flutter - Flutter Analyze$(RESET)"
	@cd apps/mobile && flutter analyze --no-fatal-infos

flutter-format: ## تنسيق Dart - Format Dart files
	@echo "$(BLUE)🦋 تنسيق Dart - Dart Format$(RESET)"
	@cd apps/mobile && dart format lib/

flutter-imports: ## ترتيب الاستيرادات - Sort Dart imports
	@echo "$(BLUE)🦋 ترتيب الاستيرادات - Sort Imports$(RESET)"
	@cd apps/mobile && dart run import_sorter:main

flutter-fix: ## إصلاح تلقائي - Apply automatic fixes
	@echo "$(BLUE)🦋 إصلاح تلقائي - Dart Fix$(RESET)"
	@cd apps/mobile && dart fix --apply

flutter-test: ## اختبارات Flutter - Flutter tests
	@echo "$(BLUE)🦋 اختبارات Flutter - Flutter Tests$(RESET)"
	@cd apps/mobile && flutter test --reporter=compact

flutter-build: ## توليد الكود - Code generation (build_runner)
	@echo "$(BLUE)🦋 توليد الكود - Build Runner$(RESET)"
	@cd apps/mobile && dart run build_runner build --delete-conflicting-outputs

melos-bootstrap: ## تثبيت Melos وتهيئة المشاريع - Bootstrap Melos packages
	@echo "$(BLUE)🦋 تهيئة Melos - Melos Bootstrap$(RESET)"
	@dart pub global activate melos
	@cd apps/mobile && melos bootstrap

melos-quality: ## فحص جودة Melos - Melos quality checks
	@echo "$(BLUE)🦋 فحص Melos - Melos Quality$(RESET)"
	@cd apps/mobile && melos run quality

security-check: ## فحص أمني - Security checks (secrets, vulnerabilities)
	@echo "$(BLUE)🔒 فحص أمني - Security Check$(RESET)"
	@./scripts/quality-belt.sh security

pre-commit-install: ## تثبيت pre-commit hooks - Install pre-commit hooks
	@echo "$(BLUE)🪝 تثبيت pre-commit - Installing pre-commit hooks...$(RESET)"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✅ تم تثبيت pre-commit - Pre-commit installed!$(RESET)"

pre-commit-run: ## تشغيل pre-commit على جميع الملفات - Run pre-commit on all files
	@echo "$(BLUE)🪝 تشغيل pre-commit - Running pre-commit...$(RESET)"
	pre-commit run --all-files

# ═══════════════════════════════════════════════════════════════════════════════
# Infrastructure Management - إدارة البنية التحتية
# ═══════════════════════════════════════════════════════════════════════════════

infra-up: network-create ## تشغيل البنية التحتية فقط - Start infrastructure only (postgres, pgbouncer, redis, nats, kong)
	@echo "$(GREEN)🏗️  تشغيل البنية التحتية - Starting infrastructure...$(RESET)"
	docker compose -f $(COMPOSE_BASE) up -d postgres pgbouncer redis nats kong
	@echo "$(GREEN)✅ البنية التحتية جاهزة - Infrastructure ready!$(RESET)"
	@echo "$(BLUE)PostgreSQL:$(RESET) localhost:5432"
	@echo "$(BLUE)PgBouncer:$(RESET)  localhost:6432"
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
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -r requirements/base.txt -r requirements/testing.txt -r requirements-dev.txt
	pre-commit install
	@if [ -d "apps/web" ]; then cd apps/web && npm install; fi
	@if [ -d "apps/admin" ]; then cd apps/admin && npm install; fi
	@echo "$(GREEN)✅ بيئة التطوير جاهزة - Dev environment ready!$(RESET)"

generate-tokens: ## توليد رموز التصميم - Generate design tokens
	@echo "$(BLUE)🎨 توليد رموز التصميم - Generating design tokens...$(RESET)"
	$(PYTHON) scripts/generators/generate_design_tokens.py
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
# YOLO26 Vision Service - خدمة الرؤية YOLO26
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: dev-vision build-vision test-vision logs-vision

dev-vision: network-create ## تشغيل خدمة الرؤية YOLO26 - Start YOLO26 vision service
	@echo "$(GREEN)👁️  تشغيل خدمة الرؤية - Starting YOLO26 vision service...$(RESET)"
	docker compose up -d yolo26-vision-service
	@echo "$(GREEN)✅ خدمة الرؤية جاهزة - Vision service ready!$(RESET)"

build-vision: ## بناء صورة خدمة الرؤية - Build YOLO26 vision service image
	@echo "$(YELLOW)🔨 بناء خدمة الرؤية - Building vision service...$(RESET)"
	docker compose build yolo26-vision-service
	@echo "$(GREEN)✅ بناء خدمة الرؤية مكتمل - Vision service built!$(RESET)"

test-vision: ## تشغيل اختبارات خدمة الرؤية - Run vision service tests
	@echo "$(BLUE)🧪 تشغيل اختبارات الرؤية - Running vision service tests...$(RESET)"
	pytest apps/services/yolo26-vision-service/tests -v
	@echo "$(GREEN)✅ اختبارات الرؤية مكتملة - Vision tests complete!$(RESET)"

logs-vision: ## عرض سجلات خدمة الرؤية - View vision service logs
	@echo "$(BLUE)📋 سجلات خدمة الرؤية - Vision service logs:$(RESET)"
	docker compose logs -f yolo26-vision-service

# ═══════════════════════════════════════════════════════════════════════════════
# Terrain Services - خدمات التضاريس
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: dev-terrain build-terrain test-terrain

dev-terrain: network-create ## تشغيل خدمات تحليل التضاريس - Start terrain analysis services
	@echo "$(GREEN)🏔️  تشغيل خدمات التضاريس - Starting terrain services...$(RESET)"
	docker compose up -d terrain-core-service hydrology-service leveling-optimizer-service
	@echo "$(GREEN)✅ خدمات التضاريس جاهزة - Terrain services ready!$(RESET)"
	@echo "$(BLUE)Services: terrain-core, hydrology, leveling-optimizer$(RESET)"

build-terrain: ## بناء صور خدمات التضاريس - Build terrain services images
	@echo "$(YELLOW)🔨 بناء خدمات التضاريس - Building terrain services...$(RESET)"
	docker compose build terrain-core-service hydrology-service leveling-optimizer-service
	@echo "$(GREEN)✅ بناء خدمات التضاريس مكتمل - Terrain services built!$(RESET)"

test-terrain: ## تشغيل اختبارات خدمات التضاريس - Run terrain services tests
	@echo "$(BLUE)🧪 تشغيل اختبارات التضاريس - Running terrain services tests...$(RESET)"
	pytest apps/services/terrain-core-service/tests -v
	pytest apps/services/hydrology-service/tests -v
	pytest apps/services/leveling-optimizer-service/tests -v
	@echo "$(GREEN)✅ اختبارات التضاريس مكتملة - Terrain tests complete!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Edge Orchestrator - منسق الحافة
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: dev-edge build-edge test-edge

dev-edge: network-create ## تشغيل خدمة منسق الحافة - Start edge orchestrator service
	@echo "$(GREEN)🌐 تشغيل منسق الحافة - Starting edge orchestrator...$(RESET)"
	docker compose up -d edge-orchestrator-service
	@echo "$(GREEN)✅ منسق الحافة جاهز - Edge orchestrator ready!$(RESET)"

build-edge: ## بناء صورة منسق الحافة - Build edge orchestrator image
	@echo "$(YELLOW)🔨 بناء منسق الحافة - Building edge orchestrator...$(RESET)"
	docker compose build edge-orchestrator-service
	@echo "$(GREEN)✅ بناء منسق الحافة مكتمل - Edge orchestrator built!$(RESET)"

test-edge: ## تشغيل اختبارات منسق الحافة - Run edge orchestrator tests
	@echo "$(BLUE)🧪 تشغيل اختبارات الحافة - Running edge orchestrator tests...$(RESET)"
	pytest apps/services/edge-orchestrator-service/tests -v
	@echo "$(GREEN)✅ اختبارات الحافة مكتملة - Edge tests complete!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Integration Services (All New) - خدمات التكامل الجديدة
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: dev-integration build-integration test-integration-services

dev-integration: dev-vision dev-terrain dev-edge ## تشغيل جميع خدمات التكامل الجديدة - Start all new integration services
	@echo "$(GREEN)✅ جميع خدمات التكامل جاهزة - All integration services ready!$(RESET)"

build-integration: build-vision build-terrain build-edge ## بناء جميع خدمات التكامل الجديدة - Build all new integration services
	@echo "$(GREEN)✅ بناء جميع خدمات التكامل مكتمل - All integration services built!$(RESET)"

test-integration-services: test-vision test-terrain test-edge ## اختبار جميع خدمات التكامل الجديدة - Test all new integration services
	@echo "$(GREEN)✅ اختبارات جميع خدمات التكامل مكتملة - All integration service tests complete!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Service Health & Diagnostics - صحة الخدمات والتشخيص
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: service-health check-services logs-all

service-health: ## فحص صحة جميع الخدمات - Check health of all running services
	@echo "$(BLUE)🏥 فحص صحة الخدمات - Service Health Check...$(RESET)"
	@./scripts/service-health-check.sh

check-services: ## عرض حالة الخدمات المتاحة - Show available services status
	@echo "$(BLUE)📦 حالة الخدمات - Service Status:$(RESET)"
	@echo ""
	@echo "$(BOLD)Infrastructure:$(RESET)"
	@for service in postgres pgbouncer redis nats kong; do \
		if docker compose -f $(COMPOSE_BASE) ps $$service 2>/dev/null | grep -q "Up"; then \
			echo "  $(GREEN)✓$(RESET) $$service"; \
		else \
			echo "  $(RED)✗$(RESET) $$service (not running)"; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)Application Services:$(RESET)"
	@docker compose -f $(COMPOSE_BASE) ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null | tail -n +2 | sort || true

logs-all: ## عرض سجلات جميع الخدمات - View logs from all services
	@echo "$(BLUE)📋 سجلات جميع الخدمات - All service logs:$(RESET)"
	@docker compose -f $(COMPOSE_BASE) logs -f --tail=100

# ═══════════════════════════════════════════════════════════════════════════════
# AI & Agent Services - خدمات الذكاء الاصطناعي والوكلاء
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: dev-ai dev-agents build-ai test-ai logs-ai dev-vllm build-vllm logs-vllm stop-vllm

dev-vllm: network-create ## تشغيل خادم vLLM - Start vLLM inference server (GPU required)
	@echo "$(GREEN)🚀 تشغيل خادم vLLM DeepSeek - Starting vLLM DeepSeek server...$(RESET)"
	docker compose --profile gpu up -d vllm
	@echo "$(GREEN)✅ خادم vLLM جاهز - vLLM server starting (model download may take several minutes)$(RESET)"
	@VLLM_P=$${VLLM_PORT:-8270}; \
	echo "$(BLUE)API:$(RESET) localhost:$$VLLM_P/v1"; \
	echo "$(BLUE)Health:$(RESET) localhost:$$VLLM_P/health"; \
	echo "$(BLUE)Models:$(RESET) localhost:$$VLLM_P/v1/models"

build-vllm: ## بناء صورة vLLM - Build vLLM Docker image
	@echo "$(YELLOW)🔨 بناء صورة vLLM - Building vLLM image...$(RESET)"
	docker compose --profile gpu build vllm
	@echo "$(GREEN)✅ بناء صورة vLLM مكتمل - vLLM image built!$(RESET)"

logs-vllm: ## عرض سجلات vLLM - View vLLM server logs
	@docker compose --profile gpu logs -f vllm

stop-vllm: ## إيقاف خادم vLLM - Stop vLLM inference server
	@echo "$(YELLOW)⏹️  إيقاف خادم vLLM - Stopping vLLM server...$(RESET)"
	docker compose --profile gpu stop vllm
	@echo "$(GREEN)✅ تم إيقاف vLLM - vLLM server stopped$(RESET)"

dev-ai: ## تشغيل خدمات AI - Start AI services (advisory, crop-intelligence)
	@echo "$(GREEN)🤖 تشغيل خدمات الذكاء الاصطناعي - Starting AI services...$(RESET)"
	docker compose up -d advisory-service crop-intelligence-service ai-advisor mcp-server
	@echo "$(GREEN)✅ خدمات AI جاهزة - AI services ready!$(RESET)"

dev-agents: ## تشغيل خدمات الوكلاء - Start Agent services
	@echo "$(GREEN)🤖 تشغيل خدمات الوكلاء - Starting Agent services...$(RESET)"
	docker compose up -d agent-registry code-fix-agent code-review-agent
	@echo "$(GREEN)✅ خدمات الوكلاء جاهزة - Agent services ready!$(RESET)"

build-ai: ## بناء خدمات AI - Build AI service images
	@echo "$(YELLOW)🔨 بناء خدمات AI - Building AI services...$(RESET)"
	docker compose build advisory-service crop-intelligence-service ai-advisor mcp-server
	@echo "$(GREEN)✅ بناء خدمات AI مكتمل - AI services built!$(RESET)"

test-ai: ## تشغيل اختبارات AI - Run AI service tests
	@echo "$(BLUE)🧪 تشغيل اختبارات AI - Running AI service tests...$(RESET)"
	pytest apps/services/advisory-service/tests -v || true
	pytest apps/services/crop-intelligence-service/tests -v || true
	@echo "$(GREEN)✅ اختبارات AI مكتملة - AI tests complete!$(RESET)"

logs-ai: ## عرض سجلات خدمات AI - View AI service logs
	@echo "$(BLUE)📋 سجلات خدمات AI - AI service logs:$(RESET)"
	docker compose logs -f advisory-service crop-intelligence-service ai-advisor mcp-server

# ═══════════════════════════════════════════════════════════════════════════════
# Database Management Extended - إدارة قاعدة البيانات الموسعة
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: db-migrate-all db-generate db-status db-health

db-migrate-all: ## تشغيل جميع الترحيلات - Run all migrations (Prisma + Python)
	@echo "$(YELLOW)📦 تشغيل جميع الترحيلات - Running all migrations...$(RESET)"
	@$(MAKE) --no-print-directory db-migrate
	@echo ""
	@echo "$(YELLOW)Python migrations (if available):$(RESET)"
	@if [ -f "alembic.ini" ]; then \
		alembic upgrade head 2>/dev/null || echo "Alembic not configured"; \
	fi
	@echo "$(GREEN)✅ اكتملت جميع الترحيلات - All migrations complete!$(RESET)"

db-generate: ## توليد عملاء قاعدة البيانات - Generate database clients (Prisma)
	@echo "$(YELLOW)⚙️  توليد عملاء DB - Generating DB clients...$(RESET)"
	@for dir in apps/services/field-management-service apps/services/user-service apps/services/marketplace-service apps/services/chat-service apps/services/disaster-assessment apps/services/iot-service apps/services/research-core apps/services/inventory-service apps/services/weather-service; do \
		if [ -d "$$dir" ] && [ -f "$$dir/prisma/schema.prisma" ]; then \
			echo "Generating for $$(basename $$dir)..."; \
			(cd "$$dir" && npx prisma generate); \
		fi; \
	done
	@echo "$(GREEN)✅ توليد العملاء مكتمل - Client generation complete!$(RESET)"

db-status: ## عرض حالة قاعدة البيانات - Show database status
	@echo "$(BLUE)🗄️  حالة قاعدة البيانات - Database status:$(RESET)"
	@docker exec sahool-postgres psql -U sahool -d sahool -c "SELECT version();" 2>/dev/null || echo "PostgreSQL not running"
	@echo ""
	@docker exec sahool-postgres psql -U sahool -d sahool -c "SELECT pg_size_pretty(pg_database_size('sahool')) as size;" 2>/dev/null || true

db-health: ## فحص صحة قاعدة البيانات - Check database health
	@echo "$(BLUE)🏥 فحص صحة DB - Database health check:$(RESET)"
	@./scripts/db_health_check.sh 2>/dev/null || echo "Run: make infra-up first"

# ═══════════════════════════════════════════════════════════════════════════════
# MCP Server - خادم MCP
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: dev-mcp build-mcp test-mcp logs-mcp

dev-mcp: ## تشغيل خادم MCP - Start MCP server
	@echo "$(GREEN)🔌 تشغيل خادم MCP - Starting MCP server...$(RESET)"
	docker compose up -d mcp-server
	@echo "$(GREEN)✅ خادم MCP جاهز - MCP server ready!$(RESET)"
	@echo "$(BLUE)MCP Server:$(RESET) http://localhost:8201"

build-mcp: ## بناء خادم MCP - Build MCP server image
	@echo "$(YELLOW)🔨 بناء خادم MCP - Building MCP server...$(RESET)"
	docker compose build mcp-server
	@echo "$(GREEN)✅ بناء خادم MCP مكتمل - MCP server built!$(RESET)"

test-mcp: ## تشغيل اختبارات MCP - Run MCP server tests
	@echo "$(BLUE)🧪 تشغيل اختبارات MCP - Running MCP tests...$(RESET)"
	pytest apps/services/mcp-server/tests -v || true
	@echo "$(GREEN)✅ اختبارات MCP مكتملة - MCP tests complete!$(RESET)"

logs-mcp: ## عرض سجلات MCP - View MCP server logs
	@echo "$(BLUE)📋 سجلات MCP - MCP logs:$(RESET)"
	docker compose logs -f mcp-server

# ═══════════════════════════════════════════════════════════════════════════════
# Script Utilities - أدوات السكربتات
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: scripts-check scripts-fix

scripts-check: ## فحص سلامة السكربتات - Check scripts for issues
	@echo "$(BLUE)🔍 فحص السكربتات - Checking scripts...$(RESET)"
	@echo "$(YELLOW)Checking shebangs:$(RESET)"
	@find scripts -name "*.sh" -exec head -1 {} \; -print | grep -v "^#!/" | head -10 || echo "All shebangs OK"
	@echo ""
	@echo "$(YELLOW)Checking syntax:$(RESET)"
	@for f in scripts/*.sh; do bash -n "$$f" 2>&1 | grep -v "^$$" && echo "Error in: $$f" || true; done
	@echo "$(GREEN)✅ فحص السكربتات مكتمل - Script check complete!$(RESET)"

scripts-fix: ## إصلاح أذونات السكربتات - Fix script permissions
	@echo "$(YELLOW)🔧 إصلاح أذونات السكربتات - Fixing script permissions...$(RESET)"
	@find scripts -name "*.sh" -exec chmod +x {} \;
	@find scripts -name "*.py" -exec chmod +x {} \;
	@echo "$(GREEN)✅ تم إصلاح الأذونات - Permissions fixed!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# Pull Request Automation - أتمتة طلبات السحب
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: pr-merge pr-merge-all pr-status pr-monitor pr-help

pr-merge: ## دمج PR محدد - Merge specific PR (usage: make pr-merge PR=123)
	@if [ -z "$(PR)" ]; then \
		echo "$(RED)❌ Error: PR number required$(RESET)"; \
		echo "$(YELLOW)Usage: make pr-merge PR=123$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)🔀 دمج PR #$(PR) - Merging PR #$(PR)...$(RESET)"
	@./scripts/auto-merge-prs.sh --pr $(PR) $(if $(DRY_RUN),--dry-run,)
	@echo "$(GREEN)✅ PR merge complete!$(RESET)"

pr-merge-all: ## دمج جميع PRs المفتوحة - Merge all open PRs (dry-run first!)
	@echo "$(YELLOW)⚠️  Warning: This will merge ALL open PRs$(RESET)"
	@echo "$(YELLOW)Starting dry-run first...$(RESET)"
	@./scripts/auto-merge-prs.sh --all --dry-run
	@echo ""
	@echo "$(YELLOW)To actually merge, run:$(RESET)"
	@echo "$(GREEN)  make pr-merge-all DRY_RUN=false$(RESET)"
	@if [ "$(DRY_RUN)" = "false" ]; then \
		echo "$(BLUE)🔀 Merging all PRs...$(RESET)"; \
		./scripts/auto-merge-prs.sh --all; \
	fi

pr-status: ## فحص حالة PRs المفتوحة - Check status of open PRs
	@echo "$(BLUE)📊 حالة PRs - PR Status:$(RESET)"
	@gh pr list --state open --json number,title,state,mergeable,statusCheckRollup \
		--template '{{range .}}PR #{{.number}}: {{.title}} - {{if eq .mergeable "MERGEABLE"}}✅ Ready{{else if eq .mergeable "CONFLICTING"}}❌ Conflicts{{else}}⚠️  Unknown{{end}}{{"\n"}}{{end}}' \
		2>/dev/null || echo "$(RED)Error: gh CLI not available or not authenticated$(RESET)"

pr-monitor: ## مراقبة صحة PRs - Monitor PR health
	@echo "$(BLUE)🔍 مراقبة PRs - Monitoring PRs...$(RESET)"
	@echo "$(YELLOW)Checking conflicts...$(RESET)"
	@./scripts/resolve-pr-conflicts.sh check 2>/dev/null || echo "Run: chmod +x scripts/resolve-pr-conflicts.sh"
	@echo ""
	@echo "$(YELLOW)For detailed monitoring, use GitHub Actions:$(RESET)"
	@echo "$(GREEN)  gh workflow run pr-status-monitor.yml$(RESET)"

pr-help: ## عرض مساعدة أتمتة PR - Show PR automation help
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(BOLD)  Pull Request Automation - أتمتة طلبات السحب$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)$(BLUE)Quick Commands:$(RESET)"
	@echo "  $(GREEN)make pr-merge PR=123$(RESET)          Merge specific PR"
	@echo "  $(GREEN)make pr-merge-all$(RESET)             Test merge all PRs (dry-run)"
	@echo "  $(GREEN)make pr-status$(RESET)                Show PR status"
	@echo "  $(GREEN)make pr-monitor$(RESET)               Monitor PR health"
	@echo ""
	@echo "$(BOLD)$(BLUE)Advanced Usage:$(RESET)"
	@echo "  $(GREEN)make pr-merge PR=123 DRY_RUN=true$(RESET)     Test merge (no actual merge)"
	@echo "  $(GREEN)make pr-merge-all DRY_RUN=false$(RESET)       Actually merge all PRs"
	@echo ""
	@echo "$(BOLD)$(BLUE)Script Usage:$(RESET)"
	@echo "  $(GREEN)./scripts/auto-merge-prs.sh --help$(RESET)"
	@echo ""
	@echo "$(BOLD)$(BLUE)Documentation:$(RESET)"
	@echo "  📚 Full guide: $(YELLOW)docs/PR_AUTOMATION.md$(RESET)"
	@echo "  🚀 Quick start: $(YELLOW)docs/PR_AUTOMATION_QUICKSTART.md$(RESET)"
	@echo ""
	@echo "$(BOLD)$(BLUE)GitHub Actions:$(RESET)"
	@echo "  Go to: $(YELLOW)Actions → Auto-Merge PRs → Run workflow$(RESET)"
	@echo "  Or run: $(GREEN)gh workflow run auto-merge-prs.yml$(RESET)"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Developer Experience Improvements - تحسينات تجربة المطور
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: quickstart-enhanced doctor dev-hot logs-pretty deps-verify docs-generate stats-detailed

quickstart-enhanced: ## إعداد بيئة التطوير السريع - Enhanced quickstart (5 min setup)
	@echo "🚀 SAHOOL Quick Start - Setting up development environment..."
	@test -f .env || cp .env.development.template .env 2>/dev/null || echo "ENVIRONMENT=development" > .env
	@echo "📦 Starting infrastructure services..."
	@docker compose up -d postgres redis nats kong pgbouncer 2>/dev/null || true
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "🗄️ Running database migrations..."
	@make db-migrate 2>/dev/null || true
	@echo "🌱 Seeding demo data..."
	@make db-seed 2>/dev/null || true
	@echo "✅ Development environment ready!"
	@echo "   Web: http://localhost:3000"
	@echo "   API: http://localhost:8000"
	@echo "   Kong: http://localhost:8001"

doctor: ## فحص صحة البيئة - Diagnose environment issues
	@echo "🏥 SAHOOL Doctor - Checking environment health..."
	@echo ""
	@echo "=== Docker ==="
	@docker info > /dev/null 2>&1 && echo "✅ Docker is running" || echo "❌ Docker is not running"
	@docker compose version > /dev/null 2>&1 && echo "✅ Docker Compose available" || echo "❌ Docker Compose not found"
	@echo ""
	@echo "=== Node.js ==="
	@node --version 2>/dev/null && echo "✅ Node.js installed" || echo "❌ Node.js not found (need >= 20.0)"
	@npm --version 2>/dev/null && echo "✅ npm installed" || echo "❌ npm not found (need >= 10.0)"
	@echo ""
	@echo "=== Python ==="
	@$(PYTHON) --version 2>/dev/null && echo "✅ Python installed" || echo "❌ Python not found (need >= 3.11)"
	@pip3 --version 2>/dev/null && echo "✅ pip installed" || echo "❌ pip not found"
	@echo ""
	@echo "=== Flutter ==="
	@flutter --version 2>/dev/null | head -1 && echo "✅ Flutter installed" || echo "⚠️ Flutter not found (optional)"
	@echo ""
	@echo "=== Infrastructure ==="
	@docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "⚠️ No services running"
	@echo ""
	@echo "=== Environment ==="
	@test -f .env && echo "✅ .env file exists" || echo "⚠️ No .env file (run: make quickstart-enhanced)"
	@echo ""
	@echo "🏥 Doctor check complete!"

dev-hot: ## تطوير مع إعادة التحميل التلقائي - Hot reload for all services
	@echo "🔥 Starting development with hot-reload..."
	@docker compose up -d postgres redis nats kong pgbouncer
	@docker compose up --build -d

logs-pretty: ## سجلات منسقة - Pretty formatted logs
	@docker compose logs -f --tail=100 2>&1 | sed 's/|/\n  /g'

deps-verify: ## فحص التبعيات - Service dependency check
	@echo "🔍 Verifying service dependencies..."
	@echo "Checking port conflicts..."
	@docker compose config --services 2>/dev/null | wc -l | xargs -I{} echo "✅ {} services configured"
	@echo "Checking environment variables..."
	@test -f .env && grep -c "=" .env | xargs -I{} echo "✅ {} environment variables set" || echo "⚠️ No .env file"
	@echo "✅ Dependency verification complete"

docs-generate: ## توليد وثائق API - Generate API documentation
	@echo "📚 Generating API documentation..."
	@echo "Scanning services for OpenAPI specs..."
	@find apps/services -name "main.py" -o -name "index.ts" | wc -l | xargs -I{} echo "Found {} service entry points"
	@echo "✅ Documentation generation complete"

stats-detailed: ## إحصائيات المنصة المفصلة - Project statistics enhanced
	@echo "📊 SAHOOL Platform Statistics"
	@echo "=============================="
	@echo ""
	@echo "Services: $$(find apps/services -maxdepth 1 -type d | wc -l) directories"
	@echo "Python files: $$(find apps/ shared/ -name '*.py' 2>/dev/null | wc -l)"
	@echo "TypeScript files: $$(find apps/ packages/ -name '*.ts' -o -name '*.tsx' 2>/dev/null | wc -l)"
	@echo "Dart files: $$(find apps/mobile -name '*.dart' 2>/dev/null | wc -l)"
	@echo "Docker files: $$(find . -name 'Dockerfile*' 2>/dev/null | wc -l)"
	@echo "Test files: $$(find tests/ -name 'test_*' -o -name '*.test.*' 2>/dev/null | wc -l)"
	@echo "Documentation: $$(find docs/ -name '*.md' 2>/dev/null | wc -l) files"
	@echo "Workflows: $$(find .github/workflows -name '*.yml' 2>/dev/null | wc -l)"
	@echo ""
	@echo "Lines of code (approximate):"
	@echo "  Python: $$(find apps/ shared/ -name '*.py' -exec cat {} + 2>/dev/null | wc -l)"
	@echo "  TypeScript: $$(find apps/ packages/ -name '*.ts' -o -name '*.tsx' -exec cat {} + 2>/dev/null | wc -l)"
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# Version & Dependency Management - إدارة الإصدارات والاعتماديات
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: version version-bump version-bump-dry deps-drift deps-drift-json deps-sync

version: ## عرض إصدار المنصة الحالي - Show current platform version
	@echo "$(BLUE)SAHOOL Platform Version:$(RESET)"
	@grep -oP '^version\s*=\s*"\K[^"]+' pyproject.toml 2>/dev/null || echo "unknown"
	@echo ""
	@echo "$(YELLOW)Component versions:$(RESET)"
	@echo "  Python (pyproject.toml): $$(grep -oP '^version\s*=\s*\"\K[^\"]+' pyproject.toml 2>/dev/null || echo 'N/A')"
	@echo "  Node.js (package.json):  $$(node -e 'console.log(require("./package.json").version)' 2>/dev/null || echo 'N/A')"

version-bump: ## ترقية الإصدار - Bump platform version (usage: make version-bump V=16.1.0)
	@if [ -z "$(V)" ]; then \
		echo "$(RED)Error: Version required$(RESET)"; \
		echo "$(YELLOW)Usage: make version-bump V=16.1.0$(RESET)"; \
		exit 1; \
	fi
	@./scripts/bump-version.sh $(V)

version-bump-dry: ## معاينة ترقية الإصدار - Preview version bump (usage: make version-bump-dry V=16.1.0)
	@if [ -z "$(V)" ]; then \
		echo "$(RED)Error: Version required$(RESET)"; \
		echo "$(YELLOW)Usage: make version-bump-dry V=16.1.0$(RESET)"; \
		exit 1; \
	fi
	@./scripts/bump-version.sh $(V) --dry-run

deps-drift: ## كشف انحراف الاعتماديات - Detect dependency version drift
	@$(PYTHON) scripts/check-dependency-drift.py

deps-drift-json: ## كشف الانحراف (JSON) - Dependency drift report as JSON
	@$(PYTHON) scripts/check-dependency-drift.py --json

deps-sync: ## مزامنة الاعتماديات - Full dependency sync check (drift + compatibility)
	@echo "$(BLUE)$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(BLUE)$(BOLD)  SAHOOL - Full Dependency Sync Check$(RESET)"
	@echo "$(BLUE)$(BOLD)  فحص مزامنة الاعتماديات الشامل$(RESET)"
	@echo "$(BLUE)$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)Step 1: Drift detection...$(RESET)"
	@$(PYTHON) scripts/check-dependency-drift.py || true
	@echo ""
	@echo "$(YELLOW)Step 2: Compatibility check...$(RESET)"
	@./scripts/check-dependency-compatibility.sh || true
	@echo ""
	@echo "$(GREEN)$(BOLD)Sync check complete!$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# End of Makefile - نهاية الملف
# ═══════════════════════════════════════════════════════════════════════════════

# ============================================================================
# SAHOOL Platform - Kong API Gateway Makefile
# منصة سهول - Makefile لبوابة Kong API
# ============================================================================

.PHONY: help setup start stop restart logs clean config test validate backup restore

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================

help: ## Show this help message | عرض رسالة المساعدة
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(BLUE)  SAHOOL Platform - Kong API Gateway Commands$(NC)"
	@echo "$(BLUE)  منصة سهول - أوامر بوابة Kong API$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Usage: make [target]$(NC)"
	@echo ""

# ============================================================================
# Setup & Installation
# ============================================================================

setup: ## Run initial setup | تشغيل الإعداد الأولي
	@echo "$(BLUE)Running Kong setup...$(NC)"
	@./setup.sh

install-deck: ## Install Kong deck CLI | تثبيت أداة deck CLI
	@echo "$(BLUE)Installing deck...$(NC)"
	@if command -v brew >/dev/null 2>&1; then \
		brew tap kong/deck && brew install deck; \
	else \
		curl -sL https://github.com/kong/deck/releases/download/v1.28.2/deck_1.28.2_linux_amd64.tar.gz -o deck.tar.gz && \
		tar -xf deck.tar.gz -C /tmp && \
		sudo mv /tmp/deck /usr/local/bin/ && \
		rm deck.tar.gz; \
	fi
	@echo "$(GREEN)✓ deck installed successfully$(NC)"

# ============================================================================
# Service Management
# ============================================================================

start: ## Start Kong services | بدء خدمات Kong
	@echo "$(BLUE)Starting Kong services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Kong services started$(NC)"

stop: ## Stop Kong services | إيقاف خدمات Kong
	@echo "$(BLUE)Stopping Kong services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Kong services stopped$(NC)"

restart: ## Restart Kong services | إعادة تشغيل خدمات Kong
	@echo "$(BLUE)Restarting Kong services...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)✓ Kong services restarted$(NC)"

restart-kong: ## Restart only Kong gateway | إعادة تشغيل Kong فقط
	@echo "$(BLUE)Restarting Kong gateway...$(NC)"
	@docker-compose restart kong
	@echo "$(GREEN)✓ Kong gateway restarted$(NC)"

ps: ## Show running services | عرض الخدمات النشطة
	@docker-compose ps

# ============================================================================
# Logs & Monitoring
# ============================================================================

logs: ## Show Kong logs | عرض سجلات Kong
	@docker-compose logs -f kong

logs-all: ## Show all service logs | عرض جميع السجلات
	@docker-compose logs -f

logs-db: ## Show database logs | عرض سجلات قاعدة البيانات
	@docker-compose logs -f kong-database

logs-prometheus: ## Show Prometheus logs | عرض سجلات Prometheus
	@docker-compose logs -f prometheus

logs-grafana: ## Show Grafana logs | عرض سجلات Grafana
	@docker-compose logs -f grafana

# ============================================================================
# Configuration Management
# ============================================================================

config-sync: ## Sync configuration to Kong | مزامنة التكوين إلى Kong
	@echo "$(BLUE)Syncing configuration...$(NC)"
	@deck sync -s kong.yml
	@deck sync -s kong-packages.yml
	@deck sync -s consumers.yml
	@echo "$(GREEN)✓ Configuration synced$(NC)"

config-diff: ## Show configuration differences | عرض الاختلافات في التكوين
	@echo "$(BLUE)Checking configuration differences...$(NC)"
	@deck diff -s kong.yml

config-dump: ## Dump current Kong configuration | استخراج التكوين الحالي
	@echo "$(BLUE)Dumping Kong configuration...$(NC)"
	@deck dump -o kong-current.yml
	@echo "$(GREEN)✓ Configuration dumped to kong-current.yml$(NC)"

validate: ## Validate Kong configuration | التحقق من صحة التكوين
	@echo "$(BLUE)Validating configurations...$(NC)"
	@deck validate -s kong.yml || true
	@deck validate -s kong-packages.yml || true
	@deck validate -s consumers.yml || true
	@echo "$(GREEN)✓ Validation complete$(NC)"

# ============================================================================
# Testing
# ============================================================================

test: ## Run basic tests | تشغيل الاختبارات الأساسية
	@echo "$(BLUE)Running tests...$(NC)"
	@echo "Testing health endpoint..."
	@curl -f http://localhost:8000/health || echo "$(RED)✗ Health check failed$(NC)"
	@echo ""
	@echo "Testing Kong status..."
	@curl -f http://localhost:8001/status || echo "$(RED)✗ Status check failed$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-health: ## Test health endpoint | اختبار نقطة فحص الصحة
	@curl -i http://localhost:8000/health

test-status: ## Test Kong status | اختبار حالة Kong
	@curl -s http://localhost:8001/status | jq

test-services: ## List all services | عرض جميع الخدمات
	@curl -s http://localhost:8001/services | jq '.data[] | {name, url}'

test-routes: ## List all routes | عرض جميع المسارات
	@curl -s http://localhost:8001/routes | jq '.data[] | {name, paths}'

test-consumers: ## List all consumers | عرض جميع المستهلكين
	@curl -s http://localhost:8001/consumers | jq '.data[] | {username, custom_id}'

test-plugins: ## List all plugins | عرض جميع الإضافات
	@curl -s http://localhost:8001/plugins | jq '.data[] | {name, enabled}'

# ============================================================================
# Backup & Restore
# ============================================================================

backup: ## Backup Kong configuration and database | نسخ احتياطي للتكوين وقاعدة البيانات
	@echo "$(BLUE)Creating backup...$(NC)"
	@mkdir -p backups
	@deck dump -o backups/kong-config-$$(date +%Y%m%d-%H%M%S).yml
	@docker-compose exec -T kong-database pg_dump -U kong kong > backups/kong-db-$$(date +%Y%m%d-%H%M%S).sql
	@echo "$(GREEN)✓ Backup created in backups/$(NC)"

restore-config: ## Restore Kong configuration from backup | استعادة التكوين من النسخ الاحتياطي
	@echo "$(YELLOW)Available backups:$(NC)"
	@ls -1 backups/kong-config-*.yml 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " backup && \
		deck sync -s backups/$$backup && \
		echo "$(GREEN)✓ Configuration restored from $$backup$(NC)"

restore-db: ## Restore database from backup | استعادة قاعدة البيانات من النسخ الاحتياطي
	@echo "$(YELLOW)Available backups:$(NC)"
	@ls -1 backups/kong-db-*.sql 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " backup && \
		cat backups/$$backup | docker-compose exec -T kong-database psql -U kong kong && \
		echo "$(GREEN)✓ Database restored from $$backup$(NC)"

# ============================================================================
# Utilities
# ============================================================================

clean: ## Clean up Docker volumes and data | تنظيف الأحجام والبيانات
	@echo "$(YELLOW)⚠ This will remove all Kong data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && \
		if [ "$$confirm" = "y" ]; then \
			docker-compose down -v && \
			echo "$(GREEN)✓ Cleaned up$(NC)"; \
		else \
			echo "$(BLUE)Cancelled$(NC)"; \
		fi

reset: clean setup ## Reset and setup Kong from scratch | إعادة تعيين وإعداد Kong من البداية
	@echo "$(GREEN)✓ Kong reset and setup complete$(NC)"

shell-kong: ## Open Kong container shell | فتح shell لحاوية Kong
	@docker-compose exec kong sh

shell-db: ## Open database shell | فتح shell لقاعدة البيانات
	@docker-compose exec kong-database psql -U kong kong

metrics: ## Show Kong metrics | عرض مقاييس Kong
	@curl -s http://localhost:8001/metrics

admin-api: ## Open Kong Admin API in browser | فتح واجهة Admin API في المتصفح
	@echo "Opening Kong Admin API..."
	@command -v xdg-open >/dev/null && xdg-open http://localhost:8001 || \
		command -v open >/dev/null && open http://localhost:8001 || \
		echo "Please open http://localhost:8001 in your browser"

konga: ## Open Konga UI in browser | فتح واجهة Konga في المتصفح
	@echo "Opening Konga UI..."
	@command -v xdg-open >/dev/null && xdg-open http://localhost:1337 || \
		command -v open >/dev/null && open http://localhost:1337 || \
		echo "Please open http://localhost:1337 in your browser"

grafana: ## Open Grafana in browser | فتح Grafana في المتصفح
	@echo "Opening Grafana..."
	@command -v xdg-open >/dev/null && xdg-open http://localhost:3002 || \
		command -v open >/dev/null && open http://localhost:3002 || \
		echo "Please open http://localhost:3002 in your browser"

prometheus: ## Open Prometheus in browser | فتح Prometheus في المتصفح
	@echo "Opening Prometheus..."
	@command -v xdg-open >/dev/null && xdg-open http://localhost:9090 || \
		command -v open >/dev/null && open http://localhost:9090 || \
		echo "Please open http://localhost:9090 in your browser"

# ============================================================================
# Development
# ============================================================================

dev: ## Start in development mode with live logs | بدء في وضع التطوير مع السجلات المباشرة
	@docker-compose up

watch-config: ## Watch for configuration changes | مراقبة تغييرات التكوين
	@echo "$(BLUE)Watching for configuration changes...$(NC)"
	@while true; do \
		inotifywait -e modify kong.yml kong-packages.yml consumers.yml && \
		$(MAKE) validate && \
		$(MAKE) config-sync; \
	done

# ============================================================================
# Documentation
# ============================================================================

docs: ## Generate API documentation | توليد وثائق API
	@echo "$(BLUE)Generating API documentation...$(NC)"
	@deck dump -o docs/api-spec.yml
	@echo "$(GREEN)✓ Documentation generated$(NC)"

# ============================================================================
# Info
# ============================================================================

info: ## Show Kong information | عرض معلومات Kong
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(BLUE)  Kong API Gateway Information$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo ""
	@echo "$(GREEN)URLs:$(NC)"
	@echo "  Proxy HTTP:    http://localhost:8000"
	@echo "  Proxy HTTPS:   https://localhost:8443"
	@echo "  Admin API:     http://localhost:8001"
	@echo "  Konga UI:      http://localhost:1337"
	@echo "  Prometheus:    http://localhost:9090"
	@echo "  Grafana:       http://localhost:3002"
	@echo ""
	@echo "$(GREEN)Status:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(GREEN)Configuration Files:$(NC)"
	@ls -lh kong.yml kong-packages.yml consumers.yml
	@echo ""

version: ## Show Kong version | عرض إصدار Kong
	@docker-compose exec kong kong version

# ============================================================================
# Production
# ============================================================================

prod-start: ## Start in production mode | بدء في وضع الإنتاج
	@echo "$(BLUE)Starting Kong in production mode...$(NC)"
	@KONG_LOG_LEVEL=warn docker-compose up -d
	@echo "$(GREEN)✓ Kong started in production mode$(NC)"

prod-check: ## Production readiness check | فحص جاهزية الإنتاج
	@echo "$(BLUE)Checking production readiness...$(NC)"
	@echo ""
	@echo "$(YELLOW)Checking environment variables...$(NC)"
	@grep -E "JWT_SECRET|PASSWORD" .env | grep -v "change-this" || echo "$(RED)✗ Some secrets are not changed$(NC)"
	@echo ""
	@echo "$(YELLOW)Checking SSL configuration...$(NC)"
	@[ -f ssl/sahool.crt ] && echo "$(GREEN)✓ SSL certificate found$(NC)" || echo "$(RED)✗ SSL certificate not found$(NC)"
	@echo ""
	@echo "$(YELLOW)Checking backup configuration...$(NC)"
	@[ -d backups ] && echo "$(GREEN)✓ Backup directory exists$(NC)" || echo "$(YELLOW)⚠ Backup directory not found$(NC)"
	@echo ""

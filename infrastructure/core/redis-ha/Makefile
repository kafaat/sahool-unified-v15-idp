# ═══════════════════════════════════════════════════════════════════════════════
# Redis Sentinel Makefile
# ملف إدارة Redis Sentinel
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: help start stop restart status logs health test-failover clean backup restore

# Default target
.DEFAULT_GOAL := help

# Docker Compose file
COMPOSE_FILE := ../../docker-compose.redis-ha.yml
ENV_FILE := .env

# Colors
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

##@ General

help: ## عرض المساعدة / Display this help
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  Redis Sentinel Management Commands"
	@echo "  أوامر إدارة Redis Sentinel"
	@echo "════════════════════════════════════════════════════════════════"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Setup

setup: ## إعداد البيئة / Setup environment
	@echo "$(BLUE)Setting up Redis Sentinel environment...$(NC)"
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "$(YELLOW)Creating .env file from example...$(NC)"; \
		cp .env.example $(ENV_FILE); \
		echo "$(GREEN)✓ Created .env file$(NC)"; \
		echo "$(RED)⚠ Please update REDIS_PASSWORD in .env file!$(NC)"; \
	else \
		echo "$(GREEN)✓ .env file already exists$(NC)"; \
	fi
	@echo "$(GREEN)✓ Setup completed!$(NC)"

##@ Lifecycle

start: ## بدء جميع الخدمات / Start all services
	@echo "$(BLUE)Starting Redis Sentinel cluster...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✓ Redis Sentinel started!$(NC)"
	@echo "$(YELLOW)Waiting for services to be ready...$(NC)"
	@sleep 10
	@$(MAKE) status

stop: ## إيقاف جميع الخدمات / Stop all services
	@echo "$(BLUE)Stopping Redis Sentinel cluster...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✓ Redis Sentinel stopped!$(NC)"

restart: ## إعادة تشغيل / Restart all services
	@echo "$(BLUE)Restarting Redis Sentinel cluster...$(NC)"
	@$(MAKE) stop
	@sleep 2
	@$(MAKE) start

##@ Monitoring

status: ## عرض حالة الخدمات / Show services status
	@echo "$(BLUE)Redis Sentinel Status:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps

logs: ## عرض السجلات / Show logs
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-master: ## عرض سجلات Master / Show master logs
	docker-compose -f $(COMPOSE_FILE) logs -f redis-master

logs-sentinel: ## عرض سجلات Sentinel / Show sentinel logs
	docker-compose -f $(COMPOSE_FILE) logs -f redis-sentinel-1 redis-sentinel-2 redis-sentinel-3

health: ## فحص الصحة / Health check
	@echo "$(BLUE)Running health check...$(NC)"
	@./health-check.sh

##@ Testing

test-failover: ## اختبار Failover / Test failover
	@echo "$(BLUE)Running failover test...$(NC)"
	@./test-failover.sh

test-connection: ## اختبار الاتصال / Test connection
	@echo "$(BLUE)Testing Redis connection...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec redis-master redis-cli -a "$${REDIS_PASSWORD}" ping || \
		echo "$(RED)✗ Connection failed!$(NC)"

##@ Maintenance

clean: ## تنظيف البيانات / Clean up data volumes
	@echo "$(RED)⚠ WARNING: This will delete all Redis data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)Cleaning up...$(NC)"; \
		docker-compose -f $(COMPOSE_FILE) down -v; \
		echo "$(GREEN)✓ Cleanup completed!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

backup: ## نسخ احتياطي / Backup Redis data
	@echo "$(BLUE)Creating backup...$(NC)"
	@mkdir -p backups
	@BACKUP_FILE="backups/redis-backup-$$(date +%Y%m%d-%H%M%S).tar.gz"; \
	docker-compose -f $(COMPOSE_FILE) exec -T redis-master redis-cli -a "$${REDIS_PASSWORD}" --no-auth-warning SAVE; \
	docker run --rm -v sahool-redis-master-data:/data -v $$(pwd)/backups:/backup alpine tar czf /backup/$$(basename $$BACKUP_FILE) -C /data .; \
	echo "$(GREEN)✓ Backup created: $$BACKUP_FILE$(NC)"

restore: ## استعادة من نسخة احتياطية / Restore from backup
	@echo "$(BLUE)Available backups:$(NC)"
	@ls -lh backups/ 2>/dev/null || echo "$(YELLOW)No backups found$(NC)"
	@echo ""
	@read -p "Enter backup filename: " BACKUP_FILE; \
	if [ -f "backups/$$BACKUP_FILE" ]; then \
		echo "$(BLUE)Restoring from $$BACKUP_FILE...$(NC)"; \
		docker-compose -f $(COMPOSE_FILE) stop redis-master; \
		docker run --rm -v sahool-redis-master-data:/data -v $$(pwd)/backups:/backup alpine tar xzf /backup/$$BACKUP_FILE -C /data; \
		docker-compose -f $(COMPOSE_FILE) start redis-master; \
		echo "$(GREEN)✓ Restore completed!$(NC)"; \
	else \
		echo "$(RED)✗ Backup file not found!$(NC)"; \
	fi

##@ Information

info: ## معلومات النظام / System information
	@echo "$(BLUE)Redis Sentinel Information:$(NC)"
	@echo ""
	@echo "$(YELLOW)Master Info:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec -T redis-sentinel-1 redis-cli -p 26379 SENTINEL master sahool-master | grep -E "ip|port|num-slaves|num-other-sentinels|flags" | paste - -
	@echo ""
	@echo "$(YELLOW)Replication Info:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec -T redis-master redis-cli -a "$${REDIS_PASSWORD}" --no-auth-warning INFO replication | grep -E "role|connected_slaves|slave[0-9]"
	@echo ""
	@echo "$(YELLOW)Memory Info:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec -T redis-master redis-cli -a "$${REDIS_PASSWORD}" --no-auth-warning INFO memory | grep -E "used_memory_human|maxmemory_human"

sentinel-info: ## معلومات Sentinel / Sentinel information
	@echo "$(BLUE)Sentinel Information:$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec -T redis-sentinel-1 redis-cli -p 26379 INFO sentinel

##@ Development

shell-master: ## دخول Master / Access master shell
	docker-compose -f $(COMPOSE_FILE) exec redis-master redis-cli -a "$${REDIS_PASSWORD}"

shell-sentinel: ## دخول Sentinel / Access sentinel shell
	docker-compose -f $(COMPOSE_FILE) exec redis-sentinel-1 redis-cli -p 26379

monitor: ## مراقبة الأوامر / Monitor commands
	docker-compose -f $(COMPOSE_FILE) exec redis-master redis-cli -a "$${REDIS_PASSWORD}" MONITOR

stats: ## إحصائيات / Statistics
	docker-compose -f $(COMPOSE_FILE) exec redis-master redis-cli -a "$${REDIS_PASSWORD}" --stat

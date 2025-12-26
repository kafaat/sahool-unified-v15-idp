# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform API Documentation - Makefile
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: help install generate serve start stop restart clean logs all

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  🌾 SAHOOL Platform - API Documentation$(NC)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)════════════════════════════════════════════════════════════════$(NC)"

install: ## Install Python dependencies
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

generate: ## Generate unified OpenAPI spec from running services
	@echo "$(BLUE)Generating OpenAPI specifications...$(NC)"
	python openapi-aggregator.py
	@echo "$(GREEN)✓ Specifications generated$(NC)"

serve: ## Start the documentation server
	@echo "$(BLUE)Starting documentation server...$(NC)"
	docker-compose -f docker-compose.docs.yml up -d
	@echo "$(GREEN)✓ Server started at http://localhost:8888$(NC)"

start: serve ## Alias for 'serve'

stop: ## Stop the documentation server
	@echo "$(BLUE)Stopping documentation server...$(NC)"
	docker-compose -f docker-compose.docs.yml down
	@echo "$(GREEN)✓ Server stopped$(NC)"

restart: stop serve ## Restart the documentation server

logs: ## View documentation server logs
	docker-compose -f docker-compose.docs.yml logs -f api-docs

status: ## Check documentation server status
	@echo "$(BLUE)Documentation Server Status:$(NC)"
	@docker-compose -f docker-compose.docs.yml ps

clean: ## Remove generated files
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	rm -f openapi-unified.yaml openapi-unified.json
	@echo "$(GREEN)✓ Cleaned$(NC)"

all: install generate serve ## Install deps, generate specs, and start server
	@echo ""
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  ✓ All done! Documentation is ready$(NC)"
	@echo "$(GREEN)════════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "Access the documentation at: $(GREEN)http://localhost:8888$(NC)"
	@echo ""

validate: ## Validate the generated OpenAPI spec
	@echo "$(BLUE)Validating OpenAPI specification...$(NC)"
	@if [ ! -f openapi-unified.yaml ]; then \
		echo "$(YELLOW)⚠ openapi-unified.yaml not found. Run 'make generate' first.$(NC)"; \
		exit 1; \
	fi
	@python -c "import yaml; yaml.safe_load(open('openapi-unified.yaml'))" && \
		echo "$(GREEN)✓ YAML is valid$(NC)" || \
		echo "$(YELLOW)✗ YAML validation failed$(NC)"

open: ## Open documentation in browser (requires xdg-open or open command)
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8888 || \
	 command -v open >/dev/null 2>&1 && open http://localhost:8888 || \
	 echo "$(YELLOW)Please open http://localhost:8888 in your browser$(NC)"

# Development targets
dev-install: ## Install development dependencies
	pip install -r requirements.txt
	pip install black flake8 mypy

dev-format: ## Format Python code
	black openapi-aggregator.py

dev-lint: ## Lint Python code
	flake8 openapi-aggregator.py --max-line-length=120
	mypy openapi-aggregator.py --ignore-missing-imports

# Service management helpers
check-services: ## Check which SAHOOL services are running
	@echo "$(BLUE)Checking SAHOOL services...$(NC)"
	@echo ""
	@echo "$(YELLOW)Starter Package:$(NC)"
	@curl -s http://localhost:3000/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) field_core (3000)" || echo "  $(YELLOW)✗$(NC) field_core (3000)"
	@curl -s http://localhost:8108/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) weather_core (8108)" || echo "  $(YELLOW)✗$(NC) weather_core (8108)"
	@curl -s http://localhost:8111/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) astronomical_calendar (8111)" || echo "  $(YELLOW)✗$(NC) astronomical_calendar (8111)"
	@curl -s http://localhost:8105/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) agro_advisor (8105)" || echo "  $(YELLOW)✗$(NC) agro_advisor (8105)"
	@curl -s http://localhost:8110/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) notification_service (8110)" || echo "  $(YELLOW)✗$(NC) notification_service (8110)"
	@echo ""
	@echo "$(YELLOW)Professional Package (sample):$(NC)"
	@curl -s http://localhost:8090/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) satellite_service (8090)" || echo "  $(YELLOW)✗$(NC) satellite_service (8090)"
	@curl -s http://localhost:8095/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) crop_health_ai (8095)" || echo "  $(YELLOW)✗$(NC) crop_health_ai (8095)"
	@curl -s http://localhost:8113/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) inventory_service (8113)" || echo "  $(YELLOW)✗$(NC) inventory_service (8113)"
	@echo ""
	@echo "$(YELLOW)Enterprise Package (sample):$(NC)"
	@curl -s http://localhost:8112/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) ai_advisor (8112)" || echo "  $(YELLOW)✗$(NC) ai_advisor (8112)"
	@curl -s http://localhost:8106/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) iot_gateway (8106)" || echo "  $(YELLOW)✗$(NC) iot_gateway (8106)"
	@curl -s http://localhost:3015/api/v1/healthz >/dev/null 2>&1 && echo "  $(GREEN)✓$(NC) research_core (3015)" || echo "  $(YELLOW)✗$(NC) research_core (3015)"

# Quick commands
quick: generate serve ## Quick: Generate and serve (alias for common workflow)
	@echo "$(GREEN)Ready!$(NC) Docs at http://localhost:8888"

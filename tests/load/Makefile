# SAHOOL Platform - Load Testing Makefile
# Convenient shortcuts for running load tests

.PHONY: help install check smoke load stress spike soak all clean setup-grafana stop-grafana results

# Default target
.DEFAULT_GOAL := help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help message
	@echo ""
	@echo "$(BLUE)SAHOOL Load Testing Suite$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install k6
	@echo "$(BLUE)Installing k6...$(NC)"
	@if command -v brew > /dev/null 2>&1; then \
		brew install k6; \
	elif command -v apt-get > /dev/null 2>&1; then \
		echo "$(YELLOW)Installing k6 on Linux...$(NC)"; \
		sudo gpg -k; \
		sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69; \
		echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list; \
		sudo apt-get update; \
		sudo apt-get install k6; \
	else \
		echo "$(YELLOW)Please install k6 manually: https://k6.io/docs/getting-started/installation/$(NC)"; \
	fi

check: ## Check if services are running
	@echo "$(BLUE)Checking services...$(NC)"
	@./run-tests.sh --check-only

smoke: ## Run smoke test (1 VU, 1 min)
	@echo "$(BLUE)Running smoke test...$(NC)"
	@./run-tests.sh smoke

load: ## Run load test (50 VUs, 10 min)
	@echo "$(BLUE)Running load test...$(NC)"
	@./run-tests.sh load

stress: ## Run stress test (200 VUs, 15 min)
	@echo "$(YELLOW)Warning: This will push the system hard!$(NC)"
	@./run-tests.sh stress

spike: ## Run spike test (10→200 VUs, 8 min)
	@echo "$(BLUE)Running spike test...$(NC)"
	@./run-tests.sh spike

soak: ## Run soak test (20 VUs, 2 hours)
	@echo "$(YELLOW)Warning: This will take 2 hours!$(NC)"
	@./run-tests.sh soak

all: ## Run all tests sequentially
	@echo "$(BLUE)Running all tests...$(NC)"
	@./run-tests.sh all

setup-grafana: ## Start Grafana and InfluxDB for metrics visualization
	@echo "$(BLUE)Starting Grafana and InfluxDB...$(NC)"
	@docker-compose -f docker-compose.load.yml up -d influxdb grafana
	@echo "$(GREEN)Grafana available at: http://localhost:3030$(NC)"
	@echo "$(GREEN)Default credentials: admin/admin$(NC)"

stop-grafana: ## Stop Grafana and InfluxDB
	@echo "$(BLUE)Stopping Grafana and InfluxDB...$(NC)"
	@docker-compose -f docker-compose.load.yml down

docker-smoke: setup-grafana ## Run smoke test in Docker with Grafana
	@echo "$(BLUE)Running smoke test in Docker...$(NC)"
	@docker-compose -f docker-compose.load.yml run --rm k6 run scenarios/smoke.js

docker-load: setup-grafana ## Run load test in Docker with Grafana
	@echo "$(BLUE)Running load test in Docker...$(NC)"
	@docker-compose -f docker-compose.load.yml run --rm k6 run scenarios/load.js

docker-stress: setup-grafana ## Run stress test in Docker with Grafana
	@echo "$(BLUE)Running stress test in Docker...$(NC)"
	@docker-compose -f docker-compose.load.yml run --rm k6 run scenarios/stress.js

docker-spike: setup-grafana ## Run spike test in Docker with Grafana
	@echo "$(BLUE)Running spike test in Docker...$(NC)"
	@docker-compose -f docker-compose.load.yml run --rm k6 run scenarios/spike.js

docker-soak: setup-grafana ## Run soak test in Docker with Grafana
	@echo "$(BLUE)Running soak test in Docker (2 hours)...$(NC)"
	@docker-compose -f docker-compose.load.yml run --rm k6 run scenarios/soak.js

results: ## Show recent test results
	@echo "$(BLUE)Recent test results:$(NC)"
	@ls -lht results/ | head -10 || echo "No results found"

clean: ## Clean up results and temporary files
	@echo "$(BLUE)Cleaning up...$(NC)"
	@rm -rf results/*.json results/*.html
	@echo "$(GREEN)Cleaned up results directory$(NC)"

clean-all: stop-grafana clean ## Stop all services and clean up everything
	@echo "$(BLUE)Cleaning up everything...$(NC)"
	@docker-compose -f docker-compose.load.yml down -v
	@rm -rf results/
	@echo "$(GREEN)Complete cleanup done$(NC)"

# Quick test combinations
quick: smoke ## Run quick smoke test (alias)

full: load stress spike ## Run comprehensive test suite (no soak)

ci: smoke load ## Run tests suitable for CI/CD

# Development helpers
dev-smoke: ## Run smoke test with detailed output
	@k6 run --http-debug scenarios/smoke.js

dev-load: ## Run load test with 10 VUs for development
	@k6 run --vus 10 --duration 2m scenarios/load.js

# Results analysis
analyze: ## Analyze latest test results
	@echo "$(BLUE)Analyzing latest results...$(NC)"
	@latest=$$(ls -t results/*.json | head -1); \
	if [ -n "$$latest" ]; then \
		echo "Latest: $$latest"; \
		jq '.metrics | to_entries[] | select(.key | contains("http_req")) | {key: .key, values: .value.values}' $$latest; \
	else \
		echo "No results found"; \
	fi

# Environment setup
setup: ## Initial setup - create directories and config
	@echo "$(BLUE)Setting up load testing environment...$(NC)"
	@mkdir -p results
	@cp -n .env.example .env 2>/dev/null || true
	@chmod +x run-tests.sh
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "$(YELLOW)Edit .env file to configure your environment$(NC)"

# Info
info: ## Show environment information
	@echo "$(BLUE)Environment Information:$(NC)"
	@echo "k6 version: $$(k6 version 2>/dev/null || echo 'Not installed')"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Results directory: $$(pwd)/results"
	@echo "Test scenarios:"
	@ls -1 scenarios/*.js | sed 's|scenarios/||' | sed 's|.js||'

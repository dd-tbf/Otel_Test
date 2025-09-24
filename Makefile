# Simple OpenTelemetry Python Server Makefile

.PHONY: help setup start stop logs clean test load-test status health

help: ## Show this help message
	@echo "OpenTelemetry Python Server with Datadog Metrics"
	@echo "==============================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Setup environment file from template
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️  Please edit .env and add your DD_API_KEY"; \
	else \
		echo "ℹ️  .env file already exists"; \
	fi

start: setup ## Start all services
	docker compose up -d

stop: ## Stop all services
	docker compose down

logs: ## Show logs for all services
	docker compose logs -f

clean: ## Stop services and remove containers, networks
	docker compose down --volumes --remove-orphans
	docker system prune -f

test: ## Run basic functionality tests
	@echo "🧪 Testing application endpoints..."
	@sleep 5  # Wait for services to start
	@curl -f http://localhost:5000/health || (echo "❌ Health check failed" && exit 1)
	@curl -f http://localhost:5000/ || (echo "❌ Home endpoint failed" && exit 1)
	@curl -f http://localhost:5000/metrics-info || (echo "❌ Metrics info failed" && exit 1)
	@echo "✅ All tests passed!"

load-test: ## Start services with load generator
	docker compose --profile load-test up -d

status: ## Show service status
	@echo "📊 Service Status"
	@echo "================"
	@docker compose ps
	@echo ""
	@echo "🔗 Available Endpoints:"
	@echo "  Application:     http://localhost:5000"
	@echo "  Health:          http://localhost:5000/health"
	@echo "  Metrics Info:    http://localhost:5000/metrics-info"
	@echo "  Collector Health: http://localhost:13133/health"
	@echo "  Collector Metrics: http://localhost:8888/metrics"

health: ## Check health of all services
	@echo "🏥 Health Check Results"
	@echo "======================"
	@echo -n "Application: "
	@curl -s -f http://localhost:5000/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo -n "Collector: "
	@curl -s -f http://localhost:13133/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

metrics: ## Generate some test metrics
	@echo "📈 Generating test metrics..."
	@for i in {1..10}; do \
		curl -s http://localhost:5000/load-test > /dev/null; \
	done
	@curl -s http://localhost:5000/generate-metrics > /dev/null
	@echo "✅ Test metrics generated!"

info: ## Show information about expected Datadog metrics
	@echo "📊 Expected Datadog Metrics"
	@echo "==========================="
	@echo "Application Metrics:"
	@echo "  • http_requests_total (counter) - HTTP request count"
	@echo "  • http_request_duration_seconds (histogram) - Request duration"
	@echo "  • active_connections (gauge) - Active connections"
	@echo "  • cpu_usage_percent (gauge) - CPU usage"
	@echo "  • memory_usage_bytes (gauge) - Memory usage"
	@echo ""
	@echo "System Metrics:"
	@echo "  • system.cpu.utilization (gauge) - System CPU"
	@echo "  • system.memory.utilization (gauge) - System memory"
	@echo "  • system.filesystem.utilization (gauge) - Disk usage"
	@echo ""
	@echo "🔍 Find metrics in Datadog:"
	@echo "  Service: simple-python-server"
	@echo "  Environment: development"
	@echo "  URL: https://app.datadoghq.com/metric/explorer"

restart: ## Restart all services
	docker compose restart

build: ## Rebuild all images
	docker compose build --no-cache
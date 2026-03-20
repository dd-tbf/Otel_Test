# Simple OpenTelemetry Python Server Makefile

.PHONY: help setup start stop logs clean test load-test status

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

metrics: ## Generate some test metrics
	@echo "📈 Generating test metrics..."
	@for i in {1..10}; do \
		curl -s http://localhost:5000/load-test > /dev/null; \
	done
	@curl -s http://localhost:5000/generate-metrics > /dev/null
	@echo "✅ Test metrics generated!"

info: ## Show information about observability signals (metrics, traces, logs)
	@echo "🎯 Observability Signals in Datadog"
	@echo "===================================="
	@echo ""
	@echo "📊 METRICS"
	@echo "Application Metrics:"
	@echo "  • http_requests_total (counter) - HTTP request count"
	@echo "  • http_request_duration_seconds (histogram) - Request duration"
	@echo "  • active_connections (gauge) - Active connections"
	@echo "  • cpu_usage_percent (gauge) - CPU usage"
	@echo "  • memory_usage_bytes (gauge) - Memory usage"
	@echo "System Metrics:"
	@echo "  • system.cpu.utilization (gauge) - System CPU"
	@echo "  • system.memory.utilization (gauge) - System memory"
	@echo "  • system.filesystem.utilization (gauge) - Disk usage"
	@echo ""
	@echo "🔍 TRACES (APM)"
	@echo "  • Automatic Flask request tracing"
	@echo "  • Custom spans for key operations"
	@echo "  • Flame graphs and performance insights"
	@echo "  • Service dependencies and map"
	@echo ""
	@echo "📝 LOGS (Correlated)"
	@echo "  • Structured logs with trace_id and span_id"
	@echo "  • Multiple levels: INFO, WARNING, ERROR"
	@echo "  • Custom fields for filtering"
	@echo "  • Click 'Trace' button to see full trace"
	@echo ""
	@echo "🔍 Find your data in Datadog:"
	@echo "  Service: simple-python-server"
	@echo "  Environment: development"
	@echo ""
	@echo "  Traces: https://app.datadoghq.com/apm/traces?query=service:simple-python-server"
	@echo "  Logs:   https://app.datadoghq.com/logs?query=service:simple-python-server"
	@echo "  Metrics: https://app.datadoghq.com/metric/explorer?query=http_requests_total"
	@echo ""
	@echo "💡 Pro Tip: Click on any error log → 'View Trace' → See complete context!"

restart: ## Restart all services
	docker compose restart

build: ## Rebuild all images
	docker compose build --no-cache

rebuild: ## Rebuild and restart (useful after code changes)
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "✅ Services rebuilt and restarted"

test-observability: ## Test traces, logs, and metrics generation
	@echo "🧪 Testing Observability Features"
	@echo "================================="
	@echo ""
	@echo "📊 Generating test data (traces, logs, metrics)..."
	@for i in {1..20}; do \
		curl -s http://localhost:5000/load-test > /dev/null; \
	done
	@curl -s http://localhost:5000/generate-metrics > /dev/null
	@echo "✅ Generated ~20 traces with correlated logs and metrics"
	@echo ""
	@echo "🔍 Where to find your data in Datadog:"
	@echo "  Traces: https://app.datadoghq.com/apm/traces?query=service:simple-python-server"
	@echo "  Logs:   https://app.datadoghq.com/logs?query=service:simple-python-server"
	@echo "  Metrics: https://app.datadoghq.com/metric/explorer?query=http_requests_total"
	@echo ""
	@echo "💡 Pro Tip: Click on any error log and then 'View Trace' to see correlation!"

logs-app: ## Show application logs (with trace correlation)
	docker compose logs python-server -f

logs-collector: ## Show collector logs
	docker compose logs otel-collector -f
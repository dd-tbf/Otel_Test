# OpenTelemetry Python Server with Datadog Observability

A dockerized Python Flask server demonstrating metrics, traces, and logs with full correlation, exported to Datadog via OpenTelemetry Collector.

## Architecture

```
┌─────────────────────────────────────────┐
│         Python Server (Flask)           │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Metrics  │ │ Traces  │ │  Logs   │   │
│  │ (OTLP)   │ │ (OTLP)  │ │ (File)  │   │
│  └─────┬────┘ └────┬────┘ └────┬────┘   │
│        └───────────┼───────────┘        │
└────────────────────┼────────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │   OpenTelemetry Collector     │
         │  - Receive (OTLP + filelog)   │
         │  - Process (batch, enrich)    │
         │  - Export (Datadog)           │
         └───────────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Datadog Platform   │
              │  - APM (Traces)      │
              │  - Metrics           │
              │  - Logs (correlated) │
              └──────────────────────┘
```

## Quick Start

### 1. Setup Environment

```bash
cp env.example .env
# Edit .env and add your Datadog API key
```

### 2. Start Services

```bash
# Start core services
docker compose up -d

# Or start with load generator
docker compose --profile load-test up -d
```

### 3. Verify Setup

```bash
docker compose ps
curl http://localhost:5000/health
```

## Metrics Generated

This project generates the following metrics in Datadog:

### Custom Application Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests. Tags: `method`, `endpoint`, `status_code` |
| `http_request_duration_seconds` | Histogram | Request processing time. Includes p50, p95, p99 percentiles |
| `active_connections` | UpDownCounter | Current active connections |
| `cpu_usage_percent` | Gauge | Simulated CPU usage (10-90%) |
| `memory_usage_bytes` | Gauge | Simulated memory usage (100-500MB) |

### APM Metrics (from Datadog Connector)

These are auto-generated from traces:

| Metric Name | Type | Description |
|-------------|------|-------------|
| `trace.opentelemetry.instrumentation.flask.server.hits` | Counter | Request count per endpoint |
| `trace.opentelemetry.instrumentation.flask.server.duration` | Histogram | Request latency |
| `trace.opentelemetry.instrumentation.flask.server.errors` | Counter | Error counts |

### System Metrics (from Collector)

| Metric Name | Type | Description |
|-------------|------|-------------|
| `system.cpu.utilization` | Gauge | Actual system CPU utilization |
| `system.memory.utilization` | Gauge | Actual system memory utilization |
| `system.filesystem.utilization` | Gauge | Filesystem usage percentage |

## Observability Signals

### Metrics
- Custom application metrics (counters, histograms, gauges)
- APM metrics auto-generated from traces via Datadog connector
- System metrics from the collector's hostmetrics receiver

### Distributed Traces
- Automatic Flask request tracing via `FlaskInstrumentor`
- Custom spans for key operations
- Service dependency visualization

### Structured Logs
- Every log includes `trace_id` and `span_id` for correlation
- Multiple log levels: INFO, WARNING, ERROR
- Logs written to file, collected by OTel Collector's filelog receiver

### Correlation
- Logs link to traces via `trace_id`
- Traces link to logs via span context
- Metrics can be explored alongside related traces

## Makefile Commands

Run `make help` for a full list of targets with short descriptions.

### Setup and Deployment

```bash
make setup      # Create .env from template
make start      # Start all services
make load-test  # Start with load generator
make build      # Rebuild all images
make rebuild    # Stop, rebuild, and restart
```

### Service Management

```bash
make stop       # Stop all services
make restart    # Restart services
make clean      # Stop and remove containers/volumes
```

### Monitoring

```bash
make status     # Show service status
make test       # Run basic endpoint checks (/health, /, /metrics-info)
make logs       # Show real-time logs
make logs-app   # Show Python server logs
make logs-collector  # Show collector logs
make info       # Show observability signals reference
```

The collector image includes a Docker `HEALTHCHECK` (HTTP probe on port 13133), so `docker compose ps` may show the collector as `(healthy)` after it starts.

### Testing

```bash
make test       # Run basic tests
make metrics    # Generate test metrics
make test-observability  # Generate sample data for all signals
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Home page, generates basic metrics and trace |
| `GET /health` | Health check |
| `GET /load-test` | Variable response time, 10% error rate |
| `GET /generate-metrics` | Generate batch of test metrics |
| `GET /metrics-info` | Get metrics information |

### Debug Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET localhost:13133/health` | Collector health |
| `GET localhost:8888/metrics` | Collector metrics (Prometheus format) |

## How It Works

### Automatic Instrumentation

**Flask Tracing:**
```python
FlaskInstrumentor().instrument_app(app)
```
Every HTTP request automatically creates a trace with method, path, status code, and duration.

**Log Correlation:**
```python
LoggingInstrumentor().instrument(set_logging_format=True)
```
Automatically adds `trace_id` and `span_id` to all log records.

### Manual Instrumentation

**Custom Spans:**
```python
with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("key", "value")
```

**Structured Logging:**
```python
logger.error("Error message", extra={"endpoint": "/api", "error_type": "validation"})
```
The `extra` dict becomes searchable attributes in Datadog.

### Datadog Connector

The collector uses the Datadog connector to generate APM metrics from traces:

```yaml
connectors:
  datadog/connector:

service:
  pipelines:
    traces:
      exporters: [datadog, datadog/connector]
    metrics:
      receivers: [otlp, hostmetrics, datadog/connector]
```

This enables standard APM metrics without code changes.

### Resource Attributes

All signals share these attributes for consistent tagging:
- `service.name`: Service identifier
- `deployment.environment`: Environment (development, production)
- `service.version`: Application version

## Troubleshooting

### Check Logs

```bash
docker compose logs otel-collector    # Collector logs
docker compose logs python-server     # Application logs
```

### Verify Export

```bash
docker compose logs otel-collector | grep -i "datadog"
docker compose logs otel-collector | grep -i "metrics"
docker compose logs otel-collector | grep -i "traces"
```

### Verify services manually

```bash
curl http://localhost:5000/health      # Application
curl http://localhost:13133/health     # Collector
docker compose ps                       # Service status
```

## Key Features

- Simple single-command setup via Docker Compose
- Full observability: metrics, traces, and logs with correlation
- Automatic Flask instrumentation for tracing
- Trace-log correlation via OpenTelemetry
- APM metrics auto-generated from traces
- Log rotation (10MB cap with automatic cleanup)
- Optional continuous load generation for testing
- Debug output for all exported data

---

Metrics, traces, and logs should appear in Datadog within 1-2 minutes of starting the services.

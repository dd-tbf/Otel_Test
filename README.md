# Simple OpenTelemetry Python Server with Full Datadog Observability

A complete dockerized Python Flask server demonstrating **metrics, traces, and logs** with full correlation, exported to Datadog via OpenTelemetry Collector.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Python Server (Flask)           │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐ │
│  │ Metrics  │ │ Traces  │ │  Logs   │ │
│  │ (OTLP)   │ │ (OTLP)  │ │ (OTLP)  │ │
│  └─────┬────┘ └────┬────┘ └────┬────┘ │
│        └───────────┼──────────┬─┘      │
└────────────────────┼──────────┼────────┘
                     │          │
                     ▼          ▼
         ┌───────────────────────────────┐
         │   OpenTelemetry Collector     │
         │  • Receive (OTLP)             │
         │  • Process (batch, enrich)    │
         │  • Export (Datadog)           │
         └───────────────┬───────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Datadog Platform   │
              │  • APM (Traces)      │
              │  • Metrics           │
              │  • Logs (correlated) │
              │  • Service Map       │
              └──────────────────────┘
```

## 🎯 Observability Signals

This project demonstrates all three pillars of observability:

### 📊 **Metrics**
- **Custom application metrics** - You define and control
  - HTTP request counters (`http_requests_total`)
  - Request duration histograms (`http_request_duration_seconds`)
  - Active connections gauge (`active_connections`)
  - Simulated resource usage (CPU, memory)
- **APM metrics** - Auto-generated from traces via Datadog connector
  - Request hits per endpoint (`trace.opentelemetry.instrumentation.flask.server.hits`)
  - Request duration (`trace.opentelemetry.instrumentation.flask.server.duration`)
  - Error counts (`trace.opentelemetry.instrumentation.flask.server.errors`)
- **System metrics** - Real host metrics from collector
  - CPU, memory, and disk usage

### 🔍 **Distributed Traces**
- **Automatic instrumentation** - Flask requests auto-traced
- **Custom spans** - Manual instrumentation for key operations
- **Service dependencies** - Visualize request flow
- **Performance insights** - Identify bottlenecks and slow endpoints

### 📝 **Structured Logs**
- **Correlated logging** - Every log includes `trace_id` and `span_id`
- **Contextual information** - Rich metadata with each log entry
- **Multiple log levels** - INFO, WARNING, ERROR for different scenarios
- **Stdout output** - Logs visible in container logs and forwarded to Datadog

### 🔗 **Correlation**
The magic happens when all three signals work together:
- **Logs → Traces**: Click a log to see the full trace
- **Traces → Logs**: View all logs for a specific trace
- **Metrics → Traces**: Jump from metric spike to example traces
- **Service Map**: Visualize dependencies and health

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env and add your Datadog API key
nano .env
```

### 2. Start Services
```bash
# Start core services
docker compose up -d

# Or start with load generator for testing
docker compose --profile load-test up -d
```

### 3. Verify Setup
```bash
# Check service status
docker compose ps

# Test the application
curl http://localhost:5000
curl http://localhost:5000/metrics-info
```

## 🛠️ Using the Makefile

This project includes a Makefile that simplifies common tasks. Below are all available commands:

### Getting Help
```bash
# Show all available commands with descriptions
make help
```

### Setup and Deployment
```bash
# Create .env file from template (automatically done by 'make start')
make setup

# Start all services (automatically runs setup if needed)
make start

# Start services with load generator for testing
make load-test

# Rebuild all images from scratch
make build
```

### Service Management
```bash
# Stop all services
make stop

# Restart all services (without rebuilding)
make restart

# Stop services and remove containers, networks, and volumes
make clean
```

### Monitoring and Debugging
```bash
# Show service status and available endpoints
make status

# Check health of all services (application + collector)
make health

# Show real-time logs for all services
make logs

# Show information about expected Datadog metrics
make info
```

### Testing
```bash
# Run basic functionality tests
make test

# Generate test metrics manually
make metrics
```

### Common Workflows

**First time setup:**
```bash
make setup  # Creates .env file
# Edit .env to add your DD_API_KEY
make start  # Starts all services
make status # Verify everything is running
```

**Daily development:**
```bash
make start   # Start services
make logs    # Monitor logs
make health  # Check service health
make stop    # Stop when done
```

**Testing metrics:**
```bash
make start       # Start services
make metrics     # Generate test data
make info        # Show expected metrics
# Check Datadog dashboard for metrics
```

**Load testing:**
```bash
make load-test   # Start with continuous load generator
make logs        # Watch requests being made
# Metrics will continuously flow to Datadog
```

**Cleanup:**
```bash
make clean  # Complete cleanup of all containers and volumes
```

## 📊 Metrics Available in Datadog

Once the services are running, you should see the following metrics in your Datadog dashboard:

### 🔹 **Application Metrics**

#### 1. **HTTP Request Counter**: `http_requests_total`
- **Type**: Counter
- **Description**: Total number of HTTP requests received
- **Tags**: 
  - `method` (GET, POST, etc.)
  - `endpoint` (/, /health, /load-test, etc.)
  - `status_code` (200, 404, 500, etc.)
  - `server` (simple-python-server)
  - `env` (development)
  - `version` (1.0.0)

#### 2. **HTTP Request Duration**: `http_request_duration_seconds`
- **Type**: Histogram
- **Description**: HTTP request processing time in seconds
- **Tags**: Same as above
- **Percentiles**: p50, p95, p99 automatically calculated

#### 3. **Active Connections**: `active_connections`
- **Type**: Gauge (UpDownCounter)
- **Description**: Number of active connections to the server
- **Tags**: `server`, `env`, `version`

#### 4. **CPU Usage**: `cpu_usage_percent`
- **Type**: Gauge
- **Description**: Simulated CPU usage percentage
- **Range**: 10% - 90%

#### 5. **Memory Usage**: `memory_usage_bytes`
- **Type**: Gauge  
- **Description**: Simulated memory usage in bytes
- **Range**: 100MB - 500MB

### 🔹 **System Metrics** (from collector)

#### 6. **System CPU Utilization**: `system.cpu.utilization`
- **Type**: Gauge
- **Description**: Actual system CPU utilization
- **Tags**: `cpu` (cpu core identifier)

#### 7. **System Memory Utilization**: `system.memory.utilization`
- **Type**: Gauge
- **Description**: Actual system memory utilization
- **Tags**: `state` (used, free, available, etc.)

#### 8. **Filesystem Utilization**: `system.filesystem.utilization`
- **Type**: Gauge
- **Description**: Filesystem usage percentage
- **Tags**: `device`, `fstype`, `mountpoint`

## 🎯 Testing Endpoints

### Application Endpoints
```bash
# Home page - generates basic metrics
curl http://localhost:5000/

# Health check - minimal metrics
curl http://localhost:5000/health

# Load test - generates variable response times and occasional errors
curl http://localhost:5000/load-test

# Generate batch metrics - creates multiple metric points
curl http://localhost:5000/generate-metrics

# Get metrics information
curl http://localhost:5000/metrics-info
```

### Debug Endpoints
```bash
# Collector health
curl http://localhost:13133/health

# Collector metrics (Prometheus format)
curl http://localhost:8888/metrics
```

### Viewing Observability Data

After making requests, view them in Datadog:

**1. View Traces (APM):**
```bash
# Make some requests
curl http://localhost:5000/
curl http://localhost:5000/load-test

# Then go to: https://app.datadoghq.com/apm/traces
# Filter: service:simple-python-server env:development
```

**2. View Logs:**
```bash
# Make requests that generate different log levels
for i in {1..20}; do curl http://localhost:5000/load-test; done

# Then go to: https://app.datadoghq.com/logs
# Filter: service:simple-python-server
# You'll see INFO, WARNING, and ERROR logs
# Click on any log → Click "Trace" to see the full trace!
```

**3. View Metrics:**
```bash
# Generate metrics
curl http://localhost:5000/generate-metrics

# Then go to: https://app.datadoghq.com/metric/explorer
# Search: http_requests_total
```

**4. Correlation Demo:**
```bash
# This will generate errors with correlated traces and logs
for i in {1..50}; do 
  curl -s http://localhost:5000/load-test
  sleep 0.5
done

# In Datadog:
# 1. Logs Explorer → Filter status:error
# 2. Click on an error log
# 3. Click "View Trace" button
# 4. See the full trace with timing and all spans
# 5. Click on error span → "Logs" tab → See all logs from that request
```

## 📈 Expected Datadog Dashboard Views

### 1. **Request Rate Dashboard**
- **Graph**: `http_requests_total` rate per second
- **Breakdown**: By endpoint, method, status code
- **Alerts**: Set up alerts for error rates > 5%

### 2. **Response Time Dashboard** 
- **Graph**: `http_request_duration_seconds` percentiles (p50, p95, p99)
- **Heatmap**: Request duration distribution
- **SLA**: Track requests under 500ms

### 3. **System Resources Dashboard**
- **CPU**: `cpu_usage_percent` and `system.cpu.utilization`
- **Memory**: `memory_usage_bytes` and `system.memory.utilization`
- **Connections**: `active_connections` over time

### 4. **Service Map**
- Shows the flow: `simple-python-server` → `otel-collector` → `datadog`
- Service health and dependencies

## 🔍 Finding Your Data in Datadog

### 1. **APM & Traces** 🔍
- **URL**: https://app.datadoghq.com/apm/traces
- **Service**: `simple-python-server`
- **Environment**: `development`
- **Features**:
  - View all traces and individual requests
  - See latency distribution and error rates
  - Analyze flame graphs for performance
  - Click on spans to see associated logs

### 2. **Logs Explorer** 📝
- **URL**: https://app.datadoghq.com/logs
- **Filters**: 
  - `service:simple-python-server`
  - `env:development`
- **Features**:
  - Search logs by message, level, or custom fields
  - Click "View Trace" to see full distributed trace
  - Filter by ERROR, WARNING, INFO levels
  - See trace_id and span_id in log attributes

### 3. **Metrics Explorer** 📊
- **URL**: https://app.datadoghq.com/metric/explorer
- **Search for**: `http_requests_total`, `cpu_usage_percent`, etc.
- **Filter by**: `env:development`, `service:simple-python-server`
- **Features**:
  - Graph metrics over time
  - Click on anomalies to see example traces
  - Create custom dashboards

### 4. **Service Catalog** 🗂️
- **URL**: https://app.datadoghq.com/services
- **Look for**: `simple-python-server` service
- **Environment**: `development`
- **Features**:
  - Service overview with key metrics
  - Service dependencies and map
  - Related traces, logs, and metrics in one place

### 5. **Service Map** 🗺️
- **URL**: https://app.datadoghq.com/apm/map
- **Features**:
  - Visual representation of service dependencies
  - Health status of each service
  - Request flow and volume

### 6. **Custom Dashboards** 📈
Create a dashboard combining all signals:

```json
{
  "widgets": [
    {
      "definition": {
        "title": "Request Rate",
        "type": "timeseries",
        "requests": [
          {
            "q": "sum:http_requests_total{env:development,service:simple-python-server}.as_rate()"
          }
        ]
      }
    },
    {
      "definition": {
        "title": "APM Request Latency",
        "type": "timeseries",
        "requests": [
          {
            "q": "avg:trace.opentelemetry.instrumentation.flask.server.duration{env:development,service:simple-python-server}"
          }
        ]
      }
    },
    {
      "definition": {
        "title": "Error Logs",
        "type": "log_stream",
        "query": "service:simple-python-server status:error"
      }
    }
  ]
}
```

## 🔗 Correlating Traces and Logs in Datadog

One of the most powerful features is the automatic correlation between traces and logs:

### How It Works

**In the Code:**
- Every log automatically includes `trace_id` and `span_id` from the active span
- OpenTelemetry's LoggingInstrumentor adds trace context to Python logs
- Logs are formatted with: `trace_id=<id> span_id=<id>`

**In Datadog:**
1. **From Logs to Traces:**
   - Open a log in Logs Explorer
   - Click the "Trace" button (appears automatically if trace_id exists)
   - See the complete distributed trace for that log entry

2. **From Traces to Logs:**
   - Open a trace in APM
   - Click on any span
   - Click "Logs" tab
   - See all logs emitted during that span execution

3. **Example Workflow:**
   ```bash
   # Generate some traffic
   curl http://localhost:5000/load-test
   ```
   
   Then in Datadog:
   - Go to **Logs**: Filter for `service:simple-python-server status:error`
   - Click on an error log
   - Click **"View Trace"** → See the full request trace
   - Click on the trace span → See all related logs
   - Navigate to **Metrics** → See spike in error rate at same time

### Correlation Example

**Log Entry:**
```json
{
  "message": "Simulated error occurred during load test",
  "service": "simple-python-server",
  "env": "development",
  "status": "error",
  "trace_id": "abc123...",   ← Links to trace
  "span_id": "def456...",    ← Links to specific span
  "endpoint": "/load-test",
  "error_type": "simulated_500"
}
```

**Corresponding Trace:**
- Service: `simple-python-server`
- Trace ID: `abc123...`
- Duration: 234ms
- Error: Yes
- Spans: Flask request → load_test endpoint
- All logs with matching trace_id are linked!

### Testing Correlation

1. **Generate an error:**
   ```bash
   # Keep making requests until you get a 500 error (10% chance)
   for i in {1..20}; do curl http://localhost:5000/load-test; done
   ```

2. **Find it in Datadog Logs:**
   - Go to Logs Explorer
   - Filter: `service:simple-python-server status:error`
   - Click on the error log

3. **View the trace:**
   - Click the **"Trace"** button in the log details
   - See the full request flow, timing, and all spans

4. **Verify correlation:**
   - In the trace view, click on the error span
   - Click **"Logs"** tab
   - See all logs from that request (INFO → ERROR progression)

## 🧪 Load Testing

### Automatic Load Generation
```bash
# Start with continuous load generation
docker compose --profile load-test up -d

# Check logs to see requests being made
docker compose logs -f load-generator
```

### Manual Load Testing
```bash
# Generate multiple requests
for i in {1..50}; do
  curl -s http://localhost:5000/load-test > /dev/null &
done
wait

# Generate batch metrics
curl http://localhost:5000/generate-metrics
```

## 🛠️ Configuration

### Datadog Sites
Update `DD_SITE` in your `.env` file:
- **US1**: `datadoghq.com` (default)
- **US3**: `us3.datadoghq.com`
- **EU**: `datadoghq.eu`
- **AP1**: `ap1.datadoghq.com`

### Metric Export Frequency
- **Application metrics**: Every 5 seconds
- **System metrics**: Every 30 seconds
- **Batch size**: 512 metrics per export

### Environment Variables
```bash
DD_API_KEY=your_api_key          # Required
DD_SITE=datadoghq.com           # Your Datadog site
DD_ENV=development              # Environment tag
DD_VERSION=1.0.0                # Version tag
SERVICE_NAME=simple-python-server # Service name
```

## 🧪 Testing Configuration Changes

When experimenting with OpenTelemetry Collector configuration, you don't need to rebuild the entire stack:

### 🚀 **Most Efficient Approach (Recommended)**
After updating `collector/otel-collector-config.yaml`, just restart the collector service:

```bash
# After editing otel-collector-config.yaml
docker compose restart otel-collector

# Check if changes took effect
docker logs otel-collector --tail=20
```

### 🔄 **Alternative Approaches**

**Option 1**: Stop and start collector only
```bash
docker compose stop otel-collector
docker compose start otel-collector
```

**Option 2**: Full restart (if you want to be extra safe)
```bash
docker compose down
docker compose up -d
```

**Option 3**: If you changed the Dockerfile too
```bash
docker compose down
docker compose build otel-collector --no-cache
docker compose up -d
```

### ⚡ **Why This Works**

Your config file is mounted as a volume:
- ✅ **File changes are immediately available** in the container
- ⚠️ **Collector needs restart** to reload configuration (no hot-reload)
- ✅ **No rebuild needed** unless Dockerfile changes
- ✅ **Python app keeps running** during collector restart

### 🔬 **Quick Test Workflow**
1. Edit `collector/otel-collector-config.yaml`
2. Run: `docker compose restart otel-collector`
3. Check logs: `docker logs otel-collector --tail=20`
4. Generate test data: `curl http://localhost:5000/generate-metrics`
5. Verify in logs or Datadog

## 🎓 How Observability Is Implemented

### Automatic Instrumentation

**Flask Auto-Instrumentation:**
```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)  # Automatic tracing!
```
- Every HTTP request automatically creates a trace
- Span includes: method, path, status code, duration
- No manual code needed for basic tracing

**Logging Auto-Instrumentation:**
```python
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=True)
```
- Automatically adds `trace_id` and `span_id` to all log records
- Works with Python's standard `logging` module
- Enables correlation between logs and traces

### Manual Instrumentation

**Custom Spans:**
```python
with tracer.start_as_current_span("generate_test_metrics") as span:
    span.set_attribute("metrics.count", num_metrics)
    # Your code here
```
- Add custom spans for important operations
- Set custom attributes for filtering and analysis
- Nested spans show operation hierarchy

**Structured Logging:**
```python
logger.error(
    "Simulated error occurred",
    extra={
        "endpoint": "/load-test",
        "error_type": "simulated_500"
    }
)
```
- `extra` dict becomes searchable log attributes in Datadog
- Automatically includes trace context
- Logs output to stdout AND sent to Datadog

### Trace-Log Correlation

**How it works:**
1. FlaskInstrumentor creates a span for each request
2. LoggingInstrumentor reads the current span context
3. Adds `trace_id` and `span_id` to log records
4. OTLP exporters send both traces and logs to collector
5. Datadog Exporter preserves the correlation
6. Datadog UI links them automatically!

**Log Format:**
```
2024-12-01 10:30:45 - app - [ERROR] - trace_id=abc123... span_id=def456... - Error message
                                         ↑                 ↑
                                         |                 |
                                    Trace Link       Span Link
```

### Resource Attributes

All signals (metrics, traces, logs) share these attributes:
```python
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "simple-python-server",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "development",
    "env": "development",      # Datadog tag
    "version": "1.0.0"        # Datadog tag
})
```

These appear in Datadog as:
- Service name for grouping
- Environment for filtering
- Version for deployment tracking

### Datadog Connector

The collector uses the **Datadog connector** to generate APM metrics from traces:

```yaml
connectors:
  datadog/connector:  # Transforms traces → APM metrics

service:
  pipelines:
    traces:
      exporters: [datadog, datadog/connector]  # Send to connector
    
    metrics:
      receivers: [otlp, hostmetrics, datadog/connector]  # Receive from connector
```

**What it does:**
- Receives traces from the traces pipeline
- Generates APM-specific metrics automatically
- Sends those metrics to the metrics pipeline
- Powers Datadog APM dashboards

**Metrics generated:**
- `trace.opentelemetry.instrumentation.flask.server.hits` - Request count per endpoint
- `trace.opentelemetry.instrumentation.flask.server.duration` - Request latency
- `trace.opentelemetry.instrumentation.flask.server.errors` - Error counts

Note: The metric names include `opentelemetry.instrumentation.flask.server` because we use OpenTelemetry's Flask instrumentation (not Datadog's native tracing library).

**Benefits:**
- No code changes needed
- Standard APM metrics across all services
- Out-of-the-box Datadog APM experience
- Complements your custom metrics

## 🔧 Troubleshooting

### Check Collector Logs
```bash
docker compose logs otel-collector
```

### Check Application Logs
```bash
docker compose logs python-server
```

### Verify Data Export

**Check Metrics:**
```bash
docker compose logs otel-collector | grep -i "metrics"
```

**Check Traces:**
```bash
docker compose logs otel-collector | grep -i "traces"
```

**Check Logs:**
```bash
docker compose logs otel-collector | grep -i "logs"
```

**Check Datadog Exporter:**
```bash
# Should show all three signals being exported
docker compose logs otel-collector | grep -i "datadog"
```

**View Application Logs (with trace correlation):**
```bash
# See logs with trace_id and span_id
docker compose logs python-server

# You should see lines like:
# trace_id=abc123... span_id=def456... - Load test completed successfully
```

### Health Checks
```bash
# Application health
curl http://localhost:5000/health

# Collector health  
curl http://localhost:13133/health

# Docker service status
docker compose ps
```

## 📚 Key Features

- ✅ **Simple Setup**: Single docker-compose command
- ✅ **Full Observability**: Metrics, traces, AND logs with correlation
- ✅ **Production-Ready**: Proper resource attributes and tagging
- ✅ **Auto-Instrumentation**: Flask automatically traced
- ✅ **Trace-Log Correlation**: Every log linked to its trace
- ✅ **Debug Output**: Console logging of all exported data
- ✅ **Health Checks**: Built-in health monitoring
- ✅ **Load Testing**: Optional continuous load generation
- ✅ **Comprehensive Metrics**: Request, system, and custom metrics
- ✅ **Distributed Tracing**: APM with flame graphs and service maps
- ✅ **Structured Logging**: JSON logs with rich context
- ✅ **Datadog Integration**: Direct export via OTLP protocol
- ✅ **Datadog Connector**: Auto-generates APM metrics from traces
- ✅ **Log Rotation**: File logs capped at 10MB with automatic rotation and cleanup
- ✅ **Dual Metrics**: Custom metrics + APM metrics for complete visibility

---

**🎉 Your metrics, traces, and logs should appear in Datadog within 1-2 minutes of starting the services!**

**🔍 Pro Tip**: Click on any error log in Datadog and then click "View Trace" to see the full request context!
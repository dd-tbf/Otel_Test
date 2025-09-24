# Simple OpenTelemetry Python Server with Datadog Metrics

A simple dockerized Python Flask server that collects and exports metrics to Datadog via OpenTelemetry Collector.

## 🏗️ Architecture

```
┌─────────────────┐    ┌───────────────────┐    ┌──────────────┐
│  Python Server  │───▶│  OTel Collector   │───▶│   Datadog    │
│   (Flask + OT)  │    │ (Datadog Exporter)│    │   Platform   │
└─────────────────┘    └───────────────────┘    └──────────────┘
```

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

## 🔍 Finding Your Metrics in Datadog

### 1. **Metrics Explorer**
- Go to: https://app.datadoghq.com/metric/explorer
- Search for: `http_requests_total`, `cpu_usage_percent`, etc.
- Filter by: `env:development`, `service:simple-python-server`

### 2. **Service Catalog**
- Go to: https://app.datadoghq.com/services
- Look for: `simple-python-server` service
- Environment: `development`

### 3. **Infrastructure**
- Go to: https://app.datadoghq.com/infrastructure
- Look for: Host metrics from collector

### 4. **Custom Dashboards**
```json
// Example dashboard widget query for request rate
{
  "requests": [
    {
      "q": "sum:http_requests_total{env:development}.as_rate()",
      "display_type": "line"
    }
  ]
}
```

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

## 🔧 Troubleshooting

### Check Collector Logs
```bash
docker compose logs otel-collector
```

### Check Application Logs
```bash
docker compose logs python-server
```

### Verify Metrics Export
```bash
# Should show debug output of exported metrics
docker compose logs otel-collector | grep -i "datadog"
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
- ✅ **Production-Ready**: Proper resource attributes and tagging
- ✅ **Debug Output**: Console logging of all exported metrics
- ✅ **Health Checks**: Built-in health monitoring
- ✅ **Load Testing**: Optional continuous load generation
- ✅ **Comprehensive Metrics**: Request, system, and custom metrics
- ✅ **Datadog Integration**: Direct export via OTLP protocol

---

**🎉 Your metrics should appear in Datadog within 1-2 minutes of starting the services!**
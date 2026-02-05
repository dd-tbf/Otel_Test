# 🚀 Quick Start: Full Observability Stack

## What's New?

Your project now sends **metrics, traces, AND logs** to Datadog with full correlation!

```
Before: Metrics only 📊
Now:    Metrics 📊 + Traces 🔍 + Logs 📝 (all correlated!)
```

---

## 🏃 Get Started in 3 Steps

### Step 1: Rebuild

```bash
make rebuild
```

This will:
- Stop existing services
- Rebuild with new dependencies (tracing + logging)
- Start all services
- Wait for health checks

### Step 2: Generate Test Data

```bash
make test-observability
```

This will:
- Generate ~20 HTTP requests
- Create traces for each request
- Generate correlated logs (INFO, WARNING, ERROR)
- Record metrics
- Show you where to find the data in Datadog

### Step 3: View in Datadog

**Traces (APM):**
- https://app.datadoghq.com/apm/traces
- Filter: `service:simple-python-server`
- Click any trace to see the flame graph

**Logs:**
- https://app.datadoghq.com/logs
- Filter: `service:simple-python-server status:error`
- Click any log → Click **"Trace"** button → See the full trace!

**Metrics:**
- https://app.datadoghq.com/metric/explorer
- Search: `http_requests_total`

---

## 🔗 The Magic: Correlation

**Test it:**

```bash
# Generate some errors
make test-observability
```

**Then in Datadog:**

1. Go to **Logs Explorer**
2. Filter: `service:simple-python-server status:error`
3. Click on any **error log**
4. Click the **"Trace"** button (top right)
5. **See the complete trace!** 🎉

You can now:
- See exact timing of the request
- View all operations in the trace
- See all logs from that request
- Understand what caused the error

---

## 🎯 What Changed?

### Code Changes
- ✅ Added OpenTelemetry tracing (auto-instrumentation)
- ✅ Added OpenTelemetry logging (with correlation)
- ✅ All logs include `trace_id` and `span_id`
- ✅ Logs go to stdout (visible in Docker logs)
- ✅ Everything sent to Datadog via OTLP

### New Capabilities
- ✅ **Distributed Tracing**: See request flow and timing
- ✅ **Correlated Logs**: Every log links to its trace
- ✅ **APM Metrics**: Automatic latency and error metrics
- ✅ **Service Map**: Visualize dependencies
- ✅ **No File Logging**: Logs go to stdout + Datadog

---

## 📖 Documentation

- **Full Details**: See `OBSERVABILITY_UPGRADE.md`
- **README**: Updated with traces and logs documentation
- **Code**: Check `app/app.py` for implementation

---

## 🛠️ Useful Commands

```bash
# Rebuild and restart everything
make rebuild

# Test observability (generate traces, logs, metrics)
make test-observability

# View application logs (with trace_id and span_id)
make logs-app

# View collector logs
make logs-collector

# Check service health
make health

# View service status and endpoints
make status

# Start continuous load testing
make load-test
```

---

## 🔍 Viewing Logs with Trace Correlation

**In Docker:**
```bash
make logs-app
```

You'll see logs like:
```
2024-12-01 10:30:45 - app - [INFO] - trace_id=abc123... span_id=def456... - Load test started
2024-12-01 10:30:45 - app - [ERROR] - trace_id=abc123... span_id=def456... - Simulated error occurred
                                        ↑                 ↑
                                        |                 |
                                   Links to trace    Links to span
```

**In Datadog:**
- Every log has these IDs as clickable fields
- Click "Trace" to jump to the full trace
- See complete context of what happened

---

## 🎓 Key Features

### Automatic Instrumentation
- Flask requests → Auto-traced (no code changes needed)
- Python logging → Auto-correlated with traces
- Just add `FlaskInstrumentor().instrument_app(app)`

### Manual Instrumentation
```python
# Custom spans for important operations
with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("custom.key", "value")
    # Your code here

# Structured logging with context
logger.info(
    "Something happened",
    extra={"custom_field": "value"}
)
```

### Correlation
- Logs automatically include current trace context
- No manual trace ID passing needed
- Works across async operations
- Preserved through OTLP export to Datadog

---

## 🧪 Example Testing Workflow

```bash
# 1. Start fresh
make rebuild

# 2. Generate test data
make test-observability

# 3. View logs with correlation
make logs-app
# Look for trace_id in the output

# 4. Go to Datadog Logs
# - Find an error log
# - Click "Trace"
# - Explore the trace
# - See all related logs

# 5. View APM traces
# - Sort by duration (find slow requests)
# - Click on a span
# - View associated logs
# - Understand the full story
```

---

## 📊 What You'll See in Datadog

### APM (Traces)
- Service: `simple-python-server`
- Endpoints: `/`, `/health`, `/load-test`, etc.
- Automatic latency metrics
- Error tracking
- Flame graphs showing timing
- Service dependencies

### Logs
- All log levels: DEBUG, INFO, WARNING, ERROR
- Trace correlation (clickable)
- Custom fields: `endpoint`, `error_type`, `work_time`, etc.
- Searchable and filterable
- Linked to traces

### Metrics
- HTTP request counts
- Request duration histograms
- Active connections
- CPU and memory usage
- System metrics from collector

### Service Map
- Visual representation of `simple-python-server`
- Health status
- Request flow

---

## 🎉 You're Ready!

You now have a **complete observability stack** with:
- ✅ Metrics for quantitative data
- ✅ Traces for request flow and timing
- ✅ Logs for contextual information
- ✅ Full correlation between all three

**The superpower**: Click any log to see its complete trace context!

Start with:
```bash
make rebuild
make test-observability
```

Then explore Datadog! 🚀

---

## 🆘 Troubleshooting

**Services won't start?**
```bash
make stop
make rebuild
make health
```

**No data in Datadog?**
```bash
# Check collector is healthy
curl http://localhost:13133/health

# Check logs are being sent
make logs-collector | grep -i "datadog"

# Verify API key
cat .env | grep DD_API_KEY
```

**Traces not correlated with logs?**
```bash
# Check logs have trace_id
make logs-app | grep "trace_id"

# Should see: trace_id=<value> span_id=<value>
```

---

For complete details, see **OBSERVABILITY_UPGRADE.md**


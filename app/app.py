#!/usr/bin/env python3
"""
Simple Python Flask server with OpenTelemetry observability.
Sends metrics, traces, and logs to Datadog via OTEL Collector.
"""

import os
import time
import random
import logging
from flask import Flask, jsonify, request
from datetime import datetime

# OpenTelemetry imports for metrics
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# OpenTelemetry imports for tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# OpenTelemetry imports for logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# OpenTelemetry instrumentation
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# OpenTelemetry resources and semantic conventions
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "simple-python-server")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
OTEL_COLLECTOR_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "http://otel-collector:4317")

print(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
print(f"📡 OTEL Collector: {OTEL_COLLECTOR_ENDPOINT}")
print(f"🏷️ Environment: {ENVIRONMENT}")

# Configure OpenTelemetry Resource (shared across all signals)
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: SERVICE_NAME,
    ResourceAttributes.SERVICE_VERSION: SERVICE_VERSION,
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: ENVIRONMENT,
    "service.name": SERVICE_NAME,  # Datadog specific
    "env": ENVIRONMENT,           # Datadog specific
    "version": SERVICE_VERSION,   # Datadog specific
})

# ============================================================================
# Configure Tracing
# ============================================================================
trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(
    endpoint=OTEL_COLLECTOR_ENDPOINT,
    insecure=True
)
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

print("✅ Tracing configured")

# ============================================================================
# Configure Logging
# ============================================================================
# Instrument Python logging to add trace context
LoggingInstrumentor().instrument(set_logging_format=True)

# Configure OTLP log exporter
log_exporter = OTLPLogExporter(
    endpoint=OTEL_COLLECTOR_ENDPOINT,
    insecure=True
)

# Set up logger provider
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
set_logger_provider(logger_provider)

# Create directory for log files if it doesn't exist
import os
os.makedirs('/var/log/app', exist_ok=True)

# Configure Python logging with OpenTelemetry handler  
otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

# Create rotating file handler for filelog receiver
# - maxBytes: 10MB limit per file
# - backupCount: 1 backup file (old file auto-deleted when new backup created)
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(
    '/var/log/app/python-server.log',
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=1               # Keep 1 backup (auto-delete older ones)
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s] - %(message)s'
)
file_handler.setFormatter(file_formatter)

# Set up logging to stdout with trace correlation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to stdout
    ]
)

# Get logger and add handlers
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)  # Add file handler
logger.addHandler(otel_handler)  # Add OTLP handler

print("✅ Logging configured with trace correlation (stdout + file + OTLP)")

# ============================================================================
# Configure Metrics
# ============================================================================
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=OTEL_COLLECTOR_ENDPOINT,
        insecure=True
    ),
    export_interval_millis=5000,  # Export every 5 seconds
)

metrics.set_meter_provider(MeterProvider(
    resource=resource,
    metric_readers=[metric_reader]
))

# Get meter
meter = metrics.get_meter(__name__)

print("✅ Metrics configured")

# Create custom metrics
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration in seconds",
    unit="s"
)

active_connections = meter.create_up_down_counter(
    name="active_connections",
    description="Number of active connections",
    unit="1"
)

# Simulate system metrics
def get_cpu_usage():
    """Simulate CPU usage"""
    return random.uniform(10.0, 90.0)

def get_memory_usage():
    """Simulate memory usage"""
    return random.randint(100_000_000, 500_000_000)

# Register observable gauge callbacks
def observe_cpu_metrics(options):
    yield metrics.Observation(get_cpu_usage())

def observe_memory_metrics(options):
    yield metrics.Observation(get_memory_usage())

# Create observable gauges with callbacks
cpu_usage_gauge = meter.create_observable_gauge(
    name="cpu_usage_percent", 
    description="CPU usage percentage",
    unit="%",
    callbacks=[observe_cpu_metrics]
)

memory_usage_gauge = meter.create_observable_gauge(
    name="memory_usage_bytes",
    description="Memory usage in bytes",
    unit="bytes",
    callbacks=[observe_memory_metrics]
)

# ============================================================================
# Flask Application
# ============================================================================
app = Flask(__name__)

# Instrument Flask for automatic tracing
FlaskInstrumentor().instrument_app(app)

print("✅ Flask instrumented for automatic tracing")

# Global counters for simulation
current_connections = 0

@app.before_request
def before_request():
    global current_connections
    request.start_time = time.time()
    current_connections += 1
    active_connections.add(1)

@app.after_request
def after_request(response):
    global current_connections
    
    # Calculate request duration
    duration = time.time() - getattr(request, 'start_time', time.time())
    
    # Record metrics
    request_counter.add(1, {
        "method": request.method,
        "endpoint": request.endpoint or "unknown",
        "status_code": str(response.status_code),
        "server": SERVICE_NAME
    })
    
    request_duration.record(duration, {
        "method": request.method,
        "endpoint": request.endpoint or "unknown",
        "status_code": str(response.status_code),
        "server": SERVICE_NAME
    })
    
    # Simulate connection closing
    if random.random() < 0.1:  # 10% chance to close a connection
        connections_to_close = random.randint(1, min(3, current_connections))
        current_connections = max(0, current_connections - connections_to_close)
        active_connections.add(-connections_to_close)
    
    print(f"📊 Request: {request.method} {request.path} -> {response.status_code} ({duration:.3f}s)")
    return response

@app.route('/')
def home():
    """Home endpoint"""
    logger.info(
        "Home endpoint accessed",
        extra={
            "endpoint": "/",
            "user_agent": request.headers.get('User-Agent', 'unknown')
        }
    )
    
    # Add custom span attributes
    span = trace.get_current_span()
    span.set_attribute("endpoint.type", "home")
    span.set_attribute("user_agent", request.headers.get('User-Agent', 'unknown'))
    
    return jsonify({
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "message": "Hello from OpenTelemetry Python Server!",
        "trace_id": format(span.get_span_context().trace_id, '032x') if span.is_recording() else None
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.debug(
        "Health check performed",
        extra={
            "endpoint": "/health",
            "active_connections": current_connections
        }
    )
    
    span = trace.get_current_span()
    span.set_attribute("health.status", "healthy")
    span.set_attribute("active_connections", current_connections)
    
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "timestamp": datetime.now().isoformat(),
        "active_connections": current_connections
    })

@app.route('/metrics-info')
def metrics_info():
    """Information about available metrics"""
    logger.info(
        "Metrics info requested",
        extra={"endpoint": "/metrics-info"}
    )
    
    return jsonify({
        "service": SERVICE_NAME,
        "observability": {
            "metrics": {
                "enabled": True,
                "export_interval": "5 seconds",
                "types": ["counter", "histogram", "gauge", "up_down_counter"]
            },
            "traces": {
                "enabled": True,
                "sampler": "always_on",
                "auto_instrumentation": ["flask"]
            },
            "logs": {
                "enabled": True,
                "correlation": "trace_id and span_id included",
                "output": "stdout and OTLP"
            }
        },
        "metrics_exported": [
            {
                "name": "http_requests_total",
                "type": "counter",
                "description": "Total number of HTTP requests",
                "labels": ["method", "endpoint", "status_code", "server"]
            },
            {
                "name": "http_request_duration_seconds", 
                "type": "histogram",
                "description": "HTTP request duration in seconds",
                "labels": ["method", "endpoint", "status_code", "server"]
            },
            {
                "name": "active_connections",
                "type": "up_down_counter", 
                "description": "Number of active connections",
                "labels": []
            },
            {
                "name": "cpu_usage_percent",
                "type": "gauge",
                "description": "CPU usage percentage (simulated)",
                "labels": []
            },
            {
                "name": "memory_usage_bytes",
                "type": "gauge", 
                "description": "Memory usage in bytes (simulated)",
                "labels": []
            }
        ],
        "collector_endpoint": OTEL_COLLECTOR_ENDPOINT
    })

@app.route('/load-test')
def load_test():
    """Endpoint to generate some load for testing"""
    span = trace.get_current_span()
    
    # Simulate some work
    work_time = random.uniform(0.1, 0.5)
    span.set_attribute("work_time_seconds", work_time)
    
    logger.info(
        "Load test started",
        extra={
            "endpoint": "/load-test",
            "work_time": work_time
        }
    )
    
    time.sleep(work_time)
    
    # Randomly return different status codes
    if random.random() < 0.1:  # 10% error rate
        logger.error(
            "Simulated error occurred during load test",
            extra={
                "endpoint": "/load-test",
                "error_type": "simulated_500",
                "work_time": work_time
            }
        )
        span.set_attribute("error", True)
        span.set_attribute("error.type", "simulated_500")
        return jsonify({"error": "Simulated error"}), 500
    elif random.random() < 0.05:  # 5% not found
        logger.warning(
            "Simulated not found error",
            extra={
                "endpoint": "/load-test",
                "error_type": "simulated_404",
                "work_time": work_time
            }
        )
        span.set_attribute("error", True)
        span.set_attribute("error.type", "simulated_404")
        return jsonify({"error": "Not found"}), 404
    
    logger.info(
        "Load test completed successfully",
        extra={
            "endpoint": "/load-test",
            "work_time": work_time,
            "status": "success"
        }
    )
    
    span.set_attribute("status", "success")
    
    return jsonify({
        "message": "Load test completed",
        "work_time": work_time,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/generate-metrics')
def generate_metrics():
    """Endpoint to generate some metrics for testing"""
    span = trace.get_current_span()
    
    # Use manual span for the metrics generation process
    with tracer.start_as_current_span("generate_test_metrics") as gen_span:
        num_metrics = random.randint(5, 15)
        gen_span.set_attribute("metrics.count", num_metrics)
        
        logger.info(
            f"Generating {num_metrics} test metrics",
            extra={
                "endpoint": "/generate-metrics",
                "metrics_count": num_metrics
            }
        )
        
        # Generate multiple requests worth of metrics
        for i in range(num_metrics):
            request_counter.add(1, {
                "method": "GET",
                "endpoint": "generated",
                "status_code": "200",
                "server": SERVICE_NAME
            })
            
            request_duration.record(random.uniform(0.1, 2.0), {
                "method": "GET", 
                "endpoint": "generated",
                "status_code": "200",
                "server": SERVICE_NAME
            })
        
        logger.info(
            f"Successfully generated {num_metrics} test metrics",
            extra={
                "endpoint": "/generate-metrics",
                "metrics_count": num_metrics,
                "status": "completed"
            }
        )
    
    span.set_attribute("metrics.generated", num_metrics)
    
    return jsonify({
        "message": "Metrics generated",
        "count": num_metrics,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"")
    print(f"🎯 Server starting on port 5000")
    print(f"📡 OTLP Endpoint: {OTEL_COLLECTOR_ENDPOINT}")
    print(f"")
    print(f"📊 Observability Signals Enabled:")
    print(f"  ✅ Metrics - Exported every 5 seconds")
    print(f"  ✅ Traces - Auto-instrumented via Flask")
    print(f"  ✅ Logs - Correlated with trace_id and span_id")
    print(f"")
    print(f"🔍 Available endpoints:")
    print(f"  - GET /         : Home page")
    print(f"  - GET /health   : Health check")
    print(f"  - GET /metrics-info : Information about observability")
    print(f"  - GET /load-test : Generate load with variable responses")
    print(f"  - GET /generate-metrics : Generate test metrics")
    print(f"")
    print(f"🔗 All requests automatically generate:")
    print(f"  • Distributed traces (APM)")
    print(f"  • Correlated logs (with trace context)")
    print(f"  • Custom metrics (counters, histograms, gauges)")
    print(f"")
    
    logger.info(
        f"Application started - {SERVICE_NAME} v{SERVICE_VERSION}",
        extra={
            "event": "startup",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "environment": ENVIRONMENT
        }
    )
    
    app.run(host='0.0.0.0', port=5000, debug=False)
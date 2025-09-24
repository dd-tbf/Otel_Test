#!/usr/bin/env python3
"""
Simple Python Flask server with OpenTelemetry metrics collection.
Sends metrics to Datadog via OTEL Collector.
"""

import os
import time
import random
from flask import Flask, jsonify, request
from datetime import datetime

# OpenTelemetry imports
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
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

# Configure OpenTelemetry Resource
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: SERVICE_NAME,
    ResourceAttributes.SERVICE_VERSION: SERVICE_VERSION,
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: ENVIRONMENT,
    "service.name": SERVICE_NAME,  # Datadog specific
    "env": ENVIRONMENT,           # Datadog specific
    "version": SERVICE_VERSION,   # Datadog specific
})

# Configure Metrics
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

# Flask app
app = Flask(__name__)

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
    return jsonify({
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "message": "Hello from OpenTelemetry Python Server!"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "timestamp": datetime.now().isoformat(),
        "active_connections": current_connections
    })

@app.route('/metrics-info')
def metrics_info():
    """Information about available metrics"""
    return jsonify({
        "service": SERVICE_NAME,
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
        "export_interval": "5 seconds",
        "collector_endpoint": OTEL_COLLECTOR_ENDPOINT
    })

@app.route('/load-test')
def load_test():
    """Endpoint to generate some load for testing"""
    # Simulate some work
    work_time = random.uniform(0.1, 0.5)
    time.sleep(work_time)
    
    # Randomly return different status codes
    if random.random() < 0.1:  # 10% error rate
        return jsonify({"error": "Simulated error"}), 500
    elif random.random() < 0.05:  # 5% not found
        return jsonify({"error": "Not found"}), 404
    
    return jsonify({
        "message": "Load test completed",
        "work_time": work_time,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/generate-metrics')
def generate_metrics():
    """Endpoint to generate some metrics for testing"""
    # Generate multiple requests worth of metrics
    for i in range(random.randint(5, 15)):
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
    
    return jsonify({
        "message": "Metrics generated",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"🎯 Server starting on port 5000")
    print(f"📊 Metrics will be exported every 5 seconds to {OTEL_COLLECTOR_ENDPOINT}")
    print(f"🔍 Available endpoints:")
    print(f"  - GET /         : Home page")
    print(f"  - GET /health   : Health check")
    print(f"  - GET /metrics-info : Information about exported metrics")
    print(f"  - GET /load-test : Generate some load")
    print(f"  - GET /generate-metrics : Generate test metrics")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
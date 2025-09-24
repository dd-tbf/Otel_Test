# Use OpenTelemetry Collector Contrib image with Datadog exporter
FROM otel/opentelemetry-collector-contrib:0.108.0

# Create non-root user for security
USER 10001:10001

# Copy the collector configuration
COPY --chown=10001:10001 otel-collector-config.yaml /etc/otelcol-contrib/config.yaml

# Expose necessary ports
EXPOSE 4317 4318 8888 13133

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:13133/health || exit 1

# Run with custom config
CMD ["--config=/etc/otelcol-contrib/config.yaml"]

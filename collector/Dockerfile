# Use OpenTelemetry Collector Contrib image with Datadog exporter
FROM otel/opentelemetry-collector-contrib:0.108.0

# BusyBox wget for HEALTHCHECK (avoids named multi-stage that triggers BuildKit circular deps on some versions)
USER 0
COPY --from=busybox:uclibc /bin/busybox /bin/busybox
# Create non-root user for security
USER 10001:10001
# Copy the collector configuration
COPY --chown=10001:10001 otel-collector-config.yaml /etc/otelcol-contrib/config.yaml

# Expose necessary ports
EXPOSE 4317 4318 8888 13133

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD ["/bin/busybox", "wget", "-q", "-O", "/dev/null", "http://127.0.0.1:13133/health"]

# Run with custom config
CMD ["--config=/etc/otelcol-contrib/config.yaml"]

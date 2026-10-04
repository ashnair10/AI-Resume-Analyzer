import os


def configure_telemetry(app) -> None:
    """Configure OpenTelemetry only when explicitly enabled.

    Local development stays dependency-light and zero-config. In deployed environments,
    point OTLP at Azure Monitor/OpenTelemetry Collector or another compatible backend.
    """
    if os.getenv("OTEL_ENABLED", "false").lower() != "true":
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    resource = Resource.create({"service.name": os.getenv("SERVICE_NAME", "techcv-api")})
    provider = TracerProvider(resource=resource)
    if endpoint:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

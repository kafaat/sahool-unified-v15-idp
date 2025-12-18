"""SAHOOL OpenTelemetry Setup v15.2 (OTLP HTTP exporter)"""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(
    service_name: str, service_layer: str, service_version: str = "1.0.0"
):
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "service.layer": service_layer,
            "deployment.environment": os.getenv("SAHOOL_ENV", "development"),
        }
    )

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces", timeout=30)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    # Instrument logging for correlation (best-effort)
    LoggingInstrumentor().instrument()
    return trace.get_tracer(service_name)


def instrument_fastapi(app):
    FastAPIInstrumentor.instrument_app(app)

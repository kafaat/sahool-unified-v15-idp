# Observability Rules v15.2

Mandatory:
- Every service must initialize OpenTelemetry tracing
- Every event must include correlation_id
- Logs should include trace context where available
- /metrics endpoint must exist

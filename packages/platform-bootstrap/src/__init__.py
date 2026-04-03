"""
SAHOOL Platform Bootstrap

Provides core infrastructure modules for SAHOOL microservices:
- event_bus: NATS JetStream singleton event bus
- tenant: Multi-tenant PostgreSQL RLS context management
- observability: Prometheus metrics and OpenTelemetry tracing

Architectural boundary
──────────────────────
This package *extends* the existing ``shared/`` modules.  It does NOT
replace them.  The mapping is:

  platform_bootstrap.event_bus   → builds on top of shared/events/
  platform_bootstrap.tenant      → builds on top of shared/db/tenant_connection.py
  platform_bootstrap.observability → builds on top of shared/monitoring/ and shared/observability/

Services should import from ``platform_bootstrap.*`` (not from
``shared.*`` directly) for the three concerns above, so that any future
consolidation only requires updating this package.

Docker usage
────────────
Copy ``packages/platform-bootstrap/src/`` to ``/app/platform_bootstrap/``
in the service Dockerfile so that ``PYTHONPATH=/app`` resolves imports::

    COPY --chown=sahool:sahool packages/platform-bootstrap/src/ /app/platform_bootstrap/
"""

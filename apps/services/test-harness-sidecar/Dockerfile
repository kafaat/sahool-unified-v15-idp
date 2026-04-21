# SAHOOL Test Harness Sidecar — staging/dev only, NEVER production.
#
# Production guards (defense in depth, 7 layers — see app/main.py + helm/):
#   1. Pydantic ENVIRONMENT validator refuses 'production'
#   2. Module-level _enforce_production_guard() at import time
#   3. Lifespan re-checks at runtime
#   4. Per-request: tenant_id MUST be in TEST_TENANT_WHITELIST
#   5. Helm chart {{ fail }} if values.environment == 'production'
#   6. Non-root user (this Dockerfile)
#   7. Production Kong ingress class is NOT bound (Helm)

FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

COPY docker/apt-update.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/apt-update.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install via the platform's shared pip wrapper (mirror fallback chain).
COPY docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh

# Install dependencies with platform-wide constraints
COPY constraints.txt /app/constraints.txt
COPY apps/services/test-harness-sidecar/requirements.txt /app/requirements.txt
RUN pip-install.sh -c /app/constraints.txt -r /app/requirements.txt

# Copy shared modules + sidecar source
COPY shared/ /app/shared/
COPY apps/services/test-harness-sidecar/src /app/src
COPY apps/services/test-harness-sidecar/openapi.yaml /app/openapi.yaml

# Non-root user (production guard #6)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8299

# Liveness probe — cheap, no DB check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8299/healthz || exit 1

# Production guard kicks in at import time inside src/main.py
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8299"]

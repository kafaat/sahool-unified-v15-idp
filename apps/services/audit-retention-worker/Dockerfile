# SAHOOL Audit Retention Worker
# =============================
# One-shot CronJob that deletes expired audit_log rows and records the
# deletion in audit_retention_events. NOT a long-running service.
#
# Multi-stage build keeps the final image lean (only asyncpg + stdlib).
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

COPY docker/apt-update.sh docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# setuptools>=78.1.1 for CVE-2024-6345, PYSEC-2025-49
# wheel>=0.46.2 for CVE-2026-24049
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2" build

COPY apps/services/audit-retention-worker/requirements.txt .
COPY constraints.txt .
RUN pip-install.sh --user -c constraints.txt -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Production
# ─────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

ARG SERVICE_NAME=audit-retention-worker
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"
LABEL org.opencontainers.image.description="Retention worker for the SAHOOL audit pipeline — deletes expired audit_log rows under the audit_retention role."

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

COPY --from=builder /root/.local /home/sahool/.local
ENV PATH=/home/sahool/.local/bin:$PATH

COPY --chown=sahool:sahool apps/services/audit-retention-worker/src/        ./src/
COPY --chown=sahool:sahool apps/services/audit-retention-worker/migrations/ ./migrations/

# Strip build tools from the runtime image (same pattern as audit-service).
RUN rm -rf /home/sahool/.local/lib/python*/site-packages/setuptools* \
           /home/sahool/.local/lib/python*/site-packages/pip* \
           /home/sahool/.local/lib/python*/site-packages/wheel* \
           /home/sahool/.local/lib/python*/site-packages/pkg_resources* \
           /home/sahool/.local/lib/python*/site-packages/jaraco* \
           /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/wheel* \
           /usr/local/lib/python*/site-packages/_distutils_hack* \
           /usr/local/lib/python*/site-packages/pkg_resources* \
           /usr/local/lib/python*/site-packages/jaraco* \
           /usr/local/bin/pip* 2>/dev/null || true

USER sahool

# Worker is a one-shot CLI, not a server — no EXPOSE, no HEALTHCHECK.
# Kubernetes treats CronJob pod exit code 0 as success.
ENTRYPOINT ["python", "-m", "src.main"]

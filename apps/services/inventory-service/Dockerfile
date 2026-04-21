# SAHOOL Inventory Service
# ============================
# Agricultural inventory management and analytics
# Multi-stage build for optimized image size
# Version: 16.0.0

ARG PYTHON_VERSION=3.11

# Stage 1: Builder
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
COPY docker/apt-update.sh docker/pip-install.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/pip-install.sh && \
    apt-update.sh && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip-install.sh --upgrade "pip>=24.3.1" "setuptools>=78.1.1" "wheel>=0.46.2"

# Install dependencies with resilient multi-mirror fallback strategy
COPY apps/services/inventory-service/requirements.txt .
COPY constraints.txt .
RUN pip-install.sh --user -c constraints.txt -r requirements.txt

# ── Prisma client generation (runs in the builder stage) ──
# Must run here (not in production stage) so that:
#   1. pip / setuptools / wheel are still available (production strips them).
#   2. The generated client lands in /root/.local/lib/python*/site-packages/prisma/
#      which is then copied to /home/sahool/.local as part of the existing
#      `COPY --from=builder /root/.local ...` line.
#   3. The downloaded Prisma Query Engine binary (cached under ~/.cache/
#      prisma-python/) can be explicitly copied into the runtime user's home
#      below, so at runtime the sahool user finds it without a network round
#      trip.
#
# The `|| true` on the generate step keeps the image build green in
# network-restricted CI — main.py's try/except tolerates a missing client
# and the warehouse / applications endpoints return 503 instead of crashing
# the whole service. (SQLAlchemy analytics path stays fully functional.)
COPY apps/services/inventory-service/prisma/schema.prisma /build/prisma/schema.prisma
ENV PATH=/root/.local/bin:$PATH
# Ensure the cache directory exists even if generate fails, so the
# production stage's `COPY --from=builder /root/.cache/prisma-python` step
# doesn't fail with a missing-source error.
RUN mkdir -p /root/.cache/prisma-python && \
    (prisma generate --schema=/build/prisma/schema.prisma || \
     echo "WARN: prisma generate failed in builder — warehouse/application endpoints will return 503 at runtime")

# Stage 2: Production
FROM python:${PYTHON_VERSION}-slim-bookworm AS production

# Build arguments
ARG SERVICE_NAME=inventory-service
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create non-root user
RUN groupadd --system --gid 1000 sahool && \
    useradd --system --uid 1000 --gid sahool --shell /bin/bash --create-home sahool

# Copy installed Python packages from builder (includes the generated
# Prisma client under site-packages/prisma/).
COPY --from=builder /root/.local /home/sahool/.local

# Copy Prisma's engine-binary cache from the builder so the runtime user
# (sahool) doesn't need a network round-trip on first query.
#
# The builder stage always creates `/root/.cache/prisma-python/` (see the
# `mkdir -p` before `prisma generate` up there), so the source path is
# guaranteed to exist — empty if the generator failed, populated if it
# succeeded. Either way the COPY below completes. We then fix ownership
# in a separate `chown` RUN because multi-stage `COPY --from=<stage>`
# cannot take `--chown`; the source files are owned by root in the
# builder and land here owned by root too, which sahool at runtime
# cannot read without the chown.
COPY --from=builder /root/.cache/prisma-python /home/sahool/.cache/prisma-python
RUN chown -R sahool:sahool /home/sahool/.cache
ENV PATH=/home/sahool/.local/bin:$PATH \
    HOME=/home/sahool

# Copy shared libraries
COPY --chown=sahool:sahool shared/ ./shared/

# Copy services shared modules (needed for errors_py module)
COPY --chown=sahool:sahool apps/services/shared/ ./apps/services/shared/


# Create compatibility layer: copy errors_py to shared/errors_py so imports work
RUN cp -r ./apps/services/shared/errors_py ./shared/ || true && \
    chown -R sahool:sahool /app

# Copy source
COPY --chown=sahool:sahool apps/services/inventory-service/src/ ./src/

# Copy Prisma schema + migrations into the image so Prisma migrate commands
# (run as an init container / job, not on app startup) can find them at
# /app/prisma/. The generated client itself is already in /home/sahool/.local
# via the earlier COPY --from=builder.
COPY --chown=sahool:sahool apps/services/inventory-service/prisma/ ./prisma/


# Strip build tools from production image (CVE-2026-23949, CVE-2026-24049).
# Must run AFTER prisma generate (done in the builder stage) since the
# generator itself uses pip/setuptools to materialise its client package.
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

# Default port (can be overridden via PORT env var)
ENV PORT=8116
EXPOSE 8116

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8116/healthz')" || exit 1

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]

# ============================================
# SAHOOL IoT Service Dockerfile
# خدمة إنترنت الأشياء والمستشعرات
# Port: 8117
# ============================================

# ───────────────────────────────────────────
# Stage 1: Builder
# ───────────────────────────────────────────
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy @sahool/shared-events package (workspace dependency)
COPY packages/shared-events ./packages/shared-events/

# Build shared-events package
WORKDIR /workspace/packages/shared-events
RUN npm config set registry https://registry.npmmirror.com && \
    npm install && npm run build || \
    (npm config set registry https://registry.npmjs.org && npm install && npm run build)

# Copy service to maintain relative path: ../../shared/ from iot-service/src/
WORKDIR /workspace
COPY apps/services/iot-service ./iot-service/

WORKDIR /workspace/iot-service

# Update package.json to use local shared-events (prevents npm from fetching from registry)
# Using npm pkg set for reliable package.json modification (more robust than sed)
RUN npm pkg set dependencies.'@sahool/shared-events'='file:../packages/shared-events'

# Install all dependencies with resilient retry loop and npm cache
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing dependencies..."; \
        if npm install --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=20000 \
            --fetch-retry-maxtimeout=120000 \
            --fetch-timeout=300000 \
            --prefer-offline \
            --no-audit \
            --no-fund; then break; fi; \
        echo "Attempt $i failed, waiting $((i * 10)) seconds before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Generate Prisma client and verify output
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f prisma/generated/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && npx prisma generate && \
     test -f prisma/generated/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build NestJS application using nest build directly (skip prebuild to avoid
# re-running prisma generate which can resolve paths differently in Docker)
RUN npx nest build

# ───────────────────────────────────────────
# Stage 2: Production
# ───────────────────────────────────────────
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="iot-service"
LABEL version="16.0.0"
LABEL description="SAHOOL IoT Service - Smart Irrigation & Sensor Management"

# Install curl for healthcheck and OpenSSL for Prisma native query engine
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl openssl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files from builder (includes generated package-lock.json)
COPY --from=builder /workspace/iot-service/package.json ./
COPY --from=builder /workspace/iot-service/package-lock.json ./

# Copy built shared-events package BEFORE npm install (required for file: protocol)
COPY --from=builder /workspace/packages/shared-events ./packages/shared-events/

# Remove @sahool/shared-events from dependencies before production install
# (we'll copy the pre-built package directly to node_modules after)
RUN npm pkg delete dependencies.'@sahool/shared-events' || true

# Install production dependencies with resilient retry loop
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing production dependencies..."; \
        if (npm ci --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=20000 \
            --fetch-retry-maxtimeout=120000 \
            --fetch-timeout=300000 \
            --prefer-offline \
            --no-audit \
            --no-fund || \
         npm install --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=20000 \
            --fetch-retry-maxtimeout=120000 \
            --fetch-timeout=300000 \
            --prefer-offline \
            --no-audit \
            --no-fund); then break; fi; \
        echo "Attempt $i failed, waiting $((i * 10)) seconds before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy built shared-events package to node_modules
RUN mkdir -p node_modules/@sahool && cp -r packages/shared-events node_modules/@sahool/shared-events && rm -rf packages

# Copy Prisma schema (for migrations)
COPY --from=builder /workspace/iot-service/prisma ./prisma

# Copy generated Prisma client from builder
# Schema uses output = "./generated/client" so actual client is at prisma/generated/client/
# Copy it to node_modules/.prisma/client/ where @prisma/client expects it at runtime
COPY --from=builder /workspace/iot-service/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /workspace/iot-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/iot-service/dist ./dist

# Create non-root user
RUN groupadd -g 1001 nodejs && \
    useradd -u 1001 -g nodejs -s /bin/bash -m nodejs && \
    chown -R nodejs:nodejs /app

USER nodejs

# Environment
ENV NODE_ENV=production \
    PORT=8117

# Expose port
EXPOSE 8117

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8117/health || exit 1

# Run application
CMD ["node", "dist/main.js"]

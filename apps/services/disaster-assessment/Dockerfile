# SAHOOL Disaster Assessment Service v16.0
# خدمة تقييم الكوارث الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model
# With PostgreSQL persistence via Prisma ORM

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="disaster-assessment"
LABEL version="16.0.0"

WORKDIR /app

# Copy package files first for better layer caching
COPY apps/services/disaster-assessment/package*.json ./

# Copy prisma schema BEFORE installing dependencies (required for postinstall hook)
COPY apps/services/disaster-assessment/prisma ./prisma/

# Install dependencies with resilient retry loop and npm cache
# Prisma schema is copied above so postinstall (prisma generate) can run successfully
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
        echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Generate Prisma client and verify output
# Schema uses custom output (prisma/generated/client/) so verify that path
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f prisma/generated/client/index.js || \
    (echo "Prisma client generation failed, retrying..." && npx prisma generate && \
     test -f prisma/generated/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy source code
COPY apps/services/disaster-assessment/ .

# Build the application using nest build directly (skip prebuild to avoid
# re-running prisma generate which can resolve paths differently in Docker)
RUN npx nest build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma native query engine
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl openssl && \
    rm -rf /var/lib/apt/lists/*

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json ./

# Copy prisma schema for migrations
COPY --from=builder /app/prisma ./prisma/

RUN npm config set registry https://registry.npmmirror.com; \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000) || \
    (npm config set registry https://registry.npmjs.org && \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000))

# Copy generated Prisma client from builder
# Schema uses output = "./generated/client" so the actual client is at prisma/generated/client/
# Copy it to node_modules/.prisma/client/ where @prisma/client expects it at runtime
COPY --from=builder /app/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /app/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3020

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3020/healthz || exit 1

# Run database migrations and start the application
# Note: In production, migrations should ideally be run as a separate init container
# Skip migrations when SKIP_DB_INIT=true (for container tests without database)
CMD ["sh", "-c", "if [ \"$SKIP_DB_INIT\" = \"true\" ]; then echo 'Skipping database migrations (SKIP_DB_INIT=true)'; else npx prisma migrate deploy || echo 'Migration failed, continuing anyway...'; fi && node dist/main.js"]

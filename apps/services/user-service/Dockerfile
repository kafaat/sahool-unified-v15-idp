# SAHOOL User Service v16.0.0
# خدمة إدارة المستخدمين

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="user-service"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from user-service/src/
COPY apps/services/user-service ./user-service/

WORKDIR /workspace/user-service

# Install dependencies with resilient retry loop and npm cache
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing dependencies..."; \
        if npm install --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund; then break; fi; \
        if [ "$i" != "3" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Generate Prisma client and verify output
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
ENV PRISMA_CLI_QUERY_ENGINE_TYPE=binary
ENV PRISMA_CLIENT_ENGINE_TYPE=binary
RUN npx prisma generate --schema=./prisma/schema.prisma && \
    test -f prisma/generated/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && \
     npx prisma generate --schema=./prisma/schema.prisma && \
     test -f prisma/generated/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application using nest build directly (skip prebuild to avoid
# re-running prisma generate which can resolve paths differently in Docker)
RUN npx nest build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma native query engine
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends curl openssl && \
    rm -rf /var/lib/apt/lists/*

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds
COPY --from=builder /workspace/user-service/package.json ./
COPY --from=builder /workspace/user-service/package-lock.json ./

# Install production dependencies with resilient retry loop
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing production dependencies..."; \
        if (npm ci --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund || \
         npm install --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund); then break; fi; \
        if [ "$i" != "3" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy prisma schema (for migrations)
COPY --from=builder /workspace/user-service/prisma ./prisma/

# Copy generated Prisma client from builder
# Schema uses output = "./generated/client" so actual client is at prisma/generated/client/
# Copy it to node_modules/.prisma/client/ where @prisma/client expects it at runtime
COPY --from=builder /workspace/user-service/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /workspace/user-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/user-service/dist ./dist

# Set port environment variable
ENV PORT=3025
ENV NODE_ENV=production

# Expose port
EXPOSE 3025

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3025/api/v1/health || exit 1

# Run database migrations and start the application
# Skip migrations when SKIP_DB_INIT=true (for container tests without database)
# Handles P3005 (non-empty database) by baselining existing migrations first
CMD ["sh", "-c", "\
  if [ \"$SKIP_DB_INIT\" = \"true\" ]; then \
    echo 'Skipping database migrations (SKIP_DB_INIT=true)'; \
  else \
    echo 'Running Prisma migrations...'; \
    if ! npx prisma migrate deploy 2>/tmp/prisma_err.log; then \
      if grep -q 'P3005' /tmp/prisma_err.log; then \
        echo 'Database not empty (P3005). Baselining existing migrations...'; \
        for dir in prisma/migrations/*/; do [ -d "$dir" ] || continue; \
          migration_name=$(basename \"$dir\"); \
          echo \"Resolving migration: $migration_name\"; \
          npx prisma migrate resolve --applied \"$migration_name\" 2>/dev/null || true; \
        done; \
        echo 'Baseline complete. Re-running migrate deploy...'; \
        npx prisma migrate deploy; \
      else \
        echo 'Migration error (non-P3005):'; \
        cat /tmp/prisma_err.log; \
        exit 1; \
      fi; \
    fi; \
  fi && exec node dist/main.js"]

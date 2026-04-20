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

# Copy @sahool/shared-events package (workspace dependency — same pattern
# as iot-service). Required because user-service now publishes
# sahool.user.* events through @sahool/shared-events.
COPY packages/shared-events ./packages/shared-events/

# Build shared-events so it's ready to be linked via the file: protocol.
WORKDIR /workspace/packages/shared-events
RUN npm config set registry https://registry.npmjs.org; \
    if npm install && npm run build; then true; \
    else npm config set registry https://registry.npmmirror.com && npm install && npm run build; fi

# Copy service to maintain relative path: ../../shared/ from user-service/src/
WORKDIR /workspace
COPY apps/services/user-service ./user-service/

WORKDIR /workspace/user-service

# Rewrite the @sahool/shared-events dep to point at the locally-built copy
# so `npm install` doesn't try to fetch a non-existent package from the
# public registry.
RUN npm pkg set dependencies.'@sahool/shared-events'='file:../packages/shared-events'

# Validate package.json is valid JSON (fail fast if corrupted by merge conflicts)
RUN node -e "JSON.parse(require('fs').readFileSync('package.json','utf8'))" || \
    (echo 'ERROR: package.json is invalid JSON. Check for merge conflict markers (<<<<<<< HEAD).' && exit 1)

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
RUN npx prisma@5 generate --schema=./prisma/schema.prisma && \
    test -f prisma/generated/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && \
     npx prisma@5 generate --schema=./prisma/schema.prisma && \
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

# Copy pre-built @sahool/shared-events to the path that the file: dep resolves
# to from /app (file:../packages/shared-events → /packages/shared-events).
# Without this, npm ci cannot resolve the local workspace dep and the module
# is missing at runtime, causing MODULE_NOT_FOUND on startup.
COPY --from=builder /workspace/packages/shared-events /packages/shared-events

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

# Apply security patches to production dependencies (fix known CVEs in transitive deps)
RUN npm config set registry https://registry.npmjs.org && npm audit fix --omit=dev --legacy-peer-deps --ignore-scripts 2>/dev/null || true

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
COPY --chmod=755 docker/docker-entrypoint-nestjs.sh /usr/local/bin/docker-entrypoint.sh
CMD ["/usr/local/bin/docker-entrypoint.sh"]

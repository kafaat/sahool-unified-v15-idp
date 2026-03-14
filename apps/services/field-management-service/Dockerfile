# SAHOOL Field Management Service
# ==========================
# Geospatial Field Management with PostGIS & TypeORM
# Uses multi-stage build for optimal image size
# Version: 16.0.0
# NOTE: Build context must be project root

# Build arguments
ARG NODE_VERSION=20
ARG SERVICE_NAME=field-management-service
ARG SERVICE_VERSION=16.0.0

# Stage 1: Build
FROM node:${NODE_VERSION}-bookworm-slim AS builder

WORKDIR /app

# Upgrade npm to latest version for better dependency resolution
RUN npm install -g npm@11.7.0 || \
    (npm config set registry https://registry.npmmirror.com && npm install -g npm@11.7.0)

# Copy shared packages first (needed for file: protocol dependencies)
COPY packages/field-shared ./packages/field-shared

# Build field-shared package first (needed for TypeScript compilation)
WORKDIR /app/packages/field-shared
# Use retry loop and npm cache for resilience against network issues
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com; \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing field-shared dependencies..."; \
        if npm install --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund && npm run build; then break; fi; \
        if [ "$i" != "3" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund && npm run build)

# Return to app directory and install dependencies
WORKDIR /app
COPY apps/services/field-management-service/package.json ./

# Fix the file: path reference for Docker build context (../../../packages -> ./packages)
RUN sed -i 's|file:\.\./\.\./\.\./packages/field-shared|file:./packages/field-shared|g' package.json || true

# Install dependencies with resilient retry loop
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com; \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing service dependencies..."; \
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

# Copy prisma schema (required for prisma generate)
COPY apps/services/field-management-service/prisma ./prisma

# Generate Prisma client (required before TypeScript compilation)
# Schema uses output = "./generated/client" so verify that path
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f prisma/generated/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && npx prisma generate && \
     test -f prisma/generated/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy source, config, and build
COPY apps/services/field-management-service/tsconfig.json ./
COPY apps/services/field-management-service/nest-cli.json ./
COPY apps/services/field-management-service/src ./src
# Prisma already generated above; run nest build directly to avoid re-running prisma generate
RUN npx nest build

# Stage 2: Production
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare ARGs for this stage
ARG NODE_VERSION=20
ARG SERVICE_NAME=field-management-service
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

WORKDIR /app

# Create non-root user for security
RUN groupadd --system sahool && \
    useradd --system --gid sahool --shell /bin/bash sahool

# Install curl for healthcheck, ca-certificates, and OpenSSL for Prisma native query engine
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends curl ca-certificates openssl && \
    rm -rf /var/lib/apt/lists/*

# Upgrade npm to latest version
RUN npm install -g npm@11.7.0 || \
    (npm config set registry https://registry.npmmirror.com && npm install -g npm@11.7.0)

# Copy shared packages (needed for file: protocol dependencies)
COPY --from=builder /app/packages ./packages

# Copy package files and install production dependencies
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json ./

# Fix the file: path reference again for production stage
RUN sed -i 's|file:\.\./\.\./\.\./packages/field-shared|file:./packages/field-shared|g' package.json || true

# Install production dependencies only with resilient retry loop
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com; \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing production dependencies..."; \
        if npm install --omit=dev --legacy-peer-deps \
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
    npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy built files
COPY --from=builder /app/dist ./dist

# Copy prisma schema for runtime migrations
COPY --from=builder /app/prisma ./prisma

# Copy generated Prisma client from builder
# Schema uses output = "./generated/client" so actual client is at prisma/generated/client/
# Copy it to node_modules/.prisma/client/ where @prisma/client expects it at runtime
COPY --from=builder /app/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /app/node_modules/@prisma/client ./node_modules/@prisma/client

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

# Environment
ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD node -e "require('http').get('http://localhost:3000/healthz', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

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
        for dir in prisma/migrations/*/; do \
          migration_name=$(basename \"$dir\"); \
          echo \"Resolving migration: $migration_name\"; \
          npx prisma migrate resolve --applied \"$migration_name\" 2>/dev/null || true; \
        done; \
        echo 'Baseline complete. Re-running migrate deploy...'; \
        npx prisma migrate deploy || echo 'Warning: migrate deploy returned non-zero but continuing...'; \
      else \
        echo 'Migration error (non-P3005):'; \
        cat /tmp/prisma_err.log; \
        exit 1; \
      fi; \
    fi; \
  fi && exec node dist/main.js"]

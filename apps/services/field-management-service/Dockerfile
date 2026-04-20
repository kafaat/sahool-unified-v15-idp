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
# Same treatment for @sahool/shared-events — field-management-service now
# uses the typed EventSubjects constants from it (see field-events.service.ts).
COPY packages/shared-events ./packages/shared-events

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

# Build shared-events so field-management can link it via file: protocol.
WORKDIR /app/packages/shared-events
RUN npm config set registry https://registry.npmjs.org; \
    if npm install && npm run build; then true; \
    else npm config set registry https://registry.npmmirror.com && npm install && npm run build; fi

# Return to app directory and install dependencies
WORKDIR /app
COPY apps/services/field-management-service/package.json ./

# Fix the file: path reference for Docker build context (../../../packages -> ./packages)
RUN sed -i 's|file:\.\./\.\./\.\./packages/field-shared|file:./packages/field-shared|g' package.json || true

# Rewrite @sahool/shared-events to the locally-built copy so npm doesn't
# try to fetch it from the public registry (it isn't published).
RUN npm pkg set dependencies.'@sahool/shared-events'='file:./packages/shared-events'

# Validate package.json is valid JSON (fail fast if corrupted by merge conflicts)
RUN node -e "JSON.parse(require('fs').readFileSync('package.json','utf8'))" || \
    (echo 'ERROR: package.json is invalid JSON. Check for merge conflict markers (<<<<<<< HEAD).' && exit 1)

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
RUN npx prisma@5 generate && \
    test -f prisma/generated/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && npx prisma@5 generate && \
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
    useradd --system --gid sahool --shell /bin/bash --create-home sahool

# Upgrade system packages and install runtime dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends curl ca-certificates openssl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

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

# Apply security patches to production dependencies (fix known CVEs in transitive deps)
RUN npm config set registry https://registry.npmjs.org && npm audit fix --omit=dev --legacy-peer-deps --ignore-scripts 2>/dev/null || true

# Copy built files
COPY --from=builder /app/dist ./dist

# Copy prisma schema for runtime migrations
COPY --from=builder /app/prisma ./prisma

# Copy generated Prisma client from builder
# Schema uses output = "./generated/client" so actual client is at prisma/generated/client/
# Copy it to node_modules/.prisma/client/ where @prisma/client expects it at runtime
COPY --from=builder /app/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /app/node_modules/@prisma/client ./node_modules/@prisma/client

# Also bake the `prisma` CLI (from package.json ~5.22.0) and its engine
# binaries into the production image. Without these, the entrypoint's
# `npx prisma migrate deploy` falls back to fetching the current latest
# version from the registry at startup — which is Prisma 7.x and fails
# with P1012 because our schema still uses the v5 `url` / `directUrl`
# datasource syntax. Having the CLI local also removes a runtime network
# dependency and guarantees the CLI version matches @prisma/client.
COPY --from=builder /app/node_modules/prisma ./node_modules/prisma
COPY --from=builder /app/node_modules/@prisma/engines ./node_modules/@prisma/engines
COPY --from=builder /app/node_modules/.bin/prisma ./node_modules/.bin/prisma

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
COPY --chmod=755 docker/docker-entrypoint-nestjs.sh /usr/local/bin/docker-entrypoint.sh
CMD ["/usr/local/bin/docker-entrypoint.sh"]

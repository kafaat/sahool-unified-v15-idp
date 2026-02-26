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
RUN npm install -g npm@11.7.0

# Copy shared packages first (needed for file: protocol dependencies)
COPY packages/field-shared ./packages/field-shared
COPY packages/nestjs-auth ./packages/nestjs-auth
# tsconfig.base.json at /app/ so packages/nestjs-auth/../../tsconfig.base.json resolves correctly
COPY tsconfig.base.json ./tsconfig.base.json

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
        echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund && npm run build)

# Return to app directory and install dependencies
WORKDIR /app
COPY apps/services/field-management-service/package.json ./

# Fix the file: path references for Docker build context (../../../packages -> ./packages)
RUN sed -i 's|file:\.\./\.\./\.\./packages/field-shared|file:./packages/field-shared|g' package.json || true
RUN sed -i 's|"@sahool/nestjs-auth": "16.0.0"|"@sahool/nestjs-auth": "file:./packages/nestjs-auth"|' package.json || true

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
        echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy prisma schema (required for prisma generate)
COPY apps/services/field-management-service/prisma ./prisma

# Generate Prisma client (required before TypeScript compilation)
RUN npx prisma generate

# Copy source, config, and build
COPY apps/services/field-management-service/tsconfig.json ./
COPY apps/services/field-management-service/nest-cli.json ./
COPY apps/services/field-management-service/src ./src
# Build nestjs-auth package (dist/ is gitignored)
RUN npm install --no-save redis 2>/dev/null || true
RUN cd /app/packages/nestjs-auth && \
    ln -sf /app/node_modules ./node_modules && \
    npx tsc --skipLibCheck || \
    npx -y typescript@5.9.3 tsc --skipLibCheck || \
    echo "WARN: nestjs-auth build failed"

# Prisma already generated above; run nest build directly to avoid re-running prisma generate
RUN npx nest build

# Stage 2: Production
FROM node:${NODE_VERSION}-bookworm-slim

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
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates openssl && \
    rm -rf /var/lib/apt/lists/*

# Upgrade npm to latest version
RUN npm install -g npm@11.7.0

# Copy shared packages (needed for file: protocol dependencies)
COPY --from=builder /app/packages ./packages

# Copy package files and install production dependencies
COPY --from=builder /app/package.json ./

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
        echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy built files
COPY --from=builder /app/dist ./dist

# Copy prisma schema for runtime migrations
COPY --from=builder /app/prisma ./prisma

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /app/node_modules/@prisma/client ./node_modules/@prisma/client

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

# Environment
ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/healthz', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["npm", "start"]

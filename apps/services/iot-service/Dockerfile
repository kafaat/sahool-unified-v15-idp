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

# Copy nestjs-auth package (workspace dependency: @sahool/nestjs-auth)
COPY packages/nestjs-auth ./nestjs-auth/
COPY tsconfig.base.json /tsconfig.base.json

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

# Update package.json to use local packages (prevents npm from fetching from registry)
# Using npm pkg set for reliable package.json modification (more robust than sed)
RUN npm pkg set dependencies.'@sahool/shared-events'='file:../packages/shared-events' && \
    npm pkg set dependencies.'@sahool/nestjs-auth'='file:../nestjs-auth'

# Install all dependencies with retry for network resilience
RUN npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000)

# Generate Prisma client and verify output
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f node_modules/.prisma/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && npx prisma generate && \
     test -f node_modules/.prisma/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build nestjs-auth package (dist/ is gitignored)
RUN npm install --no-save \
    @nestjs/common@^10.0.0 @nestjs/core@^10.0.0 rxjs@^7.0.0 \
    @nestjs/passport@^10.0.0 passport@^0.7.0 passport-jwt@^4.0.0 @nestjs/jwt@^10.0.0 \
    redis@^4.0.0 ioredis@^5.0.0 "@liaoliaots/nestjs-redis@^9.0.0" \
    --legacy-peer-deps || true
WORKDIR /workspace/nestjs-auth
RUN ln -sf /workspace/iot-service/node_modules ./node_modules && \
    npx tsc --skipLibCheck
WORKDIR /workspace/iot-service

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

# Copy nestjs-auth dist + package.json for runtime (file:../nestjs-auth reference)
COPY --from=builder /workspace/nestjs-auth/dist /nestjs-auth/dist/
COPY --from=builder /workspace/nestjs-auth/package.json /nestjs-auth/package.json

# Copy package files from builder (includes generated package-lock.json)
COPY --from=builder /workspace/iot-service/package.json ./
COPY --from=builder /workspace/iot-service/package-lock.json ./

# Copy built shared-events package BEFORE npm install (required for file: protocol)
COPY --from=builder /workspace/packages/shared-events ./packages/shared-events/

# Remove file: dependencies before production install (we'll handle them manually)
RUN npm pkg delete dependencies.'@sahool/shared-events' || true && \
    npm pkg delete dependencies.'@sahool/nestjs-auth' || true

# Install production dependencies with retry for network resilience
RUN npm config set registry https://registry.npmmirror.com && \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 && npm cache clean --force || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 && npm cache clean --force) || \
    (npm config set registry https://registry.npmjs.org && \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000))

# Copy built shared-events package to node_modules and symlink nestjs-auth
RUN mkdir -p node_modules/@sahool && cp -r packages/shared-events node_modules/@sahool/shared-events && rm -rf packages
RUN ln -s /app/node_modules /nestjs-auth/node_modules && \
    mkdir -p node_modules/@sahool/nestjs-auth && \
    cp -r /nestjs-auth/dist node_modules/@sahool/nestjs-auth/dist && \
    cp /nestjs-auth/package.json node_modules/@sahool/nestjs-auth/package.json

# Copy Prisma schema (for migrations)
COPY --from=builder /workspace/iot-service/prisma ./prisma

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /workspace/iot-service/node_modules/.prisma ./node_modules/.prisma/
COPY --from=builder /workspace/iot-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/iot-service/dist ./dist

# Create non-root user
RUN groupadd -g 1001 nodejs && \
    useradd -u 1001 -g nodejs -s /bin/bash -m nodejs && \
    chown -R nodejs:nodejs /app /nestjs-auth

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

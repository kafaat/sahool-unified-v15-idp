# SAHOOL Yield Prediction Service v16.0
# خدمة التنبؤ بالإنتاجية الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="yield-prediction"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy nestjs-auth package (workspace dependency: @sahool/nestjs-auth)
COPY packages/nestjs-auth ./nestjs-auth/

# Copy root tsconfig.base.json (nestjs-auth tsconfig extends ../../tsconfig.base.json)
COPY tsconfig.base.json /tsconfig.base.json

# Copy service to maintain relative path: ../../shared/ from yield-prediction-service/src/
COPY apps/services/yield-prediction-service /workspace/yield-prediction-service/

WORKDIR /workspace/yield-prediction-service

# Install dependencies with retry for network resilience
# Replace workspace dependency with local file path for Docker build
RUN sed -i 's|"@sahool/nestjs-auth": "16.0.0"|"@sahool/nestjs-auth": "file:../nestjs-auth"|' package.json && \
    npm pkg delete scripts.prepare --prefix /workspace/nestjs-auth 2>/dev/null || true && \
    npm config set registry https://registry.npmmirror.com; \
    (npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 --no-audit || \
    (echo "Retrying npm install..." && npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 --no-audit)) || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 --no-audit)

# Build nestjs-auth package (dist/ is gitignored and excluded by .dockerignore)
# Must build AFTER service npm install so peer deps (@nestjs/common etc.) are available
RUN cd /workspace/nestjs-auth && \
    ln -sf /workspace/yield-prediction-service/node_modules ./node_modules && \
    npx tsc --skipLibCheck || \
    npx -y typescript@5.9.3 tsc --skipLibCheck || \
    echo "WARN: nestjs-auth build failed"

# Build the application
RUN npm run build

# Production stage
FROM node:${NODE_VERSION}-alpine AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy only nestjs-auth dist + package.json for runtime (avoid builder's node_modules symlink)
# Path must be /nestjs-auth/ to match file:../nestjs-auth reference from /app/
COPY --from=builder /workspace/nestjs-auth/dist /nestjs-auth/dist/
COPY --from=builder /workspace/nestjs-auth/package.json /nestjs-auth/package.json

# Copy package files from builder (includes generated package-lock.json)
# NOTE: reflect-metadata MUST be in dependencies (not devDependencies) for NestJS to work
COPY --from=builder /workspace/yield-prediction-service/package.json ./
COPY --from=builder /workspace/yield-prediction-service/package-lock.json ./

# Install production dependencies with npm ci (deterministic) with fallback to npm install
# reflect-metadata is required at runtime for NestJS decorators and DI
# Note: Deprecation warnings (inflight, glob@7) are from transitive dependencies and are non-blocking
RUN npm config set registry https://registry.npmmirror.com && \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 --no-audit || \
    (echo "npm ci failed, falling back to npm install..." && npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 --no-audit)) || \
    (npm config set registry https://registry.npmjs.org && \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 --no-audit || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 --no-audit))

# Install nestjs-auth runtime dependencies (redis, ioredis used by token-revocation;
# @liaoliaots/nestjs-redis used by user-validation service)
RUN npm install --no-save --ignore-scripts redis ioredis @liaoliaots/nestjs-redis 2>/dev/null || true

# Symlink node_modules into nestjs-auth so its require() calls resolve peer deps
# (Node.js resolves from /nestjs-auth/ → /nestjs-auth/node_modules/ → found)
RUN ln -s /app/node_modules /nestjs-auth/node_modules

# Copy built application
COPY --from=builder /workspace/yield-prediction-service/dist ./dist

# Expose port (can be overridden via PORT env var)
# Note: Changed from 8098 to 8152 to avoid conflict with yield-engine
EXPOSE 8152

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app /nestjs-auth
USER node

ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD sh -c "curl -f http://localhost:${PORT:-8152}/api/v1/yield/health || exit 1"

# Run the application
CMD ["node", "dist/main.js"]

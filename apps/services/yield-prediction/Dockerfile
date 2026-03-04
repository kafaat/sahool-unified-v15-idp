# SAHOOL Yield Prediction Service v16.0
# خدمة التنبؤ بالإنتاجية الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="yield-prediction"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from yield-prediction/src/
COPY apps/services/yield-prediction ./yield-prediction/

WORKDIR /workspace/yield-prediction

# Install dependencies with resilient retry loop and npm cache
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing dependencies..." && \
        npm install --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund && break || \
        (echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10))); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Build the application
RUN npx nest build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy package files from builder (includes generated package-lock.json)
# NOTE: reflect-metadata MUST be in dependencies (not devDependencies) for NestJS to work
COPY --from=builder /workspace/yield-prediction/package.json ./
COPY --from=builder /workspace/yield-prediction/package-lock.json ./

# Install only production dependencies with resilient retry loop
# reflect-metadata is required at runtime for NestJS decorators and DI
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing production dependencies..." && \
        (npm ci --omit=dev --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund || \
        npm install --omit=dev --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund) && break || \
        (echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10))); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy built application
COPY --from=builder /workspace/yield-prediction/dist ./dist

# Expose port
EXPOSE 3021

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3021/api/v1/yield/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

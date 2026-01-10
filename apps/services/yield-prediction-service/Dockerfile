# SAHOOL Yield Prediction Service v16.0
# خدمة التنبؤ بالإنتاجية الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="yield-prediction"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from yield-prediction-service/src/
COPY apps/services/yield-prediction-service ./yield-prediction-service/

WORKDIR /workspace/yield-prediction-service

# Install dependencies with retry for network resilience
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy package files from builder (includes generated package-lock.json)
# NOTE: reflect-metadata MUST be in dependencies (not devDependencies) for NestJS to work
COPY --from=builder /workspace/yield-prediction-service/package.json ./
COPY --from=builder /workspace/yield-prediction-service/package-lock.json ./

# Install production dependencies with npm ci (deterministic) with fallback to npm install
# reflect-metadata is required at runtime for NestJS decorators and DI
RUN npm ci --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy built application
COPY --from=builder /workspace/yield-prediction-service/dist ./dist

# Expose port (can be overridden via PORT env var)
EXPOSE 8098

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD sh -c "curl -f http://localhost:${PORT:-8098}/api/v1/yield/health || exit 1"

# Run the application
CMD ["node", "dist/main.js"]

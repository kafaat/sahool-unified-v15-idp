# SAHOOL Crop Growth Model Service v16.0
# خدمة نموذج نمو المحاصيل
# Based on WOFOST/DSSAT/APSIM mechanistic models

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="crop-growth-model"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from crop-growth-model/src/
COPY apps/services/crop-growth-model ./crop-growth-model/

WORKDIR /workspace/crop-growth-model

# Install dependencies with retry for network resilience
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy package files
COPY apps/services/crop-growth-model/package.json apps/services/crop-growth-model/package-lock.json* ./
RUN npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy built application
COPY --from=builder /workspace/crop-growth-model/dist ./dist

# Expose port
EXPOSE 3023

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3023/api/v1/simulation/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

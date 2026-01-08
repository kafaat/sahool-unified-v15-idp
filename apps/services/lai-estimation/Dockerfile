# SAHOOL LAI Estimation Service v16.0
# خدمة تقدير مؤشر مساحة الأوراق
# Based on LAI-TransNet Two-Stage Transfer Learning Framework

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="lai-estimation"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from lai-estimation/src/
COPY apps/services/lai-estimation ./lai-estimation/

WORKDIR /workspace/lai-estimation

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
COPY apps/services/lai-estimation/package.json ./
RUN npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy built application
COPY --from=builder /workspace/lai-estimation/dist ./dist

# Expose port
EXPOSE 3022

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3022/api/v1/lai/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

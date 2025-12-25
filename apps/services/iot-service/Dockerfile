# ============================================
# SAHOOL IoT Service Dockerfile
# خدمة إنترنت الأشياء والمستشعرات
# Port: 8095
# ============================================

# ───────────────────────────────────────────
# Stage 1: Builder
# ───────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json ./

# Install all dependencies with retry for network resilience
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy source
COPY . .

# Build NestJS application
RUN npm run build

# ───────────────────────────────────────────
# Stage 2: Production
# ───────────────────────────────────────────
FROM node:20-alpine AS production

# Labels
LABEL maintainer="KAFAAT <dev@kafaat.sa>"
LABEL service="iot-service"
LABEL version="16.0.0"
LABEL description="SAHOOL IoT Service - Smart Irrigation & Sensor Management"

# Install curl for healthcheck
RUN apk add --no-cache curl

WORKDIR /app

# Copy package files
COPY package.json ./

# Install production dependencies with retry for network resilience
RUN npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 && npm cache clean --force

# Copy built application
COPY --from=builder /app/dist ./dist

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

# Environment
ENV NODE_ENV=production \
    PORT=8095

# Expose port
EXPOSE 8095

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8095/api/v1/health || exit 1

# Run application
CMD ["node", "dist/main"]

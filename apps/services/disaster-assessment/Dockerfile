# SAHOOL Disaster Assessment Service v16.0
# خدمة تقييم الكوارث الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model
# With PostgreSQL persistence via Prisma ORM

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="disaster-assessment"
LABEL version="16.0.0"

# Install OpenSSL for Prisma (required for generating client)
RUN apk update && apk add --no-cache openssl

WORKDIR /app

# Copy package files first for better layer caching
COPY apps/services/disaster-assessment/package*.json ./

# Copy prisma schema BEFORE installing dependencies (required for postinstall hook)
COPY apps/services/disaster-assessment/prisma ./prisma/

# Install dependencies with retry for network resilience
# Use --ignore-scripts to prevent postinstall from running before prisma schema is available
# Then explicitly run prisma generate
RUN npm ci --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Generate Prisma client (required before build)
RUN npx prisma generate

# Copy source code
COPY apps/services/disaster-assessment/ .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Prisma 5.22+ bundles its own OpenSSL, no system installation needed
# wget is already available in node:20-alpine for health checks

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json ./

# Copy prisma schema for migrations
COPY --from=builder /app/prisma ./prisma/

RUN npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma/
COPY --from=builder /app/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3020

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --spider --quiet --timeout=5 http://localhost:3020/api/v1/disasters/health || exit 1

# Run database migrations and start the application
# Note: In production, migrations should ideally be run as a separate init container
# Skip migrations when SKIP_DB_INIT=true (for container tests without database)
CMD ["sh", "-c", "if [ \"$SKIP_DB_INIT\" = \"true\" ]; then echo 'Skipping database migrations (SKIP_DB_INIT=true)'; else npx prisma migrate deploy || echo 'Migration failed, continuing anyway...'; fi && node dist/main.js"]

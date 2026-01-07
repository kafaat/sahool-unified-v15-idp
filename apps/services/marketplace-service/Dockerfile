# SAHOOL Marketplace & FinTech Service v16.0.0
# سوق سهول والخدمات المالية

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="marketplace-service"
LABEL version="16.0.0"

WORKDIR /app

# Copy package files first for better layer caching
COPY apps/services/marketplace-service/package.json apps/services/marketplace-service/package-lock.json* ./

# Install dependencies (with retries for network resilience)
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy source code
COPY apps/services/marketplace-service/src ./src/
COPY apps/services/marketplace-service/prisma ./prisma/
COPY apps/services/marketplace-service/tsconfig.json apps/services/marketplace-service/nest-cli.json ./

# Generate Prisma client
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma compatibility
RUN apk add --no-cache curl openssl

# Copy package files
COPY apps/services/marketplace-service/package.json apps/services/marketplace-service/package-lock.json* ./
# Install with increased retries and timeout for network resilience
RUN npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema and regenerate client for production environment
COPY --from=builder /workspace/marketplace-service/prisma ./prisma/
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy built application
COPY --from=builder /workspace/marketplace-service/dist ./dist

# Expose port
EXPOSE 3010

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3010/api/v1/healthz || exit 1

# Run the application
CMD ["node", "dist/main.js"]

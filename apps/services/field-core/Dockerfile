# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ ⚠️  FROZEN SERVICE - DO NOT USE IN PRODUCTION                              ║
# ║ This service has been replaced by: field-management-service (port 3000)   ║
# ║ Port Conflict: 3000                                                         ║
# ║ See: docs/DEPRECATED_SERVICES.md                                           ║
# ╚════════════════════════════════════════════════════════════════════════════╝
#
# SAHOOL Field Core Service
# ==========================
# Geospatial Field Management with PostGIS & Prisma Support
# Uses multi-stage build for optimal image size
# Version: 16.0.0

# Build arguments
ARG NODE_VERSION=20
ARG SERVICE_NAME=field-core
ARG SERVICE_VERSION=16.0.0

# Stage 1: Build
FROM node:${NODE_VERSION}-alpine AS builder

WORKDIR /app

# Copy shared packages first (needed for file: protocol dependencies)
# This must be done BEFORE npm install to resolve @sahool/field-shared
COPY packages/field-shared ./packages/field-shared

# Build the shared package
WORKDIR /app/packages/field-shared
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000
RUN npm run build

# Return to app directory
WORKDIR /app

# Install dependencies first (better caching) with retry for network resilience
COPY apps/services/field-core/package*.json ./
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy Prisma schema and generate client
COPY apps/services/field-core/prisma ./prisma
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy source and build
COPY apps/services/field-core/tsconfig.json ./
COPY apps/services/field-core/src ./src
RUN npm run build

# Stage 2: Production
FROM node:${NODE_VERSION}-alpine

# Re-declare ARGs for this stage
ARG SERVICE_NAME=field-core
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

WORKDIR /app

# Create non-root user for security
RUN addgroup --system sahool && \
    adduser --system --ingroup sahool --disabled-password --gecos "" sahool

# Install curl for healthcheck and OpenSSL for Prisma compatibility
RUN apk add --no-cache curl ca-certificates openssl

# Copy shared packages (needed for file: protocol dependencies)
COPY --from=builder /app/packages ./packages

# Copy package files and install production dependencies
COPY --from=builder /app/package*.json ./
RUN npm install --omit=dev --silent --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy Prisma schema and regenerate client for production environment
# Add retry logic for network resilience
COPY --from=builder /app/prisma ./prisma
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy built files
COPY --from=builder /app/dist ./dist

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

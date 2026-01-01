# SAHOOL Field Management Service
# ==========================
# Geospatial Field Management with PostGIS & Prisma Support
# Uses multi-stage build for optimal image size
# Version: 16.0.0
# NOTE: Build context must be project root

# Build arguments
ARG NODE_VERSION=20
ARG SERVICE_NAME=field-management-service
ARG SERVICE_VERSION=16.0.0

# Stage 1: Build
FROM node:${NODE_VERSION}-alpine AS builder

WORKDIR /app

# Upgrade npm to latest version for better dependency resolution
RUN npm install -g npm@11.7.0

# Copy shared packages first (needed for file: protocol dependencies)
COPY packages/field-shared ./packages/field-shared

# Install dependencies first (better caching)
COPY apps/services/field-management-service/package.json ./
RUN npm install --legacy-peer-deps

# Copy Prisma schema and generate client
COPY apps/services/field-management-service/prisma ./prisma
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy source and build
COPY apps/services/field-management-service/tsconfig.json ./
COPY apps/services/field-management-service/src ./src
RUN npm run build

# Stage 2: Production
FROM node:${NODE_VERSION}-alpine

# Re-declare ARGs for this stage
ARG SERVICE_NAME=field-management-service
ARG SERVICE_VERSION=16.0.0

LABEL org.opencontainers.image.title="SAHOOL ${SERVICE_NAME}"
LABEL org.opencontainers.image.version="${SERVICE_VERSION}"

WORKDIR /app

# Create non-root user for security
RUN addgroup --system sahool && \
    adduser --system --ingroup sahool --disabled-password --gecos "" sahool

# Install curl for healthcheck and OpenSSL for Prisma compatibility
RUN apk add --no-cache curl ca-certificates openssl

# Upgrade npm to latest version for better dependency resolution
RUN npm install -g npm@11.7.0

# Copy shared packages (needed for file: protocol dependencies)
COPY --from=builder /app/packages ./packages

# Copy package files and install production dependencies
COPY --from=builder /app/package.json ./
RUN npm install --omit=dev --legacy-peer-deps

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

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/healthz', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["npm", "start"]

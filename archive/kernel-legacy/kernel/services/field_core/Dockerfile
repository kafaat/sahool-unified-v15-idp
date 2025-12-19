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

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy Prisma schema and generate client
COPY prisma ./prisma
RUN npx prisma generate

# Copy source and build
COPY tsconfig.json ./
COPY src ./src
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
RUN addgroup --system --gid 1000 sahool && \
    adduser --system --uid 1000 --ingroup sahool --disabled-password --gecos "" sahool

# Install curl for healthcheck
RUN apk add --no-cache curl ca-certificates

# Copy built files, Prisma, and production dependencies
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
RUN npm install --only=production --silent && npx prisma generate

# Set ownership
RUN chown -R sahool:sahool /app

USER sahool

# Environment
ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/healthz || exit 1

CMD ["npm", "start"]

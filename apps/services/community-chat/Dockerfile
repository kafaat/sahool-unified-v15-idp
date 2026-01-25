# ═══════════════════════════════════════════════════════════════════════════════
# Sahool Community Chat Service
# خدمة الدردشة الحية لمجتمع سهول
#
# Multi-stage build with Node.js 20 Alpine
# ═══════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder - Install dependencies and generate Prisma client
# ───────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files from service directory
COPY apps/services/community-chat/package.json apps/services/community-chat/package-lock.json* ./

# Copy Prisma schema for client generation
COPY apps/services/community-chat/prisma/ ./prisma/

# Install all dependencies (including devDependencies for build) with retry for network resilience
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Generate Prisma client
RUN npx prisma generate

# Copy source code
COPY apps/services/community-chat/src/ ./src/

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Production - Minimal runtime image
# ───────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS production

LABEL maintainer="Sahool Team <dev@sahool.io>"
LABEL service="community-chat"
LABEL version="1.0.0"
LABEL description="Real-time chat service for Yemeni farmers community"

# Install curl for healthcheck and openssl for Prisma
RUN apk add --no-cache curl openssl

WORKDIR /app

# Copy package files from builder and install production dependencies
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json ./

# Copy Prisma schema for migrations
COPY --from=builder /app/prisma/ ./prisma/

RUN npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy the generated Prisma client from builder stage
COPY --from=builder /app/node_modules/.prisma/ ./node_modules/.prisma/
COPY --from=builder /app/node_modules/@prisma/client/ ./node_modules/@prisma/client/

RUN npm cache clean --force

# Copy source code
COPY --from=builder /app/src/ ./src/

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

# Environment variables
ENV NODE_ENV=production \
    PORT=8097

EXPOSE 8097

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD node -e "require('http').get('http://localhost:8097/healthz', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["npm", "start"]

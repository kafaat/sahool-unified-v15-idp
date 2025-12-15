# ═══════════════════════════════════════════════════════════════════════════════
# Sahool Community Chat Service
# خدمة الدردشة الحية لمجتمع سهول
#
# Multi-stage build with Node.js 20 Alpine
# ═══════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Builder - Install dependencies
# ───────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY src/ ./src/

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Production - Minimal runtime image
# ───────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS production

LABEL maintainer="Sahool Team <dev@sahool.io>"
LABEL service="community-chat"
LABEL version="1.0.0"
LABEL description="Real-time chat service for Yemeni farmers community"

# Install curl for healthcheck
RUN apk add --no-cache curl

WORKDIR /app

# Copy only production dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

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
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8097/healthz || exit 1

CMD ["npm", "start"]

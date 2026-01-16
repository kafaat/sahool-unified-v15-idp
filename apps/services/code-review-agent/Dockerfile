# Code Review Agent Dockerfile
# Multi-stage build for optimized production image

# hadolint global ignore=DL3008

# ============================================================================
# Build Stage
# ============================================================================
FROM node:20-slim AS builder

WORKDIR /app

# Install build dependencies and clean up in same layer
# hadolint ignore=DL3009
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --ignore-scripts

# Copy source code
COPY src/ ./src/

# Build TypeScript
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# ============================================================================
# Production Stage
# ============================================================================
FROM node:20-slim AS production

LABEL maintainer="KAFAAT <dev@kafaat.com>"
LABEL description="AI-powered code review agent using Claude Agent SDK"
LABEL version="1.0.0"

# Create non-root user
RUN groupadd -r agent && useradd -r -g agent agent

WORKDIR /app

# Copy built artifacts with ownership set
COPY --from=builder --chown=agent:agent /app/dist ./dist
COPY --from=builder --chown=agent:agent /app/node_modules ./node_modules
COPY --from=builder --chown=agent:agent /app/package.json ./

# Switch to non-root user
USER agent

# Environment variables
ENV NODE_ENV=production
ENV LOG_LEVEL=info

# Health check using shell form for better compatibility
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "process.exit(0)"

# Default command runs the production agent
CMD ["node", "dist/production-agent.js"]

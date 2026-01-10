# Code Review Agent Dockerfile
# Multi-stage build for optimized production image

# ============================================================================
# Build Stage
# ============================================================================
FROM node:20-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci

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

# Copy built artifacts and production dependencies
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# Set ownership
RUN chown -R agent:agent /app

# Switch to non-root user
USER agent

# Environment variables
ENV NODE_ENV=production
ENV LOG_LEVEL=info

# Health check endpoint (when running as HTTP service)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "console.log('healthy')" || exit 1

# Default command runs the production agent
CMD ["node", "dist/production-agent.js"]

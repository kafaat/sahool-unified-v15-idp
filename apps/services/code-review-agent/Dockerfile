# syntax=docker/dockerfile:1
# Code Review Agent Dockerfile
# Multi-stage build for optimized production image

# hadolint global ignore=DL3008

# ============================================================================
# Build Stage
# ============================================================================
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

WORKDIR /app

# Install build dependencies
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends python3 make g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy package files
COPY apps/services/code-review-agent/package*.json ./
COPY apps/services/code-review-agent/tsconfig.json ./

# Install dependencies with resilient retry loop and npm cache
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    install_ok=false; \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing dependencies..."; \
        if npm ci --ignore-scripts \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund; then install_ok=true; break; fi; \
        if [ "$i" != "3" ]; then \
            echo "Attempt $i failed, waiting before retry..."; \
            sleep $((i * 10)); \
        fi; \
    done; \
    if [ "$install_ok" = "false" ]; then \
        npm config set registry https://registry.npmjs.org && \
        npm ci --ignore-scripts --fetch-retries=5 --no-audit --no-fund; \
    fi

# Copy source code
COPY apps/services/code-review-agent/src/ ./src/

# Build TypeScript
RUN npx tsc

# Prune dev dependencies
RUN npm prune --production

# ============================================================================
# Production Stage
# ============================================================================
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

LABEL maintainer="KAFAAT <dev@kafaat.com>"
LABEL description="AI-powered code review agent using Claude Agent SDK"
LABEL version="1.0.0"

# Create non-root user
RUN groupadd --system agent && useradd --system --gid agent agent

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

# Disable health check - this is a CLI agent, not an HTTP service
HEALTHCHECK NONE

# Default command runs the production agent
CMD ["node", "dist/production-agent.js"]

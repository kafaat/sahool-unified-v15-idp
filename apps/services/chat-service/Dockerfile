# SAHOOL Chat Service v16.0.0
# خدمة المحادثات للسوق الزراعي

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="chat-service"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from chat-service/src/
COPY apps/services/chat-service ./chat-service/

WORKDIR /workspace/chat-service

# Install dependencies (with retries for network resilience)
# Use shell-level retry loop for better handling of network timeouts
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com; \
    for i in 1 2 3 4 5; do \
        echo "Attempt $i: Installing npm dependencies..."; \
        if npm install --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=180000 \
            --fetch-timeout=300000 \
            --prefer-offline \
            --no-audit \
            --no-fund; then break; fi; \
        if [ "$i" != "5" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=30000 --fetch-retry-maxtimeout=180000 --no-audit --no-fund)

# Generate Prisma client and verify output
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma@5 generate && \
    test -f prisma/generated/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && npx prisma@5 generate && \
     test -f prisma/generated/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application using nest build directly (skip prebuild to avoid
# re-running prisma generate which can resolve paths differently in Docker)
RUN npx nest build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma native query engine
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends curl openssl && \
    rm -rf /var/lib/apt/lists/*

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds with package-lock.json
COPY --from=builder /workspace/chat-service/package.json ./
COPY --from=builder /workspace/chat-service/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com; \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing production dependencies..."; \
        if npm ci --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=180000 \
            --fetch-timeout=300000 \
            --prefer-offline \
            --no-audit \
            --no-fund || \
        npm install --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=180000 \
            --fetch-timeout=300000 \
            --prefer-offline \
            --no-audit \
            --no-fund; then break; fi; \
        if [ "$i" != "3" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Apply security patches to production dependencies (fix known CVEs in transitive deps)
RUN npm audit fix --omit=dev --legacy-peer-deps 2>/dev/null || true

# Copy prisma schema (for migrations)
COPY --from=builder /workspace/chat-service/prisma ./prisma/

# Copy generated Prisma client from builder
# Schema uses output = "./generated/client" so actual client is at prisma/generated/client/
# Copy it to node_modules/.prisma/client/ where @prisma/client expects it at runtime
COPY --from=builder /workspace/chat-service/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /workspace/chat-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/chat-service/dist ./dist

# Set port environment variable
ENV PORT=8115
ENV NODE_ENV=production

# Expose port
EXPOSE 8115

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8115/health || exit 1

# Run database migrations and start the application
COPY --chmod=755 docker/docker-entrypoint-nestjs.sh /usr/local/bin/docker-entrypoint.sh
CMD ["/usr/local/bin/docker-entrypoint.sh"]

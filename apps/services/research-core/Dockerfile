# SAHOOL Research Core Service v15.3
# نواة البحث العلمي الزراعي

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="research-core"
LABEL version="15.3.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from research-core/src/
COPY apps/services/research-core ./research-core/

WORKDIR /workspace/research-core

# Install dependencies with retry for network resilience
# Use a retry loop to handle network issues
RUN for i in 1 2 3 4 5; do \
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 && break || \
    (echo "Attempt $i failed, retrying in 10 seconds..." && sleep 10); \
    done || (echo "npm install failed after 5 attempts" && exit 1)

# Copy prisma schema and generate client
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application
RUN npm run build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds
COPY --from=builder /workspace/research-core/package.json ./
COPY --from=builder /workspace/research-core/package-lock.json ./
# Use a retry loop to handle network issues
RUN for i in 1 2 3 4 5; do \
    npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 && break || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 && break || \
    (echo "Attempt $i failed, retrying in 10 seconds..." && sleep 10); \
    done || (echo "npm install failed after 5 attempts" && exit 1)

# Copy prisma schema (for migrations)
COPY --from=builder /workspace/research-core/prisma ./prisma/

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /workspace/research-core/node_modules/.prisma ./node_modules/.prisma/
COPY --from=builder /workspace/research-core/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/research-core/dist ./dist

# Expose port
EXPOSE 3015

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:3015/api/v1/healthz || exit 1

# Run the application
CMD ["node", "dist/main.js"]

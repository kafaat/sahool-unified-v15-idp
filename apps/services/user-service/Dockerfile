# SAHOOL User Service v16.0.0
# خدمة إدارة المستخدمين

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="user-service"
LABEL version="16.0.0"

# Prisma 5.22+ bundles its own OpenSSL, no system installation needed
# WORKDIR setup

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from user-service/src/
COPY apps/services/user-service ./user-service/

WORKDIR /workspace/user-service

# Install dependencies (with retries for network resilience)
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema and generate client
# Use environment variables to improve Prisma binary download reliability
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
ENV PRISMA_CLI_QUERY_ENGINE_TYPE=binary
ENV PRISMA_CLIENT_ENGINE_TYPE=binary
# Try multiple times with increasing delays, and skip binary download if already cached
RUN npx prisma generate --schema=./prisma/schema.prisma 2>/dev/null || \
    (echo "Retry 1..." && sleep 5 && npx prisma generate --schema=./prisma/schema.prisma) || \
    (echo "Retry 2..." && sleep 10 && npx prisma generate --schema=./prisma/schema.prisma) || \
    (echo "Retry 3..." && sleep 15 && npx prisma generate --schema=./prisma/schema.prisma) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Prisma 5.22+ bundles its own OpenSSL, no system installation needed
# wget is already available in node:20-alpine for health checks

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds
COPY --from=builder /workspace/user-service/package.json ./
COPY --from=builder /workspace/user-service/package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema (for migrations)
COPY --from=builder /workspace/user-service/prisma ./prisma/

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /workspace/user-service/node_modules/.prisma ./node_modules/.prisma/
COPY --from=builder /workspace/user-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/user-service/dist ./dist

# Set port environment variable
ENV PORT=3025

# Expose port
EXPOSE 3025

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --spider --quiet --timeout=5 http://localhost:3025/api/v1/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

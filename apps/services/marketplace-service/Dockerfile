# SAHOOL Marketplace & FinTech Service v16.0.0
# سوق سهول والخدمات المالية

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy nestjs-auth package (required for @sahool/nestjs-auth dependency)
COPY packages/nestjs-auth ./packages/nestjs-auth/

# Pre-build nestjs-auth package (install its deps and compile TypeScript)
# Note: marketplace-service uses local auth guards, nestjs-auth is a vestigial dependency
# Build errors are logged but non-fatal since local guards handle auth at runtime
WORKDIR /workspace/packages/nestjs-auth
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com; \
    if npm install --legacy-peer-deps --no-audit --no-fund 2>/dev/null && \
       npx tsc --skipLibCheck; then \
        echo "INFO: nestjs-auth built successfully"; \
    else \
        echo "WARN: nestjs-auth build skipped (marketplace uses local auth guards)"; \
    fi
# Clean nestjs-auth node_modules after pre-build to prevent npm 'extraneous' errors
# when marketplace-service resolves the file: dependency during its own npm install
RUN rm -rf node_modules

# Copy service to maintain relative path
WORKDIR /workspace
COPY apps/services/marketplace-service ./marketplace-service/

WORKDIR /workspace/marketplace-service

# Fix the file: path reference for Docker build context (both package.json and lock file)
RUN sed -i 's|file:\.\./\.\./\.\./packages/nestjs-auth|file:../packages/nestjs-auth|g' package.json || true
RUN sed -i 's|\.\./\.\./\.\./packages/nestjs-auth|../packages/nestjs-auth|g' package-lock.json || true

# Disable nestjs-auth prepare script to prevent premature tsc build during install
# (nestjs-auth is built explicitly in a later step with proper peer deps available)
WORKDIR /workspace/packages/nestjs-auth
RUN npm pkg delete scripts.prepare
WORKDIR /workspace/marketplace-service

# Install dependencies with retry loop for network resilience
# Note: Do NOT use --ignore-scripts here; Prisma needs its postinstall to download engine binaries
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
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
# Schema uses custom output (prisma/generated/client/) so verify that path
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f prisma/generated/client/index.js || \
    (echo "ERROR: Prisma client not generated at expected path" && \
     echo "Retrying prisma generate..." && \
     sleep 5 && npx prisma generate && \
     test -f prisma/generated/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application using nest build directly (skip prebuild to avoid
# re-running prisma generate which can resolve paths differently in Docker)
RUN npx nest build && \
    test -f dist/main.js || \
    (echo "ERROR: dist/main.js not found after build. Listing dist/:" && ls -la dist/ 2>/dev/null && exit 1)

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

LABEL maintainer="SAHOOL Team" \
      service="marketplace-service" \
      version="16.0.0" \
      org.opencontainers.image.title="SAHOOL Marketplace Service" \
      org.opencontainers.image.vendor="KAFAAT"

WORKDIR /app

# Install OpenSSL for Prisma, curl for health checks, and tini for signal handling
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends openssl curl tini && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

# Copy nestjs-auth package (needed for file: dependency resolution)
COPY --from=builder /workspace/packages ./packages

# Copy package files from builder (includes generated package-lock.json)
COPY --from=builder /workspace/marketplace-service/package.json ./
COPY --from=builder /workspace/marketplace-service/package-lock.json ./

# Fix the file: path reference for production stage
RUN sed -i 's|file:\.\./\.\./\.\./packages/nestjs-auth|file:./packages/nestjs-auth|g' package.json || true

# Install production dependencies with retry loop
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing production dependencies..."; \
        if (npm ci --omit=dev --ignore-scripts --legacy-peer-deps \
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
            --no-fund); then break; fi; \
        if [ "$i" != "3" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy prisma schema from builder (for migrations)
COPY --from=builder /workspace/marketplace-service/prisma ./prisma/

# Copy generated Prisma client from builder
# Schema uses output = "./generated/client" so the actual client is at prisma/generated/client/
# Copy it to node_modules/.prisma/client/ where @prisma/client expects it at runtime
COPY --from=builder /workspace/marketplace-service/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /workspace/marketplace-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/marketplace-service/dist ./dist

ENV NODE_ENV=production

# Expose port
EXPOSE 3010

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check (using curl for consistency across all services)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3010/healthz || exit 1

# Signal handling
STOPSIGNAL SIGTERM

# Init system for proper signal handling and zombie reaping
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run the application
CMD ["node", "dist/main.js"]

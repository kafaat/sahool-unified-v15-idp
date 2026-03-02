# SAHOOL Marketplace & FinTech Service v16.0.0
# سوق سهول والخدمات المالية

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="marketplace-service"
LABEL version="16.0.0"

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY shared ./shared/

# Copy nestjs-auth package (required for @sahool/nestjs-auth dependency)
COPY packages/nestjs-auth ./packages/nestjs-auth/

# Pre-build nestjs-auth package (install its deps and compile TypeScript)
WORKDIR /workspace/packages/nestjs-auth
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps --no-audit --no-fund 2>/dev/null || true && \
    npx tsc --skipLibCheck 2>/dev/null || true

# Copy service to maintain relative path
WORKDIR /workspace
COPY apps/services/marketplace-service ./marketplace-service/

WORKDIR /workspace/marketplace-service

# Fix the file: path reference for Docker build context
RUN sed -i 's|file:\.\./\.\./\.\./packages/nestjs-auth|file:../packages/nestjs-auth|g' package.json || true

# Install dependencies with retry loop for network resilience
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3 4 5; do \
        echo "Attempt $i: Installing npm dependencies..." && \
        npm install --legacy-peer-deps --ignore-scripts \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=180000 \
            --fetch-timeout=300000 \
            --prefer-offline \
            --no-audit \
            --no-fund && break || \
        (echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10))); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=30000 --fetch-retry-maxtimeout=180000 --no-audit --no-fund)

# Generate Prisma client and verify output
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f node_modules/.prisma/client/index.js || \
    (echo "ERROR: Prisma client not generated at expected path" && \
     echo "Retrying prisma generate..." && \
     sleep 5 && npx prisma generate && \
     test -f node_modules/.prisma/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application using nest build directly (skip prebuild to avoid
# re-running prisma generate which can resolve paths differently in Docker)
RUN npx nest build && \
    test -f dist/main.js || \
    (echo "ERROR: dist/main.js not found after build. Listing dist/:" && ls -la dist/ 2>/dev/null && exit 1)

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install OpenSSL for Prisma native query engine (bookworm-slim ships OpenSSL 3.x)
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssl && \
    rm -rf /var/lib/apt/lists/*

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
        echo "Attempt $i: Installing production dependencies..." && \
        (npm ci --omit=dev --ignore-scripts --legacy-peer-deps \
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
            --no-fund) && break || \
        (echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10))); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Copy prisma schema from builder (for migrations)
COPY --from=builder /workspace/marketplace-service/prisma ./prisma/

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /workspace/marketplace-service/node_modules/.prisma ./node_modules/.prisma/
COPY --from=builder /workspace/marketplace-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/marketplace-service/dist ./dist

ENV NODE_ENV=production

# Expose port
EXPOSE 3010

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check (using Node.js built-in fetch — no curl dependency needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://localhost:3010/healthz').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"

# Run the application
CMD ["node", "dist/main.js"]

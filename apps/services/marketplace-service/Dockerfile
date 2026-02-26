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
COPY apps/services/shared ./shared/

# Copy nestjs-auth package (workspace dependency: @sahool/nestjs-auth)
COPY packages/nestjs-auth ./nestjs-auth/
COPY tsconfig.base.json /tsconfig.base.json

# Copy service to maintain relative path
COPY apps/services/marketplace-service ./marketplace-service/

WORKDIR /workspace/marketplace-service

# Replace workspace dependency with local file path for Docker build
RUN sed -i 's|"@sahool/nestjs-auth": "16.0.0"|"@sahool/nestjs-auth": "file:../nestjs-auth"|' package.json

# Install dependencies with retry loop for network resilience
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3 4 5; do \
        echo "Attempt $i: Installing npm dependencies..." && \
        npm install --legacy-peer-deps \
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
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=30000 --fetch-retry-maxtimeout=180000 --no-audit --no-fund)

# Generate Prisma client and verify output
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f node_modules/.prisma/client/index.js || \
    (echo "ERROR: Prisma client not generated at expected path" && \
     echo "Retrying prisma generate..." && \
     sleep 5 && npx prisma generate && \
     test -f node_modules/.prisma/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build nestjs-auth package (dist/ is gitignored)
RUN npm install --no-save \
    @nestjs/common@^10.0.0 @nestjs/core@^10.0.0 rxjs@^7.0.0 \
    @nestjs/passport@^10.0.0 passport@^0.7.0 passport-jwt@^4.0.0 @nestjs/jwt@^10.0.0 \
    redis@^4.0.0 ioredis@^5.0.0 "@liaoliaots/nestjs-redis@^9.0.0" \
    --legacy-peer-deps || true
WORKDIR /workspace/nestjs-auth
RUN ln -sf /workspace/marketplace-service/node_modules ./node_modules && \
    npx tsc --skipLibCheck
WORKDIR /workspace/marketplace-service

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

# Copy nestjs-auth dist + package.json for runtime (file:../nestjs-auth reference)
COPY --from=builder /workspace/nestjs-auth/dist /nestjs-auth/dist/
COPY --from=builder /workspace/nestjs-auth/package.json /nestjs-auth/package.json

# Copy package files from builder (includes generated package-lock.json)
COPY --from=builder /workspace/marketplace-service/package.json ./
COPY --from=builder /workspace/marketplace-service/package-lock.json ./
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

# Symlink node_modules into nestjs-auth so its require() calls resolve peer deps
RUN ln -s /app/node_modules /nestjs-auth/node_modules

# Copy built application
COPY --from=builder /workspace/marketplace-service/dist ./dist

# Expose port
EXPOSE 3010

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app /nestjs-auth
USER node

# Health check (using Node.js built-in fetch — no curl dependency needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://localhost:3010/healthz').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"

# Run the application
CMD ["node", "dist/main.js"]

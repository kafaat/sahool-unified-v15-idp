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

# Copy nestjs-auth package (workspace dependency: @sahool/nestjs-auth)
COPY packages/nestjs-auth ./nestjs-auth/
COPY tsconfig.base.json /tsconfig.base.json

# Copy service to maintain relative path: ../../shared/ from chat-service/src/
COPY apps/services/chat-service ./chat-service/

WORKDIR /workspace/chat-service

# Replace workspace dependency with local file path for Docker build
RUN sed -i 's|"@sahool/nestjs-auth": "16.0.0"|"@sahool/nestjs-auth": "file:../nestjs-auth"|' package.json

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
        echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=30000 --fetch-retry-maxtimeout=180000 --no-audit --no-fund)

# Generate Prisma client and verify output
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate && \
    test -f node_modules/.prisma/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && npx prisma generate && \
     test -f node_modules/.prisma/client/index.js) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build nestjs-auth package (dist/ is gitignored)
RUN npm install --no-save \
    @nestjs/common@^10.0.0 @nestjs/core@^10.0.0 rxjs@^7.0.0 \
    @nestjs/passport@^10.0.0 passport@^0.7.0 passport-jwt@^4.0.0 @nestjs/jwt@^10.0.0 \
    redis@^4.0.0 ioredis@^5.0.0 "@liaoliaots/nestjs-redis@^9.0.0" \
    --legacy-peer-deps || true
WORKDIR /workspace/nestjs-auth
RUN ln -sf /workspace/chat-service/node_modules ./node_modules && \
    npx tsc --skipLibCheck
WORKDIR /workspace/chat-service

# Build the application using nest build directly (skip prebuild to avoid
# re-running prisma generate which can resolve paths differently in Docker)
RUN npx nest build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma native query engine
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl openssl && \
    rm -rf /var/lib/apt/lists/*

# Copy nestjs-auth dist + package.json for runtime (file:../nestjs-auth reference)
COPY --from=builder /workspace/nestjs-auth/dist /nestjs-auth/dist/
COPY --from=builder /workspace/nestjs-auth/package.json /nestjs-auth/package.json

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
        echo "Attempt $i failed, waiting before retry..." && sleep $((i * 10)); \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Symlink node_modules into nestjs-auth so its require() calls resolve peer deps
RUN ln -s /app/node_modules /nestjs-auth/node_modules

# Copy prisma schema (for migrations)
COPY --from=builder /workspace/chat-service/prisma ./prisma/

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /workspace/chat-service/node_modules/.prisma ./node_modules/.prisma/
COPY --from=builder /workspace/chat-service/node_modules/@prisma/client ./node_modules/@prisma/client/

# Copy built application
COPY --from=builder /workspace/chat-service/dist ./dist

# Set port environment variable
ENV PORT=8115
ENV NODE_ENV=production

# Expose port
EXPOSE 8115

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app /nestjs-auth
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8115/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

# SAHOOL Crop Growth Model Service v16.0
# خدمة نموذج نمو المحاصيل
# Based on WOFOST/DSSAT/APSIM mechanistic models

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy nestjs-auth package (workspace dependency: @sahool/nestjs-auth)
COPY packages/nestjs-auth ./nestjs-auth/

# Copy root tsconfig.base.json (nestjs-auth tsconfig extends ../../tsconfig.base.json)
COPY tsconfig.base.json /tsconfig.base.json

# Copy service to maintain relative path: ../../shared/ from crop-growth-model/src/
COPY apps/services/crop-growth-model /workspace/crop-growth-model/

WORKDIR /workspace/crop-growth-model

# Replace workspace dependency with local file path for Docker build
RUN sed -i 's|"@sahool/nestjs-auth": "16.0.0"|"@sahool/nestjs-auth": "file:../nestjs-auth"|' package.json

# Disable nestjs-auth prepare script to prevent premature tsc build during install
# (nestjs-auth is built explicitly in a later step with proper peer deps available)
WORKDIR /workspace/nestjs-auth
RUN npm pkg delete scripts.prepare
WORKDIR /workspace/crop-growth-model

# Install dependencies with resilient retry loop and npm cache
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing dependencies..."; \
        if npm install --legacy-peer-deps --ignore-scripts \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund; then break; fi; \
        if [ "$i" != "3" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --no-audit --no-fund)

# Build nestjs-auth package (dist/ is gitignored and excluded by .dockerignore)
# Must build AFTER service npm install so peer deps (@nestjs/common etc.) are available
# Install nestjs-auth devDependencies (redis, ioredis types) needed for tsc compilation
WORKDIR /workspace/nestjs-auth
RUN ln -sf /workspace/crop-growth-model/node_modules ./node_modules && \
    npm install --no-save typescript@5.9.3 redis@4 @liaoliaots/nestjs-redis@10 ioredis@5 2>/dev/null; \
    ./node_modules/.bin/tsc --skipLibCheck || \
    npx -y typescript@5.9.3 tsc --skipLibCheck || \
    (echo "ERROR: nestjs-auth build failed" && exit 1)
WORKDIR /workspace/crop-growth-model

# Build the application
RUN npx nest build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

LABEL maintainer="SAHOOL Team" \
      service="crop-growth-model" \
      version="16.0.0" \
      org.opencontainers.image.title="SAHOOL Crop Growth Model" \
      org.opencontainers.image.vendor="KAFAAT"

WORKDIR /app

# Install curl for health checks and tini for proper signal handling
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends curl tini && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

# Copy only nestjs-auth dist + package.json for runtime (avoid builder's node_modules symlink)
# Path must be /nestjs-auth/ to match file:../nestjs-auth reference from /app/
COPY --from=builder /workspace/nestjs-auth/dist /nestjs-auth/dist/
COPY --from=builder /workspace/nestjs-auth/package.json /nestjs-auth/package.json

# Copy package files from builder (includes generated package-lock.json)
COPY --from=builder /workspace/crop-growth-model/package.json ./
COPY --from=builder /workspace/crop-growth-model/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing production dependencies..."; \
        if (npm ci --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund || \
        npm install --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --prefer-offline \
            --no-audit \
            --no-fund); then break; fi; \
        if [ "$i" != "3" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Symlink node_modules into nestjs-auth so its require() calls resolve peer deps
# (Node.js resolves from /nestjs-auth/ → /nestjs-auth/node_modules/ → found)
RUN ln -s /app/node_modules /nestjs-auth/node_modules

# Copy built application
COPY --from=builder /workspace/crop-growth-model/dist ./dist

# Expose port
EXPOSE 3023

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app /nestjs-auth
USER node

ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3023/healthz || exit 1

# Signal handling
STOPSIGNAL SIGTERM

# Init system for proper signal handling and zombie reaping
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run the application
CMD ["node", "dist/main.js"]

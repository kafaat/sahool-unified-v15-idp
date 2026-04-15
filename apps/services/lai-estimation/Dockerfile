# SAHOOL LAI Estimation Service v16.0
# خدمة تقدير مؤشر مساحة الأوراق
# Based on LAI-TransNet Two-Stage Transfer Learning Framework

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

# Copy service to maintain relative path: ../../shared/ from lai-estimation/src/
COPY apps/services/lai-estimation /workspace/lai-estimation/

WORKDIR /workspace/lai-estimation

# Replace workspace dependency with local file path for Docker build
# package.json may use version string OR file: reference depending on context
RUN sed -i 's|"@sahool/nestjs-auth": "[^"]*"|"@sahool/nestjs-auth": "file:../nestjs-auth"|' package.json

# Disable nestjs-auth prepare script to prevent premature tsc build during install
# (nestjs-auth is built explicitly in a later step with proper peer deps available)
WORKDIR /workspace/nestjs-auth
RUN npm pkg delete scripts.prepare
WORKDIR /workspace/lai-estimation

# Validate package.json is valid JSON (fail fast if corrupted by merge conflicts)
RUN node -e "JSON.parse(require('fs').readFileSync('package.json','utf8'))" || \
    (echo 'ERROR: package.json is invalid JSON. Check for merge conflict markers (<<<<<<< HEAD).' && exit 1)

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
# 1. Install compile-time deps needed by nestjs-auth (@liaoliaots/nestjs-redis@10
#    satisfies the ^10.0.0 peer dep declared in nestjs-auth/package.json for NestJS 10)
# 2. Symlink service node_modules into nestjs-auth so tsc can resolve all peer deps
# 3. Run tsc with local binary, falling back to npx if not found
RUN npm install --no-save --legacy-peer-deps \
    typescript@5.9.3 "@liaoliaots/nestjs-redis@10" ioredis@5 redis@4 && \
    ln -sf /workspace/lai-estimation/node_modules /workspace/nestjs-auth/node_modules && \
    (/workspace/lai-estimation/node_modules/.bin/tsc -p /workspace/nestjs-auth/tsconfig.json --skipLibCheck || \
     npx -y typescript@5.9.3 tsc -p /workspace/nestjs-auth/tsconfig.json --skipLibCheck || \
     (echo "ERROR: nestjs-auth build failed" && exit 1))

# Build the application
RUN npx nest build

# Production stage
FROM node:${NODE_VERSION}-bookworm-slim AS production

LABEL maintainer="SAHOOL Team" \
      service="lai-estimation" \
      version="16.0.0" \
      org.opencontainers.image.title="SAHOOL LAI Estimation Service" \
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
# NOTE: Using npm ci for deterministic builds with package-lock.json
COPY --from=builder /workspace/lai-estimation/package.json ./
COPY --from=builder /workspace/lai-estimation/package-lock.json ./

# Install production dependencies with resilient retry loop
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

# Apply security patches to production dependencies (fix known CVEs in transitive deps)
RUN npm audit fix --omit=dev --legacy-peer-deps --ignore-scripts 2>/dev/null || true

# Symlink node_modules into nestjs-auth so its require() calls resolve peer deps
# (Node.js resolves from /nestjs-auth/ → /nestjs-auth/node_modules/ → found)
RUN ln -s /app/node_modules /nestjs-auth/node_modules

# Copy built application
COPY --from=builder /workspace/lai-estimation/dist ./dist

# Expose port
EXPOSE 3022

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app /nestjs-auth
USER node

ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3022/healthz || exit 1

# Signal handling
STOPSIGNAL SIGTERM

# Init system for proper signal handling and zombie reaping
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run the application
CMD ["node", "dist/main.js"]

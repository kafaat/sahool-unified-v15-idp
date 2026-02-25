# SAHOOL LAI Estimation Service v16.0
# خدمة تقدير مؤشر مساحة الأوراق
# Based on LAI-TransNet Two-Stage Transfer Learning Framework

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="lai-estimation"
LABEL version="16.0.0"

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

# Install dependencies with retry for network resilience
# Replace workspace dependency with local file path for Docker build
RUN sed -i 's|"@sahool/nestjs-auth": "16.0.0"|"@sahool/nestjs-auth": "file:../nestjs-auth"|' package.json && \
    npm config set registry https://registry.npmmirror.com; \
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    (npm config set registry https://registry.npmjs.org && \
    npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000)

# Build nestjs-auth package (dist/ is gitignored and excluded by .dockerignore)
# Must build AFTER service npm install so peer deps (@nestjs/common etc.) are available
RUN cd /workspace/nestjs-auth && \
    ln -sf /workspace/lai-estimation/node_modules ./node_modules && \
    npx tsc --skipLibCheck || \
    npx -y typescript@5.9.3 tsc --skipLibCheck || \
    echo "WARN: nestjs-auth build failed"

# Build the application
RUN npm run build

# Production stage
FROM node:${NODE_VERSION}-alpine AS production

# Re-declare build arg for this stage
ARG NODE_VERSION=20

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy nestjs-auth package for runtime dependency resolution
# Path must be /nestjs-auth/ to match file:../nestjs-auth reference from /app/
COPY --from=builder /workspace/nestjs-auth /nestjs-auth/

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds with package-lock.json
COPY --from=builder /workspace/lai-estimation/package.json ./
COPY --from=builder /workspace/lai-estimation/package-lock.json ./
RUN npm config set registry https://registry.npmmirror.com && \
    (npm ci --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000) || \
    (npm config set registry https://registry.npmjs.org && \
    (npm ci --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000))

# Symlink node_modules into nestjs-auth so its require() calls resolve peer deps
# (Node.js resolves from /nestjs-auth/ → /nestjs-auth/node_modules/ → found)
RUN ln -sf /app/node_modules /nestjs-auth/node_modules

# Copy built application
COPY --from=builder /workspace/lai-estimation/dist ./dist

# Expose port
EXPOSE 3022

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app /nestjs-auth
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3022/api/v1/lai/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

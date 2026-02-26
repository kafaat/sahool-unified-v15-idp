# SAHOOL Disaster Assessment Service v16.0
# خدمة تقييم الكوارث الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model
# With PostgreSQL persistence via Prisma ORM

# Build stage
ARG NODE_VERSION=20

FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="disaster-assessment"
LABEL version="16.0.0"

WORKDIR /app

# Copy nestjs-auth package (workspace dependency: @sahool/nestjs-auth)
COPY packages/nestjs-auth /nestjs-auth/
COPY tsconfig.base.json /tsconfig.base.json

# Copy package files first for better layer caching
COPY apps/services/disaster-assessment/package*.json ./

# Replace workspace dependency with local file path for Docker build
RUN sed -i 's|"@sahool/nestjs-auth": "16.0.0"|"@sahool/nestjs-auth": "file:../nestjs-auth"|' package.json

# Copy prisma schema BEFORE installing dependencies (required for postinstall hook)
COPY apps/services/disaster-assessment/prisma ./prisma/

# Install dependencies with retry for network resilience
# Use --ignore-scripts to prevent postinstall from running before prisma schema is available
# Then explicitly run prisma generate
RUN npm config set registry https://registry.npmmirror.com; \
    (npm ci --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000) || \
    (npm config set registry https://registry.npmjs.org && \
    (npm ci --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000))

# Generate Prisma client (required before build)
RUN npx prisma generate

# Copy source code
COPY apps/services/disaster-assessment/ .

# Build nestjs-auth package (dist/ is gitignored)
RUN npm install --no-save redis @nestjs/passport passport passport-jwt @nestjs/jwt ioredis @liaoliaots/nestjs-redis 2>/dev/null || true
RUN cd /nestjs-auth && \
    ln -sf /app/node_modules ./node_modules && \
    npx tsc --skipLibCheck || \
    npx -y typescript@5.9.3 tsc --skipLibCheck || \
    echo "WARN: nestjs-auth build failed"

# Build the application
RUN npm run build

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
COPY --from=builder /nestjs-auth/dist /nestjs-auth/dist/
COPY --from=builder /nestjs-auth/package.json /nestjs-auth/package.json

# Copy package files from builder (includes generated package-lock.json)
# NOTE: Using npm ci for deterministic builds
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json ./

# Copy prisma schema for migrations
COPY --from=builder /app/prisma ./prisma/

RUN npm config set registry https://registry.npmmirror.com; \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000) || \
    (npm config set registry https://registry.npmjs.org && \
    (npm ci --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 || \
    npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000))

# Copy generated Prisma client from builder (avoid npx downloading incompatible version)
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma/
COPY --from=builder /app/node_modules/@prisma/client ./node_modules/@prisma/client/

# Symlink node_modules into nestjs-auth so its require() calls resolve peer deps
RUN ln -s /app/node_modules /nestjs-auth/node_modules

# Copy built application
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3020

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app /nestjs-auth
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3020/healthz || exit 1

# Run database migrations and start the application
# Note: In production, migrations should ideally be run as a separate init container
# Skip migrations when SKIP_DB_INIT=true (for container tests without database)
CMD ["sh", "-c", "if [ \"$SKIP_DB_INIT\" = \"true\" ]; then echo 'Skipping database migrations (SKIP_DB_INIT=true)'; else npx prisma migrate deploy || echo 'Migration failed, continuing anyway...'; fi && node dist/main.js"]

# Sahool Web Dashboard - Docker Configuration
# لوحة التحكم الرئيسية سهول - إعدادات Docker
# Multi-stage monorepo build for Next.js 15

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy root package files for workspace resolution
COPY package.json package-lock.json* ./

# Copy workspace package definitions
COPY packages/shared-utils/package.json ./packages/shared-utils/
COPY packages/shared-ui/package.json ./packages/shared-ui/
COPY packages/shared-hooks/package.json ./packages/shared-hooks/
COPY packages/shared-types/package.json ./packages/shared-types/
COPY packages/api-client/package.json ./packages/api-client/
COPY packages/tailwind-config/package.json ./packages/tailwind-config/
COPY packages/typescript-config/package.json ./packages/typescript-config/
COPY packages/design-system/package.json ./packages/design-system/
COPY packages/i18n/package.json ./packages/i18n/
COPY packages/field-shared/package.json ./packages/field-shared/
COPY packages/mock-data/package.json ./packages/mock-data/
COPY packages/nestjs-auth/package.json ./packages/nestjs-auth/
COPY packages/shared-audit/package.json ./packages/shared-audit/
COPY packages/shared-crypto/package.json ./packages/shared-crypto/
COPY packages/shared-db/package.json ./packages/shared-db/
COPY packages/shared-events/package.json ./packages/shared-events/

# Copy web package.json
COPY apps/web/package.json ./apps/web/

# Copy service workspaces (needed for npm workspace resolution)
COPY apps/services/field-management-service/package.json ./apps/services/field-management-service/
COPY apps/services/chat-service/package.json ./apps/services/chat-service/
COPY apps/services/crop-growth-model/package.json ./apps/services/crop-growth-model/
COPY apps/services/disaster-assessment/package.json ./apps/services/disaster-assessment/
COPY apps/services/iot-service/package.json ./apps/services/iot-service/
COPY apps/services/lai-estimation/package.json ./apps/services/lai-estimation/
COPY apps/services/marketplace-service/package.json ./apps/services/marketplace-service/
COPY apps/services/research-core/package.json ./apps/services/research-core/
COPY apps/services/yield-prediction/package.json ./apps/services/yield-prediction/
COPY apps/services/yield-prediction-service/package.json ./apps/services/yield-prediction-service/
COPY apps/admin/package.json ./apps/admin/

# Install all dependencies at root level with retry loop and mirror fallback
RUN --mount=type=cache,target=/root/.npm \
    for i in 1 2 3 4 5; do \
        if npm install --legacy-peer-deps \
            --prefer-offline \
            --fetch-timeout=300000 \
            --no-audit \
            --no-fund; then break; fi; \
        if [ "$i" != "5" ]; then echo "Attempt $i failed, waiting before retry..."; sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmmirror.com && \
     npm install --legacy-peer-deps --fetch-timeout=300000 --no-audit --no-fund)

# Build the web app
FROM base AS builder
WORKDIR /app

# Copy everything from deps
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/package-lock.json ./package-lock.json

# Copy all packages source
COPY packages ./packages

# Copy web app
COPY apps/web ./apps/web

# Build arguments
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
ENV NEXT_TELEMETRY_DISABLED=1
ENV DOCKER_BUILD=true

# Build shared packages first
RUN npm run build --workspace=packages/shared-utils --if-present || true
RUN npm run build --workspace=packages/shared-ui --if-present || true
RUN npm run build --workspace=packages/shared-hooks --if-present || true
RUN npm run build --workspace=packages/api-client --if-present || true

# Build web app from root (using npm workspaces)
RUN npm run build --workspace=apps/web

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone build from the correct location
# Next.js standalone in monorepo outputs to apps/web/.next/standalone
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/public ./apps/web/public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Runtime API Gateway URL (overrides build-time NEXT_PUBLIC_API_URL for server-side rewrites)
# In K8s: set to http://kong.kong.svc.cluster.local:8000
# In Docker Compose: set to http://kong-gateway:8000
ENV API_GATEWAY_URL=""

LABEL org.opencontainers.image.title="SAHOOL Web Dashboard" \
      org.opencontainers.image.description="Web dashboard for SAHOOL National Agricultural Intelligence Platform" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.version="16.0.0" \
      org.opencontainers.image.source="https://github.com/kafaat/sahool-unified-v15-idp" \
      org.opencontainers.image.base.name="node:20-alpine"

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

# In monorepo standalone, server.js is at apps/web/server.js
WORKDIR /app/apps/web
CMD ["node", "server.js"]

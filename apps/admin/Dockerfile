# Sahool Admin Dashboard - Docker Configuration
# لوحة تحكم سهول - إعدادات Docker
# Simplified monorepo build

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
COPY packages/shared-types/package.json ./packages/shared-types/

# Copy admin package.json
COPY apps/admin/package.json ./apps/admin/

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
COPY apps/web/package.json ./apps/web/

# Validate all copied package.json files are valid JSON (fail fast if corrupted by merge conflicts)
RUN node -e "const fs=require('fs'),path=require('path');function find(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()&&e.name!='node_modules'?find(path.join(d,e.name)):e.name=='package.json'?[path.join(d,e.name)]:[]);}const files=find('.');let ok=true;files.forEach(f=>{try{JSON.parse(fs.readFileSync(f,'utf8'));}catch(e){console.error('ERROR: '+f+' is invalid JSON. Check for merge conflict markers (<<<<<<< HEAD).');ok=false;}});if(!ok)process.exit(1);console.log('All '+files.length+' package.json files are valid JSON.');"

# Install all dependencies at root level with retry loop and mirror fallback
# NOTE: --legacy-peer-deps is required due to React 19 compatibility issues with some packages
# This is a known issue with Next.js 15 + React 19 ecosystem packages
# TODO: Remove --legacy-peer-deps once all packages are updated to React 19
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

# Build the admin app
FROM base AS builder
WORKDIR /app

# Copy everything from deps
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/package-lock.json ./package-lock.json

# Copy all packages source
COPY packages ./packages

# Copy admin app
COPY apps/admin ./apps/admin

# Build arguments
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

# Build shared packages first
RUN npm run build --workspace=packages/shared-utils --if-present || true
RUN npm run build --workspace=packages/shared-ui --if-present || true
RUN npm run build --workspace=packages/shared-hooks --if-present || true
RUN npm run build --workspace=packages/api-client --if-present || true

# Build admin app from root (using npm workspaces)
RUN npm run build --workspace=apps/admin

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Install tini for proper PID 1 signal handling
RUN apk add --no-cache tini

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone build from the correct location
# Next.js standalone in monorepo outputs to apps/admin/.next/standalone
# The standalone folder contains the full monorepo structure
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/static ./apps/admin/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/public ./apps/admin/public

USER nextjs

EXPOSE 3002

ENV PORT=3002
ENV HOSTNAME="0.0.0.0"

# Runtime API Gateway URL (overrides build-time NEXT_PUBLIC_API_URL for server-side rewrites)
# In K8s: set to http://kong.kong.svc.cluster.local:8000
# In Docker Compose: set to http://kong-gateway:8000
ENV API_GATEWAY_URL=""

LABEL org.opencontainers.image.title="SAHOOL Admin Dashboard" \
      org.opencontainers.image.description="Admin portal for SAHOOL National Agricultural Intelligence Platform" \
      org.opencontainers.image.vendor="KAFAAT" \
      org.opencontainers.image.version="16.0.0" \
      org.opencontainers.image.source="https://github.com/kafaat/sahool-unified-v15-idp" \
      org.opencontainers.image.base.name="node:20-alpine"

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3002/api/health || exit 1

# Use tini as init system for proper signal handling and zombie reaping
ENTRYPOINT ["/sbin/tini", "--"]

# In monorepo standalone, server.js is at apps/admin/server.js
WORKDIR /app/apps/admin
CMD ["node", "server.js"]

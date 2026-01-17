# Sahool Web Application - Docker Configuration
# SAHOOL - National Agricultural Intelligence Platform
# Multi-stage build for Next.js 15 with monorepo workspace support

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy root package files for workspace resolution
COPY package.json package-lock.json* ./

# Copy workspace package definitions
COPY packages/shared-types/package.json ./packages/shared-types/
COPY packages/shared-utils/package.json ./packages/shared-utils/
COPY packages/shared-ui/package.json ./packages/shared-ui/
COPY packages/shared-hooks/package.json ./packages/shared-hooks/
COPY packages/api-client/package.json ./packages/api-client/
COPY packages/i18n/package.json ./packages/i18n/
COPY packages/tailwind-config/package.json ./packages/tailwind-config/
COPY packages/typescript-config/package.json ./packages/typescript-config/

# Copy web app package.json
COPY apps/web/package.json ./apps/web/

# Install all dependencies at root level
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

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

# Build arguments for environment configuration
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL
ARG NEXT_PUBLIC_SENTRY_DSN

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_SENTRY_DSN=$NEXT_PUBLIC_SENTRY_DSN
ENV NEXT_TELEMETRY_DISABLED=1
# Enable standalone output for Docker deployment
ENV DOCKER_BUILD=true

# Build shared packages first (in dependency order)
RUN npm run build --workspace=packages/shared-types --if-present || true
RUN npm run build --workspace=packages/shared-utils --if-present || true
RUN npm run build --workspace=packages/i18n --if-present || true
RUN npm run build --workspace=packages/shared-ui --if-present || true
RUN npm run build --workspace=packages/api-client --if-present || true
RUN npm run build --workspace=packages/shared-hooks --if-present || true

# Build web app from root (using npm workspaces)
RUN npm run build --workspace=apps/web

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone build from the correct location
# Next.js standalone in monorepo outputs to apps/web/.next/standalone
# The standalone folder contains the full monorepo structure
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/public ./apps/web/public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

# In monorepo standalone, server.js is at apps/web/server.js
WORKDIR /app/apps/web
CMD ["node", "server.js"]

# Sahool Admin Dashboard - Docker Configuration
# لوحة تحكم سهول - إعدادات Docker
# Simplified monorepo build

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy root package files for workspace resolution
COPY package.json package-lock.json ./

# Copy workspace package definitions
COPY packages/shared-utils/package.json ./packages/shared-utils/
COPY packages/shared-ui/package.json ./packages/shared-ui/
COPY packages/shared-hooks/package.json ./packages/shared-hooks/
COPY packages/api-client/package.json ./packages/api-client/
COPY packages/tailwind-config/package.json ./packages/tailwind-config/
COPY packages/typescript-config/package.json ./packages/typescript-config/

# Copy admin package.json
COPY apps/admin/package.json ./apps/admin/

# Install all dependencies at root level
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

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

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone build from the correct location
# Next.js standalone in monorepo outputs to apps/admin/.next/standalone
# The standalone folder contains the full monorepo structure
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/static ./apps/admin/.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/public ./apps/admin/public

USER nextjs

EXPOSE 3001

ENV PORT=3001
ENV HOSTNAME="0.0.0.0"

# In monorepo standalone, server.js is at apps/admin/server.js
WORKDIR /app/apps/admin
CMD ["node", "server.js"]

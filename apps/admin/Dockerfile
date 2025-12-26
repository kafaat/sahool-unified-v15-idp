# Sahool Admin Dashboard - Docker Configuration
# لوحة تحكم سهول - إعدادات Docker
# Monorepo-aware build

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

# Install all dependencies
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Build packages first
FROM base AS package-builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages ./packages

# Copy package source files
COPY packages/typescript-config ./packages/typescript-config
COPY packages/tailwind-config ./packages/tailwind-config
COPY packages/shared-utils ./packages/shared-utils
COPY packages/shared-ui ./packages/shared-ui
COPY packages/shared-hooks ./packages/shared-hooks
COPY packages/api-client ./packages/api-client
COPY package.json package-lock.json ./

# Build shared packages
RUN npm run build --workspace=packages/shared-utils --if-present || true
RUN npm run build --workspace=packages/shared-ui --if-present || true
RUN npm run build --workspace=packages/shared-hooks --if-present || true
RUN npm run build --workspace=packages/api-client --if-present || true

# Build the admin app
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=package-builder /app/packages ./packages
COPY package.json package-lock.json ./
COPY apps/admin ./apps/admin

# Build arguments
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

# Ensure dependencies are accessible from admin directory
# Create a proper node_modules structure in admin directory
WORKDIR /app/apps/admin
# Install dependencies locally (npm workspaces will link to root packages)
RUN npm install --legacy-peer-deps --no-package-lock

# Build from admin directory
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Create directories
RUN mkdir -p ./public
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy standalone build
# In monorepo, Next.js standalone output structure may vary
# First copy the standalone directory content
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/static ./apps/admin/.next/static

# Copy node_modules from root (contains next and all deps)
# This ensures next module is always available regardless of standalone trace issues
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules

# Also copy admin's local node_modules as additional fallback
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/node_modules ./apps/admin/node_modules

# Verify server.js exists - check both possible locations in monorepo structure
RUN if [ -f "./apps/admin/server.js" ]; then \
      echo "Found server.js in apps/admin/, moving to root..."; \
      cp ./apps/admin/server.js ./server.js; \
    fi && \
    if [ ! -f "./server.js" ]; then \
      echo "ERROR: server.js not found"; \
      ls -la . || true; \
      ls -la ./apps/admin/ 2>/dev/null || true; \
      exit 1; \
    fi

# Verify next module is available
RUN if [ ! -d "./node_modules/next" ]; then \
      echo "ERROR: next module not found in node_modules"; \
      exit 1; \
    fi

USER nextjs

EXPOSE 3001

ENV PORT=3001
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

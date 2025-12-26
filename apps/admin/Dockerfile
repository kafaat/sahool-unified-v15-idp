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
# Automatically leverage output traces to reduce image size
# Next.js standalone output is in apps/admin/.next/standalone
# Copy the standalone output - it should contain server.js, node_modules/, and the app code
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/public ./public 2>/dev/null || true

# Fallback: Copy node_modules from builder if standalone didn't include all dependencies
# This can happen in monorepo setups where Next.js standalone doesn't trace all workspace dependencies
# We copy the admin's local node_modules as a backup (it should have next and other deps)
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/node_modules ./node_modules_fallback

# Merge fallback node_modules into main node_modules if next is missing
RUN if [ ! -d "./node_modules/next" ] && [ -d "./node_modules_fallback/next" ]; then \
      echo "WARNING: next not found in standalone, using fallback..."; \
      mkdir -p ./node_modules; \
      cp -r ./node_modules_fallback/* ./node_modules/; \
    fi && \
    rm -rf ./node_modules_fallback && \
    # Verify next is now available
    if [ ! -d "./node_modules/next" ]; then \
      echo "ERROR: next module is still missing after fallback copy"; \
      exit 1; \
    fi

# Verify server.js exists before switching user
RUN if [ ! -f "./server.js" ]; then \
      echo "ERROR: server.js not found in standalone output"; \
      echo "Checking standalone structure..."; \
      ls -la . || true; \
      find . -name "server.js" -type f 2>/dev/null || echo "No server.js found"; \
      exit 1; \
    fi

# Fallback: Copy node_modules from builder if standalone didn't include all dependencies
# This can happen in monorepo setups where Next.js standalone doesn't trace all workspace dependencies
# We copy the admin's local node_modules as a backup (it should have next and other deps)
COPY --from=builder --chown=nextjs:nodejs /app/apps/admin/node_modules ./node_modules_fallback

# Merge fallback node_modules into main node_modules if next is missing
RUN if [ ! -d "./node_modules/next" ] && [ -d "./node_modules_fallback/next" ]; then \
      echo "WARNING: next not found in standalone, using fallback..."; \
      mkdir -p ./node_modules; \
      cp -r ./node_modules_fallback/* ./node_modules/; \
    fi && \
    rm -rf ./node_modules_fallback && \
    # Verify next is now available
    if [ ! -d "./node_modules/next" ]; then \
      echo "ERROR: next module is still missing after fallback copy"; \
      exit 1; \
    fi

# Verify server.js exists before switching user
RUN if [ ! -f "./server.js" ]; then \
      echo "ERROR: server.js not found in standalone output"; \
      echo "Checking standalone structure..."; \
      ls -la . || true; \
      find . -name "server.js" -type f 2>/dev/null || echo "No server.js found"; \
      exit 1; \
    fi

USER nextjs

EXPOSE 3001

ENV PORT=3001
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

# Sahool Admin Dashboard - Docker Configuration
# لوحة تحكم سهول - إعدادات Docker

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
# Prefer a reproducible install with package-lock, but fall back to `npm install`
# when the lockfile is not present (prevents build failure in local trees).
RUN if [ -f package-lock.json ]; then \
	npm ci; \
	else \
	npm install; \
	fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build arguments
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
# Increase Node memory during build to avoid webpack OOM errors
ENV NODE_OPTIONS=--max-old-space-size=4096

# Ensure public directory exists (Next.js may not create it)
RUN mkdir -p public

# Build
RUN npm run build

# Ensure public directory exists (Next.js may not create it)
RUN mkdir -p ./public || true

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

<<<<<<< HEAD
# Copy public directory (will exist after mkdir in builder stage)
COPY --from=builder /app/public ./public

=======
>>>>>>> 68c4f2a7b84c7c441a567209d85cf70ff80c5c7e
# Set the correct permission for prerender cache
RUN mkdir -p .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy public folder (created in builder stage even if empty)
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3001

ENV PORT=3001
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

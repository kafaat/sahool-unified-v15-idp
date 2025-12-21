FROM node:20-alpine AS base
WORKDIR /app

# 1) Install dependencies
FROM base AS deps
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json ./
RUN npm ci

# 2) Build
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next build (recommended to disable telemetry in CI)
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# 3) Run
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# Copy standalone output (requires next.config.js output: 'standalone')
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs
EXPOSE 3001
ENV PORT=3001
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]

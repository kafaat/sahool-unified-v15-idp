# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Field Core Service - Dockerfile
# Geospatial Field Management with PostGIS & Prisma Support
# ═══════════════════════════════════════════════════════════════════════════════

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy Prisma schema and generate client
COPY prisma ./prisma
RUN npx prisma generate

# Copy source and build
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

# Stage 2: Production
FROM node:18-alpine

WORKDIR /app

# Create non-root user for security (using system to avoid GID conflicts)
RUN addgroup --system sahool && \
    adduser --system --ingroup sahool --disabled-password --gecos "" sahool

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy built files, Prisma, and production dependencies
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
RUN npm install --only=production --silent && npx prisma generate

# Set ownership
RUN chown -R sahool:sahool /app

# Switch to non-root user
USER sahool

# Environment
ENV NODE_ENV=production
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/healthz || exit 1

EXPOSE 3000

CMD ["npm", "start"]

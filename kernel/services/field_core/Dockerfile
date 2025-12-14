# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Field Core Service - Dockerfile
# Geospatial Field Management with PostGIS Support
# ═══════════════════════════════════════════════════════════════════════════════

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm install

# Copy source and build
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

# Stage 2: Production
FROM node:18-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy built files and production dependencies
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./
RUN npm install --production

# Environment
ENV NODE_ENV=production
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/healthz || exit 1

EXPOSE 3000

CMD ["npm", "start"]

# SAHOOL Chat Service v16.0.0
# خدمة المحادثات للسوق الزراعي

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="chat-service"
LABEL version="16.0.0"

WORKDIR /app

# Install dependencies (with retries for network resilience)
COPY package.json package-lock.json* ./
RUN npm install --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema and generate client
COPY prisma ./prisma/
RUN npx prisma generate

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma compatibility
RUN apk add --no-cache curl openssl

# Copy package files
COPY package.json package-lock.json* ./
# Install with increased retries and timeout for network resilience
RUN npm install --only=production --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema and regenerate client for production environment
COPY --from=builder /app/prisma ./prisma/
RUN npx prisma generate

# Copy built application
COPY --from=builder /app/dist ./dist

# Expose port (default 3015 for chat service)
EXPOSE 3015

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3015/api/v1/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

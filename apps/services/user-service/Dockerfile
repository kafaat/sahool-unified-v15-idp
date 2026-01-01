# SAHOOL User Service v16.0.0
# خدمة إدارة المستخدمين

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="user-service"
LABEL version="16.0.0"

WORKDIR /app

# Install dependencies (with retries for network resilience)
COPY package.json package-lock.json* ./
RUN npm install --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema and generate client
# Add retry logic for network resilience
COPY prisma ./prisma/
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

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
# Add retry logic and checksum ignore for network resilience
COPY --from=builder /app/prisma ./prisma/
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy built application
COPY --from=builder /app/dist ./dist

# Set port environment variable
ENV PORT=3020

# Expose port
EXPOSE 3020

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3020/api/v1/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

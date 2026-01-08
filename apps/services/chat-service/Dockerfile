# SAHOOL Chat Service v16.0.0
# خدمة المحادثات للسوق الزراعي

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="chat-service"
LABEL version="16.0.0"

# Install OpenSSL for Prisma
RUN apk add --no-cache openssl

# Use workspace structure to maintain relative paths for shared imports
WORKDIR /workspace

# Copy shared modules first (required for imports from ../../shared/)
COPY apps/services/shared ./shared/

# Copy service to maintain relative path: ../../shared/ from chat-service/src/
COPY apps/services/chat-service ./chat-service/

WORKDIR /workspace/chat-service

# Install dependencies (with retries for network resilience)
RUN npm install --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema and generate client
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma compatibility
RUN apk add --no-cache curl openssl

# Copy package files
COPY apps/services/chat-service/package.json ./
RUN npm install --omit=dev --legacy-peer-deps --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy prisma schema and regenerate client for production environment
COPY --from=builder /workspace/chat-service/prisma ./prisma/
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
RUN npx prisma generate || \
    (sleep 5 && npx prisma generate) || \
    (sleep 10 && npx prisma generate) || \
    (echo "Prisma generate failed after retries" && exit 1)

# Copy built application
COPY --from=builder /workspace/chat-service/dist ./dist

# Set port environment variable
ENV PORT=8114

# Expose port
EXPOSE 8114

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8114/api/v1/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

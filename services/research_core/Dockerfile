# SAHOOL Research Core Service v15.3
# نواة البحث العلمي الزراعي

# Build stage
FROM node:20-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="research-core"
LABEL version="15.3.0"

WORKDIR /app

# Install OpenSSL for Prisma
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy prisma schema and generate client
COPY prisma ./prisma/
RUN npx prisma generate

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-slim AS production

WORKDIR /app

# Install curl for health checks and OpenSSL for Prisma
RUN apt-get update && apt-get install -y curl openssl && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package.json package-lock.json* ./
RUN npm install --only=production

# Copy prisma
COPY --from=builder /app/prisma ./prisma/
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma

# Copy built application
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3015

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:3015/api/v1/healthz || exit 1

# Run the application
CMD ["node", "dist/main.js"]

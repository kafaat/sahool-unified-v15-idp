# SAHOOL Yield Prediction Service v16.0
# خدمة التنبؤ بالإنتاجية الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="yield-prediction"
LABEL version="16.0.0"

WORKDIR /app

# Install dependencies with retry for network resilience
COPY package.json package-lock.json* ./
RUN npm install --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Copy package files
COPY package.json package-lock.json* ./
RUN npm install --omit=dev --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000

# Copy built application
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3021

# Set ownership and switch to non-root user (use existing node user)
RUN chown -R node:node /app
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3021/api/v1/yield/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

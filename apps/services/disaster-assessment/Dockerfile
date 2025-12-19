# SAHOOL Disaster Assessment Service v16.0
# خدمة تقييم الكوارث الزراعية
# Based on: Agricultural Remote Sensing On-Demand Service Model

# Build stage
FROM node:20-alpine AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="disaster-assessment"
LABEL version="16.0.0"

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

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
RUN npm install --only=production

# Copy built application
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:3020/api/v1/disasters/health || exit 1

# Run the application
CMD ["node", "dist/main.js"]

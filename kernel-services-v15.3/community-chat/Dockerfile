# Sahool Community Chat Service
# خدمة الدردشة الحية لمجتمع سهول

FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 8097

ENV NODE_ENV=production
ENV PORT=8097

CMD ["npm", "start"]

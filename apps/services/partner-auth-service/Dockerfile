# SAHOOL Partner Auth Service v16.0.0
# خادم مصادقة الشركاء — OAuth 2.0 / OIDC

ARG NODE_VERSION=20

# ─────────────────────────────────────────────────────────────────────────────
# Build stage
# ─────────────────────────────────────────────────────────────────────────────
FROM node:${NODE_VERSION}-bookworm-slim AS builder

LABEL maintainer="SAHOOL Team"
LABEL service="partner-auth-service"
LABEL version="16.0.0"

WORKDIR /workspace

# Copy shared packages needed by this service
COPY packages/typescript-config ./packages/typescript-config/
COPY packages/shared-types ./packages/shared-types/

# Build @sahool/shared-types so it can be referenced via file: protocol
WORKDIR /workspace/packages/shared-types
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps --no-audit --no-fund && \
    npm run build || \
    (npm config set registry https://registry.npmjs.org && \
     npm install --legacy-peer-deps --no-audit --no-fund && npm run build)

# Copy service sources
WORKDIR /workspace
COPY apps/services/shared ./shared/
COPY apps/services/partner-auth-service ./partner-auth-service/

WORKDIR /workspace/partner-auth-service

RUN node -e "JSON.parse(require('fs').readFileSync('package.json','utf8'))" || \
    (echo 'ERROR: package.json is invalid JSON. Check for merge conflict markers.' && exit 1)

# Point @sahool/shared-types at the local build instead of the public registry,
# then drop the lock file so npm generates a fresh one (avoids registry hang
# caused by lock file mismatch with the patched package.json).
RUN sed -i 's|"@sahool/shared-types": "\*"|"@sahool/shared-types": "file:../packages/shared-types"|g' package.json && \
    rm -f package-lock.json

# Resilient install (multi-mirror fallback)
RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        echo "Attempt $i: Installing dependencies..."; \
        if npm install --legacy-peer-deps \
            --fetch-retries=5 \
            --fetch-retry-mintimeout=30000 \
            --fetch-retry-maxtimeout=300000 \
            --fetch-timeout=600000 \
            --no-audit --no-fund; then break; fi; \
        if [ "$i" != "3" ]; then sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
     npm install --legacy-peer-deps --fetch-retries=5 --no-audit --no-fund)

# Prisma client + build
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1
ENV PRISMA_CLI_QUERY_ENGINE_TYPE=binary
ENV PRISMA_CLIENT_ENGINE_TYPE=binary
RUN npx prisma@5 generate --schema=./prisma/schema.prisma && \
    test -f prisma/generated/client/index.js || \
    (echo "Retrying prisma generate..." && sleep 5 && \
     npx prisma@5 generate --schema=./prisma/schema.prisma && \
     test -f prisma/generated/client/index.js) || \
    (echo "Prisma generate failed" && exit 1)

RUN npx nest build

# ─────────────────────────────────────────────────────────────────────────────
# Production stage
# ─────────────────────────────────────────────────────────────────────────────
FROM node:${NODE_VERSION}-bookworm-slim AS production

ARG NODE_VERSION=20
WORKDIR /app

# curl for healthcheck, openssl for Prisma native engine
COPY docker/apt-update.sh /usr/local/bin/
RUN apt-update.sh && \
    apt-get install -y --no-install-recommends curl openssl && \
    rm -rf /var/lib/apt/lists/*

# Bring in the pre-built @sahool/shared-types so the file: reference resolves
COPY --from=builder /workspace/packages/shared-types ./packages/shared-types/

COPY --from=builder /workspace/partner-auth-service/package.json ./
COPY --from=builder /workspace/partner-auth-service/package-lock.json ./

# Re-point file: path to match /app layout (builder used ../packages, we have ./packages)
RUN sed -i 's|"@sahool/shared-types": "file:\.\./packages/shared-types"|"@sahool/shared-types": "file:./packages/shared-types"|g' package.json

RUN --mount=type=cache,target=/root/.npm \
    npm config set registry https://registry.npmmirror.com && \
    for i in 1 2 3; do \
        if npm ci --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 --fetch-timeout=600000 \
            --prefer-offline --no-audit --no-fund || \
           npm install --omit=dev --ignore-scripts --legacy-peer-deps \
            --fetch-retries=5 --fetch-timeout=600000 \
            --prefer-offline --no-audit --no-fund; then break; fi; \
        if [ "$i" != "3" ]; then sleep $((i * 10)); else false; fi; \
    done || \
    (npm config set registry https://registry.npmjs.org && \
     npm install --omit=dev --ignore-scripts --legacy-peer-deps --fetch-retries=5)

RUN npm config set registry https://registry.npmjs.org && npm audit fix --omit=dev --legacy-peer-deps --ignore-scripts 2>/dev/null || true

COPY --from=builder /workspace/partner-auth-service/prisma ./prisma/
COPY --from=builder /workspace/partner-auth-service/prisma/generated/client/ ./node_modules/.prisma/client/
COPY --from=builder /workspace/partner-auth-service/node_modules/@prisma/client ./node_modules/@prisma/client/
COPY --from=builder /workspace/partner-auth-service/dist ./dist

ENV PORT=3030
ENV NODE_ENV=production
EXPOSE 3030

RUN chown -R node:node /app
USER node

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3030/healthz || exit 1

COPY --chmod=755 docker/docker-entrypoint-nestjs.sh /usr/local/bin/docker-entrypoint.sh
CMD ["/usr/local/bin/docker-entrypoint.sh"]

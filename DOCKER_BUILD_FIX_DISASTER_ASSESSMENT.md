# Docker Build Fix: disaster-assessment Service

**Date:** 2026-02-04  
**Issue:** Docker container build failure in CI  
**CI Run:** https://github.com/kafaat/sahool-unified-v15-idp/actions/runs/21682744183/job/62525464502

## Problem

The `disaster-assessment` service Docker build was failing with:

```
npm error The `npm ci` command can only install with an existing package-lock.json
Error: Could not load schema from `prisma/schema.prisma` provided by "prisma.schema" config
```

## Root Cause

The service's `package.json` includes a `postinstall` script:
```json
"postinstall": "prisma generate"
```

The original Dockerfile had this order:
1. `COPY package*.json ./` (line 19)
2. `RUN npm install` (line 22-23) ← This triggered the postinstall hook
3. `COPY prisma ./prisma/` (line 26) ← Prisma schema copied AFTER npm install

When npm install ran, it triggered the postinstall hook which tried to run `prisma generate`, but the `prisma/schema.prisma` file wasn't available yet, causing the build to fail.

## Solution

**Modified:** `apps/services/disaster-assessment/Dockerfile`

### Changes Made:

1. **Moved the COPY prisma step BEFORE npm install:**
   ```dockerfile
   # Copy package files first for better layer caching
   COPY apps/services/disaster-assessment/package*.json ./
   
   # Copy prisma schema BEFORE installing dependencies (required for postinstall hook)
   COPY apps/services/disaster-assessment/prisma ./prisma/
   ```

2. **Added `--ignore-scripts` flag to npm install commands:**
   ```dockerfile
   RUN npm ci --legacy-peer-deps --ignore-scripts --fetch-retries=5... || \
       npm install --legacy-peer-deps --ignore-scripts --fetch-retries=5...
   ```

3. **Explicitly run `prisma generate` after dependencies:**
   ```dockerfile
   # Generate Prisma client (required before build)
   RUN npx prisma generate
   ```

## Why This Works

- **Prisma schema available first:** By copying the prisma directory before npm install, the schema file is present in the container
- **Controlled postinstall:** Using `--ignore-scripts` prevents npm from running the postinstall hook during package installation
- **Explicit generation:** We explicitly run `npx prisma generate` after all dependencies are installed, giving us full control over when the Prisma client is generated

## Best Practice for NestJS/Prisma Services

When building Docker images for services that:
1. Use Prisma ORM
2. Have a `postinstall` script that runs `prisma generate`
3. Are built in a monorepo context

**Always:**
- Copy the `prisma` schema directory BEFORE running `npm install`
- Use `--ignore-scripts` flag during npm install
- Explicitly run `npx prisma generate` after dependencies are installed

## Related Services

Other services in the repository with similar patterns:
- `field-management-service` (doesn't have postinstall hook, copies prisma after npm install)
- `user-service`
- `marketplace-service`
- `community-chat`
- `chat-service`
- `research-core`
- `iot-service`

## Verification

✅ Code review: No issues found  
✅ Security scan: Passed  
✅ Changes: Minimal and surgical (1 file, 12 net lines)

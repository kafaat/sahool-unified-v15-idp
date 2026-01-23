# Server-Side Signature Validation - Reference Implementation

## Overview

This document provides reference implementations for validating request signatures on the server side.

⚠️ **CRITICAL**: Client-side signing provides NO security without server-side validation!

## Node.js/Express Implementation

### 1. Install Dependencies

```bash
npm install crypto
npm install redis  # For nonce storage
```

### 2. Signature Validation Middleware

```javascript
const crypto = require("crypto");
const redis = require("redis");

// Configuration
const MAX_TIMESTAMP_DRIFT_MS = 5 * 60 * 1000; // 5 minutes
const NONCE_TTL_SECONDS = 300; // 5 minutes

// Redis client for nonce tracking
const redisClient = redis.createClient({
  host: process.env.REDIS_HOST || "localhost",
  port: process.env.REDIS_PORT || 6379,
});

/**
 * Middleware to validate request signatures
 */
async function validateRequestSignature(req, res, next) {
  // Skip validation for public endpoints
  if (isPublicEndpoint(req.path)) {
    return next();
  }

  try {
    // 1. Extract signature headers
    const signature = req.headers["x-signature"];
    const timestamp = req.headers["x-timestamp"];
    const nonce = req.headers["x-nonce"];
    const version = req.headers["x-signature-version"];

    // 2. Validate headers exist
    if (!signature || !timestamp || !nonce) {
      return res.status(401).json({
        error: "MISSING_SIGNATURE",
        message: "Request signature headers missing",
      });
    }

    // 3. Validate signature version
    if (version !== "1") {
      return res.status(401).json({
        error: "INVALID_SIGNATURE_VERSION",
        message: "Unsupported signature version",
      });
    }

    // 4. Validate timestamp (replay attack protection)
    const requestTime = parseInt(timestamp);
    const now = Date.now();
    const timeDrift = Math.abs(now - requestTime);

    if (timeDrift > MAX_TIMESTAMP_DRIFT_MS) {
      return res.status(401).json({
        error: "TIMESTAMP_EXPIRED",
        message: "Request timestamp has expired",
        drift: timeDrift,
        maxDrift: MAX_TIMESTAMP_DRIFT_MS,
      });
    }

    // 5. Check nonce (prevent duplicate requests)
    const isDuplicate = await checkNonce(nonce);
    if (isDuplicate) {
      return res.status(401).json({
        error: "DUPLICATE_REQUEST",
        message: "Request has already been processed",
      });
    }

    // 6. Get user's signing key
    const signingKey = await getUserSigningKey(req.user?.id);
    if (!signingKey) {
      return res.status(401).json({
        error: "NO_SIGNING_KEY",
        message: "User signing key not found",
      });
    }

    // 7. Rebuild canonical request
    const canonicalRequest = buildCanonicalRequest(req, timestamp, nonce);

    // 8. Calculate expected signature
    const expectedSignature = calculateSignature(canonicalRequest, signingKey);

    // 9. Verify signature (constant-time comparison)
    const isValid = verifySignature(signature, expectedSignature);

    if (!isValid) {
      return res.status(401).json({
        error: "INVALID_SIGNATURE",
        message: "Request signature is invalid",
      });
    }

    // 10. Store nonce to prevent reuse
    await storeNonce(nonce);

    // Signature is valid - proceed
    next();
  } catch (error) {
    console.error("Signature validation error:", error);
    return res.status(500).json({
      error: "VALIDATION_ERROR",
      message: "Failed to validate request signature",
    });
  }
}

/**
 * Build canonical request string (must match client logic)
 */
function buildCanonicalRequest(req, timestamp, nonce) {
  const method = req.method.toUpperCase();
  const path = req.path;
  const queryParams = normalizeQueryParams(req.query);
  const bodyHash = calculateBodyHash(req.body);

  // Must match client format exactly!
  return [method, path, queryParams, timestamp, nonce, bodyHash].join("\n");
}

/**
 * Normalize query parameters (sorted alphabetically)
 */
function normalizeQueryParams(query) {
  if (!query || Object.keys(query).length === 0) {
    return "";
  }

  const sortedKeys = Object.keys(query).sort();
  const params = sortedKeys.map((key) => {
    const value = query[key];
    return `${key}=${encodeURIComponent(value)}`;
  });

  return params.join("&");
}

/**
 * Calculate SHA256 hash of request body
 */
function calculateBodyHash(body) {
  if (!body || Object.keys(body).length === 0) {
    return crypto.createHash("sha256").update("").digest("base64url");
  }

  const bodyString = JSON.stringify(body);
  return crypto.createHash("sha256").update(bodyString).digest("base64url");
}

/**
 * Calculate HMAC-SHA256 signature
 */
function calculateSignature(canonicalRequest, signingKey) {
  return crypto
    .createHmac("sha256", signingKey)
    .update(canonicalRequest)
    .digest("base64url");
}

/**
 * Verify signature using constant-time comparison
 */
function verifySignature(providedSignature, expectedSignature) {
  try {
    const providedBuffer = Buffer.from(providedSignature);
    const expectedBuffer = Buffer.from(expectedSignature);

    // Ensure same length (prevent timing attacks)
    if (providedBuffer.length !== expectedBuffer.length) {
      return false;
    }

    // Constant-time comparison
    return crypto.timingSafeEqual(providedBuffer, expectedBuffer);
  } catch (error) {
    console.error("Signature comparison error:", error);
    return false;
  }
}

/**
 * Check if nonce has been used before
 */
async function checkNonce(nonce) {
  const key = `nonce:${nonce}`;
  const exists = await redisClient.exists(key);
  return exists === 1;
}

/**
 * Store nonce to prevent reuse
 */
async function storeNonce(nonce) {
  const key = `nonce:${nonce}`;
  await redisClient.setEx(key, NONCE_TTL_SECONDS, "1");
}

/**
 * Get user's signing key from database
 * NOTE: You must implement this based on your database
 */
async function getUserSigningKey(userId) {
  if (!userId) {
    return null;
  }

  // Example: Fetch from database
  // const user = await User.findById(userId);
  // return user.signingKey;

  // For now, return a placeholder
  // TODO: Implement actual database lookup
  throw new Error("getUserSigningKey not implemented");
}

/**
 * Check if endpoint is public (doesn't require signature)
 */
function isPublicEndpoint(path) {
  const publicPaths = [
    "/auth/login",
    "/auth/register",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/auth/verify-email",
    "/auth/resend-verification",
    "/health",
    "/version",
    "/api-docs",
  ];

  return publicPaths.some((publicPath) => path.includes(publicPath));
}

// Export middleware
module.exports = {
  validateRequestSignature,
  calculateSignature, // For testing
  buildCanonicalRequest, // For testing
};
```

### 3. Apply Middleware

```javascript
const express = require("express");
const {
  validateRequestSignature,
} = require("./middleware/signature-validation");

const app = express();

// Body parser (must come before signature validation)
app.use(express.json());

// Apply signature validation to all routes
app.use(validateRequestSignature);

// Your routes here
app.post("/api/tasks", (req, res) => {
  // Request signature has been validated!
  res.json({ message: "Task created" });
});

app.listen(3000);
```

## NestJS Implementation

### Signature Validation Guard

```typescript
import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from "@nestjs/common";
import { Request } from "express";
import * as crypto from "crypto";
import { RedisService } from "./redis.service";
import { UsersService } from "../users/users.service";

@Injectable()
export class SignatureValidationGuard implements CanActivate {
  private readonly MAX_TIMESTAMP_DRIFT_MS = 5 * 60 * 1000; // 5 minutes
  private readonly NONCE_TTL_SECONDS = 300; // 5 minutes

  constructor(
    private readonly redisService: RedisService,
    private readonly usersService: UsersService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();

    // Skip public endpoints
    if (this.isPublicEndpoint(request.path)) {
      return true;
    }

    try {
      await this.validateSignature(request);
      return true;
    } catch (error) {
      throw new UnauthorizedException(error.message);
    }
  }

  private async validateSignature(req: Request): Promise<void> {
    // Extract headers
    const signature = req.headers["x-signature"] as string;
    const timestamp = req.headers["x-timestamp"] as string;
    const nonce = req.headers["x-nonce"] as string;
    const version = req.headers["x-signature-version"] as string;

    // Validate headers
    if (!signature || !timestamp || !nonce) {
      throw new Error("Missing signature headers");
    }

    if (version !== "1") {
      throw new Error("Unsupported signature version");
    }

    // Validate timestamp
    const requestTime = parseInt(timestamp);
    const now = Date.now();
    const timeDrift = Math.abs(now - requestTime);

    if (timeDrift > this.MAX_TIMESTAMP_DRIFT_MS) {
      throw new Error("Request timestamp expired");
    }

    // Check nonce
    const isDuplicate = await this.checkNonce(nonce);
    if (isDuplicate) {
      throw new Error("Duplicate request detected");
    }

    // Get signing key
    const userId = (req as any).user?.id;
    const signingKey = await this.usersService.getSigningKey(userId);

    if (!signingKey) {
      throw new Error("Signing key not found");
    }

    // Build canonical request
    const canonicalRequest = this.buildCanonicalRequest(req, timestamp, nonce);

    // Calculate expected signature
    const expectedSignature = this.calculateSignature(
      canonicalRequest,
      signingKey,
    );

    // Verify signature
    if (!this.verifySignature(signature, expectedSignature)) {
      throw new Error("Invalid signature");
    }

    // Store nonce
    await this.storeNonce(nonce);
  }

  private buildCanonicalRequest(
    req: Request,
    timestamp: string,
    nonce: string,
  ): string {
    const method = req.method.toUpperCase();
    const path = req.path;
    const queryParams = this.normalizeQueryParams(req.query);
    const bodyHash = this.calculateBodyHash(req.body);

    return [method, path, queryParams, timestamp, nonce, bodyHash].join("\n");
  }

  private normalizeQueryParams(query: any): string {
    if (!query || Object.keys(query).length === 0) {
      return "";
    }

    const sortedKeys = Object.keys(query).sort();
    const params = sortedKeys.map(
      (key) => `${key}=${encodeURIComponent(query[key])}`,
    );

    return params.join("&");
  }

  private calculateBodyHash(body: any): string {
    if (!body || Object.keys(body).length === 0) {
      return crypto.createHash("sha256").update("").digest("base64url");
    }

    const bodyString = JSON.stringify(body);
    return crypto.createHash("sha256").update(bodyString).digest("base64url");
  }

  private calculateSignature(
    canonicalRequest: string,
    signingKey: string,
  ): string {
    return crypto
      .createHmac("sha256", signingKey)
      .update(canonicalRequest)
      .digest("base64url");
  }

  private verifySignature(
    providedSignature: string,
    expectedSignature: string,
  ): boolean {
    try {
      const providedBuffer = Buffer.from(providedSignature);
      const expectedBuffer = Buffer.from(expectedSignature);

      if (providedBuffer.length !== expectedBuffer.length) {
        return false;
      }

      return crypto.timingSafeEqual(providedBuffer, expectedBuffer);
    } catch {
      return false;
    }
  }

  private async checkNonce(nonce: string): Promise<boolean> {
    const key = `nonce:${nonce}`;
    return await this.redisService.exists(key);
  }

  private async storeNonce(nonce: string): Promise<void> {
    const key = `nonce:${nonce}`;
    await this.redisService.setex(key, this.NONCE_TTL_SECONDS, "1");
  }

  private isPublicEndpoint(path: string): boolean {
    const publicPaths = [
      "/auth/login",
      "/auth/register",
      "/auth/forgot-password",
      "/health",
      "/version",
    ];

    return publicPaths.some((publicPath) => path.includes(publicPath));
  }
}
```

### Apply Guard Globally

```typescript
// app.module.ts
import { APP_GUARD } from "@nestjs/core";
import { SignatureValidationGuard } from "./guards/signature-validation.guard";

@Module({
  providers: [
    {
      provide: APP_GUARD,
      useClass: SignatureValidationGuard,
    },
  ],
})
export class AppModule {}
```

## Python/FastAPI Implementation

```python
import time
import hmac
import hashlib
import base64
import json
from typing import Optional
from fastapi import Request, HTTPException, Depends
from redis import Redis

# Configuration
MAX_TIMESTAMP_DRIFT_MS = 5 * 60 * 1000  # 5 minutes
NONCE_TTL_SECONDS = 300  # 5 minutes

# Redis client
redis_client = Redis(host='localhost', port=6379, decode_responses=True)

async def validate_request_signature(request: Request):
    """Validate request signature"""

    # Skip public endpoints
    if is_public_endpoint(request.url.path):
        return

    # Extract headers
    signature = request.headers.get('x-signature')
    timestamp = request.headers.get('x-timestamp')
    nonce = request.headers.get('x-nonce')
    version = request.headers.get('x-signature-version')

    # Validate headers exist
    if not all([signature, timestamp, nonce]):
        raise HTTPException(
            status_code=401,
            detail='Missing signature headers'
        )

    # Validate version
    if version != '1':
        raise HTTPException(
            status_code=401,
            detail='Unsupported signature version'
        )

    # Validate timestamp
    request_time = int(timestamp)
    now = int(time.time() * 1000)
    time_drift = abs(now - request_time)

    if time_drift > MAX_TIMESTAMP_DRIFT_MS:
        raise HTTPException(
            status_code=401,
            detail='Request timestamp expired'
        )

    # Check nonce
    if await check_nonce(nonce):
        raise HTTPException(
            status_code=401,
            detail='Duplicate request detected'
        )

    # Get signing key
    signing_key = await get_user_signing_key(request.state.user.id)
    if not signing_key:
        raise HTTPException(
            status_code=401,
            detail='Signing key not found'
        )

    # Build canonical request
    body = await request.body()
    canonical_request = build_canonical_request(
        request.method,
        request.url.path,
        request.query_params,
        timestamp,
        nonce,
        body
    )

    # Calculate expected signature
    expected_signature = calculate_signature(canonical_request, signing_key)

    # Verify signature
    if not verify_signature(signature, expected_signature):
        raise HTTPException(
            status_code=401,
            detail='Invalid signature'
        )

    # Store nonce
    await store_nonce(nonce)


def build_canonical_request(
    method: str,
    path: str,
    query_params: dict,
    timestamp: str,
    nonce: str,
    body: bytes
) -> str:
    """Build canonical request string"""
    query_string = normalize_query_params(query_params)
    body_hash = calculate_body_hash(body)

    return '\n'.join([
        method.upper(),
        path,
        query_string,
        timestamp,
        nonce,
        body_hash
    ])


def normalize_query_params(query_params: dict) -> str:
    """Normalize query parameters"""
    if not query_params:
        return ''

    sorted_keys = sorted(query_params.keys())
    params = [f"{key}={query_params[key]}" for key in sorted_keys]
    return '&'.join(params)


def calculate_body_hash(body: bytes) -> str:
    """Calculate SHA256 hash of body"""
    if not body:
        body = b''

    digest = hashlib.sha256(body).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


def calculate_signature(canonical_request: str, signing_key: str) -> str:
    """Calculate HMAC-SHA256 signature"""
    key_bytes = signing_key.encode('utf-8')
    message_bytes = canonical_request.encode('utf-8')

    signature = hmac.new(key_bytes, message_bytes, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')


def verify_signature(provided: str, expected: str) -> bool:
    """Verify signature using constant-time comparison"""
    try:
        return hmac.compare_digest(provided, expected)
    except:
        return False


async def check_nonce(nonce: str) -> bool:
    """Check if nonce exists"""
    key = f"nonce:{nonce}"
    return redis_client.exists(key) == 1


async def store_nonce(nonce: str):
    """Store nonce"""
    key = f"nonce:{nonce}"
    redis_client.setex(key, NONCE_TTL_SECONDS, '1')


async def get_user_signing_key(user_id: str) -> Optional[str]:
    """Get user's signing key from database"""
    # TODO: Implement database lookup
    raise NotImplementedError("get_user_signing_key not implemented")


def is_public_endpoint(path: str) -> bool:
    """Check if endpoint is public"""
    public_paths = [
        '/auth/login',
        '/auth/register',
        '/auth/forgot-password',
        '/health',
        '/version',
    ]
    return any(public_path in path for public_path in public_paths)
```

## Testing

### Test Signature Validation

```javascript
const {
  calculateSignature,
  buildCanonicalRequest,
} = require("./signature-validation");

describe("Signature Validation", () => {
  it("should calculate correct signature", () => {
    const signingKey = "test-signing-key-12345";
    const canonicalRequest =
      "POST\n/api/tasks\n\n1704290000000\ntest-nonce\nbody-hash";

    const signature = calculateSignature(canonicalRequest, signingKey);

    expect(signature).toBeDefined();
    expect(signature.length).toBeGreaterThan(0);
  });

  it("should build canonical request correctly", () => {
    const req = {
      method: "POST",
      path: "/api/tasks",
      query: { page: "1", limit: "10" },
      body: { name: "Task 1" },
    };

    const canonical = buildCanonicalRequest(req, "1704290000000", "test-nonce");

    expect(canonical).toContain("POST");
    expect(canonical).toContain("/api/tasks");
    expect(canonical).toContain("limit=10&page=1"); // Sorted
  });
});
```

## Monitoring & Logging

### Track Failed Signatures

```javascript
// Add logging to signature validation
async function validateRequestSignature(req, res, next) {
  try {
    // ... validation logic ...
  } catch (error) {
    // Log failed signature attempts
    await logSecurityEvent({
      type: "SIGNATURE_VALIDATION_FAILED",
      userId: req.user?.id,
      ip: req.ip,
      path: req.path,
      error: error.message,
      timestamp: new Date(),
    });

    // Alert on multiple failures
    await checkForSecurityThreats(req.user?.id, req.ip);

    return res.status(401).json({
      error: "INVALID_SIGNATURE",
      message: "Request signature is invalid",
    });
  }
}
```

## Database Schema

### Store User Signing Keys

```sql
-- PostgreSQL
CREATE TABLE user_signing_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  signing_key TEXT NOT NULL,
  version INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP,
  is_active BOOLEAN NOT NULL DEFAULT true,

  UNIQUE(user_id, is_active)
);

-- Index for fast lookups
CREATE INDEX idx_user_signing_keys_user_id ON user_signing_keys(user_id) WHERE is_active = true;
```

## Deployment Checklist

- [ ] Install Redis for nonce storage
- [ ] Implement `getUserSigningKey()` function
- [ ] Apply middleware to API routes
- [ ] Configure public endpoints list
- [ ] Set up monitoring/alerting
- [ ] Test with mobile app
- [ ] Deploy to staging
- [ ] Verify signatures in production
- [ ] Monitor error rates
- [ ] Document for team

---

**Note**: Adapt these examples to your specific framework and requirements.

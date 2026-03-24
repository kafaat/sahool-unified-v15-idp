/**
 * SAHOOL Admin - Rate Limiting middleware
 * وسيط تحديد معدل الطلبات
 *
 * In-memory sliding-window rate limiter for Next.js API routes.
 * Protects admin API routes from abuse.
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

interface RateLimitEntry {
  timestamps: number[];
}

// In-memory store (per-process; resets on restart)
const store = new Map<string, RateLimitEntry>();

// Cleanup stale entries every 5 minutes
let lastCleanup = Date.now();
const CLEANUP_INTERVAL = 300000;

function cleanup(windowMs: number): void {
  const now = Date.now();
  if (now - lastCleanup < CLEANUP_INTERVAL) return;
  lastCleanup = now;

  const cutoff = now - windowMs;
  for (const [key, entry] of store.entries()) {
    entry.timestamps = entry.timestamps.filter((t) => t > cutoff);
    if (entry.timestamps.length === 0) {
      store.delete(key);
    }
  }
}

export interface RateLimitConfig {
  /** Max requests per window (default: 60) */
  limit?: number;
  /** Window duration in ms (default: 60000 = 1 minute) */
  windowMs?: number;
}

/**
 * Check rate limit for a request. Returns a 429 response if limit exceeded,
 * or null if the request is allowed.
 *
 * @example
 * ```ts
 * // In an API route handler:
 * export async function POST(request: NextRequest) {
 *   const limited = checkRateLimit(request, { limit: 10 });
 *   if (limited) return limited;
 *   // ... handle request
 * }
 * ```
 */
export function checkRateLimit(
  request: NextRequest,
  config: RateLimitConfig = {}
): NextResponse | null {
  const { limit = 60, windowMs = 60000 } = config;

  // Extract client identifier
  const forwarded = request.headers.get('x-forwarded-for');
  const ip = forwarded?.split(',')[0]?.trim() || 'anonymous';
  const key = `${ip}:${request.nextUrl.pathname}`;

  const now = Date.now();
  const cutoff = now - windowMs;

  // Get or create entry
  let entry = store.get(key);
  if (!entry) {
    entry = { timestamps: [] };
    store.set(key, entry);
  }

  // Remove expired timestamps
  entry.timestamps = entry.timestamps.filter((t) => t > cutoff);

  // Check limit
  if (entry.timestamps.length >= limit) {
    const retryAfter = Math.ceil((entry.timestamps[0]! + windowMs - now) / 1000);

    return NextResponse.json(
      {
        error: 'Too many requests',
        errorAr: 'عدد الطلبات كثير جداً',
        retryAfter,
      },
      {
        status: 429,
        headers: {
          'Retry-After': String(retryAfter),
          'X-RateLimit-Limit': String(limit),
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': String(Math.ceil((entry.timestamps[0]! + windowMs) / 1000)),
        },
      }
    );
  }

  // Record this request
  entry.timestamps.push(now);

  // Periodic cleanup
  cleanup(windowMs);

  return null;
}

/**
 * Create rate limit headers for a successful response
 */
export function rateLimitHeaders(
  request: NextRequest,
  config: RateLimitConfig = {}
): Record<string, string> {
  const { limit = 60, windowMs = 60000 } = config;

  const forwarded = request.headers.get('x-forwarded-for');
  const ip = forwarded?.split(',')[0]?.trim() || 'anonymous';
  const key = `${ip}:${request.nextUrl.pathname}`;

  const entry = store.get(key);
  const remaining = entry ? Math.max(0, limit - entry.timestamps.length) : limit;

  return {
    'X-RateLimit-Limit': String(limit),
    'X-RateLimit-Remaining': String(remaining),
    'X-RateLimit-Reset': String(Math.ceil((Date.now() + windowMs) / 1000)),
  };
}

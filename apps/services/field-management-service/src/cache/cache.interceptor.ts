/**
 * Cache Interceptor - Automatic Response Caching
 *
 * Features:
 * - Automatic caching of GET requests
 * - Cache key generation from request
 * - Tenant-aware cache keys
 * - ETag support
 */

import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
  Logger,
} from "@nestjs/common";
import { Observable, of } from "rxjs";
import { tap } from "rxjs/operators";
import { Reflector } from "@nestjs/core";
import { CacheService, CACHE_TTL } from "./cache.service";

// Decorator key for cache options
export const CACHE_KEY = "cache_key";
export const CACHE_TTL_KEY = "cache_ttl";
export const NO_CACHE_KEY = "no_cache";

@Injectable()
export class CacheInterceptor implements NestInterceptor {
  private readonly logger = new Logger(CacheInterceptor.name);

  constructor(
    private cacheService: CacheService,
    private reflector: Reflector,
  ) {}

  async intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Promise<Observable<any>> {
    const request = context.switchToHttp().getRequest();

    // Only cache GET requests
    if (request.method !== "GET") {
      return next.handle();
    }

    // Check for no-cache decorator
    const noCache = this.reflector.get<boolean>(
      NO_CACHE_KEY,
      context.getHandler(),
    );
    if (noCache) {
      return next.handle();
    }

    // Check for Cache-Control: no-cache header
    const cacheControl = request.headers["cache-control"];
    if (cacheControl?.includes("no-cache")) {
      return next.handle();
    }

    // Generate cache key
    const cacheKey = this.generateCacheKey(context, request);
    if (!cacheKey) {
      return next.handle();
    }

    // Get TTL from decorator or use default
    const ttl =
      this.reflector.get<number>(CACHE_TTL_KEY, context.getHandler()) ||
      CACHE_TTL.MEDIUM;

    // Try to get from cache
    const cached = await this.cacheService.get<any>(cacheKey);
    if (cached) {
      // Add cache header (check if headers not already sent)
      const response = context.switchToHttp().getResponse();
      if (!response.headersSent) {
        response.setHeader("X-Cache", "HIT");
        response.setHeader("X-Cache-Key", cacheKey);
      }
      return of(cached);
    }

    // Execute handler and cache response
    return next.handle().pipe(
      tap(async (data: unknown) => {
        if (data) {
          await this.cacheService.set(cacheKey, data, ttl);
          const response = context.switchToHttp().getResponse();
          // Check if headers not already sent before setting
          if (!response.headersSent) {
            response.setHeader("X-Cache", "MISS");
            response.setHeader("X-Cache-Key", cacheKey);
          }
        }
      }),
    );
  }

  /**
   * Generate cache key from request
   */
  private generateCacheKey(
    context: ExecutionContext,
    request: any,
  ): string | null {
    // Check for custom cache key decorator
    const customKey = this.reflector.get<string>(
      CACHE_KEY,
      context.getHandler(),
    );
    if (customKey) {
      return this.interpolateKey(customKey, request);
    }

    // Generate default key from URL and query params. Use the tenantId
    // resolved by TenantGuard (JWT-bound, attached to request) rather than
    // the raw `x-tenant-id` header — a spoofed header would otherwise let a
    // caller poison/read another tenant's cache entries. Falls back to
    // "default" only when the guard has not attached a tenant (e.g. public
    // routes).
    const tenantId = request.tenantId || "default";
    const path = request.path;
    const query = JSON.stringify(request.query || {});

    return `${tenantId}:${path}:${this.hashString(query)}`;
  }

  /**
   * Interpolate custom key with request params
   */
  private interpolateKey(template: string, request: any): string {
    let key = template;

    // Replace :param placeholders
    if (request.params) {
      Object.entries(request.params).forEach(([name, value]) => {
        key = key.replace(`:${name}`, String(value));
      });
    }

    // Replace {query.param} placeholders
    if (request.query) {
      Object.entries(request.query).forEach(([name, value]) => {
        key = key.replace(`{query.${name}}`, String(value));
      });
    }

    // Replace {header.param} placeholders
    if (request.headers) {
      Object.entries(request.headers).forEach(([name, value]) => {
        key = key.replace(`{header.${name}}`, String(value));
      });
    }

    return key;
  }

  /**
   * Simple hash function for query strings
   */
  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }
}

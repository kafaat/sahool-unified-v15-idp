/**
 * Deprecation Interceptor
 * Adds deprecation headers to v1 API responses
 */

import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { Observable } from "rxjs";
import { tap } from "rxjs/operators";

/**
 * Deprecation configuration
 */
export interface DeprecationConfig {
  deprecationDate: string;
  sunsetDate: string;
  successorVersion: string;
  infoUrl: string;
}

/**
 * Default deprecation configuration for v1
 */
const DEFAULT_V1_DEPRECATION: DeprecationConfig = {
  deprecationDate: "2025-06-30",
  sunsetDate: "2026-06-30",
  successorVersion: "v2",
  infoUrl: "https://docs.sahool.app/api/deprecation/v1",
};

/**
 * Interceptor to add deprecation headers to API responses
 */
@Injectable()
export class DeprecationInterceptor implements NestInterceptor {
  constructor(
    private reflector: Reflector,
    private config: DeprecationConfig = DEFAULT_V1_DEPRECATION,
  ) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const response = context.switchToHttp().getResponse();

    // Check if the endpoint is marked as deprecated
    const isDeprecated = this.reflector.get<boolean>(
      "api-v1-deprecated",
      context.getHandler(),
    );

    // Check if the route is a v1 route
    const isV1Route = request.url.includes("/api/v1/");

    return next.handle().pipe(
      tap(() => {
        if (isDeprecated || isV1Route) {
          // Add deprecation headers
          response.setHeader("X-API-Deprecated", "true");
          response.setHeader(
            "X-API-Deprecation-Date",
            this.config.deprecationDate,
          );
          response.setHeader("X-API-Sunset-Date", this.config.sunsetDate);
          response.setHeader("X-API-Deprecation-Info", this.config.infoUrl);

          // Add Link header for successor version
          const successorPath = request.url.replace(
            "/v1/",
            `/${this.config.successorVersion}/`,
          );
          response.setHeader(
            "Link",
            `<${successorPath}>; rel="successor-version"`,
          );

          // Add warning header (RFC 7234)
          const warningMessage = `299 - "API version 1 is deprecated and will be removed on ${this.config.sunsetDate}"`;
          response.setHeader("Warning", warningMessage);

          // Log deprecation access
          console.warn(
            `[DEPRECATION] Deprecated endpoint accessed: ${request.method} ${request.url} ` +
              `by ${request.ip || "unknown"} - User-Agent: ${request.headers["user-agent"] || "unknown"}`,
          );
        }
      }),
    );
  }
}

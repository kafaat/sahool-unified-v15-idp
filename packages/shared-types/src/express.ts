/**
 * Express.js Type Extensions
 * Augments Express Request type with custom properties
 */

import type { Request } from "express";
import type { JWTPayload } from "./auth";

/**
 * Extended Express Request with authentication and logging context
 */
export interface AuthenticatedRequest extends Request {
  user?: JWTPayload;
  correlationId?: string;
  tenantId?: string;
  userId?: string;
  requestId?: string;
  logger?: any; // Logger instance type depends on logging library
}

/**
 * Type guard to check if request has authentication
 */
export function isAuthenticatedRequest(
  request: Request,
): request is AuthenticatedRequest {
  return "user" in request && request.user !== undefined;
}

/**
 * Type guard to check if request has correlation ID
 */
export function hasCorrelationId(
  request: Request,
): request is AuthenticatedRequest & { correlationId: string } {
  return (
    "correlationId" in request && typeof request.correlationId === "string"
  );
}

/**
 * Type guard to check if request has tenant ID
 */
export function hasTenantId(
  request: Request,
): request is AuthenticatedRequest & { tenantId: string } {
  return "tenantId" in request && typeof request.tenantId === "string";
}

/**
 * Safely get user from request
 */
export function getUserFromRequest(request: Request): JWTPayload | undefined {
  return isAuthenticatedRequest(request) ? request.user : undefined;
}

/**
 * Safely get correlation ID from request
 */
export function getCorrelationIdFromRequest(
  request: Request,
): string | undefined {
  return hasCorrelationId(request) ? request.correlationId : undefined;
}

/**
 * Safely get tenant ID from request
 */
export function getTenantIdFromRequest(request: Request): string | undefined {
  return hasTenantId(request) ? request.tenantId : undefined;
}

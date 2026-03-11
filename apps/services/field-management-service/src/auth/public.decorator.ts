/**
 * Public Route Decorator
 *
 * Marks a route as publicly accessible, bypassing JWT and tenant guards.
 * Used for health checks, liveness/readiness probes, and metrics endpoints.
 */

import { SetMetadata } from "@nestjs/common";

export const IS_PUBLIC_KEY = "isPublic";
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);

import { UnauthorizedException } from "@nestjs/common";

/**
 * Extract and validate tenantId from the authenticated JWT.
 *
 * IMPORTANT: tenantId MUST come from the JWT `tid` claim (exposed on
 * `req.user.tid` / `req.user.tenantId` by the JwtAuthGuard). It must NEVER
 * be taken from an arbitrary header such as `x-tenant-id`, as that would
 * allow cross-tenant data access.
 *
 * استخراج والتحقق من معرف المستأجر من الـ JWT فقط
 */
export function extractTenantId(req: any): string {
  // Primary: raw JWT `tid` claim as exposed on req.user.tid
  // Fallback: `req.user.tenantId` (populated by JwtAuthGuard from the same claim)
  const tenantId: string | undefined =
    req?.user?.tid || req?.user?.tenantId;

  if (!tenantId) {
    throw new UnauthorizedException(
      "Missing tenantId in JWT (tid claim required)",
    );
  }
  return tenantId;
}

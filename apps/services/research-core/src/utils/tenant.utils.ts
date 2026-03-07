import { BadRequestException } from "@nestjs/common";

/**
 * Extract and validate tenantId from request.
 * Throws BadRequestException if tenantId is missing.
 *
 * استخراج والتحقق من معرف المستأجر من الطلب
 */
export function extractTenantId(req: any): string {
  const tenantId =
    req.tenantId || req.user?.tenantId || req.headers?.["x-tenant-id"];
  if (!tenantId) {
    throw new BadRequestException("Missing tenantId");
  }
  return tenantId;
}

/**
 * Tenant Enforcement Utilities
 * أدوات فرض عزل المستأجرين
 *
 * Ensures all operations are scoped to the authenticated user's tenant.
 * The TenantGuard sets request.tenantId from JWT; these helpers enforce it.
 */

import { ForbiddenException, BadRequestException } from "@nestjs/common";

/**
 * Extract the enforced tenant ID from a request that has passed TenantGuard.
 * Throws if tenantId is missing (should never happen after TenantGuard).
 *
 * @param req - Express request object (after TenantGuard)
 * @returns The validated tenant ID string
 */
export function getRequestTenantId(req: any): string {
  const tenantId = req.tenantId;
  if (!tenantId) {
    throw new BadRequestException(
      "Tenant context is required - سياق المستأجر مطلوب",
    );
  }
  return tenantId;
}

/**
 * Verify that a resource belongs to the requesting tenant.
 * Throws ForbiddenException on mismatch.
 *
 * @param resourceTenantId - The tenant ID of the resource being accessed
 * @param requestTenantId - The tenant ID from the authenticated request
 * @param resourceType - Human-readable resource name for error messages
 */
export function assertTenantOwnership(
  resourceTenantId: string,
  requestTenantId: string,
  resourceType: string = "resource",
): void {
  if (resourceTenantId !== requestTenantId) {
    throw new ForbiddenException({
      message: `Access denied: ${resourceType} belongs to another tenant`,
      messageAr: `رفض الوصول: ${resourceType} ينتمي لمستأجر آخر`,
      error: "tenant_mismatch",
    });
  }
}

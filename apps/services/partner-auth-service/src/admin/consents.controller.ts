/**
 * Admin: inspect and revoke user ConsentGrants.
 *
 * Use cases:
 *   • Security review: "show me all consents user X granted"
 *   • Breach response: "revoke all consents for partner Y"
 *   • User support: "forget me" / GDPR Art. 17
 */

import {
  Controller,
  Delete,
  Get,
  HttpCode,
  Param,
  Query,
  UseGuards,
} from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import type { ConsentGrantAdminResponse } from "@sahool/shared-types/contracts";
import { PrismaService } from "../prisma/prisma.service";
import { AdminGuard } from "./admin.guard";

@ApiTags("Admin — Consent Grants")
@ApiBearerAuth()
@UseGuards(AdminGuard)
@Controller("api/v1/admin/partner-auth/consents")
export class ConsentsController {
  constructor(private readonly prisma: PrismaService) {}

  @Get()
  @ApiOperation({
    summary: "List consents (filter by ?clientId= or ?userId=)",
  })
  async list(
    @Query("clientId") clientId?: string,
    @Query("userId") userId?: string,
    @Query("limit") limit = "100",
    @Query("offset") offset = "0",
  ): Promise<{ results: ConsentGrantAdminResponse[]; total: number }> {
    const where: Record<string, unknown> = {};
    if (clientId) where.client = { clientId };
    if (userId) where.userId = userId;

    const [rows, total] = await this.prisma.$transaction([
      this.prisma.consentGrant.findMany({
        where,
        include: { client: { select: { name: true } } },
        orderBy: { acceptedAt: "desc" },
        take: Math.min(500, parseInt(limit, 10) || 100),
        skip: Math.max(0, parseInt(offset, 10) || 0),
      }),
      this.prisma.consentGrant.count({ where }),
    ]);

    return {
      results: rows.map((r) => ({
        id: r.id,
        clientId: r.clientId,
        clientName: r.client.name,
        userId: r.userId,
        tenantId: r.tenantId,
        scopes: r.scopes,
        acceptedAt: r.acceptedAt.toISOString(),
        revokedAt: r.revokedAt ? r.revokedAt.toISOString() : null,
        consentIp: r.consentIp,
      })),
      total,
    };
  }

  @Delete(":grantId")
  @HttpCode(200)
  @ApiOperation({
    summary: "Revoke a consent grant (user's 'forget me' per partner)",
  })
  async revoke(@Param("grantId") grantId: string) {
    await this.prisma.consentGrant.update({
      where: { id: grantId },
      data: { revokedAt: new Date() },
    });
    return { status: "revoked", grantId };
  }
}

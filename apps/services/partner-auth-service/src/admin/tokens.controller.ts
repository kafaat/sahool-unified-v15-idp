/**
 * Admin: inspect and emergency-revoke access + refresh tokens.
 * Intended for incident response (lost laptop, leaked secret, security audit).
 */

import {
  Controller,
  Get,
  HttpCode,
  Param,
  Post,
  Query,
  UseGuards,
  Logger,
} from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import type {
  AccessTokenAdminResponse,
  RefreshTokenAdminResponse,
} from "@sahool/shared-types/contracts";
import { PrismaService } from "../prisma/prisma.service";
import { AdminGuard } from "./admin.guard";

@ApiTags("Admin — Tokens")
@ApiBearerAuth()
@UseGuards(AdminGuard)
@Controller("api/v1/admin/partner-auth/tokens")
export class TokensController {
  private readonly logger = new Logger(TokensController.name);

  constructor(private readonly prisma: PrismaService) {}

  @Get("access")
  @ApiOperation({ summary: "List access tokens (filter by ?clientId= or ?userId=)" })
  async listAccess(
    @Query("clientId") clientId?: string,
    @Query("userId") userId?: string,
    @Query("includeRevoked") includeRevoked?: string,
    @Query("limit") limit = "100",
    @Query("offset") offset = "0",
  ): Promise<{ results: AccessTokenAdminResponse[]; total: number }> {
    const where: Record<string, unknown> = {};
    if (clientId) where.client = { clientId };
    if (userId) where.userId = userId;
    if (includeRevoked !== "true") where.revokedAt = null;

    const [rows, total] = await this.prisma.$transaction([
      this.prisma.accessToken.findMany({
        where,
        include: { client: { select: { name: true } } },
        orderBy: { createdAt: "desc" },
        take: Math.min(500, parseInt(limit, 10) || 100),
        skip: Math.max(0, parseInt(offset, 10) || 0),
      }),
      this.prisma.accessToken.count({ where }),
    ]);

    return {
      results: rows.map((r) => ({
        jti: r.jti,
        clientId: r.clientId,
        clientName: r.client.name,
        userId: r.userId,
        tenantId: r.tenantId,
        scopes: r.scopes,
        expiresAt: r.expiresAt.toISOString(),
        revokedAt: r.revokedAt ? r.revokedAt.toISOString() : null,
        revokedReason: r.revokedReason,
        createdAt: r.createdAt.toISOString(),
      })),
      total,
    };
  }

  @Get("refresh")
  @ApiOperation({ summary: "List refresh tokens + rotation chain" })
  async listRefresh(
    @Query("clientId") clientId?: string,
    @Query("userId") userId?: string,
    @Query("familyId") familyId?: string,
    @Query("includeRevoked") includeRevoked?: string,
    @Query("limit") limit = "100",
    @Query("offset") offset = "0",
  ): Promise<{ results: RefreshTokenAdminResponse[]; total: number }> {
    const where: Record<string, unknown> = {};
    if (clientId) where.client = { clientId };
    if (userId) where.userId = userId;
    if (familyId) where.familyId = familyId;
    if (includeRevoked !== "true") where.revokedAt = null;

    const [rows, total] = await this.prisma.$transaction([
      this.prisma.refreshToken.findMany({
        where,
        include: { client: { select: { name: true } } },
        orderBy: { createdAt: "desc" },
        take: Math.min(500, parseInt(limit, 10) || 100),
        skip: Math.max(0, parseInt(offset, 10) || 0),
      }),
      this.prisma.refreshToken.count({ where }),
    ]);

    return {
      results: rows.map((r) => ({
        id: r.id,
        clientId: r.clientId,
        clientName: r.client.name,
        userId: r.userId,
        tenantId: r.tenantId,
        scopes: r.scopes,
        familyId: r.familyId,
        rotatedToId: r.rotatedToId,
        expiresAt: r.expiresAt.toISOString(),
        revokedAt: r.revokedAt ? r.revokedAt.toISOString() : null,
        revokedReason: r.revokedReason,
        createdAt: r.createdAt.toISOString(),
      })),
      total,
    };
  }

  @Post("revoke-all/client/:clientIdOrCid")
  @HttpCode(200)
  @ApiOperation({
    summary: "Emergency revoke ALL tokens for a client (breach response)",
  })
  async revokeAllForClient(@Param("clientIdOrCid") param: string) {
    // Accept either the row UUID or the public client_id string
    const client = await this.prisma.oAuthClient.findFirst({
      where: { OR: [{ id: param }, { clientId: param }] },
    });
    if (!client) {
      return { status: "not_found" };
    }
    const when = new Date();
    const reason = "admin_bulk_revoke";
    const [accessResult, refreshResult] = await this.prisma.$transaction([
      this.prisma.accessToken.updateMany({
        where: { clientId: client.id, revokedAt: null },
        data: { revokedAt: when, revokedReason: reason },
      }),
      this.prisma.refreshToken.updateMany({
        where: { clientId: client.id, revokedAt: null },
        data: { revokedAt: when, revokedReason: reason },
      }),
    ]);
    this.logger.warn(
      JSON.stringify({
        event: "admin_bulk_revoke_client",
        clientId: client.clientId,
        accessRevoked: accessResult.count,
        refreshRevoked: refreshResult.count,
      }),
    );
    return {
      status: "revoked",
      clientId: client.clientId,
      accessTokensRevoked: accessResult.count,
      refreshTokensRevoked: refreshResult.count,
    };
  }

  @Post("revoke-all/user/:userId")
  @HttpCode(200)
  @ApiOperation({
    summary: "Revoke all tokens for a user across every partner (forget-me)",
  })
  async revokeAllForUser(@Param("userId") userId: string) {
    const when = new Date();
    const reason = "admin_user_revoke";
    const [accessResult, refreshResult, consents] = await this.prisma.$transaction([
      this.prisma.accessToken.updateMany({
        where: { userId, revokedAt: null },
        data: { revokedAt: when, revokedReason: reason },
      }),
      this.prisma.refreshToken.updateMany({
        where: { userId, revokedAt: null },
        data: { revokedAt: when, revokedReason: reason },
      }),
      this.prisma.consentGrant.updateMany({
        where: { userId, revokedAt: null },
        data: { revokedAt: when },
      }),
    ]);
    this.logger.warn(
      JSON.stringify({
        event: "admin_user_revoke",
        userId,
        access: accessResult.count,
        refresh: refreshResult.count,
        consents: consents.count,
      }),
    );
    return {
      status: "revoked",
      userId,
      accessTokensRevoked: accessResult.count,
      refreshTokensRevoked: refreshResult.count,
      consentsRevoked: consents.count,
    };
  }
}

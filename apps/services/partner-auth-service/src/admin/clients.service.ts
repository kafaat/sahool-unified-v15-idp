/**
 * Clients service — administrative operations on oauth_clients.
 *
 * Secrets / API keys: plaintext is generated here and returned to the
 * caller EXACTLY ONCE (on create or rotate). Only the bcrypt/SHA-256
 * hash persists. Callers must store the plaintext securely (ideally
 * in a secrets manager); there is no way to retrieve it later.
 *
 * All mutations that affect trust (rotate-secret, suspend, revoke) log
 * a structured audit line at info level with the admin principal id.
 */

import {
  BadRequestException,
  ConflictException,
  Injectable,
  Logger,
  NotFoundException,
} from "@nestjs/common";
import * as bcrypt from "bcryptjs";
import { createHash } from "crypto";
import { nanoid } from "nanoid";
import { PARTNER_OAUTH_SCOPES } from "@sahool/shared-types/contracts";
import type {
  PartnerClientResponse,
  PartnerClientStatus,
  PartnerRateTier,
  PartnerClientListResponse,
} from "@sahool/shared-types/contracts";
import type { OAuthClient } from "../../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";
import {
  CreateClientDto,
  UpdateClientDto,
  ListClientsQueryDto,
} from "./dto/create-client.dto";

const BCRYPT_COST = 12;
const ALLOWED_SCOPES: ReadonlySet<string> = new Set(PARTNER_OAUTH_SCOPES);

@Injectable()
export class ClientsService {
  private readonly logger = new Logger(ClientsService.name);

  constructor(private readonly prisma: PrismaService) {}

  // ── CREATE ─────────────────────────────────────────────────────────────

  async create(
    dto: CreateClientDto,
    adminId: string,
  ): Promise<PartnerClientResponse> {
    this.validateScopes(dto.allowedScopes);
    this.validateRedirectUris(dto.redirectUris);

    const clientIdBase = slugify(dto.name);
    const suffix = nanoid(8).toLowerCase();
    const clientId = `${clientIdBase}-${suffix}`;

    // Client_secret: 40 bytes base64url ≈ 54 chars — 240 bits of entropy
    const clientSecret = `sah_cs_${nanoid(40)}`;
    const clientSecretHash = await bcrypt.hash(clientSecret, BCRYPT_COST);

    // Partner API key (X-Sahool-Partner-Key) — SHA-256 hashed (not bcrypt
    // because it's looked up on every API call — must be fast).
    const apiKeyPlain = `sahk_${nanoid(32)}`;
    const apiKeyHash = sha256(apiKeyPlain);

    const row = await this.prisma.oAuthClient.create({
      data: {
        clientId,
        clientSecretHash,
        name: dto.name,
        nameAr: dto.nameAr ?? null,
        description: dto.description ?? null,
        homepageUrl: dto.homepageUrl ?? null,
        logoUrl: dto.logoUrl ?? null,
        redirectUris: dto.redirectUris,
        allowedScopes: dto.allowedScopes,
        apiKeyHash,
        rateTier: dto.rateTier ?? "starter",
        status: "active",
        contactEmail: dto.contactEmail ?? null,
      },
    });

    this.logger.log(
      JSON.stringify({
        event: "partner_client_created",
        clientId,
        adminId,
        rateTier: row.rateTier,
        scopes: dto.allowedScopes.length,
      }),
    );

    return {
      ...this.toPublic(row),
      clientSecret,
      partnerApiKey: apiKeyPlain,
    };
  }

  // ── LIST ───────────────────────────────────────────────────────────────

  async list(q: ListClientsQueryDto): Promise<PartnerClientListResponse> {
    const limit = clamp(parseInt(q.limit ?? "50", 10), 1, 200);
    const offset = Math.max(0, parseInt(q.offset ?? "0", 10) || 0);

    const where: Record<string, unknown> = {};
    if (q.status) where.status = q.status;
    if (q.name) where.name = { contains: q.name, mode: "insensitive" };

    const [rows, total] = await this.prisma.$transaction([
      this.prisma.oAuthClient.findMany({
        where,
        orderBy: { createdAt: "desc" },
        skip: offset,
        take: limit,
      }),
      this.prisma.oAuthClient.count({ where }),
    ]);

    return {
      results: rows.map((r) => this.toPublic(r)),
      total,
      limit,
      offset,
    };
  }

  // ── GET ────────────────────────────────────────────────────────────────

  async get(clientId: string): Promise<PartnerClientResponse> {
    const row = await this.findOrThrow(clientId);
    return this.toPublic(row);
  }

  // ── UPDATE ─────────────────────────────────────────────────────────────

  async update(
    clientId: string,
    dto: UpdateClientDto,
    adminId: string,
  ): Promise<PartnerClientResponse> {
    await this.findOrThrow(clientId);
    if (dto.allowedScopes) this.validateScopes(dto.allowedScopes);
    if (dto.redirectUris) this.validateRedirectUris(dto.redirectUris);

    const row = await this.prisma.oAuthClient.update({
      where: { clientId },
      data: {
        ...(dto.name !== undefined && { name: dto.name }),
        ...(dto.nameAr !== undefined && { nameAr: dto.nameAr }),
        ...(dto.description !== undefined && { description: dto.description }),
        ...(dto.homepageUrl !== undefined && { homepageUrl: dto.homepageUrl }),
        ...(dto.logoUrl !== undefined && { logoUrl: dto.logoUrl }),
        ...(dto.redirectUris !== undefined && { redirectUris: dto.redirectUris }),
        ...(dto.allowedScopes !== undefined && { allowedScopes: dto.allowedScopes }),
        ...(dto.rateTier !== undefined && { rateTier: dto.rateTier }),
        ...(dto.contactEmail !== undefined && { contactEmail: dto.contactEmail }),
      },
    });

    this.logger.log(
      JSON.stringify({
        event: "partner_client_updated",
        clientId,
        adminId,
        fields: Object.keys(dto),
      }),
    );
    return this.toPublic(row);
  }

  // ── ROTATE SECRET ──────────────────────────────────────────────────────

  async rotateSecret(
    clientId: string,
    adminId: string,
  ): Promise<PartnerClientResponse> {
    await this.findOrThrow(clientId);
    const newSecret = `sah_cs_${nanoid(40)}`;
    const hash = await bcrypt.hash(newSecret, BCRYPT_COST);
    const row = await this.prisma.oAuthClient.update({
      where: { clientId },
      data: { clientSecretHash: hash },
    });
    this.logger.warn(
      JSON.stringify({ event: "partner_client_secret_rotated", clientId, adminId }),
    );
    return { ...this.toPublic(row), clientSecret: newSecret };
  }

  // ── ROTATE API KEY ─────────────────────────────────────────────────────

  async rotateApiKey(
    clientId: string,
    adminId: string,
  ): Promise<PartnerClientResponse> {
    await this.findOrThrow(clientId);
    const plain = `sahk_${nanoid(32)}`;
    const hash = sha256(plain);
    const row = await this.prisma.oAuthClient.update({
      where: { clientId },
      data: { apiKeyHash: hash },
    });
    this.logger.warn(
      JSON.stringify({ event: "partner_api_key_rotated", clientId, adminId }),
    );
    return { ...this.toPublic(row), partnerApiKey: plain };
  }

  // ── SUSPEND / UNSUSPEND / REVOKE ───────────────────────────────────────

  async setStatus(
    clientId: string,
    status: PartnerClientStatus,
    adminId: string,
  ): Promise<PartnerClientResponse> {
    const row = await this.findOrThrow(clientId);
    if (row.status === "revoked" && status !== "revoked") {
      throw new ConflictException({
        error: "client_revoked",
        error_description: "Revoked clients cannot be reactivated",
      });
    }
    const updated = await this.prisma.oAuthClient.update({
      where: { clientId },
      data: {
        status,
        revokedAt: status === "revoked" ? new Date() : null,
      },
    });

    // Revoke: cascade-kill all outstanding tokens + grants
    if (status === "revoked") {
      const when = new Date();
      await this.prisma.$transaction([
        this.prisma.accessToken.updateMany({
          where: { clientId: updated.id, revokedAt: null },
          data: { revokedAt: when, revokedReason: "client_revoked" },
        }),
        this.prisma.refreshToken.updateMany({
          where: { clientId: updated.id, revokedAt: null },
          data: { revokedAt: when, revokedReason: "client_revoked" },
        }),
        this.prisma.consentGrant.updateMany({
          where: { clientId: updated.id, revokedAt: null },
          data: { revokedAt: when },
        }),
      ]);
    }

    this.logger.warn(
      JSON.stringify({
        event: "partner_client_status_changed",
        clientId,
        adminId,
        status,
      }),
    );
    return this.toPublic(updated);
  }

  // ── helpers ────────────────────────────────────────────────────────────

  private async findOrThrow(clientId: string): Promise<OAuthClient> {
    const row = await this.prisma.oAuthClient.findUnique({ where: { clientId } });
    if (!row) {
      throw new NotFoundException({
        error: "client_not_found",
        error_description: `No client with client_id=${clientId}`,
      });
    }
    return row;
  }

  private validateScopes(scopes: string[]) {
    const unknown = scopes.filter((s) => !ALLOWED_SCOPES.has(s));
    if (unknown.length) {
      throw new BadRequestException({
        error: "invalid_scope",
        error_description: `Unknown scope(s): ${unknown.join(", ")}. Valid values: see PARTNER_OAUTH_SCOPES.`,
      });
    }
  }

  private validateRedirectUris(uris: string[]) {
    for (const u of uris) {
      if (u.includes("#")) {
        throw new BadRequestException({
          error: "invalid_request",
          error_description:
            "redirect_uri must not contain a fragment (RFC 6749 § 3.1.2)",
        });
      }
    }
  }

  private toPublic(row: OAuthClient): PartnerClientResponse {
    return {
      id: row.id,
      clientId: row.clientId,
      name: row.name,
      nameAr: row.nameAr,
      description: row.description,
      homepageUrl: row.homepageUrl,
      logoUrl: row.logoUrl,
      redirectUris: row.redirectUris,
      allowedScopes: row.allowedScopes,
      rateTier: row.rateTier as PartnerRateTier,
      status: row.status as PartnerClientStatus,
      contactEmail: row.contactEmail,
      createdAt: row.createdAt.toISOString(),
      updatedAt: row.updatedAt.toISOString(),
      revokedAt: row.revokedAt ? row.revokedAt.toISOString() : null,
    };
  }
}

function slugify(name: string): string {
  return name
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 32) || "partner";
}

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, Number.isFinite(n) ? n : lo));
}

function sha256(s: string): string {
  return createHash("sha256").update(s).digest("hex");
}

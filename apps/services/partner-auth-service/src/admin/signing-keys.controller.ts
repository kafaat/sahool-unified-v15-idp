/**
 * Admin: RSA signing-key rotation for id_token JWS.
 * Safe rotation flow:
 *   1. POST /rotate → new kid is activated, old kid moved to retiredAt=now.
 *   2. JWKS continues to publish BOTH until the old key's TTL window lapses
 *      (current access-token TTL = 4h), so in-flight tokens still verify.
 *   3. DELETE /signing-keys/{kid} removes a fully-expired retired key.
 */

import {
  BadRequestException,
  Controller,
  Delete,
  Get,
  HttpCode,
  Logger,
  Param,
  Post,
  UseGuards,
} from "@nestjs/common";
import { ApiBearerAuth, ApiOperation, ApiTags } from "@nestjs/swagger";
import { generateKeyPairSync } from "crypto";
import { nanoid } from "nanoid";
import type { SigningKeyAdminResponse } from "@sahool/shared-types/contracts";
import { PrismaService } from "../prisma/prisma.service";
import { JwkService } from "../oidc/jwk.service";
import { AdminGuard } from "./admin.guard";

const ROTATION_WINDOW_HOURS = 4;

@ApiTags("Admin — Signing Keys")
@ApiBearerAuth()
@UseGuards(AdminGuard)
@Controller("api/v1/admin/partner-auth/signing-keys")
export class SigningKeysController {
  private readonly logger = new Logger(SigningKeysController.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly jwks: JwkService,
  ) {}

  @Get()
  @ApiOperation({ summary: "List signing keys (active + retired-but-verifying)" })
  async list(): Promise<{ results: SigningKeyAdminResponse[] }> {
    const rows = await this.prisma.signingKey.findMany({
      orderBy: { activatedAt: "desc" },
    });
    return {
      results: rows.map((r) => ({
        kid: r.kid,
        alg: r.alg,
        activatedAt: r.activatedAt.toISOString(),
        retiredAt: r.retiredAt ? r.retiredAt.toISOString() : null,
        publicPem: r.publicPem,
      })),
    };
  }

  @Post("rotate")
  @HttpCode(201)
  @ApiOperation({
    summary: "Generate a new RSA keypair, activate it, retire the old key",
  })
  async rotate(): Promise<SigningKeyAdminResponse> {
    // Generate new 2048-bit RSA keypair
    const { publicKey, privateKey } = generateKeyPairSync("rsa", {
      modulusLength: 2048,
      publicKeyEncoding: { type: "spki", format: "pem" },
      privateKeyEncoding: { type: "pkcs8", format: "pem" },
    });
    const kid = nanoid(16);

    // Retire all currently-active keys (there should be at most one)
    const now = new Date();
    await this.prisma.$transaction([
      this.prisma.signingKey.updateMany({
        where: { retiredAt: null },
        data: { retiredAt: now },
      }),
      this.prisma.signingKey.create({
        data: {
          kid,
          alg: "RS256",
          publicPem: publicKey as string,
          // TODO(next branch): encrypt with KMS/Vault KEK before persisting
          privatePemEncrypted: privateKey as string,
          activatedAt: now,
        },
      }),
    ]);

    // Hot-reload the in-memory cache so new tokens sign with the new key
    await this.jwks.reload();

    this.logger.warn(
      JSON.stringify({
        event: "signing_key_rotated",
        newKid: kid,
        retentionHours: ROTATION_WINDOW_HOURS,
      }),
    );

    return {
      kid,
      alg: "RS256",
      activatedAt: now.toISOString(),
      retiredAt: null,
      publicPem: publicKey as string,
    };
  }

  @Delete(":kid")
  @HttpCode(200)
  @ApiOperation({ summary: "Permanently delete a fully-expired retired key" })
  async deleteKey(@Param("kid") kid: string) {
    const row = await this.prisma.signingKey.findUnique({ where: { kid } });
    if (!row) return { status: "not_found", kid };
    if (row.retiredAt === null) {
      throw new BadRequestException({
        error: "key_still_active",
        error_description: "Active keys cannot be deleted — rotate first",
      });
    }
    const ageMs = Date.now() - row.retiredAt.getTime();
    if (ageMs < ROTATION_WINDOW_HOURS * 3600 * 1000) {
      throw new BadRequestException({
        error: "retention_window_active",
        error_description: `Key must remain in JWKS for ${ROTATION_WINDOW_HOURS}h after retirement (for in-flight tokens)`,
      });
    }
    await this.prisma.signingKey.delete({ where: { kid } });
    await this.jwks.reload();
    return { status: "deleted", kid };
  }
}

/**
 * JWK Service — manages RSA signing keys for id_token JWS.
 *
 * Rotation model:
 *   • The key with retiredAt = NULL is the "active" signer.
 *   • Rotating creates a new active key; the previous one stays in JWKS
 *     until its retiredAt + access-token-TTL window has passed, so any
 *     id_tokens signed by the retired key still verify until they expire.
 *
 * This scaffold generates a dev key on first boot if none exists. In
 * production, keys should be pre-seeded via migration and the private
 * PEM should be encrypted at rest with a KMS/Vault-backed KEK.
 */

import { Injectable, Logger, OnModuleInit } from "@nestjs/common";
import { createPublicKey, createPrivateKey, generateKeyPairSync, KeyObject } from "crypto";
import { nanoid } from "nanoid";
import { PrismaService } from "../prisma/prisma.service";

export interface LoadedSigningKey {
  kid: string;
  alg: string;
  publicKey: KeyObject;
  privateKey: KeyObject;
  activatedAt: Date;
  retiredAt: Date | null;
}

@Injectable()
export class JwkService implements OnModuleInit {
  private readonly logger = new Logger(JwkService.name);
  private cache: LoadedSigningKey[] = [];

  constructor(private readonly prisma: PrismaService) {}

  async onModuleInit() {
    await this.loadOrBootstrap();
  }

  /** Returns all keys that should appear in JWKS (active + not-yet-expired retirees). */
  getPublicKeys(): LoadedSigningKey[] {
    return this.cache;
  }

  /** Returns the single active key used to sign new tokens. */
  getActiveKey(): LoadedSigningKey {
    const active = this.cache.find((k) => k.retiredAt === null);
    if (!active) {
      throw new Error(
        "No active signing key available. Run migrations or seed a key.",
      );
    }
    return active;
  }

  /** Forces a reload from DB — called after rotation. */
  async reload() {
    await this.loadOrBootstrap();
  }

  private async loadOrBootstrap() {
    let rows: Array<{
      kid: string;
      alg: string;
      publicPem: string;
      privatePemEncrypted: string;
      activatedAt: Date;
      retiredAt: Date | null;
    }> = [];

    try {
      rows = await this.prisma.signingKey.findMany({
        where: { OR: [{ retiredAt: null }, { retiredAt: { gt: new Date(Date.now() - 4 * 60 * 60 * 1000) } }] },
        orderBy: { activatedAt: "desc" },
      });
    } catch (err) {
      // DB not reachable at boot (common in dev before migrate) — bootstrap
      // a transient in-memory key so /well-known endpoints still respond.
      this.logger.warn(
        `signing_keys table unavailable, using ephemeral dev key: ${
          err instanceof Error ? err.message : err
        }`,
      );
    }

    if (rows.length === 0) {
      this.logger.warn(
        "No signing keys in DB — generating ephemeral RSA key for dev. DO NOT use in production.",
      );
      const dev = this.generateRsaKey();
      this.cache = [
        {
          kid: dev.kid,
          alg: "RS256",
          publicKey: dev.publicKey,
          privateKey: dev.privateKey,
          activatedAt: new Date(),
          retiredAt: null,
        },
      ];
      return;
    }

    this.cache = rows.map((r) => ({
      kid: r.kid,
      alg: r.alg,
      publicKey: createPublicKey(r.publicPem),
      privateKey: createPrivateKey(r.privatePemEncrypted),
      activatedAt: r.activatedAt,
      retiredAt: r.retiredAt,
    }));
  }

  private generateRsaKey() {
    const { publicKey, privateKey } = generateKeyPairSync("rsa", {
      modulusLength: 2048,
      publicKeyEncoding: { type: "spki", format: "pem" },
      privateKeyEncoding: { type: "pkcs8", format: "pem" },
    });
    return {
      kid: nanoid(16),
      publicKey: createPublicKey(publicKey),
      privateKey: createPrivateKey(privateKey),
    };
  }
}

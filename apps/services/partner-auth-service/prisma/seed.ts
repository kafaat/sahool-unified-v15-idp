/**
 * Seed script for local development.
 *
 * Creates:
 *   • 1 RSA signing key (so JWKS + id_token issuance works)
 *   • 2 dev partner apps — "sahool-sandbox-cli" (full scopes) and
 *     "sahool-dev-portal" (read-only)
 *
 * Prints the plaintext client_secret + partnerApiKey to STDOUT — this is
 * the ONLY time you'll see them. Capture into your local .env / 1Password
 * before the window disappears.
 *
 * Usage:
 *   DATABASE_URL=postgresql://… npx tsx prisma/seed.ts
 *
 * SAFETY:
 *   • Idempotent-ish: if client_id already exists, skips re-creation but
 *     also skips printing a secret (so running twice doesn't leak).
 *   • NEVER run this against production.
 */

import { PrismaClient } from "./generated/client";
import { generateKeyPairSync, createHash } from "crypto";
import { nanoid } from "nanoid";
import * as bcrypt from "bcryptjs";

async function main() {
  const prisma = new PrismaClient();

  if (process.env.NODE_ENV === "production") {
    throw new Error("Seed script refuses to run with NODE_ENV=production");
  }

  console.log("🌱 partner-auth-service seed starting…\n");

  // ── Signing key ────────────────────────────────────────────────────────
  const activeKeys = await prisma.signingKey.count({ where: { retiredAt: null } });
  if (activeKeys === 0) {
    const { publicKey, privateKey } = generateKeyPairSync("rsa", {
      modulusLength: 2048,
      publicKeyEncoding: { type: "spki", format: "pem" },
      privateKeyEncoding: { type: "pkcs8", format: "pem" },
    });
    const kid = nanoid(16);
    await prisma.signingKey.create({
      data: {
        kid,
        alg: "RS256",
        publicPem: publicKey as string,
        privatePemEncrypted: privateKey as string,
      },
    });
    console.log(`  ✅ Signing key created: kid=${kid}`);
  } else {
    console.log(`  ✓ Signing key already present — skipped`);
  }

  // ── Dev client #1: full-scope sandbox CLI ──────────────────────────────
  const sandbox = await upsertClient(prisma, {
    clientId: "sahool-sandbox-cli",
    name: "SAHOOL Sandbox CLI",
    nameAr: "أداة سهول للاختبار",
    description: "Local + sandbox integration testing. All scopes enabled.",
    homepageUrl: "http://localhost:3030",
    redirectUris: [
      "http://localhost:8080/oauth/callback",
      "http://localhost:3000/oauth/callback",
      "https://sandbox.sahool.app/oauth/callback",
    ],
    allowedScopes: [
      "openid",
      "profile",
      "email",
      "offline_access",
      "fields:read",
      "fields:write",
      "boundaries:read",
      "boundaries:write",
      "operations:planting:read",
      "operations:harvest:read",
      "operations:application:read",
      "imagery:ndvi:read",
      "soil:read",
      "weather:read",
      "advisory:read",
      "carbon:read",
      "partnerapis",
      "platform",
    ],
    rateTier: "enterprise",
  });

  // ── Dev client #2: read-only dev portal demo ───────────────────────────
  const devPortal = await upsertClient(prisma, {
    clientId: "sahool-dev-portal",
    name: "SAHOOL Developer Portal Demo",
    nameAr: "عرض توضيحي لبوابة المطوّرين",
    description: "Used by dev.sahool.app to demonstrate the OAuth flow.",
    homepageUrl: "https://dev.sahool.app",
    redirectUris: ["https://dev.sahool.app/oauth/callback"],
    allowedScopes: ["openid", "profile", "fields:read", "partnerapis", "platform"],
    rateTier: "starter",
  });

  console.log("\n📋 Seed summary:");
  printClient(sandbox);
  printClient(devPortal);
  console.log("\n⚠️  Secrets are plaintext and shown ONCE only.");
  console.log("    Copy them now — they cannot be retrieved later.\n");

  await prisma.$disconnect();
}

interface UpsertSpec {
  clientId: string;
  name: string;
  nameAr?: string;
  description?: string;
  homepageUrl?: string;
  redirectUris: string[];
  allowedScopes: string[];
  rateTier: "starter" | "pro" | "enterprise";
}

async function upsertClient(
  prisma: PrismaClient,
  spec: UpsertSpec,
): Promise<{ clientId: string; clientSecret: string | null; partnerApiKey: string | null }> {
  const existing = await prisma.oAuthClient.findUnique({
    where: { clientId: spec.clientId },
  });
  if (existing) {
    console.log(`  ✓ Client already exists: ${spec.clientId} — skipped`);
    return { clientId: spec.clientId, clientSecret: null, partnerApiKey: null };
  }

  const clientSecret = `sah_cs_${nanoid(40)}`;
  const clientSecretHash = await bcrypt.hash(clientSecret, 12);
  // API key is a HIGH-ENTROPY opaque token (not a user password) — hashed
  // with SHA-256 for fast per-request lookup. See clients.service.ts for
  // the full rationale (GitHub/Stripe/AWS all use SHA-256/HMAC for API
  // keys to avoid bcrypt-per-request DoS; ~190 bits of entropy makes
  // brute-force infeasible regardless). CodeQL js/insufficient-password-
  // hash false positive — this is an API token, not a password.
  const apiKeyPlain = `sahk_${nanoid(32)}`;
  const apiKeyHash = createHash("sha256").update(apiKeyPlain).digest("hex");

  await prisma.oAuthClient.create({
    data: {
      clientId: spec.clientId,
      clientSecretHash,
      name: spec.name,
      nameAr: spec.nameAr,
      description: spec.description,
      homepageUrl: spec.homepageUrl,
      redirectUris: spec.redirectUris,
      allowedScopes: spec.allowedScopes,
      apiKeyHash,
      rateTier: spec.rateTier,
      status: "active",
    },
  });

  console.log(`  ✅ Client created: ${spec.clientId}`);
  return { clientId: spec.clientId, clientSecret, partnerApiKey: apiKeyPlain };
}

function printClient(c: { clientId: string; clientSecret: string | null; partnerApiKey: string | null }) {
  console.log(`\n  • ${c.clientId}`);
  if (c.clientSecret) {
    console.log(`      client_secret:       ${c.clientSecret}`);
    console.log(`      X-Sahool-Partner-Key: ${c.partnerApiKey}`);
  } else {
    console.log(`      (secrets already issued — not re-shown)`);
  }
}

main().catch((err) => {
  console.error("Seed failed:", err);
  process.exit(1);
});

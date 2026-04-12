/**
 * Unit test for id_token issuance: verify signature + required claims.
 * Uses an ephemeral RSA keypair (no DB needed).
 */

import { generateKeyPairSync, createPublicKey, createPrivateKey, KeyObject } from "crypto";
import { jwtVerify, importSPKI } from "jose";
import { IdTokenService } from "../oidc/id-token.service";
import type { LoadedSigningKey } from "../oidc/jwk.service";
import { JwkService } from "../oidc/jwk.service";

function makeKey(): LoadedSigningKey {
  const { publicKey, privateKey } = generateKeyPairSync("rsa", {
    modulusLength: 2048,
    publicKeyEncoding: { type: "spki", format: "pem" },
    privateKeyEncoding: { type: "pkcs8", format: "pem" },
  });
  return {
    kid: "test-kid",
    alg: "RS256",
    publicKey: createPublicKey(publicKey) as KeyObject,
    privateKey: createPrivateKey(privateKey) as KeyObject,
    activatedAt: new Date(),
    retiredAt: null,
  };
}

describe("IdTokenService", () => {
  it("issues a verifiable RS256 id_token with required OIDC claims", async () => {
    const key = makeKey();
    const stubJwks = { getActiveKey: () => key } as unknown as JwkService;
    const svc = new IdTokenService(stubJwks);

    const jwt = await svc.issue(
      {
        sub: "user-uuid-123",
        aud: "partner-leaf",
        nonce: "n-abc",
        tenant_id: "tenant-ksa-001",
        email: "grower@example.com",
        locale: "ar",
      },
      { issuer: "https://api.sahool.com", ttlSeconds: 14_400 },
    );

    expect(typeof jwt).toBe("string");
    expect(jwt.split(".").length).toBe(3);

    // Verify signature using the exported public SPKI
    const spkiPem = key.publicKey.export({ format: "pem", type: "spki" }) as string;
    const pub = await importSPKI(spkiPem, "RS256");
    const { payload, protectedHeader } = await jwtVerify(jwt, pub, {
      issuer: "https://api.sahool.com",
      audience: "partner-leaf",
    });

    expect(protectedHeader.alg).toBe("RS256");
    expect(protectedHeader.kid).toBe("test-kid");
    expect(payload.sub).toBe("user-uuid-123");
    expect(payload.nonce).toBe("n-abc");
    expect(payload.tenant_id).toBe("tenant-ksa-001");
    expect(payload.email).toBe("grower@example.com");
    expect(payload.locale).toBe("ar");
    expect(typeof payload.auth_time).toBe("number");
    expect(typeof payload.exp).toBe("number");
    expect((payload.exp as number) - (payload.iat as number)).toBe(14_400);
  });
});

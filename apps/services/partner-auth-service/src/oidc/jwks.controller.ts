/**
 * GET /.well-known/jwks.json
 * Public JWKS (RFC 7517). Partners use this to verify id_token signatures.
 */

import { Controller, Get, Header } from "@nestjs/common";
import { exportJWK } from "jose";
import type { KeyLike } from "jose";
import { JwkService } from "./jwk.service";

interface JWKS {
  keys: Array<Record<string, unknown>>;
}

@Controller(".well-known/jwks.json")
export class JwksController {
  constructor(private readonly jwkService: JwkService) {}

  @Get()
  @Header("Cache-Control", "public, max-age=3600")
  @Header("Content-Type", "application/json")
  async jwks(): Promise<JWKS> {
    const keys = this.jwkService.getPublicKeys();
    const out: Array<Record<string, unknown>> = [];
    for (const k of keys) {
      const jwk = await exportJWK(k.publicKey as unknown as KeyLike);
      out.push({
        ...jwk,
        kid: k.kid,
        alg: k.alg,
        use: "sig",
      });
    }
    return { keys: out };
  }
}

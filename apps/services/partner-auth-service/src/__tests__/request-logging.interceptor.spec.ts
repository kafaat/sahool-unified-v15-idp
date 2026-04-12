/**
 * Unit tests for sensitive-field redaction in the request-logging interceptor.
 * We want absolute confidence that tokens and secrets never escape into logs.
 */

import { RequestLoggingInterceptor } from "../utils/request-logging.interceptor";

describe("RequestLoggingInterceptor.redact", () => {
  it("redacts all sensitive OAuth fields", () => {
    const input = {
      grant_type: "refresh_token",
      refresh_token: "sah_rt_abc123",
      client_id: "partner-leaf",
      client_secret: "supersecret",
      scope: "fields:read",
      code: "auth_code_xyz",
    };
    const out = RequestLoggingInterceptor.redact(input);
    expect(out.client_secret).toBe("[REDACTED]");
    expect(out.refresh_token).toBe("[REDACTED]");
    expect(out.code).toBe("[REDACTED]");
    // Non-sensitive fields preserved
    expect(out.grant_type).toBe("refresh_token");
    expect(out.client_id).toBe("partner-leaf");
    expect(out.scope).toBe("fields:read");
  });

  it("redacts access_token and id_token when present", () => {
    const out = RequestLoggingInterceptor.redact({
      access_token: "eyJ...",
      id_token: "eyJ...",
      token_type: "bearer",
    });
    expect(out.access_token).toBe("[REDACTED]");
    expect(out.id_token).toBe("[REDACTED]");
    expect(out.token_type).toBe("bearer");
  });

  it("is case-insensitive on sensitive keys", () => {
    const out = RequestLoggingInterceptor.redact({
      Authorization: "Bearer eyJ...",
      PASSWORD: "hunter2",
    });
    expect(out.Authorization).toBe("[REDACTED]");
    expect(out.PASSWORD).toBe("[REDACTED]");
  });
});

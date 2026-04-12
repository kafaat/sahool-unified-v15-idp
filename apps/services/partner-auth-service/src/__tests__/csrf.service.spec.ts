/**
 * CSRF token issue + verify round-trip, including:
 *   • Rejection of tokens bound to a different user
 *   • Rejection of expired tokens
 *   • Rejection of tampered signatures
 */

import { CsrfService } from "../utils/csrf.service";

describe("CsrfService", () => {
  // Force a stable dev secret for the test
  beforeAll(() => {
    process.env.CSRF_SECRET = "unit-test-secret-" + "x".repeat(32);
  });

  const svc = new CsrfService();

  it("verifies a freshly issued token for the same user", () => {
    const t = svc.issue("user-123");
    expect(svc.verify(t, "user-123")).toBe(true);
  });

  it("rejects a token bound to a different user", () => {
    const t = svc.issue("user-123");
    expect(svc.verify(t, "user-456")).toBe(false);
  });

  it("rejects a tampered signature", () => {
    const t = svc.issue("user-123");
    const parts = t.split(".");
    parts[2] = parts[2].slice(0, -4) + "AAAA";
    const tampered = parts.join(".");
    expect(svc.verify(tampered, "user-123")).toBe(false);
  });

  it("rejects malformed tokens", () => {
    expect(svc.verify("not-a-token", "user-123")).toBe(false);
    expect(svc.verify("a.b", "user-123")).toBe(false);
    expect(svc.verify(undefined, "user-123")).toBe(false);
  });

  it("rejects tokens beyond their TTL", () => {
    // Issue a token then monkey-patch Date.now to the far future
    const t = svc.issue("user-123");
    const realNow = Date.now;
    try {
      Date.now = () => realNow() + 30 * 60 * 1000; // +30 min > 15 min TTL
      expect(svc.verify(t, "user-123")).toBe(false);
    } finally {
      Date.now = realNow;
    }
  });
});

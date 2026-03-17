/**
 * Auth Store Security Tests
 * اختبارات أمان مخزن المصادقة
 *
 * Tests for security fixes:
 * - sanitizeUser UUID validation for tenant_id
 * - BroadcastChannel logout notification
 * - AbortController timeout on session DELETE calls
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ═══════════════════════════════════════════════════════════════════════════
// Module Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock("js-cookie", () => ({
  default: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

vi.mock("@/lib/logger", () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}));

vi.mock("@/lib/api/auth-client", () => ({
  authApiClient: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn(),
    attemptTokenRefresh: vi.fn(),
    setToken: vi.fn(),
    clearToken: vi.fn(),
  },
}));

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Helper to render the AuthProvider and extract auth methods via context.
 * We dynamically import React, render, and the store after vi.resetModules()
 * so that each test picks up fresh module state.
 */
async function setupAuthProvider() {
  const React = await import("react");
  const { render, act, waitFor } = await import("@testing-library/react");
  const { AuthProvider, useAuth } = await import("../../stores/auth.store");

  // Use a mutable ref so the test always reads the latest auth state
  // (after re-renders from login/logout/checkAuth)
  let latestState: ReturnType<typeof useAuth> | null = null;

  function Consumer() {
    latestState = useAuth();
    return null;
  }

  // Suppress React.act warnings from auto-running checkAuth on mount
  await act(async () => {
    render(
      React.createElement(AuthProvider, null, React.createElement(Consumer)),
    );
  });

  // Wait for initial checkAuth to settle (isLoading -> false)
  await waitFor(() => {
    expect(latestState).not.toBeNull();
  });

  // Return an object with a getter for authState so tests always see the
  // latest value after React re-renders (not a stale snapshot).
  const result = { act, waitFor } as {
    act: typeof act;
    waitFor: typeof waitFor;
    authState: ReturnType<typeof useAuth>;
  };
  Object.defineProperty(result, "authState", {
    get: () => latestState!,
    enumerable: true,
  });
  return result;
}

describe("Auth Store Security", () => {
  const originalEnv = process.env;
  let originalFetch: typeof global.fetch;
  let originalBroadcastChannel: typeof globalThis.BroadcastChannel;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
    process.env = { ...originalEnv };
    originalFetch = global.fetch;
    originalBroadcastChannel = globalThis.BroadcastChannel;

    // Default fetch mock: session check returns no session, other calls succeed
    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (typeof url === "string" && url.includes("/api/auth/session")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ hasSession: false }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
  });

  afterEach(() => {
    process.env = originalEnv;
    global.fetch = originalFetch;
    globalThis.BroadcastChannel = originalBroadcastChannel;
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // sanitizeUser UUID validation
  // ═══════════════════════════════════════════════════════════════════════════

  describe("sanitizeUser UUID validation", () => {
    /**
     * Helper: sets up checkAuth to return a user with the given tenant_id.
     * sanitizeUser is called internally by checkAuth (and login), so we
     * verify its behavior by observing the resulting user state after mount.
     */
    function mockCheckAuthWithTenantId(tenantId?: string) {
      const userPayload: Record<string, unknown> = {
        id: "user-1",
        email: "farmer@sahool.com",
        name: "Farmer",
        role: "user",
      };
      if (tenantId !== undefined) {
        userPayload.tenant_id = tenantId;
      }
      return userPayload;
    }

    async function setupWithTenantId(tenantId?: string) {
      const { authApiClient } = await import("@/lib/api/auth-client");
      const userPayload = mockCheckAuthWithTenantId(tenantId);

      // checkAuth: session exists → getCurrentUser returns user with tenant_id
      global.fetch = vi.fn().mockImplementation((url: string) => {
        if (typeof url === "string" && url.includes("/api/auth/session")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ hasSession: true }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      vi.mocked(authApiClient.getCurrentUser).mockResolvedValue({
        success: true,
        data: userPayload as { id: string; email: string; name: string; role: string; tenant_id?: string },
      });

      return setupAuthProvider();
    }

    it("should keep a valid UUID v4 tenant_id", async () => {
      const validUUID = "550e8400-e29b-41d4-a716-446655440000";
      const { authState, waitFor } = await setupWithTenantId(validUUID);

      await waitFor(() => {
        expect(authState.user).not.toBeNull();
        expect(authState.user!.tenant_id).toBe(validUUID);
      });
    });

    it("should clear invalid tenant_id (malicious-input)", async () => {
      const { authState, waitFor } = await setupWithTenantId("malicious-input");

      await waitFor(() => {
        expect(authState.user).not.toBeNull();
        expect(authState.user!.tenant_id).toBeUndefined();
      });
    });

    it("should clear SQL injection attempt in tenant_id", async () => {
      const { authState, waitFor } = await setupWithTenantId("'; DROP TABLE users;--");

      await waitFor(() => {
        expect(authState.user).not.toBeNull();
        expect(authState.user!.tenant_id).toBeUndefined();
      });
    });

    it("should keep empty string tenant_id as-is (falsy, skips UUID check)", async () => {
      const { authState, waitFor } = await setupWithTenantId("");

      await waitFor(() => {
        expect(authState.user).not.toBeNull();
        // Empty string is falsy, so the UUID check is skipped and value preserved
        expect(authState.user!.tenant_id).toBe("");
      });
    });

    it("should leave tenant_id undefined when not provided by API", async () => {
      // Pass undefined to omit tenant_id from the user payload
      const { authState, waitFor } = await setupWithTenantId(undefined);

      await waitFor(() => {
        expect(authState.user).not.toBeNull();
        expect(authState.user!.tenant_id).toBeUndefined();
      });
    });

    it("should also sanitize tenant_id during checkAuth", async () => {
      const { authState, waitFor } = await setupWithTenantId("not-a-uuid-at-all");

      await waitFor(() => {
        expect(authState.user).not.toBeNull();
        expect(authState.user!.id).toBe("user-1");
        expect(authState.user!.tenant_id).toBeUndefined();
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // BroadcastChannel logout
  // ═══════════════════════════════════════════════════════════════════════════

  describe("BroadcastChannel logout notification", () => {
    it("should send broadcast message with { type: 'logout' } on logout", async () => {
      const postMessageSpy = vi.fn();
      const closeSpy = vi.fn();

      // Mock BroadcastChannel globally
      globalThis.BroadcastChannel = vi.fn().mockImplementation(() => ({
        postMessage: postMessageSpy,
        close: closeSpy,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })) as unknown as typeof BroadcastChannel;

      global.fetch = vi.fn().mockImplementation((url: string) => {
        if (typeof url === "string" && url.includes("/api/auth/session")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ hasSession: false }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      const { authState, act } = await setupAuthProvider();

      await act(async () => {
        await authState.logout();
      });

      // Verify BroadcastChannel was created with correct channel name
      expect(globalThis.BroadcastChannel).toHaveBeenCalledWith("sahool_auth");

      // Verify postMessage was called with logout type
      expect(postMessageSpy).toHaveBeenCalledWith({ type: "logout" });

      // Verify channel was closed after sending
      expect(closeSpy).toHaveBeenCalled();
    });

    it("should handle gracefully when BroadcastChannel is undefined", async () => {
      // Remove BroadcastChannel from global scope
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (globalThis as any).BroadcastChannel;

      global.fetch = vi.fn().mockImplementation((url: string) => {
        if (typeof url === "string" && url.includes("/api/auth/session")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ hasSession: false }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });

      const { authState, act } = await setupAuthProvider();

      // Should not reject when BroadcastChannel is unavailable
      await act(async () => {
        await authState.logout();
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AbortController timeout on session DELETE
  // ═══════════════════════════════════════════════════════════════════════════

  describe("Timeout on session DELETE calls", () => {
    it("should call fetch with an AbortSignal during logout", async () => {
      const fetchSpy = vi.fn().mockImplementation((url: string) => {
        if (typeof url === "string" && url.includes("/api/auth/session")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ hasSession: false }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });
      global.fetch = fetchSpy;

      // Remove BroadcastChannel to simplify
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (globalThis as any).BroadcastChannel;

      const { authState, act } = await setupAuthProvider();

      await act(async () => {
        await authState.logout();
      });

      // Find the DELETE call to /api/auth/session
      const deleteCall = fetchSpy.mock.calls.find(
        (call: unknown[]) =>
          typeof call[0] === "string" &&
          call[0].includes("/api/auth/session") &&
          call[1]?.method === "DELETE",
      );

      expect(deleteCall).toBeDefined();
      // The second argument should contain a signal property (AbortController.signal)
      expect(deleteCall![1]).toHaveProperty("signal");
      expect(deleteCall![1].signal).toBeInstanceOf(AbortSignal);
    });

    it("should continue logout even if session DELETE is aborted", async () => {
      const fetchSpy = vi.fn().mockImplementation((url: string, opts?: RequestInit) => {
        if (
          typeof url === "string" &&
          url.includes("/api/auth/session") &&
          opts?.method === "DELETE"
        ) {
          // Simulate abort error
          return Promise.reject(new DOMException("Aborted", "AbortError"));
        }
        if (typeof url === "string" && url.includes("/api/auth/session")) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ hasSession: false }),
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });
      global.fetch = fetchSpy;

      // Remove BroadcastChannel to simplify
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (globalThis as any).BroadcastChannel;

      const { authApiClient } = await import("@/lib/api/auth-client");
      const { authState, act, waitFor } = await setupAuthProvider();

      await act(async () => {
        await authState.logout();
      });

      // Should still complete logout: clearToken called, user set to null
      await waitFor(() => {
        expect(authApiClient.clearToken).toHaveBeenCalled();
        expect(authState.user).toBeNull();
        expect(authState.isAuthenticated).toBe(false);
      });
    });
  });
});

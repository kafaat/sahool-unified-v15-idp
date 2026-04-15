/**
 * Fetch-based API client with automatic token refresh on 401.
 * Access token is stored in module memory (not localStorage).
 * Refresh token is an httpOnly cookie — the browser sends it automatically.
 */

const API_BASE =
  typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
    : process.env.API_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

let _accessToken: string | null = null;
let _refreshing: Promise<boolean> | null = null;

export function setAccessToken(token: string | null) {
  _accessToken = token;
}

export function getAccessToken(): string | null {
  return _accessToken;
}

// ── Core request ──────────────────────────────────────────────────────────────

async function _fetch(path: string, init: RequestInit = {}, retry = true): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };

  if (_accessToken) {
    headers["Authorization"] = `Bearer ${_accessToken}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include", // sends httpOnly refresh_token cookie
    headers,
  });

  if (res.status === 401 && retry && path !== "/api/v1/auth/refresh") {
    // Deduplicate concurrent refresh calls
    if (!_refreshing) {
      _refreshing = _doRefresh().finally(() => {
        _refreshing = null;
      });
    }
    const refreshed = await _refreshing;
    if (refreshed) {
      return _fetch(path, init, false); // retry once
    }
    // Redirect to login
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }

  return res;
}

async function _doRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (res.ok) {
      const data = await res.json();
      _accessToken = data.access_token;
      return true;
    }
  } catch {
    // network error
  }
  _accessToken = null;
  return false;
}

// ── Public helpers ────────────────────────────────────────────────────────────

export const api = {
  get: (path: string) => _fetch(path, { method: "GET" }),

  post: (path: string, body?: unknown) =>
    _fetch(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),

  patch: (path: string, body?: unknown) =>
    _fetch(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),

  delete: (path: string) => _fetch(path, { method: "DELETE" }),
};

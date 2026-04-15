/**
 * Zustand auth store — UI state only.
 * The real security boundary is Next.js middleware.ts + server-side cookie checks.
 */
import { create } from "zustand";
import { api, setAccessToken } from "@/lib/api";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
}

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hydrate: () => Promise<void>;
  updateUser: (patch: Partial<AuthUser>) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: false,
  isAuthenticated: false,

  // ── Login ──────────────────────────────────────────────────────────────────
  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const res = await api.post("/api/v1/auth/login", { email, password });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Login failed");
      }
      const data = await res.json();
      setAccessToken(data.access_token);
      set({ user: data.user, isAuthenticated: true, isLoading: false });
    } catch (e) {
      set({ isLoading: false });
      throw e;
    }
  },

  // ── Register ───────────────────────────────────────────────────────────────
  register: async (email, name, password) => {
    set({ isLoading: true });
    try {
      const res = await api.post("/api/v1/auth/register", { email, name, password });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Registration failed");
      }
      const data = await res.json();
      setAccessToken(data.access_token);
      set({ user: data.user, isAuthenticated: true, isLoading: false });
    } catch (e) {
      set({ isLoading: false });
      throw e;
    }
  },

  // ── Logout ─────────────────────────────────────────────────────────────────
  logout: async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } catch {
      // best-effort
    }
    setAccessToken(null);
    set({ user: null, isAuthenticated: false });
    window.location.href = "/login";
  },

  // ── Hydrate (called on app mount to restore session) ──────────────────────
  hydrate: async () => {
    set({ isLoading: true });
    try {
      // Try to refresh access token first (uses httpOnly cookie)
      const refreshRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/refresh`,
        { method: "POST", credentials: "include" }
      );
      if (refreshRes.ok) {
        const { access_token } = await refreshRes.json();
        setAccessToken(access_token);
        // Now fetch user info
        const meRes = await api.get("/api/v1/auth/me");
        if (meRes.ok) {
          const user = await meRes.json();
          set({ user, isAuthenticated: true, isLoading: false });
          return;
        }
      }
    } catch {
      // silently fail — user will be redirected by middleware
    }
    setAccessToken(null);
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  // ── Local update (optimistic UI) ──────────────────────────────────────────
  updateUser: (patch) => {
    const current = get().user;
    if (current) set({ user: { ...current, ...patch } });
  },
}));

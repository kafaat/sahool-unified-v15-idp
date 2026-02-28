/**
 * Theme Store Tests
 * اختبارات مخزن السمات
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import React from "react";
import { ThemeProvider, useTheme } from "../theme.store";

function wrapper({ children }: { children: React.ReactNode }) {
  return <ThemeProvider>{children}</ThemeProvider>;
}

describe("Theme Store", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.documentElement.classList.remove("light", "dark");
  });

  describe("useTheme hook", () => {
    it("throws error when used outside ThemeProvider", () => {
      expect(() => {
        renderHook(() => useTheme());
      }).toThrow("useTheme must be used within a ThemeProvider");
    });

    it("provides initial theme state", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      expect(result.current.theme).toBeDefined();
      expect(result.current.resolvedTheme).toBeDefined();
      expect(typeof result.current.setTheme).toBe("function");
      expect(typeof result.current.toggleTheme).toBe("function");
    });

    it("resolves system theme to light by default (matchMedia mocked to false)", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      // matchMedia is mocked to return matches: false, so system resolves to light
      expect(result.current.resolvedTheme).toBe("light");
    });
  });

  describe("setTheme", () => {
    it("sets theme to dark", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => {
        result.current.setTheme("dark");
      });

      expect(result.current.theme).toBe("dark");
      expect(result.current.resolvedTheme).toBe("dark");
    });

    it("sets theme to light", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => {
        result.current.setTheme("light");
      });

      expect(result.current.theme).toBe("light");
      expect(result.current.resolvedTheme).toBe("light");
    });

    it("sets theme to system", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => {
        result.current.setTheme("system");
      });

      expect(result.current.theme).toBe("system");
      // Resolved depends on matchMedia mock
      expect(["light", "dark"]).toContain(result.current.resolvedTheme);
    });

    it("persists theme to localStorage", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => {
        result.current.setTheme("dark");
      });

      expect(localStorage.setItem).toHaveBeenCalledWith(
        "sahool-admin-theme",
        "dark",
      );
    });
  });

  describe("toggleTheme", () => {
    it("toggles from light to dark", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => {
        result.current.setTheme("light");
      });

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.resolvedTheme).toBe("dark");
    });

    it("toggles from dark to light", () => {
      const { result } = renderHook(() => useTheme(), { wrapper });

      act(() => {
        result.current.setTheme("dark");
      });

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.resolvedTheme).toBe("light");
    });
  });
});

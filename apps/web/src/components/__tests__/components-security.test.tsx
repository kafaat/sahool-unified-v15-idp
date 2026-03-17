/**
 * Web Component Render & Security Tests
 * اختبارات عرض وأمان مكونات الويب
 *
 * Verifies that key web components render correctly,
 * including ErrorBoundary behavior on errors, LocaleSwitcher,
 * and core UI primitives (Button, Card, Badge).
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

// Mock logger
vi.mock("@/lib/logger", () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    critical: vi.fn(),
    debug: vi.fn(),
  },
}));

// Mock next/navigation for LocaleSwitcher
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn().mockResolvedValue(undefined),
  }),
  usePathname: () => "/",
}));

// Mock next-intl for LocaleSwitcher
vi.mock("next-intl", () => ({
  useLocale: () => "ar",
  useTranslations: () => (key: string) => key,
}));

// Mock @sahool/i18n
vi.mock("@sahool/i18n", () => ({
  locales: ["ar", "en"],
  getLocaleDisplayName: (locale: string) =>
    locale === "ar" ? "العربية" : "English",
}));

// ---------------------------------------------------------------------------
// Imports
// ---------------------------------------------------------------------------

import { ErrorBoundary } from "../common/ErrorBoundary";
import { LocaleSwitcher } from "../common/LocaleSwitcher";
import { Button } from "../ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../ui/card";
import { Badge } from "../ui/badge";

// ---------------------------------------------------------------------------
// ErrorBoundary Tests
// ---------------------------------------------------------------------------

describe("Web ErrorBoundary", () => {
  it("renders children when no error occurs", () => {
    render(
      <ErrorBoundary>
        <div data-testid="child">Safe content</div>
      </ErrorBoundary>,
    );
    expect(screen.getByTestId("child")).toBeInTheDocument();
    expect(screen.getByText("Safe content")).toBeInTheDocument();
  });

  it("shows error UI when child component throws", () => {
    const ThrowingComponent = () => {
      throw new Error("Test error for boundary");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    // Default error UI has Arabic text
    expect(screen.getByText("حدث خطأ غير متوقع")).toBeInTheDocument();
    expect(
      screen.getByText("نعتذر عن الإزعاج. سنعمل على حل المشكلة قريباً"),
    ).toBeInTheDocument();

    // Should have retry and refresh buttons
    expect(screen.getByText("حاول مرة أخرى")).toBeInTheDocument();
    expect(screen.getByText("تحديث الصفحة")).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it("renders custom fallback when provided and error occurs", () => {
    const ThrowingComponent = () => {
      throw new Error("Fallback test");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Custom error display</div>}>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Custom error display")).toBeInTheDocument();
    consoleSpy.mockRestore();
  });

  it("calls onError callback when error is caught", () => {
    const onErrorMock = vi.fn();
    const ThrowingComponent = () => {
      throw new Error("Callback test");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary onError={onErrorMock}>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    expect(onErrorMock).toHaveBeenCalledTimes(1);
    expect(onErrorMock).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      }),
    );

    consoleSpy.mockRestore();
  });

  it("generates and displays an error reference ID", () => {
    const ThrowingComponent = () => {
      throw new Error("ID test");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    // Error ID starts with "ERR-"
    expect(screen.getByText(/رمز المرجع:/)).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it("shows home link when showHomeLink prop is true", () => {
    const ThrowingComponent = () => {
      throw new Error("Home link test");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary showHomeLink>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    expect(screen.getByText("الصفحة الرئيسية")).toBeInTheDocument();
    // Should NOT show retry when showHomeLink is true
    expect(screen.queryByText("حاول مرة أخرى")).not.toBeInTheDocument();

    consoleSpy.mockRestore();
  });
});

// ---------------------------------------------------------------------------
// LocaleSwitcher Tests
// ---------------------------------------------------------------------------

describe("Web LocaleSwitcher", () => {
  it("renders without crashing", () => {
    render(<LocaleSwitcher />);
    // Should show both locale buttons
    expect(screen.getByText("العربية")).toBeInTheDocument();
    expect(screen.getByText("English")).toBeInTheDocument();
  });

  it("marks the current locale as active/disabled", () => {
    render(<LocaleSwitcher />);
    // Current locale is "ar" (from mock), so Arabic button should be disabled
    const arabicButton = screen.getByText("العربية").closest("button");
    expect(arabicButton).toBeDisabled();
  });

  it("has accessible labels for locale switching", () => {
    render(<LocaleSwitcher />);
    const arabicButton = screen.getByLabelText("Switch to العربية");
    const englishButton = screen.getByLabelText("Switch to English");
    expect(arabicButton).toBeInTheDocument();
    expect(englishButton).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Button Tests
// ---------------------------------------------------------------------------

describe("Web Button", () => {
  it("renders without crashing", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("renders with primary variant by default", () => {
    render(<Button>Primary</Button>);
    const button = screen.getByRole("button", { name: /Primary/ });
    expect(button).toBeInTheDocument();
    expect(button.className).toContain("bg-sahool-green-600");
  });

  it("renders with danger variant", () => {
    render(<Button variant="danger">Delete</Button>);
    const button = screen.getByRole("button", { name: /Delete/ });
    expect(button.className).toContain("bg-red-600");
  });

  it("renders in loading state with spinner", () => {
    render(<Button isLoading>Submit</Button>);
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(button).toBeDisabled();
  });

  it("renders full width when fullWidth is true", () => {
    render(<Button fullWidth>Full</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("w-full");
  });

  it("renders with different sizes", () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    let button = screen.getByRole("button");
    expect(button.className).toContain("text-sm");

    rerender(<Button size="lg">Large</Button>);
    button = screen.getByRole("button");
    expect(button.className).toContain("text-lg");
  });

  it("defaults to type=button", () => {
    render(<Button>Default</Button>);
    expect(screen.getByRole("button")).toHaveAttribute("type", "button");
  });
});

// ---------------------------------------------------------------------------
// Card Tests
// ---------------------------------------------------------------------------

describe("Web Card", () => {
  it("renders without crashing", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("renders with elevated variant", () => {
    render(<Card variant="elevated">Elevated</Card>);
    const card = screen.getByText("Elevated");
    expect(card.className).toContain("shadow-lg");
  });

  it("renders Card sub-components", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Title</CardTitle>
          <CardDescription>Description text</CardDescription>
        </CardHeader>
        <CardContent>Body content</CardContent>
        <CardFooter>Footer content</CardFooter>
      </Card>,
    );

    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Description text")).toBeInTheDocument();
    expect(screen.getByText("Body content")).toBeInTheDocument();
    expect(screen.getByText("Footer content")).toBeInTheDocument();
  });

  it("renders as article element when specified", () => {
    render(
      <Card as="article" data-testid="article-card">
        Article card
      </Card>,
    );
    const card = screen.getByTestId("article-card");
    expect(card.tagName).toBe("ARTICLE");
  });

  it("is focusable when interactive", () => {
    render(
      <Card interactive data-testid="interactive-card">
        Interactive card
      </Card>,
    );
    const card = screen.getByTestId("interactive-card");
    expect(card).toHaveAttribute("tabindex", "0");
    expect(card).toHaveAttribute("role", "button");
  });
});

// ---------------------------------------------------------------------------
// Badge Tests
// ---------------------------------------------------------------------------

describe("Web Badge", () => {
  it("renders without crashing", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("renders with default variant", () => {
    render(<Badge>Default</Badge>);
    const badge = screen.getByText("Default");
    expect(badge.className).toContain("bg-gray-100");
  });

  it("renders with success variant", () => {
    render(<Badge variant="success">Success</Badge>);
    const badge = screen.getByText("Success");
    expect(badge.className).toContain("bg-sahool-green-100");
  });

  it("renders with danger variant", () => {
    render(<Badge variant="danger">Error</Badge>);
    const badge = screen.getByText("Error");
    expect(badge.className).toContain("bg-red-100");
  });

  it("renders with warning variant", () => {
    render(<Badge variant="warning">Warning</Badge>);
    const badge = screen.getByText("Warning");
    expect(badge.className).toContain("bg-yellow-100");
  });

  it("renders with info variant", () => {
    render(<Badge variant="info">Info</Badge>);
    const badge = screen.getByText("Info");
    expect(badge.className).toContain("bg-blue-100");
  });

  it("renders with different sizes", () => {
    const { rerender } = render(<Badge size="sm">Small</Badge>);
    let badge = screen.getByText("Small");
    expect(badge.className).toContain("text-xs");

    rerender(<Badge size="lg">Large</Badge>);
    badge = screen.getByText("Large");
    expect(badge.className).toContain("text-base");
  });

  it("renders as an inline span element", () => {
    render(<Badge data-testid="badge-el">Span</Badge>);
    const badge = screen.getByTestId("badge-el");
    expect(badge.tagName).toBe("SPAN");
  });
});

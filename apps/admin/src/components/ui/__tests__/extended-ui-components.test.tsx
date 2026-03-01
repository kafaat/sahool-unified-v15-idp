/**
 * Extended UI Component Tests
 * اختبارات مكونات واجهة المستخدم الموسعة
 *
 * Tests for SearchFilter, BulkActions, ExportButton, ThemeToggle
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import React from "react";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
}));

// Mock lucide-react icons
vi.mock("lucide-react", () => {
  const _React = require("react");
  const _createIcon = (name: string) => {
    const Icon = (props: Record<string, unknown>) =>
      _React.createElement("svg", { "data-testid": `icon-${name}`, ...props });
    Icon.displayName = name;
    return Icon;
  };
  return {
    __esModule: true,
    Search: _createIcon("Search"),
    X: _createIcon("X"),
    Filter: _createIcon("Filter"),
    ChevronDown: _createIcon("ChevronDown"),
    Calendar: _createIcon("Calendar"),
    Check: _createIcon("Check"),
    Download: _createIcon("Download"),
    FileSpreadsheet: _createIcon("FileSpreadsheet"),
    FileText: _createIcon("FileText"),
    Loader2: _createIcon("Loader2"),
    Trash2: _createIcon("Trash2"),
    Send: _createIcon("Send"),
    Archive: _createIcon("Archive"),
    Tag: _createIcon("Tag"),
    Edit2: _createIcon("Edit2"),
    MoreHorizontal: _createIcon("MoreHorizontal"),
    CheckCircle: _createIcon("CheckCircle"),
    AlertTriangle: _createIcon("AlertTriangle"),
    Sun: _createIcon("Sun"),
    Moon: _createIcon("Moon"),
    Monitor: _createIcon("Monitor"),
  };
});

// Mock @/lib/utils
vi.mock("@/lib/utils", () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(" "),
}));

// Mock @/lib/export
vi.mock("@/lib/export", () => ({
  exportData: vi.fn(),
  exportFormatLabels: {
    csv: { ar: "CSV", en: "CSV" },
    excel: { ar: "Excel", en: "Excel" },
    pdf: { ar: "PDF", en: "PDF" },
  },
}));

// Mock @/stores/theme.store
vi.mock("@/stores/theme.store", () => ({
  useTheme: vi.fn(() => ({
    theme: "light",
    resolvedTheme: "light",
    setTheme: vi.fn(),
    toggleTheme: vi.fn(),
  })),
}));

// Import components after mocks
import SearchFilter from "../SearchFilter";
import BulkActions from "../BulkActions";
import ThemeToggle from "../ThemeToggle";
import { useTheme } from "@/stores/theme.store";

// ═══════════════════════════════════════════════════════════════════════════
// SearchFilter Tests | اختبارات مكون البحث والفلترة
// ═══════════════════════════════════════════════════════════════════════════

describe("SearchFilter", () => {
  it("renders search input with Arabic placeholder", () => {
    render(<SearchFilter />);
    expect(screen.getByPlaceholderText("بحث...")).toBeInTheDocument();
  });

  it("renders search input with custom placeholder", () => {
    render(<SearchFilter searchPlaceholderAr="بحث في المزارع..." />);
    expect(screen.getByPlaceholderText("بحث في المزارع...")).toBeInTheDocument();
  });

  it("calls onSearchChange with debounce", async () => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout"] });
    const onSearchChange = vi.fn();
    render(<SearchFilter onSearchChange={onSearchChange} debounceMs={300} />);

    const input = screen.getByPlaceholderText("بحث...");
    fireEvent.change(input, { target: { value: "wheat" } });

    // Should not be called immediately
    expect(onSearchChange).not.toHaveBeenCalled();

    // Advance timers
    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(onSearchChange).toHaveBeenCalledWith("wheat");
    vi.useRealTimers();
  });

  it("shows clear button when search has value", () => {
    render(<SearchFilter searchValue="test" />);
    expect(screen.getByLabelText("مسح البحث")).toBeInTheDocument();
  });

  it("clears search on clear button click", () => {
    const onSearchChange = vi.fn();
    render(<SearchFilter searchValue="test" onSearchChange={onSearchChange} />);

    fireEvent.click(screen.getByLabelText("مسح البحث"));
    expect(onSearchChange).toHaveBeenCalledWith("");
  });

  it("shows filter button when filters are provided", () => {
    const filters = [
      {
        key: "status",
        label: "Status",
        labelAr: "الحالة",
        type: "select" as const,
        options: [
          { value: "active", label: "Active", labelAr: "نشط" },
          { value: "inactive", label: "Inactive", labelAr: "غير نشط" },
        ],
      },
    ];
    render(<SearchFilter filters={filters} />);
    expect(screen.getByText("الفلاتر")).toBeInTheDocument();
  });

  it("toggles filter panel on button click", () => {
    const filters = [
      {
        key: "status",
        label: "Status",
        labelAr: "الحالة",
        type: "select" as const,
        options: [
          { value: "active", label: "Active", labelAr: "نشط" },
        ],
      },
    ];
    render(<SearchFilter filters={filters} />);

    fireEvent.click(screen.getByText("الفلاتر"));
    expect(screen.getByText("الحالة")).toBeInTheDocument();
  });

  it("shows active filter count", () => {
    const filters = [
      {
        key: "status",
        label: "Status",
        labelAr: "الحالة",
        type: "select" as const,
        options: [],
      },
    ];
    const activeFilters = [
      { key: "status", value: "active", label: "الحالة" },
    ];
    render(
      <SearchFilter
        filters={filters}
        activeFilters={activeFilters}
        showFilterCount={true}
      />
    );
    // Filter count badge should show "1"
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  it("does not show filter button when no filters", () => {
    render(<SearchFilter filters={[]} />);
    expect(screen.queryByText("الفلاتر")).not.toBeInTheDocument();
  });

  it("renders active filter chips", () => {
    const activeFilters = [
      { key: "status", value: "active", label: "الحالة" },
    ];
    render(<SearchFilter activeFilters={activeFilters} />);
    expect(screen.getByText("الحالة:")).toBeInTheDocument();
    expect(screen.getByText("active")).toBeInTheDocument();
  });

  it("calls onFilterChange when removing a filter chip", () => {
    const onFilterChange = vi.fn();
    const activeFilters = [
      { key: "status", value: "active", label: "الحالة" },
    ];
    render(
      <SearchFilter
        activeFilters={activeFilters}
        onFilterChange={onFilterChange}
      />
    );

    fireEvent.click(screen.getByLabelText("إزالة الفلتر"));
    expect(onFilterChange).toHaveBeenCalledWith("status", null);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// BulkActions Tests | اختبارات مكون العمليات الجماعية
// ═══════════════════════════════════════════════════════════════════════════

describe("BulkActions", () => {
  it("returns null when no items selected", () => {
    const { container } = render(
      <BulkActions selectedCount={0} totalCount={100} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders when items are selected", () => {
    render(<BulkActions selectedCount={5} totalCount={100} />);
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("عنصر محدد من 100")).toBeInTheDocument();
  });

  it("shows default action buttons", () => {
    render(<BulkActions selectedCount={3} totalCount={10} />);
    expect(screen.getByTitle("تصدير")).toBeInTheDocument();
    expect(screen.getByTitle("أرشفة")).toBeInTheDocument();
    expect(screen.getByTitle("حذف")).toBeInTheDocument();
  });

  it("shows select all button when not all selected", () => {
    const onSelectAll = vi.fn();
    render(
      <BulkActions
        selectedCount={5}
        totalCount={100}
        onSelectAll={onSelectAll}
      />
    );
    expect(screen.getByText("تحديد الكل (100)")).toBeInTheDocument();
  });

  it("calls onSelectAll when select all clicked", () => {
    const onSelectAll = vi.fn();
    render(
      <BulkActions
        selectedCount={5}
        totalCount={100}
        onSelectAll={onSelectAll}
      />
    );

    fireEvent.click(screen.getByText("تحديد الكل (100)"));
    expect(onSelectAll).toHaveBeenCalled();
  });

  it("shows deselect button", () => {
    const onDeselectAll = vi.fn();
    render(
      <BulkActions
        selectedCount={5}
        totalCount={100}
        onDeselectAll={onDeselectAll}
      />
    );
    expect(screen.getByText("إلغاء التحديد")).toBeInTheDocument();
  });

  it("calls onDeselectAll when deselect clicked", () => {
    const onDeselectAll = vi.fn();
    render(
      <BulkActions
        selectedCount={5}
        totalCount={100}
        onDeselectAll={onDeselectAll}
      />
    );

    fireEvent.click(screen.getByText("إلغاء التحديد"));
    expect(onDeselectAll).toHaveBeenCalled();
  });

  it("shows confirmation modal for dangerous actions", () => {
    render(<BulkActions selectedCount={3} totalCount={10} />);

    fireEvent.click(screen.getByTitle("حذف"));

    // Confirmation modal should appear
    expect(screen.getByText("تأكيد العملية")).toBeInTheDocument();
    expect(screen.getByText("هل أنت متأكد من حذف العناصر المحددة؟")).toBeInTheDocument();
  });

  it("can cancel confirmation modal", () => {
    render(<BulkActions selectedCount={3} totalCount={10} />);

    fireEvent.click(screen.getByTitle("حذف"));
    expect(screen.getByText("تأكيد العملية")).toBeInTheDocument();

    fireEvent.click(screen.getByText("إلغاء"));
    expect(screen.queryByText("تأكيد العملية")).not.toBeInTheDocument();
  });

  it("renders custom actions", () => {
    const MockIcon = (props: Record<string, unknown>) =>
      React.createElement("svg", props);
    const customActions = [
      {
        id: "custom",
        label: "Custom",
        labelAr: "مخصص",
        icon: MockIcon,
      },
    ];
    render(
      <BulkActions
        selectedCount={3}
        totalCount={10}
        actions={customActions}
      />
    );
    expect(screen.getByTitle("مخصص")).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// ThemeToggle Tests | اختبارات مكون تبديل السمة
// ═══════════════════════════════════════════════════════════════════════════

describe("ThemeToggle", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders icon variant by default", () => {
    render(<ThemeToggle />);
    // Should have an aria-label for toggle
    expect(screen.getByLabelText("تبديل للوضع الداكن")).toBeInTheDocument();
  });

  it("calls toggleTheme on icon click", () => {
    const mockToggle = vi.fn();
    vi.mocked(useTheme).mockReturnValue({
      theme: "light",
      resolvedTheme: "light",
      setTheme: vi.fn(),
      toggleTheme: mockToggle,
    });

    render(<ThemeToggle variant="icon" />);
    fireEvent.click(screen.getByLabelText("تبديل للوضع الداكن"));
    expect(mockToggle).toHaveBeenCalled();
  });

  it("shows sun icon in dark mode", () => {
    vi.mocked(useTheme).mockReturnValue({
      theme: "dark",
      resolvedTheme: "dark",
      setTheme: vi.fn(),
      toggleTheme: vi.fn(),
    });

    render(<ThemeToggle variant="icon" />);
    expect(screen.getByLabelText("تبديل للوضع الفاتح")).toBeInTheDocument();
  });

  it("renders button variant with text", () => {
    vi.mocked(useTheme).mockReturnValue({
      theme: "light",
      resolvedTheme: "light",
      setTheme: vi.fn(),
      toggleTheme: vi.fn(),
    });

    render(<ThemeToggle variant="button" />);
    expect(screen.getByText("الوضع الداكن")).toBeInTheDocument();
  });

  it("renders button variant with light mode text in dark mode", () => {
    vi.mocked(useTheme).mockReturnValue({
      theme: "dark",
      resolvedTheme: "dark",
      setTheme: vi.fn(),
      toggleTheme: vi.fn(),
    });

    render(<ThemeToggle variant="button" />);
    expect(screen.getByText("الوضع الفاتح")).toBeInTheDocument();
  });

  it("renders dropdown variant", () => {
    render(<ThemeToggle variant="dropdown" />);
    expect(screen.getByLabelText("اختيار السمة")).toBeInTheDocument();
  });

  it("opens dropdown on click", () => {
    render(<ThemeToggle variant="dropdown" />);

    fireEvent.click(screen.getByLabelText("اختيار السمة"));

    expect(screen.getByText("فاتح")).toBeInTheDocument();
    expect(screen.getByText("داكن")).toBeInTheDocument();
    expect(screen.getByText("تلقائي")).toBeInTheDocument();
  });

  it("calls setTheme when dropdown option is selected", () => {
    const mockSetTheme = vi.fn();
    vi.mocked(useTheme).mockReturnValue({
      theme: "light",
      resolvedTheme: "light",
      setTheme: mockSetTheme,
      toggleTheme: vi.fn(),
    });

    render(<ThemeToggle variant="dropdown" />);

    fireEvent.click(screen.getByLabelText("اختيار السمة"));
    fireEvent.click(screen.getByText("داكن"));

    expect(mockSetTheme).toHaveBeenCalledWith("dark");
  });
});

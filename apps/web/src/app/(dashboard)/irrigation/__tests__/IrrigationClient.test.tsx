import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "../../../../__tests__/test-utils";
import IrrigationClient from "../IrrigationClient";

// Mock the API client
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    getIrrigationSchedules: vi.fn().mockResolvedValue({ success: false }),
    createIrrigationSchedule: vi.fn().mockResolvedValue({ success: true, data: { id: "new-1", fieldId: "field-new", fieldName: "حقل جديد", type: "drip", status: "scheduled", scheduledAt: new Date().toISOString(), duration: 60, waterAmount: 100 } }),
    updateIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
    deleteIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
    startIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
    stopIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
  },
}));

// Mock the toast
vi.mock("@/components/ui/toast", () => ({
  useToast: () => ({
    showToast: vi.fn(),
  }),
}));

describe("IrrigationClient", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render the irrigation management page", () => {
    render(<IrrigationClient />);
    expect(screen.getByText("إدارة الري")).toBeInTheDocument();
  });

  it("should display stat cards", () => {
    render(<IrrigationClient />);
    expect(screen.getByText("استهلاك اليوم")).toBeInTheDocument();
    expect(screen.getByText("جاري الآن")).toBeInTheDocument();
    expect(screen.getByText("مجدول اليوم")).toBeInTheDocument();
    expect(screen.getByText("كفاءة الري")).toBeInTheDocument();
  });

  it("should display table headers", () => {
    render(<IrrigationClient />);
    expect(screen.getByText("الحقل")).toBeInTheDocument();
    expect(screen.getByText("النوع")).toBeInTheDocument();
    expect(screen.getByText("الموعد")).toBeInTheDocument();
    expect(screen.getByText("كمية المياه")).toBeInTheDocument();
    expect(screen.getByText("الحالة")).toBeInTheDocument();
  });

  it("should display mock schedule data on load", () => {
    render(<IrrigationClient />);
    expect(screen.getByText("الحقل الشمالي")).toBeInTheDocument();
    expect(screen.getByText("الحقل الجنوبي")).toBeInTheDocument();
    expect(screen.getByText("حقل القمح")).toBeInTheDocument();
  });

  it("should show overdue alert when overdue schedules exist", () => {
    render(<IrrigationClient />);
    expect(screen.getByText(/جدول ري متأخر/)).toBeInTheDocument();
  });

  it("should filter schedules by search term", () => {
    render(<IrrigationClient />);

    const searchInput = screen.getByPlaceholderText("بحث عن حقل...");
    fireEvent.change(searchInput, { target: { value: "القمح" } });

    expect(screen.getByText("حقل القمح")).toBeInTheDocument();
    expect(screen.queryByText("الحقل الشمالي")).not.toBeInTheDocument();
  });

  it("should open create modal on button click", () => {
    render(<IrrigationClient />);

    const createBtn = screen.getByText("جدولة ري");
    fireEvent.click(createBtn);

    expect(screen.getByText("جدولة ري جديدة")).toBeInTheDocument();
    expect(screen.getByText("اسم الحقل")).toBeInTheDocument();
    expect(screen.getByText("نوع الري")).toBeInTheDocument();
  });

  it("should close modal on cancel", () => {
    render(<IrrigationClient />);

    fireEvent.click(screen.getByText("جدولة ري"));
    expect(screen.getByText("جدولة ري جديدة")).toBeInTheDocument();

    fireEvent.click(screen.getByText("إلغاء"));
    expect(screen.queryByText("جدولة ري جديدة")).not.toBeInTheDocument();
  });

  it("should show delete confirmation dialog", () => {
    render(<IrrigationClient />);

    // Find all delete buttons and click the first one
    const deleteButtons = screen.getAllByTitle("حذف");
    fireEvent.click(deleteButtons[0]);

    expect(screen.getByText("حذف جدول الري")).toBeInTheDocument();
    expect(screen.getByText(/هل أنت متأكد/)).toBeInTheDocument();
  });

  it("should filter by status", () => {
    render(<IrrigationClient />);

    const statusFilter = screen.getByLabelText("تصفية حسب الحالة");
    fireEvent.change(statusFilter, { target: { value: "completed" } });

    expect(screen.getByText("حقل القمح")).toBeInTheDocument();
    // Other non-completed schedules should be filtered out
    expect(screen.queryByText("بستان النخيل")).not.toBeInTheDocument();
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '../../../../__tests__/test-utils';
import IrrigationClient from '../IrrigationClient';

// Mock the API client
vi.mock('@/lib/api/client', () => ({
  apiClient: {
    getFields: vi.fn().mockResolvedValue({ success: true, data: [] }),
    getIrrigationSchedules: vi.fn().mockResolvedValue({ success: false }),
    createIrrigationSchedule: vi.fn().mockResolvedValue({
      success: true,
      data: {
        id: 'new-1',
        fieldId: 'field-new',
        name: 'ري جديد',
        type: 'scheduled',
        status: 'active',
        startDate: new Date().toISOString(),
        frequency: 'daily',
        duration: 60,
        waterAmount: 100,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    }),
    updateIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
    deleteIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
    startIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
    stopIrrigationSchedule: vi.fn().mockResolvedValue({ success: true }),
  },
}));

// Mock the toast
vi.mock('@/components/ui/toast', () => ({
  useToast: () => ({
    showToast: vi.fn(),
  }),
}));

// Mock the auth store
vi.mock('@/stores/auth.store', () => ({
  useAuth: () => ({
    user: { id: 'test-user', tenant_id: 'test-tenant-id' },
  }),
}));

describe('IrrigationClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the irrigation management page', () => {
    render(<IrrigationClient />);
    expect(screen.getByText('إدارة الري')).toBeInTheDocument();
  });

  it('should display stat cards', () => {
    render(<IrrigationClient />);
    expect(screen.getByText('إجمالي الري المخطط')).toBeInTheDocument();
    expect(screen.getByText('نشط الآن')).toBeInTheDocument();
    expect(screen.getAllByText('متوقف').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('كفاءة الري')).toBeInTheDocument();
  });

  it('should display table headers', () => {
    render(<IrrigationClient />);
    expect(screen.getByText('الاسم')).toBeInTheDocument();
    expect(screen.getByText('النوع')).toBeInTheDocument();
    expect(screen.getByText('التكرار')).toBeInTheDocument();
    expect(screen.getByText('تاريخ البدء')).toBeInTheDocument();
    expect(screen.getByText('كمية المياه')).toBeInTheDocument();
    expect(screen.getByText('الحالة')).toBeInTheDocument();
  });

  it('should display mock schedule data on load', () => {
    render(<IrrigationClient />);
    expect(screen.getByText('ري صباحي - الحقل الشمالي')).toBeInTheDocument();
    expect(screen.getByText('ري محوري - الحقل الجنوبي')).toBeInTheDocument();
    expect(screen.getByText('ري رشاشات - حقل القمح')).toBeInTheDocument();
  });

  it('should show paused alert when paused schedules exist', () => {
    render(<IrrigationClient />);
    expect(screen.getByText(/جدول ري متوقف/)).toBeInTheDocument();
  });

  it('should filter schedules by search term', () => {
    render(<IrrigationClient />);

    const searchInput = screen.getByPlaceholderText('بحث عن حقل أو جدول...');
    fireEvent.change(searchInput, { target: { value: 'القمح' } });

    expect(screen.getByText('ري رشاشات - حقل القمح')).toBeInTheDocument();
    expect(screen.queryByText('ري صباحي - الحقل الشمالي')).not.toBeInTheDocument();
  });

  it('should open create modal on button click', () => {
    render(<IrrigationClient />);

    const createBtn = screen.getByText('جدولة ري');
    fireEvent.click(createBtn);

    expect(screen.getByText('جدولة ري جديدة')).toBeInTheDocument();
    expect(screen.getByText(/اسم الجدول/)).toBeInTheDocument();
    expect(screen.getByText('نوع الجدولة')).toBeInTheDocument();
  });

  it('should close modal on cancel', () => {
    render(<IrrigationClient />);

    fireEvent.click(screen.getByText('جدولة ري'));
    expect(screen.getByText('جدولة ري جديدة')).toBeInTheDocument();

    fireEvent.click(screen.getByText('إلغاء'));
    expect(screen.queryByText('جدولة ري جديدة')).not.toBeInTheDocument();
  });

  it('should show delete confirmation dialog', () => {
    render(<IrrigationClient />);

    // Find all delete buttons and click the first one
    const deleteButtons = screen.getAllByTitle('حذف');
    fireEvent.click(deleteButtons[0]);

    expect(screen.getByText('حذف جدول الري')).toBeInTheDocument();
    expect(screen.getByText(/هل أنت متأكد/)).toBeInTheDocument();
  });

  it('should filter by status', () => {
    render(<IrrigationClient />);

    const statusFilter = screen.getByLabelText('تصفية حسب الحالة');
    fireEvent.change(statusFilter, { target: { value: 'completed' } });

    expect(screen.getByText('ري رشاشات - حقل القمح')).toBeInTheDocument();
    // Other non-completed schedules should be filtered out
    expect(screen.queryByText('ري يدوي - بستان النخيل')).not.toBeInTheDocument();
  });
});

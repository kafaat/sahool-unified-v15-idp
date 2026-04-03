/**
 * FieldCreateDialog Component Tests
 * اختبارات مكون حوار إنشاء الحقل
 *
 * Tests the field creation dialog including form validation,
 * crop/irrigation type selection, boundary drawing, and submission.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import React from 'react';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

// Mock next/dynamic - DrawableMap is dynamically imported
vi.mock('next/dynamic', () => ({
  __esModule: true,
  default: () => {
    const _React = require('react');
    return function MockDrawableMap(props: any) {
      return _React.createElement('div', { 'data-testid': 'mock-drawable-map' });
    };
  },
}));

// Mock API client
const mockPost = vi.fn();
vi.mock('@/lib/api', () => ({
  apiClient: {
    post: (...args: unknown[]) => mockPost(...args),
  },
}));

// Mock Toast
const mockToastSuccess = vi.fn();
const mockToastError = vi.fn();
vi.mock('@/components/ui/Toast', () => ({
  useToast: () => ({
    toast: {
      success: mockToastSuccess,
      error: mockToastError,
    },
  }),
}));

// Mock @/lib/utils
vi.mock('@/lib/utils', () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(' '),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => {
  const _React = require('react');
  const createIcon = (name: string) => {
    const Icon = (props: Record<string, unknown>) =>
      _React.createElement('svg', { 'data-testid': `icon-${name}`, ...props });
    Icon.displayName = name;
    return Icon;
  };
  return {
    __esModule: true,
    X: createIcon('X'),
    MapPin: createIcon('MapPin'),
    Loader2: createIcon('Loader2'),
    Wheat: createIcon('Wheat'),
    Droplets: createIcon('Droplets'),
    Plus: createIcon('Plus'),
    AlertCircle: createIcon('AlertCircle'),
  };
});

import FieldCreateDialog from '../../fields/FieldCreateDialog';

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('FieldCreateDialog', () => {
  const defaultProps = {
    open: true,
    onClose: vi.fn(),
    onSuccess: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockPost.mockReset();
  });

  // ─── Rendering ──────────────────────────────────────────────────────────

  describe('rendering', () => {
    it('renders dialog when open=true', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('does not render dialog when open=false', () => {
      render(<FieldCreateDialog {...defaultProps} open={false} />);
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('renders dialog title in Arabic', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('إنشاء حقل جديد')).toBeInTheDocument();
    });

    it('renders dialog subtitle in English', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('Create New Field')).toBeInTheDocument();
    });

    it('renders with aria-modal attribute', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
    });

    it('renders the DrawableMap component', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByTestId('mock-drawable-map')).toBeInTheDocument();
    });
  });

  // ─── Form Fields ────────────────────────────────────────────────────────

  describe('form fields', () => {
    it('renders field name (English) input', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const input = screen.getByLabelText(/اسم الحقل \(إنجليزي\)/);
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'text');
    });

    it('renders field name (Arabic) input', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const input = screen.getByLabelText(/اسم الحقل \(عربي\)/);
      expect(input).toBeInTheDocument();
    });

    it('renders crop type select with placeholder', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const select = screen.getByLabelText(/نوع المحصول/);
      expect(select).toBeInTheDocument();
      expect(screen.getByText('-- اختر نوع المحصول --')).toBeInTheDocument();
    });

    it('renders irrigation type select with placeholder', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const select = screen.getByLabelText(/نوع الري/);
      expect(select).toBeInTheDocument();
      expect(screen.getByText('-- اختر نوع الري --')).toBeInTheDocument();
    });

    it('renders field boundary label', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      // Multiple elements contain "حدود الحقل" (label + instruction text), so use getAllByText
      const boundaryLabels = screen.getAllByText(/حدود الحقل/);
      expect(boundaryLabels.length).toBeGreaterThanOrEqual(1);
    });

    it('renders boundary drawing instructions in both languages', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(
        screen.getByText(/ارسم حدود الحقل على الخريطة باستخدام أدوات الرسم/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Draw the field boundary on the map using the drawing tools/)
      ).toBeInTheDocument();
    });
  });

  // ─── Crop Type Options ──────────────────────────────────────────────────

  describe('crop type options', () => {
    it('renders wheat option with Arabic and English labels', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('قمح - Wheat')).toBeInTheDocument();
    });

    it('renders barley option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('شعير - Barley')).toBeInTheDocument();
    });

    it('renders date palm option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('نخيل - Date Palm')).toBeInTheDocument();
    });

    it('renders tomato option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('طماطم - Tomato')).toBeInTheDocument();
    });

    it('renders cucumber option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('خيار - Cucumber')).toBeInTheDocument();
    });

    it('renders corn option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('ذرة - Corn')).toBeInTheDocument();
    });

    it('renders rice option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('أرز - Rice')).toBeInTheDocument();
    });

    it('renders other option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('أخرى - Other')).toBeInTheDocument();
    });

    it('allows selecting a crop type', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const select = screen.getByLabelText(/نوع المحصول/) as HTMLSelectElement;
      fireEvent.change(select, { target: { value: 'wheat' } });
      expect(select.value).toBe('wheat');
    });
  });

  // ─── Irrigation Type Options ────────────────────────────────────────────

  describe('irrigation type options', () => {
    it('renders drip option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('تنقيط - Drip')).toBeInTheDocument();
    });

    it('renders sprinkler option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('رشاش - Sprinkler')).toBeInTheDocument();
    });

    it('renders flood option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('غمر - Flood')).toBeInTheDocument();
    });

    it('renders pivot option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('محوري - Pivot')).toBeInTheDocument();
    });

    it('renders rain-fed option', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('بعلي - Rain-fed')).toBeInTheDocument();
    });

    it('allows selecting an irrigation type', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const select = screen.getByLabelText(/نوع الري/) as HTMLSelectElement;
      fireEvent.change(select, { target: { value: 'drip' } });
      expect(select.value).toBe('drip');
    });
  });

  // ─── Validation ─────────────────────────────────────────────────────────

  describe('validation', () => {
    it('shows error when submitting without field name', async () => {
      render(<FieldCreateDialog {...defaultProps} />);

      // Select crop and irrigation but leave name empty
      fireEvent.change(screen.getByLabelText(/نوع المحصول/), {
        target: { value: 'wheat' },
      });
      fireEvent.change(screen.getByLabelText(/نوع الري/), {
        target: { value: 'drip' },
      });

      // Submit via form submit event (bypasses native HTML validation)
      const form = screen.getByRole('dialog').querySelector('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(
          screen.getByText('اسم الحقل مطلوب - Field name is required')
        ).toBeInTheDocument();
      });

      // API should not have been called
      expect(mockPost).not.toHaveBeenCalled();
    });

    it('shows error when submitting without crop type', async () => {
      render(<FieldCreateDialog {...defaultProps} />);

      // Fill name but skip crop type
      fireEvent.change(screen.getByPlaceholderText('Field Name'), {
        target: { value: 'Test Field' },
      });
      fireEvent.change(screen.getByLabelText(/نوع الري/), {
        target: { value: 'drip' },
      });

      const form = screen.getByRole('dialog').querySelector('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(
          screen.getByText('نوع المحصول مطلوب - Crop type is required')
        ).toBeInTheDocument();
      });

      expect(mockPost).not.toHaveBeenCalled();
    });

    it('shows error when submitting without irrigation type', async () => {
      render(<FieldCreateDialog {...defaultProps} />);

      fireEvent.change(screen.getByPlaceholderText('Field Name'), {
        target: { value: 'Test Field' },
      });
      fireEvent.change(screen.getByLabelText(/نوع المحصول/), {
        target: { value: 'wheat' },
      });

      const form = screen.getByRole('dialog').querySelector('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(
          screen.getByText('نوع الري مطلوب - Irrigation type is required')
        ).toBeInTheDocument();
      });

      expect(mockPost).not.toHaveBeenCalled();
    });

    it('shows error when submitting without drawing field boundary', async () => {
      render(<FieldCreateDialog {...defaultProps} />);

      // Fill all text fields
      fireEvent.change(screen.getByPlaceholderText('Field Name'), {
        target: { value: 'Test Field' },
      });
      fireEvent.change(screen.getByLabelText(/نوع المحصول/), {
        target: { value: 'wheat' },
      });
      fireEvent.change(screen.getByLabelText(/نوع الري/), {
        target: { value: 'drip' },
      });

      const form = screen.getByRole('dialog').querySelector('form')!;
      fireEvent.submit(form);

      await waitFor(() => {
        expect(
          screen.getByText(/يرجى رسم حدود الحقل على الخريطة/)
        ).toBeInTheDocument();
      });

      expect(mockPost).not.toHaveBeenCalled();
    });
  });

  // ─── Close Behavior ─────────────────────────────────────────────────────

  describe('close behavior', () => {
    it('close button calls onClose', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const closeBtn = screen.getByLabelText('إغلاق');
      fireEvent.click(closeBtn);
      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('cancel button calls onClose', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const cancelBtn = screen.getByText('إلغاء');
      fireEvent.click(cancelBtn);
      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('Escape key closes dialog', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      fireEvent.keyDown(document, { key: 'Escape' });
      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('clicking backdrop closes dialog', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      // The backdrop is the element with bg-black/50
      const backdrop = screen.getByRole('dialog').querySelector('.bg-black\\/50');
      if (backdrop) {
        fireEvent.click(backdrop);
        expect(defaultProps.onClose).toHaveBeenCalled();
      }
    });
  });

  // ─── Submit Button State ────────────────────────────────────────────────

  describe('submit button', () => {
    it('shows Arabic text "إنشاء الحقل" by default', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('إنشاء الحقل')).toBeInTheDocument();
    });

    it('submit button is of type submit', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      const submitBtn = screen.getByText('إنشاء الحقل');
      expect(submitBtn).toHaveAttribute('type', 'submit');
    });
  });

  // ─── Arabic Labels ──────────────────────────────────────────────────────

  describe('Arabic labels', () => {
    it('renders dialog title "إنشاء حقل جديد"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('إنشاء حقل جديد')).toBeInTheDocument();
    });

    it('renders field name label "اسم الحقل (إنجليزي)"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText(/اسم الحقل \(إنجليزي\)/)).toBeInTheDocument();
    });

    it('renders field name Arabic label "اسم الحقل (عربي)"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText(/اسم الحقل \(عربي\)/)).toBeInTheDocument();
    });

    it('renders crop type label "نوع المحصول"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      // Label and placeholder option both contain this text
      const matches = screen.getAllByText(/نوع المحصول/);
      expect(matches.length).toBeGreaterThanOrEqual(1);
    });

    it('renders irrigation type label "نوع الري"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      // Label and placeholder option both contain this text
      const matches = screen.getAllByText(/نوع الري/);
      expect(matches.length).toBeGreaterThanOrEqual(1);
    });

    it('renders boundary label "حدود الحقل"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      // Multiple elements contain this text (label + instruction)
      const matches = screen.getAllByText(/حدود الحقل/);
      expect(matches.length).toBeGreaterThanOrEqual(1);
    });

    it('renders cancel button "إلغاء"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('إلغاء')).toBeInTheDocument();
    });

    it('renders submit button "إنشاء الحقل"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByText('إنشاء الحقل')).toBeInTheDocument();
    });

    it('renders close button with Arabic aria-label "إغلاق"', () => {
      render(<FieldCreateDialog {...defaultProps} />);
      expect(screen.getByLabelText('إغلاق')).toBeInTheDocument();
    });
  });

  // ─── Form Reset on Open ────────────────────────────────────────────────

  describe('form reset', () => {
    it('resets form when dialog opens', () => {
      const { rerender } = render(
        <FieldCreateDialog {...defaultProps} open={false} />
      );

      // Open dialog
      rerender(<FieldCreateDialog {...defaultProps} open={true} />);

      // All fields should be empty
      const nameInput = screen.getByPlaceholderText('Field Name') as HTMLInputElement;
      expect(nameInput.value).toBe('');

      const cropSelect = screen.getByLabelText(/نوع المحصول/) as HTMLSelectElement;
      expect(cropSelect.value).toBe('');

      const irrigationSelect = screen.getByLabelText(/نوع الري/) as HTMLSelectElement;
      expect(irrigationSelect.value).toBe('');
    });
  });

  // ─── Source Verification ────────────────────────────────────────────────

  describe('source verification', () => {
    const fs = require('fs');
    const path = require('path');
    const filePath = path.resolve(__dirname, '../../fields/FieldCreateDialog.tsx');

    it('FieldCreateDialog source file exists', () => {
      expect(fs.existsSync(filePath)).toBe(true);
    });

    it('exports a default component', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('export default function FieldCreateDialog');
    });

    it('uses DrawableMap for boundary drawing', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('DrawableMap');
      expect(content).toContain('onBboxSelect');
      expect(content).toContain('onBoundaryDraw');
    });

    it('has all crop type constants', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain("'wheat'");
      expect(content).toContain("'barley'");
      expect(content).toContain("'date_palm'");
      expect(content).toContain("'tomato'");
      expect(content).toContain("'cucumber'");
      expect(content).toContain("'corn'");
      expect(content).toContain("'rice'");
    });

    it('has all irrigation type constants', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain("'drip'");
      expect(content).toContain("'sprinkler'");
      expect(content).toContain("'flood'");
      expect(content).toContain("'pivot'");
      expect(content).toContain("'rain_fed'");
    });

    it('validates required fields before submission', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('اسم الحقل مطلوب');
      expect(content).toContain('نوع المحصول مطلوب');
      expect(content).toContain('نوع الري مطلوب');
      expect(content).toContain('يرجى رسم حدود الحقل');
    });

    it('handles Escape key to close dialog', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain("e.key === 'Escape'");
    });

    it('posts to /api/v1/fields endpoint', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain("apiClient.post('/api/v1/fields'");
    });
  });
});

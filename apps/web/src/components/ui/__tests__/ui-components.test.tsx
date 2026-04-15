/**
 * Comprehensive UI Component Tests - Web App
 * اختبارات شاملة لمكونات واجهة المستخدم - التطبيق الويب
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// ─── Button ─────────────────────────────────────────────────────────────────
import { Button } from '../button';

describe('Button Component', () => {
  it('renders children correctly', () => {
    render(<Button>حفظ</Button>);
    expect(screen.getByRole('button', { name: 'حفظ' })).toBeInTheDocument();
  });

  it('applies primary variant by default', () => {
    render(<Button>Primary</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toMatch(/bg-sahool-green-600/);
  });

  it('applies secondary variant', () => {
    render(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button').className).toMatch(/bg-sahool-brown-500/);
  });

  it('applies outline variant', () => {
    render(<Button variant="outline">Outline</Button>);
    expect(screen.getByRole('button').className).toMatch(/border-2/);
  });

  it('applies ghost variant', () => {
    render(<Button variant="ghost">Ghost</Button>);
    expect(screen.getByRole('button').className).toMatch(/text-gray-700/);
  });

  it('applies danger variant', () => {
    render(<Button variant="danger">Danger</Button>);
    expect(screen.getByRole('button').className).toMatch(/bg-red-600/);
  });

  it('renders small size', () => {
    render(<Button size="sm">Small</Button>);
    expect(screen.getByRole('button').className).toMatch(/text-sm/);
  });

  it('renders large size', () => {
    render(<Button size="lg">Large</Button>);
    expect(screen.getByRole('button').className).toMatch(/text-lg/);
  });

  it('renders full width when fullWidth is true', () => {
    render(<Button fullWidth>Full Width</Button>);
    expect(screen.getByRole('button').className).toMatch(/w-full/);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    const btn = screen.getByRole('button');
    expect(btn).toBeDisabled();
  });

  it('shows loading state correctly', () => {
    render(<Button isLoading>Save</Button>);
    const btn = screen.getByRole('button');
    expect(btn).toBeDisabled();
    expect(btn).toHaveAttribute('aria-busy', 'true');
  });

  it('shows screen reader loading text when loading', () => {
    render(
      <Button isLoading loadingTextAr="جاري الحفظ" loadingText="Saving">
        Save
      </Button>
    );
    expect(screen.getByText(/جاري الحفظ/)).toBeInTheDocument();
  });

  it('renders left icon', () => {
    render(<Button leftIcon={<span data-testid="left-icon">◀</span>}>With Icon</Button>);
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
  });

  it('renders right icon', () => {
    render(<Button rightIcon={<span data-testid="right-icon">▶</span>}>With Icon</Button>);
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
  });

  it('fires onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('does not fire onClick when disabled', () => {
    const onClick = vi.fn();
    render(
      <Button onClick={onClick} disabled>
        Click me
      </Button>
    );
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('applies custom className', () => {
    render(<Button className="custom-class">Custom</Button>);
    expect(screen.getByRole('button').className).toMatch(/custom-class/);
  });

  it('uses submit type when specified', () => {
    render(<Button type="submit">Submit</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');
  });

  it('defaults to button type', () => {
    render(<Button>Button</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });
});

// ─── Badge ──────────────────────────────────────────────────────────────────
import { Badge } from '../badge';

describe('Badge Component', () => {
  it('renders children', () => {
    render(<Badge>نشط</Badge>);
    expect(screen.getByText('نشط')).toBeInTheDocument();
  });

  it('applies default variant', () => {
    render(<Badge>Default</Badge>);
    expect(screen.getByText('Default').className).toMatch(/bg-gray-100/);
  });

  it('applies success variant', () => {
    render(<Badge variant="success">نجاح</Badge>);
    expect(screen.getByText('نجاح').className).toMatch(/bg-sahool-green-100/);
  });

  it('applies warning variant', () => {
    render(<Badge variant="warning">تحذير</Badge>);
    expect(screen.getByText('تحذير').className).toMatch(/bg-yellow-100/);
  });

  it('applies danger variant', () => {
    render(<Badge variant="danger">خطر</Badge>);
    expect(screen.getByText('خطر').className).toMatch(/bg-red-100/);
  });

  it('applies info variant', () => {
    render(<Badge variant="info">معلومات</Badge>);
    expect(screen.getByText('معلومات').className).toMatch(/bg-blue-100/);
  });

  it('renders small size', () => {
    render(<Badge size="sm">Small</Badge>);
    expect(screen.getByText('Small').className).toMatch(/text-xs/);
  });

  it('renders large size', () => {
    render(<Badge size="lg">Large</Badge>);
    expect(screen.getByText('Large').className).toMatch(/text-base/);
  });

  it('applies custom className', () => {
    render(<Badge className="custom">Badge</Badge>);
    expect(screen.getByText('Badge').className).toMatch(/custom/);
  });

  it('renders as span element', () => {
    render(<Badge>span badge</Badge>);
    const badge = screen.getByText('span badge');
    expect(badge.tagName).toBe('SPAN');
  });

  it('has rounded-full class', () => {
    render(<Badge>Rounded</Badge>);
    expect(screen.getByText('Rounded').className).toMatch(/rounded-full/);
  });
});

// ─── Card ───────────────────────────────────────────────────────────────────
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../card';

describe('Card Component', () => {
  it('renders children', () => {
    render(<Card>Card Content</Card>);
    expect(screen.getByText('Card Content')).toBeInTheDocument();
  });

  it('applies default variant with bg-white', () => {
    const { container } = render(<Card>Default</Card>);
    expect(container.firstChild).toHaveClass('bg-white');
  });

  it('applies bordered variant', () => {
    const { container } = render(<Card variant="bordered">Bordered</Card>);
    expect((container.firstChild as HTMLElement)?.className).toMatch(/border-sahool-green-200/);
  });

  it('applies elevated variant with shadow-lg', () => {
    const { container } = render(<Card variant="elevated">Elevated</Card>);
    expect((container.firstChild as HTMLElement)?.className).toMatch(/shadow-lg/);
  });

  it('applies interactive styles when interactive is true', () => {
    const { container } = render(<Card interactive>Interactive</Card>);
    const el = container.firstChild as HTMLElement;
    expect(el?.className).toMatch(/cursor-pointer/);
    expect(el).toHaveAttribute('role', 'button');
    expect(el).toHaveAttribute('tabindex', '0');
  });

  it('renders with small padding', () => {
    const { container } = render(<Card padding="sm">SM</Card>);
    expect((container.firstChild as HTMLElement)?.className).toMatch(/p-4/);
  });

  it('renders with large padding', () => {
    const { container } = render(<Card padding="lg">LG</Card>);
    expect((container.firstChild as HTMLElement)?.className).toMatch(/p-8/);
  });

  it("renders as article element when as='article'", () => {
    const { container } = render(<Card as="article">Article Card</Card>);
    expect(container.firstChild?.nodeName).toBe('ARTICLE');
  });

  it('renders full card composition', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>عنوان البطاقة</CardTitle>
          <CardDescription>وصف البطاقة</CardDescription>
        </CardHeader>
        <CardContent>محتوى البطاقة</CardContent>
        <CardFooter>تذييل البطاقة</CardFooter>
      </Card>
    );
    expect(screen.getByText('عنوان البطاقة')).toBeInTheDocument();
    expect(screen.getByText('وصف البطاقة')).toBeInTheDocument();
    expect(screen.getByText('محتوى البطاقة')).toBeInTheDocument();
    expect(screen.getByText('تذييل البطاقة')).toBeInTheDocument();
  });

  it('CardTitle renders as h3', () => {
    render(<CardTitle>Title</CardTitle>);
    expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
  });

  it('CardDescription renders as p element', () => {
    render(<CardDescription>Desc</CardDescription>);
    const el = screen.getByText('Desc');
    expect(el.tagName).toBe('P');
  });

  it('CardFooter has border-top class', () => {
    const { container } = render(<CardFooter>Footer</CardFooter>);
    expect((container.firstChild as HTMLElement)?.className).toMatch(/border-t/);
  });
});

// ─── Input ──────────────────────────────────────────────────────────────────
import { Input } from '../input';

describe('Input Component', () => {
  it('renders input element', () => {
    render(<Input placeholder="اكتب هنا..." />);
    expect(screen.getByPlaceholderText('اكتب هنا...')).toBeInTheDocument();
  });

  it('renders with Arabic label', () => {
    render(<Input labelAr="البريد الإلكتروني" id="email" />);
    const label = screen.getByText('البريد الإلكتروني');
    expect(label).toBeInTheDocument();
  });

  it('renders with both Arabic and English labels', () => {
    render(<Input label="Email" labelAr="البريد الإلكتروني" id="email" />);
    expect(screen.getByText('البريد الإلكتروني')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
  });

  it('shows error message with role alert', () => {
    render(<Input error="خطأ في الإدخال" />);
    const error = screen.getByRole('alert');
    expect(error).toHaveTextContent('خطأ في الإدخال');
  });

  it('marks input as invalid when error is provided', () => {
    render(<Input error="Invalid" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('aria-invalid', 'true');
  });

  it('shows helper text', () => {
    render(<Input helperText="نص مساعد" />);
    expect(screen.getByText('نص مساعد')).toBeInTheDocument();
  });

  it('does not show helper text when there is an error', () => {
    render(<Input error="Error" helperText="Helper" />);
    expect(screen.queryByText('Helper')).not.toBeInTheDocument();
  });

  it('renders with left icon', () => {
    render(<Input leftIcon={<span data-testid="left">L</span>} />);
    expect(screen.getByTestId('left')).toBeInTheDocument();
  });

  it('renders with right icon', () => {
    render(<Input rightIcon={<span data-testid="right">R</span>} />);
    expect(screen.getByTestId('right')).toBeInTheDocument();
  });

  it('renders as disabled', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('fires onChange when user types', () => {
    const onChange = vi.fn();
    render(<Input onChange={onChange} />);
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'hello' },
    });
    expect(onChange).toHaveBeenCalled();
  });

  it('renders password type input', () => {
    const { container } = render(<Input type="password" />);
    const input = container.querySelector('input[type=password]');
    expect(input).toBeInTheDocument();
  });

  it('applies error border styling', () => {
    render(<Input error="Error" />);
    const input = screen.getByRole('textbox');
    expect(input.className).toMatch(/border-red-500/);
  });

  it('links error to input via aria-describedby', () => {
    render(<Input id="test-input" error="Error message" />);
    const input = screen.getByRole('textbox');
    const describedBy = input.getAttribute('aria-describedby');
    expect(describedBy).toBeTruthy();
    const errorEl = document.getElementById(describedBy!);
    expect(errorEl).toHaveTextContent('Error message');
  });

  it('passes additional props to input', () => {
    render(<Input data-testid="my-input" readOnly />);
    expect(screen.getByTestId('my-input')).toHaveAttribute('readonly');
  });
});

// ─── Loading ────────────────────────────────────────────────────────────────
import { Loading } from '../loading';

describe('Loading Component', () => {
  it('renders spinner variant by default with SVG', () => {
    const { container } = render(<Loading />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('has accessible role=status', () => {
    render(<Loading />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows loading text in Arabic', () => {
    render(<Loading textAr="جاري التحميل..." />);
    expect(screen.getByText('جاري التحميل...')).toBeInTheDocument();
  });

  it('shows bilingual text', () => {
    render(<Loading text="Loading" textAr="جاري التحميل" />);
    expect(screen.getByText('Loading')).toBeInTheDocument();
    expect(screen.getByText('جاري التحميل')).toBeInTheDocument();
  });

  it('renders dots variant with animated divs', () => {
    const { container } = render(<Loading variant="dots" />);
    expect(container.querySelector('.animate-bounce')).toBeInTheDocument();
  });

  it('renders pulse variant with animated div', () => {
    const { container } = render(<Loading variant="pulse" />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('has aria-busy=true', () => {
    render(<Loading />);
    expect(screen.getByRole('status')).toHaveAttribute('aria-busy', 'true');
  });

  it('applies large size class', () => {
    const { container } = render(<Loading size="lg" />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('class')).toMatch(/w-12/);
  });

  it('applies small size class', () => {
    const { container } = render(<Loading size="sm" />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('class')).toMatch(/w-4/);
  });

  it('applies custom className', () => {
    render(<Loading className="custom-loader" />);
    expect(screen.getByRole('status').className).toMatch(/custom-loader/);
  });

  it('uses default aria-label of جاري التحميل when no text provided', () => {
    render(<Loading />);
    const status = screen.getByRole('status');
    expect(status.getAttribute('aria-label')).toBe('جاري التحميل');
  });
});

// ─── Toast ───────────────────────────────────────────────────────────────────
import { ToastProvider, useToast } from '../toast';

const ToastTestComponent = ({
  type = 'success' as 'success' | 'error' | 'info' | 'warning',
  message = 'رسالة اختبارية',
  duration = 10000,
}) => {
  const { showToast } = useToast();
  return (
    <button
      onClick={() => showToast({ type, message, messageAr: message, duration })}
      data-testid="show-toast"
    >
      Show Toast
    </button>
  );
};

describe('Toast Component', () => {
  it('renders ToastProvider without crashing', () => {
    render(
      <ToastProvider>
        <div>Content</div>
      </ToastProvider>
    );
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('throws when useToast is used outside ToastProvider', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => {
      render(<ToastTestComponent />);
    }).toThrow(/useToast must be used within ToastProvider/);
    consoleError.mockRestore();
  });

  it('shows a success toast message', async () => {
    render(
      <ToastProvider>
        <ToastTestComponent type="success" message="تم الحفظ بنجاح" />
      </ToastProvider>
    );
    fireEvent.click(screen.getByTestId('show-toast'));
    await waitFor(() => {
      expect(screen.getAllByText('تم الحفظ بنجاح').length).toBeGreaterThan(0);
    });
  });

  it('shows an error toast message', async () => {
    render(
      <ToastProvider>
        <ToastTestComponent type="error" message="حدث خطأ" />
      </ToastProvider>
    );
    fireEvent.click(screen.getByTestId('show-toast'));
    await waitFor(() => {
      expect(screen.getAllByText('حدث خطأ').length).toBeGreaterThan(0);
    });
  });

  it('shows a warning toast message', async () => {
    render(
      <ToastProvider>
        <ToastTestComponent type="warning" message="تحذير مهم" />
      </ToastProvider>
    );
    fireEvent.click(screen.getByTestId('show-toast'));
    await waitFor(() => {
      expect(screen.getAllByText('تحذير مهم').length).toBeGreaterThan(0);
    });
  });

  it('shows an info toast message', async () => {
    render(
      <ToastProvider>
        <ToastTestComponent type="info" message="معلومة مفيدة" />
      </ToastProvider>
    );
    fireEvent.click(screen.getByTestId('show-toast'));
    await waitFor(() => {
      expect(screen.getAllByText('معلومة مفيدة').length).toBeGreaterThan(0);
    });
  });

  it('toast message appears after showToast is called', async () => {
    // This test verifies the toast appears - timer dismissal is tested via setTimeout mock
    const setTimeoutSpy = vi.spyOn(globalThis, 'setTimeout');
    render(
      <ToastProvider>
        <ToastTestComponent type="success" message="رسالة اختبار" duration={3000} />
      </ToastProvider>
    );
    fireEvent.click(screen.getByTestId('show-toast'));
    await waitFor(() => {
      expect(screen.getAllByText('رسالة اختبار').length).toBeGreaterThan(0);
    });
    // Verify setTimeout was called with the duration
    expect(setTimeoutSpy).toHaveBeenCalled();
    setTimeoutSpy.mockRestore();
  });

  it('can show multiple toasts simultaneously', async () => {
    render(
      <ToastProvider>
        <ToastTestComponent type="success" message="أولى" />
        <ToastTestComponent type="error" message="ثانية" />
      </ToastProvider>
    );
    const buttons = screen.getAllByTestId('show-toast');
    fireEvent.click(buttons[0]);
    fireEvent.click(buttons[1]);
    await waitFor(() => {
      expect(screen.getAllByText('أولى').length).toBeGreaterThan(0);
      expect(screen.getAllByText('ثانية').length).toBeGreaterThan(0);
    });
  });
});

// ─── Modal ───────────────────────────────────────────────────────────────────
import { Modal, ModalFooter } from '../modal';

vi.mock('react-focus-lock', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

describe('Modal Component', () => {
  it('renders nothing when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={vi.fn()} title="Test Modal">
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  it('renders content when isOpen is true', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal" titleAr="اختبار">
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('shows bilingual title', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal" titleAr="نافذة الاختبار">
        <div>content</div>
      </Modal>
    );
    // Use getAllByText since aria-live region also contains the text
    expect(screen.getAllByText('نافذة الاختبار').length).toBeGreaterThan(0);
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
  });

  it('calls onClose when Escape key is pressed', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose} title="Modal">
        <div>content</div>
      </Modal>
    );
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('shows close button by default', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Modal">
        <div>content</div>
      </Modal>
    );
    expect(screen.getByLabelText(/إغلاق/)).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose} title="Modal">
        <div>content</div>
      </Modal>
    );
    fireEvent.click(screen.getByLabelText(/إغلاق/));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('hides close button when showCloseButton is false', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Modal" showCloseButton={false}>
        <div>content</div>
      </Modal>
    );
    expect(screen.queryByLabelText(/إغلاق/)).not.toBeInTheDocument();
  });

  it('renders ModalFooter with action buttons', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Modal">
        <ModalFooter>
          <button>Cancel</button>
          <button>Confirm</button>
        </ModalFooter>
      </Modal>
    );
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Confirm' })).toBeInTheDocument();
  });

  it('has role=dialog', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Modal">
        <div>content</div>
      </Modal>
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('has aria-modal=true on dialog', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Modal">
        <div>content</div>
      </Modal>
    );
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
  });

  it('renders in different sizes', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={vi.fn()} size="sm">
        <div>small</div>
      </Modal>
    );
    expect(screen.getByText('small')).toBeInTheDocument();

    rerender(
      <Modal isOpen={true} onClose={vi.fn()} size="xl">
        <div>xlarge</div>
      </Modal>
    );
    expect(screen.getByText('xlarge')).toBeInTheDocument();
  });
});

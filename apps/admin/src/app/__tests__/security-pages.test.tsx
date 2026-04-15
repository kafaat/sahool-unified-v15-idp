/**
 * Security Pages Tests - Admin Application
 * اختبارات صفحات الأمان - تطبيق الإدارة
 *
 * Verifies that security-related pages render correctly,
 * contain expected form fields, and do NOT expose demo credentials.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn().mockResolvedValue(undefined),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/login',
}));

// Mock next/link as a plain anchor
vi.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    ...rest
  }: {
    children: React.ReactNode;
    href: string;
    [key: string]: unknown;
  }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));

// Mock auth store
vi.mock('@/stores/auth.store', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    checkAuth: vi.fn(),
  }),
}));

// Mock config/api-base
vi.mock('@/config/api-base', () => ({
  API_BASE_URL: 'http://localhost:8000',
}));

// Mock logger to avoid console noise
vi.mock('../../lib/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    critical: vi.fn(),
    debug: vi.fn(),
  },
}));

// ---------------------------------------------------------------------------
// Lazy imports (must be after vi.mock calls)
// ---------------------------------------------------------------------------

import LoginPage from '../(auth)/login/page';
import RegisterPage from '../(auth)/register/page';
import ForgotPasswordPage from '../(auth)/forgot-password/page';

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('Admin Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<LoginPage />);
    // The heading "تسجيل الدخول" should be present (also appears in button)
    expect(screen.getByRole('heading', { name: /تسجيل الدخول/ })).toBeInTheDocument();
  });

  it('displays the SAHOOL brand name', () => {
    render(<LoginPage />);
    expect(screen.getByText('سهول')).toBeInTheDocument();
  });

  it('renders an email input field', () => {
    render(<LoginPage />);
    const emailInput = screen.getByPlaceholderText('admin@sahool.io');
    expect(emailInput).toBeInTheDocument();
    expect(emailInput).toHaveAttribute('type', 'email');
  });

  it('renders a password input field', () => {
    render(<LoginPage />);
    const passwordInput = screen.getByPlaceholderText('••••••••');
    expect(passwordInput).toBeInTheDocument();
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('renders the login submit button', () => {
    render(<LoginPage />);
    const submitButton = screen.getByRole('button', { name: /تسجيل الدخول/i });
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toHaveAttribute('type', 'submit');
  });

  it('does NOT show demo credentials text (بيانات الدخول للتجربة)', () => {
    render(<LoginPage />);
    expect(screen.queryByText(/بيانات الدخول للتجربة/i)).not.toBeInTheDocument();
  });

  it('does NOT expose admin123 password anywhere on the page', () => {
    render(<LoginPage />);
    expect(screen.queryByText(/admin123/i)).not.toBeInTheDocument();
  });

  it('does NOT expose hardcoded demo email', () => {
    render(<LoginPage />);
    // Should not contain pre-filled demo email as text content
    expect(screen.queryByText('admin@sahool.io')).not.toBeInTheDocument();
  });

  it('renders a registration link', () => {
    render(<LoginPage />);
    const registerLink = screen.getByRole('link', {
      name: /إنشاء حساب جديد/i,
    });
    expect(registerLink).toBeInTheDocument();
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('renders a forgot password link', () => {
    render(<LoginPage />);
    const forgotLink = screen.getByRole('link', {
      name: /نسيت كلمة المرور/i,
    });
    expect(forgotLink).toBeInTheDocument();
    expect(forgotLink).toHaveAttribute('href', '/forgot-password');
  });

  it('has email and password labels in Arabic', () => {
    render(<LoginPage />);
    expect(screen.getByLabelText('البريد الإلكتروني')).toBeInTheDocument();
    expect(screen.getByLabelText('كلمة المرور')).toBeInTheDocument();
  });

  it('has password toggle visibility button', () => {
    render(<LoginPage />);
    const toggleButton = screen.getByRole('button', {
      name: /إظهار كلمة المرور/i,
    });
    expect(toggleButton).toBeInTheDocument();
  });
});

describe('Admin Register Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<RegisterPage />);
    expect(screen.getByText('إنشاء حساب جديد')).toBeInTheDocument();
  });

  it('displays the SAHOOL brand name', () => {
    render(<RegisterPage />);
    expect(screen.getByText('سهول')).toBeInTheDocument();
  });

  it('renders first name field', () => {
    render(<RegisterPage />);
    expect(screen.getByLabelText('الاسم الأول')).toBeInTheDocument();
  });

  it('renders last name field', () => {
    render(<RegisterPage />);
    expect(screen.getByLabelText('اسم العائلة')).toBeInTheDocument();
  });

  it('renders email field', () => {
    render(<RegisterPage />);
    expect(screen.getByLabelText('البريد الإلكتروني')).toBeInTheDocument();
  });

  it('renders password field', () => {
    render(<RegisterPage />);
    expect(screen.getByLabelText('كلمة المرور')).toBeInTheDocument();
  });

  it('renders submit button', () => {
    render(<RegisterPage />);
    const submitButton = screen.getByRole('button', { name: /إنشاء حساب/i });
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toHaveAttribute('type', 'submit');
  });

  it('renders login link for existing users', () => {
    render(<RegisterPage />);
    const loginLink = screen.getByRole('link', { name: /تسجيل الدخول/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute('href', '/login');
  });
});

describe('Admin Forgot Password Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<ForgotPasswordPage />);
    expect(screen.getByText('نسيت كلمة المرور؟')).toBeInTheDocument();
  });

  it('displays the SAHOOL brand name', () => {
    render(<ForgotPasswordPage />);
    expect(screen.getByText('سهول')).toBeInTheDocument();
  });

  it('renders email input for password recovery', () => {
    render(<ForgotPasswordPage />);
    const emailInput = screen.getByPlaceholderText('admin@sahool.io');
    expect(emailInput).toBeInTheDocument();
    expect(emailInput).toHaveAttribute('type', 'email');
  });

  it('renders recovery channel options', () => {
    render(<ForgotPasswordPage />);
    // Channel options appear as buttons with Arabic labels
    // "البريد الإلكتروني" also appears in the email input label, so use getAllByText
    expect(screen.getAllByText('البريد الإلكتروني').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('رسالة نصية')).toBeInTheDocument();
    expect(screen.getByText('واتساب')).toBeInTheDocument();
    expect(screen.getByText('تيليجرام')).toBeInTheDocument();
  });

  it('renders submit button', () => {
    render(<ForgotPasswordPage />);
    const submitButton = screen.getByRole('button', {
      name: /إرسال رابط إعادة التعيين/i,
    });
    expect(submitButton).toBeInTheDocument();
  });

  it('renders back to login link', () => {
    render(<ForgotPasswordPage />);
    const backLink = screen.getByRole('link', {
      name: /العودة لتسجيل الدخول/i,
    });
    expect(backLink).toBeInTheDocument();
    expect(backLink).toHaveAttribute('href', '/login');
  });
});

/**
 * Auth Pages Security & Render Tests - Web Application
 * اختبارات أمان وعرض صفحات المصادقة - تطبيق الويب
 *
 * Verifies that authentication pages render correctly with expected
 * form fields and do not expose sensitive information.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

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
    register: vi.fn(),
  }),
}));

// Mock toast provider
vi.mock('@/components/ui/toast', () => ({
  useToast: () => ({
    showToast: vi.fn(),
    hideToast: vi.fn(),
  }),
  ToastProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock logger
vi.mock('@/lib/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    critical: vi.fn(),
    debug: vi.fn(),
  },
}));

// ---------------------------------------------------------------------------
// Imports (after mocks)
// ---------------------------------------------------------------------------

import LoginClient from '../../(auth)/login/LoginClient';
import RegisterClient from '../../(auth)/register/RegisterClient';
import ForgotPasswordClient from '../../(auth)/forgot-password/ForgotPasswordClient';

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('Web Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<LoginClient />);
    // The page should show the login heading in Arabic
    expect(screen.getByText('تسجيل الدخول إلى سهول')).toBeInTheDocument();
  });

  it('displays the English subtitle', () => {
    render(<LoginClient />);
    expect(screen.getByText('Login to SAHOOL')).toBeInTheDocument();
  });

  it('renders a password input field', () => {
    render(<LoginClient />);
    // The password input uses the Input component with labelAr "كلمة المرور"
    expect(screen.getByText('كلمة المرور')).toBeInTheDocument();
    const passwordInput = screen.getByPlaceholderText('••••••••');
    expect(passwordInput).toBeInTheDocument();
  });

  it('renders the login submit button', () => {
    render(<LoginClient />);
    const submitButton = screen.getByRole('button', {
      name: /تسجيل الدخول.*Login/i,
    });
    expect(submitButton).toBeInTheDocument();
  });

  it('renders phone and email login method toggle', () => {
    render(<LoginClient />);
    // Toggle buttons contain phone and email labels
    // "البريد الإلكتروني" may appear multiple times (toggle + form label)
    expect(screen.getAllByText(/رقم الهاتف/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/البريد الإلكتروني/).length).toBeGreaterThanOrEqual(1);
  });

  it('renders forgot password link', () => {
    render(<LoginClient />);
    const forgotLink = screen.getByRole('link', {
      name: /نسيت كلمة المرور/i,
    });
    expect(forgotLink).toBeInTheDocument();
    expect(forgotLink).toHaveAttribute('href', '/forgot-password');
  });

  it('renders create account link', () => {
    render(<LoginClient />);
    const registerLink = screen.getByRole('link', {
      name: /إنشاء حساب جديد/i,
    });
    expect(registerLink).toBeInTheDocument();
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('does NOT expose hardcoded credentials', () => {
    render(<LoginClient />);
    expect(screen.queryByText(/admin123/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/بيانات الدخول للتجربة/i)).not.toBeInTheDocument();
  });
});

describe('Web Register Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<RegisterClient />);
    expect(screen.getByText('إنشاء حساب جديد')).toBeInTheDocument();
  });

  it('displays English subtitle', () => {
    render(<RegisterClient />);
    expect(screen.getByText('Create New Account')).toBeInTheDocument();
  });

  it('renders first and last name fields', () => {
    render(<RegisterClient />);
    expect(screen.getByText('الاسم الأول')).toBeInTheDocument();
    expect(screen.getByText('اسم العائلة')).toBeInTheDocument();
  });

  it('renders password and confirm password fields', () => {
    render(<RegisterClient />);
    // Both password fields exist
    const passwordInputs = screen.getAllByPlaceholderText('••••••••');
    expect(passwordInputs.length).toBeGreaterThanOrEqual(2);
  });

  it('renders phone and email registration method toggle', () => {
    render(<RegisterClient />);
    // Should have phone and email toggle buttons (text may appear multiple times)
    expect(screen.getAllByText(/رقم الهاتف/).length).toBeGreaterThanOrEqual(1);
  });

  it('renders submit button', () => {
    render(<RegisterClient />);
    const submitButton = screen.getByRole('button', {
      name: /إنشاء حساب.*Create Account/i,
    });
    expect(submitButton).toBeInTheDocument();
  });

  it('renders login link for existing users', () => {
    render(<RegisterClient />);
    const loginLink = screen.getByRole('link', {
      name: /تسجيل الدخول.*Login/i,
    });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('shows Yemen operator info', () => {
    render(<RegisterClient />);
    // Default method is phone, should show Yemen operator prefixes
    expect(screen.getByText(/يمن موبايل/)).toBeInTheDocument();
  });
});

describe('Web Forgot Password Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<ForgotPasswordClient />);
    expect(screen.getByText('نسيت كلمة المرور؟')).toBeInTheDocument();
  });

  it('displays English subtitle', () => {
    render(<ForgotPasswordClient />);
    expect(screen.getByText('Forgot Password?')).toBeInTheDocument();
  });

  it('renders recovery channel selector', () => {
    render(<ForgotPasswordClient />);
    expect(screen.getByText('طريقة الاسترداد')).toBeInTheDocument();
    expect(screen.getByText('Recovery Method')).toBeInTheDocument();
  });

  it('renders all four recovery channel options', () => {
    render(<ForgotPasswordClient />);
    // Channel options rendered as button text (Arabic labels + English sub-labels)
    // "Email" may appear multiple times (channel button + input label), so use getAllByText
    expect(screen.getAllByText('Email').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('SMS')).toBeInTheDocument();
    expect(screen.getByText('WhatsApp')).toBeInTheDocument();
    expect(screen.getByText('Telegram')).toBeInTheDocument();
  });

  it('renders submit button', () => {
    render(<ForgotPasswordClient />);
    const submitButton = screen.getByRole('button', {
      name: /إرسال رابط إعادة التعيين.*Send Reset Link/i,
    });
    expect(submitButton).toBeInTheDocument();
  });

  it('renders back to login link', () => {
    render(<ForgotPasswordClient />);
    const backLink = screen.getByRole('link', {
      name: /العودة لتسجيل الدخول.*Back to Login/i,
    });
    expect(backLink).toBeInTheDocument();
    expect(backLink).toHaveAttribute('href', '/login');
  });
});

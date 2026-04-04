'use client';

/**
 * SAHOOL Admin Login Page
 * صفحة تسجيل الدخول للوحة الإدارة
 */

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/stores/auth.store';
import { Loader2, Lock, Mail, Eye, EyeOff, Leaf } from 'lucide-react';
import { validators } from '@/lib/validation';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  // Prevent open redirect — only allow relative paths starting with /
  const rawReturnTo = searchParams.get('returnTo') || '/dashboard';
  const returnTo =
    rawReturnTo.startsWith('/') && !rawReturnTo.startsWith('//') ? rawReturnTo : '/dashboard';
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Field-level validation errors
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [touched, setTouched] = useState({ email: false, password: false });

  // 2FA states
  const [requires2FA, setRequires2FA] = useState(false);
  const [twoFACode, setTwoFACode] = useState('');

  const validateEmail = (value: string): string => {
    if (!value.trim()) return 'البريد الإلكتروني مطلوب';
    if (!validators.email(value)) return 'صيغة البريد الإلكتروني غير صحيحة';
    return '';
  };

  const validatePassword = (value: string): string => {
    if (!value) return 'كلمة المرور مطلوبة';
    if (value.length < 6) return 'كلمة المرور يجب أن تكون 6 أحرف على الأقل';
    return '';
  };

  const handleEmailBlur = () => {
    setTouched((prev) => ({ ...prev, email: true }));
    setEmailError(validateEmail(email));
  };

  const handlePasswordBlur = () => {
    setTouched((prev) => ({ ...prev, password: true }));
    setPasswordError(validatePassword(password));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields before submit
    const eErr = validateEmail(email);
    const pErr = validatePassword(password);
    setEmailError(eErr);
    setPasswordError(pErr);
    setTouched({ email: true, password: true });
    if (eErr || pErr) return;

    setError('');
    setIsLoading(true);

    try {
      const result = await login(email, password, requires2FA ? twoFACode : undefined);

      // Check if 2FA is required
      if (result && typeof result === 'object' && 'requires_2fa' in result && result.requires_2fa) {
        setRequires2FA(true);
        setError('');
      } else {
        router.push(returnTo);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'فشل تسجيل الدخول');
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FASubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Call 2FA verification endpoint
      await login(email, password, twoFACode);
      router.push(returnTo);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'رمز التحقق غير صحيح');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sahool-50 to-sahool-100 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-sahool-600 rounded-full mb-4">
            <Leaf className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">سهول</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">لوحة إدارة المنصة الزراعية</p>
        </div>

        {/* Login Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6 text-center">
            {requires2FA ? 'التحقق الثنائي' : 'تسجيل الدخول'}
          </h2>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-sm" role="alert">
              {error}
            </div>
          )}

          {requires2FA && (
            <div className="bg-blue-50 text-blue-700 p-4 rounded-lg mb-6 text-sm">
              أدخل رمز التحقق من تطبيق المصادقة أو استخدم رمز النسخ الاحتياطي
            </div>
          )}

          <form onSubmit={requires2FA ? handle2FASubmit : handleSubmit} className="space-y-5">
            {!requires2FA && (
              <>
                {/* Email Field */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                  >
                    البريد الإلكتروني
                  </label>
                  <div className="relative">
                    <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        if (touched.email) setEmailError(validateEmail(e.target.value));
                      }}
                      onBlur={handleEmailBlur}
                      className={`w-full pr-10 pl-4 py-3 border rounded-lg focus:ring-2 outline-none transition ${
                        touched.email && emailError
                          ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                          : 'border-gray-300 dark:border-gray-600 focus:ring-sahool-500 focus:border-sahool-500'
                      } dark:bg-gray-700 dark:text-gray-100 dark:placeholder-gray-500`}
                      placeholder="admin@sahool.io"
                      required
                      dir="ltr"
                      aria-invalid={touched.email && !!emailError}
                      aria-describedby={emailError ? 'email-error' : undefined}
                    />
                  </div>
                  {touched.email && emailError && (
                    <p id="email-error" className="text-red-600 text-xs mt-1.5" role="alert">
                      {emailError}
                    </p>
                  )}
                </div>

                {/* Password Field */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label
                      htmlFor="password"
                      className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                      كلمة المرور
                    </label>
                    <Link
                      href="/forgot-password"
                      className="text-sm text-sahool-600 hover:text-sahool-700 hover:underline"
                    >
                      نسيت كلمة المرور؟
                    </Link>
                  </div>
                  <div className="relative">
                    <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        if (touched.password) setPasswordError(validatePassword(e.target.value));
                      }}
                      onBlur={handlePasswordBlur}
                      className={`w-full pr-10 pl-12 py-3 border rounded-lg focus:ring-2 outline-none transition ${
                        touched.password && passwordError
                          ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                          : 'border-gray-300 dark:border-gray-600 focus:ring-sahool-500 focus:border-sahool-500'
                      } dark:bg-gray-700 dark:text-gray-100`}
                      placeholder="••••••••"
                      required
                      dir="ltr"
                      aria-invalid={touched.password && !!passwordError}
                      aria-describedby={passwordError ? 'password-error' : undefined}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      aria-label={showPassword ? 'إخفاء كلمة المرور' : 'إظهار كلمة المرور'}
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  {touched.password && passwordError && (
                    <p id="password-error" className="text-red-600 text-xs mt-1.5" role="alert">
                      {passwordError}
                    </p>
                  )}
                </div>
              </>
            )}

            {requires2FA && (
              /* 2FA Code Field */
              <div>
                <label
                  htmlFor="twoFACode"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                >
                  رمز التحقق
                </label>
                <div className="relative">
                  <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="twoFACode"
                    type="text"
                    value={twoFACode}
                    onChange={(e) => setTwoFACode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    className="w-full pr-10 pl-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-sahool-500 outline-none transition text-center text-2xl tracking-widest"
                    placeholder="000000"
                    required
                    maxLength={6}
                    dir="ltr"
                    autoFocus
                  />
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                  أدخل الرمز المكون من 6 أرقام من تطبيق المصادقة
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-sahool-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-sahool-700 focus:ring-4 focus:ring-sahool-200 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>{requires2FA ? 'جاري التحقق...' : 'جاري تسجيل الدخول...'}</span>
                </>
              ) : (
                <span>{requires2FA ? 'تحقق' : 'تسجيل الدخول'}</span>
              )}
            </button>

            {/* Back button for 2FA */}
            {requires2FA && (
              <button
                type="button"
                onClick={() => {
                  setRequires2FA(false);
                  setTwoFACode('');
                  setError('');
                }}
                className="w-full text-sahool-600 py-2 px-4 rounded-lg font-medium hover:bg-sahool-50 transition"
              >
                العودة لتسجيل الدخول
              </button>
            )}
          </form>

          {/* Registration Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              ليس لديك حساب؟{' '}
              <Link
                href="/register"
                className="text-sahool-600 font-medium hover:text-sahool-700 hover:underline"
              >
                إنشاء حساب جديد
              </Link>
            </p>
          </div>

          {/* Demo credentials removed for security - use .env or seed scripts */}
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 dark:text-gray-400 text-sm mt-6">
          © {new Date().getFullYear()} سهول - جميع الحقوق محفوظة
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-sahool-50 to-sahool-100 dark:from-gray-900 dark:to-gray-950 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-sahool-600" />
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}

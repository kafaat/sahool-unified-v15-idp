'use client';

/**
 * SAHOOL Admin Login Page
 * صفحة تسجيل الدخول للوحة الإدارة
 */

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/stores/auth.store';
import { Loader2, Lock, Mail, Eye, EyeOff, Leaf } from 'lucide-react';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnTo = searchParams.get('returnTo') || '/dashboard';
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 2FA states
  const [requires2FA, setRequires2FA] = useState(false);
  const [tempToken, setTempToken] = useState('');
  const [twoFACode, setTwoFACode] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(email, password, requires2FA ? twoFACode : undefined);

      // Check if 2FA is required
      if (result && typeof result === 'object' && 'requires_2fa' in result && result.requires_2fa) {
        setRequires2FA(true);
        setTempToken(result.temp_token || '');
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
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-600 rounded-full mb-4">
            <Leaf className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">سهول</h1>
          <p className="text-gray-600 mt-2">لوحة إدارة المنصة الزراعية</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
            {requires2FA ? 'التحقق الثنائي' : 'تسجيل الدخول'}
          </h2>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-sm">
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
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    البريد الإلكتروني
                  </label>
                  <div className="relative">
                    <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pr-10 pl-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition"
                      placeholder="admin@sahool.io"
                      required
                      dir="ltr"
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    كلمة المرور
                  </label>
                  <div className="relative">
                    <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pr-10 pl-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition"
                      placeholder="••••••••"
                      required
                      dir="ltr"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </>
            )}

            {requires2FA && (
              /* 2FA Code Field */
              <div>
                <label
                  htmlFor="twoFACode"
                  className="block text-sm font-medium text-gray-700 mb-2"
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
                    className="w-full pr-10 pl-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition text-center text-2xl tracking-widest"
                    placeholder="000000"
                    required
                    maxLength={6}
                    dir="ltr"
                    autoFocus
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  أدخل الرمز المكون من 6 أرقام من تطبيق المصادقة
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 focus:ring-4 focus:ring-green-200 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
                className="w-full text-green-600 py-2 px-4 rounded-lg font-medium hover:bg-green-50 transition"
              >
                العودة لتسجيل الدخول
              </button>
            )}
          </form>

          {/* Demo Credentials (Development Only) */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
              <p className="font-medium mb-2">بيانات الدخول للتجربة:</p>
              <p>البريد: admin@sahool.io</p>
              <p>كلمة المرور: admin123</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          © 2025 سهول - جميع الحقوق محفوظة
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}

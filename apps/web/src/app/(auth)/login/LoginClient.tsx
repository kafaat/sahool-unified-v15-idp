'use client';
import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Mail, Lock, Phone, Smartphone, MessageSquare } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { useAuth } from '@/stores/auth.store';
import { useToast } from '@/components/ui/toast';

type LoginMethod = 'email' | 'phone';

/**
 * Extracts error message from various error types
 * @param error - The error object to extract message from
 * @returns A user-friendly error message
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    // Check for axios-style error response
    const axiosError = error as { response?: { data?: { message?: string } } };
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    return error.message;
  }
  return 'Invalid credentials';
}

/** Validates that a returnTo path is same-origin (starts with /) and not an auth page */
function isSafeReturnTo(value: string | null): value is string {
  if (!value) return false;
  try {
    // Must be a relative path, not an absolute URL pointing elsewhere
    if (!value.startsWith('/')) return false;
    // Prevent open redirect via //evil.com or /\\ tricks
    if (value.startsWith('//') || value.startsWith('/\\')) return false;
    // Don't redirect back to auth pages — that would create a loop
    const authPages = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-otp'];
    return !authPages.some((page) => value.startsWith(page));
  } catch {
    return false;
  }
}

export default function LoginClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const { showToast } = useToast();
  const [loginMethod, setLoginMethod] = useState<LoginMethod>('phone');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSendingOtp, setIsSendingOtp] = useState(false);

  const identifier = loginMethod === 'email' ? email : phone;

  const handleOtpLogin = async () => {
    if (!phone) {
      showToast({
        type: 'error',
        messageAr: 'يرجى إدخال رقم الهاتف أولاً',
        message: 'Please enter your phone number first',
      });
      return;
    }
    setIsSendingOtp(true);
    try {
      const response = await fetch('/api/auth/send-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          identifier: phone,
          channel: 'sms',
          purpose: 'login',
        }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data?.error || data?.message || 'Failed to send OTP');
      }
      showToast({
        type: 'success',
        messageAr: 'تم إرسال رمز التحقق',
        message: 'Verification code sent',
      });
      const params = new URLSearchParams({
        identifier: phone,
        purpose: 'login',
        channel: 'sms',
      });
      router.push(`/verify-otp?${params.toString()}`);
    } catch (error) {
      showToast({
        type: 'error',
        messageAr: 'فشل إرسال رمز التحقق',
        message: getErrorMessage(error),
      });
    } finally {
      setIsSendingOtp(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(identifier, password);
      showToast({
        type: 'success',
        messageAr: 'تم تسجيل الدخول بنجاح',
        message: 'Login successful',
      });
      // Hard redirect so the browser sends the freshly-set httpOnly cookie
      // in a full HTTP request — router.push (RSC soft-nav) does not always
      // carry cookies that were just set by the session API route.
      const returnTo = searchParams.get('returnTo');
      const destination = isSafeReturnTo(returnTo) ? returnTo : '/dashboard';
      window.location.href = destination;
    } catch (error) {
      const errorMessage = getErrorMessage(error);

      showToast({
        type: 'error',
        messageAr: 'فشل تسجيل الدخول',
        message: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
      <Card className="w-full max-w-md" variant="elevated">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-sahool-green-100 rounded-full flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-sahool-green-600 rounded-full" />
          </div>
          <CardTitle className="text-2xl">
            <span className="block">تسجيل الدخول إلى سهول</span>
            <span className="block text-base text-gray-600 mt-1">Login to SAHOOL</span>
          </CardTitle>
          <CardDescription>
            <span className="block text-gray-600">منصة الإدارة الزراعية المتكاملة</span>
            <span className="block text-xs text-gray-500">Integrated Agricultural Management Platform</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Login method toggle */}
            <div className="flex rounded-lg border border-gray-200 p-1 bg-gray-50" role="radiogroup" aria-label="طريقة تسجيل الدخول - Login method">
              <button
                type="button"
                onClick={() => setLoginMethod('phone')}
                role="radio"
                aria-checked={loginMethod === 'phone'}
                aria-label="تسجيل الدخول برقم الهاتف - Login with phone number"
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-sm font-medium transition-all ${
                  loginMethod === 'phone'
                    ? 'bg-sahool-green-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <Smartphone className="w-4 h-4" aria-hidden="true" />
                <span>رقم الهاتف</span>
              </button>
              <button
                type="button"
                onClick={() => setLoginMethod('email')}
                role="radio"
                aria-checked={loginMethod === 'email'}
                aria-label="تسجيل الدخول بالبريد الإلكتروني - Login with email"
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-sm font-medium transition-all ${
                  loginMethod === 'email'
                    ? 'bg-sahool-green-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <Mail className="w-4 h-4" aria-hidden="true" />
                <span>البريد الإلكتروني</span>
              </button>
            </div>

            {loginMethod === 'phone' ? (
              <Input
                type="tel"
                label="Phone Number"
                labelAr="رقم الهاتف"
                placeholder="+967 7X XXX XXXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                leftIcon={<Phone className="w-4 h-4" />}
                required
                autoComplete="tel"
              />
            ) : (
              <Input
                type="email"
                label="Email"
                labelAr="البريد الإلكتروني"
                placeholder="example@sahool.ye"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<Mail className="w-4 h-4" />}
                required
                autoComplete="email"
              />
            )}
            <Input
              type="password"
              label="Password"
              labelAr="كلمة المرور"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-4 h-4" />}
              required
              autoComplete="current-password"
            />
            <Button type="submit" fullWidth isLoading={isLoading} size="lg">
              <span className="font-semibold">تسجيل الدخول</span>
              <span className="mx-2">•</span>
              <span className="text-sm">Login</span>
            </Button>
          </form>
          {loginMethod === 'phone' && (
            <div className="mt-3">
              <div className="relative my-3">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="bg-white px-2 text-gray-500">أو • or</span>
                </div>
              </div>
              <Button
                type="button"
                variant="outline"
                fullWidth
                isLoading={isSendingOtp}
                onClick={handleOtpLogin}
                size="lg"
              >
                <MessageSquare className="w-4 h-4" aria-hidden="true" />
                <span className="mx-2 font-semibold">الدخول برمز SMS</span>
                <span className="text-sm">• Login with SMS code</span>
              </Button>
            </div>
          )}
          <div className="mt-6 text-center space-y-3">
            <Link
              href="/forgot-password"
              className="text-sm text-sahool-green-600 hover:text-sahool-green-700 font-medium block"
            >
              نسيت كلمة المرور؟ • Forgot Password?
            </Link>
            <div className="border-t pt-3">
              <p className="text-sm text-gray-600 mb-1">
                <span>ليس لديك حساب؟</span>
                <span className="mx-1">•</span>
                <span className="text-xs">Don&apos;t have an account?</span>
              </p>
              <Link
                href="/register"
                className="text-sm text-sahool-green-600 hover:text-sahool-green-700 font-medium"
              >
                إنشاء حساب جديد • Create Account
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

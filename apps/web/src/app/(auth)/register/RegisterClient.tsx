'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Mail, Lock, User, Phone, Smartphone } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { useAuth } from '@/stores/auth.store';
import { authApiClient } from '@/lib/api/auth-client';
import { useToast } from '@/components/ui/toast';

/**
 * Yemen mobile phone number validation
 * شركات الاتصالات اليمنية:
 * - Yemen Mobile (يمن موبايل): 77x, 78x
 * - SabaFone (سبأفون): 71x
 * - YOU (يو): 73x
 * - Y (واي): 70x
 */
const YEMEN_PHONE_REGEX = /^(?:\+?967|00967|0)?(?:7[01378]\d{7})$/;
const YEMEN_COUNTRY_CODE = '+967';

/** Recognized Yemen mobile operators with prefix info */
const YEMEN_OPERATORS = [
  { name: 'Yemen Mobile', nameAr: 'يمن موبايل', prefixes: ['77', '78'] },
  { name: 'SabaFone', nameAr: 'سبأفون', prefixes: ['71'] },
  { name: 'YOU', nameAr: 'يو', prefixes: ['73'] },
  { name: 'Y Telecom', nameAr: 'واي', prefixes: ['70'] },
] as const;

/**
 * Detect Yemen mobile operator from phone number
 */
function detectYemenOperator(phone: string): string | null {
  const cleaned = phone.replace(/[\s\-+]/g, '');
  // Extract the 2-digit prefix after country code
  let prefix = '';
  if (cleaned.startsWith('00967')) prefix = cleaned.slice(5, 7);
  else if (cleaned.startsWith('967')) prefix = cleaned.slice(3, 5);
  else if (cleaned.startsWith('0')) prefix = cleaned.slice(1, 3);
  else if (cleaned.startsWith('7')) prefix = cleaned.slice(0, 2);

  for (const op of YEMEN_OPERATORS) {
    if ((op.prefixes as readonly string[]).includes(prefix)) return `${op.nameAr} (${op.name})`;
  }
  return null;
}

/**
 * Validate Yemen phone number
 */
function validateYemenPhone(phone: string): { valid: boolean; error?: string } {
  if (!phone) return { valid: false, error: 'رقم الهاتف مطلوب | Phone number is required' };
  const cleaned = phone.replace(/[\s-]/g, '');
  if (!YEMEN_PHONE_REGEX.test(cleaned)) {
    return {
      valid: false,
      error: 'رقم هاتف يمني غير صالح | Invalid Yemen phone number (e.g. +967 77X XXX XXX)',
    };
  }
  return { valid: true };
}

type RegisterMethod = 'email' | 'phone';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  phone: string;
}

interface RegisterError {
  field?: string;
  message: string;
}

/**
 * Extracts error message from various error types
 * @param error - The error object to extract message from
 * @returns A user-friendly error message
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    // Check for axios-style error response
    const axiosError = error as { response?: { data?: { message?: string; detail?: string } } };
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    return error.message;
  }
  return 'Registration failed. Please try again.';
}

/**
 * Validates the registration form data
 * @param data - Form data to validate
 * @returns Array of validation errors
 */
function validateForm(data: RegisterFormData): RegisterError[] {
  const errors: RegisterError[] = [];

  // Email validation
  if (!data.email) {
    errors.push({ field: 'email', message: 'Email is required' });
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push({ field: 'email', message: 'Invalid email format' });
  }

  // First name validation
  if (!data.firstName.trim()) {
    errors.push({ field: 'firstName', message: 'First name is required' });
  } else if (data.firstName.trim().length < 2) {
    errors.push({ field: 'firstName', message: 'First name must be at least 2 characters' });
  }

  // Last name validation
  if (!data.lastName.trim()) {
    errors.push({ field: 'lastName', message: 'Last name is required' });
  } else if (data.lastName.trim().length < 2) {
    errors.push({ field: 'lastName', message: 'Last name must be at least 2 characters' });
  }

  // Password validation
  if (!data.password) {
    errors.push({ field: 'password', message: 'Password is required' });
  } else if (data.password.length < 8) {
    errors.push({ field: 'password', message: 'Password must be at least 8 characters' });
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(data.password)) {
    errors.push({
      field: 'password',
      message: 'Password must contain uppercase, lowercase, and number',
    });
  }

  // Confirm password validation
  if (!data.confirmPassword) {
    errors.push({ field: 'confirmPassword', message: 'Please confirm your password' });
  } else if (data.password !== data.confirmPassword) {
    errors.push({ field: 'confirmPassword', message: 'Passwords do not match' });
  }

  // Phone validation (required for phone method, must be valid Yemen number if provided)
  if (data.phone) {
    const phoneResult = validateYemenPhone(data.phone);
    if (!phoneResult.valid) {
      errors.push({ field: 'phone', message: phoneResult.error || 'Invalid phone number' });
    }
  }

  return errors;
}

export default function RegisterClient() {
  const router = useRouter();
  // useAuth is available for future auto-login feature
  useAuth();
  const { showToast } = useToast();

  const [registerMethod, setRegisterMethod] = useState<RegisterMethod>('phone');
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    phone: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [detectedOperator, setDetectedOperator] = useState<string | null>(null);

  const handleChange =
    (field: keyof RegisterFormData) => (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setFormData((prev) => ({ ...prev, [field]: value }));
      // Clear field error when user starts typing
      if (errors[field]) {
        setErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[field];
          return newErrors;
        });
      }
      // Detect Yemen operator when typing phone
      if (field === 'phone') {
        setDetectedOperator(detectYemenOperator(value));
      }
    };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Add method-specific required field validation
    if (registerMethod === 'phone' && !formData.phone) {
      setErrors({ phone: 'رقم الهاتف مطلوب | Phone number is required' });
      showToast({
        type: 'error',
        messageAr: 'يرجى إدخال رقم الهاتف',
        message: 'Please enter your phone number',
      });
      return;
    }
    if (registerMethod === 'email' && !formData.email) {
      setErrors({ email: 'البريد الإلكتروني مطلوب | Email is required' });
      showToast({
        type: 'error',
        messageAr: 'يرجى إدخال البريد الإلكتروني',
        message: 'Please enter your email',
      });
      return;
    }

    // Validate form
    const validationErrors = validateForm(formData);
    if (validationErrors.length > 0) {
      const errorMap: Record<string, string> = {};
      validationErrors.forEach((err) => {
        if (err.field) {
          errorMap[err.field] = err.message;
        }
      });
      setErrors(errorMap);

      // Show first error as toast
      const firstError = validationErrors[0];
      showToast({
        type: 'error',
        messageAr: 'يرجى تصحيح الأخطاء في النموذج',
        message: firstError ? firstError.message : 'Please fix the form errors',
      });
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      // Normalize phone to international format
      let normalizedPhone = formData.phone.trim();
      if (normalizedPhone && !normalizedPhone.startsWith('+')) {
        normalizedPhone = normalizedPhone.replace(/^(00967|967|0)/, '');
        normalizedPhone = `${YEMEN_COUNTRY_CODE}${normalizedPhone}`;
      }

      // Use the typed authApiClient.register() instead of a raw fetch
      // string-built from process.env.NEXT_PUBLIC_API_URL. The new path
      // routes through the Next.js rewrite (same-origin), applies a
      // 15 s timeout, and throws a typed Error with the server's
      // message — which the catch block below maps into a bilingual
      // toast via `getErrorMessage()`. CSRF and automatic retries are
      // intentionally NOT applied here (auth endpoints are anonymous
      // and self-registration is a single user-initiated request).
      // See E2E_USER_JOURNEY_AUDIT.md F-3 for the rationale.
      const result = await authApiClient.register({
        email: formData.email,
        phone: normalizedPhone,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
      });

      if (!result.success) {
        throw new Error(result.error || result.message || 'Registration failed');
      }

      showToast({
        type: 'success',
        messageAr: 'تم إنشاء الحساب بنجاح',
        message: 'Account created successfully',
      });

      // Auto-login after successful registration if tokens are returned.
      // The session endpoint sets httpOnly cookies — the next navigation
      // will carry them automatically.
      const tokens = result.data;
      if (tokens?.access_token) {
        const sessionResponse = await fetch('/api/auth/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            access_token: tokens.access_token,
            refresh_token: tokens.refresh_token,
          }),
        });

        if (sessionResponse.ok) {
          // Hard redirect so the browser sends the freshly-set httpOnly cookie
          // in a full HTTP request — router.push (RSC soft-nav) does not always
          // carry cookies that were just set by the session API route.
          window.location.href = '/dashboard';
          return;
        }
      }

      // If no auto-login (e.g. duplicate email returns success without tokens),
      // redirect to login page.
      router.push('/login');
    } catch (error) {
      const errorMessage = getErrorMessage(error);

      showToast({
        type: 'error',
        messageAr: 'فشل إنشاء الحساب',
        message: errorMessage,
      });

      // Set specific field error if the API returns field info
      if (errorMessage.toLowerCase().includes('email')) {
        setErrors({ email: errorMessage });
      }
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
            <div>إنشاء حساب جديد</div>
            <div className="text-base text-gray-600 mt-1">Create New Account</div>
          </CardTitle>
          <CardDescription>
            <div className="text-gray-600">انضم إلى منصة سهول الزراعية المتكاملة</div>
            <div className="text-xs text-gray-500">Join SAHOOL Smart Agricultural Platform</div>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Registration method toggle */}
            <div className="flex rounded-lg border border-gray-200 p-1 bg-gray-50">
              <button
                type="button"
                onClick={() => setRegisterMethod('phone')}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-sm font-medium transition-all ${
                  registerMethod === 'phone'
                    ? 'bg-sahool-green-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <Smartphone className="w-4 h-4" />
                <span>رقم الهاتف</span>
                <span className="text-xs opacity-75">Phone</span>
              </button>
              <button
                type="button"
                onClick={() => setRegisterMethod('email')}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-sm font-medium transition-all ${
                  registerMethod === 'email'
                    ? 'bg-sahool-green-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <Mail className="w-4 h-4" />
                <span>البريد الإلكتروني</span>
                <span className="text-xs opacity-75">Email</span>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input
                type="text"
                label="First Name"
                labelAr="الاسم الأول"
                placeholder="محمد"
                value={formData.firstName}
                onChange={handleChange('firstName')}
                leftIcon={<User className="w-4 h-4" />}
                error={errors.firstName}
                required
                autoComplete="given-name"
              />
              <Input
                type="text"
                label="Last Name"
                labelAr="اسم العائلة"
                placeholder="الأحمد"
                value={formData.lastName}
                onChange={handleChange('lastName')}
                error={errors.lastName}
                required
                autoComplete="family-name"
              />
            </div>

            {/* Phone field - primary for phone method */}
            <div>
              <Input
                type="tel"
                label={registerMethod === 'phone' ? 'Phone Number' : 'Phone (Optional)'}
                labelAr={registerMethod === 'phone' ? 'رقم الهاتف' : 'رقم الهاتف (اختياري)'}
                placeholder="+967 7X XXX XXXX"
                value={formData.phone}
                onChange={handleChange('phone')}
                leftIcon={<Phone className="w-4 h-4" />}
                error={errors.phone}
                required={registerMethod === 'phone'}
                autoComplete="tel"
              />
              {detectedOperator && (
                <p className="mt-1 text-xs text-sahool-green-600 font-medium">{detectedOperator}</p>
              )}
              {registerMethod === 'phone' && !formData.phone && (
                <p className="mt-1 text-xs text-gray-500">
                  يمن موبايل (77, 78) • سبأفون (71) • يو (73) • واي (70)
                </p>
              )}
            </div>

            {/* Email field - primary for email method */}
            <Input
              type="email"
              label={registerMethod === 'email' ? 'Email' : 'Email (Optional)'}
              labelAr={
                registerMethod === 'email' ? 'البريد الإلكتروني' : 'البريد الإلكتروني (اختياري)'
              }
              placeholder="example@sahool.ye"
              value={formData.email}
              onChange={handleChange('email')}
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.email}
              required={registerMethod === 'email'}
              autoComplete="email"
            />
            <Input
              type="password"
              label="Password"
              labelAr="كلمة المرور"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange('password')}
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password}
              helperText="At least 8 characters with uppercase, lowercase, and a number • 8 أحرف على الأقل مع حرف كبير وحرف صغير ورقم"
              required
              autoComplete="new-password"
            />
            <Input
              type="password"
              label="Confirm Password"
              labelAr="تأكيد كلمة المرور"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleChange('confirmPassword')}
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.confirmPassword}
              required
              autoComplete="new-password"
            />
            <Button type="submit" fullWidth isLoading={isLoading} size="lg">
              <span className="font-semibold">إنشاء حساب</span>
              <span className="mx-2">•</span>
              <span className="text-sm">Create Account</span>
            </Button>
          </form>
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              <span>لديك حساب بالفعل؟</span>
              <span className="mx-1">•</span>
              <span className="text-xs">Already have an account?</span>
            </p>
            <Link
              href="/login"
              className="text-sm text-sahool-green-600 hover:text-sahool-green-700 font-medium mt-1 inline-block"
            >
              تسجيل الدخول • Login
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

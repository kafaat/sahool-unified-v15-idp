"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail, Lock, User, Phone } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useAuth } from "@/stores/auth.store";
import { useToast } from "@/components/ui/toast";

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
  return "Registration failed. Please try again.";
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
    errors.push({ field: "email", message: "Email is required" });
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.push({ field: "email", message: "Invalid email format" });
  }

  // First name validation
  if (!data.firstName.trim()) {
    errors.push({ field: "firstName", message: "First name is required" });
  } else if (data.firstName.trim().length < 2) {
    errors.push({ field: "firstName", message: "First name must be at least 2 characters" });
  }

  // Last name validation
  if (!data.lastName.trim()) {
    errors.push({ field: "lastName", message: "Last name is required" });
  } else if (data.lastName.trim().length < 2) {
    errors.push({ field: "lastName", message: "Last name must be at least 2 characters" });
  }

  // Password validation
  if (!data.password) {
    errors.push({ field: "password", message: "Password is required" });
  } else if (data.password.length < 8) {
    errors.push({ field: "password", message: "Password must be at least 8 characters" });
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(data.password)) {
    errors.push({
      field: "password",
      message: "Password must contain uppercase, lowercase, and number",
    });
  }

  // Confirm password validation
  if (!data.confirmPassword) {
    errors.push({ field: "confirmPassword", message: "Please confirm your password" });
  } else if (data.password !== data.confirmPassword) {
    errors.push({ field: "confirmPassword", message: "Passwords do not match" });
  }

  // Phone validation (optional but must be valid if provided)
  if (data.phone && !/^\+?[\d\s-]{7,15}$/.test(data.phone)) {
    errors.push({ field: "phone", message: "Invalid phone number format" });
  }

  return errors;
}

export default function RegisterClient() {
  const router = useRouter();
  // useAuth is available for future auto-login feature
  useAuth();
  const { showToast } = useToast();

  const [formData, setFormData] = useState<RegisterFormData>({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    phone: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (field: keyof RegisterFormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
    // Clear field error when user starts typing
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

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
        type: "error",
        messageAr: "يرجى تصحيح الأخطاء في النموذج",
        message: firstError ? firstError.message : "Please fix the form errors",
      });
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      // Call registration API
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: formData.email.toLowerCase().trim(),
            password: formData.password,
            first_name: formData.firstName.trim(),
            last_name: formData.lastName.trim(),
            phone: formData.phone.trim() || undefined,
          }),
          credentials: "include",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.detail || "Registration failed");
      }

      showToast({
        type: "success",
        messageAr: "تم إنشاء الحساب بنجاح",
        message: "Account created successfully",
      });

      // Auto-login after successful registration if tokens are returned
      if (data.access_token) {
        // Set session via API
        const sessionResponse = await fetch("/api/auth/session", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            access_token: data.access_token,
            refresh_token: data.refresh_token,
          }),
        });

        if (sessionResponse.ok) {
          router.push("/dashboard");
          return;
        }
      }

      // If no auto-login, redirect to login page
      showToast({
        type: "info",
        messageAr: "يرجى تسجيل الدخول للمتابعة",
        message: "Please login to continue",
      });
      router.push("/login");
    } catch (error) {
      const errorMessage = getErrorMessage(error);

      showToast({
        type: "error",
        messageAr: "فشل إنشاء الحساب",
        message: errorMessage,
      });

      // Set specific field error if the API returns field info
      if (errorMessage.toLowerCase().includes("email")) {
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
            <div className="text-xs text-gray-500">
              Join SAHOOL Smart Agricultural Platform
            </div>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Input
                type="text"
                label="First Name"
                labelAr="الاسم الأول"
                placeholder="محمد"
                value={formData.firstName}
                onChange={handleChange("firstName")}
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
                onChange={handleChange("lastName")}
                error={errors.lastName}
                required
                autoComplete="family-name"
              />
            </div>
            <Input
              type="email"
              label="Email"
              labelAr="البريد الإلكتروني"
              placeholder="example@sahool.com"
              value={formData.email}
              onChange={handleChange("email")}
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.email}
              required
              autoComplete="email"
            />
            <Input
              type="tel"
              label="Phone (Optional)"
              labelAr="رقم الهاتف (اختياري)"
              placeholder="+966 5X XXX XXXX"
              value={formData.phone}
              onChange={handleChange("phone")}
              leftIcon={<Phone className="w-4 h-4" />}
              error={errors.phone}
              autoComplete="tel"
            />
            <Input
              type="password"
              label="Password"
              labelAr="كلمة المرور"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange("password")}
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password}
              helperText="At least 8 characters with uppercase, lowercase, and number"
              required
              autoComplete="new-password"
            />
            <Input
              type="password"
              label="Confirm Password"
              labelAr="تأكيد كلمة المرور"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleChange("confirmPassword")}
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

"use client";

/**
 * SAHOOL Admin Reset Password Page
 * صفحة إعادة تعيين كلمة المرور للوحة الإدارة
 */

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Loader2, Lock, Leaf, ArrowRight, CheckCircle, Eye, EyeOff, AlertTriangle } from "lucide-react";
import { API_BASE_URL } from "@/config/api";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Password validation
  const passwordErrors = [];
  if (newPassword.length > 0 && newPassword.length < 8) {
    passwordErrors.push("يجب أن تكون كلمة المرور 8 أحرف على الأقل");
  }
  if (confirmPassword.length > 0 && newPassword !== confirmPassword) {
    passwordErrors.push("كلمات المرور غير متطابقة");
  }

  const isFormValid = newPassword.length >= 8 && newPassword === confirmPassword && token;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!token) {
      setError("رمز إعادة التعيين غير صالح أو مفقود");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("كلمات المرور غير متطابقة");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.error || "فشل في إعادة تعيين كلمة المرور");
      }

      setIsSuccess(true);

      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push("/login");
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "حدث خطأ غير متوقع");
    } finally {
      setIsLoading(false);
    }
  };

  // No token provided
  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-600 rounded-full mb-4">
              <Leaf className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">سهول</h1>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              رابط غير صالح
            </h2>
            <p className="text-gray-600 mb-6">
              رابط إعادة تعيين كلمة المرور غير صالح أو منتهي الصلاحية.
              يرجى طلب رابط جديد.
            </p>
            <Link
              href="/forgot-password"
              className="inline-flex items-center justify-center gap-2 bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 transition"
            >
              طلب رابط جديد
            </Link>
          </div>
        </div>
      </div>
    );
  }

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

        {/* Reset Password Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {isSuccess ? (
            /* Success State */
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                تم تغيير كلمة المرور بنجاح
              </h2>
              <p className="text-gray-600 mb-6">
                يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة.
                سيتم توجيهك تلقائيًا...
              </p>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 text-green-600 font-medium hover:text-green-700"
              >
                <ArrowRight className="w-4 h-4" />
                تسجيل الدخول الآن
              </Link>
            </div>
          ) : (
            /* Form State */
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-2 text-center">
                إعادة تعيين كلمة المرور
              </h2>
              <p className="text-gray-600 text-sm mb-6 text-center">
                أدخل كلمة المرور الجديدة لحسابك
              </p>

              {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-sm">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* New Password Field */}
                <div>
                  <label
                    htmlFor="newPassword"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    كلمة المرور الجديدة
                  </label>
                  <div className="relative">
                    <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="newPassword"
                      type={showPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full pr-10 pl-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition"
                      placeholder="••••••••"
                      required
                      minLength={8}
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

                {/* Confirm Password Field */}
                <div>
                  <label
                    htmlFor="confirmPassword"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    تأكيد كلمة المرور
                  </label>
                  <div className="relative">
                    <Lock className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full pr-10 pl-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition"
                      placeholder="••••••••"
                      required
                      minLength={8}
                      dir="ltr"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Password Errors */}
                {passwordErrors.length > 0 && (
                  <div className="text-sm text-red-500 space-y-1">
                    {passwordErrors.map((err, i) => (
                      <p key={i}>• {err}</p>
                    ))}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isLoading || !isFormValid}
                  className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 focus:ring-4 focus:ring-green-200 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>جاري إعادة التعيين...</span>
                    </>
                  ) : (
                    <span>إعادة تعيين كلمة المرور</span>
                  )}
                </button>
              </form>

              {/* Back to Login */}
              <div className="mt-6 text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center gap-2 text-green-600 font-medium hover:text-green-700"
                >
                  <ArrowRight className="w-4 h-4" />
                  العودة لتسجيل الدخول
                </Link>
              </div>
            </>
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

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        </div>
      }
    >
      <ResetPasswordForm />
    </Suspense>
  );
}

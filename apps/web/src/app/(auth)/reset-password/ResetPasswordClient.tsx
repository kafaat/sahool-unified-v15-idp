"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Lock, ArrowRight, CheckCircle, AlertTriangle, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const { showToast } = useToast();

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Password validation
  const passwordErrors: string[] = [];
  if (newPassword.length > 0 && newPassword.length < 8) {
    passwordErrors.push("Password must be at least 8 characters");
  }
  if (confirmPassword.length > 0 && newPassword !== confirmPassword) {
    passwordErrors.push("Passwords do not match");
  }

  const isFormValid = newPassword.length >= 8 && newPassword === confirmPassword && token;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      showToast({
        type: "error",
        messageAr: "رمز إعادة التعيين غير صالح",
        message: "Invalid reset token",
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      showToast({
        type: "error",
        messageAr: "كلمات المرور غير متطابقة",
        message: "Passwords do not match",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/auth/reset-password", {
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
        throw new Error(data.message || data.error || "Failed to reset password");
      }

      setIsSuccess(true);
      showToast({
        type: "success",
        messageAr: "تم تغيير كلمة المرور بنجاح",
        message: "Password reset successful",
      });

      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push("/login");
      }, 3000);
    } catch (error) {
      showToast({
        type: "error",
        messageAr: "فشل في إعادة تعيين كلمة المرور",
        message: error instanceof Error ? error.message : "An error occurred",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // No token provided
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
        <Card className="w-full max-w-md" variant="elevated">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <CardTitle className="text-2xl">
              <div>رابط غير صالح</div>
              <div className="text-base text-gray-600 mt-1">Invalid Link</div>
            </CardTitle>
            <CardDescription>
              <div className="text-gray-600">
                رابط إعادة تعيين كلمة المرور غير صالح أو منتهي الصلاحية
              </div>
              <div className="text-xs text-gray-500 mt-1">
                The password reset link is invalid or has expired
              </div>
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Link href="/forgot-password">
              <Button size="lg">
                <span>طلب رابط جديد</span>
                <span className="mx-2">•</span>
                <span className="text-sm">Request New Link</span>
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
      <Card className="w-full max-w-md" variant="elevated">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-sahool-green-100 rounded-full flex items-center justify-center mb-4">
            {isSuccess ? (
              <CheckCircle className="w-8 h-8 text-sahool-green-600" />
            ) : (
              <Lock className="w-8 h-8 text-sahool-green-600" />
            )}
          </div>
          <CardTitle className="text-2xl">
            <div>{isSuccess ? "تم التغيير بنجاح" : "إعادة تعيين كلمة المرور"}</div>
            <div className="text-base text-gray-600 mt-1">
              {isSuccess ? "Password Changed" : "Reset Password"}
            </div>
          </CardTitle>
          <CardDescription>
            {isSuccess ? (
              <>
                <div className="text-gray-600">
                  يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  You can now login with your new password
                </div>
              </>
            ) : (
              <>
                <div className="text-gray-600">أدخل كلمة المرور الجديدة لحسابك</div>
                <div className="text-xs text-gray-500 mt-1">
                  Enter a new password for your account
                </div>
              </>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSuccess ? (
            <div className="text-center space-y-4">
              <p className="text-sm text-gray-600">
                سيتم توجيهك تلقائيًا...
                <br />
                <span className="text-xs">Redirecting automatically...</span>
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-sahool-green-600 hover:text-sahool-green-700 font-medium"
              >
                <ArrowRight className="w-4 h-4 rotate-180" />
                <span>تسجيل الدخول الآن • Login Now</span>
              </Link>
            </div>
          ) : (
            <>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  type="password"
                  label="New Password"
                  labelAr="كلمة المرور الجديدة"
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  leftIcon={<Lock className="w-4 h-4" />}
                  required
                  minLength={8}
                  autoComplete="new-password"
                />
                <Input
                  type="password"
                  label="Confirm Password"
                  labelAr="تأكيد كلمة المرور"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  leftIcon={<Lock className="w-4 h-4" />}
                  required
                  minLength={8}
                  autoComplete="new-password"
                />
                {passwordErrors.length > 0 && (
                  <div className="text-sm text-red-500 space-y-1">
                    {passwordErrors.map((err, i) => (
                      <p key={i}>• {err}</p>
                    ))}
                  </div>
                )}
                <Button
                  type="submit"
                  fullWidth
                  isLoading={isLoading}
                  size="lg"
                  disabled={!isFormValid}
                >
                  <span className="font-semibold">إعادة تعيين كلمة المرور</span>
                  <span className="mx-2">•</span>
                  <span className="text-sm">Reset Password</span>
                </Button>
              </form>
              <div className="mt-6 text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-2 text-sm text-sahool-green-600 hover:text-sahool-green-700 font-medium"
                >
                  <ArrowRight className="w-4 h-4 rotate-180" />
                  <span>العودة لتسجيل الدخول • Back to Login</span>
                </Link>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function ResetPasswordClient() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white">
          <Loader2 className="w-8 h-8 animate-spin text-sahool-green-600" />
        </div>
      }
    >
      <ResetPasswordForm />
    </Suspense>
  );
}

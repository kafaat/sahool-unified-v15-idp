"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail, Lock } from "lucide-react";
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
  return "Invalid credentials";
}

export default function LoginClient() {
  const router = useRouter();
  const { login } = useAuth();
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      showToast({
        type: "success",
        messageAr: "تم تسجيل الدخول بنجاح",
        message: "Login successful",
      });
      router.push("/dashboard");
    } catch (error) {
      const errorMessage = getErrorMessage(error);

      showToast({
        type: "error",
        messageAr: "فشل تسجيل الدخول",
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
            <div>تسجيل الدخول إلى سهول</div>
            <div className="text-base text-gray-600 mt-1">Login to SAHOOL</div>
          </CardTitle>
          <CardDescription>
            <div className="text-gray-600">منصة الإدارة الزراعية المتكاملة</div>
            <div className="text-xs text-gray-500">
              Integrated Agricultural Management Platform
            </div>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="email"
              label="Email"
              labelAr="البريد الإلكتروني"
              placeholder="example@sahool.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
              required
              autoComplete="email"
            />
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

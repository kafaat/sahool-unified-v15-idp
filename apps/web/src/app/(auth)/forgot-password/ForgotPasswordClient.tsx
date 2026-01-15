"use client";

import { useState } from "react";
import Link from "next/link";
import { Mail, ArrowRight, CheckCircle } from "lucide-react";
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

export default function ForgotPasswordClient() {
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.error || "Failed to send reset email");
      }

      setIsSuccess(true);
      showToast({
        type: "success",
        messageAr: "تم إرسال رابط إعادة التعيين",
        message: "Reset link sent successfully",
      });
    } catch (error) {
      showToast({
        type: "error",
        messageAr: "فشل في إرسال الرابط",
        message: error instanceof Error ? error.message : "An error occurred",
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
            {isSuccess ? (
              <CheckCircle className="w-8 h-8 text-sahool-green-600" />
            ) : (
              <Mail className="w-8 h-8 text-sahool-green-600" />
            )}
          </div>
          <CardTitle className="text-2xl">
            <div>{isSuccess ? "تم الإرسال" : "نسيت كلمة المرور؟"}</div>
            <div className="text-base text-gray-600 mt-1">
              {isSuccess ? "Email Sent" : "Forgot Password?"}
            </div>
          </CardTitle>
          <CardDescription>
            {isSuccess ? (
              <>
                <div className="text-gray-600">
                  إذا كان هناك حساب مرتبط بهذا البريد، فسيتم إرسال رابط إعادة التعيين
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  If an account exists with this email, a reset link has been sent
                </div>
              </>
            ) : (
              <>
                <div className="text-gray-600">
                  أدخل بريدك الإلكتروني وسنرسل لك رابطًا لإعادة تعيين كلمة المرور
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Enter your email and we will send you a password reset link
                </div>
              </>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSuccess ? (
            <div className="text-center space-y-4">
              <p className="text-sm text-gray-600">
                الرابط صالح لمدة ساعة واحدة فقط
                <br />
                <span className="text-xs">The link is valid for 1 hour only</span>
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-sahool-green-600 hover:text-sahool-green-700 font-medium"
              >
                <ArrowRight className="w-4 h-4 rotate-180" />
                <span>العودة لتسجيل الدخول • Back to Login</span>
              </Link>
            </div>
          ) : (
            <>
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
                <Button type="submit" fullWidth isLoading={isLoading} size="lg">
                  <span className="font-semibold">إرسال رابط إعادة التعيين</span>
                  <span className="mx-2">•</span>
                  <span className="text-sm">Send Reset Link</span>
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

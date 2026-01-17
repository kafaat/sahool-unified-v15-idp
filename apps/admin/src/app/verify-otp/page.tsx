"use client";

/**
 * SAHOOL Admin OTP Verification Page
 * صفحة التحقق من رمز OTP للوحة الإدارة
 */

import { useState, useEffect, useRef, Suspense, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Loader2, Shield, Clock, RefreshCw, Leaf, ArrowRight, CheckCircle } from "lucide-react";
import { API_BASE_URL } from "@/config/api";

// OTP expiration time in seconds
const OTP_EXPIRATION_TIME = 300; // 5 minutes
// Cooldown time for resend in seconds
const RESEND_COOLDOWN_TIME = 60; // 1 minute

// Bilingual translations
const translations = {
  ar: {
    title: "سهول",
    subtitle: "لوحة إدارة المنصة الزراعية",
    verifyTitle: "التحقق من الرمز",
    verifySubtitle: "أدخل رمز التحقق المرسل إلى",
    otpSentVia: {
      sms: "عبر رسالة نصية",
      whatsapp: "عبر واتساب",
      telegram: "عبر تيليجرام",
      email: "عبر البريد الإلكتروني",
    },
    enterOtp: "أدخل رمز التحقق المكون من 6 أرقام",
    timeRemaining: "الوقت المتبقي",
    otpExpired: "انتهت صلاحية الرمز",
    resendOtp: "إعادة إرسال الرمز",
    resendIn: "إعادة الإرسال بعد",
    seconds: "ثانية",
    verify: "تحقق",
    verifying: "جاري التحقق...",
    success: "تم التحقق بنجاح",
    successMessage: "جاري تحويلك...",
    backToLogin: "العودة لتسجيل الدخول",
    invalidOtp: "الرمز غير صحيح",
    resendSuccess: "تم إعادة إرسال الرمز بنجاح",
    resendError: "فشل في إعادة إرسال الرمز",
    copyright: "جميع الحقوق محفوظة",
    purpose: {
      password_reset: "إعادة تعيين كلمة المرور",
      verify_phone: "التحقق من رقم الهاتف",
      verify_email: "التحقق من البريد الإلكتروني",
    },
  },
  en: {
    title: "SAHOOL",
    subtitle: "Agricultural Platform Admin Panel",
    verifyTitle: "Verify OTP",
    verifySubtitle: "Enter the verification code sent to",
    otpSentVia: {
      sms: "via SMS",
      whatsapp: "via WhatsApp",
      telegram: "via Telegram",
      email: "via Email",
    },
    enterOtp: "Enter the 6-digit verification code",
    timeRemaining: "Time remaining",
    otpExpired: "OTP has expired",
    resendOtp: "Resend OTP",
    resendIn: "Resend in",
    seconds: "seconds",
    verify: "Verify",
    verifying: "Verifying...",
    success: "Verification Successful",
    successMessage: "Redirecting you...",
    backToLogin: "Back to Login",
    invalidOtp: "Invalid OTP",
    resendSuccess: "OTP resent successfully",
    resendError: "Failed to resend OTP",
    copyright: "All rights reserved",
    purpose: {
      password_reset: "Password Reset",
      verify_phone: "Phone Verification",
      verify_email: "Email Verification",
    },
  },
};

type Language = "ar" | "en";
type Channel = "sms" | "whatsapp" | "telegram" | "email";
type Purpose = "password_reset" | "verify_phone" | "verify_email";

function VerifyOTPForm() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Get query params
  const identifier = searchParams.get("identifier") || "";
  const purpose = (searchParams.get("purpose") || "password_reset") as Purpose;
  const channel = (searchParams.get("channel") || "sms") as Channel;

  // State
  const [otp, setOtp] = useState<string[]>(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(OTP_EXPIRATION_TIME);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [isVerified, setIsVerified] = useState(false);
  const [language, setLanguage] = useState<Language>("ar");

  // Refs for OTP input fields
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const t = translations[language];

  // Timer for OTP expiration
  useEffect(() => {
    if (timeRemaining <= 0 || isVerified) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeRemaining, isVerified]);

  // Timer for resend cooldown
  useEffect(() => {
    if (resendCooldown <= 0) return;

    const timer = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [resendCooldown]);

  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Handle OTP input change
  const handleOtpChange = (index: number, value: string) => {
    // Only allow digits
    const digit = value.replace(/\D/g, "").slice(-1);

    const newOtp = [...otp];
    newOtp[index] = digit;
    setOtp(newOtp);
    setError("");

    // Auto-focus next input
    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all digits are filled
    if (digit && index === 5 && newOtp.every((d) => d !== "")) {
      handleVerify(newOtp.join(""));
    }
  };

  // Handle key down events
  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    const currentValue = otp[index] ?? "";
    if (e.key === "Backspace" && !currentValue && index > 0) {
      // Move to previous input on backspace if current is empty
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === "ArrowLeft" && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === "ArrowRight" && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  // Handle paste
  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    const newOtp = [...otp];

    for (let i = 0; i < pastedData.length && i < 6; i++) {
      const char = pastedData[i];
      if (char !== undefined) {
        newOtp[i] = char;
      }
    }

    setOtp(newOtp);
    setError("");

    // Focus the next empty input or the last one
    const nextEmptyIndex = newOtp.findIndex((d) => d === "");
    if (nextEmptyIndex !== -1) {
      inputRefs.current[nextEmptyIndex]?.focus();
    } else {
      inputRefs.current[5]?.focus();
      // Auto-submit if all filled
      handleVerify(newOtp.join(""));
    }
  };

  // Verify OTP
  const handleVerify = useCallback(async (otpCode?: string) => {
    const code = otpCode || otp.join("");

    if (code.length !== 6) {
      setError(t.invalidOtp);
      return;
    }

    if (timeRemaining <= 0) {
      setError(t.otpExpired);
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/verify-otp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          identifier,
          otp: code,
          purpose,
          channel,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.detail || t.invalidOtp);
      }

      setIsVerified(true);

      // Redirect based on purpose
      setTimeout(() => {
        if (purpose === "password_reset") {
          // Redirect to reset password page with token
          const token = data.token || data.reset_token;
          router.push(`/reset-password?token=${token}&identifier=${encodeURIComponent(identifier)}`);
        } else {
          // Redirect to dashboard for phone/email verification
          router.push("/dashboard");
        }
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.invalidOtp);
      // Clear OTP on error
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } finally {
      setIsLoading(false);
    }
  }, [otp, identifier, purpose, channel, timeRemaining, router, t]);

  // Resend OTP
  const handleResend = async () => {
    if (resendCooldown > 0 || isResending) return;

    setIsResending(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/resend-otp`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          identifier,
          purpose,
          channel,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.detail || t.resendError);
      }

      setSuccess(t.resendSuccess);
      setTimeRemaining(OTP_EXPIRATION_TIME);
      setResendCooldown(RESEND_COOLDOWN_TIME);
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.resendError);
    } finally {
      setIsResending(false);
    }
  };

  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleVerify();
  };

  // Mask identifier for display
  const maskIdentifier = (id: string) => {
    if (id.includes("@")) {
      // Email
      const [local, domain] = id.split("@");
      const localPart = local ?? "";
      const maskedLocal = localPart.length > 2
        ? `${localPart[0] ?? ""}${"*".repeat(localPart.length - 2)}${localPart[localPart.length - 1] ?? ""}`
        : localPart;
      return `${maskedLocal}@${domain ?? ""}`;
    } else {
      // Phone
      if (id.length > 4) {
        return `${"*".repeat(id.length - 4)}${id.slice(-4)}`;
      }
      return id;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Language Toggle */}
        <div className="flex justify-end mb-4">
          <button
            onClick={() => setLanguage(language === "ar" ? "en" : "ar")}
            className="text-sm text-gray-600 hover:text-green-600 transition px-3 py-1 rounded-lg hover:bg-white/50"
          >
            {language === "ar" ? "English" : "العربية"}
          </button>
        </div>

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-600 rounded-full mb-4">
            <Leaf className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600 mt-2">{t.subtitle}</p>
        </div>

        {/* OTP Verification Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8" dir={language === "ar" ? "rtl" : "ltr"}>
          {isVerified ? (
            /* Success State */
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {t.success}
              </h2>
              <p className="text-gray-600 mb-4">
                {t.successMessage}
              </p>
              <Loader2 className="w-6 h-6 animate-spin text-green-600 mx-auto" />
            </div>
          ) : (
            /* Form State */
            <>
              {/* Header */}
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-4">
                  <Shield className="w-6 h-6 text-green-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  {t.verifyTitle}
                </h2>
                <p className="text-gray-600 text-sm">
                  {t.verifySubtitle}
                </p>
                <p className="text-green-600 font-medium mt-1" dir="ltr">
                  {maskIdentifier(identifier)}
                </p>
                <p className="text-gray-500 text-xs mt-1">
                  {t.otpSentVia[channel]} - {t.purpose[purpose]}
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-sm text-center">
                  {error}
                </div>
              )}

              {/* Success Message */}
              {success && (
                <div className="bg-green-50 text-green-600 p-4 rounded-lg mb-6 text-sm text-center">
                  {success}
                </div>
              )}

              {/* OTP Expired Warning */}
              {timeRemaining <= 0 && (
                <div className="bg-amber-50 text-amber-600 p-4 rounded-lg mb-6 text-sm text-center">
                  {t.otpExpired}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* OTP Input Fields */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3 text-center">
                    {t.enterOtp}
                  </label>
                  <div className="flex justify-center gap-2" dir="ltr">
                    {otp.map((digit, index) => (
                      <input
                        key={index}
                        ref={(el) => {
                          inputRefs.current[index] = el;
                        }}
                        type="text"
                        inputMode="numeric"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        onPaste={handlePaste}
                        className={`w-12 h-14 text-center text-2xl font-semibold border-2 rounded-lg outline-none transition
                          ${digit ? "border-green-500 bg-green-50" : "border-gray-300"}
                          ${timeRemaining <= 0 ? "bg-gray-100 cursor-not-allowed" : ""}
                          focus:ring-2 focus:ring-green-500 focus:border-green-500`}
                        disabled={isLoading || timeRemaining <= 0}
                        autoFocus={index === 0}
                      />
                    ))}
                  </div>
                </div>

                {/* Timer */}
                <div className="flex items-center justify-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">{t.timeRemaining}:</span>
                  <span
                    className={`font-mono font-medium ${
                      timeRemaining <= 60 ? "text-red-500" : "text-green-600"
                    }`}
                  >
                    {formatTime(timeRemaining)}
                  </span>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isLoading || otp.join("").length !== 6 || timeRemaining <= 0}
                  className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 focus:ring-4 focus:ring-green-200 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>{t.verifying}</span>
                    </>
                  ) : (
                    <span>{t.verify}</span>
                  )}
                </button>

                {/* Resend OTP */}
                <div className="text-center">
                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={resendCooldown > 0 || isResending}
                    className={`inline-flex items-center gap-2 text-sm font-medium transition
                      ${resendCooldown > 0 || isResending
                        ? "text-gray-400 cursor-not-allowed"
                        : "text-green-600 hover:text-green-700"
                      }`}
                  >
                    <RefreshCw className={`w-4 h-4 ${isResending ? "animate-spin" : ""}`} />
                    {resendCooldown > 0 ? (
                      <span>
                        {t.resendIn} {resendCooldown} {t.seconds}
                      </span>
                    ) : (
                      <span>{t.resendOtp}</span>
                    )}
                  </button>
                </div>
              </form>

              {/* Back to Login */}
              <div className="mt-6 text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center gap-2 text-green-600 font-medium hover:text-green-700"
                >
                  <ArrowRight className={`w-4 h-4 ${language === "ar" ? "" : "rotate-180"}`} />
                  {t.backToLogin}
                </Link>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          &copy; 2025 {t.title} - {t.copyright}
        </p>
      </div>
    </div>
  );
}

export default function VerifyOTPPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        </div>
      }
    >
      <VerifyOTPForm />
    </Suspense>
  );
}

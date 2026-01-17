"use client";

import { useState, useEffect, useRef, Suspense, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Shield, Clock, RefreshCw, CheckCircle, Loader2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

const OTP_LENGTH = 6;
const OTP_EXPIRATION_SECONDS = 300; // 5 minutes
const RESEND_COOLDOWN_SECONDS = 60; // 1 minute

type Purpose = "password_reset" | "verify_phone";
type Channel = "sms" | "whatsapp" | "telegram";

interface VerifyOTPFormProps {
  identifier: string;
  purpose: Purpose;
  channel: Channel;
}

function OTPInput({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !value[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleChange = (index: number, inputValue: string) => {
    // Only accept digits
    const digit = inputValue.replace(/\D/g, "").slice(-1);

    const newValue = value.split("");
    newValue[index] = digit;
    const newOtp = newValue.join("");
    onChange(newOtp);

    // Move to next input if digit entered
    if (digit && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, OTP_LENGTH);
    onChange(pastedData.padEnd(OTP_LENGTH, ""));

    // Focus the next empty input or last input
    const nextIndex = Math.min(pastedData.length, OTP_LENGTH - 1);
    inputRefs.current[nextIndex]?.focus();
  };

  return (
    <div className="flex gap-2 justify-center" dir="ltr">
      {Array.from({ length: OTP_LENGTH }).map((_, index) => (
        <input
          key={index}
          ref={(el) => {
            inputRefs.current[index] = el;
          }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={value[index] || ""}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          disabled={disabled}
          className="w-12 h-14 text-center text-2xl font-bold border-2 border-gray-300 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-sahool-green-500 focus:border-transparent
                     disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
                     transition-colors"
          aria-label={`Digit ${index + 1}`}
        />
      ))}
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function getChannelLabel(channel: Channel): { ar: string; en: string } {
  const labels: Record<Channel, { ar: string; en: string }> = {
    sms: { ar: "رسالة نصية", en: "SMS" },
    whatsapp: { ar: "واتساب", en: "WhatsApp" },
    telegram: { ar: "تيليجرام", en: "Telegram" },
  };
  return labels[channel] || labels.sms;
}

function getPurposeLabel(purpose: Purpose): { ar: string; en: string } {
  const labels: Record<Purpose, { ar: string; en: string }> = {
    password_reset: { ar: "إعادة تعيين كلمة المرور", en: "Password Reset" },
    verify_phone: { ar: "التحقق من رقم الهاتف", en: "Phone Verification" },
  };
  return labels[purpose] || labels.verify_phone;
}

function VerifyOTPForm({ identifier, purpose, channel }: VerifyOTPFormProps) {
  const router = useRouter();
  const { showToast } = useToast();

  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [expirationTime, setExpirationTime] = useState(OTP_EXPIRATION_SECONDS);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [isResending, setIsResending] = useState(false);

  const channelLabel = getChannelLabel(channel);
  const purposeLabel = getPurposeLabel(purpose);

  // Expiration timer
  useEffect(() => {
    if (expirationTime <= 0 || isSuccess) return;

    const timer = setInterval(() => {
      setExpirationTime((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, [expirationTime, isSuccess]);

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;

    const timer = setInterval(() => {
      setResendCooldown((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, [resendCooldown]);

  const handleVerify = useCallback(async () => {
    if (otp.length !== OTP_LENGTH) {
      showToast({
        type: "error",
        messageAr: "الرجاء إدخال رمز التحقق كاملًا",
        message: "Please enter the complete verification code",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/auth/verify-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          identifier,
          otp,
          purpose,
          channel,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.error || "Verification failed");
      }

      setIsSuccess(true);
      showToast({
        type: "success",
        messageAr: "تم التحقق بنجاح",
        message: "Verification successful",
      });

      // Redirect based on purpose
      setTimeout(() => {
        if (purpose === "password_reset") {
          // For password reset, redirect to reset-password with token
          const resetToken = data.reset_token || data.resetToken;
          if (resetToken) {
            router.push(`/reset-password?token=${resetToken}`);
          } else {
            router.push("/login");
          }
        } else {
          // For phone verification, redirect to dashboard
          router.push("/dashboard");
        }
      }, 2000);
    } catch (error) {
      showToast({
        type: "error",
        messageAr: "رمز التحقق غير صحيح",
        message: error instanceof Error ? error.message : "Invalid verification code",
      });
    } finally {
      setIsLoading(false);
    }
  }, [otp, identifier, purpose, channel, router, showToast]);

  // Auto-submit when OTP is complete
  useEffect(() => {
    if (otp.length === OTP_LENGTH && !isLoading && !isSuccess) {
      handleVerify();
    }
  }, [otp, isLoading, isSuccess, handleVerify]);

  const handleResend = async () => {
    if (resendCooldown > 0 || isResending) return;

    setIsResending(true);

    try {
      const response = await fetch("/api/auth/send-otp", {
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
        throw new Error(data.message || data.error || "Failed to resend OTP");
      }

      setResendCooldown(RESEND_COOLDOWN_SECONDS);
      setExpirationTime(OTP_EXPIRATION_SECONDS);
      setOtp("");
      showToast({
        type: "success",
        messageAr: "تم إرسال رمز تحقق جديد",
        message: "New verification code sent",
      });
    } catch (error) {
      showToast({
        type: "error",
        messageAr: "فشل في إرسال رمز التحقق",
        message: error instanceof Error ? error.message : "Failed to resend code",
      });
    } finally {
      setIsResending(false);
    }
  };

  const isExpired = expirationTime === 0;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
      <Card className="w-full max-w-md" variant="elevated">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-sahool-green-100 rounded-full flex items-center justify-center mb-4">
            {isSuccess ? (
              <CheckCircle className="w-8 h-8 text-sahool-green-600" />
            ) : (
              <Shield className="w-8 h-8 text-sahool-green-600" />
            )}
          </div>
          <CardTitle className="text-2xl">
            <div>{isSuccess ? "تم التحقق بنجاح" : "التحقق من الرمز"}</div>
            <div className="text-base text-gray-600 mt-1">
              {isSuccess ? "Verification Successful" : "Verify Code"}
            </div>
          </CardTitle>
          <CardDescription>
            {isSuccess ? (
              <>
                <div className="text-gray-600">جاري التحويل...</div>
                <div className="text-xs text-gray-500 mt-1">Redirecting...</div>
              </>
            ) : (
              <>
                <div className="text-gray-600">
                  أدخل رمز التحقق المرسل عبر {channelLabel.ar} إلى
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Enter the verification code sent via {channelLabel.en} to
                </div>
                <div className="font-mono text-sahool-green-600 mt-2 text-lg" dir="ltr">
                  {identifier}
                </div>
                <div className="text-xs text-gray-500 mt-2">
                  <span className="font-semibold">{purposeLabel.ar}</span>
                  <span className="mx-1">•</span>
                  <span>{purposeLabel.en}</span>
                </div>
              </>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSuccess ? (
            <div className="text-center space-y-4">
              <Loader2 className="w-6 h-6 animate-spin text-sahool-green-600 mx-auto" />
              <p className="text-sm text-gray-600">
                {purpose === "password_reset" ? (
                  <>
                    سيتم توجيهك لإعادة تعيين كلمة المرور
                    <br />
                    <span className="text-xs">Redirecting to password reset...</span>
                  </>
                ) : (
                  <>
                    سيتم توجيهك للوحة التحكم
                    <br />
                    <span className="text-xs">Redirecting to dashboard...</span>
                  </>
                )}
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* OTP Input */}
              <OTPInput
                value={otp}
                onChange={setOtp}
                disabled={isLoading || isExpired}
              />

              {/* Timer */}
              <div className="flex items-center justify-center gap-2 text-sm">
                <Clock className={`w-4 h-4 ${isExpired ? "text-red-500" : "text-gray-500"}`} />
                {isExpired ? (
                  <span className="text-red-500">
                    <span>انتهت صلاحية الرمز</span>
                    <span className="mx-1">•</span>
                    <span className="text-xs">Code expired</span>
                  </span>
                ) : (
                  <span className="text-gray-600">
                    <span>صالح لمدة</span>
                    <span className="mx-1 font-mono font-semibold text-sahool-green-600">
                      {formatTime(expirationTime)}
                    </span>
                    <span className="text-xs">• Valid for {formatTime(expirationTime)}</span>
                  </span>
                )}
              </div>

              {/* Verify Button */}
              <Button
                onClick={handleVerify}
                fullWidth
                isLoading={isLoading}
                size="lg"
                disabled={otp.length !== OTP_LENGTH || isExpired}
              >
                <span className="font-semibold">تحقق من الرمز</span>
                <span className="mx-2">•</span>
                <span className="text-sm">Verify Code</span>
              </Button>

              {/* Resend Section */}
              <div className="text-center space-y-2">
                <p className="text-sm text-gray-600">
                  لم تستلم الرمز؟
                  <span className="mx-1">•</span>
                  <span className="text-xs">Didn&apos;t receive the code?</span>
                </p>
                <Button
                  variant="ghost"
                  onClick={handleResend}
                  disabled={resendCooldown > 0 || isResending}
                  className="text-sahool-green-600 hover:text-sahool-green-700"
                >
                  {isResending ? (
                    <Loader2 className="w-4 h-4 animate-spin me-2" />
                  ) : (
                    <RefreshCw className="w-4 h-4 me-2" />
                  )}
                  {resendCooldown > 0 ? (
                    <span>
                      <span>إعادة الإرسال بعد {formatTime(resendCooldown)}</span>
                      <span className="mx-1">•</span>
                      <span className="text-xs">Resend in {formatTime(resendCooldown)}</span>
                    </span>
                  ) : (
                    <span>
                      <span>إعادة إرسال الرمز</span>
                      <span className="mx-1">•</span>
                      <span className="text-xs">Resend Code</span>
                    </span>
                  )}
                </Button>
              </div>

              {/* Back to Login */}
              <div className="pt-4 border-t text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-2 text-sm text-sahool-green-600 hover:text-sahool-green-700 font-medium"
                >
                  <ArrowRight className="w-4 h-4 rotate-180" />
                  <span>العودة لتسجيل الدخول • Back to Login</span>
                </Link>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function VerifyOTPWithParams() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { showToast } = useToast();

  const identifier = searchParams.get("identifier") || "";
  const purpose = (searchParams.get("purpose") as Purpose) || "verify_phone";
  const channel = (searchParams.get("channel") as Channel) || "sms";

  // Validate required params
  useEffect(() => {
    if (!identifier) {
      showToast({
        type: "error",
        messageAr: "معرف غير صالح",
        message: "Invalid identifier",
      });
      router.push("/login");
    }
  }, [identifier, router, showToast]);

  if (!identifier) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-green-600" />
      </div>
    );
  }

  return (
    <VerifyOTPForm
      identifier={identifier}
      purpose={purpose}
      channel={channel}
    />
  );
}

export default function VerifyOTPClient() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white">
          <Loader2 className="w-8 h-8 animate-spin text-sahool-green-600" />
        </div>
      }
    >
      <VerifyOTPWithParams />
    </Suspense>
  );
}

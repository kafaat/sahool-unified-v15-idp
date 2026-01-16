"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Mail, ArrowRight, CheckCircle, MessageSquare, MessageCircle, Send, Phone } from "lucide-react";
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

type RecoveryChannel = "email" | "sms" | "whatsapp" | "telegram";

interface ChannelOption {
  id: RecoveryChannel;
  labelAr: string;
  labelEn: string;
  icon: React.ReactNode;
}

const CHANNEL_OPTIONS: ChannelOption[] = [
  { id: "email", labelAr: "البريد الإلكتروني", labelEn: "Email", icon: <Mail className="w-4 h-4" /> },
  { id: "sms", labelAr: "رسالة نصية", labelEn: "SMS", icon: <MessageSquare className="w-4 h-4" /> },
  { id: "whatsapp", labelAr: "واتساب", labelEn: "WhatsApp", icon: <MessageCircle className="w-4 h-4" /> },
  { id: "telegram", labelAr: "تيليجرام", labelEn: "Telegram", icon: <Send className="w-4 h-4" /> },
];

export default function ForgotPasswordClient() {
  const router = useRouter();
  const { showToast } = useToast();
  const [channel, setChannel] = useState<RecoveryChannel>("email");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const isEmailChannel = channel === "email";

  const getChannelDescription = () => {
    switch (channel) {
      case "sms":
        return { ar: "سيتم إرسال رمز التحقق عبر رسالة نصية", en: "OTP will be sent via SMS" };
      case "whatsapp":
        return { ar: "سيتم إرسال رمز التحقق عبر واتساب", en: "OTP will be sent via WhatsApp" };
      case "telegram":
        return { ar: "سيتم إرسال رمز التحقق عبر تيليجرام", en: "OTP will be sent via Telegram" };
      default:
        return { ar: "سيتم إرسال رابط إعادة التعيين", en: "Reset link will be sent" };
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isEmailChannel) {
        // Email channel - use existing forgot-password endpoint
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
      } else {
        // SMS/WhatsApp/Telegram - use send-otp endpoint
        const response = await fetch("/api/auth/send-otp", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            identifier: phone,
            channel,
            purpose: "password_reset",
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || data.error || "Failed to send OTP");
        }

        showToast({
          type: "success",
          messageAr: "تم إرسال رمز التحقق",
          message: "OTP sent successfully",
        });

        // Redirect to OTP verification page
        const params = new URLSearchParams({
          identifier: phone,
          purpose: "password_reset",
          channel,
        });
        router.push(`/verify-otp?${params.toString()}`);
      }
    } catch (error) {
      showToast({
        type: "error",
        messageAr: "فشل في إرسال الطلب",
        message: error instanceof Error ? error.message : "An error occurred",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const selectedChannel = CHANNEL_OPTIONS.find((opt) => opt.id === channel);
  const channelIcon = selectedChannel?.icon || <Mail className="w-8 h-8 text-sahool-green-600" />;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sahool-green-50 to-white p-4">
      <Card className="w-full max-w-md" variant="elevated">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-sahool-green-100 rounded-full flex items-center justify-center mb-4">
            {isSuccess ? (
              <CheckCircle className="w-8 h-8 text-sahool-green-600" />
            ) : (
              <span className="text-sahool-green-600 scale-[2]">{channelIcon}</span>
            )}
          </div>
          <CardTitle className="text-2xl">
            <div>{isSuccess ? "تم الإرسال" : "نسيت كلمة المرور؟"}</div>
            <div className="text-base text-gray-600 mt-1">
              {isSuccess ? "Sent Successfully" : "Forgot Password?"}
            </div>
          </CardTitle>
          <CardDescription>
            {isSuccess ? (
              <>
                <div className="text-gray-600">
                  {isEmailChannel
                    ? "إذا كان هناك حساب مرتبط بهذا البريد، فسيتم إرسال رابط إعادة التعيين"
                    : "تم إرسال رمز التحقق إلى رقمك"}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {isEmailChannel
                    ? "If an account exists with this email, a reset link has been sent"
                    : "OTP has been sent to your phone number"}
                </div>
              </>
            ) : (
              <>
                <div className="text-gray-600">
                  اختر طريقة استرداد الحساب
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Choose your recovery method
                </div>
              </>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSuccess ? (
            <div className="text-center space-y-4">
              <p className="text-sm text-gray-600">
                {isEmailChannel ? "الرابط صالح لمدة ساعة واحدة فقط" : "رمز التحقق صالح لمدة 10 دقائق"}
                <br />
                <span className="text-xs">
                  {isEmailChannel ? "The link is valid for 1 hour only" : "The OTP is valid for 10 minutes"}
                </span>
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
              {/* Channel Selector */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  طريقة الاسترداد
                  <span className="text-xs text-gray-500 mr-2">Recovery Method</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {CHANNEL_OPTIONS.map((option) => (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => setChannel(option.id)}
                      className={`flex items-center justify-center gap-2 p-3 rounded-lg border-2 transition-all ${
                        channel === option.id
                          ? "border-sahool-green-600 bg-sahool-green-50 text-sahool-green-700"
                          : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                      }`}
                    >
                      {option.icon}
                      <div className="flex flex-col items-start">
                        <span className="text-sm font-medium">{option.labelAr}</span>
                        <span className="text-xs text-gray-500">{option.labelEn}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Conditional Input based on channel */}
                {isEmailChannel ? (
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
                ) : (
                  <Input
                    type="tel"
                    label="Phone Number"
                    labelAr="رقم الهاتف"
                    placeholder="+966 5X XXX XXXX"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    leftIcon={<Phone className="w-4 h-4" />}
                    required
                    autoComplete="tel"
                  />
                )}

                {/* Channel-specific description */}
                <p className="text-xs text-gray-500 text-center">
                  {getChannelDescription().ar}
                  <br />
                  <span className="text-gray-400">{getChannelDescription().en}</span>
                </p>

                <Button type="submit" fullWidth isLoading={isLoading} size="lg">
                  <span className="font-semibold">
                    {isEmailChannel ? "إرسال رابط إعادة التعيين" : "إرسال رمز التحقق"}
                  </span>
                  <span className="mx-2">•</span>
                  <span className="text-sm">
                    {isEmailChannel ? "Send Reset Link" : "Send OTP"}
                  </span>
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

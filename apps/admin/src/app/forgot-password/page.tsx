"use client";

/**
 * SAHOOL Admin Forgot Password Page
 * صفحة نسيان كلمة المرور للوحة الإدارة
 *
 * Supports multi-channel OTP: Email, SMS, WhatsApp, Telegram
 */

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2, Mail, Leaf, ArrowRight, CheckCircle, MessageSquare, MessageCircle, Send, Phone } from "lucide-react";
import { API_BASE_URL } from "@/config/api";

type RecoveryChannel = "email" | "sms" | "whatsapp" | "telegram";

interface ChannelOption {
  id: RecoveryChannel;
  labelAr: string;
  labelEn: string;
  icon: React.ReactNode;
}

const CHANNEL_OPTIONS: ChannelOption[] = [
  { id: "email", labelAr: "البريد الإلكتروني", labelEn: "Email", icon: <Mail className="w-5 h-5" /> },
  { id: "sms", labelAr: "رسالة نصية", labelEn: "SMS", icon: <MessageSquare className="w-5 h-5" /> },
  { id: "whatsapp", labelAr: "واتساب", labelEn: "WhatsApp", icon: <MessageCircle className="w-5 h-5" /> },
  { id: "telegram", labelAr: "تيليجرام", labelEn: "Telegram", icon: <Send className="w-5 h-5" /> },
];

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [channel, setChannel] = useState<RecoveryChannel>("email");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const isEmailChannel = channel === "email";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      if (isEmailChannel) {
        // Email channel - use existing forgot-password endpoint
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/forgot-password`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || data.error || "فشل في إرسال طلب إعادة تعيين كلمة المرور");
        }

        setIsSuccess(true);
      } else {
        // SMS/WhatsApp/Telegram - use send-otp endpoint
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/send-otp`, {
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
          throw new Error(data.message || data.error || "فشل في إرسال رمز التحقق");
        }

        // Redirect to OTP verification page
        const params = new URLSearchParams({
          identifier: phone,
          purpose: "password_reset",
          channel,
        });
        router.push(`/verify-otp?${params.toString()}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "حدث خطأ غير متوقع");
    } finally {
      setIsLoading(false);
    }
  };

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

        {/* Forgot Password Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {isSuccess ? (
            /* Success State */
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                تم إرسال رابط إعادة التعيين
              </h2>
              <p className="text-gray-600 mb-6">
                إذا كان هناك حساب مرتبط بهذا البريد الإلكتروني، فسيتم إرسال رابط
                إعادة تعيين كلمة المرور إليه.
              </p>
              <p className="text-sm text-gray-500 mb-6">
                الرابط صالح لمدة ساعة واحدة فقط.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 text-green-600 font-medium hover:text-green-700"
              >
                <ArrowRight className="w-4 h-4" />
                العودة لتسجيل الدخول
              </Link>
            </div>
          ) : (
            /* Form State */
            <>
              <h2 className="text-xl font-semibold text-gray-900 mb-2 text-center">
                نسيت كلمة المرور؟
              </h2>
              <p className="text-gray-600 text-sm mb-6 text-center">
                اختر طريقة استرداد الحساب
                <br />
                <span className="text-xs text-gray-500">Choose your recovery method</span>
              </p>

              {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 text-sm">
                  {error}
                </div>
              )}

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
                          ? "border-green-600 bg-green-50 text-green-700"
                          : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                      }`}
                    >
                      {option.icon}
                      <span className="text-sm font-medium">{option.labelAr}</span>
                    </button>
                  ))}
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Email Field (shown for email channel) */}
                {isEmailChannel ? (
                  <div>
                    <label
                      htmlFor="email"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      البريد الإلكتروني
                      <span className="text-xs text-gray-500 mr-2">Email</span>
                    </label>
                    <div className="relative">
                      <Mail className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full pr-10 pl-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition"
                        placeholder="admin@sahool.io"
                        required
                        dir="ltr"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      سيتم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني
                    </p>
                  </div>
                ) : (
                  /* Phone Field (shown for SMS/WhatsApp/Telegram) */
                  <div>
                    <label
                      htmlFor="phone"
                      className="block text-sm font-medium text-gray-700 mb-2"
                    >
                      رقم الهاتف
                      <span className="text-xs text-gray-500 mr-2">Phone Number</span>
                    </label>
                    <div className="relative">
                      <Phone className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        id="phone"
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        className="w-full pr-10 pl-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition"
                        placeholder="+966 5X XXX XXXX"
                        required
                        dir="ltr"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {channel === "sms" && "سيتم إرسال رمز التحقق عبر رسالة نصية"}
                      {channel === "whatsapp" && "سيتم إرسال رمز التحقق عبر واتساب"}
                      {channel === "telegram" && "سيتم إرسال رمز التحقق عبر تيليجرام"}
                    </p>
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 focus:ring-4 focus:ring-green-200 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>جاري الإرسال...</span>
                    </>
                  ) : (
                    <span>
                      {isEmailChannel ? "إرسال رابط إعادة التعيين" : "إرسال رمز التحقق"}
                    </span>
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

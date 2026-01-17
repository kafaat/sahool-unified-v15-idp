"use client";

/**
 * SAHOOL Admin Security Settings - Two-Factor Authentication
 * إعدادات الأمان - المصادقة الثنائية
 */

import { useState, useEffect } from "react";
import { useAuth } from "@/stores/auth.store";
import { apiClient } from "@/lib/api-client";
import { validators, validationErrors } from "@/lib/validation";
import { logger } from "../../../lib/logger";
import {
  Shield,
  Smartphone,
  Key,
  AlertCircle,
  CheckCircle,
  Download,
  RefreshCw,
  XCircle,
  Loader2,
} from "lucide-react";

interface TwoFASetup {
  secret: string;
  qr_code: string;
  manual_entry_key: string;
  issuer: string;
  account_name: string;
}

interface TwoFAStatus {
  enabled: boolean;
  backup_codes_remaining: number;
}

interface TwoFAVerifyResponse {
  backup_codes: string[];
}

interface _BackupCode {
  code: string;
  used: boolean;
}

export default function SecuritySettingsPage() {
  const { user: _user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // 2FA status
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [backupCodesRemaining, setBackupCodesRemaining] = useState(0);

  // Setup flow
  const [showSetup, setShowSetup] = useState(false);
  const [setupData, setSetupData] = useState<TwoFASetup | null>(null);
  const [verificationCode, setVerificationCode] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  // Disable flow
  const [showDisable, setShowDisable] = useState(false);
  const [disableCode, setDisableCode] = useState("");

  // Load 2FA status
  useEffect(() => {
    loadTwoFAStatus();
  }, []);

  const loadTwoFAStatus = async () => {
    try {
      const response = await apiClient.get<TwoFAStatus>("/admin/2fa/status");
      if (response.success && response.data) {
        setTwoFAEnabled(response.data.enabled);
        setBackupCodesRemaining(response.data.backup_codes_remaining);
      }
    } catch (err) {
      logger.error("Error loading 2FA status:", err);
    }
  };

  const handleSetupStart = async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await apiClient.post<TwoFASetup>("/admin/2fa/setup");
      if (response.success && response.data) {
        setSetupData(response.data);
        setShowSetup(true);
      } else {
        setError(response.error || "فشل في بدء إعداد المصادقة الثنائية");
      }
    } catch (err) {
      setError("حدث خطأ أثناء إعداد المصادقة الثنائية");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyAndEnable = async () => {
    // Validate 2FA code format
    if (!validators.twoFactorCode(verificationCode)) {
      setError(validationErrors.twoFactorCode);
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await apiClient.post<TwoFAVerifyResponse>(
        "/admin/2fa/verify",
        {
          token: verificationCode,
        },
      );

      if (response.success && response.data) {
        setBackupCodes(response.data.backup_codes);
        setShowBackupCodes(true);
        setSuccess("تم تفعيل المصادقة الثنائية بنجاح!");
        setTwoFAEnabled(true);
        setShowSetup(false);
        await loadTwoFAStatus();
      } else {
        setError(response.error || "رمز التحقق غير صحيح");
      }
    } catch (err) {
      setError("حدث خطأ أثناء التحقق من الرمز");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisable = async () => {
    if (!disableCode) {
      setError("الرجاء إدخال رمز التحقق");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await apiClient.post("/admin/2fa/disable", {
        token: disableCode,
      });

      if (response.success) {
        setSuccess("تم تعطيل المصادقة الثنائية");
        setTwoFAEnabled(false);
        setShowDisable(false);
        setDisableCode("");
        await loadTwoFAStatus();
      } else {
        setError(response.error || "رمز التحقق غير صحيح");
      }
    } catch (err) {
      setError("حدث خطأ أثناء تعطيل المصادقة الثنائية");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerateBackupCodes = async () => {
    const code = prompt("أدخل رمز التحقق من تطبيق المصادقة:");
    if (!code) return;

    // Validate 2FA code format before sending
    if (!validators.twoFactorCode(code)) {
      setError(validationErrors.twoFactorCode);
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await apiClient.post<TwoFAVerifyResponse>(
        "/admin/2fa/backup-codes",
        {
          token: code,
        },
      );

      if (response.success && response.data) {
        setBackupCodes(response.data.backup_codes);
        setShowBackupCodes(true);
        setSuccess("تم إنشاء رموز النسخ الاحتياطي الجديدة");
        await loadTwoFAStatus();
      } else {
        setError(response.error || "رمز التحقق غير صحيح");
      }
    } catch (err) {
      setError("حدث خطأ أثناء إنشاء رموز النسخ الاحتياطي");
    } finally {
      setIsLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    const text = backupCodes.join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sahool-backup-codes.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Shield className="w-8 h-8 text-green-600" />
            إعدادات الأمان
          </h1>
          <p className="text-gray-600 mt-2">
            إدارة المصادقة الثنائية وحماية حسابك
          </p>
        </div>

        {/* Status Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p>{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-start gap-3">
            <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p>{success}</p>
          </div>
        )}

        {/* 2FA Status Card */}
        {!showSetup && !showBackupCodes && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  المصادقة الثنائية (2FA)
                </h2>
                <p className="text-gray-600 mb-4">
                  أضف طبقة إضافية من الأمان لحسابك باستخدام تطبيق المصادقة
                </p>

                {twoFAEnabled ? (
                  <div className="flex items-center gap-2 text-green-600 mb-4">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-medium">مفعّلة</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-gray-400 mb-4">
                    <XCircle className="w-5 h-5" />
                    <span className="font-medium">غير مفعّلة</span>
                  </div>
                )}

                {twoFAEnabled && (
                  <p className="text-sm text-gray-500">
                    رموز النسخ الاحتياطي المتبقية: {backupCodesRemaining}
                  </p>
                )}
              </div>

              <Smartphone className="w-12 h-12 text-green-600" />
            </div>

            <div className="mt-6 flex gap-3">
              {!twoFAEnabled ? (
                <button
                  onClick={handleSetupStart}
                  disabled={isLoading}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50 flex items-center gap-2"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Shield className="w-5 h-5" />
                  )}
                  تفعيل المصادقة الثنائية
                </button>
              ) : (
                <>
                  <button
                    onClick={() => setShowDisable(true)}
                    className="border border-red-300 text-red-600 px-6 py-2 rounded-lg hover:bg-red-50 transition"
                  >
                    تعطيل المصادقة الثنائية
                  </button>
                  <button
                    onClick={handleRegenerateBackupCodes}
                    disabled={isLoading}
                    className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition flex items-center gap-2"
                  >
                    <RefreshCw className="w-5 h-5" />
                    إنشاء رموز جديدة
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {/* Setup Flow */}
        {showSetup && setupData && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              إعداد المصادقة الثنائية
            </h2>

            <div className="space-y-6">
              {/* Step 1: Scan QR Code */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">
                  1. امسح رمز QR باستخدام تطبيق المصادقة
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  استخدم تطبيقات مثل Google Authenticator أو Authy
                </p>
                <div className="flex justify-center bg-gray-50 p-4 rounded-lg">
                  <img
                    src={setupData.qr_code}
                    alt="QR Code"
                    className="w-64 h-64"
                  />
                </div>
              </div>

              {/* Step 2: Manual Entry */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">
                  أو أدخل المفتاح يدوياً:
                </h3>
                <div className="flex items-center gap-3">
                  <code className="flex-1 bg-white px-4 py-2 rounded border border-gray-300 font-mono text-sm">
                    {setupData.manual_entry_key}
                  </code>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(setupData.manual_entry_key);
                      setSuccess("تم النسخ إلى الحافظة");
                    }}
                    className="px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50"
                  >
                    نسخ
                  </button>
                </div>
              </div>

              {/* Step 3: Verify Code */}
              <div>
                <h3 className="font-medium text-gray-900 mb-2">
                  2. أدخل رمز التحقق من التطبيق
                </h3>
                <input
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  value={verificationCode}
                  onChange={(e) => {
                    // Only allow digits, max 6 characters
                    const sanitized = e.target.value
                      .replace(/\D/g, "")
                      .slice(0, 6);
                    setVerificationCode(sanitized);
                  }}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-2xl tracking-widest"
                  placeholder="000000"
                  maxLength={6}
                  autoFocus
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={handleVerifyAndEnable}
                  disabled={isLoading || verificationCode.length !== 6}
                  className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                >
                  {isLoading ? "جاري التحقق..." : "تحقق وفعّل"}
                </button>
                <button
                  onClick={() => {
                    setShowSetup(false);
                    setSetupData(null);
                    setVerificationCode("");
                  }}
                  className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  إلغاء
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Backup Codes Display */}
        {showBackupCodes && backupCodes.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-start gap-3 mb-4">
              <Key className="w-6 h-6 text-yellow-600 flex-shrink-0" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  رموز النسخ الاحتياطي
                </h2>
                <p className="text-gray-600">
                  احفظ هذه الرموز في مكان آمن. يمكنك استخدام كل رمز مرة واحدة
                  فقط للدخول إذا فقدت الوصول لتطبيق المصادقة.
                </p>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <div className="grid grid-cols-2 gap-3">
                {backupCodes.map((code, index) => (
                  <code
                    key={index}
                    className="bg-white px-4 py-2 rounded border border-gray-300 font-mono text-center"
                  >
                    {code}
                  </code>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={downloadBackupCodes}
                className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download className="w-5 h-5" />
                تحميل الرموز
              </button>
              <button
                onClick={() => setShowBackupCodes(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                تم الحفظ
              </button>
            </div>
          </div>
        )}

        {/* Disable Confirmation */}
        {showDisable && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              تعطيل المصادقة الثنائية
            </h2>

            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-6">
              <p className="text-yellow-800">
                سيؤدي تعطيل المصادقة الثنائية إلى تقليل أمان حسابك. هل أنت
                متأكد؟
              </p>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                أدخل رمز التحقق أو رمز النسخ الاحتياطي
              </label>
              <input
                type="text"
                value={disableCode}
                onChange={(e) => setDisableCode(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                placeholder="000000 أو XXXX-XXXX"
                autoFocus
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleDisable}
                disabled={isLoading || !disableCode}
                className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition disabled:opacity-50"
              >
                {isLoading ? "جاري التعطيل..." : "تعطيل المصادقة الثنائية"}
              </button>
              <button
                onClick={() => {
                  setShowDisable(false);
                  setDisableCode("");
                }}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                إلغاء
              </button>
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="font-semibold text-blue-900 mb-3">
            ما هي المصادقة الثنائية؟
          </h3>
          <p className="text-blue-800 text-sm mb-3">
            المصادقة الثنائية (2FA) هي طبقة أمان إضافية تتطلب رمز تحقق بالإضافة
            إلى كلمة المرور عند تسجيل الدخول.
          </p>
          <ul className="text-blue-800 text-sm space-y-2">
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>حماية أفضل لحسابك من الوصول غير المصرح به</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>تطبيقات المصادقة أكثر أماناً من الرسائل النصية</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>رموز النسخ الاحتياطي للوصول في حالات الطوارئ</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

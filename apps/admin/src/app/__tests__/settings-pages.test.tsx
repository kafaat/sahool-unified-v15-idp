/**
 * Settings Pages - File Structure & Content Verification Tests
 * اختبارات صفحات الإعدادات - التحقق من بنية الملفات والمحتوى
 *
 * Tests: settings main page, security settings
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const APP_DIR = path.resolve(__dirname, '..');

function readPage(relativePath: string): string {
  const filePath = path.resolve(APP_DIR, relativePath);
  expect(fs.existsSync(filePath), `File not found: ${relativePath}`).toBe(true);
  return fs.readFileSync(filePath, 'utf-8');
}

// ─── Settings Main Page ──────────────────────────────────────────────────────

describe('Settings: Main Page', () => {
  const PAGE_PATH = 'settings/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function\s+SettingsPage/);
  });

  it('contains Arabic title and subtitle', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('الإعدادات');
    expect(content).toContain('إدارة إعدادات النظام والحساب');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/ui/Toast'");
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/DataTable'");
    expect(content).toContain("from '@/lib/utils'");
    expect(content).toContain("from '../../lib/logger'");
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('User');
    expect(content).toContain('Lock');
    expect(content).toContain('Bell');
    expect(content).toContain('Globe');
    expect(content).toContain('Shield');
    expect(content).toContain('Database');
    expect(content).toContain('Flag');
    expect(content).toContain('Save');
  });

  it('has tab navigation with four sections', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('selectedTab');
    expect(content).toContain("setSelectedTab('profile')");
    expect(content).toContain("setSelectedTab('preferences')");
    expect(content).toContain("setSelectedTab('system')");
    expect(content).toContain("setSelectedTab('users')");
  });

  it('has Arabic tab labels', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('الملف الشخصي');
    expect(content).toContain('إعدادات النظام');
    expect(content).toContain('إدارة المستخدمين');
  });

  it('has profile section with form fields', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('profileData');
    expect(content).toContain('محمد أحمد');
    expect(content).toContain('admin@sahool.io');
    expect(content).toContain('+967 777 123 456');
    expect(content).toContain('صنعاء، اليمن');
  });

  it('has password change section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تغيير كلمة المرور');
    expect(content).toContain('كلمة المرور القديمة');
    expect(content).toContain('كلمة المرور الجديدة');
    expect(content).toContain('تأكيد كلمة المرور');
    expect(content).toContain('passwordData');
  });

  it('has password visibility toggles', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('showOldPassword');
    expect(content).toContain('showNewPassword');
    expect(content).toContain('showConfirmPassword');
    expect(content).toContain('Eye');
    expect(content).toContain('EyeOff');
  });

  it('has notification preferences', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('الإشعارات');
    expect(content).toContain('emailNotifications');
    expect(content).toContain('smsNotifications');
    expect(content).toContain('pushNotifications');
    expect(content).toContain('weeklyReports');
    expect(content).toContain('criticalAlerts');
  });

  it('has system settings section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('systemSettings');
    expect(content).toContain('apiEndpoint');
    expect(content).toContain('maxUploadSize');
    expect(content).toContain('sessionTimeout');
    expect(content).toContain('maintenanceMode');
    expect(content).toContain('autoBackup');
  });

  it('has feature flags section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('featureFlags');
    expect(content).toContain('newDashboard');
    expect(content).toContain('aiDiagnosis');
  });

  it('has admin users management with mock data', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('mockAdmins');
    expect(content).toContain('محمد أحمد');
    expect(content).toContain('فاطمة سعيد');
    expect(content).toContain('علي حسن');
    expect(content).toContain('مدير النظام');
    expect(content).toContain('مشرف');
    expect(content).toContain('مدقق');
  });

  it('uses DataTable for admin users', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('DataTable');
    expect(content).toContain('admins');
  });

  it('has toast notifications for save actions', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تم حفظ الملف الشخصي بنجاح');
    expect(content).toContain('تم تغيير كلمة المرور بنجاح');
    expect(content).toContain('تم حفظ إعدادات النظام بنجاح');
  });

  it('validates password confirmation match', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('كلمة المرور الجديدة وتأكيد كلمة المرور غير متطابقين');
  });
});

// ─── Security Settings Page ──────────────────────────────────────────────────

describe('Settings: Security Page', () => {
  const PAGE_PATH = 'settings/security/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function\s+SecuritySettingsPage/);
  });

  it('contains Arabic labels for security settings', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('إعدادات الأمان');
    expect(content).toContain('إدارة المصادقة الثنائية وحماية حسابك');
    expect(content).toContain('المصادقة الثنائية (2FA)');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/stores/auth.store'");
    expect(content).toContain("from '@/lib/api'");
    expect(content).toContain("from '@/lib/validation'");
    expect(content).toContain("from '@/lib/logger'");
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('Shield');
    expect(content).toContain('Smartphone');
    expect(content).toContain('Key');
    expect(content).toContain('AlertCircle');
    expect(content).toContain('CheckCircle');
    expect(content).toContain('Download');
    expect(content).toContain('RefreshCw');
    expect(content).toContain('Loader2');
  });

  it('defines TwoFASetup interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface TwoFASetup');
    expect(content).toContain('secret');
    expect(content).toContain('qr_code');
    expect(content).toContain('manual_entry_key');
  });

  it('defines TwoFAStatus interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface TwoFAStatus');
    expect(content).toContain('enabled');
    expect(content).toContain('backup_codes_remaining');
  });

  it('defines TwoFAVerifyResponse interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface TwoFAVerifyResponse');
    expect(content).toContain('backup_codes');
  });

  it('has 2FA setup flow', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('handleSetupStart');
    expect(content).toContain('showSetup');
    expect(content).toContain('setupData');
    expect(content).toContain('تفعيل المصادقة الثنائية');
  });

  it('has 2FA verification step', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('handleVerifyAndEnable');
    expect(content).toContain('verificationCode');
    expect(content).toContain('تحقق وفعّل');
    expect(content).toContain("inputMode=\"numeric\"");
  });

  it('has 2FA disable flow', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('handleDisable');
    expect(content).toContain('showDisable');
    expect(content).toContain('disableCode');
    expect(content).toContain('تعطيل المصادقة الثنائية');
  });

  it('has backup codes management', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('backupCodes');
    expect(content).toContain('showBackupCodes');
    expect(content).toContain('handleRegenerateBackupCodes');
    expect(content).toContain('رموز النسخ الاحتياطي');
    expect(content).toContain('إنشاء رموز جديدة');
  });

  it('has backup codes download functionality', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('downloadBackupCodes');
    expect(content).toContain('sahool-backup-codes.txt');
    expect(content).toContain('تحميل الرموز');
  });

  it('shows 2FA enabled/disabled status', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('مفعّلة');
    expect(content).toContain('غير مفعّلة');
    expect(content).toContain('twoFAEnabled');
    expect(content).toContain('رموز النسخ الاحتياطي المتبقية');
  });

  it('has QR code display for setup', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('امسح رمز QR باستخدام تطبيق المصادقة');
    expect(content).toContain('Google Authenticator');
    expect(content).toContain('Authy');
    expect(content).toContain('setupData.qr_code');
  });

  it('has manual entry key option', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('أو أدخل المفتاح يدوياً');
    expect(content).toContain('manual_entry_key');
    expect(content).toContain('نسخ');
  });

  it('has error and success message display', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('error');
    expect(content).toContain('success');
    expect(content).toContain('تم تفعيل المصادقة الثنائية بنجاح');
    expect(content).toContain('تم تعطيل المصادقة الثنائية');
  });

  it('has informational section about 2FA', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('ما هي المصادقة الثنائية؟');
    expect(content).toContain('حماية أفضل لحسابك من الوصول غير المصرح به');
    expect(content).toContain('رموز النسخ الاحتياطي للوصول في حالات الطوارئ');
  });

  it('uses validation for 2FA codes', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('validators.twoFactorCode');
    expect(content).toContain('validationErrors.twoFactorCode');
  });

  it('calls correct API endpoints', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('/admin/2fa/status');
    expect(content).toContain('/admin/2fa/setup');
    expect(content).toContain('/admin/2fa/verify');
    expect(content).toContain('/admin/2fa/disable');
    expect(content).toContain('/admin/2fa/backup-codes');
  });

  it('has disable confirmation warning', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('سيؤدي تعطيل المصادقة الثنائية إلى تقليل أمان حسابك');
  });
});

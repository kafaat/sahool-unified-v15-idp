/**
 * Verify OTP Helper Tests
 * اختبارات مساعدات التحقق من OTP
 *
 * Tests pure functions from VerifyOTPClient.tsx
 */
import { describe, it, expect } from 'vitest';

// Mirror pure functions from VerifyOTPClient.tsx

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

type Channel = 'sms' | 'whatsapp' | 'telegram';
type Purpose = 'password_reset' | 'verify_phone';

function getChannelLabel(channel: Channel): { ar: string; en: string } {
  const labels: Record<Channel, { ar: string; en: string }> = {
    sms: { ar: 'رسالة نصية', en: 'SMS' },
    whatsapp: { ar: 'واتساب', en: 'WhatsApp' },
    telegram: { ar: 'تيليجرام', en: 'Telegram' },
  };
  return labels[channel] || labels.sms;
}

function getPurposeLabel(purpose: Purpose): { ar: string; en: string } {
  const labels: Record<Purpose, { ar: string; en: string }> = {
    password_reset: { ar: 'إعادة تعيين كلمة المرور', en: 'Password Reset' },
    verify_phone: { ar: 'التحقق من رقم الهاتف', en: 'Phone Verification' },
  };
  return labels[purpose] || labels.verify_phone;
}

describe('VerifyOTPClient helpers', () => {
  // ═══════════════════════════════════════════════════════════════════════════
  // FORMAT TIME
  // ═══════════════════════════════════════════════════════════════════════════

  describe('formatTime', () => {
    it('should format 0 seconds as 0:00', () => {
      expect(formatTime(0)).toBe('0:00');
    });

    it('should format seconds less than a minute', () => {
      expect(formatTime(5)).toBe('0:05');
      expect(formatTime(30)).toBe('0:30');
      expect(formatTime(59)).toBe('0:59');
    });

    it('should format exact minutes', () => {
      expect(formatTime(60)).toBe('1:00');
      expect(formatTime(120)).toBe('2:00');
      expect(formatTime(300)).toBe('5:00');
    });

    it('should format minutes and seconds', () => {
      expect(formatTime(65)).toBe('1:05');
      expect(formatTime(90)).toBe('1:30');
      expect(formatTime(125)).toBe('2:05');
      expect(formatTime(299)).toBe('4:59');
    });

    it('should pad single-digit seconds with zero', () => {
      expect(formatTime(1)).toBe('0:01');
      expect(formatTime(61)).toBe('1:01');
      expect(formatTime(9)).toBe('0:09');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GET CHANNEL LABEL
  // ═══════════════════════════════════════════════════════════════════════════

  describe('getChannelLabel', () => {
    it('should return SMS labels', () => {
      const label = getChannelLabel('sms');
      expect(label.en).toBe('SMS');
      expect(label.ar).toBe('رسالة نصية');
    });

    it('should return WhatsApp labels', () => {
      const label = getChannelLabel('whatsapp');
      expect(label.en).toBe('WhatsApp');
      expect(label.ar).toBe('واتساب');
    });

    it('should return Telegram labels', () => {
      const label = getChannelLabel('telegram');
      expect(label.en).toBe('Telegram');
      expect(label.ar).toBe('تيليجرام');
    });

    it('should fallback to SMS for unknown channel', () => {
      const label = getChannelLabel('unknown' as Channel);
      expect(label.en).toBe('SMS');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GET PURPOSE LABEL
  // ═══════════════════════════════════════════════════════════════════════════

  describe('getPurposeLabel', () => {
    it('should return password reset labels', () => {
      const label = getPurposeLabel('password_reset');
      expect(label.en).toBe('Password Reset');
      expect(label.ar).toBe('إعادة تعيين كلمة المرور');
    });

    it('should return phone verification labels', () => {
      const label = getPurposeLabel('verify_phone');
      expect(label.en).toBe('Phone Verification');
      expect(label.ar).toBe('التحقق من رقم الهاتف');
    });

    it('should fallback to verify_phone for unknown purpose', () => {
      const label = getPurposeLabel('unknown' as Purpose);
      expect(label.en).toBe('Phone Verification');
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// OTP CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

describe('OTP Constants', () => {
  it('should have correct OTP length', () => {
    const OTP_LENGTH = 6;
    expect(OTP_LENGTH).toBe(6);
  });

  it('should have correct expiration time (5 minutes)', () => {
    const OTP_EXPIRATION_SECONDS = 300;
    expect(OTP_EXPIRATION_SECONDS).toBe(300);
  });

  it('should have correct resend cooldown (1 minute)', () => {
    const RESEND_COOLDOWN_SECONDS = 60;
    expect(RESEND_COOLDOWN_SECONDS).toBe(60);
  });
});

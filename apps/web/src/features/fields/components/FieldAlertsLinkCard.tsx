'use client';

/**
 * FieldAlertsLinkCard
 * بطاقة ربط التنبيهات بالحقل
 *
 * Displays who will receive alerts for this field (the currently
 * authenticated user) and exposes a simple on/off toggle + an
 * optional per-field contact phone override. All state is stored
 * inside the existing `Field.metadata` JSONB column so no backend
 * migration or new endpoint is required — the parent component
 * PATCHes `field.metadata` via whatever update hook it already uses.
 *
 * Metadata shape (additive, forward-compatible):
 *
 *   field.metadata.alerts: {
 *     enabled: boolean;              // on/off toggle
 *     contactName?: string;          // snapshot at bind time
 *     contactEmail?: string;
 *     contactPhone?: string;         // optional override
 *     linkedAt: string;              // ISO timestamp
 *     channels?: {                   // per-channel opt-in
 *       sms?: boolean;
 *       email?: boolean;
 *       push?: boolean;
 *     };
 *   }
 *
 * The parent is responsible for calling the mutation to persist
 * changes — this component only renders and raises `onChange` with
 * the next full alert-metadata object.
 */

import React, { useMemo, useState } from 'react';
import { Bell, BellOff, Mail, Phone, User, Check } from 'lucide-react';

// ---------------------------------------------------------------------------
// Shapes
// ---------------------------------------------------------------------------

export interface FieldAlertsMetadata {
  enabled: boolean;
  contactName?: string;
  contactEmail?: string;
  contactPhone?: string;
  linkedAt?: string;
  channels?: {
    sms?: boolean;
    email?: boolean;
    push?: boolean;
  };
}

export interface FieldAlertsLinkCardProps {
  /**
   * Currently authenticated user. Typically pulled from `useAuth()`
   * so the card reflects whoever is logged-in right now.
   */
  user: {
    id: string;
    name: string;
    name_ar?: string;
    email: string;
    role?: string;
  } | null;

  /**
   * Raw metadata blob from the backend. Only `metadata.alerts` is
   * read; any other metadata keys are ignored.
   */
  metadata?: Record<string, unknown> | null;

  /**
   * Called whenever the user toggles alerts or edits the phone
   * override. Receives the full next `alerts` metadata object so the
   * parent can merge it into `field.metadata` and PATCH.
   */
  onChange?: (nextAlerts: FieldAlertsMetadata) => void;

  /**
   * Disable interaction (read-only mode). Useful for viewers who do
   * not have write access to the field.
   */
  readOnly?: boolean;
}

// ---------------------------------------------------------------------------
// Metadata reader
// ---------------------------------------------------------------------------

function readAlertsFromMetadata(
  metadata: Record<string, unknown> | null | undefined,
): FieldAlertsMetadata {
  const defaultAlerts: FieldAlertsMetadata = {
    enabled: true,
    channels: { sms: true, email: true, push: false },
  };
  if (!metadata) return defaultAlerts;
  const raw = (metadata as Record<string, unknown>).alerts;
  if (!raw || typeof raw !== 'object') return defaultAlerts;
  const obj = raw as Record<string, unknown>;
  return {
    enabled: obj.enabled !== false, // default true unless explicitly disabled
    contactName: typeof obj.contactName === 'string' ? obj.contactName : undefined,
    contactEmail:
      typeof obj.contactEmail === 'string' ? obj.contactEmail : undefined,
    contactPhone:
      typeof obj.contactPhone === 'string' ? obj.contactPhone : undefined,
    linkedAt: typeof obj.linkedAt === 'string' ? obj.linkedAt : undefined,
    channels:
      obj.channels && typeof obj.channels === 'object'
        ? {
            sms: (obj.channels as Record<string, unknown>).sms !== false,
            email:
              (obj.channels as Record<string, unknown>).email !== false,
            push: (obj.channels as Record<string, unknown>).push === true,
          }
        : defaultAlerts.channels,
  };
}

// ---------------------------------------------------------------------------
// Public helper: seed alerts metadata at field-creation time
// ---------------------------------------------------------------------------

export function buildInitialFieldAlerts(user: {
  name?: string;
  name_ar?: string;
  email?: string;
  phone?: string;
}): FieldAlertsMetadata {
  return {
    enabled: true,
    contactName: user.name_ar ?? user.name,
    contactEmail: user.email,
    contactPhone: user.phone,
    linkedAt: new Date().toISOString(),
    channels: { sms: true, email: true, push: false },
  };
}

// ---------------------------------------------------------------------------
// Loose phone validation — E.164-ish, lenient for local formats
// ---------------------------------------------------------------------------

const PHONE_REGEX = /^[+]?[0-9\s()-]{7,20}$/;

function isAcceptablePhone(raw: string): boolean {
  return PHONE_REGEX.test(raw.trim());
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const FieldAlertsLinkCard: React.FC<FieldAlertsLinkCardProps> = ({
  user,
  metadata,
  onChange,
  readOnly = false,
}) => {
  const initial = useMemo(() => readAlertsFromMetadata(metadata), [metadata]);
  const [enabled, setEnabled] = useState<boolean>(initial.enabled);
  const [phone, setPhone] = useState<string>(
    initial.contactPhone ?? '',
  );
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [isEditingPhone, setIsEditingPhone] = useState<boolean>(false);
  const [channels, setChannels] = useState(
    initial.channels ?? { sms: true, email: true, push: false },
  );

  const displayName = user?.name_ar?.trim() || user?.name?.trim() || '—';
  const displayEmail = user?.email ?? '—';

  const emit = (patch: Partial<FieldAlertsMetadata>) => {
    if (!onChange) return;
    onChange({
      enabled,
      contactName: displayName,
      contactEmail: displayEmail,
      contactPhone: phone.trim() || undefined,
      linkedAt: initial.linkedAt ?? new Date().toISOString(),
      channels,
      ...patch,
    });
  };

  const handleToggle = () => {
    if (readOnly) return;
    const next = !enabled;
    setEnabled(next);
    emit({ enabled: next });
  };

  const handleSavePhone = () => {
    const trimmed = phone.trim();
    if (trimmed && !isAcceptablePhone(trimmed)) {
      setPhoneError('صيغة رقم الهاتف غير صحيحة');
      return;
    }
    setPhoneError(null);
    setIsEditingPhone(false);
    emit({ contactPhone: trimmed || undefined });
  };

  const handleChannelToggle = (key: 'sms' | 'email' | 'push') => {
    if (readOnly) return;
    const next = { ...channels, [key]: !channels[key] };
    setChannels(next);
    emit({ channels: next });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {enabled ? (
            <Bell className="w-5 h-5 text-emerald-600" />
          ) : (
            <BellOff className="w-5 h-5 text-gray-400" />
          )}
          <h3 className="font-semibold text-gray-900">التنبيهات والتواصل</h3>
        </div>
        <button
          type="button"
          onClick={handleToggle}
          disabled={readOnly}
          aria-pressed={enabled}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            enabled ? 'bg-emerald-600' : 'bg-gray-300'
          } ${readOnly ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          aria-label={enabled ? 'إيقاف التنبيهات' : 'تفعيل التنبيهات'}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              enabled ? '-translate-x-5' : '-translate-x-1'
            }`}
          />
        </button>
      </div>

      {/* Status line */}
      <p className="text-xs text-gray-600 mb-3">
        {enabled
          ? 'ستُرسل تنبيهات هذا الحقل إلى معلومات حسابك أدناه. يمكنك تعطيل التنبيهات في أي وقت.'
          : 'التنبيهات موقوفة لهذا الحقل حالياً.'}
      </p>

      {/* Identity panel — ربط اسم المستخدم والبريد الإلكتروني */}
      <div className="space-y-2 bg-gray-50 rounded-md border border-gray-200 p-3 text-sm">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-gray-700">
            <User className="w-4 h-4 text-gray-500" aria-hidden="true" />
            <span className="text-xs text-gray-500">الاسم</span>
          </div>
          <span className="font-medium text-gray-900 truncate">
            {displayName}
          </span>
        </div>

        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-gray-700">
            <Mail className="w-4 h-4 text-gray-500" aria-hidden="true" />
            <span className="text-xs text-gray-500">البريد الإلكتروني</span>
          </div>
          <span className="font-medium text-gray-900 truncate" dir="ltr">
            {displayEmail}
          </span>
        </div>

        {/* Phone row with inline edit */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-gray-700">
            <Phone className="w-4 h-4 text-gray-500" aria-hidden="true" />
            <span className="text-xs text-gray-500">رقم الهاتف</span>
          </div>
          {isEditingPhone && !readOnly ? (
            <div className="flex items-center gap-1 flex-1 justify-start max-w-[240px]">
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value.slice(0, 20))}
                placeholder="+966 5X XXX XXXX"
                dir="ltr"
                maxLength={20}
                className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-emerald-500"
                aria-label="رقم الهاتف للتنبيهات"
              />
              <button
                type="button"
                onClick={handleSavePhone}
                className="p-1 bg-emerald-600 text-white rounded hover:bg-emerald-700"
                aria-label="حفظ رقم الهاتف"
              >
                <Check className="w-3 h-3" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => !readOnly && setIsEditingPhone(true)}
              disabled={readOnly}
              className={`font-medium text-gray-900 ${
                readOnly ? 'cursor-default' : 'hover:text-emerald-700 cursor-pointer'
              }`}
              dir="ltr"
            >
              {phone.trim() || <span className="text-gray-400">— اضغط للإضافة —</span>}
            </button>
          )}
        </div>
        {phoneError && (
          <p className="text-xs text-red-600 text-right">{phoneError}</p>
        )}
      </div>

      {/* Channel preferences */}
      {enabled && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500 mb-2">قنوات الإرسال:</p>
          <div className="flex flex-wrap gap-2">
            {(
              [
                { key: 'sms', label: 'رسالة نصية (SMS)' },
                { key: 'email', label: 'البريد الإلكتروني' },
                { key: 'push', label: 'إشعارات التطبيق' },
              ] as Array<{ key: 'sms' | 'email' | 'push'; label: string }>
            ).map(({ key, label }) => {
              const active = !!channels[key];
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => handleChannelToggle(key)}
                  disabled={readOnly}
                  aria-pressed={active}
                  className={`inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-full border transition-colors ${
                    active
                      ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  } ${readOnly ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
                >
                  {active && <Check className="w-3 h-3" aria-hidden="true" />}
                  <span>{label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default FieldAlertsLinkCard;

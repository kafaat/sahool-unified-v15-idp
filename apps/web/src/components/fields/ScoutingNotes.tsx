'use client';

/**
 * Scouting Notes — ملاحظات الفحص الميداني
 * GPS-pinned field notes with category filters, severity badges,
 * photo placeholders, and coordinate display.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { clsx } from 'clsx';
import {
  MapPin,
  Plus,
  Clock,
  User,
  ChevronDown,
  X,
  Camera,
  Filter,
  Navigation,
  ImageIcon,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ScoutingNote {
  id: string;
  lat: number;
  lng: number;
  category: 'disease' | 'pest' | 'weed' | 'irrigation' | 'nutrient' | 'other';
  text: string;
  textAr: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  createdBy?: string;
  photoUrl?: string;
}

export interface ScoutingNotesProps {
  fieldId: string;
  notes: ScoutingNote[];
  onAddNote?: (note: Omit<ScoutingNote, 'id' | 'createdAt'>) => void;
  className?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CATEGORY_CONFIG: Record<
  ScoutingNote['category'],
  { icon: string; labelAr: string; labelEn: string; color: string; iconColor: string }
> = {
  disease: {
    icon: '\u{1F9A0}',
    labelAr: 'مرض',
    labelEn: 'Disease',
    color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    iconColor: 'text-red-500',
  },
  pest: {
    icon: '\u{1F41B}',
    labelAr: 'آفة',
    labelEn: 'Pest',
    color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    iconColor: 'text-orange-500',
  },
  weed: {
    icon: '\u{1F33F}',
    labelAr: 'اعشاب ضارة',
    labelEn: 'Weed',
    color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    iconColor: 'text-green-500',
  },
  irrigation: {
    icon: '\u{1F4A7}',
    labelAr: 'ري',
    labelEn: 'Irrigation',
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    iconColor: 'text-blue-500',
  },
  nutrient: {
    icon: '\u2697\uFE0F',
    labelAr: 'تغذية',
    labelEn: 'Nutrient',
    color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    iconColor: 'text-purple-500',
  },
  other: {
    icon: '\u{1F4DD}',
    labelAr: 'اخرى',
    labelEn: 'Other',
    color: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
    iconColor: 'text-gray-500',
  },
};

const SEVERITY_CONFIG: Record<
  ScoutingNote['severity'],
  { labelAr: string; dot: string; bg: string; border: string }
> = {
  low: {
    labelAr: 'منخفض',
    dot: 'bg-green-500',
    bg: 'bg-green-50 dark:bg-green-900/20',
    border: 'border-green-200 dark:border-green-800',
  },
  medium: {
    labelAr: 'متوسط',
    dot: 'bg-yellow-500',
    bg: 'bg-yellow-50 dark:bg-yellow-900/20',
    border: 'border-yellow-200 dark:border-yellow-800',
  },
  high: {
    labelAr: 'مرتفع',
    dot: 'bg-orange-500',
    bg: 'bg-orange-50 dark:bg-orange-900/20',
    border: 'border-orange-200 dark:border-orange-800',
  },
  critical: {
    labelAr: 'حرج',
    dot: 'bg-red-500',
    bg: 'bg-red-50 dark:bg-red-900/20',
    border: 'border-red-200 dark:border-red-800',
  },
};

const CATEGORIES = Object.keys(CATEGORY_CONFIG) as ScoutingNote['category'][];
const SEVERITIES = Object.keys(SEVERITY_CONFIG) as ScoutingNote['severity'][];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatRelativeTime(dateStr: string): string {
  const diffMs = Date.now() - new Date(dateStr).getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'الآن';
  if (diffMin < 60) return `منذ ${diffMin} د`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `منذ ${diffHr} س`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 30) return `منذ ${diffDay} ي`;
  return new Date(dateStr).toLocaleDateString('ar-SA');
}

function formatCoordinate(value: number, type: 'lat' | 'lng'): string {
  const dir = type === 'lat' ? (value >= 0 ? 'N' : 'S') : value >= 0 ? 'E' : 'W';
  return `${Math.abs(value).toFixed(5)}\u00B0${dir}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ScoutingNotes({
  fieldId,
  notes,
  onAddNote,
  className,
}: ScoutingNotesProps) {
  const [showForm, setShowForm] = useState(false);
  const [filterCategory, setFilterCategory] = useState<ScoutingNote['category'] | 'all'>('all');
  const [formCategory, setFormCategory] = useState<ScoutingNote['category']>('disease');
  const [formSeverity, setFormSeverity] = useState<ScoutingNote['severity']>('medium');
  const [formText, setFormText] = useState('');
  const [formTextAr, setFormTextAr] = useState('');
  const [formLat, setFormLat] = useState('24.7136');
  const [formLng, setFormLng] = useState('46.6753');

  const filteredNotes = useMemo(() => {
    if (filterCategory === 'all') return notes;
    return notes.filter((n) => n.category === filterCategory);
  }, [notes, filterCategory]);

  const resetForm = useCallback(() => {
    setFormCategory('disease');
    setFormSeverity('medium');
    setFormText('');
    setFormTextAr('');
    setFormLat('24.7136');
    setFormLng('46.6753');
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (!onAddNote) return;
      if (!formText.trim() && !formTextAr.trim()) return;

      onAddNote({
        lat: parseFloat(formLat) || 0,
        lng: parseFloat(formLng) || 0,
        category: formCategory,
        text: formText.trim(),
        textAr: formTextAr.trim(),
        severity: formSeverity,
      });

      resetForm();
      setShowForm(false);
    },
    [onAddNote, formLat, formLng, formCategory, formText, formTextAr, formSeverity, resetForm],
  );

  const handleCancel = useCallback(() => {
    resetForm();
    setShowForm(false);
  }, [resetForm]);

  return (
    <div dir="rtl" className={clsx('space-y-4', className)}>
      {/* ---- Header ---- */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5 text-green-600 dark:text-green-400" />
          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">
            ملاحظات الفحص الميداني
          </h3>
          <span className="text-xs text-gray-500 dark:text-gray-400">Scouting Notes</span>
          {notes.length > 0 && (
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 text-xs font-medium text-green-700 dark:text-green-300">
              {notes.length}
            </span>
          )}
        </div>

        {onAddNote && !showForm && (
          <button
            type="button"
            onClick={() => setShowForm(true)}
            className={clsx(
              'inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg transition',
              'text-white bg-green-600 hover:bg-green-700',
              'focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
            )}
          >
            <Plus className="w-4 h-4" />
            اضافة ملاحظة
          </button>
        )}
      </div>

      {/* ---- Category filter ---- */}
      {notes.length > 0 && !showForm && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <Filter className="w-3.5 h-3.5 text-gray-400 shrink-0" />
          <button
            type="button"
            onClick={() => setFilterCategory('all')}
            className={clsx(
              'whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium transition',
              filterCategory === 'all'
                ? 'bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-800'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700',
            )}
          >
            الكل ({notes.length})
          </button>
          {CATEGORIES.map((cat) => {
            const cfg = CATEGORY_CONFIG[cat];
            const count = notes.filter((n) => n.category === cat).length;
            if (count === 0) return null;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => setFilterCategory(cat)}
                className={clsx(
                  'whitespace-nowrap rounded-full px-3 py-1 text-xs font-medium transition',
                  filterCategory === cat
                    ? cfg.color
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700',
                )}
              >
                {cfg.icon} {cfg.labelAr} ({count})
              </button>
            );
          })}
        </div>
      )}

      {/* ---- Add Note Form ---- */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          className={clsx(
            'p-4 rounded-xl border space-y-4',
            'bg-white dark:bg-gray-800',
            'border-green-200 dark:border-green-800',
            'shadow-sm',
          )}
        >
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              ملاحظة جديدة | New Note
            </h4>
            <button
              type="button"
              onClick={handleCancel}
              className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              aria-label="اغلاق"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Category + Severity */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label
                htmlFor="scouting-cat"
                className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                التصنيف | Category
              </label>
              <div className="relative">
                <select
                  id="scouting-cat"
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value as ScoutingNote['category'])}
                  className={clsx(
                    'w-full px-3 py-2 rounded-lg border text-sm appearance-none',
                    'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                    'border-gray-300 dark:border-gray-600',
                    'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                  )}
                >
                  {CATEGORIES.map((cat) => {
                    const cfg = CATEGORY_CONFIG[cat];
                    return (
                      <option key={cat} value={cat}>
                        {cfg.icon} {cfg.labelAr} - {cfg.labelEn}
                      </option>
                    );
                  })}
                </select>
                <ChevronDown className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                الشدة | Severity
              </label>
              <div className="flex gap-1.5">
                {SEVERITIES.map((sev) => {
                  const cfg = SEVERITY_CONFIG[sev];
                  const isActive = formSeverity === sev;
                  return (
                    <button
                      key={sev}
                      type="button"
                      onClick={() => setFormSeverity(sev)}
                      className={clsx(
                        'flex-1 px-2 py-1.5 text-xs font-medium rounded-lg border transition',
                        isActive
                          ? clsx(cfg.bg, cfg.border, 'ring-1 ring-offset-1 ring-current')
                          : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600',
                      )}
                    >
                      <span className={clsx('inline-block w-2 h-2 rounded-full ml-1', cfg.dot)} />
                      {cfg.labelAr}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* GPS Coordinates */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label
                htmlFor="scouting-lat"
                className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                <Navigation className="h-3 w-3 inline ml-1" />
                خط العرض | Lat
              </label>
              <input
                id="scouting-lat"
                type="text"
                dir="ltr"
                value={formLat}
                onChange={(e) => setFormLat(e.target.value)}
                className={clsx(
                  'w-full px-3 py-2 rounded-lg border text-sm font-mono',
                  'bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                )}
              />
            </div>
            <div>
              <label
                htmlFor="scouting-lng"
                className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                <Navigation className="h-3 w-3 inline ml-1" />
                خط الطول | Lng
              </label>
              <input
                id="scouting-lng"
                type="text"
                dir="ltr"
                value={formLng}
                onChange={(e) => setFormLng(e.target.value)}
                className={clsx(
                  'w-full px-3 py-2 rounded-lg border text-sm font-mono',
                  'bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition',
                )}
              />
            </div>
          </div>

          {/* Photo placeholder */}
          <div>
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              <Camera className="h-3 w-3 inline ml-1" />
              صورة | Photo
            </label>
            <div
              className={clsx(
                'flex items-center justify-center h-24 rounded-lg border-2 border-dashed cursor-pointer transition',
                'border-gray-300 dark:border-gray-600',
                'hover:border-green-400 dark:hover:border-green-600',
                'bg-gray-50 dark:bg-gray-700/50',
              )}
            >
              <div className="text-center">
                <ImageIcon className="h-6 w-6 mx-auto text-gray-400 dark:text-gray-500" />
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  اضغط لاضافة صورة
                </p>
              </div>
            </div>
          </div>

          {/* Text areas */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label
                htmlFor="scouting-text-ar"
                className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                الملاحظة (عربي)
              </label>
              <textarea
                id="scouting-text-ar"
                dir="rtl"
                rows={3}
                value={formTextAr}
                onChange={(e) => setFormTextAr(e.target.value)}
                placeholder="اكتب ملاحظتك هنا..."
                className={clsx(
                  'w-full px-3 py-2 rounded-lg border text-sm resize-none',
                  'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500',
                  'placeholder:text-gray-400 dark:placeholder:text-gray-500 transition',
                )}
              />
            </div>
            <div>
              <label
                htmlFor="scouting-text-en"
                className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                Note (English)
              </label>
              <textarea
                id="scouting-text-en"
                dir="ltr"
                rows={3}
                value={formText}
                onChange={(e) => setFormText(e.target.value)}
                placeholder="Write your note here..."
                className={clsx(
                  'w-full px-3 py-2 rounded-lg border text-sm resize-none',
                  'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                  'border-gray-300 dark:border-gray-600',
                  'focus:ring-2 focus:ring-green-500 focus:border-green-500',
                  'placeholder:text-gray-400 dark:placeholder:text-gray-500 transition',
                )}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 pt-1">
            <button
              type="button"
              onClick={handleCancel}
              className={clsx(
                'px-4 py-2 text-sm font-medium rounded-lg transition',
                'text-gray-700 dark:text-gray-300',
                'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600',
              )}
            >
              الغاء
            </button>
            <button
              type="submit"
              disabled={!formText.trim() && !formTextAr.trim()}
              className={clsx(
                'px-4 py-2 text-sm font-medium text-white rounded-lg transition',
                'bg-green-600 hover:bg-green-700',
                'focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'flex items-center gap-1.5',
              )}
            >
              <Plus className="w-4 h-4" />
              حفظ الملاحظة
            </button>
          </div>
        </form>
      )}

      {/* ---- Notes List ---- */}
      {filteredNotes.length === 0 && !showForm ? (
        <div className="py-12 text-center rounded-xl border border-dashed border-gray-300 dark:border-gray-600">
          <MapPin className="w-8 h-8 mx-auto text-gray-300 dark:text-gray-600 mb-2" />
          <p className="text-sm text-gray-500 dark:text-gray-400">لا توجد ملاحظات بعد</p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            No scouting notes yet for field {fieldId}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredNotes.map((note) => {
            const catCfg = CATEGORY_CONFIG[note.category];
            const sevCfg = SEVERITY_CONFIG[note.severity];

            return (
              <div
                key={note.id}
                className={clsx(
                  'p-3.5 rounded-xl border transition',
                  'bg-white dark:bg-gray-800',
                  sevCfg.border,
                  'hover:shadow-sm',
                )}
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={clsx(
                        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                        catCfg.color,
                      )}
                    >
                      <span>{catCfg.icon}</span>
                      {catCfg.labelAr}
                    </span>
                    <span
                      className={clsx(
                        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border',
                        sevCfg.bg,
                        sevCfg.border,
                      )}
                    >
                      <span className={clsx('w-1.5 h-1.5 rounded-full', sevCfg.dot)} />
                      {sevCfg.labelAr}
                    </span>
                  </div>

                  {/* Coordinates */}
                  <div className="flex items-center gap-1 text-[11px] font-mono text-gray-400 dark:text-gray-500 flex-shrink-0" dir="ltr">
                    <MapPin className="w-3 h-3" />
                    {formatCoordinate(note.lat, 'lat')}, {formatCoordinate(note.lng, 'lng')}
                  </div>
                </div>

                {/* Photo placeholder */}
                {note.photoUrl ? (
                  <div className="mb-2 h-32 rounded-lg bg-gray-100 dark:bg-gray-700 overflow-hidden">
                    <img
                      src={note.photoUrl}
                      alt="صورة الملاحظة"
                      className="w-full h-full object-cover"
                    />
                  </div>
                ) : (
                  <div className="mb-2 h-20 rounded-lg bg-gray-50 dark:bg-gray-700/50 flex items-center justify-center border border-dashed border-gray-200 dark:border-gray-600">
                    <div className="text-center">
                      <Camera className="h-4 w-4 mx-auto text-gray-300 dark:text-gray-500" />
                      <p className="text-[10px] text-gray-300 dark:text-gray-500 mt-0.5">
                        لا توجد صورة
                      </p>
                    </div>
                  </div>
                )}

                {/* Text */}
                {note.textAr && (
                  <p className="text-sm text-gray-800 dark:text-gray-200 mb-1">{note.textAr}</p>
                )}
                {note.text && (
                  <p className="text-sm text-gray-500 dark:text-gray-400" dir="ltr">
                    {note.text}
                  </p>
                )}

                {/* Footer */}
                <div className="flex items-center gap-3 mt-2.5 pt-2 border-t border-gray-100 dark:border-gray-700">
                  <span className="inline-flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                    <Clock className="w-3 h-3" />
                    {formatRelativeTime(note.createdAt)}
                  </span>
                  {note.createdBy && (
                    <span className="inline-flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                      <User className="w-3 h-3" />
                      {note.createdBy}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

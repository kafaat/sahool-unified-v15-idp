'use client';

/**
 * SAHOOL Field Form Component
 * مكون نموذج الحقل
 */

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Save, X, MapPin, Info } from 'lucide-react';
import { useLocale } from 'next-intl';
import { useFarms } from '@/features/farms';
import { YEMEN_GOVERNORATES } from '@/data/yemen-locations';
import type { Field, FieldFormData, GeoPolygon } from '../types';

// Dynamic import – no SSR for Leaflet
const GoogleMapsFieldDrawer = dynamic(
  () => import('@/components/maps/LeafletFieldDrawer'),
  { ssr: false, loading: () => <div className="h-[calc(100vh-320px)] min-h-[400px] bg-gray-100 rounded-lg animate-pulse" /> }
);

interface FieldFormProps {
  field?: Field;
  onSubmit: (data: FieldFormData) => void | Promise<void>;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

const MAX_NAME_LENGTH = 255;
const MIN_NAME_LENGTH = 2;

export const FieldForm: React.FC<FieldFormProps> = ({
  field,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const locale = useLocale();
  const isRtl = locale === 'ar';

  const { data: farms = [] } = useFarms();

  const [tab, setTab] = useState<'info' | 'boundary'>('info');
  const [mapFlyTo, setMapFlyTo] = useState<[number, number] | null>(null);
  const [mapFlyZoom, setMapFlyZoom] = useState(11);
  const [formData, setFormData] = useState<FieldFormData>({
    name:          field?.name          || '',
    nameAr:        field?.nameAr        || '',
    area:          field?.area          || 0,
    crop:          field?.crop          || '',
    cropAr:        field?.cropAr        || '',
    description:   field?.description   || '',
    descriptionAr: field?.descriptionAr || '',
    farmId:        field?.farmId        || '',
    polygon:       field?.polygon,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    const trimmedName = (formData.nameAr || formData.name).trim();
    if (!trimmedName) {
      newErrors.nameAr = isRtl ? 'اسم الحقل مطلوب' : 'Field name is required';
    } else if (trimmedName.length < MIN_NAME_LENGTH) {
      newErrors.nameAr = isRtl
        ? `الاسم قصير جداً (الحد الأدنى ${MIN_NAME_LENGTH} أحرف)`
        : `Name too short (min ${MIN_NAME_LENGTH} chars)`;
    } else if (trimmedName.length > MAX_NAME_LENGTH) {
      newErrors.nameAr = isRtl
        ? `الاسم طويل جداً (الحد الأقصى ${MAX_NAME_LENGTH} حرف)`
        : `Name too long (max ${MAX_NAME_LENGTH} chars)`;
    }

    const coords = formData.polygon?.coordinates?.[0];
    if (!coords || coords.length < 4) {
      newErrors.polygon = isRtl
        ? 'يجب رسم حدود الحقل (3 نقاط على الأقل)'
        : 'Field boundary required (at least 3 points)';
    }

    setErrors(newErrors);

    if (newErrors.nameAr) setTab('info');
    else if (newErrors.polygon) setTab('boundary');

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    const name = (formData.nameAr || formData.name).trim();
    // Both name fields carry the same value — the backend stores both columns
    await onSubmit({ ...formData, name, nameAr: name });
  };

  const handleChange = <K extends keyof FieldFormData>(key: K, value: FieldFormData[K]) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    if (errors[key as string]) {
      setErrors((prev) => { const e = { ...prev }; delete e[key as string]; return e; });
    }
  };

  /** Single name input writes to both name and nameAr */
  const handleNameChange = (val: string) => {
    setFormData((prev) => ({ ...prev, name: val, nameAr: val }));
    if (errors.nameAr) setErrors((prev) => { const e = { ...prev }; delete e.nameAr; return e; });
  };

  /** Single crop selection writes to both crop and cropAr */
  const handleCropChange = (val: string) => {
    setFormData((prev) => ({ ...prev, crop: val, cropAr: val }));
  };

  /** Single description input writes to both description and descriptionAr */
  const handleDescChange = (val: string) => {
    setFormData((prev) => ({ ...prev, description: val, descriptionAr: val }));
  };

  /** When a farm is selected, resolve its center so the boundary tab opens there */
  const handleFarmChange = (farmId: string) => {
    handleChange('farmId', farmId);
    if (!farmId) { setMapFlyTo(null); return; }

    const farm = farms.find((f) => f.id === farmId);
    if (!farm) { setMapFlyTo(null); return; }

    // Priority 1 — explicitly stored center (set when farm boundary was drawn)
    if (farm.centerLat != null && farm.centerLng != null) {
      setMapFlyTo([farm.centerLat, farm.centerLng]);
      setMapFlyZoom(farm.zoom ?? 12);
      return;
    }

    // Priority 2 — derive center from stored bbox
    if (farm.bbox) {
      const [minLng, minLat, maxLng, maxLat] = farm.bbox;
      setMapFlyTo([(minLat + maxLat) / 2, (minLng + maxLng) / 2]);
      setMapFlyZoom(farm.zoom ?? 12);
      return;
    }

    // Priority 3 — stored point coordinates
    if (farm.coordinates) {
      setMapFlyTo([farm.coordinates.lat, farm.coordinates.lng]);
      setMapFlyZoom(12);
      return;
    }

    // Priority 4 — match locationAr against Yemen districts/governorates
    const locationAr = farm.locationAr ?? '';
    if (locationAr) {
      for (const gov of YEMEN_GOVERNORATES) {
        const dist = gov.districts.find((d) => locationAr.includes(d.nameAr));
        if (dist) {
          setMapFlyTo(dist.center);
          setMapFlyZoom(11);
          return;
        }
        if (locationAr.includes(gov.nameAr)) {
          setMapFlyTo(gov.center);
          setMapFlyZoom(9);
          return;
        }
      }
    }

    // No geometry — clear so map stays at Yemen overview
    setMapFlyTo(null);
  };

  const handleBoundaryChange = (geojson: GeoPolygon | null) => {
    if (geojson) {
      const coords = geojson.coordinates[0] ?? [];
      const area = computeAreaHectares(coords);
      setFormData((prev) => ({ ...prev, polygon: geojson, area }));
      setErrors((prev) => { const e = { ...prev }; delete e.polygon; return e; });
    } else {
      setFormData((prev) => ({ ...prev, polygon: undefined, area: 0 }));
    }
  };

  // Display value for the name input (prefer nameAr as canonical)
  const nameValue = formData.nameAr || formData.name;
  const cropValue = formData.cropAr || formData.crop;
  const descValue = formData.descriptionAr || formData.description;

  return (
    <form onSubmit={handleSubmit} className="bg-white flex flex-col h-full">
      <div className="px-6 pt-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {field
            ? (isRtl ? 'تعديل الحقل' : 'Edit Field')
            : (isRtl ? 'إضافة حقل جديد' : 'Add New Field')}
        </h2>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 border-b border-gray-200">
          <button
            type="button"
            onClick={() => setTab('info')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
              tab === 'info'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Info className="w-4 h-4" />
            {isRtl ? 'المعلومات الأساسية' : 'Basic Info'}
          </button>
          <button
            type="button"
            onClick={() => setTab('boundary')}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
              tab === 'boundary'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            } ${errors.polygon ? 'text-red-500' : ''}`}
          >
            <MapPin className="w-4 h-4" />
            {isRtl ? 'حدود الحقل' : 'Field Boundary'}
            {errors.polygon && <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />}
          </button>
        </div>
      </div>

      {/* Tab: Basic Info */}
      {tab === 'info' && (
        <div className="px-6 space-y-5">

          {/* ── Farm selector ──────────────────────────────────────────────── */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {isRtl ? 'المزرعة' : 'Farm'}
            </label>
            <select
              value={formData.farmId ?? ''}
              onChange={(e) => handleFarmChange(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 bg-white"
              dir={isRtl ? 'rtl' : 'ltr'}
            >
              <option value="">
                {isRtl ? '— اختر المزرعة —' : '— Select a farm —'}
              </option>
              {farms.map((farm) => (
                <option key={farm.id} value={farm.id}>
                  {isRtl ? (farm.nameAr || farm.name) : (farm.name || farm.nameAr)}
                </option>
              ))}
            </select>
          </div>

          {/* ── Field name ─────────────────────────────────────────────────── */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {isRtl ? 'اسم الحقل *' : 'Field Name *'}
            </label>
            <input
              type="text"
              required
              maxLength={MAX_NAME_LENGTH}
              value={nameValue}
              onChange={(e) => handleNameChange(e.target.value)}
              className={`w-full px-4 py-2 border-2 rounded-lg focus:outline-none focus:border-blue-500 ${
                errors.nameAr ? 'border-red-400' : 'border-gray-200'
              }`}
              placeholder={isRtl ? 'أدخل اسم الحقل' : 'Enter field name'}
              dir={isRtl ? 'rtl' : 'ltr'}
            />
            {errors.nameAr && <p className="mt-1 text-sm text-red-600">{errors.nameAr}</p>}
          </div>

          {/* ── Computed area (read-only) ───────────────────────────────────── */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {isRtl ? 'المساحة المحسوبة' : 'Computed Area'}
            </label>
            <div className={`w-full px-4 py-2 border-2 rounded-lg bg-gray-50 text-gray-600 ${
              formData.area > 0 ? 'border-green-300' : 'border-gray-200'
            }`}>
              {formData.area > 0
                ? `${formData.area.toFixed(2)} ${isRtl ? 'هكتار' : 'ha'}`
                : (isRtl ? 'ستُحسب تلقائياً عند رسم الحدود' : 'Auto-calculated from boundary')}
            </div>
          </div>

          {/* ── Crop ───────────────────────────────────────────────────────── */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {isRtl ? 'نوع المحصول' : 'Crop Type'}
            </label>
            <select
              value={cropValue}
              onChange={(e) => handleCropChange(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 bg-white"
              dir="rtl"
            >
              <option value="">{isRtl ? '— اختر نوع المحصول —' : '— Select crop type —'}</option>

              <optgroup label="🍎 الفواكه (Fruits)" style={{ color: 'white', backgroundColor: '#374151' }}>
                <option value="تفاح">تفاح</option>
                <option value="أفوكادو">أفوكادو</option>
                <option value="موز">موز</option>
                <option value="توت">توت</option>
                <option value="توت أسود">توت أسود</option>
                <option value="توت أزرق">توت أزرق</option>
                <option value="كرز">كرز</option>
                <option value="حمضيات">حمضيات</option>
                <option value="توت بري">توت بري</option>
                <option value="قشطة">قشطة</option>
                <option value="تمر">تمر</option>
                <option value="تين">تين</option>
                <option value="عنب زبيب">عنب زبيب</option>
                <option value="عنب نبيذ">عنب نبيذ</option>
                <option value="عنب مائدة">عنب مائدة</option>
                <option value="كيوي">كيوي</option>
                <option value="ليمون">ليمون</option>
                <option value="ليتشي">ليتشي</option>
                <option value="مانجو">مانجو</option>
                <option value="شمام">شمام</option>
                <option value="نكتارين">نكتارين</option>
                <option value="زيتون">زيتون</option>
                <option value="برتقال">برتقال</option>
                <option value="خوخ">خوخ</option>
                <option value="كمثرى">كمثرى</option>
                <option value="أناناس">أناناس</option>
                <option value="برقوق">برقوق</option>
                <option value="رمان">رمان</option>
                <option value="توت العليق">توت العليق</option>
                <option value="فراولة">فراولة</option>
                <option value="سوجاربي">سوجاربي</option>
                <option value="بطيخ">بطيخ</option>
              </optgroup>

              <optgroup label="🥬 الخضروات (Vegetables)" style={{ color: 'white', backgroundColor: '#374151' }}>
                <option value="فلفل أناهايم">فلفل أناهايم</option>
                <option value="خرشوف">خرشوف</option>
                <option value="هليون">هليون</option>
                <option value="فاصوليا طازجة">فاصوليا طازجة</option>
                <option value="فلفل رومي">فلفل رومي</option>
                <option value="فول طازج">فول طازج</option>
                <option value="بروكلي">بروكلي</option>
                <option value="كرنب بروكسل">كرنب بروكسل</option>
                <option value="ملفوف">ملفوف</option>
                <option value="جزر">جزر</option>
                <option value="قرنبيط">قرنبيط</option>
                <option value="كرفس">كرفس</option>
                <option value="هندباء ورقي">هندباء ورقي</option>
                <option value="هندباء جذر">هندباء جذر</option>
                <option value="ملفوف صيني">ملفوف صيني</option>
                <option value="خيار مخلل">خيار مخلل</option>
                <option value="خيار تقطيع">خيار تقطيع</option>
                <option value="باذنجان">باذنجان</option>
                <option value="أنديف">أنديف</option>
                <option value="ثوم">ثوم</option>
                <option value="بصل أخضر">بصل أخضر</option>
                <option value="خس رأس">خس رأس</option>
                <option value="فلفل هالابينيو">فلفل هالابينيو</option>
                <option value="كيل">كيل</option>
                <option value="خس ورقي">خس ورقي</option>
                <option value="كراث">كراث</option>
                <option value="نعناع">نعناع</option>
                <option value="بصل">بصل</option>
                <option value="بازلاء طازجة">بازلاء طازجة</option>
                <option value="فلفل بوبلانو">فلفل بوبلانو</option>
                <option value="بطاطس">بطاطس</option>
                <option value="قرع">قرع</option>
                <option value="فجل">فجل</option>
                <option value="فلفل سيرانو">فلفل سيرانو</option>
                <option value="سبانخ">سبانخ</option>
                <option value="ذرة حلوة">ذرة حلوة</option>
                <option value="بطاطا حلوة">بطاطا حلوة</option>
                <option value="طماطم مكسيكية">طماطم مكسيكية</option>
                <option value="طماطم">طماطم</option>
              </optgroup>

              <optgroup label="🌾 الحبوب والبقوليات (Grains & Legumes)" style={{ color: 'white', backgroundColor: '#374151' }}>
                <option value="شعير">شعير</option>
                <option value="فاصوليا جافة">فاصوليا جافة</option>
                <option value="فول جاف">فول جاف</option>
                <option value="ذرة">ذرة</option>
                <option value="عدس">عدس</option>
                <option value="دخن">دخن</option>
                <option value="شوفان">شوفان</option>
                <option value="فول سوداني">فول سوداني</option>
                <option value="بازلاء جافة">بازلاء جافة</option>
                <option value="فشار">فشار</option>
                <option value="كينوا">كينوا</option>
                <option value="أرز">أرز</option>
                <option value="ذرة بذور">ذرة بذور</option>
                <option value="ذرة رفيعة">ذرة رفيعة</option>
                <option value="فول الصويا">فول الصويا</option>
                <option value="تيف">تيف</option>
                <option value="قمح">قمح</option>
                <option value="قمح شتوي">قمح شتوي</option>
              </optgroup>

              <optgroup label="📌 محاصيل أخرى" style={{ color: 'white', backgroundColor: '#374151' }}>
                <option value="برسيم / فصة">برسيم / فصة</option>
                <option value="لوز">لوز</option>
                <option value="كاكاو">كاكاو</option>
                <option value="قهوة">قهوة</option>
                <option value="كزبرة">كزبرة</option>
                <option value="قطن">قطن</option>
                <option value="أوكالبتوس">أوكالبتوس</option>
                <option value="عشب">عشب</option>
                <option value="عشب المراعي">عشب المراعي</option>
                <option value="بندق">بندق</option>
                <option value="قنب">قنب</option>
                <option value="جنجل">جنجل</option>
                <option value="مكاديميا">مكاديميا</option>
                <option value="خردل">خردل</option>
                <option value="بيكان">بيكان</option>
                <option value="فستق">فستق</option>
                <option value="حور">حور</option>
                <option value="كانولا">كانولا</option>
                <option value="ورد">ورد</option>
                <option value="قصب السكر">قصب السكر</option>
                <option value="دوار الشمس">دوار الشمس</option>
                <option value="تبغ">تبغ</option>
                <option value="توليب">توليب</option>
                <option value="عشب الملاعب">عشب الملاعب</option>
                <option value="جوز">جوز</option>
              </optgroup>
            </select>
          </div>

          {/* ── Description ────────────────────────────────────────────────── */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {isRtl ? 'الوصف' : 'Description'}
            </label>
            <textarea
              value={descValue}
              onChange={(e) => handleDescChange(e.target.value)}
              rows={3}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder={isRtl ? 'وصف الحقل' : 'Field description'}
              dir={isRtl ? 'rtl' : 'ltr'}
            />
          </div>
        </div>
      )}

      {/* Tab: Boundary */}
      {tab === 'boundary' && (
        <div className="px-6 flex flex-col flex-1 min-h-0">
          <GoogleMapsFieldDrawer
            height="calc(100vh - 320px)"
            initialCenter={mapFlyTo ?? [15.5527, 48.5164]}
            initialZoom={mapFlyTo ? mapFlyZoom : 7}
            initialPolygon={formData.polygon}
            onBoundaryChange={handleBoundaryChange}
          />
          {formData.area > 0 && (
            <p className="mt-3 text-sm font-medium text-green-700">
              {isRtl
                ? `المساحة المحسوبة: ${formData.area.toFixed(2)} هكتار`
                : `Computed area: ${formData.area.toFixed(2)} ha`}
            </p>
          )}
          {errors.polygon && (
            <p className="mt-2 text-sm text-red-600">{errors.polygon}</p>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 mt-auto mx-6 mb-6 pt-6 border-t-2 border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex items-center gap-2 px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={isSubmitting}
          >
            <X className="w-4 h-4" />
            <span>{isRtl ? 'إلغاء' : 'Cancel'}</span>
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="w-4 h-4" />
          <span>{isSubmitting ? (isRtl ? 'جاري الحفظ...' : 'Saving...') : (isRtl ? 'حفظ' : 'Save')}</span>
        </button>
      </div>
    </form>
  );
};

export default FieldForm;

// ─── Haversine area helper (runs client-side) ────────────────────────────────

function toRad(deg: number) {
  return (deg * Math.PI) / 180;
}

function computeAreaHectares(coords: number[][]): number {
  if (coords.length < 4) return 0;
  const R = 6371000;
  let area = 0;
  for (let i = 0; i < coords.length - 1; i++) {
    const c1 = coords[i] as [number, number];
    const c2 = coords[(i + 1) % coords.length] as [number, number];
    area += toRad(c2[0] - c1[0]) * (2 + Math.sin(toRad(c1[1])) + Math.sin(toRad(c2[1])));
  }
  area = Math.abs((area * R * R) / 2);
  return area / 10000;
}

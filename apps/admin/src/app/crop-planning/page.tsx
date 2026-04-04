'use client';

// Crop Planning Wizard — تخطيط الموسم الزراعي
// 7-step wizard: field → crop → prep → seeding → irrigation → monitoring → harvest

import { useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import {
  MapPin, Leaf, Shovel, Sprout, Droplets, Eye, Wheat,
  ChevronLeft, ChevronRight, Save, CheckCircle, Circle,
} from 'lucide-react';

// ─── Types ───────────────────────────────────────────────────────────────────

interface CropOption {
  code: string; nameAr: string; icon: string; season: string;
  plantingMonths: string; daysToHarvest: number; waterMm: number; yieldTonsHa: number;
}

interface PlanData {
  fieldId: string; cropCode: string; plantingDate: string;
  variety: string; seedRate: number; rowSpacing: number;
  irrigationMethod: string; irrigationFrequency: number; irrigationAmount: number;
  prepChecklist: boolean[];
  monitoringPlan: { ndvi: boolean; scouting: boolean; pest: boolean; soil: boolean };
}

// ─── Data ────────────────────────────────────────────────────────────────────

const FIELDS = [
  { id: 'f1', name: 'حقل القمح الشمالي', area: 5.2, soil: 'طيني', lastCrop: 'شعير' },
  { id: 'f2', name: 'حقل الطماطم', area: 3.0, soil: 'رملي طيني', lastCrop: 'بصل' },
  { id: 'f3', name: 'بستان النخيل', area: 8.5, soil: 'رملي', lastCrop: 'نخيل (دائم)' },
];

const CROPS: CropOption[] = [
  { code: 'wheat', nameAr: 'قمح', icon: '🌾', season: 'شتوي', plantingMonths: 'أكتوبر-ديسمبر', daysToHarvest: 150, waterMm: 450, yieldTonsHa: 4.5 },
  { code: 'barley', nameAr: 'شعير', icon: '🌾', season: 'شتوي', plantingMonths: 'أكتوبر-نوفمبر', daysToHarvest: 120, waterMm: 300, yieldTonsHa: 3.5 },
  { code: 'sorghum', nameAr: 'ذرة رفيعة', icon: '🌽', season: 'صيفي', plantingMonths: 'يونيو-يوليو', daysToHarvest: 120, waterMm: 350, yieldTonsHa: 2.5 },
  { code: 'tomato', nameAr: 'طماطم', icon: '🍅', season: 'ربيعي', plantingMonths: 'مارس-أبريل', daysToHarvest: 90, waterMm: 500, yieldTonsHa: 25 },
  { code: 'onion', nameAr: 'بصل', icon: '🧅', season: 'خريفي', plantingMonths: 'سبتمبر-أكتوبر', daysToHarvest: 120, waterMm: 400, yieldTonsHa: 15 },
  { code: 'date_palm', nameAr: 'نخيل', icon: '🌴', season: 'دائم', plantingMonths: 'مارس-أبريل', daysToHarvest: 180, waterMm: 600, yieldTonsHa: 8 },
  { code: 'coffee', nameAr: 'بن يمني', icon: '☕', season: 'دائم', plantingMonths: 'مارس-مايو', daysToHarvest: 365, waterMm: 800, yieldTonsHa: 2 },
  { code: 'qat', nameAr: 'قات', icon: '🌿', season: 'دائم', plantingMonths: 'طوال العام', daysToHarvest: 90, waterMm: 500, yieldTonsHa: 0 },
];

const STEPS = [
  { id: 1, nameAr: 'اختيار الحقل', icon: MapPin },
  { id: 2, nameAr: 'اختيار المحصول', icon: Leaf },
  { id: 3, nameAr: 'تحضير الحقل', icon: Shovel },
  { id: 4, nameAr: 'البذار', icon: Sprout },
  { id: 5, nameAr: 'خطة الري', icon: Droplets },
  { id: 6, nameAr: 'برنامج المراقبة', icon: Eye },
  { id: 7, nameAr: 'الحصاد المتوقع', icon: Wheat },
];

const PREP_ITEMS = [
  'حراثة أولية (عمق 30 سم)', 'حراثة ثانية (تنعيم)', 'تسوية الأرض',
  'تحليل التربة', 'تسميد أساسي (DAP + بوتاسيوم)', 'تجهيز شبكة الري', 'ري تأسيسي',
];

// ─── Component ───────────────────────────────────────────────────────────────

export default function CropPlanningPage() {
  const [step, setStep] = useState(1);
  const [plan, setPlan] = useState<PlanData>({
    fieldId: FIELDS[0]?.id ?? '', cropCode: '', plantingDate: '', variety: '',
    seedRate: 120, rowSpacing: 20, irrigationMethod: 'drip',
    irrigationFrequency: 5, irrigationAmount: 25,
    prepChecklist: PREP_ITEMS.map(() => false),
    monitoringPlan: { ndvi: true, scouting: true, pest: true, soil: false },
  });

  const selectedField = useMemo(() => FIELDS.find(f => f.id === plan.fieldId) ?? FIELDS[0], [plan.fieldId]);
  const selectedCrop = useMemo(() => CROPS.find(c => c.code === plan.cropCode), [plan.cropCode]);

  const harvestDate = useMemo(() => {
    if (!plan.plantingDate || !selectedCrop) return null;
    const d = new Date(plan.plantingDate);
    d.setDate(d.getDate() + selectedCrop.daysToHarvest);
    return d.toLocaleDateString('ar-YE', { year: 'numeric', month: 'long', day: 'numeric' });
  }, [plan.plantingDate, selectedCrop]);

  const expectedYield = useMemo(() => {
    if (!selectedCrop || !selectedField) return 0;
    return (selectedCrop.yieldTonsHa * (selectedField?.area ?? 1)).toFixed(1);
  }, [selectedCrop, selectedField]);

  const prepProgress = useMemo(() => {
    const done = plan.prepChecklist.filter(Boolean).length;
    return Math.round((done / PREP_ITEMS.length) * 100);
  }, [plan.prepChecklist]);

  return (
    <div className="p-6 space-y-6" dir="rtl">
      <Header title="تخطيط الموسم الزراعي" subtitle="خطة شاملة من تحضير الحقل إلى الحصاد" />

      <div className="flex gap-6">
        {/* Sidebar Steps */}
        <div className="w-56 flex-shrink-0">
          <div className="bg-white dark:bg-gray-800 rounded-xl border p-4 space-y-2">
            {STEPS.map(s => {
              const Icon = s.icon;
              const isActive = step === s.id;
              const isDone = step > s.id;
              return (
                <button key={s.id} onClick={() => setStep(s.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg text-sm transition-all ${
                    isActive ? 'bg-green-50 dark:bg-green-900/20 text-green-700 font-bold border border-green-200' :
                    isDone ? 'text-green-600' : 'text-gray-500 hover:bg-gray-50'
                  }`}>
                  {isDone ? <CheckCircle className="w-5 h-5 text-green-500" /> :
                   isActive ? <Icon className="w-5 h-5" /> : <Circle className="w-5 h-5" />}
                  <span>{s.nameAr}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step Content */}
        <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl border p-6 min-h-[500px]">
          {/* Step 1: Field Selection */}
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold">اختيار الحقل</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {FIELDS.map(f => (
                  <button key={f.id} onClick={() => setPlan(p => ({ ...p, fieldId: f.id }))}
                    className={`p-4 rounded-xl border-2 text-right transition-all ${
                      plan.fieldId === f.id ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : 'border-gray-200 hover:border-gray-300'
                    }`}>
                    <p className="font-bold text-gray-900 dark:text-white">{f.name}</p>
                    <p className="text-sm text-gray-500 mt-1">المساحة: {f.area} هكتار</p>
                    <p className="text-sm text-gray-500">التربة: {f.soil}</p>
                    <p className="text-sm text-gray-500">آخر محصول: {f.lastCrop}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Crop Selection */}
          {step === 2 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold">اختيار المحصول</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {CROPS.map(c => (
                  <button key={c.code} onClick={() => setPlan(p => ({ ...p, cropCode: c.code }))}
                    className={`p-4 rounded-xl border-2 text-center transition-all ${
                      plan.cropCode === c.code ? 'border-green-500 bg-green-50 shadow-lg' : 'border-gray-200 hover:border-gray-300'
                    }`}>
                    <span className="text-3xl block mb-2">{c.icon}</span>
                    <p className="font-bold">{c.nameAr}</p>
                    <span className="text-xs px-2 py-0.5 bg-gray-100 rounded-full">{c.season}</span>
                    <p className="text-xs text-gray-500 mt-1">{c.plantingMonths}</p>
                    <p className="text-xs text-gray-500">{c.daysToHarvest} يوم | {c.yieldTonsHa} طن/هـ</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Field Preparation */}
          {step === 3 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold">تحضير الحقل</h2>
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div className="bg-green-500 h-3 rounded-full transition-all" style={{ width: `${prepProgress}%` }} />
              </div>
              <p className="text-sm text-gray-500">{prepProgress}% مكتمل</p>
              <div className="space-y-2">
                {PREP_ITEMS.map((item, i) => (
                  <label key={i} className="flex items-center gap-3 p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" checked={plan.prepChecklist[i] ?? false}
                      onChange={() => setPlan(p => {
                        const cl = [...p.prepChecklist]; cl[i] = !cl[i]; return { ...p, prepChecklist: cl };
                      })} className="w-5 h-5 rounded text-green-600" />
                    <span className={plan.prepChecklist[i] ? 'line-through text-gray-400' : ''}>{item}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Step 4: Seeding */}
          {step === 4 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold">البذار والزراعة</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">تاريخ الزراعة</label>
                  <input type="date" value={plan.plantingDate}
                    onChange={e => setPlan(p => ({ ...p, plantingDate: e.target.value }))}
                    className="w-full p-2 border rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">الصنف</label>
                  <input type="text" value={plan.variety} placeholder="مثال: سخا 95"
                    onChange={e => setPlan(p => ({ ...p, variety: e.target.value }))}
                    className="w-full p-2 border rounded-lg" dir="rtl" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">معدل البذار (كجم/هكتار)</label>
                  <input type="number" value={plan.seedRate}
                    onChange={e => setPlan(p => ({ ...p, seedRate: +e.target.value }))}
                    className="w-full p-2 border rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">مسافة الصفوف (سم)</label>
                  <input type="number" value={plan.rowSpacing}
                    onChange={e => setPlan(p => ({ ...p, rowSpacing: +e.target.value }))}
                    className="w-full p-2 border rounded-lg" />
                </div>
              </div>
              {selectedCrop && (
                <div className="p-4 bg-blue-50 rounded-lg text-sm">
                  <p>💡 <strong>توصية:</strong> {selectedCrop.nameAr} يُزرع في {selectedCrop.plantingMonths}</p>
                  <p>معدل البذار الموصى: {selectedCrop.code === 'wheat' ? '120-140' : selectedCrop.code === 'tomato' ? '0.3-0.5' : '100-120'} كجم/هكتار</p>
                </div>
              )}
            </div>
          )}

          {/* Step 5: Irrigation Plan */}
          {step === 5 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold">خطة الري</h2>
              <div className="grid grid-cols-3 gap-3">
                {['drip', 'sprinkler', 'flood', 'pivot'].map(m => (
                  <button key={m} onClick={() => setPlan(p => ({ ...p, irrigationMethod: m }))}
                    className={`p-3 rounded-lg border-2 text-center ${plan.irrigationMethod === m ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
                    <span className="text-xl">{m === 'drip' ? '💧' : m === 'sprinkler' ? '🌧️' : m === 'flood' ? '🌊' : '🔄'}</span>
                    <p className="text-sm font-medium mt-1">{m === 'drip' ? 'تنقيط' : m === 'sprinkler' ? 'رشاش' : m === 'flood' ? 'غمر' : 'محوري'}</p>
                  </button>
                ))}
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium mb-1">كل (أيام)</label>
                  <input type="number" value={plan.irrigationFrequency}
                    onChange={e => setPlan(p => ({ ...p, irrigationFrequency: +e.target.value }))}
                    className="w-full p-2 border rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">الكمية (مم)</label>
                  <input type="number" value={plan.irrigationAmount}
                    onChange={e => setPlan(p => ({ ...p, irrigationAmount: +e.target.value }))}
                    className="w-full p-2 border rounded-lg" />
                </div>
              </div>
              {selectedCrop && (
                <p className="text-sm text-gray-500">الاحتياج المائي الكلي: {selectedCrop.waterMm} مم/موسم</p>
              )}
            </div>
          )}

          {/* Step 6: Monitoring */}
          {step === 6 && (
            <div className="space-y-4">
              <h2 className="text-lg font-bold">برنامج المراقبة</h2>
              {[
                { key: 'ndvi' as const, label: 'مراقبة NDVI بالأقمار الصناعية', desc: 'كل 5 أيام — Sentinel-2', icon: '🛰️' },
                { key: 'scouting' as const, label: 'فحص ميداني أسبوعي', desc: 'زيارة الحقل وتسجيل الملاحظات', icon: '👁️' },
                { key: 'pest' as const, label: 'مراقبة الآفات والأمراض', desc: 'كل أسبوعين — فحص بصري + مصائد', icon: '🐛' },
                { key: 'soil' as const, label: 'مراقبة رطوبة التربة', desc: 'مستشعر IoT أو SAR رادار', icon: '💧' },
              ].map(item => (
                <label key={item.key} className="flex items-center gap-4 p-4 rounded-lg border hover:bg-gray-50 cursor-pointer">
                  <input type="checkbox" checked={plan.monitoringPlan[item.key]}
                    onChange={() => setPlan(p => ({
                      ...p, monitoringPlan: { ...p.monitoringPlan, [item.key]: !p.monitoringPlan[item.key] }
                    }))} className="w-5 h-5 rounded text-green-600" />
                  <span className="text-2xl">{item.icon}</span>
                  <div>
                    <p className="font-medium">{item.label}</p>
                    <p className="text-sm text-gray-500">{item.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          )}

          {/* Step 7: Harvest Forecast */}
          {step === 7 && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold">موعد الحصاد المتوقع</h2>
              {selectedCrop && plan.plantingDate ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 bg-green-50 rounded-xl text-center border border-green-200">
                      <p className="text-sm text-gray-600">تاريخ الحصاد</p>
                      <p className="text-xl font-bold text-green-700 mt-1">{harvestDate}</p>
                    </div>
                    <div className="p-4 bg-amber-50 rounded-xl text-center border border-amber-200">
                      <p className="text-sm text-gray-600">الإنتاج المتوقع</p>
                      <p className="text-xl font-bold text-amber-700 mt-1">{expectedYield} طن</p>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-xl text-center border border-blue-200">
                      <p className="text-sm text-gray-600">الإيراد التقديري</p>
                      <p className="text-xl font-bold text-blue-700 mt-1">
                        {(Number(expectedYield) * 1850).toLocaleString('ar-SA')} ريال
                      </p>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-medium mb-2">ملخص الخطة:</h3>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>🌾 المحصول: {selectedCrop.nameAr} — {selectedCrop.season}</li>
                      <li>📐 الحقل: {selectedField?.name} ({selectedField?.area} هكتار)</li>
                      <li>🌱 تاريخ الزراعة: {new Date(plan.plantingDate).toLocaleDateString('ar-YE')}</li>
                      <li>💧 الري: {plan.irrigationMethod === 'drip' ? 'تنقيط' : plan.irrigationMethod} — كل {plan.irrigationFrequency} أيام</li>
                      <li>📊 المراقبة: {Object.values(plan.monitoringPlan).filter(Boolean).length} برامج نشطة</li>
                      <li>✅ تحضير الحقل: {prepProgress}% مكتمل</li>
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">يرجى اختيار المحصول وتاريخ الزراعة أولاً (الخطوات 2 و 4)</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button onClick={() => setStep(s => Math.max(1, s - 1))} disabled={step === 1}
          className="flex items-center gap-2 px-6 py-2 border rounded-lg disabled:opacity-30 hover:bg-gray-50">
          <ChevronRight className="w-4 h-4" /> السابق
        </button>
        <div className="flex gap-3">
          {step === 7 && (
            <button className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
              <Save className="w-4 h-4" /> حفظ الخطة
            </button>
          )}
          <button onClick={() => setStep(s => Math.min(7, s + 1))} disabled={step === 7}
            className="flex items-center gap-2 px-6 py-2 bg-sahool-600 text-white rounded-lg disabled:opacity-30 hover:bg-sahool-700">
            التالي <ChevronLeft className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

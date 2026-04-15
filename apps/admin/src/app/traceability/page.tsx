// Sahool Admin Dashboard - Product Traceability
// تتبع المنتجات — سلسلة التوريد

'use client';

import { useState, useEffect, useMemo } from 'react';
import { apiClient, API_URLS, downloadCSV } from '@/lib/api';
import { API_PATHS } from '@/config/api';
import { logger } from '@/lib/logger';
import {
  Package,
  QrCode,
  MapPin,
  Calendar,
  Search,
  Download,
  Loader2,
  CheckCircle2,
  Truck,
  Warehouse,
  Leaf,
  ShieldCheck,
  Eye,
  Clock,
} from 'lucide-react';

// ─── Types ───────────────────────────────────────────────────────────────────

interface TraceabilityBatch {
  id: string;
  batch_code: string;
  product_name_ar: string;
  crop_type: string;
  farm_name_ar: string;
  field_name_ar: string;
  governorate_ar: string;
  quantity_kg: number;
  unit_price_yer: number;
  harvest_date: string;
  status: 'harvested' | 'stored' | 'in_transit' | 'delivered' | 'sold';
  quality_grade: 'A' | 'B' | 'C';
  certifications: string[];
  qr_code_url?: string;
  created_at: string;
}

interface TraceabilityEvent {
  id: string;
  batch_id: string;
  event_type: 'harvest' | 'quality_check' | 'storage' | 'transport' | 'delivery' | 'sale';
  event_type_ar: string;
  description_ar: string;
  location_ar: string;
  timestamp: string;
  actor_name_ar: string;
  metadata?: Record<string, string>;
}

interface TraceabilityStats {
  total_batches: number;
  active_batches: number;
  delivered_batches: number;
  total_quantity_tons: number;
  avg_quality_score: number;
  certified_percent: number;
}

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_STATS: TraceabilityStats = {
  total_batches: 234,
  active_batches: 48,
  delivered_batches: 186,
  total_quantity_tons: 1850,
  avg_quality_score: 87,
  certified_percent: 72,
};

const MOCK_BATCHES: TraceabilityBatch[] = [
  {
    id: 'b1',
    batch_code: 'SAH-2026-QMH-001',
    product_name_ar: 'قمح — سخا 95',
    crop_type: 'wheat',
    farm_name_ar: 'مزرعة الرشيد',
    field_name_ar: 'حقل القمح الشمالي',
    governorate_ar: 'صنعاء',
    quantity_kg: 4560,
    unit_price_yer: 850,
    harvest_date: '2026-03-10',
    status: 'stored',
    quality_grade: 'A',
    certifications: ['GlobalGAP', 'عضوي'],
    created_at: '2026-03-10T08:00:00Z',
  },
  {
    id: 'b2',
    batch_code: 'SAH-2026-BN-002',
    product_name_ar: 'بن يمني — مخا',
    crop_type: 'coffee',
    farm_name_ar: 'مزرعة الجبل',
    field_name_ar: 'حقل البن العلوي',
    governorate_ar: 'إب',
    quantity_kg: 850,
    unit_price_yer: 12000,
    harvest_date: '2025-12-15',
    status: 'in_transit',
    quality_grade: 'A',
    certifications: ['عضوي', 'Fair Trade'],
    created_at: '2025-12-15T10:00:00Z',
  },
  {
    id: 'b3',
    batch_code: 'SAH-2026-TOM-003',
    product_name_ar: 'طماطم — هجين 1023',
    crop_type: 'tomato',
    farm_name_ar: 'مزرعة الخير',
    field_name_ar: 'حقل الطماطم A',
    governorate_ar: 'تعز',
    quantity_kg: 14000,
    unit_price_yer: 650,
    harvest_date: '2026-02-28',
    status: 'delivered',
    quality_grade: 'B',
    certifications: ['GlobalGAP'],
    created_at: '2026-02-28T06:00:00Z',
  },
  {
    id: 'b4',
    batch_code: 'SAH-2026-BTT-004',
    product_name_ar: 'بطاطس — سبونتا',
    crop_type: 'potato',
    farm_name_ar: 'مزرعة السلام',
    field_name_ar: 'حقل البطاطس',
    governorate_ar: 'الحديدة',
    quantity_kg: 19000,
    unit_price_yer: 500,
    harvest_date: '2026-02-20',
    status: 'sold',
    quality_grade: 'A',
    certifications: [],
    created_at: '2026-02-20T07:00:00Z',
  },
  {
    id: 'b5',
    batch_code: 'SAH-2026-SHR-005',
    product_name_ar: 'شعير — جيزة 136',
    crop_type: 'barley',
    farm_name_ar: 'مزرعة النور',
    field_name_ar: 'حقل الشعير',
    governorate_ar: 'إب',
    quantity_kg: 4650,
    unit_price_yer: 700,
    harvest_date: '2026-03-15',
    status: 'harvested',
    quality_grade: 'B',
    certifications: [],
    created_at: '2026-03-15T09:00:00Z',
  },
  {
    id: 'b6',
    batch_code: 'SAH-2026-MNG-006',
    product_name_ar: 'مانجو — تيمور',
    crop_type: 'mango',
    farm_name_ar: 'مزرعة الساحل',
    field_name_ar: 'بستان المانجو',
    governorate_ar: 'عدن',
    quantity_kg: 6200,
    unit_price_yer: 2500,
    harvest_date: '2026-03-05',
    status: 'in_transit',
    quality_grade: 'A',
    certifications: ['عضوي'],
    created_at: '2026-03-05T11:00:00Z',
  },
];

const MOCK_EVENTS: TraceabilityEvent[] = [
  {
    id: 'e1',
    batch_id: 'b1',
    event_type: 'harvest',
    event_type_ar: 'حصاد',
    description_ar: 'تم حصاد 4.56 طن من القمح — صنف سخا 95',
    location_ar: 'مزرعة الرشيد — صنعاء',
    timestamp: '2026-03-10T08:00:00Z',
    actor_name_ar: 'أحمد الرشيدي',
  },
  {
    id: 'e2',
    batch_id: 'b1',
    event_type: 'quality_check',
    event_type_ar: 'فحص جودة',
    description_ar: 'رطوبة 12.5% — نقاوة 98% — الدرجة: A',
    location_ar: 'مختبر الجودة — صنعاء',
    timestamp: '2026-03-10T14:00:00Z',
    actor_name_ar: 'د. سمير الحداد',
  },
  {
    id: 'e3',
    batch_id: 'b1',
    event_type: 'storage',
    event_type_ar: 'تخزين',
    description_ar: 'تخزين في صومعة 3 — درجة حرارة 18°م — رطوبة 55%',
    location_ar: 'صوامع صنعاء المركزية',
    timestamp: '2026-03-11T09:00:00Z',
    actor_name_ar: 'خالد المخزني',
  },
  {
    id: 'e4',
    batch_id: 'b2',
    event_type: 'harvest',
    event_type_ar: 'حصاد',
    description_ar: 'تم حصاد 850 كجم من البن — الكرز الأحمر',
    location_ar: 'مزرعة الجبل — إب',
    timestamp: '2025-12-15T10:00:00Z',
    actor_name_ar: 'محمد الجبلي',
  },
  {
    id: 'e5',
    batch_id: 'b2',
    event_type: 'quality_check',
    event_type_ar: 'فحص جودة',
    description_ar: 'فحص حبوب البن — الحجم: 16+ — العيوب: 2% — الدرجة: A',
    location_ar: 'مختبر البن — إب',
    timestamp: '2025-12-20T11:00:00Z',
    actor_name_ar: 'د. عبدالله البنّاء',
  },
  {
    id: 'e6',
    batch_id: 'b2',
    event_type: 'transport',
    event_type_ar: 'نقل',
    description_ar: 'شحن بالشاحنة المبردة إلى ميناء عدن — الوصول المتوقع: 48 ساعة',
    location_ar: 'إب → عدن',
    timestamp: '2026-03-14T06:00:00Z',
    actor_name_ar: 'شركة النقل السريع',
  },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getStatusConfig(status: string) {
  const config: Record<string, { label: string; color: string; icon: typeof Package }> = {
    harvested: {
      label: 'تم الحصاد',
      color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
      icon: Leaf,
    },
    stored: {
      label: 'مُخزّن',
      color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
      icon: Warehouse,
    },
    in_transit: {
      label: 'قيد النقل',
      color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
      icon: Truck,
    },
    delivered: {
      label: 'تم التسليم',
      color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
      icon: CheckCircle2,
    },
    sold: {
      label: 'تم البيع',
      color: 'bg-sahool-100 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-400',
      icon: Package,
    },
  };
  return config[status] || { label: status, color: 'bg-gray-100 text-gray-700', icon: Package };
}

function getEventIcon(type: string) {
  const icons: Record<string, typeof Package> = {
    harvest: Leaf,
    quality_check: ShieldCheck,
    storage: Warehouse,
    transport: Truck,
    delivery: CheckCircle2,
    sale: Package,
  };
  return icons[type] || Package;
}

function getGradeColor(grade: string) {
  switch (grade) {
    case 'A':
      return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400';
    case 'B':
      return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400';
    default:
      return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400';
  }
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function TraceabilityPage() {
  const [batches, setBatches] = useState<TraceabilityBatch[]>([]);
  const [events, setEvents] = useState<TraceabilityEvent[]>([]);
  const [stats, setStats] = useState<TraceabilityStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [batchRes, eventRes] = await Promise.allSettled([
        apiClient.get(`${API_URLS.traceability}${API_PATHS.traceability.batches}`),
        apiClient.get(`${API_URLS.traceability}${API_PATHS.traceability.events}`),
      ]);
      setBatches(batchRes.status === 'fulfilled' ? batchRes.value.data : MOCK_BATCHES);
      setEvents(eventRes.status === 'fulfilled' ? eventRes.value.data : MOCK_EVENTS);
      setStats(MOCK_STATS);
    } catch (err) {
      logger.warn('Traceability API unavailable, using demo data', err);
      setBatches(MOCK_BATCHES);
      setEvents(MOCK_EVENTS);
      setStats(MOCK_STATS);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredBatches = useMemo(() => {
    return batches.filter((b) => {
      const query = searchQuery.toLowerCase();
      const matchSearch =
        !searchQuery ||
        b.product_name_ar.toLowerCase().includes(query) ||
        b.batch_code.toLowerCase().includes(query) ||
        b.farm_name_ar.toLowerCase().includes(query);
      const matchStatus = statusFilter === 'all' || b.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [batches, searchQuery, statusFilter]);

  const selectedBatchEvents = useMemo(() => {
    if (!selectedBatch) return [];
    return events
      .filter((e) => e.batch_id === selectedBatch)
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [events, selectedBatch]);

  const selectedBatchData = batches.find((b) => b.id === selectedBatch);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-600" />
        <span className="mr-3 text-gray-500 dark:text-gray-400">جاري تحميل بيانات التتبع...</span>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <QrCode className="w-7 h-7 text-sahool-600" />
            تتبع المنتجات وسلسلة التوريد
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            تتبع كل دفعة من الحقل إلى المستهلك — رموز QR وسجل كامل
          </p>
        </div>
        <button
          onClick={() => downloadCSV(batches, 'traceability')}
          className="flex items-center gap-2 px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          title="تصدير CSV"
        >
          <Download className="w-4 h-4" />
          تصدير
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            {
              label: 'إجمالي الدفعات',
              value: stats.total_batches,
              icon: Package,
              color: 'text-blue-600 dark:text-blue-400',
            },
            {
              label: 'دفعات نشطة',
              value: stats.active_batches,
              icon: Truck,
              color: 'text-yellow-600 dark:text-yellow-400',
            },
            {
              label: 'تم التسليم',
              value: stats.delivered_batches,
              icon: CheckCircle2,
              color: 'text-green-600 dark:text-green-400',
            },
            {
              label: 'الكمية الكلية',
              value: `${stats.total_quantity_tons} طن`,
              icon: Warehouse,
              color: 'text-purple-600 dark:text-purple-400',
            },
            {
              label: 'متوسط الجودة',
              value: `${stats.avg_quality_score}%`,
              icon: ShieldCheck,
              color: 'text-sahool-600 dark:text-sahool-400',
            },
            {
              label: 'نسبة المعتمد',
              value: `${stats.certified_percent}%`,
              icon: Leaf,
              color: 'text-green-600 dark:text-green-400',
            },
          ].map((s) => (
            <div
              key={s.label}
              className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <s.icon className={`w-4 h-4 ${s.color}`} />
                <span className="text-xs text-gray-500 dark:text-gray-400">{s.label}</span>
              </div>
              <p className={`text-lg font-bold ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="بحث بكود الدفعة أو اسم المنتج أو المزرعة..."
            className="w-full pr-10 pl-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2 text-sm"
        >
          <option value="all">كل الحالات</option>
          <option value="harvested">تم الحصاد</option>
          <option value="stored">مُخزّن</option>
          <option value="in_transit">قيد النقل</option>
          <option value="delivered">تم التسليم</option>
          <option value="sold">تم البيع</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Batches List */}
        <div className="lg:col-span-2 space-y-3">
          {filteredBatches.map((batch) => {
            const sc = getStatusConfig(batch.status);
            const isSelected = selectedBatch === batch.id;
            return (
              <div
                key={batch.id}
                onClick={() => setSelectedBatch(isSelected ? null : batch.id)}
                className={`bg-white dark:bg-gray-900 rounded-xl border p-4 cursor-pointer transition-all ${
                  isSelected
                    ? 'border-sahool-500 dark:border-sahool-600 ring-1 ring-sahool-200 dark:ring-sahool-800'
                    : 'border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-xs font-mono bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded">
                        {batch.batch_code}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${sc.color}`}>
                        {sc.label}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-bold ${getGradeColor(batch.quality_grade)}`}
                      >
                        درجة {batch.quality_grade}
                      </span>
                    </div>
                    <h3 className="font-bold text-gray-900 dark:text-gray-100">
                      {batch.product_name_ar}
                    </h3>
                    <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {batch.farm_name_ar} — {batch.governorate_ar}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {batch.harvest_date}
                      </span>
                      <span className="flex items-center gap-1">
                        <Package className="w-3 h-3" />
                        {(batch.quantity_kg / 1000).toFixed(1)} طن
                      </span>
                    </div>
                    {batch.certifications.length > 0 && (
                      <div className="flex gap-2 mt-2">
                        {batch.certifications.map((cert) => (
                          <span
                            key={cert}
                            className="text-xs bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 px-2 py-0.5 rounded border border-green-200 dark:border-green-800"
                          >
                            {cert}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="text-left flex-shrink-0">
                    <p className="text-lg font-bold text-sahool-600 dark:text-sahool-400">
                      {((batch.quantity_kg * batch.unit_price_yer) / 1000000).toFixed(1)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">مليون ر.ي</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Event Timeline (Right Panel) */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-sahool-600" />
            سجل الأحداث
          </h3>
          {!selectedBatch ? (
            <div className="text-center py-12 text-gray-400 dark:text-gray-500">
              <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">اختر دفعة لعرض سجل الأحداث</p>
            </div>
          ) : (
            <div className="space-y-0">
              {selectedBatchData && (
                <div className="mb-4 p-3 bg-sahool-50 dark:bg-sahool-900/20 rounded-lg border border-sahool-200 dark:border-sahool-800">
                  <p className="text-sm font-bold text-sahool-700 dark:text-sahool-300">
                    {selectedBatchData.product_name_ar}
                  </p>
                  <p className="text-xs text-sahool-600 dark:text-sahool-400">
                    {selectedBatchData.batch_code}
                  </p>
                </div>
              )}
              {selectedBatchEvents.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">لا توجد أحداث مسجلة</p>
              ) : (
                selectedBatchEvents.map((event, i) => {
                  const EventIcon = getEventIcon(event.event_type);
                  return (
                    <div key={event.id} className="relative flex gap-3 pb-6">
                      {/* Timeline line */}
                      {i < selectedBatchEvents.length - 1 && (
                        <div className="absolute right-[15px] top-8 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />
                      )}
                      {/* Icon */}
                      <div className="w-8 h-8 rounded-full bg-sahool-100 dark:bg-sahool-900/30 flex items-center justify-center flex-shrink-0 z-10">
                        <EventIcon className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
                      </div>
                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-bold text-gray-900 dark:text-gray-100">
                            {event.event_type_ar}
                          </span>
                          <span className="text-xs text-gray-400">
                            {new Date(event.timestamp).toLocaleDateString('ar-YE')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {event.description_ar}
                        </p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
                          <MapPin className="w-3 h-3" />
                          <span>{event.location_ar}</span>
                        </div>
                        <p className="text-xs text-gray-400 mt-0.5">{event.actor_name_ar}</p>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

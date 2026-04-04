'use client';

/**
 * Yemen Soil Type Map Page
 * خريطة التربة اليمنية — خريطة تفاعلية لأنواع التربة والمناطق الزراعية والمناخية
 */

import React, { useState } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import {
  Map,
  Layers,
  FlaskConical,
  TreePine,
  Thermometer,
  Droplets,
  Mountain,
  Sun,
  Wind,
  ChevronDown,
  ChevronUp,
  Info,
  BookOpen,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  Gauge,
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface SoilProperty {
  label: string;
  label_ar: string;
  value: string;
  unit?: string;
}

interface AgroEcoZone {
  id: string;
  name_ar: string;
  name_en: string;
  region_ar: string;
  climate_ar: string;
  climate_en: string;
  soil_type_ar: string;
  soil_type_en: string;
  altitude_range: string;
  rainfall_range: string;
  temperature_range: string;
  properties: SoilProperty[];
  suitable_crops_ar: string[];
  suitable_crops_en: string[];
  color: {
    bg: string;
    border: string;
    badge: string;
    icon: string;
    header: string;
  };
  icon: React.ReactNode;
  area_km2: number;
  field_count: number;
}

interface SoilTest {
  test: string;
  test_ar: string;
  importance_ar: string;
  frequency_ar: string;
}

interface SoilAmendment {
  issue_ar: string;
  amendment_ar: string;
  rate_ar: string;
  notes_ar: string;
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const AGRO_ECO_ZONES: AgroEcoZone[] = [
  {
    id: 'tihama',
    name_ar: 'تهامة',
    name_en: 'Tihama',
    region_ar: 'السهل الساحلي الغربي',
    climate_ar: 'حار رطب — درجات حرارة عالية وأمطار موسمية',
    climate_en: 'Hot & Humid — High temperatures, seasonal rainfall',
    soil_type_ar: 'تربة رملية طينية / طمية',
    soil_type_en: 'Sandy-Clay / Alluvial',
    altitude_range: '0 – 200 م',
    rainfall_range: '100 – 500 ملم/سنة',
    temperature_range: '28 – 42 °C',
    properties: [
      { label: 'pH', label_ar: 'الحموضة', value: '7.0 – 8.2' },
      { label: 'Organic Matter', label_ar: 'المادة العضوية', value: '0.5 – 1.2', unit: '%' },
      { label: 'Water Holding Capacity', label_ar: 'احتباس الماء', value: 'منخفض – متوسط' },
      { label: 'Salinity (EC)', label_ar: 'الملوحة', value: '1.5 – 4.0', unit: 'dS/m' },
      { label: 'Texture', label_ar: 'قوام التربة', value: 'رملية طينية' },
    ],
    suitable_crops_ar: ['الذرة الرفيعة', 'السمسم', 'المانجو', 'الموز', 'القطن', 'قصب السكر'],
    suitable_crops_en: ['Sorghum', 'Sesame', 'Mango', 'Banana', 'Cotton', 'Sugarcane'],
    color: {
      bg: 'bg-amber-50 dark:bg-amber-900/10',
      border: 'border-amber-200 dark:border-amber-800',
      badge: 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300',
      icon: 'text-amber-600 dark:text-amber-400',
      header: 'bg-amber-100 dark:bg-amber-900/20',
    },
    icon: <Sun className="w-5 h-5" />,
    area_km2: 28500,
    field_count: 1842,
  },
  {
    id: 'highlands',
    name_ar: 'المرتفعات',
    name_en: 'Highlands',
    region_ar: 'المرتفعات الوسطى والجنوبية',
    climate_ar: 'معتدل — شتاء بارد وصيف دافئ مع أمطار وفيرة',
    climate_en: 'Temperate — Cool winters, warm summers, high rainfall',
    soil_type_ar: 'تربة طينية طميية / بركانية',
    soil_type_en: 'Clay-Loam / Volcanic',
    altitude_range: '1500 – 3000 م',
    rainfall_range: '400 – 1000 ملم/سنة',
    temperature_range: '12 – 28 °C',
    properties: [
      { label: 'pH', label_ar: 'الحموضة', value: '5.8 – 7.2' },
      { label: 'Organic Matter', label_ar: 'المادة العضوية', value: '2.0 – 5.5', unit: '%' },
      { label: 'Water Holding Capacity', label_ar: 'احتباس الماء', value: 'عالي' },
      { label: 'Salinity (EC)', label_ar: 'الملوحة', value: '0.3 – 1.0', unit: 'dS/m' },
      { label: 'Texture', label_ar: 'قوام التربة', value: 'طينية ثقيلة – طميية' },
    ],
    suitable_crops_ar: ['القمح', 'الشعير', 'البن اليمني', 'القات', 'الخضروات', 'الفاكهة المعتدلة'],
    suitable_crops_en: [
      'Wheat',
      'Barley',
      'Yemeni Coffee',
      'Qat',
      'Vegetables',
      'Temperate Fruits',
    ],
    color: {
      bg: 'bg-green-50 dark:bg-green-900/10',
      border: 'border-green-200 dark:border-green-800',
      badge: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
      icon: 'text-green-600 dark:text-green-400',
      header: 'bg-green-100 dark:bg-green-900/20',
    },
    icon: <Mountain className="w-5 h-5" />,
    area_km2: 45000,
    field_count: 3210,
  },
  {
    id: 'northern-highlands',
    name_ar: 'المرتفعات الشمالية',
    name_en: 'Northern Highlands',
    region_ar: 'المحافظات الشمالية — صعدة وعمران',
    climate_ar: 'بارد جاف — شتاء صقيعي وصيف معتدل',
    climate_en: 'Cool & Arid — Frosty winters, mild summers',
    soil_type_ar: 'تربة صخرية ضحلة / كلسية',
    soil_type_en: 'Rocky-Shallow / Calcareous',
    altitude_range: '2000 – 3600 م',
    rainfall_range: '150 – 350 ملم/سنة',
    temperature_range: '5 – 22 °C',
    properties: [
      { label: 'pH', label_ar: 'الحموضة', value: '7.5 – 8.5' },
      { label: 'Organic Matter', label_ar: 'المادة العضوية', value: '0.8 – 2.0', unit: '%' },
      { label: 'Water Holding Capacity', label_ar: 'احتباس الماء', value: 'منخفض' },
      { label: 'Salinity (EC)', label_ar: 'الملوحة', value: '0.5 – 1.5', unit: 'dS/m' },
      { label: 'Texture', label_ar: 'قوام التربة', value: 'صخرية حجرية' },
    ],
    suitable_crops_ar: ['الشعير', 'العنب', 'اللوز', 'التين', 'الرمان', 'الخوخ'],
    suitable_crops_en: ['Barley', 'Grapes', 'Almonds', 'Figs', 'Pomegranate', 'Peaches'],
    color: {
      bg: 'bg-stone-50 dark:bg-stone-900/10',
      border: 'border-stone-200 dark:border-stone-700',
      badge: 'bg-stone-100 dark:bg-stone-900/30 text-stone-800 dark:text-stone-300',
      icon: 'text-stone-600 dark:text-stone-400',
      header: 'bg-stone-100 dark:bg-stone-900/20',
    },
    icon: <Wind className="w-5 h-5" />,
    area_km2: 38000,
    field_count: 980,
  },
  {
    id: 'eastern-plateau',
    name_ar: 'الهضبة الشرقية',
    name_en: 'Eastern Plateau',
    region_ar: 'مأرب والجوف والبيضاء',
    climate_ar: 'شبه جاف — حرارة معتدلة وأمطار شحيحة غير منتظمة',
    climate_en: 'Semi-Arid — Moderate heat, sparse irregular rainfall',
    soil_type_ar: 'تربة طميية حمراء / بنية',
    soil_type_en: 'Loamy Red-Brown',
    altitude_range: '1000 – 2000 م',
    rainfall_range: '100 – 250 ملم/سنة',
    temperature_range: '18 – 35 °C',
    properties: [
      { label: 'pH', label_ar: 'الحموضة', value: '7.2 – 8.0' },
      { label: 'Organic Matter', label_ar: 'المادة العضوية', value: '0.6 – 1.8', unit: '%' },
      { label: 'Water Holding Capacity', label_ar: 'احتباس الماء', value: 'متوسط' },
      { label: 'Salinity (EC)', label_ar: 'الملوحة', value: '1.0 – 2.5', unit: 'dS/m' },
      { label: 'Texture', label_ar: 'قوام التربة', value: 'طميية' },
    ],
    suitable_crops_ar: ['القمح', 'التمور', 'الذرة الرفيعة', 'اللوبيا', 'الحبة السوداء', 'الكمون'],
    suitable_crops_en: ['Wheat', 'Dates', 'Sorghum', 'Cowpea', 'Black Seed', 'Cumin'],
    color: {
      bg: 'bg-orange-50 dark:bg-orange-900/10',
      border: 'border-orange-200 dark:border-orange-800',
      badge: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300',
      icon: 'text-orange-600 dark:text-orange-400',
      header: 'bg-orange-100 dark:bg-orange-900/20',
    },
    icon: <Layers className="w-5 h-5" />,
    area_km2: 120000,
    field_count: 1420,
  },
  {
    id: 'hadhramaut',
    name_ar: 'حضرموت',
    name_en: 'Hadhramaut',
    region_ar: 'وادي حضرموت والمهرة',
    climate_ar: 'شديد الجفاف — حرارة عالية وأمطار نادرة جداً',
    climate_en: 'Hyper-Arid — Very high heat, extremely rare rainfall',
    soil_type_ar: 'تربة رملية حصوية / وادية',
    soil_type_en: 'Sandy-Gravelly / Wadi Alluvial',
    altitude_range: '0 – 800 م',
    rainfall_range: '20 – 100 ملم/سنة',
    temperature_range: '25 – 48 °C',
    properties: [
      { label: 'pH', label_ar: 'الحموضة', value: '7.8 – 8.8' },
      { label: 'Organic Matter', label_ar: 'المادة العضوية', value: '0.1 – 0.5', unit: '%' },
      { label: 'Water Holding Capacity', label_ar: 'احتباس الماء', value: 'منخفض جداً' },
      { label: 'Salinity (EC)', label_ar: 'الملوحة', value: '2.0 – 6.0', unit: 'dS/m' },
      { label: 'Texture', label_ar: 'قوام التربة', value: 'رملية خشنة' },
    ],
    suitable_crops_ar: ['النخيل (التمور)', 'البرسيم (الفصة)', 'الحناء', 'اللوز', 'البصل', 'الكوسا'],
    suitable_crops_en: ['Date Palm', 'Alfalfa', 'Henna', 'Almonds', 'Onions', 'Zucchini'],
    color: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/10',
      border: 'border-yellow-200 dark:border-yellow-800',
      badge: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
      icon: 'text-yellow-600 dark:text-yellow-400',
      header: 'bg-yellow-100 dark:bg-yellow-900/20',
    },
    icon: <Sun className="w-5 h-5" />,
    area_km2: 191000,
    field_count: 760,
  },
  {
    id: 'southern-coast',
    name_ar: 'الساحل الجنوبي',
    name_en: 'Southern Coast',
    region_ar: 'عدن ولحج وأبين وشبوة الساحلية',
    climate_ar: 'حار — رطوبة عالية وتربة ملحية ساحلية',
    climate_en: 'Hot — High humidity, saline coastal soils',
    soil_type_ar: 'تربة ملحية رملية / طينية ساحلية',
    soil_type_en: 'Saline-Sandy / Coastal Clay',
    altitude_range: '0 – 300 م',
    rainfall_range: '50 – 200 ملم/سنة',
    temperature_range: '26 – 40 °C',
    properties: [
      { label: 'pH', label_ar: 'الحموضة', value: '7.5 – 9.0' },
      { label: 'Organic Matter', label_ar: 'المادة العضوية', value: '0.3 – 1.0', unit: '%' },
      { label: 'Water Holding Capacity', label_ar: 'احتباس الماء', value: 'منخفض – متوسط' },
      { label: 'Salinity (EC)', label_ar: 'الملوحة', value: '3.0 – 8.0', unit: 'dS/m' },
      { label: 'Texture', label_ar: 'قوام التربة', value: 'رملية – طينية ملحية' },
    ],
    suitable_crops_ar: ['الطماطم', 'البصل', 'الباذنجان', 'الخيار', 'زراعة الأسماك', 'المانجروف'],
    suitable_crops_en: ['Tomatoes', 'Onions', 'Eggplant', 'Cucumber', 'Fish Farming', 'Mangrove'],
    color: {
      bg: 'bg-cyan-50 dark:bg-cyan-900/10',
      border: 'border-cyan-200 dark:border-cyan-800',
      badge: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-800 dark:text-cyan-300',
      icon: 'text-cyan-600 dark:text-cyan-400',
      header: 'bg-cyan-100 dark:bg-cyan-900/20',
    },
    icon: <Droplets className="w-5 h-5" />,
    area_km2: 22000,
    field_count: 1105,
  },
  {
    id: 'socotra',
    name_ar: 'سقطرى',
    name_en: 'Socotra',
    region_ar: 'جزيرة سقطرى — المحيط الهندي',
    climate_ar: 'جزيرة معتدلة — رياح موسمية قوية وتربة فريدة متنوعة',
    climate_en: 'Island Temperate — Strong monsoons, unique diverse soils',
    soil_type_ar: 'تربة جزيرية فريدة / صخرية كارستية',
    soil_type_en: 'Unique Island / Karst Rocky',
    altitude_range: '0 – 1500 م',
    rainfall_range: '150 – 600 ملم/سنة',
    temperature_range: '20 – 34 °C',
    properties: [
      { label: 'pH', label_ar: 'الحموضة', value: '6.5 – 8.0' },
      { label: 'Organic Matter', label_ar: 'المادة العضوية', value: '1.0 – 3.5', unit: '%' },
      { label: 'Water Holding Capacity', label_ar: 'احتباس الماء', value: 'متوسط – عالي' },
      { label: 'Salinity (EC)', label_ar: 'الملوحة', value: '0.5 – 2.5', unit: 'dS/m' },
      { label: 'Texture', label_ar: 'قوام التربة', value: 'متنوعة — صخرية وطميية' },
    ],
    suitable_crops_ar: [
      'نباتات متوطنة',
      'شجرة دم الأخوين',
      'التمر الهندي',
      'شجرة القمبير',
      'الألوة',
      'البخور',
    ],
    suitable_crops_en: [
      'Endemic Plants',
      'Dragon Blood Tree',
      'Tamarind',
      'Qambar Tree',
      'Aloe',
      'Frankincense',
    ],
    color: {
      bg: 'bg-purple-50 dark:bg-purple-900/10',
      border: 'border-purple-200 dark:border-purple-800',
      badge: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
      icon: 'text-purple-600 dark:text-purple-400',
      header: 'bg-purple-100 dark:bg-purple-900/20',
    },
    icon: <TreePine className="w-5 h-5" />,
    area_km2: 3625,
    field_count: 215,
  },
];

const SOIL_TESTS: SoilTest[] = [
  {
    test: 'pH Analysis',
    test_ar: 'قياس حموضة التربة (pH)',
    importance_ar: 'يحدد توافر العناصر الغذائية وصحة الجذور',
    frequency_ar: 'مرة واحدة كل موسم',
  },
  {
    test: 'EC / Salinity',
    test_ar: 'الموصلية الكهربائية (EC) والملوحة',
    importance_ar: 'يكشف الضغط الملحي المؤثر على النمو',
    frequency_ar: 'كل 3 أشهر في المناطق الساحلية',
  },
  {
    test: 'Organic Matter',
    test_ar: 'المادة العضوية والكربون',
    importance_ar: 'يقيّم خصوبة التربة وقدرتها على الاحتفاظ بالماء',
    frequency_ar: 'مرة سنوياً',
  },
  {
    test: 'NPK Analysis',
    test_ar: 'تحليل النيتروجين والفوسفور والبوتاسيوم',
    importance_ar: 'العناصر الغذائية الرئيسية لنمو المحاصيل',
    frequency_ar: 'قبل كل موسم زراعي',
  },
  {
    test: 'Micronutrients',
    test_ar: 'العناصر الصغرى (حديد، زنك، منغنيز)',
    importance_ar: 'أساسية لمنع أمراض نقص التغذية',
    frequency_ar: 'مرة كل سنتين',
  },
  {
    test: 'Soil Texture',
    test_ar: 'قوام التربة (رمل، طين، طمي)',
    importance_ar: 'يحدد التصريف ومعدلات الري المناسبة',
    frequency_ar: 'مرة واحدة عند تأسيس الحقل',
  },
];

const SOIL_AMENDMENTS: SoilAmendment[] = [
  {
    issue_ar: 'تربة حمضية (pH < 6.0)',
    amendment_ar: 'كلس زراعي (كربونات الكالسيوم)',
    rate_ar: '1 – 3 طن/هكتار',
    notes_ar: 'تطبيق في الخريف وتقليب بعمق 20 سم',
  },
  {
    issue_ar: 'تربة قلوية (pH > 8.5)',
    amendment_ar: 'كبريت زراعي أو جبس',
    rate_ar: '200 – 500 كجم/هكتار',
    notes_ar: 'مع ري كافٍ لغسيل الأملاح',
  },
  {
    issue_ar: 'ملوحة عالية (EC > 4.0)',
    amendment_ar: 'غسيل ملحي بالماء العذب',
    rate_ar: '150 – 250 ملم/مرة',
    notes_ar: 'تحسين الصرف قبل الغسيل — تكرار حتى انخفاض EC',
  },
  {
    issue_ar: 'نقص المادة العضوية',
    amendment_ar: 'سماد عضوي / كومبوست',
    rate_ar: '10 – 20 طن/هكتار',
    notes_ar: 'تقليب في التربة قبل الزراعة',
  },
  {
    issue_ar: 'نقص النيتروجين',
    amendment_ar: 'يوريا 46% أو نترات أمونيوم',
    rate_ar: '46 – 92 كجم/هكتار',
    notes_ar: 'تطبيق على جرعات متقسمة — الأولى عند الإنبات',
  },
  {
    issue_ar: 'تربة رملية خفيفة (احتباس ماء منخفض)',
    amendment_ar: 'بيرلايت أو هيدروجيل + كومبوست',
    rate_ar: '5 – 10 كجم/100م²',
    notes_ar: 'يزيد من قدرة التربة على الاحتفاظ بالماء والغذاء',
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function SoilMapPage() {
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);
  const [expandedZoneId, setExpandedZoneId] = useState<string | null>('highlands');
  const [activeTab, setActiveTab] = useState<'zones' | 'tests' | 'amendments'>('zones');
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'offline'>('loading');

  // Try to connect to soil-analysis-service for live data
  React.useEffect(() => {
    fetch('/api/proxy/soil-analysis/healthz')
      .then((r) => r.ok ? setApiStatus('connected') : setApiStatus('offline'))
      .catch(() => setApiStatus('offline'));
  }, []);

  const selectedZone = AGRO_ECO_ZONES.find((z) => z.id === selectedZoneId);

  const totalFields = AGRO_ECO_ZONES.reduce((s, z) => s + z.field_count, 0);

  function toggleExpand(zoneId: string) {
    setExpandedZoneId((prev) => (prev === zoneId ? null : zoneId));
    setSelectedZoneId(zoneId);
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* ── Header ── */}
      <Header
        title="خريطة التربة اليمنية"
        subtitle="خريطة تفاعلية لأنواع التربة والمناطق الزراعية والمناخية في اليمن"
      />

      {/* Data source indicator */}
      {apiStatus === 'offline' && (
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-700">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>بيانات مرجعية ثابتة — خدمة تحليل التربة غير متاحة حالياً</span>
        </div>
      )}

      {/* ── Stats Row ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="أنواع التربة المرصودة"
          value={7}
          icon={Layers}
          iconColor="text-amber-600"
          suffix="نوع"
        />
        <StatCard
          title="المناطق الزراعية البيئية"
          value={7}
          icon={Map}
          iconColor="text-green-600"
          suffix="منطقة"
        />
        <StatCard
          title="الحقول المسجلة"
          value={totalFields}
          icon={TreePine}
          iconColor="text-emerald-600"
          suffix="حقل"
          trend={{ value: 8, isPositive: true }}
        />
        <StatCard
          title="اختبارات التربة المنجزة"
          value={2847}
          icon={FlaskConical}
          iconColor="text-blue-600"
          suffix="اختبار"
          trend={{ value: 15, isPositive: true }}
        />
      </div>

      {/* ── Tab Navigation ── */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        {[
          {
            id: 'zones' as const,
            label: 'المناطق الزراعية البيئية',
            icon: <Map className="w-4 h-4" />,
          },
          {
            id: 'tests' as const,
            label: 'دليل الاختبارات',
            icon: <FlaskConical className="w-4 h-4" />,
          },
          {
            id: 'amendments' as const,
            label: 'مرشد تحسين التربة',
            icon: <BookOpen className="w-4 h-4" />,
          },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-sahool-600 text-sahool-700 dark:text-sahool-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            {tab.icon}
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* ── Zones Tab ── */}
      {activeTab === 'zones' && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Zone Cards List */}
          <div className="xl:col-span-2 space-y-3">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              اضغط على أي منطقة لعرض التفاصيل الكاملة
            </p>

            {AGRO_ECO_ZONES.map((zone) => {
              const isExpanded = expandedZoneId === zone.id;
              return (
                <div
                  key={zone.id}
                  className={`rounded-xl border transition-all cursor-pointer ${zone.color.bg} ${zone.color.border} ${
                    isExpanded ? 'shadow-md' : 'hover:shadow-sm'
                  }`}
                >
                  {/* Zone Header Row */}
                  <button
                    type="button"
                    onClick={() => toggleExpand(zone.id)}
                    className="w-full text-right"
                  >
                    <div
                      className={`flex items-center gap-3 p-4 rounded-t-xl ${isExpanded ? zone.color.header : ''}`}
                    >
                      {/* Icon */}
                      <div
                        className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${zone.color.badge}`}
                      >
                        <span className={zone.color.icon}>{zone.icon}</span>
                      </div>

                      {/* Name & Summary */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-base font-bold text-gray-900 dark:text-gray-100">
                            {zone.name_ar}
                          </h3>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            ({zone.name_en})
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-xs font-medium ${zone.color.badge}`}
                          >
                            {zone.field_count.toLocaleString('ar-YE')} حقل
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5 truncate">
                          {zone.soil_type_ar} — {zone.region_ar}
                        </p>
                      </div>

                      {/* Quick Stats */}
                      <div className="hidden sm:flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">
                        <div className="text-center">
                          <p className="font-bold text-gray-700 dark:text-gray-300">
                            {zone.altitude_range}
                          </p>
                          <p>الارتفاع</p>
                        </div>
                        <div className="text-center">
                          <p className="font-bold text-gray-700 dark:text-gray-300">
                            {zone.rainfall_range}
                          </p>
                          <p>الأمطار</p>
                        </div>
                      </div>

                      {/* Expand Icon */}
                      <div className={`flex-shrink-0 ${zone.color.icon}`}>
                        {isExpanded ? (
                          <ChevronUp className="w-5 h-5" />
                        ) : (
                          <ChevronDown className="w-5 h-5" />
                        )}
                      </div>
                    </div>
                  </button>

                  {/* Expanded Detail */}
                  {isExpanded && (
                    <div className="p-4 pt-0 border-t border-gray-100 dark:border-gray-700/50 space-y-4">
                      {/* Climate Summary */}
                      <div className="flex gap-3 mt-3">
                        <div className="flex-1 p-3 bg-white/70 dark:bg-gray-800/50 rounded-lg">
                          <div className="flex items-center gap-1.5 mb-1">
                            <Thermometer className="w-4 h-4 text-red-500" />
                            <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                              المناخ
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            {zone.climate_ar}
                          </p>
                        </div>
                        <div className="flex-1 p-3 bg-white/70 dark:bg-gray-800/50 rounded-lg">
                          <div className="flex items-center gap-1.5 mb-1">
                            <Droplets className="w-4 h-4 text-blue-500" />
                            <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                              درجة الحرارة
                            </span>
                          </div>
                          <p className="text-sm font-bold text-gray-700 dark:text-gray-300">
                            {zone.temperature_range}
                          </p>
                        </div>
                      </div>

                      {/* Soil Properties Grid */}
                      <div>
                        <h4 className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                          خصائص التربة الرئيسية
                        </h4>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                          {zone.properties.map((prop) => (
                            <div
                              key={prop.label}
                              className="p-2.5 bg-white/70 dark:bg-gray-800/50 rounded-lg"
                            >
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {prop.label_ar}
                              </p>
                              <p className="text-sm font-bold text-gray-800 dark:text-gray-200 mt-0.5">
                                {prop.value}
                                {prop.unit && (
                                  <span className="text-xs font-normal text-gray-500 mr-1">
                                    {prop.unit}
                                  </span>
                                )}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Suitable Crops */}
                      <div>
                        <h4 className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                          المحاصيل الملائمة
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {zone.suitable_crops_ar.map((crop, i) => (
                            <span
                              key={crop}
                              className={`px-2.5 py-1 rounded-full text-xs font-medium ${zone.color.badge}`}
                            >
                              {crop}
                              <span className="text-gray-400 mr-1 text-xs">
                                ({zone.suitable_crops_en[i]})
                              </span>
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Range Info */}
                      <div className="grid grid-cols-3 gap-2 pt-1">
                        <div className="flex items-center gap-2 p-2 bg-white/70 dark:bg-gray-800/50 rounded-lg">
                          <Mountain className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <div>
                            <p className="text-xs text-gray-400">الارتفاع</p>
                            <p className="text-xs font-bold text-gray-700 dark:text-gray-300">
                              {zone.altitude_range}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 p-2 bg-white/70 dark:bg-gray-800/50 rounded-lg">
                          <Droplets className="w-4 h-4 text-blue-400 flex-shrink-0" />
                          <div>
                            <p className="text-xs text-gray-400">هطول الأمطار</p>
                            <p className="text-xs font-bold text-gray-700 dark:text-gray-300">
                              {zone.rainfall_range}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 p-2 bg-white/70 dark:bg-gray-800/50 rounded-lg">
                          <Map className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <div>
                            <p className="text-xs text-gray-400">المساحة</p>
                            <p className="text-xs font-bold text-gray-700 dark:text-gray-300">
                              {zone.area_km2.toLocaleString('ar-YE')} كم²
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Zone Detail / Filter Panel */}
          <div className="space-y-4">
            {/* Zone Filter Selector */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
              <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                <Map className="w-4 h-4 text-sahool-600" />
                تصفية حسب المنطقة
              </h3>
              <div className="space-y-1.5">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedZoneId(null);
                    setExpandedZoneId(null);
                  }}
                  className={`w-full text-right px-3 py-2 rounded-lg text-sm transition-colors ${
                    !selectedZoneId
                      ? 'bg-sahool-50 dark:bg-sahool-900/20 text-sahool-700 dark:text-sahool-400 font-medium'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                >
                  جميع المناطق ({AGRO_ECO_ZONES.length})
                </button>
                {AGRO_ECO_ZONES.map((zone) => (
                  <button
                    key={zone.id}
                    type="button"
                    onClick={() => toggleExpand(zone.id)}
                    className={`w-full text-right px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between gap-2 ${
                      selectedZoneId === zone.id
                        ? `${zone.color.badge} font-medium`
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span className={zone.color.icon}>{zone.icon}</span>
                      {zone.name_ar}
                    </span>
                    <span className="text-xs opacity-70">{zone.field_count}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Selected Zone Summary Card */}
            {selectedZone ? (
              <div
                className={`rounded-xl border p-4 ${selectedZone.color.bg} ${selectedZone.color.border}`}
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className={selectedZone.color.icon}>{selectedZone.icon}</span>
                  <div>
                    <h4 className="font-bold text-gray-900 dark:text-gray-100">
                      {selectedZone.name_ar}
                    </h4>
                    <p className="text-xs text-gray-500">{selectedZone.name_en}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">نوع التربة</span>
                    <span className="font-medium text-gray-800 dark:text-gray-200">
                      {selectedZone.soil_type_ar}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">المساحة</span>
                    <span className="font-medium text-gray-800 dark:text-gray-200">
                      {selectedZone.area_km2.toLocaleString('ar-YE')} كم²
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">الحقول</span>
                    <span className="font-medium text-gray-800 dark:text-gray-200">
                      {selectedZone.field_count.toLocaleString('ar-YE')} حقل
                    </span>
                  </div>
                  <hr className="border-gray-200 dark:border-gray-700" />
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {selectedZone.climate_ar}
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 text-center">
                <Info className="w-8 h-8 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  اختر منطقة لعرض ملخص خصائصها
                </p>
              </div>
            )}

            {/* Yemen Map Placeholder */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
              <h4 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                <Map className="w-4 h-4 text-sahool-600" />
                خريطة اليمن الزراعية
              </h4>
              <div className="relative bg-gradient-to-br from-amber-50 via-green-50 to-blue-50 dark:from-gray-800 dark:via-gray-850 dark:to-gray-800 rounded-lg h-48 flex items-center justify-center border border-dashed border-gray-300 dark:border-gray-600">
                <div className="text-center">
                  <Map className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
                  <p className="text-xs text-gray-400 dark:text-gray-500">الخريطة التفاعلية</p>
                  <p className="text-xs text-gray-300 dark:text-gray-600">PostGIS / MapLibre GL</p>
                </div>
                {/* Color legend spots */}
                <div className="absolute bottom-2 right-2 flex gap-1">
                  {[
                    'bg-amber-400',
                    'bg-green-400',
                    'bg-stone-400',
                    'bg-orange-400',
                    'bg-yellow-400',
                    'bg-cyan-400',
                    'bg-purple-400',
                  ].map((c, i) => (
                    <div
                      key={i}
                      className={`w-3 h-3 rounded-full ${c} opacity-80`}
                      title={AGRO_ECO_ZONES[i]?.name_ar}
                    />
                  ))}
                </div>
              </div>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 text-center">
                سيتم دمج خريطة المتجهات الجغرافية مع PostGIS
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Tests Tab ── */}
      {activeTab === 'tests' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recommended Tests */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <FlaskConical className="w-5 h-5 text-blue-600" />
              الاختبارات الموصى بها
            </h3>
            <div className="space-y-3">
              {SOIL_TESTS.map((test, i) => (
                <div
                  key={test.test}
                  className="flex gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700"
                >
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0 text-blue-700 dark:text-blue-400 font-bold text-sm">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
                      {test.test_ar}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                      {test.importance_ar}
                    </p>
                    <div className="flex items-center gap-1 mt-1.5">
                      <CheckCircle className="w-3 h-3 text-green-500" />
                      <span className="text-xs text-green-700 dark:text-green-400">
                        {test.frequency_ar}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Interpretation Guide */}
          <div className="space-y-4">
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
              <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-amber-600" />
                دليل تفسير النتائج
              </h3>

              {/* pH Guide */}
              <div className="mb-4">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  مقياس حموضة التربة (pH)
                </p>
                <div className="space-y-1.5">
                  {[
                    {
                      range: '< 5.5',
                      label: 'حمضي جداً',
                      color: 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400',
                    },
                    {
                      range: '5.5 – 6.5',
                      label: 'حمضي قليلاً — مثالي للبن والفاكهة',
                      color:
                        'bg-orange-100 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400',
                    },
                    {
                      range: '6.5 – 7.5',
                      label: 'محايد — مثالي لمعظم المحاصيل',
                      color: 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400',
                    },
                    {
                      range: '7.5 – 8.5',
                      label: 'قلوي — مقبول للحبوب والنخيل',
                      color:
                        'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400',
                    },
                    {
                      range: '> 8.5',
                      label: 'قلوي جداً — يستدعي معالجة',
                      color: 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400',
                    },
                  ].map((row) => (
                    <div
                      key={row.range}
                      className={`flex items-center justify-between px-3 py-1.5 rounded-lg text-xs ${row.color}`}
                    >
                      <span className="font-bold">{row.range}</span>
                      <span>{row.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* EC Guide */}
              <div>
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  مقياس الملوحة (EC — dS/m)
                </p>
                <div className="space-y-1.5">
                  {[
                    {
                      range: '< 1.0',
                      label: 'غير ملحية — آمنة لجميع المحاصيل',
                      color: 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400',
                    },
                    {
                      range: '1.0 – 2.0',
                      label: 'ملوحة منخفضة — مناسبة لمعظم المحاصيل',
                      color: 'bg-lime-100 dark:bg-lime-900/20 text-lime-700 dark:text-lime-400',
                    },
                    {
                      range: '2.0 – 4.0',
                      label: 'متوسطة — تأثير محدود على الحساسة',
                      color:
                        'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400',
                    },
                    {
                      range: '4.0 – 8.0',
                      label: 'مرتفعة — حبوب ونخيل فقط',
                      color:
                        'bg-orange-100 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400',
                    },
                    {
                      range: '> 8.0',
                      label: 'حرجة — تتطلب معالجة عاجلة',
                      color: 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400',
                    },
                  ].map((row) => (
                    <div
                      key={row.range}
                      className={`flex items-center justify-between px-3 py-1.5 rounded-lg text-xs ${row.color}`}
                    >
                      <span className="font-bold">{row.range}</span>
                      <span>{row.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Organic Matter Guide */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
              <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                <Gauge className="w-4 h-4 text-green-600" />
                المادة العضوية — معايير التقييم
              </h3>
              <div className="grid grid-cols-3 gap-2">
                {[
                  {
                    label: 'منخفضة',
                    range: '< 1%',
                    color:
                      'bg-red-50 dark:bg-red-900/10 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800',
                  },
                  {
                    label: 'مقبولة',
                    range: '1 – 3%',
                    color:
                      'bg-yellow-50 dark:bg-yellow-900/10 text-yellow-700 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800',
                  },
                  {
                    label: 'ممتازة',
                    range: '> 3%',
                    color:
                      'bg-green-50 dark:bg-green-900/10 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800',
                  },
                ].map((m) => (
                  <div key={m.label} className={`p-3 rounded-lg border text-center ${m.color}`}>
                    <p className="font-bold text-sm">{m.range}</p>
                    <p className="text-xs mt-0.5">{m.label}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Amendments Tab ── */}
      {activeTab === 'amendments' && (
        <div className="space-y-4">
          <div className="flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800 rounded-xl">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">تنبيه مهم</p>
              <p className="text-sm text-amber-700 dark:text-amber-400 mt-0.5">
                التوصيات التالية هي إرشادات عامة. يجب إجراء اختبار تربة معتمد قبل تطبيق أي معالجة.
                استشر خبير زراعي محلي.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {SOIL_AMENDMENTS.map((amendment, i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/20 flex items-center justify-center flex-shrink-0">
                    <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900 dark:text-gray-100">المشكلة</p>
                    <p className="text-sm text-red-700 dark:text-red-400">{amendment.issue_ar}</p>
                  </div>
                </div>

                <div className="space-y-2 mr-11">
                  <div className="flex items-start gap-2">
                    <ArrowRight className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">التعديل الموصى به</p>
                      <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
                        {amendment.amendment_ar}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-2">
                    <Gauge className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">المعدل</p>
                      <p className="text-sm font-semibold text-blue-700 dark:text-blue-400">
                        {amendment.rate_ar}
                      </p>
                    </div>
                  </div>

                  <div className="p-2.5 bg-gray-50 dark:bg-gray-800 rounded-lg mt-2">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                      ملاحظات التطبيق
                    </p>
                    <p className="text-xs text-gray-700 dark:text-gray-300">{amendment.notes_ar}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Zone-Specific Recommendations */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h3 className="text-base font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Map className="w-5 h-5 text-sahool-600" />
              توصيات خاصة بالمناطق اليمنية
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                {
                  zone: 'تهامة',
                  icon: <Sun className="w-4 h-4" />,
                  color: 'text-amber-600',
                  bg: 'bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-800',
                  tips: [
                    'إضافة كومبوست لتحسين الاحتباس المائي',
                    'مراقبة دورية لملوحة التربة',
                    'الري بالتنقيط لتقليل الملوحة',
                  ],
                },
                {
                  zone: 'المرتفعات',
                  icon: <Mountain className="w-4 h-4" />,
                  color: 'text-green-600',
                  bg: 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800',
                  tips: [
                    'الحفاظ على المادة العضوية',
                    'مراقبة حموضة تربة البن (pH 5.5-6.5)',
                    'برامج تخصيب متوازنة NPK',
                  ],
                },
                {
                  zone: 'حضرموت',
                  icon: <Sun className="w-4 h-4" />,
                  color: 'text-yellow-600',
                  bg: 'bg-yellow-50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-800',
                  tips: [
                    'غسيل ملحي دوري للنخيل',
                    'إضافة مادة عضوية كثيفة',
                    'ري بالتنقيط لتوفير المياه',
                  ],
                },
                {
                  zone: 'الساحل الجنوبي',
                  icon: <Droplets className="w-4 h-4" />,
                  color: 'text-cyan-600',
                  bg: 'bg-cyan-50 dark:bg-cyan-900/10 border-cyan-200 dark:border-cyan-800',
                  tips: [
                    'اختيار أصناف متحملة للملوحة',
                    'تحسين الصرف الزراعي',
                    'مراقبة EC بعد كل ري',
                  ],
                },
              ].map((rec) => (
                <div key={rec.zone} className={`p-4 rounded-xl border ${rec.bg}`}>
                  <div className={`flex items-center gap-2 mb-3 font-bold ${rec.color}`}>
                    {rec.icon}
                    <span className="text-sm">{rec.zone}</span>
                  </div>
                  <ul className="space-y-1.5">
                    {rec.tips.map((tip) => (
                      <li
                        key={tip}
                        className="flex items-start gap-1.5 text-xs text-gray-700 dark:text-gray-300"
                      >
                        <CheckCircle className="w-3.5 h-3.5 text-green-500 flex-shrink-0 mt-0.5" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

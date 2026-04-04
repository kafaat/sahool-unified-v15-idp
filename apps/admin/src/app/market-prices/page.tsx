'use client';

// Market Prices Dashboard Page
// صفحة لوحة أسعار السوق

import React, { useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import { cn } from '@/lib/utils';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  BarChart2,
  Bell,
  ShoppingBasket,
  Store,
  RefreshCw,
  Download,
  Filter,
  Star,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  MapPin,
  Award,
  ChevronRight,
  X,
} from 'lucide-react';

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

type Trend = 'up' | 'down' | 'stable';
type Quality = 'PREMIUM' | 'GRADE_A' | 'GRADE_B';

interface MarketPrice {
  id: string;
  cropName: string;
  cropNameEn: string;
  cropIcon: string;
  currentPrice: number;
  previousPrice: number;
  unit: string;
  changePercent: number;
  market: string;
  marketEn: string;
  quality: Quality;
  trend: Trend;
  lastUpdated: string;
  category: string;
  weekHistory: number[];
  marketComparison: { market: string; price: number }[];
  bestSellRecommendation: string;
}

// ─────────────────────────────────────────────
// Mock Data
// ─────────────────────────────────────────────

const MOCK_PRICES: MarketPrice[] = [
  {
    id: '1',
    cropName: 'قمح',
    cropNameEn: 'Wheat',
    cropIcon: '🌾',
    currentPrice: 2.8,
    previousPrice: 2.71,
    unit: 'ريال/كغ',
    changePercent: 3.2,
    market: 'الرياض',
    marketEn: 'Riyadh',
    quality: 'GRADE_A',
    trend: 'up',
    lastUpdated: 'منذ 30 دقيقة',
    category: 'حبوب',
    weekHistory: [2.6, 2.65, 2.71, 2.7, 2.74, 2.78, 2.8],
    marketComparison: [
      { market: 'الرياض', price: 2.8 },
      { market: 'جدة', price: 2.75 },
      { market: 'الدمام', price: 2.77 },
    ],
    bestSellRecommendation: 'الرياض — أعلى سعر حالياً بزيادة 3.2% عن الأسبوع الماضي',
  },
  {
    id: '2',
    cropName: 'شعير',
    cropNameEn: 'Barley',
    cropIcon: '🌿',
    currentPrice: 2.1,
    previousPrice: 2.13,
    unit: 'ريال/كغ',
    changePercent: -1.5,
    market: 'جدة',
    marketEn: 'Jeddah',
    quality: 'GRADE_A',
    trend: 'down',
    lastUpdated: 'منذ ساعة',
    category: 'حبوب',
    weekHistory: [2.2, 2.18, 2.15, 2.14, 2.13, 2.11, 2.1],
    marketComparison: [
      { market: 'جدة', price: 2.1 },
      { market: 'الرياض', price: 2.14 },
      { market: 'الدمام', price: 2.12 },
    ],
    bestSellRecommendation: 'الرياض — أعلى سعر بـ 2.14 ريال/كغ رغم الاتجاه النزولي',
  },
  {
    id: '3',
    cropName: 'تمور (خلاص)',
    cropNameEn: 'Dates (Khalas)',
    cropIcon: '🌴',
    currentPrice: 35.0,
    previousPrice: 32.41,
    unit: 'ريال/كغ',
    changePercent: 8.0,
    market: 'القصيم',
    marketEn: 'Qassim',
    quality: 'PREMIUM',
    trend: 'up',
    lastUpdated: 'منذ 15 دقيقة',
    category: 'فواكه',
    weekHistory: [30.0, 31.0, 31.5, 32.41, 33.0, 34.0, 35.0],
    marketComparison: [
      { market: 'القصيم', price: 35.0 },
      { market: 'الرياض', price: 33.5 },
      { market: 'المدينة', price: 34.0 },
    ],
    bestSellRecommendation: 'القصيم — موسم الطلب الذروة، يُنصح بالبيع الفوري',
  },
  {
    id: '4',
    cropName: 'طماطم',
    cropNameEn: 'Tomato',
    cropIcon: '🍅',
    currentPrice: 4.5,
    previousPrice: 4.75,
    unit: 'ريال/كغ',
    changePercent: -5.2,
    market: 'الرياض',
    marketEn: 'Riyadh',
    quality: 'GRADE_A',
    trend: 'down',
    lastUpdated: 'منذ 45 دقيقة',
    category: 'خضروات',
    weekHistory: [5.0, 4.9, 4.8, 4.75, 4.7, 4.6, 4.5],
    marketComparison: [
      { market: 'الرياض', price: 4.5 },
      { market: 'جدة', price: 4.6 },
      { market: 'الدمام', price: 4.55 },
    ],
    bestSellRecommendation: 'جدة — أعلى سعر حالياً بـ 4.60 ريال/كغ',
  },
  {
    id: '5',
    cropName: 'بطاطس',
    cropNameEn: 'Potato',
    cropIcon: '🥔',
    currentPrice: 3.2,
    previousPrice: 3.14,
    unit: 'ريال/كغ',
    changePercent: 1.8,
    market: 'الدمام',
    marketEn: 'Dammam',
    quality: 'GRADE_A',
    trend: 'stable',
    lastUpdated: 'منذ ساعتين',
    category: 'خضروات',
    weekHistory: [3.1, 3.12, 3.14, 3.15, 3.16, 3.18, 3.2],
    marketComparison: [
      { market: 'الدمام', price: 3.2 },
      { market: 'الرياض', price: 3.18 },
      { market: 'جدة', price: 3.15 },
    ],
    bestSellRecommendation: 'الدمام — استقرار سعري مع ارتفاع طفيف، مناسب للتخزين',
  },
  {
    id: '6',
    cropName: 'بصل',
    cropNameEn: 'Onion',
    cropIcon: '🧅',
    currentPrice: 2.9,
    previousPrice: 2.96,
    unit: 'ريال/كغ',
    changePercent: -2.1,
    market: 'جدة',
    marketEn: 'Jeddah',
    quality: 'GRADE_B',
    trend: 'down',
    lastUpdated: 'منذ 3 ساعات',
    category: 'خضروات',
    weekHistory: [3.1, 3.05, 3.0, 2.96, 2.95, 2.92, 2.9],
    marketComparison: [
      { market: 'جدة', price: 2.9 },
      { market: 'الرياض', price: 2.95 },
      { market: 'مكة', price: 2.93 },
    ],
    bestSellRecommendation: 'الرياض — أعلى سعر حالياً بـ 2.95 ريال/كغ',
  },
  {
    id: '7',
    cropName: 'بن يمني',
    cropNameEn: 'Yemeni Coffee',
    cropIcon: '☕',
    currentPrice: 120.0,
    previousPrice: 106.67,
    unit: 'ريال/كغ',
    changePercent: 12.5,
    market: 'صنعاء',
    marketEn: "Sana'a",
    quality: 'PREMIUM',
    trend: 'up',
    lastUpdated: 'منذ ساعة',
    category: 'محاصيل نقدية',
    weekHistory: [100.0, 103.0, 106.67, 108.0, 112.0, 117.0, 120.0],
    marketComparison: [
      { market: 'صنعاء', price: 120.0 },
      { market: 'عدن', price: 115.0 },
      { market: 'إب', price: 118.0 },
    ],
    bestSellRecommendation: 'صنعاء — ارتفاع استثنائي 12.5%، فرصة بيع ممتازة',
  },
  {
    id: '8',
    cropName: 'ذرة رفيعة',
    cropNameEn: 'Sorghum',
    cropIcon: '🌾',
    currentPrice: 1.8,
    previousPrice: 1.79,
    unit: 'ريال/كغ',
    changePercent: 0.5,
    market: 'الحديدة',
    marketEn: 'Hodeidah',
    quality: 'GRADE_B',
    trend: 'stable',
    lastUpdated: 'منذ 4 ساعات',
    category: 'حبوب',
    weekHistory: [1.78, 1.78, 1.79, 1.79, 1.79, 1.8, 1.8],
    marketComparison: [
      { market: 'الحديدة', price: 1.8 },
      { market: 'صنعاء', price: 1.82 },
      { market: 'تعز', price: 1.78 },
    ],
    bestSellRecommendation: 'صنعاء — سعر أعلى بـ 1.82 ريال/كغ مع استقرار عام',
  },
  {
    id: '9',
    cropName: 'مانجو',
    cropNameEn: 'Mango',
    cropIcon: '🥭',
    currentPrice: 15.0,
    previousPrice: 14.11,
    unit: 'ريال/كغ',
    changePercent: 6.3,
    market: 'عدن',
    marketEn: 'Aden',
    quality: 'PREMIUM',
    trend: 'up',
    lastUpdated: 'منذ 20 دقيقة',
    category: 'فواكه',
    weekHistory: [12.5, 13.0, 13.5, 14.11, 14.5, 14.8, 15.0],
    marketComparison: [
      { market: 'عدن', price: 15.0 },
      { market: 'تعز', price: 14.5 },
      { market: 'إب', price: 14.8 },
    ],
    bestSellRecommendation: 'عدن — موسم الذروة، الطلب مرتفع وارتفاع 6.3% هذا الأسبوع',
  },
  {
    id: '10',
    cropName: 'عنب',
    cropNameEn: 'Grapes',
    cropIcon: '🍇',
    currentPrice: 8.5,
    previousPrice: 8.83,
    unit: 'ريال/كغ',
    changePercent: -3.7,
    market: 'تعز',
    marketEn: 'Taiz',
    quality: 'GRADE_A',
    trend: 'down',
    lastUpdated: 'منذ ساعتين',
    category: 'فواكه',
    weekHistory: [9.2, 9.0, 8.83, 8.7, 8.6, 8.55, 8.5],
    marketComparison: [
      { market: 'تعز', price: 8.5 },
      { market: 'صنعاء', price: 8.7 },
      { market: 'إب', price: 8.65 },
    ],
    bestSellRecommendation: 'صنعاء — أعلى سعر بـ 8.70 ريال/كغ، يُفضل النقل',
  },
];

const MARKETS = ['الكل', 'الرياض', 'جدة', 'الدمام', 'القصيم', 'صنعاء', 'عدن', 'الحديدة', 'تعز'];
const CATEGORIES = ['الكل', 'حبوب', 'خضروات', 'فواكه', 'محاصيل نقدية'];
const TRENDS = ['الكل', 'صاعد', 'هابط', 'مستقر'];

// ─────────────────────────────────────────────
// Helper Components
// ─────────────────────────────────────────────

function QualityBadge({ quality }: { quality: Quality }) {
  const config: Record<Quality, { label: string; className: string }> = {
    PREMIUM: {
      label: 'ممتاز',
      className: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
    },
    GRADE_A: {
      label: 'درجة أ',
      className: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    },
    GRADE_B: {
      label: 'درجة ب',
      className: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    },
  };
  const { label, className } = config[quality];
  return (
    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', className)}>
      {quality === 'PREMIUM' && <Star className="inline w-3 h-3 mr-0.5 mb-0.5" />}
      {label}
    </span>
  );
}

function TrendIcon({ trend, size = 4 }: { trend: Trend; size?: number }) {
  if (trend === 'up') return <TrendingUp className={cn(`w-${size} h-${size}`, 'text-green-500')} />;
  if (trend === 'down')
    return <TrendingDown className={cn(`w-${size} h-${size}`, 'text-red-500')} />;
  return <Minus className={cn(`w-${size} h-${size}`, 'text-gray-400')} />;
}

function ChangeLabel({ change, trend }: { change: number; trend: Trend }) {
  const abs = Math.abs(change).toFixed(1);
  if (trend === 'up')
    return (
      <span className="flex items-center gap-0.5 text-green-600 dark:text-green-400 font-medium text-sm">
        <ArrowUpRight className="w-3.5 h-3.5" />+{abs}%
      </span>
    );
  if (trend === 'down')
    return (
      <span className="flex items-center gap-0.5 text-red-600 dark:text-red-400 font-medium text-sm">
        <ArrowDownRight className="w-3.5 h-3.5" />-{abs}%
      </span>
    );
  return (
    <span className="flex items-center gap-0.5 text-gray-500 dark:text-gray-400 font-medium text-sm">
      <Minus className="w-3.5 h-3.5" />
      {abs}%
    </span>
  );
}

function MiniSparkline({ data, trend }: { data: number[]; trend: Trend }) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const width = 80;
  const height = 28;
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x},${y}`;
  });
  const color = trend === 'up' ? '#16a34a' : trend === 'down' ? '#dc2626' : '#6b7280';
  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points.join(' ')}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

function PriceCard({
  crop,
  onClick,
  isSelected,
}: {
  crop: MarketPrice;
  onClick: () => void;
  isSelected: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-right bg-white dark:bg-gray-800 rounded-xl border p-4 transition-all hover:shadow-md hover:-translate-y-0.5',
        isSelected
          ? 'border-sahool-500 ring-2 ring-sahool-200 dark:ring-sahool-800 shadow-md'
          : 'border-gray-100 dark:border-gray-700'
      )}
    >
      {/* Header row */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{crop.cropIcon}</span>
          <div>
            <p className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
              {crop.cropName}
            </p>
            <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
              <MapPin className="w-3 h-3" />
              {crop.market}
            </div>
          </div>
        </div>
        <QualityBadge quality={crop.quality} />
      </div>

      {/* Price and change */}
      <div className="flex items-end justify-between mb-3">
        <div>
          <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {crop.currentPrice.toFixed(2)}
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500">{crop.unit}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <ChangeLabel change={crop.changePercent} trend={crop.trend} />
          <div className="flex items-center gap-1">
            <TrendIcon trend={crop.trend} size={3} />
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {crop.trend === 'up' ? 'صاعد' : crop.trend === 'down' ? 'هابط' : 'مستقر'}
            </span>
          </div>
        </div>
      </div>

      {/* Sparkline */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400 dark:text-gray-500">{crop.lastUpdated}</span>
        <MiniSparkline data={crop.weekHistory} trend={crop.trend} />
      </div>
    </button>
  );
}

function DetailPanel({ crop, onClose }: { crop: MarketPrice; onClose: () => void }) {
  const maxHistory = Math.max(...crop.weekHistory);
  const minHistory = Math.min(...crop.weekHistory);
  const range = maxHistory - minHistory || 1;

  const days = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
  const today = new Date().getDay();
  const dayLabels = Array.from({ length: 7 }, (_, i) => days[(today - 6 + i + 7) % 7]);

  const maxMarketPrice = Math.max(...crop.marketComparison.map((m) => m.price));

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5 shadow-sm">
      {/* Panel header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{crop.cropIcon}</span>
          <div>
            <h3 className="font-bold text-gray-900 dark:text-gray-100">{crop.cropName}</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">{crop.cropNameEn}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Current price highlight */}
      <div
        className={cn(
          'rounded-xl p-4 mb-4 flex items-center justify-between',
          crop.trend === 'up'
            ? 'bg-green-50 dark:bg-green-900/20'
            : crop.trend === 'down'
              ? 'bg-red-50 dark:bg-red-900/20'
              : 'bg-gray-50 dark:bg-gray-700/50'
        )}
      >
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">السعر الحالي</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {crop.currentPrice.toFixed(2)}{' '}
            <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
              {crop.unit}
            </span>
          </p>
        </div>
        <div className="text-left">
          <ChangeLabel change={crop.changePercent} trend={crop.trend} />
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            السابق: {crop.previousPrice.toFixed(2)}
          </p>
        </div>
      </div>

      {/* 7-day price history */}
      <div className="mb-5">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-1">
          <Activity className="w-4 h-4" />
          سجل الأسعار (7 أيام)
        </p>
        <div className="space-y-1.5">
          {crop.weekHistory.map((price, i) => {
            const barPercent = ((price - minHistory) / range) * 100;
            const isToday = i === crop.weekHistory.length - 1;
            return (
              <div key={i} className="flex items-center gap-2">
                <span className="text-xs text-gray-400 dark:text-gray-500 w-16 text-left shrink-0">
                  {dayLabels[i]}
                </span>
                <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full transition-all',
                      isToday
                        ? crop.trend === 'up'
                          ? 'bg-green-500'
                          : crop.trend === 'down'
                            ? 'bg-red-500'
                            : 'bg-sahool-500'
                        : 'bg-gray-300 dark:bg-gray-600'
                    )}
                    style={{ width: `${Math.max(barPercent, 8)}%` }}
                  />
                </div>
                <span
                  className={cn(
                    'text-xs font-medium w-14 text-right shrink-0',
                    isToday
                      ? 'text-gray-900 dark:text-gray-100'
                      : 'text-gray-500 dark:text-gray-400'
                  )}
                >
                  {price.toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Market comparison */}
      <div className="mb-5">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-1">
          <Store className="w-4 h-4" />
          مقارنة الأسواق
        </p>
        <div className="space-y-2">
          {crop.marketComparison.map((m, i) => {
            const barPercent = maxMarketPrice > 0 ? (m.price / maxMarketPrice) * 100 : 0;
            const isBest = m.price === maxMarketPrice;
            return (
              <div key={i} className="flex items-center gap-2">
                <span className="text-xs text-gray-500 dark:text-gray-400 w-16 shrink-0 text-left">
                  {m.market}
                </span>
                <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full',
                      isBest ? 'bg-amber-400' : 'bg-gray-300 dark:bg-gray-600'
                    )}
                    style={{ width: `${barPercent}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300 w-14 text-right shrink-0">
                  {m.price.toFixed(2)}
                  {isBest && <Award className="inline w-3 h-3 text-amber-500 mr-0.5 mb-0.5" />}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Best sell recommendation */}
      <div className="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-3 border border-amber-100 dark:border-amber-800">
        <p className="text-xs font-semibold text-amber-800 dark:text-amber-300 mb-1 flex items-center gap-1">
          <Star className="w-3.5 h-3.5" />
          توصية البيع الأمثل
        </p>
        <p className="text-xs text-amber-700 dark:text-amber-400">{crop.bestSellRecommendation}</p>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Page Component
// ─────────────────────────────────────────────

export default function MarketPricesPage() {
  const [marketFilter, setMarketFilter] = useState('الكل');
  const [categoryFilter, setCategoryFilter] = useState('الكل');
  const [trendFilter, setTrendFilter] = useState('الكل');
  const [selectedCrop, setSelectedCrop] = useState<MarketPrice | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const filteredPrices = useMemo(() => {
    const trendLabelMap: Record<string, Trend | 'الكل'> = {
      الكل: 'الكل',
      صاعد: 'up',
      هابط: 'down',
      مستقر: 'stable',
    };
    return MOCK_PRICES.filter((p) => {
      if (marketFilter !== 'الكل' && p.market !== marketFilter) return false;
      if (categoryFilter !== 'الكل' && p.category !== categoryFilter) return false;
      if (trendFilter !== 'الكل' && p.trend !== trendLabelMap[trendFilter]) return false;
      return true;
    });
  }, [marketFilter, categoryFilter, trendFilter]);

  const stats = useMemo(() => {
    const tracked = MOCK_PRICES.length;
    const markets = new Set(MOCK_PRICES.map((p) => p.market)).size;
    const alerts = MOCK_PRICES.filter((p) => Math.abs(p.changePercent) >= 5).length;
    const avgChange = MOCK_PRICES.reduce((sum, p) => sum + p.changePercent, 0) / MOCK_PRICES.length;
    return { tracked, markets, alerts, avgChange };
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1200);
  };

  const handleSelectCrop = (crop: MarketPrice) => {
    setSelectedCrop((prev) => (prev?.id === crop.id ? null : crop));
  };

  return (
    <div dir="rtl" className="p-6 min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* ── Header ── */}
      <Header
        title="أسعار السوق"
        subtitle="تتبع وتحليل أسعار المحاصيل والمنتجات الزراعية في الأسواق المحلية والإقليمية"
      />

      {/* ── Stats Row ── */}
      <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="المحاصيل المرصودة"
          value={stats.tracked}
          icon={ShoppingBasket}
          iconColor="text-sahool-600"
          suffix="محصول"
        />
        <StatCard
          title="الأسواق المراقبة"
          value={stats.markets}
          icon={Store}
          iconColor="text-blue-600"
          suffix="سوق"
        />
        <StatCard
          title="تنبيهات الأسعار النشطة"
          value={stats.alerts}
          icon={Bell}
          iconColor="text-red-500"
          trend={{ value: 2, isPositive: false }}
        />
        <StatCard
          title="متوسط التغير السعري"
          value={`${stats.avgChange > 0 ? '+' : ''}${stats.avgChange.toFixed(1)}`}
          icon={BarChart2}
          iconColor={stats.avgChange >= 0 ? 'text-green-600' : 'text-red-600'}
          suffix="%"
        />
      </div>

      {/* ── Filters ── */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 shrink-0">
            <Filter className="w-4 h-4" />
            <span>تصفية:</span>
          </div>

          {/* Market filter */}
          <select
            value={marketFilter}
            onChange={(e) => setMarketFilter(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            {MARKETS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>

          {/* Category filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          {/* Trend filter */}
          <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            {TRENDS.map((t) => (
              <button
                key={t}
                onClick={() => setTrendFilter(t)}
                className={cn(
                  'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
                  trendFilter === t
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                )}
              >
                {t === 'صاعد' && <TrendingUp className="inline w-3.5 h-3.5 ml-1 text-green-500" />}
                {t === 'هابط' && <TrendingDown className="inline w-3.5 h-3.5 ml-1 text-red-500" />}
                {t === 'مستقر' && <Minus className="inline w-3.5 h-3.5 ml-1 text-gray-400" />}
                {t}
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 mr-auto">
            <button
              onClick={handleRefresh}
              className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              title="تحديث"
            >
              <RefreshCw
                className={cn(
                  'w-4 h-4 text-gray-500 dark:text-gray-400',
                  isRefreshing && 'animate-spin'
                )}
              />
            </button>
            <button
              disabled
              className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              title="تصدير (قريبًا)"
            >
              <Download className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </button>
          </div>
        </div>

        {/* Active filter chips */}
        {(marketFilter !== 'الكل' || categoryFilter !== 'الكل' || trendFilter !== 'الكل') && (
          <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
            <span className="text-xs text-gray-400 dark:text-gray-500">مرشّح بـ:</span>
            {marketFilter !== 'الكل' && (
              <span className="flex items-center gap-1 px-2 py-1 bg-sahool-50 dark:bg-sahool-900/30 text-sahool-700 dark:text-sahool-300 text-xs rounded-full">
                {marketFilter}
                <button onClick={() => setMarketFilter('الكل')}>
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {categoryFilter !== 'الكل' && (
              <span className="flex items-center gap-1 px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                {categoryFilter}
                <button onClick={() => setCategoryFilter('الكل')}>
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {trendFilter !== 'الكل' && (
              <span className="flex items-center gap-1 px-2 py-1 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                {trendFilter}
                <button onClick={() => setTrendFilter('الكل')}>
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            <span className="text-xs text-gray-400 dark:text-gray-500">
              — {filteredPrices.length} نتيجة
            </span>
          </div>
        )}
      </div>

      {/* ── Main content: grid + detail panel ── */}
      <div className="mt-6 flex gap-6">
        {/* Price cards grid */}
        <div className="flex-1 min-w-0">
          {filteredPrices.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-12 text-center">
              <ShoppingBasket className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400">
                لا توجد نتائج تطابق التصفية المحددة
              </p>
              <button
                onClick={() => {
                  setMarketFilter('الكل');
                  setCategoryFilter('الكل');
                  setTrendFilter('الكل');
                }}
                className="mt-3 text-sm text-sahool-600 dark:text-sahool-400 hover:underline"
              >
                إعادة تعيين الفلاتر
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredPrices.map((crop) => (
                <PriceCard
                  key={crop.id}
                  crop={crop}
                  isSelected={selectedCrop?.id === crop.id}
                  onClick={() => handleSelectCrop(crop)}
                />
              ))}
            </div>
          )}

          {/* Summary footer */}
          {filteredPrices.length > 0 && (
            <div className="mt-4 flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
              <span>
                عرض {filteredPrices.length} من {MOCK_PRICES.length} محصول
              </span>
              <span className="flex items-center gap-1">
                <Activity className="w-3.5 h-3.5" />
                آخر تحديث: اليوم 14:32
              </span>
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selectedCrop ? (
          <div className="w-80 shrink-0 hidden lg:block">
            <DetailPanel crop={selectedCrop} onClose={() => setSelectedCrop(null)} />
          </div>
        ) : (
          <div className="w-80 shrink-0 hidden lg:flex items-center justify-center">
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-dashed border-gray-200 dark:border-gray-700 p-8 text-center w-full">
              <ChevronRight className="w-8 h-8 text-gray-300 dark:text-gray-600 mx-auto mb-2 rotate-180" />
              <p className="text-sm text-gray-400 dark:text-gray-500">اختر محصولاً لعرض التفاصيل</p>
            </div>
          </div>
        )}
      </div>

      {/* Mobile detail panel (slide-up on selection) */}
      {selectedCrop && (
        <div className="mt-6 lg:hidden">
          <DetailPanel crop={selectedCrop} onClose={() => setSelectedCrop(null)} />
        </div>
      )}
    </div>
  );
}

'use client';

/**
 * SAHOOL Market Prices Client
 * أسعار السوق
 */

import React, { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Filter,
  BarChart3,
  DollarSign,
  Wheat,
  RefreshCw,
} from 'lucide-react';

interface CommodityPrice {
  id: string;
  crop: string;
  cropAr: string;
  variety: string;
  varietyAr: string;
  unit: string;
  unitAr: string;
  currentPrice: number;
  previousPrice: number;
  changePercent: number;
  trend: 'up' | 'down' | 'stable';
  market: string;
  marketAr: string;
  lastUpdated: string;
  weekHigh: number;
  weekLow: number;
}

const MOCK_PRICES: CommodityPrice[] = [
  { id: 'CP-001', crop: 'Wheat', cropAr: 'قمح', variety: 'Sakha 95', varietyAr: 'سخا 95', unit: 'ton', unitAr: 'طن', currentPrice: 1850, previousPrice: 1780, changePercent: 3.9, trend: 'up', market: 'Riyadh', marketAr: 'الرياض', lastUpdated: '2026-04-04', weekHigh: 1870, weekLow: 1750 },
  { id: 'CP-002', crop: 'Barley', cropAr: 'شعير', variety: 'Local', varietyAr: 'محلي', unit: 'ton', unitAr: 'طن', currentPrice: 1420, previousPrice: 1450, changePercent: -2.1, trend: 'down', market: 'Jeddah', marketAr: 'جدة', lastUpdated: '2026-04-04', weekHigh: 1460, weekLow: 1400 },
  { id: 'CP-003', crop: 'Dates (Sukkari)', cropAr: 'تمور سكري', variety: 'Sukkari', varietyAr: 'سكري', unit: 'kg', unitAr: 'كجم', currentPrice: 45, previousPrice: 45, changePercent: 0.0, trend: 'stable', market: 'Al-Qassim', marketAr: 'القصيم', lastUpdated: '2026-04-04', weekHigh: 48, weekLow: 43 },
  { id: 'CP-004', crop: 'Tomato', cropAr: 'طماطم', variety: 'Cherry', varietyAr: 'شيري', unit: 'kg', unitAr: 'كجم', currentPrice: 8.5, previousPrice: 7.2, changePercent: 18.1, trend: 'up', market: 'Riyadh', marketAr: 'الرياض', lastUpdated: '2026-04-04', weekHigh: 9.0, weekLow: 7.0 },
  { id: 'CP-005', crop: 'Alfalfa', cropAr: 'برسيم', variety: 'Local', varietyAr: 'محلي', unit: 'bale', unitAr: 'ربطة', currentPrice: 32, previousPrice: 35, changePercent: -8.6, trend: 'down', market: 'Tabuk', marketAr: 'تبوك', lastUpdated: '2026-04-03', weekHigh: 36, weekLow: 31 },
  { id: 'CP-006', crop: 'Cucumber', cropAr: 'خيار', variety: 'Greenhouse', varietyAr: 'بيوت محمية', unit: 'kg', unitAr: 'كجم', currentPrice: 4.2, previousPrice: 3.8, changePercent: 10.5, trend: 'up', market: 'Jeddah', marketAr: 'جدة', lastUpdated: '2026-04-04', weekHigh: 4.5, weekLow: 3.5 },
  { id: 'CP-007', crop: 'Dates (Ajwa)', cropAr: 'تمور عجوة', variety: 'Ajwa', varietyAr: 'عجوة', unit: 'kg', unitAr: 'كجم', currentPrice: 120, previousPrice: 118, changePercent: 1.7, trend: 'up', market: 'Madinah', marketAr: 'المدينة', lastUpdated: '2026-04-04', weekHigh: 125, weekLow: 115 },
  { id: 'CP-008', crop: 'Onion', cropAr: 'بصل', variety: 'Red', varietyAr: 'أحمر', unit: 'kg', unitAr: 'كجم', currentPrice: 3.0, previousPrice: 3.5, changePercent: -14.3, trend: 'down', market: 'Riyadh', marketAr: 'الرياض', lastUpdated: '2026-04-03', weekHigh: 3.8, weekLow: 2.9 },
];

const trendIcons: Record<string, React.ReactNode> = {
  up: <TrendingUp className="w-4 h-4 text-green-600" />,
  down: <TrendingDown className="w-4 h-4 text-red-600" />,
  stable: <Minus className="w-4 h-4 text-gray-500" />,
};

const trendTextColors: Record<string, string> = {
  up: 'text-green-600',
  down: 'text-red-600',
  stable: 'text-gray-500',
};

export default function MarketPricesClient() {
  const [cropFilter, setCropFilter] = useState<string>('all');

  const uniqueCrops = Array.from(new Set(MOCK_PRICES.map(p => p.cropAr)));
  const filtered = cropFilter === 'all' ? MOCK_PRICES : MOCK_PRICES.filter(p => p.cropAr === cropFilter);

  const stats = {
    totalCrops: MOCK_PRICES.length,
    rising: MOCK_PRICES.filter(p => p.trend === 'up').length,
    falling: MOCK_PRICES.filter(p => p.trend === 'down').length,
    stable: MOCK_PRICES.filter(p => p.trend === 'stable').length,
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">أسعار السوق</h1>
            <p className="text-gray-600 mt-1">Market Prices</p>
          </div>
          <button className="flex items-center gap-2 px-5 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">
            <RefreshCw className="w-5 h-5" />
            <span>تحديث الأسعار</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Wheat className="w-5 h-5 text-amber-600" />
            <p className="text-sm text-gray-600">إجمالي المحاصيل</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.totalCrops}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">أسعار مرتفعة</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{stats.rising}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingDown className="w-5 h-5 text-red-600" />
            <p className="text-sm text-gray-600">أسعار منخفضة</p>
          </div>
          <p className="text-3xl font-bold text-red-600">{stats.falling}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-5 h-5 text-gray-600" />
            <p className="text-sm text-gray-600">أسعار مستقرة</p>
          </div>
          <p className="text-3xl font-bold text-gray-600">{stats.stable}</p>
        </div>
      </div>

      {/* Filter + Table */}
      <div className="bg-white rounded-xl border-2 border-gray-200">
        <div className="flex items-center gap-3 p-6 border-b border-gray-200">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-600">المحصول:</span>
          <button
            onClick={() => setCropFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${cropFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          >
            الكل
          </button>
          {uniqueCrops.map(crop => (
            <button
              key={crop}
              onClick={() => setCropFilter(crop)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${cropFilter === crop ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              {crop}
            </button>
          ))}
        </div>

        <div className="p-6 overflow-x-auto">
          <table className="w-full text-right">
            <thead>
              <tr className="border-b border-gray-200 text-sm text-gray-500">
                <th className="pb-3 pr-4 font-medium">المحصول</th>
                <th className="pb-3 pr-4 font-medium">الصنف</th>
                <th className="pb-3 pr-4 font-medium">السعر الحالي</th>
                <th className="pb-3 pr-4 font-medium">التغير</th>
                <th className="pb-3 pr-4 font-medium">الاتجاه</th>
                <th className="pb-3 pr-4 font-medium">أعلى / أدنى (أسبوع)</th>
                <th className="pb-3 pr-4 font-medium">السوق</th>
                <th className="pb-3 font-medium">آخر تحديث</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-4 pr-4">
                    <p className="font-semibold text-gray-900">{item.cropAr}</p>
                    <p className="text-xs text-gray-500">{item.crop}</p>
                  </td>
                  <td className="py-4 pr-4 text-sm text-gray-700">{item.varietyAr}</td>
                  <td className="py-4 pr-4">
                    <span className="font-bold text-gray-900">{item.currentPrice}</span>
                    <span className="text-xs text-gray-500 mr-1">ر.س/{item.unitAr}</span>
                  </td>
                  <td className="py-4 pr-4">
                    <span className={`text-sm font-medium ${trendTextColors[item.trend]}`}>
                      {item.changePercent > 0 ? '+' : ''}{item.changePercent}%
                    </span>
                  </td>
                  <td className="py-4 pr-4">{trendIcons[item.trend]}</td>
                  <td className="py-4 pr-4 text-sm text-gray-700">
                    {item.weekHigh} / {item.weekLow}
                  </td>
                  <td className="py-4 pr-4 text-sm text-gray-700">{item.marketAr}</td>
                  <td className="py-4 text-sm text-gray-500">{item.lastUpdated}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

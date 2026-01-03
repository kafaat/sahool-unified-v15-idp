'use client';

// Farms Management Page
// صفحة إدارة المزارع

import { useEffect, useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import Header from '@/components/layout/Header';
import StatusBadge from '@/components/ui/StatusBadge';
import DataTable from '@/components/ui/DataTable';
import { fetchFarms } from '@/lib/api';
import { formatDate, formatArea, getHealthScoreColor, cn } from '@/lib/utils';
import type { Farm } from '@/types';
import type { BaseFarmData } from '@/components/maps/FarmsMap';
import { YEMEN_GOVERNORATES } from '@/types';
import {
  MapPin,
  Search,
  Filter,
  List,
  Map as MapIcon,
  Plus,
  RefreshCw,
  Download,
  Eye,
} from 'lucide-react';
import Link from 'next/link';
import { logger } from '../../lib/logger';

// Dynamic import for map (no SSR)
const FarmsMap = dynamic(() => import('@/components/maps/FarmsMap'), {
  ssr: false,
  loading: () => (
    <div className="h-[600px] bg-gray-100 animate-pulse rounded-xl flex items-center justify-center">
      <p className="text-gray-500">جاري تحميل الخريطة...</p>
    </div>
  ),
});

type ViewMode = 'map' | 'table';

export default function FarmsPage() {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('map');
  const [selectedFarm, setSelectedFarm] = useState<Farm | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [governorateFilter, setGovernorateFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadFarms();
  }, []);

  async function loadFarms() {
    setIsLoading(true);
    try {
      const data = await fetchFarms();
      setFarms(data);
    } catch (error) {
      logger.error('Failed to load farms:', error);
    } finally {
      setIsLoading(false);
    }
  }

  // Filter farms
  const filteredFarms = useMemo(() => {
    return farms.filter((f) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !(f.nameAr || '').toLowerCase().includes(query) &&
          !f.name.toLowerCase().includes(query) &&
          !f.governorate.toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (governorateFilter && f.governorate !== governorateFilter) return false;
      if (statusFilter && f.status !== statusFilter) return false;
      return true;
    });
  }, [farms, searchQuery, governorateFilter, statusFilter]);

  // Stats by governorate
  const governorateStats = useMemo(() => {
    const stats: Record<string, { count: number; area: number; avgHealth: number }> = {};
    farms.forEach((f) => {
      if (!stats[f.governorate]) {
        stats[f.governorate] = { count: 0, area: 0, avgHealth: 0 };
      }
      stats[f.governorate].count++;
      stats[f.governorate].area += f.area;
      stats[f.governorate].avgHealth += f.healthScore;
    });
    Object.keys(stats).forEach((key) => {
      stats[key].avgHealth = stats[key].avgHealth / stats[key].count;
    });
    return stats;
  }, [farms]);

  const handleFarmClick = (farm: BaseFarmData) => {
    setSelectedFarm(farm as Farm);
  };

  // Table columns
  const columns = [
    {
      key: 'nameAr',
      header: 'اسم المزرعة',
      render: (farm: Farm) => (
        <div>
          <p className="font-medium text-gray-900">{farm.nameAr}</p>
          <p className="text-xs text-gray-500">{farm.name}</p>
        </div>
      ),
    },
    {
      key: 'governorate',
      header: 'المحافظة',
      render: (farm: Farm) => (
        <span className="text-gray-700">{farm.governorate}</span>
      ),
    },
    {
      key: 'area',
      header: 'المساحة',
      render: (farm: Farm) => (
        <span className="text-gray-700">{formatArea(farm.area)}</span>
      ),
    },
    {
      key: 'crops',
      header: 'المحاصيل',
      render: (farm: Farm) => (
        <span className="text-gray-700">{farm.crops.join(', ')}</span>
      ),
    },
    {
      key: 'healthScore',
      header: 'الصحة',
      render: (farm: Farm) => (
        <span className={cn('px-2 py-1 rounded font-bold text-sm', getHealthScoreColor(farm.healthScore))}>
          {farm.healthScore}%
        </span>
      ),
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (farm: Farm) => <StatusBadge status={farm.status} />,
    },
    {
      key: 'actions',
      header: '',
      render: (farm: Farm) => (
        <Link
          href={`/farms/${farm.id}`}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors inline-flex"
        >
          <Eye className="w-4 h-4 text-gray-500" />
        </Link>
      ),
      className: 'w-12',
    },
  ];

  return (
    <div className="p-6">
      <Header
        title="إدارة المزارع"
        subtitle={`${farms.length} مزرعة مسجلة`}
      />

      {/* Stats by Governorate */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {Object.entries(governorateStats).slice(0, 6).map(([gov, stats]) => (
          <div
            key={gov}
            className={cn(
              'bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all',
              governorateFilter === gov && 'ring-2 ring-sahool-500 border-sahool-500'
            )}
            onClick={() => setGovernorateFilter(governorateFilter === gov ? '' : gov)}
          >
            <p className="text-xl font-bold text-gray-900">{stats.count}</p>
            <p className="text-sm text-gray-500 truncate">{gov}</p>
            <p className="text-xs text-gray-400 mt-1">{stats.area.toFixed(0)} هكتار</p>
          </div>
        ))}
      </div>

      {/* Filters and View Toggle */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالاسم أو المحافظة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          {/* Governorate Filter */}
          <select
            value={governorateFilter}
            onChange={(e) => setGovernorateFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل المحافظات</option>
            {YEMEN_GOVERNORATES.map((gov) => (
              <option key={gov.id} value={gov.nameAr}>
                {gov.nameAr}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="active">نشط</option>
            <option value="inactive">غير نشط</option>
            <option value="pending">معلق</option>
          </select>

          {/* View Toggle */}
          <div className="flex border border-gray-200 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('map')}
              className={cn(
                'p-2 transition-colors',
                viewMode === 'map' ? 'bg-sahool-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
              )}
            >
              <MapIcon className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={cn(
                'p-2 transition-colors',
                viewMode === 'table' ? 'bg-sahool-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
              )}
            >
              <List className="w-5 h-5" />
            </button>
          </div>

          {/* Actions */}
          <button
            onClick={loadFarms}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className={cn('w-5 h-5 text-gray-600', isLoading && 'animate-spin')} />
          </button>
          <button className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-5 h-5 text-gray-600" />
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors">
            <Plus className="w-5 h-5" />
            إضافة مزرعة
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="mt-6">
        {isLoading ? (
          <div className="h-[600px] bg-gray-200 animate-pulse rounded-xl"></div>
        ) : viewMode === 'map' ? (
          <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
            <FarmsMap
              farms={filteredFarms}
              onFarmClick={handleFarmClick}
              selectedFarmId={selectedFarm?.id}
              showHealthOverlay={true}
              className="h-[600px]"
            />
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredFarms}
            keyExtractor={(farm) => farm.id}
            onRowClick={handleFarmClick}
            emptyMessage="لا توجد مزارع مطابقة للبحث"
          />
        )}
      </div>

      {/* Selected Farm Panel */}
      {selectedFarm && viewMode === 'map' && (
        <div className="fixed bottom-6 left-6 right-6 mr-64 bg-white rounded-xl shadow-2xl border border-gray-100 p-6 animate-slide-up z-40">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-xl font-bold text-gray-900">{selectedFarm.nameAr}</h3>
              <p className="text-gray-500">{selectedFarm.governorate} • {selectedFarm.district}</p>
            </div>
            <button
              onClick={() => setSelectedFarm(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">المساحة</p>
              <p className="font-bold">{formatArea(selectedFarm.area)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">المحاصيل</p>
              <p className="font-medium">{selectedFarm.crops.join(', ')}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">مستوى الصحة</p>
              <span className={cn('px-2 py-1 rounded font-bold', getHealthScoreColor(selectedFarm.healthScore))}>
                {selectedFarm.healthScore}%
              </span>
            </div>
            <div>
              <p className="text-sm text-gray-500">آخر تحديث</p>
              <p className="font-medium">{formatDate(selectedFarm.lastUpdated)}</p>
            </div>
          </div>
          <div className="mt-4 flex gap-3">
            <Link
              href={`/farms/${selectedFarm.id}`}
              className="px-4 py-2 bg-sahool-600 text-white rounded-lg text-sm font-medium hover:bg-sahool-700 transition-colors"
            >
              عرض التفاصيل
            </Link>
            <Link
              href={`/diseases?farmId=${selectedFarm.id}`}
              className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              التشخيصات
            </Link>
            <Link
              href={`/sensors?farmId=${selectedFarm.id}`}
              className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              المستشعرات
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

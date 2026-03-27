'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Satellite,
  MapPin,
  TrendingUp,
  AlertTriangle,
  Droplets,
  Plus,
  ChevronDown,
  CloudSun,
  Thermometer,
  Wind,
  CloudRain,
  SprayCan,
  Layers,
  Mountain,
  Radio,
  Leaf,
  FlaskConical,
  Radar,
  Calendar,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Eye,
  Search,
  RefreshCw,
  Download,
  Wifi,
  WifiOff,
  Bot,
} from 'lucide-react';
import {
  useFarmonautFields,
  useFarmonautStats,
  useFarmonautAlerts,
  useFarmonautTimeSeries,
  useFarmonautWeather,
  useFarmonautDirectionGrid,
} from '@/features/farmonaut';
import { MAP_LAYERS, HYBRID_COLORS } from '@/features/farmonaut/api';
import type { FarmonautField, MapLayerType, CropHealthStatus, TimePeriod } from '@/features/farmonaut';

// ---------------------------------------------------------------------------
// Health status helpers
// ---------------------------------------------------------------------------
const HEALTH_CONFIG: Record<CropHealthStatus, { color: string; bg: string; label: string; labelAr: string }> = {
  healthy: { color: 'text-green-700', bg: 'bg-green-100', label: 'Healthy', labelAr: 'صحي' },
  moderate: { color: 'text-yellow-700', bg: 'bg-yellow-100', label: 'Moderate', labelAr: 'متوسط' },
  stressed: { color: 'text-orange-700', bg: 'bg-orange-100', label: 'Stressed', labelAr: 'مجهد' },
  critical: { color: 'text-red-700', bg: 'bg-red-100', label: 'Critical', labelAr: 'حرج' },
};

const SEVERITY_CONFIG: Record<string, { color: string; bg: string; border: string }> = {
  critical: { color: 'text-red-700', bg: 'bg-red-50', border: 'border-red-200' },
  warning: { color: 'text-orange-700', bg: 'bg-orange-50', border: 'border-orange-200' },
  advisory: { color: 'text-yellow-700', bg: 'bg-yellow-50', border: 'border-yellow-200' },
  info: { color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-200' },
};

const WEATHER_ICONS: Record<string, string> = {
  sunny: '☀️',
  partly_cloudy: '⛅',
  cloudy: '☁️',
  rainy: '🌧️',
  stormy: '⛈️',
  windy: '💨',
};

// Layer groups for the map control panel (matching Farmonaut UI)
const LAYER_GROUPS = [
  { key: 'Basic Analysis', keyAr: 'التحليل الأساسي', icon: Eye, types: ['hybrid', 'colorblind'] },
  { key: 'Satellite Image', keyAr: 'صورة القمر الصناعي', icon: Satellite, types: ['tci', 'etci'] },
  { key: 'Crop Health (Early)', keyAr: 'صحة المحصول (مبكر)', icon: Leaf, types: ['ndvi', 'evi', 'savi'] },
  { key: 'Crop Health (Late)', keyAr: 'صحة المحصول (متأخر)', icon: Leaf, types: ['ndre'] },
  { key: 'Irrigation', keyAr: 'الري', icon: Droplets, types: ['ndwi', 'evapotranspiration', 'ndmi'] },
  { key: 'Soil Health', keyAr: 'صحة التربة', icon: FlaskConical, types: ['soc'] },
  { key: 'Advanced Analysis', keyAr: 'تحليل متقدم', icon: BarChart3, types: ['erosion'] },
  { key: 'Topography', keyAr: 'التضاريس', icon: Mountain, types: ['dem'] },
  { key: 'Radar (SAR)', keyAr: 'الرادار', icon: Radio, types: ['sar_rvi', 'sar_rsm'] },
];

export default function FarmonautClient() {
  const [selectedLayer, setSelectedLayer] = useState<MapLayerType>('hybrid');
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [timeSeriesPeriod, setTimeSeriesPeriod] = useState<TimePeriod>('90d');
  const [searchQuery, setSearchQuery] = useState('');

  // Data hooks
  const { data: fields = [], isLoading, error } = useFarmonautFields();
  const { data: stats } = useFarmonautStats();
  const { data: alerts = [] } = useFarmonautAlerts();
  const selectedField = selectedFieldId || (fields.length > 0 ? fields[0].id : '');
  const { data: timeSeries = [] } = useFarmonautTimeSeries(selectedField, timeSeriesPeriod);
  const { data: weather = [] } = useFarmonautWeather(selectedField);
  const { data: directionGrid } = useFarmonautDirectionGrid(selectedField, selectedLayer);

  const activeLayer = MAP_LAYERS.find((l) => l.type === selectedLayer) ?? MAP_LAYERS[0];

  const unresolvedAlerts = useMemo(() => alerts.filter((a) => !a.isResolved), [alerts]);

  // Search-filtered fields
  const filteredFields = useMemo(() => {
    if (!searchQuery.trim()) return fields;
    const q = searchQuery.toLowerCase();
    return fields.filter(
      (f) =>
        f.name.toLowerCase().includes(q) ||
        f.nameAr.includes(q) ||
        f.cropType.toLowerCase().includes(q) ||
        f.cropTypeAr.includes(q)
    );
  }, [fields, searchQuery]);

  // Health distribution for summary
  const healthDistribution = useMemo(() => {
    const dist = { healthy: 0, moderate: 0, stressed: 0, critical: 0 };
    fields.forEach((f) => { dist[f.healthStatus]++; });
    return dist;
  }, [fields]);

  // Loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600" />
      </div>
    );
  }

  // Error
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل بيانات المراقبة</p>
          <p className="text-gray-500 text-sm">Failed to load monitoring data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ================================================================= */}
      {/* A. Header + Farm Selector */}
      {/* ================================================================= */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">مراقبة الأقمار الصناعية</h1>
          <p className="text-gray-500 mt-1">Farmonaut Satellite Monitoring</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedFieldId ?? ''}
            onChange={(e) => setSelectedFieldId(e.target.value || null)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
          >
            <option value="">جميع المزارع | All Farms</option>
            {fields.map((f) => (
              <option key={f.id} value={f.id}>
                {f.nameAr} ({f.cropTypeAr})
              </option>
            ))}
          </select>
          <Link
            href="/farmonaut/add-field"
            className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
          >
            <Plus className="w-4 h-4" />
            <span>إضافة حقل</span>
          </Link>
        </div>
      </div>

      {/* ================================================================= */}
      {/* B. Stats Cards (4 KPIs) */}
      {/* ================================================================= */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Satellite className="w-5 h-5 text-blue-600" />}
          iconBg="bg-blue-100"
          label="آخر مرور للقمر"
          labelEn="Last Satellite Pass"
          value={stats?.lastSatellitePass ? new Date(stats.lastSatellitePass).toLocaleDateString('ar-SA') : '-'}
          sub={`القادم: ${stats?.nextSatellitePass ? new Date(stats.nextSatellitePass).toLocaleDateString('ar-SA') : '-'}`}
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5 text-green-600" />}
          iconBg="bg-green-100"
          label="متوسط NDVI"
          labelEn="Average NDVI"
          value={stats?.averageNdvi?.toFixed(2) ?? '0.00'}
          sub={
            stats?.ndviTrend === 'up'
              ? '↑ اتجاه تصاعدي'
              : stats?.ndviTrend === 'down'
                ? '↓ اتجاه هبوطي'
                : '→ مستقر'
          }
          valueColor={
            stats?.ndviTrend === 'up' ? 'text-green-600' : stats?.ndviTrend === 'down' ? 'text-red-600' : 'text-gray-900'
          }
        />
        <StatCard
          icon={<AlertTriangle className="w-5 h-5 text-orange-600" />}
          iconBg="bg-orange-100"
          label="تنبيهات نشطة"
          labelEn="Active Alerts"
          value={String(stats?.activeAlerts ?? unresolvedAlerts.length)}
          valueColor={
            (stats?.activeAlerts ?? 0) > 0 ? 'text-orange-600' : 'text-green-600'
          }
          sub={`${stats?.waterStressFields ?? 0} حقول إجهاد مائي`}
        />
        <StatCard
          icon={<Layers className="w-5 h-5 text-purple-600" />}
          iconBg="bg-purple-100"
          label="المساحة المراقبة"
          labelEn="Monitored Area"
          value={`${stats?.totalArea?.toFixed(1) ?? '0'} هـ`}
          sub={`${stats?.totalFields ?? fields.length} حقول`}
        />
      </div>

      {/* ================================================================= */}
      {/* B2. Health Distribution + JEEVN AI Quick Insights */}
      {/* ================================================================= */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Health Distribution */}
        <div className="bg-white rounded-lg border p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">توزيع صحة الحقول | Health Distribution</h3>
          <div className="flex gap-1 h-4 rounded-full overflow-hidden bg-gray-100">
            {fields.length > 0 && (
              <>
                {healthDistribution.healthy > 0 && (
                  <div className="bg-green-500 transition-all" style={{ width: `${(healthDistribution.healthy / fields.length) * 100}%` }} title={`صحي: ${healthDistribution.healthy}`} />
                )}
                {healthDistribution.moderate > 0 && (
                  <div className="bg-yellow-500 transition-all" style={{ width: `${(healthDistribution.moderate / fields.length) * 100}%` }} title={`متوسط: ${healthDistribution.moderate}`} />
                )}
                {healthDistribution.stressed > 0 && (
                  <div className="bg-orange-500 transition-all" style={{ width: `${(healthDistribution.stressed / fields.length) * 100}%` }} title={`مجهد: ${healthDistribution.stressed}`} />
                )}
                {healthDistribution.critical > 0 && (
                  <div className="bg-red-500 transition-all" style={{ width: `${(healthDistribution.critical / fields.length) * 100}%` }} title={`حرج: ${healthDistribution.critical}`} />
                )}
              </>
            )}
          </div>
          <div className="flex justify-between mt-2 text-xs">
            <span className="text-green-600">صحي: {healthDistribution.healthy}</span>
            <span className="text-yellow-600">متوسط: {healthDistribution.moderate}</span>
            <span className="text-orange-600">مجهد: {healthDistribution.stressed}</span>
            <span className="text-red-600">حرج: {healthDistribution.critical}</span>
          </div>
        </div>

        {/* JEEVN AI Quick Insights */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <Bot className="w-5 h-5 text-indigo-600" />
            <h3 className="text-sm font-semibold text-indigo-900">JEEVN AI - رؤى سريعة</h3>
          </div>
          <div className="space-y-2 text-sm">
            {healthDistribution.critical > 0 && (
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                <span className="text-gray-700">
                  <strong className="text-red-600">{healthDistribution.critical} حقل حرج</strong> - يحتاج تدخل فوري (ري / تسميد)
                </span>
              </div>
            )}
            {unresolvedAlerts.filter((a) => a.type === 'water_stress').length > 0 && (
              <div className="flex items-start gap-2">
                <Droplets className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                <span className="text-gray-700">
                  {unresolvedAlerts.filter((a) => a.type === 'water_stress').length} تنبيه إجهاد مائي - يُوصى بزيادة الري
                </span>
              </div>
            )}
            {unresolvedAlerts.filter((a) => a.type === 'pest' || a.type === 'disease').length > 0 && (
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 shrink-0" />
                <span className="text-gray-700">
                  {unresolvedAlerts.filter((a) => a.type === 'pest' || a.type === 'disease').length} خطر آفات/أمراض - استكشف الحقول المتأثرة
                </span>
              </div>
            )}
            {healthDistribution.critical === 0 && unresolvedAlerts.length === 0 && (
              <div className="flex items-start gap-2">
                <TrendingUp className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                <span className="text-gray-700">جميع الحقول في حالة جيدة. استمر في المراقبة الدورية.</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ================================================================= */}
      {/* C. Map Control Panel + Satellite Map */}
      {/* ================================================================= */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Map Control Panel */}
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="p-3 border-b bg-gray-50">
            <h2 className="font-semibold text-gray-900 text-sm">التحكم في الخريطة</h2>
            <p className="text-xs text-gray-500">Map Control</p>
          </div>
          <div className="p-2 space-y-3 max-h-[520px] overflow-y-auto">
            {LAYER_GROUPS.map((group) => {
              const GroupIcon = group.icon;
              return (
                <div key={group.key}>
                  <div className="flex items-center gap-2 px-2 py-1">
                    <GroupIcon className="w-3.5 h-3.5 text-gray-500" />
                    <span className="text-xs font-medium text-gray-600">{group.keyAr}</span>
                  </div>
                  {group.types.map((type) => {
                    const layer = MAP_LAYERS.find((l) => l.type === type);
                    if (!layer) return null;
                    const isActive = selectedLayer === type;
                    return (
                      <button
                        key={type}
                        onClick={() => setSelectedLayer(type as MapLayerType)}
                        className={`w-full text-right px-3 py-2 rounded-md text-sm transition-colors ${
                          isActive
                            ? 'bg-green-50 text-green-700 font-medium border border-green-200'
                            : 'hover:bg-gray-50 text-gray-700'
                        }`}
                      >
                        <div className="font-medium text-xs">{layer.labelAr}</div>
                        <div className="text-[10px] text-gray-400">{layer.label}</div>
                      </button>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </div>

        {/* Satellite Map */}
        <div className="lg:col-span-3 bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-gray-900">{activeLayer.labelAr}</h2>
              <p className="text-xs text-gray-500">{activeLayer.descriptionAr}</p>
            </div>
            {selectedLayer === 'sar_rvi' || selectedLayer === 'sar_rsm' ? (
              <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full font-medium">
                يعمل عبر السحب | Works through clouds
              </span>
            ) : null}
          </div>

          {/* Map Placeholder */}
          <div className="aspect-[16/9] bg-gradient-to-br from-green-100 via-green-200 to-green-300 flex items-center justify-center relative">
            {/* Simulated field boundaries */}
            {fields.map((field, idx) => (
              <div
                key={field.id}
                className={`absolute w-16 h-12 rounded border-2 flex items-center justify-center text-[10px] font-bold cursor-pointer transition-all ${
                  selectedFieldId === field.id ? 'ring-2 ring-blue-500 scale-110' : ''
                }`}
                style={{
                  top: `${20 + idx * 15}%`,
                  left: `${15 + idx * 18}%`,
                  backgroundColor: getFieldMapColor(field, selectedLayer),
                  borderColor: getFieldMapBorderColor(field.healthStatus),
                }}
                onClick={() => setSelectedFieldId(field.id)}
                title={field.nameAr}
              >
                {field.ndvi.toFixed(2)}
              </div>
            ))}
            <div className="text-center z-10">
              <Radar className="w-16 h-16 text-green-700 mx-auto mb-2 opacity-30" />
              <p className="text-green-800 font-medium text-sm">خريطة تفاعلية - {activeLayer.labelAr}</p>
              <p className="text-green-700 text-xs">Sentinel-2 / Landsat-8 / SAR</p>
            </div>
          </div>

          {/* Color Legend */}
          <div className="p-3 border-t">
            {selectedLayer === 'hybrid' ? (
              <div className="flex flex-wrap gap-3">
                {HYBRID_COLORS.map((hc) => (
                  <div key={hc.color} className="flex items-center gap-1.5">
                    <div className="w-4 h-4 rounded-full border" style={{ backgroundColor: hc.hex }} />
                    <span className="text-xs text-gray-600">{hc.meaningAr}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-3">
                {activeLayer.colorStops.map((stop) => (
                  <div key={stop.value} className="flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: stop.color }} />
                    <span className="text-xs text-gray-600">{stop.labelAr}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ================================================================= */}
      {/* D. 9-Direction Grid Analysis */}
      {/* ================================================================= */}
      {directionGrid && (
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-gray-900">تحليل الاتجاهات التسعة</h2>
              <p className="text-xs text-gray-500">9-Direction Grid Analysis - {activeLayer.label}</p>
            </div>
            <span className="text-xs text-gray-400">{directionGrid.analysisDate}</span>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-3 gap-2 max-w-md mx-auto">
              {(['NW', 'N', 'NE', 'W', 'C', 'E', 'SW', 'S', 'SE'] as const).map((zone) => {
                const zoneData = directionGrid.zones.find((z) => z.zone === zone);
                if (!zoneData) return <div key={zone} className="p-3 bg-gray-50 rounded" />;
                const health = HEALTH_CONFIG[zoneData.healthStatus];
                return (
                  <div
                    key={zone}
                    className={`p-3 rounded-lg border ${health.bg} ${zone === 'C' ? 'ring-2 ring-green-300' : ''}`}
                    title={zoneData.recommendationAr}
                  >
                    <div className="text-center">
                      <div className="text-[10px] text-gray-500 font-medium">{zoneData.labelAr}</div>
                      <div className={`text-lg font-bold ${health.color}`}>{zoneData.ndvi.toFixed(2)}</div>
                      <div className={`text-[10px] font-medium ${health.color}`}>{health.labelAr}</div>
                      {zoneData.irrigationNeeded && (
                        <Droplets className="w-3 h-3 text-blue-500 mx-auto mt-1" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-center text-xs text-gray-400 mt-3">
              اضغط على المنطقة لعرض التوصيات | Click a zone for recommendations
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ================================================================= */}
        {/* E. NDVI Time Series Chart */}
        {/* ================================================================= */}
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">المسار الزمني للمؤشرات</h2>
            <select
              value={timeSeriesPeriod}
              onChange={(e) => setTimeSeriesPeriod(e.target.value as TimePeriod)}
              className="px-3 py-1 border rounded text-sm"
            >
              <option value="7d">7 أيام</option>
              <option value="30d">30 يوم</option>
              <option value="90d">3 أشهر</option>
              <option value="6m">6 أشهر</option>
              <option value="1y">سنة</option>
            </select>
          </div>
          <div className="p-4">
            {timeSeries.length > 0 ? (
              <div className="space-y-2">
                {/* Simple bar chart visualization */}
                <div className="flex items-end gap-1 h-40">
                  {timeSeries.map((point, idx) => {
                    const height = Math.max(point.ndvi * 100, 5);
                    const color = point.ndvi >= 0.6 ? 'bg-green-500' : point.ndvi >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';
                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                        <span className="text-[9px] text-gray-500">{point.ndvi.toFixed(2)}</span>
                        <div
                          className={`w-full rounded-t ${color} transition-all`}
                          style={{ height: `${height}%` }}
                          title={`${point.date}: NDVI ${point.ndvi.toFixed(2)}`}
                        />
                        <span className="text-[8px] text-gray-400 rotate-[-45deg] origin-top-left">
                          {point.date.slice(5)}
                        </span>
                      </div>
                    );
                  })}
                </div>
                <div className="flex justify-between text-xs text-gray-400 pt-4">
                  <span>{timeSeries[0]?.date}</span>
                  <span>{timeSeries[timeSeries.length - 1]?.date}</span>
                </div>
              </div>
            ) : (
              <div className="h-40 flex items-center justify-center text-gray-400 text-sm">
                لا توجد بيانات تاريخية
              </div>
            )}
          </div>
        </div>

        {/* ================================================================= */}
        {/* G. Weather Forecast */}
        {/* ================================================================= */}
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">توقعات الطقس - 7 أيام</h2>
            <p className="text-xs text-gray-500">Weather Forecast with Spray Windows</p>
          </div>
          <div className="divide-y">
            {weather.map((day) => (
              <div key={day.date} className="p-3 flex items-center justify-between hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{WEATHER_ICONS[day.condition] ?? '🌤️'}</span>
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {new Date(day.date).toLocaleDateString('ar-SA', { weekday: 'short', month: 'short', day: 'numeric' })}
                    </div>
                    <div className="text-xs text-gray-500">{day.conditionAr}</div>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <div className="flex items-center gap-1">
                    <Thermometer className="w-3 h-3 text-red-500" />
                    <span>{day.tempMin}°-{day.tempMax}°</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Droplets className="w-3 h-3 text-blue-500" />
                    <span>{day.humidity}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Wind className="w-3 h-3 text-gray-500" />
                    <span>{day.windSpeed} كم/س</span>
                  </div>
                  {day.precipitation > 0 && (
                    <div className="flex items-center gap-1">
                      <CloudRain className="w-3 h-3 text-blue-600" />
                      <span>{day.precipitation} مم</span>
                    </div>
                  )}
                  {day.sprayWindow ? (
                    <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-[10px] font-medium flex items-center gap-1">
                      <SprayCan className="w-3 h-3" /> نافذة رش
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 bg-red-100 text-red-600 rounded-full text-[10px] font-medium">
                      لا رش
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ================================================================= */}
      {/* F. Alerts Panel */}
      {/* ================================================================= */}
      {unresolvedAlerts.length > 0 && (
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <h2 className="font-semibold text-gray-900">تنبيهات نشطة</h2>
            <span className="px-2 py-0.5 bg-orange-200 text-orange-800 text-xs font-medium rounded-full">
              {unresolvedAlerts.length}
            </span>
          </div>
          <div className="divide-y">
            {unresolvedAlerts.map((alert) => {
              const sev = SEVERITY_CONFIG[alert.severity] ?? SEVERITY_CONFIG.info;
              return (
                <div key={alert.id} className={`p-4 ${sev.bg}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${sev.color} ${sev.bg} border ${sev.border}`}>
                          {alert.severity === 'critical' ? 'حرج' : alert.severity === 'warning' ? 'تحذير' : 'استشارة'}
                        </span>
                        <span className="text-xs text-gray-400">{alert.typeAr}</span>
                      </div>
                      <h3 className="font-medium text-gray-900">{alert.titleAr}</h3>
                      <p className="text-sm text-gray-600 mt-1">{alert.descriptionAr}</p>
                      <div className="mt-2 p-2 bg-white/60 rounded text-sm">
                        <span className="font-medium text-gray-700">التوصية: </span>
                        {alert.recommendationAr}
                      </div>
                    </div>
                    <div className="text-left mr-4">
                      <span className="text-xs text-gray-400">{alert.fieldNameAr}</span>
                      <div className="text-[10px] text-gray-400 mt-1">
                        {new Date(alert.detectedAt).toLocaleDateString('ar-SA')}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ================================================================= */}
      {/* E. Field List (All Farms) */}
      {/* ================================================================= */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 className="font-semibold text-gray-900">جميع المزارع | Show All Farms</h2>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="بحث عن حقل..."
                className="pl-3 pr-9 py-1.5 border rounded-lg text-sm w-48 focus:ring-2 focus:ring-green-500 focus:outline-none"
              />
            </div>
            <span className="text-sm text-gray-500">{filteredFields.length} حقول | {stats?.totalArea?.toFixed(1) ?? '0'} هكتار</span>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">الحقل</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">المحصول</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">المرحلة</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">المساحة</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">NDVI</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">رطوبة التربة</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500">آخر صورة</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500">التفاصيل</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredFields.map((field) => {
                const health = HEALTH_CONFIG[field.healthStatus];
                return (
                  <tr
                    key={field.id}
                    className={`hover:bg-gray-50 cursor-pointer ${selectedFieldId === field.id ? 'bg-green-50' : ''}`}
                    onClick={() => setSelectedFieldId(field.id)}
                  >
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900 text-sm">{field.nameAr}</div>
                      <div className="text-xs text-gray-400">{field.name}</div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{field.cropTypeAr}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{field.growthStageAr}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{field.area} هـ</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <span className={`text-sm font-bold ${health.color}`}>{field.ndvi.toFixed(2)}</span>
                        {field.ndviChange > 0 ? (
                          <ArrowUpRight className="w-3 h-3 text-green-500" />
                        ) : field.ndviChange < 0 ? (
                          <ArrowDownRight className="w-3 h-3 text-red-500" />
                        ) : (
                          <Minus className="w-3 h-3 text-gray-400" />
                        )}
                        <span className={`text-xs ${field.ndviChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {field.ndviChange > 0 ? '+' : ''}{field.ndviChange.toFixed(2)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${field.soilMoisture > 40 ? 'bg-blue-500' : field.soilMoisture > 25 ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${field.soilMoisture}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">{field.soilMoisture}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${health.color} ${health.bg}`}>
                        {health.labelAr}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">{field.lastImageDate}</td>
                    <td className="px-4 py-3 text-center">
                      <Link
                        href={`/farmonaut/field/${field.id}`}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs text-green-700 bg-green-50 rounded hover:bg-green-100"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Eye className="w-3 h-3" />
                        عرض
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ================================================================= */}
      {/* H. Historical Data Link */}
      {/* ================================================================= */}
      <div className="bg-white rounded-lg border p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Calendar className="w-5 h-5 text-indigo-600" />
          <div>
            <h3 className="font-medium text-gray-900">البيانات التاريخية والفاصل الزمني</h3>
            <p className="text-xs text-gray-500">Historical data from 2017 - Side by side comparison & Timelapse</p>
          </div>
        </div>
        <Link
          href={selectedField ? `/farmonaut/field/${selectedField}` : '#'}
          className="px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 text-sm font-medium"
        >
          عرض البيانات التاريخية
        </Link>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helper Components
// ---------------------------------------------------------------------------

function StatCard({
  icon,
  iconBg,
  label,
  labelEn,
  value,
  sub,
  valueColor = 'text-gray-900',
}: {
  icon: React.ReactNode;
  iconBg: string;
  label: string;
  labelEn: string;
  value: string;
  sub?: string;
  valueColor?: string;
}) {
  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 ${iconBg} rounded-lg flex items-center justify-center`}>
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs text-gray-500 truncate">{label}</div>
          <div className={`text-lg font-bold ${valueColor}`}>{value}</div>
          {sub && <div className="text-[10px] text-gray-400 truncate">{sub}</div>}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Map Color Helpers
// ---------------------------------------------------------------------------

function getFieldMapColor(field: FarmonautField, layer: MapLayerType): string {
  if (layer === 'hybrid') {
    if (field.healthStatus === 'healthy' && field.waterStressLevel < 20) return 'rgba(34,197,94,0.6)';
    if (field.healthStatus === 'moderate') return 'rgba(249,115,22,0.6)';
    if (field.waterStressLevel > 50) return 'rgba(168,85,247,0.6)';
    if (field.healthStatus === 'critical') return 'rgba(239,68,68,0.6)';
    return 'rgba(34,197,94,0.4)';
  }
  const ndvi = field.ndvi;
  if (ndvi >= 0.6) return 'rgba(34,197,94,0.6)';
  if (ndvi >= 0.4) return 'rgba(234,179,8,0.6)';
  if (ndvi >= 0.2) return 'rgba(249,115,22,0.6)';
  return 'rgba(239,68,68,0.6)';
}

function getFieldMapBorderColor(status: CropHealthStatus): string {
  const map: Record<CropHealthStatus, string> = {
    healthy: '#22c55e',
    moderate: '#eab308',
    stressed: '#f97316',
    critical: '#ef4444',
  };
  return map[status];
}

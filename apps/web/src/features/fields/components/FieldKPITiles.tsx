'use client';

/**
 * SAHOOL Field KPI Tiles
 * بطاقات KPI للحقل — Sentinel Hub (35+ indices) + OpenWeather (25 KPIs)
 */

import React, { useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import { useFieldKpiSnapshot, useTriggerKpiRefresh } from '../hooks/useFieldKPIs';
import type { FieldKpiSnapshot } from '../api';

// ─── Status helpers ───────────────────────────────────────────────────────────

type Status = 'good' | 'warning' | 'critical' | 'na';

const dot: Record<Status, string> = {
  good: 'bg-green-500',
  warning: 'bg-yellow-500',
  critical: 'bg-red-500',
  na: 'bg-gray-300',
};

const border: Record<Status, string> = {
  good: 'border-green-400',
  warning: 'border-yellow-400',
  critical: 'border-red-400',
  na: 'border-gray-200',
};

function ndviSt(v?: number | null): Status {
  if (v == null) return 'na';
  return v >= 0.5 ? 'good' : v >= 0.3 ? 'warning' : 'critical';
}
function rangedSt(v: number | null | undefined, good: number, warn: number): Status {
  if (v == null) return 'na';
  return v >= good ? 'good' : v >= warn ? 'warning' : 'critical';
}
function tempSt(v?: number | null): Status {
  if (v == null) return 'na';
  return v > 45 || v < -5 ? 'critical' : v > 38 || v < 5 ? 'warning' : 'good';
}
function uvSt(v?: number | null): Status {
  if (v == null) return 'na';
  return v <= 5 ? 'good' : v <= 8 ? 'warning' : 'critical';
}
function aqiSt(v?: number | null): Status {
  if (v == null) return 'na';
  return v <= 2 ? 'good' : v <= 3 ? 'warning' : 'critical';
}

// ─── Tile atoms ───────────────────────────────────────────────────────────────

interface TileProps {
  label: string;
  labelAr: string;
  value: React.ReactNode;
  status: Status;
  unit?: string;
  /** Sentinel Hub index ID — when set, tile is clickable and activates map layer */
  layerId?: string;
  activeLayerId?: string;
  onLayerChange?: (id: string) => void;
}

function Tile({ label, labelAr, value, status, unit, layerId, activeLayerId, onLayerChange }: TileProps) {
  const isActive = !!layerId && layerId === activeLayerId;
  const isClickable = !!layerId && !!onLayerChange;

  return (
    <div
      className={[
        'bg-white rounded-xl border-l-4 border p-3 shadow-sm transition-all select-none',
        border[status],
        isActive
          ? 'ring-2 ring-green-500 ring-offset-1 border-green-300 shadow-md bg-green-50/30'
          : 'border-gray-100',
        isClickable ? 'cursor-pointer hover:shadow-md hover:ring-1 hover:ring-green-300' : '',
      ].join(' ')}
      onClick={isClickable ? () => onLayerChange!(layerId!) : undefined}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={
        isClickable
          ? (e) => { if (e.key === 'Enter' || e.key === ' ') onLayerChange!(layerId!); }
          : undefined
      }
    >
      <div className="flex items-start justify-between mb-1">
        <div className="min-w-0">
          <p className="text-xs font-medium text-gray-600 truncate">{label}</p>
          <p className="text-xs text-gray-400 truncate">{labelAr}</p>
        </div>
        <div className="flex flex-col items-end gap-0.5 flex-shrink-0 ml-1">
          <span className={`w-2 h-2 rounded-full mt-0.5 ${dot[status]}`} />
          {isClickable && (
            <span className="text-[9px] leading-none" title={isActive ? 'على الخريطة' : 'عرض على الخريطة'}>
              {isActive ? '🛰️' : '🗺️'}
            </span>
          )}
        </div>
      </div>
      <p className="text-lg font-bold text-gray-900 mt-1 leading-tight">
        {value != null ? (
          <>
            {value}
            {unit && <span className="text-xs font-normal text-gray-500 ml-1">{unit}</span>}
          </>
        ) : (
          <span className="text-gray-300 text-sm">—</span>
        )}
      </p>
      {isActive && (
        <p className="text-[10px] text-green-600 font-semibold mt-1">● على الخريطة</p>
      )}
    </div>
  );
}

function Skeleton() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-3 shadow-sm animate-pulse">
      <div className="h-3 bg-gray-200 rounded w-2/3 mb-2" />
      <div className="h-3 bg-gray-100 rounded w-1/2 mb-3" />
      <div className="h-5 bg-gray-200 rounded w-1/3" />
    </div>
  );
}

// ─── Section wrapper ──────────────────────────────────────────────────────────

function Section({
  title,
  titleAr,
  subtitle,
  loading,
  count,
  onRefresh,
  children,
}: {
  title: string;
  titleAr: string;
  subtitle?: string;
  loading: boolean;
  count: number;
  onRefresh?: () => void;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-700">{titleAr}</h3>
          <p className="text-xs text-gray-400">{subtitle ?? title}</p>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            تحديث
          </button>
        )}
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {loading
          ? Array.from({ length: count }).map((_, i) => <Skeleton key={i} />)
          : children}
      </div>
    </div>
  );
}

// ─── Shared props for sentinel sections ───────────────────────────────────────

interface SentinelProps {
  kpi?: FieldKpiSnapshot | null;
  loading: boolean;
  /** Active Sentinel Hub layer shown on map — highlight matching tile */
  activeLayerId?: string;
  /** Called when user clicks a tile to switch the map's active layer */
  onLayerChange?: (id: string) => void;
}

// ─── Theme sections ───────────────────────────────────────────────────────────

function fmt(v: number | null | undefined, decimals = 3) {
  return v != null ? Number(v).toFixed(decimals) : null;
}

export function VegetationSection({
  kpi, loading, onRefresh, activeLayerId, onLayerChange,
}: SentinelProps & { onRefresh: () => void }) {
  const lp = { activeLayerId, onLayerChange };
  return (
    <Section title="Sentinel Hub — Vegetation" titleAr="مؤشرات النباتات — Sentinel Hub"
      subtitle="NDVI · EVI · LAI · GNDVI · NDRE · MSAVI · OSAVI · EVI2 · CVI · MCARI · TCARI · WDRVI · VARI"
      loading={loading} count={15} onRefresh={onRefresh}>
      <Tile label="NDVI"  labelAr="مؤشر الغطاء النباتي"          value={fmt(kpi?.ndvi)}   status={ndviSt(kpi?.ndvi)}              layerId="NDVI"  {...lp} />
      <Tile label="EVI"   labelAr="مؤشر النباتات المحسّن"         value={fmt(kpi?.evi)}    status={rangedSt(kpi?.evi, 0.4, 0.2)}   layerId="EVI"   {...lp} />
      <Tile label="LAI"   labelAr="مؤشر مساحة الأوراق"            value={fmt(kpi?.lai)}    status={rangedSt(kpi?.lai, 2, 1)}       layerId="LAI"   {...lp} />
      <Tile label="SAVI"  labelAr="مؤشر معدّل للتربة"             value={fmt(kpi?.savi)}   status={rangedSt(kpi?.savi, 0.35, 0.15)} layerId="SAVI"  {...lp} />
      <Tile label="NDMI"  labelAr="مؤشر رطوبة النبات"             value={fmt(kpi?.ndmi)}   status={rangedSt(kpi?.ndmi, 0.1, -0.1)} />
      <Tile label="GNDVI" labelAr="NDVI الأخضر"                   value={fmt(kpi?.gndvi)}  status={rangedSt(kpi?.gndvi, 0.4, 0.2)} layerId="GNDVI" {...lp} />
      <Tile label="NDRE"  labelAr="NDVI الحافة الحمراء"            value={fmt(kpi?.ndre)}   status={rangedSt(kpi?.ndre, 0.2, 0.1)}  layerId="NDRE"  {...lp} />
      <Tile label="MSAVI" labelAr="SAVI المعدّل"                   value={fmt(kpi?.msavi)}  status={rangedSt(kpi?.msavi, 0.3, 0.1)} layerId="MSAVI" {...lp} />
      <Tile label="OSAVI" labelAr="SAVI المحسّن"                   value={fmt(kpi?.osavi)}  status={rangedSt(kpi?.osavi, 0.35, 0.15)} layerId="OSAVI" {...lp} />
      <Tile label="EVI2"  labelAr="EVI ثنائي النطاق"              value={fmt(kpi?.evi2)}   status={rangedSt(kpi?.evi2, 0.4, 0.2)}  layerId="EVI2"  {...lp} />
      <Tile label="CVI"   labelAr="مؤشر الكلوروفيل"               value={fmt(kpi?.cvi)}    status={rangedSt(kpi?.cvi, 2, 1)} />
      <Tile label="MCARI" labelAr="نسبة امتصاص الكلوروفيل"        value={fmt(kpi?.mcari)}  status={rangedSt(kpi?.mcari, 0.1, 0)} />
      <Tile label="TCARI" labelAr="نسبة الكلوروفيل المحوّلة"      value={fmt(kpi?.tcari)}  status={rangedSt(kpi?.tcari, 0.1, 0)} />
      <Tile label="WDRVI" labelAr="نطاق ديناميكي عريض"            value={fmt(kpi?.wdrvi)}  status={rangedSt(kpi?.wdrvi, 0.1, -0.1)} />
      <Tile label="VARI"  labelAr="مؤشر مقاوم للغلاف الجوي"       value={fmt(kpi?.vari)}   status={rangedSt(kpi?.vari, 0.1, 0)}   layerId="ARVI"  {...lp} />
    </Section>
  );
}

export function WaterSection({ kpi, loading, activeLayerId, onLayerChange }: SentinelProps) {
  const lp = { activeLayerId, onLayerChange };
  return (
    <Section title="Sentinel Hub — Water" titleAr="مؤشرات المياه — Sentinel Hub"
      subtitle="NDWI · MNDWI · Turbidity · Chlorophyll-a · Phycocyanin"
      loading={loading} count={5}>
      <Tile label="NDWI"         labelAr="مؤشر الماء"          value={fmt(kpi?.ndwi)}        status={rangedSt(kpi?.ndwi, 0.2, 0)}    layerId="NDWI"  {...lp} />
      <Tile label="MNDWI"        labelAr="NDWI المعدّل"         value={fmt(kpi?.mndwi)}       status={rangedSt(kpi?.mndwi, 0.2, 0)}   layerId="MNDWI" {...lp} />
      <Tile label="Turbidity"    labelAr="عكارة الماء"          value={fmt(kpi?.turbidity)}   status={kpi?.turbidity != null ? 'good' : 'na'} />
      <Tile label="Chlorophyll-a" labelAr="الكلوروفيل أ"        value={fmt(kpi?.chlorophyll, 2)} unit="μg/L" status={kpi?.chlorophyll != null ? 'good' : 'na'} />
      <Tile label="Phycocyanin"  labelAr="فيكوسيانين (طحالب)"  value={fmt(kpi?.phycocyanin, 2)} unit="μg/L" status={kpi?.phycocyanin != null ? 'good' : 'na'} />
    </Section>
  );
}

export function SoilSection({ kpi, loading, activeLayerId, onLayerChange }: SentinelProps) {
  const lp = { activeLayerId, onLayerChange };
  return (
    <Section title="Sentinel Hub — Soil / Bare Land" titleAr="التربة والأراضي الجرداء — Sentinel Hub"
      subtitle="BSI · NBSI"
      loading={loading} count={2}>
      <Tile label="BSI"  labelAr="مؤشر التربة العارية" value={fmt(kpi?.bsi)}  status={rangedSt(kpi?.bsi, 0.1, 0)}  layerId="BSI"  {...lp} />
      <Tile label="NBSI" labelAr="BSI المعيّر"          value={fmt(kpi?.nbsi)} status={rangedSt(kpi?.nbsi, 0.1, 0)} layerId="NBSI" {...lp} />
    </Section>
  );
}

export function FireSection({ kpi, loading, activeLayerId, onLayerChange }: SentinelProps) {
  const lp = { activeLayerId, onLayerChange };
  return (
    <Section title="Sentinel Hub — Fire / Burn" titleAr="الحرائق والحرق — Sentinel Hub"
      subtitle="NBR · NBR2 · BAIS2"
      loading={loading} count={3}>
      <Tile label="NBR"   labelAr="نسبة الحرق المعيّرة"   value={fmt(kpi?.nbr)}   status={kpi?.nbr   != null ? (kpi.nbr   < -0.1 ? 'critical' : kpi.nbr   < 0.1 ? 'warning' : 'good') : 'na'} layerId="NBR"   {...lp} />
      <Tile label="NBR2"  labelAr="نسبة الحرق 2"           value={fmt(kpi?.nbr2)}  status={kpi?.nbr2  != null ? (kpi.nbr2  < -0.1 ? 'critical' : 'good') : 'na'}                              layerId="NBR2"  {...lp} />
      <Tile label="BAIS2" labelAr="مؤشر المناطق المحروقة" value={fmt(kpi?.bais2)} status={kpi?.bais2 != null ? (kpi.bais2 > 1.5  ? 'critical' : 'good') : 'na'}                              layerId="BAIS2" {...lp} />
    </Section>
  );
}

export function UrbanSection({ kpi, loading, activeLayerId, onLayerChange }: SentinelProps) {
  const lp = { activeLayerId, onLayerChange };
  return (
    <Section title="Sentinel Hub — Urban / Built-up" titleAr="العمران والمباني — Sentinel Hub"
      subtitle="NDBI · IBI"
      loading={loading} count={2}>
      <Tile label="NDBI" labelAr="مؤشر المناطق المبنية"  value={fmt(kpi?.ndbi)} status={rangedSt(kpi?.ndbi, 0.1, 0)} layerId="NDBI" {...lp} />
      <Tile label="IBI"  labelAr="مؤشر المناطق المعمّرة" value={fmt(kpi?.ibi)}  status={rangedSt(kpi?.ibi,  0.1, 0)} layerId="IBI"  {...lp} />
    </Section>
  );
}

export function SnowSection({ kpi, loading, activeLayerId, onLayerChange }: SentinelProps) {
  const lp = { activeLayerId, onLayerChange };
  return (
    <Section title="Sentinel Hub — Snow / Ice" titleAr="الثلوج والجليد — Sentinel Hub"
      subtitle="NDSI · NDGI"
      loading={loading} count={2}>
      <Tile label="NDSI" labelAr="مؤشر الثلج"   value={fmt(kpi?.ndsi)} status={rangedSt(kpi?.ndsi, 0.4, 0.2)} layerId="NDSI" {...lp} />
      <Tile label="NDGI" labelAr="مؤشر الجليد"  value={fmt(kpi?.ndgi)} status={rangedSt(kpi?.ndgi, 0.2, 0)}   layerId="NDGI" {...lp} />
    </Section>
  );
}

export function AtmosphereSection({ kpi, loading, activeLayerId, onLayerChange }: SentinelProps) {
  const lp = { activeLayerId, onLayerChange };
  return (
    <Section title="Sentinel Hub — Atmosphere" titleAr="الغلاف الجوي — Sentinel Hub"
      subtitle="LST · Cloud Probability · ARVI"
      loading={loading} count={3}>
      <Tile label="LST"         labelAr="حرارة سطح الأرض"          value={fmt(kpi?.lst, 1)}              unit="°C" status={tempSt(kpi?.lst)}                                                                        layerId="LST"  {...lp} />
      <Tile label="Cloud Prob." labelAr="احتمالية السحب"            value={fmt(kpi?.cloudProbability, 1)} unit="%" status={kpi?.cloudProbability != null ? (kpi.cloudProbability < 30 ? 'good' : kpi.cloudProbability < 70 ? 'warning' : 'critical') : 'na'} />
      <Tile label="ARVI"        labelAr="مؤشر نباتي مقاوم للغلاف"  value={fmt(kpi?.arvi)}                        status={rangedSt(kpi?.arvi, 0.4, 0.2)}                                                              layerId="ARVI" {...lp} />
    </Section>
  );
}

export function WeatherSection({ kpi, loading }: { kpi?: FieldKpiSnapshot | null; loading: boolean }) {
  return (
    <Section title="OpenWeatherMap — Current Conditions" titleAr="بيانات الطقس الحالية — OpenWeather"
      subtitle="Temperature · Humidity · Wind · Pressure · Cloud Cover · Visibility · UV"
      loading={loading} count={8}>
      <Tile label="Temperature"  labelAr="درجة الحرارة"        value={fmt(kpi?.temperature, 1)}  unit="°C"   status={tempSt(kpi?.temperature)} />
      <Tile label="Humidity"     labelAr="الرطوبة"              value={fmt(kpi?.humidity, 0)}     unit="%"    status={kpi?.humidity  != null ? 'good' : 'na'} />
      <Tile label="Wind Speed"   labelAr="سرعة الرياح"          value={fmt(kpi?.windSpeed, 1)}    unit="km/h" status={kpi?.windSpeed  != null ? (kpi.windSpeed > 60 ? 'critical' : kpi.windSpeed > 30 ? 'warning' : 'good') : 'na'} />
      <Tile label="Wind Dir."    labelAr="اتجاه الرياح"         value={fmt(kpi?.windDirection, 0)} unit="°"   status={kpi?.windDirection != null ? 'good' : 'na'} />
      <Tile label="Precipitation" labelAr="هطول الأمطار"        value={fmt(kpi?.precipitation, 1)} unit="mm" status={kpi?.precipitation != null ? 'good' : 'na'} />
      <Tile label="Pressure"     labelAr="الضغط الجوي"          value={fmt(kpi?.pressure, 0)}     unit="hPa" status={kpi?.pressure    != null ? 'good' : 'na'} />
      <Tile label="Cloud Cover"  labelAr="الغطاء السحابي"       value={fmt(kpi?.cloudCover, 0)}   unit="%"   status={kpi?.cloudCover  != null ? 'good' : 'na'} />
      <Tile label="UV Index"     labelAr="الأشعة فوق البنفسجية" value={fmt(kpi?.uvIndex, 1)}               status={uvSt(kpi?.uvIndex)} />
      {kpi?.weatherConditionAr && (
        <div className="col-span-full text-xs text-gray-500 mt-1">
          الحالة: {kpi.weatherConditionAr}
          {kpi.weatherCondition && ` · ${kpi.weatherCondition}`}
        </div>
      )}
    </Section>
  );
}

export function AirQualitySection({ kpi, loading }: { kpi?: FieldKpiSnapshot | null; loading: boolean }) {
  const AQI_AR: Record<number, string> = { 1: 'جيدة', 2: 'مقبولة', 3: 'معتدلة', 4: 'سيئة', 5: 'سيئة جداً' };
  return (
    <Section title="OpenWeatherMap — Air Pollution" titleAr="جودة الهواء — OpenWeather"
      subtitle="AQI · CO · NO · NO₂ · O₃ · SO₂ · NH₃ · PM2.5 · PM10"
      loading={loading} count={9}>
      <Tile label="AQI"   labelAr="مؤشر جودة الهواء"      value={kpi?.aqi  != null ? `${kpi.aqi} — ${AQI_AR[kpi.aqi] ?? ''}` : null} status={aqiSt(kpi?.aqi)} />
      <Tile label="CO"    labelAr="أول أكسيد الكربون"      value={fmt(kpi?.co, 1)}   unit="μg/m³" status={kpi?.co  != null ? (kpi.co  > 10000 ? 'critical' : kpi.co  > 4000 ? 'warning' : 'good') : 'na'} />
      <Tile label="NO"    labelAr="أكسيد النيتريك"          value={fmt(kpi?.no, 2)}   unit="μg/m³" status={kpi?.no  != null ? 'good' : 'na'} />
      <Tile label="NO₂"   labelAr="ثاني أكسيد النيتروجين"  value={fmt(kpi?.no2, 2)}  unit="μg/m³" status={kpi?.no2 != null ? (kpi.no2 > 200 ? 'critical' : kpi.no2 > 100 ? 'warning' : 'good') : 'na'} />
      <Tile label="O₃"    labelAr="الأوزون"                 value={fmt(kpi?.o3, 2)}   unit="μg/m³" status={kpi?.o3  != null ? (kpi.o3  > 180 ? 'critical' : kpi.o3  > 100 ? 'warning' : 'good') : 'na'} />
      <Tile label="SO₂"   labelAr="ثاني أكسيد الكبريت"     value={fmt(kpi?.so2, 2)}  unit="μg/m³" status={kpi?.so2 != null ? (kpi.so2 > 350 ? 'critical' : kpi.so2 > 125 ? 'warning' : 'good') : 'na'} />
      <Tile label="NH₃"   labelAr="الأمونيا"                value={fmt(kpi?.nh3, 2)}  unit="μg/m³" status={kpi?.nh3 != null ? 'good' : 'na'} />
      <Tile label="PM2.5" labelAr="جسيمات دقيقة 2.5"       value={fmt(kpi?.pm25, 1)} unit="μg/m³" status={kpi?.pm25 != null ? (kpi.pm25 > 75 ? 'critical' : kpi.pm25 > 35 ? 'warning' : 'good') : 'na'} />
      <Tile label="PM10"  labelAr="جسيمات دقيقة 10"        value={fmt(kpi?.pm10, 1)} unit="μg/m³" status={kpi?.pm10 != null ? (kpi.pm10 > 150 ? 'critical' : kpi.pm10 > 50 ? 'warning' : 'good') : 'na'} />
    </Section>
  );
}

export function SolarSection({ kpi, loading }: { kpi?: FieldKpiSnapshot | null; loading: boolean }) {
  return (
    <Section title="Open-Meteo — Solar Irradiance" titleAr="الإشعاع الشمسي — Open-Meteo"
      subtitle="GHI · DNI · DHI (Clear-sky & Actual)"
      loading={loading} count={6}>
      <Tile label="GHI Clear-sky" labelAr="إشعاع كلي (صافٍ)"       value={fmt(kpi?.ghiClearSky, 0)} unit="W/m²" status={kpi?.ghiClearSky != null ? 'good' : 'na'} />
      <Tile label="DNI Clear-sky" labelAr="إشعاع مباشر (صافٍ)"     value={fmt(kpi?.dniClearSky, 0)} unit="W/m²" status={kpi?.dniClearSky != null ? 'good' : 'na'} />
      <Tile label="DHI Clear-sky" labelAr="إشعاع منتشر (صافٍ)"     value={fmt(kpi?.dhiClearSky, 0)} unit="W/m²" status={kpi?.dhiClearSky != null ? 'good' : 'na'} />
      <Tile label="GHI Actual"    labelAr="إشعاع كلي فعلي"          value={fmt(kpi?.ghiCloudy, 0)}   unit="W/m²" status={kpi?.ghiCloudy   != null ? 'good' : 'na'} />
      <Tile label="DNI Actual"    labelAr="إشعاع مباشر فعلي"        value={fmt(kpi?.dniCloudy, 0)}   unit="W/m²" status={kpi?.dniCloudy   != null ? 'good' : 'na'} />
      <Tile label="DHI Actual"    labelAr="إشعاع منتشر فعلي"        value={fmt(kpi?.dhiCloudy, 0)}   unit="W/m²" status={kpi?.dhiCloudy   != null ? 'good' : 'na'} />
    </Section>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface FieldKPITilesProps {
  fieldId: string;
  centroidLat?: number;
  centroidLng?: number;
  polygonCoordinates?: number[][];
  disableAutoTrigger?: boolean;
}

export function FieldKPITiles({
  fieldId,
  centroidLat,
  centroidLng,
  polygonCoordinates,
  disableAutoTrigger = false,
}: FieldKPITilesProps) {
  const { data: kpi, isLoading } = useFieldKpiSnapshot(fieldId);
  const refresh = useTriggerKpiRefresh(fieldId);

  const isEmptySnapshot =
    kpi != null &&
    kpi.ndvi == null && kpi.temperature == null &&
    kpi.humidity == null && kpi.aqi == null && kpi.ghiClearSky == null;

  useEffect(() => {
    if (
      !disableAutoTrigger &&
      !isLoading &&
      (kpi === null || isEmptySnapshot) &&
      centroidLat != null &&
      centroidLng != null &&
      !refresh.isPending
    ) {
      refresh.mutate({ lat: centroidLat, lng: centroidLng, polygonCoordinates });
    }
  }, [isLoading, kpi, isEmptySnapshot, centroidLat, centroidLng, disableAutoTrigger]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleRefresh = () => {
    if (centroidLat != null && centroidLng != null) {
      refresh.mutate({ lat: centroidLat, lng: centroidLng, polygonCoordinates });
    }
  };

  const working = isLoading || refresh.isPending;

  if (!working && (kpi === null || isEmptySnapshot) && (centroidLat == null || centroidLng == null)) {
    return (
      <div className="text-center py-8 text-gray-500 text-sm">
        <p>لا تتوفر بيانات KPI — يرجى رسم حدود الحقل أولاً لتفعيل التحليل.</p>
        <p className="text-xs text-gray-400 mt-1">KPI data unavailable — draw the field boundary first.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-gray-800">مؤشرات الحقل</h2>
          <p className="text-xs text-gray-400">Sentinel Hub (35+ indices) + OpenWeather (25 KPIs)</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={working || (centroidLat == null || centroidLng == null)}
          className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800 disabled:opacity-40 font-medium"
        >
          <RefreshCw className={`w-4 h-4 ${working ? 'animate-spin' : ''}`} />
          {working ? 'جاري التحديث...' : 'تحديث الكل'}
        </button>
      </div>

      {kpi?.fetchedAt && !working && (
        <p className="text-xs text-gray-400 -mt-6">
          آخر تحديث: {new Date(kpi.fetchedAt).toLocaleString('ar-SA')}
          {kpi.satelliteSource && ` · ${kpi.satelliteSource}`}
        </p>
      )}

      {/* 7 satellite theme sections */}
      <VegetationSection kpi={kpi} loading={working} onRefresh={handleRefresh} />
      <WaterSection      kpi={kpi} loading={working} />
      <SoilSection       kpi={kpi} loading={working} />
      <FireSection       kpi={kpi} loading={working} />
      <UrbanSection      kpi={kpi} loading={working} />
      <SnowSection       kpi={kpi} loading={working} />
      <AtmosphereSection kpi={kpi} loading={working} />

      {/* 3 weather / air / solar sections */}
      <WeatherSection    kpi={kpi} loading={working} />
      <AirQualitySection kpi={kpi} loading={working} />
      <SolarSection      kpi={kpi} loading={working} />
    </div>
  );
}

export default FieldKPITiles;

'use client';

import React, { useState, useMemo } from 'react';
import { Building2, Plus, Search, MapPin, Droplets, Users, AlertTriangle, X, Loader2 } from 'lucide-react';
import { useLocale } from 'next-intl';
import { useFarms, useFarmStats, useUpdateFarm, useCreateFarm } from '@/features/farms';
import type { Farm, FarmStatus, FarmFormData } from '@/features/farms';
import dynamic from 'next/dynamic';
import { logger } from '@/lib/logger';
import { YEMEN_GOVERNORATES } from '@/data/yemen-locations';

const FarmDrawer = dynamic(
  () => import('@/components/maps/LeafletFieldDrawer'),
  { ssr: false, loading: () => <div className="h-[500px] bg-gray-100 rounded-lg animate-pulse flex items-center justify-center"><span className="text-gray-500 text-sm">جاري تحميل الخريطة...</span></div> }
);

/** Derive [minLng, minLat, maxLng, maxLat] from a GeoJSON Polygon. */
function polygonToBbox(polygon: GeoJSON.Polygon | null): [number, number, number, number] | null {
  if (!polygon) return null;
  const coords = polygon.coordinates[0];
  if (!coords || coords.length === 0) return null;
  const lngs = coords.map((c) => c[0]!);
  const lats = coords.map((c) => c[1]!);
  return [Math.min(...lngs), Math.min(...lats), Math.max(...lngs), Math.max(...lats)];
}

/** Compute area in hectares from a GeoJSON Polygon using the spherical excess formula. */
function computeAreaHa(polygon: GeoJSON.Polygon | null): number {
  if (!polygon) return 0;
  const ring = polygon.coordinates[0];
  if (!ring || ring.length < 4) return 0;
  const R = 6371000; // Earth radius in metres
  const toRad = (d: number) => (d * Math.PI) / 180;
  let area = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = toRad(ring[i]![0]!);
    const yi = toRad(ring[i]![1]!);
    const xj = toRad(ring[j]![0]!);
    const yj = toRad(ring[j]![1]!);
    area += (xj - xi) * (2 + Math.sin(yi) + Math.sin(yj));
  }
  const areaM2 = Math.abs((area * R * R) / 2);
  return Math.round((areaM2 / 10000) * 100) / 100; // m² → hectares, 2 decimals
}

const WATER_SOURCES = [
  { value: 'آبار',  labelAr: 'آبار',  labelEn: 'Wells' },
  { value: 'امطار', labelAr: 'امطار', labelEn: 'Rain' },
  { value: 'سدود',  labelAr: 'سدود',  labelEn: 'Dams' },
  { value: 'سيول',  labelAr: 'سيول',  labelEn: 'Floods' },
  { value: 'غيول',  labelAr: 'غيول',  labelEn: 'Springs' },
  { value: 'أنهار', labelAr: 'أنهار', labelEn: 'Rivers' },
] as const;

const statusConfig: Record<FarmStatus, { color: string; labelAr: string }> = {
  active: { color: 'bg-green-100 text-green-800', labelAr: 'نشطة' },
  inactive: { color: 'bg-gray-100 text-gray-800', labelAr: 'غير نشطة' },
  seasonal: { color: 'bg-blue-100 text-blue-800', labelAr: 'موسمية' },
};

export default function FarmsClient() {
  const locale = useLocale();
  const isRtl = locale === 'ar';

  const [searchTerm, setSearchTerm] = useState('');
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [editName, setEditName] = useState('');
  const [editNameAr, setEditNameAr] = useState('');
  const [editWaterSource, setEditWaterSource] = useState('');
  const [editBbox, setEditBbox] = useState<[number, number, number, number] | null>(null);
  const [editCenterLat, setEditCenterLat] = useState<number | null>(null);
  const [editCenterLng, setEditCenterLng] = useState<number | null>(null);
  const [createZoom, setCreateZoom] = useState<number>(10);
  const [editZoom, setEditZoom] = useState<number>(10);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newFarm, setNewFarm] = useState<Omit<FarmFormData, 'region' | 'regionAr'>>({ name: '', nameAr: '', location: '', locationAr: '', totalAreaHa: 0, waterSource: '', waterSourceAr: '' });

  // Create dialog — location dropdowns
  const [createGov, setCreateGov] = useState('');
  const [createDist, setCreateDist] = useState('');
  const [createFlyTo, setCreateFlyTo] = useState<[number, number] | null>(null);

  // Edit dialog — location dropdowns
  const [editGov, setEditGov] = useState('');
  const [editDist, setEditDist] = useState('');
  const [editFlyTo, setEditFlyTo] = useState<[number, number] | null>(null);

  const { data: farms = [], isLoading, error } = useFarms();
  const { data: stats } = useFarmStats();
  const updateFarm = useUpdateFarm();
  const createFarm = useCreateFarm();

  const createGovData = YEMEN_GOVERNORATES.find((g) => g.nameAr === createGov) ?? null;
  const editGovData   = YEMEN_GOVERNORATES.find((g) => g.nameAr === editGov)   ?? null;

  const handleCreateGovChange = (govAr: string) => {
    setCreateGov(govAr);
    setCreateDist('');
    setCreateFlyTo(null);
    const gov = YEMEN_GOVERNORATES.find((g) => g.nameAr === govAr);
    if (gov) {
      setCreateFlyTo(gov.center);
      setNewFarm((prev) => ({ ...prev, location: gov.nameEn, locationAr: gov.nameAr }));
    } else {
      setNewFarm((prev) => ({ ...prev, location: '', locationAr: '' }));
    }
  };

  const handleCreateDistChange = (distAr: string) => {
    setCreateDist(distAr);
    const gov = YEMEN_GOVERNORATES.find((g) => g.nameAr === createGov);
    const dist = gov?.districts.find((d) => d.nameAr === distAr);
    if (dist) {
      setCreateFlyTo(dist.center);
      setNewFarm((prev) => ({
        ...prev,
        location: `${dist.nameEn}, ${gov!.nameEn}`,
        locationAr: `${dist.nameAr}، ${gov!.nameAr}`,
      }));
    }
  };

  const handleEditGovChange = (govAr: string) => {
    setEditGov(govAr);
    setEditDist('');
    setEditFlyTo(null);
    const gov = YEMEN_GOVERNORATES.find((g) => g.nameAr === govAr);
    if (gov) setEditFlyTo(gov.center);
  };

  const handleEditDistChange = (distAr: string) => {
    setEditDist(distAr);
    const gov = YEMEN_GOVERNORATES.find((g) => g.nameAr === editGov);
    const dist = gov?.districts.find((d) => d.nameAr === distAr);
    if (dist) setEditFlyTo(dist.center);
  };

  const handleCreateFarm = () => {
    createFarm.mutate(
      { ...newFarm, region: '', regionAr: '', zoom: createZoom },
      {
        onSuccess: () => {
          setShowCreateDialog(false);
          setNewFarm({ name: '', nameAr: '', location: '', locationAr: '', totalAreaHa: 0, waterSource: '', waterSourceAr: '', centerLat: undefined, centerLng: undefined });
          setCreateZoom(10);
          setCreateGov('');
          setCreateDist('');
          setCreateFlyTo(null);
        },
      }
    );
  };

  const filteredFarms = useMemo(() => {
    if (!searchTerm) return farms;
    const term = searchTerm.toLowerCase();
    return farms.filter(
      (f) =>
        f.name.toLowerCase().includes(term) ||
        f.nameAr.includes(searchTerm) ||
        f.locationAr.includes(searchTerm)
    );
  }, [farms, searchTerm]);

  if (isLoading && farms.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  const handleOpenEdit = (farm: Farm) => {
    setEditingFarm(farm);
    setEditName(farm.name);
    setEditNameAr(farm.nameAr);
    setEditWaterSource(farm.waterSource ?? '');
    // Pre-fill governorate/district from saved locationAr (best-effort match)
    const matchedGov = YEMEN_GOVERNORATES.find(
      (g) => farm.locationAr?.includes(g.nameAr)
    );
    if (matchedGov) {
      setEditGov(matchedGov.nameAr);
      setEditFlyTo(matchedGov.center);
      const matchedDist = matchedGov.districts.find(
        (d) => farm.locationAr?.includes(d.nameAr)
      );
      if (matchedDist) {
        setEditDist(matchedDist.nameAr);
        setEditFlyTo(matchedDist.center);
      }
    }
  };

  const handleSaveEdit = () => {
    if (!editingFarm) return;
    const editGovObj  = YEMEN_GOVERNORATES.find((g) => g.nameAr === editGov);
    const editDistObj = editGovObj?.districts.find((d) => d.nameAr === editDist);
    const locationEn = editDistObj
      ? `${editDistObj.nameEn}, ${editGovObj!.nameEn}`
      : editGovObj?.nameEn ?? editingFarm.location;
    const locationAr = editDistObj
      ? `${editDistObj.nameAr}، ${editGovObj!.nameAr}`
      : editGovObj?.nameAr ?? editingFarm.locationAr;
    updateFarm.mutate(
      {
        id: editingFarm.id,
        data: {
          name: editName, nameAr: editNameAr,
          waterSource: editWaterSource, waterSourceAr: editWaterSource,
          location: locationEn, locationAr,
          zoom: editZoom,
          ...(editBbox ? { bbox: editBbox } : {}),
          ...(editCenterLat !== null ? { centerLat: editCenterLat } : {}),
          ...(editCenterLng !== null ? { centerLng: editCenterLng } : {}),
          ...(editingFarm.totalAreaHa ? { totalAreaHa: editingFarm.totalAreaHa } : {}),
        },
      },
      {
        onSuccess: () => {
          setEditingFarm(null); setEditBbox(null);
          setEditCenterLat(null); setEditCenterLng(null);
          setEditZoom(10);
          setEditWaterSource(''); setEditGov(''); setEditDist(''); setEditFlyTo(null);
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Create Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl flex flex-col max-h-[95vh]">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b shrink-0">
              <h2 className="text-lg font-bold text-gray-900">إضافة مزرعة جديدة</h2>
              <button onClick={() => setShowCreateDialog(false)} disabled={createFarm.isPending} className="text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body — scrollable */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {/* Fields row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'اسم المزرعة' : 'Farm Name'}
                  </label>
                  <input
                    value={newFarm.name}
                    onChange={(e) => setNewFarm({ ...newFarm, name: e.target.value, nameAr: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                    dir={isRtl ? 'rtl' : 'ltr'}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'المحافظة' : 'Governorate'}
                  </label>
                  <select
                    value={createGov}
                    onChange={(e) => handleCreateGovChange(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 bg-white"
                    dir="rtl"
                  >
                    <option value="">{isRtl ? '— اختر المحافظة —' : '— Select Governorate —'}</option>
                    {YEMEN_GOVERNORATES.map((g) => (
                      <option key={g.nameAr} value={g.nameAr}>
                        {isRtl ? g.nameAr : g.nameEn}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'المديرية' : 'District'}
                  </label>
                  <select
                    value={createDist}
                    onChange={(e) => handleCreateDistChange(e.target.value)}
                    disabled={!createGovData}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 bg-white disabled:opacity-50"
                    dir="rtl"
                  >
                    <option value="">{isRtl ? '— اختر المديرية —' : '— Select District —'}</option>
                    {(createGovData?.districts ?? []).map((d) => (
                      <option key={d.nameAr} value={d.nameAr}>
                        {isRtl ? d.nameAr : d.nameEn}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'المساحة الكلية (هكتار)' : 'Total Area (ha)'}
                  </label>
                  <input
                    type="number"
                    min={0}
                    value={newFarm.totalAreaHa}
                    onChange={(e) => setNewFarm({ ...newFarm, totalAreaHa: Number(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'مصدر المياه' : 'Water Source'}
                  </label>
                  <select
                    value={newFarm.waterSource}
                    onChange={(e) => setNewFarm({ ...newFarm, waterSource: e.target.value, waterSourceAr: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 bg-white"
                    dir={isRtl ? 'rtl' : 'ltr'}
                  >
                    <option value="">{isRtl ? '— اختر مصدر المياه —' : '— Select water source —'}</option>
                    {WATER_SOURCES.map((ws) => (
                      <option key={ws.value} value={ws.value}>
                        {isRtl ? ws.labelAr : ws.labelEn}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Map */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isRtl ? 'حدود المزرعة (اختياري)' : 'Farm Boundary (optional)'}
                </label>
                <FarmDrawer
                  height="500px"
                  initialCenter={[15.5527, 48.5164]}
                  initialZoom={6}
                  externalFlyTo={createFlyTo}
                  externalFlyZoom={createDist ? 11 : 8}
                  onZoomChange={setCreateZoom}
                  onBoundaryChange={(polygon) => {
                    const bbox = polygonToBbox(polygon);
                    const area = computeAreaHa(polygon);
                    const centerLat = bbox ? (bbox[1] + bbox[3]) / 2 : undefined;
                    const centerLng = bbox ? (bbox[0] + bbox[2]) / 2 : undefined;
                    setNewFarm((prev) => ({
                      ...prev,
                      bbox: bbox ?? undefined,
                      centerLat,
                      centerLng,
                      ...(area > 0 ? { totalAreaHa: area } : {}),
                    }));
                  }}
                />
              </div>

              {/* احداثيات المزرعة — auto-filled from bbox + zoom */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    {isRtl ? 'خط العرض (Lat)' : 'Latitude'}
                  </label>
                  <input
                    type="text"
                    disabled
                    value={newFarm.centerLat != null ? newFarm.centerLat.toFixed(6) : ''}
                    placeholder={isRtl ? 'تلقائي' : 'Auto'}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 text-gray-600 text-sm cursor-not-allowed"
                    dir="ltr"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    {isRtl ? 'خط الطول (Lng)' : 'Longitude'}
                  </label>
                  <input
                    type="text"
                    disabled
                    value={newFarm.centerLng != null ? newFarm.centerLng.toFixed(6) : ''}
                    placeholder={isRtl ? 'تلقائي' : 'Auto'}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 text-gray-600 text-sm cursor-not-allowed"
                    dir="ltr"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    {isRtl ? 'مستوى التكبير' : 'Zoom'}
                  </label>
                  <input
                    type="text"
                    disabled
                    value={createZoom}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 text-gray-600 text-sm cursor-not-allowed"
                    dir="ltr"
                  />
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 px-6 py-4 border-t shrink-0">
              <button
                onClick={() => setShowCreateDialog(false)}
                disabled={createFarm.isPending}
                className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isRtl ? 'إلغاء' : 'Cancel'}
              </button>
              <button
                onClick={handleCreateFarm}
                disabled={createFarm.isPending || !newFarm.name}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {createFarm.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                {createFarm.isPending ? (isRtl ? 'جاري الإنشاء...' : 'Creating...') : (isRtl ? 'إنشاء' : 'Create')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Dialog */}
      {editingFarm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl flex flex-col max-h-[95vh]">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b shrink-0">
              <h2 className="text-lg font-bold text-gray-900">تعديل المزرعة</h2>
              <button onClick={() => { setEditingFarm(null); setEditGov(''); setEditDist(''); setEditFlyTo(null); }} disabled={updateFarm.isPending} className="text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'اسم المزرعة' : 'Farm Name'}
                  </label>
                  <input
                    value={editName}
                    onChange={(e) => { setEditName(e.target.value); setEditNameAr(e.target.value); }}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
                    dir={isRtl ? 'rtl' : 'ltr'}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'مصدر المياه' : 'Water Source'}
                  </label>
                  <select
                    value={editWaterSource}
                    onChange={(e) => setEditWaterSource(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 bg-white"
                    dir={isRtl ? 'rtl' : 'ltr'}
                  >
                    <option value="">{isRtl ? '— اختر مصدر المياه —' : '— Select water source —'}</option>
                    {WATER_SOURCES.map((ws) => (
                      <option key={ws.value} value={ws.value}>
                        {isRtl ? ws.labelAr : ws.labelEn}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'المحافظة' : 'Governorate'}
                  </label>
                  <select
                    value={editGov}
                    onChange={(e) => handleEditGovChange(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 bg-white"
                    dir="rtl"
                  >
                    <option value="">{isRtl ? '— اختر المحافظة —' : '— Select Governorate —'}</option>
                    {YEMEN_GOVERNORATES.map((g) => (
                      <option key={g.nameAr} value={g.nameAr}>
                        {isRtl ? g.nameAr : g.nameEn}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isRtl ? 'المديرية' : 'District'}
                  </label>
                  <select
                    value={editDist}
                    onChange={(e) => handleEditDistChange(e.target.value)}
                    disabled={!editGovData}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 bg-white disabled:opacity-50"
                    dir="rtl"
                  >
                    <option value="">{isRtl ? '— اختر المديرية —' : '— Select District —'}</option>
                    {(editGovData?.districts ?? []).map((d) => (
                      <option key={d.nameAr} value={d.nameAr}>
                        {isRtl ? d.nameAr : d.nameEn}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Map */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isRtl ? 'حدود المزرعة (اختياري)' : 'Farm Boundary (optional)'}
                </label>
                <FarmDrawer
                  height="500px"
                  initialCenter={[15.5527, 48.5164]}
                  initialZoom={6}
                  externalFlyTo={editFlyTo}
                  externalFlyZoom={editDist ? 11 : 8}
                  onZoomChange={setEditZoom}
                  onBoundaryChange={(polygon) => {
                    const bbox = polygonToBbox(polygon);
                    setEditBbox(bbox);
                    setEditCenterLat(bbox ? (bbox[1] + bbox[3]) / 2 : null);
                    setEditCenterLng(bbox ? (bbox[0] + bbox[2]) / 2 : null);
                    const area = computeAreaHa(polygon);
                    if (area > 0 && editingFarm) {
                      setEditingFarm((prev) => prev ? { ...prev, totalAreaHa: area } : prev);
                    }
                  }}
                />
              </div>

              {/* احداثيات المزرعة — auto-filled from bbox + zoom */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    {isRtl ? 'خط العرض (Lat)' : 'Latitude'}
                  </label>
                  <input
                    type="text"
                    disabled
                    value={editCenterLat != null ? editCenterLat.toFixed(6) : (editingFarm?.centerLat != null ? Number(editingFarm.centerLat).toFixed(6) : '')}
                    placeholder={isRtl ? 'تلقائي' : 'Auto'}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 text-gray-600 text-sm cursor-not-allowed"
                    dir="ltr"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    {isRtl ? 'خط الطول (Lng)' : 'Longitude'}
                  </label>
                  <input
                    type="text"
                    disabled
                    value={editCenterLng != null ? editCenterLng.toFixed(6) : (editingFarm?.centerLng != null ? Number(editingFarm.centerLng).toFixed(6) : '')}
                    placeholder={isRtl ? 'تلقائي' : 'Auto'}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 text-gray-600 text-sm cursor-not-allowed"
                    dir="ltr"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    {isRtl ? 'مستوى التكبير' : 'Zoom'}
                  </label>
                  <input
                    type="text"
                    disabled
                    value={editZoom}
                    className="w-full px-3 py-2 border rounded-lg bg-gray-50 text-gray-600 text-sm cursor-not-allowed"
                    dir="ltr"
                  />
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 px-6 py-4 border-t shrink-0">
              <button
                onClick={() => { setEditingFarm(null); setEditGov(''); setEditDist(''); setEditFlyTo(null); }}
                disabled={updateFarm.isPending}
                className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isRtl ? 'إلغاء' : 'Cancel'}
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={updateFarm.isPending}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {updateFarm.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                {updateFarm.isPending ? (isRtl ? 'جاري الحفظ...' : 'Saving...') : (isRtl ? 'حفظ' : 'Save')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">إدارة المزارع</h1>
          <p className="text-gray-500 mt-1">Farm Management</p>
        </div>
        <button
          onClick={() => setShowCreateDialog(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>إضافة مزرعة</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي المزارع</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats?.totalFarms ?? farms.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">مزارع نشطة</div>
          <div className="text-2xl font-bold text-green-600">{stats?.activeFarms ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">المساحة الكلية</div>
          <div className="text-2xl font-bold text-blue-600">{stats?.totalAreaHa ?? 0} هـ</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">المساحة المزروعة</div>
          <div className="text-2xl font-bold text-sahool-green-600">
            {stats?.cultivatedAreaHa ?? 0} هـ
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي العمال</div>
          <div className="text-2xl font-bold text-purple-600">{stats?.totalWorkers ?? 0}</div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="بحث في المزارع..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
        />
      </div>

      {/* Farm Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredFarms.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">لا توجد مزارع</div>
        ) : (
          filteredFarms.map((farm) => {
            // Defensive lookup: backend Farm model may not return a status
            // field (it's a UI-only convention), so narrow at runtime and
            // fall back to 'active'. Using the narrowed key removes the
            // prior TS7053 implicit-any on the index expression.
            // استعلام آمن للحالة مع قيمة افتراضية عند عدم إرجاع الحقل من الخلفية
            const isKnownStatus =
              farm.status === 'active' ||
              farm.status === 'inactive' ||
              farm.status === 'seasonal';
            if (!isKnownStatus) {
              logger.warn('Unknown farm status, defaulting to active', {
                status: farm.status,
                farmId: farm.id,
              });
            }
            const statusKey: FarmStatus = isKnownStatus ? farm.status : 'active';
            const st = statusConfig[statusKey];
            return (
              <div
                key={farm.id}
                className="bg-white rounded-lg border hover:shadow-md transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-sahool-green-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{farm.nameAr}</h3>
                        <p className="text-sm text-gray-500">{farm.name}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${st.color}`}>
                      {st.labelAr}
                    </span>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{farm.locationAr}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Droplets className="w-4 h-4 text-blue-400" />
                      <span>{farm.waterSourceAr}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Users className="w-4 h-4 text-gray-400" />
                      <span>{farm.workersCount} عامل</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t grid grid-cols-3 gap-2 text-center">
                    <div>
                      <div className="text-lg font-bold text-gray-900">{farm.totalAreaHa}</div>
                      <div className="text-xs text-gray-500">هكتار كلي</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-sahool-green-600">
                        {farm.cultivatedAreaHa}
                      </div>
                      <div className="text-xs text-gray-500">مزروع</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-blue-600">{farm.fieldsCount}</div>
                      <div className="text-xs text-gray-500">حقل</div>
                    </div>
                  </div>
                </div>
                <div className="px-6 py-3 bg-gray-50 border-t flex justify-end">
                  <button
                    onClick={() => handleOpenEdit(farm)}
                    className="text-sahool-green-600 hover:text-sahool-green-700 text-sm font-medium"
                  >
                    تفاصيل وتعديل
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

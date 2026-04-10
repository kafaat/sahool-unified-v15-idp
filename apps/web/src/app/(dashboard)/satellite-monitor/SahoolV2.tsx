/**
 * SAHOOL V2 — Satellite Monitoring & Smart Agriculture Platform
 * المنصة الزراعية الذكية — النسخة الثانية
 *
 * يبني على المكونات الموجودة في المنصة (47 ميزة) بدلاً من إعادة بنائها.
 * كل شاشة تستورد مكوناتها من features/ و components/.
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';

// ── Existing SAHOOL Components ─────────────────────────────
// Map & Fields
import { MapView } from '@/components/dashboard/MapView';
// Weather
import { WeatherDashboard } from '@/features/weather/components/WeatherDashboard';
// Scouting
import { ScoutingMode } from '@/features/scouting/components/ScoutingMode.dynamic';
import { ScoutingHistory } from '@/features/scouting/components/ScoutingHistory';
// Tasks
import { TasksBoard } from '@/features/tasks/components/TasksBoard';
// UI Components
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// Satellite Monitor hooks
import {
  useSatelliteMonitorFields,
  useSatelliteMonitorStats,
  useSatelliteMonitorAlerts,
} from '@/features/satellite-monitor';
import { MAP_LAYERS, HYBRID_COLORS } from '@/features/satellite-monitor/api';
import type {
  MapLayerType,
} from '@/features/satellite-monitor';

// ── Screens ────────────────────────────────────────────────
const SCREENS = [
  { id: 'dash', ic: '⌂', label: 'لوحة القيادة' },
  { id: 'map', ic: '◎', label: 'الخريطة' },
  { id: 'idx', ic: '◈', label: 'طبقات المؤشرات' },
  { id: 'ts', ic: '▦', label: 'السلاسل الزمنية' },
  { id: 'rep', ic: '▤', label: 'التقارير' },
  { id: 'wx', ic: '☁', label: 'الطقس + GDD' },
  { id: 'scout', ic: '◉', label: 'المسح الميداني' },
  { id: 'ai', ic: '◇', label: 'المستشار AI' },
  { id: 'sensor', ic: '≋', label: 'المستشعرات' },
  { id: 'tasks', ic: '◻', label: 'المهام' },
  { id: 'team', ic: '◫', label: 'الفريق' },
  { id: 'files', ic: '▣', label: 'الملفات' },
  { id: 'trace', ic: '◆', label: 'تتبع المنتج' },
] as const;

type ScreenId = typeof SCREENS[number]['id'];

// ── Main Layout ────────────────────────────────────────────
export default function SahoolV2() {
  const [screen, setScreen] = useState<ScreenId>('dash');
  const [collapsed, setCollapsed] = useState(false);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  const [selectedLayer, setSelectedLayer] = useState<MapLayerType>('hybrid');

  // Data hooks
  const { data: fields = [] } = useSatelliteMonitorFields();
  const { data: stats } = useSatelliteMonitorStats();
  const { data: alerts = [] } = useSatelliteMonitorAlerts();

  const currentScreen = SCREENS.find((s) => s.id === screen)!;

  return (
    <div
      className="ar"
      style={{
        background: 'var(--bg, #04080B)',
        color: 'var(--t1, #DFF0FF)',
        minHeight: '100vh',
        direction: 'rtl',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: "'Noto Kufi Arabic', Tahoma, sans-serif",
      }}
    >
      {/* ══ HEADER ══════════════════════════════════════════ */}
      <header
        style={{
          background: 'var(--sf, #090F14)',
          borderBottom: '1px solid var(--b1, #1C3040)',
          padding: '0 20px',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, height: 56 }}>
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: 10,
              background: 'linear-gradient(135deg, #10B981, #065F46)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 20,
              flexShrink: 0,
            }}
          >
            🌾
          </div>
          <span style={{ fontSize: 18, fontWeight: 600, color: '#10B981', letterSpacing: 2, fontFamily: "'IBM Plex Mono', monospace" }}>
            SAHOOL
          </span>
          <span style={{ fontSize: 11, color: '#426A88' }}>سهول · الزراعة الذكية</span>

          <div style={{ flex: 1 }} />

          {/* Field selector chips */}
          <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
            {fields.slice(0, 5).map((f) => (
              <button
                key={f.id}
                onClick={() => setSelectedFieldId(f.id)}
                style={{
                  background: selectedFieldId === f.id ? 'rgba(16,185,129,0.12)' : 'transparent',
                  border: `1px solid ${selectedFieldId === f.id ? '#10B981' : '#1C3040'}`,
                  color: selectedFieldId === f.id ? '#10B981' : '#426A88',
                  borderRadius: 6,
                  padding: '4px 10px',
                  fontSize: 10,
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                }}
              >
                {f.nameAr}
              </button>
            ))}
          </div>

          {/* Notifications */}
          <button
            type="button"
            aria-label={`الإشعارات (${alerts.filter((a) => !a.isResolved).length} غير مقروءة)`}
            style={{ position: 'relative', cursor: 'pointer', background: 'transparent', border: 'none', padding: 4 }}
          >
            <span style={{ fontSize: 16 }}>🔔</span>
            {alerts.filter((a) => !a.isResolved).length > 0 && (
              <span
                style={{
                  position: 'absolute',
                  top: -4,
                  right: -4,
                  width: 14,
                  height: 14,
                  borderRadius: '50%',
                  background: '#EF4444',
                  color: '#fff',
                  fontSize: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 900,
                }}
              >
                {alerts.filter((a) => !a.isResolved).length}
              </span>
            )}
          </button>

          {/* Offline indicator */}
          <span
            style={{
              fontSize: 9,
              background: 'rgba(16,185,129,0.12)',
              color: '#10B981',
              border: '1px solid rgba(16,185,129,0.28)',
              padding: '2px 8px',
              borderRadius: 999,
              fontWeight: 700,
            }}
          >
            Offline ✓
          </span>
        </div>
      </header>

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* ══ SIDEBAR ═══════════════════════════════════════ */}
        <nav
          style={{
            width: collapsed ? 54 : 210,
            minWidth: collapsed ? 54 : 210,
            background: 'var(--sf, #090F14)',
            borderLeft: '1px solid var(--b1, #1C3040)',
            display: 'flex',
            flexDirection: 'column',
            transition: 'width 0.2s ease',
            overflow: 'hidden',
          }}
        >
          <div style={{ padding: 8, borderBottom: '1px solid #1C3040' }}>
            <button
              onClick={() => setCollapsed((c) => !c)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#426A88',
                cursor: 'pointer',
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: 6,
                borderRadius: 6,
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 12,
              }}
            >
              {collapsed ? '»' : '«'}
            </button>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: 8 }}>
            {SCREENS.map((s) => (
              <button
                type="button"
                key={s.id}
                onClick={() => setScreen(s.id)}
                aria-current={screen === s.id ? 'page' : undefined}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 9,
                  padding: '9px 12px',
                  borderRadius: 8,
                  cursor: 'pointer',
                  border: screen === s.id ? '1px solid rgba(16,185,129,0.25)' : '1px solid transparent',
                  background: screen === s.id ? 'rgba(16,185,129,0.1)' : 'transparent',
                  color: screen === s.id ? '#10B981' : '#426A88',
                  marginBottom: 2,
                  transition: 'all 0.16s',
                  overflow: 'hidden',
                  width: '100%',
                  fontFamily: 'inherit',
                  textAlign: 'right',
                }}
              >
                <span style={{ fontSize: 15, width: 22, textAlign: 'center', flexShrink: 0, fontFamily: "'IBM Plex Mono', monospace" }}>
                  {s.ic}
                </span>
                {!collapsed && <span style={{ fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap' }}>{s.label}</span>}
              </button>
            ))}
          </div>
        </nav>

        {/* ══ MAIN CONTENT ══════════════════════════════════ */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '18px 20px' }}>
          {/* Screen header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <span style={{ fontSize: 18, color: '#10B981', fontFamily: "'IBM Plex Mono', monospace" }}>{currentScreen.ic}</span>
            <h1 style={{ fontSize: 15, fontWeight: 900, color: '#DFF0FF' }}>{currentScreen.label}</h1>
          </div>

          {/* ── DASHBOARD ─────────────────────────────────── */}
          {screen === 'dash' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {/* KPIs */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                {[
                  { l: 'إجمالي الحقول', v: stats?.totalFields ?? fields.length, u: 'حقل', c: '#10B981' },
                  { l: 'تنبيهات نشطة', v: stats?.activeAlerts ?? alerts.filter((a) => !a.isResolved).length, u: 'تنبيه', c: '#EF4444' },
                  { l: 'متوسط NDVI', v: ((stats?.averageNdvi ?? 0) * 100).toFixed(0), u: '%', c: '#38BDF8' },
                  { l: 'المساحة المراقبة', v: stats?.totalArea?.toFixed(1) ?? '0', u: 'هـ', c: '#F59E0B' },
                ].map((x) => (
                  <Card key={x.l} variant="bordered" padding="md">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ fontSize: 26, fontWeight: 900, color: x.c, lineHeight: 1 }}>
                          {x.v}
                          <span style={{ fontSize: 11, fontWeight: 400, color: '#426A88', marginRight: 3 }}>{x.u}</span>
                        </div>
                        <div style={{ fontSize: 10, color: '#426A88', marginTop: 4 }}>{x.l}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Field list */}
              <Card variant="bordered">
                <div style={{ padding: '12px 16px', borderBottom: '1px solid #1C3040', display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 13, fontWeight: 800 }}>◎ حقولي</span>
                  <Button size="sm" onClick={() => setScreen('map')}>الخريطة</Button>
                </div>
                {fields.map((f) => (
                  <div
                    key={f.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '8px 14px',
                      borderBottom: '1px solid #1C3040',
                      fontSize: 11,
                      cursor: 'pointer',
                    }}
                    onClick={() => setSelectedFieldId(f.id)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          background: f.healthStatus === 'healthy' ? '#10B981' : f.healthStatus === 'moderate' ? '#F59E0B' : '#EF4444',
                        }}
                      />
                      <div>
                        <div style={{ fontWeight: 700, color: '#DFF0FF' }}>{f.nameAr}</div>
                        <div style={{ fontSize: 9, color: '#426A88' }}>{f.cropTypeAr} · {f.area} هـ</div>
                      </div>
                    </div>
                    <span style={{ fontWeight: 700, color: f.ndvi >= 0.6 ? '#10B981' : f.ndvi >= 0.4 ? '#F59E0B' : '#EF4444' }}>
                      {Math.round(f.ndvi * 100)}%
                    </span>
                  </div>
                ))}
              </Card>

              {/* Hybrid legend */}
              <Card variant="bordered" padding="md">
                <div style={{ fontSize: 12, fontWeight: 800, marginBottom: 12 }}>مقياس Hybrid — 5 ألوان للمزارع البسيط</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
                  {HYBRID_COLORS.map((h) => (
                    <div key={h.meaningAr} style={{ textAlign: 'center' }}>
                      <div style={{ height: 28, background: h.hex, borderRadius: 6, marginBottom: 6 }} />
                      <div style={{ fontSize: 9, color: '#82B8D4', lineHeight: 1.4 }}>{h.meaningAr}</div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* ── MAP (uses existing MapView) ────────────────── */}
          {screen === 'map' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                {['hybrid', 'ndvi', 'ndre', 'ndwi', 'soc', 'dem', 'sar_rvi'].map((layer) => {
                  const cfg = MAP_LAYERS.find((l) => l.type === layer);
                  return (
                    <button
                      key={layer}
                      onClick={() => setSelectedLayer(layer as MapLayerType)}
                      style={{
                        padding: '4px 11px',
                        borderRadius: 6,
                        fontSize: 10,
                        fontWeight: 700,
                        cursor: 'pointer',
                        border: selectedLayer === layer ? '1px solid rgba(16,185,129,0.35)' : '1px solid #1C3040',
                        color: selectedLayer === layer ? '#10B981' : '#426A88',
                        background: selectedLayer === layer ? 'rgba(16,185,129,0.14)' : '#131F28',
                        fontFamily: "'IBM Plex Mono', monospace",
                      }}
                    >
                      {cfg?.labelAr ?? layer}
                    </button>
                  );
                })}
              </div>
              <Card variant="bordered" style={{ height: 'calc(100vh - 250px)', overflow: 'hidden' }}>
                <MapView
                  onFieldSelect={(id) => setSelectedFieldId(id)}
                  fields={fields.map((f) => {
                    const coords = (f.boundary ?? []).map(
                      (pt) => [pt.lng, pt.lat] as [number, number],
                    );
                    if (coords.length > 0) {
                      coords.push(coords[0]!);
                    }
                    return {
                      ...f,
                      crop_type: f.cropType,
                      ndvi_current: f.ndvi,
                      name_ar: f.nameAr,
                      area_hectares: f.area,
                      boundary: {
                        type: 'Polygon' as const,
                        coordinates: [coords],
                      },
                    };
                  }) as never[]}
                />
              </Card>
            </div>
          )}

          {/* ── WEATHER (uses existing WeatherDashboard) ──── */}
          {screen === 'wx' && (
            <WeatherDashboard lat={15.37} lon={44.19} enabled />
          )}

          {/* ── SCOUTING (uses existing components) ──────── */}
          {screen === 'scout' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <Card variant="bordered" padding="md">
                <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12 }}>◉ مسح ميداني جديد</div>
                {selectedFieldId ? (
                  <ScoutingMode fieldId={selectedFieldId} />
                ) : (
                  <div style={{ textAlign: 'center', padding: 24, color: '#426A88' }}>
                    اختر حقلاً من الشريط العلوي لبدء المسح الميداني
                  </div>
                )}
              </Card>
              <Card variant="bordered" padding="md">
                <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12 }}>سجل المسح السابق</div>
                <ScoutingHistory />
              </Card>
            </div>
          )}

          {/* ── TASKS (uses existing TasksBoard) ──────────── */}
          {screen === 'tasks' && (
            <TasksBoard onTaskClick={(_id) => {}} />
          )}

          {/* ── FILES ─────────────────────────────────────── */}
          {screen === 'files' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <Card variant="bordered" padding="md">
                <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12 }}>▣ مدير الملفات</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
                  {[
                    { icon: '📄', label: 'تقارير PDF', count: 12, color: '#EF4444' },
                    { icon: '🗺️', label: 'KML / Shapefile', count: 4, color: '#8B5CF6' },
                    { icon: '📸', label: 'صور الحقل', count: 28, color: '#10B981' },
                    { icon: '📊', label: 'تصدير البيانات', count: 8, color: '#38BDF8' },
                  ].map((cat) => (
                    <div
                      key={cat.label}
                      style={{
                        background: '#131F28',
                        border: '1px solid #1C3040',
                        borderRadius: 10,
                        padding: 16,
                        textAlign: 'center',
                        cursor: 'pointer',
                      }}
                    >
                      <div style={{ fontSize: 28, marginBottom: 8 }}>{cat.icon}</div>
                      <div style={{ fontSize: 11, fontWeight: 700, color: '#DFF0FF' }}>{cat.label}</div>
                      <div style={{ fontSize: 20, fontWeight: 900, color: cat.color, marginTop: 4 }}>{cat.count}</div>
                    </div>
                  ))}
                </div>
              </Card>
              {/* Upload zone */}
              <label style={{ display: 'block' }}>
              <Card
                variant="bordered"
                padding="lg"
                style={{
                  border: '2px dashed #1C3040',
                  textAlign: 'center',
                  cursor: 'pointer',
                }}
              >
                <input
                  type="file"
                  accept=".kml,.shp,.geojson,.json,.pdf,.csv,.jpg,.png"
                  multiple
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    // Basic client-side validation: reject empty selection,
                    // enforce 50MB per-file limit (matches backend upload
                    // limits across file ingestion endpoints). Real upload
                    // wiring is handled by the feature-specific mutation
                    // elsewhere — this is a catalog placeholder.
                    const files = Array.from(e.target.files ?? []);
                    if (files.length === 0) return;
                    const MAX_BYTES = 50 * 1024 * 1024;
                    const oversize = files.find((f) => f.size > MAX_BYTES);
                    if (oversize) {
                      // eslint-disable-next-line no-alert
                      alert(`الملف "${oversize.name}" يتجاوز الحد الأقصى 50 ميجابايت`);
                      e.target.value = '';
                      return;
                    }
                    // Reset the input so re-selecting the same file fires onChange.
                    e.target.value = '';
                  }}
                />
                <div style={{ fontSize: 32, marginBottom: 8, color: '#426A88' }}>📁</div>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#82B8D4' }}>اسحب ملفاتك هنا أو انقر للرفع</div>
                <div style={{ fontSize: 9, color: '#426A88', marginTop: 4 }}>
                  KML, Shapefile, GeoJSON, PDF, CSV, صور (حتى 50MB)
                </div>
              </Card>
              </label>
            </div>
          )}

          {/* ── TRACE (Product Traceability) ──────────────── */}
          {screen === 'trace' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                {/* QR Code */}
                <Card variant="bordered" padding="md">
                  <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12 }}>◆ QR Code المنتج</div>
                  <div
                    style={{
                      width: 160,
                      height: 160,
                      background: '#fff',
                      borderRadius: 12,
                      margin: '0 auto 12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 80,
                    }}
                  >
                    📱
                  </div>
                  <div style={{ textAlign: 'center', fontSize: 10, color: '#426A88' }}>
                    امسح لعرض رحلة المنتج من المزرعة للمستهلك
                  </div>
                  <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 12 }}>
                    <Button size="sm">توليد QR</Button>
                    <Button size="sm" variant="outline">طباعة</Button>
                  </div>
                </Card>

                {/* Blockchain Timeline */}
                <Card variant="bordered" padding="md">
                  <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12 }}>سلسلة التتبع — Blockchain</div>
                  {[
                    { step: 'المزرعة', icon: '🌾', date: '15 مارس 2026', status: 'done', hash: '0xA3F...' },
                    { step: 'المعالجة', icon: '⚙️', date: '18 مارس 2026', status: 'done', hash: '0xB7C...' },
                    { step: 'النقل', icon: '🚛', date: '20 مارس 2026', status: 'active', hash: '—' },
                    { step: 'السوق', icon: '🏪', date: '—', status: 'pending', hash: '—' },
                  ].map((s, i) => (
                    <div
                      key={s.step}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 12,
                        padding: '10px 0',
                        borderBottom: i < 3 ? '1px solid #1C3040' : 'none',
                      }}
                    >
                      <div
                        style={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          background: s.status === 'done' ? 'rgba(16,185,129,0.15)' : s.status === 'active' ? 'rgba(245,158,11,0.15)' : 'rgba(66,106,136,0.1)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 16,
                          flexShrink: 0,
                        }}
                      >
                        {s.icon}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 11, fontWeight: 700, color: s.status === 'pending' ? '#426A88' : '#DFF0FF' }}>{s.step}</div>
                        <div style={{ fontSize: 9, color: '#426A88' }}>{s.date}</div>
                      </div>
                      <span
                        style={{
                          fontSize: 8,
                          fontFamily: "'IBM Plex Mono', monospace",
                          color: s.status === 'done' ? '#10B981' : '#426A88',
                        }}
                      >
                        {s.hash}
                      </span>
                    </div>
                  ))}
                </Card>
              </div>

              {/* Certificates */}
              <Card variant="bordered" padding="md">
                <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 12 }}>الشهادات والامتثال</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                  {[
                    { name: 'GlobalGAP IFA v6', status: 'active', exp: '2026-12-31', color: '#10B981' },
                    { name: 'عضوي — IFOAM', status: 'pending', exp: '—', color: '#F59E0B' },
                    { name: 'FSMA 204', status: 'active', exp: '2027-06-30', color: '#38BDF8' },
                  ].map((cert) => (
                    <div
                      key={cert.name}
                      style={{
                        background: '#131F28',
                        border: `1px solid ${cert.color}40`,
                        borderRight: `3px solid ${cert.color}`,
                        borderRadius: 8,
                        padding: 12,
                      }}
                    >
                      <div style={{ fontSize: 11, fontWeight: 700, color: '#DFF0FF' }}>{cert.name}</div>
                      <div style={{ fontSize: 9, color: '#426A88', marginTop: 4 }}>انتهاء: {cert.exp}</div>
                      <span
                        style={{
                          fontSize: 8,
                          fontWeight: 700,
                          color: cert.color,
                          background: `${cert.color}15`,
                          border: `1px solid ${cert.color}40`,
                          padding: '1px 6px',
                          borderRadius: 999,
                          marginTop: 6,
                          display: 'inline-block',
                        }}
                      >
                        {cert.status === 'active' ? 'فعّال' : 'قيد المراجعة'}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* ── AI CHAT (links to /copilot) ──────────────── */}
          {screen === 'ai' && (
            <Card variant="bordered" padding="lg" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>◇</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: '#10B981', marginBottom: 8 }}>المستشار الزراعي</div>
              <div style={{ fontSize: 11, color: '#82B8D4', marginBottom: 16, lineHeight: 2 }}>
                12 وكيل AI متخصص · Tri-RAG · 91+ ملف معرفي زراعي عربي
                <br />
                متصل بـ copilot-api:8088 عبر IntentClassifier + IntentRouter
              </div>
              <Link href="/copilot">
                <Button size="lg">فتح المحادثة</Button>
              </Link>
            </Card>
          )}

          {/* ── Placeholder for other screens ─────────────── */}
          {['idx', 'ts', 'rep', 'sensor', 'team'].includes(screen) && (
            <Card variant="bordered" padding="lg" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 36, color: '#10B981', marginBottom: 12, fontFamily: "'IBM Plex Mono', monospace" }}>
                {currentScreen.ic}
              </div>
              <div style={{ fontSize: 16, fontWeight: 800, marginBottom: 8 }}>{currentScreen.label}</div>
              <div style={{ fontSize: 11, color: '#426A88' }}>
                يستخدم المكونات الموجودة في المنصة — جاري التكامل
              </div>
            </Card>
          )}
        </main>
      </div>

      {/* ══ FOOTER ══════════════════════════════════════════ */}
      <footer
        style={{
          background: 'var(--sf, #090F14)',
          borderTop: '1px solid var(--b1, #1C3040)',
          padding: '5px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', gap: 14 }}>
          {[
            { l: 'الموسم', v: 'ربيع 2026' },
            { l: 'الأقمار', v: 'Sentinel-2' },
            { l: 'API', v: 'copilot-api:8088' },
          ].map((x) => (
            <div key={x.l} style={{ display: 'flex', gap: 4, fontSize: 8 }}>
              <span style={{ color: '#1A3550' }}>{x.l}:</span>
              <span style={{ color: '#10B981', fontWeight: 600, fontFamily: "'IBM Plex Mono', monospace" }}>{x.v}</span>
            </div>
          ))}
        </div>
        <div style={{ fontSize: 7, color: '#1A3550', fontFamily: "'IBM Plex Mono', monospace" }}>
          SAHOOL v16 · PostGIS · NATS JetStream · 12 AI Agents · Offline-First
        </div>
      </footer>
    </div>
  );
}

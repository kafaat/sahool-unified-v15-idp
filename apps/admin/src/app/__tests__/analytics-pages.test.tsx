/**
 * Analytics Pages - File Structure & Content Verification Tests
 * اختبارات صفحات التحليلات - التحقق من بنية الملفات والمحتوى
 *
 * Tests: profitability, satellite, yield, soil, gap-analysis, field-compare
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const APP_DIR = path.resolve(__dirname, '..');

function readPage(relativePath: string): string {
  const filePath = path.resolve(APP_DIR, relativePath);
  expect(fs.existsSync(filePath), `File not found: ${relativePath}`).toBe(true);
  return fs.readFileSync(filePath, 'utf-8');
}

// ─── Profitability Analytics ─────────────────────────────────────────────────

describe('Analytics: Profitability Page', () => {
  const PAGE_PATH = 'analytics/profitability/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function\s+ProfitabilityPage/);
  });

  it('contains Arabic labels for profitability', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تحليل الربحية');
    expect(content).toContain('إجمالي الإيرادات');
    expect(content).toContain('صافي الربح');
    expect(content).toContain('هامش الربح');
    expect(content).toContain('عائد الاستثمار');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain("from '@/lib/api/analytics'");
    expect(content).toContain('fetchProfitabilityData');
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('DollarSign');
    expect(content).toContain('TrendingUp');
    expect(content).toContain('TrendingDown');
  });

  it('imports dynamic chart components', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('DynamicMonthlyTrendChart');
    expect(content).toContain('DynamicCropProfitabilityChart');
    expect(content).toContain('DynamicCostBreakdownChart');
  });

  it('defines ProfitabilityData interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface ProfitabilityData');
    expect(content).toContain('totalRevenue');
    expect(content).toContain('netProfit');
    expect(content).toContain('profitMargin');
  });

  it('has period selector (month/quarter/year)', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('selectedPeriod');
    expect(content).toContain('شهري');
    expect(content).toContain('ربع سنوي');
    expect(content).toContain('سنوي');
  });

  it('includes crop details table with Arabic headers', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('المحصول');
    expect(content).toContain('المساحة');
    expect(content).toContain('الإيرادات');
    expect(content).toContain('التكاليف');
  });

  it('includes season summary section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('ملخص الموسم');
    expect(content).toContain('seasonAr');
  });
});

// ─── Satellite Analytics ─────────────────────────────────────────────────────

describe('Analytics: Satellite Page', () => {
  const PAGE_PATH = 'analytics/satellite/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function\s+SatellitePage/);
  });

  it('contains Arabic labels for satellite data', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تحليلات البيانات الفضائية');
    expect(content).toContain('إجمالي الحقول');
    expect(content).toContain('التغطية');
    expect(content).toContain('تنبيهات حرجة');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain('fetchSatelliteData');
  });

  it('uses dynamic import for SatelliteMap', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("dynamic(() => import('@/components/maps/SatelliteMap')");
    expect(content).toContain('ssr: false');
  });

  it('defines INDEX_OPTIONS with vegetation indices', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('INDEX_OPTIONS');
    expect(content).toContain('ndvi');
    expect(content).toContain('ndwi');
    expect(content).toContain('savi');
    expect(content).toContain('مؤشر الغطاء النباتي');
  });

  it('has NDVI helper functions', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('getNDVIColor');
    expect(content).toContain('getNDVILabel');
    expect(content).toContain('ممتاز');
    expect(content).toContain('حرج');
  });

  it('defines SatelliteData interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface SatelliteData');
    expect(content).toContain('totalFields');
    expect(content).toContain('ndviTrends');
  });

  it('has date range selector', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('dateRange');
    expect(content).toContain('أسبوع');
    expect(content).toContain('شهر');
    expect(content).toContain('موسم');
  });

  it('includes NDVI trend chart', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('NDVITrendChart');
    expect(content).toContain('اتجاه NDVI');
  });

  it('displays field details panel', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تفاصيل الحقل');
    expect(content).toContain('NDVI الحالي');
    expect(content).toContain('هكتار');
  });
});

// ─── Yield Analytics ─────────────────────────────────────────────────────────

describe('Analytics: Yield Page', () => {
  const PAGE_PATH = 'analytics/yield/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function\s+YieldAnalysisPage/);
  });

  it('contains Arabic labels for yield analysis', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تحليل الغلة العميق');
    expect(content).toContain('عدد الحقول');
    expect(content).toContain('المساحة الكلية');
    expect(content).toContain('إجمالي الغلة');
    expect(content).toContain('متوسط الغلة');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/lib/api'");
    expect(content).toContain("from '@/lib/logger'");
    expect(content).toContain('BarChart3');
    expect(content).toContain('TrendingUp');
  });

  it('defines FieldYield interface with Arabic fields', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface FieldYield');
    expect(content).toContain('field_name_ar');
    expect(content).toContain('crop_name_ar');
    expect(content).toContain('yield_ton_per_ha');
  });

  it('includes mock data with Yemeni farms', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('MOCK_FIELDS');
    expect(content).toContain('مزرعة الرشيد');
    expect(content).toContain('صنعاء');
    expect(content).toContain('حقل القمح الشمالي');
  });

  it('has comparison dimensions', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('DIMENSIONS');
    expect(content).toContain('المحصول');
    expect(content).toContain('نوع التربة');
    expect(content).toContain('نوع الري');
    expect(content).toContain('المحافظة');
  });

  it('has season trends section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('MOCK_TRENDS');
    expect(content).toContain('اتجاه الغلة عبر المواسم');
  });

  it('has detailed fields table', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('بيانات الحقول التفصيلية');
    expect(content).toContain('الغلة (طن/هك)');
    expect(content).toContain('NDVI');
  });
});

// ─── Soil Analytics ──────────────────────────────────────────────────────────

describe('Analytics: Soil Page', () => {
  const PAGE_PATH = 'analytics/soil/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function\s+SoilMonitoringPage/);
  });

  it('contains Arabic labels for soil monitoring', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('مراقبة تغذية التربة');
    expect(content).toContain('إجمالي الاختبارات');
    expect(content).toContain('متوسط pH');
    expect(content).toContain('ملوحة عالية');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/lib/api'");
    expect(content).toContain("from '@/config/api'");
    expect(content).toContain('AlertTriangle');
    expect(content).toContain('Droplets');
  });

  it('defines SoilTest interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface SoilTest');
    expect(content).toContain('nitrogen_ppm');
    expect(content).toContain('phosphorus_ppm');
    expect(content).toContain('potassium_ppm');
    expect(content).toContain('salinity_level');
  });

  it('defines NUTRIENT_THRESHOLDS with NPK and more', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('NUTRIENT_THRESHOLDS');
    expect(content).toContain('النيتروجين (N)');
    expect(content).toContain('الفوسفور (P)');
    expect(content).toContain('البوتاسيوم (K)');
  });

  it('has nutrient status helper function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('getNutrientStatus');
    expect(content).toContain('مثالي');
    expect(content).toContain('ناقص');
    expect(content).toContain('مفرط');
  });

  it('includes mock soil test data', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('MOCK_TESTS');
    expect(content).toContain('حقل القمح الشمالي');
    expect(content).toContain('طينية');
  });

  it('has salinity labels in Arabic', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('SALINITY_LABELS');
    expect(content).toContain('منخفضة');
    expect(content).toContain('متوسطة');
    expect(content).toContain('مرتفعة');
    expect(content).toContain('حرجة');
  });

  it('includes recommendations section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('التوصيات');
    expect(content).toContain('recommendations_ar');
  });

  it('has filter by status', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('filterStatus');
    expect(content).toContain('كل الحالات');
  });
});

// ─── Gap Analysis ────────────────────────────────────────────────────────────

describe('Analytics: Gap Analysis Page', () => {
  const PAGE_PATH = 'analytics/gap-analysis/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function/);
  });

  it('contains Arabic labels for gap analysis', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تحليل الفجوات');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain("from '@/lib/utils'");
  });

  it('imports lucide-react icons for feature status', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('CheckCircle2');
    expect(content).toContain('XCircle');
    expect(content).toContain('Trophy');
  });

  it('defines FeatureStatus type', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("type FeatureStatus = 'full' | 'partial' | 'gap' | 'advantage'");
  });

  it('defines FeatureItem interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface FeatureItem');
    expect(content).toContain('status: FeatureStatus');
  });

  it('defines FeatureCategory interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface FeatureCategory');
  });
});

// ─── Field Compare ───────────────────────────────────────────────────────────

describe('Analytics: Field Compare Page', () => {
  const PAGE_PATH = 'analytics/field-compare/page.tsx';
  let content: string;

  it('file exists', () => {
    content = readPage(PAGE_PATH);
    expect(content.length).toBeGreaterThan(0);
  });

  it('is a client component', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("'use client'");
  });

  it('exports a default function', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toMatch(/export\s+default\s+function\s+FieldComparePage/);
  });

  it('contains Arabic labels for field comparison', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('مقارنة الحقول المتقدمة');
    expect(content).toContain('الحقل الأول');
    expect(content).toContain('الحقل الثاني');
    expect(content).toContain('مقارنة المؤشرات');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/lib/api'");
    expect(content).toContain("from '@/config/api'");
  });

  it('imports comparison-related icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('ArrowLeftRight');
    expect(content).toContain('Leaf');
    expect(content).toContain('Droplets');
    expect(content).toContain('Thermometer');
    expect(content).toContain('BarChart3');
  });

  it('defines FieldMetrics interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface FieldMetrics');
    expect(content).toContain('ndvi');
    expect(content).toContain('soilMoisture');
    expect(content).toContain('yieldEstimate');
    expect(content).toContain('diseaseRisk');
    expect(content).toContain('overallHealth');
  });

  it('includes mock field data', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('MOCK_FIELDS');
    expect(content).toContain('حقل القمح الشمالي');
    expect(content).toContain('حقل الطماطم');
  });

  it('has helper functions for risk and health display', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('getRiskColor');
    expect(content).toContain('getRiskLabel');
    expect(content).toContain('getHealthColor');
    expect(content).toContain('getHealthLabel');
    expect(content).toContain('منخفض');
    expect(content).toContain('متوسط');
    expect(content).toContain('مرتفع');
  });

  it('has swap fields functionality', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('swapFields');
    expect(content).toContain('تبديل الحقول');
  });

  it('includes comparison sections with Arabic headers', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('مؤشرات الغطاء النباتي');
    expect(content).toContain('التربة والمغذيات');
    expect(content).toContain('المناخ والري');
    expect(content).toContain('الإنتاجية والتكلفة');
    expect(content).toContain('المخاطر');
  });

  it('has key insights section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('الملاحظات الرئيسية');
    expect(content).toContain('فرق NDVI ملحوظ');
    expect(content).toContain('فجوة الإنتاجية');
  });

  it('has compareValue helper', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('function compareValue');
  });
});

/**
 * Precision Agriculture Pages - File Structure & Content Verification Tests
 * اختبارات صفحات الزراعة الدقيقة - التحقق من بنية الملفات والمحتوى
 *
 * Tests: fertilizer, gdd, pivot, spray, vra
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

// ─── Fertilizer Prescription Page ─────────────────────────────────────────────

describe('Precision Agriculture: Fertilizer Page', () => {
  const PAGE_PATH = 'precision-agriculture/fertilizer/page.tsx';
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
    expect(content).toMatch(/export\s+default\s+function\s+FertilizerPrescriptionPage/);
  });

  it('contains Arabic labels for fertilizer management', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('وصفات التسميد المتغير');
    expect(content).toContain('إجمالي الوصفات');
    expect(content).toContain('المناطق');
    expect(content).toContain('المساحة الكلية');
    expect(content).toContain('التكلفة الإجمالية');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain("from '@/components/ui/StatusBadge'");
    expect(content).toContain("from '@/lib/api'");
    expect(content).toContain("from '@/config/api'");
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('FlaskConical');
    expect(content).toContain('MapPin');
    expect(content).toContain('Layers');
    expect(content).toContain('Leaf');
    expect(content).toContain('Zap');
  });

  it('defines NutrientLevel interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface NutrientLevel');
    expect(content).toContain('current: number');
    expect(content).toContain('target: number');
    expect(content).toContain("status: 'deficient' | 'low' | 'optimal' | 'high' | 'excessive'");
  });

  it('defines ZonePrescription interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface ZonePrescription');
    expect(content).toContain('nitrogen: NutrientLevel');
    expect(content).toContain('phosphorus: NutrientLevel');
    expect(content).toContain('potassium: NutrientLevel');
    expect(content).toContain('applicationRate');
  });

  it('defines FertilizerPrescription interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface FertilizerPrescription');
    expect(content).toContain('zones: ZonePrescription[]');
    expect(content).toContain("status: 'draft' | 'reviewed' | 'approved' | 'applied'");
  });

  it('defines FertilizerProduct interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface FertilizerProduct');
    expect(content).toContain('nContent');
    expect(content).toContain('pContent');
    expect(content).toContain('kContent');
  });

  it('includes mock fertilizer products', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('MOCK_PRODUCTS');
    expect(content).toContain('يوريا 46%');
    expect(content).toContain('داب 18-46-0');
    expect(content).toContain('سماد مركب 20-20-20');
  });

  it('includes mock prescriptions with zones', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('MOCK_PRESCRIPTIONS');
    expect(content).toContain('المنطقة الشمالية');
    expect(content).toContain('المنطقة الوسطى');
    expect(content).toContain('المنطقة الجنوبية');
  });

  it('has high priority zone alert', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('أولوية عالية تحتاج تسميد عاجل');
  });
});

// ─── GDD (Growing Degree Days) Page ──────────────────────────────────────────

describe('Precision Agriculture: GDD Page', () => {
  const PAGE_PATH = 'precision-agriculture/gdd/page.tsx';
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
    expect(content).toMatch(/export\s+default\s+function\s+GDDPage/);
  });

  it('contains Arabic labels for GDD monitoring', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('مراقبة درجات النمو الحرارية');
    expect(content).toContain('إجمالي الحقول');
    expect(content).toContain('قيد المراقبة');
    expect(content).toContain('تنبيهات حرجة');
    expect(content).toContain('قرب الانتقال');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain('fetchGDDData');
    expect(content).toContain("from '@/lib/api/precision'");
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('Thermometer');
    expect(content).toContain('Sprout');
    expect(content).toContain('AlertTriangle');
    expect(content).toContain('TrendingUp');
    expect(content).toContain('Calendar');
  });

  it('imports dynamic chart components', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('DynamicGDDStageDistributionChart');
    expect(content).toContain('DynamicGDDHistoryChart');
  });

  it('defines GDDField interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface GDDField');
    expect(content).toContain('currentGDD');
    expect(content).toContain('targetGDD');
    expect(content).toContain('currentStageAr');
    expect(content).toContain('nextStageAr');
    expect(content).toContain('daysToNextStage');
    expect(content).toContain('gddToNextStage');
  });

  it('has stage distribution section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('توزيع مراحل النمو');
    expect(content).toContain('stageDistribution');
  });

  it('has GDD history section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تاريخ GDD');
  });

  it('displays current and next stage info', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('المرحلة الحالية');
    expect(content).toContain('المرحلة القادمة');
    expect(content).toContain('يوم متبقي');
    expect(content).toContain('GDD متبقي');
  });

  it('has GDD progress bar', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('تقدم GDD');
  });
});

// ─── Pivot Irrigation Page ──────────────────────────────────────────────────

describe('Precision Agriculture: Pivot Page', () => {
  const PAGE_PATH = 'precision-agriculture/pivot/page.tsx';
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
    expect(content).toMatch(/export\s+default\s+function\s+PivotIrrigationPage/);
  });

  it('contains Arabic labels for pivot management', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('الري المحوري');
    expect(content).toContain('إجمالي المحاور');
    expect(content).toContain('محاور نشطة');
    expect(content).toContain('استهلاك اليوم');
    expect(content).toContain('توفير المياه');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain("from '@/lib/utils'");
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('Droplets');
    expect(content).toContain('Play');
    expect(content).toContain('Pause');
    expect(content).toContain('RotateCw');
    expect(content).toContain('Settings');
    expect(content).toContain('Grid3X3');
  });

  it('defines PivotSystem interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface PivotSystem');
    expect(content).toContain("status: 'running' | 'stopped' | 'maintenance' | 'scheduled'");
    expect(content).toContain('current_angle');
    expect(content).toContain('vri_zones_count');
    expect(content).toContain('efficiency_percent');
  });

  it('defines PivotStatistics interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface PivotStatistics');
    expect(content).toContain('total_pivots');
    expect(content).toContain('water_savings_percent');
  });

  it('has status labels in Arabic', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('STATUS_LABELS');
    expect(content).toContain('يعمل');
    expect(content).toContain('متوقف');
    expect(content).toContain('صيانة');
    expect(content).toContain('مجدول');
  });

  it('includes mock pivot data', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('generateMockPivots');
    expect(content).toContain('المحوري الرئيسي - الشمال');
    expect(content).toContain('محوري الحقل الشرقي');
  });

  it('has PivotVisualization component with SVG', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('function PivotVisualization');
    expect(content).toContain('<svg viewBox');
    expect(content).toContain('animateTransform');
  });

  it('has control panel with action buttons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('لوحة التحكم');
    expect(content).toContain('إيقاف');
    expect(content).toContain('تشغيل');
    expect(content).toContain('عكس الاتجاه');
    expect(content).toContain('الإعدادات');
  });

  it('has VRI zones and sectors sections', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('القطاعات ومناطق VRI');
    expect(content).toContain('الأبراج');
    expect(content).toContain('القطاعات');
    expect(content).toContain('مناطق VRI');
  });

  it('has recent activity section', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('النشاط الأخير');
    expect(content).toContain('بدأ دورة الري');
    expect(content).toContain('تحديث خريطة VRI');
  });
});

// ─── Spray Management Page ──────────────────────────────────────────────────

describe('Precision Agriculture: Spray Page', () => {
  const PAGE_PATH = 'precision-agriculture/spray/page.tsx';
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
    expect(content).toMatch(/export\s+default\s+function\s+SprayPage/);
  });

  it('contains Arabic labels for spray management', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('إدارة الرش الذكي');
    expect(content).toContain('نوافذ قادمة');
    expect(content).toContain('مثالي الآن');
    expect(content).toContain('تم الإكمال');
    expect(content).toContain('التكلفة الإجمالية');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain('fetchSprayWindows');
    expect(content).toContain('fetchSprayHistory');
    expect(content).toContain("from '@/lib/api/precision'");
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('Droplet');
    expect(content).toContain('Wind');
    expect(content).toContain('CheckCircle');
    expect(content).toContain('Clock');
    expect(content).toContain('Sun');
  });

  it('imports dynamic chart components', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('DynamicProductUsageChart');
    expect(content).toContain('DynamicCostDistributionChart');
  });

  it('defines SprayWindow interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface SprayWindow');
    expect(content).toContain("productType: 'pesticide' | 'herbicide' | 'fungicide' | 'fertilizer'");
    expect(content).toContain("status: 'upcoming' | 'optimal' | 'missed' | 'completed'");
    expect(content).toContain('recommendationsAr');
  });

  it('defines SprayHistory interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface SprayHistory');
    expect(content).toContain('effectiveness');
    expect(content).toContain('quantity');
    expect(content).toContain('cost');
  });

  it('has product type labels in Arabic', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('مبيدات حشرية');
    expect(content).toContain('مبيدات أعشاب');
    expect(content).toContain('مبيدات فطرية');
    expect(content).toContain('أسمدة');
  });

  it('has status labels in Arabic', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('getStatusLabel');
    expect(content).toContain('قادم');
    expect(content).toContain('مثالي الآن');
    expect(content).toContain('فات الموعد');
    expect(content).toContain('مكتمل');
  });

  it('has tabs for windows and history', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('activeTab');
    expect(content).toContain('نوافذ الرش القادمة');
    expect(content).toContain('سجل الرش');
  });

  it('has history table with Arabic headers', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('المزرعة / الحقل');
    expect(content).toContain('المنتج');
    expect(content).toContain('المساحة');
    expect(content).toContain('الكمية');
    expect(content).toContain('التكلفة');
    expect(content).toContain('الفعالية');
  });
});

// ─── VRA (Variable Rate Application) Page ────────────────────────────────────

describe('Precision Agriculture: VRA Page', () => {
  const PAGE_PATH = 'precision-agriculture/vra/page.tsx';
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
    expect(content).toMatch(/export\s+default\s+function\s+VRAPage/);
  });

  it('contains Arabic labels for VRA management', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('إدارة التطبيق المتغير (VRA)');
    expect(content).toContain('إجمالي الوصفات');
    expect(content).toContain('قيد المراجعة');
    expect(content).toContain('تمت الموافقة');
    expect(content).toContain('تم التطبيق');
  });

  it('imports key dependencies', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from '@/components/layout/Header'");
    expect(content).toContain("from '@/components/ui/StatCard'");
    expect(content).toContain("from '@/components/ui/StatusBadge'");
    expect(content).toContain('fetchVRAPrescriptions');
    expect(content).toContain('approvePrescription');
    expect(content).toContain('rejectPrescription');
    expect(content).toContain("from '@/lib/api/precision'");
  });

  it('imports lucide-react icons', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('FileText');
    expect(content).toContain('CheckCircle');
    expect(content).toContain('XCircle');
    expect(content).toContain('Clock');
    expect(content).toContain('Filter');
    expect(content).toContain('Download');
  });

  it('imports next/link for navigation', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain("from 'next/link'");
  });

  it('defines VRAPrescription interface', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('interface VRAPrescription');
    expect(content).toContain("prescriptionType: 'fertilizer' | 'pesticide' | 'irrigation'");
    expect(content).toContain("status: 'pending' | 'approved' | 'rejected' | 'applied'");
    expect(content).toContain('zones');
    expect(content).toContain('totalCost');
  });

  it('has prescription type labels in Arabic', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('getPrescriptionTypeLabel');
    expect(content).toContain('سماد');
    expect(content).toContain('مبيد');
    expect(content).toContain('ري');
  });

  it('has filter controls', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('selectedStatus');
    expect(content).toContain('selectedType');
    expect(content).toContain('جميع الحالات');
    expect(content).toContain('جميع الأنواع');
  });

  it('has prescriptions table with Arabic headers', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('المزرعة / الحقل');
    expect(content).toContain('النوع');
    expect(content).toContain('المساحة');
    expect(content).toContain('المناطق');
    expect(content).toContain('التكلفة');
    expect(content).toContain('الحالة');
    expect(content).toContain('إجراءات');
  });

  it('has approve and reject handlers', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('handleApprove');
    expect(content).toContain('handleReject');
  });

  it('links to prescription detail page', () => {
    content = content || readPage(PAGE_PATH);
    expect(content).toContain('/precision-agriculture/vra/');
    expect(content).toContain('عرض التفاصيل');
  });
});

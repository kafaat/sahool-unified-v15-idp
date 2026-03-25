/**
 * Core Pages Tests - Irrigation, Weather, Tasks, Equipment, Sensors, Inventory
 * اختبارات الصفحات الأساسية - الري، الطقس، المهام، المعدات، المستشعرات، المخزون
 *
 * Verifies page file existence, structure, directives, imports, and Arabic labels.
 * Uses filesystem checks to avoid server-side module issues with 'use client' pages.
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const APP_DIR = path.resolve(__dirname, '..');

/**
 * Validate that a resolved path stays within the base directory.
 * Prevents path traversal (e.g., via "../" segments).
 */
function safePath(base: string, relative: string): string {
  const resolved = path.resolve(base, relative);
  if (!resolved.startsWith(base + path.sep) && resolved !== base) {
    throw new Error(`Path traversal detected: ${relative}`);
  }
  return resolved;
}

/**
 * Read page file content with existence check.
 * Returns the file content string or null if file not found.
 */
function readPageFile(relativePath: string): { content: string; filePath: string } | null {
  const tsxPath = safePath(APP_DIR, relativePath + '.tsx');
  const tsPath = safePath(APP_DIR, relativePath + '.ts');

  const filePath = fs.existsSync(tsxPath) ? tsxPath : fs.existsSync(tsPath) ? tsPath : null;

  if (!filePath) return null;

  const content = fs.readFileSync(filePath, 'utf-8');
  return { content, filePath };
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Page Tests - اختبارات صفحة الري
// ═══════════════════════════════════════════════════════════════════════════

describe('Irrigation Page', () => {
  const page = readPageFile('irrigation/page');

  it('page file exists', () => {
    expect(page, 'irrigation/page.tsx not found').not.toBeNull();
  });

  it('has "use client" directive', () => {
    expect(page!.content).toMatch(/['"]use client['"]/);
  });

  it('exports a default component', () => {
    expect(page!.content).toMatch(/export\s+default\s+function\s+IrrigationPage/);
  });

  it('imports required React hooks', () => {
    expect(page!.content).toContain('useEffect');
    expect(page!.content).toContain('useState');
  });

  it('imports Header component', () => {
    expect(page!.content).toMatch(/import\s+Header\s+from/);
  });

  it('imports StatCard component', () => {
    expect(page!.content).toMatch(/import\s+StatCard\s+from/);
  });

  it('imports DataTable component', () => {
    expect(page!.content).toMatch(/import\s+DataTable\s+from/);
  });

  it('imports API utilities', () => {
    expect(page!.content).toContain('apiClient');
    expect(page!.content).toContain('API_URLS');
  });

  it('contains Arabic page title', () => {
    expect(page!.content).toContain('الري الذكي');
  });

  it('contains Arabic subtitle', () => {
    expect(page!.content).toContain('جدولة الري وتوفير المياه بالذكاء الاصطناعي');
  });

  it('contains Arabic stat labels', () => {
    expect(page!.content).toContain('إجمالي المياه');
    expect(page!.content).toContain('وفر المياه');
    expect(page!.content).toContain('التبخر اليومي');
    expect(page!.content).toContain('التكلفة المتوقعة');
  });

  it('contains Arabic tab labels', () => {
    expect(page!.content).toContain('جدول الري');
    expect(page!.content).toContain('الميزان المائي');
    expect(page!.content).toContain('كفاءة الري');
  });

  it('contains Arabic crop names', () => {
    expect(page!.content).toContain('طماطم');
    expect(page!.content).toContain('قمح');
    expect(page!.content).toContain('نخيل');
  });

  it('contains Arabic irrigation method names', () => {
    expect(page!.content).toContain('ري بالتنقيط');
    expect(page!.content).toContain('ري رشاش');
    expect(page!.content).toContain('ري غمر');
  });

  it('contains Arabic recommendations section', () => {
    expect(page!.content).toContain('التوصيات');
    expect(page!.content).toContain('تنبيهات');
  });

  it('contains Arabic refresh button text', () => {
    expect(page!.content).toContain('تحديث');
  });

  it('defines IrrigationSchedule interface', () => {
    expect(page!.content).toContain('interface IrrigationSchedule');
  });

  it('defines IrrigationPlan interface', () => {
    expect(page!.content).toContain('interface IrrigationPlan');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Weather Page Tests - اختبارات صفحة الطقس
// ═══════════════════════════════════════════════════════════════════════════

describe('Weather Page', () => {
  const page = readPageFile('weather/page');

  it('page file exists', () => {
    expect(page, 'weather/page.tsx not found').not.toBeNull();
  });

  it('has "use client" directive', () => {
    expect(page!.content).toMatch(/['"]use client['"]/);
  });

  it('exports a default component', () => {
    expect(page!.content).toMatch(/export\s+default\s+function\s+WeatherPage/);
  });

  it('imports required React hooks', () => {
    expect(page!.content).toContain('useState');
    expect(page!.content).toContain('useEffect');
  });

  it('imports API utilities', () => {
    expect(page!.content).toContain('apiClient');
    expect(page!.content).toContain('API_URLS');
  });

  it('imports lucide-react weather icons', () => {
    expect(page!.content).toContain('Cloud');
    expect(page!.content).toContain('Thermometer');
    expect(page!.content).toContain('Wind');
    expect(page!.content).toContain('Droplets');
  });

  it('contains Arabic page title', () => {
    expect(page!.content).toContain('الطقس والمناخ');
  });

  it('contains Arabic weather labels', () => {
    expect(page!.content).toContain('الرطوبة');
    expect(page!.content).toContain('توقعات');
  });

  it('contains Arabic loading text', () => {
    expect(page!.content).toContain('جاري تحميل بيانات الطقس');
  });

  it('contains Arabic agricultural report label', () => {
    expect(page!.content).toContain('مخاطر الطقس');
  });

  it('defines WeatherLocation interface', () => {
    expect(page!.content).toContain('interface WeatherLocation');
  });

  it('defines CurrentWeather interface', () => {
    expect(page!.content).toContain('interface CurrentWeather');
  });

  it('defines ForecastDay interface', () => {
    expect(page!.content).toContain('interface ForecastDay');
  });

  it('defines AgriculturalReport interface', () => {
    expect(page!.content).toContain('interface AgriculturalReport');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Tasks Page Tests - اختبارات صفحة المهام
// ═══════════════════════════════════════════════════════════════════════════

describe('Tasks Page', () => {
  const page = readPageFile('tasks/page');

  it('page file exists', () => {
    expect(page, 'tasks/page.tsx not found').not.toBeNull();
  });

  it('has "use client" directive', () => {
    expect(page!.content).toMatch(/['"]use client['"]/);
  });

  it('exports a default component', () => {
    expect(page!.content).toMatch(/export\s+default\s+function\s+TasksPage/);
  });

  it('imports required React hooks', () => {
    expect(page!.content).toContain('useEffect');
    expect(page!.content).toContain('useState');
    expect(page!.content).toContain('useMemo');
    expect(page!.content).toContain('useCallback');
  });

  it('imports Header component', () => {
    expect(page!.content).toMatch(/import\s+Header\s+from/);
  });

  it('imports DataTable component', () => {
    expect(page!.content).toMatch(/import\s+DataTable\s+from/);
  });

  it('imports API utilities', () => {
    expect(page!.content).toContain('apiClient');
  });

  it('imports Task types', () => {
    expect(page!.content).toContain('Task');
    expect(page!.content).toContain('TaskStatus');
    expect(page!.content).toContain('Priority');
  });

  it('contains Arabic page title', () => {
    expect(page!.content).toContain('إدارة المهام');
  });

  it('contains Arabic subtitle pattern', () => {
    expect(page!.content).toContain('مهمة مسجلة');
  });

  it('contains Arabic stat label', () => {
    expect(page!.content).toContain('إجمالي المهام');
  });

  it('contains Arabic column headers', () => {
    expect(page!.content).toContain('عنوان المهمة');
    expect(page!.content).toContain('الأولوية');
    expect(page!.content).toContain('الحالة');
  });

  it('contains Arabic form labels', () => {
    expect(page!.content).toContain('إضافة مهمة');
    expect(page!.content).toContain('حذف المهمة');
  });

  it('contains Arabic form placeholder', () => {
    expect(page!.content).toContain('عنوان المهمة بالعربية');
  });

  it('defines TaskFormData interface', () => {
    expect(page!.content).toContain('interface TaskFormData');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Page Tests - اختبارات صفحة المعدات
// ═══════════════════════════════════════════════════════════════════════════

describe('Equipment Page', () => {
  const page = readPageFile('equipment/page');

  it('page file exists', () => {
    expect(page, 'equipment/page.tsx not found').not.toBeNull();
  });

  it('has "use client" directive', () => {
    expect(page!.content).toMatch(/['"]use client['"]/);
  });

  it('exports a default component', () => {
    expect(page!.content).toMatch(/export\s+default\s+function\s+EquipmentPage/);
  });

  it('imports required React hooks', () => {
    expect(page!.content).toContain('useEffect');
    expect(page!.content).toContain('useState');
    expect(page!.content).toContain('useMemo');
    expect(page!.content).toContain('useCallback');
  });

  it('imports Header component', () => {
    expect(page!.content).toMatch(/import\s+Header\s+from/);
  });

  it('imports DataTable component', () => {
    expect(page!.content).toMatch(/import\s+DataTable\s+from/);
  });

  it('imports API utilities', () => {
    expect(page!.content).toContain('apiClient');
  });

  it('imports Equipment type', () => {
    expect(page!.content).toContain('Equipment');
  });

  it('contains Arabic page title', () => {
    expect(page!.content).toContain('إدارة المعدات');
  });

  it('contains Arabic subtitle pattern', () => {
    expect(page!.content).toContain('معدة مسجلة');
  });

  it('contains Arabic stat labels', () => {
    expect(page!.content).toContain('إجمالي المعدات');
    expect(page!.content).toContain('تحتاج صيانة');
  });

  it('contains Arabic equipment type labels', () => {
    expect(page!.content).toContain('جرار');
    expect(page!.content).toContain('حصادة');
    expect(page!.content).toContain('مضخة');
    expect(page!.content).toContain('رشاش');
    expect(page!.content).toContain('طائرة بدون طيار');
  });

  it('contains Arabic equipment status labels', () => {
    expect(page!.content).toContain('تعمل');
    expect(page!.content).toContain('صيانة');
    expect(page!.content).toContain('متوقفة');
    expect(page!.content).toContain('معطلة');
  });

  it('contains Arabic column headers', () => {
    expect(page!.content).toContain('اسم المعدة');
    expect(page!.content).toContain('آخر صيانة');
    expect(page!.content).toContain('الصيانة القادمة');
  });

  it('contains Arabic form labels', () => {
    expect(page!.content).toContain('إضافة معدة');
    expect(page!.content).toContain('نوع المعدة');
  });

  it('defines EquipmentType type', () => {
    expect(page!.content).toMatch(/type\s+EquipmentType\s*=/);
  });

  it('defines EquipmentStatus type', () => {
    expect(page!.content).toMatch(/type\s+EquipmentStatus\s*=/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Sensors Page Tests - اختبارات صفحة المستشعرات
// ═══════════════════════════════════════════════════════════════════════════

describe('Sensors Page', () => {
  const page = readPageFile('sensors/page');

  it('page file exists', () => {
    expect(page, 'sensors/page.tsx not found').not.toBeNull();
  });

  it('has "use client" directive', () => {
    expect(page!.content).toMatch(/['"]use client['"]/);
  });

  it('exports a default component', () => {
    expect(page!.content).toMatch(/export\s+default\s+function\s+SensorsPage/);
  });

  it('imports required React hooks', () => {
    expect(page!.content).toContain('useEffect');
    expect(page!.content).toContain('useState');
    expect(page!.content).toContain('useMemo');
    expect(page!.content).toContain('useCallback');
  });

  it('imports Header component', () => {
    expect(page!.content).toMatch(/import\s+Header\s+from/);
  });

  it('imports DataTable component', () => {
    expect(page!.content).toMatch(/import\s+DataTable\s+from/);
  });

  it('imports IoT service from API', () => {
    expect(page!.content).toContain('iotService');
  });

  it('imports Toast hook', () => {
    expect(page!.content).toContain('useToast');
  });

  it('contains Arabic page title', () => {
    expect(page!.content).toContain('إدارة المستشعرات وأجهزة IoT');
  });

  it('contains Arabic subtitle pattern', () => {
    expect(page!.content).toContain('جهاز مسجل');
  });

  it('contains Arabic stat labels', () => {
    expect(page!.content).toContain('إجمالي الأجهزة');
    expect(page!.content).toContain('متصل');
    expect(page!.content).toContain('غير متصل');
    expect(page!.content).toContain('خطأ');
  });

  it('contains Arabic device type labels', () => {
    expect(page!.content).toContain('رطوبة التربة');
    expect(page!.content).toContain('محطة طقس');
    expect(page!.content).toContain('كاميرا');
    expect(page!.content).toContain('عداد التدفق');
  });

  it('contains Arabic column headers', () => {
    expect(page!.content).toContain('الجهاز');
    expect(page!.content).toContain('الرقم التسلسلي');
    expect(page!.content).toContain('الحقل');
    expect(page!.content).toContain('الحالة');
    expect(page!.content).toContain('آخر قراءة');
    expect(page!.content).toContain('البطارية');
  });

  it('contains Arabic CRUD button labels', () => {
    expect(page!.content).toContain('تسجيل جهاز');
    expect(page!.content).toContain('تعديل');
    expect(page!.content).toContain('حذف');
    expect(page!.content).toContain('تأكيد الحذف');
  });

  it('contains Arabic form labels', () => {
    expect(page!.content).toContain('اسم الجهاز');
    expect(page!.content).toContain('نوع الجهاز');
    expect(page!.content).toContain('الرقم التسلسلي');
    expect(page!.content).toContain('معرف الحقل');
  });

  it('contains Arabic search placeholder', () => {
    expect(page!.content).toContain('بحث بالاسم أو الرقم التسلسلي');
  });

  it('contains Arabic readings modal text', () => {
    expect(page!.content).toContain('قراءات الجهاز');
    expect(page!.content).toContain('جاري تحميل القراءات');
    expect(page!.content).toContain('لا توجد قراءات متاحة');
  });

  it('contains DeviceFormModal subcomponent', () => {
    expect(page!.content).toContain('function DeviceFormModal');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Inventory Page Tests - اختبارات صفحة المخزون
// ═══════════════════════════════════════════════════════════════════════════

describe('Inventory Page', () => {
  const page = readPageFile('inventory/page');

  it('page file exists', () => {
    expect(page, 'inventory/page.tsx not found').not.toBeNull();
  });

  it('has "use client" directive', () => {
    expect(page!.content).toMatch(/['"]use client['"]/);
  });

  it('exports a default component', () => {
    expect(page!.content).toMatch(/export\s+default\s+function\s+InventoryPage/);
  });

  it('imports required React hooks', () => {
    expect(page!.content).toContain('useEffect');
    expect(page!.content).toContain('useState');
    expect(page!.content).toContain('useMemo');
    expect(page!.content).toContain('useCallback');
  });

  it('imports Header component', () => {
    expect(page!.content).toMatch(/import\s+Header\s+from/);
  });

  it('imports DataTable component', () => {
    expect(page!.content).toMatch(/import\s+DataTable\s+from/);
  });

  it('imports ConfirmDialog component', () => {
    expect(page!.content).toMatch(/import\s+ConfirmDialog\s+from/);
  });

  it('imports Toast hook', () => {
    expect(page!.content).toContain('useToast');
  });

  it('imports mock data', () => {
    expect(page!.content).toContain('MOCK_INVENTORY');
  });

  it('contains Arabic page title', () => {
    expect(page!.content).toContain('إدارة المخزون');
  });

  it('contains Arabic subtitle pattern', () => {
    expect(page!.content).toContain('صنف');
  });

  it('contains Arabic stat labels', () => {
    expect(page!.content).toContain('إجمالي الأصناف');
    expect(page!.content).toContain('إجمالي القيمة');
    expect(page!.content).toContain('مخزون منخفض');
    expect(page!.content).toContain('نفذ');
  });

  it('contains Arabic category options', () => {
    expect(page!.content).toContain('بذور');
    expect(page!.content).toContain('أسمدة');
    expect(page!.content).toContain('مبيدات');
    expect(page!.content).toContain('معدات');
  });

  it('contains Arabic status options', () => {
    expect(page!.content).toContain('متوفر');
    expect(page!.content).toContain('مخزون منخفض');
    expect(page!.content).toContain('منتهي الصلاحية');
  });

  it('contains Arabic column headers', () => {
    expect(page!.content).toContain('الصنف');
    expect(page!.content).toContain('المزرعة');
    expect(page!.content).toContain('الكمية');
    expect(page!.content).toContain('القيمة');
    expect(page!.content).toContain('الحالة');
    expect(page!.content).toContain('آخر تحديث');
  });

  it('contains Arabic CRUD action labels', () => {
    expect(page!.content).toContain('إضافة صنف');
    expect(page!.content).toContain('تعديل الصنف');
    expect(page!.content).toContain('تفاصيل الصنف');
    expect(page!.content).toContain('حذف الصنف');
  });

  it('contains Arabic form field labels', () => {
    expect(page!.content).toContain('اسم الصنف');
    expect(page!.content).toContain('الفئة');
    expect(page!.content).toContain('اسم المزرعة');
    expect(page!.content).toContain('الوحدة');
    expect(page!.content).toContain('الحد الأدنى');
  });

  it('contains Arabic search placeholder', () => {
    expect(page!.content).toContain('بحث بالصنف أو المزرعة');
  });

  it('contains Arabic cancel/save button labels', () => {
    expect(page!.content).toContain('إلغاء');
    expect(page!.content).toContain('حفظ التعديلات');
    expect(page!.content).toContain('إضافة');
  });

  it('contains Arabic success toast messages', () => {
    expect(page!.content).toContain('تمت إضافة الصنف بنجاح');
    expect(page!.content).toContain('تم تحديث الصنف بنجاح');
    expect(page!.content).toContain('تم حذف الصنف بنجاح');
  });

  it('contains DetailRow helper component', () => {
    expect(page!.content).toContain('function DetailRow');
  });

  it('contains FormField helper component', () => {
    expect(page!.content).toContain('function FormField');
  });

  it('defines CATEGORY_OPTIONS constant', () => {
    expect(page!.content).toContain('CATEGORY_OPTIONS');
  });

  it('defines STATUS_OPTIONS constant', () => {
    expect(page!.content).toContain('STATUS_OPTIONS');
  });
});

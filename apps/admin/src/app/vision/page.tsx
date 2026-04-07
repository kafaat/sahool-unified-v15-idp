'use client';

/**
 * Computer Vision Page — الرؤية الحاسوبية
 * Displays loaded models, health status, and detection stats
 */

import { useEffect, useState, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { Eye, ScanLine, Target, Gauge, RefreshCw } from 'lucide-react';
import { logger } from '@/lib/logger';
import { visionService, type VisionModel } from '@/lib/api';

export default function VisionPage() {
  const { toast } = useToast();
  const [models, setModels] = useState<VisionModel[]>([]);
  const [health, setHealth] = useState<Record<string, unknown>>({});
  const [isLoading, setIsLoading] = useState(true);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [modelsRes, healthRes] = await Promise.all([
        visionService.getModels(),
        visionService.getHealth(),
      ]);
      setModels(modelsRes);
      setHealth(healthRes);
    } catch (error) {
      logger.error('Failed to load vision data:', error);
      toast.error('خطأ في التحميل', 'فشل تحميل بيانات الرؤية الحاسوبية');
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => { loadData(); }, [loadData]);

  const loadedCount = models.filter((m) => m.status === 'active').length;
  const avgAccuracy = models.length > 0
    ? (models.reduce((sum, m) => sum + m.accuracy, 0) / models.length * 100).toFixed(1)
    : '—';
  const gpuUsage = health.gpu_usage != null ? `${health.gpu_usage}%` : '—';
  const totalDetections = health.total_detections != null ? Number(health.total_detections).toLocaleString() : '—';

  const columns = [
    { key: 'name', header: 'الاسم' },
    { key: 'variant', header: 'النوع' },
    { key: 'task', header: 'المهمة' },
    { key: 'version', header: 'الإصدار' },
    {
      key: 'status',
      header: 'الحالة',
      render: (item: VisionModel) => {
        const colors: Record<string, string> = {
          active: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
          loading: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
          error: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
        };
        const labels: Record<string, string> = { active: 'نشط', loading: 'جاري التحميل', error: 'خطأ' };
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[item.status] ?? ''}`}>
            {labels[item.status] ?? item.status}
          </span>
        );
      },
    },
    { key: 'accuracy', header: 'الدقة', render: (item: VisionModel) => `${(item.accuracy * 100).toFixed(1)}%` },
    { key: 'size_mb', header: 'الحجم (MB)', render: (item: VisionModel) => `${item.size_mb} MB` },
  ];

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <Header title="الرؤية الحاسوبية" subtitle="Computer Vision" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Eye className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{loadedCount}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نماذج محملة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <ScanLine className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{totalDetections}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الاكتشافات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{avgAccuracy}%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متوسط الدقة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Gauge className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{gpuUsage}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">استخدام GPU</p>
            </div>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">النماذج المحملة</h3>
          <button onClick={loadData} className="flex items-center gap-1 px-3 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100">
            <RefreshCw className="w-4 h-4" /> تحديث
          </button>
        </div>
      </div>

      {/* Models Table */}
      <DataTable
        columns={columns}
        data={models}
        keyExtractor={(item) => item.id}
        isLoading={isLoading}
        emptyMessage="لا توجد نماذج محملة"
      />

      {/* Health Info */}
      {Object.keys(health).length > 0 && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">حالة الخدمة</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            {Object.entries(health).map(([key, value]) => (
              <div key={key} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-gray-500 dark:text-gray-400 text-xs">{key}</p>
                <p className="text-gray-900 dark:text-gray-100 font-medium">{String(value)}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

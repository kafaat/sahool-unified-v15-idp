'use client';

/**
 * Computer Vision Page
 * الرؤية الحاسوبية
 */

import Header from '@/components/layout/Header';
import { Eye, ScanLine, Target, Gauge, Camera } from 'lucide-react';

export default function VisionPage() {
  return (
    <div className="p-6">
      <Header title="الرؤية الحاسوبية" subtitle="Computer Vision" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Eye className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">5</p>
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
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">1,089</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">اكتشافات اليوم</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">88.4%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">الدقة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Gauge className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">67%</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">استخدام GPU</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content placeholder */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
        <Camera className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          سيتم عرض إدارة نماذج الرؤية الحاسوبية هنا
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          Computer vision model management and detection results will be displayed here
        </p>
      </div>
    </div>
  );
}

'use client';

/**
 * Drone Management Page
 * إدارة الطائرات المسيّرة
 */

import Header from '@/components/layout/Header';
import { Plane, Navigation, CheckCircle, MapPin } from 'lucide-react';

export default function DronePage() {
  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-6">
      <Header title="إدارة الطائرات المسيّرة" subtitle="Drone Management" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Plane className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">18</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الطائرات</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Navigation className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">5</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">رحلات نشطة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">142</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مهام مكتملة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">1,250 ha</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مساحة التغطية</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content placeholder */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
        <Plane className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          سيتم عرض قائمة أسطول الطائرات المسيّرة هنا
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          Drone fleet list and mission management will be displayed here
        </p>
      </div>
    </div>
  );
}

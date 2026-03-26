'use client';

/**
 * Edge Devices Page
 * أجهزة الحافة
 */

import Header from '@/components/layout/Header';
import { Server, Wifi, WifiOff, Box, Cpu } from 'lucide-react';

export default function EdgeDevicesPage() {
  return (
    <div className="p-6">
      <Header title="أجهزة الحافة" subtitle="Edge Devices" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Server className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">34</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الأجهزة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Wifi className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">28</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متصل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <WifiOff className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">6</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">غير متصل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Box className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">12</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">نماذج منشورة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content placeholder */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
        <Cpu className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          سيتم عرض قائمة أجهزة الحافة هنا
        </h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          Edge device list and model deployment management will be displayed here
        </p>
      </div>
    </div>
  );
}

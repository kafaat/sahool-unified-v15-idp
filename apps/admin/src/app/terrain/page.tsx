"use client";

/**
 * Terrain Analysis Page
 * تحليل التضاريس
 */

import Header from "@/components/layout/Header";
import {
  Mountain,
  CheckCircle,
  Clock,
  Upload,
  MapPin,
} from "lucide-react";

export default function TerrainPage() {
  return (
    <div className="p-6">
      <Header title="تحليل التضاريس" subtitle="Terrain Analysis" />

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">256</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">تحليلات مكتملة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">14</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">قيد الانتظار</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Upload className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">89</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">رفع DEM</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">4,320 ha</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي المساحة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content placeholder */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
        <Mountain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">سيتم عرض قائمة تحليلات التضاريس هنا</h3>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Terrain analysis list with DEM processing and slope/aspect results will be displayed here</p>
      </div>
    </div>
  );
}

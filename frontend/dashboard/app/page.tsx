'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import { TaskList } from '@/components/TaskList'
import { EventTimeline } from '@/components/EventTimeline'
import { StatsCards } from '@/components/StatsCards'

// Dynamic import for MapView (client-side only)
const MapView = dynamic(() => import('@/components/MapView'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center">
      <span className="text-gray-500">جاري تحميل الخريطة...</span>
    </div>
  ),
})

export default function DashboardPage() {
  const [selectedField, setSelectedField] = useState<string | null>(null)

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-800">لوحة التحكم</h2>
          <p className="text-sm text-gray-500">
            {new Date().toLocaleDateString('ar-YE', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 bg-green-500 rounded-full live-indicator"></span>
            <span className="text-gray-600">متصل</span>
          </div>
          <button className="bg-sahool-primary text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700">
            + مهمة جديدة
          </button>
        </div>
      </header>

      {/* Stats */}
      <div className="px-6 py-4">
        <StatsCards />
      </div>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-12 gap-4 px-6 pb-6 min-h-0">
        {/* Map - 8 columns */}
        <div className="col-span-8 bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between">
            <h3 className="font-bold text-gray-800">🗺️ خريطة الحقول</h3>
            <div className="flex gap-2">
              <button className="text-xs px-3 py-1 rounded-full bg-emerald-100 text-emerald-700">
                الحقول
              </button>
              <button className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600">
                NDVI
              </button>
              <button className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-600">
                المهام
              </button>
            </div>
          </div>
          <div className="h-[calc(100%-60px)]">
            <MapView onFieldSelect={setSelectedField} />
          </div>
        </div>

        {/* Right Panel - 4 columns */}
        <div className="col-span-4 flex flex-col gap-4 min-h-0">
          {/* Tasks */}
          <div className="bg-white rounded-xl shadow-sm flex-1 overflow-hidden flex flex-col">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-bold text-gray-800">📋 مهام اليوم</h3>
              <span className="text-xs bg-sahool-primary text-white px-2 py-1 rounded-full">
                12 مهمة
              </span>
            </div>
            <div className="flex-1 overflow-auto p-4">
              <TaskList fieldId={selectedField} />
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-xl shadow-sm flex-1 overflow-hidden flex flex-col">
            <div className="p-4 border-b flex items-center justify-between">
              <h3 className="font-bold text-gray-800">📊 الأحداث المباشرة</h3>
              <span className="flex items-center gap-1 text-xs text-green-600">
                <span className="w-2 h-2 bg-green-500 rounded-full live-indicator"></span>
                مباشر
              </span>
            </div>
            <div className="flex-1 overflow-auto p-4">
              <EventTimeline />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

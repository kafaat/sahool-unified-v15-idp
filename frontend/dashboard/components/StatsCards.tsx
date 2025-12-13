'use client'

import { useEffect, useState } from 'react'

interface Stats {
  totalFields: number
  totalArea: number
  healthScore: number
  pendingTasks: number
  completedTasks: number
  activeAlerts: number
}

export function StatsCards() {
  const [stats, setStats] = useState<Stats>({
    totalFields: 4,
    totalArea: 29.5,
    healthScore: 72,
    pendingTasks: 8,
    completedTasks: 4,
    activeAlerts: 3,
  })

  return (
    <div className="grid grid-cols-6 gap-4">
      {/* Fields */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500">الحقول</p>
            <p className="text-2xl font-bold text-gray-800">{stats.totalFields}</p>
          </div>
          <span className="text-3xl">🌱</span>
        </div>
        <p className="text-xs text-gray-400 mt-2">{stats.totalArea} هكتار</p>
      </div>

      {/* Health Score */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500">صحة المحاصيل</p>
            <p className={`text-2xl font-bold ${
              stats.healthScore >= 70 ? 'text-emerald-600' :
              stats.healthScore >= 50 ? 'text-amber-600' : 'text-red-600'
            }`}>{stats.healthScore}%</p>
          </div>
          <span className="text-3xl">💚</span>
        </div>
        <div className="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              stats.healthScore >= 70 ? 'bg-emerald-500' :
              stats.healthScore >= 50 ? 'bg-amber-500' : 'bg-red-500'
            }`}
            style={{ width: `${stats.healthScore}%` }}
          ></div>
        </div>
      </div>

      {/* Pending Tasks */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500">مهام معلقة</p>
            <p className="text-2xl font-bold text-blue-600">{stats.pendingTasks}</p>
          </div>
          <span className="text-3xl">📋</span>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          <span className="text-emerald-500">✓ {stats.completedTasks}</span> مكتملة اليوم
        </p>
      </div>

      {/* Alerts */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500">تنبيهات نشطة</p>
            <p className={`text-2xl font-bold ${
              stats.activeAlerts > 0 ? 'text-red-600' : 'text-gray-400'
            }`}>{stats.activeAlerts}</p>
          </div>
          <span className="text-3xl">{stats.activeAlerts > 0 ? '🔔' : '✅'}</span>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          {stats.activeAlerts > 0 ? 'تحتاج مراجعة' : 'لا توجد تنبيهات'}
        </p>
      </div>

      {/* Weather */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500">الطقس اليوم</p>
            <p className="text-2xl font-bold text-cyan-600">32°</p>
          </div>
          <span className="text-3xl">☀️</span>
        </div>
        <p className="text-xs text-gray-400 mt-2">صنعاء - مشمس</p>
      </div>

      {/* Water Usage */}
      <div className="bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500">استهلاك المياه</p>
            <p className="text-2xl font-bold text-blue-500">85%</p>
          </div>
          <span className="text-3xl">💧</span>
        </div>
        <p className="text-xs text-emerald-500 mt-2">↓ 15% توفير</p>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { SkeletonCard } from './ui/Skeleton'

interface Stats {
  totalFields: number
  totalArea: number
  healthScore: number
  pendingTasks: number
  completedTasks: number
  activeAlerts: number
  temperature: number
  weatherCondition: string
  waterUsage: number
  waterSaving: number
}

interface StatsCardProps {
  title: string
  value: string | number
  icon: string
  subtitle?: string
  color?: string
  progress?: number
}

function StatsCard({ title, value, icon, subtitle, color = 'var(--text-primary)', progress }: StatsCardProps) {
  return (
    <div className="card rounded-xl p-4 transition-transform hover:scale-[1.02]">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{title}</p>
          <p className="text-2xl font-bold" style={{ color }}>{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
      {progress !== undefined && (
        <div className="mt-2 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${progress}%`,
              backgroundColor: progress >= 70 ? '#10b981' : progress >= 50 ? '#f59e0b' : '#ef4444'
            }}
          />
        </div>
      )}
      {subtitle && (
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>{subtitle}</p>
      )}
    </div>
  )
}

export function StatsCards() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        // TODO: Replace with actual API call
        // const response = await fetch('/api/v1/stats')
        // const data = await response.json()

        // Simulated delay for loading state demo
        await new Promise(resolve => setTimeout(resolve, 800))

        // Mock data
        setStats({
          totalFields: 4,
          totalArea: 29.5,
          healthScore: 72,
          pendingTasks: 8,
          completedTasks: 4,
          activeAlerts: 3,
          temperature: 32,
          weatherCondition: 'مشمس',
          waterUsage: 85,
          waterSaving: 15,
        })
        setError(null)
      } catch (err) {
        setError('فشل تحميل الإحصائيات')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="card rounded-xl p-4 text-center" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)' }}>
        <p className="text-red-500">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-2 px-4 py-2 text-sm rounded-lg bg-red-500 text-white hover:bg-red-600"
        >
          إعادة المحاولة
        </button>
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <StatsCard
        title="الحقول"
        value={stats.totalFields}
        icon="🌱"
        subtitle={`${stats.totalArea} هكتار`}
        color="var(--text-primary)"
      />

      <StatsCard
        title="صحة المحاصيل"
        value={`${stats.healthScore}%`}
        icon="💚"
        progress={stats.healthScore}
        color={stats.healthScore >= 70 ? '#10b981' : stats.healthScore >= 50 ? '#f59e0b' : '#ef4444'}
      />

      <StatsCard
        title="مهام معلقة"
        value={stats.pendingTasks}
        icon="📋"
        subtitle={`✓ ${stats.completedTasks} مكتملة اليوم`}
        color="#3b82f6"
      />

      <StatsCard
        title="تنبيهات نشطة"
        value={stats.activeAlerts}
        icon={stats.activeAlerts > 0 ? '🔔' : '✅'}
        subtitle={stats.activeAlerts > 0 ? 'تحتاج مراجعة' : 'لا توجد تنبيهات'}
        color={stats.activeAlerts > 0 ? '#ef4444' : 'var(--text-muted)'}
      />

      <StatsCard
        title="الطقس اليوم"
        value={`${stats.temperature}°`}
        icon="☀️"
        subtitle={`صنعاء - ${stats.weatherCondition}`}
        color="#06b6d4"
      />

      <StatsCard
        title="استهلاك المياه"
        value={`${stats.waterUsage}%`}
        icon="💧"
        subtitle={`↓ ${stats.waterSaving}% توفير`}
        color="#3b82f6"
      />
    </div>
  )
}

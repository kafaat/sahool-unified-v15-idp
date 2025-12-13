'use client'

interface StatusBadgeProps {
  status: string
  size?: 'sm' | 'md' | 'lg'
}

const STATUS_CONFIG: Record<string, { label: string; colors: string }> = {
  // Task statuses
  open: { label: 'مفتوحة', colors: 'bg-blue-100 text-blue-800' },
  in_progress: { label: 'قيد التنفيذ', colors: 'bg-yellow-100 text-yellow-800' },
  done: { label: 'مكتملة', colors: 'bg-green-100 text-green-800' },
  canceled: { label: 'ملغاة', colors: 'bg-gray-100 text-gray-800' },

  // Health statuses
  healthy: { label: 'صحي', colors: 'bg-emerald-100 text-emerald-800' },
  warning: { label: 'تحذير', colors: 'bg-amber-100 text-amber-800' },
  critical: { label: 'حرج', colors: 'bg-red-100 text-red-800' },

  // Priority
  low: { label: 'منخفضة', colors: 'bg-gray-100 text-gray-600' },
  medium: { label: 'متوسطة', colors: 'bg-blue-100 text-blue-700' },
  high: { label: 'عالية', colors: 'bg-orange-100 text-orange-700' },
  urgent: { label: 'عاجلة', colors: 'bg-red-100 text-red-700' },

  // Connection
  connected: { label: 'متصل', colors: 'bg-green-100 text-green-700' },
  disconnected: { label: 'غير متصل', colors: 'bg-gray-100 text-gray-500' },

  // Alerts
  info: { label: 'معلومة', colors: 'bg-sky-100 text-sky-700' },
  alert: { label: 'تنبيه', colors: 'bg-amber-100 text-amber-700' },
  error: { label: 'خطأ', colors: 'bg-red-100 text-red-700' },
}

const SIZE_CLASSES = {
  sm: 'text-xs px-1.5 py-0.5',
  md: 'text-xs px-2 py-1',
  lg: 'text-sm px-3 py-1.5',
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] || { label: status, colors: 'bg-gray-100 text-gray-600' }

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${config.colors} ${SIZE_CLASSES[size]}`}>
      {config.label}
    </span>
  )
}

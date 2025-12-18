'use client'

import { useEffect, useState } from 'react'
import { Task } from '@/lib/api'
import { TaskCard } from './TaskCard'

interface TaskListProps {
  fieldId?: string | null
}

// Sample tasks data (will be replaced with API call)
const SAMPLE_TASKS: Task[] = [
  {
    id: 'task_001',
    tenant_id: 'tenant_1',
    field_id: 'field_001',
    title: 'ري الطماطم - الصباح',
    description: 'ري الحقل الشمالي لمدة 30 دقيقة',
    status: 'open',
    priority: 'high',
    due_date: new Date().toISOString(),
    assigned_to: 'أحمد',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'task_002',
    tenant_id: 'tenant_1',
    field_id: 'field_001',
    title: 'رش مبيدات وقائية',
    description: 'رش مبيد فطري للوقاية من البياض الدقيقي',
    status: 'in_progress',
    priority: 'medium',
    due_date: new Date(Date.now() + 86400000).toISOString(),
    assigned_to: 'محمد',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'task_003',
    tenant_id: 'tenant_1',
    field_id: 'field_002',
    title: 'فحص مرض صدأ البن',
    description: 'فحص ميداني للكشف عن علامات مرض صدأ الأوراق',
    status: 'open',
    priority: 'urgent',
    due_date: new Date().toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'task_004',
    tenant_id: 'tenant_1',
    field_id: 'field_002',
    title: 'تسميد البن - NPK',
    description: 'إضافة سماد NPK 20-20-20 بمعدل 50 كجم/هكتار',
    status: 'open',
    priority: 'medium',
    due_date: new Date(Date.now() + 172800000).toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'task_005',
    tenant_id: 'tenant_1',
    field_id: 'field_003',
    title: 'تقليم القات',
    description: 'تقليم الأغصان الجافة والمصابة',
    status: 'done',
    priority: 'low',
    evidence_photos: ['photo1.jpg', 'photo2.jpg'],
    evidence_notes: 'تم التقليم بنجاح',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'task_006',
    tenant_id: 'tenant_1',
    field_id: 'field_004',
    title: 'حصاد الموز الناضج',
    description: 'جمع العناقيد الناضجة من الصف 1-5',
    status: 'open',
    priority: 'high',
    due_date: new Date().toISOString(),
    assigned_to: 'علي',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

export function TaskList({ fieldId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [filter, setFilter] = useState<'all' | 'open' | 'done'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    setLoading(true)
    setTimeout(() => {
      let filteredTasks = SAMPLE_TASKS

      // Filter by field if specified
      if (fieldId) {
        filteredTasks = filteredTasks.filter((t) => t.field_id === fieldId)
      }

      setTasks(filteredTasks)
      setLoading(false)
    }, 500)
  }, [fieldId])

  const handleComplete = async (taskId: string) => {
    // Update local state
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, status: 'done' as const } : t
      )
    )
    // TODO: Call API
  }

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'open') return task.status === 'open' || task.status === 'in_progress'
    if (filter === 'done') return task.status === 'done'
    return true
  })

  const openCount = tasks.filter((t) => t.status === 'open' || t.status === 'in_progress').length
  const doneCount = tasks.filter((t) => t.status === 'done').length

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="h-20 bg-gray-200 rounded-lg"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Filter tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setFilter('all')}
          className={`text-xs px-3 py-1 rounded-full transition-colors ${
            filter === 'all'
              ? 'bg-sahool-primary text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          الكل ({tasks.length})
        </button>
        <button
          onClick={() => setFilter('open')}
          className={`text-xs px-3 py-1 rounded-full transition-colors ${
            filter === 'open'
              ? 'bg-sahool-primary text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          مفتوحة ({openCount})
        </button>
        <button
          onClick={() => setFilter('done')}
          className={`text-xs px-3 py-1 rounded-full transition-colors ${
            filter === 'done'
              ? 'bg-sahool-primary text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          مكتملة ({doneCount})
        </button>
      </div>

      {/* Task cards */}
      {filteredTasks.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <span className="text-4xl">📋</span>
          <p className="mt-2">لا توجد مهام</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onComplete={handleComplete}
            />
          ))}
        </div>
      )}
    </div>
  )
}

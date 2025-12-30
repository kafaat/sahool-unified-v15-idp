// @ts-nocheck - Temporary fix for types with React 19
'use client';

// Activity Feed Component
// تدفق النشاطات

import { useState } from 'react';
import {
  Activity,
  Bug,
  Droplets,
  Sprout,
  User,
  MapPin,
  FileText,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Filter
} from 'lucide-react';
import { formatDate } from '@/lib/utils';
import Link from 'next/link';

export interface ActivityItem {
  id: string;
  type: 'diagnosis' | 'irrigation' | 'task' | 'alert' | 'farm' | 'prescription' | 'sensor' | 'general';
  action: string;
  actionAr: string;
  description: string;
  descriptionAr: string;
  userId?: string;
  userName?: string;
  farmId?: string;
  farmName?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
  actionUrl?: string;
}

interface ActivityFeedProps {
  activities: ActivityItem[];
  maxItems?: number;
  showFilters?: boolean;
  showTimestamps?: boolean;
  className?: string;
}

export default function ActivityFeed({
  activities,
  maxItems = 20,
  showFilters = true,
  showTimestamps = true,
  className = ''
}: ActivityFeedProps) {
  const [filter, setFilter] = useState<'all' | 'diagnosis' | 'irrigation' | 'task' | 'alert'>('all');
  const [filteredActivities, setFilteredActivities] = useState<ActivityItem[]>(
    activities.slice(0, maxItems)
  );

  const handleFilterChange = (newFilter: typeof filter) => {
    setFilter(newFilter);
    let filtered = activities;

    if (newFilter !== 'all') {
      filtered = activities.filter(a => a.type === newFilter);
    }

    setFilteredActivities(filtered.slice(0, maxItems));
  };

  const getActivityIcon = (type: string) => {
    const icons: Record<string, typeof Activity> = {
      diagnosis: Bug,
      irrigation: Droplets,
      task: FileText,
      alert: AlertTriangle,
      farm: MapPin,
      prescription: Sprout,
      sensor: Activity,
      general: Activity,
    };
    return icons[type] || Activity;
  };

  const getActivityColor = (type: string) => {
    const colors: Record<string, string> = {
      diagnosis: 'bg-purple-100 text-purple-600',
      irrigation: 'bg-blue-100 text-blue-600',
      task: 'bg-yellow-100 text-yellow-600',
      alert: 'bg-red-100 text-red-600',
      farm: 'bg-green-100 text-green-600',
      prescription: 'bg-emerald-100 text-emerald-600',
      sensor: 'bg-cyan-100 text-cyan-600',
      general: 'bg-gray-100 text-gray-600',
    };
    return colors[type] || 'bg-gray-100 text-gray-600';
  };

  const getActivityTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      diagnosis: 'تشخيص',
      irrigation: 'ري',
      task: 'مهمة',
      alert: 'تنبيه',
      farm: 'مزرعة',
      prescription: 'وصفة',
      sensor: 'مستشعر',
      general: 'عام',
    };
    return labels[type] || type;
  };

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-100 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-sahool-600" />
            <h2 className="font-bold text-gray-900">النشاطات الأخيرة</h2>
          </div>
          {showFilters && (
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filter}
                onChange={(e) => handleFilterChange(e.target.value as typeof filter)}
                className="px-3 py-1.5 text-xs font-medium border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
              >
                <option value="all">الكل</option>
                <option value="diagnosis">تشخيصات</option>
                <option value="irrigation">ري</option>
                <option value="task">مهام</option>
                <option value="alert">تنبيهات</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Activities List */}
      <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
        {filteredActivities.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>لا توجد نشاطات</p>
          </div>
        ) : (
          filteredActivities.map((activity) => {
            const Icon = getActivityIcon(activity.type);
            const colorClass = getActivityColor(activity.type);

            return (
              <div
                key={activity.id}
                className="p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className={`p-2 rounded-lg ${colorClass} flex-shrink-0`}>
                    <Icon className="w-4 h-4" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 text-sm">
                          {activity.actionAr}
                        </h3>
                        <p className="text-sm text-gray-600 mt-0.5">
                          {activity.descriptionAr}
                        </p>
                      </div>
                      <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full flex-shrink-0">
                        {getActivityTypeLabel(activity.type)}
                      </span>
                    </div>

                    {/* Metadata */}
                    <div className="flex items-center gap-3 text-xs text-gray-500 mt-2">
                      {activity.userName && (
                        <div className="flex items-center gap-1">
                          <User className="w-3 h-3" />
                          <span>{activity.userName}</span>
                        </div>
                      )}
                      {activity.farmName && (
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          <span>{activity.farmName}</span>
                        </div>
                      )}
                      {showTimestamps && (
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(activity.timestamp)}</span>
                        </div>
                      )}
                      {activity.actionUrl && (
                        <Link
                          href={activity.actionUrl}
                          className="mr-auto text-sahool-600 hover:text-sahool-700 font-medium"
                        >
                          عرض ←
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      {filteredActivities.length > 0 && filteredActivities.length < activities.length && (
        <div className="p-3 border-t border-gray-100 text-center">
          <button
            onClick={() => setFilteredActivities(activities.slice(0, maxItems + 10))}
            className="text-sm text-sahool-600 hover:text-sahool-700 font-medium"
          >
            تحميل المزيد ←
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * Field Map with Tasks Component
 * مكون خريطة الحقول مع المهام
 *
 * An integrated map component that displays both fields and their associated tasks
 */

"use client";

import { useRef, useEffect, useState } from "react";
import { logger } from "@/lib/logger";
import { MapPin, Loader2, Filter } from "lucide-react";
import { TaskMarkers } from "./TaskMarkers";
import { useTasks } from "@/features/tasks/hooks/useTasks";
import { useFields } from "../hooks/useFieldsList";
import type { Priority, TaskStatus } from "@/features/tasks/types";

interface FieldMapWithTasksProps {
  /** Fixed height for the map */
  height?: string;
  /** Filter tasks by field ID */
  fieldId?: string;
  /** Filter tasks by priority */
  priority?: Priority;
  /** Filter tasks by status */
  status?: TaskStatus;
  /** Enable task clustering */
  enableClustering?: boolean;
  /** Show filter controls */
  showFilters?: boolean;
}

/**
 * Field Map with Tasks Component
 * Displays an interactive map with fields and tasks
 */
export function FieldMapWithTasks({
  height = "500px",
  fieldId,
  priority,
  status,
  enableClustering = true,
  showFilters = true,
}: FieldMapWithTasksProps) {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [filterPriority, setFilterPriority] = useState<Priority | undefined>(
    priority,
  );
  const [filterStatus, setFilterStatus] = useState<TaskStatus | undefined>(
    status,
  );

  // Fetch data
  const { data: allTasks = [], isLoading: tasksLoading } = useTasks({
    field_id: fieldId,
    priority: filterPriority,
    status: filterStatus,
  });
  const { data: fields = [], isLoading: fieldsLoading } = useFields();

  const isLoading = tasksLoading || fieldsLoading;

  // Initialize map
  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) {
      logger.warn("Leaflet is not loaded. Include it in your layout.");
      return;
    }

    // Create map if it doesn't exist
    if (!mapRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current).setView([15.5527, 48.5164], 6);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;
    }

    // Cleanup
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Fit map to show all tasks/fields
  useEffect(() => {
    if (!mapRef.current || !fields.length) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) return;

    // Get all field centroids
    const bounds: [number, number][] = [];
    fields.forEach((field) => {
      if (field.centroid) {
        const [lng, lat] = field.centroid.coordinates;
        bounds.push([lat, lng]);
      }
    });

    if (bounds.length > 0) {
      const leafletBounds = L.latLngBounds(bounds);
      mapRef.current.fitBounds(leafletBounds, { padding: [50, 50] });
    }
  }, [fields]);

  // Calculate task statistics
  const taskStats = {
    total: allTasks.length,
    urgent: allTasks.filter((t) => t.priority === "urgent").length,
    high: allTasks.filter((t) => t.priority === "high").length,
    medium: allTasks.filter((t) => t.priority === "medium").length,
    low: allTasks.filter((t) => t.priority === "low").length,
    open: allTasks.filter((t) => t.status === "open").length,
    in_progress: allTasks.filter((t) => t.status === "in_progress").length,
    completed: allTasks.filter((t) => t.status === "completed").length,
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow" style={{ height }}>
        <div className="h-full flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-green-600" />
          <span className="mr-3 text-gray-600">جاري تحميل الخريطة...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <MapPin className="w-5 h-5 ml-2 text-green-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              خريطة المهام
            </h2>
          </div>
          <div className="flex gap-4 text-sm">
            <span className="text-gray-600">
              {taskStats.total} مهمة على {fields.length} حقل
            </span>
          </div>
        </div>

        {/* Task Statistics */}
        <div className="mt-3 flex flex-wrap gap-3 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-600 ml-1"></div>
            <span className="text-gray-600">
              عاجل: <strong>{taskStats.urgent}</strong>
            </span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-500 ml-1"></div>
            <span className="text-gray-600">
              عالي: <strong>{taskStats.high}</strong>
            </span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-yellow-500 ml-1"></div>
            <span className="text-gray-600">
              متوسط: <strong>{taskStats.medium}</strong>
            </span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-500 ml-1"></div>
            <span className="text-gray-600">
              منخفض: <strong>{taskStats.low}</strong>
            </span>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mt-3 flex flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterPriority || ""}
                onChange={(e) =>
                  setFilterPriority((e.target.value as Priority) || undefined)
                }
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="">كل الأولويات</option>
                <option value="urgent">عاجل</option>
                <option value="high">عالي</option>
                <option value="medium">متوسط</option>
                <option value="low">منخفض</option>
              </select>
            </div>

            <div>
              <select
                value={filterStatus || ""}
                onChange={(e) =>
                  setFilterStatus((e.target.value as TaskStatus) || undefined)
                }
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="">كل الحالات</option>
                <option value="open">مفتوح</option>
                <option value="pending">معلق</option>
                <option value="in_progress">قيد التنفيذ</option>
                <option value="completed">مكتمل</option>
                <option value="cancelled">ملغي</option>
              </select>
            </div>

            {(filterPriority || filterStatus) && (
              <button
                onClick={() => {
                  setFilterPriority(undefined);
                  setFilterStatus(undefined);
                }}
                className="text-sm text-green-600 hover:text-green-700 font-medium"
              >
                إعادة تعيين الفلاتر
              </button>
            )}
          </div>
        )}
      </div>

      {/* Map Container */}
      <div ref={mapContainerRef} style={{ height }} className="w-full" />

      {/* Task Markers */}
      <TaskMarkers
        tasks={allTasks}
        fields={fields}
        mapRef={mapRef}
        enableClustering={enableClustering}
      />

      {/* Legend */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <div className="text-sm text-gray-600 mb-2 font-medium">الرموز:</div>
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span>💧</span>
            <span className="text-gray-700">ري</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🔍</span>
            <span className="text-gray-700">فحص</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🌱</span>
            <span className="text-gray-700">تسميد</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🌾</span>
            <span className="text-gray-700">زراعة</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🌽</span>
            <span className="text-gray-700">حصاد</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🐛</span>
            <span className="text-gray-700">مكافحة آفات</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🔧</span>
            <span className="text-gray-700">صيانة</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FieldMapWithTasks;

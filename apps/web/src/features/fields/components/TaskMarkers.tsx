/**
 * SAHOOL Task Markers Component
 * مكون علامات المهام على الخريطة
 *
 * Displays tasks as markers on the field map with:
 * - Different icons for different task types
 * - Color coding by priority
 * - Task clustering when zoomed out
 * - Popup with task details
 * - Navigation to task details on click
 */

"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import type { Task } from "@/features/tasks/types";
import type { Field } from "../types";

// Task type labels in Arabic
const TASK_TYPE_LABELS: Record<string, string> = {
  irrigation: "ري",
  inspection: "فحص",
  fertilization: "تسميد",
  planting: "زراعة",
  harvesting: "حصاد",
  pest_control: "مكافحة آفات",
  maintenance: "صيانة",
  other: "أخرى",
};

// Task type icons (Unicode emojis as fallback, can be replaced with custom icons)
const TASK_TYPE_ICONS: Record<string, string> = {
  irrigation: "💧",
  inspection: "🔍",
  fertilization: "🌱",
  planting: "🌾",
  harvesting: "🌽",
  pest_control: "🐛",
  maintenance: "🔧",
  other: "📋",
};

// Priority colors
const PRIORITY_COLORS: Record<string, string> = {
  urgent: "#dc2626", // red-600
  high: "#ef4444", // red-500
  medium: "#eab308", // yellow-500
  low: "#22c55e", // green-500
};

// Status labels in Arabic
const STATUS_LABELS: Record<string, string> = {
  open: "مفتوح",
  pending: "معلق",
  in_progress: "قيد التنفيذ",
  completed: "مكتمل",
  cancelled: "ملغي",
};

interface TaskMarkersProps {
  /** Array of tasks to display on the map */
  tasks: Task[];
  /** Array of fields to get locations from */
  fields: Field[];
  /** Map instance ref from parent component */
  mapRef: React.RefObject<any>;
  /** Whether to enable task clustering (requires leaflet.markercluster) */
  enableClustering?: boolean;
  /** Callback when a task marker is clicked */
  onTaskClick?: (taskId: string) => void;
}

/**
 * TaskMarkers Component
 * Displays tasks as markers on the map with clustering support
 */
export function TaskMarkers({
  tasks,
  fields,
  mapRef,
  enableClustering = true,
  onTaskClick,
}: TaskMarkersProps) {
  const router = useRouter();
  const markersRef = useRef<any[]>([]);
  const clusterGroupRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window === "undefined" || !mapRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) {
      console.warn(
        "Leaflet is not loaded. Make sure it is loaded via CDN in layout.",
      );
      return;
    }

    // Create a map of field_id to field for quick lookup
    const fieldMap = new Map<string, Field>();
    fields.forEach((field) => {
      if (field.centroid) {
        fieldMap.set(field.id, field);
      }
    });

    // Clear existing markers
    if (clusterGroupRef.current) {
      mapRef.current.removeLayer(clusterGroupRef.current);
      clusterGroupRef.current = null;
    }
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    // Filter tasks that have associated fields with locations
    const tasksWithLocations = tasks.filter((task) => {
      return task.field_id && fieldMap.has(task.field_id);
    });

    if (tasksWithLocations.length === 0) return;

    // Check if MarkerClusterGroup is available
    const hasClusterSupport = enableClustering && L.markerClusterGroup;

    // Create marker cluster group if clustering is enabled and supported
    if (hasClusterSupport) {
      clusterGroupRef.current = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        iconCreateFunction: (cluster: any) => {
          const count = cluster.getChildCount();
          const markers = cluster.getAllChildMarkers();

          // Count tasks by priority in cluster
          const priorityCounts = {
            urgent: 0,
            high: 0,
            medium: 0,
            low: 0,
          };

          markers.forEach((marker: any) => {
            const priority = marker.options.taskPriority;
            if (priority && priorityCounts.hasOwnProperty(priority)) {
              priorityCounts[priority as keyof typeof priorityCounts]++;
            }
          });

          // Determine cluster color based on highest priority
          let clusterColor = PRIORITY_COLORS.low;
          if (priorityCounts.urgent > 0) clusterColor = PRIORITY_COLORS.urgent;
          else if (priorityCounts.high > 0) clusterColor = PRIORITY_COLORS.high;
          else if (priorityCounts.medium > 0)
            clusterColor = PRIORITY_COLORS.medium;

          return L.divIcon({
            html: `
              <div style="
                background-color: ${clusterColor};
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
              ">
                ${count}
              </div>
            `,
            className: "task-cluster-marker",
            iconSize: [40, 40],
          });
        },
      });
    }

    // Create markers for each task
    tasksWithLocations.forEach((task) => {
      const field = fieldMap.get(task.field_id!);
      if (!field || !field.centroid) return;

      const [lng, lat] = field.centroid.coordinates;
      const taskType = task.type || "other";
      const priority = task.priority || "low";
      const icon = TASK_TYPE_ICONS[taskType] || TASK_TYPE_ICONS.other;
      const color = PRIORITY_COLORS[priority] || PRIORITY_COLORS.low;

      // Create custom icon
      const customIcon = L.divIcon({
        html: `
          <div style="
            background-color: ${color};
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            cursor: pointer;
            position: relative;
          ">
            ${icon}
          </div>
        `,
        className: "custom-task-marker",
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      // Format due date
      const dueDate = task.due_date
        ? new Date(task.due_date).toLocaleDateString("ar-YE", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })
        : "غير محدد";

      // Check if task is overdue
      const isOverdue =
        task.due_date &&
        new Date(task.due_date) < new Date() &&
        task.status !== "completed" &&
        task.status !== "cancelled";

      // Create marker
      const marker = L.marker([lat, lng], {
        icon: customIcon,
        taskPriority: priority, // Store for cluster color calculation
      }).bindPopup(
        `
          <div style="direction: rtl; text-align: right; min-width: 250px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="border-bottom: 2px solid ${color}; padding-bottom: 8px; margin-bottom: 8px;">
              <h3 style="font-weight: bold; margin: 0 0 4px 0; font-size: 16px; color: #111;">
                ${task.title_ar || task.title}
              </h3>
              <p style="margin: 0; font-size: 12px; color: #666;">
                ${task.title}
              </p>
            </div>

            <div style="margin-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 13px; color: #666;">النوع:</span>
                <span style="font-size: 13px; font-weight: 600; color: #111;">
                  ${icon} ${TASK_TYPE_LABELS[taskType] || taskType}
                </span>
              </div>

              <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 13px; color: #666;">الحالة:</span>
                <span style="font-size: 13px; font-weight: 600; color: #111;">
                  ${STATUS_LABELS[task.status] || task.status}
                </span>
              </div>

              <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 13px; color: #666;">الأولوية:</span>
                <span style="
                  font-size: 13px;
                  font-weight: 600;
                  padding: 2px 8px;
                  border-radius: 12px;
                  background-color: ${color};
                  color: white;
                ">
                  ${priority === "urgent" ? "عاجل" : priority === "high" ? "عالية" : priority === "medium" ? "متوسطة" : "منخفضة"}
                </span>
              </div>

              <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 13px; color: #666;">الموعد النهائي:</span>
                <span style="font-size: 13px; font-weight: 600; color: ${isOverdue ? "#dc2626" : "#111"};">
                  ${dueDate}
                  ${isOverdue ? ' <span style="color: #dc2626;">⚠️ متأخر</span>' : ""}
                </span>
              </div>

              <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 13px; color: #666;">الحقل:</span>
                <span style="font-size: 13px; font-weight: 600; color: #111;">
                  ${field.nameAr || field.name}
                </span>
              </div>
            </div>

            ${
              task.description_ar || task.description
                ? `
              <div style="
                margin-top: 8px;
                padding: 8px;
                background: #f9fafb;
                border-radius: 6px;
                border-right: 3px solid ${color};
              ">
                <p style="margin: 0; font-size: 12px; color: #374151; line-height: 1.5;">
                  ${task.description_ar || task.description}
                </p>
              </div>
            `
                : ""
            }

            <button
              onclick="window.dispatchEvent(new CustomEvent('task-marker-click', { detail: '${task.id}' }))"
              style="
                width: 100%;
                margin-top: 12px;
                padding: 8px 16px;
                background: linear-gradient(to bottom, #16a34a, #15803d);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
              "
              onmouseover="this.style.transform='translateY(-1px)';this.style.boxShadow='0 2px 6px rgba(0,0,0,0.15)'"
              onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 1px 3px rgba(0,0,0,0.1)'"
            >
              عرض تفاصيل المهمة
            </button>
          </div>
        `,
        {
          maxWidth: 300,
          className: "task-marker-popup",
        },
      );

      // Add to cluster group or directly to map
      if (clusterGroupRef.current) {
        clusterGroupRef.current.addLayer(marker);
      } else {
        marker.addTo(mapRef.current);
      }

      markersRef.current.push(marker);
    });

    // Add cluster group to map
    if (clusterGroupRef.current) {
      mapRef.current.addLayer(clusterGroupRef.current);
    }

    // Handle task click from popup
    const handleTaskClick = (event: any) => {
      const taskId = event.detail;
      if (onTaskClick) {
        onTaskClick(taskId);
      } else {
        router.push(`/dashboard/tasks/${taskId}`);
      }
    };

    window.addEventListener("task-marker-click", handleTaskClick);

    // Cleanup
    return () => {
      window.removeEventListener("task-marker-click", handleTaskClick);
      if (clusterGroupRef.current) {
        mapRef.current?.removeLayer(clusterGroupRef.current);
        clusterGroupRef.current = null;
      }
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current = [];
    };
  }, [tasks, fields, mapRef, enableClustering, onTaskClick, router]);

  return null; // This component doesn't render anything directly
}

export default TaskMarkers;

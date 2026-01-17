/**
 * TaskMarkers Component Usage Example
 * مثال على استخدام مكون علامات المهام
 */

"use client";

import { useRef, useEffect } from "react";
import { TaskMarkers } from "./TaskMarkers";
import { useTasks } from "@/features/tasks/hooks/useTasks";
import { useFields } from "../hooks/useFields";
import { Loader2 } from "lucide-react";

/**
 * Example 1: Basic Usage with Map
 * Display tasks on a field map with default settings
 */
export function TaskMapExample() {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const { data: tasks = [], isLoading: tasksLoading } = useTasks();
  const { data: fields = [], isLoading: fieldsLoading } = useFields();

  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) return;

    // Initialize map if it doesn't exist
    if (!mapRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current).setView([15.5527, 48.5164], 6);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  if (tasksLoading || fieldsLoading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold">خريطة المهام</h2>
        <p className="text-sm text-gray-600">
          عرض {tasks.length} مهمة على الخريطة
        </p>
      </div>
      <div ref={mapContainerRef} className="h-96 w-full" />
      <TaskMarkers tasks={tasks} fields={fields} mapRef={mapRef} />
    </div>
  );
}

/**
 * Example 2: Without Clustering
 * Display tasks without marker clustering
 */
export function TaskMapWithoutClusteringExample() {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const { data: tasks = [] } = useTasks();
  const { data: fields = [] } = useFields();

  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) return;

    if (!mapRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current).setView([15.5527, 48.5164], 6);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
      }).addTo(map);
      mapRef.current = map;
    }
  }, []);

  return (
    <div className="h-96">
      <div ref={mapContainerRef} className="h-full w-full" />
      <TaskMarkers
        tasks={tasks}
        fields={fields}
        mapRef={mapRef}
        enableClustering={false}
      />
    </div>
  );
}

/**
 * Example 3: Filtered Tasks
 * Display only high priority tasks
 */
export function HighPriorityTaskMapExample() {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const { data: allTasks = [] } = useTasks({ priority: "high" });
  const { data: fields = [] } = useFields();

  // Filter for high priority tasks only
  const highPriorityTasks = allTasks.filter(
    (task) => task.priority === "high" || task.priority === "urgent",
  );

  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) return;

    if (!mapRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current).setView([15.5527, 48.5164], 6);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
      }).addTo(map);
      mapRef.current = map;
    }
  }, []);

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200 bg-red-50">
        <h2 className="text-lg font-semibold text-red-900">
          المهام ذات الأولوية العالية
        </h2>
        <p className="text-sm text-red-700">
          {highPriorityTasks.length} مهمة عاجلة
        </p>
      </div>
      <div ref={mapContainerRef} className="h-96 w-full" />
      <TaskMarkers tasks={highPriorityTasks} fields={fields} mapRef={mapRef} />
    </div>
  );
}

/**
 * Example 4: Custom Task Click Handler
 * Handle task clicks with custom logic
 */
export function TaskMapWithCustomClickExample() {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const { data: tasks = [] } = useTasks();
  const { data: fields = [] } = useFields();

  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L) return;

    if (!mapRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current).setView([15.5527, 48.5164], 6);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
      }).addTo(map);
      mapRef.current = map;
    }
  }, []);

  const handleTaskClick = (taskId: string) => {
    const task = tasks.find((t) => t.id === taskId);
    if (task) {
      alert(`تم النقر على المهمة: ${task.title_ar || task.title}`);
      // Add your custom logic here
      // e.g., open a modal, show a sidebar, etc.
    }
  };

  return (
    <div className="h-96">
      <div ref={mapContainerRef} className="h-full w-full" />
      <TaskMarkers
        tasks={tasks}
        fields={fields}
        mapRef={mapRef}
        onTaskClick={handleTaskClick}
      />
    </div>
  );
}

/**
 * Example 5: Field-Specific Tasks
 * Display tasks for a specific field
 */
export function FieldTaskMapExample({ fieldId }: { fieldId: string }) {
  const mapRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const { data: allTasks = [] } = useTasks({ field_id: fieldId });
  const { data: fields = [] } = useFields();

  // Filter tasks for this field
  const fieldTasks = allTasks.filter((task) => task.field_id === fieldId);
  const field = fields.find((f) => f.id === fieldId);

  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    const L = (window as typeof window & { L?: any }).L;
    if (!L || !field?.centroid) return;

    if (!mapRef.current && mapContainerRef.current) {
      const [lng, lat] = field.centroid.coordinates;
      const map = L.map(mapContainerRef.current).setView([lat, lng], 14);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
      }).addTo(map);
      mapRef.current = map;
    }
  }, [field]);

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold">
          مهام الحقل: {field?.nameAr || field?.name}
        </h2>
        <p className="text-sm text-gray-600">{fieldTasks.length} مهمة</p>
      </div>
      <div ref={mapContainerRef} className="h-96 w-full" />
      <TaskMarkers
        tasks={fieldTasks}
        fields={fields}
        mapRef={mapRef}
        enableClustering={false} // Disable clustering for single field view
      />
    </div>
  );
}

"use client";

/**
 * SAHOOL AlertsPanel Example Usage
 * مثال على استخدام مكون لوحة التنبيهات
 */

import React, { useState } from "react";
import { AlertsPanel, type FieldAlert } from "./AlertsPanel";
import type { TaskFormData } from "@/features/tasks/types";

// Mock alerts data
const mockAlerts: FieldAlert[] = [
  {
    id: "alert-1",
    fieldId: "field-123",
    type: "ndvi_drop",
    severity: "critical",
    title: "انخفاض حاد في مؤشر NDVI",
    message:
      "تم رصد انخفاض بنسبة 25% في مؤشر NDVI خلال الأسبوع الماضي. قد يشير ذلك إلى مشكلة في صحة المحصول.",
    data: {
      current_value: 0.45,
      previous_value: 0.6,
      drop_percentage: 25,
      affected_area: "2.5 هكتار",
      detection_date: "2024-01-15",
    },
    createdAt: new Date("2024-01-15T10:30:00"),
    acknowledged: false,
  },
  {
    id: "alert-2",
    fieldId: "field-123",
    type: "weather_warning",
    severity: "warning",
    title: "تحذير من صقيع متوقع",
    message:
      "من المتوقع انخفاض درجات الحرارة إلى ما دون الصفر خلال الليلة القادمة. يُنصح باتخاذ إجراءات وقائية.",
    data: {
      expected_temp: "-2°C",
      probability: "85%",
      start_time: "2024-01-16 02:00",
      end_time: "2024-01-16 06:00",
      recommendation: "استخدام أغطية الحماية من الصقيع",
    },
    createdAt: new Date("2024-01-15T14:20:00"),
    acknowledged: false,
  },
  {
    id: "alert-3",
    fieldId: "field-123",
    type: "soil_moisture",
    severity: "warning",
    title: "انخفاض في رطوبة التربة",
    message:
      "مستوى رطوبة التربة أقل من المستوى الموصى به. يُنصح بالري في أقرب وقت ممكن.",
    data: {
      current_moisture: "15%",
      optimal_range: "25-35%",
      last_irrigation: "2024-01-10",
      days_since_irrigation: 5,
      recommendation: "ري فوري مطلوب",
    },
    createdAt: new Date("2024-01-14T08:15:00"),
    acknowledged: false,
  },
  {
    id: "alert-4",
    fieldId: "field-123",
    type: "task_overdue",
    severity: "critical",
    title: "مهمة التسميد متأخرة",
    message:
      'مهمة "تسميد القمح - المرحلة الثانية" متأخرة بثلاثة أيام. يجب إتمامها في أقرب وقت.',
    data: {
      task_id: "task-567",
      task_title: "تسميد القمح - المرحلة الثانية",
      due_date: "2024-01-12",
      days_overdue: 3,
      assigned_to: "أحمد محمد",
      priority: "عالية",
    },
    createdAt: new Date("2024-01-15T06:00:00"),
    acknowledged: false,
  },
  {
    id: "alert-5",
    fieldId: "field-123",
    type: "weather_warning",
    severity: "info",
    title: "توقعات بأمطار خفيفة",
    message:
      "من المتوقع هطول أمطار خفيفة خلال 24 ساعة القادمة. قد تساعد في تحسين رطوبة التربة.",
    data: {
      expected_rainfall: "5-10 mm",
      probability: "70%",
      start_time: "2024-01-16 18:00",
      duration: "3-4 ساعات",
      impact: "إيجابي - تحسن رطوبة التربة",
    },
    createdAt: new Date("2024-01-14T16:45:00"),
    acknowledged: true,
  },
];

export const AlertsPanelExample: React.FC = () => {
  const [alerts, setAlerts] = useState<FieldAlert[]>(mockAlerts);

  // Handle alert dismissal
  const handleDismiss = async (alertId: string) => {
    console.log("Dismissing alert:", alertId);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    // Update alert state
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert,
      ),
    );
  };

  // Handle task creation
  const handleCreateTask = async (data: TaskFormData) => {
    console.log("Creating task from alert:", data);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    window.alert("تم إنشاء المهمة بنجاح!");
  };

  // Handle view details
  const handleViewDetails = (alertItem: FieldAlert) => {
    console.log("Viewing alert details:", alertItem);
    window.alert(`عرض تفاصيل التنبيه: ${alertItem.title}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            لوحة تنبيهات الحقل - مثال توضيحي
          </h1>
          <p className="text-gray-600">
            هذا مثال على استخدام مكون AlertsPanel مع بيانات تجريبية
          </p>
        </div>

        {/* Example 1: With WebSocket */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            مثال 1: مع WebSocket (التحديثات الفورية)
          </h2>
          <AlertsPanel
            fieldId="field-123"
            alerts={alerts}
            onDismiss={handleDismiss}
            onCreateTask={handleCreateTask}
            onViewDetails={handleViewDetails}
            enableWebSocket={true}
            wsUrl="ws://localhost:3001/field-alerts"
          />
        </div>

        {/* Example 2: With Polling */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            مثال 2: مع التحديث الدوري (Polling)
          </h2>
          <AlertsPanel
            fieldId="field-123"
            alerts={alerts}
            onDismiss={handleDismiss}
            onCreateTask={handleCreateTask}
            onViewDetails={handleViewDetails}
            enableWebSocket={false}
            pollingInterval={30000} // 30 seconds
          />
        </div>

        {/* Example 3: Minimal (no real-time updates) */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            مثال 3: بسيط (بدون تحديثات فورية)
          </h2>
          <AlertsPanel
            fieldId="field-123"
            alerts={alerts}
            onDismiss={handleDismiss}
            onCreateTask={handleCreateTask}
            onViewDetails={handleViewDetails}
          />
        </div>
      </div>
    </div>
  );
};

export default AlertsPanelExample;

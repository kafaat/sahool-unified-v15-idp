# Action Windows Integration Examples

# أمثلة دمج نوافذ العمل

## Example 1: Simple Integration

```tsx
// pages/fields/[fieldId]/action-windows.tsx
import {
  SprayWindowsPanel,
  IrrigationWindowsPanel,
} from "@/features/action-windows";

export default function FieldActionWindowsPage({
  params,
}: {
  params: { fieldId: string };
}) {
  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Spray Windows */}
      <SprayWindowsPanel
        fieldId={params.fieldId}
        days={7}
        showTimeline={true}
      />

      {/* Irrigation Windows */}
      <IrrigationWindowsPanel
        fieldId={params.fieldId}
        days={7}
        showTimeline={true}
      />
    </div>
  );
}
```

## Example 2: With Task Creation

```tsx
// pages/fields/[fieldId]/recommendations.tsx
import { useState } from "react";
import {
  SprayWindowsPanel,
  IrrigationWindowsPanel,
} from "@/features/action-windows";
import { useCreateTask } from "@/features/tasks/hooks/useTasks";
import type { SprayWindow, IrrigationWindow } from "@/features/action-windows";
import type { TaskFormData } from "@/features/tasks/types";
import { toast } from "sonner"; // Or your toast library

export default function FieldRecommendationsPage({
  params,
}: {
  params: { fieldId: string };
}) {
  const createTask = useCreateTask();

  const handleCreateSprayTask = async (window: SprayWindow) => {
    const taskData: TaskFormData = {
      title: `Spray Application`,
      title_ar: `رش المبيدات`,
      description: `Optimal spray window: ${new Date(window.startTime).toLocaleString()}`,
      description_ar: `نافذة رش مثالية: ${new Date(window.startTime).toLocaleString("ar-EG")}`,
      due_date: window.startTime,
      priority: window.score >= 90 ? "high" : "medium",
      field_id: params.fieldId,
      status: "open",
    };

    try {
      await createTask.mutateAsync(taskData);
      toast.success("تم إنشاء مهمة الرش بنجاح");
    } catch (error) {
      toast.error("فشل إنشاء مهمة الرش");
    }
  };

  const handleCreateIrrigationTask = async (window: IrrigationWindow) => {
    const taskData: TaskFormData = {
      title: `Irrigation - ${window.waterAmount}mm`,
      title_ar: `ري - ${window.waterAmount}ملم`,
      description: `${window.reason}\nWater: ${window.waterAmount}mm, Duration: ${window.duration}h`,
      description_ar: `${window.reasonAr}\nالماء: ${window.waterAmount}ملم، المدة: ${window.duration}س`,
      due_date: window.startTime,
      priority:
        window.priority === "urgent" || window.priority === "high"
          ? "high"
          : "medium",
      field_id: params.fieldId,
      status: "open",
    };

    try {
      await createTask.mutateAsync(taskData);
      toast.success("تم إنشاء مهمة الري بنجاح");
    } catch (error) {
      toast.error("فشل إنشاء مهمة الري");
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      <h1 className="text-3xl font-bold" dir="rtl">
        توصيات العمل
      </h1>

      <SprayWindowsPanel
        fieldId={params.fieldId}
        days={7}
        onCreateTask={handleCreateSprayTask}
        showTimeline={true}
      />

      <IrrigationWindowsPanel
        fieldId={params.fieldId}
        days={7}
        onCreateTask={handleCreateIrrigationTask}
        showTimeline={true}
      />
    </div>
  );
}
```

## Example 3: Complete Demo with Tabs

```tsx
// pages/fields/[fieldId]/windows.tsx
import { ActionWindowsDemo } from "@/features/action-windows";

export default function FieldWindowsPage({
  params,
}: {
  params: { fieldId: string };
}) {
  // Fetch field data
  const { data: field } = useField(params.fieldId);

  if (!field) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mx-auto p-6">
      <ActionWindowsDemo
        fieldId={params.fieldId}
        fieldName={field.name}
        fieldNameAr={field.name_ar}
        days={7}
      />
    </div>
  );
}
```

## Example 4: Using Hooks Directly

```tsx
// components/FieldDashboard.tsx
import {
  useSprayWindows,
  useIrrigationWindows,
  useActionRecommendations,
} from "@/features/action-windows";

export function FieldDashboard({ fieldId }: { fieldId: string }) {
  const { data: sprayWindows, isLoading: sprayLoading } = useSprayWindows({
    fieldId,
    days: 7,
    criteria: {
      windSpeedMax: 12,
      temperatureMax: 28,
    },
  });

  const { data: irrigationWindows, isLoading: irrigLoading } =
    useIrrigationWindows({
      fieldId,
      days: 7,
    });

  const { data: recommendations } = useActionRecommendations({
    fieldId,
    actionTypes: ["spray", "irrigate"],
    days: 7,
  });

  // Custom rendering logic
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Spray Summary */}
      <div className="bg-white rounded-lg p-6 border">
        <h3 className="text-xl font-bold mb-4" dir="rtl">
          نوافذ الرش
        </h3>
        {sprayLoading ? (
          <p>Loading...</p>
        ) : (
          <div>
            <p dir="rtl">
              نوافذ مثالية:{" "}
              {sprayWindows?.filter((w) => w.status === "optimal").length}
            </p>
            <p dir="rtl">إجمالي النوافذ: {sprayWindows?.length}</p>
          </div>
        )}
      </div>

      {/* Irrigation Summary */}
      <div className="bg-white rounded-lg p-6 border">
        <h3 className="text-xl font-bold mb-4" dir="rtl">
          نوافذ الري
        </h3>
        {irrigLoading ? (
          <p>Loading...</p>
        ) : (
          <div>
            <p dir="rtl">
              عاجل:{" "}
              {irrigationWindows?.filter((w) => w.priority === "urgent").length}
            </p>
            <p dir="rtl">إجمالي النوافذ: {irrigationWindows?.length}</p>
          </div>
        )}
      </div>

      {/* Recommendations */}
      <div className="col-span-full bg-white rounded-lg p-6 border">
        <h3 className="text-xl font-bold mb-4" dir="rtl">
          التوصيات العاجلة
        </h3>
        <div className="space-y-2">
          {recommendations
            ?.filter((r) => r.priority === "urgent" || r.priority === "high")
            .map((rec) => (
              <div
                key={rec.id}
                className="p-4 bg-orange-50 rounded-lg"
                dir="rtl"
              >
                <p className="font-semibold">{rec.titleAr}</p>
                <p className="text-sm text-gray-600">{rec.descriptionAr}</p>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
```

## Example 5: Custom Spray Criteria

```tsx
// pages/fields/[fieldId]/custom-spray.tsx
import { useState } from "react";
import { SprayWindowsPanel } from "@/features/action-windows";
import type { SprayWindowCriteria } from "@/features/action-windows";

export default function CustomSprayPage({
  params,
}: {
  params: { fieldId: string };
}) {
  const [criteria, setCriteria] = useState<Partial<SprayWindowCriteria>>({
    windSpeedMax: 15,
    windSpeedMin: 3,
    temperatureMin: 10,
    temperatureMax: 30,
    humidityMin: 50,
    humidityMax: 90,
    rainProbabilityMax: 20,
    minDuration: 2,
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Criteria Form */}
      <div className="bg-white rounded-lg p-6 border">
        <h2 className="text-xl font-bold mb-4" dir="rtl">
          معايير الرش المخصصة
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1" dir="rtl">
              سرعة الرياح القصوى (كم/س)
            </label>
            <input
              type="number"
              value={criteria.windSpeedMax}
              onChange={(e) =>
                setCriteria({
                  ...criteria,
                  windSpeedMax: Number(e.target.value),
                })
              }
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1" dir="rtl">
              درجة الحرارة القصوى (°م)
            </label>
            <input
              type="number"
              value={criteria.temperatureMax}
              onChange={(e) =>
                setCriteria({
                  ...criteria,
                  temperatureMax: Number(e.target.value),
                })
              }
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          {/* Add more controls as needed */}
        </div>
      </div>

      {/* Spray Windows with Custom Criteria */}
      <SprayWindowsPanel
        fieldId={params.fieldId}
        days={7}
        criteria={criteria}
        showTimeline={true}
      />
    </div>
  );
}
```

## Example 6: Dashboard Widget

```tsx
// components/widgets/ActionWindowsWidget.tsx
import {
  useOptimalSprayWindows,
  useUrgentIrrigationWindows,
} from "@/features/action-windows";
import { Calendar, Droplets } from "lucide-react";

export function ActionWindowsWidget({ fieldId }: { fieldId: string }) {
  const { data: optimalSpray } = useOptimalSprayWindows({ fieldId, days: 3 });
  const { data: urgentIrrigation } = useUrgentIrrigationWindows({
    fieldId,
    days: 3,
  });

  return (
    <div className="bg-white rounded-lg border p-4 space-y-4">
      <h3 className="font-bold text-lg" dir="rtl">
        نوافذ العمل القادمة
      </h3>

      {/* Optimal Spray Windows */}
      {optimalSpray && optimalSpray.length > 0 && (
        <div className="bg-green-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2" dir="rtl">
            <Calendar className="w-4 h-4 text-green-700" />
            <span className="font-semibold text-green-900">
              نوافذ رش مثالية
            </span>
          </div>
          <p className="text-sm text-green-800" dir="rtl">
            {optimalSpray.length} نافذة متاحة في الأيام القادمة
          </p>
        </div>
      )}

      {/* Urgent Irrigation */}
      {urgentIrrigation && urgentIrrigation.length > 0 && (
        <div className="bg-red-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2" dir="rtl">
            <Droplets className="w-4 h-4 text-red-700" />
            <span className="font-semibold text-red-900">ري عاجل مطلوب</span>
          </div>
          <p className="text-sm text-red-800" dir="rtl">
            {urgentIrrigation.length} حقل يحتاج إلى ري فوري
          </p>
        </div>
      )}
    </div>
  );
}
```

## Example 7: With Error Handling

```tsx
// pages/fields/[fieldId]/actions.tsx
import { useState } from "react";
import { SprayWindowsPanel } from "@/features/action-windows";
import { useCreateTask } from "@/features/tasks/hooks/useTasks";
import { AlertCircle, CheckCircle2 } from "lucide-react";
import type { SprayWindow } from "@/features/action-windows";

export default function FieldActionsPage({
  params,
}: {
  params: { fieldId: string };
}) {
  const [feedback, setFeedback] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);
  const createTask = useCreateTask();

  const handleCreateTask = async (window: SprayWindow) => {
    try {
      setFeedback(null);

      await createTask.mutateAsync({
        title: `Spray - ${new Date(window.startTime).toLocaleDateString()}`,
        title_ar: `رش - ${new Date(window.startTime).toLocaleDateString("ar-EG")}`,
        description: `Spray window score: ${window.score}/100`,
        description_ar: `نتيجة نافذة الرش: ${window.score}/100`,
        due_date: window.startTime,
        priority: window.score >= 90 ? "high" : "medium",
        field_id: params.fieldId,
        status: "open",
      });

      setFeedback({
        type: "success",
        message: "تم إنشاء مهمة الرش بنجاح",
      });

      setTimeout(() => setFeedback(null), 5000);
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "فشل إنشاء المهمة",
      });
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Feedback Message */}
      {feedback && (
        <div
          className={`rounded-lg p-4 flex items-center gap-3 ${
            feedback.type === "success"
              ? "bg-green-50 border border-green-200"
              : "bg-red-50 border border-red-200"
          }`}
        >
          {feedback.type === "success" ? (
            <CheckCircle2 className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-600" />
          )}
          <p
            className={`font-medium ${
              feedback.type === "success" ? "text-green-800" : "text-red-800"
            }`}
            dir="rtl"
          >
            {feedback.message}
          </p>
        </div>
      )}

      <SprayWindowsPanel
        fieldId={params.fieldId}
        days={7}
        onCreateTask={handleCreateTask}
        showTimeline={true}
      />
    </div>
  );
}
```

## Notes

- All components are fully bilingual (English/Arabic)
- Task creation is integrated with the existing tasks API
- Error handling should be implemented in production
- Loading states are handled by React Query
- All components are accessible (ARIA labels, keyboard navigation)
- Responsive design works on all screen sizes

/**
 * Fields Feature - Usage Examples
 * أمثلة على استخدام ميزة الحقول
 *
 * This file demonstrates how to use the updated fields hooks with real API
 */

"use client";

import {
  useFields,
  useField,
  useCreateField,
  useUpdateField,
  useDeleteField,
  useFieldStats,
} from "../hooks/useFields";
import { useAuth } from "@/stores/auth.store";
import type { FieldFormData } from "../types";
import { logger } from "@/lib/logger";
import { AstralFieldWidget } from "../components/AstralFieldWidget";

/**
 * Example 1: Fetching all fields
 */
export function FieldsListExample() {
  const { data: fields, isLoading, error } = useFields();

  if (isLoading) return <div>جاري التحميل... / Loading...</div>;
  if (error) return <div>خطأ في التحميل / Error loading fields</div>;

  return (
    <div>
      <h2>الحقول / Fields</h2>
      <ul>
        {fields?.map((field) => (
          <li key={field.id}>
            {field.nameAr} / {field.name} - {field.area} هكتار
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Example 2: Fetching fields with filters
 */
export function FilteredFieldsExample() {
  const { data: fields } = useFields({
    search: "wheat",
    minArea: 2,
    maxArea: 10,
    status: "active",
  });

  return (
    <div>
      <h2>حقول القمح / Wheat Fields</h2>
      {fields?.map((field) => (
        <div key={field.id}>{field.nameAr}</div>
      ))}
    </div>
  );
}

/**
 * Example 3: Fetching a single field
 */
export function FieldDetailsExample({ fieldId }: { fieldId: string }) {
  const { data: field, isLoading, error } = useField(fieldId);

  if (isLoading) return <div>جاري التحميل...</div>;
  if (error) return <div>خطأ: {error.message}</div>;
  if (!field) return <div>الحقل غير موجود / Field not found</div>;

  return (
    <div>
      <h2>
        {field.nameAr} / {field.name}
      </h2>
      <p>المساحة / Area: {field.area} هكتار</p>
      <p>
        المحصول / Crop: {field.cropAr} / {field.crop}
      </p>
      <p>الوصف / Description: {field.descriptionAr || field.description}</p>
    </div>
  );
}

/**
 * Example 4: Creating a new field
 */
export function CreateFieldExample() {
  const { user } = useAuth();
  const createField = useCreateField();

  const handleCreateField = async () => {
    const newField: FieldFormData = {
      name: "New Field",
      nameAr: "حقل جديد",
      area: 5.5,
      crop: "Wheat",
      cropAr: "قمح",
      description: "A new field for wheat cultivation",
      descriptionAr: "حقل جديد لزراعة القمح",
      polygon: {
        type: "Polygon",
        coordinates: [
          [
            [44.2, 15.3],
            [44.21, 15.3],
            [44.21, 15.31],
            [44.2, 15.31],
            [44.2, 15.3],
          ],
        ],
      },
    };

    try {
      await createField.mutateAsync({
        data: newField,
        tenantId: user?.tenant_id,
      });
      alert("تم إنشاء الحقل بنجاح / Field created successfully!");
    } catch (error) {
      const err = error as Error;
      try {
        const errorData = JSON.parse(err.message);
        alert(`خطأ: ${errorData.messageAr}\nError: ${errorData.message}`);
      } catch {
        alert(`خطأ: ${err.message}`);
      }
    }
  };

  return (
    <button onClick={handleCreateField} disabled={createField.isPending}>
      {createField.isPending
        ? "جاري الإنشاء..."
        : "إنشاء حقل جديد / Create New Field"}
    </button>
  );
}

/**
 * Example 5: Updating a field
 */
export function UpdateFieldExample({ fieldId }: { fieldId: string }) {
  const { user } = useAuth();
  const updateField = useUpdateField();

  const handleUpdateField = async () => {
    try {
      await updateField.mutateAsync({
        id: fieldId,
        data: {
          crop: "Barley",
          cropAr: "شعير",
          area: 6.0,
        },
        tenantId: user?.tenant_id,
      });
      alert("تم تحديث الحقل بنجاح / Field updated successfully!");
    } catch (error) {
      const err = error as Error;
      try {
        const errorData = JSON.parse(err.message);
        alert(`خطأ: ${errorData.messageAr}\nError: ${errorData.message}`);
      } catch {
        alert(`خطأ: ${err.message}`);
      }
    }
  };

  return (
    <button onClick={handleUpdateField} disabled={updateField.isPending}>
      {updateField.isPending ? "جاري التحديث..." : "تحديث الحقل / Update Field"}
    </button>
  );
}

/**
 * Example 6: Deleting a field
 */
export function DeleteFieldExample({ fieldId }: { fieldId: string }) {
  const deleteField = useDeleteField();

  const handleDeleteField = async () => {
    if (
      !confirm(
        "هل أنت متأكد من حذف هذا الحقل؟ / Are you sure you want to delete this field?",
      )
    ) {
      return;
    }

    try {
      await deleteField.mutateAsync(fieldId);
      alert("تم حذف الحقل بنجاح / Field deleted successfully!");
    } catch (error) {
      const err = error as Error;
      try {
        const errorData = JSON.parse(err.message);
        alert(`خطأ: ${errorData.messageAr}\nError: ${errorData.message}`);
      } catch {
        alert(`خطأ: ${err.message}`);
      }
    }
  };

  return (
    <button
      onClick={handleDeleteField}
      disabled={deleteField.isPending}
      className="text-red-600"
    >
      {deleteField.isPending ? "جاري الحذف..." : "حذف الحقل / Delete Field"}
    </button>
  );
}

/**
 * Example 7: Fetching field statistics
 */
export function FieldStatsExample() {
  const { user } = useAuth();
  const { data: stats, isLoading } = useFieldStats(user?.tenant_id);

  if (isLoading) return <div>جاري تحميل الإحصائيات...</div>;

  return (
    <div>
      <h2>إحصائيات الحقول / Field Statistics</h2>
      <p>إجمالي الحقول / Total Fields: {stats?.total}</p>
      <p>إجمالي المساحة / Total Area: {stats?.totalArea} هكتار</p>
      <div>
        <h3>المحاصيل / Crops:</h3>
        <ul>
          {Object.entries(stats?.byCrop || {}).map(([crop, count]) => (
            <li key={crop}>
              {crop}: {count}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

/**
 * Example 8: Using Astral Field Widget
 */
export function AstralFieldWidgetExample({ fieldId }: { fieldId: string }) {
  const { data: field } = useField(fieldId);
  // createField hook available via useCreateField() when needed for task creation

  const handleCreateTask = async (taskData: {
    title: string;
    title_ar: string;
    description: string;
    description_ar: string;
    due_date: string;
    field_id: string;
    priority: "high" | "medium" | "low";
  }) => {
    logger.info("Creating task from astronomical recommendation:", taskData);
    // Here you would call your task creation API
    alert(
      `مهمة جديدة: ${taskData.title_ar}\nNew task: ${taskData.title}\nموعد التنفيذ: ${taskData.due_date}`,
    );
  };

  if (!field) return <div>جاري التحميل...</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">
        التقويم الفلكي للحقل: {field.nameAr}
      </h2>
      <AstralFieldWidget
        field={field}
        onCreateTask={handleCreateTask}
        compact={false}
      />
    </div>
  );
}

/**
 * Example 9: Complete CRUD example with error handling
 */
export function FieldsCRUDExample() {
  const { user } = useAuth();
  const { data: fields, isLoading, error } = useFields();
  // Note: createField available via useCreateField() when needed
  const updateField = useUpdateField();
  const deleteField = useDeleteField();

  // Handle API errors with fallback to mock data
  if (error) {
    logger.warn("API error, displaying cached/mock data:", error);
  }

  // Show loading state
  if (isLoading) {
    return <div className="text-center">جاري التحميل... / Loading...</div>;
  }

  return (
    <div>
      <h1>إدارة الحقول / Field Management</h1>

      {/* Display error banner if API failed but we have fallback data */}
      {error && fields && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          <p>
            تحذير: يتم استخدام البيانات المحفوظة. الاتصال بالخادم غير متاح.
            <br />
            Warning: Using cached data. Server connection unavailable.
          </p>
        </div>
      )}

      {/* Fields list */}
      <div className="grid gap-4">
        {fields?.map((field) => (
          <div key={field.id} className="border p-4 rounded">
            <h3>
              {field.nameAr} / {field.name}
            </h3>
            <p>المساحة / Area: {field.area} هكتار</p>
            <p>
              المحصول / Crop: {field.cropAr} / {field.crop}
            </p>

            {/* Action buttons */}
            <div className="mt-2 space-x-2">
              <button
                onClick={() =>
                  updateField.mutate({
                    id: field.id,
                    data: { area: field.area + 1 },
                    tenantId: user?.tenant_id,
                  })
                }
                disabled={updateField.isPending}
              >
                تحديث / Update
              </button>
              <button
                onClick={() => deleteField.mutate(field.id)}
                disabled={deleteField.isPending}
                className="text-red-600"
              >
                حذف / Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Tasks Feature - Mock Data (Development Fallback)
 * بيانات وهمية للمهام
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type { Task } from "./types";

export const MOCK_TASKS: Task[] = [
  {
    id: "1",
    tenant_id: "mock-tenant",
    field_id: "field-1",
    farm_id: "farm-1",
    title: "Irrigate Field #1",
    title_ar: "ري الحقل رقم 1",
    description: "Complete irrigation for field #1",
    description_ar: "إكمال ري الحقل رقم 1",
    status: "open",
    priority: "high",
    type: "irrigation",
    due_date: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
    assigned_to: "user-1",
    evidence_photos: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
  {
    id: "2",
    tenant_id: "mock-tenant",
    field_id: "field-2",
    farm_id: "farm-1",
    title: "Fertilize Field #2",
    title_ar: "تسميد الحقل رقم 2",
    description: "Apply fertilizer to field #2",
    description_ar: "تطبيق السماد على الحقل رقم 2",
    status: "in_progress",
    priority: "medium",
    type: "fertilization",
    due_date: new Date(Date.now() + 1000 * 60 * 60 * 48).toISOString(),
    assigned_to: "user-2",
    evidence_photos: [],
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
  },
  {
    id: "3",
    tenant_id: "mock-tenant",
    field_id: "field-3",
    farm_id: "farm-1",
    title: "Pest Inspection",
    title_ar: "فحص الآفات",
    description: "Check for pests in field #3",
    description_ar: "فحص الآفات في الحقل رقم 3",
    status: "completed",
    priority: "low",
    type: "inspection",
    due_date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    assigned_to: "user-1",
    evidence_photos: [],
    completed_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
  },
];

/**
 * Equipment Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة المعدات
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

import type { Equipment } from "@/types";

type EquipmentType = "tractor" | "harvester" | "pump" | "sprayer" | "drone";
type EquipmentStatus = "operational" | "maintenance" | "idle" | "broken";

interface EquipmentItem extends Equipment {
  farm_name?: string;
  farm_id?: string;
  nameAr?: string;
  last_maintenance_date?: string;
  next_maintenance_date?: string;
}

export const MOCK_FARMS_LIST = [
  { id: "farm-1", name: "مزرعة ١" },
  { id: "farm-2", name: "مزرعة ٢" },
  { id: "farm-3", name: "مزرعة ٣" },
  { id: "farm-4", name: "مزرعة ٤" },
  { id: "farm-5", name: "مزرعة ٥" },
];

export const MOCK_EQUIPMENT: EquipmentItem[] = [
  { id: "eq-1", name: "John Deere 5075E", nameAr: "جرار جون ديري 5075E", type: "tractor", status: "operational", farm_name: "مزرعة ١", farm_id: "farm-1", lastMaintenance: "2025-12-20T00:00:00Z", nextMaintenance: "2026-03-20T00:00:00Z", last_maintenance_date: "2025-12-20T00:00:00Z", next_maintenance_date: "2026-03-20T00:00:00Z", fuelLevel: 75, hoursUsed: 1240 },
  { id: "eq-2", name: "Kubota M7060", nameAr: "جرار كوبوتا M7060", type: "tractor", status: "operational", farm_name: "مزرعة ٣", farm_id: "farm-3", lastMaintenance: "2025-11-15T00:00:00Z", nextMaintenance: "2026-02-15T00:00:00Z", last_maintenance_date: "2025-11-15T00:00:00Z", next_maintenance_date: "2026-02-15T00:00:00Z", fuelLevel: 60, hoursUsed: 890 },
  { id: "eq-3", name: "CLAAS Lexion 770", nameAr: "حصادة كلاس لكسيون 770", type: "harvester", status: "idle", farm_name: "مزرعة ١", farm_id: "farm-1", lastMaintenance: "2025-10-05T00:00:00Z", nextMaintenance: "2026-04-05T00:00:00Z", last_maintenance_date: "2025-10-05T00:00:00Z", next_maintenance_date: "2026-04-05T00:00:00Z", fuelLevel: 90, hoursUsed: 560 },
  { id: "eq-4", name: "Grundfos SP 30-8", nameAr: "مضخة جروندفوس SP 30-8", type: "pump", status: "operational", farm_name: "مزرعة ٢", farm_id: "farm-2", lastMaintenance: "2026-01-10T00:00:00Z", nextMaintenance: "2026-04-10T00:00:00Z", last_maintenance_date: "2026-01-10T00:00:00Z", next_maintenance_date: "2026-04-10T00:00:00Z", hoursUsed: 3200 },
  { id: "eq-5", name: "DJI Agras T40", nameAr: "طائرة دي جي آي أجراس T40", type: "drone", status: "maintenance", farm_name: "مزرعة ٤", farm_id: "farm-4", lastMaintenance: "2026-02-01T00:00:00Z", nextMaintenance: "2026-02-20T00:00:00Z", last_maintenance_date: "2026-02-01T00:00:00Z", next_maintenance_date: "2026-02-20T00:00:00Z", hoursUsed: 120 },
  { id: "eq-6", name: "STIHL SR 450", nameAr: "رشاش شتيل SR 450", type: "sprayer", status: "operational", farm_name: "مزرعة ٥", farm_id: "farm-5", lastMaintenance: "2025-12-28T00:00:00Z", nextMaintenance: "2026-03-28T00:00:00Z", last_maintenance_date: "2025-12-28T00:00:00Z", next_maintenance_date: "2026-03-28T00:00:00Z", hoursUsed: 450 },
  { id: "eq-7", name: "New Holland T6.180", nameAr: "جرار نيو هولاند T6.180", type: "tractor", status: "broken", farm_name: "مزرعة ٢", farm_id: "farm-2", lastMaintenance: "2025-09-15T00:00:00Z", nextMaintenance: "2025-12-15T00:00:00Z", last_maintenance_date: "2025-09-15T00:00:00Z", next_maintenance_date: "2025-12-15T00:00:00Z", fuelLevel: 20, hoursUsed: 2800 },
  { id: "eq-8", name: "Hardi Commander 6600", nameAr: "رشاش هاردي كوماندر 6600", type: "sprayer", status: "operational", farm_name: "مزرعة ١", farm_id: "farm-1", lastMaintenance: "2026-01-20T00:00:00Z", nextMaintenance: "2026-04-20T00:00:00Z", last_maintenance_date: "2026-01-20T00:00:00Z", next_maintenance_date: "2026-04-20T00:00:00Z", hoursUsed: 680 },
  { id: "eq-9", name: "Submersible Pump 15HP", nameAr: "مضخة غاطسة 15 حصان", type: "pump", status: "maintenance", farm_name: "مزرعة ٣", farm_id: "farm-3", lastMaintenance: "2026-02-05T00:00:00Z", nextMaintenance: "2026-02-25T00:00:00Z", last_maintenance_date: "2026-02-05T00:00:00Z", next_maintenance_date: "2026-02-25T00:00:00Z", hoursUsed: 5100 },
  { id: "eq-10", name: "DJI Matrice 350 RTK", nameAr: "طائرة دي جي آي ماتريس 350", type: "drone", status: "operational", farm_name: "مزرعة ٥", farm_id: "farm-5", lastMaintenance: "2026-01-25T00:00:00Z", nextMaintenance: "2026-04-25T00:00:00Z", last_maintenance_date: "2026-01-25T00:00:00Z", next_maintenance_date: "2026-04-25T00:00:00Z", hoursUsed: 85 },
  { id: "eq-11", name: "Case IH 2150", nameAr: "حصادة كيس 2150", type: "harvester", status: "idle", farm_name: "مزرعة ٤", farm_id: "farm-4", lastMaintenance: "2025-11-20T00:00:00Z", nextMaintenance: "2026-05-20T00:00:00Z", last_maintenance_date: "2025-11-20T00:00:00Z", next_maintenance_date: "2026-05-20T00:00:00Z", fuelLevel: 85, hoursUsed: 420 },
  { id: "eq-12", name: "Grundfos CR 32-6", nameAr: "مضخة جروندفوس CR 32-6", type: "pump", status: "operational", farm_name: "مزرعة ٤", farm_id: "farm-4", lastMaintenance: "2026-01-05T00:00:00Z", nextMaintenance: "2026-04-05T00:00:00Z", last_maintenance_date: "2026-01-05T00:00:00Z", next_maintenance_date: "2026-04-05T00:00:00Z", hoursUsed: 2100 },
];

export const EQUIPMENT_TYPES: { value: EquipmentType; label: string; labelEn: string }[] = [
  { value: "tractor", label: "جرار", labelEn: "Tractor" },
  { value: "harvester", label: "حصادة", labelEn: "Harvester" },
  { value: "pump", label: "مضخة", labelEn: "Pump" },
  { value: "sprayer", label: "رشاش", labelEn: "Sprayer" },
  { value: "drone", label: "طائرة بدون طيار", labelEn: "Drone" },
];

export const EQUIPMENT_STATUSES: { value: EquipmentStatus; label: string; labelEn: string }[] = [
  { value: "operational", label: "تعمل", labelEn: "Operational" },
  { value: "maintenance", label: "صيانة", labelEn: "Maintenance" },
  { value: "idle", label: "متوقفة", labelEn: "Idle" },
  { value: "broken", label: "معطلة", labelEn: "Broken" },
];

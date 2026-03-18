"use client";

// Equipment Management Page
// صفحة إدارة المعدات

import { useEffect, useState, useMemo, useCallback } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";
import { API_URLS } from "@/config/api";
import { logger } from "@/lib/logger";
import type { Equipment } from "@/types";
import {
  Search,
  Plus,
  RefreshCw,
  Download,
  Wrench,
  Tractor,
  Droplets,
  SprayCan,
  Plane,
  CheckCircle2,
  AlertTriangle,
  PauseCircle,
  XCircle,
  X,
  Calendar,
  Eye,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// أنواع البيانات
// ═══════════════════════════════════════════════════════════════════════════

type EquipmentType = "tractor" | "harvester" | "pump" | "sprayer" | "drone";
type EquipmentStatus = "operational" | "maintenance" | "idle" | "broken";

interface EquipmentItem extends Equipment {
  farm_name?: string;
  farm_id?: string;
  nameAr?: string;
  last_maintenance_date?: string;
  next_maintenance_date?: string;
}

interface CreateEquipmentPayload {
  name: string;
  nameAr: string;
  type: EquipmentType;
  status: EquipmentStatus;
  farm_name: string;
  farm_id: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants (inline - always needed for UI rendering)
// الثوابت (مضمنة - مطلوبة دائماً لعرض الواجهة)
// ═══════════════════════════════════════════════════════════════════════════

const EQUIPMENT_TYPES: { value: EquipmentType; label: string; labelEn: string }[] = [
  { value: "tractor", label: "جرار", labelEn: "Tractor" },
  { value: "harvester", label: "حصادة", labelEn: "Harvester" },
  { value: "pump", label: "مضخة", labelEn: "Pump" },
  { value: "sprayer", label: "رشاش", labelEn: "Sprayer" },
  { value: "drone", label: "طائرة بدون طيار", labelEn: "Drone" },
];

const EQUIPMENT_STATUSES: { value: EquipmentStatus; label: string; labelEn: string }[] = [
  { value: "operational", label: "تعمل", labelEn: "Operational" },
  { value: "maintenance", label: "صيانة", labelEn: "Maintenance" },
  { value: "idle", label: "متوقفة", labelEn: "Idle" },
  { value: "broken", label: "معطلة", labelEn: "Broken" },
];

const MOCK_FARMS_LIST = [
  { id: "farm-1", name: "مزرعة ١" },
  { id: "farm-2", name: "مزرعة ٢" },
  { id: "farm-3", name: "مزرعة ٣" },
  { id: "farm-4", name: "مزرعة ٤" },
  { id: "farm-5", name: "مزرعة ٥" },
];

// Mock equipment data - dynamic import for dead-code elimination in production builds.
// In production, the .mock module is never bundled because the import() is unreachable.
async function getMockEquipment(): Promise<EquipmentItem[]> {
  if (process.env.NODE_ENV !== "production") {
    const { MOCK_EQUIPMENT } = await import("./equipment.mock");
    return MOCK_EQUIPMENT;
  }
  return [];
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════

function getEquipmentTypeIcon(type: string) {
  switch (type) {
    case "tractor":
      return <Tractor className="w-4 h-4" />;
    case "harvester":
      return <Tractor className="w-4 h-4" />;
    case "pump":
      return <Droplets className="w-4 h-4" />;
    case "sprayer":
      return <SprayCan className="w-4 h-4" />;
    case "drone":
      return <Plane className="w-4 h-4" />;
    default:
      return <Wrench className="w-4 h-4" />;
  }
}

function getEquipmentTypeLabel(type: string): string {
  const found = EQUIPMENT_TYPES.find((t) => t.value === type);
  return found ? found.label : type;
}

function getStatusBadge(status: string) {
  switch (status) {
    case "operational":
      return {
        label: "تعمل",
        color: "text-green-700 bg-green-100",
        icon: <CheckCircle2 className="w-3 h-3" />,
      };
    case "maintenance":
      return {
        label: "صيانة",
        color: "text-yellow-700 bg-yellow-100",
        icon: <AlertTriangle className="w-3 h-3" />,
      };
    case "idle":
      return {
        label: "متوقفة",
        color: "text-gray-700 bg-gray-100",
        icon: <PauseCircle className="w-3 h-3" />,
      };
    case "broken":
      return {
        label: "معطلة",
        color: "text-red-700 bg-red-100",
        icon: <XCircle className="w-3 h-3" />,
      };
    default:
      return {
        label: status,
        color: "text-gray-700 bg-gray-100",
        icon: null,
      };
  }
}

function isMaintenanceDueSoon(nextMaintenanceDate: string | undefined): boolean {
  if (!nextMaintenanceDate) return false;
  const now = new Date();
  const next = new Date(nextMaintenanceDate);
  const diffDays = (next.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
  return diffDays <= 14 && diffDays >= 0;
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// دوال الاتصال بالخادم
// ═══════════════════════════════════════════════════════════════════════════

async function loadEquipmentFromAPI(): Promise<EquipmentItem[]> {
  try {
    const response = await apiClient.get(
      API_URLS.equipmentEndpoints.list
    );
    return response.data;
  } catch {
    logger.log("Falling back to static mock equipment data");
    return getMockEquipment();
  }
}

async function createEquipmentAPI(payload: CreateEquipmentPayload): Promise<EquipmentItem | null> {
  try {
    const response = await apiClient.post(
      API_URLS.equipmentEndpoints.list,
      payload
    );
    return response.data;
  } catch {
    logger.log("Create equipment API unavailable, using mock response");
    // Return a mock created item for development
    const newItem: EquipmentItem = {
      id: `eq-${Date.now()}`,
      name: payload.name,
      nameAr: payload.nameAr,
      type: payload.type,
      status: payload.status,
      farm_name: payload.farm_name,
      farm_id: payload.farm_id,
      lastMaintenance: new Date().toISOString(),
      nextMaintenance: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      last_maintenance_date: new Date().toISOString(),
      next_maintenance_date: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      hoursUsed: 0,
    };
    return newItem;
  }
}

async function updateEquipmentAPI(id: string, payload: Partial<EquipmentItem>): Promise<EquipmentItem | null> {
  try {
    const response = await apiClient.put(
      API_URLS.equipmentEndpoints.byId(id),
      payload
    );
    return response.data;
  } catch {
    logger.log("Update equipment API unavailable, using local update");
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// المكون الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

export default function EquipmentPage() {
  const [equipment, setEquipment] = useState<EquipmentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedEquipment, setSelectedEquipment] = useState<EquipmentItem | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [farmFilter, setFarmFilter] = useState("");

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Add form state
  const [formName, setFormName] = useState("");
  const [formNameAr, setFormNameAr] = useState("");
  const [formType, setFormType] = useState<EquipmentType>("tractor");
  const [formStatus, setFormStatus] = useState<EquipmentStatus>("operational");
  const [formFarm, setFormFarm] = useState(MOCK_FARMS_LIST[0]?.id || "");

  const loadEquipment = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await loadEquipmentFromAPI();
      setEquipment(data);
    } catch (error) {
      logger.error("Failed to load equipment:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEquipment();
  }, [loadEquipment]);

  // Filter equipment
  const filteredEquipment = useMemo(() => {
    return equipment.filter((eq) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !eq.name.toLowerCase().includes(query) &&
          !(eq.nameAr || "").toLowerCase().includes(query) &&
          !(eq.farm_name || "").toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (typeFilter && eq.type !== typeFilter) return false;
      if (statusFilter && eq.status !== statusFilter) return false;
      if (farmFilter && eq.farm_id !== farmFilter) return false;
      return true;
    });
  }, [equipment, searchQuery, typeFilter, statusFilter, farmFilter]);

  // Stats
  const stats = useMemo(() => {
    const total = equipment.length;
    const operational = equipment.filter((eq) => eq.status === "operational").length;
    const maintenance = equipment.filter(
      (eq) =>
        eq.status === "maintenance" ||
        isMaintenanceDueSoon(eq.next_maintenance_date || eq.nextMaintenance)
    ).length;
    const idle = equipment.filter((eq) => eq.status === "idle").length;
    const broken = equipment.filter((eq) => eq.status === "broken").length;
    return { total, operational, maintenance, idle, broken };
  }, [equipment]);

  // Unique farm names for filter
  const farmsList = useMemo(() => {
    const farms = new Map<string, string>();
    equipment.forEach((eq) => {
      if (eq.farm_id && eq.farm_name) {
        farms.set(eq.farm_id, eq.farm_name);
      }
    });
    return Array.from(farms.entries()).map(([id, name]) => ({ id, name }));
  }, [equipment]);

  // Reset form
  function resetForm() {
    setFormName("");
    setFormNameAr("");
    setFormType("tractor");
    setFormStatus("operational");
    setFormFarm(MOCK_FARMS_LIST[0]?.id || "");
  }

  // Handle add equipment
  async function handleAddEquipment() {
    if (!formName.trim() || !formNameAr.trim()) return;
    setIsSubmitting(true);

    const selectedFarm = MOCK_FARMS_LIST.find((f) => f.id === formFarm);
    const result = await createEquipmentAPI({
      name: formName,
      nameAr: formNameAr,
      type: formType,
      status: formStatus,
      farm_name: selectedFarm?.name || "",
      farm_id: formFarm,
    });

    if (result) {
      setEquipment((prev) => [result, ...prev]);
    }

    setIsSubmitting(false);
    setShowAddModal(false);
    resetForm();
  }

  // Handle status update
  async function handleStatusUpdate(item: EquipmentItem, newStatus: EquipmentStatus) {
    const result = await updateEquipmentAPI(item.id, { status: newStatus });
    // Update locally regardless of API success (offline-first)
    setEquipment((prev) =>
      prev.map((eq) =>
        eq.id === item.id ? { ...eq, status: newStatus } : eq
      )
    );
    if (result) {
      logger.log("Equipment status updated via API");
    }
    setShowEditModal(false);
    setSelectedEquipment(null);
  }

  // Handle view detail
  function handleViewDetail(item: EquipmentItem) {
    setSelectedEquipment(item);
    setShowDetailModal(true);
  }

  // Handle edit
  function handleEdit(item: EquipmentItem) {
    setSelectedEquipment(item);
    setShowEditModal(true);
  }

  // Table columns
  const columns = [
    {
      key: "name",
      header: "اسم المعدة",
      render: (item: EquipmentItem) => (
        <div className="flex items-center gap-3">
          <div className={cn(
            "w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0",
            item.type === "tractor" && "bg-blue-100 text-blue-600",
            item.type === "harvester" && "bg-amber-100 text-amber-600",
            item.type === "pump" && "bg-cyan-100 text-cyan-600",
            item.type === "sprayer" && "bg-purple-100 text-purple-600",
            item.type === "drone" && "bg-emerald-100 text-emerald-600",
          )}>
            {getEquipmentTypeIcon(item.type)}
          </div>
          <div>
            <p className="font-medium text-gray-900">{item.nameAr || item.name}</p>
            <p className="text-xs text-gray-500">{item.name}</p>
          </div>
        </div>
      ),
    },
    {
      key: "type",
      header: "النوع",
      render: (item: EquipmentItem) => (
        <span className="text-gray-700">{getEquipmentTypeLabel(item.type)}</span>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (item: EquipmentItem) => {
        const badge = getStatusBadge(item.status);
        return (
          <span
            className={cn(
              "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium",
              badge.color
            )}
          >
            {badge.icon}
            {badge.label}
          </span>
        );
      },
    },
    {
      key: "farm_name",
      header: "المزرعة",
      render: (item: EquipmentItem) => (
        <span className="text-gray-700">{item.farm_name || "-"}</span>
      ),
    },
    {
      key: "lastMaintenance",
      header: "آخر صيانة",
      render: (item: EquipmentItem) => (
        <span className="text-gray-600 text-sm">
          {formatDate(item.last_maintenance_date || item.lastMaintenance)}
        </span>
      ),
    },
    {
      key: "nextMaintenance",
      header: "الصيانة القادمة",
      render: (item: EquipmentItem) => {
        const nextDate = item.next_maintenance_date || item.nextMaintenance;
        const dueSoon = isMaintenanceDueSoon(nextDate);
        return (
          <span
            className={cn(
              "text-sm",
              dueSoon ? "text-yellow-600 font-medium" : "text-gray-600"
            )}
          >
            {formatDate(nextDate)}
            {dueSoon && (
              <span className="mr-1 text-yellow-500">
                <AlertTriangle className="w-3 h-3 inline" />
              </span>
            )}
          </span>
        );
      },
    },
    {
      key: "actions",
      header: "",
      render: (item: EquipmentItem) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleViewDetail(item);
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="عرض التفاصيل"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleEdit(item);
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="تعديل الحالة"
          >
            <Wrench className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      ),
      className: "w-24",
    },
  ];

  return (
    <div className="p-6">
      <Header
        title="إدارة المعدات"
        subtitle={`${equipment.length} معدة مسجلة`}
      />

      {/* Stat Cards */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "" && "ring-2 ring-sahool-500 border-sahool-500"
          )}
          onClick={() => setStatusFilter("")}
        >
          <div className="flex items-center justify-between">
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <Wrench className="w-5 h-5 text-sahool-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-1">إجمالي المعدات</p>
        </div>

        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "operational" && "ring-2 ring-green-500 border-green-500"
          )}
          onClick={() =>
            setStatusFilter(statusFilter === "operational" ? "" : "operational")
          }
        >
          <div className="flex items-center justify-between">
            <p className="text-2xl font-bold text-green-600">{stats.operational}</p>
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-1">تعمل</p>
        </div>

        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "maintenance" && "ring-2 ring-yellow-500 border-yellow-500"
          )}
          onClick={() =>
            setStatusFilter(statusFilter === "maintenance" ? "" : "maintenance")
          }
        >
          <div className="flex items-center justify-between">
            <p className="text-2xl font-bold text-yellow-600">{stats.maintenance}</p>
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-1">تحتاج صيانة</p>
        </div>

        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "idle" && "ring-2 ring-gray-400 border-gray-400"
          )}
          onClick={() =>
            setStatusFilter(statusFilter === "idle" ? "" : "idle")
          }
        >
          <div className="flex items-center justify-between">
            <p className="text-2xl font-bold text-gray-600">{stats.idle}</p>
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <PauseCircle className="w-5 h-5 text-gray-500" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-1">متوقفة</p>
        </div>

        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "broken" && "ring-2 ring-red-500 border-red-500"
          )}
          onClick={() =>
            setStatusFilter(statusFilter === "broken" ? "" : "broken")
          }
        >
          <div className="flex items-center justify-between">
            <p className="text-2xl font-bold text-red-600">{stats.broken}</p>
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-600" />
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-1">معطلة</p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالاسم أو المزرعة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الأنواع</option>
            {EQUIPMENT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            {EQUIPMENT_STATUSES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>

          {/* Farm Filter */}
          <select
            value={farmFilter}
            onChange={(e) => setFarmFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل المزارع</option>
            {farmsList.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>

          {/* Actions */}
          <button
            onClick={loadEquipment}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="تحديث"
          >
            <RefreshCw
              className={cn(
                "w-5 h-5 text-gray-600",
                isLoading && "animate-spin"
              )}
            />
          </button>
          <button
            disabled
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="تصدير (قريبًا)"
          >
            <Download className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={() => {
              resetForm();
              setShowAddModal(true);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            إضافة معدة
          </button>
        </div>
      </div>

      {/* Equipment Table */}
      <div className="mt-6">
        <DataTable
          columns={columns}
          data={filteredEquipment}
          keyExtractor={(item) => item.id}
          onRowClick={handleViewDetail}
          emptyMessage="لا توجد معدات مطابقة للبحث"
          isLoading={isLoading}
        />
      </div>

      {/* Add Equipment Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 animate-in fade-in slide-in-from-bottom-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold text-gray-900">إضافة معدة جديدة</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {/* Name (English) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الاسم (إنجليزي)
                </label>
                <input
                  type="text"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder="مثال: John Deere 5075E"
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                />
              </div>

              {/* Name (Arabic) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الاسم (عربي)
                </label>
                <input
                  type="text"
                  value={formNameAr}
                  onChange={(e) => setFormNameAr(e.target.value)}
                  placeholder="مثال: جرار جون ديري 5075E"
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                />
              </div>

              {/* Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  نوع المعدة
                </label>
                <select
                  value={formType}
                  onChange={(e) => setFormType(e.target.value as EquipmentType)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                >
                  {EQUIPMENT_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label} ({t.labelEn})
                    </option>
                  ))}
                </select>
              </div>

              {/* Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الحالة
                </label>
                <select
                  value={formStatus}
                  onChange={(e) => setFormStatus(e.target.value as EquipmentStatus)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                >
                  {EQUIPMENT_STATUSES.map((s) => (
                    <option key={s.value} value={s.value}>
                      {s.label} ({s.labelEn})
                    </option>
                  ))}
                </select>
              </div>

              {/* Farm */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  المزرعة
                </label>
                <select
                  value={formFarm}
                  onChange={(e) => setFormFarm(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                >
                  {MOCK_FARMS_LIST.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                إلغاء
              </button>
              <button
                onClick={handleAddEquipment}
                disabled={isSubmitting || !formName.trim() || !formNameAr.trim()}
                className={cn(
                  "flex items-center gap-2 px-6 py-2 bg-sahool-600 text-white rounded-lg transition-colors",
                  isSubmitting || !formName.trim() || !formNameAr.trim()
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:bg-sahool-700"
                )}
              >
                {isSubmitting && <RefreshCw className="w-4 h-4 animate-spin" />}
                إضافة
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedEquipment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 animate-in fade-in slide-in-from-bottom-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold text-gray-900">تفاصيل المعدة</h2>
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  setSelectedEquipment(null);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6">
              {/* Equipment Header */}
              <div className="flex items-center gap-4 mb-6">
                <div className={cn(
                  "w-14 h-14 rounded-xl flex items-center justify-center",
                  selectedEquipment.type === "tractor" && "bg-blue-100 text-blue-600",
                  selectedEquipment.type === "harvester" && "bg-amber-100 text-amber-600",
                  selectedEquipment.type === "pump" && "bg-cyan-100 text-cyan-600",
                  selectedEquipment.type === "sprayer" && "bg-purple-100 text-purple-600",
                  selectedEquipment.type === "drone" && "bg-emerald-100 text-emerald-600",
                )}>
                  {getEquipmentTypeIcon(selectedEquipment.type)}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {selectedEquipment.nameAr || selectedEquipment.name}
                  </h3>
                  <p className="text-sm text-gray-500">{selectedEquipment.name}</p>
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">النوع</p>
                  <p className="font-medium text-gray-900">
                    {getEquipmentTypeLabel(selectedEquipment.type)}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">الحالة</p>
                  {(() => {
                    const badge = getStatusBadge(selectedEquipment.status);
                    return (
                      <span
                        className={cn(
                          "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium",
                          badge.color
                        )}
                      >
                        {badge.icon}
                        {badge.label}
                      </span>
                    );
                  })()}
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">المزرعة</p>
                  <p className="font-medium text-gray-900">
                    {selectedEquipment.farm_name || "-"}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">ساعات التشغيل</p>
                  <p className="font-medium text-gray-900">
                    {selectedEquipment.hoursUsed != null
                      ? `${selectedEquipment.hoursUsed.toLocaleString("ar-YE")} ساعة`
                      : "-"}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center gap-1 mb-1">
                    <Calendar className="w-3 h-3 text-gray-400" />
                    <p className="text-xs text-gray-500">آخر صيانة</p>
                  </div>
                  <p className="font-medium text-gray-900">
                    {formatDate(
                      selectedEquipment.last_maintenance_date ||
                        selectedEquipment.lastMaintenance
                    )}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center gap-1 mb-1">
                    <Calendar className="w-3 h-3 text-gray-400" />
                    <p className="text-xs text-gray-500">الصيانة القادمة</p>
                  </div>
                  <p
                    className={cn(
                      "font-medium",
                      isMaintenanceDueSoon(
                        selectedEquipment.next_maintenance_date ||
                          selectedEquipment.nextMaintenance
                      )
                        ? "text-yellow-600"
                        : "text-gray-900"
                    )}
                  >
                    {formatDate(
                      selectedEquipment.next_maintenance_date ||
                        selectedEquipment.nextMaintenance
                    )}
                  </p>
                </div>
                {selectedEquipment.fuelLevel != null && (
                  <div className="bg-gray-50 rounded-lg p-3 col-span-2">
                    <p className="text-xs text-gray-500 mb-2">مستوى الوقود</p>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={cn(
                            "h-full rounded-full transition-all",
                            selectedEquipment.fuelLevel >= 60
                              ? "bg-green-500"
                              : selectedEquipment.fuelLevel >= 30
                                ? "bg-yellow-500"
                                : "bg-red-500"
                          )}
                          style={{ width: `${selectedEquipment.fuelLevel}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-700">
                        {selectedEquipment.fuelLevel}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100">
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  handleEdit(selectedEquipment);
                }}
                className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                تعديل الحالة
              </button>
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  setSelectedEquipment(null);
                }}
                className="px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
              >
                إغلاق
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Status Modal */}
      {showEditModal && selectedEquipment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 animate-in fade-in slide-in-from-bottom-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h2 className="text-xl font-bold text-gray-900">تعديل حالة المعدة</h2>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedEquipment(null);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center",
                  selectedEquipment.type === "tractor" && "bg-blue-100 text-blue-600",
                  selectedEquipment.type === "harvester" && "bg-amber-100 text-amber-600",
                  selectedEquipment.type === "pump" && "bg-cyan-100 text-cyan-600",
                  selectedEquipment.type === "sprayer" && "bg-purple-100 text-purple-600",
                  selectedEquipment.type === "drone" && "bg-emerald-100 text-emerald-600",
                )}>
                  {getEquipmentTypeIcon(selectedEquipment.type)}
                </div>
                <div>
                  <p className="font-medium text-gray-900">
                    {selectedEquipment.nameAr || selectedEquipment.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    الحالة الحالية: {getStatusBadge(selectedEquipment.status).label}
                  </p>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">اختر الحالة الجديدة:</p>

              <div className="grid grid-cols-2 gap-3">
                {EQUIPMENT_STATUSES.map((s) => {
                  const badge = getStatusBadge(s.value);
                  const isCurrentStatus = selectedEquipment.status === s.value;
                  return (
                    <button
                      key={s.value}
                      onClick={() =>
                        handleStatusUpdate(selectedEquipment, s.value)
                      }
                      disabled={isCurrentStatus}
                      className={cn(
                        "flex items-center gap-2 p-3 rounded-lg border-2 transition-all text-sm font-medium",
                        isCurrentStatus
                          ? "border-gray-300 bg-gray-50 text-gray-400 cursor-not-allowed"
                          : "border-gray-200 hover:border-sahool-500 hover:bg-sahool-50 text-gray-700"
                      )}
                    >
                      {badge.icon}
                      {s.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100">
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedEquipment(null);
                }}
                className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                إلغاء
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

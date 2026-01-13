"use client";

import { useState, useEffect } from "react";

// Types
interface Sample {
  id: string;
  barcode: string;
  status:
    | "pending"
    | "in_transit"
    | "received"
    | "processing"
    | "analyzed"
    | "archived";
  type: string;
  experimentName?: string;
  collectedAt?: string;
  batchCode?: string;
}

interface BatchSummary {
  id: string;
  batchCode: string;
  sampleCount: number;
  status: string;
  laboratory: string;
  collectionDate: string;
}

// Demo data - في الواقع تأتي من API
const demoSamples: Sample[] = [
  {
    id: "1",
    barcode: "SOIL-0001",
    status: "in_transit",
    type: "تربة",
    experimentName: "تجربة القمح",
    batchCode: "BATCH-2025-001",
  },
  {
    id: "2",
    barcode: "SOIL-0002",
    status: "in_transit",
    type: "تربة",
    experimentName: "تجربة القمح",
    batchCode: "BATCH-2025-001",
  },
  {
    id: "3",
    barcode: "LEAF-0001",
    status: "received",
    type: "أوراق",
    experimentName: "تجربة القمح",
    batchCode: "BATCH-2025-001",
  },
  {
    id: "4",
    barcode: "LEAF-0002",
    status: "received",
    type: "أوراق",
    experimentName: "تجربة القمح",
    batchCode: "BATCH-2025-001",
  },
  {
    id: "5",
    barcode: "WATER-0001",
    status: "processing",
    type: "ماء",
    experimentName: "تجربة الري",
    batchCode: "BATCH-2025-002",
  },
  {
    id: "6",
    barcode: "SOIL-0003",
    status: "analyzed",
    type: "تربة",
    experimentName: "تجربة القمح",
    batchCode: "BATCH-2025-001",
  },
  {
    id: "7",
    barcode: "SOIL-0004",
    status: "analyzed",
    type: "تربة",
    experimentName: "تجربة القمح",
    batchCode: "BATCH-2025-001",
  },
  {
    id: "8",
    barcode: "LEAF-0003",
    status: "pending",
    type: "أوراق",
    experimentName: "تجربة الطماطم",
    batchCode: "BATCH-2025-003",
  },
];

const demoBatches: BatchSummary[] = [
  {
    id: "1",
    batchCode: "BATCH-2025-001",
    sampleCount: 10,
    status: "received",
    laboratory: "مختبر سهول المركزي",
    collectionDate: "2025-01-10",
  },
  {
    id: "2",
    batchCode: "BATCH-2025-002",
    sampleCount: 5,
    status: "processing",
    laboratory: "مختبر سهول المركزي",
    collectionDate: "2025-01-12",
  },
  {
    id: "3",
    batchCode: "BATCH-2025-003",
    sampleCount: 8,
    status: "pending",
    laboratory: "مختبر خارجي",
    collectionDate: "2025-01-14",
  },
];

// Status configuration
const statusConfig = {
  pending: {
    label: "قيد الانتظار",
    color: "bg-gray-100 text-gray-800",
    icon: "⏳",
  },
  in_transit: {
    label: "في الطريق",
    color: "bg-blue-100 text-blue-800",
    icon: "🚚",
  },
  received: {
    label: "وصل المختبر",
    color: "bg-yellow-100 text-yellow-800",
    icon: "📥",
  },
  processing: {
    label: "قيد التحليل",
    color: "bg-purple-100 text-purple-800",
    icon: "🔬",
  },
  analyzed: {
    label: "تم التحليل",
    color: "bg-green-100 text-green-800",
    icon: "✅",
  },
  archived: { label: "مؤرشف", color: "bg-gray-200 text-gray-600", icon: "📁" },
};

export default function LabDashboard() {
  const [samples, setSamples] = useState<Sample[]>(demoSamples);
  const [batches, setBatches] = useState<BatchSummary[]>(demoBatches);
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"kanban" | "list">("kanban");

  // Filter samples by batch
  const filteredSamples = selectedBatch
    ? samples.filter((s) => s.batchCode === selectedBatch)
    : samples;

  // Stats
  const stats = {
    total: samples.length,
    pending: samples.filter((s) => s.status === "pending").length,
    inTransit: samples.filter((s) => s.status === "in_transit").length,
    received: samples.filter((s) => s.status === "received").length,
    processing: samples.filter((s) => s.status === "processing").length,
    analyzed: samples.filter((s) => s.status === "analyzed").length,
  };

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                مركز إدارة المختبر والعينات
              </h1>
              <p className="text-gray-500 mt-1">
                تتبع العينات من الحقل إلى التحليل
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setViewMode("kanban")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  viewMode === "kanban"
                    ? "bg-green-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                عرض Kanban
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  viewMode === "list"
                    ? "bg-green-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                عرض قائمة
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8">
          <StatCard
            title="إجمالي العينات"
            value={stats.total}
            icon="📊"
            color="bg-gray-700"
          />
          <StatCard
            title="قيد الانتظار"
            value={stats.pending}
            icon="⏳"
            color="bg-gray-500"
          />
          <StatCard
            title="في الطريق"
            value={stats.inTransit}
            icon="🚚"
            color="bg-blue-500"
          />
          <StatCard
            title="وصلت"
            value={stats.received}
            icon="📥"
            color="bg-yellow-500"
          />
          <StatCard
            title="قيد التحليل"
            value={stats.processing}
            icon="🔬"
            color="bg-purple-500"
          />
          <StatCard
            title="مكتملة"
            value={stats.analyzed}
            icon="✅"
            color="bg-green-500"
          />
        </div>

        {/* Batch Filter */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <h3 className="font-semibold mb-3 text-gray-700">تصفية حسب الدفعة</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedBatch(null)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedBatch === null
                  ? "bg-green-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              جميع الدفعات
            </button>
            {batches.map((batch) => (
              <button
                key={batch.id}
                onClick={() => setSelectedBatch(batch.batchCode)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedBatch === batch.batchCode
                    ? "bg-green-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {batch.batchCode} ({batch.sampleCount})
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        {viewMode === "kanban" ? (
          <KanbanView samples={filteredSamples} statusConfig={statusConfig} />
        ) : (
          <ListView samples={filteredSamples} statusConfig={statusConfig} />
        )}
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: number;
  icon: string;
  color: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div
          className={`w-12 h-12 ${color} rounded-lg flex items-center justify-center text-white text-xl`}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}

// Kanban View Component
function KanbanView({
  samples,
  statusConfig,
}: {
  samples: Sample[];
  statusConfig: any;
}) {
  const columns: Array<keyof typeof statusConfig> = [
    "pending",
    "in_transit",
    "received",
    "processing",
    "analyzed",
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {columns.map((status) => (
        <LabColumn
          key={status as string}
          title={`${statusConfig[status].icon} ${statusConfig[status].label}`}
          samples={samples.filter((s) => s.status === status)}
          color={statusConfig[status].color}
        />
      ))}
    </div>
  );
}

// Lab Column Component
function LabColumn({
  title,
  samples,
  color,
}: {
  title: string;
  samples: Sample[];
  color: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className={`${color} px-4 py-3 font-semibold`}>
        {title} <span className="text-sm opacity-75">({samples.length})</span>
      </div>
      <div className="p-3 space-y-3 min-h-[200px]">
        {samples.length === 0 ? (
          <div className="text-center text-gray-400 py-8">لا توجد عينات</div>
        ) : (
          samples.map((sample) => (
            <SampleCard key={sample.id} sample={sample} />
          ))
        )}
      </div>
    </div>
  );
}

// Sample Card Component
function SampleCard({ sample }: { sample: Sample }) {
  return (
    <div className="bg-gray-50 p-3 rounded-lg border border-gray-100 hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex justify-between items-start mb-2">
        <span className="font-mono text-sm bg-white px-2 py-1 rounded border">
          {sample.barcode}
        </span>
        <span className="text-xs font-semibold text-gray-500 bg-white px-2 py-1 rounded">
          {sample.type}
        </span>
      </div>
      {sample.experimentName && (
        <p className="text-xs text-gray-500 truncate">
          {sample.experimentName}
        </p>
      )}
    </div>
  );
}

// List View Component
function ListView({
  samples,
  statusConfig,
}: {
  samples: Sample[];
  statusConfig: any;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
              الباركود
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
              النوع
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
              التجربة
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
              الدفعة
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
              الحالة
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {samples.map((sample) => (
            <tr key={sample.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-mono text-sm">{sample.barcode}</td>
              <td className="px-4 py-3 text-sm">{sample.type}</td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {sample.experimentName || "-"}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {sample.batchCode || "-"}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusConfig[sample.status].color}`}
                >
                  {statusConfig[sample.status].icon}{" "}
                  {statusConfig[sample.status].label}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

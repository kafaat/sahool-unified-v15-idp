"use client";

// Research Management Page
// صفحة إدارة الأبحاث

import { useEffect, useState, useMemo } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
import {
  FlaskConical,
  Search,
  RefreshCw,
  Download,
  Eye,
  Plus,
  Users,
  Calendar,
  MapPin,
  BarChart3,
} from "lucide-react";
import { logger } from "../../lib/logger";
import { MOCK_TRIALS } from "./research.mock";
import type { ResearchTrial } from "./research.mock";

export default function ResearchPage() {
  const [trials, setTrials] = useState<ResearchTrial[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    loadTrials();
  }, []);

  async function loadTrials() {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setTrials(MOCK_TRIALS);
    } catch (error) {
      logger.error("Failed to load research trials:", error);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredTrials = useMemo(() => {
    return trials.filter((t) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !t.name.toLowerCase().includes(query) &&
          !t.nameAr.includes(query) &&
          !t.cropAr.includes(query)
        ) {
          return false;
        }
      }
      if (statusFilter && t.status !== statusFilter) return false;
      return true;
    });
  }, [trials, searchQuery, statusFilter]);

  const stats = useMemo(() => ({
    total: trials.length,
    active: trials.filter((t) => t.status === "active").length,
    completed: trials.filter((t) => t.status === "completed").length,
    totalBudget: trials.reduce((acc, t) => acc + t.budget, 0),
    totalResearchers: trials.reduce((acc, t) => acc + t.researchers, 0),
  }), [trials]);

  const getStatusLabel = (status: ResearchTrial["status"]) => {
    const labels: Record<ResearchTrial["status"], string> = {
      planning: "قيد التخطيط",
      active: "نشط",
      completed: "مكتمل",
      on_hold: "معلق",
      cancelled: "ملغي",
    };
    return labels[status];
  };

  const getStatusColor = (status: ResearchTrial["status"]) => {
    const colors: Record<ResearchTrial["status"], string> = {
      planning: "bg-blue-100 text-blue-800",
      active: "bg-green-100 text-green-800",
      completed: "bg-gray-100 text-gray-800",
      on_hold: "bg-yellow-100 text-yellow-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return colors[status];
  };

  const columns = [
    {
      key: "name",
      header: "التجربة",
      render: (trial: ResearchTrial) => (
        <div>
          <p className="font-medium text-gray-900">{trial.nameAr}</p>
          <p className="text-xs text-gray-500">{trial.cropAr}</p>
        </div>
      ),
    },
    {
      key: "field",
      header: "الموقع",
      render: (trial: ResearchTrial) => (
        <div className="flex items-center gap-1 text-gray-700 text-sm">
          <MapPin className="w-4 h-4 text-gray-400" />
          {trial.fieldNameAr}
        </div>
      ),
    },
    {
      key: "team",
      header: "الفريق",
      render: (trial: ResearchTrial) => (
        <div className="flex items-center gap-1 text-gray-700">
          <Users className="w-4 h-4 text-gray-400" />
          {trial.researchers} باحث
        </div>
      ),
    },
    {
      key: "dates",
      header: "المدة",
      render: (trial: ResearchTrial) => (
        <div className="text-sm">
          <p className="text-gray-500">{formatDate(trial.startDate)}</p>
          <p className="text-gray-900">{formatDate(trial.endDate)}</p>
        </div>
      ),
    },
    {
      key: "progress",
      header: "التقدم",
      render: (trial: ResearchTrial) => (
        <div className="w-24">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-gray-600">{trial.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={cn(
                "h-2 rounded-full",
                trial.progress === 100 ? "bg-green-500" : "bg-sahool-500"
              )}
              style={{ width: `${trial.progress}%` }}
            />
          </div>
        </div>
      ),
    },
    {
      key: "budget",
      header: "الميزانية",
      render: (trial: ResearchTrial) => (
        <div className="text-sm">
          <p className="font-medium text-gray-900">
            {trial.spent.toLocaleString()} / {trial.budget.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500">{trial.currency}</p>
        </div>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (trial: ResearchTrial) => (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(trial.status))}>
          {getStatusLabel(trial.status)}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (_trial: ResearchTrial) => (
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="عرض">
          <Eye className="w-4 h-4 text-gray-500" />
        </button>
      ),
      className: "w-16",
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة الأبحاث" subtitle={`${trials.length} تجربة بحثية`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-500">إجمالي التجارب</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.active}</p>
              <p className="text-sm text-gray-500">نشط</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
              <p className="text-sm text-gray-500">مكتمل</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.totalResearchers}</p>
              <p className="text-sm text-gray-500">باحث</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{(stats.totalBudget / 1000).toFixed(0)}K</p>
              <p className="text-sm text-gray-500">الميزانية (SAR)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالاسم أو المحصول..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="planning">قيد التخطيط</option>
            <option value="active">نشط</option>
            <option value="completed">مكتمل</option>
            <option value="on_hold">معلق</option>
            <option value="cancelled">ملغي</option>
          </select>

          <button
            onClick={loadTrials}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")} />
          </button>
          <button className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-5 h-5 text-gray-600" />
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors">
            <Plus className="w-5 h-5" />
            تجربة جديدة
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white rounded-xl border border-gray-100 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={filteredTrials}
            keyExtractor={(trial) => trial.id}
            emptyMessage="لا توجد تجارب مطابقة للبحث"
          />
        )}
      </div>
    </div>
  );
}

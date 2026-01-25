"use client";

import React, { useState, useEffect } from "react";
import { FlaskConical, Plus, Calendar, MapPin, BarChart3, Users } from "lucide-react";

interface Trial {
  id: string;
  name: string;
  nameAr: string;
  description: string;
  crop: string;
  cropAr: string;
  startDate: string;
  endDate: string;
  status: "planning" | "active" | "completed" | "on_hold";
  fieldId: string;
  fieldName: string;
  researchers: number;
  progress: number;
}

const mockTrials: Trial[] = [
  {
    id: "1",
    name: "Wheat Drought Resistance Study",
    nameAr: "دراسة مقاومة القمح للجفاف",
    description: "تقييم أصناف القمح المختلفة لتحمل الإجهاد المائي",
    crop: "Wheat",
    cropAr: "القمح",
    startDate: "2026-01-01",
    endDate: "2026-06-30",
    status: "active",
    fieldId: "F001",
    fieldName: "حقل التجارب 1",
    researchers: 5,
    progress: 45,
  },
  {
    id: "2",
    name: "Organic Fertilizer Efficiency",
    nameAr: "كفاءة الأسمدة العضوية",
    description: "مقارنة بين الأسمدة العضوية والكيميائية",
    crop: "Tomato",
    cropAr: "الطماطم",
    startDate: "2026-02-15",
    endDate: "2026-08-15",
    status: "planning",
    fieldId: "F002",
    fieldName: "حقل التجارب 2",
    researchers: 3,
    progress: 0,
  },
  {
    id: "3",
    name: "Date Palm Yield Optimization",
    nameAr: "تحسين إنتاجية النخيل",
    description: "دراسة تأثير الري بالتنقيط على إنتاج التمور",
    crop: "Date Palm",
    cropAr: "النخيل",
    startDate: "2025-06-01",
    endDate: "2025-12-31",
    status: "completed",
    fieldId: "F003",
    fieldName: "بستان النخيل",
    researchers: 4,
    progress: 100,
  },
];

export default function ResearchClient() {
  const [trials, setTrials] = useState<Trial[]>(mockTrials);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"all" | "active" | "completed">("all");

  useEffect(() => {
    setTimeout(() => setIsLoading(false), 500);
  }, []);

  const getStatusBadge = (status: Trial["status"]) => {
    const styles = {
      planning: "bg-blue-100 text-blue-800",
      active: "bg-green-100 text-green-800",
      completed: "bg-gray-100 text-gray-800",
      on_hold: "bg-yellow-100 text-yellow-800",
    };
    const labels = {
      planning: "قيد التخطيط",
      active: "نشط",
      completed: "مكتمل",
      on_hold: "معلق",
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const filteredTrials = trials.filter((trial) => {
    if (activeTab === "all") return true;
    if (activeTab === "active") return trial.status === "active" || trial.status === "planning";
    return trial.status === "completed";
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التجارب البحثية</h1>
          <p className="text-gray-500 mt-1">Research Trials Management</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
          <Plus className="w-4 h-4" />
          <span>تجربة جديدة</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي التجارب</div>
              <div className="text-xl font-bold text-gray-900">{trials.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">نشطة</div>
              <div className="text-xl font-bold text-green-600">
                {trials.filter((t) => t.status === "active").length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">مكتملة</div>
              <div className="text-xl font-bold text-gray-600">
                {trials.filter((t) => t.status === "completed").length}
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">الباحثين</div>
              <div className="text-xl font-bold text-purple-600">
                {trials.reduce((acc, t) => acc + t.researchers, 0)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex gap-4">
          {[
            { key: "all", label: "الكل" },
            { key: "active", label: "النشطة" },
            { key: "completed", label: "المكتملة" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as typeof activeTab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? "border-sahool-green-600 text-sahool-green-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Trials Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTrials.map((trial) => (
          <div key={trial.id} className="bg-white rounded-lg border p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 bg-sahool-green-100 rounded-lg flex items-center justify-center">
                <FlaskConical className="w-5 h-5 text-sahool-green-600" />
              </div>
              {getStatusBadge(trial.status)}
            </div>

            <h3 className="font-semibold text-gray-900 mb-1">{trial.nameAr}</h3>
            <p className="text-sm text-gray-500 mb-3">{trial.name}</p>

            <p className="text-sm text-gray-600 mb-4 line-clamp-2">{trial.description}</p>

            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-gray-500">
                <MapPin className="w-4 h-4" />
                <span>{trial.fieldName}</span>
              </div>
              <div className="flex items-center gap-2 text-gray-500">
                <Calendar className="w-4 h-4" />
                <span>{trial.startDate} - {trial.endDate}</span>
              </div>
            </div>

            {trial.status === "active" && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">التقدم</span>
                  <span className="font-medium">{trial.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-sahool-green-600 h-2 rounded-full transition-all"
                    style={{ width: `${trial.progress}%` }}
                  />
                </div>
              </div>
            )}

            <button className="w-full mt-4 px-4 py-2 border border-sahool-green-600 text-sahool-green-600 rounded-lg hover:bg-sahool-green-50 transition-colors text-sm font-medium">
              عرض التفاصيل
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

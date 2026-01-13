/**
 * Analytics Dashboard Component
 * لوحة معلومات التحليلات
 */

"use client";

import React, { useState } from "react";
import { useTranslations } from "next-intl";
import { BarChart3, TrendingUp, DollarSign, Download } from "lucide-react";
import { useAnalyticsSummary, useKPIMetrics } from "../hooks/useAnalytics";
import type { AnalyticsFilters } from "../types";
import { KPICards } from "./KPICards";
import { YieldAnalysis } from "./YieldAnalysis.dynamic";
import { CostAnalysis } from "./CostAnalysis.dynamic";
import { ReportGenerator } from "./ReportGenerator";

export const AnalyticsDashboard: React.FC = () => {
  const t = useTranslations("analytics");
  const [filters, setFilters] = useState<AnalyticsFilters>({
    period: "month",
  });
  const [activeTab, setActiveTab] = useState<
    "overview" | "yield" | "cost" | "reports"
  >("overview");

  const { data: summary, isLoading: summaryLoading } =
    useAnalyticsSummary(filters);
  const { data: kpis } = useKPIMetrics(filters);

  const tabs = [
    { id: "overview", icon: BarChart3 },
    { id: "yield", icon: TrendingUp },
    { id: "cost", icon: DollarSign },
    { id: "reports", icon: Download },
  ] as const;

  const tabLabels = {
    overview: t("overview"),
    yield: t("yieldAnalysis"),
    cost: t("costAnalysis"),
    reports: t("reports"),
  };

  const periods = [
    { value: "week" },
    { value: "month" },
    { value: "season" },
    { value: "year" },
  ] as const;

  const periodLabels = {
    week: t("thisWeek"),
    month: t("thisMonth"),
    season: t("thisSeason"),
    year: t("thisYear"),
  };

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{t("title")}</h1>
              <p className="mt-1 text-sm text-gray-500">{t("subtitle")}</p>
            </div>

            {/* Period Selector */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">
                {t("period")}:
              </label>
              <select
                value={filters.period || "month"}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    period: e.target.value as AnalyticsFilters["period"],
                  })
                }
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {periods.map((period) => (
                  <option key={period.value} value={period.value}>
                    {periodLabels[period.value]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 flex gap-4 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap
                    ${
                      activeTab === tab.id
                        ? "bg-green-500 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tabLabels[tab.id]}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {summaryLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        ) : (
          <>
            {/* Summary Stats */}
            {summary && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-sm text-gray-600">{t("totalArea")}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {summary.totalArea.toLocaleString("ar-SA")}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">{t("hectare")}</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-sm text-gray-600">{t("totalYield")}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {summary.totalYield.toLocaleString("ar-SA")}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">{t("kg")}</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-sm text-gray-600">{t("netProfit")}</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">
                    {summary.totalProfit.toLocaleString("ar-SA")}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">{t("sar")}</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <p className="text-sm text-gray-600">
                    {t("averageProductivity")}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {summary.averageYieldPerHectare.toLocaleString("ar-SA")}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    {t("kgPerHectare")}
                  </p>
                </div>
              </div>
            )}

            {/* Tab Content */}
            {activeTab === "overview" && kpis && <KPICards kpis={kpis} />}
            {activeTab === "yield" && <YieldAnalysis filters={filters} />}
            {activeTab === "cost" && <CostAnalysis filters={filters} />}
            {activeTab === "reports" && <ReportGenerator filters={filters} />}
          </>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;

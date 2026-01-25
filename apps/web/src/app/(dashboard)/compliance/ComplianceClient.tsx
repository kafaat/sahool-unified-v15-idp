"use client";

import React, { useState, useEffect } from "react";
import { Shield, CheckCircle, AlertTriangle, FileText, Calendar, TrendingUp, Award } from "lucide-react";

interface ComplianceItem {
  id: string;
  category: string;
  categoryAr: string;
  requirement: string;
  requirementAr: string;
  status: "compliant" | "partial" | "non_compliant" | "pending_review";
  lastAudit: string;
  nextAudit: string;
  score: number;
  notes?: string;
}

interface Certification {
  id: string;
  name: string;
  nameAr: string;
  issuer: string;
  issuerAr: string;
  status: "active" | "expired" | "pending";
  issueDate: string;
  expiryDate: string;
}

const mockCompliance: ComplianceItem[] = [
  {
    id: "1",
    category: "Food Safety",
    categoryAr: "سلامة الغذاء",
    requirement: "Pesticide Residue Limits",
    requirementAr: "حدود بقايا المبيدات",
    status: "compliant",
    lastAudit: "2026-01-15",
    nextAudit: "2026-04-15",
    score: 95,
  },
  {
    id: "2",
    category: "Worker Safety",
    categoryAr: "سلامة العمال",
    requirement: "PPE Requirements",
    requirementAr: "متطلبات معدات الحماية",
    status: "compliant",
    lastAudit: "2026-01-10",
    nextAudit: "2026-04-10",
    score: 100,
  },
  {
    id: "3",
    category: "Environment",
    categoryAr: "البيئة",
    requirement: "Water Usage Records",
    requirementAr: "سجلات استخدام المياه",
    status: "partial",
    lastAudit: "2026-01-12",
    nextAudit: "2026-04-12",
    score: 75,
    notes: "Missing irrigation logs for December",
  },
  {
    id: "4",
    category: "Traceability",
    categoryAr: "التتبع",
    requirement: "Batch Identification",
    requirementAr: "تعريف الدفعات",
    status: "compliant",
    lastAudit: "2026-01-08",
    nextAudit: "2026-04-08",
    score: 92,
  },
  {
    id: "5",
    category: "Documentation",
    categoryAr: "التوثيق",
    requirement: "Training Records",
    requirementAr: "سجلات التدريب",
    status: "pending_review",
    lastAudit: "2026-01-20",
    nextAudit: "2026-04-20",
    score: 85,
  },
];

const mockCertifications: Certification[] = [
  {
    id: "1",
    name: "GlobalGAP",
    nameAr: "جلوبال جاب",
    issuer: "GLOBALG.A.P.",
    issuerAr: "منظمة جلوبال جاب",
    status: "active",
    issueDate: "2025-06-01",
    expiryDate: "2026-06-01",
  },
  {
    id: "2",
    name: "Organic Certification",
    nameAr: "شهادة العضوية",
    issuer: "Saudi Organic Authority",
    issuerAr: "هيئة الزراعة العضوية",
    status: "active",
    issueDate: "2025-03-15",
    expiryDate: "2026-03-15",
  },
  {
    id: "3",
    name: "ISO 22000",
    nameAr: "آيزو 22000",
    issuer: "SGS",
    issuerAr: "إس جي إس",
    status: "pending",
    issueDate: "",
    expiryDate: "",
  },
];

export default function ComplianceClient() {
  const [compliance, setCompliance] = useState<ComplianceItem[]>(mockCompliance);
  const [certifications, setCertifications] = useState<Certification[]>(mockCertifications);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => setIsLoading(false), 500);
  }, []);

  const getStatusColor = (status: ComplianceItem["status"]) => {
    const colors = {
      compliant: "text-green-600 bg-green-100",
      partial: "text-yellow-600 bg-yellow-100",
      non_compliant: "text-red-600 bg-red-100",
      pending_review: "text-blue-600 bg-blue-100",
    };
    return colors[status];
  };

  const getStatusLabel = (status: ComplianceItem["status"]) => {
    const labels = {
      compliant: "متوافق",
      partial: "جزئي",
      non_compliant: "غير متوافق",
      pending_review: "قيد المراجعة",
    };
    return labels[status];
  };

  const getCertStatusColor = (status: Certification["status"]) => {
    const colors = {
      active: "text-green-600 bg-green-100",
      expired: "text-red-600 bg-red-100",
      pending: "text-yellow-600 bg-yellow-100",
    };
    return colors[status];
  };

  const getCertStatusLabel = (status: Certification["status"]) => {
    const labels = {
      active: "نشطة",
      expired: "منتهية",
      pending: "قيد الإصدار",
    };
    return labels[status];
  };

  const overallScore = Math.round(compliance.reduce((acc, c) => acc + c.score, 0) / compliance.length);
  const compliantCount = compliance.filter(c => c.status === "compliant").length;
  const activeCerts = certifications.filter(c => c.status === "active").length;

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
          <h1 className="text-2xl font-bold text-gray-900">الامتثال والجودة</h1>
          <p className="text-gray-500 mt-1">GlobalGAP Compliance & Quality Management</p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors">
            تقرير التدقيق
          </button>
          <button className="px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors">
            + فحص جديد
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">نسبة الامتثال</div>
              <div className="text-lg font-bold text-green-600">{overallScore}%</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متطلبات متوافقة</div>
              <div className="text-lg font-bold text-blue-600">{compliantCount}/{compliance.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Award className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">شهادات نشطة</div>
              <div className="text-lg font-bold text-purple-600">{activeCerts}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">التدقيق القادم</div>
              <div className="text-lg font-bold text-amber-600">2026-04-08</div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Checklist */}
        <div className="lg:col-span-2 bg-white rounded-lg border overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">قائمة الامتثال</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">الفئة</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">المتطلب</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">الحالة</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">النتيجة</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">التدقيق القادم</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {compliance.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{item.categoryAr}</div>
                      <div className="text-xs text-gray-500">{item.category}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-gray-900">{item.requirementAr}</div>
                      {item.notes && (
                        <div className="text-xs text-amber-600 mt-1">{item.notes}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                        {getStatusLabel(item.status)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${item.score >= 90 ? "bg-green-500" : item.score >= 70 ? "bg-yellow-500" : "bg-red-500"}`}
                            style={{ width: `${item.score}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">{item.score}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center text-sm text-gray-500">
                      {item.nextAudit}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Certifications */}
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900">الشهادات</h2>
          </div>
          <div className="divide-y">
            {certifications.map((cert) => (
              <div key={cert.id} className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-sahool-green-600" />
                    <div>
                      <h3 className="font-medium text-gray-900">{cert.nameAr}</h3>
                      <p className="text-xs text-gray-500">{cert.name}</p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCertStatusColor(cert.status)}`}>
                    {getCertStatusLabel(cert.status)}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  <div>الجهة: {cert.issuerAr}</div>
                  {cert.status === "active" && (
                    <>
                      <div>تاريخ الإصدار: {cert.issueDate}</div>
                      <div>تاريخ الانتهاء: {cert.expiryDate}</div>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Compliance Score Chart Placeholder */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">تطور نسبة الامتثال</h2>
        </div>
        <div className="p-4">
          <div className="h-64 bg-gradient-to-t from-green-50 to-white flex items-end justify-around px-8">
            {[78, 82, 85, 88, 90, 92].map((score, i) => (
              <div key={i} className="flex flex-col items-center gap-2">
                <div
                  className="w-12 bg-sahool-green-500 rounded-t-lg transition-all hover:bg-sahool-green-600"
                  style={{ height: `${score * 2}px` }}
                />
                <span className="text-xs text-gray-500">
                  {["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"][i]}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

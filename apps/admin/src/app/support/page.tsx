// Sahool Admin Dashboard - Support Chat Management
// إدارة دردشات الدعم الفني

"use client";

import { useState, useEffect } from "react";
import { apiClient, API_URLS } from "@/lib/api";
import { logger } from "../../lib/logger";

interface SupportRequest {
  id: string;
  roomId: string;
  farmerId: string;
  farmerName: string;
  governorate: string;
  topic: string;
  status: "pending" | "active" | "resolved" | "closed";
  expertId?: string;
  expertName?: string;
  createdAt: string;
  acceptedAt?: string;
  resolvedAt?: string;
  messagesCount: number;
}

interface ChatStats {
  totalConnections: number;
  onlineExperts: number;
  activeSessions: number;
  pendingRequests: number;
  resolvedToday: number;
  avgResponseTime: number;
}

// Mock data for development
const mockStats: ChatStats = {
  totalConnections: 47,
  onlineExperts: 3,
  activeSessions: 8,
  pendingRequests: 5,
  resolvedToday: 23,
  avgResponseTime: 4.2,
};

const mockRequests: SupportRequest[] = [
  {
    id: "req-1",
    roomId: "support_farmer1_1702656000000",
    farmerId: "farmer-1",
    farmerName: "أحمد محمد",
    governorate: "صنعاء",
    topic: "مشكلة في تشخيص مرض البياض الدقيقي",
    status: "active",
    expertId: "expert-1",
    expertName: "م. سالم العمري",
    createdAt: new Date(Date.now() - 30 * 60000).toISOString(),
    acceptedAt: new Date(Date.now() - 25 * 60000).toISOString(),
    messagesCount: 12,
  },
  {
    id: "req-2",
    roomId: "support_farmer2_1702656100000",
    farmerId: "farmer-2",
    farmerName: "علي أحمد",
    governorate: "تعز",
    topic: "استفسار عن جدول الري",
    status: "pending",
    createdAt: new Date(Date.now() - 5 * 60000).toISOString(),
    messagesCount: 2,
  },
  {
    id: "req-3",
    roomId: "support_farmer3_1702656200000",
    farmerId: "farmer-3",
    farmerName: "محمد سعيد",
    governorate: "إب",
    topic: "مشكلة في محصول البن",
    status: "pending",
    createdAt: new Date(Date.now() - 10 * 60000).toISOString(),
    messagesCount: 3,
  },
  {
    id: "req-4",
    roomId: "support_farmer4_1702656300000",
    farmerId: "farmer-4",
    farmerName: "خالد عبدالله",
    governorate: "حضرموت",
    topic: "نصائح للتسميد",
    status: "resolved",
    expertId: "expert-2",
    expertName: "م. فاطمة الحداد",
    createdAt: new Date(Date.now() - 120 * 60000).toISOString(),
    acceptedAt: new Date(Date.now() - 115 * 60000).toISOString(),
    resolvedAt: new Date(Date.now() - 60 * 60000).toISOString(),
    messagesCount: 18,
  },
];

export default function SupportPage() {
  const [stats, setStats] = useState<ChatStats>(mockStats);
  const [requests, setRequests] = useState<SupportRequest[]>(mockRequests);
  const [filter, setFilter] = useState<
    "all" | "pending" | "active" | "resolved"
  >("all");
  const [selectedRequest, setSelectedRequest] = useState<SupportRequest | null>(
    null,
  );

  useEffect(() => {
    fetchStats();
    fetchRequests();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await apiClient.get(
        `${API_URLS.communityChat}/v1/stats`,
      );
      setStats(response.data);
    } catch (error) {
      logger.log("Using mock stats");
    }
  };

  const fetchRequests = async () => {
    try {
      const response = await apiClient.get(
        `${API_URLS.communityChat}/v1/requests`,
      );
      setRequests(response.data);
    } catch (error) {
      logger.log("Using mock requests");
    }
  };

  const filteredRequests = requests.filter((req) => {
    if (filter === "all") return true;
    return req.status === filter;
  });

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-yellow-100 text-yellow-800",
      active: "bg-green-100 text-green-800",
      resolved: "bg-blue-100 text-blue-800",
      closed: "bg-gray-100 text-gray-800",
    };
    const labels: Record<string, string> = {
      pending: "في الانتظار",
      active: "نشط",
      resolved: "تم الحل",
      closed: "مغلق",
    };
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}
      >
        {labels[status]}
      </span>
    );
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 60) return `منذ ${diffMins} دقيقة`;
    if (diffMins < 1440) return `منذ ${Math.floor(diffMins / 60)} ساعة`;
    return date.toLocaleDateString("ar-YE");
  };

  return (
    <div className="p-6 max-w-7xl mx-auto" dir="rtl">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">مركز الدعم الفني</h1>
          <p className="text-gray-500 mt-1">
            إدارة محادثات المزارعين مع الخبراء
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-sm text-gray-600">Socket.io متصل</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
          <div className="text-2xl font-bold text-gray-900">
            {stats.totalConnections}
          </div>
          <div className="text-sm text-gray-500">اتصال نشط</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
          <div className="text-2xl font-bold text-green-600">
            {stats.onlineExperts}
          </div>
          <div className="text-sm text-gray-500">خبير متاح</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
          <div className="text-2xl font-bold text-blue-600">
            {stats.activeSessions}
          </div>
          <div className="text-sm text-gray-500">جلسة نشطة</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
          <div className="text-2xl font-bold text-yellow-600">
            {stats.pendingRequests}
          </div>
          <div className="text-sm text-gray-500">طلب معلق</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
          <div className="text-2xl font-bold text-purple-600">
            {stats.resolvedToday}
          </div>
          <div className="text-sm text-gray-500">محلول اليوم</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
          <div className="text-2xl font-bold text-gray-900">
            {stats.avgResponseTime}د
          </div>
          <div className="text-sm text-gray-500">متوسط الرد</div>
        </div>
      </div>

      {/* Online Experts */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-6 border border-gray-100">
        <h2 className="text-lg font-semibold mb-3">الخبراء المتصلون</h2>
        <div className="flex flex-wrap gap-3">
          {[
            { name: "م. سالم العمري", specialty: "أمراض النبات", sessions: 2 },
            {
              name: "م. فاطمة الحداد",
              specialty: "الري والتسميد",
              sessions: 1,
            },
            {
              name: "م. عبدالرحمن علي",
              specialty: "البن والفواكه",
              sessions: 0,
            },
          ].map((expert, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 bg-gray-50 rounded-lg p-3 min-w-[200px]"
            >
              <div className="relative">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-700 font-semibold">
                    {expert.name.charAt(3)}
                  </span>
                </div>
                <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
              </div>
              <div>
                <div className="font-medium text-sm">{expert.name}</div>
                <div className="text-xs text-gray-500">{expert.specialty}</div>
                <div className="text-xs text-green-600">
                  {expert.sessions > 0
                    ? `${expert.sessions} جلسة نشطة`
                    : "متاح"}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-4">
        {[
          { key: "all", label: "الكل" },
          { key: "pending", label: "في الانتظار" },
          { key: "active", label: "نشط" },
          { key: "resolved", label: "تم الحل" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key as typeof filter)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === tab.key
                ? "bg-green-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {tab.label}
            {tab.key === "pending" && (
              <span className="mr-2 bg-yellow-200 text-yellow-800 px-1.5 py-0.5 rounded-full text-xs">
                {requests.filter((r) => r.status === "pending").length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Requests Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">
                المزارع
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">
                المحافظة
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">
                الموضوع
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">
                الخبير
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">
                الرسائل
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">
                الحالة
              </th>
              <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">
                الوقت
              </th>
              <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600">
                إجراء
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredRequests.map((request) => (
              <tr key={request.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">
                    {request.farmerName}
                  </div>
                  <div className="text-xs text-gray-500">
                    {request.farmerId}
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {request.governorate}
                </td>
                <td className="px-4 py-3">
                  <div
                    className="text-sm text-gray-700 max-w-xs truncate"
                    title={request.topic}
                  >
                    {request.topic}
                  </div>
                </td>
                <td className="px-4 py-3">
                  {request.expertName ? (
                    <span className="text-green-700">{request.expertName}</span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-center">
                  <span className="bg-gray-100 px-2 py-1 rounded text-sm">
                    {request.messagesCount}
                  </span>
                </td>
                <td className="px-4 py-3">{getStatusBadge(request.status)}</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {formatTime(request.createdAt)}
                </td>
                <td className="px-4 py-3 text-center">
                  <button
                    onClick={() => setSelectedRequest(request)}
                    className="text-green-600 hover:text-green-800 text-sm font-medium"
                  >
                    عرض
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredRequests.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            لا توجد طلبات دعم
          </div>
        )}
      </div>

      {/* Request Detail Modal */}
      {selectedRequest && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-100">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold">تفاصيل طلب الدعم</h3>
                  <p className="text-gray-500 text-sm mt-1">
                    الغرفة: {selectedRequest.roomId.split("_").pop()}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedRequest(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <div className="text-sm text-gray-500">المزارع</div>
                  <div className="font-medium">
                    {selectedRequest.farmerName}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">المحافظة</div>
                  <div className="font-medium">
                    {selectedRequest.governorate}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">الخبير</div>
                  <div className="font-medium">
                    {selectedRequest.expertName || "لم يتم التعيين"}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">الحالة</div>
                  <div>{getStatusBadge(selectedRequest.status)}</div>
                </div>
              </div>

              <div className="mb-6">
                <div className="text-sm text-gray-500 mb-1">الموضوع</div>
                <div className="bg-gray-50 rounded-lg p-3">
                  {selectedRequest.topic}
                </div>
              </div>

              <div className="mb-6">
                <div className="text-sm text-gray-500 mb-1">الجدول الزمني</div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>تم الإنشاء</span>
                    <span>
                      {new Date(selectedRequest.createdAt).toLocaleString(
                        "ar-YE",
                      )}
                    </span>
                  </div>
                  {selectedRequest.acceptedAt && (
                    <div className="flex justify-between text-green-600">
                      <span>تم القبول</span>
                      <span>
                        {new Date(selectedRequest.acceptedAt).toLocaleString(
                          "ar-YE",
                        )}
                      </span>
                    </div>
                  )}
                  {selectedRequest.resolvedAt && (
                    <div className="flex justify-between text-blue-600">
                      <span>تم الحل</span>
                      <span>
                        {new Date(selectedRequest.resolvedAt).toLocaleString(
                          "ar-YE",
                        )}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Mock Chat Preview */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-3">آخر الرسائل</div>
                <div className="space-y-2 text-sm">
                  <div className="bg-white rounded-lg p-2 max-w-[80%]">
                    <div className="text-xs text-gray-500">
                      {selectedRequest.farmerName}
                    </div>
                    <div>السلام عليكم، عندي مشكلة في المحصول...</div>
                  </div>
                  {selectedRequest.expertName && (
                    <div className="bg-green-100 rounded-lg p-2 max-w-[80%] mr-auto">
                      <div className="text-xs text-green-700">
                        {selectedRequest.expertName}
                      </div>
                      <div>أهلاً بك، هل يمكنك إرسال صورة؟</div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-100 flex gap-3">
              {selectedRequest.status === "pending" && (
                <button className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                  تعيين خبير
                </button>
              )}
              {selectedRequest.status === "active" && (
                <button className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                  إغلاق كمحلول
                </button>
              )}
              <button
                onClick={() => setSelectedRequest(null)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                إغلاق
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

// Copilot Management Page - Sahool AI Copilot Admin
// صفحة إدارة المساعد الذكي - لوحة تحكم سهول

import { useEffect, useState, useMemo, useCallback } from "react";
import Header from "@/components/layout/Header";
import { cn } from "@/lib/utils";
import { logger } from "../../lib/logger";
import { API_URLS } from "@/config/api";
import axios from "axios";
import {
  Bot,
  FileText,
  Shield,
  Wrench,
  RefreshCw,
  Plus,
  Trash2,
  Search,
  MessageSquare,
  Users,
  ShieldAlert,
  Database,
  ChevronLeft,
  ChevronRight,
  X,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  ExternalLink,
} from "lucide-react";

// ─── Constants ───────────────────────────────────────────────────────────────

const COPILOT_API = process.env.NEXT_PUBLIC_COPILOT_API_URL || "/api/copilot";

type TabId = "dashboard" | "rag" | "guards" | "tools";

const TABS: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: "dashboard", label: "لوحة المتابعة | Dashboard", icon: Bot },
  { id: "rag", label: "إدارة RAG | RAG Management", icon: FileText },
  { id: "guards", label: "سجل الحماية | Guard Logs", icon: Shield },
  { id: "tools", label: "الأدوات | Tools", icon: Wrench },
];

// ─── Types ───────────────────────────────────────────────────────────────────

interface RAGDocument {
  id: string;
  title: string;
  title_ar?: string;
  source?: string;
  content_type?: string;
  chunk_count?: number;
  created_at?: string;
  status?: string;
}

interface GuardLogEntry {
  id: string;
  tool_name: string;
  input_summary?: string;
  decision: "allowed" | "blocked" | "warning";
  reason?: string;
  timestamp: string;
  user_id?: string;
}

interface ToolInfo {
  name: string;
  description?: string;
  description_ar?: string;
  category?: string;
  allowed: boolean;
  requires_guard?: boolean;
}

interface DashboardStats {
  total_chats: number;
  active_users: number;
  blocked_tools: number;
  rag_docs_count: number;
}

// ─── API Functions ───────────────────────────────────────────────────────────

async function fetchDashboardStats(): Promise<DashboardStats> {
  // Aggregate stats from multiple endpoints
  const [docsRes, toolsRes] = await Promise.allSettled([
    axios.get(API_URLS.copilotEndpoints.ragDocuments),
    axios.get(API_URLS.copilotEndpoints.tools),
  ]);

  const docs =
    docsRes.status === "fulfilled" ? docsRes.value.data?.documents || docsRes.value.data || [] : [];
  const tools =
    toolsRes.status === "fulfilled" ? toolsRes.value.data?.tools || toolsRes.value.data || [] : [];

  const blockedCount = Array.isArray(tools)
    ? tools.filter((t: ToolInfo) => !t.allowed).length
    : 0;

  return {
    total_chats: 0,
    active_users: 0,
    blocked_tools: blockedCount,
    rag_docs_count: Array.isArray(docs) ? docs.length : 0,
  };
}

async function fetchRAGDocuments(): Promise<RAGDocument[]> {
  const res = await axios.get(API_URLS.copilotEndpoints.ragDocuments);
  return res.data?.documents || res.data || [];
}

async function addRAGDocument(payload: {
  title: string;
  title_ar?: string;
  content: string;
  source?: string;
}): Promise<RAGDocument> {
  const res = await axios.post(API_URLS.copilotEndpoints.ragDocuments, payload);
  return res.data;
}

async function deleteRAGDocument(id: string): Promise<void> {
  await axios.delete(`${API_URLS.copilotEndpoints.ragDocuments}/${encodeURIComponent(id)}`);
}

async function fetchGuardLogs(): Promise<GuardLogEntry[]> {
  // Guard logs are fetched via the guard endpoint with a dry run
  // In a real scenario, there would be a dedicated logs endpoint.
  // We simulate with a POST to guard with a probe payload.
  try {
    const res = await axios.post(API_URLS.copilotEndpoints.guardLogs, {
      tool_name: "__list_logs__",
      dry_run: true,
    });
    return res.data?.logs || res.data || [];
  } catch {
    // If guard endpoint doesn't return logs, return empty array
    return [];
  }
}

async function fetchTools(): Promise<ToolInfo[]> {
  const res = await axios.get(API_URLS.copilotEndpoints.tools);
  return res.data?.tools || res.data || [];
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function CopilotPage() {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const [isLoading, setIsLoading] = useState(true);

  // Dashboard state
  const [stats, setStats] = useState<DashboardStats>({
    total_chats: 0,
    active_users: 0,
    blocked_tools: 0,
    rag_docs_count: 0,
  });

  // RAG state
  const [ragDocs, setRagDocs] = useState<RAGDocument[]>([]);
  const [ragSearch, setRagSearch] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [addForm, setAddForm] = useState({
    title: "",
    title_ar: "",
    content: "",
    source: "",
  });
  const [isAdding, setIsAdding] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  // Guard logs state
  const [guardLogs, setGuardLogs] = useState<GuardLogEntry[]>([]);

  // Tools state
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [toolSearch, setToolSearch] = useState("");

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // ─── Data Loading ────────────────────────────────────────────────────────

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchDashboardStats();
      setStats(data);
    } catch (error) {
      logger.error("Failed to load copilot dashboard stats:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadRAGDocs = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchRAGDocuments();
      setRagDocs(data);
    } catch (error) {
      logger.error("Failed to load RAG documents:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadGuardLogs = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchGuardLogs();
      setGuardLogs(data);
    } catch (error) {
      logger.error("Failed to load guard logs:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadTools = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchTools();
      setTools(data);
    } catch (error) {
      logger.error("Failed to load tools:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadActiveTab = useCallback(() => {
    setCurrentPage(1);
    switch (activeTab) {
      case "dashboard":
        loadDashboard();
        break;
      case "rag":
        loadRAGDocs();
        break;
      case "guards":
        loadGuardLogs();
        break;
      case "tools":
        loadTools();
        break;
    }
  }, [activeTab, loadDashboard, loadRAGDocs, loadGuardLogs, loadTools]);

  useEffect(() => {
    loadActiveTab();
  }, [loadActiveTab]);

  // ─── RAG Actions ─────────────────────────────────────────────────────────

  const handleAddDocument = async () => {
    if (!addForm.title || !addForm.content) return;
    setIsAdding(true);
    try {
      await addRAGDocument({
        title: addForm.title,
        title_ar: addForm.title_ar || undefined,
        content: addForm.content,
        source: addForm.source || undefined,
      });
      setAddForm({ title: "", title_ar: "", content: "", source: "" });
      setShowAddModal(false);
      await loadRAGDocs();
    } catch (error) {
      logger.error("Failed to add RAG document:", error);
    } finally {
      setIsAdding(false);
    }
  };

  const handleDeleteDocument = async (id: string) => {
    setIsDeleting(id);
    try {
      await deleteRAGDocument(id);
      setRagDocs((prev) => prev.filter((d) => d.id !== id));
    } catch (error) {
      logger.error("Failed to delete RAG document:", error);
    } finally {
      setIsDeleting(null);
    }
  };

  // ─── Filtered Data ───────────────────────────────────────────────────────

  const filteredRagDocs = useMemo(() => {
    if (!ragSearch) return ragDocs;
    const query = ragSearch.toLowerCase();
    return ragDocs.filter(
      (d) =>
        d.title.toLowerCase().includes(query) ||
        (d.title_ar || "").toLowerCase().includes(query) ||
        (d.source || "").toLowerCase().includes(query),
    );
  }, [ragDocs, ragSearch]);

  const filteredTools = useMemo(() => {
    if (!toolSearch) return tools;
    const query = toolSearch.toLowerCase();
    return tools.filter(
      (t) =>
        t.name.toLowerCase().includes(query) ||
        (t.description || "").toLowerCase().includes(query) ||
        (t.description_ar || "").toLowerCase().includes(query) ||
        (t.category || "").toLowerCase().includes(query),
    );
  }, [tools, toolSearch]);

  // Paginated guard logs
  const totalGuardPages = Math.ceil(guardLogs.length / itemsPerPage);
  const paginatedGuardLogs = guardLogs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage,
  );

  // ─── Render Helpers ──────────────────────────────────────────────────────

  const formatTimestamp = (ts: string) => {
    try {
      const d = new Date(ts);
      return d.toLocaleDateString("ar-YE", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return ts;
    }
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case "allowed":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
            <CheckCircle2 className="w-3 h-3" />
            مسموح | Allowed
          </span>
        );
      case "blocked":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
            <XCircle className="w-3 h-3" />
            محظور | Blocked
          </span>
        );
      case "warning":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
            <AlertTriangle className="w-3 h-3" />
            تحذير | Warning
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
            {decision}
          </span>
        );
    }
  };

  // ─── Tab: Dashboard ──────────────────────────────────────────────────────

  const renderDashboard = () => (
    <>
      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <MessageSquare className="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total_chats}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">إجمالي المحادثات | Total Chats</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-green-50 rounded-lg">
              <Users className="w-5 h-5 text-green-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-green-600">{stats.active_users}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">المستخدمون النشطون | Active Users</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-red-50 rounded-lg">
              <ShieldAlert className="w-5 h-5 text-red-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-red-600">{stats.blocked_tools}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">أدوات محظورة | Blocked Tools</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Database className="w-5 h-5 text-purple-600" />
            </div>
          </div>
          <p className="text-2xl font-bold text-purple-600">{stats.rag_docs_count}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">مستندات RAG | RAG Documents</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-100 dark:border-gray-700">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
          إجراءات سريعة | Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setActiveTab("rag")}
            className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-right"
          >
            <div className="p-2 bg-purple-100 rounded-lg">
              <FileText className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">إدارة المستندات | Manage Documents</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إضافة وحذف مستندات RAG</p>
            </div>
          </button>

          <button
            onClick={() => setActiveTab("guards")}
            className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-right"
          >
            <div className="p-2 bg-amber-100 rounded-lg">
              <Shield className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">سجل الحماية | Guard Logs</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">مراجعة قرارات الحماية</p>
            </div>
          </button>

          <button
            onClick={() => setActiveTab("tools")}
            className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-right"
          >
            <div className="p-2 bg-blue-100 rounded-lg">
              <Wrench className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">الأدوات المتاحة | Available Tools</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">عرض وإدارة أدوات الكوبايلوت</p>
            </div>
          </button>
        </div>
      </div>

      {/* API Status */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-100 dark:border-gray-700">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
          حالة الخدمة | Service Status
        </h3>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-gray-700 dark:text-gray-300">copilot-api</span>
          </div>
          <a
            href={`${COPILOT_API}/healthz`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-sahool-600 hover:underline inline-flex items-center gap-1"
          >
            فحص الصحة | Health Check
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </>
  );

  // ─── Tab: RAG Management ─────────────────────────────────────────────────

  const renderRAG = () => (
    <>
      {/* Search & Actions */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث في المستندات... | Search documents..."
              value={ragSearch}
              onChange={(e) => setRagSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <button
            onClick={loadRAGDocs}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            title="تحديث | Refresh"
          >
            <RefreshCw
              className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")}
            />
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            إضافة مستند | Add Document
          </button>
        </div>
      </div>

      {/* RAG Documents Table */}
      {isLoading ? (
        <div className="mt-6 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="bg-gray-200 animate-pulse rounded-xl h-16" />
          ))}
        </div>
      ) : filteredRagDocs.length === 0 ? (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-100 dark:border-gray-700">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">لا توجد مستندات | No documents found</p>
        </div>
      ) : (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
                  <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                    العنوان | Title
                  </th>
                  <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                    المصدر | Source
                  </th>
                  <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                    النوع | Type
                  </th>
                  <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                    الأجزاء | Chunks
                  </th>
                  <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                    التاريخ | Date
                  </th>
                  <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                    الحالة | Status
                  </th>
                  <th className="px-4 py-3 w-12" />
                </tr>
              </thead>
              <tbody>
                {filteredRagDocs.map((doc) => (
                  <tr
                    key={doc.id}
                    className="border-b border-gray-50 dark:border-gray-700 hover:bg-gray-50/50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">
                          {doc.title_ar || doc.title}
                        </p>
                        {doc.title_ar && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">{doc.title}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                      {doc.source || "-"}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                        {doc.content_type || "text"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                      {doc.chunk_count ?? "-"}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                      {doc.created_at ? formatTimestamp(doc.created_at) : "-"}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          "inline-flex px-2 py-0.5 rounded text-xs font-medium",
                          doc.status === "active" || doc.status === "indexed"
                            ? "bg-green-100 text-green-700"
                            : doc.status === "processing"
                              ? "bg-amber-100 text-amber-700"
                              : "bg-gray-100 text-gray-700",
                        )}
                      >
                        {doc.status === "active" || doc.status === "indexed"
                          ? "مفهرس | Indexed"
                          : doc.status === "processing"
                            ? "قيد المعالجة | Processing"
                            : doc.status || "غير معروف"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        disabled={isDeleting === doc.id}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                        title="حذف | Delete"
                      >
                        {isDeleting === doc.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-100 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
            {filteredRagDocs.length} مستند | {filteredRagDocs.length} document(s)
          </div>
        </div>
      )}

      {/* Add Document Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowAddModal(false)}
          />
          <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto animate-slide-up">
            <button
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 left-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors z-10"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                إضافة مستند RAG
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Add RAG Document</p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    العنوان (إنجليزي) | Title (English) *
                  </label>
                  <input
                    type="text"
                    value={addForm.title}
                    onChange={(e) =>
                      setAddForm((prev) => ({ ...prev, title: e.target.value }))
                    }
                    className="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    placeholder="Document title..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    العنوان (عربي) | Title (Arabic)
                  </label>
                  <input
                    type="text"
                    value={addForm.title_ar}
                    onChange={(e) =>
                      setAddForm((prev) => ({ ...prev, title_ar: e.target.value }))
                    }
                    className="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    placeholder="عنوان المستند..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    المحتوى | Content *
                  </label>
                  <textarea
                    value={addForm.content}
                    onChange={(e) =>
                      setAddForm((prev) => ({ ...prev, content: e.target.value }))
                    }
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    placeholder="محتوى المستند... | Document content..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    المصدر | Source
                  </label>
                  <input
                    type="text"
                    value={addForm.source}
                    onChange={(e) =>
                      setAddForm((prev) => ({ ...prev, source: e.target.value }))
                    }
                    className="w-full px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    placeholder="https://... or file path"
                  />
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleAddDocument}
                  disabled={isAdding || !addForm.title || !addForm.content}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-sahool-600 text-white rounded-lg font-medium hover:bg-sahool-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isAdding ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Plus className="w-5 h-5" />
                  )}
                  {isAdding ? "جاري الإضافة..." : "إضافة | Add"}
                </button>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-3 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  إلغاء | Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );

  // ─── Tab: Guard Logs ─────────────────────────────────────────────────────

  const renderGuardLogs = () => (
    <>
      {/* Actions */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              سجل قرارات نظام الحماية للأدوات | Tool guard decision log
            </p>
          </div>
          <button
            onClick={loadGuardLogs}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            title="تحديث | Refresh"
          >
            <RefreshCw
              className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")}
            />
          </button>
        </div>
      </div>

      {/* Guard Logs Table */}
      {isLoading ? (
        <div className="mt-6 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="bg-gray-200 animate-pulse rounded-xl h-16" />
          ))}
        </div>
      ) : guardLogs.length === 0 ? (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-100 dark:border-gray-700">
          <Shield className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            لا توجد سجلات حماية | No guard logs available
          </p>
          <p className="text-sm text-gray-400 mt-2">
            ستظهر السجلات عند تشغيل الأدوات عبر الكوبايلوت
          </p>
        </div>
      ) : (
        <>
          <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
                    <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                      الأداة | Tool
                    </th>
                    <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                      الملخص | Summary
                    </th>
                    <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                      القرار | Decision
                    </th>
                    <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                      السبب | Reason
                    </th>
                    <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                      المستخدم | User
                    </th>
                    <th className="text-right px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                      الوقت | Time
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedGuardLogs.map((log) => (
                    <tr
                      key={log.id}
                      className="border-b border-gray-50 dark:border-gray-700 hover:bg-gray-50/50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center gap-1.5 font-medium text-gray-900 dark:text-gray-100">
                          <Wrench className="w-3.5 h-3.5 text-gray-400" />
                          {log.tool_name}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 max-w-[200px] truncate">
                        {log.input_summary || "-"}
                      </td>
                      <td className="px-4 py-3">{getDecisionBadge(log.decision)}</td>
                      <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400 max-w-[200px] truncate">
                        {log.reason || "-"}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                        {log.user_id || "-"}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                        <span className="inline-flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatTimestamp(log.timestamp)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {totalGuardPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
              <span className="px-4 py-2 text-sm">
                صفحة {currentPage} من {totalGuardPages}
              </span>
              <button
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalGuardPages, p + 1))
                }
                disabled={currentPage === totalGuardPages}
                className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      )}
    </>
  );

  // ─── Tab: Tools ──────────────────────────────────────────────────────────

  const renderTools = () => (
    <>
      {/* Search & Actions */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث في الأدوات... | Search tools..."
              value={toolSearch}
              onChange={(e) => setToolSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <button
            onClick={loadTools}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            title="تحديث | Refresh"
          >
            <RefreshCw
              className={cn("w-5 h-5 text-gray-600", isLoading && "animate-spin")}
            />
          </button>
        </div>
      </div>

      {/* Tools Grid */}
      {isLoading ? (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-gray-200 animate-pulse rounded-xl h-36" />
          ))}
        </div>
      ) : filteredTools.length === 0 ? (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-100 dark:border-gray-700">
          <Wrench className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            لا توجد أدوات | No tools available
          </p>
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTools.map((tool) => (
            <div
              key={tool.name}
              className={cn(
                "bg-white dark:bg-gray-800 rounded-xl p-5 border transition-all",
                tool.allowed
                  ? "border-gray-100 dark:border-gray-700 hover:border-green-200 hover:shadow-sm"
                  : "border-red-100 bg-red-50/30",
              )}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div
                    className={cn(
                      "p-2 rounded-lg",
                      tool.allowed ? "bg-green-50" : "bg-red-50",
                    )}
                  >
                    <Wrench
                      className={cn(
                        "w-4 h-4",
                        tool.allowed ? "text-green-600" : "text-red-600",
                      )}
                    />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100 text-sm">{tool.name}</p>
                    {tool.category && (
                      <span className="inline-flex px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 mt-0.5">
                        {tool.category}
                      </span>
                    )}
                  </div>
                </div>
                <span
                  className={cn(
                    "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
                    tool.allowed
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700",
                  )}
                >
                  {tool.allowed ? (
                    <>
                      <CheckCircle2 className="w-3 h-3" />
                      مسموح
                    </>
                  ) : (
                    <>
                      <XCircle className="w-3 h-3" />
                      محظور
                    </>
                  )}
                </span>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {tool.description_ar || tool.description || "بدون وصف | No description"}
              </p>

              {tool.requires_guard && (
                <div className="mt-3 flex items-center gap-1.5 text-xs text-amber-600">
                  <Shield className="w-3 h-3" />
                  يتطلب فحص الحماية | Requires guard check
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {!isLoading && tools.length > 0 && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex flex-wrap gap-6 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-gray-600 dark:text-gray-400">
                {tools.filter((t) => t.allowed).length} مسموح | Allowed
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-gray-600 dark:text-gray-400">
                {tools.filter((t) => !t.allowed).length} محظور | Blocked
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-gray-600 dark:text-gray-400">
                {tools.filter((t) => t.requires_guard).length} يتطلب حماية | Guarded
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );

  // ─── Main Render ─────────────────────────────────────────────────────────

  return (
    <div className="p-6">
      <Header
        title="إدارة المساعد الذكي | Copilot"
        subtitle="إدارة الكوبايلوت والأدوات ومستندات RAG"
      />

      {/* Tabs */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div className="flex border-b border-gray-100 dark:border-gray-700 overflow-x-auto">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-5 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors",
                  activeTab === tab.id
                    ? "border-sahool-600 text-sahool-600 bg-sahool-50/50"
                    : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700",
                )}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === "dashboard" && renderDashboard()}
      {activeTab === "rag" && renderRAG()}
      {activeTab === "guards" && renderGuardLogs()}
      {activeTab === "tools" && renderTools()}
    </div>
  );
}

/**
 * Scouting Feature - API Layer
 * طبقة API لميزة الكشافة الحقلية
 */

import { SCOUTING_ENDPOINTS, API_PREFIX } from "@sahool/shared-types/contracts";
import { type AxiosError } from "axios";
import { createApiClient, logger } from "@/lib/api/factory";
import type {
  ScoutingSession,
  Observation,
  ObservationFormData,
  ObservationCategory,
  Severity,
  ScoutingHistoryFilter,
  ScoutingStatistics,
  SessionSummary,
  ApiScoutingResponse,
  ApiSessionResponse,
  ApiSessionsListResponse,
  ApiObservationResponse,
  ApiObservationsListResponse,
  ApiStatisticsResponse,
} from "../types/scouting";

// Use shared API factory (handles auth, CSRF, error standardization)
const api = createApiClient({ timeout: 15000 });

// Cache configuration
const CACHE_KEY = "scouting_offline_cache";
const MAX_CACHE_SIZE = 100; // Maximum number of cached observations
const CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1000; // 7 days TTL

interface CachedObservation extends Observation {
  _offline?: boolean;
  _cachedAt?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages
// ═══════════════════════════════════════════════════════════════════════════

export const ERROR_MESSAGES = {
  SESSION_CREATE_FAILED: {
    en: "Failed to start scouting session. Please try again.",
    ar: "فشل في بدء جلسة الكشافة. الرجاء المحاولة مرة أخرى.",
  },
  SESSION_END_FAILED: {
    en: "Failed to end scouting session. Please try again.",
    ar: "فشل في إنهاء جلسة الكشافة. الرجاء المحاولة مرة أخرى.",
  },
  OBSERVATION_CREATE_FAILED: {
    en: "Failed to save observation. Please try again.",
    ar: "فشل في حفظ الملاحظة. الرجاء المحاولة مرة أخرى.",
  },
  OBSERVATION_UPDATE_FAILED: {
    en: "Failed to update observation. Please try again.",
    ar: "فشل في تحديث الملاحظة. الرجاء المحاولة مرة أخرى.",
  },
  OBSERVATION_DELETE_FAILED: {
    en: "Failed to delete observation. Please try again.",
    ar: "فشل في حذف الملاحظة. الرجاء المحاولة مرة أخرى.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch data. Using cached data.",
    ar: "فشل في جلب البيانات. استخدام البيانات المخزنة.",
  },
  NETWORK_ERROR: {
    en: "Network error. Please check your connection.",
    ar: "خطأ في الاتصال. يرجى التحقق من الاتصال.",
  },
  PHOTO_UPLOAD_FAILED: {
    en: "Failed to upload photo. Please try again.",
    ar: "فشل في تحميل الصورة. الرجاء المحاولة مرة أخرى.",
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Mock Data for Offline Support
// ═══════════════════════════════════════════════════════════════════════════

const MOCK_SESSION: ScoutingSession = {
  id: "session-1",
  fieldId: "1",
  fieldName: "North Field",
  fieldNameAr: "الحقل الشمالي",
  status: "active",
  startTime: new Date().toISOString(),
  scoutId: "user-1",
  scoutName: "Ahmed Al-Shahrani",
  observationsCount: 0,
  observations: [],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Upload photo to server
 */
async function uploadPhoto(file: File, sessionId: string): Promise<string> {
  const formData = new FormData();
  formData.append("photo", file);
  formData.append("sessionId", sessionId);

  try {
    const response = await api.post(`${API_PREFIX}/scouting/photos`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data.data?.url || response.data.url;
  } catch (error) {
    logger.error("Failed to upload photo:", error);
    throw new Error(ERROR_MESSAGES.PHOTO_UPLOAD_FAILED.en);
  }
}

/**
 * Validate that a cached observation has the expected shape.
 */
function isValidCachedObservation(item: unknown): item is CachedObservation {
  if (!item || typeof item !== "object") return false;
  const obj = item as Record<string, unknown>;
  return (
    typeof obj.id === "string" &&
    typeof obj.sessionId === "string" &&
    typeof obj.category === "string" &&
    typeof obj.createdAt === "string"
  );
}

/**
 * Store observation in offline cache
 */
function cacheObservation(observation: Observation): void {
  if (typeof window === "undefined") return;

  try {
    const cached = localStorage.getItem(CACHE_KEY);
    let cache: CachedObservation[] = [];

    if (cached) {
      const parsed = JSON.parse(cached);
      if (Array.isArray(parsed)) {
        cache = parsed.filter(isValidCachedObservation);
      }
    }

    // Enforce max cache size - remove oldest entries if at limit
    if (cache.length >= MAX_CACHE_SIZE) {
      cache = cache.slice(cache.length - MAX_CACHE_SIZE + 1);
    }

    cache.push({
      ...observation,
      _offline: true,
      _cachedAt: new Date().toISOString(),
    });
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
  } catch (error) {
    logger.warn("Failed to cache observation:", error);
  }
}

/**
 * Get offline cached observations, filtering out expired entries.
 */
function getCachedObservations(): Observation[] {
  if (typeof window === "undefined") return [];

  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return [];

    const parsed = JSON.parse(cached);
    if (!Array.isArray(parsed)) {
      logger.warn("Invalid scouting cache format, clearing");
      localStorage.removeItem(CACHE_KEY);
      return [];
    }

    const now = Date.now();
    const valid = parsed.filter((item: unknown) => {
      if (!isValidCachedObservation(item)) return false;
      // Check TTL expiration
      if (item._cachedAt) {
        const cachedTime = new Date(item._cachedAt).getTime();
        if (now - cachedTime > CACHE_TTL_MS) return false;
      }
      return true;
    });

    // Update cache if expired entries were removed
    if (valid.length !== parsed.length) {
      localStorage.setItem(CACHE_KEY, JSON.stringify(valid));
    }

    return valid;
  } catch (error) {
    logger.warn("Failed to get cached observations:", error);
    localStorage.removeItem(CACHE_KEY);
    return [];
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

export const scoutingApi = {
  // ───────────────────────────────────────────────────────────────────────────
  // Session Management
  // ───────────────────────────────────────────────────────────────────────────

  /**
   * Start a new scouting session
   * بدء جلسة كشافة جديدة
   */
  startSession: async (
    fieldId: string,
    notes?: string,
  ): Promise<ScoutingSession> => {
    try {
      const response = await api.post<ApiSessionResponse>(
        `${API_PREFIX}/scouting/sessions`,
        {
          fieldId,
          notes,
          startTime: new Date().toISOString(),
        },
      );

      return response.data.data || MOCK_SESSION;
    } catch (error) {
      logger.warn("Failed to start session via API, using mock data:", error);

      // Return mock session for offline use
      return {
        ...MOCK_SESSION,
        fieldId,
        notes,
        id: `offline-session-${Date.now()}`,
      };
    }
  },

  /**
   * End an active scouting session
   * إنهاء جلسة كشافة نشطة
   */
  endSession: async (
    sessionId: string,
    notes?: string,
  ): Promise<ScoutingSession> => {
    try {
      const response = await api.put<ApiSessionResponse>(
        `${API_PREFIX}/scouting/sessions/${sessionId}/end`,
        {
          endTime: new Date().toISOString(),
          notes,
        },
      );

      return (
        response.data.data || {
          ...MOCK_SESSION,
          id: sessionId,
          status: "completed",
        }
      );
    } catch (error) {
      logger.error("Failed to end session:", error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.SESSION_END_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.SESSION_END_FAILED.ar;

      throw new Error(
        JSON.stringify({ message: errorMessage, messageAr: errorMessageAr }),
      );
    }
  },

  /**
   * Get session by ID
   * الحصول على جلسة بواسطة المعرف
   */
  getSession: async (sessionId: string): Promise<ScoutingSession> => {
    try {
      const response = await api.get<ApiSessionResponse>(
        `${API_PREFIX}/scouting/sessions/${sessionId}`,
      );
      return response.data.data || { ...MOCK_SESSION, id: sessionId };
    } catch (error) {
      logger.warn(`Failed to fetch session ${sessionId}:`, error);
      return { ...MOCK_SESSION, id: sessionId };
    }
  },

  /**
   * Get active session for a field
   * الحصول على الجلسة النشطة لحقل
   */
  getActiveSession: async (
    fieldId: string,
  ): Promise<ScoutingSession | null> => {
    try {
      const response = await api.get<ApiSessionResponse>(
        `${API_PREFIX}/scouting/sessions/active`,
        {
          params: { fieldId },
        },
      );
      return response.data.data || null;
    } catch (error) {
      logger.warn(`No active session found for field ${fieldId}:`, error);
      return null;
    }
  },

  /**
   * Get session summary
   * الحصول على ملخص الجلسة
   */
  getSessionSummary: async (sessionId: string): Promise<SessionSummary> => {
    try {
      const response = await api.get<ApiScoutingResponse<SessionSummary>>(
        `${API_PREFIX}/scouting/sessions/${sessionId}/summary`,
      );
      return (
        response.data.data || {
          totalObservations: 0,
          byCategory: {} as Record<ObservationCategory, number>,
          bySeverity: {} as Record<Severity, number>,
          averageSeverity: 0,
          criticalIssues: 0,
          tasksCreated: 0,
          photosTaken: 0,
        }
      );
    } catch (error) {
      logger.warn(`Failed to fetch session summary for ${sessionId}:`, error);
      return {
        totalObservations: 0,
        byCategory: {} as Record<ObservationCategory, number>,
        bySeverity: {} as Record<Severity, number>,
        averageSeverity: 0,
        criticalIssues: 0,
        tasksCreated: 0,
        photosTaken: 0,
      };
    }
  },

  // ───────────────────────────────────────────────────────────────────────────
  // Observation Management
  // ───────────────────────────────────────────────────────────────────────────

  /**
   * Add observation to session
   * إضافة ملاحظة إلى الجلسة
   */
  addObservation: async (
    sessionId: string,
    data: ObservationFormData,
  ): Promise<Observation> => {
    try {
      // Upload photos first if any
      let photoUrls: string[] = [];
      if (data.photos && data.photos.length > 0) {
        photoUrls = await Promise.all(
          data.photos.map((file) => uploadPhoto(file, sessionId)),
        );
      }

      const observationData = {
        sessionId,
        location: data.location,
        locationName: data.locationName,
        locationNameAr: data.locationNameAr,
        category: data.category,
        subcategory: data.subcategory,
        subcategoryAr: data.subcategoryAr,
        severity: data.severity,
        notes: data.notes,
        notesAr: data.notesAr,
        photoUrls,
        createTask: data.createTask,
      };

      const response = await api.post<ApiObservationResponse>(
        `${API_PREFIX}/scouting/observations`,
        observationData,
      );

      return response.data.data!;
    } catch (error) {
      logger.error("Failed to create observation:", error);

      // Create offline observation
      const observation: Observation = {
        id: `offline-obs-${Date.now()}`,
        sessionId,
        fieldId: "", // Will be filled from session
        location: data.location,
        locationName: data.locationName,
        locationNameAr: data.locationNameAr,
        category: data.category,
        subcategory: data.subcategory,
        subcategoryAr: data.subcategoryAr,
        severity: data.severity,
        notes: data.notes,
        notesAr: data.notesAr,
        photos: [],
        taskCreated: data.createTask,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      // Cache for later sync
      cacheObservation(observation);

      return observation;
    }
  },

  /**
   * Update observation
   * تحديث ملاحظة
   */
  updateObservation: async (
    observationId: string,
    data: Partial<ObservationFormData>,
  ): Promise<Observation> => {
    try {
      const response = await api.put<ApiObservationResponse>(
        `${API_PREFIX}/scouting/observations/${observationId}`,
        data,
      );

      return response.data.data!;
    } catch (error) {
      logger.error(`Failed to update observation ${observationId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.OBSERVATION_UPDATE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.OBSERVATION_UPDATE_FAILED.ar;

      throw new Error(
        JSON.stringify({ message: errorMessage, messageAr: errorMessageAr }),
      );
    }
  },

  /**
   * Delete observation
   * حذف ملاحظة
   */
  deleteObservation: async (observationId: string): Promise<void> => {
    try {
      await api.delete(`${API_PREFIX}/scouting/observations/${observationId}`);
    } catch (error) {
      logger.error(`Failed to delete observation ${observationId}:`, error);

      const axiosError = error as AxiosError<{
        message?: string;
        message_ar?: string;
      }>;
      const errorMessage =
        axiosError.response?.data?.message ||
        ERROR_MESSAGES.OBSERVATION_DELETE_FAILED.en;
      const errorMessageAr =
        axiosError.response?.data?.message_ar ||
        ERROR_MESSAGES.OBSERVATION_DELETE_FAILED.ar;

      throw new Error(
        JSON.stringify({ message: errorMessage, messageAr: errorMessageAr }),
      );
    }
  },

  /**
   * Get observations for session
   * الحصول على ملاحظات الجلسة
   */
  getObservations: async (sessionId: string): Promise<Observation[]> => {
    try {
      const response = await api.get<ApiObservationsListResponse>(
        `${API_PREFIX}/scouting/sessions/${sessionId}/observations`,
      );
      return response.data.data || [];
    } catch (error) {
      logger.warn(
        `Failed to fetch observations for session ${sessionId}:`,
        error,
      );

      // Return cached observations if offline
      return getCachedObservations().filter(
        (obs) => obs.sessionId === sessionId,
      );
    }
  },

  // ───────────────────────────────────────────────────────────────────────────
  // History & Statistics
  // ───────────────────────────────────────────────────────────────────────────

  /**
   * Get scouting history
   * الحصول على سجل الكشافة
   */
  getHistory: async (
    filters?: ScoutingHistoryFilter,
  ): Promise<ScoutingSession[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.fieldId) params.set("fieldId", filters.fieldId);
      if (filters?.scoutId) params.set("scoutId", filters.scoutId);
      if (filters?.category) params.set("category", filters.category);
      if (filters?.minSeverity)
        params.set("minSeverity", filters.minSeverity.toString());
      if (filters?.startDate) params.set("startDate", filters.startDate);
      if (filters?.endDate) params.set("endDate", filters.endDate);
      if (filters?.status) params.set("status", filters.status);

      const response = await api.get<ApiSessionsListResponse>(
        `${API_PREFIX}/scouting/sessions?${params.toString()}`,
      );

      return response.data.data || [];
    } catch (error) {
      logger.warn("Failed to fetch scouting history:", error);
      return [];
    }
  },

  /**
   * Get scouting statistics
   * الحصول على إحصائيات الكشافة
   */
  getStatistics: async (fieldId?: string): Promise<ScoutingStatistics> => {
    try {
      const params = fieldId ? `?fieldId=${fieldId}` : "";
      const response = await api.get<ApiStatisticsResponse>(
        `${SCOUTING_ENDPOINTS.STATS}${params}`,
      );

      return (
        response.data.data || {
          totalSessions: 0,
          totalObservations: 0,
          averageObservationsPerSession: 0,
          mostCommonCategory: "other",
          mostCommonSeverity: 3,
          sessionsThisWeek: 0,
          sessionsThisMonth: 0,
          trendData: [],
        }
      );
    } catch (error) {
      logger.warn("Failed to fetch scouting statistics:", error);
      return {
        totalSessions: 0,
        totalObservations: 0,
        averageObservationsPerSession: 0,
        mostCommonCategory: "other",
        mostCommonSeverity: 3,
        sessionsThisWeek: 0,
        sessionsThisMonth: 0,
        trendData: [],
      };
    }
  },

  // ───────────────────────────────────────────────────────────────────────────
  // Report Generation
  // ───────────────────────────────────────────────────────────────────────────

  /**
   * Generate scouting report
   * إنشاء تقرير الكشافة
   */
  generateReport: async (
    sessionId: string,
    config: {
      includePhotos?: boolean;
      includeMap?: boolean;
      language?: "en" | "ar" | "both";
      format?: "pdf" | "excel";
    } = {},
  ): Promise<{ downloadUrl: string }> => {
    try {
      const response = await api.post(
        `${API_PREFIX}/scouting/sessions/${sessionId}/report`,
        {
          includePhotos: config.includePhotos ?? true,
          includeMap: config.includeMap ?? true,
          language: config.language ?? "both",
          format: config.format ?? "pdf",
        },
      );

      return {
        downloadUrl:
          response.data.data?.downloadUrl || response.data.downloadUrl,
      };
    } catch (error) {
      logger.error("Failed to generate report:", error);
      throw new Error("Failed to generate report. Please try again.");
    }
  },

  // ───────────────────────────────────────────────────────────────────────────
  // Offline Sync
  // ───────────────────────────────────────────────────────────────────────────

  /**
   * Sync offline observations
   * مزامنة الملاحظات غير المتصلة
   */
  syncOfflineData: async (): Promise<{ synced: number; failed: number }> => {
    const cached = getCachedObservations();
    if (cached.length === 0) {
      return { synced: 0, failed: 0 };
    }

    let synced = 0;
    let failed = 0;

    for (const observation of cached) {
      try {
        await api.post(`${API_PREFIX}/scouting/observations`, observation);
        synced++;
      } catch (error) {
        logger.error("Failed to sync observation:", error);
        failed++;
      }
    }

    // Clear synced observations
    if (synced > 0) {
      try {
        localStorage.removeItem("scouting_offline_cache");
      } catch (error) {
        logger.warn("Failed to clear offline cache:", error);
      }
    }

    return { synced, failed };
  },
};

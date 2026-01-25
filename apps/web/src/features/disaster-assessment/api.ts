/**
 * Disaster Assessment Feature - API Layer
 * طبقة API لميزة تقييم الكوارث
 */

import axios from "axios";
import { logger } from "@/lib/logger";
import Cookies from "js-cookie";
import type {
  RiskAssessment,
  DisasterEvent,
  DisasterFilters,
  DisasterFormData,
  DisasterStats,
  WeatherAlert,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = Cookies.get("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: "Network error. Using cached data.",
    ar: "خطأ في الاتصال. استخدام البيانات المخزنة.",
  },
  FETCH_FAILED: {
    en: "Failed to fetch disaster assessment data.",
    ar: "فشل في جلب بيانات تقييم الكوارث.",
  },
  CREATE_FAILED: {
    en: "Failed to create disaster event.",
    ar: "فشل في إنشاء حدث الكارثة.",
  },
};

const MOCK_RISKS: RiskAssessment[] = [
  {
    id: "1",
    type: "drought",
    typeAr: "جفاف",
    riskLevel: "medium",
    affectedArea: "Central Region",
    affectedAreaAr: "المنطقة الوسطى",
    probability: 45,
    potentialLoss: 150000,
    currency: "SAR",
    mitigationPlan: "Activate emergency irrigation reserves",
    mitigationPlanAr: "تفعيل احتياطيات الري الطارئة",
    lastUpdated: "2026-01-25",
    metadata: {},
    createdAt: "2026-01-20T10:00:00Z",
    updatedAt: "2026-01-25T08:00:00Z",
  },
  {
    id: "2",
    type: "frost",
    typeAr: "صقيع",
    riskLevel: "high",
    affectedArea: "Northern Farms",
    affectedAreaAr: "المزارع الشمالية",
    probability: 70,
    potentialLoss: 85000,
    currency: "SAR",
    mitigationPlan: "Deploy frost protection covers",
    mitigationPlanAr: "نشر أغطية الحماية من الصقيع",
    lastUpdated: "2026-01-25",
    metadata: {},
    createdAt: "2026-01-22T09:00:00Z",
    updatedAt: "2026-01-25T07:00:00Z",
  },
  {
    id: "3",
    type: "pest",
    typeAr: "آفات",
    riskLevel: "low",
    affectedArea: "Al-Kharj Fields",
    affectedAreaAr: "حقول الخرج",
    probability: 25,
    potentialLoss: 45000,
    currency: "SAR",
    lastUpdated: "2026-01-24",
    metadata: {},
    createdAt: "2026-01-15T14:00:00Z",
    updatedAt: "2026-01-24T11:00:00Z",
  },
  {
    id: "4",
    type: "storm",
    typeAr: "عاصفة",
    riskLevel: "critical",
    affectedArea: "Eastern Province",
    affectedAreaAr: "المنطقة الشرقية",
    probability: 85,
    potentialLoss: 320000,
    currency: "SAR",
    mitigationPlan: "Secure equipment, harvest ripe crops immediately",
    mitigationPlanAr: "تأمين المعدات، حصاد المحاصيل الناضجة فوراً",
    lastUpdated: "2026-01-25",
    metadata: {},
    createdAt: "2026-01-25T05:00:00Z",
    updatedAt: "2026-01-25T10:00:00Z",
  },
];

const MOCK_EVENTS: DisasterEvent[] = [
  {
    id: "1",
    type: "storm",
    typeAr: "عاصفة رملية",
    date: "2026-01-20",
    location: "Qassim Region",
    locationAr: "منطقة القصيم",
    affectedArea: 150,
    areaUnit: "hectares",
    severity: "moderate",
    status: "resolved",
    damageEstimate: 25000,
    currency: "SAR",
    description: "Sandstorm causing minor crop damage",
    descriptionAr: "عاصفة رملية تسببت في أضرار طفيفة للمحاصيل",
    metadata: {},
    createdAt: "2026-01-20T14:00:00Z",
    updatedAt: "2026-01-22T10:00:00Z",
  },
  {
    id: "2",
    type: "flood",
    typeAr: "سيول",
    date: "2026-01-18",
    location: "Asir Mountains",
    locationAr: "جبال عسير",
    affectedArea: 80,
    areaUnit: "hectares",
    severity: "severe",
    status: "monitoring",
    damageEstimate: 180000,
    currency: "SAR",
    description: "Flash flooding from heavy rainfall",
    descriptionAr: "فيضانات مفاجئة من الأمطار الغزيرة",
    affectedCrops: ["vegetables", "fruits"],
    metadata: {},
    createdAt: "2026-01-18T08:00:00Z",
    updatedAt: "2026-01-24T16:00:00Z",
  },
];

const MOCK_STATS: DisasterStats = {
  activeRisks: 4,
  criticalRisks: 2,
  totalPotentialLoss: 600000,
  activeEvents: 1,
  totalDamage: 205000,
  eventsThisYear: 2,
  byType: {
    drought: 1,
    frost: 1,
    pest: 1,
    storm: 1,
    flood: 0,
    disease: 0,
    fire: 0,
    other: 0,
  },
  byRiskLevel: {
    low: 1,
    medium: 1,
    high: 1,
    critical: 1,
  },
  recentAlerts: 3,
};

export const disasterApi = {
  getRisks: async (filters?: DisasterFilters): Promise<RiskAssessment[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set("type", filters.type);
      if (filters?.riskLevel) params.set("risk_level", filters.riskLevel);
      if (filters?.search) params.set("search", filters.search);

      const response = await api.get(`/api/v1/disaster/risks?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      logger.warn("API returned unexpected format, using mock data");
      return MOCK_RISKS;
    } catch (error) {
      logger.warn("Failed to fetch risks, using mock data:", error);
      return MOCK_RISKS;
    }
  },

  getRiskById: async (id: string): Promise<RiskAssessment> => {
    try {
      const response = await api.get(`/api/v1/disaster/risks/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch risk ${id}, using mock data:`, error);
      const mockRisk = MOCK_RISKS.find((r) => r.id === id);
      if (mockRisk) return mockRisk;
      throw new Error(`Risk assessment with ID ${id} not found`);
    }
  },

  getEvents: async (filters?: DisasterFilters): Promise<DisasterEvent[]> => {
    try {
      const params = new URLSearchParams();
      if (filters?.type) params.set("type", filters.type);
      if (filters?.status) params.set("status", filters.status);
      if (filters?.dateFrom) params.set("date_from", filters.dateFrom);
      if (filters?.dateTo) params.set("date_to", filters.dateTo);

      const response = await api.get(`/api/v1/disaster/events?${params.toString()}`);
      const data = response.data.data || response.data;

      if (Array.isArray(data)) {
        return data;
      }

      return MOCK_EVENTS;
    } catch (error) {
      logger.warn("Failed to fetch events, using mock data:", error);
      return MOCK_EVENTS;
    }
  },

  getEventById: async (id: string): Promise<DisasterEvent> => {
    try {
      const response = await api.get(`/api/v1/disaster/events/${id}`);
      return response.data.data || response.data;
    } catch (error) {
      logger.warn(`Failed to fetch event ${id}, using mock data:`, error);
      const mockEvent = MOCK_EVENTS.find((e) => e.id === id);
      if (mockEvent) return mockEvent;
      throw new Error(`Disaster event with ID ${id} not found`);
    }
  },

  createEvent: async (data: DisasterFormData): Promise<DisasterEvent> => {
    try {
      const response = await api.post("/api/v1/disaster/events", data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error("Failed to create disaster event:", error);
      throw error;
    }
  },

  updateEvent: async (id: string, data: Partial<DisasterFormData>): Promise<DisasterEvent> => {
    try {
      const response = await api.put(`/api/v1/disaster/events/${id}`, data);
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update event ${id}:`, error);
      throw error;
    }
  },

  updateEventStatus: async (id: string, status: string): Promise<DisasterEvent> => {
    try {
      const response = await api.patch(`/api/v1/disaster/events/${id}/status`, { status });
      return response.data.data || response.data;
    } catch (error) {
      logger.error(`Failed to update event status ${id}:`, error);
      throw error;
    }
  },

  getWeatherAlerts: async (): Promise<WeatherAlert[]> => {
    try {
      const response = await api.get("/api/v1/disaster/weather-alerts");
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Failed to fetch weather alerts:", error);
      return [];
    }
  },

  getStats: async (): Promise<DisasterStats> => {
    try {
      const response = await api.get("/api/v1/disaster/stats");
      return response.data.data || response.data;
    } catch (error) {
      logger.warn("Failed to fetch disaster stats, using mock data:", error);
      return MOCK_STATS;
    }
  },
};

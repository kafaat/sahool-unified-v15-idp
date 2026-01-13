/**
 * Sahool Admin Dashboard Types
 * أنواع البيانات للوحة تحكم سهول
 *
 * This file re-exports shared types and adds admin-specific extensions
 */

// Re-export all shared types from api-client
export type {
  // Core Types
  Locale,
  Priority,
  Severity,
  TaskStatus,
  DiagnosisStatus,
  FarmStatus,
  // Geometry Types
  Coordinates,
  GeoPosition,
  GeoPoint,
  GeoPolygon,
  GeoMultiPolygon,
  GeoLineString,
  GeoGeometry,
  GeoFeature,
  GeoFeatureCollection,
  // Domain Types
  Task,
  CreateTaskRequest,
  TaskEvidence,
  Field,
  Farm,
  WeatherData,
  WeatherForecast,
  DailyForecast,
  WeatherAlert,
  DiagnosisRecord,
  ExpertReview,
  DiagnosisStats,
  DashboardStats,
  DashboardData,
  FieldIndicators,
  Indicator,
  SensorReading,
  Equipment,
  Notification,
  CommunityPost,
  // Alert Types
  AlertSeverity,
  AlertCategory,
  AlertStatus,
  Alert,
  AlertFilters,
  AlertStats,
  // User & Auth Types
  UserRole,
  User,
  AuthState,
  LoginRequest,
  LoginResponse,
  // KPI Types
  TrendDirection,
  HealthStatus,
  KPI,
  // Other
  Governorate,
  Treatment,
  ApiResponse,
  PaginatedResponse,
  ApiClientConfig,
  ServicePorts,
} from "@sahool/api-client";

// ═══════════════════════════════════════════════════════════════════════════
// Admin-specific type extensions
// ═══════════════════════════════════════════════════════════════════════════

import type {
  Farm as BaseFarm,
  DiagnosisRecord as BaseDiagnosis,
  SensorReading as BaseSensorReading,
  Governorate as BaseGovernorate,
  GeoPolygon,
  Treatment,
} from "@sahool/api-client";

/** Extended Farm type with admin-specific fields */
export interface AdminFarm extends BaseFarm {
  polygon?: GeoPolygon;
  district?: string;
}

/** Extended Diagnosis with treatment info */
export interface AdminDiagnosisRecord extends BaseDiagnosis {
  treatment?: Treatment;
}

/** Extended Sensor Reading with virtual sensor support */
export interface AdminSensorReading extends BaseSensorReading {
  isVirtual: boolean;
}

/** Admin-specific user roles */
export type AdminUserRole = "admin" | "expert" | "viewer";

// ═══════════════════════════════════════════════════════════════════════════
// Yemen governorates for the map
// ═══════════════════════════════════════════════════════════════════════════

export const YEMEN_GOVERNORATES: BaseGovernorate[] = [
  {
    id: "sanaa",
    name: "Sanaa",
    nameAr: "صنعاء",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 15.3694, lng: 44.191 },
  },
  {
    id: "aden",
    name: "Aden",
    nameAr: "عدن",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 12.7855, lng: 45.0187 },
  },
  {
    id: "taiz",
    name: "Taiz",
    nameAr: "تعز",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 13.5789, lng: 44.0219 },
  },
  {
    id: "hadramaut",
    name: "Hadramaut",
    nameAr: "حضرموت",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 15.9543, lng: 48.7863 },
  },
  {
    id: "ibb",
    name: "Ibb",
    nameAr: "إب",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 13.9728, lng: 44.1693 },
  },
  {
    id: "hodeidah",
    name: "Al Hudaydah",
    nameAr: "الحديدة",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 14.7979, lng: 42.954 },
  },
  {
    id: "dhamar",
    name: "Dhamar",
    nameAr: "ذمار",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 14.5427, lng: 44.4051 },
  },
  {
    id: "marib",
    name: "Marib",
    nameAr: "مأرب",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 15.4547, lng: 45.3268 },
  },
  {
    id: "hajjah",
    name: "Hajjah",
    nameAr: "حجة",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 15.6917, lng: 43.6033 },
  },
  {
    id: "amran",
    name: "Amran",
    nameAr: "عمران",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 15.6594, lng: 43.9439 },
  },
  {
    id: "saadah",
    name: "Saadah",
    nameAr: "صعدة",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 16.941, lng: 43.7636 },
  },
  {
    id: "lahij",
    name: "Lahij",
    nameAr: "لحج",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 13.0337, lng: 44.8833 },
  },
  {
    id: "abyan",
    name: "Abyan",
    nameAr: "أبين",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 13.5833, lng: 45.8667 },
  },
  {
    id: "shabwah",
    name: "Shabwah",
    nameAr: "شبوة",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 14.5333, lng: 46.8333 },
  },
  {
    id: "albaydah",
    name: "Al Bayda",
    nameAr: "البيضاء",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 14.1667, lng: 45.5667 },
  },
  {
    id: "aljawf",
    name: "Al Jawf",
    nameAr: "الجوف",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 16.5, lng: 45.5 },
  },
  {
    id: "almahwit",
    name: "Al Mahwit",
    nameAr: "المحويت",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 15.4667, lng: 43.55 },
  },
  {
    id: "almahrah",
    name: "Al Mahrah",
    nameAr: "المهرة",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 16.5, lng: 51.5 },
  },
  {
    id: "raymah",
    name: "Raymah",
    nameAr: "ريمة",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 14.6167, lng: 43.7167 },
  },
  {
    id: "socotra",
    name: "Socotra",
    nameAr: "سقطرى",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 12.4634, lng: 53.8237 },
  },
  {
    id: "aldhalei",
    name: "Ad Dali",
    nameAr: "الضالع",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 13.6833, lng: 44.7333 },
  },
  {
    id: "sanaa_city",
    name: "Sanaa City",
    nameAr: "أمانة العاصمة",
    farmCount: 0,
    totalArea: 0,
    avgHealthScore: 0,
    coordinates: { lat: 15.3694, lng: 44.191 },
  },
];

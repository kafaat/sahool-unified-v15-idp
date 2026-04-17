/**
 * SAHOOL Admin Advanced API Services v16.0.0
 * خدمات API المتقدمة للوحة الإدارة - سهول
 *
 * API integration for audit, vision, terrain, edge devices, drones,
 * virtual sensors, and scouting services.
 *
 * Uses centralized API config from @/config/api
 */

import { logger } from '../logger';
import type { PaginationParams, PaginatedResponse } from './services';
import { SERVICE_URLS, API_URLS } from '@/config/api';

// Default fetch options — httpOnly cookies
const fetchDefaults: RequestInit = {
  credentials: 'same-origin',
};

// =============================================================================
// CSV Export Helper | مساعد تصدير CSV
// =============================================================================

/**
 * Download an array of objects as a CSV file
 * تحميل مصفوفة من الكائنات كملف CSV
 */
export function downloadCSV(data: Record<string, unknown>[] | object[], filename: string): void {
  if (data.length === 0 || !data[0]) return;
  const rows = data as Record<string, unknown>[];
  const first = rows[0];
  if (!first) return;
  const headers = Object.keys(first);
  const csvRows = [
    headers.join(','),
    ...rows.map((row) =>
      headers
        .map((h) => {
          const val = row[h];
          const str = val === null || val === undefined ? '' : String(val);
          // Escape quotes and wrap in quotes if needed
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str;
        })
        .join(',')
    ),
  ];
  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

// =============================================================================
// Audit Service | خدمة التدقيق
// =============================================================================

/** سجل التدقيق — Audit log entry */
export interface AuditLog {
  id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  ip_address: string;
  details: Record<string, unknown>;
  status: 'success' | 'failure';
}

/** إحصائيات التدقيق — Audit statistics */
export interface AuditStats {
  total_logs: number;
  actions_today: number;
  unique_users: number;
  failure_rate: number;
  top_actions: Array<{ action: string; count: number }>;
}

// Raw shape returned by audit-service's /audit/logs (snake_case,
// skip/limit/has_more). We map this to the admin's PaginatedResponse<T>
// shape (data/meta) so callers and DataTable keep working. Without this
// mapping the page silently renders empty because `response.data` is
// undefined on the real backend shape.
//
// Request-side note:
//   We send ONLY the audit-service-native parameter names
//   (skip/limit/start_date/end_date). No admin-side BFF wraps this
//   endpoint today; `API_URLS.auditEndpoints.logs` resolves directly
//   to port 8114 (audit-service). If someone later inserts a BFF,
//   update the param set HERE — don't double-send page+skip or
//   from+start_date, because different receivers would interpret
//   them inconsistently.
//
// Response-side fallback:
//   The `data?: T[]` + `meta?: {...}` branch below is purely
//   DEFENSIVE against a hypothetical future BFF wrapper that might
//   rewrap the response. It does NOT imply such a BFF exists today.
interface AuditServicePaginated<T> {
  items?: T[];
  total?: number;
  skip?: number;
  limit?: number;
  has_more?: boolean;
  // Hypothetical-BFF fallback — see note above. Never set in
  // production today; kept so a future wrap doesn't break the UI.
  data?: T[];
  meta?: { total: number; page: number; limit: number; totalPages: number };
}

export const auditService = {
  /** جلب سجلات التدقيق — Fetch audit logs.
   *  Maps audit-service's {items, total, skip, limit, has_more} shape to
   *  the admin's {data, meta} shape. audit-service uses skip-based
   *  pagination, so we translate page→skip for the request and
   *  total→totalPages for the response. */
  async getAll(
    params?: PaginationParams & {
      action?: string;
      resource_type?: string;
      user_id?: string;
      status?: string;
      from?: string;
      to?: string;
    }
  ): Promise<PaginatedResponse<AuditLog>> {
    const page = params?.page ?? 1;
    const limit = params?.limit ?? 20;
    try {
      const qp = new URLSearchParams();
      // Translate 1-based page → 0-based skip for audit-service.
      qp.set('skip', String(Math.max(0, (page - 1) * limit)));
      qp.set('limit', String(limit));
      if (params?.search) qp.set('search', params.search);
      if (params?.action) qp.set('action', params.action);
      if (params?.resource_type) qp.set('resource_type', params.resource_type);
      if (params?.user_id) qp.set('user_id', params.user_id);
      if (params?.status) qp.set('status', params.status);
      if (params?.from) qp.set('start_date', params.from);
      if (params?.to) qp.set('end_date', params.to);
      const response = await fetch(
        `${API_URLS.auditEndpoints.logs}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const body = await response.json() as AuditServicePaginated<AuditLog>;
      // Prefer the real audit-service shape (items/total/has_more); fall
      // back to the legacy {data, meta} if a future BFF uses it.
      const data: AuditLog[] = body.items ?? body.data ?? [];
      const total = body.total ?? body.meta?.total ?? data.length;
      const totalPages = limit > 0 ? Math.max(1, Math.ceil(total / limit)) : 1;
      return {
        data,
        meta: { total, page, limit, totalPages },
      };
    } catch (error) {
      logger.error('Failed to load audit logs:', error);
      return { data: [], meta: { total: 0, page, limit, totalPages: 1 } };
    }
  },

  /** إحصائيات التدقيق — Fetch audit stats */
  async getStats(): Promise<AuditStats> {
    try {
      const response = await fetch(API_URLS.auditEndpoints.stats, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as AuditStats;
    } catch (error) {
      logger.error('Failed to load audit stats:', error);
      return { total_logs: 0, actions_today: 0, unique_users: 0, failure_rate: 0, top_actions: [] };
    }
  },
};

// =============================================================================
// Vision Service | خدمة الرؤية الحاسوبية
// =============================================================================

/** نموذج الرؤية — Vision model */
export interface VisionModel {
  id: string;
  name: string;
  variant: string;
  version: string;
  task: string;
  status: 'active' | 'loading' | 'error';
  accuracy: number;
  size_mb: number;
  loaded_at: string;
}

/** نتيجة الاكتشاف — Vision detection result */
export interface VisionDetection {
  id: string;
  image_url: string;
  task: string;
  detections: Array<{ class: string; confidence: number; bbox: number[] }>;
  created_at: string;
  model_variant: string;
  processing_time_ms: number;
}

export const visionService = {
  /** جلب النماذج المحملة — Get loaded models */
  async getModels(): Promise<VisionModel[]> {
    try {
      const response = await fetch(API_URLS.visionEndpoints.models, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      return Array.isArray(result) ? result : (result?.data ?? []);
    } catch (error) {
      logger.error('Failed to load vision models:', error);
      return [];
    }
  },

  /** فحص صحة الخدمة — Get service health */
  async getHealth(): Promise<Record<string, unknown>> {
    try {
      const response = await fetch(
        `${SERVICE_URLS.yoloVision}/healthz`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      logger.error('Failed to get vision health:', error);
      return {};
    }
  },
};

// =============================================================================
// Terrain Service | خدمة تحليل التضاريس
// =============================================================================

/** تحليل التضاريس — Terrain analysis */
export interface TerrainAnalysis {
  id: string;
  field_id: string;
  analysis_type: 'dem' | 'slope' | 'aspect';
  status: 'completed' | 'processing' | 'failed';
  created_at: string;
  result_url?: string;
  metadata: Record<string, unknown>;
}

export const terrainService = {
  /** جلب التحليلات — Fetch analyses */
  async getAnalyses(
    params?: PaginationParams & { field_id?: string; analysis_type?: string; status?: string }
  ): Promise<PaginatedResponse<TerrainAnalysis>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.field_id) qp.set('field_id', params.field_id);
      if (params?.analysis_type) qp.set('analysis_type', params.analysis_type);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(
        `${API_URLS.terrainEndpoints.analyze}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<TerrainAnalysis>;
    } catch (error) {
      logger.error('Failed to load terrain analyses:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },
};

// =============================================================================
// Edge Device Service | خدمة أجهزة الحافة
// =============================================================================

/** جهاز الحافة — Edge device */
export interface EdgeDevice {
  id: string;
  name: string;
  device_type: string;
  status: 'online' | 'offline' | 'error';
  ip_address: string;
  last_seen: string;
  firmware_version: string;
  models_deployed: number;
  cpu_usage: number;
  memory_usage: number;
  gpu_usage?: number;
}

const EDGE_DEVICES_URL = `${SERVICE_URLS.edgeOrchestrator}/api/v1/edge/devices`;

export const edgeService = {
  /** جلب الأجهزة — Fetch devices */
  async getDevices(
    params?: PaginationParams & { status?: string }
  ): Promise<PaginatedResponse<EdgeDevice>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(`${EDGE_DEVICES_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<EdgeDevice>;
    } catch (error) {
      logger.error('Failed to load edge devices:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** جلب جهاز بالمعرف — Get device by ID */
  async getDeviceById(id: string): Promise<EdgeDevice | null> {
    try {
      const response = await fetch(`${EDGE_DEVICES_URL}/${id}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as EdgeDevice;
    } catch (error) {
      logger.error('Failed to load edge device:', error);
      return null;
    }
  },
};

// =============================================================================
// Drone Service | خدمة الطائرات المسيّرة
// =============================================================================

/** طائرة مسيّرة — Drone device */
export interface DroneDevice {
  id: string;
  name: string;
  model: string;
  status: 'available' | 'in_flight' | 'maintenance' | 'offline';
  battery_level: number;
  last_flight: string;
  total_flights: number;
}

/** رحلة طيران — Drone flight */
export interface DroneFlight {
  id: string;
  drone_id: string;
  field_id: string;
  flight_type: string;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  start_time: string;
  end_time?: string;
  area_covered_ha?: number;
}

export const droneService = {
  /** جلب الطائرات — Fetch drone devices */
  async getDevices(
    params?: PaginationParams & { status?: string }
  ): Promise<PaginatedResponse<DroneDevice>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(
        `${API_URLS.droneEndpoints.devices}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<DroneDevice>;
    } catch (error) {
      logger.error('Failed to load drones:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** جلب الرحلات — Fetch flights */
  async getFlights(
    params?: PaginationParams & { status?: string; drone_id?: string }
  ): Promise<PaginatedResponse<DroneFlight>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      if (params?.drone_id) qp.set('drone_id', params.drone_id);
      const response = await fetch(
        `${API_URLS.droneEndpoints.flights}?${qp}`,
        fetchDefaults
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<DroneFlight>;
    } catch (error) {
      logger.error('Failed to load drone flights:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },
};

// =============================================================================
// Virtual Sensor Service | خدمة المستشعرات الافتراضية
// =============================================================================

/** مستشعر افتراضي — Virtual sensor */
export interface VirtualSensor {
  id: string;
  name: string;
  sensor_type: string;
  status: 'active' | 'inactive' | 'error';
  source_sensors: string[];
  algorithm: string;
  last_reading: number;
  unit: string;
  last_updated: string;
  accuracy: number;
}

const VIRTUAL_SENSORS_URL = `${SERVICE_URLS.virtualSensors}/api/v1/sensors/virtual`;

export const virtualSensorService = {
  /** جلب المستشعرات — Fetch virtual sensors */
  async getAll(
    params?: PaginationParams & { sensor_type?: string; status?: string }
  ): Promise<PaginatedResponse<VirtualSensor>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.sensor_type) qp.set('sensor_type', params.sensor_type);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(`${VIRTUAL_SENSORS_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<VirtualSensor>;
    } catch (error) {
      logger.error('Failed to load virtual sensors:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },
};

// =============================================================================
// Scouting Service | خدمة الاستكشاف الميداني
// =============================================================================

/** تقرير استكشاف — Scouting report */
export interface ScoutingReport {
  id: string;
  field_id: string;
  scout_name: string;
  date: string;
  pest_found: boolean;
  pest_type?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  location: { lat: number; lng: number };
  notes: string;
  images: string[];
  status: 'pending' | 'reviewed' | 'resolved';
}

const SCOUTING_URL = `${SERVICE_URLS.pestDetection}/api/v1/scouting/reports`;

export const scoutingService = {
  /** جلب التقارير — Fetch scouting reports */
  async getAll(
    params?: PaginationParams & { field_id?: string; severity?: string; status?: string }
  ): Promise<PaginatedResponse<ScoutingReport>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.field_id) qp.set('field_id', params.field_id);
      if (params?.severity) qp.set('severity', params.severity);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(`${SCOUTING_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<ScoutingReport>;
    } catch (error) {
      logger.error('Failed to load scouting reports:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },
};

// =============================================================================
// Cooperative Service | خدمة التعاونيات
// =============================================================================

/** تعاونية — Cooperative */
export interface Cooperative {
  id: string;
  name: string;
  name_ar: string;
  region: string;
  member_count: number;
  status: 'active' | 'inactive' | 'pending';
  created_at: string;
  total_area_ha: number;
  crops: string[];
}

/** إحصائيات التعاونيات — Cooperative statistics */
export interface CooperativeStats {
  total_cooperatives: number;
  active_cooperatives: number;
  total_members: number;
  total_area_ha: number;
  top_crops: Array<{ crop: string; count: number }>;
}

const COOPERATIVE_URL = `${SERVICE_URLS.cooperative}/api/v1/cooperatives`;

export const cooperativeService = {
  /** جلب التعاونيات — Fetch cooperatives */
  async list(
    params?: PaginationParams & { status?: string; region?: string }
  ): Promise<PaginatedResponse<Cooperative>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      if (params?.region) qp.set('region', params.region);
      const response = await fetch(`${COOPERATIVE_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<Cooperative>;
    } catch (error) {
      logger.error('Failed to load cooperatives:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** جلب تعاونية بالمعرف — Get cooperative by ID */
  async getById(id: string): Promise<Cooperative | null> {
    try {
      const response = await fetch(`${COOPERATIVE_URL}/${id}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as Cooperative;
    } catch (error) {
      logger.error('Failed to load cooperative:', error);
      return null;
    }
  },

  /** إحصائيات التعاونيات — Fetch cooperative stats */
  async getStats(): Promise<CooperativeStats> {
    try {
      const response = await fetch(`${COOPERATIVE_URL}/stats`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as CooperativeStats;
    } catch (error) {
      logger.error('Failed to load cooperative stats:', error);
      return { total_cooperatives: 0, active_cooperatives: 0, total_members: 0, total_area_ha: 0, top_crops: [] };
    }
  },
};

// =============================================================================
// Compliance Service (GlobalGAP) | خدمة الامتثال
// =============================================================================

/** سجل امتثال — Compliance record */
export interface ComplianceRecord {
  id: string;
  farm_id: string;
  standard: string;
  version: string;
  status: 'compliant' | 'non_compliant' | 'pending_review' | 'in_progress';
  score: number;
  audit_date: string;
  next_audit_date: string;
  findings: number;
}

/** إحصائيات الامتثال — Compliance statistics */
export interface ComplianceStats {
  total_records: number;
  compliant_count: number;
  non_compliant_count: number;
  average_score: number;
  upcoming_audits: number;
}

const COMPLIANCE_URL = `${SERVICE_URLS.globalgap}/api/v1/compliance`;

export const complianceService = {
  /** جلب سجلات الامتثال — Fetch compliance records */
  async list(
    params?: PaginationParams & { status?: string; standard?: string }
  ): Promise<PaginatedResponse<ComplianceRecord>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      if (params?.standard) qp.set('standard', params.standard);
      const response = await fetch(`${COMPLIANCE_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<ComplianceRecord>;
    } catch (error) {
      logger.error('Failed to load compliance records:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** إحصائيات الامتثال — Fetch compliance stats */
  async getStats(): Promise<ComplianceStats> {
    try {
      const response = await fetch(`${COMPLIANCE_URL}/stats`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as ComplianceStats;
    } catch (error) {
      logger.error('Failed to load compliance stats:', error);
      return { total_records: 0, compliant_count: 0, non_compliant_count: 0, average_score: 0, upcoming_audits: 0 };
    }
  },
};

// =============================================================================
// Disaster Assessment Service | خدمة تقييم الكوارث
// =============================================================================

/** تقييم كارثة — Disaster assessment */
export interface DisasterAssessment {
  id: string;
  field_id: string;
  disaster_type: 'flood' | 'drought' | 'frost' | 'hail' | 'pest_outbreak' | 'disease_outbreak' | 'fire';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'reported' | 'assessed' | 'mitigated' | 'resolved';
  reported_at: string;
  assessed_at?: string;
  affected_area_ha: number;
  estimated_loss: number;
  description: string;
}

const DISASTER_URL = `${SERVICE_URLS.disasterAssessment}/api/v1/disasters`;

export const disasterService = {
  /** جلب تقييمات الكوارث — Fetch disaster assessments */
  async list(
    params?: PaginationParams & { disaster_type?: string; severity?: string; status?: string }
  ): Promise<PaginatedResponse<DisasterAssessment>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.disaster_type) qp.set('disaster_type', params.disaster_type);
      if (params?.severity) qp.set('severity', params.severity);
      if (params?.status) qp.set('status', params.status);
      const response = await fetch(`${DISASTER_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<DisasterAssessment>;
    } catch (error) {
      logger.error('Failed to load disaster assessments:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** جلب تقييم بالمعرف — Get assessment by ID */
  async getById(id: string): Promise<DisasterAssessment | null> {
    try {
      const response = await fetch(`${DISASTER_URL}/${id}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as DisasterAssessment;
    } catch (error) {
      logger.error('Failed to load disaster assessment:', error);
      return null;
    }
  },
};

// =============================================================================
// Insurance Service | خدمة التأمين الزراعي
// =============================================================================

/** وثيقة تأمين — Insurance policy */
export interface InsurancePolicy {
  id: string;
  farm_id: string;
  policy_number: string;
  crop_type: string;
  coverage_type: string;
  premium: number;
  coverage_amount: number;
  start_date: string;
  end_date: string;
  status: 'active' | 'expired' | 'cancelled' | 'pending';
}

/** مطالبة تأمين — Insurance claim */
export interface InsuranceClaim {
  id: string;
  policy_id: string;
  claim_number: string;
  disaster_type: string;
  claim_amount: number;
  approved_amount?: number;
  status: 'submitted' | 'under_review' | 'approved' | 'rejected' | 'paid';
  submitted_at: string;
  resolved_at?: string;
}

/** إحصائيات التأمين — Insurance statistics */
export interface InsuranceStats {
  total_policies: number;
  active_policies: number;
  total_claims: number;
  pending_claims: number;
  total_premium: number;
  total_paid_claims: number;
}

const INSURANCE_URL = `${SERVICE_URLS.advisory}/api/v1/insurance`;

export const insuranceService = {
  /** جلب وثائق التأمين — Fetch insurance policies */
  async listPolicies(
    params?: PaginationParams & { status?: string; crop_type?: string }
  ): Promise<PaginatedResponse<InsurancePolicy>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      if (params?.crop_type) qp.set('crop_type', params.crop_type);
      const response = await fetch(`${INSURANCE_URL}/policies?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<InsurancePolicy>;
    } catch (error) {
      logger.error('Failed to load insurance policies:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** جلب مطالبات التأمين — Fetch insurance claims */
  async listClaims(
    params?: PaginationParams & { status?: string; policy_id?: string }
  ): Promise<PaginatedResponse<InsuranceClaim>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.status) qp.set('status', params.status);
      if (params?.policy_id) qp.set('policy_id', params.policy_id);
      const response = await fetch(`${INSURANCE_URL}/claims?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<InsuranceClaim>;
    } catch (error) {
      logger.error('Failed to load insurance claims:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** إحصائيات التأمين — Fetch insurance stats */
  async getStats(): Promise<InsuranceStats> {
    try {
      const response = await fetch(`${INSURANCE_URL}/stats`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as InsuranceStats;
    } catch (error) {
      logger.error('Failed to load insurance stats:', error);
      return { total_policies: 0, active_policies: 0, total_claims: 0, pending_claims: 0, total_premium: 0, total_paid_claims: 0 };
    }
  },
};

// =============================================================================
// Market Price Service | خدمة أسعار السوق
// =============================================================================

/** سعر سوقي — Market price entry */
export interface MarketPrice {
  id: string;
  crop_type: string;
  market: string;
  price: number;
  currency: string;
  unit: string;
  date: string;
  change_pct: number;
  source: string;
}

/** إحصائيات الأسعار — Market price statistics */
export interface MarketPriceStats {
  total_entries: number;
  markets_tracked: number;
  crops_tracked: number;
  last_updated: string;
  top_gainers: Array<{ crop: string; change_pct: number }>;
  top_losers: Array<{ crop: string; change_pct: number }>;
}

const MARKET_PRICE_URL = `${SERVICE_URLS.advisory}/api/v1/market-prices`;

export const marketPriceService = {
  /** جلب أسعار السوق — Fetch market prices */
  async list(
    params?: PaginationParams & { crop_type?: string; market?: string }
  ): Promise<PaginatedResponse<MarketPrice>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.crop_type) qp.set('crop_type', params.crop_type);
      if (params?.market) qp.set('market', params.market);
      const response = await fetch(`${MARKET_PRICE_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<MarketPrice>;
    } catch (error) {
      logger.error('Failed to load market prices:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** إحصائيات الأسعار — Fetch market price stats */
  async getStats(): Promise<MarketPriceStats> {
    try {
      const response = await fetch(`${MARKET_PRICE_URL}/stats`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as MarketPriceStats;
    } catch (error) {
      logger.error('Failed to load market price stats:', error);
      return { total_entries: 0, markets_tracked: 0, crops_tracked: 0, last_updated: '', top_gainers: [], top_losers: [] };
    }
  },
};

// =============================================================================
// Season Service (Astronomical Calendar) | خدمة المواسم والتقويم الفلكي
// =============================================================================

/** موسم زراعي — Agricultural season */
export interface Season {
  id: string;
  name: string;
  name_ar: string;
  type: 'planting' | 'growing' | 'harvest' | 'fallow';
  start_date: string;
  end_date: string;
  region: string;
  crops: string[];
  is_current: boolean;
}

/** إحصائيات المواسم — Season statistics */
export interface SeasonStats {
  total_seasons: number;
  current_season: string;
  current_season_ar: string;
  upcoming_events: Array<{ event: string; event_ar: string; date: string }>;
  active_crops: number;
}

const SEASON_URL = `${SERVICE_URLS.astronomicalCalendar}/api/v1/seasons`;

export const seasonService = {
  /** جلب المواسم — Fetch seasons */
  async list(
    params?: PaginationParams & { type?: string; region?: string }
  ): Promise<PaginatedResponse<Season>> {
    try {
      const qp = new URLSearchParams();
      if (params?.page) qp.set('page', params.page.toString());
      if (params?.limit) qp.set('limit', params.limit.toString());
      if (params?.search) qp.set('search', params.search);
      if (params?.type) qp.set('type', params.type);
      if (params?.region) qp.set('region', params.region);
      const response = await fetch(`${SEASON_URL}?${qp}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<Season>;
    } catch (error) {
      logger.error('Failed to load seasons:', error);
      return { data: [], meta: { total: 0, page: 1, limit: 20, totalPages: 1 } };
    }
  },

  /** جلب الموسم الحالي — Get current season */
  async getCurrent(): Promise<Season | null> {
    try {
      const response = await fetch(`${SEASON_URL}/current`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as Season;
    } catch (error) {
      logger.error('Failed to load current season:', error);
      return null;
    }
  },

  /** إحصائيات المواسم — Fetch season stats */
  async getStats(): Promise<SeasonStats> {
    try {
      const response = await fetch(`${SEASON_URL}/stats`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as SeasonStats;
    } catch (error) {
      logger.error('Failed to load season stats:', error);
      return { total_seasons: 0, current_season: '', current_season_ar: '', upcoming_events: [], active_crops: 0 };
    }
  },
};

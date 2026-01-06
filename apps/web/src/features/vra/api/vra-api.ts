/**
 * VRA (Variable Rate Application) API Client
 * عميل واجهة برمجة التطبيقات للتطبيق المتغير المعدل
 *
 * API client for VRA prescription maps and variable rate application features.
 */

import { apiClient } from '@/lib/api';
import type { ApiResponse } from '@/lib/api/types';
import { logger } from '@/lib/logger';
import type {
  PrescriptionRequest,
  PrescriptionResponse,
  PrescriptionHistoryResponse,
  ExportFormat,
} from '../types/vra';

// ═══════════════════════════════════════════════════════════════════════════
// Error Messages
// ═══════════════════════════════════════════════════════════════════════════

export const VRA_ERROR_MESSAGES = {
  GENERATE_FAILED: {
    en: 'Failed to generate VRA prescription',
    ar: 'فشل في توليد وصفة التطبيق المتغير',
  },
  HISTORY_FETCH_FAILED: {
    en: 'Failed to fetch prescription history',
    ar: 'فشل في جلب سجل الوصفات',
  },
  EXPORT_FAILED: {
    en: 'Failed to export prescription',
    ar: 'فشل في تصدير الوصفة',
  },
  DETAILS_FETCH_FAILED: {
    en: 'Failed to fetch prescription details',
    ar: 'فشل في جلب تفاصيل الوصفة',
  },
  DELETE_FAILED: {
    en: 'Failed to delete prescription',
    ar: 'فشل في حذف الوصفة',
  },
  INVALID_FIELD_ID: {
    en: 'Invalid field ID provided',
    ar: 'معرف الحقل غير صالح',
  },
  INVALID_PRESCRIPTION_ID: {
    en: 'Invalid prescription ID provided',
    ar: 'معرف الوصفة غير صالح',
  },
  INVALID_VRA_TYPE: {
    en: 'Invalid VRA type provided',
    ar: 'نوع التطبيق المتغير غير صالح',
  },
  INVALID_EXPORT_FORMAT: {
    en: 'Invalid export format',
    ar: 'تنسيق التصدير غير صالح',
  },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Generate VRA Prescription Map
 * توليد خريطة وصفة التطبيق المتغير
 *
 * Creates a variable rate application prescription map based on NDVI zones,
 * yield data, soil analysis, or combined factors.
 *
 * @param request - Prescription generation request
 * @returns Generated prescription with zones and recommendations
 */
export async function generatePrescription(
  request: PrescriptionRequest
): Promise<ApiResponse<PrescriptionResponse>> {
  // Validate required fields
  if (!request.fieldId || typeof request.fieldId !== 'string' || request.fieldId.trim().length === 0) {
    return {
      success: false,
      error: VRA_ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: VRA_ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  if (!request.vraType) {
    return {
      success: false,
      error: VRA_ERROR_MESSAGES.INVALID_VRA_TYPE.en,
      error_ar: VRA_ERROR_MESSAGES.INVALID_VRA_TYPE.ar,
    };
  }

  try {
    // Build request payload matching backend API
    const payload = {
      field_id: request.fieldId,
      latitude: request.latitude,
      longitude: request.longitude,
      vra_type: request.vraType,
      target_rate: request.targetRate,
      unit: request.unit,
      num_zones: request.numZones || 3,
      zone_method: request.zoneMethod || 'ndvi',
      min_rate: request.minRate,
      max_rate: request.maxRate,
      product_price_per_unit: request.productPricePerUnit,
      notes: request.notes,
      notes_ar: request.notesAr,
    };

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/vra/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      logger.error('[generatePrescription] API returned error:', errorData);
      return {
        success: false,
        error: errorData.detail || VRA_ERROR_MESSAGES.GENERATE_FAILED.en,
        error_ar: VRA_ERROR_MESSAGES.GENERATE_FAILED.ar,
      };
    }

    const data = await response.json();

    // Transform response to match frontend types
    const prescription: PrescriptionResponse = {
      id: data.id,
      fieldId: data.field_id,
      vraType: data.vra_type,
      createdAt: data.created_at,
      targetRate: data.target_rate,
      minRate: data.min_rate,
      maxRate: data.max_rate,
      unit: data.unit,
      numZones: data.num_zones,
      zoneMethod: data.zone_method,
      zones: data.zones.map((zone: any) => ({
        zoneId: zone.zone_id,
        zoneName: zone.zone_name,
        zoneNameAr: zone.zone_name_ar,
        zoneLevel: zone.zone_level,
        ndviMin: zone.ndvi_min,
        ndviMax: zone.ndvi_max,
        areaHa: zone.area_ha,
        percentage: zone.percentage,
        centroid: zone.centroid,
        recommendedRate: zone.recommended_rate,
        unit: zone.unit,
        totalProduct: zone.total_product,
        color: zone.color,
      })),
      totalAreaHa: data.total_area_ha,
      totalProductNeeded: data.total_product_needed,
      flatRateProduct: data.flat_rate_product,
      savingsPercent: data.savings_percent,
      savingsAmount: data.savings_amount,
      costSavings: data.cost_savings,
      notes: data.notes,
      notesAr: data.notes_ar,
      geojsonUrl: data.geojson_url,
      shapefileUrl: data.shapefile_url,
      isoxmlUrl: data.isoxml_url,
    };

    return {
      success: true,
      data: prescription,
    };
  } catch (error) {
    logger.error('[generatePrescription] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : VRA_ERROR_MESSAGES.GENERATE_FAILED.en,
      error_ar: VRA_ERROR_MESSAGES.GENERATE_FAILED.ar,
    };
  }
}

/**
 * Get Prescription History for Field
 * الحصول على سجل الوصفات للحقل
 *
 * Retrieves all VRA prescriptions for a specific field, sorted by creation date.
 *
 * @param fieldId - Field ID
 * @param limit - Maximum number of prescriptions to return (default: 10)
 * @returns Prescription history with summaries
 */
export async function getPrescriptionHistory(
  fieldId: string,
  limit: number = 10
): Promise<ApiResponse<PrescriptionHistoryResponse>> {
  if (!fieldId || typeof fieldId !== 'string' || fieldId.trim().length === 0) {
    return {
      success: false,
      error: VRA_ERROR_MESSAGES.INVALID_FIELD_ID.en,
      error_ar: VRA_ERROR_MESSAGES.INVALID_FIELD_ID.ar,
    };
  }

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/vra/prescriptions/${fieldId}?limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      logger.error('[getPrescriptionHistory] API returned error:', errorData);
      return {
        success: false,
        error: errorData.detail || VRA_ERROR_MESSAGES.HISTORY_FETCH_FAILED.en,
        error_ar: VRA_ERROR_MESSAGES.HISTORY_FETCH_FAILED.ar,
      };
    }

    const data = await response.json();

    // Transform response
    const history: PrescriptionHistoryResponse = {
      fieldId: data.field_id,
      count: data.count,
      prescriptions: data.prescriptions.map((p: any) => ({
        id: p.id,
        fieldId: p.field_id,
        vraType: p.vra_type,
        createdAt: p.created_at,
        targetRate: p.target_rate,
        unit: p.unit,
        numZones: p.num_zones,
        totalAreaHa: p.total_area_ha,
        savingsPercent: p.savings_percent,
        savingsAmount: p.savings_amount,
        costSavings: p.cost_savings,
      })),
    };

    return {
      success: true,
      data: history,
    };
  } catch (error) {
    logger.error('[getPrescriptionHistory] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : VRA_ERROR_MESSAGES.HISTORY_FETCH_FAILED.en,
      error_ar: VRA_ERROR_MESSAGES.HISTORY_FETCH_FAILED.ar,
    };
  }
}

/**
 * Get Prescription Details by ID
 * الحصول على تفاصيل الوصفة بالمعرف
 *
 * Retrieves detailed information about a specific prescription, including all zones.
 *
 * @param prescriptionId - Prescription ID
 * @returns Full prescription details
 */
export async function getPrescriptionDetails(
  prescriptionId: string
): Promise<ApiResponse<PrescriptionResponse>> {
  if (!prescriptionId || typeof prescriptionId !== 'string' || prescriptionId.trim().length === 0) {
    return {
      success: false,
      error: VRA_ERROR_MESSAGES.INVALID_PRESCRIPTION_ID.en,
      error_ar: VRA_ERROR_MESSAGES.INVALID_PRESCRIPTION_ID.ar,
    };
  }

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/vra/prescription/${prescriptionId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      logger.error('[getPrescriptionDetails] API returned error:', errorData);
      return {
        success: false,
        error: errorData.detail || VRA_ERROR_MESSAGES.DETAILS_FETCH_FAILED.en,
        error_ar: VRA_ERROR_MESSAGES.DETAILS_FETCH_FAILED.ar,
      };
    }

    const data = await response.json();

    // Transform response (same as generatePrescription)
    const prescription: PrescriptionResponse = {
      id: data.id,
      fieldId: data.field_id,
      vraType: data.vra_type,
      createdAt: data.created_at,
      targetRate: data.target_rate,
      minRate: data.min_rate,
      maxRate: data.max_rate,
      unit: data.unit,
      numZones: data.num_zones,
      zoneMethod: data.zone_method,
      zones: data.zones.map((zone: any) => ({
        zoneId: zone.zone_id,
        zoneName: zone.zone_name,
        zoneNameAr: zone.zone_name_ar,
        zoneLevel: zone.zone_level,
        ndviMin: zone.ndvi_min,
        ndviMax: zone.ndvi_max,
        areaHa: zone.area_ha,
        percentage: zone.percentage,
        centroid: zone.centroid,
        recommendedRate: zone.recommended_rate,
        unit: zone.unit,
        totalProduct: zone.total_product,
        color: zone.color,
      })),
      totalAreaHa: data.total_area_ha,
      totalProductNeeded: data.total_product_needed,
      flatRateProduct: data.flat_rate_product,
      savingsPercent: data.savings_percent,
      savingsAmount: data.savings_amount,
      costSavings: data.cost_savings,
      notes: data.notes,
      notesAr: data.notes_ar,
      geojsonUrl: data.geojson_url,
      shapefileUrl: data.shapefile_url,
      isoxmlUrl: data.isoxml_url,
    };

    return {
      success: true,
      data: prescription,
    };
  } catch (error) {
    logger.error('[getPrescriptionDetails] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : VRA_ERROR_MESSAGES.DETAILS_FETCH_FAILED.en,
      error_ar: VRA_ERROR_MESSAGES.DETAILS_FETCH_FAILED.ar,
    };
  }
}

/**
 * Export Prescription
 * تصدير الوصفة
 *
 * Exports prescription in various formats for equipment compatibility:
 * - GeoJSON: For web display and GIS applications
 * - CSV: For spreadsheet analysis
 * - Shapefile: For farm equipment and GIS software
 * - ISO-XML: For ISOBUS-compatible equipment
 *
 * @param prescriptionId - Prescription ID
 * @param format - Export format
 * @returns Export data in requested format
 */
export async function exportPrescription(
  prescriptionId: string,
  format: ExportFormat
): Promise<ApiResponse<any>> {
  if (!prescriptionId || typeof prescriptionId !== 'string' || prescriptionId.trim().length === 0) {
    return {
      success: false,
      error: VRA_ERROR_MESSAGES.INVALID_PRESCRIPTION_ID.en,
      error_ar: VRA_ERROR_MESSAGES.INVALID_PRESCRIPTION_ID.ar,
    };
  }

  const validFormats: ExportFormat[] = ['geojson', 'csv', 'shapefile', 'isoxml'];
  if (!validFormats.includes(format)) {
    return {
      success: false,
      error: VRA_ERROR_MESSAGES.INVALID_EXPORT_FORMAT.en,
      error_ar: VRA_ERROR_MESSAGES.INVALID_EXPORT_FORMAT.ar,
    };
  }

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/vra/export/${prescriptionId}?format=${format}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      logger.error('[exportPrescription] API returned error:', errorData);
      return {
        success: false,
        error: errorData.detail || VRA_ERROR_MESSAGES.EXPORT_FAILED.en,
        error_ar: VRA_ERROR_MESSAGES.EXPORT_FAILED.ar,
      };
    }

    const data = await response.json();

    return {
      success: true,
      data,
    };
  } catch (error) {
    logger.error('[exportPrescription] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : VRA_ERROR_MESSAGES.EXPORT_FAILED.en,
      error_ar: VRA_ERROR_MESSAGES.EXPORT_FAILED.ar,
    };
  }
}

/**
 * Delete Prescription
 * حذف الوصفة
 *
 * Deletes a prescription from the system.
 *
 * @param prescriptionId - Prescription ID
 * @returns Success status
 */
export async function deletePrescription(
  prescriptionId: string
): Promise<ApiResponse<{ success: boolean; message: string; messageAr: string }>> {
  if (!prescriptionId || typeof prescriptionId !== 'string' || prescriptionId.trim().length === 0) {
    return {
      success: false,
      error: VRA_ERROR_MESSAGES.INVALID_PRESCRIPTION_ID.en,
      error_ar: VRA_ERROR_MESSAGES.INVALID_PRESCRIPTION_ID.ar,
    };
  }

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/vra/prescription/${prescriptionId}`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      logger.error('[deletePrescription] API returned error:', errorData);
      return {
        success: false,
        error: errorData.detail || VRA_ERROR_MESSAGES.DELETE_FAILED.en,
        error_ar: VRA_ERROR_MESSAGES.DELETE_FAILED.ar,
      };
    }

    const data = await response.json();

    return {
      success: true,
      data: {
        success: data.success,
        message: data.message,
        messageAr: data.message_ar,
      },
    };
  } catch (error) {
    logger.error('[deletePrescription] Request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : VRA_ERROR_MESSAGES.DELETE_FAILED.en,
      error_ar: VRA_ERROR_MESSAGES.DELETE_FAILED.ar,
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// TanStack Query Key Factory
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Query keys for VRA features
 * Use these keys with TanStack Query for caching and invalidation
 */
export const vraKeys = {
  all: ['vra'] as const,
  prescriptions: () => [...vraKeys.all, 'prescriptions'] as const,
  prescription: (id: string) => [...vraKeys.prescriptions(), id] as const,
  history: (fieldId: string) => [...vraKeys.all, 'history', fieldId] as const,
  export: (prescriptionId: string, format: ExportFormat) =>
    [...vraKeys.all, 'export', prescriptionId, format] as const,
} as const;

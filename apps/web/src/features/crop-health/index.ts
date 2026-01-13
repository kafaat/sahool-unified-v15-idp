/**
 * Crop Health Feature
 * ميزة صحة المحصول والتشخيص
 *
 * This feature handles:
 * - Crop health monitoring
 * - AI-powered disease diagnosis
 * - Treatment recommendations
 * - Expert consultations
 * - Disease alerts
 */

// Component exports
export { HealthDashboard } from "./components/HealthDashboard";
export { DiagnosisTool } from "./components/DiagnosisTool";
export { DiagnosisResult as DiagnosisResultView } from "./components/DiagnosisResult";

// Hook exports
export {
  useHealthSummary,
  useHealthRecords,
  useHealthRecord,
  useCreateHealthRecord,
  useUpdateHealthRecord,
  useDiagnosisRequests,
  useDiagnosisRequest,
  useCreateDiagnosis,
  useUploadDiagnosisImages,
  useDiagnosisResult,
  useDiseases,
  useDiseaseAlerts,
  useDismissAlert,
  useRequestConsultation,
  useConsultations,
} from "./hooks/useCropHealth";

// Type exports
export type {
  DiseaseSeverity,
  DiagnosisStatus,
  TreatmentType,
  DiseaseCategory,
  Disease,
  Treatment,
  TreatmentMaterial,
  DiagnosisRequest,
  DiagnosisResult,
  DiagnosedDisease,
  HealthRecord,
  HealthSummary,
  HealthFilters,
  DiseaseAlert,
  ExpertConsultation,
} from "./types";

export const CROP_HEALTH_FEATURE = "crop-health" as const;

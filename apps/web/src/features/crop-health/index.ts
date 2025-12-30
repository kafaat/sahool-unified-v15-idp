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
export { HealthDashboard } from './components/HealthDashboard';
export { DiagnosisTool } from './components/DiagnosisTool';
export { DiagnosisResult as DiagnosisResultView } from './components/DiagnosisResult';
export { DiseaseRiskForecast } from './components/DiseaseRiskForecast';

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
} from './hooks/useCropHealth';

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
} from './types';

// Disease Risk Forecast Types
export type {
  WeatherFactors,
  CropStage,
  RiskLevel,
  DiseaseRisk,
  RiskForecast,
  DiseaseRiskForecastProps,
} from './components/DiseaseRiskForecast';

export const CROP_HEALTH_FEATURE = 'crop-health' as const;

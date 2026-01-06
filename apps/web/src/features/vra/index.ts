/**
 * SAHOOL VRA (Variable Rate Application) Feature
 * ميزة التطبيق المتغير المعدل
 *
 * Complete VRA prescription map generation and management system.
 * نظام كامل لتوليد وإدارة خرائط التطبيق المتغير المعدل.
 *
 * @module features/vra
 */

// ═══════════════════════════════════════════════════════════════════════════
// Components
// ═══════════════════════════════════════════════════════════════════════════

export { VRAPanel } from './components/VRAPanel';
export { PrescriptionMap } from './components/PrescriptionMap';
export { PrescriptionTable } from './components/PrescriptionTable';
export { VRAHistory } from './components/VRAHistory';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks
// ═══════════════════════════════════════════════════════════════════════════

export {
  useVRA,
  usePrescriptionHistory,
  usePrescriptionDetails,
  useGeneratePrescription,
  useExportPrescription,
  useDeletePrescription,
  vraKeys,
} from './hooks/useVRA';

// ═══════════════════════════════════════════════════════════════════════════
// API
// ═══════════════════════════════════════════════════════════════════════════

export {
  generatePrescription,
  getPrescriptionHistory,
  getPrescriptionDetails,
  exportPrescription,
  deletePrescription,
  VRA_ERROR_MESSAGES,
} from './api/vra-api';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  VRAType,
  VRAMethod,
  ZoneLevel,
  ExportFormat,
  PrescriptionRequest,
  PrescriptionResponse,
  PrescriptionSummary,
  PrescriptionHistoryResponse,
  PrescriptionExport,
  ZoneResult,
  VRAPanelState,
  VRAFormErrors,
  VRATypeConfig,
  ZoneMethodConfig,
} from './types/vra';

export {
  VRA_TYPES,
  ZONE_METHODS,
  ZONE_LEVEL_NAMES,
  ZONE_COLORS,
  ZONE_COUNT_OPTIONS,
  EXPORT_FORMAT_LABELS,
} from './types/vra';

// ═══════════════════════════════════════════════════════════════════════════
// Usage Examples
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Example 1: Basic VRA Panel Usage
 * مثال 1: الاستخدام الأساسي للوحة VRA
 *
 * ```tsx
 * import { VRAPanel } from '@/features/vra';
 *
 * function MyFieldPage({ field }) {
 *   return (
 *     <VRAPanel
 *       fieldId={field.id}
 *       fieldName={field.name}
 *       fieldNameAr={field.nameAr}
 *       latitude={field.latitude}
 *       longitude={field.longitude}
 *       onPrescriptionGenerated={(prescription) => {
 *         console.log('Generated:', prescription);
 *       }}
 *     />
 *   );
 * }
 * ```
 *
 * Example 2: Using VRA Hooks Directly
 * مثال 2: استخدام خطافات VRA مباشرة
 *
 * ```tsx
 * import { useVRA } from '@/features/vra';
 *
 * function MyComponent({ fieldId }) {
 *   const vra = useVRA(fieldId);
 *
 *   const handleGenerate = async () => {
 *     await vra.generate.mutateAsync({
 *       fieldId,
 *       latitude: 15.5,
 *       longitude: 44.2,
 *       vraType: 'fertilizer',
 *       targetRate: 100,
 *       unit: 'kg/ha',
 *       numZones: 3,
 *     });
 *   };
 *
 *   return (
 *     <div>
 *       <button onClick={handleGenerate} disabled={vra.generate.isPending}>
 *         Generate Prescription
 *       </button>
 *
 *       {vra.history.data && (
 *         <div>
 *           {vra.history.data.prescriptions.map(p => (
 *             <div key={p.id}>{p.vraType} - {p.savingsPercent}%</div>
 *           ))}
 *         </div>
 *       )}
 *     </div>
 *   );
 * }
 * ```
 *
 * Example 3: Prescription Map Only
 * مثال 3: خريطة الوصفة فقط
 *
 * ```tsx
 * import { PrescriptionMap, usePrescriptionDetails } from '@/features/vra';
 *
 * function PrescriptionViewer({ prescriptionId }) {
 *   const { data: prescription, isLoading } = usePrescriptionDetails(prescriptionId);
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (!prescription) return null;
 *
 *   return <PrescriptionMap prescription={prescription} height="600px" />;
 * }
 * ```
 *
 * Example 4: History View with Actions
 * مثال 4: عرض السجل مع الإجراءات
 *
 * ```tsx
 * import { VRAHistory } from '@/features/vra';
 *
 * function FieldHistoryPage({ field }) {
 *   return (
 *     <VRAHistory
 *       fieldId={field.id}
 *       fieldName={field.name}
 *       fieldNameAr={field.nameAr}
 *       limit={20}
 *     />
 *   );
 * }
 * ```
 */

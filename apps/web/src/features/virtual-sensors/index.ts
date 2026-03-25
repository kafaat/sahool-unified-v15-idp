export { virtualSensorsApi, ERROR_MESSAGES } from './api';
export type {
  ET0Result,
  ETCResult,
  CropInfo,
  SoilInfo,
  SoilMoistureEstimate,
  IrrigationRecommendation,
  IrrigationQuickCheck,
} from './types';

// Hooks - خطافات
export { virtualSensorKeys } from './hooks/useVirtualSensors';
export {
  useVSCrops,
  useCropKc,
  useVSSoils,
  useIrrigationMethods,
  useCalculateET0,
  useCalculateETC,
  useEstimateSoilMoisture,
  useIrrigationRecommendation,
  useQuickIrrigationCheck,
} from './hooks/useVirtualSensors';

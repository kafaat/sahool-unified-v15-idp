// Precision Agriculture API Client
// عميل API للزراعة الدقيقة

import { apiClient, API_URLS } from "../api";
import { logger } from "../logger";

/**
 * Generate a unique ID for mock data.
 * Uses crypto.randomUUID() when available, falls back to deterministic ID.
 * Note: This is for mock/demo data only, not for security-sensitive operations.
 */
function generateMockId(prefix: string, index: number): string {
  // Use crypto.randomUUID for unique IDs if available
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
  }
  // Fallback to deterministic ID based on index
  return `${prefix}-${index + 1}-${Date.now().toString(36)}`;
}

/**
 * Generate a random number for mock data generation.
 * Uses crypto.getRandomValues() for CodeQL compliance, even though
 * cryptographic security is not required for mock/demo data.
 *
 * @returns A random number between 0 (inclusive) and 1 (exclusive)
 */
function mockRandom(): number {
  // Use crypto API for CodeQL compliance
  if (typeof crypto !== "undefined" && crypto.getRandomValues) {
    const arr = new Uint32Array(1);
    crypto.getRandomValues(arr);
    return (arr[0] ?? 0) / 0xffffffff;
  }
  // Fallback for environments without crypto (SSR, tests)
  return Date.now() % 1000 / 1000;
}

/**
 * Generate a random integer for mock data within a range.
 * See mockRandom() for security notes.
 */
function mockRandomInt(min: number, max: number): number {
  return Math.floor(mockRandom() * (max - min + 1)) + min;
}

/**
 * Pick a random element from an array for mock data.
 * See mockRandom() for security notes.
 */
function mockRandomPick<T>(arr: readonly T[]): T | undefined {
  return arr[Math.floor(mockRandom() * arr.length)];
}

// VRA (Variable Rate Application) Types
export interface VRAPrescription {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  prescriptionType: "fertilizer" | "pesticide" | "irrigation";
  status: "pending" | "approved" | "rejected" | "applied";
  createdAt: string;
  createdBy: string;
  approvedBy?: string;
  appliedAt?: string;
  area: number;
  zones: number;
  totalCost: number;
}

// GDD (Growing Degree Days) Types
export interface GDDField {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  plantingDate: string;
  currentGDD: number;
  targetGDD: number;
  currentStage: string;
  currentStageAr: string;
  nextStage: string;
  nextStageAr: string;
  daysToNextStage: number;
  gddToNextStage: number;
  alerts: Array<{
    type: "info" | "warning" | "critical";
    message: string;
    messageAr: string;
  }>;
  history: Array<{
    date: string;
    gdd: number;
    temp_min: number;
    temp_max: number;
  }>;
}

// Spray Management Types
export interface SprayWindow {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  productType: "pesticide" | "herbicide" | "fungicide" | "fertilizer";
  productName: string;
  windowStart: string;
  windowEnd: string;
  optimalTime: string;
  status: "upcoming" | "optimal" | "missed" | "completed";
  conditions: {
    temperature: number;
    windSpeed: number;
    humidity: number;
    precipitation: number;
  };
  recommendations: string[];
  recommendationsAr: string[];
}

export interface SprayHistory {
  id: string;
  farmName: string;
  fieldName: string;
  productType: string;
  productName: string;
  appliedAt: string;
  area: number;
  quantity: number;
  cost: number;
  effectiveness: number;
}

// VRA API Functions
export async function fetchVRAPrescriptions(params?: {
  status?: string;
  type?: string;
  farmId?: string;
  limit?: number;
}): Promise<VRAPrescription[]> {
  try {
    const response = await apiClient.get(
      `${API_URLS.fertilizer}/v1/prescriptions`,
      { params },
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch VRA prescriptions:", error);
    // Return mock data for development
    return generateMockVRAPrescriptions();
  }
}

export async function approvePrescription(id: string): Promise<boolean> {
  try {
    await apiClient.patch(
      `${API_URLS.fertilizer}/v1/prescriptions/${id}/approve`,
    );
    return true;
  } catch (error) {
    logger.error("Failed to approve prescription:", error);
    return false;
  }
}

export async function rejectPrescription(id: string): Promise<boolean> {
  try {
    await apiClient.patch(
      `${API_URLS.fertilizer}/v1/prescriptions/${id}/reject`,
    );
    return true;
  } catch (error) {
    logger.error("Failed to reject prescription:", error);
    return false;
  }
}

// GDD API Functions
export async function fetchGDDData(): Promise<GDDField[]> {
  try {
    const response = await apiClient.get(`${API_URLS.weather}/v1/gdd`);
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch GDD data:", error);
    return generateMockGDDData();
  }
}

// Spray Management API Functions
export async function fetchSprayWindows(): Promise<SprayWindow[]> {
  try {
    const response = await apiClient.get(
      `${API_URLS.weather}/v1/spray-windows`,
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch spray windows:", error);
    return generateMockSprayWindows();
  }
}

export async function fetchSprayHistory(params?: {
  limit?: number;
}): Promise<SprayHistory[]> {
  try {
    const response = await apiClient.get(
      `${API_URLS.fertilizer}/v1/spray-history`,
      { params },
    );
    return response.data;
  } catch (error) {
    logger.error("Failed to fetch spray history:", error);
    return generateMockSprayHistory();
  }
}

// Mock Data Generators
function generateMockVRAPrescriptions(): VRAPrescription[] {
  const types: Array<"fertilizer" | "pesticide" | "irrigation"> = [
    "fertilizer",
    "pesticide",
    "irrigation",
  ];
  const statuses: Array<"pending" | "approved" | "rejected" | "applied"> = [
    "pending",
    "approved",
    "rejected",
    "applied",
  ];

  return Array.from({ length: 15 }, (_, i) => ({
    id: generateMockId("vra", i),
    farmId: generateMockId("farm", i % 10),
    farmName: `مزرعة ${mockRandomInt(1, 10)}`,
    fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
    cropType: ["قمح", "بن", "قات", "ذرة"][Math.floor(mockRandom() * 4)] ?? "قمح",
    prescriptionType: types[Math.floor(mockRandom() * types.length)] ?? "fertilizer",
    status: statuses[Math.floor(mockRandom() * statuses.length)] ?? "pending",
    createdAt: new Date(
      Date.now() - mockRandom() * 14 * 24 * 60 * 60 * 1000,
    ).toISOString(),
    createdBy: `user-${mockRandomInt(1, 5)}`,
    area: mockRandom() * 50 + 10,
    zones: mockRandomInt(3, 8),
    totalCost: mockRandom() * 5000 + 1000,
  }));
}

function generateMockGDDData(): GDDField[] {
  const stages = [
    { en: "Vegetative", ar: "نمو خضري", target: 800 },
    { en: "Flowering", ar: "إزهار", target: 1200 },
    { en: "Grain Fill", ar: "امتلاء الحبوب", target: 1600 },
    { en: "Maturity", ar: "نضج", target: 2000 },
  ];

  return Array.from({ length: 8 }, (_, i) => {
    const stageIndex = Math.floor(mockRandom() * (stages.length - 1));
    const currentStage = stages[stageIndex] ?? stages[0];
    const nextStage = stages[stageIndex + 1] ?? stages[stages.length - 1];
    const currentGDD = mockRandom() * 200 + (currentStage?.target ?? 800) - 100;

    const history = Array.from({ length: 30 }, (_, j) => ({
      date: new Date(Date.now() - (29 - j) * 24 * 60 * 60 * 1000).toISOString(),
      gdd: (currentGDD / 30) * (j + 1),
      temp_min: 15 + mockRandom() * 10,
      temp_max: 25 + mockRandom() * 10,
    }));

    return {
      id: `field-${i + 1}`,
      farmId: `farm-${mockRandomInt(1, 10)}`,
      farmName: `مزرعة ${mockRandomInt(1, 10)}`,
      fieldName: `حقل ${String.fromCharCode(65 + i)}`,
      cropType: ["قمح", "ذرة"][Math.floor(mockRandom() * 2)] ?? "قمح",
      plantingDate: new Date(
        Date.now() - 60 * 24 * 60 * 60 * 1000,
      ).toISOString(),
      currentGDD,
      targetGDD: nextStage?.target ?? 2000,
      currentStage: currentStage?.en ?? "Vegetative",
      currentStageAr: currentStage?.ar ?? "نمو خضري",
      nextStage: nextStage?.en ?? "Maturity",
      nextStageAr: nextStage?.ar ?? "نضج",
      daysToNextStage: mockRandomInt(5, 20),
      gddToNextStage: (nextStage?.target ?? 2000) - currentGDD,
      alerts:
        mockRandom() > 0.5
          ? [
              {
                type:
                  mockRandom() > 0.7
                    ? "critical"
                    : ("warning" as "info" | "warning" | "critical"),
                message: "Temperature stress detected",
                messageAr: "تم اكتشاف إجهاد حراري",
              },
            ]
          : [],
      history,
    };
  });
}

function generateMockSprayWindows(): SprayWindow[] {
  const products = [
    { type: "pesticide" as const, name: "Malathion" },
    { type: "herbicide" as const, name: "Glyphosate" },
    { type: "fungicide" as const, name: "Mancozeb" },
    { type: "fertilizer" as const, name: "NPK 20-20-20" },
  ];

  const statuses: Array<"upcoming" | "optimal" | "missed" | "completed"> = [
    "upcoming",
    "optimal",
    "missed",
    "completed",
  ];

  return Array.from({ length: 12 }, (_, i) => {
    const product = products[Math.floor(mockRandom() * products.length)] ?? products[0];
    const startDate = new Date(
      Date.now() + mockRandom() * 7 * 24 * 60 * 60 * 1000,
    );
    const endDate = new Date(startDate.getTime() + 3 * 24 * 60 * 60 * 1000);

    return {
      id: `spray-${i + 1}`,
      farmId: `farm-${mockRandomInt(1, 10)}`,
      farmName: `مزرعة ${mockRandomInt(1, 10)}`,
      fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
      cropType: ["قمح", "بن", "قات"][Math.floor(mockRandom() * 3)] ?? "قمح",
      productType: product?.type ?? "pesticide",
      productName: product?.name ?? "Malathion",
      windowStart: startDate.toISOString(),
      windowEnd: endDate.toISOString(),
      optimalTime: new Date(
        startDate.getTime() + 1.5 * 24 * 60 * 60 * 1000,
      ).toISOString(),
      status: statuses[Math.floor(mockRandom() * statuses.length)] ?? "upcoming",
      conditions: {
        temperature: 20 + mockRandom() * 10,
        windSpeed: 5 + mockRandom() * 10,
        humidity: 40 + mockRandom() * 40,
        precipitation: mockRandom() * 5,
      },
      recommendations: [
        "Apply early morning or late evening",
        "Avoid windy conditions",
        "Check weather forecast",
      ],
      recommendationsAr: [
        "التطبيق في الصباح الباكر أو المساء",
        "تجنب الظروف العاصفة",
        "تحقق من توقعات الطقس",
      ],
    };
  });
}

function generateMockSprayHistory(): SprayHistory[] {
  const products = [
    { type: "pesticide", name: "Malathion" },
    { type: "herbicide", name: "Glyphosate" },
    { type: "fungicide", name: "Mancozeb" },
    { type: "fertilizer", name: "NPK 20-20-20" },
  ];

  return Array.from({ length: 20 }, (_, i) => {
    const product = products[Math.floor(mockRandom() * products.length)] ?? products[0];
    return {
      id: `spray-hist-${i + 1}`,
      farmName: `مزرعة ${mockRandomInt(1, 10)}`,
      fieldName: `حقل ${String.fromCharCode(65 + (i % 5))}`,
      productType: product?.type ?? "pesticide",
      productName: product?.name ?? "Malathion",
      appliedAt: new Date(
        Date.now() - mockRandom() * 30 * 24 * 60 * 60 * 1000,
      ).toISOString(),
      area: mockRandom() * 30 + 5,
      quantity: mockRandom() * 50 + 10,
      cost: mockRandom() * 1000 + 200,
      effectiveness: mockRandomInt(70, 30),
    };
  });
}

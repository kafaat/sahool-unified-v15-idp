/**
 * VRA Panel Component
 * مكون لوحة التطبيق المتغير المعدل
 *
 * Main panel for generating and managing VRA prescription maps.
 */

"use client";

import React, { useState } from "react";
import { Loader2, Sprout, TrendingDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useGeneratePrescription } from "../hooks/useVRA";
import type {
  VRAType,
  VRAMethod,
  PrescriptionRequest,
  PrescriptionResponse,
} from "../types/vra";
import { VRA_TYPES, ZONE_METHODS, ZONE_COUNT_OPTIONS } from "../types/vra";
import { PrescriptionMap } from "./PrescriptionMap";
import { PrescriptionTable } from "./PrescriptionTable";

// ═══════════════════════════════════════════════════════════════════════════
// Component Props
// ═══════════════════════════════════════════════════════════════════════════

export interface VRAPanelProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  latitude: number;
  longitude: number;
  onPrescriptionGenerated?: (prescription: PrescriptionResponse) => void;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const VRAPanel: React.FC<VRAPanelProps> = ({
  fieldId,
  fieldName,
  fieldNameAr,
  latitude,
  longitude,
  onPrescriptionGenerated,
}) => {
  // State
  const [vraType, setVraType] = useState<VRAType>("fertilizer");
  const [targetRate, setTargetRate] = useState<number>(100);
  const [numZones, setNumZones] = useState<number>(3);
  const [zoneMethod, setZoneMethod] = useState<VRAMethod>("ndvi");
  const [productPrice, setProductPrice] = useState<number | undefined>();
  const [notes, setNotes] = useState<string>("");
  const [currentPrescription, setCurrentPrescription] =
    useState<PrescriptionResponse | null>(null);

  // Hooks
  const generateMutation = useGeneratePrescription();

  // Handlers
  const handleGenerate = async () => {
    const request: PrescriptionRequest = {
      fieldId,
      latitude,
      longitude,
      vraType,
      targetRate,
      unit: VRA_TYPES[vraType].defaultUnit,
      numZones,
      zoneMethod,
      productPricePerUnit: productPrice,
      notes,
    };

    try {
      const prescription = await generateMutation.mutateAsync(request);
      setCurrentPrescription(prescription);
      if (onPrescriptionGenerated) {
        onPrescriptionGenerated(prescription);
      }
    } catch (error) {
      console.error("Failed to generate prescription:", error);
    }
  };

  const selectedType = VRA_TYPES[vraType];
  const selectedMethod = ZONE_METHODS[zoneMethod];

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sprout className="w-5 h-5" />
            <span>Variable Rate Application | التطبيق المتغير المعدل</span>
          </CardTitle>
          {fieldNameAr && (
            <p className="text-sm text-gray-600">
              {fieldName} | {fieldNameAr}
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          {/* VRA Type Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Application Type | نوع التطبيق
            </label>
            <select
              value={vraType}
              onChange={(e) => setVraType(e.target.value as VRAType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {Object.values(VRA_TYPES).map((type) => (
                <option key={type.type} value={type.type}>
                  {type.name} | {type.nameAr}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {selectedType.description} | {selectedType.descriptionAr}
            </p>
          </div>

          {/* Target Rate */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Target Rate | المعدل المستهدف ({selectedType.defaultUnit})
            </label>
            <Input
              type="number"
              value={targetRate}
              onChange={(e) => setTargetRate(Number(e.target.value))}
              min={0}
              step={0.1}
              className="w-full"
            />
          </div>

          {/* Number of Zones */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Number of Zones | عدد المناطق
            </label>
            <div className="flex gap-4">
              {ZONE_COUNT_OPTIONS.map((count) => (
                <label
                  key={count}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <input
                    type="radio"
                    name="numZones"
                    value={count}
                    checked={numZones === count}
                    onChange={() => setNumZones(count)}
                    className="w-4 h-4 text-green-600"
                  />
                  <span>
                    {count} Zones | {count} مناطق
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Zone Method */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Zone Classification Method | طريقة تصنيف المناطق
            </label>
            <select
              value={zoneMethod}
              onChange={(e) => setZoneMethod(e.target.value as VRAMethod)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {Object.values(ZONE_METHODS).map((method) => (
                <option key={method.method} value={method.method}>
                  {method.name} | {method.nameAr}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {selectedMethod.description} | {selectedMethod.descriptionAr}
            </p>
          </div>

          {/* Product Price (Optional) */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Product Price per Unit (Optional) | سعر المنتج لكل وحدة (اختياري)
            </label>
            <Input
              type="number"
              value={productPrice || ""}
              onChange={(e) =>
                setProductPrice(
                  e.target.value ? Number(e.target.value) : undefined,
                )
              }
              min={0}
              step={0.01}
              placeholder="0.00"
              className="w-full"
            />
            <p className="mt-1 text-xs text-gray-500">
              For cost savings calculation | لحساب توفير التكاليف
            </p>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Notes | ملاحظات
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Add any notes about this prescription..."
            />
          </div>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={generateMutation.isPending}
            className="w-full"
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating... | جاري التوليد...
              </>
            ) : (
              <>
                <Sprout className="w-4 h-4 mr-2" />
                Generate Prescription | توليد الوصفة
              </>
            )}
          </Button>

          {/* Error Display */}
          {generateMutation.isError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">
                {generateMutation.error?.message ||
                  "Failed to generate prescription"}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Display */}
      {currentPrescription && (
        <>
          {/* Savings Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-green-600" />
                <span>Savings Analysis | تحليل التوفير</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    Total Product | إجمالي المنتج
                  </p>
                  <p className="text-2xl font-bold text-green-700">
                    {currentPrescription.totalProductNeeded.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">
                    {currentPrescription.unit}
                  </p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Savings | التوفير</p>
                  <p className="text-2xl font-bold text-blue-700">
                    {currentPrescription.savingsPercent.toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500">
                    {currentPrescription.savingsAmount.toFixed(2)}{" "}
                    {currentPrescription.unit}
                  </p>
                </div>
                {currentPrescription.costSavings && (
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600">
                      Cost Savings | توفير التكلفة
                    </p>
                    <p className="text-2xl font-bold text-purple-700">
                      ${currentPrescription.costSavings.toFixed(2)}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Prescription Map */}
          <PrescriptionMap prescription={currentPrescription} />

          {/* Prescription Table */}
          <PrescriptionTable prescription={currentPrescription} />
        </>
      )}
    </div>
  );
};

export default VRAPanel;

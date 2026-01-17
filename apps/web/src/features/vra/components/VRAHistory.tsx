/**
 * VRA History Component
 * مكون سجل التطبيق المتغير المعدل
 *
 * List of past VRA prescriptions with details and actions.
 */

"use client";

import React, { useState } from "react";
import {
  History,
  Eye,
  Trash2,
  Calendar,
  TrendingDown,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  usePrescriptionHistory,
  usePrescriptionDetails,
  useDeletePrescription,
} from "../hooks/useVRA";
import { VRA_TYPES } from "../types/vra";
import { PrescriptionMap } from "./PrescriptionMap";
import { PrescriptionTable } from "./PrescriptionTable";

// ═══════════════════════════════════════════════════════════════════════════
// Component Props
// ═══════════════════════════════════════════════════════════════════════════

export interface VRAHistoryProps {
  fieldId: string;
  fieldName?: string;
  fieldNameAr?: string;
  limit?: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const VRAHistory: React.FC<VRAHistoryProps> = ({
  fieldId,
  fieldName,
  fieldNameAr,
  limit = 10,
}) => {
  const [selectedPrescriptionId, setSelectedPrescriptionId] = useState<
    string | null
  >(null);

  // Hooks
  const historyQuery = usePrescriptionHistory(fieldId, { limit });
  const detailsQuery = usePrescriptionDetails(selectedPrescriptionId || "", {
    enabled: !!selectedPrescriptionId,
  });
  const deleteMutation = useDeletePrescription();

  // Handlers
  const handleView = (prescriptionId: string) => {
    setSelectedPrescriptionId(prescriptionId);
  };

  const handleDelete = async (prescriptionId: string) => {
    if (
      !confirm(
        "Are you sure you want to delete this prescription? | هل أنت متأكد من حذف هذه الوصفة؟",
      )
    ) {
      return;
    }

    try {
      await deleteMutation.mutateAsync(prescriptionId);
      if (selectedPrescriptionId === prescriptionId) {
        setSelectedPrescriptionId(null);
      }
    } catch (error) {
      console.error("Failed to delete prescription:", error);
    }
  };

  const handleClose = () => {
    setSelectedPrescriptionId(null);
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Get VRA type config
  const getTypeConfig = (vraType: string) => {
    return VRA_TYPES[vraType as keyof typeof VRA_TYPES];
  };

  return (
    <div className="space-y-6">
      {/* History List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5" />
            <span>Prescription History | سجل الوصفات</span>
          </CardTitle>
          {fieldNameAr && (
            <p className="text-sm text-gray-600">
              {fieldName} | {fieldNameAr}
            </p>
          )}
        </CardHeader>
        <CardContent>
          {historyQuery.isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : historyQuery.isError ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">
                {historyQuery.error?.message ||
                  "Failed to load prescription history"}
              </p>
            </div>
          ) : !historyQuery.data ||
            historyQuery.data.prescriptions.length === 0 ? (
            <div className="text-center py-8">
              <History className="w-12 h-12 mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">
                No prescriptions found for this field | لم يتم العثور على وصفات
                لهذا الحقل
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {historyQuery.data.prescriptions.map((prescription) => {
                const typeConfig = getTypeConfig(prescription.vraType);
                return (
                  <div
                    key={prescription.id}
                    className={`p-4 border-2 rounded-lg transition-all ${
                      selectedPrescriptionId === prescription.id
                        ? "border-green-500 bg-green-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      {/* Left Section - Info */}
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-3">
                          <h4 className="font-semibold text-lg">
                            {typeConfig.name} | {typeConfig.nameAr}
                          </h4>
                          <span className="px-2 py-1 bg-gray-100 text-xs font-medium rounded">
                            {prescription.numZones} Zones
                          </span>
                        </div>

                        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(prescription.createdAt)}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <TrendingDown className="w-4 h-4 text-green-600" />
                            <span className="font-medium text-green-600">
                              {prescription.savingsPercent.toFixed(1)}% Savings
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                          <div>
                            <p className="text-gray-500">Target Rate</p>
                            <p className="font-semibold">
                              {prescription.targetRate} {prescription.unit}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500">Total Area</p>
                            <p className="font-semibold">
                              {prescription.totalAreaHa.toFixed(2)} ha
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500">Product Saved</p>
                            <p className="font-semibold text-green-600">
                              {prescription.savingsAmount.toFixed(2)}{" "}
                              {prescription.unit}
                            </p>
                          </div>
                          {prescription.costSavings && (
                            <div>
                              <p className="text-gray-500">Cost Savings</p>
                              <p className="font-semibold text-purple-600">
                                ${prescription.costSavings.toFixed(2)}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Right Section - Actions */}
                      <div className="flex flex-col gap-2">
                        <Button
                          variant={
                            selectedPrescriptionId === prescription.id
                              ? "primary"
                              : "outline"
                          }
                          size="sm"
                          onClick={() =>
                            selectedPrescriptionId === prescription.id
                              ? handleClose()
                              : handleView(prescription.id)
                          }
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          {selectedPrescriptionId === prescription.id
                            ? "Close"
                            : "View"}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(prescription.id)}
                          disabled={deleteMutation.isPending}
                        >
                          {deleteMutation.isPending ? (
                            <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4 mr-1" />
                          )}
                          Delete
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selected Prescription Details */}
      {selectedPrescriptionId && (
        <>
          {detailsQuery.isLoading ? (
            <Card>
              <CardContent className="py-8">
                <div className="flex items-center justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                  <span className="ml-3 text-gray-600">
                    Loading prescription details...
                  </span>
                </div>
              </CardContent>
            </Card>
          ) : detailsQuery.isError ? (
            <Card>
              <CardContent className="py-8">
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">
                    {detailsQuery.error?.message ||
                      "Failed to load prescription details"}
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : detailsQuery.data ? (
            <>
              {/* Prescription Map */}
              <PrescriptionMap prescription={detailsQuery.data} />

              {/* Prescription Table */}
              <PrescriptionTable prescription={detailsQuery.data} />
            </>
          ) : null}
        </>
      )}
    </div>
  );
};

export default VRAHistory;

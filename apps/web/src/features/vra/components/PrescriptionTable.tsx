/**
 * Prescription Table Component
 * مكون جدول الوصفة
 *
 * Table view of VRA prescription zones with export functionality.
 */

'use client';

import React, { useState } from 'react';
import { Table, Download, FileJson, FileText, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useExportPrescription } from '../hooks/useVRA';
import type { PrescriptionResponse, ExportFormat } from '../types/vra';
import { EXPORT_FORMAT_LABELS } from '../types/vra';

// ═══════════════════════════════════════════════════════════════════════════
// Component Props
// ═══════════════════════════════════════════════════════════════════════════

export interface PrescriptionTableProps {
  prescription: PrescriptionResponse;
  showExport?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const PrescriptionTable: React.FC<PrescriptionTableProps> = ({
  prescription,
  showExport = true,
}) => {
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(null);
  const exportMutation = useExportPrescription();

  // Handle export
  const handleExport = async (format: ExportFormat) => {
    setExportingFormat(format);

    try {
      const data = await exportMutation.mutateAsync({
        prescriptionId: prescription.id,
        format,
      });

      // Trigger download
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: format === 'geojson' ? 'application/geo+json' : 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `prescription_${prescription.id}_${format}.${format === 'geojson' ? 'geojson' : 'json'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExportingFormat(null);
    }
  };

  // Handle CSV export (client-side generation)
  const handleCSVExport = () => {
    const headers = [
      'Zone ID',
      'Zone Name',
      'Zone Name (AR)',
      'Zone Level',
      'NDVI Min',
      'NDVI Max',
      'Area (ha)',
      'Percentage (%)',
      'Rate',
      'Unit',
      'Total Product',
    ];

    const rows = prescription.zones.map((zone) => [
      zone.zoneId,
      zone.zoneName,
      zone.zoneNameAr,
      zone.zoneLevel,
      zone.ndviMin.toFixed(3),
      zone.ndviMax.toFixed(3),
      zone.areaHa.toFixed(2),
      zone.percentage.toFixed(1),
      zone.recommendedRate.toFixed(2),
      zone.unit,
      zone.totalProduct.toFixed(2),
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
      '',
      `Total Area,${prescription.totalAreaHa.toFixed(2)} ha`,
      `Total Product,${prescription.totalProductNeeded.toFixed(2)} ${prescription.unit}`,
      `Flat Rate Product,${prescription.flatRateProduct.toFixed(2)} ${prescription.unit}`,
      `Savings,${prescription.savingsPercent.toFixed(1)}%`,
      `Savings Amount,${prescription.savingsAmount.toFixed(2)} ${prescription.unit}`,
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `prescription_${prescription.id}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Table className="w-5 h-5" />
            <span>Zone Details | تفاصيل المناطق</span>
          </CardTitle>
          {showExport && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCSVExport}
                disabled={exportingFormat !== null}
              >
                {exportingFormat === 'csv' ? (
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                ) : (
                  <FileText className="w-4 h-4 mr-1" />
                )}
                CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport('geojson')}
                disabled={exportingFormat !== null}
              >
                {exportingFormat === 'geojson' ? (
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                ) : (
                  <FileJson className="w-4 h-4 mr-1" />
                )}
                GeoJSON
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b-2 border-gray-300">
                <th className="text-left p-3 text-sm font-semibold">
                  Zone | منطقة
                </th>
                <th className="text-left p-3 text-sm font-semibold">
                  Level | مستوى
                </th>
                <th className="text-right p-3 text-sm font-semibold">
                  NDVI Range | نطاق NDVI
                </th>
                <th className="text-right p-3 text-sm font-semibold">
                  Area | المساحة (ha)
                </th>
                <th className="text-right p-3 text-sm font-semibold">
                  % of Field | % من الحقل
                </th>
                <th className="text-right p-3 text-sm font-semibold">
                  Rate | المعدل
                </th>
                <th className="text-right p-3 text-sm font-semibold">
                  Total Product | إجمالي المنتج
                </th>
              </tr>
            </thead>
            <tbody>
              {prescription.zones.map((zone) => (
                <tr
                  key={zone.zoneId}
                  className="border-b border-gray-200 hover:bg-gray-50"
                >
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-4 h-4 rounded border border-gray-300"
                        style={{ backgroundColor: zone.color }}
                      />
                      <div>
                        <p className="text-sm font-medium">{zone.zoneName}</p>
                        <p className="text-xs text-gray-500">{zone.zoneNameAr}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-3">
                    <span className="text-sm capitalize">{zone.zoneLevel.replace('_', ' ')}</span>
                  </td>
                  <td className="p-3 text-right">
                    <span className="text-sm">
                      {zone.ndviMin.toFixed(2)} - {zone.ndviMax.toFixed(2)}
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    <span className="text-sm font-medium">{zone.areaHa.toFixed(2)}</span>
                  </td>
                  <td className="p-3 text-right">
                    <span className="text-sm">{zone.percentage.toFixed(1)}%</span>
                  </td>
                  <td className="p-3 text-right">
                    <div className="text-sm">
                      <p className="font-semibold text-green-700">
                        {zone.recommendedRate.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500">{zone.unit}</p>
                    </div>
                  </td>
                  <td className="p-3 text-right">
                    <div className="text-sm">
                      <p className="font-medium">{zone.totalProduct.toFixed(2)}</p>
                      <p className="text-xs text-gray-500">{zone.unit}</p>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t-2 border-gray-300 bg-gray-50">
                <td colSpan={3} className="p-3 text-sm font-bold">
                  Total | المجموع
                </td>
                <td className="p-3 text-right text-sm font-bold">
                  {prescription.totalAreaHa.toFixed(2)} ha
                </td>
                <td className="p-3 text-right text-sm font-bold">
                  100%
                </td>
                <td className="p-3 text-right text-sm font-bold text-green-700">
                  {prescription.targetRate.toFixed(2)}*
                </td>
                <td className="p-3 text-right text-sm font-bold">
                  {prescription.totalProductNeeded.toFixed(2)} {prescription.unit}
                </td>
              </tr>
              <tr className="bg-blue-50">
                <td colSpan={6} className="p-3 text-sm font-semibold text-blue-700">
                  Flat Rate Application | التطبيق بمعدل ثابت
                </td>
                <td className="p-3 text-right text-sm font-semibold text-blue-700">
                  {prescription.flatRateProduct.toFixed(2)} {prescription.unit}
                </td>
              </tr>
              <tr className="bg-green-50">
                <td colSpan={6} className="p-3 text-sm font-bold text-green-700">
                  Savings vs. Flat Rate | التوفير مقارنة بالمعدل الثابت
                </td>
                <td className="p-3 text-right text-sm font-bold text-green-700">
                  {prescription.savingsAmount.toFixed(2)} {prescription.unit} ({prescription.savingsPercent.toFixed(1)}%)
                </td>
              </tr>
              {prescription.costSavings && (
                <tr className="bg-purple-50">
                  <td colSpan={6} className="p-3 text-sm font-bold text-purple-700">
                    Cost Savings | توفير التكلفة
                  </td>
                  <td className="p-3 text-right text-sm font-bold text-purple-700">
                    ${prescription.costSavings.toFixed(2)}
                  </td>
                </tr>
              )}
            </tfoot>
          </table>
        </div>

        {/* Notes Section */}
        <div className="mt-4 text-xs text-gray-500">
          <p>* Average target rate across all zones | المعدل المستهدف المتوسط عبر جميع المناطق</p>
          <p className="mt-1">
            Prescription ID: {prescription.id} | Created: {new Date(prescription.createdAt).toLocaleDateString()}
          </p>
          {prescription.notes && (
            <p className="mt-2 p-2 bg-gray-50 rounded border border-gray-200">
              <span className="font-medium">Notes:</span> {prescription.notes}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default PrescriptionTable;

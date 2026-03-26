/**
 * Compliance Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة تقارير الامتثال
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface ComplianceRecord {
  id: string;
  farmId: string;
  farmName: string;
  farmNameAr: string;
  standard: 'globalgap' | 'organic' | 'iso' | 'haccp';
  status: 'compliant' | 'partial' | 'non_compliant' | 'pending' | 'expired';
  score: number;
  lastAudit: string;
  nextAudit: string;
  auditor: string;
  findings: number;
  criticalFindings: number;
}

export const MOCK_RECORDS: ComplianceRecord[] = [
  {
    id: '1',
    farmId: 'F001',
    farmName: 'Al-Rashid Farm',
    farmNameAr: 'مزرعة الراشد',
    standard: 'globalgap',
    status: 'compliant',
    score: 95,
    lastAudit: '2026-01-15',
    nextAudit: '2027-01-15',
    auditor: 'SGS Arabia',
    findings: 2,
    criticalFindings: 0,
  },
  {
    id: '2',
    farmId: 'F002',
    farmName: 'Green Valley',
    farmNameAr: 'الوادي الأخضر',
    standard: 'organic',
    status: 'compliant',
    score: 88,
    lastAudit: '2025-12-10',
    nextAudit: '2026-12-10',
    auditor: 'Control Union',
    findings: 5,
    criticalFindings: 0,
  },
  {
    id: '3',
    farmId: 'F003',
    farmName: 'Desert Oasis',
    farmNameAr: 'واحة الصحراء',
    standard: 'globalgap',
    status: 'partial',
    score: 72,
    lastAudit: '2026-01-05',
    nextAudit: '2026-04-05',
    auditor: 'Bureau Veritas',
    findings: 12,
    criticalFindings: 2,
  },
  {
    id: '4',
    farmId: 'F004',
    farmName: 'Palm Gardens',
    farmNameAr: 'حدائق النخيل',
    standard: 'iso',
    status: 'pending',
    score: 0,
    lastAudit: '',
    nextAudit: '2026-02-20',
    auditor: 'TUV',
    findings: 0,
    criticalFindings: 0,
  },
  {
    id: '5',
    farmId: 'F005',
    farmName: 'Old Farms',
    farmNameAr: 'المزارع القديمة',
    standard: 'globalgap',
    status: 'expired',
    score: 65,
    lastAudit: '2024-06-15',
    nextAudit: '2025-06-15',
    auditor: 'SGS Arabia',
    findings: 18,
    criticalFindings: 5,
  },
];

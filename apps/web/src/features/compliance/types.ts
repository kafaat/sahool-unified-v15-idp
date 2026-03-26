/**
 * Compliance Feature - Types
 * أنواع ميزة الامتثال والجودة
 */

export type ComplianceStatus =
  | 'compliant'
  | 'partial'
  | 'non_compliant'
  | 'pending_review'
  | 'not_applicable';
export type CertificationStatus = 'active' | 'expired' | 'pending' | 'revoked';
export type AuditSeverity = 'critical' | 'major' | 'minor' | 'observation';

export interface ComplianceItem {
  id: string;
  category: string;
  categoryAr: string;
  requirement: string;
  requirementAr: string;
  description?: string;
  descriptionAr?: string;
  status: ComplianceStatus;
  score: number;
  maxScore: number;
  lastAudit: string;
  nextAudit: string;
  auditor?: string;
  evidence?: string[];
  notes?: string;
  notesAr?: string;
  actions?: ComplianceAction[];
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface ComplianceAction {
  id: string;
  description: string;
  descriptionAr: string;
  assignedTo: string;
  dueDate: string;
  completedDate?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
}

export interface Certification {
  id: string;
  name: string;
  nameAr: string;
  type: 'globalgap' | 'organic' | 'iso' | 'haccp' | 'other';
  issuer: string;
  issuerAr: string;
  status: CertificationStatus;
  certificateNumber: string;
  issueDate: string;
  expiryDate: string;
  scope?: string;
  scopeAr?: string;
  attachments?: string[];
  metadata: Record<string, unknown>;
}

export interface AuditReport {
  id: string;
  auditDate: string;
  auditor: string;
  auditType: 'internal' | 'external' | 'surveillance';
  overallScore: number;
  findings: AuditFinding[];
  recommendations?: string[];
  recommendationsAr?: string[];
  status: 'draft' | 'final' | 'approved';
  attachments?: string[];
}

export interface AuditFinding {
  id: string;
  category: string;
  description: string;
  descriptionAr: string;
  severity: AuditSeverity;
  status: 'open' | 'closed' | 'in_progress';
  rootCause?: string;
  correctiveAction?: string;
  dueDate?: string;
  closedDate?: string;
}

export interface ComplianceFilters {
  category?: string;
  status?: ComplianceStatus;
  search?: string;
}

export interface ComplianceStats {
  overallScore: number;
  totalRequirements: number;
  compliantCount: number;
  partialCount: number;
  nonCompliantCount: number;
  pendingAudits: number;
  activeCertifications: number;
  expiringCertifications: number;
  openFindings: number;
  byCategory: Record<string, { score: number; total: number }>;
}

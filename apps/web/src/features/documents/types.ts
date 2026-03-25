/**
 * Documents Feature - Types
 * أنواع ميزة الوثائق
 */

export type DocumentCategory =
  | 'compliance'
  | 'permits'
  | 'contracts'
  | 'reports'
  | 'certificates'
  | 'maps'
  | 'invoices'
  | 'other';
export type DocumentStatus = 'draft' | 'active' | 'expired' | 'archived';

export interface Document {
  id: string;
  title: string;
  titleAr: string;
  category: DocumentCategory;
  status: DocumentStatus;
  fileName: string;
  fileSize: number;
  fileType: string;
  fileUrl?: string;
  farmId?: string;
  farmName?: string;
  farmNameAr?: string;
  tags: string[];
  description?: string;
  descriptionAr?: string;
  expiryDate?: string;
  uploadedBy: string;
  uploadedByAr: string;
  createdAt: string;
  updatedAt: string;
}

export interface DocumentFilters {
  category?: DocumentCategory;
  status?: DocumentStatus;
  farmId?: string;
  search?: string;
}

export interface DocumentUploadData {
  title: string;
  titleAr: string;
  category: DocumentCategory;
  farmId?: string;
  tags?: string[];
  description?: string;
  descriptionAr?: string;
  expiryDate?: string;
  file: File;
}

export interface DocumentStats {
  totalDocuments: number;
  activeDocuments: number;
  expiringDocuments: number;
  totalSizeMb: number;
  byCategory: Record<string, number>;
}

/**
 * Inventory Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة إدارة المخزون
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface InventoryItem {
  id: string;
  name: string;
  nameAr: string;
  category: string;
  categoryAr: string;
  farmId: string;
  farmName: string;
  farmNameAr: string;
  quantity: number;
  unit: string;
  minQuantity: number;
  value: number;
  currency: string;
  status: "in_stock" | "low_stock" | "out_of_stock" | "expired";
  lastUpdated: string;
  expiryDate?: string;
}

export const MOCK_INVENTORY: InventoryItem[] = [
  {
    id: "1",
    name: "NPK Fertilizer",
    nameAr: "سماد NPK",
    category: "fertilizers",
    categoryAr: "أسمدة",
    farmId: "F001",
    farmName: "Al-Rashid Farm",
    farmNameAr: "مزرعة الراشد",
    quantity: 500,
    unit: "كيلو",
    minQuantity: 100,
    value: 15000,
    currency: "SAR",
    status: "in_stock",
    lastUpdated: "2026-01-25",
  },
  {
    id: "2",
    name: "Wheat Seeds",
    nameAr: "بذور قمح",
    category: "seeds",
    categoryAr: "بذور",
    farmId: "F002",
    farmName: "Green Valley",
    farmNameAr: "الوادي الأخضر",
    quantity: 50,
    unit: "كيلو",
    minQuantity: 100,
    value: 2500,
    currency: "SAR",
    status: "low_stock",
    lastUpdated: "2026-01-24",
  },
  {
    id: "3",
    name: "Pesticide A",
    nameAr: "مبيد حشري أ",
    category: "pesticides",
    categoryAr: "مبيدات",
    farmId: "F001",
    farmName: "Al-Rashid Farm",
    farmNameAr: "مزرعة الراشد",
    quantity: 0,
    unit: "لتر",
    minQuantity: 20,
    value: 0,
    currency: "SAR",
    status: "out_of_stock",
    lastUpdated: "2026-01-20",
  },
  {
    id: "4",
    name: "Organic Fertilizer",
    nameAr: "سماد عضوي",
    category: "fertilizers",
    categoryAr: "أسمدة",
    farmId: "F003",
    farmName: "Desert Oasis",
    farmNameAr: "واحة الصحراء",
    quantity: 200,
    unit: "كيلو",
    minQuantity: 50,
    value: 8000,
    currency: "SAR",
    status: "in_stock",
    lastUpdated: "2026-01-23",
    expiryDate: "2026-06-15",
  },
  {
    id: "5",
    name: "Herbicide B",
    nameAr: "مبيد أعشاب ب",
    category: "pesticides",
    categoryAr: "مبيدات",
    farmId: "F002",
    farmName: "Green Valley",
    farmNameAr: "الوادي الأخضر",
    quantity: 15,
    unit: "لتر",
    minQuantity: 10,
    value: 1200,
    currency: "SAR",
    status: "expired",
    lastUpdated: "2026-01-15",
    expiryDate: "2025-12-01",
  },
];

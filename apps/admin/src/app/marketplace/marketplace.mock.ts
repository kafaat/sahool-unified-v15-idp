/**
 * Marketplace Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة إدارة السوق
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface Product {
  id: string;
  name: string;
  nameAr: string;
  category: string;
  categoryAr: string;
  seller: string;
  sellerAr: string;
  price: number;
  currency: string;
  unit: string;
  quantity: number;
  status: "active" | "pending" | "rejected" | "sold_out";
  views: number;
  orders: number;
  createdAt: string;
  image?: string;
}

export const MOCK_PRODUCTS: Product[] = [
  {
    id: "1",
    name: "Organic Wheat Seeds",
    nameAr: "بذور قمح عضوي",
    category: "seeds",
    categoryAr: "بذور",
    seller: "Ahmed Farm",
    sellerAr: "مزرعة أحمد",
    price: 150,
    currency: "SAR",
    unit: "كيلو",
    quantity: 500,
    status: "active",
    views: 234,
    orders: 12,
    createdAt: "2026-01-20",
  },
  {
    id: "2",
    name: "NPK Fertilizer",
    nameAr: "سماد NPK",
    category: "fertilizers",
    categoryAr: "أسمدة",
    seller: "Green Supplies",
    sellerAr: "المستلزمات الخضراء",
    price: 280,
    currency: "SAR",
    unit: "كيس 50 كيلو",
    quantity: 200,
    status: "active",
    views: 567,
    orders: 45,
    createdAt: "2026-01-18",
  },
  {
    id: "3",
    name: "Drip Irrigation Kit",
    nameAr: "نظام ري بالتنقيط",
    category: "equipment",
    categoryAr: "معدات",
    seller: "Agri Tech",
    sellerAr: "تقنيات زراعية",
    price: 1200,
    currency: "SAR",
    unit: "طقم",
    quantity: 50,
    status: "pending",
    views: 89,
    orders: 0,
    createdAt: "2026-01-24",
  },
  {
    id: "4",
    name: "Organic Pesticide",
    nameAr: "مبيد حشري عضوي",
    category: "pesticides",
    categoryAr: "مبيدات",
    seller: "Bio Farm",
    sellerAr: "المزرعة الحيوية",
    price: 95,
    currency: "SAR",
    unit: "لتر",
    quantity: 0,
    status: "sold_out",
    views: 456,
    orders: 78,
    createdAt: "2026-01-10",
  },
  {
    id: "5",
    name: "Tomato Seeds - Hybrid",
    nameAr: "بذور طماطم هجين",
    category: "seeds",
    categoryAr: "بذور",
    seller: "Quality Seeds",
    sellerAr: "بذور الجودة",
    price: 45,
    currency: "SAR",
    unit: "كيس 100 جرام",
    quantity: 1000,
    status: "rejected",
    views: 12,
    orders: 0,
    createdAt: "2026-01-22",
  },
];

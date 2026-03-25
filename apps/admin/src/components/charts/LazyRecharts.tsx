'use client';

/**
 * Lazy-loaded Recharts Re-exports
 * إعادة تصدير مكونات Recharts مع التحميل الكسول
 *
 * This module re-exports all recharts components used across admin pages.
 * Consumer pages should import from LazyRecharts.dynamic.tsx instead of recharts directly.
 * This enables code splitting - recharts (~120KB) is only loaded when charts are rendered.
 */

export {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

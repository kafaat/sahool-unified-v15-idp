/**
 * Recharts Type Overrides for React 19 Compatibility
 * These declarations override the recharts types to work with React 19
 * Using 'any' for component types to bypass React 19 JSX compatibility issues
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

declare module 'recharts' {
  // Use 'any' to bypass React 19 JSX type compatibility issues
  export const ResponsiveContainer: any;
  export const BarChart: any;
  export const LineChart: any;
  export const PieChart: any;
  export const AreaChart: any;
  export const XAxis: any;
  export const YAxis: any;
  export const Tooltip: any;
  export const Legend: any;
  export const Bar: any;
  export const Line: any;
  export const Area: any;
  export const Pie: any;
  export const Cell: any;
  export const CartesianGrid: any;
  export const ReferenceLine: any;
  export const ComposedChart: any;
  export const Brush: any;
  export const Scatter: any;
  export const ScatterChart: any;
  export const ZAxis: any;
  export const RadialBarChart: any;
  export const RadialBar: any;
  export const Radar: any;
  export const RadarChart: any;
  export const PolarGrid: any;
  export const PolarAngleAxis: any;
  export const PolarRadiusAxis: any;
  export const Treemap: any;
  export const Funnel: any;
  export const FunnelChart: any;
  export const LabelList: any;
  export const ErrorBar: any;
  export const ReferenceArea: any;
  export const ReferenceDot: any;
}

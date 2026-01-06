/**
 * SAHOOL Dashboard Components Index
 * فهرس مكونات لوحة التحكم - محدث مع المكونات المسترجعة من الأرشيف
 */

// Core Components
export { KPICard } from './KPICard';
export { KPIGrid } from './KPIGrid';
export { AlertItem } from './AlertItem';
export { AlertPanel } from './AlertPanel';
export { QuickActions } from './QuickActions';
export { Cockpit } from './Cockpit';

// Recovered/Enhanced Components
export { StatsCards } from './StatsCards';
export { TaskCard } from './TaskCard';
export { TaskList } from './TaskList';
export { EventTimeline } from './EventTimeline';
// Export dynamic (lazy-loaded) map component by default for optimal bundle size (~200KB saved)
export { MapView } from './MapView.dynamic';

// UI Components
export { Skeleton, SkeletonCard, SkeletonTaskItem, SkeletonEventItem } from './ui/Skeleton';

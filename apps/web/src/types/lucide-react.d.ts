/**
 * Lucide React Type Overrides for React 19 Compatibility
 * These declarations override the lucide-react types to work with React 19
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

declare module 'lucide-react' {
  import { ForwardRefExoticComponent, RefAttributes, SVGProps } from 'react';

  export type LucideIcon = ForwardRefExoticComponent<
    Omit<SVGProps<SVGSVGElement>, 'ref'> & RefAttributes<SVGSVGElement>
  >;

  // Use 'any' to bypass React 19 JSX type compatibility issues
  // Core icons
  export const LayoutDashboard: any;
  export const Users: any;
  export const Sprout: any;
  export const FileText: any;
  export const TrendingUp: any;
  export const TrendingDown: any;
  export const Settings: any;
  export const Building2: any;
  export const Package: any;
  export const Calendar: any;
  export const FileBarChart: any;
  export const Menu: any;
  export const X: any;
  export const ChevronDown: any;
  export const ChevronUp: any;
  export const ChevronLeft: any;
  export const ChevronRight: any;
  export const Search: any;
  export const Bell: any;
  export const User: any;
  export const LogOut: any;
  export const Home: any;
  export const AlertCircle: any;
  export const CheckCircle: any;
  export const CheckCircle2: any;
  export const XCircle: any;
  export const Info: any;
  export const AlertTriangle: any;
  export const Loader2: any;
  export const Plus: any;
  export const Minus: any;
  export const Edit: any;
  export const Edit2: any;
  export const Trash: any;
  export const Trash2: any;
  export const Eye: any;
  export const EyeOff: any;
  export const Lock: any;
  export const Unlock: any;
  export const Mail: any;
  export const Phone: any;
  export const MapPin: any;
  export const Globe: any;
  export const Sun: any;
  export const Moon: any;
  export const Cloud: any;
  export const CloudRain: any;
  export const CloudSun: any;
  export const Thermometer: any;
  export const Droplet: any;
  export const Droplets: any;
  export const Wind: any;
  export const Leaf: any;
  export const Trees: any;
  export const Mountain: any;
  export const Map: any;
  export const Navigation: any;
  export const Compass: any;
  export const Target: any;
  export const Layers: any;
  export const Grid: any;
  export const Grid3x3: any;
  export const List: any;
  export const ListTodo: any;
  export const BarChart: any;
  export const BarChart3: any;
  export const LineChart: any;
  export const PieChart: any;
  export const Activity: any;
  export const Zap: any;
  export const Battery: any;
  export const Wifi: any;
  export const Upload: any;
  export const Download: any;
  export const RefreshCw: any;
  export const RotateCw: any;
  export const Copy: any;
  export const Clipboard: any;
  export const Save: any;
  export const Share: any;
  export const Share2: any;
  export const ExternalLink: any;
  export const Link: any;
  export const Image: any;
  export const FileImage: any;
  export const Camera: any;
  export const Video: any;
  export const Mic: any;
  export const Volume2: any;
  export const VolumeX: any;
  export const Play: any;
  export const Pause: any;
  export const Square: any;
  export const Circle: any;
  export const Heart: any;
  export const Star: any;
  export const Bookmark: any;
  export const Flag: any;
  export const Tag: any;
  export const Hash: any;
  export const Filter: any;
  export const SortAsc: any;
  export const SortDesc: any;
  export const ArrowUp: any;
  export const ArrowDown: any;
  export const ArrowLeft: any;
  export const ArrowRight: any;
  export const ArrowUpRight: any;
  export const ArrowDownLeft: any;
  export const MoreHorizontal: any;
  export const MoreVertical: any;
  export const Clock: any;
  export const Timer: any;
  export const Maximize: any;
  export const Maximize2: any;
  export const Minimize: any;
  export const ZoomIn: any;
  export const ZoomOut: any;
  // Marketplace & Wallet icons
  export const ShoppingCart: any;
  export const ShoppingBag: any;
  export const CreditCard: any;
  export const DollarSign: any;
  export const Wallet: any;
  export const Send: any;
  // Community icons
  export const ThumbsUp: any;
  export const MessageCircle: any;
  export const Award: any;
  // Equipment & IoT icons
  export const Wrench: any;
  export const Power: any;
  export const Signal: any;
  // Settings icons
  export const Shield: any;
  export const Monitor: any;
  export const Check: any;
  // Weather icons
  export const Gauge: any;
  export const Sunrise: any;
  export const Sunset: any;
}

/**
 * Dynamic (SSR-safe) export of FieldBoundaryMap
 * Leaflet requires browser APIs — must never render on the server.
 */

import dynamic from 'next/dynamic';

const FieldBoundaryMapDynamic = dynamic(() => import('./FieldBoundaryMap'), {
  loading: () => (
    <div
      className="bg-gray-100 animate-pulse flex items-center justify-center rounded-lg"
      style={{ height: '420px' }}
    >
      <p className="text-gray-500 text-sm">جاري تحميل الخريطة...</p>
    </div>
  ),
  ssr: false,
});

export { FieldBoundaryMapDynamic as FieldBoundaryMap };
export default FieldBoundaryMapDynamic;

import React from 'react';
import { createRoot } from 'react-dom/client';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import MapView from '../../../apps/web/src/components/dashboard/MapView';
import type { Field } from '../../../apps/web/src/lib/api/types';
import './style.css';

declare global {
  interface Window {
    fixtureMap: maplibregl.Map;
    fixtureErrors: string[];
    selectedField: string | null;
    attributionExecuted?: number;
    popupExecuted?: number;
  }
}

window.fixtureErrors = [];
const mode = new URLSearchParams(location.search).get('mode');
if (mode === 'attribution') {
  const map = new maplibregl.Map({
    container: 'root', attributionControl: false,
    style: { version: 8, sources: {}, layers: [] }, center: [44.2, 15], zoom: 6,
  });
  window.fixtureMap = map;
  map.on('error', (event) => window.fixtureErrors.push(event.error.message));
  const malicious = '<details open onload="window.attributionExecuted=1" ontoggle="window.attributionExecuted=1">attribution</details>';
  map.addControl(new maplibregl.AttributionControl({
    compact: false,
    customAttribution: `${malicious}<a href="https://example.org/credit">Safe credit</a>`,
  }));
  map.on('load', () => {
    map.addSource('attributed-source', {
      type: 'geojson', attribution: malicious,
      data: { type: 'Feature', properties: {}, geometry: { type: 'Point', coordinates: [44.2, 15] } },
    });
    map.addLayer({ id: 'attributed-layer', type: 'circle', source: 'attributed-source' });
  });
} else {
  // Observe the real consumer's map instance; every MapLibre operation still runs.
  const originalAddSource = maplibregl.Map.prototype.addSource;
  maplibregl.Map.prototype.addSource = function (...args) {
    if (args[0] === 'fields') {
      window.fixtureMap = this;
      this.on('error', (event) => window.fixtureErrors.push(event.error.message));
    }
    return originalAddSource.apply(this, args);
  };
  const fields: Field[] = [
    {
      id: 'bare-soil', farm_id: 'test-farm', status: 'active', area: 1,
      name: '<img src=x onerror="window.popupExecuted=1">', crop: 'wheat', ndvi_value: 0,
      boundary: { type: 'Polygon', coordinates: [[[44.18, 14.99], [44.20, 14.99], [44.20, 15.01], [44.18, 15.01], [44.18, 14.99]]] },
    },
    {
      id: 'healthy', farm_id: 'test-farm', status: 'active', area: 1,
      name: 'Healthy field', crop: 'coffee', ndvi_value: 0.7,
      boundary: { type: 'Polygon', coordinates: [[[44.21, 14.99], [44.23, 14.99], [44.23, 15.01], [44.21, 15.01], [44.21, 14.99]]] },
    },
  ];
  createRoot(document.getElementById('root')!).render(
    <MapView fields={fields} onFieldSelect={(id) => { window.selectedField = id; }} />,
  );
}

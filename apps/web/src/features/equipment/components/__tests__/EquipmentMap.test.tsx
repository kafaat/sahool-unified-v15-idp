/**
 * Regression test for EquipmentMap Leaflet cleanup.
 *
 * Bug: the previous implementation only cleared marker references in its
 * useEffect cleanup and never called `map.remove()`, leaving the
 * `_leaflet_id` attribute on the container DOM element. On a subsequent
 * remount Leaflet's L.Map constructor would throw
 *   "Map container is already initialized."
 * which propagated to the dashboard error boundary.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// ---- Leaflet stub (loaded via CDN as window.L in the real app). ------------
const mapRemove = vi.fn();
const tileAddTo = vi.fn();
const tileLayerFn = vi.fn(() => ({ addTo: tileAddTo }));

const mapInstance = {
  remove: mapRemove,
  setView: vi.fn().mockReturnThis(),
  fitBounds: vi.fn(),
};

const mapFactory = vi.fn((container: HTMLElement) => {
  // mimic Leaflet tagging the container so a second L.map() call would
  // throw "Map container is already initialized".
  (container as HTMLElement & { _leaflet_id?: number })._leaflet_id = 1;
  return {
    ...mapInstance,
    setView: vi.fn(() => mapInstance),
  };
});

beforeEach(() => {
  mapRemove.mockClear();
  mapFactory.mockClear();
  tileLayerFn.mockClear();
  tileAddTo.mockClear();

  (window as unknown as { L: unknown }).L = {
    map: mapFactory,
    tileLayer: tileLayerFn,
    divIcon: vi.fn(() => ({})),
    marker: vi.fn(() => ({
      addTo: vi.fn().mockReturnThis(),
      bindPopup: vi.fn().mockReturnThis(),
      remove: vi.fn(),
    })),
    latLngBounds: vi.fn(() => ({})),
  };
});

// React Query provider for the useEquipment hook used inside EquipmentMap.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../hooks/useEquipment', () => ({
  useEquipment: () => ({ data: [], isLoading: false }),
}));

// Import AFTER the mocks are registered.
import { EquipmentMap } from '../EquipmentMap';

function renderWithClient(ui: React.ReactElement) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>{ui}</QueryClientProvider>
  );
}

describe('EquipmentMap', () => {
  it('initializes a Leaflet map exactly once on mount', async () => {
    renderWithClient(<EquipmentMap />);
    await waitFor(() => expect(mapFactory).toHaveBeenCalledTimes(1));
  });

  it('calls map.remove() and clears _leaflet_id on unmount', async () => {
    const { unmount, container } = renderWithClient(<EquipmentMap />);
    await waitFor(() => expect(mapFactory).toHaveBeenCalledTimes(1));

    // Sanity: Leaflet stub should have tagged the map container DOM node.
    const mapDiv = container.querySelector('div.h-96') as
      | (HTMLDivElement & { _leaflet_id?: number })
      | null;
    expect(mapDiv).toBeTruthy();
    expect(mapDiv?._leaflet_id).toBe(1);

    unmount();

    expect(mapRemove).toHaveBeenCalledTimes(1);
    // _leaflet_id must be gone so a remount would not throw
    // "Map container is already initialized".
    expect(mapDiv?._leaflet_id).toBeUndefined();
  });
});

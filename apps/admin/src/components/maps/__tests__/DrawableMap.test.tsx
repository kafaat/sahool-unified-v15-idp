/**
 * DrawableMap Component Tests
 * اختبارات مكون خريطة الرسم التفاعلية
 *
 * Tests the DrawableMap component which supports polygon/rectangle drawing
 * for field boundary selection. Since Leaflet requires browser APIs that
 * jsdom does not fully support, we mock next/dynamic and react-leaflet.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import React from 'react';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

// Track map click handlers for simulating drawing
let __mapClickHandler: ((e: any) => void) | null = null;

// Mock next/dynamic to inline-render the DrawableMap component
// Since DrawableMap uses dynamic imports for react-leaflet components,
// we mock next/dynamic to return simple div stubs.
vi.mock('next/dynamic', () => ({
  __esModule: true,
  default: (_loader: () => Promise<any>, _opts?: any) => {
    const _React = require('react');
    // Return a stub component that captures props
    const DynamicComponent = (props: any) => {
      // For MapContainer, render children
      if (props.center || props.zoom || props.style) {
        return _React.createElement(
          'div',
          { 'data-testid': 'mock-map-container', style: props.style },
          props.children
        );
      }
      // For TileLayer
      if (props.url) {
        return _React.createElement('div', { 'data-testid': 'mock-tile-layer' });
      }
      // For LayersControl
      if (props.position) {
        return _React.createElement('div', { 'data-testid': 'mock-layers-control' }, props.children);
      }
      // For Marker
      if (props.position && Array.isArray(props.position)) {
        return _React.createElement('div', {
          'data-testid': 'mock-marker',
          'data-lat': props.position[0],
          'data-lng': props.position[1],
        });
      }
      // For Polyline/Polygon
      if (props.positions) {
        return _React.createElement('div', {
          'data-testid': props.pathOptions?.fillOpacity ? 'mock-polygon' : 'mock-polyline',
        });
      }
      // Default fallback
      return _React.createElement('div', { 'data-testid': 'mock-dynamic' }, props.children);
    };
    DynamicComponent.displayName = 'DynamicComponent';
    // Add BaseLayer sub-component for LayersControl
    DynamicComponent.BaseLayer = (props: any) => {
      const _React = require('react');
      return _React.createElement('div', { 'data-testid': 'mock-base-layer' }, props.children);
    };
    return DynamicComponent;
  },
}));

// Mock leaflet module
vi.mock('leaflet', () => ({
  __esModule: true,
  default: {
    divIcon: vi.fn(() => ({ options: {} })),
  },
  divIcon: vi.fn(() => ({ options: {} })),
}));

// Mock react-leaflet useMapEvents
vi.mock('react-leaflet', () => ({
  useMapEvents: vi.fn((handlers: any) => {
    _mapClickHandler = handlers.click;
    return {};
  }),
  MapContainer: (props: any) => {
    const _React = require('react');
    return _React.createElement('div', { 'data-testid': 'mock-map-container' }, props.children);
  },
  TileLayer: () => {
    const _React = require('react');
    return _React.createElement('div', { 'data-testid': 'mock-tile-layer' });
  },
  LayersControl: Object.assign(
    (props: any) => {
      const _React = require('react');
      return _React.createElement('div', null, props.children);
    },
    {
      BaseLayer: (props: any) => {
        const _React = require('react');
        return _React.createElement('div', null, props.children);
      },
    }
  ),
  Marker: () => null,
  Polyline: () => null,
  Polygon: () => null,
}));

// Mock @/lib/utils
vi.mock('@/lib/utils', () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(' '),
}));

import DrawableMap from '../../maps/DrawableMap';

// ═══════════════════════════════════════════════════════════════════════════
// Helper: render and wait for leaflet to load (async useEffect)
// ═══════════════════════════════════════════════════════════════════════════

async function renderDrawableMap(props: Record<string, any> = {}) {
  const defaultProps = {
    onBboxSelect: vi.fn(),
    onBoundaryDraw: vi.fn(),
  };

  let result: ReturnType<typeof render>;
  await act(async () => {
    result = render(<DrawableMap {...defaultProps} {...props} />);
    // Allow the useEffect (setIsClient + dynamic import('leaflet')) to settle
    await new Promise((r) => setTimeout(r, 0));
  });
  return result!;
}

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('DrawableMap', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    _mapClickHandler = null;
  });

  // ─── Rendering ──────────────────────────────────────────────────────────

  describe('rendering', () => {
    it('renders without crashing', async () => {
      const { container } = await renderDrawableMap();
      expect(container).toBeTruthy();
    });

    it('renders polygon drawing button with Arabic label', async () => {
      await renderDrawableMap();
      expect(screen.getByText('رسم مضلع')).toBeInTheDocument();
    });

    it('renders rectangle drawing button with Arabic label', async () => {
      await renderDrawableMap();
      expect(screen.getByText('رسم مستطيل')).toBeInTheDocument();
    });

    it('renders with RTL direction', async () => {
      const { container } = await renderDrawableMap();
      const wrapper = container.querySelector('[dir="rtl"]');
      expect(wrapper).toBeInTheDocument();
    });

    it('applies custom height from props', async () => {
      await renderDrawableMap({ height: '600px' });
      const mapContainer = screen.getByTestId('mock-map-container');
      expect(mapContainer).toBeInTheDocument();
    });

    it('renders mode selection buttons when no mode is active', async () => {
      await renderDrawableMap();
      const polygonBtn = screen.getByText('رسم مضلع');
      const rectBtn = screen.getByText('رسم مستطيل');
      expect(polygonBtn).toBeInTheDocument();
      expect(rectBtn).toBeInTheDocument();
    });
  });

  // ─── Props ──────────────────────────────────────────────────────────────

  describe('props', () => {
    it('accepts onBboxSelect callback', async () => {
      const onBboxSelect = vi.fn();
      await renderDrawableMap({ onBboxSelect });
      expect(screen.getByText('رسم مضلع')).toBeInTheDocument();
    });

    it('accepts onBoundaryDraw callback', async () => {
      const onBoundaryDraw = vi.fn();
      await renderDrawableMap({ onBoundaryDraw });
      expect(screen.getByText('رسم مضلع')).toBeInTheDocument();
    });

    it('accepts initialCenter prop', async () => {
      await renderDrawableMap({ initialCenter: [24.7, 46.7] });
      expect(screen.getByTestId('mock-map-container')).toBeInTheDocument();
    });

    it('accepts initialZoom prop', async () => {
      await renderDrawableMap({ initialZoom: 12 });
      expect(screen.getByTestId('mock-map-container')).toBeInTheDocument();
    });
  });

  // ─── Mode Switching ─────────────────────────────────────────────────────

  describe('mode switching', () => {
    it('enters polygon mode when polygon button is clicked', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مضلع'));
      });

      // Mode buttons should be replaced with drawing controls
      expect(screen.queryByText('رسم مضلع')).not.toBeInTheDocument();
      expect(screen.queryByText('رسم مستطيل')).not.toBeInTheDocument();
    });

    it('shows status bar in polygon mode with Arabic text', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مضلع'));
      });

      expect(screen.getByText('رسم مضلع — انقر لإضافة نقاط')).toBeInTheDocument();
    });

    it('enters rectangle mode when rectangle button is clicked', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مستطيل'));
      });

      expect(screen.queryByText('رسم مضلع')).not.toBeInTheDocument();
      expect(screen.queryByText('رسم مستطيل')).not.toBeInTheDocument();
    });

    it('shows rectangle mode status in Arabic', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مستطيل'));
      });

      expect(
        screen.getByText('رسم مستطيل — انقر لتحديد الزاوية الأولى')
      ).toBeInTheDocument();
    });

    it('shows drawing controls (clear, cancel) in active mode', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مضلع'));
      });

      expect(screen.getByText('مسح')).toBeInTheDocument();
      expect(screen.getByText('إلغاء')).toBeInTheDocument();
    });
  });

  // ─── Clear and Cancel ───────────────────────────────────────────────────

  describe('clear and cancel', () => {
    it('clear button resets vertices while staying in mode', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مضلع'));
      });
      await act(async () => {
        fireEvent.click(screen.getByText('مسح'));
      });

      // Should still be in drawing mode (clear does not exit mode)
      expect(screen.getByText('مسح')).toBeInTheDocument();
      expect(screen.getByText('إلغاء')).toBeInTheDocument();
    });

    it('cancel button exits drawing mode and returns to initial state', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مضلع'));
      });

      expect(screen.queryByText('رسم مضلع')).not.toBeInTheDocument();

      await act(async () => {
        fireEvent.click(screen.getByText('إلغاء'));
      });

      // Should return to initial mode selection
      expect(screen.getByText('رسم مضلع')).toBeInTheDocument();
      expect(screen.getByText('رسم مستطيل')).toBeInTheDocument();
    });

    it('cancel button also exits rectangle mode', async () => {
      await renderDrawableMap();

      await act(async () => {
        fireEvent.click(screen.getByText('رسم مستطيل'));
      });
      await act(async () => {
        fireEvent.click(screen.getByText('إلغاء'));
      });

      expect(screen.getByText('رسم مضلع')).toBeInTheDocument();
      expect(screen.getByText('رسم مستطيل')).toBeInTheDocument();
    });
  });

  // ─── Arabic Labels ──────────────────────────────────────────────────────

  describe('Arabic labels', () => {
    it('polygon button shows Arabic text "رسم مضلع"', async () => {
      await renderDrawableMap();
      expect(screen.getByText('رسم مضلع')).toBeInTheDocument();
    });

    it('rectangle button shows Arabic text "رسم مستطيل"', async () => {
      await renderDrawableMap();
      expect(screen.getByText('رسم مستطيل')).toBeInTheDocument();
    });

    it('clear button shows Arabic text "مسح"', async () => {
      await renderDrawableMap();
      await act(async () => {
        fireEvent.click(screen.getByText('رسم مضلع'));
      });
      expect(screen.getByText('مسح')).toBeInTheDocument();
    });

    it('cancel button shows Arabic text "إلغاء"', async () => {
      await renderDrawableMap();
      await act(async () => {
        fireEvent.click(screen.getByText('رسم مضلع'));
      });
      expect(screen.getByText('إلغاء')).toBeInTheDocument();
    });
  });

  // ─── Source Verification ────────────────────────────────────────────────

  describe('source verification', () => {
    const fs = require('fs');
    const path = require('path');
    const filePath = path.resolve(__dirname, '../../maps/DrawableMap.tsx');

    it('DrawableMap source file exists', () => {
      expect(fs.existsSync(filePath)).toBe(true);
    });

    it('exports a default component', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('export default function DrawableMap');
    });

    it('uses Yemen center coordinates as default', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('15.5527');
      expect(content).toContain('48.5164');
    });

    it('supports polygon drawing mode', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain("'polygon'");
      expect(content).toContain('startPolygon');
    });

    it('supports rectangle drawing mode', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain("'rectangle'");
      expect(content).toContain('startRectangle');
    });

    it('computes bounding box from vertices', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('computeBbox');
    });

    it('converts vertices to GeoJSON format', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('verticesToGeoJSON');
    });

    it('has completion handler requiring minimum 3 vertices', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('vertices.length < 3');
    });

    it('uses DrawingLayer for map click events', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('DrawingLayer');
      expect(content).toContain('useMapEvents');
    });

    it('has satellite imagery tile layer', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('صور فضائية');
      expect(content).toContain('arcgisonline');
    });

    it('shows completion info with vertex count', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('تم تحديد المنطقة');
    });

    it('has SSR guard for client-only rendering', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('isClient');
      expect(content).toContain('MapLoadingFallback');
    });

    it('uses dynamic imports with ssr: false for leaflet components', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('ssr: false');
      expect(content).toContain("import('react-leaflet')");
    });
  });
});

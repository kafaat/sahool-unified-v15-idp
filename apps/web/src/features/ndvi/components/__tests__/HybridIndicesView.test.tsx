/**
 * Tests for HybridIndicesView (Farmonaut-style two-index split overlay).
 * اختبارات عرض المقارنة الهجينة بين مؤشرين على خريطة واحدة.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// Mock the data hook so tests don't depend on TanStack Query / network.
vi.mock('../../hooks/useNDVI', () => ({
  useIndexMap: vi.fn((fieldId: string, indexType: string) => ({
    data: {
      fieldId,
      indexType,
      date: '2026-04-25',
      rasterUrl: `data:image/png;base64,placeholder-${indexType}`,
      bounds: [
        [15.34, 44.18],
        [15.37, 44.21],
      ] as [[number, number], [number, number]],
      colorScale: { min: -1, max: 1, stops: [] },
      simulated: true,
      dataSource: 'simulated',
    },
    isLoading: false,
    error: null,
  })),
}));

// SpectralIndexSwitcher imports lucide-react — keep the test light-weight by
// stubbing it; the swap behaviour itself is owned by the switcher's own tests.
vi.mock('../SpectralIndexSwitcher', () => ({
  SpectralIndexSwitcher: ({
    value,
    onChange,
  }: {
    value: string;
    onChange: (next: string) => void;
  }) => (
    <button
      type="button"
      data-testid={`switcher-stub-${value}`}
      onClick={() => onChange(value === 'ndvi' ? 'evi' : 'ndvi')}
    >
      {value}
    </button>
  ),
}));

import { HybridIndicesView } from '../HybridIndicesView';

describe('HybridIndicesView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders both rasters with default 50/50 split', () => {
    render(<HybridIndicesView fieldId="FIELD-1" />);
    const root = screen.getByTestId('hybrid-indices-view');
    expect(root).toBeInTheDocument();
    expect(root.getAttribute('data-split-percent')).toBe('50');
    expect(screen.getAllByRole('img').length).toBe(2);
  });

  it('honours initial indices and split percent', () => {
    render(
      <HybridIndicesView
        fieldId="FIELD-2"
        leftIndex="evi"
        rightIndex="ndre"
        initialSplitPercent={30}
      />,
    );
    expect(screen.getByTestId('hybrid-indices-view').getAttribute('data-split-percent')).toBe(
      '30',
    );
  });

  it('exposes an ARIA slider on the divider with valid range attributes', () => {
    render(<HybridIndicesView fieldId="FIELD-3" />);
    const divider = screen.getByTestId('hybrid-indices-divider');
    expect(divider).toHaveAttribute('role', 'slider');
    expect(divider).toHaveAttribute('aria-valuemin', '0');
    expect(divider).toHaveAttribute('aria-valuemax', '100');
    expect(divider).toHaveAttribute('aria-valuenow', '50');
    expect(divider).toHaveAttribute('aria-orientation', 'vertical');
    expect(divider).toHaveAttribute('tabindex', '0');
  });

  it('moves divider with arrow keys (LTR: ArrowRight increases)', () => {
    render(<HybridIndicesView fieldId="FIELD-4" language="en" />);
    const divider = screen.getByTestId('hybrid-indices-divider');
    divider.focus();

    fireEvent.keyDown(divider, { key: 'ArrowRight' });
    expect(divider).toHaveAttribute('aria-valuenow', '52');

    fireEvent.keyDown(divider, { key: 'ArrowRight', shiftKey: true });
    expect(divider).toHaveAttribute('aria-valuenow', '62');

    fireEvent.keyDown(divider, { key: 'Home' });
    expect(divider).toHaveAttribute('aria-valuenow', '0');

    fireEvent.keyDown(divider, { key: 'End' });
    expect(divider).toHaveAttribute('aria-valuenow', '100');
  });

  it('reverses arrow-key semantics in RTL', () => {
    render(<HybridIndicesView fieldId="FIELD-5" language="ar" initialSplitPercent={50} />);
    const divider = screen.getByTestId('hybrid-indices-divider');
    divider.focus();

    // In RTL, ArrowLeft visually moves divider RIGHT → percent grows
    fireEvent.keyDown(divider, { key: 'ArrowLeft' });
    expect(divider).toHaveAttribute('aria-valuenow', '52');

    fireEvent.keyDown(divider, { key: 'ArrowRight' });
    expect(divider).toHaveAttribute('aria-valuenow', '50');
  });

  it('clamps split percent to [0, 100]', () => {
    render(<HybridIndicesView fieldId="FIELD-6" initialSplitPercent={50} />);
    const divider = screen.getByTestId('hybrid-indices-divider');
    divider.focus();
    for (let i = 0; i < 60; i++) fireEvent.keyDown(divider, { key: 'ArrowLeft' });
    const v = Number(divider.getAttribute('aria-valuenow'));
    expect(v).toBeGreaterThanOrEqual(0);
    expect(v).toBeLessThanOrEqual(100);
  });

  it('renders per-side switchers and legends by default', () => {
    render(<HybridIndicesView fieldId="FIELD-7" />);
    expect(screen.getByTestId('hybrid-switcher-left')).toBeInTheDocument();
    expect(screen.getByTestId('hybrid-switcher-right')).toBeInTheDocument();
    expect(screen.getByTestId('hybrid-legend-left')).toBeInTheDocument();
    expect(screen.getByTestId('hybrid-legend-right')).toBeInTheDocument();
  });

  it('hides switchers and legends when disabled', () => {
    render(
      <HybridIndicesView fieldId="FIELD-8" showSwitchers={false} showLegends={false} />,
    );
    expect(screen.queryByTestId('hybrid-switcher-left')).not.toBeInTheDocument();
    expect(screen.queryByTestId('hybrid-legend-right')).not.toBeInTheDocument();
  });

  it('fires onIndicesChange when the switcher updates the active index', () => {
    const onIndicesChange = vi.fn();
    render(
      <HybridIndicesView
        fieldId="FIELD-9"
        leftIndex="ndvi"
        rightIndex="ndwi"
        onIndicesChange={onIndicesChange}
      />,
    );
    expect(onIndicesChange).toHaveBeenCalledWith('ndvi', 'ndwi');

    act(() => {
      fireEvent.click(screen.getByTestId('switcher-stub-ndvi'));
    });
    expect(onIndicesChange).toHaveBeenLastCalledWith('evi', 'ndwi');
  });
});

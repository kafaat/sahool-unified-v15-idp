/**
 * MultiDateSplitScreen regression tests — pins the N-panel side-by-side
 * compare view (2 / 3 / 4 / 6 panels) that supersedes SplitScreenNDVI.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import {
  MultiDateSplitScreen,
  PANEL_COUNTS,
} from '../MultiDateSplitScreen';
import type { MultiDateCompare } from '../../api';

function compare(rowCount: number): MultiDateCompare {
  const rows = Array.from({ length: rowCount }, (_, i) => {
    const value = 0.3 + i * 0.1;
    return {
      date: `2026-0${i + 1}-01`,
      value,
      delta_from_previous: i === 0 ? null : 0.1,
      status: {
        key: 'good' as const,
        en: 'Good',
        ar: 'جيد',
      },
    };
  });
  return {
    fieldId: 'field-1',
    indexName: 'ndvi',
    dates: rows.map((r) => r.date),
    rows,
    summary: {
      count_dates: rowCount,
      count_with_data: rowCount,
      min: rows[0]!.value,
      max: rows[rowCount - 1]!.value,
      overall_delta: (rowCount - 1) * 0.1,
    },
    dataSource: 'simulated',
  };
}

describe('MultiDateSplitScreen', () => {
  it('exposes the canonical 2/3/4/6 panel count set', () => {
    expect([...PANEL_COUNTS]).toEqual([2, 3, 4, 6]);
  });

  it('renders one panel per row', () => {
    const data = compare(4);
    render(<MultiDateSplitScreen data={data} />);
    const panels = screen.getByTestId('multi-date-split-panels').children;
    expect(panels).toHaveLength(4);
    expect(screen.getByTestId('multi-date-panel-2026-01-01')).toBeInTheDocument();
    expect(screen.getByTestId('multi-date-panel-2026-04-01')).toBeInTheDocument();
  });

  it('snaps non-canonical row counts to the nearest supported grid', () => {
    // 5 rows → should snap to 4 or 6 (the grid isn't strict about row fit)
    render(<MultiDateSplitScreen data={compare(5)} />);
    const label = screen.getByTestId('multi-date-split-grid').textContent || '';
    expect(label).toMatch(/(4-panel|6-panel)/);
  });

  it('renders delta arrows correctly based on sign', () => {
    const data: MultiDateCompare = {
      ...compare(3),
      rows: [
        {
          date: '2026-01-01',
          value: 0.5,
          delta_from_previous: null,
          status: { key: 'good', en: 'Good', ar: 'جيد' },
        },
        {
          date: '2026-02-01',
          value: 0.7,
          delta_from_previous: 0.2,
          status: { key: 'excellent', en: 'Excellent', ar: 'ممتاز' },
        },
        {
          date: '2026-03-01',
          value: 0.3,
          delta_from_previous: -0.4,
          status: { key: 'moderate', en: 'Moderate', ar: 'متوسط' },
        },
      ],
    };
    render(<MultiDateSplitScreen data={data} />);
    // Jan panel has no previous, so it shows '—'
    expect(screen.getByTestId('multi-date-panel-2026-01-01').textContent).toContain('—');
    // Feb is an improvement, must show ▲
    expect(screen.getByTestId('multi-date-panel-2026-02-01').textContent).toContain('▲');
    // Mar is a decline, must show ▼
    expect(screen.getByTestId('multi-date-panel-2026-03-01').textContent).toContain('▼');
  });

  it('renders summary footer when overall delta is present', () => {
    render(<MultiDateSplitScreen data={compare(4)} />);
    const summary = screen.getByTestId('multi-date-split-summary');
    expect(summary.textContent).toMatch(/Range/);
    expect(summary.textContent).toMatch(/Overall/);
    expect(summary.textContent).toMatch(/المدى/);
  });

  it('shows loading/error/empty states', () => {
    const { rerender } = render(<MultiDateSplitScreen data={undefined} loading />);
    expect(screen.getByTestId('multi-date-split-loading')).toBeInTheDocument();

    rerender(<MultiDateSplitScreen data={undefined} error={new Error('boom')} />);
    expect(screen.getByTestId('multi-date-split-error').textContent).toMatch(/boom/);

    rerender(<MultiDateSplitScreen data={compare(0)} />);
    // 0 rows → empty state
    expect(screen.getByTestId('multi-date-split-empty')).toBeInTheDocument();
  });

  it('treats a 1-row payload as empty (copilot review round 2)', () => {
    // A lone row can't render a "compare" view — the empty-state copy
    // asks for "at least 2 dates", so a single panel would contradict
    // the message. Regression pin: rows.length < 2 → empty state.
    render(<MultiDateSplitScreen data={compare(1)} />);
    expect(screen.getByTestId('multi-date-split-empty')).toBeInTheDocument();
    expect(screen.queryByTestId('multi-date-split-panels')).not.toBeInTheDocument();
  });

  it('tints panel backgrounds using the supplied colorScale', () => {
    const colorScale = { min: 0, max: 1, colors: ['#000000', '#ffffff'] };
    render(<MultiDateSplitScreen data={compare(2)} colorScale={colorScale} />);
    const panel = screen.getByTestId('multi-date-panel-2026-01-01');
    const banner = panel.querySelector('div') as HTMLElement;
    // ratio 0.3 / 1 → floor(0.3 * 2) = 0 → colors[0] = '#000000'
    expect(banner?.style.backgroundColor).toMatch(/rgb\(0, 0, 0\)/);
  });
});

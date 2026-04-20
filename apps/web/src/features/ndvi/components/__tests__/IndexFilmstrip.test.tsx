/**
 * IndexFilmstrip regression tests — pins the per-date thumbnail carousel
 * that drives the "look at 20 acquisitions at once" UX.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { IndexFilmstrip } from '../IndexFilmstrip';
import type { IndexFilmstripData as FilmstripData } from '../../api';

const filmstrip: FilmstripData = {
  fieldId: 'field-1',
  indexName: 'ndre',
  stepDays: 7,
  colorScale: {
    min: -1,
    max: 1,
    colors: ['#4B0082', '#FF0000', '#FFAA00', '#FFFF00', '#00CC00', '#006400'],
  },
  label: { en: 'Red-Edge', ar: 'الحافة الحمراء' },
  frames: [
    {
      date: '2026-03-01',
      rasterUrl: 'sim://ndre/2026-03-01',
      value: 0.3,
      status: { key: 'moderate', en: 'Moderate', ar: 'متوسط' },
      cloudCover: 12.5,
    },
    {
      date: '2026-03-08',
      rasterUrl: 'sim://ndre/2026-03-08',
      value: 0.52,
      status: { key: 'good', en: 'Good', ar: 'جيد' },
      cloudCover: 3.0,
    },
    {
      date: '2026-03-15',
      rasterUrl: 'sim://ndre/2026-03-15',
      value: null,
      status: { key: 'unknown', en: 'Unknown', ar: 'غير معروف' },
    },
  ],
  count: 3,
  dataSource: 'simulated',
};

describe('IndexFilmstrip', () => {
  it('renders a tile per frame with formatted value', () => {
    render(<IndexFilmstrip data={filmstrip} />);
    expect(screen.getByTestId('index-filmstrip-frame-2026-03-01')).toBeInTheDocument();
    expect(screen.getByTestId('index-filmstrip-frame-2026-03-08').textContent).toContain(
      '0.52'
    );
    // Missing values render as an em dash so users know the tile failed
    expect(screen.getByTestId('index-filmstrip-frame-2026-03-15').textContent).toContain(
      '—'
    );
  });

  it('highlights the active date with aria-pressed=true', () => {
    render(<IndexFilmstrip data={filmstrip} activeDate="2026-03-08" />);
    const active = screen
      .getByTestId('index-filmstrip-frame-2026-03-08')
      .querySelector('button');
    const inactive = screen
      .getByTestId('index-filmstrip-frame-2026-03-01')
      .querySelector('button');
    expect(active).toHaveAttribute('aria-pressed', 'true');
    expect(inactive).toHaveAttribute('aria-pressed', 'false');
  });

  it('emits onSelectDate when a non-active tile is clicked', () => {
    const onSelectDate = vi.fn();
    render(
      <IndexFilmstrip
        data={filmstrip}
        activeDate="2026-03-01"
        onSelectDate={onSelectDate}
      />
    );
    fireEvent.click(
      screen
        .getByTestId('index-filmstrip-frame-2026-03-08')
        .querySelector('button')!
    );
    expect(onSelectDate).toHaveBeenCalledWith('2026-03-08');
  });

  it('does not re-emit for the already-active date', () => {
    const onSelectDate = vi.fn();
    render(
      <IndexFilmstrip
        data={filmstrip}
        activeDate="2026-03-08"
        onSelectDate={onSelectDate}
      />
    );
    fireEvent.click(
      screen
        .getByTestId('index-filmstrip-frame-2026-03-08')
        .querySelector('button')!
    );
    expect(onSelectDate).not.toHaveBeenCalled();
  });

  it('renders cloud cover % when present', () => {
    render(<IndexFilmstrip data={filmstrip} />);
    expect(screen.getByTestId('index-filmstrip-frame-2026-03-01').textContent).toMatch(
      /13%/
    );
  });

  it('shows loading state', () => {
    render(<IndexFilmstrip data={undefined} loading />);
    expect(screen.getByTestId('index-filmstrip-loading')).toBeInTheDocument();
  });

  it('shows error state with message', () => {
    render(<IndexFilmstrip data={undefined} error={new Error('boom')} />);
    expect(screen.getByTestId('index-filmstrip-error').textContent).toMatch(/boom/);
  });

  it('shows empty state when frames is empty', () => {
    render(<IndexFilmstrip data={{ ...filmstrip, frames: [], count: 0 }} />);
    expect(screen.getByTestId('index-filmstrip-empty')).toBeInTheDocument();
  });

  it('renders bilingual header (EN + AR)', () => {
    render(<IndexFilmstrip data={filmstrip} />);
    const section = screen.getByTestId('index-filmstrip');
    expect(section.textContent).toContain('Red-Edge');
    expect(section.textContent).toMatch(/الحافة الحمراء/);
    expect(section.textContent).toMatch(/every 7 day/);
  });
});

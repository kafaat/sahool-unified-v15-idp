/**
 * PixelInspectorPopup regression tests — pins the click-a-pixel popup
 * that gives EOSDA/OneSoil-parity UX.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PixelInspectorPopup } from '../PixelInspectorPopup';
import type { PixelInspection } from '../../api';

const fullInspection: PixelInspection = {
  fieldId: 'field-1',
  location: { latitude: 24.7136, longitude: 46.6753 },
  date: '2026-04-12',
  satellite: 'sentinel-2',
  indices: {
    ndvi: 0.72,
    ndre: 0.43,
    ndwi: 0.12,
    evi: 0.65,
    savi: 0.58,
    lai: 3.8,
    gndvi: 0.55,
    mcari: 0.8,
    pri: 0.02,
    fpar: 0.71,
    fapar: 0.68,
    bsi: -0.2,
  },
  mappable: ['ndvi', 'ndre', 'ndwi', 'evi', 'savi', 'lai'],
  dataSource: 'simulated',
};

describe('PixelInspectorPopup', () => {
  it('renders nothing catastrophic when data is undefined', () => {
    render(<PixelInspectorPopup data={undefined} />);
    expect(screen.getByTestId('pixel-inspector')).toBeInTheDocument();
    expect(screen.queryByTestId('pixel-inspector-body')).not.toBeInTheDocument();
  });

  it('shows loading state while awaiting data', () => {
    render(<PixelInspectorPopup data={undefined} loading />);
    expect(screen.getByText(/Reading pixel/i)).toBeInTheDocument();
  });

  it('shows error state with the error message', () => {
    render(
      <PixelInspectorPopup
        data={undefined}
        error={new Error('503 from tile server')}
      />
    );
    const alert = screen.getByRole('alert');
    expect(alert.textContent).toContain('503 from tile server');
  });

  it('renders lat/lon and ISO date in the header', () => {
    render(<PixelInspectorPopup data={fullInspection} />);
    expect(screen.getByText(/24\.71360/)).toBeInTheDocument();
    expect(screen.getByText(/46\.67530/)).toBeInTheDocument();
    expect(screen.getByText(/2026-04-12/)).toBeInTheDocument();
  });

  it('renders every supplied index value', () => {
    render(<PixelInspectorPopup data={fullInspection} />);
    expect(screen.getByTestId('pixel-index-ndvi').textContent).toContain('0.720');
    expect(screen.getByTestId('pixel-index-ndre').textContent).toContain('0.430');
    expect(screen.getByTestId('pixel-index-lai').textContent).toContain('3.80');
    expect(screen.getByTestId('pixel-index-bsi').textContent).toContain('-0.200');
  });

  it('marks mappable indices visually (● bullet) so users know which can overlay', () => {
    render(<PixelInspectorPopup data={fullInspection} />);
    // All 6 mappable indices should carry the bullet marker
    for (const key of ['ndvi', 'ndre', 'ndwi', 'evi', 'savi', 'lai']) {
      const row = screen.getByTestId(`pixel-index-${key}`);
      expect(row.textContent).toMatch(/●/);
    }
    // Non-mappable indices don't carry it
    const bsi = screen.getByTestId('pixel-index-bsi');
    // bsi is non-mappable; title dt should not end with bullet
    expect(bsi.querySelector('dt')?.textContent || '').not.toMatch(/●/);
  });

  it('calls onClose when the close button is clicked', () => {
    const onClose = vi.fn();
    render(<PixelInspectorPopup data={fullInspection} onClose={onClose} />);
    fireEvent.click(screen.getByTestId('pixel-inspector-close'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('renders bilingual section headers', () => {
    render(<PixelInspectorPopup data={fullInspection} />);
    // English + Arabic section labels
    expect(screen.getByText('Core')).toBeInTheDocument();
    expect(screen.getByText('الأساسية')).toBeInTheDocument();
    expect(screen.getByText('Water')).toBeInTheDocument();
    expect(screen.getByText('المياه')).toBeInTheDocument();
  });

  it('skips sections whose indices are all absent from the payload', () => {
    const partial: PixelInspection = {
      ...fullInspection,
      indices: { ndvi: 0.5 }, // only Core has anything
    };
    render(<PixelInspectorPopup data={partial} />);
    // Water section should be hidden because none of its indices are present
    expect(screen.queryByText('Water')).not.toBeInTheDocument();
    // Core still renders
    expect(screen.getByText('Core')).toBeInTheDocument();
  });
});

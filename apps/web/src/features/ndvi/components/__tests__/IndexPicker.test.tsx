/**
 * IndexPicker regression tests — pins the EOSDA/OneSoil "pick your
 * index" UX. Covers: 6-index coverage, bilingual labels, active state,
 * keyboard/aria semantics, disabled behaviour, and click-to-change.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { IndexPicker, MAPPABLE_INDICES } from '../IndexPicker';

describe('IndexPicker', () => {
  it('renders all 6 mappable indices as radio chips', () => {
    render(<IndexPicker value="ndvi" onChange={() => {}} />);
    expect(screen.getAllByRole('radio')).toHaveLength(6);
    for (const idx of MAPPABLE_INDICES) {
      expect(screen.getByTestId(`index-picker-${idx.key}`)).toBeInTheDocument();
    }
  });

  it('marks the active index with aria-checked=true and the others false', () => {
    render(<IndexPicker value="ndre" onChange={() => {}} />);
    const ndreChip = screen.getByTestId('index-picker-ndre');
    const ndviChip = screen.getByTestId('index-picker-ndvi');
    expect(ndreChip).toHaveAttribute('aria-checked', 'true');
    expect(ndviChip).toHaveAttribute('aria-checked', 'false');
  });

  it('shows bilingual labels by default (EN + AR)', () => {
    render(<IndexPicker value="ndvi" onChange={() => {}} />);
    // NDVI chip shows both the English code and the Arabic label
    const ndviChip = screen.getByTestId('index-picker-ndvi');
    expect(ndviChip.textContent).toContain('NDVI');
    expect(ndviChip.textContent).toMatch(/كثافة/);
  });

  it('hides Arabic labels when bilingual=false', () => {
    render(<IndexPicker value="ndvi" onChange={() => {}} bilingual={false} />);
    const ndviChip = screen.getByTestId('index-picker-ndvi');
    expect(ndviChip.textContent).not.toMatch(/كثافة/);
    expect(ndviChip.textContent).toContain('NDVI');
  });

  it('calls onChange with the selected index key on click', () => {
    const onChange = vi.fn();
    render(<IndexPicker value="ndvi" onChange={onChange} />);
    fireEvent.click(screen.getByTestId('index-picker-ndre'));
    expect(onChange).toHaveBeenCalledWith('ndre');
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  it('does not fire onChange when clicking the already-active chip', () => {
    const onChange = vi.fn();
    render(<IndexPicker value="ndvi" onChange={onChange} />);
    fireEvent.click(screen.getByTestId('index-picker-ndvi'));
    expect(onChange).not.toHaveBeenCalled();
  });

  it('suppresses onChange when disabled', () => {
    const onChange = vi.fn();
    render(<IndexPicker value="ndvi" onChange={onChange} disabled />);
    fireEvent.click(screen.getByTestId('index-picker-ndre'));
    expect(onChange).not.toHaveBeenCalled();
  });

  it('exposes role=radiogroup with a label for screen readers', () => {
    render(<IndexPicker value="ndvi" onChange={() => {}} />);
    const group = screen.getByRole('radiogroup');
    expect(group).toHaveAttribute('aria-label', 'Vegetation index selector');
  });

  it('MAPPABLE_INDICES covers exactly the 6 indices the backend renders', () => {
    // Pin the contract: this list MUST match the backend's
    // `MAPPABLE_INDICES` dict in apps/services/vegetation-analysis-service/
    // src/map_registry.py. Adding a 7th here without the backend
    // breaks with a 400 at runtime.
    expect(new Set(MAPPABLE_INDICES.map((i) => i.key))).toEqual(
      new Set(['ndvi', 'ndre', 'ndwi', 'evi', 'savi', 'lai'])
    );
  });
});

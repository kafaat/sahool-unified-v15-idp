/**
 * IndexTimeSlider regression tests — pins the unified time-scrubber
 * UX (EOSDA pattern: one slider controls tile layer + legend +
 * inspector).
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { IndexTimeSlider } from '../IndexTimeSlider';

const DATES = ['2026-01-05', '2026-02-10', '2026-03-20', '2026-04-12'];

describe('IndexTimeSlider', () => {
  it('renders an empty state with a helpful bilingual hint', () => {
    render(<IndexTimeSlider dates={[]} value="" onChange={() => {}} />);
    const empty = screen.getByTestId('index-time-slider-empty');
    expect(empty.textContent).toMatch(/No acquisitions/i);
    expect(empty.textContent).toMatch(/لا توجد بيانات/);
  });

  it('renders prev/next buttons + a native range input', () => {
    render(<IndexTimeSlider dates={DATES} value={DATES[2]!} onChange={() => {}} />);
    expect(screen.getByTestId('index-time-prev')).toBeInTheDocument();
    expect(screen.getByTestId('index-time-next')).toBeInTheDocument();
    const range = screen.getByTestId('index-time-range') as HTMLInputElement;
    expect(range.type).toBe('range');
    expect(range.max).toBe('3');
    expect(range.value).toBe('2');
  });

  it('disables previous at the first date and next at the last date', () => {
    const { rerender } = render(
      <IndexTimeSlider dates={DATES} value={DATES[0]!} onChange={() => {}} />
    );
    expect(screen.getByTestId('index-time-prev')).toBeDisabled();
    expect(screen.getByTestId('index-time-next')).not.toBeDisabled();

    rerender(<IndexTimeSlider dates={DATES} value={DATES[3]!} onChange={() => {}} />);
    expect(screen.getByTestId('index-time-prev')).not.toBeDisabled();
    expect(screen.getByTestId('index-time-next')).toBeDisabled();
  });

  it('moves forward through dates on next click', () => {
    const onChange = vi.fn();
    render(<IndexTimeSlider dates={DATES} value={DATES[1]!} onChange={onChange} />);
    fireEvent.click(screen.getByTestId('index-time-next'));
    expect(onChange).toHaveBeenCalledWith(DATES[2]);
  });

  it('moves backward through dates on prev click', () => {
    const onChange = vi.fn();
    render(<IndexTimeSlider dates={DATES} value={DATES[2]!} onChange={onChange} />);
    fireEvent.click(screen.getByTestId('index-time-prev'));
    expect(onChange).toHaveBeenCalledWith(DATES[1]);
  });

  it('fires onChange when the range input is dragged', () => {
    const onChange = vi.fn();
    render(<IndexTimeSlider dates={DATES} value={DATES[0]!} onChange={onChange} />);
    fireEvent.change(screen.getByTestId('index-time-range'), { target: { value: '3' } });
    expect(onChange).toHaveBeenCalledWith(DATES[3]);
  });

  it('does not re-fire onChange when the range is set to the current index', () => {
    const onChange = vi.fn();
    render(<IndexTimeSlider dates={DATES} value={DATES[1]!} onChange={onChange} />);
    fireEvent.change(screen.getByTestId('index-time-range'), { target: { value: '1' } });
    expect(onChange).not.toHaveBeenCalled();
  });

  it('exposes aria-valuemin/max/now/text for screen readers', () => {
    render(<IndexTimeSlider dates={DATES} value={DATES[2]!} onChange={() => {}} />);
    const range = screen.getByTestId('index-time-range');
    expect(range).toHaveAttribute('aria-valuemin', '0');
    expect(range).toHaveAttribute('aria-valuemax', '3');
    expect(range).toHaveAttribute('aria-valuenow', '2');
    expect(range).toHaveAttribute('aria-valuetext', DATES[2]!);
  });

  it('sorts incoming dates chronologically (resilient to unordered props)', () => {
    const onChange = vi.fn();
    const shuffled = [DATES[2]!, DATES[0]!, DATES[3]!, DATES[1]!];
    render(<IndexTimeSlider dates={shuffled} value={DATES[0]!} onChange={onChange} />);
    // "Next" from the earliest date must go to the 2nd earliest, not to
    // whatever's next in the input array
    fireEvent.click(screen.getByTestId('index-time-next'));
    expect(onChange).toHaveBeenCalledWith(DATES[1]);
  });

  it('suppresses all navigation when disabled', () => {
    const onChange = vi.fn();
    render(
      <IndexTimeSlider dates={DATES} value={DATES[1]!} onChange={onChange} disabled />
    );
    fireEvent.click(screen.getByTestId('index-time-next'));
    fireEvent.click(screen.getByTestId('index-time-prev'));
    fireEvent.change(screen.getByTestId('index-time-range'), { target: { value: '3' } });
    expect(onChange).not.toHaveBeenCalled();
  });
});

/**
 * IntervalStepSelector regression tests — pins the "every N days"
 * cadence picker that drives filmstrip + composite + multi-compare.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import {
  IntervalStepSelector,
  INTERVAL_PRESETS,
} from '../IntervalStepSelector';

describe('IntervalStepSelector', () => {
  it('renders the 4 canonical presets (3 / 7 / 14 / 30 days)', () => {
    render(<IntervalStepSelector value={7} onChange={() => {}} />);
    for (const preset of INTERVAL_PRESETS) {
      expect(
        screen.getByTestId(`interval-step-${preset.days}`)
      ).toBeInTheDocument();
    }
    expect(new Set(INTERVAL_PRESETS.map((p) => p.days))).toEqual(
      new Set([3, 7, 14, 30])
    );
  });

  it('marks the active preset with aria-checked=true', () => {
    render(<IntervalStepSelector value={14} onChange={() => {}} />);
    expect(screen.getByTestId('interval-step-14')).toHaveAttribute(
      'aria-checked',
      'true'
    );
    expect(screen.getByTestId('interval-step-7')).toHaveAttribute(
      'aria-checked',
      'false'
    );
  });

  it('fires onChange with the selected step on click', () => {
    const onChange = vi.fn();
    render(<IntervalStepSelector value={7} onChange={onChange} />);
    fireEvent.click(screen.getByTestId('interval-step-30'));
    expect(onChange).toHaveBeenCalledWith(30);
  });

  it('does not fire onChange when the active preset is clicked', () => {
    const onChange = vi.fn();
    render(<IntervalStepSelector value={7} onChange={onChange} />);
    fireEvent.click(screen.getByTestId('interval-step-7'));
    expect(onChange).not.toHaveBeenCalled();
  });

  it('suppresses onChange when disabled', () => {
    const onChange = vi.fn();
    render(<IntervalStepSelector value={7} onChange={onChange} disabled />);
    fireEvent.click(screen.getByTestId('interval-step-3'));
    expect(onChange).not.toHaveBeenCalled();
  });

  it('renders Arabic copy by default and hides it when bilingual=false', () => {
    const { rerender } = render(
      <IntervalStepSelector value={7} onChange={() => {}} />
    );
    expect(screen.getByTestId('interval-step-30').textContent).toMatch(/شهر/);

    rerender(
      <IntervalStepSelector value={7} onChange={() => {}} bilingual={false} />
    );
    expect(screen.getByTestId('interval-step-30').textContent).not.toMatch(
      /شهر/
    );
  });

  it('exposes role=radiogroup with an aria-label', () => {
    render(<IntervalStepSelector value={7} onChange={() => {}} />);
    const group = screen.getByRole('radiogroup');
    expect(group).toHaveAttribute('aria-label', 'Interval step');
  });
});

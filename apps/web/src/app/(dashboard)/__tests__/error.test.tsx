/**
 * Tests for the dashboard route error boundary.
 *
 * Reproduces the symptom seen in production where a Leaflet error
 * ("Map container is already initialized") thrown by /sensors or
 * /equipment kept showing on /satellite because Next.js error
 * boundaries do not auto-reset on URL change.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// We need to control the value of usePathname between renders, so override
// the global setup mock with a stateful one.
let mockPathname = '/sensors';
const pushMock = vi.fn();

vi.mock('next/navigation', () => ({
  usePathname: () => mockPathname,
  useRouter: () => ({
    push: pushMock,
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

vi.mock('@/lib/logger', () => ({
  logger: { error: vi.fn(), warn: vi.fn(), info: vi.fn(), debug: vi.fn() },
}));

import DashboardError from '../error';

describe('DashboardError boundary', () => {
  beforeEach(() => {
    mockPathname = '/sensors';
    pushMock.mockReset();
  });

  it('renders the bilingual error UI with the underlying message', () => {
    render(
      <DashboardError
        error={new Error('Map container is already initialized.')}
        reset={vi.fn()}
      />
    );

    expect(screen.getByText('حدث خطأ في لوحة التحكم')).toBeInTheDocument();
    expect(screen.getByText('Dashboard Error')).toBeInTheDocument();
    expect(
      screen.getByText('Map container is already initialized.')
    ).toBeInTheDocument();
  });

  it('calls reset when the retry button is clicked', () => {
    const reset = vi.fn();
    render(<DashboardError error={new Error('boom')} reset={reset} />);

    fireEvent.click(screen.getByText('إعادة المحاولة'));
    expect(reset).toHaveBeenCalledTimes(1);
  });

  it('does NOT auto-reset on the first render (same pathname)', () => {
    const reset = vi.fn();
    render(<DashboardError error={new Error('boom')} reset={reset} />);

    expect(reset).not.toHaveBeenCalled();
  });

  it('auto-resets when the pathname changes (navigation away from broken page)', () => {
    const reset = vi.fn();
    const { rerender } = render(
      <DashboardError error={new Error('boom')} reset={reset} />
    );

    expect(reset).not.toHaveBeenCalled();

    // Simulate user navigating to a different route while error UI is mounted.
    mockPathname = '/satellite';
    rerender(<DashboardError error={new Error('boom')} reset={reset} />);

    expect(reset).toHaveBeenCalledTimes(1);
  });

  it('does not loop reset() when pathname stays the same across re-renders', () => {
    const reset = vi.fn();
    const { rerender } = render(
      <DashboardError error={new Error('boom')} reset={reset} />
    );

    rerender(<DashboardError error={new Error('boom')} reset={reset} />);
    rerender(<DashboardError error={new Error('boom')} reset={reset} />);

    expect(reset).not.toHaveBeenCalled();
  });
});

import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';

import type { Field } from '../../types';

// Mock the data hook BEFORE importing FieldsList so the component picks it up.
vi.mock('../../hooks/useFields', () => ({
  useFields: vi.fn(),
}));

import { FieldsList } from '../FieldsList';
import { useFields } from '../../hooks/useFields';

const mockUseFields = useFields as unknown as ReturnType<typeof vi.fn>;

function makeField(overrides: Partial<Field> = {}): Field {
  return {
    id: 'field-1',
    name: 'Field 1',
    nameAr: 'حقل 1',
    area: 10,
    status: 'active',
    ...overrides,
  } as Field;
}

describe('FieldsList — highlightedFieldId', () => {
  beforeEach(() => {
    mockUseFields.mockReset();
    // jsdom does not implement scrollIntoView; stub it so the component
    // can call it without throwing.
    Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
      configurable: true,
      value: vi.fn(),
    });
  });

  it('marks the matching card with aria-current and the highlighted test id', async () => {
    mockUseFields.mockReturnValue({
      data: [
        makeField({ id: 'a', name: 'A' }),
        makeField({ id: 'b', name: 'B' }),
        makeField({ id: 'c', name: 'C' }),
      ],
      isLoading: false,
    });

    render(<FieldsList highlightedFieldId="b" />);

    const highlighted = await screen.findByTestId('field-card-highlighted');
    expect(highlighted).toBeInTheDocument();
    expect(highlighted).toHaveAttribute('aria-current', 'true');
    // The highlighted wrapper should contain the matching field's name.
    expect(highlighted.textContent).toContain('B');
  });

  it('calls onMissingHighlight when the stored id is not in the loaded list', async () => {
    mockUseFields.mockReturnValue({
      data: [makeField({ id: 'a' }), makeField({ id: 'b' })],
      isLoading: false,
    });
    const onMissingHighlight = vi.fn();

    render(
      <FieldsList
        highlightedFieldId="deleted-field"
        onMissingHighlight={onMissingHighlight}
      />,
    );

    await waitFor(() => {
      expect(onMissingHighlight).toHaveBeenCalledWith('deleted-field');
    });
    // No highlighted card should be rendered.
    expect(screen.queryByTestId('field-card-highlighted')).toBeNull();
  });

  it('does not act while the list is still loading', () => {
    mockUseFields.mockReturnValue({ data: undefined, isLoading: true });
    const onMissingHighlight = vi.fn();

    render(
      <FieldsList
        highlightedFieldId="anything"
        onMissingHighlight={onMissingHighlight}
      />,
    );

    expect(onMissingHighlight).not.toHaveBeenCalled();
    expect(screen.queryByTestId('field-card-highlighted')).toBeNull();
  });

  it('does nothing when highlightedFieldId is null', () => {
    mockUseFields.mockReturnValue({
      data: [makeField({ id: 'a' })],
      isLoading: false,
    });
    const onMissingHighlight = vi.fn();

    render(
      <FieldsList
        highlightedFieldId={null}
        onMissingHighlight={onMissingHighlight}
      />,
    );

    expect(onMissingHighlight).not.toHaveBeenCalled();
    expect(screen.queryByTestId('field-card-highlighted')).toBeNull();
  });
});

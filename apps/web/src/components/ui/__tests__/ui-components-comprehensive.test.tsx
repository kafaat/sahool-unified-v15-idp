/**
 * Comprehensive UI Component Tests - Extended Coverage
 * اختبارات شاملة إضافية لمكونات واجهة المستخدم
 *
 * Tests cover accessibility, edge cases, and bilingual support
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import { Button } from '../button';
import { Badge } from '../badge';
import { Input } from '../input';

// ═══════════════════════════════════════════════════════════════════════════
// Button - Accessibility & Edge Cases
// ═══════════════════════════════════════════════════════════════════════════

describe('Button - Accessibility', () => {
  it('should have aria-disabled when loading', () => {
    render(<Button isLoading>Save</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'true');
  });

  it('should have aria-disabled when disabled', () => {
    render(<Button disabled>Save</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-disabled', 'true');
  });

  it('should not have aria-busy when not loading', () => {
    render(<Button>Save</Button>);
    expect(screen.getByRole('button')).not.toHaveAttribute('aria-busy');
  });

  it('should show spinner svg when loading', () => {
    const { container } = render(<Button isLoading>Save</Button>);
    expect(container.querySelector('svg.animate-spin')).toBeInTheDocument();
  });

  it('should hide children text visually when loading', () => {
    render(<Button isLoading>Save</Button>);
    const hiddenText = screen.getByText('Save');
    expect(hiddenText).toHaveAttribute('aria-hidden', 'true');
  });

  it('should show bilingual loading text for screen readers', () => {
    render(
      <Button isLoading loadingText="Saving" loadingTextAr="جاري الحفظ">
        Save
      </Button>
    );
    const srText = screen.getByText(/جاري الحفظ - Saving/);
    expect(srText).toHaveClass('sr-only');
  });

  it('should default loading text to Arabic and English', () => {
    render(<Button isLoading>Save</Button>);
    expect(screen.getByText(/جاري التحميل - Loading/)).toBeInTheDocument();
  });
});

describe('Button - Icon Rendering', () => {
  it('should not render icon containers when no icons', () => {
    const { container } = render(<Button>Text Only</Button>);
    expect(container.querySelectorAll('[aria-hidden]')).toHaveLength(0);
  });

  it('should render both left and right icons', () => {
    render(
      <Button
        leftIcon={<span data-testid="left">L</span>}
        rightIcon={<span data-testid="right">R</span>}
      >
        Both Icons
      </Button>
    );
    expect(screen.getByTestId('left')).toBeInTheDocument();
    expect(screen.getByTestId('right')).toBeInTheDocument();
  });

  it('should not render icons when loading', () => {
    render(
      <Button
        isLoading
        leftIcon={<span data-testid="left">L</span>}
        rightIcon={<span data-testid="right">R</span>}
      >
        Loading
      </Button>
    );
    expect(screen.queryByTestId('left')).not.toBeInTheDocument();
    expect(screen.queryByTestId('right')).not.toBeInTheDocument();
  });
});

describe('Button - Size Combinations', () => {
  it('should render all size variants without error', () => {
    const sizes = ['sm', 'md', 'lg'] as const;
    sizes.forEach((size) => {
      const { unmount } = render(<Button size={size}>Size {size}</Button>);
      expect(screen.getByRole('button')).toBeInTheDocument();
      unmount();
    });
  });

  it('should render all variant combinations without error', () => {
    const variants = ['primary', 'secondary', 'outline', 'ghost', 'danger'] as const;
    variants.forEach((variant) => {
      const { unmount } = render(<Button variant={variant}>Variant {variant}</Button>);
      expect(screen.getByRole('button')).toBeInTheDocument();
      unmount();
    });
  });
});

describe('Button - Event Handling', () => {
  it('should not fire onClick when loading', () => {
    const onClick = vi.fn();
    render(
      <Button onClick={onClick} isLoading>
        Loading
      </Button>
    );
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('should pass through onFocus', () => {
    const onFocus = vi.fn();
    render(<Button onFocus={onFocus}>Focus Me</Button>);
    fireEvent.focus(screen.getByRole('button'));
    expect(onFocus).toHaveBeenCalledTimes(1);
  });

  it('should pass through onBlur', () => {
    const onBlur = vi.fn();
    render(<Button onBlur={onBlur}>Blur Me</Button>);
    fireEvent.blur(screen.getByRole('button'));
    expect(onBlur).toHaveBeenCalledTimes(1);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Badge - Extended Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Badge - Extended', () => {
  it('should render all size variants', () => {
    const sizes = ['sm', 'md', 'lg'] as const;
    sizes.forEach((size) => {
      const { unmount } = render(<Badge size={size}>{size}</Badge>);
      expect(screen.getByText(size)).toBeInTheDocument();
      unmount();
    });
  });

  it('should render all color variants', () => {
    const variants = ['default', 'success', 'warning', 'danger', 'info'] as const;
    variants.forEach((variant) => {
      const { unmount } = render(<Badge variant={variant}>{variant}</Badge>);
      expect(screen.getByText(variant)).toBeInTheDocument();
      unmount();
    });
  });

  it('should render Arabic text correctly', () => {
    render(<Badge variant="success">نشط</Badge>);
    expect(screen.getByText('نشط')).toBeInTheDocument();
  });

  it('should render with inline-flex', () => {
    render(<Badge>Flex Badge</Badge>);
    expect(screen.getByText('Flex Badge').className).toMatch(/inline-flex/);
  });

  it('should render with font-medium', () => {
    render(<Badge>Medium</Badge>);
    expect(screen.getByText('Medium').className).toMatch(/font-medium/);
  });

  it('should render with border', () => {
    render(<Badge>Bordered</Badge>);
    expect(screen.getByText('Bordered').className).toMatch(/border/);
  });

  it('should pass through data attributes', () => {
    render(<Badge data-testid="badge-test">Data Attr</Badge>);
    expect(screen.getByTestId('badge-test')).toBeInTheDocument();
  });

  it('should have displayName', () => {
    expect(Badge.displayName).toBe('Badge');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Input - Accessibility & Edge Cases
// ═══════════════════════════════════════════════════════════════════════════

describe('Input - Accessibility', () => {
  it('should link label to input via htmlFor', () => {
    render(<Input label="Email" id="email-input" />);
    const label = screen.getByText('Email');
    expect(label.closest('label')).toHaveAttribute('for', 'email-input');
  });

  it('should generate unique ID when id prop not provided', () => {
    render(<Input label="Name" />);
    const input = screen.getByRole('textbox');
    expect(input.id).toBeTruthy();
    expect(input.id.length).toBeGreaterThan(0);
  });

  it('should have aria-invalid only when error exists', () => {
    const { rerender } = render(<Input />);
    expect(screen.getByRole('textbox')).not.toHaveAttribute('aria-invalid');

    rerender(<Input error="Error" />);
    expect(screen.getByRole('textbox')).toHaveAttribute('aria-invalid', 'true');
  });

  it('should have aria-describedby pointing to error element', () => {
    render(<Input id="test" error="Field is required" />);
    const input = screen.getByRole('textbox');
    const describedBy = input.getAttribute('aria-describedby');
    expect(describedBy).toBe('test-error');
  });

  it('should have aria-describedby pointing to helper element', () => {
    render(<Input id="test" helperText="Enter your name" />);
    const input = screen.getByRole('textbox');
    const describedBy = input.getAttribute('aria-describedby');
    expect(describedBy).toBe('test-helper');
  });

  it('should not have aria-describedby when neither error nor helper', () => {
    render(<Input />);
    const input = screen.getByRole('textbox');
    expect(input.getAttribute('aria-describedby')).toBeNull();
  });

  it('should show error with role=alert', () => {
    render(<Input error="خطأ في الإدخال" />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent('خطأ في الإدخال');
  });
});

describe('Input - Bilingual Labels', () => {
  it('should show Arabic label with bullet separator when both provided', () => {
    render(<Input label="Email" labelAr="البريد الإلكتروني" />);
    expect(screen.getByText('البريد الإلكتروني')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('•')).toBeInTheDocument();
  });

  it('should show only Arabic label when no English provided', () => {
    render(<Input labelAr="الاسم" />);
    expect(screen.getByText('الاسم')).toBeInTheDocument();
    expect(screen.queryByText('•')).not.toBeInTheDocument();
  });

  it('should show only English label when no Arabic provided', () => {
    render(<Input label="Name" />);
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.queryByText('•')).not.toBeInTheDocument();
  });

  it('should not show label area when neither label provided', () => {
    const { container } = render(<Input />);
    expect(container.querySelector('label')).not.toBeInTheDocument();
  });
});

describe('Input - Icon Support', () => {
  it('should apply padding for left icon', () => {
    render(<Input leftIcon={<span>L</span>} />);
    expect(screen.getByRole('textbox').className).toMatch(/ps-10/);
  });

  it('should apply padding for right icon', () => {
    render(<Input rightIcon={<span>R</span>} />);
    expect(screen.getByRole('textbox').className).toMatch(/pe-10/);
  });

  it('should apply both paddings when both icons present', () => {
    render(<Input leftIcon={<span>L</span>} rightIcon={<span>R</span>} />);
    const input = screen.getByRole('textbox');
    expect(input.className).toMatch(/ps-10/);
    expect(input.className).toMatch(/pe-10/);
  });
});

describe('Input - Error vs Helper Text', () => {
  it('should show error instead of helper when both provided', () => {
    render(<Input error="Error msg" helperText="Helper msg" />);
    expect(screen.getByText('Error msg')).toBeInTheDocument();
    expect(screen.queryByText('Helper msg')).not.toBeInTheDocument();
  });

  it('should show helper when no error', () => {
    render(<Input helperText="Helper msg" />);
    expect(screen.getByText('Helper msg')).toBeInTheDocument();
  });

  it('should apply red border for error state', () => {
    render(<Input error="Error" />);
    expect(screen.getByRole('textbox').className).toMatch(/border-red-500/);
  });

  it('should not apply red border without error', () => {
    render(<Input />);
    expect(screen.getByRole('textbox').className).not.toMatch(/border-red-500/);
  });
});

describe('Input - displayName and type', () => {
  it('should have displayName', () => {
    expect(Input.displayName).toBe('Input');
  });

  it('should default to text type', () => {
    render(<Input />);
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'text');
  });

  it('should render email type', () => {
    const { container } = render(<Input type="email" />);
    expect(container.querySelector('input[type=email]')).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Button displayName
// ═══════════════════════════════════════════════════════════════════════════

describe('Button - displayName', () => {
  it('should have displayName', () => {
    expect(Button.displayName).toBe('Button');
  });
});

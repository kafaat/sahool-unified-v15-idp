# Feedback & Notification Components

Modern, accessible feedback and notification components for SAHOOL applications.

## Components Overview

- **ModernToast** - Toast notifications with context provider
- **ModernAlert** - Alert banners with dismiss animation
- **ModernBadge** - Badges with pulse animation
- **ModernProgress** - Linear and circular progress indicators
- **ModernSpinner** - Multiple spinner styles
- **ConfirmDialog** - Confirmation modal with glass effect

## Installation & Setup

### 1. Install Dependencies

```bash
npm install @sahool/shared-ui lucide-react
```

### 2. Configure Tailwind CSS

Add the required animations to your `tailwind.config.js`:

```javascript
module.exports = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './node_modules/@sahool/shared-ui/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      keyframes: {
        'slide-in-right': {
          '0%': { transform: 'translateX(100%) scale(0.95)', opacity: '0' },
          '100%': { transform: 'translateX(0) scale(1)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'progress-stripes': {
          '0%': { backgroundPosition: '1rem 0' },
          '100%': { backgroundPosition: '0 0' },
        },
        'progress-indeterminate': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(400%)' },
        },
      },
      animation: {
        'slide-in-right': 'slide-in-right 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'progress-stripes': 'progress-stripes 1s linear infinite',
        'progress-indeterminate': 'progress-indeterminate 1.5s ease-in-out infinite',
      },
    },
  },
}
```

## Component Documentation

### ModernToast

Toast notifications with automatic dismiss and context management.

#### Basic Usage

```tsx
import { ToastProvider, useToast } from '@sahool/shared-ui';

function App() {
  return (
    <ToastProvider position="top-right">
      <YourContent />
    </ToastProvider>
  );
}

function YourContent() {
  const toast = useToast();

  return (
    <button onClick={() => toast.success('Success!', 'Operation completed')}>
      Show Toast
    </button>
  );
}
```

#### API

**ToastProvider Props:**
- `position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'` - Toast position (default: 'top-right')
- `maxToasts?: number` - Maximum number of toasts (default: 5)

**useToast Hook:**
```typescript
const toast = useToast();

// Helper methods
toast.success(title, description?);
toast.error(title, description?);
toast.warning(title, description?);
toast.info(title, description?);

// Advanced usage
toast.addToast({
  title: 'Custom Toast',
  description: 'Description',
  variant: 'success',
  duration: 5000,
  id: 'optional-id'
});

// Remove toast
toast.removeToast(id);
```

#### Examples

```tsx
// Success toast
toast.success('Saved!', 'Your changes have been saved successfully.');

// Error toast
toast.error('Failed!', 'Unable to save changes. Please try again.');

// Custom duration
toast.addToast({
  title: 'Processing',
  description: 'This will take a while...',
  variant: 'info',
  duration: 10000, // 10 seconds
});
```

---

### ModernAlert

Alert banners with dismissible functionality and variants.

#### Basic Usage

```tsx
import { ModernAlert } from '@sahool/shared-ui';

<ModernAlert
  variant="success"
  title="Success"
  description="Your action was completed successfully"
  dismissible
/>
```

#### API

**Props:**
- `variant?: 'success' | 'error' | 'warning' | 'info'` - Alert style (default: 'info')
- `title: string` - Alert title (required)
- `description?: string` - Alert description
- `dismissible?: boolean` - Show dismiss button (default: false)
- `onDismiss?: () => void` - Callback when dismissed
- `icon?: LucideIcon | false` - Custom icon or hide icon
- `actions?: ReactNode` - Action buttons
- `children?: ReactNode` - Custom content

#### Examples

```tsx
// Basic alert
<ModernAlert
  variant="info"
  title="Information"
  description="This is an informational message."
/>

// With actions
<ModernAlert
  variant="warning"
  title="Pending Action"
  description="Please confirm your email address"
  actions={
    <>
      <button className="btn-primary">Confirm</button>
      <button className="btn-secondary">Resend</button>
    </>
  }
/>

// With custom content
<ModernAlert variant="error" title="Validation Errors">
  <ul className="list-disc list-inside space-y-1">
    <li>Email is required</li>
    <li>Password must be at least 8 characters</li>
  </ul>
</ModernAlert>

// Custom icon
import { Rocket } from 'lucide-react';

<ModernAlert
  variant="success"
  title="Launch Successful"
  icon={Rocket}
/>
```

---

### ModernBadge

Badges with pulse animation and multiple variants.

#### Basic Usage

```tsx
import { ModernBadge } from '@sahool/shared-ui';

<ModernBadge variant="primary">New</ModernBadge>
```

#### API

**Props:**
- `variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral'` - Badge color (default: 'primary')
- `size?: 'sm' | 'md' | 'lg'` - Badge size (default: 'md')
- `pulse?: boolean` - Enable pulse animation (default: false)
- `dot?: boolean` - Show status dot (default: false)
- `icon?: LucideIcon` - Icon to display
- `outline?: boolean` - Outline style (default: false)
- `pill?: boolean` - Pill shape (default: false)
- `onClick?: () => void` - Click handler (makes badge interactive)

#### Examples

```tsx
import { Bell, Mail } from 'lucide-react';

// Basic badges
<ModernBadge variant="success">Active</ModernBadge>
<ModernBadge variant="warning">Pending</ModernBadge>
<ModernBadge variant="danger">Critical</ModernBadge>

// With pulse animation
<ModernBadge variant="danger" pulse>Live</ModernBadge>

// With status dot
<ModernBadge variant="success" dot pulse>Online</ModernBadge>

// With icon
<ModernBadge variant="primary" icon={Bell}>
  Notifications
</ModernBadge>

// Outline style
<ModernBadge variant="info" outline>Draft</ModernBadge>

// Pill shape
<ModernBadge variant="success" pill>New</ModernBadge>

// Interactive badge
<ModernBadge
  variant="danger"
  onClick={() => clearNotifications()}
>
  Clear 5
</ModernBadge>

// Notification badge on button
<div className="relative">
  <button>Messages</button>
  <ModernBadge
    variant="danger"
    size="sm"
    pill
    className="absolute -top-2 -right-2"
  >
    12
  </ModernBadge>
</div>
```

---

### ModernProgress

Linear and circular progress indicators.

#### Basic Usage

```tsx
import { ModernProgress, CircularProgress } from '@sahool/shared-ui';

// Linear progress
<ModernProgress value={60} showLabel />

// Circular progress
<CircularProgress value={75} showLabel />
```

#### API

**ModernProgress Props:**
- `value: number` - Progress value (0-100)
- `max?: number` - Maximum value (default: 100)
- `variant?: 'primary' | 'success' | 'warning' | 'danger' | 'gradient'` - Color variant (default: 'primary')
- `size?: 'sm' | 'md' | 'lg'` - Bar height (default: 'md')
- `showLabel?: boolean` - Show percentage (default: false)
- `label?: string` - Custom label text
- `animated?: boolean` - Smooth animation (default: true)
- `indeterminate?: boolean` - Loading state (default: false)
- `striped?: boolean` - Striped pattern (default: false)
- `glow?: boolean` - Glow effect (default: false)

**CircularProgress Props:**
- `value: number` - Progress value (0-100)
- `max?: number` - Maximum value (default: 100)
- `size?: number` - Circle size in pixels (default: 64)
- `strokeWidth?: number` - Circle stroke width (default: 6)
- `variant?: 'primary' | 'success' | 'warning' | 'danger'` - Color variant (default: 'primary')
- `showLabel?: boolean` - Show percentage (default: false)

#### Examples

```tsx
// Basic linear progress
<ModernProgress value={45} />

// With label
<ModernProgress
  value={60}
  showLabel
  label="Upload Progress"
/>

// Different variants
<ModernProgress value={75} variant="success" />
<ModernProgress value={50} variant="warning" />
<ModernProgress value={30} variant="danger" />
<ModernProgress value={85} variant="gradient" glow />

// Striped and animated
<ModernProgress value={70} striped />

// Indeterminate (loading)
<ModernProgress value={0} indeterminate label="Processing..." />

// Different sizes
<ModernProgress value={60} size="sm" />
<ModernProgress value={60} size="md" />
<ModernProgress value={60} size="lg" />

// Circular progress
<CircularProgress value={75} showLabel />
<CircularProgress
  value={80}
  size={96}
  strokeWidth={8}
  variant="success"
/>

// Upload progress example
const [uploadProgress, setUploadProgress] = useState(0);

<ModernProgress
  value={uploadProgress}
  showLabel
  label="Uploading file..."
  variant="gradient"
  glow
/>
```

---

### ModernSpinner

Multiple loading spinner styles.

#### Basic Usage

```tsx
import { ModernSpinner, SpinnerOverlay } from '@sahool/shared-ui';

<ModernSpinner />
```

#### API

**ModernSpinner Props:**
- `variant?: 'dots' | 'ring' | 'bars' | 'pulse' | 'bounce' | 'gradient'` - Spinner style (default: 'ring')
- `size?: 'sm' | 'md' | 'lg' | 'xl'` - Spinner size (default: 'md')
- `color?: 'primary' | 'white' | 'gray' | 'success' | 'warning' | 'danger'` - Color (default: 'primary')
- `label?: string` - Accessibility label (default: 'Loading')

**SpinnerOverlay Props:**
- `visible: boolean` - Show/hide overlay
- `variant?: ModernSpinnerProps['variant']` - Spinner style (default: 'gradient')
- `message?: string` - Loading message

#### Examples

```tsx
// Different variants
<ModernSpinner variant="dots" />
<ModernSpinner variant="ring" />
<ModernSpinner variant="bars" />
<ModernSpinner variant="pulse" />
<ModernSpinner variant="bounce" />
<ModernSpinner variant="gradient" />

// Different sizes
<ModernSpinner size="sm" />
<ModernSpinner size="md" />
<ModernSpinner size="lg" />
<ModernSpinner size="xl" />

// Different colors
<ModernSpinner color="primary" />
<ModernSpinner color="success" />
<ModernSpinner color="white" />

// In buttons
<button className="btn-primary">
  <ModernSpinner size="sm" color="white" variant="dots" />
  Loading...
</button>

// Full-page overlay
const [loading, setLoading] = useState(false);

<SpinnerOverlay
  visible={loading}
  variant="gradient"
  message="Loading your content..."
/>

<button onClick={() => {
  setLoading(true);
  // ... async operation
  setTimeout(() => setLoading(false), 3000);
}}>
  Load Data
</button>
```

---

### ConfirmDialog

Confirmation modal with glass morphism effect.

#### Basic Usage

```tsx
import { ConfirmDialog } from '@sahool/shared-ui';

const [open, setOpen] = useState(false);

<ConfirmDialog
  open={open}
  onClose={() => setOpen(false)}
  onConfirm={() => {
    // Handle confirmation
    console.log('Confirmed!');
  }}
  title="Confirm Action"
  description="Are you sure you want to proceed?"
/>
```

#### API

**Props:**
- `open: boolean` - Dialog visibility (required)
- `onClose: () => void` - Close handler (required)
- `onConfirm: () => void | Promise<void>` - Confirm handler (required)
- `title: string` - Dialog title (required)
- `description?: string` - Dialog description
- `variant?: 'info' | 'warning' | 'danger' | 'success'` - Dialog style (default: 'info')
- `confirmLabel?: string` - Confirm button text (default: 'Confirm')
- `cancelLabel?: string` - Cancel button text (default: 'Cancel')
- `icon?: LucideIcon | false` - Custom icon or hide icon
- `loading?: boolean` - External loading state
- `closeOnConfirm?: boolean` - Auto-close on confirm (default: true)
- `closeOnEscape?: boolean` - Close on Escape key (default: true)
- `closeOnBackdrop?: boolean` - Close on backdrop click (default: true)
- `children?: ReactNode` - Custom content

#### Examples

```tsx
// Info dialog
<ConfirmDialog
  open={showInfo}
  onClose={() => setShowInfo(false)}
  onConfirm={() => console.log('Confirmed')}
  variant="info"
  title="Information"
  description="This is an informational dialog."
/>

// Warning dialog
<ConfirmDialog
  open={showWarning}
  onClose={() => setShowWarning(false)}
  onConfirm={() => console.log('Proceeding')}
  variant="warning"
  title="Are you sure?"
  description="This action may have consequences."
  confirmLabel="Proceed"
/>

// Danger dialog
<ConfirmDialog
  open={showDelete}
  onClose={() => setShowDelete(false)}
  onConfirm={async () => {
    await deleteItem();
  }}
  variant="danger"
  title="Delete Item?"
  description="This action cannot be undone."
  confirmLabel="Delete"
/>

// With custom content
<ConfirmDialog
  open={showDialog}
  onClose={() => setShowDialog(false)}
  onConfirm={handleConfirm}
  variant="danger"
  title="Delete Account?"
  description="This will permanently delete your account and all data."
>
  <div className="mt-3 p-3 bg-red-50 dark:bg-red-950/30 rounded-lg">
    <p className="text-sm text-red-800 dark:text-red-200">
      Type <strong>DELETE</strong> to confirm.
    </p>
    <input
      type="text"
      className="mt-2 w-full px-3 py-2 border rounded"
      placeholder="Type DELETE"
    />
  </div>
</ConfirmDialog>

// With async confirmation
const [isDeleting, setIsDeleting] = useState(false);

<ConfirmDialog
  open={showDelete}
  onClose={() => setShowDelete(false)}
  onConfirm={async () => {
    setIsDeleting(true);
    try {
      await api.deleteItem(itemId);
      toast.success('Deleted', 'Item deleted successfully');
    } catch (error) {
      toast.error('Failed', 'Could not delete item');
    } finally {
      setIsDeleting(false);
    }
  }}
  variant="danger"
  title="Delete Item?"
  loading={isDeleting}
/>
```

## Accessibility Features

All components follow WCAG 2.1 Level AA guidelines:

- **Keyboard Navigation**: Full keyboard support with focus management
- **Screen Readers**: Proper ARIA labels and live regions
- **Focus Trapping**: Modals trap focus within the dialog
- **Color Contrast**: Meets WCAG contrast requirements
- **Reduced Motion**: Respects prefers-reduced-motion setting

## Best Practices

### Toast Notifications

1. **Keep it brief** - Titles should be 3-5 words, descriptions 1-2 sentences
2. **Use appropriate variants** - Success for confirmations, error for failures
3. **Limit toast count** - Use `maxToasts` to prevent overwhelming users
4. **Set appropriate duration** - 3-5s for success, 7-10s for errors

### Alerts

1. **Use for persistent messages** - Unlike toasts, alerts remain until dismissed
2. **Include actionable items** - Use the `actions` prop for next steps
3. **Don't overuse** - Too many alerts can clutter the interface

### Badges

1. **Be concise** - 1-2 words maximum
2. **Use pulse sparingly** - Only for truly real-time/urgent indicators
3. **Provide context** - Ensure badge meaning is clear from surrounding content

### Progress Indicators

1. **Always show label for long operations** - Help users understand what's happening
2. **Use indeterminate for unknown duration** - Don't fake progress
3. **Match variant to context** - Danger for critical operations, success for completions

### Spinners

1. **Provide loading message** - Especially for slow operations
2. **Use appropriate size** - Match spinner size to content area
3. **Avoid multiple spinners** - Use one clear loading indicator

### Dialogs

1. **Clear action buttons** - Use specific labels like "Delete" not just "Yes"
2. **Explain consequences** - Especially for destructive actions
3. **Allow easy cancellation** - Support Escape key and backdrop click

## Examples

See `FeedbackComponents.example.tsx` for comprehensive usage examples.

## TypeScript Support

All components are fully typed. Import types as needed:

```typescript
import type {
  ToastContextType,
  ModernAlertProps,
  ModernBadgeProps,
  ModernProgressProps,
  ModernSpinnerProps,
  ConfirmDialogProps,
} from '@sahool/shared-ui';
```

## Contributing

When contributing to these components:

1. Maintain accessibility standards
2. Follow the existing code style
3. Add TypeScript types for all props
4. Update this documentation
5. Test in both light and dark modes
6. Test keyboard navigation
7. Test with screen readers

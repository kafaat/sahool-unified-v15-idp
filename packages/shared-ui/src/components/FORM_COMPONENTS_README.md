# Modern Form Components - مكونات النماذج الحديثة

Complete set of modern, accessible form components for the SAHOOL web application.

## Components Overview

### 1. ModernSelect - القائمة المنسدلة

Advanced dropdown component with search, multi-select, and custom styling.

**Features:**
- ✅ Single and multi-select support
- ✅ Searchable dropdown with filtering
- ✅ Custom icons for options
- ✅ Clearable selection
- ✅ Keyboard navigation (Arrow keys, Enter, Escape)
- ✅ Dark mode support
- ✅ RTL support for Arabic
- ✅ Full ARIA accessibility

**Usage:**
```tsx
import { ModernSelect } from '@sahool/shared-ui';

const options = [
  { value: 'sa', label: 'Saudi Arabia', icon: <Icon /> },
  { value: 'ae', label: 'UAE' },
];

<ModernSelect
  label="Select Country"
  options={options}
  value={selectedValue}
  onChange={setSelectedValue}
  searchable
  clearable
  variant="default" // default | filled | outlined
  size="md" // sm | md | lg
/>
```

---

### 2. ModernCheckbox - مربع الاختيار

Animated checkbox with custom icons and smooth transitions.

**Features:**
- ✅ Smooth check/uncheck animations
- ✅ Custom icons support
- ✅ Indeterminate state
- ✅ Label positioning (left/right)
- ✅ Description text support
- ✅ Ripple effect on interaction
- ✅ Dark mode support
- ✅ Full ARIA accessibility

**Usage:**
```tsx
import { ModernCheckbox } from '@sahool/shared-ui';

<ModernCheckbox
  label="Accept Terms"
  description="You must accept to continue"
  checked={accepted}
  onChange={(e) => setAccepted(e.target.checked)}
  variant="default" // default | gradient | filled
  size="md" // sm | md | lg
  required
/>
```

---

### 3. ModernRadio - زر الاختيار الدائري

Radio group with animated selection and multiple display variants.

**Features:**
- ✅ Three display variants: default, card, button
- ✅ Smooth selection animations
- ✅ Custom icons and descriptions
- ✅ Horizontal and vertical orientation
- ✅ Individual option disable
- ✅ Dark mode support
- ✅ Full ARIA accessibility

**Usage:**
```tsx
import { ModernRadio } from '@sahool/shared-ui';

const options = [
  { value: 'basic', label: 'Basic', description: '$10/month', icon: <Icon /> },
  { value: 'pro', label: 'Pro', description: '$25/month' },
];

<ModernRadio
  label="Select Plan"
  name="plan"
  options={options}
  value={selectedPlan}
  onChange={setSelectedPlan}
  variant="card" // default | card | button
  orientation="vertical" // vertical | horizontal
  size="md" // sm | md | lg
/>
```

---

### 4. ModernSwitch - مفتاح التبديل

Toggle switch with smooth animations and optional icons.

**Features:**
- ✅ Smooth toggle animations
- ✅ Three variants: default, gradient, iOS-style
- ✅ Optional on/off icons
- ✅ Custom icon support
- ✅ Glow effect on gradient variant
- ✅ Label positioning (left/right)
- ✅ Dark mode support
- ✅ Full ARIA accessibility with role="switch"

**Usage:**
```tsx
import { ModernSwitch } from '@sahool/shared-ui';

<ModernSwitch
  label="Dark Mode"
  description="Enable dark theme"
  checked={darkMode}
  onChange={(e) => setDarkMode(e.target.checked)}
  variant="gradient" // default | gradient | ios
  size="md" // sm | md | lg
  showIcons
/>
```

---

### 5. ModernSlider - شريط التمرير

Range slider with tooltip, marks, and value display.

**Features:**
- ✅ Smooth dragging with visual feedback
- ✅ Optional tooltip on hover/drag
- ✅ Value display with custom formatting
- ✅ Marks/ticks support
- ✅ Custom min/max/step
- ✅ Unit display (%, $, etc.)
- ✅ Dark mode support
- ✅ Full ARIA accessibility

**Usage:**
```tsx
import { ModernSlider } from '@sahool/shared-ui';

const marks = [
  { value: 0, label: '$0' },
  { value: 500, label: '$500' },
  { value: 1000, label: '$1000' },
];

<ModernSlider
  label="Price Range"
  value={price}
  onChange={setPrice}
  min={0}
  max={1000}
  step={50}
  unit="$"
  showValue
  showTooltip
  showMarks
  marks={marks}
  variant="gradient" // default | gradient | minimal
  size="md" // sm | md | lg
/>
```

---

### 6. DatePicker - منتقي التاريخ

Modern date picker with calendar interface and date range support.

**Features:**
- ✅ Interactive calendar grid
- ✅ Month/year navigation
- ✅ Min/max date restrictions
- ✅ Multiple date formats (dd/mm/yyyy, mm/dd/yyyy, yyyy-mm-dd)
- ✅ Today button for quick selection
- ✅ Bilingual support (Arabic/English)
- ✅ Clearable selection
- ✅ Dark mode support
- ✅ Full ARIA accessibility

**Usage:**
```tsx
import { DatePicker } from '@sahool/shared-ui';

<DatePicker
  label="Birth Date"
  value={birthDate}
  onChange={setBirthDate}
  placeholder="Select date"
  format="dd/mm/yyyy" // dd/mm/yyyy | mm/dd/yyyy | yyyy-mm-dd
  variant="default" // default | filled | outlined
  size="md" // sm | md | lg
  clearable
  min={new Date('1900-01-01')}
  max={new Date()}
/>
```

---

## Common Features

All components share these features:

### 🎨 Styling
- **Tailwind CSS** - Utility-first styling
- **Dark Mode** - Automatic dark mode support
- **Variants** - Multiple style variants
- **Sizes** - Small, medium, and large sizes
- **Custom Classes** - Support for custom className prop

### 🌍 Internationalization
- **RTL Support** - Full right-to-left layout support for Arabic
- **Bilingual Labels** - English and Arabic text support
- **Direction-aware** - Automatic layout adjustment based on document direction

### ♿ Accessibility
- **ARIA Attributes** - Comprehensive ARIA labels and roles
- **Keyboard Navigation** - Full keyboard support
- **Screen Readers** - Optimized for screen reader users
- **Focus Management** - Clear focus indicators
- **Error States** - Accessible error messaging

### ✨ Animations
- **Smooth Transitions** - CSS transitions for all state changes
- **Hover Effects** - Interactive hover states
- **Scale Animations** - Subtle scale effects on interaction
- **Ripple Effects** - Material Design-inspired ripples
- **Loading States** - Built-in loading indicators

### 🎯 Developer Experience
- **TypeScript** - Full type definitions
- **Props Interfaces** - Comprehensive prop types
- **Ref Forwarding** - Support for React refs
- **Controlled Components** - Fully controlled via props
- **Error Handling** - Built-in error states and validation

---

## Best Practices

### Form Validation
```tsx
const [errors, setErrors] = useState({});

<ModernSelect
  label="Country"
  value={country}
  onChange={setCountry}
  error={errors.country}
  required
/>
```

### Accessibility
```tsx
<ModernCheckbox
  label="Subscribe"
  aria-label="Subscribe to newsletter"
  aria-describedby="newsletter-description"
/>
<p id="newsletter-description">Receive weekly updates</p>
```

### Dark Mode
All components automatically support dark mode through Tailwind's `dark:` variants. No additional configuration needed.

### RTL Support
Components automatically adapt to RTL layout when `document.dir === 'rtl'`. The DatePicker component uses Arabic labels in RTL mode.

---

## Examples

See `ModernFormComponents.example.tsx` for comprehensive examples of all components with different configurations and use cases.

---

## File Locations

- **Components**: `/packages/shared-ui/src/components/`
  - `ModernSelect.tsx`
  - `ModernCheckbox.tsx`
  - `ModernRadio.tsx`
  - `ModernSwitch.tsx`
  - `ModernSlider.tsx`
  - `DatePicker.tsx`
- **Types**: `/packages/shared-ui/src/components/modern.types.ts`
- **Example**: `/packages/shared-ui/src/components/ModernFormComponents.example.tsx`
- **Exports**: `/packages/shared-ui/src/index.ts`

---

## Dependencies

These components require:
- React >= 18.0.0
- `@sahool/shared-utils` (for `cn` utility)
- `lucide-react` (for icons)
- Tailwind CSS (for styling)

---

## License

Part of the SAHOOL Unified Platform v15 IDP

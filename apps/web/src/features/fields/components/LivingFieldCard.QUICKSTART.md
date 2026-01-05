# Living Field Card - Quick Start Guide
# دليل البدء السريع - بطاقة الحقل الحي

## ⚡ 60-Second Quickstart

### 1. Import the Component
```tsx
import { LivingFieldCard } from '@/features/fields';
```

### 2. Use It
```tsx
<LivingFieldCard fieldId="your-field-id" />
```

### 3. Done! 🎉

---

## 📊 What You Get

```
┌─────────────────────────────────────────────────┐
│  الحقل الشمالي                    📈 يتحسن     │
│  North Field                                    │
│  ⚠️ 2 تنبيهات                                  │
├─────────────────────────────────────────────────┤
│                                                 │
│                    ● 75                         │
│                  النقاط                         │
│                 الإجمالية                      │
│                                                 │
├─────────────────────────────────────────────────┤
│  [❤️ 80]  [💧 70]  [👁️ 60]  [🌙 90]           │
│  الصحة    الترطيب  الاهتمام  الفلكي           │
├─────────────────────────────────────────────────┤
│  🟢 ممتاز (>70)  🟡 متوسط (40-70)  🔴 ضعيف  │
├─────────────────────────────────────────────────┤
│  ⚠️ التنبيهات                                  │
│  • صحة المحصول منخفضة - يُنصح بالفحص          │
│  • رطوبة التربة منخفضة - مطلوب ري              │
├─────────────────────────────────────────────────┤
│  ℹ️ التوصيات (5) ▼                             │
│  • تحسين صحة المحصول - عاجل                    │
│  • زيادة الري - عالي                           │
│  • إكمال المهام المعلقة - متوسط                │
│  • مثالي للزراعة (فلكياً) - متوسط              │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Customization Examples

### With Field Names
```tsx
<LivingFieldCard
  fieldId="field-north-1"
  fieldName="North Wheat Field"
  fieldNameAr="حقل القمح الشمالي"
/>
```

### In a Grid Layout
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 p-6">
  {fields.map(field => (
    <LivingFieldCard
      key={field.id}
      fieldId={field.id}
      fieldName={field.name}
      fieldNameAr={field.nameAr}
    />
  ))}
</div>
```

### Full-Width Dashboard
```tsx
<div className="max-w-4xl mx-auto p-6">
  <LivingFieldCard fieldId="main-field" />
</div>
```

---

## 🔧 Advanced Usage: Direct Hook Access

```tsx
import { useLivingFieldScore } from '@/features/fields';

function MyCustomComponent({ fieldId }) {
  const { data, isLoading, isError } = useLivingFieldScore(fieldId);

  if (isLoading) return <Spinner />;
  if (isError) return <ErrorMessage />;

  return (
    <div>
      <h2>Field Health: {data.overall}/100</h2>
      <div>
        Health: {data.health} |
        Hydration: {data.hydration} |
        Attention: {data.attention} |
        Astral: {data.astral}
      </div>
      <p>Trend: {data.trend}</p>
      <p>{data.alerts.length} alerts</p>
      <p>{data.recommendations.length} recommendations</p>
    </div>
  );
}
```

---

## 📦 What's Included

| File | Size | Purpose |
|------|------|---------|
| `LivingFieldCard.tsx` | 17KB | Main component |
| `useLivingFieldScore.ts` | 24KB | Data hook |
| `LivingFieldCard.example.tsx` | 3KB | Usage examples |
| `LivingFieldCard.md` | 9KB | Full documentation |
| `LivingFieldCard.QUICKSTART.md` | This file | Quick reference |
| `LivingFieldCard.summary.md` | 8KB | Implementation summary |

---

## 🎯 Score Breakdown

### Overall Score (0-100)
- **35%** Health (from NDVI satellite data)
- **35%** Hydration (from sensors + weather)
- **20%** Attention (from task completion)
- **10%** Astral (from astronomical calendar)

### Color Coding
- 🟢 **Green (70-100):** Excellent health
- 🟡 **Yellow (40-69):** Moderate, needs attention
- 🔴 **Red (0-39):** Poor, immediate action required

---

## 🚨 Common Issues & Solutions

### Issue: "No data available"
**Solution:** Ensure the field has NDVI data from the satellite service.

### Issue: Component doesn't load
**Solution:** Check that all required hooks are available:
- `useFieldNDVI` from `@/features/ndvi`
- `useCurrentWeather` from `@/features/weather`
- `useToday` from `@/features/astronomical`
- `useTasksByField` from `@/features/tasks`
- `useSensors` from `@/features/iot`

### Issue: TypeScript errors
**Solution:** Make sure you're importing from the correct path:
```tsx
import { LivingFieldCard } from '@/features/fields';
// NOT from '@/features/fields/components/LivingFieldCard'
```

---

## 📱 Responsive Behavior

- **Mobile (<640px):** 2-column sub-score grid
- **Tablet (640px-1024px):** 4-column sub-score grid
- **Desktop (>1024px):** Full layout with animations

---

## ♿ Accessibility Features

- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ ARIA labels
- ✅ High contrast colors
- ✅ Tooltip explanations
- ✅ Focus indicators

---

## 🎨 Styling

Uses Tailwind CSS with custom color schemes:
- Green: Sahool brand green (`sahool-green-*`)
- Yellow: Warning yellow
- Red: Danger red
- Gray: Neutral tones

---

## 🔗 Related Components

- `FieldCard` - Basic field information
- `FieldDetails` - Detailed field view
- `AstralFieldWidget` - Astronomical widget
- `HealthZonesLayer` - Map health zones

---

## 📚 More Information

- **Full Documentation:** [LivingFieldCard.md](./LivingFieldCard.md)
- **Examples:** [LivingFieldCard.example.tsx](./LivingFieldCard.example.tsx)
- **Summary:** [LivingFieldCard.summary.md](./LivingFieldCard.summary.md)

---

## 💡 Pro Tips

1. **Performance:** The component uses React Query caching. Data is cached for 2-15 minutes depending on the source.

2. **Real-time Updates:** For real-time updates, you can reduce the staleTime in the hook:
   ```tsx
   const { data } = useLivingFieldScore(fieldId, {
     enabled: true,
     includeAlerts: true,
     includeRecommendations: true,
   });
   ```

3. **Custom Styling:** Override colors by wrapping in a div with custom CSS:
   ```tsx
   <div className="living-field-custom">
     <LivingFieldCard fieldId={id} />
   </div>
   ```

---

**Need Help?** Check the full documentation in `LivingFieldCard.md`

**Found a Bug?** Please report it to the development team.

**Have Ideas?** See "Future Enhancements" in the summary document.

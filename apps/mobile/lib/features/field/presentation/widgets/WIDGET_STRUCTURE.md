# Field Health Widget - Visual Structure

## Widget Hierarchy

```
FieldHealthWidget
│
├─ Full View Mode (default)
│  │
│  ├─ Container (Card)
│  │  └─ Column
│  │     │
│  │     ├─ InkWell (Main Content - Tappable)
│  │     │  └─ Padding
│  │     │     └─ Column
│  │     │        │
│  │     │        ├─ Row (Main Health Display)
│  │     │        │  │
│  │     │        │  ├─ Circular Progress (100x100)
│  │     │        │  │  └─ Stack
│  │     │        │  │     ├─ CircularProgressIndicator
│  │     │        │  │     └─ Column (Score Display)
│  │     │        │  │        ├─ Text (Score: "75")
│  │     │        │  │        └─ Text (Label: "درجة")
│  │     │        │  │
│  │     │        │  └─ Expanded (Details Section)
│  │     │        │     └─ Column
│  │     │        │        │
│  │     │        │        ├─ Row (Title & Alert)
│  │     │        │        │  ├─ Column (Status)
│  │     │        │        │  │  ├─ Text ("صحة الحقل / Field Health")
│  │     │        │        │  │  └─ Row
│  │     │        │        │  │     ├─ Text (Status: "ممتاز")
│  │     │        │        │  │     └─ Trend Badge (↗️ +5%)
│  │     │        │        │  │
│  │     │        │        │  └─ Alert Badge (if alerts > 0)
│  │     │        │        │     └─ Container
│  │     │        │        │        └─ Row
│  │     │        │        │           ├─ Icon (warning)
│  │     │        │        │           └─ Text (count)
│  │     │        │        │
│  │     │        │        └─ Row (Mini Indicators Grid)
│  │     │        │           ├─ NDVI Indicator
│  │     │        │           │  └─ Container
│  │     │        │           │     └─ Column
│  │     │        │           │        ├─ Icon (eco)
│  │     │        │           │        ├─ Text (value: "0.72")
│  │     │        │           │        └─ Text (label: "NDVI")
│  │     │        │           │
│  │     │        │           ├─ Irrigation Indicator
│  │     │        │           │  └─ (same structure)
│  │     │        │           │
│  │     │        │           ├─ Tasks Indicator
│  │     │        │           │  └─ (same structure)
│  │     │        │           │
│  │     │        │           └─ Weather Indicator
│  │     │        │              └─ (same structure)
│  │     │        │
│  │     │        └─ Row (Expand Indicator)
│  │     │           ├─ Text ("عرض التفاصيل / Show Details")
│  │     │           └─ AnimatedRotation
│  │     │              └─ Icon (arrow_down)
│  │     │
│  │     └─ SizeTransition (Expandable Section)
│  │        └─ Container (Recommendations)
│  │           └─ Column
│  │              │
│  │              ├─ Divider
│  │              │
│  │              ├─ Text ("التوصيات / Recommendations")
│  │              │
│  │              └─ List of Recommendations
│  │                 └─ For each recommendation:
│  │                    └─ Container (Recommendation Card)
│  │                       └─ Column
│  │                          │
│  │                          ├─ Row (Recommendation Info)
│  │                          │  ├─ Container (Icon)
│  │                          │  │  └─ Icon
│  │                          │  │
│  │                          │  └─ Expanded (Content)
│  │                          │     └─ Column
│  │                          │        ├─ Row (Title & Priority)
│  │                          │        │  ├─ Text (title)
│  │                          │        │  └─ Badge ("عاجل" if high)
│  │                          │        │
│  │                          │        └─ Text (description)
│  │                          │
│  │                          └─ InkWell (Quick Action Button)
│  │                             └─ Container
│  │                                └─ Row
│  │                                   ├─ Icon (add_task)
│  │                                   └─ Text ("إنشاء مهمة")
│  │
│  └─ (Border highlight if alerts present)
│
└─ Compact View Mode (compact: true)
   │
   └─ Container (Small Card)
      └─ Row
         │
         ├─ Circular Progress (60x60)
         │  └─ Stack
         │     ├─ CircularProgressIndicator
         │     └─ Text (Score: "75")
         │
         ├─ Expanded (Info)
         │  └─ Column
         │     ├─ Row (Status & Trend)
         │     │  ├─ Text (Status: "ممتاز")
         │     │  └─ Trend Badge (↗️ +5%)
         │     │
         │     └─ Text (NDVI: "0.72")
         │
         └─ Alert Badge (if alerts > 0)
```

## Component Breakdown

### 1. Circular Progress Component

```
┌─────────────────┐
│   ╱───────╲    │  ← CircularProgressIndicator
│  │    75    │   │  ← Score Text (32pt, bold)
│   ╲───────╱    │
│     درجة       │  ← Label Text (10pt)
└─────────────────┘
   100x100 pixels
```

### 2. Mini Indicator Component

```
┌──────────────┐
│   🌱 Icon    │  ← Icon (20px)
│   0.72       │  ← Value (11pt, bold)
│   NDVI       │  ← Label (8pt)
└──────────────┘
 Color-coded border
```

### 3. Trend Badge Component

```
┌─────────────┐
│ ↗️ +5%      │  ← Icon + Percentage
└─────────────┘
 Color: green (up)
        blue (stable)
        red (down)
```

### 4. Alert Badge Component

```
┌────────────┐
│ ⚠️  3      │  ← Warning icon + count
└────────────┘
 Red background
 Pulsing effect
```

### 5. Recommendation Card

```
┌──────────────────────────────────────┐
│ ┌────┐                               │
│ │ 💧 │  إجهاد مائي محتمل      [عاجل]│  ← Title + Priority
│ └────┘                               │
│        مؤشر NDVI منخفض...           │  ← Description
│                                      │
│  ┌──────────────────────────────┐   │
│  │ ➕ إنشاء مهمة / Create Task  │   │  ← Quick Action
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

## Layout Specifications

### Full View Dimensions

```
Total Width: 100% - 32px (16px margin each side)
Total Height: Dynamic (based on content)

Main Card:
  Padding: 20px
  Border Radius: 20px
  Shadow: Medium elevation

Circular Progress:
  Size: 100x100
  Stroke Width: 8px
  Margin Right: 20px

Mini Indicators:
  Height: ~60px
  Spacing: 8px between
  Border Radius: 12px
  Padding: 8px horizontal, 10px vertical

Expandable Section:
  Animation Duration: 300ms
  Curve: EaseInOut
```

### Compact View Dimensions

```
Total Width: 100% - 8px (4px margin each side)
Total Height: ~80px

Card:
  Padding: 12px
  Border Radius: 16px
  Shadow: Small elevation

Circular Progress:
  Size: 60x60
  Stroke Width: 5px
  Margin Right: 12px
```

## Color Mapping

### Health Status Colors

```dart
Excellent (80-100):  #2E7D32  ████ Dark Green
Good (60-79):        #4CAF50  ████ Green
Moderate (40-59):    #FF9800  ████ Orange
Poor (0-39):         #F44336  ████ Red
```

### Indicator Colors

```dart
NDVI:        Dynamic (based on value)
             0.6+     → Green
             0.4-0.6  → Orange
             <0.4     → Red

Irrigation:  #2196F3  ████ Blue

Tasks:       Dynamic (based on count)
             0        → Green
             1-2      → Blue
             3-5      → Orange
             6+       → Red

Weather:     #4CAF50  ████ Green (favorable)
```

### Alert Colors

```dart
Warning:     #FFD600  ████ Yellow
Danger:      #D32F2F  ████ Dark Red
Info:        #1976D2  ████ Blue
Success:     #388E3C  ████ Green
```

## Responsive Behavior

### Screen Size Adaptations

```
Small (< 360px):
  - Use compact mode automatically
  - Reduce padding
  - Smaller text sizes

Medium (360px - 768px):
  - Standard layout
  - Full features

Large (> 768px):
  - Wider cards
  - More spacing
  - Larger touch targets
```

### Orientation

```
Portrait:
  - Vertical layout
  - Full width cards
  - Scrollable content

Landscape:
  - Horizontal optimization
  - Two-column layout option
  - Compact mode preferred
```

## Animation Timings

```
Expand/Collapse:   300ms  easeInOut
Circular Progress: 1000ms linear (initial)
Trend Badge:       200ms  easeIn
Alert Pulse:       1500ms infinite
```

## Accessibility Tree

```
FieldHealthWidget
├─ Semantics: "Field Health Score Widget"
│  │
│  ├─ Button: "Show field health details"
│  │  ├─ Label: "Field health score: 75 out of 100"
│  │  ├─ Hint: "Tap to expand recommendations"
│  │  └─ Value: "Excellent status"
│  │
│  ├─ Group: "Health Indicators"
│  │  ├─ Label: "NDVI: 0.72, Good"
│  │  ├─ Label: "Irrigation: Good status"
│  │  ├─ Label: "Tasks: 2 pending"
│  │  └─ Label: "Weather: Favorable"
│  │
│  └─ Group: "Recommendations" (when expanded)
│     ├─ Button: "Create task: Water stress recommendation"
│     └─ Button: "Create task: Monitor plant health"
```

## State Management

```
State Variables:
├─ _isExpanded: bool          → Expansion state
├─ _animationController       → Animation control
└─ _expandAnimation           → Expansion curve

Computed Properties:
├─ healthData: FieldHealthData → Calculated metrics
├─ recommendations: List      → Generated list
└─ alertCount: int            → Total alerts

External State (Riverpod):
├─ field: Field               → Field entity
└─ tasksProvider             → Task data
```

## Performance Considerations

```
Widget Rebuilds:
├─ Only on field data change
├─ Animations run on separate layer
└─ Recommendations calculated lazily

Optimizations:
├─ const constructors where possible
├─ Cached health calculations
├─ Efficient list rendering
└─ Proper animation disposal

Memory:
├─ Minimal state storage
├─ No memory leaks
└─ Proper cleanup on dispose
```

## Usage in Different Contexts

### 1. Field Details Screen
```
Full View
Scrollable
All features enabled
```

### 2. Fields List
```
Compact View
Multiple instances
Optimized rendering
```

### 3. Dashboard
```
Horizontal Scroll
Full View for critical fields
Compact View for overview
```

### 4. Map Overlay
```
Compact View
Minimal information
Quick glance
```

---

**Visual Design**: Material Design 3
**Animation**: 60 FPS target
**Accessibility**: WCAG AA compliant
**RTL Support**: Full bidirectional layout

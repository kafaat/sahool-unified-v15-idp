# @sahool/shared-utils

Unified utility functions for all SAHOOL frontend applications. Covers formatting, validation, color/label helpers, performance primitives, and AI context engineering modules for agricultural advisory systems.

## Installation

```bash
npm install @sahool/shared-utils
```

## Usage

```typescript
import {
  cn,
  formatDate,
  formatCurrency,
  formatArea,
  getSeverityColor,
  getStatusLabel,
  debounce,
  ContextCompressor,
  FarmMemory,
} from "@sahool/shared-utils";
```

## API Reference

### Class Utilities

```typescript
cn("px-4 py-2", isActive && "bg-green-600", "rounded-md");
// Merges Tailwind classes via clsx + tailwind-merge
```

### Date & Number Formatting

```typescript
formatDate("2026-02-25", "ar");          // Arabic locale date
formatDateTime("2026-02-25T10:00:00");   // Date + time
formatNumber(1234.5, "en");              // "1,234.5"
formatArea(8.5, "ar");                   // "٨٫٥ هكتار"
formatCurrency(1250, "ar", "YER");       // YER formatted
formatPercentage(0.782);                 // "78.2%"
```

### Color & Label Helpers

```typescript
getStatusColor("active");      // "text-green-600 bg-green-100"
getSeverityColor("critical");  // "text-red-600 bg-red-100"
getStatusLabel("pending", "ar");   // "قيد المراجعة"
getSeverityLabel("high", "en");    // "High"
getHealthScoreColor(85);       // "text-green-600 bg-green-100"
```

### Validation

```typescript
isEmpty(null);             // true
isValidEmail("a@b.com");   // true
isValidYemenPhone("+9671234567890"); // validates Yemen phone format
```

### String Utilities

```typescript
truncate("Long text here", 10);  // "Long text..."
capitalize("hello");              // "Hello"
generateId("field");             // "field_1706000000000_abc123xyz"
```

### Performance Utilities

```typescript
import { debounce, throttle, memoize, batchCalls, createLRUCache, measureTime } from "@sahool/shared-utils";

const debouncedSearch = debounce(search, 300);
const throttledUpdate = throttle(update, 1000);
const memoizedCalc = memoize(expensiveCalc);
const cache = createLRUCache<string, number>(100); // 100-item LRU cache
```

### AI Context Engineering

```typescript
import {
  ContextCompressor,
  CompressionStrategy,
  FarmMemory,
  MemoryType,
  RecommendationEvaluator,
  EvaluationCriteria,
} from "@sahool/shared-utils";

// Compress farm data to fit LLM context windows
const compressor = new ContextCompressor({ maxTokens: 4000 });
const result = compressor.compress(farmData, CompressionStrategy.LEVEL_2);

// Tenant-isolated persistent farm memory
const memory = new FarmMemory({ tenantId: "farm-001", maxEntries: 500 });
memory.store(MemoryType.EVENT, { crop: "wheat", action: "irrigation" });
const relevant = memory.recall("nitrogen deficiency wheat");

// Evaluate AI recommendation quality (LLM-as-Judge)
const evaluator = new RecommendationEvaluator();
const score = evaluator.evaluate(recommendation, {
  criteria: [EvaluationCriteria.ACCURACY, EvaluationCriteria.ACTIONABILITY],
});
```

### API Client

```typescript
import { KongClient } from "@sahool/shared-utils/api";
// Pre-configured HTTP client for Kong Gateway with auth headers
```

### Observability

```typescript
import { SentryClient, trackError } from "@sahool/shared-utils/observability";
// Sentry integration with SAHOOL error context
```

## Types

```typescript
export type Locale   = "ar" | "en";
export type Severity = "low" | "medium" | "high" | "critical";
export type Status   = "pending" | "confirmed" | "rejected" | "treated" | "active" | "inactive";
```

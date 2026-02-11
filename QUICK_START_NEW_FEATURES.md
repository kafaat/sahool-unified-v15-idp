# Quick Start Guide - New Features & Improvements
# دليل البداية السريعة - الميزات والتحسينات الجديدة

## 📱 Mobile App Features

### 1. Empty State Widgets

**Import:**
```dart
import 'package:sahool_field_app/core/widgets/empty_state_widget.dart';
```

**Usage Examples:**
```dart
// Generic empty state
EmptyStateWidget(
  title: 'No Data',
  titleAr: 'لا توجد بيانات',
  message: 'Start adding items',
  messageAr: 'ابدأ بإضافة العناصر',
  icon: Icons.inbox_outlined,
)

// For empty fields list
EmptyFieldsState(
  onAddField: () => Navigator.push(...),
)

// For empty tasks
EmptyTasksState(
  onAddTask: () => showDialog(...),
)
```

### 2. Loading State Widgets

**Import:**
```dart
import 'package:sahool_field_app/core/widgets/loading_state_widget.dart';
```

**Usage Examples:**
```dart
// Basic loading
LoadingStateWidget(
  message: 'Loading...',
  messageAr: 'جارٍ التحميل...',
  showMessage: true,
)

// Skeleton loader for lists
SkeletonLoader(
  itemCount: 5,
  height: 80.0,
)

// In buttons
ElevatedButton(
  child: isLoading 
    ? InlineLoading(label: 'Saving', labelAr: 'جارٍ الحفظ')
    : Text('Save'),
)
```

### 3. Performance Monitor

**Import:**
```dart
import 'package:sahool_field_app/core/performance/performance_monitor.dart';
```

**Usage Examples:**
```dart
// Track screen load
@override
void initState() {
  super.initState();
  PerformanceMonitor().start('screen_load_home');
}

@override
void didChangeDependencies() {
  super.didChangeDependencies();
  PerformanceMonitor().end('screen_load_home');
}

// Track API calls
final data = await PerformanceMonitor().trackApiCall(
  'get_fields',
  () => apiClient.getFields(),
);

// Use mixin
class MyWidget extends StatelessWidget with PerformanceTrackingMixin {
  Future<void> loadData() async {
    await trackApiCall('load_data', () => api.fetch());
  }
}

// Log summary
PerformanceMonitor().logSummary();
```

---

## 🌐 Web App Features

### Centralized Error Handler

**Import:**
```typescript
import { ApiErrorHandler, useApiErrorHandler } from '@/lib/api/error-handler';
```

**Usage in Components:**
```typescript
function MyComponent() {
  const { handleError } = useApiErrorHandler();

  const fetchData = async () => {
    try {
      const response = await axios.get('/api/fields');
      return response.data;
    } catch (error) {
      const apiError = handleError(error);
      
      // Get localized message
      const message = ApiErrorHandler.formatErrorMessage(apiError, 'ar');
      toast.error(message);
      
      // Check if retryable
      if (ApiErrorHandler.isRetryable(apiError)) {
        const delay = ApiErrorHandler.getRetryDelay(apiError, 1);
        setTimeout(fetchData, delay);
      }
    }
  };
}
```

**Error Messages (Bilingual):**
```typescript
// 401: Session expired
"انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى."
"Session expired. Please login again."

// 403: Access denied
"تم رفض الوصول. ليس لديك صلاحية لهذا الإجراء."
"Access denied. You do not have permission for this action."

// 429: Rate limit
"طلبات كثيرة جداً. حاول مرة أخرى لاحقاً."
"Too many requests. Please try again later."
```

---

## 🔐 Admin Dashboard Features

### 1. Rate Limiter

**Import:**
```typescript
import { checkRateLimit, resetRateLimit } from '@/lib/rate-limiter';
```

**Usage in API Routes:**
```typescript
export async function POST(request: NextRequest) {
  const { email } = await request.json();
  
  // Check rate limit
  const rateLimit = checkRateLimit(`login:${email}`, {
    maxAttempts: 5,
    windowMs: 15 * 60 * 1000,
    lockoutDurationMs: 30 * 60 * 1000,
  });
  
  if (!rateLimit.allowed) {
    return NextResponse.json(
      { error: rateLimit.message },
      { status: 429 }
    );
  }
  
  // ... authentication logic
  
  // On success
  resetRateLimit(`login:${email}`);
}
```

**Configuration:**
```typescript
{
  maxAttempts: 5,           // Max attempts allowed
  windowMs: 15 * 60 * 1000, // Time window (15 min)
  lockoutDurationMs: 30 * 60 * 1000, // Lockout (30 min)
}
```

### 2. Session Management Page

**Access:** `/settings/sessions`

**Features:**
- View all active sessions
- Device and browser information
- IP address and location
- Last activity timestamp
- Revoke suspicious sessions
- Auto-refresh every 30 seconds
- Bilingual interface (AR/EN)

**API Endpoint Required:**
```typescript
// GET /api/admin/sessions
{
  sessions: [
    {
      id: string,
      userId: string,
      userEmail: string,
      ipAddress: string,
      userAgent: string,
      createdAt: string,
      lastActivity: string,
      expiresAt: string,
      isCurrent: boolean,
      location?: { city: string, country: string }
    }
  ]
}

// DELETE /api/admin/sessions/:id
// Revokes a specific session
```

---

## 🎨 Best Practices

### Mobile App

1. **Always use specialized empty states:**
   ```dart
   // ✅ Good
   EmptyFieldsState(onAddField: _addField)
   
   // ❌ Avoid
   Center(child: Text('No fields'))
   ```

2. **Use skeleton loaders for lists:**
   ```dart
   // ✅ Good
   isLoading ? SkeletonLoader(itemCount: 5) : ListView(...)
   
   // ❌ Avoid
   isLoading ? CircularProgressIndicator() : ListView(...)
   ```

3. **Track important operations:**
   ```dart
   // ✅ Track screen loads and heavy operations
   PerformanceMonitor().trackApiCall('fetch_data', () => api.fetch());
   ```

### Web App

1. **Use error handler consistently:**
   ```typescript
   // ✅ Good
   const { handleError } = useApiErrorHandler();
   catch (err) { const error = handleError(err); }
   
   // ❌ Avoid
   catch (err) { console.error(err); }
   ```

2. **Show localized messages:**
   ```typescript
   // ✅ Good
   const message = ApiErrorHandler.formatErrorMessage(error, locale);
   toast.error(message);
   ```

### Admin Dashboard

1. **Always use rate limiting on auth endpoints:**
   ```typescript
   // ✅ Good - Protected
   const rateLimit = checkRateLimit(`login:${email}`);
   
   // ❌ Avoid - Unprotected
   // Direct login without rate limiting
   ```

2. **Monitor active sessions:**
   - Check session management page regularly
   - Revoke suspicious sessions immediately
   - Monitor for unusual activity patterns

---

## 📊 Monitoring & Analytics

### Performance Metrics

**Mobile App:**
```dart
// Log performance summary
PerformanceMonitor().logSummary();

// Output:
// screen_load_HomeScreen: avg=245ms, min=198ms, max=312ms
// api_get_fields: avg=156ms, min=98ms, max=289ms
```

**Thresholds:**
- Screen loads: < 500ms (ideal), < 1000ms (acceptable)
- API calls: < 200ms (ideal), < 500ms (acceptable)
- Operations > 3000ms trigger warnings

---

## 🔒 Security Notes

### Rate Limiting
- **Login attempts:** Max 5 per 15 minutes
- **Lockout period:** 30 minutes
- **Applies to:** Email-based rate limiting
- **Production:** Consider Redis-based implementation

### Session Management
- **Session duration:** 1 day
- **Refresh token:** 7 days
- **Idle timeout:** 30 minutes
- **Revocation:** Immediate effect

---

## 📚 Additional Resources

- **Full Documentation:** `IMPROVEMENTS_SUMMARY_2026-02-11.md`
- **Mobile App Structure:** `apps/mobile/sahool_field_app/STRUCTURE.md`
- **Web App README:** `apps/web/README.md`
- **Admin Dashboard:** `apps/admin/README.md`

---

**Version:** 16.0.0  
**Last Updated:** 2026-02-11  
**Developed by:** GitHub Copilot + KAFAAT Team

# Fields Feature - API Integration Guide

## Overview / نظرة عامة

The Fields feature has been updated to use **real API endpoints** instead of mock data, with automatic fallback to cached/mock data if the API is unavailable.

تم تحديث ميزة الحقول لاستخدام **نقاط نهاية API حقيقية** بدلاً من البيانات الوهمية، مع التراجع التلقائي إلى البيانات المخزنة/الوهمية في حالة عدم توفر API.

---

## What Changed / ما الذي تغير

### 1. New API Layer (`api.ts`)

- Created a dedicated API layer using **axios**
- Connects to field-ops service endpoints
- Automatic token authentication from cookies
- Smart error handling with fallback to mock data
- Arabic and English error messages

### 2. Updated Hooks (`hooks/useFields.ts`)

- All hooks now use real API calls
- Automatic retry on failure (1 retry)
- Fallback to mock data on API errors
- Query key management for better caching
- Added new `useFieldStats` hook

### 3. Enhanced Types (`types.ts`)

- Added complete `Field` interface (no longer importing from external package)
- Added `GeoPolygon` and `GeoPoint` types
- Added `FieldStats` and `FieldError` types
- More comprehensive field properties

---

## API Endpoints / نقاط نهاية API

The feature connects to the following field-ops endpoints:

| Method | Endpoint               | Description                  |
| ------ | ---------------------- | ---------------------------- |
| GET    | `/api/v1/fields`       | List all fields with filters |
| GET    | `/api/v1/fields/{id}`  | Get single field by ID       |
| POST   | `/api/v1/fields`       | Create a new field           |
| PUT    | `/api/v1/fields/{id}`  | Update existing field        |
| DELETE | `/api/v1/fields/{id}`  | Delete a field               |
| GET    | `/api/v1/fields/stats` | Get field statistics         |

### Base URL

- Default: `http://localhost:8000` (Kong Gateway)
- Kong routes `/api/v1/fields/*` to field-ops service (port 8100)
- Configurable via `NEXT_PUBLIC_API_URL` environment variable

---

## Features / الميزات

### ✅ Real API Integration

- Connects to actual field-ops microservice
- Automatic authentication with Bearer token
- Timeout protection (10 seconds)

### ✅ Offline Support

- Falls back to mock data if API is unavailable
- Console warnings when using fallback data
- No crashes or blank screens on network errors

### ✅ Arabic Error Messages

- All error messages in both Arabic and English
- Proper error handling with user-friendly messages
- Structured error responses

### ✅ Smart Caching

- React Query caching with 2-minute stale time
- Automatic cache invalidation on mutations
- Optimistic updates for better UX

### ✅ Type Safety

- Full TypeScript support
- Type mapping between API and UI models
- No `any` types in hook signatures

---

## Usage Examples / أمثلة الاستخدام

### Fetching Fields

```tsx
import { useFields } from "@/features/fields";

function MyComponent() {
  const { data: fields, isLoading, error } = useFields();

  if (isLoading) return <div>Loading...</div>;
  if (error) console.warn("API error, using cached data");

  return <div>{fields?.map((f) => f.name)}</div>;
}
```

### Creating a Field

```tsx
import { useCreateField } from "@/features/fields";
import { useAuth } from "@/stores/auth.store";

function CreateFieldButton() {
  const { user } = useAuth();
  const createField = useCreateField();

  const handleCreate = async () => {
    try {
      await createField.mutateAsync({
        data: {
          name: "New Field",
          nameAr: "حقل جديد",
          area: 5.5,
          crop: "Wheat",
          cropAr: "قمح",
        },
        tenantId: user?.tenant_id,
      });
      alert("Field created!");
    } catch (error) {
      const errorData = JSON.parse(error.message);
      alert(errorData.messageAr);
    }
  };

  return <button onClick={handleCreate}>Create</button>;
}
```

### Filtering Fields

```tsx
import { useFields } from "@/features/fields";

function FilteredFields() {
  const { data: fields } = useFields({
    search: "wheat",
    minArea: 2,
    maxArea: 10,
    status: "active",
    farmId: "farm-123",
  });

  return <div>{fields?.length} fields found</div>;
}
```

See `examples/usage.tsx` for more comprehensive examples.

---

## Error Messages / رسائل الخطأ

All error messages are available in both languages:

```typescript
import { ERROR_MESSAGES } from "@/features/fields";

// Example:
ERROR_MESSAGES.NETWORK_ERROR.ar; // "خطأ في الاتصال. استخدام البيانات المحفوظة."
ERROR_MESSAGES.NETWORK_ERROR.en; // "Network error. Using offline data."
```

Available error messages:

- `NETWORK_ERROR` - Connection failed
- `FETCH_FAILED` - Failed to retrieve fields
- `CREATE_FAILED` - Failed to create field
- `UPDATE_FAILED` - Failed to update field
- `DELETE_FAILED` - Failed to delete field
- `NOT_FOUND` - Field not found

---

## Field Data Mapping / تعيين بيانات الحقل

The API layer automatically maps between API fields and UI fields:

### API → UI Mapping

```typescript
{
  id: apiField.id,
  name: apiField.name,
  nameAr: apiField.nameAr || apiField.name,
  area: apiField.areaHectares || apiField.area,
  crop: apiField.cropType || apiField.crop,
  cropAr: apiField.cropTypeAr || apiField.cropAr,
  farmId: apiField.tenantId || apiField.farmId,
  polygon: apiField.boundary || apiField.polygon,
  // ... etc
}
```

### UI → API Mapping

```typescript
{
  name: field.name,
  nameAr: field.nameAr,
  tenantId: field.farmId || tenantId,
  cropType: field.crop,
  cropTypeAr: field.cropAr,
  coordinates: field.polygon?.coordinates?.[0],
  boundary: field.polygon,
  areaHectares: field.area,
  // ... etc
}
```

---

## Testing the Integration / اختبار التكامل

### 1. With API Available

```bash
# Start the field-ops service (port 8100)
cd services/field-ops
npm run dev

# Start Kong Gateway (port 8000)
docker-compose up kong

# Start the web app
cd apps/web
npm run dev

# Navigate to http://localhost:3000
# Check browser console - should see API calls
```

### 2. With API Unavailable (Offline Mode)

```bash
# Don't start field-ops service
# Only start web app
cd apps/web
npm run dev

# Navigate to http://localhost:3000
# Check browser console - should see:
# "Failed to fetch fields from API, using mock data"
# The app will still work with mock data!
```

---

## Environment Variables / متغيرات البيئة

Configure in `.env` or `.env.local`:

```bash
# API Base URL (Kong Gateway)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Default Tenant ID for development
NEXT_PUBLIC_DEFAULT_TENANT_ID=tenant_1
```

---

## Migration Checklist / قائمة مرجعية للترحيل

- [x] Create API layer (`api.ts`)
- [x] Update hooks to use real API
- [x] Add error handling with fallback
- [x] Add Arabic error messages
- [x] Update types for full Field interface
- [x] Add authentication token support
- [x] Add field statistics hook
- [x] Create usage examples
- [x] Test with API available
- [x] Test with API unavailable (offline mode)
- [ ] Update existing components to handle errors gracefully
- [ ] Add loading skeletons for better UX
- [ ] Add toast notifications for errors (optional)

---

## Next Steps / الخطوات التالية

1. **Update Components**: Update existing field components to show error banners when using cached data
2. **Add Notifications**: Integrate toast notifications for success/error messages
3. **Add Loading States**: Add skeleton loaders for better loading experience
4. **Add Optimistic Updates**: Implement optimistic UI updates for better responsiveness
5. **Add Retry Logic**: Add manual retry buttons when API fails
6. **Add Sync Indicator**: Show online/offline status in UI

---

## Support / الدعم

For issues or questions:

- Check browser console for detailed error messages
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Ensure field-ops service is running on port 8100
- Check Kong Gateway is routing correctly

---

**Last Updated**: 2025-12-24
**Version**: 17.0.0

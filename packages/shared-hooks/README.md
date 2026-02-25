# @sahool/shared-hooks

Shared React hooks for the SAHOOL platform, covering authentication, permissions, real-time WebSocket connections, API data fetching, and browser storage.

## Installation

```bash
npm install @sahool/shared-hooks
```

Peer dependency: `react >= 18.0.0`

## Usage

```typescript
import {
  useAuth,
  useCan,
  useWebSocket,
  useApi,
  useDebounce,
  useLocalStorage,
} from "@sahool/shared-hooks";
```

## Hook Reference

### Authentication

```typescript
// Get the current authenticated user and auth state
const { user, isAuthenticated, login, logout, isLoading } = useAuth();

// Permission checks (all return boolean)
const canEditField   = useCan("field:write");
const canManageUsers = useCan("users:manage");
const hasAnyAdmin    = useCanAny(["admin:read", "admin:write"]);
const hasAllPerms    = useCanAll(["field:read", "field:write"]);
const isFarmer       = useHasRole("farmer");
```

Available permission constants:
```typescript
import { PERMISSIONS, ROLES, ROLE_PERMISSIONS } from "@sahool/shared-hooks";

// Helper functions
import { roleHasPermission, hasPermission, getRolePermissions } from "@sahool/shared-hooks";
```

### WebSocket (Real-Time Updates)

```typescript
const { isConnected, send, disconnect, reconnect, error } = useWebSocket({
  url: "ws://localhost:8081/ws/fields",
  onMessage: (msg) => console.log(msg.type, msg.payload),
  onConnect: () => console.log("Connected"),
  reconnectInterval: 5000,       // ms between reconnect attempts
  maxReconnectAttempts: 10,
  enabled: isAuthenticated,
});
```

### API Data Fetching

```typescript
// Single resource fetch with loading/error state
const { data, isLoading, error, refetch } = useApi<Field[]>("/api/v1/fields");

// Paginated fetch
const { data, page, totalPages, nextPage, prevPage } = usePaginatedApi<Field>(
  "/api/v1/fields",
  { pageSize: 20 }
);
```

### Debounce

```typescript
// Debounce a value (e.g., search input)
const debouncedQuery = useDebounce(searchQuery, 300);

// Debounce a callback
const { callback: debouncedSave } = useDebouncedCallback(save, 500);
```

### Local Storage

```typescript
// Typed persistent state synchronized with localStorage
const [theme, setTheme] = useLocalStorage<"light" | "dark">("theme", "light");
const [language, setLanguage] = useLocalStorage<"ar" | "en">("lang", "ar");
```

### Auth Context (Provider Setup)

```typescript
import { AuthContext, createAuthContextValue } from "@sahool/shared-hooks";

// In your app root:
const authValue = createAuthContextValue({ /* initial state */ });

<AuthContext.Provider value={authValue}>
  <App />
</AuthContext.Provider>
```

## Event Stream Hook

```typescript
import { useEventStream } from "@sahool/shared-hooks/events";

// Subscribe to NATS-forwarded server-sent events
const { events } = useEventStream("sahool.field.created");
```

## Dependencies

- `@sahool/api-client` - Pre-configured API client for Kong Gateway
- `js-cookie` - Cookie management for token storage

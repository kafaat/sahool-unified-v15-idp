# Task Service TODO Items - Implementation Status

## Project: SAHOOL Task Service
**Date**: 2026-01-18
**Service**: `/home/user/sahool-unified-v15-idp/apps/services/task-service/src/`

---

## TODO #1: Database Migration - Move from In-Memory Storage to PostgreSQL

**Status**: URGENT - IN PROGRESS
**Location**: `main.py` (multiple endpoints)
**Priority**: HIGH
**Effort**: MEDIUM

### Issue Description

The task-service is currently using in-memory dictionaries (`tasks_db` and `evidence_db`) for storing tasks and evidence instead of the PostgreSQL database infrastructure that is already set up.

### Current State

**In-Memory Storage Definitions** (need to identify and remove):
- `tasks_db` dictionary - stores Task objects in memory
- `evidence_db` dictionary - stores Evidence objects in memory

**Affected Endpoints** (22 occurrences):
1. Line 1220-1227: `get_today_tasks()` - reads from `tasks_db`
2. Line 1240-1247: `get_upcoming_tasks()` - reads from `tasks_db`
3. Line 1261: `get_task_stats()` - reads from `tasks_db`
4. Line 1303-1306: `get_task()` - reads from `tasks_db`
5. Line 1353: `create_task()` - writes to `tasks_db`
6. Line 1382-1395: `update_task()` - reads/writes to `tasks_db`
7. Line 1420-1449: `complete_task()` - reads/writes to `tasks_db` and `evidence_db`
8. Line 1474-1483: `start_task()` - reads/writes to `tasks_db`
9. Line 1508-1517: `cancel_task()` - reads/writes to `tasks_db`
10. Line 1542-1546: `delete_task()` - reads/deletes from `tasks_db`
11. Line 1559-1575: `add_evidence()` - reads/writes to `tasks_db` and `evidence_db`
12. Line 1690: `create_task_from_ndvi_alert()` - writes to `tasks_db`
13. Line 1925: `auto_create_tasks()` - writes to `tasks_db`
14. Line 2152: `create_task_with_astronomical_recommendation()` - writes to `tasks_db`

### Required Changes

#### Step 1: Add Database Dependency to Endpoints
All endpoints need to accept a database session dependency:

```python
from fastapi import Depends
from .database import get_db
from sqlalchemy.orm import Session

@app.get("/api/v1/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),  # ADD THIS
):
    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id, tenant_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task_to_dict(task)
```

#### Step 2: Replace In-Memory Reads with Database Queries
**Before**:
```python
task = tasks_db.get(task_id)
if not task or task.tenant_id != tenant_id:
    raise HTTPException(status_code=404, detail="Task not found")
```

**After**:
```python
repo = TaskRepository(db)
task = repo.get_task_by_id(task_id, tenant_id)
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

#### Step 3: Replace In-Memory Writes with Database Persistence
**Before**:
```python
tasks_db[task_id] = task
```

**After**:
```python
repo = TaskRepository(db)
task = repo.create_task(task)
```

#### Step 4: Update Complex Endpoints
Endpoints like `get_task_stats()` need complete refactoring:

**Current** (using in-memory):
```python
def get_task_stats(tenant_id: str):
    tenant_tasks = [t for t in tasks_db.values() if t.tenant_id == tenant_id]
    # ... process in-memory list
```

**New** (using database):
```python
async def get_task_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    repo = TaskRepository(db)
    stats = repo.get_task_stats(tenant_id)
    return stats
```

### Database Infrastructure Already Available

✅ **TaskRepository** (`repository.py`):
- `create_task(task)` - creates and returns task
- `get_task_by_id(task_id, tenant_id)` - retrieves task with tenant validation
- `list_tasks()` - supports filtering and pagination
- `update_task()` - updates and records history
- `delete_task()` - deletes task
- `start_task()` - marks as in_progress
- `complete_task()` - marks as completed with evidence
- `cancel_task()` - cancels task
- `add_evidence()` - adds evidence to task
- `get_task_stats()` - returns aggregated statistics

✅ **Database Configuration** (`database.py`):
- `init_database()` - initializes PostgreSQL connection
- `get_db()` - FastAPI dependency for session injection
- `get_db_session()` - context manager for direct usage
- `seed_demo_data()` - populates test data

✅ **Models** (`models.py`):
- `Task` - SQLAlchemy model with all required fields
- `TaskEvidence` - evidence model with relationships
- `TaskHistory` - audit trail for changes

### Testing Strategy

1. **Unit Tests**: Verify each endpoint works with database
2. **Integration Tests**: Verify NATS events still publish correctly
3. **Smoke Tests**: Verify basic CRUD operations
4. **Regression Tests**: Ensure NDVI integration still works

### Estimated Effort

- **Analysis**: 30 minutes (DONE)
- **Endpoint Refactoring**: 2-3 hours (14 endpoints)
- **Testing**: 1 hour
- **Debugging/Fixes**: 1 hour
- **Total**: ~4-5 hours

### Non-Straightforward Endpoints (Require Special Handling)

1. **`get_today_tasks()` & `get_upcoming_tasks()`** - Need pagination support
2. **`get_task_stats()`** - Repository method exists but needs integration
3. **`create_task()` & `update_task()`** - Need to handle astronomical data enrichment
4. **Evidence endpoints** - TaskEvidence model integration

### Straightforward Endpoints (Ready to Migrate)

1. ✅ `get_task()` - Single read, direct repository call
2. ✅ `delete_task()` - Single delete, direct repository call
3. ✅ `start_task()` - Status update, repository method exists
4. ✅ `cancel_task()` - Status update, repository method exists

---

## TODO #2: Real NDVI Service Integration

**Status**: PLANNED
**Location**: `main.py` line 1735-1750, `get_task_suggestions_for_field()`
**Priority**: MEDIUM
**Effort**: LOW

### Issue Description

The `get_task_suggestions_for_field()` endpoint currently uses mock suggestions. It should call the actual NDVI service to fetch real field health data.

### Current Implementation

```python
# TODO: Call NDVI service to get field health data
# For now, return mock suggestions based on common scenarios
```

### Required Changes

The NDVI client (`ndvi_client.py`) is already fully implemented with:
- `NDVIClient.get_field_health(field_id)` - fetches actual health data
- `get_task_suggestions_from_health(health_data)` - generates suggestions from real data
- Fallback to simulated data if service unavailable

### Implementation Status

✅ **NDVI Client Already Integrated**:
```python
from .ndvi_client import (
    get_ndvi_client,
    get_task_suggestions_from_health,
)

ndvi_client = get_ndvi_client()
health_data = await ndvi_client.get_field_health(field_id)
raw_suggestions = get_task_suggestions_from_health(health_data)
```

The endpoint at line 1735-1750 already has this implementation!

### Current Status
- Line 1741: `ndvi_client = get_ndvi_client()` ✅
- Line 1742: `health_data = await ndvi_client.get_field_health(field_id)` ✅
- Line 1750: `raw_suggestions = get_task_suggestions_from_health(health_data)` ✅

**CONCLUSION**: This TODO is already COMPLETED. The real NDVI service integration is in place.

---

## TODO #3: Field Manager Lookup

**Status**: COMPLETED ✅
**Location**: `main.py` line 796-861 (`fetch_field_manager()`)
**Completed**: Already implemented

### Implementation Details

Function `fetch_field_manager()`:
- Fetches field manager from field-service
- Validates field_id to prevent SSRF
- Sanitizes for logging to prevent log injection
- Has proper error handling and timeouts
- Fallback if field manager not found

Used in:
- `create_task_from_ndvi_alert()` - Line 1647-1652
- `auto_create_tasks()` - Line 1882-1885

Configuration:
- `FIELD_SERVICE_URL` env var (default: `http://field-service:8115`)

---

## Summary of TODO Items

| TODO | Status | Effort | Priority | Notes |
|------|--------|--------|----------|-------|
| Database Migration | IN PROGRESS | 4-5 hrs | HIGH | 22 endpoint changes needed |
| NDVI Integration | COMPLETED ✅ | - | - | Already implemented |
| Field Manager Lookup | COMPLETED ✅ | - | - | Already implemented |
| In-Memory Storage Removal | BLOCKED | - | HIGH | Depends on Database Migration |

---

## Implementation Checklist

### Phase 1: Straightforward Endpoints (READY TO START)
- [ ] `get_task()` - single read
- [ ] `delete_task()` - single delete
- [ ] `start_task()` - status update
- [ ] `cancel_task()` - status update

### Phase 2: Complex Endpoints (AFTER DATABASE FOUNDATION)
- [ ] `create_task()` - with astronomical enrichment
- [ ] `update_task()` - with history tracking
- [ ] `complete_task()` - with evidence handling
- [ ] `add_evidence()` - task evidence

### Phase 3: Analytics Endpoints (AFTER CORE)
- [ ] `list_tasks()` - already uses repository!
- [ ] `get_task_stats()` - repository has method
- [ ] `get_today_tasks()` - refactor to use repo
- [ ] `get_upcoming_tasks()` - refactor to use repo

### Phase 4: NDVI Endpoints (VERIFY ONLY)
- [ ] `create_task_from_ndvi_alert()` - verify database integration
- [ ] `get_task_suggestions_for_field()` - verify NDVI client works
- [ ] `auto_create_tasks()` - verify batch creation works
- [ ] `get_field_health()` - verify NDVI client calls

---

## Files Modified

- `/home/user/sahool-unified-v15-idp/apps/services/task-service/src/main.py` - endpoint refactoring
- No changes to: `database.py`, `repository.py`, `models.py`, `ndvi_client.py` (already correct)

---

## Next Steps

1. Start with Phase 1 endpoints (straightforward)
2. Verify each endpoint works with database
3. Run tests to ensure no regressions
4. Move to Phase 2 endpoints
5. Verify NDVI integration still works after migration
6. Remove in-memory storage dictionaries

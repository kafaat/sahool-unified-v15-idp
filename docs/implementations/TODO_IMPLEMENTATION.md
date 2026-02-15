# Task Service TODO Items - Implementation Status

## Project: SAHOOL Task Service
**Date**: 2026-01-18
**Service**: `/home/user/sahool-unified-v15-idp/apps/services/task-service/src/`

---

## TODO #1: Database Migration - Move from In-Memory Storage to PostgreSQL

**Status**: COMPLETED ✅
**Location**: `routes/tasks.py` (all endpoints migrated)
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
| Database Migration | COMPLETED ✅ | 4-5 hrs | HIGH | All endpoints migrated to PostgreSQL via TaskRepository |
| NDVI Integration | COMPLETED ✅ | - | - | Already implemented |
| Field Manager Lookup | COMPLETED ✅ | - | - | Already implemented |
| In-Memory Storage Removal | COMPLETED ✅ | - | HIGH | No in-memory dicts remain; all routes use DB |

---

## Implementation Checklist

### Phase 1: Straightforward Endpoints ✅ COMPLETED
- [x] `get_task()` - single read via `TaskRepository.get_task_by_id()`
- [x] `delete_task()` - single delete via `TaskRepository.delete_task()`
- [x] `start_task()` - status update via `TaskRepository.start_task()`
- [x] `cancel_task()` - status update via `TaskRepository.cancel_task()`

### Phase 2: Complex Endpoints ✅ COMPLETED
- [x] `create_task()` - with astronomical enrichment + `TaskRepository.create_task()`
- [x] `update_task()` - with history tracking via `TaskRepository.update_task()`
- [x] `complete_task()` - with evidence handling via `TaskRepository.complete_task()`
- [x] `add_evidence()` - task evidence via `TaskRepository.add_evidence()`

### Phase 3: Analytics Endpoints ✅ COMPLETED
- [x] `list_tasks()` - uses `TaskRepository.list_tasks()` with full filtering
- [x] `get_task_stats()` - uses `TaskRepository.get_task_stats()`
- [x] `get_today_tasks()` - refactored to use `TaskRepository.list_tasks()`
- [x] `get_upcoming_tasks()` - refactored to use `TaskRepository.list_tasks()`

### Phase 4: NDVI Endpoints ✅ VERIFIED
- [x] `create_task_from_ndvi_alert()` - database integration confirmed
- [x] `get_task_suggestions_for_field()` - NDVI client integration works
- [x] `auto_create_tasks()` - batch creation via database works
- [x] `get_field_health()` - NDVI client calls confirmed

---

## Architecture

All task endpoints are in `routes/tasks.py`, `routes/astronomical.py`, and `routes/ndvi.py`.
Each endpoint uses `db: Session = Depends(get_db)` and `TaskRepository(db)` for database access.
No in-memory storage dictionaries (`tasks_db`, `evidence_db`) exist in the codebase.

## Files

- `apps/services/task-service/src/main.py` - FastAPI app with lifecycle management
- `apps/services/task-service/src/routes/tasks.py` - Task CRUD routes (all use DB)
- `apps/services/task-service/src/routes/astronomical.py` - Astronomical calendar routes
- `apps/services/task-service/src/routes/ndvi.py` - NDVI integration routes
- `apps/services/task-service/src/repository.py` - TaskRepository (sync + async)
- `apps/services/task-service/src/database.py` - Database configuration & session management
- `apps/services/task-service/src/models.py` - SQLAlchemy ORM models (Task, TaskEvidence, TaskHistory)

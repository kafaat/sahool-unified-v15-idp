# PostgreSQL Migration - Endpoint Updates

This file contains the patches needed to update all task-service endpoints to use PostgreSQL.

## Endpoints to Update

### 1. get_today_tasks - Line ~1030

```python
@app.get("/api/v1/tasks/today", response_model=dict)
async def get_today_tasks(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),  # ADD THIS
):
    """Get tasks due today"""
    repo = TaskRepository(db)  # ADD THIS

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    tasks, _ = repo.list_tasks(  # REPLACE with this
        tenant_id=tenant_id,
        due_after=today_start,
        due_before=today_end,
        limit=100,
    )

    return {
        "tasks": [db_task_to_dict(t) for t in tasks],
        "count": len(tasks),
    }
```

### 2. get_task_stats - Line ~1050

```python
@app.get("/api/v1/tasks/stats", response_model=dict)
async def get_task_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),  # ADD THIS
):
    """Get task statistics"""
    repo = TaskRepository(db)  # ADD THIS
    return repo.get_task_stats(tenant_id)  # REPLACE with this
```

### 3. get_task - Line ~1100

```python
@app.get("/api/v1/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),  # ADD THIS
):
    """Get a specific task by ID"""
    repo = TaskRepository(db)  # ADD THIS
    task = repo.get_task_by_id(task_id, tenant_id)  # REPLACE with this
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task_to_dict(task)  # REPLACE with this
```

### 4. create_task - Line ~1110

```python
@app.post("/api/v1/tasks", response_model=Task, status_code=201)
async def create_task(
    data: TaskCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),  # ADD THIS
):
    """Create a new task"""
    repo = TaskRepository(db)  # ADD THIS
    now = datetime.utcnow()
    task_id = f"task_{uuid.uuid4().hex[:12]}"

    task = TaskModel(  # CHANGE from Task to TaskModel
        task_id=task_id,
        tenant_id=tenant_id,
        title=data.title,
        title_ar=data.title_ar,
        description=data.description,
        description_ar=data.description_ar,
        task_type=data.task_type.value,  # ADD .value
        priority=data.priority.value,  # ADD .value
        status="pending",  # CHANGE from TaskStatus.PENDING
        field_id=data.field_id,
        zone_id=data.zone_id,
        assigned_to=data.assigned_to,
        created_by="user_system",
        due_date=data.due_date,
        scheduled_time=data.scheduled_time,
        estimated_duration_minutes=data.estimated_duration_minutes,
        created_at=now,
        updated_at=now,
        metadata=data.metadata,
    )

    # Fetch and populate astronomical data if due_date is provided
    if data.due_date:
        astro_data = await fetch_astronomical_data(data.due_date, data.task_type)
        task.astronomical_score = astro_data.get("score")
        task.moon_phase_at_due_date = astro_data.get("moon_phase_ar")
        task.lunar_mansion_at_due_date = astro_data.get("lunar_mansion_ar")
        task.optimal_time_of_day = astro_data.get("optimal_time")
        task.astronomical_recommendation = astro_data.get("full_data")
        task.astronomical_warnings = astro_data.get("warnings", [])
    else:
        task.astronomical_score = data.astronomical_score
        task.moon_phase_at_due_date = data.moon_phase_at_due_date
        task.lunar_mansion_at_due_date = data.lunar_mansion_at_due_date
        task.optimal_time_of_day = data.optimal_time_of_day
        task.suggested_by_calendar = data.suggested_by_calendar
        task.astronomical_recommendation = data.astronomical_recommendation

    created_task = repo.create_task(task)  # ADD THIS
    return db_task_to_dict(created_task)  # REPLACE with this
```

### 5. update_task - Line ~1160

```python
@app.put("/api/v1/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),  # ADD THIS
):
    """Update a task"""
    repo = TaskRepository(db)  # ADD THIS

    # Convert Pydantic model to dict, excluding unset fields
    update_data = {}
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            # Convert enums to values
            if isinstance(value, Enum):
                update_data[field] = value.value
            else:
                update_data[field] = value

    # Refresh astronomical data if due_date was changed
    if "due_date" in update_data and update_data["due_date"]:
        # Fetch task type
        task = repo.get_task_by_id(task_id, tenant_id)
        if task:
            astro_data = await fetch_astronomical_data(
                update_data["due_date"],
                TaskType(task.task_type)
            )
            update_data["astronomical_score"] = astro_data.get("score")
            update_data["moon_phase_at_due_date"] = astro_data.get("moon_phase_ar")
            update_data["lunar_mansion_at_due_date"] = astro_data.get("lunar_mansion_ar")
            update_data["optimal_time_of_day"] = astro_data.get("optimal_time")
            update_data["astronomical_recommendation"] = astro_data.get("full_data")
            update_data["astronomical_warnings"] = astro_data.get("warnings", [])

    updated_task = repo.update_task(
        task_id=task_id,
        tenant_id=tenant_id,
        updates=update_data,
        performed_by="user_system",
    )

    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task_to_dict(updated_task)
```

### 6. start_task, complete_task, cancel_task, delete_task

```python
@app.post("/api/v1/tasks/{task_id}/start", response_model=Task)
async def start_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Mark a task as in progress"""
    repo = TaskRepository(db)
    task = repo.start_task(task_id, tenant_id, "user_system")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task_to_dict(task)


@app.post("/api/v1/tasks/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: str,
    data: TaskComplete,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Mark a task as completed with evidence"""
    repo = TaskRepository(db)

    task = repo.complete_task(
        task_id=task_id,
        tenant_id=tenant_id,
        performed_by="user_system",
        notes=data.notes or data.notes_ar,
        actual_duration_minutes=data.actual_duration_minutes,
        completion_metadata=data.completion_metadata,
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Add photo evidence
    if data.photo_urls:
        for url in data.photo_urls:
            evidence = TaskEvidenceModel(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                type="photo",
                content=url,
                captured_at=datetime.utcnow(),
            )
            repo.add_evidence(evidence)

    # Refresh task to get updated evidence
    task = repo.get_task_by_id(task_id, tenant_id)
    return db_task_to_dict(task)


@app.post("/api/v1/tasks/{task_id}/cancel", response_model=Task)
async def cancel_task(
    task_id: str,
    reason: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Cancel a task"""
    repo = TaskRepository(db)
    task = repo.cancel_task(task_id, tenant_id, "user_system", reason)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task_to_dict(task)


@app.delete("/api/v1/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete a task"""
    repo = TaskRepository(db)
    success = repo.delete_task(task_id, tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
```

### 7. add_evidence

```python
@app.post("/api/v1/tasks/{task_id}/evidence", response_model=Evidence, status_code=201)
async def add_evidence(
    task_id: str,
    evidence_type: str = Query(..., description="Type: photo, note, voice, measurement"),
    content: str = Query(..., description="URL or text content"),
    lat: float | None = None,
    lon: float | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Add evidence to a task"""
    repo = TaskRepository(db)

    # Verify task exists
    task = repo.get_task_by_id(task_id, tenant_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    evidence = TaskEvidenceModel(
        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        type=evidence_type,
        content=content,
        captured_at=datetime.utcnow(),
        location={"lat": lat, "lon": lon} if lat and lon else None,
    )

    created_evidence = repo.add_evidence(evidence)

    return {
        "evidence_id": created_evidence.evidence_id,
        "task_id": created_evidence.task_id,
        "type": created_evidence.type,
        "content": created_evidence.content,
        "captured_at": created_evidence.captured_at,
        "location": created_evidence.location,
    }
```

### 8. create_task_from_ndvi_alert - Update to use database

Replace `tasks_db[task_id] = task` with:

```python
    repo = TaskRepository(db)  # Add at start of function
    created_task = repo.create_task(task)  # Replace tasks_db assignment
    # ... rest of the function
    return db_task_to_dict(created_task)  # At the end
```

### 9. auto_create_tasks - Update to use database

Replace task creation loop with:

```python
    repo = TaskRepository(db)  # Add at start
    # ... in the loop:
    created_task = repo.create_task(task)  # Replace tasks_db assignment
    created_tasks.append(created_task)
```

### 10. create_task_with_astronomical_recommendation - Update to use database

Replace `tasks_db[task_id] = task` with:

```python
    repo = TaskRepository(db)  # Add at start of function
    created_task = repo.create_task(task)  # Replace tasks_db assignment
    return db_task_to_dict(created_task)  # At the end
```

## Summary

All endpoints need:

1. Add `db: Session = Depends(get_db)` parameter
2. Create `repo = TaskRepository(db)` at the start
3. Replace in-memory operations with repository methods
4. Use `db_task_to_dict()` to convert models to dicts for responses
5. Convert enum values to strings when creating database models (.value)

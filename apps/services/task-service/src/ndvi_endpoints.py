"""
NDVI Integration Endpoints for Task Service
نقاط تكامل NDVI لخدمة المهام

These endpoints should be integrated into main.py
"""

# To integrate these endpoints into main.py, add the following code after the
# add_evidence endpoint and before the Astronomical-Based Task Endpoints section:

NDVI_ENDPOINTS_CODE = '''
# ═══════════════════════════════════════════════════════════════════════════
# NDVI Integration Endpoints - نقاط تكامل NDVI
# ═══════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/tasks/from-ndvi-alert", response_model=Task, status_code=201)
async def create_task_from_ndvi_alert(
    data: NdviAlertTaskRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Create task from NDVI alert
    إنشاء مهمة من تنبيه NDVI

    Automatically creates a task when NDVI anomaly is detected:
    - Calculates priority based on severity
    - Generates Arabic and English descriptions
    - Auto-assigns if requested
    - Sends notifications
    """
    logger.info(
        f"Creating task from NDVI alert: field={data.field_id}, "
        f"type={data.alert_type}, ndvi={data.ndvi_value:.3f}"
    )

    try:
        # Calculate priority based on NDVI severity
        priority = calculate_ndvi_priority(
            ndvi_value=data.ndvi_value,
            previous_ndvi=data.previous_ndvi,
            alert_type=data.alert_type,
            alert_metadata=data.alert_metadata,
        )

        # Generate task content in English and Arabic
        title, title_ar, description, description_ar = generate_ndvi_task_content(
            alert_type=data.alert_type,
            ndvi_value=data.ndvi_value,
            previous_ndvi=data.previous_ndvi,
            field_id=data.field_id,
            zone_id=data.zone_id,
        )

        # Determine task type based on NDVI value
        if data.ndvi_value < 0.3:
            task_type = TaskType.SCOUTING  # Critical - needs investigation
        elif data.alert_type == "drop":
            task_type = TaskType.IRRIGATION  # Likely water stress
        else:
            task_type = TaskType.SCOUTING  # General investigation

        # Calculate due date based on priority
        now = datetime.utcnow()
        due_date_map = {
            TaskPriority.URGENT: timedelta(hours=4),  # 4 hours for urgent
            TaskPriority.HIGH: timedelta(hours=12),  # 12 hours for high
            TaskPriority.MEDIUM: timedelta(days=1),  # 1 day for medium
            TaskPriority.LOW: timedelta(days=2),  # 2 days for low
        }
        due_date = now + due_date_map.get(priority, timedelta(days=1))

        # Determine assignee
        assigned_to = data.assigned_to
        if data.auto_assign and not assigned_to:
            # Fetch field manager from field service
            field_manager = await fetch_field_manager(data.field_id, tenant_id)
            if field_manager:
                assigned_to = field_manager
                logger.info(f"Auto-assigned NDVI task to field manager: {assigned_to}")
            else:
                logger.warning(
                    f"Could not fetch field manager for field {data.field_id}, "
                    f"task will be created without assignment"
                )

        # Build metadata
        metadata = {
            "source": "ndvi_alert",
            "alert_type": data.alert_type,
            "ndvi_value": data.ndvi_value,
            "previous_ndvi": data.previous_ndvi,
            **(data.alert_metadata or {}),
        }

        # Create task
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task = Task(
            task_id=task_id,
            tenant_id=tenant_id,
            title=title,
            title_ar=title_ar,
            description=description,
            description_ar=description_ar,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            field_id=data.field_id,
            zone_id=data.zone_id,
            assigned_to=assigned_to,
            created_by="system_ndvi",
            due_date=due_date,
            created_at=now,
            updated_at=now,
            metadata=metadata,
        )

        tasks_db[task_id] = task

        # Send notification if task is assigned
        if assigned_to:
            await send_task_notification(
                tenant_id=tenant_id,
                task=task,
                notification_type="ndvi_alert_task",
            )

        logger.info(
            f"Task created from NDVI alert: {task_id} "
            f"(priority={priority.value}, assigned_to={assigned_to})"
        )

        return task

    except Exception as e:
        logger.error(f"Error creating task from NDVI alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to create task from NDVI alert: {str(e)}"
        )


@app.get("/api/v1/tasks/suggest-for-field/{field_id}", response_model=dict)
async def get_task_suggestions_for_field(
    field_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get task suggestions based on field health
    الحصول على اقتراحات المهام بناءً على صحة الحقل

    Analyzes field's NDVI history and current status to suggest tasks:
    - Reviews recent NDVI trends
    - Identifies areas of concern
    - Suggests preventive and corrective actions
    - Returns prioritized list with confidence scores
    """
    logger.info(f"Generating task suggestions for field: {field_id}")

    try:
        # Call NDVI service to get field health data
        from .ndvi_client import get_ndvi_client, get_task_suggestions_from_health

        ndvi_client = get_ndvi_client()
        health_data = await ndvi_client.get_field_health(field_id=field_id)

        logger.info(
            f"Retrieved health data for field {field_id}: "
            f"score={health_data.health_score}, status={health_data.health_status.value}"
        )

        # Generate task suggestions based on health data
        raw_suggestions = get_task_suggestions_from_health(health_data)

        # Convert to TaskSuggestion objects
        suggestions = []
        for raw in raw_suggestions:
            # Map task type string to TaskType enum
            task_type_map = {
                "scouting": TaskType.SCOUTING,
                "irrigation": TaskType.IRRIGATION,
                "sampling": TaskType.SAMPLING,
                "fertilization": TaskType.FERTILIZATION,
                "spraying": TaskType.SPRAYING,
            }
            task_type = task_type_map.get(raw["task_type"], TaskType.SCOUTING)

            # Map priority string to TaskPriority enum
            priority_map = {
                "urgent": TaskPriority.URGENT,
                "high": TaskPriority.HIGH,
                "medium": TaskPriority.MEDIUM,
                "low": TaskPriority.LOW,
            }
            priority = priority_map.get(raw["priority"], TaskPriority.MEDIUM)

            suggestions.append(
                TaskSuggestion(
                    task_type=task_type,
                    priority=priority,
                    title=raw["title"],
                    title_ar=raw["title_ar"],
                    description=raw["description"],
                    description_ar=raw["description_ar"],
                    reason=raw["reason"],
                    reason_ar=raw["reason_ar"],
                    confidence=raw["confidence"],
                    suggested_due_days=raw["suggested_due_days"],
                    metadata={
                        "source": "ndvi_analysis",
                        "health_score": health_data.health_score,
                        "health_status": health_data.health_status.value,
                        "ndvi_mean": health_data.ndvi_mean,
                        "zones": health_data.zones,
                    },
                )
            )

        logger.info(f"Generated {len(suggestions)} task suggestions for field {field_id}")

        return {
            "field_id": field_id,
            "suggestions": [s.model_dump() for s in suggestions],
            "total": len(suggestions),
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error generating task suggestions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate task suggestions: {str(e)}"
        )


@app.post("/api/v1/tasks/auto-create", response_model=dict, status_code=201)
async def auto_create_tasks(
    data: TaskAutoCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Batch create tasks from recommendations
    إنشاء دفعة من المهام من التوصيات

    Creates multiple tasks at once from AI/ML recommendations:
    - Validates all suggestions
    - Creates tasks with appropriate priorities
    - Auto-assigns if requested
    - Sends batch notifications
    - Returns summary of created tasks
    """
    logger.info(
        f"Auto-creating {len(data.suggestions)} tasks for field {data.field_id}"
    )

    created_tasks = []
    failed_tasks = []
    now = datetime.utcnow()

    try:
        # Determine assignee
        assigned_to = data.assigned_to
        if data.auto_assign and not assigned_to:
            # Fetch field manager from field service
            field_manager = await fetch_field_manager(data.field_id, tenant_id)
            if field_manager:
                assigned_to = field_manager
                logger.info(f"Auto-assigned batch tasks to field manager: {assigned_to}")
            else:
                logger.warning(
                    f"Could not fetch field manager for field {data.field_id}, "
                    f"tasks will be created without assignment"
                )

        # Create tasks from suggestions
        for idx, suggestion in enumerate(data.suggestions):
            try:
                # Calculate due date
                due_date = now + timedelta(days=suggestion.suggested_due_days)

                # Create task
                task_id = f"task_{uuid.uuid4().hex[:12]}"
                task = Task(
                    task_id=task_id,
                    tenant_id=tenant_id,
                    title=suggestion.title,
                    title_ar=suggestion.title_ar,
                    description=suggestion.description,
                    description_ar=suggestion.description_ar,
                    task_type=suggestion.task_type,
                    priority=suggestion.priority,
                    status=TaskStatus.PENDING,
                    field_id=data.field_id,
                    assigned_to=assigned_to,
                    created_by="system_auto",
                    due_date=due_date,
                    created_at=now,
                    updated_at=now,
                    metadata={
                        "source": "auto_create",
                        "confidence": suggestion.confidence,
                        "reason": suggestion.reason,
                        "reason_ar": suggestion.reason_ar,
                        **(suggestion.metadata or {}),
                    },
                )

                tasks_db[task_id] = task
                created_tasks.append(task)

                logger.info(
                    f"Auto-created task {idx + 1}/{len(data.suggestions)}: "
                    f"{task_id} ({suggestion.task_type.value})"
                )

            except Exception as task_error:
                logger.error(
                    f"Failed to create task from suggestion {idx}: {task_error}"
                )
                failed_tasks.append(
                    {
                        "index": idx,
                        "suggestion": suggestion.title,
                        "error": str(task_error),
                    }
                )

        # Send batch notification if tasks were created
        if created_tasks and assigned_to:
            try:
                # Send a summary notification
                summary_task = Task(
                    task_id="batch_summary",
                    tenant_id=tenant_id,
                    title=f"{len(created_tasks)} New Tasks Created",
                    title_ar=f"تم إنشاء {len(created_tasks)} مهمة جديدة",
                    description=f"Field {data.field_id} has {len(created_tasks)} new recommended tasks",
                    description_ar=f"الحقل {data.field_id} لديه {len(created_tasks)} مهمة موصى بها جديدة",
                    task_type=TaskType.OTHER,
                    priority=TaskPriority.MEDIUM,
                    status=TaskStatus.PENDING,
                    field_id=data.field_id,
                    assigned_to=assigned_to,
                    created_by="system_auto",
                    created_at=now,
                    updated_at=now,
                )

                await send_task_notification(
                    tenant_id=tenant_id,
                    task=summary_task,
                    notification_type="tasks_batch_created",
                )
            except Exception as notif_error:
                logger.warning(f"Failed to send batch notification: {notif_error}")

        logger.info(
            f"Auto-create completed: {len(created_tasks)} created, "
            f"{len(failed_tasks)} failed"
        )

        return {
            "field_id": data.field_id,
            "created": [t.model_dump() for t in created_tasks],
            "failed": failed_tasks,
            "summary": {
                "total_requested": len(data.suggestions),
                "created_count": len(created_tasks),
                "failed_count": len(failed_tasks),
                "assigned_to": assigned_to,
            },
        }

    except Exception as e:
        logger.error(f"Error in auto-create tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to auto-create tasks: {str(e)}"
        )
'''

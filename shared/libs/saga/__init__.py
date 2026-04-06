"""
SAHOOL Saga Orchestrator
========================
منسق الـ Saga للعمليات الموزعة

Orchestrated Saga pattern for distributed transactions across
SAHOOL's 72 microservices. Provides:

- Persistent state (survives crashes)
- Compensation with retry + backoff
- Per-step timeouts
- Idempotency keys
- Full audit trail

Usage:
    from shared.libs.saga import SagaOrchestrator, SagaDefinition, SagaStep

    saga = SagaDefinition(
        name="create_field",
        steps=[
            SagaStep(name="create_field", action=create_field_fn, compensate=delete_field_fn),
            SagaStep(name="init_billing", action=init_billing_fn, compensate=cancel_billing_fn),
            SagaStep(name="set_permissions", action=set_perms_fn, compensate=revoke_perms_fn),
        ],
    )

    orchestrator = SagaOrchestrator(db_factory=get_session)
    result = await orchestrator.execute(saga, context={"tenant_id": "t1", "field_data": {...}})
"""

from .models import (
    SagaExecution,
    SagaState,
    SagaStepRecord,
    StepState,
)
from .orchestrator import SagaDefinition, SagaOrchestrator, SagaStep

__all__ = [
    "SagaOrchestrator",
    "SagaDefinition",
    "SagaStep",
    "SagaExecution",
    "SagaStepRecord",
    "SagaState",
    "StepState",
]

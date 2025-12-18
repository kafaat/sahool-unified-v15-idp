# ADR-002: Service Layering Architecture

## Status
Accepted

## Date
2025-01-01

## Context

SAHOOL Platform needs a clear service organization that:
1. Prevents circular dependencies
2. Separates concerns (sensing vs. deciding vs. acting)
3. Enables independent scaling
4. Enforces data ownership boundaries
5. Supports gradual complexity growth

## Decision

**Adopt a 4-Layer Architecture**

### Layer Definitions

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Platform Core (البنية الأساسية)                │
│ Purpose: Infrastructure & Governance                    │
│ Communication: Manages all inter-service communication  │
│ Examples: process-manager, schema-registry, gateway     │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ Events
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 2: Signal Producers (الحواس) 🔒 NO PUBLIC API    │
│ Purpose: Sense the world, produce raw signals           │
│ Communication: Publish events ONLY, no HTTP consumers   │
│ Examples: astro-agri, weather, ndvi, image-diagnosis    │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Events
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Decision Services (العقل)                     │
│ Purpose: Analyze signals, make recommendations          │
│ Communication: Subscribe to L2, publish decisions       │
│ Examples: crop-lifecycle, disease-risk, advisor         │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Events
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 4: Execution Services (الأيدي)                   │
│ Purpose: Take action, interact with users/devices       │
│ Communication: Subscribe to L3, expose APIs             │
│ Examples: tasks, alerts, equipment                      │
└─────────────────────────────────────────────────────────┘
```

### Communication Rules

| From → To | Allowed | Method |
|-----------|---------|--------|
| L2 → L3 | ✅ | Events only |
| L2 → L4 | ❌ | Never direct |
| L3 → L4 | ✅ | Events only |
| L4 → L3 | ⚠️ | Events only (feedback) |
| Any → L1 | ✅ | Events + Internal API |
| L1 → Any | ✅ | Events + Orchestration |

### Layer 2 Restrictions (Critical)

```yaml
Signal Producers (Layer 2):
  MUST:
    - Publish events to NATS
    - Expose only internal endpoints (/internal/*)
    - Be stateless (except for caching)
  
  MUST NOT:
    - Expose public API endpoints
    - Call other services directly
    - Make business decisions
    - Store business state
    
  Enforcement:
    - sahool-gen prevents public routes
    - docker-compose uses 'expose' not 'ports'
    - Kong has no routes to L2 services
```

### Data Ownership

```yaml
Each service owns its data exclusively:
  
  astro-agri:
    - agricultural_stars
    - folk_proverbs
    - planting_rules
    - regional_variations
  
  crop-lifecycle:
    - crop_plantings
    - growth_stages
    - stage_transitions
  
  tasks:
    - tasks
    - task_assignments
    - task_completions
```

## Consequences

### Positive
- ✅ Clear boundaries prevent spaghetti architecture
- ✅ Each layer scales independently
- ✅ Easy to understand data flow
- ✅ Testable in isolation
- ✅ Natural event-driven design

### Negative
- ❌ More services to manage
- ❌ Latency for multi-layer flows
- ❌ Requires discipline to maintain boundaries

### Mitigations
- sahool-gen enforces rules at creation time
- CI/CD checks for cross-layer violations
- Process Manager handles complex flows

## Related
- ADR-001: Event Bus
- docs/ENGINEERING_GUARDRAILS.md
- tools/sahool-gen/

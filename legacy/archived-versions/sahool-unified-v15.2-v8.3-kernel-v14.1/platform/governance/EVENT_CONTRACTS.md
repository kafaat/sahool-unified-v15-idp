# SAHOOL Event Contracts v15.2

This folder defines **authoritative event contracts** for the SAHOOL kernel.

## Subjects (NATS)

| Subject | Producer Layer | Consumers | Description |
|---|---|---|---|
| `internal.image.analyze` | Layer 3+ (requester) | Layer 2 (image-diagnosis) | Request an image analysis (internal only) |
| `internal.image.analyzed` | Layer 2 | Layer 3+ | Image analysis results |
| `decision.disease.risk_assessed` | Layer 3 | Layer 4+ | Disease risk decision |

## Envelope (required)

Every event MUST contain:

- `event_id` (uuid)
- `event_type` (subject string)
- `tenant_id`
- `timestamp` (UTC ISO8601, ends with `Z`)
- `correlation_id` (uuid)
- `trace.trace_id` (optional)
- `trace.span_id` (optional)
- `payload` (subject specific)
- `schema_version` (string: `v15.2`)

## Schemas

JSON Schema files live in `governance/schemas/`.

Services MUST validate produced events before publishing.
Decision/action services SHOULD validate consumed events before processing.

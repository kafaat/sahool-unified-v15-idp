# Governance Schemas

> مخططات الحوكمة | Governance Schemas

JSON schemas for validating service metadata and template inputs across the SAHOOL platform.

## Contents

| File | Purpose |
|------|---------|
| [service-metadata.schema.json](./service-metadata.schema.json) | Validates service entries in `services.yaml` |
| [template-input.schema.json](./template-input.schema.json) | Validates IDP template input parameters |

## Service Metadata Schema

Validates that each service in `governance/services.yaml` has required fields:

- `name`: Service identifier
- `type`: `python` or `nodejs`
- `port`: Unique port number
- `layer`: `acquisition`, `intelligence`, `decision`, or `business`
- `status`: `active`, `deprecated`, or `archived`
- `owner`: Team or individual owner

## Template Input Schema

Validates input parameters when scaffolding new services via `sahoolctl`:

- `service_name`: kebab-case identifier
- `template`: Valid template type
- `port`: Port number (unique, within range)
- `layer`: Event architecture layer

## Validation

Schemas are validated in CI via `governance-validation.yml` workflow.

## Related

- [Service Registry](../services.yaml) — Service definitions
- [IDP Templates](../../idp/templates/) — Service scaffolding templates
- [Event Schemas](../events/schemas/) — Event payload schemas

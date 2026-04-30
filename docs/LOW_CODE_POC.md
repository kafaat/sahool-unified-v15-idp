# SAHOOL Low-Code PoC

This PoC implements the first safe slice of the SAHOOL Low-Code direction: use existing SAHOOL design tokens and one OpenAPI operation to generate Flutter UI scaffolding without importing an external Low-Code runtime.

## Scope

- Generate a Flutter `ThemeData` starter from `governance/design/design-tokens.yaml`.
- Generate one Flutter form from `api/services/vegetation-analysis-service.openapi.yaml`.
- Require Tenant Context and RBAC inputs before the generated form renders.
- Keep generated widgets dependency-free beyond Flutter itself.
- Keep generated UI as form-only: it does not perform API calls.

## Files

| File | Purpose |
| --- | --- |
| `scripts/generate_flutter_theme_from_tokens.py` | Reads design tokens and writes the generated Flutter theme. |
| `scripts/generate_openapi_flutter_form_poc.py` | Reads one OpenAPI operation and writes a guarded Flutter form widget. |
| `apps/mobile/lib/core/theme/generated/sahool_token_theme.dart` | Generated token-backed Flutter `ThemeData`. |
| `apps/mobile/lib/features/lowcode/generated/analyzesatellitegeometry_form.dart` | Generated guarded form for `analyzeSatelliteGeometry`. |

## Commands

```bash
npm run lowcode:poc
npm run lint:sahool
```

Run the generators separately when needed:

```bash
npm run lowcode:theme
npm run lowcode:form:poc
```

## Guardrails

- **Tenant Context**: generated widgets require a non-empty `tenantId`.
- **RBAC**: generated widgets require an explicit operation permission before rendering.
- **No direct network calls**: the generated form emits a payload through `onSubmit`; API clients remain outside the generated UI.
- **No new Flutter packages**: the PoC uses Flutter SDK widgets only.
- **Token-only styling**: generated theme values come from `governance/design/design-tokens.yaml`.

## Next Step

After this PoC is reviewed, the next safe extension is to add a schema registry adapter that selects approved OpenAPI operations and maps them to audited form templates.

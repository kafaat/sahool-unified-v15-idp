# Frontend authentication and test-contract verification

Base: `ab53c98596daca1740d2ac5a5dbd48db7b24e34f`.

The repaired contracts pass their focused checks. The full web suite still fails eight existing CSP nonce assertions; this change leaves both the policy and those assertions unchanged. [verification.json](verification.json) records commands, actual exit codes, report digests, checked source hashes, and the failing case names.

## Behavior changed

The lightweight authentication client no longer treats a successful HTTP status as sufficient evidence of a valid login or registration response. It rejects invalid JSON, non-object JSON, incomplete session payloads, and explicit `success: false` responses. A session payload must contain a nonempty access token and a user object with a nonempty ID. Error values are returned only when they are strings. This is minimum session-shape validation, not JWT verification; signature and authorization checks remain server responsibilities.

Registration continues to accept the backend's explicit, token-free `{ success: true, message }` acknowledgement. The user-service uses that response to avoid exposing whether an email is already registered. An incomplete token-bearing response cannot masquerade as this acknowledgement. Existing valid login, new-account registration, and privacy acknowledgement cases remain successful.

The tests now exercise the actual contracts:

- Login uses the same-origin `/api/auth/login` BFF with cookie credentials.
- Refresh checks expiry and security attributes on the returned response cookies, and sends the backend's camelCase `refreshToken` field.
- Field mutations accept the explicit tenant or the existing `tenant_id` cookie fallback, and reject missing tenant context before any request. The backend remains responsible for the authoritative JWT tenant.
- The sidebar mock includes the production `DatabaseZap` icon.
- Admin layout tests retain request-dependent dynamic rendering. Field creation is tested through a real form submission to the central endpoint constant, including the drawn boundary and returned field.
- Crop readiness tests supply the required Express response and assert HTTP 200 for healthy memory and HTTP 503 at the pressure threshold.

No dependency manifest, lockfile, runtime support policy, production tenant policy, Prisma implementation, or CI gating policy is changed here.

## Results

Tests ran on verified official Node.js `v20.20.2`, with the existing isolated installation of Vitest `3.2.4`, Next.js `15.5.14`, Jest `29.7.0`, and TypeScript `5.9.3`. This evidence does not claim a fresh `npm ci` or acceptance of the separate JavaScript dependency upgrade.

| Check | Result |
| --- | --- |
| Four repaired web suites | 88 passed, 0 failed, 0 skipped |
| Two repaired admin suites | 102 passed, 0 failed, 0 skipped |
| Complete web suite | 1,358 passed, **8 failed**, 0 skipped |
| Complete admin suite | 2,515 passed, 0 failed, 0 skipped |
| Crop health/readiness | 4 passed, 0 failed, 0 skipped |
| Web TypeScript check | Exit 0 |
| Changed web/admin source lint | Exit 0, no errors or warnings |
| Same 49 auth cases against the original client | 21 passed, **28 failed as expected**, 0 skipped |

The auth negative control uses the exact base client in an isolated directory, with the final candidate tests and the same test dependencies. It confirms that the new rejection cases expose the original behavior. It does not modify the candidate client or replace production dependencies.

The local NestJS authentication package was built normally before the crop check. Initial incomplete dependency links and missing generated declarations produced setup failures; the logs are retained separately, and the final checks above ran after those local setup issues were corrected. No generated build output or dependency installation is committed.

## Unresolved CSP nonce enforcement

The eight failing assertions describe a real, currently unimplemented security behavior. They are not caused by the tests choosing an invalid nonce string:

1. `apps/web/src/middleware.ts`, in `addSecurityHeaders`, generates a nonce, puts it on the **response** `X-Nonce` header, and obtains CSP from `getCSPConfig` / `getCSPHeader`.
2. `apps/web/src/lib/security/csp-config.ts`, in `getCSPDirectives`, deliberately ignores `_nonce`. Its comments describe compatibility with the current inline hydration scripts and styles. The emitted policy includes neither a nonce source nor `strict-dynamic`.
3. `getCSPHeader` serializes those directives. A source search found no other production web header that enforces nonce sources.
4. `apps/web/src/app/layout.tsx` emits the theme initialization script without a nonce.

Changing a fixture to a valid Base64 nonce would therefore still leave these assertions failing. This repair does not replace them with expectations that require permissive inline script execution, mark them skipped, or introduce a CSP rollout. Enforcing nonce-based CSP needs a separate change that propagates the per-request nonce into the request/rendering path and validates actual hydration, inline scripts, styles, and browser behavior.

The complete web suite is **not green**. Any publication or merge decision must retain this limitation.

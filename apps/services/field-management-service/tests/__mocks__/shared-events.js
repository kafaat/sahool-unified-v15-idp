/**
 * Minimal stub for @sahool/shared-events.
 *
 * The real package imports `nats` (which has native addon dependencies) and
 * `uuid` (which may be ESM-only in the installed version).  Both cause Jest
 * to crash when loading the module at test time.
 *
 * Tests mock FieldEventsService completely, so only the type information
 * (from tsconfig.test.json paths) is needed at compile time.  This stub
 * satisfies the runtime require() call with the minimal constants used by
 * field-events.service.ts.
 */

// Mirror the real `EventSubjects` registry exported from
// packages/shared-events/src/events.ts.  Only the keys that actually exist
// in the real package are kept here: domain-specific subjects (boundary,
// crop season, field operations) are declared locally inside
// field-events.service.ts (FIELD_SUBJECTS) and do NOT go through this
// registry, so mirroring them here would only cause silent drift if a
// future test starts importing `EventSubjects.BOUNDARY_CHANGED`.
const EventSubjects = {
  FIELD_CREATED: "sahool.field.created",
  FIELD_UPDATED: "sahool.field.updated",
  FIELD_DELETED: "sahool.field.deleted",
};

module.exports = {
  EventSubjects,
  // Stubs for any other exports that may be re-exported
  publish: () => Promise.resolve(),
  subscribe: () => {},
  NatsClient: class {},
};

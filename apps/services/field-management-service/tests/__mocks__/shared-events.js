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

const EventSubjects = {
  FIELD_CREATED: "sahool.field.created",
  FIELD_UPDATED: "sahool.field.updated",
  FIELD_DELETED: "sahool.field.deleted",
  BOUNDARY_CHANGED: "sahool.field.boundary_changed",
  CROP_SEASON_STARTED: "sahool.field.crop_season.started",
  CROP_SEASON_UPDATED: "sahool.field.crop_season.updated",
  CROP_SEASON_ENDED: "sahool.field.crop_season.ended",
  CROP_SEASON_DELETED: "sahool.field.crop_season.deleted",
  FIELD_OPERATION_RECORDED: "sahool.field.operation.recorded",
  FIELD_OPERATION_UPDATED: "sahool.field.operation.updated",
  FIELD_OPERATION_DELETED: "sahool.field.operation.deleted",
};

module.exports = {
  EventSubjects,
  // Stubs for any other exports that may be re-exported
  publish: () => Promise.resolve(),
  subscribe: () => {},
  NatsClient: class {},
};

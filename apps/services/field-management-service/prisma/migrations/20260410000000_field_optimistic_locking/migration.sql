-- SAHOOL Field Management - Optimistic locking on Field.version
--
-- The `version` column was introduced in 0001_init_postgis. This migration
-- is a defensive idempotent guard that (re)creates the column with a safe
-- default if a drift is ever detected. It MUST be safe to re-apply.
--
-- drift:safe reason=idempotent-optimistic-locking

-- 1. Ensure the column exists with a sane default (no-op on fresh DBs).
ALTER TABLE "fields"
    ADD COLUMN IF NOT EXISTS "version" INTEGER NOT NULL DEFAULT 1;

-- 2. Backfill any stray NULLs (should not exist given NOT NULL above,
--    but safe in case the column was added without a default in the past).
UPDATE "fields" SET "version" = 1 WHERE "version" IS NULL;

-- 3. Ensure the auto-increment trigger exists (created in 0001_init_postgis).
--    Guard with a DO block to avoid errors if it is already present.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'increment_fields_version'
    ) THEN
        CREATE TRIGGER increment_fields_version
            BEFORE UPDATE ON "fields"
            FOR EACH ROW
            EXECUTE FUNCTION increment_version_column();
    END IF;
END
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Upgrade PgBouncer Authentication from MD5 to SCRAM-SHA-256
-- Date: 2026-01-08
-- Description: Complete migration from MD5 to SCRAM-SHA-256 authentication
--
-- BACKGROUND:
-- - PostgreSQL 16 defaults to SCRAM-SHA-256 password hashing (stronger than MD5)
-- - PgBouncer 1.21+ supports SCRAM-SHA-256 authentication
-- - SCRAM-SHA-256 provides better security through:
--   * Salted password hashing (prevents rainbow table attacks)
--   * Challenge-response authentication (prevents replay attacks)
--   * No plaintext password transmission
--
-- CHANGES REQUIRED:
-- 1. PostgreSQL: password_encryption = scram-sha-256 (already set in postgresql.conf)
-- 2. PostgreSQL: pg_hba.conf uses scram-sha-256 (already configured)
-- 3. PgBouncer: auth_type = scram-sha-256 (updated in pgbouncer.ini)
-- 4. Ensure all user passwords are SCRAM-SHA-256 encoded
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 1: Verify PostgreSQL Configuration
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    current_password_encryption TEXT;
BEGIN
    -- Check password_encryption setting
    SELECT setting INTO current_password_encryption
    FROM pg_settings
    WHERE name = 'password_encryption';

    IF current_password_encryption = 'scram-sha-256' THEN
        RAISE NOTICE '✓ PostgreSQL password_encryption is set to scram-sha-256';
    ELSE
        RAISE WARNING '⚠ PostgreSQL password_encryption is set to: %. Should be scram-sha-256',
                     current_password_encryption;
        RAISE EXCEPTION 'Please set password_encryption = scram-sha-256 in postgresql.conf and restart PostgreSQL';
    END IF;
END
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 2: Audit User Password Encryption Methods
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    user_record RECORD;
    md5_count INTEGER := 0;
    scram_count INTEGER := 0;
    null_count INTEGER := 0;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE 'User Password Encryption Audit';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';

    FOR user_record IN
        SELECT
            usename,
            CASE
                WHEN passwd IS NULL THEN 'No Password'
                WHEN passwd LIKE 'md5%' THEN 'MD5'
                WHEN passwd LIKE 'SCRAM-SHA-256%' THEN 'SCRAM-SHA-256'
                ELSE 'Unknown'
            END as encryption_method
        FROM pg_shadow
        WHERE usename NOT IN ('postgres')  -- Exclude superuser from audit
        ORDER BY usename
    LOOP
        RAISE NOTICE 'User: % | Method: %',
                     RPAD(user_record.usename, 20),
                     user_record.encryption_method;

        -- Count encryption methods
        IF user_record.encryption_method = 'MD5' THEN
            md5_count := md5_count + 1;
        ELSIF user_record.encryption_method = 'SCRAM-SHA-256' THEN
            scram_count := scram_count + 1;
        ELSIF user_record.encryption_method = 'No Password' THEN
            null_count := null_count + 1;
        END IF;
    END LOOP;

    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '  SCRAM-SHA-256 users: %', scram_count;
    RAISE NOTICE '  MD5 users: %', md5_count;
    RAISE NOTICE '  No password: %', null_count;
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';

    IF md5_count > 0 THEN
        RAISE WARNING '⚠ Found % users with MD5 passwords. These need to be reset!', md5_count;
        RAISE WARNING 'To reset passwords, run: ALTER USER <username> PASSWORD ''<new_password>'';';
        RAISE WARNING 'The new password will automatically be hashed with SCRAM-SHA-256';
    ELSE
        RAISE NOTICE '✓ All users have SCRAM-SHA-256 passwords';
    END IF;
END
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 3: Ensure PgBouncer User Has Necessary Permissions
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    -- Grant pg_monitor to sahool user (needed to read pg_shadow via get_auth function)
    IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'sahool') THEN
        GRANT pg_monitor TO sahool;
        RAISE NOTICE '✓ Granted pg_monitor to sahool user';
    END IF;

    -- Grant pg_monitor to pgbouncer user (if exists)
    IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
        GRANT pg_monitor TO pgbouncer;
        RAISE NOTICE '✓ Granted pg_monitor to pgbouncer user';
    END IF;
END
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 4: Verify pgbouncer.get_auth() Function Exists
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    function_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'pgbouncer'
        AND p.proname = 'get_auth'
    ) INTO function_exists;

    IF function_exists THEN
        RAISE NOTICE '✓ pgbouncer.get_auth() function exists';

        -- Grant execute permissions
        IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'sahool') THEN
            GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(TEXT) TO sahool;
            RAISE NOTICE '✓ Granted EXECUTE on pgbouncer.get_auth() to sahool';
        END IF;

        IF EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'pgbouncer') THEN
            GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(TEXT) TO pgbouncer;
            RAISE NOTICE '✓ Granted EXECUTE on pgbouncer.get_auth() to pgbouncer';
        END IF;
    ELSE
        RAISE WARNING '⚠ pgbouncer.get_auth() function not found';
        RAISE WARNING 'Run: infrastructure/core/postgres/init/02-pgbouncer-user.sql';
    END IF;
END
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 5: Create Helper Function to Reset User Passwords
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION pgbouncer.reset_user_password_to_scram(
    p_username TEXT,
    p_password TEXT
)
RETURNS TEXT AS $$
DECLARE
    old_method TEXT;
    new_method TEXT;
BEGIN
    -- Check current password method
    SELECT
        CASE
            WHEN passwd IS NULL THEN 'No Password'
            WHEN passwd LIKE 'md5%' THEN 'MD5'
            WHEN passwd LIKE 'SCRAM-SHA-256%' THEN 'SCRAM-SHA-256'
            ELSE 'Unknown'
        END
    INTO old_method
    FROM pg_shadow
    WHERE usename = p_username;

    IF old_method IS NULL THEN
        RETURN 'ERROR: User not found';
    END IF;

    -- Reset password (will use current password_encryption setting)
    EXECUTE format('ALTER USER %I PASSWORD %L', p_username, p_password);

    -- Verify new password method
    SELECT
        CASE
            WHEN passwd LIKE 'SCRAM-SHA-256%' THEN 'SCRAM-SHA-256'
            WHEN passwd LIKE 'md5%' THEN 'MD5'
            ELSE 'Unknown'
        END
    INTO new_method
    FROM pg_shadow
    WHERE usename = p_username;

    RETURN format('Password reset: %s -> %s', old_method, new_method);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Set search path for security
ALTER FUNCTION pgbouncer.reset_user_password_to_scram(TEXT, TEXT) SET search_path = pg_catalog;

-- Grant execute to postgres superuser only
REVOKE ALL ON FUNCTION pgbouncer.reset_user_password_to_scram(TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION pgbouncer.reset_user_password_to_scram(TEXT, TEXT) TO postgres;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 6: Final Verification
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    all_checks_passed BOOLEAN := TRUE;
    check_result RECORD;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE 'SCRAM-SHA-256 Migration Verification';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';

    -- Check 1: password_encryption
    SELECT setting = 'scram-sha-256' as passed,
           'password_encryption = scram-sha-256' as check_name,
           setting as current_value
    INTO check_result
    FROM pg_settings
    WHERE name = 'password_encryption';

    RAISE NOTICE '% %: %',
                 CASE WHEN check_result.passed THEN '✓' ELSE '✗' END,
                 check_result.check_name,
                 check_result.current_value;
    all_checks_passed := all_checks_passed AND check_result.passed;

    -- Check 2: pg_monitor role for sahool
    SELECT EXISTS (
        SELECT 1
        FROM pg_auth_members
        WHERE roleid = (SELECT oid FROM pg_roles WHERE rolname = 'pg_monitor')
        AND member = (SELECT oid FROM pg_roles WHERE rolname = 'sahool')
    ) as passed INTO check_result;

    RAISE NOTICE '% sahool has pg_monitor role',
                 CASE WHEN check_result.passed THEN '✓' ELSE '✗' END;
    all_checks_passed := all_checks_passed AND check_result.passed;

    -- Check 3: pgbouncer.get_auth() function exists
    SELECT EXISTS (
        SELECT 1
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'pgbouncer' AND p.proname = 'get_auth'
    ) as passed INTO check_result;

    RAISE NOTICE '% pgbouncer.get_auth() function exists',
                 CASE WHEN check_result.passed THEN '✓' ELSE '✗' END;
    all_checks_passed := all_checks_passed AND check_result.passed;

    -- Check 4: No MD5 passwords
    SELECT NOT EXISTS (
        SELECT 1 FROM pg_shadow
        WHERE passwd LIKE 'md5%'
        AND usename != 'postgres'
    ) as passed INTO check_result;

    RAISE NOTICE '% No MD5 passwords (excluding postgres superuser)',
                 CASE WHEN check_result.passed THEN '✓' ELSE '⚠' END;

    RAISE NOTICE '═══════════════════════════════════════════════════════════════';

    IF all_checks_passed THEN
        RAISE NOTICE '✓ SCRAM-SHA-256 migration successful!';
        RAISE NOTICE '';
        RAISE NOTICE 'Next steps:';
        RAISE NOTICE '1. Update PgBouncer configuration:';
        RAISE NOTICE '   - pgbouncer.ini: auth_type = scram-sha-256';
        RAISE NOTICE '   - docker-compose: AUTH_TYPE: scram-sha-256';
        RAISE NOTICE '2. Restart PgBouncer service';
        RAISE NOTICE '3. Test connectivity through PgBouncer';
    ELSE
        RAISE WARNING '⚠ Some checks failed. Review output above.';
    END IF;
END
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration Complete
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- USAGE EXAMPLES:
--
-- 1. Reset a user password to SCRAM-SHA-256:
--    SELECT pgbouncer.reset_user_password_to_scram('username', 'new_password');
--
-- 2. Verify all users have SCRAM passwords:
--    SELECT usename,
--           CASE WHEN passwd LIKE 'SCRAM-SHA-256%' THEN 'SCRAM' ELSE 'OTHER' END
--    FROM pg_shadow
--    WHERE usename != 'postgres';
--
-- 3. Test PgBouncer authentication:
--    psql "host=localhost port=6432 dbname=sahool user=sahool sslmode=require"
--
-- ═══════════════════════════════════════════════════════════════════════════════

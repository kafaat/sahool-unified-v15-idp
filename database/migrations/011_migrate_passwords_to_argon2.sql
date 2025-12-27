-- Migration: Add password migration tracking
-- الترحيل: إضافة تتبع ترحيل كلمات المرور

-- Add column to track which passwords need migration to Argon2id
-- إضافة عمود لتتبع كلمات المرور التي تحتاج للترحيل إلى Argon2id

BEGIN;

-- Add password migration tracking column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'password_needs_migration'
    ) THEN
        ALTER TABLE users ADD COLUMN password_needs_migration BOOLEAN DEFAULT FALSE;

        -- Add comment
        COMMENT ON COLUMN users.password_needs_migration IS
            'Flag indicating password needs migration to Argon2id on next login';
    END IF;
END $$;

-- Add index for efficient querying of users needing migration
CREATE INDEX IF NOT EXISTS idx_users_password_migration
    ON users (password_needs_migration)
    WHERE password_needs_migration = TRUE;

-- Add column to track password algorithm (for monitoring)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'password_algorithm'
    ) THEN
        ALTER TABLE users ADD COLUMN password_algorithm VARCHAR(20) DEFAULT 'argon2id';

        -- Add comment
        COMMENT ON COLUMN users.password_algorithm IS
            'Password hashing algorithm used: argon2id, bcrypt, pbkdf2_sha256';
    END IF;
END $$;

-- Flag all existing bcrypt passwords for migration
-- (bcrypt hashes start with $2a$, $2b$, or $2y$)
UPDATE users
SET
    password_needs_migration = TRUE,
    password_algorithm = 'bcrypt',
    updated_at = NOW()
WHERE
    password_hash IS NOT NULL
    AND (
        password_hash LIKE '$2a$%'
        OR password_hash LIKE '$2b$%'
        OR password_hash LIKE '$2y$%'
    )
    AND password_needs_migration = FALSE;

-- Flag all existing PBKDF2 passwords for migration
-- (PBKDF2 hashes are in format: salt$hash without $2 prefix or $argon2 prefix)
UPDATE users
SET
    password_needs_migration = TRUE,
    password_algorithm = 'pbkdf2_sha256',
    updated_at = NOW()
WHERE
    password_hash IS NOT NULL
    AND password_hash NOT LIKE '$2%'
    AND password_hash NOT LIKE '$argon2%'
    AND password_hash LIKE '%$%'
    AND password_needs_migration = FALSE;

-- Mark Argon2id passwords as not needing migration
UPDATE users
SET
    password_needs_migration = FALSE,
    password_algorithm = 'argon2id',
    updated_at = NOW()
WHERE
    password_hash IS NOT NULL
    AND password_hash LIKE '$argon2%';

-- Add trigger to automatically set password_algorithm on password update
CREATE OR REPLACE FUNCTION set_password_algorithm()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.password_hash IS NOT NULL AND NEW.password_hash != OLD.password_hash THEN
        -- Detect algorithm from hash format
        IF NEW.password_hash LIKE '$argon2%' THEN
            NEW.password_algorithm := 'argon2id';
            NEW.password_needs_migration := FALSE;
        ELSIF NEW.password_hash LIKE '$2a$%' OR
              NEW.password_hash LIKE '$2b$%' OR
              NEW.password_hash LIKE '$2y$%' THEN
            NEW.password_algorithm := 'bcrypt';
            NEW.password_needs_migration := TRUE;
        ELSIF NEW.password_hash LIKE '%$%' THEN
            NEW.password_algorithm := 'pbkdf2_sha256';
            NEW.password_needs_migration := TRUE;
        ELSE
            NEW.password_algorithm := 'unknown';
            NEW.password_needs_migration := TRUE;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS trigger_set_password_algorithm ON users;
CREATE TRIGGER trigger_set_password_algorithm
    BEFORE INSERT OR UPDATE OF password_hash ON users
    FOR EACH ROW
    EXECUTE FUNCTION set_password_algorithm();

-- Create view for monitoring migration progress
CREATE OR REPLACE VIEW password_migration_stats AS
SELECT
    password_algorithm,
    COUNT(*) as count,
    SUM(CASE WHEN password_needs_migration THEN 1 ELSE 0 END) as needs_migration,
    ROUND(100.0 * SUM(CASE WHEN password_needs_migration THEN 1 ELSE 0 END) / COUNT(*), 2) as migration_percentage
FROM users
WHERE password_hash IS NOT NULL
GROUP BY password_algorithm
ORDER BY count DESC;

-- Grant permissions
GRANT SELECT ON password_migration_stats TO PUBLIC;

COMMIT;

-- Show migration statistics
SELECT
    'Password Migration Statistics' as report,
    password_algorithm,
    count,
    needs_migration,
    migration_percentage || '%' as percentage
FROM password_migration_stats;

-- Show summary
DO $$
DECLARE
    total_users INTEGER;
    needs_migration INTEGER;
    argon2_users INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_users FROM users WHERE password_hash IS NOT NULL;
    SELECT COUNT(*) INTO needs_migration FROM users WHERE password_needs_migration = TRUE;
    SELECT COUNT(*) INTO argon2_users FROM users WHERE password_algorithm = 'argon2id';

    RAISE NOTICE '';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Password Migration Setup Complete';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Total users with passwords:        %', total_users;
    RAISE NOTICE 'Users needing migration:           %', needs_migration;
    RAISE NOTICE 'Users already on Argon2id:         %', argon2_users;
    RAISE NOTICE '';
    RAISE NOTICE 'Migration will happen automatically on next login for each user.';
    RAISE NOTICE 'Monitor progress with: SELECT * FROM password_migration_stats;';
    RAISE NOTICE '=================================================================';
END $$;

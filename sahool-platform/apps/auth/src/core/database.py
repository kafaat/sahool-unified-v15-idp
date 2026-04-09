import asyncpg
from asyncpg import Pool

# ── SQL Schema ────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS permissions (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug     TEXT NOT NULL UNIQUE,
    resource TEXT NOT NULL,
    action   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id       UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    jti        UUID PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_id  UUID NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rt_user    ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_rt_family  ON refresh_tokens(family_id);
CREATE INDEX IF NOT EXISTS idx_rt_revoked ON refresh_tokens(revoked) WHERE revoked = FALSE;

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_prt_user ON password_reset_tokens(user_id);
"""

SEED_ROLES_SQL = """
INSERT INTO roles (name) VALUES ('admin'), ('user'), ('moderator')
ON CONFLICT (name) DO NOTHING;
"""

SEED_PERMISSIONS_SQL = """
INSERT INTO permissions (slug, resource, action) VALUES
    ('users:read',   'users', 'read'),
    ('users:write',  'users', 'write'),
    ('users:delete', 'users', 'delete'),
    ('roles:assign', 'roles', 'assign')
ON CONFLICT (slug) DO NOTHING;
"""

ASSIGN_ADMIN_PERMS_SQL = """
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permissions p
WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;
"""


# ── Pool helpers ──────────────────────────────────────────────────────────────

async def create_pool(database_url: str) -> Pool:
    return await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )


async def run_migrations(pool: Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA_SQL)
        await conn.execute(SEED_ROLES_SQL)
        await conn.execute(SEED_PERMISSIONS_SQL)
        await conn.execute(ASSIGN_ADMIN_PERMS_SQL)


async def seed_admin(pool: Pool, email: str, name: str, password_hash: str) -> None:
    """Insert default admin user and assign admin role if not already present."""
    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", email
            )
            if user is None:
                user_id = await conn.fetchval(
                    """
                    INSERT INTO users (email, name, password_hash, is_active)
                    VALUES ($1, $2, $3, TRUE)
                    RETURNING id
                    """,
                    email, name, password_hash,
                )
            else:
                user_id = user["id"]

            role_id = await conn.fetchval(
                "SELECT id FROM roles WHERE name = 'admin'"
            )
            if role_id:
                await conn.execute(
                    """
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES ($1, $2)
                    ON CONFLICT DO NOTHING
                    """,
                    user_id, role_id,
                )

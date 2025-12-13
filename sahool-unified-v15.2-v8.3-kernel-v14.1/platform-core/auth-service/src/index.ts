import express, { Request, Response } from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import dotenv from "dotenv";
import { Pool } from "pg";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { v4 as uuidv4 } from "uuid";
import fs from "fs";
import { z } from "zod";

dotenv.config();

const REQUIRE_TENANT_HEADER = (process.env.REQUIRE_TENANT_HEADER || "true").toLowerCase() === "true";

const PORT = parseInt(process.env.PORT || "3001", 10);
const DATABASE_URL = process.env.DATABASE_URL || "postgresql://sahool:sahool@localhost:5432/sahool";
const JWT_ISSUER = process.env.JWT_ISSUER || "sahool";
const JWT_AUDIENCE = process.env.JWT_AUDIENCE || "sahool-clients";
const PASSWORD_PEPPER = process.env.PASSWORD_PEPPER || "change_me";
const JWT_PRIVATE_KEY_PATH = process.env.JWT_PRIVATE_KEY_PATH || "./keys/private.pem";
const JWT_PUBLIC_KEY_PATH = process.env.JWT_PUBLIC_KEY_PATH || "./keys/public.pem";

const privateKey = fs.readFileSync(JWT_PRIVATE_KEY_PATH, "utf8");
const publicKey = fs.readFileSync(JWT_PUBLIC_KEY_PATH, "utf8");

const pool = new Pool({ connectionString: DATABASE_URL });

async function initDb() {
  // Enterprise schema (multi-tenant, RBAC, sessions, API keys, audit)
  // Safe to run multiple times (IF NOT EXISTS / ADD COLUMN IF NOT EXISTS patterns)
  await pool.query(`
    CREATE TABLE IF NOT EXISTS tenants (
      id UUID PRIMARY KEY,
      slug TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      name_ar TEXT,
      is_active BOOLEAN NOT NULL DEFAULT true,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    -- default tenant (for internal dev)
    INSERT INTO tenants (id, slug, name)
    VALUES ('00000000-0000-0000-0000-000000000001','default','Default Tenant')
    ON CONFLICT (id) DO NOTHING;

    CREATE TABLE IF NOT EXISTS users (
      id UUID PRIMARY KEY,
      tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
      email TEXT NOT NULL,
      name TEXT NOT NULL,
      name_ar TEXT,
      password_hash TEXT NOT NULL,
      email_verified BOOLEAN NOT NULL DEFAULT false,
      phone TEXT,
      phone_verified BOOLEAN NOT NULL DEFAULT false,
      mfa_enabled BOOLEAN NOT NULL DEFAULT false,
      mfa_secret TEXT,
      failed_login_count INT NOT NULL DEFAULT 0,
      locked_until TIMESTAMPTZ,
      last_login_at TIMESTAMPTZ,
      deleted_at TIMESTAMPTZ,
      deleted_by UUID,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_users_tenant_email UNIQUE (tenant_id, email)
    );

    CREATE INDEX IF NOT EXISTS ix_users_tenant_email ON users (tenant_id, email);
    CREATE INDEX IF NOT EXISTS ix_users_tenant_active ON users (tenant_id, deleted_at);

    CREATE TABLE IF NOT EXISTS roles (
      id UUID PRIMARY KEY,
      tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
      name TEXT NOT NULL,
      name_ar TEXT,
      description TEXT,
      description_ar TEXT,
      deleted_at TIMESTAMPTZ,
      deleted_by UUID,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_roles_tenant_name UNIQUE (tenant_id, name)
    );
    CREATE INDEX IF NOT EXISTS ix_roles_tenant_name ON roles (tenant_id, name);

    CREATE TABLE IF NOT EXISTS permissions (
      id UUID PRIMARY KEY,
      tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE, -- NULL = system-wide
      code TEXT NOT NULL,
      name TEXT NOT NULL,
      name_ar TEXT,
      description TEXT,
      description_ar TEXT,
      deleted_at TIMESTAMPTZ,
      deleted_by UUID,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_permissions_tenant_code UNIQUE (tenant_id, code)
    );
    CREATE INDEX IF NOT EXISTS ix_permissions_tenant_code ON permissions (tenant_id, code);

    CREATE TABLE IF NOT EXISTS user_roles (
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      PRIMARY KEY (user_id, role_id)
    );

    CREATE TABLE IF NOT EXISTS role_permissions (
      role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
      permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      PRIMARY KEY (role_id, permission_id)
    );

    CREATE TABLE IF NOT EXISTS auth_sessions (
      id UUID PRIMARY KEY,
      tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      refresh_token_hash TEXT NOT NULL,
      device_id TEXT,
      device_name TEXT,
      ip TEXT,
      user_agent TEXT,
      expires_at TIMESTAMPTZ NOT NULL,
      revoked_at TIMESTAMPTZ,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_auth_sessions_user_active ON auth_sessions (user_id, revoked_at);
    CREATE INDEX IF NOT EXISTS ix_auth_sessions_tenant_user ON auth_sessions (tenant_id, user_id);

    CREATE TABLE IF NOT EXISTS api_keys (
      id UUID PRIMARY KEY,
      tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
      key_hash TEXT NOT NULL,
      name TEXT NOT NULL,
      description TEXT,
      allowed_ips TEXT[],
      created_by UUID REFERENCES users(id) ON DELETE SET NULL,
      last_used_at TIMESTAMPTZ,
      expires_at TIMESTAMPTZ,
      revoked_at TIMESTAMPTZ,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_api_keys_tenant_name ON api_keys (tenant_id, name);
    CREATE INDEX IF NOT EXISTS ix_api_keys_tenant_active ON api_keys (tenant_id, revoked_at);

    CREATE TABLE IF NOT EXISTS password_history (
      id UUID PRIMARY KEY,
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      password_hash TEXT NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_password_history_user_created ON password_history (user_id, created_at);

    CREATE TABLE IF NOT EXISTS user_oauth_providers (
      id UUID PRIMARY KEY,
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      provider TEXT NOT NULL,
      provider_user_id TEXT NOT NULL,
      access_token TEXT,
      refresh_token TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_oauth_provider_user UNIQUE (provider, provider_user_id)
    );
    CREATE INDEX IF NOT EXISTS ix_oauth_user_provider ON user_oauth_providers (user_id, provider);

    CREATE TABLE IF NOT EXISTS auth_audit_logs (
      id UUID PRIMARY KEY,
      tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
      actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
      action TEXT NOT NULL,
      resource_type TEXT,
      resource_id TEXT,
      ip TEXT,
      user_agent TEXT,
      meta JSONB,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS ix_auth_audit_tenant_created ON auth_audit_logs (tenant_id, created_at);
  `);
}


const RegisterSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
  password: z.string().min(8)
});

const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
  mfaCode: z.string().min(4).optional()
});

function getTenantId(req: Request): string {
  const tid = String(req.header("X-Tenant-Id") || "");
  if (REQUIRE_TENANT_HEADER && !tid) throw new Error("missing_tenant_header");
  return tid || "00000000-0000-0000-0000-000000000001";
}

function signToken(payload: { sub: string; tid: string; roles: string[]; email?: string; name?: string }) {
  return jwt.sign(payload, privateKey, {
    algorithm: "RS256",
    issuer: JWT_ISSUER,
    audience: JWT_AUDIENCE,
    expiresIn: "8h"
  });
}

function verifyToken(token: string) {
  return jwt.verify(token, publicKey, { algorithms: ["RS256"], issuer: JWT_ISSUER, audience: JWT_AUDIENCE });
}

const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(cors());
app.use(helmet());
app.use(morgan("combined"));

app.get("/health", async (_req: Request, res: Response) => {
  try {
    await pool.query("SELECT 1 as ok");
    return res.json({ ok: true, service: "auth-service", time: new Date().toISOString() });
  } catch (e: any) {
    return res.status(500).json({ ok: false, error: String(e?.message || e) });
  }
});

app.post("/v1/auth/register", async (req: Request, res: Response) => {
  const parsed = RegisterSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ ok: false, error: parsed.error.flatten() });

  const { email, name, password, tid } = parsed.data;
  const id = uuidv4();
  const passwordHash = await bcrypt.hash(password + PASSWORD_PEPPER, 12);

  try {
    const result = await pool.query(
      `INSERT INTO users (id, email, name, password_hash, tenant_id) VALUES ($1,$2,$3,$4,$5)
       RETURNING id, email, name, tenant_id`,
      [id, email.toLowerCase(), name, passwordHash, tid]
    );

    const user = result.rows[0];
    const token = signToken({
      sub: user.id,
      email: user.email,
      name: user.name,
      roles: ["user"],
      tid: user.tenant_id
    });

    return res.status(201).json({ ok: true, user: { id: user.id, email: user.email, name: user.name, roles: ["user"], tid: user.tenant_id }, token });
  } catch (e: any) {
    if (String(e?.message || "").includes("duplicate")) {
      return res.status(409).json({ ok: false, error: "Email already exists" });
    }
    return res.status(500).json({ ok: false, error: String(e?.message || e) });
  }
});

app.post("/v1/auth/login", async (req: Request, res: Response) => {
  const parsed = LoginSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ ok: false, error: parsed.error.flatten() });

  const { email, password } = parsed.data;
  const tenantId = getTenantId(req);
  const result = await pool.query(`SELECT id, email, name, name_ar, password_hash, tenant_id, mfa_enabled, mfa_secret, failed_login_count, locked_until, deleted_at FROM users WHERE email = $1 AND tenant_id = $2 AND deleted_at IS NULL`, [email.toLowerCase(), tenantId]);
  if (result.rowCount === 0) return res.status(401).json({ ok: false, error: "Invalid credentials" });

  const user = result.rows[0];
  const ok = await bcrypt.compare(password + PASSWORD_PEPPER, user.password_hash);
  if (!ok) return res.status(401).json({ ok: false, error: "Invalid credentials" });

  if (user.locked_until && new Date(user.locked_until).getTime() > Date.now()) {
    return res.status(423).json({ ok: false, error: "Account locked" });
  }
  if (user.mfa_enabled) {
    const mfaCode = parsed.data.mfaCode;
    if (!mfaCode || !user.mfa_secret) return res.status(401).json({ ok: false, error: "MFA required" });
    const otplib = require("otplib");
    const valid = otplib.authenticator.check(mfaCode, user.mfa_secret);
    if (!valid) return res.status(401).json({ ok: false, error: "Invalid MFA" });
  }

  const token = signToken({ sub: user.id, email: user.email, name: user.name, roles: ["user"], tid: user.tenant_id });
  return res.json({ ok: true, token, user: { id: user.id, email: user.email, name: user.name, roles: ["user"], tid: user.tenant_id } });
});

app.get("/v1/auth/verify", async (req: Request, res: Response) => {
  const header = req.header("authorization") || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : "";
  if (!token) return res.status(401).json({ ok: false, error: "Missing bearer token" });

  try {
    const payload = verifyToken(token);
    const tid = getTenantId(req);
    if (String(payload.tid) !== String(tid)) return res.status(403).json({ ok:false, error:"tenant_mismatch" });
    return res.json({ ok: true, payload });
  } catch (e: any) {
    return res.status(401).json({ ok: false, error: "Invalid token", detail: String(e?.message || e) });
  }
});

async function main() {
  await initDb();
  app.listen(PORT, () => console.log(`✅ auth-service listening on :${PORT}`));
}

main().catch((e) => {
  console.error("❌ auth-service failed to start", e);
  process.exit(1);
});

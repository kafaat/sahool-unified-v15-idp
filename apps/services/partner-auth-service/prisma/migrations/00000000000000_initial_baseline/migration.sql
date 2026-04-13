-- CreateTable
CREATE TABLE "oauth_clients" (
    "id" UUID NOT NULL,
    "client_id" VARCHAR(128) NOT NULL,
    "client_secret_hash" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "name_ar" VARCHAR(255),
    "description" TEXT,
    "homepage_url" VARCHAR(500),
    "logo_url" VARCHAR(500),
    "redirect_uris" TEXT[],
    "allowed_scopes" TEXT[],
    "api_key_hash" VARCHAR(255),
    "rate_tier" VARCHAR(32) NOT NULL DEFAULT 'starter',
    "status" VARCHAR(32) NOT NULL DEFAULT 'active',
    "contact_email" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "revoked_at" TIMESTAMPTZ,

    CONSTRAINT "oauth_clients_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_codes" (
    "id" UUID NOT NULL,
    "code_hash" VARCHAR(255) NOT NULL,
    "client_id" UUID NOT NULL,
    "user_id" VARCHAR(128) NOT NULL,
    "tenant_id" VARCHAR(128) NOT NULL,
    "redirect_uri" VARCHAR(500) NOT NULL,
    "scopes" TEXT[],
    "code_challenge" VARCHAR(255),
    "code_challenge_method" VARCHAR(16),
    "nonce" VARCHAR(255),
    "expires_at" TIMESTAMPTZ NOT NULL,
    "used_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "auth_codes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "access_tokens" (
    "jti" VARCHAR(128) NOT NULL,
    "client_id" UUID NOT NULL,
    "user_id" VARCHAR(128) NOT NULL,
    "tenant_id" VARCHAR(128) NOT NULL,
    "scopes" TEXT[],
    "expires_at" TIMESTAMPTZ NOT NULL,
    "revoked_at" TIMESTAMPTZ,
    "revoked_reason" VARCHAR(255),
    "refresh_token_id" UUID,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "access_tokens_pkey" PRIMARY KEY ("jti")
);

-- CreateTable
CREATE TABLE "refresh_tokens" (
    "id" UUID NOT NULL,
    "token_hash" VARCHAR(255) NOT NULL,
    "client_id" UUID NOT NULL,
    "user_id" VARCHAR(128) NOT NULL,
    "tenant_id" VARCHAR(128) NOT NULL,
    "scopes" TEXT[],
    "expires_at" TIMESTAMPTZ NOT NULL,
    "rotated_to_id" UUID,
    "family_id" UUID NOT NULL,
    "revoked_at" TIMESTAMPTZ,
    "revoked_reason" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "consent_grants" (
    "id" UUID NOT NULL,
    "client_id" UUID NOT NULL,
    "user_id" VARCHAR(128) NOT NULL,
    "tenant_id" VARCHAR(128) NOT NULL,
    "scopes" TEXT[],
    "accepted_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "revoked_at" TIMESTAMPTZ,
    "consent_ip" VARCHAR(64),
    "consent_user_agent" VARCHAR(500),

    CONSTRAINT "consent_grants_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "signing_keys" (
    "kid" VARCHAR(32) NOT NULL,
    "alg" VARCHAR(16) NOT NULL DEFAULT 'RS256',
    "public_pem" TEXT NOT NULL,
    "private_pem_encrypted" TEXT NOT NULL,
    "activated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "retired_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "signing_keys_pkey" PRIMARY KEY ("kid")
);

-- CreateIndex
CREATE UNIQUE INDEX "oauth_clients_client_id_key" ON "oauth_clients"("client_id");

-- CreateIndex
CREATE UNIQUE INDEX "oauth_clients_api_key_hash_key" ON "oauth_clients"("api_key_hash");

-- CreateIndex
CREATE INDEX "idx_oauth_client_status" ON "oauth_clients"("status");

-- CreateIndex
CREATE UNIQUE INDEX "auth_codes_code_hash_key" ON "auth_codes"("code_hash");

-- CreateIndex
CREATE INDEX "idx_auth_code_client_user" ON "auth_codes"("client_id", "user_id");

-- CreateIndex
CREATE INDEX "idx_auth_code_expires" ON "auth_codes"("expires_at");

-- CreateIndex
CREATE INDEX "idx_access_token_client_user" ON "access_tokens"("client_id", "user_id");

-- CreateIndex
CREATE INDEX "idx_access_token_expires" ON "access_tokens"("expires_at");

-- CreateIndex
CREATE INDEX "idx_access_token_revoked" ON "access_tokens"("revoked_at");

-- CreateIndex
CREATE UNIQUE INDEX "refresh_tokens_token_hash_key" ON "refresh_tokens"("token_hash");

-- CreateIndex
CREATE INDEX "idx_refresh_token_client_user" ON "refresh_tokens"("client_id", "user_id");

-- CreateIndex
CREATE INDEX "idx_refresh_token_family" ON "refresh_tokens"("family_id");

-- CreateIndex
CREATE INDEX "idx_refresh_token_expires" ON "refresh_tokens"("expires_at");

-- CreateIndex
CREATE UNIQUE INDEX "consent_grants_client_id_user_id_key" ON "consent_grants"("client_id", "user_id");

-- CreateIndex
CREATE INDEX "idx_signing_key_retired" ON "signing_keys"("retired_at");

-- AddForeignKey
ALTER TABLE "auth_codes" ADD CONSTRAINT "auth_codes_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "oauth_clients"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "access_tokens" ADD CONSTRAINT "access_tokens_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "oauth_clients"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "refresh_tokens" ADD CONSTRAINT "refresh_tokens_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "oauth_clients"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "consent_grants" ADD CONSTRAINT "consent_grants_client_id_fkey" FOREIGN KEY ("client_id") REFERENCES "oauth_clients"("id") ON DELETE CASCADE ON UPDATE CASCADE;


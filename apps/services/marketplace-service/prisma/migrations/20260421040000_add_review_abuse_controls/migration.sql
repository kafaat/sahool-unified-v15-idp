-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: review abuse-controls (helpful-vote + report join tables)
-- جداول الربط لمنع الإساءة في نظام التقييمات
--
-- Addresses audit items #4 and #5:
--   * markReviewHelpful previously incremented a bare counter with no join
--     table — the same user could click the button N times and push the
--     rating arbitrarily. The new `review_helpful_votes` table enforces
--     one vote per (tenant, review, user) via a composite unique. The
--     denormalised `helpful` counter on `product_reviews` is recomputed
--     from this table after every vote upsert.
--   * reportReview previously flipped `reported=true` with zero audit
--     trail (who reported, why, when). The new `review_reports` table
--     logs every report. The `product_reviews.report_count` column holds
--     the denormalised count; `reported` flips when it crosses a
--     threshold enforced in the service layer.
-- ═══════════════════════════════════════════════════════════════════════════════

-- ── 1. Add report_count column to product_reviews ─────────────────────────────
ALTER TABLE "product_reviews"
    ADD COLUMN IF NOT EXISTS "report_count" INTEGER NOT NULL DEFAULT 0;

-- ── 2. review_helpful_votes ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "review_helpful_votes" (
    "id"         UUID         NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"  VARCHAR      NOT NULL,
    "review_id"  UUID         NOT NULL,
    "user_id"    VARCHAR      NOT NULL,
    "helpful"    BOOLEAN      NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "review_helpful_votes_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "review_helpful_votes_review_id_fkey" FOREIGN KEY ("review_id")
        REFERENCES "product_reviews"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_helpful_vote_tenant_review_user"
    ON "review_helpful_votes" ("tenant_id", "review_id", "user_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_review_helpful_vote_id_tenant"
    ON "review_helpful_votes" ("id", "tenant_id");
CREATE INDEX IF NOT EXISTS "review_helpful_votes_tenant_review_idx"
    ON "review_helpful_votes" ("tenant_id", "review_id");
CREATE INDEX IF NOT EXISTS "review_helpful_votes_user_id_idx"
    ON "review_helpful_votes" ("user_id");

-- ── 3. review_reports ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "review_reports" (
    "id"               UUID         NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"        VARCHAR      NOT NULL,
    "review_id"        UUID         NOT NULL,
    "reporter_id"      VARCHAR      NOT NULL,
    "reason"           TEXT         NOT NULL,
    "acknowledged"     BOOLEAN      NOT NULL DEFAULT false,
    "acknowledged_by"  VARCHAR,
    "acknowledged_at"  TIMESTAMP(3),
    "created_at"       TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "review_reports_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "review_reports_review_id_fkey" FOREIGN KEY ("review_id")
        REFERENCES "product_reviews"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_report_tenant_review_reporter"
    ON "review_reports" ("tenant_id", "review_id", "reporter_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_review_report_id_tenant"
    ON "review_reports" ("id", "tenant_id");
CREATE INDEX IF NOT EXISTS "review_reports_tenant_review_idx"
    ON "review_reports" ("tenant_id", "review_id");
CREATE INDEX IF NOT EXISTS "review_reports_acknowledged_idx"
    ON "review_reports" ("acknowledged");

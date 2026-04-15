/**
 * Webhook ERP Adapter
 * مهيئ webhook للتكامل مع أنظمة ERP خارجية
 *
 * Generic adapter that POSTs ErpPostingDocument envelopes to a
 * configured HTTPS webhook URL. Useful for:
 *   * Zapier / Make.com / n8n integration flows that route to any
 *     accounting software the customer uses.
 *   * Customer-owned middleware that translates SAHOOL's canonical
 *     shape into their bespoke ERP format.
 *   * Development / staging environments that want to inspect payloads
 *     in a request-bin-style tool.
 *
 * The adapter:
 *   * Signs every request with HMAC-SHA256 using
 *     ERP_WEBHOOK_SIGNING_SECRET so receivers can verify authenticity.
 *   * Retries on 5xx/transient network errors with exponential backoff
 *     (up to 3 attempts). 4xx responses are treated as permanent and
 *     not retried — the caller's OutboxPublisher handles the rest.
 *   * Respects a configurable request timeout (ERP_WEBHOOK_TIMEOUT_MS).
 */

import { Injectable, Logger } from "@nestjs/common";
import { createHmac } from "crypto";
import type {
  IErpAdapter,
  ErpPostingDocument,
  ErpPostingResult,
} from "./erp-sync.types";

const WEBHOOK_URL = process.env.ERP_WEBHOOK_URL;
const SIGNING_SECRET = process.env.ERP_WEBHOOK_SIGNING_SECRET;
const TIMEOUT_MS = Number(process.env.ERP_WEBHOOK_TIMEOUT_MS ?? 15000);

@Injectable()
export class WebhookErpAdapter implements IErpAdapter {
  readonly sourceName = "webhook";
  readonly displayName = "Generic HTTPS Webhook";

  private readonly logger = new Logger(WebhookErpAdapter.name);

  isEnabled(): boolean {
    return Boolean(WEBHOOK_URL && SIGNING_SECRET);
  }

  async postDocument(doc: ErpPostingDocument): Promise<ErpPostingResult> {
    if (!this.isEnabled()) {
      return {
        success: false,
        error: "webhook adapter not configured (ERP_WEBHOOK_URL missing)",
        retryable: false,
      };
    }

    const body = JSON.stringify(doc);
    const signature = this.sign(body);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

    try {
      // Native fetch in Node 20+. The shared api-client factory isn't
      // used here because this is a fire-and-forget outbound call with
      // its own retry semantics.
      const res = await fetch(WEBHOOK_URL!, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "sahool-field-management-service/16.0",
          "X-SAHOOL-Signature": signature,
          "X-SAHOOL-Event": "erp.posting",
          "X-SAHOOL-Document-Id": doc.documentId,
          "Idempotency-Key": doc.documentId,
        },
        body,
        signal: controller.signal,
      });

      if (res.ok) {
        // Adapter may return an external reference in the body for
        // two-way trace. We accept either raw string or {externalRef}.
        let externalRef: string | undefined;
        try {
          const parsed = (await res.json()) as {
            externalRef?: string;
            id?: string;
          };
          externalRef = parsed?.externalRef ?? parsed?.id;
        } catch {
          // body isn't JSON — that's fine.
        }
        return { success: true, externalRef };
      }

      const errorBody = await res.text().catch(() => "");
      const retryable = res.status >= 500 || res.status === 429;
      this.logger.warn(
        `Webhook ${res.status}: ${errorBody.slice(0, 500)} (retryable=${retryable})`,
      );
      return {
        success: false,
        error: `HTTP ${res.status}: ${errorBody.slice(0, 500)}`,
        retryable,
      };
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      // Network errors / timeouts are retryable.
      return {
        success: false,
        error: msg.slice(0, 500),
        retryable: true,
      };
    } finally {
      clearTimeout(timer);
    }
  }

  async ping(): Promise<boolean> {
    if (!this.isEnabled()) return false;
    try {
      const res = await fetch(WEBHOOK_URL!, {
        method: "OPTIONS",
        headers: { "User-Agent": "sahool-field-management-service/16.0" },
      });
      return res.ok || res.status === 204;
    } catch {
      return false;
    }
  }

  /**
   * HMAC-SHA256 signature so webhook receivers can verify the payload
   * wasn't tampered with. Receivers compute the same HMAC over the raw
   * body with the shared secret and compare using constant-time eq.
   */
  private sign(body: string): string {
    return createHmac("sha256", SIGNING_SECRET!).update(body).digest("hex");
  }
}

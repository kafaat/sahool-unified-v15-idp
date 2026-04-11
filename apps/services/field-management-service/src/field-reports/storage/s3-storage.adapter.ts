/**
 * S3 / MinIO Report Storage Adapter
 * مهيّئ تخزين التقارير على S3 / MinIO
 *
 * Production-grade object-storage backend for rendered reports.
 * Zero third-party dependencies — uses Node's built-in `crypto` for
 * AWS Signature V4 and `fetch` (Node 20+) for HTTP. This avoids
 * pulling in the 30+ MB AWS SDK and keeps the service image small.
 *
 * Features:
 *   1. PutObject — uploads the rendered report to a tenant-scoped key
 *      like `tenants/{tenantId}/fields/{fieldId}/reports/{reportId}.html`
 *   2. Presigned GetObject — returns a short-lived signed URL
 *      (default 7 days) so the mobile/web client can fetch the report
 *      directly from S3/MinIO without routing through this service.
 *   3. Idempotency — uploading the same key twice overwrites the
 *      existing object (S3 semantics) so retries are safe.
 *
 * Environment variables:
 *   REPORT_STORAGE=s3                   # Opt-in
 *   S3_ENDPOINT=http://minio:9000        # Full URL (host + port)
 *   S3_REGION=us-east-1                  # Any value; MinIO ignores
 *   S3_BUCKET=sahool-field-reports       # Bucket must already exist
 *   S3_ACCESS_KEY=...                    # Access key
 *   S3_SECRET_KEY=...                    # Secret key
 *   S3_FORCE_PATH_STYLE=true             # true for MinIO, false for AWS
 *   S3_URL_TTL_SECONDS=604800            # Default 7 days
 *   S3_PUBLIC_ENDPOINT=...               # Optional — URL served to clients
 *
 * Security:
 *   * All keys are prefixed with the tenant id, so cross-tenant
 *     enumeration is impossible.
 *   * Presigned URLs expire after `S3_URL_TTL_SECONDS`.
 *   * Content-type is set explicitly to avoid XSS via wrong sniffing.
 */

import { createHash, createHmac } from "node:crypto";
import { Injectable, Logger } from "@nestjs/common";
import type {
  IReportStorageProvider,
  ReportUploadResult,
} from "./report-storage.provider";

interface S3Config {
  endpoint: string;
  region: string;
  bucket: string;
  accessKey: string;
  secretKey: string;
  forcePathStyle: boolean;
  urlTtlSeconds: number;
  publicEndpoint: string | null;
}

@Injectable()
export class S3ReportStorage implements IReportStorageProvider {
  readonly name = "s3";
  private readonly logger = new Logger(S3ReportStorage.name);
  private readonly config: S3Config;

  constructor() {
    this.config = this.loadConfig();
  }

  // ---------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------

  async store(args: {
    tenantId: string;
    fieldId: string;
    reportId: string;
    contentType: string;
    body: Buffer | string;
  }): Promise<ReportUploadResult> {
    const key = this.buildKey(args.tenantId, args.fieldId, args.reportId, args.contentType);
    const body =
      typeof args.body === "string" ? Buffer.from(args.body, "utf8") : args.body;
    const sizeBytes = body.length;

    await this.putObject(key, body, args.contentType);

    const expiresAt = new Date(
      Date.now() + this.config.urlTtlSeconds * 1000,
    );
    const url = this.presignGet(key, this.config.urlTtlSeconds);

    this.logger.log(
      `Uploaded report ${args.reportId} to s3://${this.config.bucket}/${key} (${sizeBytes} bytes)`,
    );

    return {
      url,
      expiresAt,
      sizeBytes,
      contentType: args.contentType,
    };
  }

  // ---------------------------------------------------------------------
  // Configuration
  // ---------------------------------------------------------------------

  private loadConfig(): S3Config {
    const endpoint = (process.env.S3_ENDPOINT ?? "http://minio:9000").replace(
      /\/+$/,
      "",
    );
    const bucket = process.env.S3_BUCKET ?? "sahool-field-reports";
    const accessKey = process.env.S3_ACCESS_KEY ?? "";
    const secretKey = process.env.S3_SECRET_KEY ?? "";
    const region = process.env.S3_REGION ?? "us-east-1";
    const forcePathStyle = (process.env.S3_FORCE_PATH_STYLE ?? "true") === "true";
    const urlTtlSeconds = Number(process.env.S3_URL_TTL_SECONDS ?? 604800);
    const publicEndpoint = process.env.S3_PUBLIC_ENDPOINT
      ? process.env.S3_PUBLIC_ENDPOINT.replace(/\/+$/, "")
      : null;

    if (!accessKey || !secretKey) {
      // We do NOT throw here because the module may be constructed at
      // boot time even when S3 isn't used. The first `store()` call
      // will fail loudly if credentials are missing.
      this.logger.warn(
        "S3ReportStorage constructed without credentials — first upload will fail",
      );
    }

    return {
      endpoint,
      region,
      bucket,
      accessKey,
      secretKey,
      forcePathStyle,
      urlTtlSeconds: Math.max(60, Math.min(urlTtlSeconds, 7 * 24 * 60 * 60)),
      publicEndpoint,
    };
  }

  // ---------------------------------------------------------------------
  // Object key layout
  // ---------------------------------------------------------------------

  private buildKey(
    tenantId: string,
    fieldId: string,
    reportId: string,
    contentType: string,
  ): string {
    const ext = this.extensionFor(contentType);
    return `tenants/${tenantId}/fields/${fieldId}/reports/${reportId}${ext}`;
  }

  private extensionFor(contentType: string): string {
    if (contentType.includes("pdf")) return ".pdf";
    if (contentType.includes("json")) return ".json";
    if (contentType.includes("html")) return ".html";
    if (contentType.includes("svg")) return ".svg";
    if (contentType.includes("csv")) return ".csv";
    return ".bin";
  }

  // ---------------------------------------------------------------------
  // PutObject with AWS SigV4
  // ---------------------------------------------------------------------

  private async putObject(
    key: string,
    body: Buffer,
    contentType: string,
  ): Promise<void> {
    const { url, host, pathname } = this.buildUrl(key);
    const now = new Date();
    const amzDate = this.amzDate(now);
    const dateStamp = amzDate.slice(0, 8);

    const payloadHash = createHash("sha256").update(body).digest("hex");

    const headers: Record<string, string> = {
      "content-type": contentType,
      host,
      "x-amz-content-sha256": payloadHash,
      "x-amz-date": amzDate,
    };

    const signedHeaders = Object.keys(headers).sort().join(";");
    const canonicalHeaders =
      Object.entries(headers)
        .map(([k, v]) => `${k.toLowerCase()}:${v.trim()}\n`)
        .sort()
        .join("") + "";

    const canonicalRequest = [
      "PUT",
      pathname,
      "", // no query
      canonicalHeaders,
      signedHeaders,
      payloadHash,
    ].join("\n");

    const credentialScope = `${dateStamp}/${this.config.region}/s3/aws4_request`;
    const stringToSign = [
      "AWS4-HMAC-SHA256",
      amzDate,
      credentialScope,
      createHash("sha256").update(canonicalRequest).digest("hex"),
    ].join("\n");

    const signingKey = this.deriveSigningKey(dateStamp);
    const signature = createHmac("sha256", signingKey)
      .update(stringToSign)
      .digest("hex");

    const authorization =
      `AWS4-HMAC-SHA256 ` +
      `Credential=${this.config.accessKey}/${credentialScope}, ` +
      `SignedHeaders=${signedHeaders}, ` +
      `Signature=${signature}`;

    const resp = await fetch(url, {
      method: "PUT",
      headers: {
        ...headers,
        authorization,
      },
      body,
    });

    if (!resp.ok) {
      const errorText = await resp.text().catch(() => "");
      throw new Error(
        `S3 PutObject failed: ${resp.status} ${resp.statusText} — ${errorText.slice(0, 500)}`,
      );
    }
  }

  // ---------------------------------------------------------------------
  // Presigned GET URL (AWS SigV4 query-string signing)
  // ---------------------------------------------------------------------

  private presignGet(key: string, expiresSeconds: number): string {
    const { host, pathname, urlForSigning } = this.buildUrl(
      key,
      /*public*/ true,
    );
    const now = new Date();
    const amzDate = this.amzDate(now);
    const dateStamp = amzDate.slice(0, 8);
    const credentialScope = `${dateStamp}/${this.config.region}/s3/aws4_request`;

    const qs = new URLSearchParams();
    qs.set("X-Amz-Algorithm", "AWS4-HMAC-SHA256");
    qs.set(
      "X-Amz-Credential",
      `${this.config.accessKey}/${credentialScope}`,
    );
    qs.set("X-Amz-Date", amzDate);
    qs.set("X-Amz-Expires", String(expiresSeconds));
    qs.set("X-Amz-SignedHeaders", "host");

    // URLSearchParams output preserves insertion order; SigV4 requires
    // query params sorted lexicographically by key.
    const sortedQs = new URLSearchParams(
      [...qs.entries()].sort(([a], [b]) => (a < b ? -1 : 1)),
    );

    const canonicalRequest = [
      "GET",
      pathname,
      sortedQs.toString(),
      `host:${host}\n`,
      "host",
      "UNSIGNED-PAYLOAD",
    ].join("\n");

    const stringToSign = [
      "AWS4-HMAC-SHA256",
      amzDate,
      credentialScope,
      createHash("sha256").update(canonicalRequest).digest("hex"),
    ].join("\n");

    const signingKey = this.deriveSigningKey(dateStamp);
    const signature = createHmac("sha256", signingKey)
      .update(stringToSign)
      .digest("hex");

    sortedQs.set("X-Amz-Signature", signature);
    return `${urlForSigning}?${sortedQs.toString()}`;
  }

  // ---------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------

  private buildUrl(
    key: string,
    usePublic = false,
  ): { url: string; host: string; pathname: string; urlForSigning: string } {
    const base = usePublic
      ? this.config.publicEndpoint ?? this.config.endpoint
      : this.config.endpoint;

    // Path-style: http://host/bucket/key
    // Virtual-hosted: http://bucket.host/key
    let fullUrl: string;
    let host: string;
    let pathname: string;

    if (this.config.forcePathStyle) {
      fullUrl = `${base}/${this.config.bucket}/${this.encodeKey(key)}`;
      host = new URL(base).host;
      pathname = `/${this.config.bucket}/${this.encodeKey(key)}`;
    } else {
      const parsed = new URL(base);
      host = `${this.config.bucket}.${parsed.host}`;
      fullUrl = `${parsed.protocol}//${host}/${this.encodeKey(key)}`;
      pathname = `/${this.encodeKey(key)}`;
    }
    return { url: fullUrl, host, pathname, urlForSigning: fullUrl };
  }

  private encodeKey(key: string): string {
    // Encode each segment but keep `/` as-is (S3 treats it as a separator).
    return key
      .split("/")
      .map((segment) => encodeURIComponent(segment))
      .join("/");
  }

  private amzDate(now: Date): string {
    // yyyymmddThhmmssZ
    return (
      now.toISOString().replace(/[:-]/g, "").split(".")[0] + "Z"
    );
  }

  private deriveSigningKey(dateStamp: string): Buffer {
    const kDate = createHmac("sha256", "AWS4" + this.config.secretKey)
      .update(dateStamp)
      .digest();
    const kRegion = createHmac("sha256", kDate)
      .update(this.config.region)
      .digest();
    const kService = createHmac("sha256", kRegion).update("s3").digest();
    const kSigning = createHmac("sha256", kService)
      .update("aws4_request")
      .digest();
    return kSigning;
  }
}

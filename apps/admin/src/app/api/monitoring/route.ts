import { NextResponse } from "next/server";

export const runtime = "nodejs";

/**
 * Sentry tunnel route handler.
 *
 * Proxies Sentry envelope POSTs from the browser SDK to Sentry's ingest
 * endpoint, preventing ad-blockers from blocking `*.sentry.io` requests.
 *
 * Configured via `tunnelRoute: "/monitoring"` in `next.config.js`.
 *
 * Reference: https://docs.sentry.io/platforms/javascript/guides/nextjs/configuration/tunneling/
 */
export async function POST(request: Request): Promise<Response> {
  try {
    const configuredDsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

    // Tunnel disabled when no DSN is configured.
    if (!configuredDsn) {
      return new NextResponse(null, { status: 204 });
    }

    const envelopeBody = await request.text();

    // A Sentry envelope is newline-delimited; the first line is a JSON
    // header containing the DSN of the originating SDK.
    const firstNewline = envelopeBody.indexOf("\n");
    const headerLine =
      firstNewline === -1 ? envelopeBody : envelopeBody.slice(0, firstNewline);

    let envelopeHeader: { dsn?: unknown };
    try {
      envelopeHeader = JSON.parse(headerLine);
    } catch {
      return NextResponse.json(
        { error: "invalid_envelope_header" },
        { status: 400 },
      );
    }

    const envelopeDsn = envelopeHeader.dsn;
    if (typeof envelopeDsn !== "string" || envelopeDsn !== configuredDsn) {
      return NextResponse.json(
        { error: "dsn_mismatch" },
        { status: 400 },
      );
    }

    // Parse the DSN to derive the ingest host and project id.
    // Sentry DSN format: https://<publicKey>@<host>/<projectId>
    let dsnUrl: URL;
    try {
      dsnUrl = new URL(envelopeDsn);
    } catch {
      return NextResponse.json(
        { error: "invalid_dsn" },
        { status: 400 },
      );
    }

    const projectId = dsnUrl.pathname.replace(/^\/+/, "");
    if (!projectId) {
      return NextResponse.json(
        { error: "invalid_dsn_project" },
        { status: 400 },
      );
    }

    const ingestPath = `/api/${projectId}/envelope/`;
    const upstreamUrl = `${dsnUrl.protocol}//${dsnUrl.host}${ingestPath}`;

    const upstreamResponse = await fetch(upstreamUrl, {
      method: "POST",
      body: envelopeBody,
      headers: {
        "Content-Type": "application/x-sentry-envelope",
      },
    });

    if (!upstreamResponse.ok) {
      return NextResponse.json(
        { error: "upstream_error" },
        { status: 502 },
      );
    }

    return NextResponse.json({ ok: true });
  } catch {
    // Swallow the error to avoid leaking stack traces to the client.
    return NextResponse.json({ error: "tunnel_failed" }, { status: 500 });
  }
}

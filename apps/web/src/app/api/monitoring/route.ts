import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(request: Request) {
  try {
    const expectedDsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

    if (!expectedDsn) {
      return new NextResponse(null, { status: 204 });
    }

    const envelope = await request.text();
    const firstNewline = envelope.indexOf("\n");
    const headerLine = firstNewline === -1 ? envelope : envelope.slice(0, firstNewline);

    const header = JSON.parse(headerLine) as { dsn?: string };
    const dsn = header?.dsn;

    if (!dsn || dsn !== expectedDsn) {
      return NextResponse.json({ error: "invalid_dsn" }, { status: 400 });
    }

    const dsnUrl = new URL(dsn);
    const projectId = dsnUrl.pathname.replace(/^\//, "");
    const sentryHost = dsnUrl.host;

    if (!projectId || !sentryHost) {
      return NextResponse.json({ error: "invalid_dsn" }, { status: 400 });
    }

    const upstream = `https://${sentryHost}/api/${projectId}/envelope/`;

    await fetch(upstream, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-sentry-envelope",
      },
      body: envelope,
    });

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: "tunnel_failed" }, { status: 500 });
  }
}

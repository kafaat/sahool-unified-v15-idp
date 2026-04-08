import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import Papa from "papaparse";

export async function GET(req: Request) {
  const session = await auth();
  if (!session?.user?.id || session.user.role !== "admin") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { searchParams } = new URL(req.url);
  const type = searchParams.get("type") ?? "usage"; // usage | audit
  const format = searchParams.get("format") ?? "csv"; // csv | pdf
  const date = searchParams.get("date") ?? new Date().toISOString().slice(0, 10);

  // Fetch data
  let rows: Record<string, unknown>[] = [];
  let filename = "";

  if (type === "usage") {
    filename = `api-usage-${date}`;
    const data = await prisma.apiUsageLog.findMany({
      where: { date },
      include: { user: { select: { email: true, name: true } } },
      orderBy: { sentinelCalls: "desc" },
    });
    rows = data.map((r) => ({
      email: r.user.email,
      name: r.user.name ?? "",
      date: r.date,
      sentinel_calls: r.sentinelCalls,
      sentinel_limit: r.sentinelLimit,
      weather_calls: r.weatherCalls,
      weather_limit: r.weatherLimit,
      total_calls: r.sentinelCalls + r.weatherCalls,
    }));
  } else {
    filename = `audit-log-${new Date().toISOString().slice(0, 10)}`;
    const data = await prisma.adminAuditLog.findMany({
      orderBy: { createdAt: "desc" },
      take: 1000,
      include: { admin: { select: { email: true } } },
    });
    rows = data.map((r) => ({
      timestamp: r.createdAt.toISOString(),
      admin_email: r.admin.email,
      action: r.action,
      target_id: r.targetId,
      meta: r.meta ?? "",
    }));
  }

  if (format === "csv") {
    const csv = Papa.unparse(rows);
    return new Response(csv, {
      headers: {
        "Content-Type": "text/csv",
        "Content-Disposition": `attachment; filename="${filename}.csv"`,
      },
    });
  }

  // PDF — basic HTML-to-text table (react-pdf is server-side but needs JSX compilation)
  // Using a simple HTML response that the browser can print as PDF
  const headers = rows.length > 0 ? Object.keys(rows[0]) : [];
  const tableRows = rows
    .map((r) => `<tr>${headers.map((h) => `<td>${String(r[h]).replace(/</g, "&lt;")}</td>`).join("")}</tr>`)
    .join("");

  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>${filename}</title>
<style>
  body { font-family: sans-serif; font-size: 11px; padding: 20px; }
  h1 { font-size: 16px; margin-bottom: 12px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #ddd; padding: 4px 8px; text-align: left; }
  th { background: #f5f5f5; font-weight: 600; }
  tr:nth-child(even) { background: #fafafa; }
  @media print { body { padding: 0; } }
</style>
</head>
<body>
<h1>${filename}</h1>
<p style="color:#666;margin-bottom:12px">Generated: ${new Date().toISOString()} · ${rows.length} rows</p>
<table>
<thead><tr>${headers.map((h) => `<th>${h}</th>`).join("")}</tr></thead>
<tbody>${tableRows}</tbody>
</table>
<script>window.onload = () => window.print();</script>
</body>
</html>`;

  return new Response(html, {
    headers: { "Content-Type": "text/html" },
  });
}

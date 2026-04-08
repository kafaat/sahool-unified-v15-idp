import { prisma } from "@/lib/prisma";
import { formatDate } from "@/lib/utils";
import Link from "next/link";

export default async function AuditPage({
  searchParams,
}: {
  searchParams: { page?: string };
}) {
  const page = Math.max(1, parseInt(searchParams.page ?? "1"));
  const pageSize = 50;

  const [logs, total] = await Promise.all([
    prisma.adminAuditLog.findMany({
      orderBy: { createdAt: "desc" },
      skip: (page - 1) * pageSize,
      take: pageSize,
      include: { admin: { select: { email: true } } },
    }),
    prisma.adminAuditLog.count(),
  ]);

  const pages = Math.ceil(total / pageSize);

  const ACTION_LABELS: Record<string, string> = {
    "user.active": "Activated user",
    "user.suspended": "Suspended user",
    "field.revoke": "Revoked field",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Audit Log <span className="text-muted-foreground text-lg font-normal">({total.toLocaleString()} entries)</span></h1>
        <div className="flex gap-2">
          <a href="/api/admin/export?type=audit&format=csv"
            className="px-4 py-1.5 border rounded-md text-sm hover:bg-muted transition-colors">
            Export CSV
          </a>
          <a href="/api/admin/export?type=audit&format=pdf"
            className="px-4 py-1.5 border rounded-md text-sm hover:bg-muted transition-colors">
            Export PDF
          </a>
        </div>
      </div>

      <div className="border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["Timestamp", "Admin", "Action", "Target ID", "Details"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium text-muted-foreground">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-t hover:bg-muted/20 transition-colors">
                <td className="px-4 py-3 text-muted-foreground text-xs">{formatDate(log.createdAt)}</td>
                <td className="px-4 py-3">{log.admin.email}</td>
                <td className="px-4 py-3">
                  <span className="font-mono text-xs bg-muted px-2 py-0.5 rounded">
                    {ACTION_LABELS[log.action] ?? log.action}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{log.targetId.slice(0, 12)}…</td>
                <td className="px-4 py-3 text-xs text-muted-foreground">
                  {log.meta ? (
                    <details>
                      <summary className="cursor-pointer hover:text-foreground">View</summary>
                      <pre className="mt-1 p-2 bg-muted rounded text-xs overflow-auto max-w-xs">
                        {JSON.stringify(JSON.parse(log.meta), null, 2)}
                      </pre>
                    </details>
                  ) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {logs.length === 0 && (
          <div className="px-4 py-8 text-center text-muted-foreground text-sm">No audit entries yet.</div>
        )}
      </div>

      {/* Pagination */}
      {pages > 1 && (
        <div className="flex gap-2 justify-center text-sm">
          {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
            <Link key={p} href={`?page=${p}`}
              className={`px-3 py-1.5 rounded-md border transition-colors ${p === page ? "bg-primary text-primary-foreground border-primary" : "hover:bg-muted"}`}>
              {p}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic"; // always fresh for live quota gauges

function QuotaBar({ used, limit }: { used: number; limit: number }) {
  const pct = Math.min(100, Math.round((used / Math.max(limit, 1)) * 100));
  const color = pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-muted-foreground w-16 text-right">{used}/{limit}</span>
    </div>
  );
}

export default async function UsagePage({
  searchParams,
}: {
  searchParams: { date?: string };
}) {
  const date = searchParams.date ?? new Date().toISOString().slice(0, 10);

  const rows = await prisma.apiUsageLog.findMany({
    where: { date },
    include: { user: { select: { email: true, name: true } } },
    orderBy: [{ sentinelCalls: "desc" }, { weatherCalls: "desc" }],
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">API Usage</h1>
        <form className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">Date:</label>
          <input type="date" name="date" defaultValue={date} max={new Date().toISOString().slice(0, 10)}
            className="px-3 py-1.5 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
          <button type="submit" className="px-4 py-1.5 bg-primary text-primary-foreground rounded-md text-sm hover:bg-primary/90 transition-colors">
            Go
          </button>
        </form>
      </div>

      <div className="border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["User", "Sentinel Hub", "OpenWeather", "Total"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium text-muted-foreground">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-t">
                <td className="px-4 py-3">
                  <div className="font-medium">{row.user.email}</div>
                  {row.user.name && <div className="text-xs text-muted-foreground">{row.user.name}</div>}
                </td>
                <td className="px-4 py-3 min-w-[160px]">
                  <QuotaBar used={row.sentinelCalls} limit={row.sentinelLimit} />
                </td>
                <td className="px-4 py-3 min-w-[160px]">
                  <QuotaBar used={row.weatherCalls} limit={row.weatherLimit} />
                </td>
                <td className="px-4 py-3 font-medium">{row.sentinelCalls + row.weatherCalls}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && (
          <div className="px-4 py-8 text-center text-muted-foreground text-sm">No usage recorded for {date}.</div>
        )}
      </div>
    </div>
  );
}

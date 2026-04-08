import { prisma } from "@/lib/prisma";
import { today } from "@/lib/utils";

export default async function DashboardPage() {
  const [userCount, fieldCount, todayUsage] = await Promise.all([
    prisma.user.count({ where: { role: "user" } }),
    prisma.field.count(),
    prisma.apiUsageLog.aggregate({
      where: { date: today() },
      _sum: { sentinelCalls: true, weatherCalls: true },
    }),
  ]);

  const last30 = await prisma.user.groupBy({
    by: ["createdAt"],
    where: { createdAt: { gte: new Date(Date.now() - 30 * 86400_000) } },
    _count: true,
  });

  const shCalls = todayUsage._sum.sentinelCalls ?? 0;
  const owCalls = todayUsage._sum.weatherCalls ?? 0;

  const stats = [
    { label: "Total users", value: userCount },
    { label: "Active fields", value: fieldCount },
    { label: "SH calls today", value: shCalls },
    { label: "OW calls today", value: owCalls },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="bg-card border rounded-xl p-5 space-y-1">
            <p className="text-sm text-muted-foreground">{s.label}</p>
            <p className="text-3xl font-bold">{s.value.toLocaleString()}</p>
          </div>
        ))}
      </div>

      <div className="bg-card border rounded-xl p-5 space-y-3">
        <h2 className="font-semibold text-sm">New registrations (last 30 days)</h2>
        <p className="text-muted-foreground text-sm">{last30.length} days with activity · {userCount} total users</p>
      </div>
    </div>
  );
}

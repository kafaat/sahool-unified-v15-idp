import { prisma } from "@/lib/prisma";
import { formatDate } from "@/lib/utils";
import UserActions from "./UserActions";

export default async function UsersPage({
  searchParams,
}: {
  searchParams: { status?: string; q?: string };
}) {
  const where: Record<string, unknown> = { role: "user" };
  if (searchParams.status && searchParams.status !== "all") where.status = searchParams.status;
  if (searchParams.q) where.email = { contains: searchParams.q };

  const users = await prisma.user.findMany({
    where,
    orderBy: { createdAt: "desc" },
    include: {
      _count: { select: { fields: true } },
      apiUsage: {
        where: { date: new Date().toISOString().slice(0, 10) },
        take: 1,
      },
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Users <span className="text-muted-foreground text-lg font-normal">({users.length})</span></h1>
      </div>

      {/* Filters */}
      <form className="flex gap-3">
        <input name="q" defaultValue={searchParams.q} placeholder="Search email…"
          className="px-3 py-1.5 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring w-56" />
        <select name="status" defaultValue={searchParams.status ?? "all"}
          className="px-3 py-1.5 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring">
          <option value="all">All statuses</option>
          <option value="active">Active</option>
          <option value="suspended">Suspended</option>
        </select>
        <button type="submit" className="px-4 py-1.5 bg-primary text-primary-foreground rounded-md text-sm hover:bg-primary/90 transition-colors">
          Filter
        </button>
      </form>

      {/* Table */}
      <div className="border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["Email", "Name", "Status", "Fields", "API calls today", "Created", "Actions"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium text-muted-foreground">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map((user) => {
              const usage = user.apiUsage[0];
              const calls = (usage?.sentinelCalls ?? 0) + (usage?.weatherCalls ?? 0);
              return (
                <tr key={user.id} className="border-t hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3 font-medium">{user.email}</td>
                  <td className="px-4 py-3 text-muted-foreground">{user.name ?? "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                      user.status === "active" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">{user._count.fields}</td>
                  <td className="px-4 py-3">{calls}</td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDate(user.createdAt)}</td>
                  <td className="px-4 py-3">
                    <UserActions userId={user.id} status={user.status} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {users.length === 0 && (
          <div className="px-4 py-8 text-center text-muted-foreground text-sm">No users found.</div>
        )}
      </div>
    </div>
  );
}

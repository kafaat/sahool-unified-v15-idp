import { prisma } from "@/lib/prisma";
import { formatDate } from "@/lib/utils";
import RevokeFieldButton from "./RevokeFieldButton";

export default async function AdminFieldsPage() {
  const fields = await prisma.field.findMany({
    orderBy: { createdAt: "desc" },
    include: { user: { select: { email: true } } },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">All Fields <span className="text-muted-foreground text-lg font-normal">({fields.length})</span></h1>
      <div className="border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              {["Name", "Owner", "Area (km²)", "Center", "Created", "Actions"].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium text-muted-foreground">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {fields.map((f) => (
              <tr key={f.id} className="border-t hover:bg-muted/20 transition-colors">
                <td className="px-4 py-3 font-medium">{f.name}</td>
                <td className="px-4 py-3 text-muted-foreground">{f.user.email}</td>
                <td className="px-4 py-3">{f.areaSqKm?.toFixed(2) ?? "—"}</td>
                <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                  {f.centerLat?.toFixed(4)}, {f.centerLng?.toFixed(4)}
                </td>
                <td className="px-4 py-3 text-muted-foreground">{formatDate(f.createdAt)}</td>
                <td className="px-4 py-3">
                  <RevokeFieldButton fieldId={f.id} fieldName={f.name} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {fields.length === 0 && (
          <div className="px-4 py-8 text-center text-muted-foreground text-sm">No fields yet.</div>
        )}
      </div>
    </div>
  );
}

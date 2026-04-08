import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import Link from "next/link";
import { parseBBox, bboxAreaKm2 } from "@/lib/bbox";
import { formatDate } from "@/lib/utils";

export default async function FieldsPage() {
  const session = await auth();
  const fields = await prisma.field.findMany({
    where: { userId: session!.user!.id },
    orderBy: { createdAt: "desc" },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">My Fields</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {fields.length} field{fields.length !== 1 ? "s" : ""}
          </p>
        </div>
        <Link
          href="/fields/new"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          + New field
        </Link>
      </div>

      {fields.length === 0 ? (
        <div className="border-2 border-dashed rounded-xl p-12 text-center space-y-3">
          <p className="text-muted-foreground">No fields yet.</p>
          <Link href="/fields/new" className="text-primary font-medium hover:underline text-sm">
            Draw your first field on the map
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {fields.map((field) => {
            const bbox = parseBBox(field.bbox);
            const area = field.areaSqKm ?? bboxAreaKm2(bbox);
            return (
              <Link
                key={field.id}
                href={`/fields/${field.id}`}
                className="group bg-card border rounded-xl p-5 hover:shadow-md transition-shadow space-y-3"
              >
                <div className="flex items-start justify-between">
                  <h2 className="font-semibold group-hover:text-primary transition-colors line-clamp-1">
                    {field.name}
                  </h2>
                  <span className="text-xs text-muted-foreground shrink-0 ml-2">
                    {area.toFixed(2)} km²
                  </span>
                </div>
                {field.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">{field.description}</p>
                )}
                <div className="text-xs text-muted-foreground">
                  {field.centerLat?.toFixed(4)}°N, {field.centerLng?.toFixed(4)}°E
                </div>
                <div className="text-xs text-muted-foreground border-t pt-2">
                  Created {formatDate(field.createdAt)}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

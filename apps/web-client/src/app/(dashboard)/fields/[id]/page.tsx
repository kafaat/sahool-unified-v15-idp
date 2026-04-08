import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { notFound } from "next/navigation";
import { parseBBox } from "@/lib/bbox";
import { formatDate } from "@/lib/utils";
import FieldDetailClient from "./FieldDetailClient";

export default async function FieldDetailPage({ params }: { params: { id: string } }) {
  const session = await auth();
  const field = await prisma.field.findFirst({
    where: { id: params.id, userId: session!.user!.id },
  });
  if (!field) notFound();

  return (
    <FieldDetailClient
      field={{
        ...field,
        bbox: parseBBox(field.bbox),
        createdAt: field.createdAt.toISOString(),
        updatedAt: field.updatedAt.toISOString(),
      }}
    />
  );
}

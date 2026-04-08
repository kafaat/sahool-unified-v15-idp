import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function DELETE(_req: Request, { params }: { params: { id: string } }) {
  const session = await auth();
  if (!session?.user?.id || session.user.role !== "admin") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }
  const field = await prisma.field.findUnique({ where: { id: params.id } });
  if (!field) return NextResponse.json({ error: "Not found" }, { status: 404 });

  await prisma.field.delete({ where: { id: params.id } });
  await prisma.adminAuditLog.create({
    data: {
      adminId: session.user.id,
      action: "field.revoke",
      targetId: params.id,
      meta: JSON.stringify({ fieldName: field.name, ownerId: field.userId }),
    },
  });
  return NextResponse.json({ success: true });
}

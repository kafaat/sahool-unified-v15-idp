import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { z } from "zod";

const patchSchema = z.object({ status: z.enum(["active", "suspended"]) });

export async function PATCH(req: Request, { params }: { params: { id: string } }) {
  const session = await auth();
  if (!session?.user?.id || session.user.role !== "admin") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }
  try {
    const { status } = patchSchema.parse(await req.json());
    await prisma.user.update({ where: { id: params.id }, data: { status } });
    await prisma.adminAuditLog.create({
      data: {
        adminId: session.user.id,
        action: `user.${status}`,
        targetId: params.id,
        meta: JSON.stringify({ changedBy: session.user.email }),
      },
    });
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "Update failed" }, { status: 500 });
  }
}

import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function GET(_req: Request, { params }: { params: { id: string } }) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const field = await prisma.field.findFirst({
    where: { id: params.id, userId: session.user.id },
  });
  if (!field) return NextResponse.json({ error: "Not found" }, { status: 404 });

  return NextResponse.json({ ...field, bbox: JSON.parse(field.bbox) });
}

export async function DELETE(_req: Request, { params }: { params: { id: string } }) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const field = await prisma.field.findFirst({
    where: { id: params.id, userId: session.user.id },
  });
  if (!field) return NextResponse.json({ error: "Not found" }, { status: 404 });

  await prisma.field.delete({ where: { id: params.id } });
  return NextResponse.json({ success: true });
}

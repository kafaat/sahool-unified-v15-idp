import { NextResponse } from "next/server";
import { z } from "zod";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { validateBBox, bboxCenter, bboxAreaKm2, serializeBBox, type BBoxArray } from "@/lib/bbox";

const createFieldSchema = z.object({
  name: z.string().min(1).max(120),
  description: z.string().max(500).optional(),
  bbox: z.tuple([z.number(), z.number(), z.number(), z.number()]),
});

export async function GET() {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const fields = await prisma.field.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(
    fields.map((f) => ({ ...f, bbox: JSON.parse(f.bbox) }))
  );
}

export async function POST(req: Request) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  try {
    const body = await req.json();
    const { name, description, bbox } = createFieldSchema.parse(body);
    const bboxArr = bbox as BBoxArray;

    const validation = validateBBox(bboxArr);
    if (!validation.valid) {
      return NextResponse.json({ error: validation.error }, { status: 400 });
    }

    const center = bboxCenter(bboxArr);
    const area = bboxAreaKm2(bboxArr);

    const field = await prisma.field.create({
      data: {
        userId: session.user.id,
        name,
        description,
        bbox: serializeBBox(bboxArr),
        centerLng: center.lng,
        centerLat: center.lat,
        areaSqKm: area,
      },
    });

    return NextResponse.json({ ...field, bbox: bboxArr }, { status: 201 });
  } catch (err) {
    if (err instanceof z.ZodError) {
      return NextResponse.json({ error: err.errors[0].message }, { status: 400 });
    }
    return NextResponse.json({ error: "Failed to create field" }, { status: 500 });
  }
}

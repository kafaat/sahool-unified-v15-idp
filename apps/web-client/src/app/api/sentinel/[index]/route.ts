import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { fetchSentinelImage, type SentinelIndex } from "@/lib/sentinel";
import { incrementUsage, isOverLimit } from "@/lib/usage";
import { parseBBox } from "@/lib/bbox";

const VALID_INDICES = new Set(["NDVI", "EVI", "NDWI", "TRUE_COLOR", "FALSE_COLOR"]);

export async function GET(
  req: Request,
  { params }: { params: { index: string } }
) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const index = params.index.toUpperCase() as SentinelIndex;
  if (!VALID_INDICES.has(index)) {
    return NextResponse.json({ error: `Invalid index. Use: ${[...VALID_INDICES].join(", ")}` }, { status: 400 });
  }

  // Check daily quota
  if (await isOverLimit(session.user.id, "sentinel")) {
    return NextResponse.json({ error: "Daily Sentinel Hub limit reached" }, { status: 429 });
  }

  const { searchParams } = new URL(req.url);
  const fieldId = searchParams.get("fieldId");
  const dateFrom = searchParams.get("from") ?? new Date(Date.now() - 30 * 86400_000).toISOString().slice(0, 10);
  const dateTo = searchParams.get("to") ?? new Date().toISOString().slice(0, 10);

  // Resolve bbox: from field record or explicit query params
  let bbox: [number, number, number, number];
  if (fieldId) {
    const field = await prisma.field.findFirst({
      where: { id: fieldId, userId: session.user.id },
    });
    if (!field) return NextResponse.json({ error: "Field not found" }, { status: 404 });
    bbox = parseBBox(field.bbox);
  } else {
    const w = parseFloat(searchParams.get("w") ?? "");
    const s = parseFloat(searchParams.get("s") ?? "");
    const e = parseFloat(searchParams.get("e") ?? "");
    const n = parseFloat(searchParams.get("n") ?? "");
    if ([w, s, e, n].some(isNaN)) {
      return NextResponse.json({ error: "Provide fieldId or w,s,e,n params" }, { status: 400 });
    }
    bbox = [w, s, e, n];
  }

  const start = Date.now();
  let statusCode = 200;

  try {
    const shRes = await fetchSentinelImage(index, bbox, dateFrom, dateTo);
    statusCode = shRes.status;

    if (!shRes.ok) {
      const text = await shRes.text();
      return NextResponse.json({ error: `Sentinel Hub error: ${text}` }, { status: shRes.status });
    }

    const imageBuffer = await shRes.arrayBuffer();

    // Log request
    await Promise.all([
      incrementUsage(session.user.id, "sentinel"),
      prisma.sentinelRequest.create({
        data: {
          userId: session.user.id,
          fieldId: fieldId ?? null,
          index,
          bbox: JSON.stringify(bbox),
          dateFrom,
          dateTo,
          statusCode,
          durationMs: Date.now() - start,
        },
      }),
    ]);

    return new Response(imageBuffer, {
      headers: {
        "Content-Type": "image/png",
        "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
        "X-SH-Index": index,
        "X-SH-Duration-Ms": String(Date.now() - start),
      },
    });
  } catch (err) {
    await prisma.sentinelRequest.create({
      data: {
        userId: session.user.id,
        fieldId: fieldId ?? null,
        index,
        bbox: JSON.stringify(bbox),
        dateFrom,
        dateTo,
        statusCode: 500,
        durationMs: Date.now() - start,
      },
    }).catch(() => {});
    return NextResponse.json({ error: "Sentinel Hub request failed" }, { status: 500 });
  }
}

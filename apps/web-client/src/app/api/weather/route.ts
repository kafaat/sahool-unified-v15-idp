import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { getCurrentWeather, getForecast, getHistorical, getAgroMonitoring } from "@/lib/weather";
import { incrementUsage, isOverLimit } from "@/lib/usage";
import { parseBBox, bboxCenter } from "@/lib/bbox";

export async function GET(req: Request) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  if (await isOverLimit(session.user.id, "weather")) {
    return NextResponse.json({ error: "Daily weather limit reached" }, { status: 429 });
  }

  const { searchParams } = new URL(req.url);
  const fieldId = searchParams.get("fieldId");
  let lat: number, lng: number;

  if (fieldId) {
    const field = await prisma.field.findFirst({
      where: { id: fieldId, userId: session.user.id },
    });
    if (!field) return NextResponse.json({ error: "Field not found" }, { status: 404 });
    const center = bboxCenter(parseBBox(field.bbox));
    lat = center.lat;
    lng = center.lng;
  } else {
    lat = parseFloat(searchParams.get("lat") ?? "");
    lng = parseFloat(searchParams.get("lng") ?? "");
    if (isNaN(lat) || isNaN(lng)) {
      return NextResponse.json({ error: "Provide fieldId or lat,lng params" }, { status: 400 });
    }
  }

  const start = Date.now();

  try {
    const [current, forecast, historical, agro] = await Promise.all([
      getCurrentWeather(lat, lng),
      getForecast(lat, lng),
      getHistorical(lat, lng),
      getAgroMonitoring(lat, lng),
    ]);

    await Promise.all([
      incrementUsage(session.user.id, "weather"),
      prisma.weatherRequest.create({
        data: {
          userId: session.user.id,
          fieldId: fieldId ?? null,
          endpoint: "all",
          lat,
          lng,
          statusCode: 200,
          durationMs: Date.now() - start,
        },
      }),
    ]);

    return NextResponse.json({ current, forecast, historical, agro });
  } catch (err) {
    await prisma.weatherRequest.create({
      data: {
        userId: session.user.id,
        fieldId: fieldId ?? null,
        endpoint: "all",
        lat,
        lng,
        statusCode: 500,
        durationMs: Date.now() - start,
      },
    }).catch(() => {});
    return NextResponse.json({ error: "Weather request failed" }, { status: 500 });
  }
}

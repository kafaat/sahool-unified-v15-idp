import { prisma } from "@/lib/prisma";

type UsageType = "sentinel" | "weather";

/** Upsert today's usage counter for a user. Call after every SH / OW proxy request. */
export async function incrementUsage(userId: string, type: UsageType) {
  const date = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  const field = type === "sentinel" ? "sentinelCalls" : "weatherCalls";

  await prisma.apiUsageLog.upsert({
    where: { userId_date: { userId, date } },
    create: { userId, date, [field]: 1 },
    update: { [field]: { increment: 1 } },
  });
}

/** Check if a user has exceeded their daily limit. Returns false if within limits. */
export async function isOverLimit(userId: string, type: UsageType): Promise<boolean> {
  const date = new Date().toISOString().slice(0, 10);
  const row = await prisma.apiUsageLog.findUnique({
    where: { userId_date: { userId, date } },
  });
  if (!row) return false;
  if (type === "sentinel") return row.sentinelCalls >= row.sentinelLimit;
  return row.weatherCalls >= row.weatherLimit;
}

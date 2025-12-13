import express, { Request, Response } from "express";
    import cors from "cors";
    import helmet from "helmet";
    import morgan from "morgan";
    import dotenv from "dotenv";
    import Redis from "ioredis";

    dotenv.config();

    const PORT = parseInt(process.env.PORT || "3020", 10);
    const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";
    const redis = new Redis(REDIS_URL);

    const app = express();
    app.use(express.json({ limit: "1mb" }));
    app.use(cors());
    app.use(helmet());
    app.use(morgan("combined"));

    app.get("/health", async (_req: Request, res: Response) => {
      try {
        await redis.ping();
        return res.json({ ok: true, service: "@sahool/crop-advisor", time: new Date().toISOString() });
      } catch (e: any) {
        return res.status(500).json({ ok: false, error: String(e?.message || e) });
      }
    });

    app.post("/v1/advice", async (req: Request, res: Response) => {
  const { fieldId = "unknown", crop = "wheat" } = (req.body || {}) as any;

  // Fetch latest signals (best-effort)
  async function latest(stream: string) {
    const items = await redis.xrevrange(stream, "+", "-", "COUNT", 1);
    if (!items?.length) return null;
    const kv = items[0][1] as string[];
    const idx = kv.findIndex((x) => x === "payload");
    if (idx >= 0 && kv[idx + 1]) return JSON.parse(kv[idx + 1]);
    return null;
  }

  const weather = await latest("signals.weather");
  const ndvi = await latest("signals.ndvi");
  const astral = await latest("signals.astral");

  const ndviVal = typeof ndvi?.ndvi === "number" ? ndvi.ndvi : null;
  const tips: string[] = [];

  if (ndviVal !== null) {
    if (ndviVal < 0.35) tips.push("NDVI منخفض: راجع الري/التسميد، وافحص الإجهاد المائي أو نقص العناصر.");
    else if (ndviVal < 0.55) tips.push("NDVI متوسط: حافظ على جدول ري منتظم وتأكد من مكافحة الآفات.");
    else tips.push("NDVI جيد: استمر، وراقب التغيرات الأسبوعية.");
  } else {
    tips.push("لا توجد قراءة NDVI حديثة: شغّل ndvi-signal أو أدخل بيانات الحقل.");
  }

  if (weather?.tempC && weather.tempC >= 32) tips.push("حرارة مرتفعة: قلل عمليات الرش في وقت الظهيرة، وفضّل الصباح الباكر.");
  if (astral?.recommendation) tips.push(String(astral.recommendation));

  const advice = {
    fieldId,
    crop,
    time: new Date().toISOString(),
    signals: { weather, ndvi, astral },
    tips
  };

  await redis.xadd("decisions.crop_advice", "*", "payload", JSON.stringify(advice));
  return res.json({ ok: true, advice });
});

    app.listen(PORT, () => console.log(`✅ @sahool/crop-advisor listening on :${PORT}`));

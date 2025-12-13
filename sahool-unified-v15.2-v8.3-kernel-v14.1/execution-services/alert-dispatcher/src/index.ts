import express, { Request, Response } from "express";
    import cors from "cors";
    import helmet from "helmet";
    import morgan from "morgan";
    import dotenv from "dotenv";
    import Redis from "ioredis";

    dotenv.config();

    const PORT = parseInt(process.env.PORT || "3031", 10);
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
        return res.json({ ok: true, service: "@sahool/alert-dispatcher", time: new Date().toISOString() });
      } catch (e: any) {
        return res.status(500).json({ ok: false, error: String(e?.message || e) });
      }
    });

    app.post("/v1/alerts", async (req: Request, res: Response) => {
  const { type = "info", message, fieldId } = (req.body || {}) as any;
  if (!message) return res.status(400).json({ ok: false, error: "message is required" });

  const alert = {
    id: `alert_${Date.now()}`,
    type,
    message,
    fieldId: fieldId || null,
    createdAt: new Date().toISOString()
  };

  await redis.xadd("execution.alerts", "*", "payload", JSON.stringify(alert));
  return res.status(201).json({ ok: true, alert });
});

app.get("/v1/alerts", async (_req: Request, res: Response) => {
  const items = await redis.xrevrange("execution.alerts", "+", "-", "COUNT", 50);
  const alerts = items.map((it) => {
    const kv = it[1] as string[];
    const idx = kv.findIndex((x) => x === "payload");
    return idx >= 0 ? JSON.parse(kv[idx + 1]) : null;
  }).filter(Boolean);
  return res.json({ ok: true, alerts });
});

    app.listen(PORT, () => console.log(`✅ @sahool/alert-dispatcher listening on :${PORT}`));

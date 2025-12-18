import express, { Request, Response } from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import dotenv from "dotenv";
import Redis from "ioredis";

dotenv.config();

const PORT = parseInt(process.env.PORT || "3011", 10);
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
    return res.json({ ok: true, service: "ndvi-signal", time: new Date().toISOString() });
  } catch (e: any) {
    return res.status(500).json({ ok: false, error: String(e?.message || e) });
  }
});

app.get("/v1/ndvi/sample", async (_req: Request, res: Response) => {
  const payload = {"fieldId": "field_123", "date": "2025-12-13", "ndvi": 0.62, "note": "sample value"};
  // publish a lightweight event
  await redis.xadd("signals.ndvi", "*", "payload", JSON.stringify(payload));
  return res.json({ ok: true, data: payload });
});

app.listen(PORT, () => console.log(`✅ ndvi-signal listening on :${PORT}`));

import express, { Request, Response } from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import dotenv from "dotenv";
import Redis from "ioredis";

dotenv.config();

const PORT = parseInt(process.env.PORT || "3010", 10);
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
    return res.json({ ok: true, service: "weather-signal", time: new Date().toISOString() });
  } catch (e: any) {
    return res.status(500).json({ ok: false, error: String(e?.message || e) });
  }
});

app.get("/v1/weather/today", async (_req: Request, res: Response) => {
  const payload = {"location": "Yemen", "summary": "Sunny to partly cloudy", "tempC": 28, "windKph": 12};
  // publish a lightweight event
  await redis.xadd("signals.weather", "*", "payload", JSON.stringify(payload));
  return res.json({ ok: true, data: payload });
});

app.listen(PORT, () => console.log(`✅ weather-signal listening on :${PORT}`));

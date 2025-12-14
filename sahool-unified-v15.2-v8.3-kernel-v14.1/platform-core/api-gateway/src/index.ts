import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import dotenv from "dotenv";
import rateLimit from "express-rate-limit";
import { createProxyMiddleware } from "http-proxy-middleware";
import Redis from "ioredis";
import jwt from "jsonwebtoken";
import fs from "fs";

dotenv.config();

const PORT = parseInt(process.env.PORT || "3000", 10);
const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || "http://localhost:3001";

const SERVICES: Record<string, string> = {
  auth: AUTH_SERVICE_URL,
  weather: process.env.WEATHER_SERVICE_URL || "http://localhost:3010",
  ndvi: process.env.NDVI_SERVICE_URL || "http://localhost:3011",
  calendar: process.env.CALENDAR_SERVICE_URL || "http://localhost:3013",
  advisor: process.env.ADVISOR_SERVICE_URL || "http://localhost:3020",
  task: process.env.TASK_SERVICE_URL || "http://localhost:3030",
  alert: process.env.ALERT_SERVICE_URL || "http://localhost:3031"
};

// Support both environment variable directly OR file path
let publicKey: string;

if (process.env.JWT_PUBLIC_KEY) {
  // Key provided directly as environment variable (preferred for security)
  publicKey = process.env.JWT_PUBLIC_KEY.replace(/\\n/g, '\n');
} else {
  // Fallback to file path (for backward compatibility)
  const JWT_PUBLIC_KEY_PATH = process.env.JWT_PUBLIC_KEY_PATH || "./keys/public.pem";
  publicKey = fs.readFileSync(JWT_PUBLIC_KEY_PATH, "utf8");
}

const redis = new Redis(REDIS_URL);

type TokenPayload = {
  sub: string;
  email: string;
  name: string;
  role: string;
  tenantId: string;
  iat?: number;
  exp?: number;
};

function requireAuth(req: Request, res: Response, next: NextFunction) {
  const auth = req.header("authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  if (!token) return res.status(401).json({ ok: false, error: "Missing bearer token" });

  try {
    const decoded = jwt.verify(token, publicKey, { algorithms: ["RS256"] }) as TokenPayload;
    (req as any).user = decoded;
    return next();
  } catch (e: any) {
    return res.status(401).json({ ok: false, error: "Invalid token", detail: String(e?.message || e) });
  }
}

const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(cors());
app.use(helmet());
app.use(morgan("combined"));

app.use(
  rateLimit({
    windowMs: 60_000,
    limit: 300,
    standardHeaders: "draft-7",
    legacyHeaders: false
  })
);

app.get("/health", async (_req: Request, res: Response) => {
  try {
    await redis.ping();
    return res.json({ ok: true, service: "api-gateway", time: new Date().toISOString(), routes: Object.keys(SERVICES) });
  } catch (e: any) {
    return res.status(500).json({ ok: false, error: String(e?.message || e) });
  }
});

// Public passthrough to auth service
app.use("/api/v1/auth", createProxyMiddleware({ target: SERVICES.auth, changeOrigin: true, pathRewrite: { "^/api/v1/auth": "/v1/auth" } }));

// Protected routes
app.use("/api/v1/weather", requireAuth, createProxyMiddleware({ target: SERVICES.weather, changeOrigin: true, pathRewrite: { "^/api/v1/weather": "" } }));
app.use("/api/v1/ndvi", requireAuth, createProxyMiddleware({ target: SERVICES.ndvi, changeOrigin: true, pathRewrite: { "^/api/v1/ndvi": "" } }));
app.use("/api/v1/calendar", requireAuth, createProxyMiddleware({ target: SERVICES.calendar, changeOrigin: true, pathRewrite: { "^/api/v1/calendar": "" } }));
app.use("/api/v1/advisor", requireAuth, createProxyMiddleware({ target: SERVICES.advisor, changeOrigin: true, pathRewrite: { "^/api/v1/advisor": "" } }));
app.use("/api/v1/tasks", requireAuth, createProxyMiddleware({ target: SERVICES.task, changeOrigin: true, pathRewrite: { "^/api/v1/tasks": "" } }));
app.use("/api/v1/alerts", requireAuth, createProxyMiddleware({ target: SERVICES.alert, changeOrigin: true, pathRewrite: { "^/api/v1/alerts": "" } }));

app.use((_req, res) => res.status(404).json({ ok: false, error: "Not Found" }));

app.listen(PORT, () => console.log(`✅ api-gateway listening on :${PORT}`));

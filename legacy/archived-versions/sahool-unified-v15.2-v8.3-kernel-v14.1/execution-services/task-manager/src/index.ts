import express, { Request, Response } from "express";
    import cors from "cors";
    import helmet from "helmet";
    import morgan from "morgan";
    import dotenv from "dotenv";
    import Redis from "ioredis";

    dotenv.config();

    const PORT = parseInt(process.env.PORT || "3030", 10);
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
        return res.json({ ok: true, service: "@sahool/task-manager", time: new Date().toISOString() });
      } catch (e: any) {
        return res.status(500).json({ ok: false, error: String(e?.message || e) });
      }
    });

    app.post("/v1/tasks", async (req: Request, res: Response) => {
  const { title, dueDate, fieldId, priority = "normal" } = (req.body || {}) as any;
  if (!title) return res.status(400).json({ ok: false, error: "title is required" });

  const task = {
    id: `task_${Date.now()}`,
    title,
    dueDate: dueDate || null,
    fieldId: fieldId || null,
    priority,
    status: "open",
    createdAt: new Date().toISOString()
  };

  await redis.xadd("execution.tasks", "*", "payload", JSON.stringify(task));
  return res.status(201).json({ ok: true, task });
});

app.get("/v1/tasks", async (_req: Request, res: Response) => {
  const items = await redis.xrevrange("execution.tasks", "+", "-", "COUNT", 50);
  const tasks = items.map((it) => {
    const kv = it[1] as string[];
    const idx = kv.findIndex((x) => x === "payload");
    return idx >= 0 ? JSON.parse(kv[idx + 1]) : null;
  }).filter(Boolean);
  return res.json({ ok: true, tasks });
});

    app.listen(PORT, () => console.log(`✅ @sahool/task-manager listening on :${PORT}`));

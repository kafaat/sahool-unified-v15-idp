import express from "express";
import client from "prom-client";

const app = express();
const port = Number(process.env.PORT || "{{port}}");
const service = process.env.SERVICE_NAME || "{{name}}";

const register = new client.Registry();
client.collectDefaultMetrics({ register });

const httpReqs = new client.Counter({
  name: "http_requests_total",
  help: "Total HTTP requests",
  labelNames: ["service", "path", "method"] as const,
});
register.registerMetric(httpReqs);

app.get("/healthz", (_req, res) => res.json({ status: "ok", service }));
app.get("/readyz", (_req, res) => res.json({ status: "ready", service }));
app.get("/metrics", async (_req, res) => {
  res.set("Content-Type", register.contentType);
  res.end(await register.metrics());
});
app.get("/", (_req, res) => {
  httpReqs.inc({ service, path: "/", method: "GET" });
  res.json({ service });
});

app.listen(port, "0.0.0.0", () =>
  console.log(`[${service}] listening on ${port}`),
);

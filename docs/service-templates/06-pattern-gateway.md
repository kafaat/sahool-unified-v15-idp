# 06 · Protocol Gateway Template

**Gold standard:** `apps/services/ws-gateway/`
**Related:** `ussd-gateway`, `whatsapp-bot-service`, `wechat-service`,
`iot-gateway`, `mcp-server`.
**Use when:** the service bridges NATS (or the core platform) to an
external protocol — WebSocket, USSD, SMS, MQTT, WhatsApp/WeChat,
Model-Context-Protocol, etc.

> قالب خدمات البوابات — ربط منصة سهول ببروتوكولات خارجية.

---

## Why `ws-gateway`?

- Canonical `NATS → WebSocket` bridge (inbound events to browser
  clients).
- JWT-authenticated rooms with tenant isolation baked in.
- Backpressure handling (slow clients get dropped, not the broker).
- Graceful drain: refuses new connections, finishes in-flight
  messages, then exits.

---

## Core responsibilities of a gateway

A gateway is **thin, stateless, and has no business logic**. It does
exactly five things:

1. **Terminate the external protocol** — upgrade HTTP to WebSocket,
   parse USSD codes, validate WhatsApp webhook signatures, etc.
2. **Authenticate / authorize the external user** against SAHOOL's
   identity service.
3. **Translate** messages between the external wire format and the
   internal NATS event format (bilingual when a human is on the other
   end).
4. **Relay** the translated messages — NATS→external or external→NATS.
5. **Track connection/session lifecycle** and expose health metrics.

If a gateway starts making DB writes or running domain logic, it's
mutated into a Pattern 02 service — move that logic into its own
service and keep the gateway thin.

---

## Canonical directory

```
apps/services/<name>-gateway/
├── Dockerfile
├── requirements.txt
├── src/
│   ├── main.py                 # FastAPI / Starlette / NestJS bootstrap
│   ├── protocol/
│   │   ├── handler.py          # the external protocol's parser/formatter
│   │   └── session.py          # per-connection state (ephemeral, in-memory)
│   ├── auth.py                 # JWT / API key / HMAC signature verification
│   ├── nats_bridge.py          # subscribe/publish helpers
│   ├── translator.py           # external ⇆ NATS payload mapping
│   └── metrics.py
└── tests/
```

---

## Key patterns

### 1 · Per-connection state is ephemeral

Never persist session state to Postgres. Use an in-process dict keyed
by `(tenant_id, user_id, connection_id)`. If the process dies, the
client reconnects and re-authenticates — **no session replay**.

If state must survive process death (e.g. partially-read USSD menu),
store it in Redis with a short TTL (<5 min).

### 2 · Tenant isolation via JWT

Every connection is authenticated on open. The extracted `tid` is
**stapled to the session object** — it must never be re-read from
subsequent client messages. A client cannot switch tenants mid-stream.

### 3 · Subject-scoped subscriptions

When bridging NATS→external, only subscribe to the tenant-scoped
subject:

```python
await nc.subscribe(f"sahool.tenant.{tenant_id}.>", cb=...)
```

Never subscribe to `sahool.>` and filter client-side — that's a
cross-tenant leak waiting to happen.

### 4 · Backpressure

Slow clients must not slow down the broker. The rule: **drop the
client, not the event**.

```python
try:
    await ws.send_json(event, timeout=2.0)
except asyncio.TimeoutError:
    logger.warning("slow_client_dropped", tenant_id=tid, client_id=cid)
    await ws.close(code=1013)   # try again later
```

### 5 · Per-connection rate limit

```python
# Token bucket: 60 inbound msgs/min per connection.
if not rate_limiter.consume(connection_id):
    await ws.send_json({"error": "rate_limited"})
    continue
```

### 6 · Graceful drain

On `SIGTERM`:

1. Stop accepting new connections (return 503 on the upgrade route).
2. Send a `{"event":"server_draining"}` advisory to every open
   connection so clients can reconnect to a different replica.
3. Wait up to `DRAIN_TIMEOUT_S` (default 30 s) for clients to close.
4. Force-close any remaining connections and `nats.drain()`.

### 7 · Metrics

Required counters / gauges:

- `gateway_connections_active{protocol, tenant}`
- `gateway_messages_inbound_total{protocol, direction="in"}`
- `gateway_messages_outbound_total{protocol, direction="out"}`
- `gateway_translate_errors_total{protocol, reason}`
- `gateway_rate_limit_drops_total{tenant}`
- `gateway_broker_lag_seconds` (histogram) — time from NATS
  publish → client receive.

---

## Delta from Pattern 02/03

| Concern | Pattern 02/03 | Gateway |
|---|---|---|
| Persistent DB | optional | **never** |
| Domain logic | yes | **never** |
| NATS | publish + subscribe | **subscribe-heavy + lightweight publish** |
| Long-lived connections | no | **yes (WS, MQTT, USSD session)** |
| Tenant state | in DB | in-process / Redis (ephemeral) |
| Scaling | horizontal, stateless | horizontal, but sticky per connection |

---

## Protocol-specific notes

### WebSocket (`ws-gateway`)

- Upgrade handler protected by rate-limit on the HTTP layer **before**
  accepting the upgrade.
- Use Starlette's `WebSocketRoute` — one coroutine per connection.
- Message framing: JSON with envelope
  `{ "type": "<event>", "tenantId", "payload": {...}, "ts": "..." }`.

### USSD (`ussd-gateway`)

- Stateful menu (tree) backed by Redis with `SESSION_TTL=180s`.
- Bilingual menus selected on the first prompt (`1=English, 2=عربي`).
- No free-text inputs without sanitization — USSD is open to the PSTN.

### WhatsApp / WeChat

- Webhook signature verification on every inbound request.
- Template messages only for business-initiated conversations (Meta
  policy).
- Media downloads proxied through MinIO so the public URL is never
  leaked back to the external provider.

### MQTT (`iot-gateway`)

- Mutual-TLS for device auth.
- Topic mapping: device `f/<device_id>/telemetry` → NATS
  `sahool.tenant.<tid>.iot.device.<device_id>.telemetry`.
- QoS 1 for commands, QoS 0 for telemetry.

### Model-Context-Protocol (`mcp-server`)

- Implements the standard MCP over stdio for AI agents.
- Every tool invocation is logged and rate-limited per (tenant, agent).

---

## Coverage matrix

| Gateway | Auth | Tenant isolation | Backpressure | Metrics | Graceful drain | Last audit |
|---|---|---|---|---|---|---|
| ws-gateway | JWT | ✅ | ✅ | ✅ | ✅ | gold |
| ussd-gateway | API key | ✅ | ⚠️ | ✅ | ✅ | — |
| whatsapp-bot-service | HMAC | ✅ | ✅ | ⚠️ | ⚠️ | — |
| wechat-service | HMAC | ✅ | ⚠️ | ⚠️ | — | — |
| iot-gateway | mTLS | ✅ | ✅ | ✅ | ✅ | — |
| mcp-server | session | ✅ | ⚠️ | ✅ | ✅ | — |

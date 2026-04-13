# 07 · Edge / IoT Orchestrator Template

**Gold standard:** `apps/services/edge-orchestrator-service/`
**Related:** `iot-service`, `drone-service`.
**Use when:** the service manages fleets of edge devices (Jetson Orin,
Raspberry Pi, drones, pivot controllers) that can be intermittently
connected and must sync state bidirectionally.

> قالب خدمات تنسيق الأجهزة الطرفية — إدارة أساطيل أجهزة Jetson
> والطائرات المسيّرة ومحطات الري مع المزامنة ثنائية الاتجاه.

---

## Why `edge-orchestrator-service`?

- Bidirectional WebSocket bridge with a backing command queue per
  device (so commands survive a disconnect).
- Model-deploy-to-edge pipeline (pushes YOLO26 weights to Jetson
  Orin).
- Hash-based integrity checks on every file transfer.
- Tenant-scoped NATS subjects: `sahool.tenant.<tid>.edge.metrics`,
  `sahool.tenant.<tid>.edge.detection`.
- Handles flapping connections without duplicating events.

---

## Key patterns

### 1 · Device identity and registration

- Every edge device has a **stable, tenant-scoped device ID** (UUID
  v4, not the hardware MAC).
- Registration is a one-time exchange:
  1. Device presents an admin-issued bootstrap token.
  2. Service mints a **device credential** (JWT with `aud=device`,
     long TTL, rotatable).
  3. Device stores the credential on secure storage (TPM, encrypted
     SD).
- Lost credential → admin revokes + device re-bootstraps.

### 2 · Command queue pattern

Edge devices are often offline. Never broadcast commands naively.
Instead, maintain a **per-device command queue** (Redis or Postgres
JSONB) and replay on reconnect:

```
client reconnects via WebSocket
  ↓
server authenticates (device JWT)
  ↓
server pops N pending commands from queue and streams them
  ↓
device ACKs each — server removes from queue
  ↓
if device disconnects before ACK, command stays pending
```

Every command carries `{commandId, issuedAt, priority, ttl}`.
Commands past their TTL are dropped to the DLQ with a bilingual
reason.

### 3 · Event de-duplication on reconnect

When a device reconnects after a network blip, it replays pending
**outbound** events too. The service must dedup by `eventId` within a
24-hour window (Redis SET with expiry).

### 4 · Model / config deployment

Downloading a 50 MB model over a flaky link? Rules:

- Transfer in **chunks** with per-chunk SHA-256.
- Verify final file hash against the registry before activation.
- Atomic swap: write to `models/<name>.new`, verify, then `mv`.
- Roll back on crash (device checks `models/<name>.prev` at boot).

### 5 · Telemetry batching

Don't send a NATS event per sensor reading — the gateway should batch:

```
device pushes {readings: [...]}        (every 30 s, 100 readings)
  ↓
orchestrator validates + normalizes
  ↓
orchestrator publishes ONE NATS event
  `sahool.tenant.<tid>.edge.metrics.batch`
  with the reading array
```

This keeps NATS throughput linear in fleet size, not reading rate.

### 6 · Offline mode contract

Every edge service must document a clear **offline-mode contract**:

- What does the device do when NATS is unreachable? (Store locally,
  flush on reconnect.)
- What does the server do when the device is unreachable? (Queue
  commands, flag `device_offline` alert after N minutes.)
- What are the sync conflict rules? (Last-write-wins?
  Device-wins-for-measurements, server-wins-for-config?)

### 7 · Drone-specific additions (for `drone-service`)

- Flight plans are versioned and signed — the drone rejects any plan
  that doesn't verify.
- No-fly zones enforced server-side via PostGIS — reject any plan
  that intersects an NFZ.
- Telemetry (altitude, battery, GPS) streamed over a separate high-
  frequency channel; commands over the main command channel.

### 8 · Metrics

- `edge_devices_connected{tenant}`
- `edge_command_queue_depth{device}`
- `edge_model_deploy_bytes_total{device, model}`
- `edge_model_deploy_failures_total{device, reason}`
- `edge_reconnect_total{device}` — spikes indicate a flaky link
- `edge_offline_duration_seconds` (histogram)

---

## Delta from Pattern 02/06

Edge orchestrators are a **gateway (Pattern 06) with persistent state**:

| Concern | Pattern 06 Gateway | Pattern 07 Edge Orchestrator |
|---|---|---|
| Persistent DB | never | **yes — device registry, command queue, deploy history** |
| Long-lived connections | yes | yes |
| Command replay on reconnect | no | **yes, per device** |
| File transfer | no | yes (model / config deploys) |
| Offline-mode contract | n/a | **mandatory** |

---

## Coverage matrix

| Service | Device registry | Command queue | Model deploy | Telemetry batching | Offline contract |
|---|---|---|---|---|---|
| edge-orchestrator-service | ✅ gold | ✅ | ✅ | ✅ | ✅ |
| iot-service | ⚠️ (via device table) | — | — | ✅ (MQTT→NATS) | partial |
| drone-service | ✅ | — | — | — | — |

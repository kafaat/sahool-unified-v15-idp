/**
 * SAHOOL Mock WebSocket Server
 * خادم محاكاة للأحداث المباشرة (ws-gateway)
 */

const http = require("http");
const crypto = require("crypto");

// WebSocket implementation (minimal)
function parseWebSocketFrame(buffer) {
  const firstByte = buffer[0];
  const opcode = firstByte & 0x0f;

  const secondByte = buffer[1];
  const isMasked = Boolean(secondByte & 0x80);
  let payloadLength = secondByte & 0x7f;

  let offset = 2;
  if (payloadLength === 126) {
    payloadLength = buffer.readUInt16BE(2);
    offset += 2;
  } else if (payloadLength === 127) {
    payloadLength = Number(buffer.readBigUInt64BE(2));
    offset += 8;
  }

  let maskKey;
  if (isMasked) {
    maskKey = buffer.slice(offset, offset + 4);
    offset += 4;
  }

  let payload = buffer.slice(offset, offset + payloadLength);
  if (isMasked) {
    for (let i = 0; i < payload.length; i++) {
      payload[i] ^= maskKey[i % 4];
    }
  }

  return { opcode, payload: payload.toString("utf8") };
}

function createWebSocketFrame(data) {
  const payload = Buffer.from(data);
  const length = payload.length;

  let frame;
  if (length <= 125) {
    frame = Buffer.alloc(2 + length);
    frame[0] = 0x81; // Text frame
    frame[1] = length;
    payload.copy(frame, 2);
  } else if (length <= 65535) {
    frame = Buffer.alloc(4 + length);
    frame[0] = 0x81;
    frame[1] = 126;
    frame.writeUInt16BE(length, 2);
    payload.copy(frame, 4);
  } else {
    frame = Buffer.alloc(10 + length);
    frame[0] = 0x81;
    frame[1] = 127;
    frame.writeBigUInt64BE(BigInt(length), 2);
    payload.copy(frame, 10);
  }

  return frame;
}

// Mock events
const eventTypes = [
  {
    type: "task_created",
    payload: () => ({ title: "مهمة جديدة: ري الحقل", field_id: "field_001" }),
  },
  {
    type: "task_completed",
    payload: () => ({ title: "تم إكمال: فحص المحاصيل", field_id: "field_002" }),
  },
  {
    type: "ndvi_processed",
    payload: () => ({
      field_id: "field_00" + (Math.floor(Math.random() * 4) + 1),
      ndvi: (Math.random() * 0.5 + 0.3).toFixed(2),
      status: Math.random() > 0.5 ? "healthy" : "warning",
    }),
  },
  {
    type: "weather_alert_issued",
    payload: () => ({
      type: "موجة حارة",
      severity: "warning",
      location: "صنعاء",
    }),
  },
  {
    type: "image_diagnosed",
    payload: () => ({
      disease_detected: Math.random() > 0.7,
      confidence: (Math.random() * 0.3 + 0.7).toFixed(2),
      disease: "البياض الدقيقي",
    }),
  },
  {
    type: "sensor_reading",
    payload: () => ({
      sensor_id: "sensor_001",
      value: Math.floor(Math.random() * 100),
      type: "soil_moisture",
    }),
  },
];

const clients = new Set();

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("SAHOOL WebSocket Server - Use WebSocket connection on /events");
});

server.on("upgrade", (req, socket, head) => {
  if (req.url === "/events") {
    // WebSocket handshake
    const key = req.headers["sec-websocket-key"];
    const acceptKey = crypto
      .createHash("sha1")
      .update(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
      .digest("base64");

    socket.write(
      "HTTP/1.1 101 Switching Protocols\r\n" +
        "Upgrade: websocket\r\n" +
        "Connection: Upgrade\r\n" +
        `Sec-WebSocket-Accept: ${acceptKey}\r\n` +
        "\r\n",
    );

    clients.add(socket);
    console.log(`[WS] Client connected. Total clients: ${clients.size}`);

    // Send welcome message
    const welcomeMsg = JSON.stringify({
      type: "connected",
      message: "مرحباً بك في خادم الأحداث المباشرة",
    });
    socket.write(createWebSocketFrame(welcomeMsg));

    socket.on("data", (buffer) => {
      try {
        const { opcode, payload } = parseWebSocketFrame(buffer);

        if (opcode === 8) {
          // Close frame
          clients.delete(socket);
          socket.end();
          return;
        }

        if (opcode === 9) {
          // Ping - respond with pong
          const pongFrame = Buffer.alloc(2);
          pongFrame[0] = 0x8a;
          pongFrame[1] = 0;
          socket.write(pongFrame);
          return;
        }

        if (opcode === 1 && payload) {
          const message = JSON.parse(payload);
          console.log("[WS] Received:", message);

          if (message.type === "subscribe") {
            const response = JSON.stringify({
              type: "subscribed",
              subjects: message.subjects,
            });
            socket.write(createWebSocketFrame(response));
          } else if (message.type === "pong") {
            // Client responded to our ping
          }
        }
      } catch (e) {
        console.error("[WS] Error parsing message:", e.message);
      }
    });

    socket.on("close", () => {
      clients.delete(socket);
      console.log(`[WS] Client disconnected. Total clients: ${clients.size}`);
    });

    socket.on("error", (err) => {
      clients.delete(socket);
      console.error("[WS] Socket error:", err.message);
    });
  } else {
    socket.destroy();
  }
});

// Broadcast events periodically
setInterval(() => {
  if (clients.size === 0) return;

  const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
  const event = {
    type: "event",
    data: {
      event_id: `evt_${Date.now()}`,
      event_type: eventType.type,
      aggregate_id: `agg_${Math.random().toString(36).substr(2, 9)}`,
      tenant_id: "tenant_1",
      timestamp: new Date().toISOString(),
      payload: eventType.payload(),
    },
  };

  const frame = createWebSocketFrame(JSON.stringify(event));

  for (const client of clients) {
    try {
      client.write(frame);
    } catch (e) {
      clients.delete(client);
    }
  }

  console.log(`[WS] Broadcasted event: ${eventType.type}`);
}, 10000); // Every 10 seconds

const PORT = process.env.WS_PORT || 8081;
server.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║          SAHOOL Mock WebSocket Server                            ║
║          خادم محاكاة الأحداث المباشرة (ws-gateway)                ║
╠══════════════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                                        ║
║  URL:  ws://localhost:${PORT}/events                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Events Simulated:                                               ║
║    ✓ task_created      - إنشاء مهمة                              ║
║    ✓ task_completed    - إكمال مهمة                              ║
║    ✓ ndvi_processed    - تحليل NDVI                              ║
║    ✓ weather_alert     - تنبيهات الطقس                           ║
║    ✓ image_diagnosed   - تشخيص الصور                             ║
║    ✓ sensor_reading    - قراءات المستشعرات                       ║
╚══════════════════════════════════════════════════════════════════╝
  `);
});

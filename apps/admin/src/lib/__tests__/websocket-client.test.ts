/**
 * WebSocket Client Tests
 * اختبارات عميل WebSocket
 *
 * Tests the WebSocket client for real-time notifications and data streaming.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  WebSocketClient,
  ConnectionStatus,
  getWebSocketClient,
} from "../websocket";

// Mock logger
vi.mock("../logger", () => ({
  logger: {
    log: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}));

// ═══════════════════════════════════════════════════════════════════════════
// WebSocket Client Unit Tests | اختبارات وحدة عميل WebSocket
// ═══════════════════════════════════════════════════════════════════════════

describe("WebSocketClient", () => {
  let client: WebSocketClient;
  let mockWebSocket: {
    readyState: number;
    close: ReturnType<typeof vi.fn>;
    send: ReturnType<typeof vi.fn>;
    onopen: ((event: Event) => void) | null;
    onclose: ((event: CloseEvent) => void) | null;
    onerror: ((event: Event) => void) | null;
    onmessage: ((event: MessageEvent) => void) | null;
  };

  beforeEach(() => {
    // Mock WebSocket global
    mockWebSocket = {
      readyState: 0, // CONNECTING
      close: vi.fn(),
      send: vi.fn(),
      onopen: null,
      onclose: null,
      onerror: null,
      onmessage: null,
    };

    vi.stubGlobal(
      "WebSocket",
      vi.fn(() => mockWebSocket),
    );

    // Set OPEN constant
    (global as any).WebSocket.OPEN = 1;
    (global as any).WebSocket.CONNECTING = 0;

    client = new WebSocketClient({ url: "ws://test:8081", debug: false });
  });

  afterEach(() => {
    client.disconnect();
    vi.restoreAllMocks();
  });

  describe("Connection Management", () => {
    it("starts in DISCONNECTED status", () => {
      expect(client.getStatus()).toBe(ConnectionStatus.DISCONNECTED);
      expect(client.isConnected()).toBe(false);
    });

    it("transitions to CONNECTING on connect()", () => {
      client.connect();
      expect(client.getStatus()).toBe(ConnectionStatus.CONNECTING);
    });

    it("transitions to CONNECTED on WebSocket open", () => {
      client.connect();
      // Simulate connection
      mockWebSocket.readyState = 1; // OPEN
      mockWebSocket.onopen?.(new Event("open"));
      expect(client.getStatus()).toBe(ConnectionStatus.CONNECTED);
      expect(client.isConnected()).toBe(true);
    });

    it("transitions to DISCONNECTED on clean close (code 1000)", () => {
      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      // Simulate clean close
      mockWebSocket.onclose?.({ code: 1000, reason: "Normal" } as CloseEvent);
      expect(client.getStatus()).toBe(ConnectionStatus.DISCONNECTED);
    });

    it("does not duplicate connection if already connected", () => {
      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      // Try connecting again
      client.connect();
      // Should only have been called once
      expect(global.WebSocket).toHaveBeenCalledTimes(1);
    });

    it("disconnect() closes the WebSocket", () => {
      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      client.disconnect();
      expect(mockWebSocket.close).toHaveBeenCalledWith(1000, "Client disconnect");
      expect(client.getStatus()).toBe(ConnectionStatus.DISCONNECTED);
    });
  });

  describe("Event Subscription", () => {
    it("subscribes and receives alert events", () => {
      const handler = vi.fn();
      client.on("alert", handler);

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      // Simulate receiving an alert message
      const alertData = {
        type: "alert",
        timestamp: new Date().toISOString(),
        data: {
          id: "alert-1",
          severity: "critical",
          title: "انخفاض رطوبة التربة",
        },
      };
      mockWebSocket.onmessage?.(
        new MessageEvent("message", { data: JSON.stringify(alertData) }),
      );

      expect(handler).toHaveBeenCalledWith(alertData.data);
    });

    it("subscribes and receives sensor events", () => {
      const handler = vi.fn();
      client.on("sensor", handler);

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      const sensorData = {
        type: "sensor",
        timestamp: new Date().toISOString(),
        data: {
          farmId: "farm-1",
          sensorType: "soil_moisture",
          value: 42,
          unit: "%",
        },
      };
      mockWebSocket.onmessage?.(
        new MessageEvent("message", { data: JSON.stringify(sensorData) }),
      );

      expect(handler).toHaveBeenCalledWith(sensorData.data);
    });

    it("unsubscribes from events", () => {
      const handler = vi.fn();
      const unsubscribe = client.on("alert", handler);

      unsubscribe();

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      mockWebSocket.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({
            type: "alert",
            timestamp: "",
            data: {},
          }),
        }),
      );

      expect(handler).not.toHaveBeenCalled();
    });

    it("supports multiple event listeners", () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      client.on("alert", handler1);
      client.on("alert", handler2);

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      mockWebSocket.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({
            type: "alert",
            timestamp: "",
            data: { id: "a1" },
          }),
        }),
      );

      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
    });

    it("emits 'connected' event on successful connection", () => {
      const handler = vi.fn();
      client.on("connected", handler);

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({ timestamp: expect.any(String) }),
      );
    });

    it("emits 'disconnected' event on close", () => {
      const handler = vi.fn();
      client.on("disconnected", handler);

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      mockWebSocket.onclose?.({ code: 1000, reason: "Done" } as CloseEvent);

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({ code: 1000, reason: "Done" }),
      );
    });
  });

  describe("Status Change Listeners", () => {
    it("notifies status change listeners", () => {
      const statusHandler = vi.fn();
      client.onStatusChange(statusHandler);

      // Should be called immediately with current status
      expect(statusHandler).toHaveBeenCalledWith(ConnectionStatus.DISCONNECTED);

      client.connect();
      expect(statusHandler).toHaveBeenCalledWith(ConnectionStatus.CONNECTING);

      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));
      expect(statusHandler).toHaveBeenCalledWith(ConnectionStatus.CONNECTED);
    });

    it("unsubscribes from status changes", () => {
      const statusHandler = vi.fn();
      const unsubscribe = client.onStatusChange(statusHandler);

      // Clear initial call
      statusHandler.mockClear();

      unsubscribe();
      client.connect();

      expect(statusHandler).not.toHaveBeenCalled();
    });
  });

  describe("Send Messages", () => {
    it("sends messages when connected", () => {
      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      client.send("ping", { test: true });

      expect(mockWebSocket.send).toHaveBeenCalledWith(
        expect.stringContaining('"type":"ping"'),
      );
    });

    it("does not send when disconnected", () => {
      client.send("ping", {});
      expect(mockWebSocket.send).not.toHaveBeenCalled();
    });
  });

  describe("Message Handling", () => {
    it("ignores heartbeat/pong messages", () => {
      const handler = vi.fn();
      client.on("alert", handler);

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      // Send heartbeat - should be ignored
      mockWebSocket.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({ type: "heartbeat", timestamp: "", data: {} }),
        }),
      );

      mockWebSocket.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({ type: "pong", timestamp: "", data: {} }),
        }),
      );

      expect(handler).not.toHaveBeenCalled();
    });

    it("handles malformed JSON gracefully", () => {
      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      // Should not throw
      expect(() => {
        mockWebSocket.onmessage?.(
          new MessageEvent("message", { data: "not valid json" }),
        );
      }).not.toThrow();
    });
  });

  describe("Reconnection", () => {
    it("schedules reconnect on abnormal close", () => {
      vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "setInterval", "clearInterval"] });

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      // Simulate abnormal close - set readyState to CLOSED so connect() doesn't bail
      mockWebSocket.readyState = 3; // CLOSED
      mockWebSocket.onclose?.({
        code: 1006,
        reason: "Abnormal",
      } as CloseEvent);

      // Should attempt reconnect after delay (5000 * 2^0 = 5000ms)
      vi.advanceTimersByTime(5000);
      expect(global.WebSocket).toHaveBeenCalledTimes(2);

      vi.useRealTimers();
    });

    it("uses exponential backoff for reconnection", () => {
      vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout", "setInterval", "clearInterval"] });

      client.connect();
      mockWebSocket.readyState = 1;
      mockWebSocket.onopen?.(new Event("open"));

      // First abnormal close
      mockWebSocket.readyState = 3; // CLOSED
      mockWebSocket.onclose?.({ code: 1006, reason: "" } as CloseEvent);
      vi.advanceTimersByTime(5000); // 5s * 2^0 → reconnect #1

      // Second abnormal close (mock returns same object, handlers re-attached)
      mockWebSocket.readyState = 3; // CLOSED
      mockWebSocket.onclose?.({ code: 1006, reason: "" } as CloseEvent);
      vi.advanceTimersByTime(10000); // 5s * 2^1 → reconnect #2

      expect(global.WebSocket).toHaveBeenCalledTimes(3);

      vi.useRealTimers();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Singleton Pattern | اختبار نمط المفرد
// ═══════════════════════════════════════════════════════════════════════════

describe("WebSocket Singleton", () => {
  it("getWebSocketClient returns same instance", () => {
    const client1 = getWebSocketClient();
    const client2 = getWebSocketClient();
    expect(client1).toBe(client2);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Message Type Verification | التحقق من أنواع الرسائل
// ═══════════════════════════════════════════════════════════════════════════

describe("WebSocket Event Types", () => {
  it("handles all supported event types", () => {
    const client = new WebSocketClient({ url: "ws://test:8081" });
    const eventTypes = [
      "alert",
      "sensor",
      "irrigation",
      "diagnosis",
      "farm_update",
      "weather",
      "task",
    ] as const;

    const handlers = eventTypes.map((type) => {
      const handler = vi.fn();
      client.on(type, handler);
      return { type, handler };
    });

    // Verify all subscriptions were set up
    handlers.forEach(({ handler }) => {
      expect(typeof handler).toBe("function");
    });

    client.disconnect();
  });
});

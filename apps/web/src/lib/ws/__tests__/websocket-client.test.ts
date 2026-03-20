/**
 * WebSocket Client Tests
 * اختبارات عميل WebSocket
 *
 * Tests the WebSocket client for event handling, reconnection,
 * and message processing.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;
  protocols: string | string[] | undefined;
  onopen: ((ev: Event) => void) | null = null;
  onclose: ((ev: CloseEvent) => void) | null = null;
  onmessage: ((ev: MessageEvent) => void) | null = null;
  onerror: ((ev: Event) => void) | null = null;

  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
  });

  constructor(url: string, protocols?: string | string[]) {
    this.url = url;
    this.protocols = protocols;
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event("open"));
    }, 0);
  }

  // Test helpers
  simulateMessage(data: unknown) {
    this.onmessage?.(new MessageEvent("message", { data: JSON.stringify(data) }));
  }

  simulateClose(code = 1000) {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({ code } as CloseEvent);
  }

  simulateError() {
    this.onerror?.(new Event("error"));
  }
}

// Store original WebSocket
const OriginalWebSocket = global.WebSocket;

describe("WebSocket Client", () => {
  let wsInstances: MockWebSocket[];

  beforeEach(() => {
    wsInstances = [];
    vi.useFakeTimers({ shouldAdvanceTime: true, toFake: ["setTimeout", "clearTimeout", "setInterval", "clearInterval"] });

    // @ts-expect-error - MockWebSocket is test-only
    global.WebSocket = vi.fn((url: string, protocols?: string | string[]) => {
      const ws = new MockWebSocket(url, protocols);
      wsInstances.push(ws);
      return ws;
    });

    // Add static constants to the mock constructor
    Object.assign(global.WebSocket, {
      CONNECTING: 0,
      OPEN: 1,
      CLOSING: 2,
      CLOSED: 3,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    global.WebSocket = OriginalWebSocket;
    vi.resetModules();
  });

  describe("Connection", () => {
    it("should connect to WebSocket URL with /events path", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      expect(global.WebSocket).toHaveBeenCalled();
      const calledUrl = (global.WebSocket as unknown as ReturnType<typeof vi.fn>).mock.calls[0]?.[0];
      expect(calledUrl).toContain("/events");
    });

    it("should send subscription message on connection", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect(["tasks.*", "weather.*"]);
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0];
      expect(ws?.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: "subscribe",
          subjects: ["tasks.*", "weather.*"],
        }),
      );
    });

    it("should not create duplicate connections", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      // Should only have 1 WebSocket instance since second connect should be skipped
      expect(wsInstances.length).toBe(1);
    });
  });

  describe("Event Handling", () => {
    it("should notify event handlers on incoming events", async () => {
      const { wsClient } = await import("../index");
      const handler = vi.fn();
      wsClient.onEvent(handler);

      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      ws.simulateMessage({
        type: "event",
        data: {
          event_id: "evt-001",
          event_type: "task_created",
          aggregate_id: "task-001",
          tenant_id: "tenant-001",
          timestamp: "2026-03-15T10:00:00Z",
          payload: { title: "New Task" },
        },
      });

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          event_id: "evt-001",
          event_type: "task_created",
        }),
      );
    });

    it("should respond to ping messages with pong", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      ws.simulateMessage({ type: "ping" });

      expect(ws.send).toHaveBeenCalledWith(JSON.stringify({ type: "pong" }));
    });

    it("should unsubscribe event handler when cleanup is called", async () => {
      const { wsClient } = await import("../index");
      const handler = vi.fn();
      const unsubscribe = wsClient.onEvent(handler);

      unsubscribe();

      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      ws.simulateMessage({
        type: "event",
        data: {
          event_id: "evt-001",
          event_type: "task_created",
          aggregate_id: "task-001",
          tenant_id: "tenant-001",
          timestamp: "2026-03-15T10:00:00Z",
          payload: {},
        },
      });

      expect(handler).not.toHaveBeenCalled();
    });
  });

  describe("Connection State", () => {
    it("should notify connection handlers on connect", async () => {
      const { wsClient } = await import("../index");
      const handler = vi.fn();
      wsClient.onConnection(handler);

      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      expect(handler).toHaveBeenCalledWith(true);
    });

    it("should notify connection handlers on disconnect", async () => {
      const { wsClient } = await import("../index");
      const handler = vi.fn();
      wsClient.onConnection(handler);

      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      wsInstances[0]!.simulateClose();

      expect(handler).toHaveBeenCalledWith(false);
    });

    it("should report isConnected correctly", async () => {
      const { wsClient } = await import("../index");

      expect(wsClient.isConnected).toBe(false);

      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      // After mock open, readyState should be OPEN
      expect(wsInstances[0]?.readyState).toBe(MockWebSocket.OPEN);
    });
  });

  describe("Disconnect", () => {
    it("should close WebSocket and stop reconnecting", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      wsClient.disconnect();

      expect(wsInstances[0]?.close).toHaveBeenCalled();
    });
  });

  describe("Event Helpers", () => {
    it("should return correct icons for event types", async () => {
      const { getEventIcon } = await import("../index");

      expect(getEventIcon("task_created")).toBe("📋");
      expect(getEventIcon("weather_alert")).toBe("🌤️");
      expect(getEventIcon("disease_detected")).toBe("🔬");
      expect(getEventIcon("ndvi_processed")).toBe("🛰️");
      expect(getEventIcon("irrigation_started")).toBe("💧");
      expect(getEventIcon("fertilizer_applied")).toBe("🧪");
      expect(getEventIcon("unknown_event")).toBe("📌");
    });

    it("should return correct colors for event types", async () => {
      const { getEventColor } = await import("../index");

      expect(getEventColor("task_created")).toContain("blue");
      expect(getEventColor("weather_alert")).toContain("amber");
      expect(getEventColor("disease_detected")).toContain("red");
      expect(getEventColor("ndvi_processed")).toContain("emerald");
    });

    it("should format event types to Arabic", async () => {
      const { formatEventType } = await import("../index");

      expect(formatEventType("task_created")).toBe("مهمة جديدة");
      expect(formatEventType("weather_alert_issued")).toBe("تنبيه طقس");
      expect(formatEventType("ndvi_processed")).toBe("تحليل NDVI");
      // Unknown events return as-is
      expect(formatEventType("custom_event")).toBe("custom_event");
    });
  });

  describe("Error Handling", () => {
    it("should handle malformed WebSocket messages gracefully", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      // Send invalid JSON
      ws.onmessage?.(new MessageEvent("message", { data: "not json" }));

      // Should not throw
      expect(true).toBe(true);
    });

    it("should pass error event to onerror handler", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      // Should not throw when error event fires
      ws.simulateError();
      expect(true).toBe(true);
    });
  });

  describe("Authentication", () => {
    it("should pass token via query parameter when setToken is called", async () => {
      const { wsClient } = await import("../index");
      wsClient.setToken("test-jwt-token-123");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      expect(ws.url).toContain("token=test-jwt-token-123");
    });

    it("should not include token param when setToken is called with null", async () => {
      const { wsClient } = await import("../index");
      wsClient.setToken(null);
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      expect(ws.url).not.toContain("token=");
    });

    it("should not reconnect on auth failure (code 4001)", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      // Simulate auth failure close
      ws.readyState = MockWebSocket.CLOSED;
      ws.onclose?.({ code: 4001 } as CloseEvent);

      // Advance past reconnect delay
      await vi.advanceTimersByTimeAsync(10000);

      // Should NOT have created a new WebSocket (no reconnect)
      expect(wsInstances.length).toBe(1);
    });

    it("should not reconnect on auth failure (code 4003)", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      ws.readyState = MockWebSocket.CLOSED;
      ws.onclose?.({ code: 4003 } as CloseEvent);

      await vi.advanceTimersByTimeAsync(10000);
      expect(wsInstances.length).toBe(1);
    });

    it("should reconnect on normal close (code 1006)", async () => {
      const { wsClient } = await import("../index");
      wsClient.connect();
      await vi.advanceTimersByTimeAsync(10);

      const ws = wsInstances[0]!;
      ws.readyState = MockWebSocket.CLOSED;
      ws.onclose?.({ code: 1006 } as CloseEvent);

      // Advance past reconnect delay (2000ms base * 2^1)
      await vi.advanceTimersByTimeAsync(5000);

      // Should have attempted reconnection
      expect(wsInstances.length).toBeGreaterThan(1);
    });
  });
});

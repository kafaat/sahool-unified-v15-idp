/**
 * useWebSocket Hook Tests
 * اختبارات هوك WebSocket
 *
 * Tests authentication, reconnection, error handling,
 * and message buffering for the useWebSocket hook.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useWebSocket } from "../useWebSocket";

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;
  protocol: string = "";
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
    this.readyState = MockWebSocket.CONNECTING;
  }

  simulateOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.(new Event("open"));
  }

  simulateClose(code = 1000) {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({ code } as CloseEvent);
  }

  simulateError() {
    this.onerror?.(new Event("error"));
  }

  simulateMessage(data: unknown) {
    this.onmessage?.(
      new MessageEvent("message", { data: JSON.stringify(data) }),
    );
  }
}

// Mock logger
vi.mock("../../lib/logger", () => ({
  logger: {
    log: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

const OriginalWebSocket = global.WebSocket;

describe("useWebSocket", () => {
  let wsInstances: MockWebSocket[];

  beforeEach(() => {
    wsInstances = [];
    vi.useFakeTimers({
      shouldAdvanceTime: true,
      toFake: ["setTimeout", "clearTimeout", "setInterval", "clearInterval"],
    });

    // @ts-expect-error - MockWebSocket is test-only
    global.WebSocket = vi.fn((url: string, protocols?: string | string[]) => {
      const ws = new MockWebSocket(url, protocols);
      wsInstances.push(ws);
      return ws;
    });

    Object.assign(global.WebSocket, {
      CONNECTING: 0,
      OPEN: 1,
      CLOSING: 2,
      CLOSED: 3,
    });

    // Mock document.hidden for tab visibility
    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => false,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    global.WebSocket = OriginalWebSocket;
    vi.resetAllMocks();
  });

  describe("Connection", () => {
    it("should connect when enabled", () => {
      renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081", enabled: true }),
      );

      expect(wsInstances.length).toBe(1);
    });

    it("should not connect when disabled", () => {
      renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081", enabled: false }),
      );

      expect(wsInstances.length).toBe(0);
    });

    it("should set isConnected to true on open", () => {
      const { result } = renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081" }),
      );

      expect(result.current.isConnected).toBe(false);

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      expect(result.current.isConnected).toBe(true);
    });
  });

  describe("Authentication", () => {
    it("should pass token via Sec-WebSocket-Protocol subprotocol", () => {
      renderHook(() =>
        useWebSocket({
          url: "ws://localhost:8081",
          token: "my-jwt-token",
        }),
      );

      expect(wsInstances[0]?.url).not.toContain("token=");
      expect(wsInstances[0]?.protocols).toEqual([
        "v1.sahool.events",
        "auth.my-jwt-token",
      ]);
    });

    it("should not pass protocols when token is null", () => {
      renderHook(() =>
        useWebSocket({
          url: "ws://localhost:8081",
          token: null,
        }),
      );

      expect(wsInstances[0]?.protocols).toBeUndefined();
    });

    it("should not leak token in URL", () => {
      renderHook(() =>
        useWebSocket({
          url: "ws://localhost:8081",
          token: "secret-token",
        }),
      );

      expect(wsInstances[0]?.url).not.toContain("secret-token");
    });

    it("should set error on auth failure close (code 4001)", () => {
      const { result } = renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081", token: "bad-token" }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      act(() => {
        wsInstances[0]?.simulateClose(4001);
      });

      expect(result.current.error).toBe("Authentication failed");
      expect(result.current.isConnected).toBe(false);
    });

    it("should not auto-reconnect on auth failure", async () => {
      renderHook(() =>
        useWebSocket({
          url: "ws://localhost:8081",
          token: "expired-token",
          reconnectInterval: 1000,
        }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      act(() => {
        wsInstances[0]?.simulateClose(4001);
      });

      // Advance past reconnect interval
      await vi.advanceTimersByTimeAsync(5000);

      // Should NOT have created additional WebSocket connections
      expect(wsInstances.length).toBe(1);
    });
  });

  describe("Error Handling", () => {
    it("should set error state on WebSocket error", () => {
      const { result } = renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081" }),
      );

      act(() => {
        wsInstances[0]?.simulateError();
      });

      expect(result.current.error).toBe("Connection unavailable");
    });
  });

  describe("Message Handling", () => {
    it("should call onMessage for incoming messages", () => {
      const onMessage = vi.fn();
      renderHook(() =>
        useWebSocket({
          url: "ws://localhost:8081",
          onMessage,
        }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      act(() => {
        wsInstances[0]?.simulateMessage({
          type: "event",
          data: { event_id: "1" },
        });
      });

      expect(onMessage).toHaveBeenCalledWith(
        expect.objectContaining({ type: "event" }),
      );
    });

    it("should handle pong messages without calling onMessage", () => {
      const onMessage = vi.fn();
      renderHook(() =>
        useWebSocket({
          url: "ws://localhost:8081",
          onMessage,
        }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      act(() => {
        wsInstances[0]?.simulateMessage({ type: "pong" });
      });

      expect(onMessage).not.toHaveBeenCalled();
    });
  });

  describe("Send and Buffer", () => {
    it("should send message when connected", () => {
      const { result } = renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081" }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      act(() => {
        result.current.send({ type: "test" });
      });

      expect(wsInstances[0]?.send).toHaveBeenCalledWith(
        JSON.stringify({ type: "test" }),
      );
    });
  });

  describe("Disconnect", () => {
    it("should close WebSocket on disconnect", () => {
      const { result } = renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081" }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      act(() => {
        result.current.disconnect();
      });

      expect(wsInstances[0]?.close).toHaveBeenCalled();
    });

    it("should not reconnect after manual disconnect", async () => {
      const { result } = renderHook(() =>
        useWebSocket({
          url: "ws://localhost:8081",
          reconnectInterval: 1000,
        }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      act(() => {
        result.current.disconnect();
      });

      await vi.advanceTimersByTimeAsync(5000);

      // Should only have the original connection
      expect(wsInstances.length).toBe(1);
    });
  });

  describe("Cleanup", () => {
    it("should close WebSocket on unmount", () => {
      const { unmount } = renderHook(() =>
        useWebSocket({ url: "ws://localhost:8081" }),
      );

      act(() => {
        wsInstances[0]?.simulateOpen();
      });

      unmount();

      expect(wsInstances[0]?.close).toHaveBeenCalled();
    });
  });
});

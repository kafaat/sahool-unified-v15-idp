import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useWebSocket } from './useWebSocket';
import type { WSMessage } from './useWebSocket';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  public url: string;
  public readyState: number = MockWebSocket.CONNECTING;
  public onopen: ((event: Event) => void) | null = null;
  public onclose: ((event: CloseEvent) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 0);
  }

  send(data: string) {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close'));
  }

  // Test helper to simulate receiving a message
  simulateMessage(data: unknown) {
    const event = new MessageEvent('message', {
      data: JSON.stringify(data),
    });
    this.onmessage?.(event);
  }

  // Test helper to simulate an error
  simulateError() {
    this.onerror?.(new Event('error'));
  }
}

describe('useWebSocket', () => {
  let mockWebSocketInstances: MockWebSocket[] = [];

  beforeEach(() => {
    mockWebSocketInstances = [];
    vi.useFakeTimers();

    // Mock WebSocket constructor
    global.WebSocket = vi.fn((url: string) => {
      const instance = new MockWebSocket(url);
      mockWebSocketInstances.push(instance);
      return instance as unknown as WebSocket;
    }) as unknown as typeof WebSocket;
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.restoreAllMocks();
  });

  describe('connection management', () => {
    it('should establish connection on mount', async () => {
      const onConnect = vi.fn();
      const { result } = renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          onConnect,
        })
      );

      expect(result.current.isConnected).toBe(false);

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(result.current.isConnected).toBe(true);
      expect(onConnect).toHaveBeenCalledTimes(1);
    });

    it('should not connect when enabled is false', async () => {
      const onConnect = vi.fn();
      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          onConnect,
          enabled: false,
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(onConnect).not.toHaveBeenCalled();
      expect(mockWebSocketInstances).toHaveLength(0);
    });

    it('should disconnect on unmount', async () => {
      const { result, unmount } = renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(result.current.isConnected).toBe(true);

      const closeSpy = vi.spyOn(mockWebSocketInstances[0], 'close');
      unmount();

      expect(closeSpy).toHaveBeenCalled();
    });
  });

  describe('message handling', () => {
    it('should handle incoming messages', async () => {
      const onMessage = vi.fn();
      const testMessage: WSMessage = {
        type: 'test',
        payload: { data: 'hello' },
      };

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          onMessage,
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      act(() => {
        mockWebSocketInstances[0].simulateMessage(testMessage);
      });

      expect(onMessage).toHaveBeenCalledWith(testMessage);
    });

    it('should handle malformed messages gracefully', async () => {
      const onMessage = vi.fn();
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          onMessage,
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      // Simulate receiving invalid JSON
      act(() => {
        const event = new MessageEvent('message', {
          data: 'invalid json',
        });
        mockWebSocketInstances[0].onmessage?.(event);
      });

      expect(onMessage).not.toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });

    it('should send messages when connected', async () => {
      const { result } = renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      const sendSpy = vi.spyOn(mockWebSocketInstances[0], 'send');
      const testData = { type: 'test', payload: 'data' };

      act(() => {
        result.current.send(testData);
      });

      expect(sendSpy).toHaveBeenCalledWith(JSON.stringify(testData));
    });

    it('should not send messages when not connected', () => {
      const { result } = renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
        })
      );

      // Try to send before connection is established
      expect(() => {
        act(() => {
          result.current.send({ test: 'data' });
        });
      }).not.toThrow();
    });
  });

  describe('error handling', () => {
    it('should handle connection errors', async () => {
      const onError = vi.fn();
      const { result } = renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          onError,
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      act(() => {
        mockWebSocketInstances[0].simulateError();
      });

      expect(onError).toHaveBeenCalled();
      expect(result.current.error).toBe('Connection error');
    });
  });

  describe('reconnection logic', () => {
    it('should reconnect with exponential backoff', async () => {
      const onDisconnect = vi.fn();
      const reconnectInterval = 1000; // 1 second base interval

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          reconnectInterval,
          maxReconnectAttempts: 5,
          onDisconnect,
        })
      );

      // Initial connection
      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(mockWebSocketInstances).toHaveLength(1);

      // Simulate disconnect
      act(() => {
        mockWebSocketInstances[0].close();
      });

      expect(onDisconnect).toHaveBeenCalledTimes(1);

      // First reconnection attempt: delay = 1000 * 1.5^0 = 1000ms
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1000);
      });
      expect(mockWebSocketInstances).toHaveLength(2);

      // Disconnect again
      act(() => {
        mockWebSocketInstances[1].close();
      });

      // Second reconnection attempt: delay = 1000 * 1.5^1 = 1500ms
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1500);
      });
      expect(mockWebSocketInstances).toHaveLength(3);

      // Disconnect again
      act(() => {
        mockWebSocketInstances[2].close();
      });

      // Third reconnection attempt: delay = 1000 * 1.5^2 = 2250ms
      await act(async () => {
        await vi.advanceTimersByTimeAsync(2250);
      });
      expect(mockWebSocketInstances).toHaveLength(4);
    });

    it('should cap backoff delay at MAX_RECONNECT_DELAY (30 seconds)', async () => {
      const reconnectInterval = 5000; // 5 seconds base interval

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          reconnectInterval,
          maxReconnectAttempts: 20,
        })
      );

      // Initial connection
      await act(async () => {
        await vi.runAllTimersAsync();
      });

      // Simulate multiple disconnections to reach high exponential values
      // After 10 attempts: 5000 * 1.5^10 = 288,626ms (> 30,000ms)
      // Should be capped at 30,000ms

      for (let i = 0; i < 10; i++) {
        act(() => {
          mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
        });

        const expectedDelay = Math.min(
          reconnectInterval * Math.pow(1.5, i),
          30000
        );

        await act(async () => {
          await vi.advanceTimersByTimeAsync(expectedDelay);
        });
      }

      expect(mockWebSocketInstances).toHaveLength(11); // Initial + 10 reconnections

      // Next reconnection should use max delay (30 seconds)
      act(() => {
        mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
      });

      // Should not reconnect before 30 seconds
      await act(async () => {
        await vi.advanceTimersByTimeAsync(29999);
      });
      expect(mockWebSocketInstances).toHaveLength(11);

      // Should reconnect at 30 seconds
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1);
      });
      expect(mockWebSocketInstances).toHaveLength(12);
    });

    it('should stop reconnecting after maxReconnectAttempts', async () => {
      const maxReconnectAttempts = 3;
      const reconnectInterval = 1000;

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          reconnectInterval,
          maxReconnectAttempts,
        })
      );

      // Initial connection
      await act(async () => {
        await vi.runAllTimersAsync();
      });

      // Simulate disconnections up to max attempts
      for (let i = 0; i < maxReconnectAttempts; i++) {
        act(() => {
          mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
        });

        await act(async () => {
          const delay = Math.min(
            reconnectInterval * Math.pow(1.5, i),
            30000
          );
          await vi.advanceTimersByTimeAsync(delay);
        });
      }

      expect(mockWebSocketInstances).toHaveLength(1 + maxReconnectAttempts);

      // Disconnect one more time
      act(() => {
        mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
      });

      // Should not attempt to reconnect
      await act(async () => {
        await vi.advanceTimersByTimeAsync(10000);
      });

      expect(mockWebSocketInstances).toHaveLength(1 + maxReconnectAttempts);
    });

    it('should reset reconnect attempts after successful connection', async () => {
      const onConnect = vi.fn();
      const reconnectInterval = 1000;

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          reconnectInterval,
          maxReconnectAttempts: 5,
          onConnect,
        })
      );

      // Initial connection
      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(onConnect).toHaveBeenCalledTimes(1);

      // Disconnect and reconnect twice
      for (let i = 0; i < 2; i++) {
        act(() => {
          mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
        });

        await act(async () => {
          const delay = reconnectInterval * Math.pow(1.5, i);
          await vi.advanceTimersByTimeAsync(delay);
        });
      }

      expect(mockWebSocketInstances).toHaveLength(3);
      expect(onConnect).toHaveBeenCalledTimes(3);

      // After successful reconnection, attempts should reset
      // Next disconnect should use the base delay again
      act(() => {
        mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
      });

      // Should use base interval (1000ms) not exponential
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1000);
      });

      expect(mockWebSocketInstances).toHaveLength(4);
    });
  });

  describe('manual control', () => {
    it('should manually disconnect', async () => {
      const { result } = renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(result.current.isConnected).toBe(true);

      act(() => {
        result.current.disconnect();
      });

      expect(result.current.isConnected).toBe(false);

      // Should not auto-reconnect
      await act(async () => {
        await vi.advanceTimersByTimeAsync(10000);
      });

      expect(mockWebSocketInstances).toHaveLength(1);
    });

    it('should manually reconnect', async () => {
      const { result } = renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
        })
      );

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(result.current.isConnected).toBe(true);
      expect(mockWebSocketInstances).toHaveLength(1);

      act(() => {
        result.current.reconnect();
      });

      await act(async () => {
        await vi.runAllTimersAsync();
      });

      expect(mockWebSocketInstances).toHaveLength(2);
      expect(result.current.isConnected).toBe(true);
    });
  });

  describe('backoff calculation tests', () => {
    it('should calculate correct delays for first 5 attempts', async () => {
      const reconnectInterval = 1000;
      const expectedDelays = [
        1000,  // 1000 * 1.5^0
        1500,  // 1000 * 1.5^1
        2250,  // 1000 * 1.5^2
        3375,  // 1000 * 1.5^3
        5062,  // 1000 * 1.5^4 (rounded)
      ];

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          reconnectInterval,
          maxReconnectAttempts: 10,
        })
      );

      // Initial connection
      await act(async () => {
        await vi.runAllTimersAsync();
      });

      for (let i = 0; i < expectedDelays.length; i++) {
        const initialCount = mockWebSocketInstances.length;

        act(() => {
          mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
        });

        // Should not reconnect before expected delay
        await act(async () => {
          await vi.advanceTimersByTimeAsync(expectedDelays[i] - 1);
        });
        expect(mockWebSocketInstances).toHaveLength(initialCount);

        // Should reconnect at expected delay
        await act(async () => {
          await vi.advanceTimersByTimeAsync(1);
        });
        expect(mockWebSocketInstances).toHaveLength(initialCount + 1);
      }
    });

    it('should verify MAX_RECONNECT_DELAY is enforced', async () => {
      const reconnectInterval = 10000; // 10 seconds
      // After 5 attempts: 10000 * 1.5^5 = 75,937ms (> 30,000ms)

      renderHook(() =>
        useWebSocket({
          url: 'ws://localhost:3000',
          reconnectInterval,
          maxReconnectAttempts: 10,
        })
      );

      // Initial connection
      await act(async () => {
        await vi.runAllTimersAsync();
      });

      // Go through 5 reconnections to exceed MAX_RECONNECT_DELAY
      for (let i = 0; i < 5; i++) {
        act(() => {
          mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
        });

        const expectedDelay = Math.min(
          reconnectInterval * Math.pow(1.5, i),
          30000
        );

        await act(async () => {
          await vi.advanceTimersByTimeAsync(expectedDelay);
        });
      }

      // Next attempt should be capped at 30 seconds
      act(() => {
        mockWebSocketInstances[mockWebSocketInstances.length - 1].close();
      });

      // Should not reconnect at the uncapped delay (75,937ms)
      await act(async () => {
        await vi.advanceTimersByTimeAsync(30000);
      });

      // Should have reconnected at 30 seconds (the cap)
      expect(mockWebSocketInstances).toHaveLength(7); // Initial + 6 reconnections
    });
  });
});

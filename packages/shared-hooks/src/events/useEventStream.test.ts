import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  useEventStream,
  useNDVIStream,
  useAlertStream,
  useWeatherStream,
} from './useEventStream';
import type { ReactNode } from 'react';

// Create wrapper with QueryClient
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe('useEventStream', () => {
  let mockEventSource: {
    onmessage: ((event: MessageEvent) => void) | null;
    onerror: ((event: Event) => void) | null;
    onopen: ((event: Event) => void) | null;
    close: ReturnType<typeof vi.fn>;
    readyState: number;
  };

  beforeEach(() => {
    vi.useFakeTimers();
    mockEventSource = {
      onmessage: null,
      onerror: null,
      onopen: null,
      close: vi.fn(),
      readyState: 0,
    };

    global.EventSource = vi.fn(() => mockEventSource) as unknown as typeof EventSource;
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('should connect to event stream when enabled', () => {
    renderHook(
      () =>
        useEventStream({
          url: '/api/events/ndvi',
          enabled: true,
          onMessage: vi.fn(),
        }),
      { wrapper: createWrapper() }
    );

    expect(global.EventSource).toHaveBeenCalledWith('/api/events/ndvi');
  });

  it('should not connect when disabled', () => {
    renderHook(
      () =>
        useEventStream({
          url: '/api/events/ndvi',
          enabled: false,
          onMessage: vi.fn(),
        }),
      { wrapper: createWrapper() }
    );

    expect(global.EventSource).not.toHaveBeenCalled();
  });

  it('should call onMessage when receiving data', async () => {
    const onMessage = vi.fn();
    const testData = { fieldId: '123', ndvi: 0.75 };

    renderHook(
      () =>
        useEventStream({
          url: '/api/events/ndvi',
          enabled: true,
          onMessage,
        }),
      { wrapper: createWrapper() }
    );

    // Simulate message
    act(() => {
      mockEventSource.onmessage?.(
        new MessageEvent('message', { data: JSON.stringify(testData) })
      );
    });

    expect(onMessage).toHaveBeenCalledWith(testData);
  });

  it('should call onError when connection fails', async () => {
    const onError = vi.fn();

    renderHook(
      () =>
        useEventStream({
          url: '/api/events/ndvi',
          enabled: true,
          onMessage: vi.fn(),
          onError,
        }),
      { wrapper: createWrapper() }
    );

    // Simulate error
    act(() => {
      mockEventSource.onerror?.(new Event('error'));
    });

    expect(onError).toHaveBeenCalled();
  });

  it('should close connection on unmount', () => {
    const { unmount } = renderHook(
      () =>
        useEventStream({
          url: '/api/events/ndvi',
          enabled: true,
          onMessage: vi.fn(),
        }),
      { wrapper: createWrapper() }
    );

    unmount();

    expect(mockEventSource.close).toHaveBeenCalled();
  });

  it('should reconnect with exponential backoff on error', async () => {
    const onError = vi.fn();

    renderHook(
      () =>
        useEventStream({
          url: '/api/events/ndvi',
          enabled: true,
          onMessage: vi.fn(),
          onError,
          reconnect: true,
          maxRetries: 3,
        }),
      { wrapper: createWrapper() }
    );

    // Initial connection
    expect(global.EventSource).toHaveBeenCalledTimes(1);

    // Simulate first error
    act(() => {
      mockEventSource.onerror?.(new Event('error'));
    });

    // Wait for first reconnect (1000ms base delay)
    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(global.EventSource).toHaveBeenCalledTimes(2);
  });
});

describe('useNDVIStream', () => {
  beforeEach(() => {
    global.EventSource = vi.fn(() => ({
      onmessage: null,
      onerror: null,
      onopen: null,
      close: vi.fn(),
      readyState: 1,
    })) as unknown as typeof EventSource;
  });

  it('should connect to NDVI endpoint with fieldId', () => {
    renderHook(() => useNDVIStream('field-123'), { wrapper: createWrapper() });

    expect(global.EventSource).toHaveBeenCalledWith(
      expect.stringContaining('/api/events/ndvi')
    );
  });

  it('should not connect without fieldId', () => {
    renderHook(() => useNDVIStream(''), { wrapper: createWrapper() });

    expect(global.EventSource).not.toHaveBeenCalled();
  });
});

describe('useAlertStream', () => {
  beforeEach(() => {
    global.EventSource = vi.fn(() => ({
      onmessage: null,
      onerror: null,
      onopen: null,
      close: vi.fn(),
      readyState: 1,
    })) as unknown as typeof EventSource;
  });

  it('should connect to alerts endpoint', () => {
    renderHook(() => useAlertStream(), { wrapper: createWrapper() });

    expect(global.EventSource).toHaveBeenCalledWith(
      expect.stringContaining('/api/events/alerts')
    );
  });

  it('should filter by severity when provided', () => {
    renderHook(() => useAlertStream({ severity: 'critical' }), {
      wrapper: createWrapper(),
    });

    expect(global.EventSource).toHaveBeenCalledWith(
      expect.stringContaining('severity=critical')
    );
  });
});

describe('useWeatherStream', () => {
  beforeEach(() => {
    global.EventSource = vi.fn(() => ({
      onmessage: null,
      onerror: null,
      onopen: null,
      close: vi.fn(),
      readyState: 1,
    })) as unknown as typeof EventSource;
  });

  it('should connect to weather endpoint with coordinates', () => {
    renderHook(() => useWeatherStream({ lat: 24.7136, lng: 46.6753 }), {
      wrapper: createWrapper(),
    });

    expect(global.EventSource).toHaveBeenCalledWith(
      expect.stringContaining('/api/events/weather')
    );
  });

  it('should not connect without coordinates', () => {
    renderHook(() => useWeatherStream({}), { wrapper: createWrapper() });

    expect(global.EventSource).not.toHaveBeenCalled();
  });
});

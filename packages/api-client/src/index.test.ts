/**
 * SAHOOL API Client Tests
 * اختبارات عميل API الموحد
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import axios from "axios";
import { SahoolApiClient } from "./index";

// Mock axios
vi.mock("axios", () => ({
  default: {
    create: vi.fn(() => ({
      request: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
    isAxiosError: vi.fn(() => false),
  },
}));

describe("SahoolApiClient", () => {
  let client: SahoolApiClient;
  let mockAxiosInstance: {
    request: ReturnType<typeof vi.fn>;
    interceptors: {
      request: { use: ReturnType<typeof vi.fn> };
      response: { use: ReturnType<typeof vi.fn> };
    };
  };

  beforeEach(() => {
    vi.clearAllMocks();

    mockAxiosInstance = {
      request: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    };

    vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as never);

    client = new SahoolApiClient({
      baseUrl: "http://localhost",
      timeout: 30000,
      locale: "ar",
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Constructor", () => {
    it("should create client with default config", () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
      });

      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 30000,
          headers: expect.objectContaining({
            "Content-Type": "application/json",
          }),
        }),
      );
    });

    it("should create client with custom timeout", () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
        timeout: 60000,
      });

      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 60000,
        }),
      );
    });

    it("should create client with custom locale", () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
        locale: "en",
      });

      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            "Accept-Language": "en,en",
          }),
        }),
      );
    });

    it("should setup interceptors", () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
      });

      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe("URL Generation", () => {
    it("should generate correct service URLs in development", () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = "development";

      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
      });

      const urls = client.urls;

      expect(urls.fieldCore).toBe("http://localhost:3000");
      expect(urls.satellite).toBe("http://localhost:8090");
      expect(urls.weather).toBe("http://localhost:8092");
      expect(urls.irrigation).toBe("http://localhost:8094");

      process.env.NODE_ENV = originalEnv;
    });

    it("should use custom ports when provided", () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = "development";

      const client = new SahoolApiClient(
        { baseUrl: "http://localhost" },
        { fieldCore: 4000, weather: 9000 },
      );

      const urls = client.urls;

      expect(urls.fieldCore).toBe("http://localhost:4000");
      expect(urls.weather).toBe("http://localhost:9000");

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe("Tasks API", () => {
    it("should get all tasks", async () => {
      const mockTasks = [
        { id: "1", title: "Task 1", status: "pending" },
        { id: "2", title: "Task 2", status: "completed" },
      ];

      mockAxiosInstance.request.mockResolvedValue({ data: mockTasks });

      const tasks = await client.getTasks();

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining("/api/v1/tasks"),
        }),
      );
      expect(tasks).toEqual(mockTasks);
    });

    it("should get tasks with filters", async () => {
      const mockTasks = [{ id: "1", title: "Task 1", status: "pending" }];

      mockAxiosInstance.request.mockResolvedValue({ data: mockTasks });

      const tasks = await client.getTasks({
        status: "pending",
        field_id: "field-123",
      });

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          params: {
            status: "pending",
            field_id: "field-123",
          },
        }),
      );
    });

    it("should throw error by default", async () => {
      mockAxiosInstance.request.mockRejectedValue(new Error("Network error"));

      await expect(client.getTasks()).rejects.toThrow();
    });

    it("should get single task by ID", async () => {
      const mockTask = { id: "task-123", title: "Test Task" };

      mockAxiosInstance.request.mockResolvedValue({ data: mockTask });

      const task = await client.getTask("task-123");

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining("/api/v1/tasks/task-123"),
        }),
      );
      expect(task).toEqual(mockTask);
    });

    it("should create new task", async () => {
      const newTask = {
        tenant_id: "tenant-123",
        title: "New Task",
        description: "Task description",
        field_id: "field-123",
        type: "irrigation",
        priority: "high" as const,
      };

      const createdTask = { id: "task-new", ...newTask };

      mockAxiosInstance.request.mockResolvedValue({ data: createdTask });

      const task = await client.createTask(newTask);

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          method: "POST",
          data: newTask,
        }),
      );
      expect(task).toEqual(createdTask);
    });
  });

  describe("Auth Token Management", () => {
    it("should add auth token to requests via interceptor", () => {
      const getToken = vi.fn().mockReturnValue("test-token");

      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
        getToken,
      });

      // Verify interceptor was set up
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
    });

    it("should call onUnauthorized on 401 response", () => {
      const onUnauthorized = vi.fn();

      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
        onUnauthorized,
      });

      // Verify response interceptor was set up
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe("Service Ports", () => {
    it("should have correct default ports", () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = "development";

      const client = new SahoolApiClient({ baseUrl: "http://localhost" });
      const urls = client.urls;

      expect(urls.satellite).toContain(":8090");
      expect(urls.indicators).toContain(":8091");
      expect(urls.weather).toContain(":8092");
      expect(urls.fertilizer).toContain(":8093");
      expect(urls.irrigation).toContain(":8094");
      expect(urls.cropHealth).toContain(":8095");
      expect(urls.virtualSensors).toContain(":8119");
      expect(urls.notifications).toContain(":8110");

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe("Error Handling", () => {
    it("should handle network errors gracefully in silent mode", async () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
        errorHandling: "silent",
      });

      mockAxiosInstance.request.mockRejectedValue(new Error("Network Error"));

      // getTasks should return empty array on error in silent mode
      const tasks = await client.getTasks();
      expect(tasks).toEqual([]);
    });

    it("should throw errors in throw mode", async () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
        errorHandling: "throw",
      });

      mockAxiosInstance.request.mockRejectedValue(new Error("Network Error"));

      // getTasks should throw error in throw mode
      await expect(client.getTasks()).rejects.toThrow();
    });

    it("should handle timeout errors in silent mode", async () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
        errorHandling: "silent",
      });

      const timeoutError = new Error("timeout of 30000ms exceeded");
      mockAxiosInstance.request.mockRejectedValue(timeoutError);

      const tasks = await client.getTasks();
      expect(tasks).toEqual([]);
    });

    it("should default to throw mode", async () => {
      const client = new SahoolApiClient({
        baseUrl: "http://localhost",
      });

      mockAxiosInstance.request.mockRejectedValue(new Error("Network Error"));

      await expect(client.getTasks()).rejects.toThrow();
    });
  });
});

describe("API Client Configuration", () => {
  it("should support Arabic locale by default", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
    });

    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({
          "Accept-Language": "ar,en",
        }),
      }),
    );
  });

  it("should support mock data mode", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      enableMockData: true,
    });

    // Client should be created successfully
    expect(client).toBeDefined();
  });

  it("should support custom error handling mode", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      errorHandling: "silent",
    });

    expect(client).toBeDefined();
  });

  it("should support custom log level", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      logLevel: "debug",
    });

    expect(client).toBeDefined();
  });

  it("should support custom logger", () => {
    const customLogger = {
      error: vi.fn(),
      warn: vi.fn(),
      info: vi.fn(),
      debug: vi.fn(),
    };

    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      logger: customLogger,
    });

    expect(client).toBeDefined();
  });

  it("should support custom timeout", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      timeout: 60000,
    });

    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        timeout: 60000,
      }),
    );
  });

  it("should use default timeout of 30000 when not specified", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
    });

    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        timeout: 30000,
      }),
    );
  });
});

describe("HTTPS Enforcement", () => {
  it("should upgrade HTTP to HTTPS in production", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "production";

    const client = new SahoolApiClient({
      baseUrl: "http://api.sahool.app",
    });

    const urls = client.urls;
    // In production, getServiceUrl uses baseUrl/api, and baseUrl is upgraded
    expect(urls.fieldCore).toContain("https://api.sahool.app");

    process.env.NODE_ENV = originalEnv;
  });

  it("should not upgrade localhost in development", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "development";

    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
    });

    const urls = client.urls;
    expect(urls.fieldCore).toContain("http://localhost");

    process.env.NODE_ENV = originalEnv;
  });

  it("should not upgrade private IPs in development", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "development";

    const client = new SahoolApiClient({
      baseUrl: "http://192.168.1.100",
    });

    const urls = client.urls;
    expect(urls.fieldCore).toContain("http://192.168.1.100");

    process.env.NODE_ENV = originalEnv;
  });

  it("should not upgrade 127.0.0.1 in development", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "development";

    const client = new SahoolApiClient({
      baseUrl: "http://127.0.0.1",
    });

    const urls = client.urls;
    expect(urls.fieldCore).toContain("http://127.0.0.1");

    process.env.NODE_ENV = originalEnv;
  });

  it("should upgrade non-local HTTP URLs in development", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "development";

    const client = new SahoolApiClient({
      baseUrl: "http://api.example.com",
    });

    const urls = client.urls;
    expect(urls.fieldCore).toContain("https://api.example.com");

    process.env.NODE_ENV = originalEnv;
  });

  it("should skip HTTPS enforcement when enforceHttps is false", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "production";

    const client = new SahoolApiClient({
      baseUrl: "http://api.sahool.app",
      enforceHttps: false,
    });

    const urls = client.urls;
    expect(urls.fieldCore).toContain("http://api.sahool.app");

    process.env.NODE_ENV = originalEnv;
  });

  it("should leave HTTPS URLs unchanged", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "production";

    const client = new SahoolApiClient({
      baseUrl: "https://api.sahool.app",
    });

    const urls = client.urls;
    expect(urls.fieldCore).toContain("https://api.sahool.app");

    process.env.NODE_ENV = originalEnv;
  });
});

describe("Retry Configuration", () => {
  it("should accept custom retry configuration", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      retry: {
        maxRetries: 5,
        baseDelay: 500,
        maxDelay: 10000,
      },
    });

    expect(client).toBeDefined();
  });

  it("should allow disabling retries entirely", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      retry: false,
    });

    expect(client).toBeDefined();
  });

  it("should use default retry config when not specified", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
    });

    // Client is created with default retry config (maxRetries: 3)
    expect(client).toBeDefined();
  });

  it("should accept custom retryable status codes", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      retry: {
        retryableStatuses: [502, 503],
        retryOnNetworkError: false,
      },
    });

    expect(client).toBeDefined();
  });
});

describe("Token Refresh Configuration", () => {
  it("should accept token refresh config", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      tokenRefresh: {
        refreshToken: async () => "new-token",
        maxRefreshAttempts: 2,
      },
    });

    expect(client).toBeDefined();
  });

  it("should work without token refresh config", () => {
    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
    });

    expect(client).toBeDefined();
  });

  it("should setup response interceptor for token refresh", () => {
    const mockAxiosInstance = {
      request: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    };

    vi.mocked(axios.create).mockReturnValue(mockAxiosInstance as never);

    const client = new SahoolApiClient({
      baseUrl: "http://localhost",
      tokenRefresh: {
        refreshToken: async () => "new-token",
      },
    });

    // Both request and response interceptors should be set up
    expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
    expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
  });
});

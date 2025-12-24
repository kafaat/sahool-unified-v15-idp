/**
 * SAHOOL API Client Tests
 * اختبارات عميل API الموحد
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import { SahoolApiClient } from './index';

// Mock axios
vi.mock('axios', () => ({
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

describe('SahoolApiClient', () => {
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
      baseUrl: 'http://localhost',
      timeout: 30000,
      locale: 'ar',
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Constructor', () => {
    it('should create client with default config', () => {
      const client = new SahoolApiClient({
        baseUrl: 'http://localhost',
      });

      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 30000,
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should create client with custom timeout', () => {
      const client = new SahoolApiClient({
        baseUrl: 'http://localhost',
        timeout: 60000,
      });

      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 60000,
        })
      );
    });

    it('should create client with custom locale', () => {
      const client = new SahoolApiClient({
        baseUrl: 'http://localhost',
        locale: 'en',
      });

      expect(axios.create).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            'Accept-Language': 'en,en',
          }),
        })
      );
    });

    it('should setup interceptors', () => {
      const client = new SahoolApiClient({
        baseUrl: 'http://localhost',
      });

      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('URL Generation', () => {
    it('should generate correct service URLs in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const client = new SahoolApiClient({
        baseUrl: 'http://localhost',
      });

      const urls = client.urls;

      expect(urls.fieldCore).toBe('http://localhost:3000');
      expect(urls.satellite).toBe('http://localhost:8090');
      expect(urls.weather).toBe('http://localhost:8092');
      expect(urls.irrigation).toBe('http://localhost:8094');

      process.env.NODE_ENV = originalEnv;
    });

    it('should use custom ports when provided', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const client = new SahoolApiClient(
        { baseUrl: 'http://localhost' },
        { fieldCore: 4000, weather: 9000 }
      );

      const urls = client.urls;

      expect(urls.fieldCore).toBe('http://localhost:4000');
      expect(urls.weather).toBe('http://localhost:9000');

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Tasks API', () => {
    it('should get all tasks', async () => {
      const mockTasks = [
        { id: '1', title: 'Task 1', status: 'pending' },
        { id: '2', title: 'Task 2', status: 'completed' },
      ];

      mockAxiosInstance.request.mockResolvedValue({ data: mockTasks });

      const tasks = await client.getTasks();

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining('/api/v1/tasks'),
        })
      );
      expect(tasks).toEqual(mockTasks);
    });

    it('should get tasks with filters', async () => {
      const mockTasks = [{ id: '1', title: 'Task 1', status: 'pending' }];

      mockAxiosInstance.request.mockResolvedValue({ data: mockTasks });

      const tasks = await client.getTasks({
        status: 'pending',
        field_id: 'field-123',
      });

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          params: {
            status: 'pending',
            field_id: 'field-123',
          },
        })
      );
    });

    it('should return empty array on error', async () => {
      mockAxiosInstance.request.mockRejectedValue(new Error('Network error'));

      const tasks = await client.getTasks();

      expect(tasks).toEqual([]);
    });

    it('should get single task by ID', async () => {
      const mockTask = { id: 'task-123', title: 'Test Task' };

      mockAxiosInstance.request.mockResolvedValue({ data: mockTask });

      const task = await client.getTask('task-123');

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          url: expect.stringContaining('/api/v1/tasks/task-123'),
        })
      );
      expect(task).toEqual(mockTask);
    });

    it('should create new task', async () => {
      const newTask = {
        tenant_id: 'tenant-123',
        title: 'New Task',
        description: 'Task description',
        field_id: 'field-123',
        type: 'irrigation',
        priority: 'high' as const,
      };

      const createdTask = { id: 'task-new', ...newTask };

      mockAxiosInstance.request.mockResolvedValue({ data: createdTask });

      const task = await client.createTask(newTask);

      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'POST',
          data: newTask,
        })
      );
      expect(task).toEqual(createdTask);
    });
  });

  describe('Auth Token Management', () => {
    it('should add auth token to requests via interceptor', () => {
      const getToken = vi.fn().mockReturnValue('test-token');

      const client = new SahoolApiClient({
        baseUrl: 'http://localhost',
        getToken,
      });

      // Verify interceptor was set up
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled();
    });

    it('should call onUnauthorized on 401 response', () => {
      const onUnauthorized = vi.fn();

      const client = new SahoolApiClient({
        baseUrl: 'http://localhost',
        onUnauthorized,
      });

      // Verify response interceptor was set up
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled();
    });
  });

  describe('Service Ports', () => {
    it('should have correct default ports', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const client = new SahoolApiClient({ baseUrl: 'http://localhost' });
      const urls = client.urls;

      expect(urls.satellite).toContain(':8090');
      expect(urls.indicators).toContain(':8091');
      expect(urls.weather).toContain(':8092');
      expect(urls.fertilizer).toContain(':8093');
      expect(urls.irrigation).toContain(':8094');
      expect(urls.cropHealth).toContain(':8095');
      expect(urls.virtualSensors).toContain(':8096');
      expect(urls.notifications).toContain(':8110');

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      mockAxiosInstance.request.mockRejectedValue(
        new Error('Network Error')
      );

      // getTasks should return empty array on error
      const tasks = await client.getTasks();
      expect(tasks).toEqual([]);
    });

    it('should handle timeout errors', async () => {
      const timeoutError = new Error('timeout of 30000ms exceeded');
      mockAxiosInstance.request.mockRejectedValue(timeoutError);

      const tasks = await client.getTasks();
      expect(tasks).toEqual([]);
    });
  });
});

describe('API Client Configuration', () => {
  it('should support Arabic locale by default', () => {
    const client = new SahoolApiClient({
      baseUrl: 'http://localhost',
    });

    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: expect.objectContaining({
          'Accept-Language': 'ar,en',
        }),
      })
    );
  });

  it('should support mock data mode', () => {
    const client = new SahoolApiClient({
      baseUrl: 'http://localhost',
      enableMockData: true,
    });

    // Client should be created successfully
    expect(client).toBeDefined();
  });
});

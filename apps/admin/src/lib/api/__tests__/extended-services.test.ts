/**
 * Extended API Services Tests
 * اختبارات خدمات API الموسعة
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  taskService,
  inventoryService,
  researchService,
  marketplaceService,
} from "../extended-services";

// Mock shared-types contracts
vi.mock("@sahool/shared-types/contracts", () => ({
  TASK_ENDPOINTS: {
    LIST: "/api/v1/tasks",
    GET: "/api/v1/tasks/:taskId",
    CREATE: "/api/v1/tasks",
    UPDATE: "/api/v1/tasks/:taskId",
    COMPLETE: "/api/v1/tasks/:taskId/complete",
    DELETE: "/api/v1/tasks/:taskId",
  },
  INVENTORY_ENDPOINTS: {
    LIST: "/api/v1/inventory",
    GET: "/api/v1/inventory/:itemId",
    CREATE: "/api/v1/inventory",
    UPDATE: "/api/v1/inventory/:itemId",
    DELETE: "/api/v1/inventory/:itemId",
  },
  MARKETPLACE_ENDPOINTS: {
    LISTINGS: "/api/v1/marketplace/listings",
    LISTING_CREATE: "/api/v1/marketplace/listings",
  },
  API_PREFIX: "/api/v1",
  buildUrl: (template: string, params: Record<string, string>) => {
    let url = template;
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`:${key}`, value);
    }
    return url;
  },
}));

// Ensure global.fetch is always a fresh vi.fn() before each test
beforeEach(() => {
  global.fetch = vi.fn() as typeof fetch;
});

function mockFetch(data: unknown, ok = true, status = 200) {
  (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
    ok,
    status,
    json: () => Promise.resolve(data),
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Task Service Tests | اختبارات خدمة المهام
// ═══════════════════════════════════════════════════════════════════════════

describe("Task Service", () => {

  describe("getAll", () => {
    it("fetches tasks with pagination", async () => {
      const mockData = {
        data: [{ id: "t-1", title: "Irrigate Field A" }],
        meta: { total: 1, page: 1, limit: 10, totalPages: 1 },
      };
      mockFetch(mockData);

      const result = await taskService.getAll({ page: 1, limit: 10 });
      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalled();
    });

    it("includes filter params in URL", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });

      await taskService.getAll({
        status: "pending",
        priority: "high",
        type: "irrigation",
        assignedTo: "user-1",
        fieldId: "f-1",
      });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain("status=pending");
      expect(url).toContain("priority=high");
      expect(url).toContain("type=irrigation");
      expect(url).toContain("assigned_to=user-1");
      expect(url).toContain("field_id=f-1");
    });

    it("throws on HTTP error", async () => {
      mockFetch({}, false, 500);
      await expect(taskService.getAll()).rejects.toThrow("HTTP 500");
    });
  });

  describe("getById", () => {
    it("fetches task by ID", async () => {
      const mockTask = { id: "t-1", title: "Harvest wheat" };
      mockFetch(mockTask);

      const result = await taskService.getById("t-1");
      expect(result).toEqual(mockTask);
    });

    it("throws on 404", async () => {
      mockFetch({}, false, 404);
      await expect(taskService.getById("nonexistent")).rejects.toThrow();
    });
  });

  describe("create", () => {
    it("creates task with POST", async () => {
      const newTask = {
        title: "Apply fertilizer",
        titleAr: "تطبيق السماد",
        type: "fertilization" as const,
        priority: "high" as const,
      };
      mockFetch({ id: "t-new", ...newTask });

      const result = await taskService.create(newTask);
      expect(result.id).toBe("t-new");
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  describe("update", () => {
    it("updates task with PUT", async () => {
      mockFetch({ id: "t-1", status: "in_progress" });

      const result = await taskService.update("t-1", { status: "in_progress" });
      expect(result.status).toBe("in_progress");
    });
  });

  describe("complete", () => {
    it("completes task with POST", async () => {
      mockFetch({ id: "t-1", status: "completed" });

      const result = await taskService.complete("t-1", "Done successfully", 2.5);
      expect(result.status).toBe("completed");

      const [url, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(url).toContain("complete");
      expect(options.method).toBe("POST");
      const body = JSON.parse(options.body);
      expect(body.notes).toBe("Done successfully");
      expect(body.actualDuration).toBe(2.5);
    });
  });

  describe("delete", () => {
    it("deletes task with DELETE", async () => {
      mockFetch({ success: true });

      const result = await taskService.delete("t-1");
      expect(result.success).toBe(true);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Inventory Service Tests | اختبارات خدمة المخزون
// ═══════════════════════════════════════════════════════════════════════════

describe("Inventory Service", () => {

  describe("getAll", () => {
    it("fetches inventory items", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      const result = await inventoryService.getAll();
      expect(result.data).toEqual([]);
    });

    it("filters by category and status", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await inventoryService.getAll({ category: "fertilizer", status: "low_stock" });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain("category=fertilizer");
      expect(url).toContain("status=low_stock");
    });

    it("includes search param", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await inventoryService.getAll({ search: "urea" });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain("search=urea");
    });
  });

  describe("getById", () => {
    it("fetches inventory item by ID", async () => {
      mockFetch({ id: "inv-1", name: "Urea 46%" });
      const result = await inventoryService.getById("inv-1");
      expect(result.name).toBe("Urea 46%");
    });
  });

  describe("getTransactions", () => {
    it("fetches item transactions", async () => {
      mockFetch({
        data: [{ id: "tx-1", type: "purchase", quantity: 100 }],
        meta: { total: 1, page: 1, limit: 10, totalPages: 1 },
      });

      const result = await inventoryService.getTransactions("inv-1");
      expect(result.data).toHaveLength(1);
      expect(result.data[0].type).toBe("purchase");
    });
  });

  describe("create", () => {
    it("creates inventory item", async () => {
      mockFetch({ id: "inv-new" });
      const result = await inventoryService.create({
        name: "NPK 20-20-20",
        nameAr: "سماد NPK",
        category: "fertilizer",
        quantity: 500,
        unit: "kg",
        unitAr: "كجم",
      });
      expect(result.id).toBe("inv-new");
    });
  });

  describe("adjustQuantity", () => {
    it("adjusts inventory quantity", async () => {
      mockFetch({ id: "inv-1", quantity: 450 });
      const result = await inventoryService.adjustQuantity("inv-1", -50, "usage", "Field A irrigation");
      expect(result.quantity).toBe(450);

      const [, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(options.method).toBe("POST");
      const body = JSON.parse(options.body);
      expect(body.quantity).toBe(-50);
      expect(body.type).toBe("usage");
    });
  });

  describe("update", () => {
    it("updates inventory item", async () => {
      mockFetch({ id: "inv-1", quantity: 600 });
      const result = await inventoryService.update("inv-1", { quantity: 600 });
      expect(result.quantity).toBe(600);
    });
  });

  describe("delete", () => {
    it("deletes inventory item", async () => {
      mockFetch({ success: true });
      const result = await inventoryService.delete("inv-1");
      expect(result.success).toBe(true);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Research Service Tests | اختبارات خدمة البحوث
// ═══════════════════════════════════════════════════════════════════════════

describe("Research Service", () => {

  describe("getAllProjects", () => {
    it("fetches research projects", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      const result = await researchService.getAllProjects();
      expect(result.data).toEqual([]);
    });

    it("filters projects by status", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await researchService.getAllProjects({ status: "active" });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain("status=active");
    });
  });

  describe("getProjectById", () => {
    it("fetches project by ID", async () => {
      mockFetch({ id: "proj-1", title: "Wheat Yield Study" });
      const result = await researchService.getProjectById("proj-1");
      expect(result.title).toBe("Wheat Yield Study");
    });
  });

  describe("createProject", () => {
    it("creates research project", async () => {
      mockFetch({ id: "proj-new" });
      const result = await researchService.createProject({
        title: "Soil Salinity Study",
        titleAr: "دراسة ملوحة التربة",
      });
      expect(result.id).toBe("proj-new");
    });
  });

  describe("updateProject", () => {
    it("updates project status and findings", async () => {
      mockFetch({ id: "proj-1", status: "completed" });
      const result = await researchService.updateProject("proj-1", {
        status: "completed",
        findings: "Salinity levels decreased by 15%",
      });
      expect(result.status).toBe("completed");
    });
  });

  describe("deleteProject", () => {
    it("deletes research project", async () => {
      mockFetch({ success: true });
      const result = await researchService.deleteProject("proj-1");
      expect(result.success).toBe(true);
    });
  });

  describe("getAllExperiments", () => {
    it("fetches experiments", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      const result = await researchService.getAllExperiments();
      expect(result.data).toEqual([]);
    });

    it("filters by project ID", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await researchService.getAllExperiments({ projectId: "proj-1" });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain("project_id=proj-1");
    });
  });

  describe("createExperiment", () => {
    it("creates experiment", async () => {
      mockFetch({ id: "exp-new" });
      const result = await researchService.createExperiment({
        projectId: "proj-1",
        name: "Nitrogen Test A",
        nameAr: "اختبار النيتروجين أ",
      });
      expect(result.id).toBe("exp-new");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Marketplace Service Tests | اختبارات خدمة السوق
// ═══════════════════════════════════════════════════════════════════════════

describe("Marketplace Service", () => {
  describe("getAll", () => {
    it("fetches all listings", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      const result = await marketplaceService.getAll();
      expect(result.data).toEqual([]);
    });

    it("filters by category and price range", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await marketplaceService.getAll({
        category: "produce",
        minPrice: 100,
        maxPrice: 500,
        status: "active",
      });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain("category=produce");
      expect(url).toContain("min_price=100");
      expect(url).toContain("max_price=500");
      expect(url).toContain("status=active");
    });

    it("includes search param", async () => {
      mockFetch({ data: [], meta: { total: 0, page: 1, limit: 10, totalPages: 0 } });
      await marketplaceService.getAll({ search: "tractor" });

      const url = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
      expect(url).toContain("search=tractor");
    });
  });

  describe("getById", () => {
    it("fetches listing by ID", async () => {
      mockFetch({ id: "listing-1", title: "Used Tractor" });
      const result = await marketplaceService.getById("listing-1");
      expect(result.title).toBe("Used Tractor");
    });

    it("throws on error", async () => {
      mockFetch({}, false, 404);
      await expect(marketplaceService.getById("nonexistent")).rejects.toThrow();
    });
  });

  describe("create", () => {
    it("creates marketplace listing", async () => {
      mockFetch({ id: "listing-new" });
      const result = await marketplaceService.create({
        title: "Organic Wheat",
        titleAr: "قمح عضوي",
        category: "produce",
        price: 350,
      });
      expect(result.id).toBe("listing-new");
    });
  });

  describe("update", () => {
    it("updates listing", async () => {
      mockFetch({ id: "listing-1", status: "sold" });
      const result = await marketplaceService.update("listing-1", { status: "sold" });
      expect(result.status).toBe("sold");
    });
  });

  describe("delete", () => {
    it("deletes listing", async () => {
      mockFetch({ success: true });
      const result = await marketplaceService.delete("listing-1");
      expect(result.success).toBe(true);
    });
  });
});

/**
 * SAHOOL Admin Extended API Services v16.0.0
 * خدمات API الإدارية الموسعة - سهول
 *
 * Additional API integration for tasks, inventory, research, marketplace, and community
 *
 * Uses unified API contracts from @sahool/shared-types/contracts
 */

import { logger } from "../logger";
import { PaginationParams, PaginatedResponse } from "./services";
import {
  TASK_ENDPOINTS,
  INVENTORY_ENDPOINTS,
  MARKETPLACE_ENDPOINTS,
  API_PREFIX,
  buildUrl,
} from "@sahool/shared-types/contracts";

// Default fetch options to ensure httpOnly cookies are sent with requests
const fetchDefaults: RequestInit = {
  credentials: "same-origin",
};

// =============================================================================
// Task Management Service | خدمة إدارة المهام
// =============================================================================

export interface Task {
  id: string;
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  type: "irrigation" | "fertilization" | "pest_control" | "harvest" | "maintenance" | "other";
  priority: "low" | "medium" | "high" | "urgent";
  status: "pending" | "in_progress" | "completed" | "cancelled";
  assignedTo?: string;
  assignedToName?: string;
  fieldId?: string;
  fieldName?: string;
  dueDate?: string;
  completedAt?: string;
  completedBy?: string;
  estimatedDuration?: number; // hours
  actualDuration?: number; // hours
  cost?: number;
  notes?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateTaskData {
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  type: Task["type"];
  priority: Task["priority"];
  assignedTo?: string;
  fieldId?: string;
  dueDate?: string;
  estimatedDuration?: number;
  cost?: number;
  notes?: string;
}

export const taskService = {
  /**
   * Get all tasks
   * جلب جميع المهام
   */
  async getAll(params?: PaginationParams & {
    status?: string;
    priority?: string;
    type?: string;
    assignedTo?: string;
    fieldId?: string;
  }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set("page", params.page.toString());
      if (params?.limit) queryParams.set("limit", params.limit.toString());
      if (params?.status) queryParams.set("status", params.status);
      if (params?.priority) queryParams.set("priority", params.priority);
      if (params?.type) queryParams.set("type", params.type);
      if (params?.assignedTo) queryParams.set("assigned_to", params.assignedTo);
      if (params?.fieldId) queryParams.set("field_id", params.fieldId);

      const response = await fetch(`${TASK_ENDPOINTS.LIST}?${queryParams.toString()}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<Task>;
    } catch (error) {
      logger.error("Failed to fetch tasks", { error });
      throw error;
    }
  },

  /**
   * Get task by ID
   * جلب مهمة بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(buildUrl(TASK_ENDPOINTS.GET, { taskId: id }), fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as Task;
    } catch (error) {
      logger.error("Failed to fetch task", { id, error });
      throw error;
    }
  },

  /**
   * Create task
   * إنشاء مهمة
   */
  async create(data: CreateTaskData) {
    try {
      const response = await fetch(TASK_ENDPOINTS.CREATE, {
        ...fetchDefaults,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as Task;
    } catch (error) {
      logger.error("Failed to create task", { error });
      throw error;
    }
  },

  /**
   * Update task
   * تحديث مهمة
   */
  async update(id: string, data: Partial<CreateTaskData> & { status?: Task["status"] }) {
    try {
      const response = await fetch(buildUrl(TASK_ENDPOINTS.UPDATE, { taskId: id }), {
        ...fetchDefaults,
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as Task;
    } catch (error) {
      logger.error("Failed to update task", { id, error });
      throw error;
    }
  },

  /**
   * Complete task
   * إكمال مهمة
   */
  async complete(id: string, notes?: string, actualDuration?: number) {
    try {
      const response = await fetch(buildUrl(TASK_ENDPOINTS.COMPLETE, { taskId: id }), {
        ...fetchDefaults,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes, actualDuration }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as Task;
    } catch (error) {
      logger.error("Failed to complete task", { id, error });
      throw error;
    }
  },

  /**
   * Delete task
   * حذف مهمة
   */
  async delete(id: string) {
    try {
      const response = await fetch(buildUrl(TASK_ENDPOINTS.DELETE, { taskId: id }), {
        ...fetchDefaults,
        method: "DELETE",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as { success: boolean };
    } catch (error) {
      logger.error("Failed to delete task", { id, error });
      throw error;
    }
  },
};

// =============================================================================
// Inventory Management Service | خدمة إدارة المخزون
// =============================================================================

export interface InventoryItem {
  id: string;
  name: string;
  nameAr: string;
  category: "fertilizer" | "pesticide" | "herbicide" | "seed" | "fuel" | "spare_parts" | "other";
  sku?: string;
  quantity: number;
  unit: string;
  unitAr: string;
  minQuantity?: number;
  maxQuantity?: number;
  unitPrice?: number;
  totalValue?: number;
  supplier?: string;
  location?: string;
  expiryDate?: string;
  batchNumber?: string;
  status: "in_stock" | "low_stock" | "out_of_stock" | "expired";
  lastRestocked?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateInventoryData {
  name: string;
  nameAr: string;
  category: InventoryItem["category"];
  sku?: string;
  quantity: number;
  unit: string;
  unitAr: string;
  minQuantity?: number;
  maxQuantity?: number;
  unitPrice?: number;
  supplier?: string;
  location?: string;
  expiryDate?: string;
  batchNumber?: string;
}

export interface InventoryTransaction {
  id: string;
  itemId: string;
  itemName: string;
  type: "purchase" | "usage" | "adjustment" | "return" | "waste";
  quantity: number;
  unit: string;
  reason?: string;
  reference?: string; // task_id, order_id, etc.
  performedBy: string;
  performedByName?: string;
  createdAt: string;
}

export const inventoryService = {
  /**
   * Get all inventory items
   * جلب جميع عناصر المخزون
   */
  async getAll(params?: PaginationParams & { category?: string; status?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set("page", params.page.toString());
      if (params?.limit) queryParams.set("limit", params.limit.toString());
      if (params?.search) queryParams.set("search", params.search);
      if (params?.category) queryParams.set("category", params.category);
      if (params?.status) queryParams.set("status", params.status);

      const response = await fetch(`${INVENTORY_ENDPOINTS.LIST}?${queryParams.toString()}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<InventoryItem>;
    } catch (error) {
      logger.error("Failed to fetch inventory", { error });
      throw error;
    }
  },

  /**
   * Get inventory item by ID
   * جلب عنصر مخزون بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(buildUrl(INVENTORY_ENDPOINTS.GET, { itemId: id }), fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as InventoryItem;
    } catch (error) {
      logger.error("Failed to fetch inventory item", { id, error });
      throw error;
    }
  },

  /**
   * Get item transactions
   * جلب معاملات العنصر
   */
  async getTransactions(itemId: string, params?: PaginationParams) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set("page", params.page.toString());
      if (params?.limit) queryParams.set("limit", params.limit.toString());

      const response = await fetch(`${buildUrl(INVENTORY_ENDPOINTS.GET, { itemId })}/transactions?${queryParams.toString()}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<InventoryTransaction>;
    } catch (error) {
      logger.error("Failed to fetch inventory transactions", { itemId, error });
      throw error;
    }
  },

  /**
   * Create inventory item
   * إنشاء عنصر مخزون
   */
  async create(data: CreateInventoryData) {
    try {
      const response = await fetch(INVENTORY_ENDPOINTS.CREATE, {
        ...fetchDefaults,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as InventoryItem;
    } catch (error) {
      logger.error("Failed to create inventory item", { error });
      throw error;
    }
  },

  /**
   * Update inventory item
   * تحديث عنصر مخزون
   */
  async update(id: string, data: Partial<CreateInventoryData>) {
    try {
      const response = await fetch(buildUrl(INVENTORY_ENDPOINTS.UPDATE, { itemId: id }), {
        ...fetchDefaults,
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as InventoryItem;
    } catch (error) {
      logger.error("Failed to update inventory item", { id, error });
      throw error;
    }
  },

  /**
   * Adjust inventory quantity
   * تعديل كمية المخزون
   */
  async adjustQuantity(id: string, quantity: number, type: InventoryTransaction["type"], reason?: string) {
    try {
      const response = await fetch(`${buildUrl(INVENTORY_ENDPOINTS.GET, { itemId: id })}/adjust`, {
        ...fetchDefaults,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity, type, reason }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as InventoryItem;
    } catch (error) {
      logger.error("Failed to adjust inventory", { id, error });
      throw error;
    }
  },

  /**
   * Delete inventory item
   * حذف عنصر مخزون
   */
  async delete(id: string) {
    try {
      const response = await fetch(buildUrl(INVENTORY_ENDPOINTS.DELETE, { itemId: id }), {
        ...fetchDefaults,
        method: "DELETE",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as { success: boolean };
    } catch (error) {
      logger.error("Failed to delete inventory item", { id, error });
      throw error;
    }
  },
};

// =============================================================================
// Research Management Service | خدمة إدارة البحوث
// =============================================================================

export interface ResearchProject {
  id: string;
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  status: "planning" | "active" | "paused" | "completed" | "cancelled";
  startDate?: string;
  endDate?: string;
  fieldIds?: string[];
  methodology?: string;
  findings?: string;
  leadResearcher?: string;
  leadResearcherName?: string;
  collaborators?: string[];
  budget?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Experiment {
  id: string;
  projectId: string;
  projectTitle?: string;
  name: string;
  nameAr: string;
  description?: string;
  fieldId?: string;
  fieldName?: string;
  parameters?: Record<string, unknown>;
  results?: Record<string, unknown>;
  status: "setup" | "running" | "analyzing" | "completed";
  startDate?: string;
  endDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProjectData {
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  startDate?: string;
  fieldIds?: string[];
  methodology?: string;
  leadResearcher?: string;
  budget?: number;
}

export interface CreateExperimentData {
  projectId: string;
  name: string;
  nameAr: string;
  description?: string;
  fieldId?: string;
  parameters?: Record<string, unknown>;
  startDate?: string;
}

export const researchService = {
  /**
   * Get all research projects
   * جلب جميع مشاريع البحث
   */
  async getAllProjects(params?: PaginationParams & { status?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set("page", params.page.toString());
      if (params?.limit) queryParams.set("limit", params.limit.toString());
      if (params?.search) queryParams.set("search", params.search);
      if (params?.status) queryParams.set("status", params.status);

      const response = await fetch(`${API_PREFIX}/research/projects?${queryParams.toString()}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<ResearchProject>;
    } catch (error) {
      logger.error("Failed to fetch research projects", { error });
      throw error;
    }
  },

  /**
   * Get project by ID
   * جلب مشروع بحث بالمعرف
   */
  async getProjectById(id: string) {
    try {
      const response = await fetch(`${API_PREFIX}/research/projects/${encodeURIComponent(id)}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as ResearchProject;
    } catch (error) {
      logger.error("Failed to fetch research project", { id, error });
      throw error;
    }
  },

  /**
   * Create research project
   * إنشاء مشروع بحث
   */
  async createProject(data: CreateProjectData) {
    try {
      const response = await fetch(`${API_PREFIX}/research/projects`, {
        ...fetchDefaults,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as ResearchProject;
    } catch (error) {
      logger.error("Failed to create research project", { error });
      throw error;
    }
  },

  /**
   * Update research project
   * تحديث مشروع بحث
   */
  async updateProject(id: string, data: Partial<CreateProjectData> & { status?: ResearchProject["status"]; findings?: string }) {
    try {
      const response = await fetch(`${API_PREFIX}/research/projects/${encodeURIComponent(id)}`, {
        ...fetchDefaults,
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as ResearchProject;
    } catch (error) {
      logger.error("Failed to update research project", { id, error });
      throw error;
    }
  },

  /**
   * Delete research project
   * حذف مشروع بحث
   */
  async deleteProject(id: string) {
    try {
      const response = await fetch(`${API_PREFIX}/research/projects/${encodeURIComponent(id)}`, {
        ...fetchDefaults,
        method: "DELETE",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as { success: boolean };
    } catch (error) {
      logger.error("Failed to delete research project", { id, error });
      throw error;
    }
  },

  /**
   * Get all experiments
   * جلب جميع التجارب
   */
  async getAllExperiments(params?: PaginationParams & { projectId?: string }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set("page", params.page.toString());
      if (params?.limit) queryParams.set("limit", params.limit.toString());
      if (params?.projectId) queryParams.set("project_id", params.projectId);

      const response = await fetch(`${API_PREFIX}/research/experiments?${queryParams.toString()}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<Experiment>;
    } catch (error) {
      logger.error("Failed to fetch experiments", { error });
      throw error;
    }
  },

  /**
   * Create experiment
   * إنشاء تجربة
   */
  async createExperiment(data: CreateExperimentData) {
    try {
      const response = await fetch(`${API_PREFIX}/research/experiments`, {
        ...fetchDefaults,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as Experiment;
    } catch (error) {
      logger.error("Failed to create experiment", { error });
      throw error;
    }
  },
};

// =============================================================================
// Marketplace Service | خدمة السوق
// =============================================================================

export interface MarketplaceListing {
  id: string;
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  category: "equipment" | "produce" | "seeds" | "fertilizer" | "service" | "other";
  price: number;
  currency: string;
  unit?: string;
  quantity?: number;
  status: "active" | "sold" | "expired" | "inactive";
  sellerId: string;
  sellerName?: string;
  images?: string[];
  location?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateListingData {
  title: string;
  titleAr: string;
  description?: string;
  descriptionAr?: string;
  category: MarketplaceListing["category"];
  price: number;
  currency?: string;
  unit?: string;
  quantity?: number;
  images?: string[];
  location?: string;
}

export const marketplaceService = {
  /**
   * Get all listings
   * جلب جميع القوائم
   */
  async getAll(params?: PaginationParams & {
    category?: string;
    minPrice?: number;
    maxPrice?: number;
    status?: string;
  }) {
    try {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set("page", params.page.toString());
      if (params?.limit) queryParams.set("limit", params.limit.toString());
      if (params?.search) queryParams.set("search", params.search);
      if (params?.category) queryParams.set("category", params.category);
      if (params?.minPrice) queryParams.set("min_price", params.minPrice.toString());
      if (params?.maxPrice) queryParams.set("max_price", params.maxPrice.toString());
      if (params?.status) queryParams.set("status", params.status);

      const response = await fetch(`${MARKETPLACE_ENDPOINTS.LISTINGS}?${queryParams.toString()}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as PaginatedResponse<MarketplaceListing>;
    } catch (error) {
      logger.error("Failed to fetch marketplace listings", { error });
      throw error;
    }
  },

  /**
   * Get listing by ID
   * جلب قائمة بالمعرف
   */
  async getById(id: string) {
    try {
      const response = await fetch(`${MARKETPLACE_ENDPOINTS.LISTINGS}/${encodeURIComponent(id)}`, fetchDefaults);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as MarketplaceListing;
    } catch (error) {
      logger.error("Failed to fetch marketplace listing", { id, error });
      throw error;
    }
  },

  /**
   * Create listing
   * إنشاء قائمة
   */
  async create(data: CreateListingData) {
    try {
      const response = await fetch(MARKETPLACE_ENDPOINTS.LISTING_CREATE, {
        ...fetchDefaults,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as MarketplaceListing;
    } catch (error) {
      logger.error("Failed to create marketplace listing", { error });
      throw error;
    }
  },

  /**
   * Update listing
   * تحديث قائمة
   */
  async update(id: string, data: Partial<CreateListingData> & { status?: MarketplaceListing["status"] }) {
    try {
      const response = await fetch(`${MARKETPLACE_ENDPOINTS.LISTINGS}/${encodeURIComponent(id)}`, {
        ...fetchDefaults,
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as MarketplaceListing;
    } catch (error) {
      logger.error("Failed to update marketplace listing", { id, error });
      throw error;
    }
  },

  /**
   * Delete listing
   * حذف قائمة
   */
  async delete(id: string) {
    try {
      const response = await fetch(`${MARKETPLACE_ENDPOINTS.LISTINGS}/${encodeURIComponent(id)}`, {
        ...fetchDefaults,
        method: "DELETE",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json() as { success: boolean };
    } catch (error) {
      logger.error("Failed to delete marketplace listing", { id, error });
      throw error;
    }
  },
};

// Export all extended services
export default {
  tasks: taskService,
  inventory: inventoryService,
  research: researchService,
  marketplace: marketplaceService,
};

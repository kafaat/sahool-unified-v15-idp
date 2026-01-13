/**
 * Example Service Implementation
 * مثال على تطبيق الخدمة
 *
 * @description Demonstrates how to use the shared error handling module
 */

import { Injectable, Logger } from "@nestjs/common";
import {
  ErrorCode,
  NotFoundException,
  ValidationException,
  BusinessLogicException,
  DatabaseException,
  ExternalServiceException,
  HandleErrors,
  retryWithBackoff,
  createSuccessResponse,
  createPaginatedResponse,
} from "../index";

// Example DTOs
interface CreateFarmDto {
  name: string;
  area: number;
  location: { lat: number; lng: number };
}

interface UpdateFarmDto {
  name?: string;
  area?: number;
}

interface Farm {
  id: string;
  name: string;
  area: number;
  location: { lat: number; lng: number };
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Example Farm Service
 * خدمة المزارع كمثال
 */
@Injectable()
export class ExampleFarmService {
  private readonly logger = new Logger(ExampleFarmService.name);
  private farms: Map<string, Farm> = new Map();

  /**
   * Example 1: Not Found Exception
   * مثال 1: استثناء عدم العثور
   */
  async findById(id: string): Promise<Farm> {
    const farm = this.farms.get(id);

    if (!farm) {
      // Using the specific helper method
      throw NotFoundException.farm(id);
    }

    return farm;
  }

  /**
   * Example 2: Validation Exception with Field Errors
   * مثال 2: استثناء التحقق مع أخطاء الحقول
   */
  async create(data: CreateFarmDto): Promise<Farm> {
    const errors = [];

    // Validate name
    if (!data.name || data.name.trim().length === 0) {
      errors.push({
        field: "name",
        message: "Name is required",
        messageAr: "الاسم مطلوب",
      });
    }

    // Validate area
    if (data.area <= 0) {
      errors.push({
        field: "area",
        message: "Area must be greater than zero",
        messageAr: "المساحة يجب أن تكون أكبر من صفر",
      });
    }

    // Validate location
    if (!data.location || !data.location.lat || !data.location.lng) {
      errors.push({
        field: "location",
        message: "Location coordinates are required",
        messageAr: "إحداثيات الموقع مطلوبة",
      });
    }

    if (errors.length > 0) {
      throw ValidationException.fromFieldErrors(errors);
    }

    // Create farm
    const farm: Farm = {
      id: `farm-${Date.now()}`,
      name: data.name,
      area: data.area,
      location: data.location,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.farms.set(farm.id, farm);
    return farm;
  }

  /**
   * Example 3: Business Logic Exception
   * مثال 3: استثناء منطق الأعمال
   */
  async transferArea(
    fromFarmId: string,
    toFarmId: string,
    area: number,
  ): Promise<void> {
    // Validate amount is positive
    if (area <= 0) {
      throw BusinessLogicException.amountMustBePositive(area);
    }

    // Get farms
    const fromFarm = await this.findById(fromFarmId);
    const toFarm = await this.findById(toFarmId);

    // Check if from farm has sufficient area
    if (fromFarm.area < area) {
      throw BusinessLogicException.insufficientBalance(fromFarm.area, area);
    }

    // Perform transfer
    fromFarm.area -= area;
    toFarm.area += area;
    fromFarm.updatedAt = new Date();
    toFarm.updatedAt = new Date();

    this.farms.set(fromFarm.id, fromFarm);
    this.farms.set(toFarm.id, toFarm);
  }

  /**
   * Example 4: Using HandleErrors Decorator
   * مثال 4: استخدام ديكوراتور معالجة الأخطاء
   */
  @HandleErrors(ErrorCode.DATABASE_ERROR)
  async updateWithDecorator(id: string, data: UpdateFarmDto): Promise<Farm> {
    const farm = await this.findById(id);

    if (data.name) farm.name = data.name;
    if (data.area) farm.area = data.area;
    farm.updatedAt = new Date();

    this.farms.set(id, farm);
    return farm;
  }

  /**
   * Example 5: Database Exception
   * مثال 5: استثناء قاعدة البيانات
   */
  async saveToDatabase(farm: Farm): Promise<Farm> {
    try {
      // Simulate Prisma/database operation
      // In real code: await this.prisma.farm.create({ data: farm });

      // Simulate a unique constraint violation
      const isDuplicate = Array.from(this.farms.values()).some(
        (f) => f.name === farm.name && f.id !== farm.id,
      );

      if (isDuplicate) {
        // Simulate Prisma error
        const error = {
          code: "P2002",
          meta: { target: ["name"] },
        };
        throw DatabaseException.fromDatabaseError(error);
      }

      this.farms.set(farm.id, farm);
      return farm;
    } catch (error) {
      // Handle database errors
      if (error instanceof DatabaseException) {
        throw error;
      }
      throw DatabaseException.fromDatabaseError(error);
    }
  }

  /**
   * Example 6: External Service Exception with Retry
   * مثال 6: استثناء الخدمة الخارجية مع إعادة المحاولة
   */
  async fetchWeatherData(farmId: string): Promise<any> {
    const farm = await this.findById(farmId);

    try {
      // Use retry with backoff for external service calls
      return await retryWithBackoff(
        async () => {
          // Simulate external API call
          // In real code: return await this.weatherService.getCurrentWeather(farm.location);

          // Simulate occasional failures
          if (Math.random() > 0.7) {
            throw new Error("Weather service timeout");
          }

          return {
            temperature: 25,
            humidity: 60,
            location: farm.location,
          };
        },
        {
          maxRetries: 3,
          initialDelay: 1000,
          maxDelay: 5000,
        },
      );
    } catch (error) {
      throw ExternalServiceException.weatherService(error);
    }
  }

  /**
   * Example 7: Success Response
   * مثال 7: استجابة النجاح
   */
  async getById(id: string) {
    const farm = await this.findById(id);
    return createSuccessResponse(
      farm,
      "Farm retrieved successfully",
      "تم استرجاع المزرعة بنجاح",
    );
  }

  /**
   * Example 8: Paginated Response
   * مثال 8: استجابة مقسمة إلى صفحات
   */
  async findAll(page: number = 1, limit: number = 20) {
    const allFarms = Array.from(this.farms.values());
    const total = allFarms.length;
    const start = (page - 1) * limit;
    const end = start + limit;
    const farms = allFarms.slice(start, end);

    return createPaginatedResponse(
      farms,
      page,
      limit,
      total,
      "Farms retrieved successfully",
      "تم استرجاع المزارع بنجاح",
    );
  }

  /**
   * Example 9: Multiple Validations
   * مثال 9: تحققات متعددة
   */
  async validateFarmData(data: CreateFarmDto): Promise<void> {
    const errors = [];

    // Name validation
    if (!data.name) {
      errors.push({
        field: "name",
        message: "Name is required",
        messageAr: "الاسم مطلوب",
        constraint: "isNotEmpty",
      });
    } else if (data.name.length < 3) {
      errors.push({
        field: "name",
        message: "Name must be at least 3 characters",
        messageAr: "الاسم يجب أن يكون 3 أحرف على الأقل",
        constraint: "minLength",
        value: data.name,
      });
    }

    // Area validation
    if (data.area === undefined || data.area === null) {
      errors.push({
        field: "area",
        message: "Area is required",
        messageAr: "المساحة مطلوبة",
        constraint: "isNotEmpty",
      });
    } else if (data.area <= 0) {
      errors.push({
        field: "area",
        message: "Area must be positive",
        messageAr: "المساحة يجب أن تكون موجبة",
        constraint: "isPositive",
        value: data.area,
      });
    } else if (data.area > 10000) {
      errors.push({
        field: "area",
        message: "Area cannot exceed 10,000 hectares",
        messageAr: "المساحة لا يمكن أن تتجاوز 10,000 هكتار",
        constraint: "max",
        value: data.area,
      });
    }

    // Location validation
    if (!data.location) {
      errors.push({
        field: "location",
        message: "Location is required",
        messageAr: "الموقع مطلوب",
        constraint: "isNotEmpty",
      });
    } else {
      if (
        data.location.lat < -90 ||
        data.location.lat > 90 ||
        data.location.lng < -180 ||
        data.location.lng > 180
      ) {
        errors.push({
          field: "location",
          message: "Invalid coordinates",
          messageAr: "إحداثيات غير صالحة",
          constraint: "isValidCoordinates",
          value: data.location,
        });
      }
    }

    if (errors.length > 0) {
      throw ValidationException.fromFieldErrors(errors);
    }
  }

  /**
   * Example 10: State Transition Validation
   * مثال 10: التحقق من انتقال الحالة
   */
  async archiveFarm(id: string): Promise<void> {
    const farm = await this.findById(id);

    // Check if farm can be archived
    // (e.g., cannot archive if it has active crops)
    const hasActiveCrops = false; // Simulate check

    if (hasActiveCrops) {
      throw BusinessLogicException.operationNotAllowed(
        "archive",
        "Cannot archive farm with active crops",
      );
    }

    // Archive the farm
    this.farms.delete(id);
    this.logger.log(`Farm ${id} archived successfully`);
  }
}

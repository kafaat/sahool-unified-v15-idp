/**
 * Example: Users Controller V1 (Deprecated)
 * Demonstrates how to create a v1 controller with deprecation warnings
 */

import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  UseInterceptors,
} from "@nestjs/common";
import { ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import {
  BaseControllerV1,
  ApiV1,
  ApiDeprecated,
  DeprecationInterceptor,
} from "@sahool/versioning";

// DTO imports
interface CreateUserDto {
  email: string;
  password: string;
  name: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

/**
 * Users V1 Controller
 * @deprecated This controller uses API v1 which is deprecated
 */
@ApiV1("Users")
@Controller({ path: "users", version: "1" })
@UseInterceptors(DeprecationInterceptor)
export class UsersV1Controller extends BaseControllerV1 {
  constructor(private readonly usersService: any) {
    super();
  }

  /**
   * Create a new user (v1)
   */
  @Post()
  @ApiOperation({
    summary: "Create a new user (v1 - Deprecated)",
    description: "Creates a new user with the provided information",
  })
  @ApiResponse({
    status: 201,
    description: "User created successfully",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        data: {
          type: "object",
          properties: {
            id: { type: "string" },
            email: { type: "string" },
            name: { type: "string" },
          },
        },
        message: { type: "string", example: "User created successfully" },
      },
    },
  })
  @ApiDeprecated("Use POST /api/v2/users instead", "/api/v2/users")
  async create(@Body() createUserDto: CreateUserDto) {
    // Log deprecation warning
    this.logDeprecationWarning("POST /api/v1/users");

    // Create user using service
    const user = await this.usersService.create(createUserDto);

    // Return v1 format response
    return this.success(user, "User created successfully");
  }

  /**
   * Get all users (v1)
   */
  @Get()
  @ApiOperation({
    summary: "Get all users (v1 - Deprecated)",
    description: "Retrieves a list of all users with v1 pagination",
  })
  @ApiQuery({ name: "skip", required: false, type: Number, example: 0 })
  @ApiQuery({ name: "take", required: false, type: Number, example: 20 })
  @ApiResponse({
    status: 200,
    description: "Users retrieved successfully",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        data: { type: "array", items: { type: "object" } },
        count: { type: "number", example: 100 },
      },
    },
  })
  @ApiDeprecated("Use GET /api/v2/users instead", "/api/v2/users")
  async findAll(@Query("skip") skip?: string, @Query("take") take?: string) {
    // Log deprecation warning
    this.logDeprecationWarning("GET /api/v1/users");

    // Parse v1 pagination parameters
    const skipNum = skip ? parseInt(skip, 10) : 0;
    const takeNum = take ? parseInt(take, 10) : 20;

    // Fetch users
    const users = await this.usersService.findAll({
      skip: skipNum,
      take: takeNum,
    });

    const total = await this.usersService.count();

    // Return v1 format paginated response
    return this.paginated(users, {
      skip: skipNum,
      take: takeNum,
      count: total,
    });
  }

  /**
   * Get user by ID (v1)
   */
  @Get(":id")
  @ApiOperation({
    summary: "Get user by ID (v1 - Deprecated)",
    description: "Retrieves a single user by their ID",
  })
  @ApiResponse({
    status: 200,
    description: "User retrieved successfully",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: true },
        data: { type: "object" },
      },
    },
  })
  @ApiResponse({
    status: 404,
    description: "User not found",
    schema: {
      type: "object",
      properties: {
        success: { type: "boolean", example: false },
        message: { type: "string", example: "User not found" },
      },
    },
  })
  @ApiDeprecated("Use GET /api/v2/users/:id instead", "/api/v2/users/:id")
  async findOne(@Param("id") id: string) {
    // Log deprecation warning
    this.logDeprecationWarning(`GET /api/v1/users/${id}`);

    // Fetch user
    const user = await this.usersService.findOne(id);

    if (!user) {
      return this.error("User not found");
    }

    // Return v1 format response
    return this.success(user);
  }
}

/**
 * Example v1 response:
 *
 * GET /api/v1/users
 * {
 *   "success": true,
 *   "data": [
 *     {
 *       "id": "123",
 *       "email": "user@example.com",
 *       "name": "John Doe"
 *     }
 *   ],
 *   "count": 100
 * }
 *
 * Headers:
 * X-API-Version: 1
 * X-API-Deprecated: true
 * X-API-Deprecation-Date: 2025-06-30
 * X-API-Sunset-Date: 2026-06-30
 * Link: </api/v2/users>; rel="successor-version"
 * Warning: 299 - "API version 1 is deprecated and will be removed on 2026-06-30"
 */

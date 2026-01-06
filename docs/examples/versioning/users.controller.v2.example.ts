/**
 * Example: Users Controller V2 (Current)
 * Demonstrates how to create a v2 controller with enhanced features
 */

import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
} from '@nestjs/common';
import { ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import {
  BaseControllerV2,
  ApiV2,
  RequestId,
  SortOrder,
} from '@sahool/versioning';

// DTO imports
interface CreateUserV2Dto {
  email: string;
  password: string;
  name: string;
  phoneNumber?: string;
  role?: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  phoneNumber?: string;
  role: string;
  status: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Users V2 Controller
 * Enhanced version with improved pagination and response format
 */
@ApiV2('Users')
@Controller({ path: 'users', version: '2' })
export class UsersV2Controller extends BaseControllerV2 {
  constructor(private readonly usersService: any) {
    super();
  }

  /**
   * Create a new user (v2)
   */
  @Post()
  @ApiOperation({
    summary: 'Create a new user (v2)',
    description: 'Creates a new user with enhanced validation and response format',
  })
  @ApiResponse({
    status: 201,
    description: 'User created successfully',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean', example: true },
        data: { type: 'object' },
        message: { type: 'string', example: 'User created successfully' },
        version: { type: 'string', example: '2' },
        timestamp: { type: 'string', example: '2026-01-06T10:30:00Z' },
        meta: {
          type: 'object',
          properties: {
            requestId: { type: 'string', example: 'req_123456' },
          },
        },
      },
    },
  })
  async create(
    @Body() createUserDto: CreateUserV2Dto,
    @RequestId() requestId: string,
  ) {
    // Create user using service
    const user = await this.usersService.create(createUserDto);

    // Return v2 format response
    return this.success(user, requestId, 'User created successfully');
  }

  /**
   * Get all users (v2)
   */
  @Get()
  @ApiOperation({
    summary: 'Get all users (v2)',
    description: 'Retrieves a list of all users with enhanced pagination and sorting',
  })
  @ApiQuery({
    name: 'page',
    required: false,
    type: Number,
    example: 1,
    description: 'Page number (starts at 1)',
  })
  @ApiQuery({
    name: 'limit',
    required: false,
    type: Number,
    example: 20,
    description: 'Number of items per page (max 100)',
  })
  @ApiQuery({
    name: 'sort',
    required: false,
    type: String,
    example: 'createdAt',
    description: 'Field to sort by',
  })
  @ApiQuery({
    name: 'order',
    required: false,
    enum: ['asc', 'desc'],
    example: 'desc',
    description: 'Sort order',
  })
  @ApiQuery({
    name: 'status',
    required: false,
    type: String,
    example: 'active',
    description: 'Filter by user status',
  })
  @ApiResponse({
    status: 200,
    description: 'Users retrieved successfully',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean', example: true },
        data: { type: 'array', items: { type: 'object' } },
        version: { type: 'string', example: '2' },
        timestamp: { type: 'string', example: '2026-01-06T10:30:00Z' },
        meta: {
          type: 'object',
          properties: {
            requestId: { type: 'string', example: 'req_123456' },
            pagination: {
              type: 'object',
              properties: {
                page: { type: 'number', example: 1 },
                limit: { type: 'number', example: 20 },
                total: { type: 'number', example: 100 },
                totalPages: { type: 'number', example: 5 },
                hasNext: { type: 'boolean', example: true },
                hasPrev: { type: 'boolean', example: false },
              },
            },
          },
        },
      },
    },
  })
  async findAll(
    @RequestId() requestId: string,
    @Query('page') page?: string,
    @Query('limit') limit?: string,
    @Query('sort') sort?: string,
    @Query('order') order?: string,
    @Query('status') status?: string,
  ) {
    // Parse v2 pagination parameters
    const { page: p, limit: l, skip } = this.parsePaginationParams(page, limit);

    // Parse sort parameters
    const { field, order: sortOrder } = this.parseSortParams(sort, order);

    // Build filter options
    const filterOptions = {
      skip,
      take: l,
      sortBy: field,
      sortOrder,
      ...(status && { status }),
    };

    // Fetch users with count
    const [users, total] = await this.usersService.findAllWithCount(filterOptions);

    // Return v2 format paginated response
    return this.paginated(users, p, l, total, requestId);
  }

  /**
   * Get user by ID (v2)
   */
  @Get(':id')
  @ApiOperation({
    summary: 'Get user by ID (v2)',
    description: 'Retrieves a single user by their ID with enhanced error handling',
  })
  @ApiResponse({
    status: 200,
    description: 'User retrieved successfully',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean', example: true },
        data: { type: 'object' },
        version: { type: 'string', example: '2' },
        timestamp: { type: 'string', example: '2026-01-06T10:30:00Z' },
        meta: {
          type: 'object',
          properties: {
            requestId: { type: 'string', example: 'req_123456' },
          },
        },
      },
    },
  })
  @ApiResponse({
    status: 404,
    description: 'User not found',
    schema: {
      type: 'object',
      properties: {
        success: { type: 'boolean', example: false },
        error: {
          type: 'object',
          properties: {
            code: { type: 'string', example: 'USER_NOT_FOUND' },
            message: { type: 'string', example: 'User not found' },
            details: { type: 'string', example: 'No user exists with ID: 123' },
            timestamp: { type: 'string', example: '2026-01-06T10:30:00Z' },
          },
        },
        version: { type: 'string', example: '2' },
        meta: {
          type: 'object',
          properties: {
            requestId: { type: 'string', example: 'req_123456' },
            documentation: {
              type: 'string',
              example: 'https://docs.sahool.app/errors/USER_NOT_FOUND'
            },
          },
        },
      },
    },
  })
  async findOne(
    @Param('id') id: string,
    @RequestId() requestId: string,
  ) {
    // Fetch user
    const user = await this.usersService.findOne(id);

    if (!user) {
      // Return v2 format error response
      return this.error(
        'USER_NOT_FOUND',
        'User not found',
        requestId,
        `No user exists with ID: ${id}`,
        'userId',
      );
    }

    // Return v2 format response
    return this.success(user, requestId);
  }

  /**
   * Get user statistics (v2 only)
   */
  @Get('stats/summary')
  @ApiOperation({
    summary: 'Get user statistics (v2 only)',
    description: 'New endpoint available only in v2',
  })
  @ApiResponse({
    status: 200,
    description: 'Statistics retrieved successfully',
  })
  async getStatistics(@RequestId() requestId: string) {
    const stats = await this.usersService.getStatistics();

    return this.success(stats, requestId, 'Statistics retrieved successfully');
  }
}

/**
 * Example v2 response:
 *
 * GET /api/v2/users?page=1&limit=20&sort=createdAt&order=desc
 * {
 *   "success": true,
 *   "data": [
 *     {
 *       "id": "123",
 *       "email": "user@example.com",
 *       "name": "John Doe",
 *       "phoneNumber": "+967123456789",
 *       "role": "FARMER",
 *       "status": "ACTIVE",
 *       "createdAt": "2026-01-01T00:00:00Z",
 *       "updatedAt": "2026-01-06T10:30:00Z"
 *     }
 *   ],
 *   "version": "2",
 *   "timestamp": "2026-01-06T10:30:00Z",
 *   "meta": {
 *     "requestId": "req_123456",
 *     "pagination": {
 *       "page": 1,
 *       "limit": 20,
 *       "total": 100,
 *       "totalPages": 5,
 *       "hasNext": true,
 *       "hasPrev": false
 *     }
 *   }
 * }
 *
 * Headers:
 * X-API-Version: 2
 * X-Request-ID: req_123456
 */

/**
 * Example v2 error response:
 *
 * GET /api/v2/users/999
 * {
 *   "success": false,
 *   "error": {
 *     "code": "USER_NOT_FOUND",
 *     "message": "User not found",
 *     "details": "No user exists with ID: 999",
 *     "field": "userId",
 *     "timestamp": "2026-01-06T10:30:00Z"
 *   },
 *   "version": "2",
 *   "meta": {
 *     "requestId": "req_123456",
 *     "documentation": "https://docs.sahool.app/errors/USER_NOT_FOUND"
 *   }
 * }
 */

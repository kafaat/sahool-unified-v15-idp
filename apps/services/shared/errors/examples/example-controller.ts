/**
 * Example Controller Implementation
 * مثال على تطبيق المتحكم
 *
 * @description Demonstrates how to use error handling in NestJS controllers
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
  ApiBody,
} from '@nestjs/swagger';
import {
  ErrorResponseDto,
  ValidationErrorResponseDto,
  SuccessResponseDto,
  PaginatedResponseDto,
} from '../error-response.dto';
import { ExampleFarmService } from './example-service';

/**
 * Example Controller
 * متحكم المثال
 */
@ApiTags('Farms (Example)')
@Controller('api/v1/example/farms')
export class ExampleFarmController {
  constructor(private readonly farmService: ExampleFarmService) {}

  /**
   * Create a new farm
   * إنشاء مزرعة جديدة
   */
  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Create a new farm',
    description: 'إنشاء مزرعة جديدة',
  })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        name: { type: 'string', example: 'My Farm' },
        area: { type: 'number', example: 100 },
        location: {
          type: 'object',
          properties: {
            lat: { type: 'number', example: 15.5527 },
            lng: { type: 'number', example: 48.5164 },
          },
        },
      },
      required: ['name', 'area', 'location'],
    },
  })
  @ApiResponse({
    status: 201,
    description: 'Farm created successfully',
    type: SuccessResponseDto,
  })
  @ApiResponse({
    status: 400,
    description: 'Validation error',
    type: ValidationErrorResponseDto,
  })
  @ApiResponse({
    status: 500,
    description: 'Internal server error',
    type: ErrorResponseDto,
  })
  async create(@Body() data: any) {
    // Validate the data (this will throw ValidationException if invalid)
    await this.farmService.validateFarmData(data);

    // Create the farm
    const farm = await this.farmService.create(data);

    // Return success response
    return this.farmService.getById(farm.id);
  }

  /**
   * Get all farms with pagination
   * الحصول على جميع المزارع مع التقسيم إلى صفحات
   */
  @Get()
  @ApiOperation({
    summary: 'Get all farms',
    description: 'الحصول على جميع المزارع مع التقسيم إلى صفحات',
  })
  @ApiQuery({
    name: 'page',
    required: false,
    type: Number,
    description: 'Page number (default: 1)',
    example: 1,
  })
  @ApiQuery({
    name: 'limit',
    required: false,
    type: Number,
    description: 'Items per page (default: 20)',
    example: 20,
  })
  @ApiResponse({
    status: 200,
    description: 'Farms retrieved successfully',
    type: PaginatedResponseDto,
  })
  async findAll(
    @Query('page') page: string = '1',
    @Query('limit') limit: string = '20',
  ) {
    return this.farmService.findAll(parseInt(page, 10), parseInt(limit, 10));
  }

  /**
   * Get farm by ID
   * الحصول على مزرعة حسب المعرف
   */
  @Get(':id')
  @ApiOperation({
    summary: 'Get farm by ID',
    description: 'الحصول على مزرعة حسب المعرف',
  })
  @ApiParam({
    name: 'id',
    description: 'Farm ID',
    example: 'farm-123',
  })
  @ApiResponse({
    status: 200,
    description: 'Farm found',
    type: SuccessResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: 'Farm not found',
    type: ErrorResponseDto,
  })
  async findById(@Param('id') id: string) {
    // This will throw NotFoundException if farm doesn't exist
    return this.farmService.getById(id);
  }

  /**
   * Update farm
   * تحديث المزرعة
   */
  @Put(':id')
  @ApiOperation({
    summary: 'Update farm',
    description: 'تحديث بيانات المزرعة',
  })
  @ApiParam({
    name: 'id',
    description: 'Farm ID',
    example: 'farm-123',
  })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        name: { type: 'string', example: 'Updated Farm Name' },
        area: { type: 'number', example: 150 },
      },
    },
  })
  @ApiResponse({
    status: 200,
    description: 'Farm updated successfully',
    type: SuccessResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: 'Farm not found',
    type: ErrorResponseDto,
  })
  async update(@Param('id') id: string, @Body() data: any) {
    // Using the decorator-based error handling
    const farm = await this.farmService.updateWithDecorator(id, data);
    return this.farmService.getById(farm.id);
  }

  /**
   * Delete farm
   * حذف المزرعة
   */
  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({
    summary: 'Archive farm',
    description: 'أرشفة المزرعة',
  })
  @ApiParam({
    name: 'id',
    description: 'Farm ID',
    example: 'farm-123',
  })
  @ApiResponse({
    status: 204,
    description: 'Farm archived successfully',
  })
  @ApiResponse({
    status: 404,
    description: 'Farm not found',
    type: ErrorResponseDto,
  })
  @ApiResponse({
    status: 422,
    description: 'Cannot archive farm with active crops',
    type: ErrorResponseDto,
  })
  async archive(@Param('id') id: string) {
    // This will throw BusinessLogicException if farm has active crops
    await this.farmService.archiveFarm(id);
  }

  /**
   * Transfer area between farms
   * نقل المساحة بين المزارع
   */
  @Post(':fromId/transfer/:toId')
  @ApiOperation({
    summary: 'Transfer area between farms',
    description: 'نقل المساحة من مزرعة إلى أخرى',
  })
  @ApiParam({
    name: 'fromId',
    description: 'Source farm ID',
    example: 'farm-123',
  })
  @ApiParam({
    name: 'toId',
    description: 'Destination farm ID',
    example: 'farm-456',
  })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        area: { type: 'number', example: 25 },
      },
      required: ['area'],
    },
  })
  @ApiResponse({
    status: 200,
    description: 'Area transferred successfully',
    type: SuccessResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: 'Farm not found',
    type: ErrorResponseDto,
  })
  @ApiResponse({
    status: 422,
    description: 'Insufficient area or invalid amount',
    type: ErrorResponseDto,
  })
  async transferArea(
    @Param('fromId') fromId: string,
    @Param('toId') toId: string,
    @Body('area') area: number,
  ) {
    // This will throw BusinessLogicException if:
    // 1. Amount is not positive
    // 2. Source farm doesn't have sufficient area
    await this.farmService.transferArea(fromId, toId, area);

    return {
      success: true,
      message: 'Area transferred successfully',
      messageAr: 'تم نقل المساحة بنجاح',
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Get weather data for farm
   * الحصول على بيانات الطقس للمزرعة
   */
  @Get(':id/weather')
  @ApiOperation({
    summary: 'Get farm weather data',
    description: 'الحصول على بيانات الطقس للمزرعة',
  })
  @ApiParam({
    name: 'id',
    description: 'Farm ID',
    example: 'farm-123',
  })
  @ApiResponse({
    status: 200,
    description: 'Weather data retrieved successfully',
    type: SuccessResponseDto,
  })
  @ApiResponse({
    status: 404,
    description: 'Farm not found',
    type: ErrorResponseDto,
  })
  @ApiResponse({
    status: 502,
    description: 'Weather service unavailable',
    type: ErrorResponseDto,
  })
  async getWeather(@Param('id') id: string) {
    // This will throw ExternalServiceException if weather service fails
    const weatherData = await this.farmService.fetchWeatherData(id);

    return {
      success: true,
      data: weatherData,
      message: 'Weather data retrieved successfully',
      messageAr: 'تم استرجاع بيانات الطقس بنجاح',
      timestamp: new Date().toISOString(),
    };
  }
}

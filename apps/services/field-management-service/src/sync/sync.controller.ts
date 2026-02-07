/**
 * Sync Controller - Mobile Sync Endpoints
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Body,
  Query,
  ValidationPipe,
  HttpCode,
  HttpStatus,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from "@nestjs/swagger";
import { SyncService } from "./sync.service";
import {
  IsString,
  IsOptional,
  IsBoolean,
  IsNumber,
  IsArray,
  IsObject,
  Min,
  Max,
} from "class-validator";
import { Type, Transform } from "class-transformer";

class DeltaSyncQueryDto {
  @IsString()
  tenantId: string;

  @IsOptional()
  @IsString()
  since?: string;

  @IsOptional()
  @Transform(({ value }) => value === "true")
  @IsBoolean()
  includeDeleted?: boolean;

  @IsOptional()
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  @Max(100)
  limit?: number;
}

class BatchSyncDto {
  @IsString()
  deviceId: string;

  @IsString()
  userId: string;

  @IsString()
  tenantId: string;

  @IsArray()
  fields: any[];
}

class SyncStatusQueryDto {
  @IsString()
  deviceId: string;

  @IsString()
  tenantId: string;

  @IsOptional()
  @IsString()
  userId?: string;
}

class UpdateSyncStatusDto {
  @IsString()
  deviceId: string;

  @IsString()
  userId: string;

  @IsString()
  tenantId: string;

  @IsOptional()
  @IsNumber()
  lastSyncVersion?: number;

  @IsOptional()
  @IsObject()
  deviceInfo?: any;

  @IsOptional()
  @IsString()
  status?: string;
}

@ApiTags("Sync - المزامنة")
@Controller("api/v1")
export class SyncController {
  constructor(private readonly syncService: SyncService) {}

  /**
   * Delta sync - get fields modified since timestamp
   */
  @Get("fields/sync")
  @ApiOperation({
    summary: "Delta sync fields",
    description: "جلب الحقول المعدلة منذ وقت محدد",
  })
  @ApiQuery({ name: "tenantId", required: true })
  @ApiQuery({ name: "since", required: false })
  @ApiQuery({ name: "includeDeleted", required: false })
  @ApiQuery({ name: "limit", required: false })
  @ApiResponse({ status: 200, description: "Sync data retrieved" })
  async deltaSync(
    @Query(new ValidationPipe({ transform: true })) query: DeltaSyncQueryDto,
  ) {
    const result = await this.syncService.deltaSync(query);
    return {
      success: true,
      ...result,
    };
  }

  /**
   * Batch sync - upload multiple fields
   */
  @Post("fields/sync/batch")
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Batch sync fields",
    description: "تحميل مجموعة من الحقول مع اكتشاف التعارض",
  })
  @ApiResponse({ status: 200, description: "Batch sync completed" })
  async batchSync(
    @Body(new ValidationPipe({ transform: true })) dto: BatchSyncDto,
  ) {
    const result = await this.syncService.batchSync(dto);
    return {
      success: true,
      ...result,
    };
  }

  /**
   * Get sync status for a device
   */
  @Get("sync/status")
  @ApiOperation({
    summary: "Get device sync status",
    description: "جلب حالة مزامنة الجهاز",
  })
  @ApiQuery({ name: "deviceId", required: true })
  @ApiQuery({ name: "tenantId", required: true })
  @ApiQuery({ name: "userId", required: false })
  @ApiResponse({ status: 200, description: "Sync status retrieved" })
  async getSyncStatus(
    @Query(new ValidationPipe({ transform: true })) query: SyncStatusQueryDto,
  ) {
    const status = await this.syncService.getSyncStatus(
      query.deviceId,
      query.tenantId,
      query.userId,
    );
    return {
      success: true,
      data: status,
    };
  }

  /**
   * Update sync status
   */
  @Put("sync/status")
  @ApiOperation({
    summary: "Update device sync status",
    description: "تحديث حالة مزامنة الجهاز",
  })
  @ApiResponse({ status: 200, description: "Sync status updated" })
  async updateSyncStatus(
    @Body(new ValidationPipe({ transform: true })) dto: UpdateSyncStatusDto,
  ) {
    const status = await this.syncService.updateDeviceSyncStatus(dto);
    return {
      success: true,
      data: status,
      message: "تم تحديث حالة المزامنة بنجاح",
    };
  }
}

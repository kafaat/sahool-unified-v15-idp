/**
 * NDVI Controller - Vegetation Index Endpoints
 */

import {
  Controller,
  Get,
  Put,
  Body,
  Param,
  Query,
  ParseUUIDPipe,
  ValidationPipe,
  Req,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiParam, ApiQuery } from "@nestjs/swagger";
import { NdviService } from "./ndvi.service";
import { IsNumber, IsOptional, IsString, Min, Max } from "class-validator";

class UpdateNdviDto {
  @IsNumber()
  @Min(-1)
  @Max(1)
  value: number;

  @IsOptional()
  @IsString()
  source?: string;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100)
  cloudCover?: number;
}

@ApiTags("NDVI - مؤشر الغطاء النباتي")
@Controller("api/v1")
export class NdviController {
  constructor(private readonly ndviService: NdviService) {}

  /**
   * Get NDVI analysis for a field
   */
  @Get("fields/:id/ndvi")
  @ApiOperation({ summary: "Get NDVI analysis for a field" })
  @ApiParam({ name: "id", type: String })
  @ApiResponse({ status: 200, description: "NDVI data retrieved" })
  async getFieldNdvi(@Param("id", ParseUUIDPipe) id: string) {
    const data = await this.ndviService.getFieldNdvi(id);
    return {
      success: true,
      data,
    };
  }

  /**
   * Update NDVI value for a field
   */
  @Put("fields/:id/ndvi")
  @ApiOperation({ summary: "Update NDVI value" })
  @ApiParam({ name: "id", type: String })
  @ApiResponse({ status: 200, description: "NDVI updated" })
  async updateFieldNdvi(
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: UpdateNdviDto,
  ) {
    const data = await this.ndviService.updateFieldNdvi(
      id,
      dto.value,
      dto.source,
      dto.cloudCover,
    );
    return {
      success: true,
      data,
      message: "تم تحديث مؤشر NDVI بنجاح",
    };
  }

  /**
   * Get NDVI summary for a tenant
   */
  @Get("ndvi/summary")
  @ApiOperation({ summary: "Get NDVI summary for tenant" })
  @ApiQuery({ name: "tenantId", required: false })
  @ApiResponse({ status: 200, description: "NDVI summary retrieved" })
  async getTenantSummary(
    @Req() req: any,
    @Query("tenantId") queryTenantId?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'] || queryTenantId;
    const data = await this.ndviService.getTenantNdviSummary(tenantId);
    return {
      success: true,
      data,
    };
  }
}

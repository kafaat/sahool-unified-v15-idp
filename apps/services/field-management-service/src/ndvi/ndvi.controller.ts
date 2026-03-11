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
import { getRequestTenantId } from "../auth/tenant.utils";

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
  async getFieldNdvi(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const data = await this.ndviService.getFieldNdvi(id, tenantId);
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
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: UpdateNdviDto,
  ) {
    const tenantId = getRequestTenantId(req);
    const data = await this.ndviService.updateFieldNdvi(
      id,
      tenantId,
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
  @ApiResponse({ status: 200, description: "NDVI summary retrieved" })
  async getTenantSummary(@Req() req: any) {
    // Always use authenticated tenant, ignore query params
    const tenantId = getRequestTenantId(req);
    const data = await this.ndviService.getTenantNdviSummary(tenantId);
    return {
      success: true,
      data,
    };
  }
}

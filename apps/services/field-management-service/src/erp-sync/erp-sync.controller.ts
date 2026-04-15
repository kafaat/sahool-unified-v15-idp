/**
 * ERP Sync Controller
 * وحدة تحكم تكامل ERP
 */

import {
  Controller,
  Post,
  Get,
  Param,
  ParseUUIDPipe,
  Req,
  HttpCode,
  HttpStatus,
  UseInterceptors,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiParam } from "@nestjs/swagger";
import { ErpSyncService } from "./erp-sync.service";
import { IdempotencyInterceptor } from "../idempotency/idempotency.interceptor";
import { getRequestTenantId } from "../auth/tenant.utils";

@ApiTags("ERP Sync - تكامل المحاسبة")
@Controller("api/v1/erp-sync")
export class ErpSyncController {
  constructor(private readonly service: ErpSyncService) {}

  /**
   * Trigger posting of a FieldOperation to every enabled ERP adapter.
   * Idempotent via Idempotency-Key header so clients can safely retry
   * after a network error.
   */
  @Post("field-operations/:id/post")
  @HttpCode(HttpStatus.OK)
  @UseInterceptors(IdempotencyInterceptor)
  @ApiOperation({
    summary: "Post a field operation to external ERP",
    description: "ترحيل عملية الحقل إلى نظام ERP الخارجي",
  })
  @ApiParam({ name: "id", description: "FieldOperation UUID" })
  async postFieldOperation(
    @Req() req: any,
    @Param("id", ParseUUIDPipe) id: string,
  ) {
    const tenantId = getRequestTenantId(req);
    const results = await this.service.postFieldOperation(id, tenantId);
    return { success: true, data: results };
  }

  /**
   * Health check — which adapters are enabled and reachable.
   */
  @Get("health")
  @ApiOperation({ summary: "ERP sync adapter health" })
  async health() {
    const data = await this.service.health();
    return { success: true, data };
  }
}

import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  Request,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiBearerAuth,
  ApiQuery,
} from "@nestjs/swagger";
import { ProtocolsService } from "./protocols.service";
import { CreateProtocolDto, UpdateProtocolDto } from "./dto/protocol.dto";
import { ScientificLockGuard } from "@/core/guards/scientific-lock.guard";

@ApiTags("protocols")
@ApiBearerAuth()
@Controller("experiments/:experimentId/protocols")
@UseGuards(ScientificLockGuard)
export class ProtocolsController {
  constructor(private readonly service: ProtocolsService) {}

  @Post()
  @ApiOperation({ summary: "Create new protocol - إنشاء بروتوكول جديد" })
  create(
    @Param("experimentId") experimentId: string,
    @Body() dto: CreateProtocolDto,
    @Request() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.create({ ...dto, experimentId }, tenantId);
  }

  @Get()
  @ApiOperation({ summary: "List experiment protocols - قائمة البروتوكولات" })
  @ApiQuery({ name: "page", required: false, type: Number })
  @ApiQuery({ name: "limit", required: false, type: Number })
  findAll(
    @Param("experimentId") experimentId: string,
    @Request() req: any,
    @Query("page") page?: number,
    @Query("limit") limit?: number,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.findAll(experimentId, tenantId, { page, limit });
  }

  @Get(":id")
  @ApiOperation({ summary: "Get protocol details - تفاصيل البروتوكول" })
  findOne(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.findOne(id, tenantId);
  }

  @Put(":id")
  @ApiOperation({ summary: "Update protocol - تحديث البروتوكول" })
  update(@Param("id") id: string, @Body() dto: UpdateProtocolDto, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.update(id, dto, tenantId);
  }

  @Post(":id/approve")
  @ApiOperation({ summary: "Approve protocol - اعتماد البروتوكول" })
  approve(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.approve(id, req.user?.id || "system", tenantId);
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete protocol - حذف البروتوكول" })
  delete(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.delete(id, tenantId);
  }
}

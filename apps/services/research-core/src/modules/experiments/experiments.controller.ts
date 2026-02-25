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
import { ExperimentsService } from "./experiments.service";
import { CreateExperimentDto, UpdateExperimentDto } from "./dto/experiment.dto";
import { ScientificLockGuard } from "@/core/guards/scientific-lock.guard";

@ApiTags("experiments")
@ApiBearerAuth()
@Controller("experiments")
@UseGuards(ScientificLockGuard)
export class ExperimentsController {
  constructor(private readonly service: ExperimentsService) {}

  @Post()
  @ApiOperation({ summary: "Create new experiment - إنشاء تجربة جديدة" })
  create(@Body() dto: CreateExperimentDto, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.create(dto, req.user?.id || "system", tenantId);
  }

  @Get()
  @ApiOperation({ summary: "List all experiments - قائمة التجارب" })
  @ApiQuery({ name: "status", required: false })
  @ApiQuery({ name: "researcherId", required: false })
  @ApiQuery({ name: "page", required: false, type: Number })
  @ApiQuery({ name: "limit", required: false, type: Number })
  findAll(
    @Request() req: any,
    @Query("status") status?: string,
    @Query("researcherId") researcherId?: string,
    @Query("page") page?: number,
    @Query("limit") limit?: number,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.findAll(tenantId, { status, researcherId, page, limit });
  }

  @Get(":id")
  @ApiOperation({ summary: "Get experiment details - تفاصيل التجربة" })
  findOne(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.findOne(id, tenantId);
  }

  @Get(":id/summary")
  @ApiOperation({ summary: "Get experiment summary - ملخص التجربة" })
  getSummary(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.getSummary(id, tenantId);
  }

  @Put(":id")
  @ApiOperation({ summary: "Update experiment - تحديث التجربة" })
  update(@Param("id") id: string, @Body() dto: UpdateExperimentDto, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.update(id, dto, tenantId);
  }

  @Post(":id/lock")
  @ApiOperation({ summary: "Lock experiment - قفل التجربة" })
  lock(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.lock(id, req.user?.id || "system", tenantId);
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete experiment - حذف التجربة" })
  delete(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.delete(id, tenantId);
  }
}

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
  ParseBoolPipe,
  Request,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiBearerAuth,
  ApiQuery,
} from "@nestjs/swagger";
import { TreatmentsService } from "./treatments.service";
import { CreateTreatmentDto, UpdateTreatmentDto } from "./dto/treatment.dto";
import { ScientificLockGuard } from "@/core/guards/scientific-lock.guard";

@ApiTags("treatments")
@ApiBearerAuth()
@Controller("experiments/:experimentId/treatments")
@UseGuards(ScientificLockGuard)
export class TreatmentsController {
  constructor(private readonly service: TreatmentsService) {}

  @Post()
  @ApiOperation({ summary: "Create new treatment - إنشاء معالجة جديدة" })
  create(
    @Param("experimentId") experimentId: string,
    @Body() dto: CreateTreatmentDto,
    @Request() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.create({ ...dto, experimentId }, tenantId);
  }

  @Get()
  @ApiOperation({ summary: "List experiment treatments - قائمة المعالجات" })
  @ApiQuery({ name: "plotId", required: false })
  @ApiQuery({ name: "type", required: false })
  @ApiQuery({ name: "isControl", required: false, type: Boolean })
  @ApiQuery({ name: "page", required: false, type: Number })
  @ApiQuery({ name: "limit", required: false, type: Number })
  findAll(
    @Param("experimentId") experimentId: string,
    @Request() req: any,
    @Query("plotId") plotId?: string,
    @Query("type") type?: string,
    @Query("isControl") isControl?: boolean,
    @Query("page") page?: number,
    @Query("limit") limit?: number,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.findAll(experimentId, tenantId, {
      plotId,
      type,
      isControl,
      page,
      limit,
    });
  }

  @Get(":id")
  @ApiOperation({ summary: "Get treatment details - تفاصيل المعالجة" })
  findOne(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.findOne(id, tenantId);
  }

  @Put(":id")
  @ApiOperation({ summary: "Update treatment - تحديث المعالجة" })
  update(@Param("id") id: string, @Body() dto: UpdateTreatmentDto, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.update(id, dto, tenantId);
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete treatment - حذف المعالجة" })
  delete(@Param("id") id: string, @Request() req: any) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    return this.service.delete(id, tenantId);
  }
}

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
import { LogsService } from "./logs.service";
import { CreateLogDto, UpdateLogDto, SyncLogDto } from "./dto/log.dto";
import { ScientificLockGuard } from "@/core/guards/scientific-lock.guard";

@ApiTags("logs")
@ApiBearerAuth()
@Controller("experiments/:experimentId/logs")
@UseGuards(ScientificLockGuard)
export class LogsController {
  constructor(private readonly service: LogsService) {}

  @Post()
  @ApiOperation({ summary: "Create daily log - إنشاء سجل يومي" })
  create(
    @Param("experimentId") experimentId: string,
    @Body() dto: CreateLogDto,
    @Request() req: any,
  ) {
    return this.service.create(
      { ...dto, experimentId },
      req.user?.id || "system",
    );
  }

  @Get()
  @ApiOperation({ summary: "List experiment logs - قائمة السجلات" })
  @ApiQuery({ name: "plotId", required: false })
  @ApiQuery({ name: "category", required: false })
  @ApiQuery({ name: "startDate", required: false })
  @ApiQuery({ name: "endDate", required: false })
  @ApiQuery({ name: "page", required: false, type: Number })
  @ApiQuery({ name: "limit", required: false, type: Number })
  findAll(
    @Param("experimentId") experimentId: string,
    @Query("plotId") plotId?: string,
    @Query("category") category?: string,
    @Query("startDate") startDate?: string,
    @Query("endDate") endDate?: string,
    @Query("page") page?: number,
    @Query("limit") limit?: number,
  ) {
    return this.service.findAll(experimentId, {
      plotId,
      category,
      startDate,
      endDate,
      page,
      limit,
    });
  }

  @Get(":id")
  @ApiOperation({ summary: "Get log details - تفاصيل السجل" })
  findOne(@Param("id") id: string) {
    return this.service.findOne(id);
  }

  @Get(":id/verify")
  @ApiOperation({ summary: "Verify log integrity - التحقق من سلامة السجل" })
  verifyIntegrity(@Param("id") id: string) {
    return this.service.verifyLogIntegrity(id);
  }

  @Put(":id")
  @ApiOperation({ summary: "Update log - تحديث السجل" })
  update(
    @Param("id") id: string,
    @Body() dto: UpdateLogDto,
    @Request() req: any,
  ) {
    return this.service.update(id, dto, req.user?.id || "system");
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete log - حذف السجل" })
  delete(@Param("id") id: string) {
    return this.service.delete(id);
  }

  @Post("sync")
  @ApiOperation({ summary: "Sync offline logs - مزامنة السجلات غير المتصلة" })
  syncOffline(@Body() logs: SyncLogDto[], @Request() req: any) {
    return this.service.syncOfflineLogs(logs, req.user?.id || "system");
  }
}

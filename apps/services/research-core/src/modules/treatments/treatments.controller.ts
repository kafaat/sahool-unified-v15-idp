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
  ) {
    return this.service.create({ ...dto, experimentId });
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
    @Query("plotId") plotId?: string,
    @Query("type") type?: string,
    @Query("isControl") isControl?: boolean,
    @Query("page") page?: number,
    @Query("limit") limit?: number,
  ) {
    return this.service.findAll(experimentId, {
      plotId,
      type,
      isControl,
      page,
      limit,
    });
  }

  @Get(":id")
  @ApiOperation({ summary: "Get treatment details - تفاصيل المعالجة" })
  findOne(@Param("id") id: string) {
    return this.service.findOne(id);
  }

  @Put(":id")
  @ApiOperation({ summary: "Update treatment - تحديث المعالجة" })
  update(@Param("id") id: string, @Body() dto: UpdateTreatmentDto) {
    return this.service.update(id, dto);
  }

  @Delete(":id")
  @ApiOperation({ summary: "Delete treatment - حذف المعالجة" })
  delete(@Param("id") id: string) {
    return this.service.delete(id);
  }
}

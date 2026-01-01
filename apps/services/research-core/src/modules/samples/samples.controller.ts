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
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiQuery } from '@nestjs/swagger';
import { SamplesService } from './samples.service';
import { CreateSampleDto, UpdateSampleDto } from './dto/sample.dto';
import { ScientificLockGuard } from '@/core/guards/scientific-lock.guard';

@ApiTags('samples')
@ApiBearerAuth()
@Controller('experiments/:experimentId/samples')
@UseGuards(ScientificLockGuard)
export class SamplesController {
  constructor(private readonly service: SamplesService) {}

  @Post()
  @ApiOperation({ summary: 'Create new sample - إنشاء عينة جديدة' })
  create(
    @Param('experimentId') experimentId: string,
    @Body() dto: CreateSampleDto,
  ) {
    return this.service.create({ ...dto, experimentId });
  }

  @Get()
  @ApiOperation({ summary: 'List experiment samples - قائمة العينات' })
  @ApiQuery({ name: 'plotId', required: false })
  @ApiQuery({ name: 'type', required: false })
  @ApiQuery({ name: 'analysisStatus', required: false })
  @ApiQuery({ name: 'collectedBy', required: false })
  @ApiQuery({ name: 'startDate', required: false })
  @ApiQuery({ name: 'endDate', required: false })
  @ApiQuery({ name: 'page', required: false, type: Number })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  findAll(
    @Param('experimentId') experimentId: string,
    @Query('plotId') plotId?: string,
    @Query('type') type?: string,
    @Query('analysisStatus') analysisStatus?: string,
    @Query('collectedBy') collectedBy?: string,
    @Query('startDate') startDate?: string,
    @Query('endDate') endDate?: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.service.findAll(experimentId, {
      plotId,
      type,
      analysisStatus,
      collectedBy,
      startDate,
      endDate,
      page,
      limit,
    });
  }

  @Get('code/:sampleCode')
  @ApiOperation({ summary: 'Get sample by code - الحصول على عينة بالرمز' })
  findBySampleCode(@Param('sampleCode') sampleCode: string) {
    return this.service.findBySampleCode(sampleCode);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get sample details - تفاصيل العينة' })
  findOne(@Param('id') id: string) {
    return this.service.findOne(id);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update sample - تحديث العينة' })
  update(@Param('id') id: string, @Body() dto: UpdateSampleDto) {
    return this.service.update(id, dto);
  }

  @Put(':id/analysis')
  @ApiOperation({ summary: 'Update analysis status - تحديث حالة التحليل' })
  updateAnalysis(
    @Param('id') id: string,
    @Body()
    body: {
      status: string;
      analyzedBy?: string;
      analysisResults?: Record<string, unknown>;
    },
    @Request() req: any,
  ) {
    return this.service.updateAnalysisStatus(
      id,
      body.status,
      body.analyzedBy || req.user?.id || 'system',
      body.analysisResults,
    );
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete sample - حذف العينة' })
  delete(@Param('id') id: string) {
    return this.service.delete(id);
  }
}

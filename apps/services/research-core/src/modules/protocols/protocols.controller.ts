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
import { ProtocolsService } from './protocols.service';
import { CreateProtocolDto, UpdateProtocolDto } from './dto/protocol.dto';
import { ScientificLockGuard } from '@/core/guards/scientific-lock.guard';

@ApiTags('protocols')
@ApiBearerAuth()
@Controller('experiments/:experimentId/protocols')
@UseGuards(ScientificLockGuard)
export class ProtocolsController {
  constructor(private readonly service: ProtocolsService) {}

  @Post()
  @ApiOperation({ summary: 'Create new protocol - إنشاء بروتوكول جديد' })
  create(
    @Param('experimentId') experimentId: string,
    @Body() dto: CreateProtocolDto,
  ) {
    return this.service.create({ ...dto, experimentId });
  }

  @Get()
  @ApiOperation({ summary: 'List experiment protocols - قائمة البروتوكولات' })
  @ApiQuery({ name: 'page', required: false, type: Number })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  findAll(
    @Param('experimentId') experimentId: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.service.findAll(experimentId, { page, limit });
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get protocol details - تفاصيل البروتوكول' })
  findOne(@Param('id') id: string) {
    return this.service.findOne(id);
  }

  @Put(':id')
  @ApiOperation({ summary: 'Update protocol - تحديث البروتوكول' })
  update(@Param('id') id: string, @Body() dto: UpdateProtocolDto) {
    return this.service.update(id, dto);
  }

  @Post(':id/approve')
  @ApiOperation({ summary: 'Approve protocol - اعتماد البروتوكول' })
  approve(@Param('id') id: string, @Request() req: any) {
    return this.service.approve(id, req.user?.id || 'system');
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete protocol - حذف البروتوكول' })
  delete(@Param('id') id: string) {
    return this.service.delete(id);
  }
}

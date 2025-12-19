import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Request,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { SignaturesService } from './signatures.service';

@ApiTags('signatures')
@ApiBearerAuth()
@Controller('signatures')
export class SignaturesController {
  constructor(private readonly service: SignaturesService) {}

  @Post('sign')
  @ApiOperation({ summary: 'Sign an entity - توقيع كيان' })
  sign(
    @Body()
    body: {
      entityType: string;
      entityId: string;
      purpose: string;
      data: Record<string, unknown>;
    },
    @Request() req: any,
  ) {
    return this.service.signEntity(
      body.entityType,
      body.entityId,
      req.user?.id || 'system',
      body.purpose,
      body.data,
      { ip: req.ip, userAgent: req.headers?.['user-agent'] },
    );
  }

  @Post('verify')
  @ApiOperation({ summary: 'Verify entity signature - التحقق من توقيع كيان' })
  verify(
    @Body()
    body: {
      entityType: string;
      entityId: string;
      data: Record<string, unknown>;
    },
  ) {
    return this.service.verifyEntity(body.entityType, body.entityId, body.data);
  }

  @Get(':entityType/:entityId/history')
  @ApiOperation({ summary: 'Get signature history - تاريخ التوقيعات' })
  getHistory(
    @Param('entityType') entityType: string,
    @Param('entityId') entityId: string,
  ) {
    return this.service.getSignatureHistory(entityType, entityId);
  }

  @Post(':id/invalidate')
  @ApiOperation({ summary: 'Invalidate signature - إبطال توقيع' })
  invalidate(
    @Param('id') id: string,
    @Body() body: { reason: string },
    @Request() req: any,
  ) {
    return this.service.invalidateSignature(id, body.reason, req.user?.id || 'system');
  }
}

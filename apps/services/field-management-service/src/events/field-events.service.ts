import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { connect, NatsConnection, StringCodec } from 'nats';

@Injectable()
export class FieldEventsService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(FieldEventsService.name);
  private nc: NatsConnection | null = null;
  private sc = StringCodec();

  async onModuleInit() {
    const natsUrl = process.env.NATS_URL || 'nats://nats:4222';
    try {
      this.nc = await connect({ servers: natsUrl });
      this.logger.log('Connected to NATS');
    } catch (e) {
      this.logger.warn(`NATS connection failed: ${e}. Running in degraded mode.`);
    }
  }

  async onModuleDestroy() {
    if (this.nc) {
      try {
        await this.nc.drain();
        this.logger.log('NATS connection drained and closed');
      } catch (e) {
        this.logger.warn(`NATS close failed: ${e}`);
      }
    }
  }

  isConnected(): boolean {
    return this.nc !== null && !this.nc.isClosed();
  }

  async publishFieldCreated(tenantId: string, fieldId: string, data: Record<string, unknown>) {
    await this.publish('sahool.field.created', { tenantId, fieldId, ...data });
  }

  async publishFieldUpdated(tenantId: string, fieldId: string, data: Record<string, unknown>) {
    await this.publish('sahool.field.updated', { tenantId, fieldId, ...data });
  }

  async publishFieldDeleted(tenantId: string, fieldId: string) {
    await this.publish('sahool.field.deleted', { tenantId, fieldId, deletedAt: new Date().toISOString() });
  }

  async publishBoundaryChanged(tenantId: string, fieldId: string, data: Record<string, unknown>) {
    await this.publish('sahool.field.boundary.changed', { tenantId, fieldId, ...data });
  }

  // ── Crop season events ──────────────────────────────────────────────────

  async publishCropSeasonStarted(
    tenantId: string,
    fieldId: string,
    data: Record<string, unknown>,
  ) {
    await this.publish('sahool.field.crop_season.started', {
      tenantId,
      fieldId,
      ...data,
    });
  }

  async publishCropSeasonUpdated(
    tenantId: string,
    fieldId: string,
    data: Record<string, unknown>,
  ) {
    await this.publish('sahool.field.crop_season.updated', {
      tenantId,
      fieldId,
      ...data,
    });
  }

  async publishCropSeasonEnded(
    tenantId: string,
    fieldId: string,
    data: Record<string, unknown>,
  ) {
    await this.publish('sahool.field.crop_season.ended', {
      tenantId,
      fieldId,
      ...data,
    });
  }

  async publishCropSeasonDeleted(
    tenantId: string,
    fieldId: string,
    data: Record<string, unknown>,
  ) {
    await this.publish('sahool.field.crop_season.deleted', {
      tenantId,
      fieldId,
      ...data,
    });
  }

  // ── Field operation events ──────────────────────────────────────────────

  async publishFieldOperationRecorded(
    tenantId: string,
    fieldId: string,
    data: Record<string, unknown>,
  ) {
    await this.publish('sahool.field.operation.recorded', {
      tenantId,
      fieldId,
      ...data,
    });
  }

  async publishFieldOperationUpdated(
    tenantId: string,
    fieldId: string,
    data: Record<string, unknown>,
  ) {
    await this.publish('sahool.field.operation.updated', {
      tenantId,
      fieldId,
      ...data,
    });
  }

  async publishFieldOperationDeleted(
    tenantId: string,
    fieldId: string,
    data: Record<string, unknown>,
  ) {
    await this.publish('sahool.field.operation.deleted', {
      tenantId,
      fieldId,
      ...data,
    });
  }

  private async publish(subject: string, payload: Record<string, unknown>) {
    if (!this.nc || this.nc.isClosed()) {
      this.logger.warn(`NATS unavailable, skipping ${subject}`);
      return;
    }
    try {
      const data = JSON.stringify({ ...payload, timestamp: new Date().toISOString() });
      this.nc.publish(subject, this.sc.encode(data));
      this.logger.debug(`Published ${subject}`);
    } catch (e) {
      this.logger.error(`Failed to publish ${subject}: ${e}`);
    }
  }

  /**
   * Raw publish hook used by the OutboxPublisher worker. Unlike the
   * private `publish()` above, this one THROWS on NATS disconnection
   * so the outbox worker can increment retry_count and reschedule —
   * silently dropping events would defeat the whole point of the
   * transactional outbox pattern.
   */
  async publishRaw(subject: string, envelope: Record<string, unknown>): Promise<void> {
    if (!this.nc || this.nc.isClosed()) {
      throw new Error(`NATS unavailable while publishing ${subject}`);
    }
    const data = JSON.stringify(envelope);
    this.nc.publish(subject, this.sc.encode(data));
    this.logger.debug(`Published ${subject} via outbox`);
  }
}

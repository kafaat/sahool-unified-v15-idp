/**
 * OutboxService Unit Tests
 * اختبارات وحدة خدمة Outbox
 */

import { Test, TestingModule } from "@nestjs/testing";
import { OutboxService } from "../outbox.service";

describe("OutboxService", () => {
  let service: OutboxService;
  const txClient = {
    outboxEvent: {
      create: jest.fn(),
      update: jest.fn(),
    },
  };

  beforeEach(async () => {
    jest.clearAllMocks();
    const module: TestingModule = await Test.createTestingModule({
      providers: [OutboxService],
    }).compile();
    service = module.get(OutboxService);
  });

  it("writes a canonical envelope into the outbox table", async () => {
    await service.writeInTransaction(txClient as any, {
      eventType: "sahool.field.crop_season.started",
      tenantId: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      aggregateType: "CropSeason",
      aggregateId: "11111111-2222-3333-4444-555555555555",
      payload: { cropType: "wheat", sowingDate: "2026-01-10" },
    });

    expect(txClient.outboxEvent.create).toHaveBeenCalled();
    const { data } = txClient.outboxEvent.create.mock.calls[0][0];
    expect(data.eventType).toBe("sahool.field.crop_season.started");
    expect(data.published).toBe(false);
    expect(data.schemaRef).toContain("sahool.field.crop_season.started");

    const envelope = JSON.parse(data.payloadJson);
    expect(envelope.event_type).toBe("sahool.field.crop_season.started");
    expect(envelope.payload.cropType).toBe("wheat");
    expect(envelope.tenant_id).toBe("f47ac10b-58cc-4372-a567-0e02b2c3d479");
    expect(envelope.correlation_id).toMatch(/^[0-9a-f-]{36}$/);
  });

  it("generates a correlation id when none is provided", async () => {
    await service.writeInTransaction(txClient as any, {
      eventType: "sahool.field.operation.recorded",
      tenantId: "11111111-2222-3333-4444-555555555555",
      aggregateType: "FieldOperation",
      aggregateId: "99999999-8888-7777-6666-555555555555",
      payload: {},
    });

    const { data } = txClient.outboxEvent.create.mock.calls[0][0];
    expect(data.correlationId).toBeDefined();
    expect(data.correlationId).toMatch(/^[0-9a-f-]{36}$/);
  });

  it("respects an explicit correlation id", async () => {
    const explicitCid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee";
    await service.writeInTransaction(txClient as any, {
      eventType: "sahool.test",
      tenantId: "11111111-2222-3333-4444-555555555555",
      correlationId: explicitCid,
      payload: {},
    });
    const { data } = txClient.outboxEvent.create.mock.calls[0][0];
    expect(data.correlationId).toBe(explicitCid);
  });

  it("markFailed increments retry_count and caches the error", async () => {
    await service.markFailed(txClient as any, "row-id", "NATS disconnected");
    expect(txClient.outboxEvent.update).toHaveBeenCalledWith({
      where: { id: "row-id" },
      data: expect.objectContaining({
        retryCount: { increment: 1 },
        lastError: "NATS disconnected",
      }),
    });
  });
});

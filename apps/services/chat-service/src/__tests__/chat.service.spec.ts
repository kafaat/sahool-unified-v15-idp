/**
 * Chat Service Unit Tests
 * اختبارات وحدة خدمة المحادثات
 *
 * Tests cover: health endpoints, module initialization, message creation,
 * conversation creation, and participant management.
 */

import { Test, TestingModule } from "@nestjs/testing";
import {
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { ChatService } from "../chat/chat.service";
import { ChatController } from "../chat/chat.controller";
import { HealthController } from "../health/health.controller";
import { PrismaService } from "../prisma/prisma.service";
import { ChatEventsService } from "../events/chat-events.service";
import { CreateConversationDto } from "../chat/dto/create-conversation.dto";
import { SendMessageDto, MessageType } from "../chat/dto/send-message.dto";

// ═══════════════════════════════════════════════════════════════════════════
// Shared Test Constants
// ═══════════════════════════════════════════════════════════════════════════

const TENANT_ID = "tenant-001";
const USER_ID_BUYER = "user-buyer-123";
const USER_ID_SELLER = "user-seller-456";
const CONVERSATION_ID = "conv-789";
const MESSAGE_ID = "msg-001";
const PRODUCT_ID = "prod-123";

const mockConversation = {
  id: CONVERSATION_ID,
  tenantId: TENANT_ID,
  participantIds: [USER_ID_BUYER, USER_ID_SELLER],
  productId: PRODUCT_ID,
  orderId: null,
  lastMessage: "Hello",
  lastMessageAt: new Date("2026-03-01T10:00:00Z"),
  isActive: true,
  createdAt: new Date("2026-03-01T09:00:00Z"),
  updatedAt: new Date("2026-03-01T10:00:00Z"),
  messages: [],
  participants: [
    {
      id: "part-1",
      tenantId: TENANT_ID,
      conversationId: CONVERSATION_ID,
      userId: USER_ID_BUYER,
      role: "BUYER",
      lastReadAt: new Date("2026-03-01T10:00:00Z"),
      unreadCount: 0,
      isOnline: true,
      lastSeenAt: new Date("2026-03-01T10:00:00Z"),
      isTyping: false,
      joinedAt: new Date("2026-03-01T09:00:00Z"),
    },
    {
      id: "part-2",
      tenantId: TENANT_ID,
      conversationId: CONVERSATION_ID,
      userId: USER_ID_SELLER,
      role: "SELLER",
      lastReadAt: new Date("2026-03-01T09:30:00Z"),
      unreadCount: 2,
      isOnline: false,
      lastSeenAt: new Date("2026-03-01T09:30:00Z"),
      isTyping: false,
      joinedAt: new Date("2026-03-01T09:00:00Z"),
    },
  ],
};

const mockMessage = {
  id: MESSAGE_ID,
  tenantId: TENANT_ID,
  conversationId: CONVERSATION_ID,
  senderId: USER_ID_BUYER,
  content: "I am interested in buying wheat",
  messageType: "TEXT",
  attachmentUrl: null,
  offerAmount: null,
  offerCurrency: "YER",
  isRead: false,
  readAt: null,
  createdAt: new Date("2026-03-01T10:05:00Z"),
  updatedAt: new Date("2026-03-01T10:05:00Z"),
};

// ═══════════════════════════════════════════════════════════════════════════
// Mock PrismaService Factory
// ═══════════════════════════════════════════════════════════════════════════

function createMockPrisma() {
  return {
    conversation: {
      findFirst: jest.fn(),
      create: jest.fn(),
      findMany: jest.fn(),
      update: jest.fn(),
    },
    message: {
      create: jest.fn(),
      findFirst: jest.fn(),
      findMany: jest.fn(),
      count: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
    },
    participant: {
      findMany: jest.fn(),
      create: jest.fn(),
      updateMany: jest.fn(),
      deleteMany: jest.fn(),
    },
    // For service methods that call `this.prisma.$transaction(async (tx) => ...)`
    // run the callback inline with the mock itself — lets specs assert that
    // participant.create + conversation.update were both invoked.
    $transaction: jest.fn(async (cb: any) => cb(mockPrismaForTx)),
    $queryRaw: jest.fn(),
  } as any;
}

// Lazy reference so the $transaction mock above can see the same object it
// lives on — set inside beforeEach via `mockPrismaForTx = mockPrisma` assignment.
let mockPrismaForTx: any;

// ═══════════════════════════════════════════════════════════════════════════
// Health Endpoint Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Health Endpoints", () => {
  describe("ChatController /chat/health", () => {
    let controller: ChatController;

    beforeEach(async () => {
      const mockPrisma = createMockPrisma();
      const module: TestingModule = await Test.createTestingModule({
        controllers: [ChatController],
        providers: [
          ChatService,
          { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
        ],
      }).compile();

      controller = module.get<ChatController>(ChatController);
    });

    it("should return health status with service name and timestamp", () => {
      const result = controller.healthCheck();

      expect(result).toHaveProperty("status", "ok");
      expect(result).toHaveProperty("service", "chat-service");
      expect(result).toHaveProperty("timestamp");
      expect(typeof result.timestamp).toBe("string");
      // Verify ISO format
      expect(new Date(result.timestamp).toISOString()).toBe(result.timestamp);
    });
  });

  describe("HealthController", () => {
    let controller: HealthController;
    let mockPrisma: ReturnType<typeof createMockPrisma>;

    beforeEach(async () => {
      mockPrisma = createMockPrisma();
      const module: TestingModule = await Test.createTestingModule({
        controllers: [HealthController],
        providers: [
          { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
        ],
      }).compile();

      controller = module.get<HealthController>(HealthController);
    });

    it("should return healthy status with database check on /health", async () => {
      mockPrisma.$queryRaw.mockResolvedValue([{ "?column?": 1 }]);

      const result = await controller.health();

      expect(result.status).toBe("healthy");
      expect(result.service).toBe("chat-service");
      expect(result.version).toBe("16.0.0");
      expect(result.dependencies.database).toBe("connected");
      expect(result).toHaveProperty("uptime");
    });

    it("should report database disconnected when query fails on /health", async () => {
      mockPrisma.$queryRaw.mockRejectedValue(new Error("Connection refused"));

      const result = await controller.health();

      expect(result.status).toBe("healthy");
      expect(result.dependencies.database).toBe("disconnected");
    });

    it("should return ok on /healthz without database check", () => {
      const result = controller.healthz();

      expect(result.status).toBe("ok");
      expect(result.service).toBe("chat-service");
      expect(result).toHaveProperty("uptime");
    });

    it("should report readiness based on database connectivity on /readyz", async () => {
      mockPrisma.$queryRaw.mockResolvedValue([{ "?column?": 1 }]);

      const result = await controller.readyz();

      expect(result.status).toBe("ready");
      expect(result.database).toBe(true);
    });

    it("should report not_ready when database is down on /readyz", async () => {
      mockPrisma.$queryRaw.mockRejectedValue(new Error("Connection refused"));

      const result = await controller.readyz();

      expect(result.status).toBe("not_ready");
      expect(result.database).toBe(false);
    });

    it("should return alive on /livez", () => {
      const result = controller.livenessCheck();

      expect(result.status).toBe("alive");
      expect(result.service).toBe("chat-service");
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Module Initialization Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Module Initialization", () => {
  it("should compile the ChatService with PrismaService dependency", async () => {
    const mockPrisma = createMockPrisma();
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ChatService,
        { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
      ],
    }).compile();

    const service = module.get<ChatService>(ChatService);
    const prisma = module.get<PrismaService>(PrismaService);

    expect(service).toBeDefined();
    expect(service).toBeInstanceOf(ChatService);
    expect(prisma).toBeDefined();
  });

  it("should compile ChatController with ChatService dependency", async () => {
    const mockPrisma = createMockPrisma();
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ChatController],
      providers: [
        ChatService,
        { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
      ],
    }).compile();

    const controller = module.get<ChatController>(ChatController);
    expect(controller).toBeDefined();
    expect(controller).toBeInstanceOf(ChatController);
  });

  it("should compile HealthController with PrismaService dependency", async () => {
    const mockPrisma = createMockPrisma();
    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
      ],
    }).compile();

    const controller = module.get<HealthController>(HealthController);
    expect(controller).toBeDefined();
    expect(controller).toBeInstanceOf(HealthController);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Conversation Creation Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("ChatService - Conversation Creation", () => {
  let service: ChatService;
  let mockPrisma: ReturnType<typeof createMockPrisma>;

  beforeEach(async () => {
    mockPrisma = createMockPrisma();
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ChatService,
        { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
      ],
    }).compile();

    service = module.get<ChatService>(ChatService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should return existing conversation when one already exists for the participants", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      productId: PRODUCT_ID,
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

    const result = await service.createConversation(dto, TENANT_ID);

    expect(result).toEqual(mockConversation);
    expect(mockPrisma.conversation.findFirst).toHaveBeenCalledWith({
      where: {
        tenantId: TENANT_ID,
        participantIds: { hasEvery: dto.participantIds },
        productId: PRODUCT_ID,
        orderId: null,
      },
      include: {
        participants: true,
        messages: { orderBy: { createdAt: "desc" }, take: 1 },
      },
    });
    expect(mockPrisma.conversation.create).not.toHaveBeenCalled();
  });

  it("should create a new conversation when none exists", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      productId: PRODUCT_ID,
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(null);
    mockPrisma.conversation.create.mockResolvedValue(mockConversation);

    const result = await service.createConversation(dto, TENANT_ID);

    expect(result).toEqual(mockConversation);
    expect(mockPrisma.conversation.create).toHaveBeenCalledWith({
      data: {
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER, USER_ID_SELLER],
        productId: PRODUCT_ID,
        orderId: undefined,
        participants: {
          create: [
            { tenantId: TENANT_ID, userId: USER_ID_BUYER, role: "BUYER" },
            { tenantId: TENANT_ID, userId: USER_ID_SELLER, role: "SELLER" },
          ],
        },
      },
      include: {
        participants: true,
        messages: true,
      },
    });
  });

  it("should assign the first participant as BUYER and second as SELLER", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(null);
    mockPrisma.conversation.create.mockResolvedValue(mockConversation);

    await service.createConversation(dto, TENANT_ID);

    const createCall = mockPrisma.conversation.create.mock.calls[0][0];
    const participantsCreate = createCall.data.participants.create;
    expect(participantsCreate[0].role).toBe("BUYER");
    expect(participantsCreate[0].userId).toBe(USER_ID_BUYER);
    expect(participantsCreate[1].role).toBe("SELLER");
    expect(participantsCreate[1].userId).toBe(USER_ID_SELLER);
  });

  it("should create a conversation with orderId", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      orderId: "order-555",
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(null);
    mockPrisma.conversation.create.mockResolvedValue({
      ...mockConversation,
      orderId: "order-555",
    });

    const result = await service.createConversation(dto, TENANT_ID);

    expect(result.orderId).toBe("order-555");
    const createCall = mockPrisma.conversation.create.mock.calls[0][0];
    expect(createCall.data.orderId).toBe("order-555");
  });

  it("should handle conversation creation without productId or orderId", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(null);
    mockPrisma.conversation.create.mockResolvedValue({
      ...mockConversation,
      productId: null,
      orderId: null,
    });

    const result = await service.createConversation(dto, TENANT_ID);

    expect(result.productId).toBeNull();
    expect(result.orderId).toBeNull();
    // Verify findFirst used null for optional fields
    const findCall = mockPrisma.conversation.findFirst.mock.calls[0][0];
    expect(findCall.where.productId).toBeNull();
    expect(findCall.where.orderId).toBeNull();
  });

  it("should propagate database errors during conversation creation", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
    };
    mockPrisma.conversation.findFirst.mockRejectedValue(
      new Error("Database connection lost"),
    );

    await expect(service.createConversation(dto, TENANT_ID)).rejects.toThrow(
      "Database connection lost",
    );
  });

  // ─────────────────────────────────────────────────────────────────────
  // Regression tests for scope wiring — closes Copilot review #4 on
  // PR #1664 which noted that createConversation never persisted
  // scopeType/scopeId, so getConversationByScope would always 404.
  // ─────────────────────────────────────────────────────────────────────

  it("persists scopeType/scopeId when creating a field-chat style conversation", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      scopeType: "field",
      scopeId: "fld_abc123",
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(null);
    mockPrisma.conversation.create.mockImplementation(async ({ data }: any) => ({
      ...mockConversation,
      ...data,
    }));

    const result = await service.createConversation(dto, TENANT_ID);

    // Scope is forwarded to the create call and ends up on the row.
    const createCall = mockPrisma.conversation.create.mock.calls[0][0];
    expect(createCall.data.scopeType).toBe("field");
    expect(createCall.data.scopeId).toBe("fld_abc123");
    expect(result.scopeType).toBe("field");
    expect(result.scopeId).toBe("fld_abc123");
  });

  it("dedups on (scopeType, scopeId) when both are provided", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      scopeType: "task",
      scopeId: "task_42",
    };
    mockPrisma.conversation.findFirst.mockResolvedValue({
      ...mockConversation,
      scopeType: "task",
      scopeId: "task_42",
    });

    const result = await service.createConversation(dto, TENANT_ID);

    // findFirst WHERE used the scope key, not the participant/product key.
    const where = mockPrisma.conversation.findFirst.mock.calls[0][0].where;
    expect(where).toEqual({
      tenantId: TENANT_ID,
      scopeType: "task",
      scopeId: "task_42",
    });
    // create was never called — existing row returned.
    expect(mockPrisma.conversation.create).not.toHaveBeenCalled();
    expect(result.scopeType).toBe("task");
  });

  it("still dedups on (productId, orderId, participantIds) when no scope is given", async () => {
    const dto: CreateConversationDto = {
      participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      productId: PRODUCT_ID,
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(null);
    mockPrisma.conversation.create.mockResolvedValue(mockConversation);

    await service.createConversation(dto, TENANT_ID);

    const where = mockPrisma.conversation.findFirst.mock.calls[0][0].where;
    // No scope filter — participants/product/order path is preserved.
    expect(where).not.toHaveProperty("scopeType");
    expect(where.productId).toBe(PRODUCT_ID);
    expect(where.orderId).toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Message Creation & Validation Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("ChatService - Message Creation & Validation", () => {
  let service: ChatService;
  let mockPrisma: ReturnType<typeof createMockPrisma>;

  beforeEach(async () => {
    mockPrisma = createMockPrisma();
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ChatService,
        { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
      ],
    }).compile();

    service = module.get<ChatService>(ChatService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should send a text message successfully within a transaction", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: USER_ID_BUYER,
      content: "Hello, I want to buy wheat",
      messageType: MessageType.TEXT,
    };

    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

    const createdMessage = { ...mockMessage, content: dto.content };
    mockPrisma.$transaction.mockImplementation(async (callback: any) => {
      return callback({
        message: { create: jest.fn().mockResolvedValue(createdMessage) },
        conversation: { updateMany: jest.fn().mockResolvedValue({ count: 1 }) },
        participant: { updateMany: jest.fn().mockResolvedValue({ count: 1 }) },
      });
    });

    const result = await service.sendMessage(dto, TENANT_ID);

    expect(result).toEqual(createdMessage);
    expect(mockPrisma.conversation.findFirst).toHaveBeenCalledWith({
      where: { id: CONVERSATION_ID, tenantId: TENANT_ID },
    });
  });

  it("should throw NotFoundException when conversation does not exist", async () => {
    const dto: SendMessageDto = {
      conversationId: "non-existent-conv",
      senderId: USER_ID_BUYER,
      content: "Hello",
      messageType: MessageType.TEXT,
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(null);

    await expect(service.sendMessage(dto, TENANT_ID)).rejects.toThrow(
      NotFoundException,
    );
  });

  it("should throw BadRequestException when sender is not a participant", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: "user-outsider-999",
      content: "I should not be able to send this",
      messageType: MessageType.TEXT,
    };
    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

    await expect(service.sendMessage(dto, TENANT_ID)).rejects.toThrow(
      BadRequestException,
    );
  });

  it("should send an OFFER type message with amount and currency", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: USER_ID_BUYER,
      content: "I offer 5000 YER",
      messageType: MessageType.OFFER,
      offerAmount: 5000.0,
      offerCurrency: "YER",
    };

    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

    const offerMessage = {
      ...mockMessage,
      content: dto.content,
      messageType: "OFFER",
      offerAmount: 5000.0,
      offerCurrency: "YER",
    };
    const mockCreate = jest.fn().mockResolvedValue(offerMessage);
    mockPrisma.$transaction.mockImplementation(async (callback: any) => {
      return callback({
        message: { create: mockCreate },
        conversation: { updateMany: jest.fn().mockResolvedValue({ count: 1 }) },
        participant: { updateMany: jest.fn() },
      });
    });

    const result = await service.sendMessage(dto, TENANT_ID);

    expect(result.offerAmount).toBe(5000.0);
    expect(result.offerCurrency).toBe("YER");
    // Verify the create call included offer data
    const createArg = mockCreate.mock.calls[0][0];
    expect(createArg.data.offerAmount).toBe(5000.0);
    expect(createArg.data.offerCurrency).toBe("YER");
    expect(createArg.data.messageType).toBe("OFFER");
  });

  it("should default messageType to TEXT and offerCurrency to YER when not specified", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: USER_ID_BUYER,
      content: "Simple message",
    };

    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

    const mockCreate = jest.fn().mockResolvedValue(mockMessage);
    mockPrisma.$transaction.mockImplementation(async (callback: any) => {
      return callback({
        message: { create: mockCreate },
        conversation: { updateMany: jest.fn().mockResolvedValue({ count: 1 }) },
        participant: { updateMany: jest.fn() },
      });
    });

    await service.sendMessage(dto, TENANT_ID);

    const createArg = mockCreate.mock.calls[0][0];
    expect(createArg.data.messageType).toBe("TEXT");
    expect(createArg.data.offerCurrency).toBe("YER");
  });

  it("should update conversation lastMessage and lastMessageAt within the transaction", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: USER_ID_BUYER,
      content: "Updated last message",
      messageType: MessageType.TEXT,
    };

    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

    const mockUpdateMany = jest.fn().mockResolvedValue({ count: 1 });
    mockPrisma.$transaction.mockImplementation(async (callback: any) => {
      return callback({
        message: { create: jest.fn().mockResolvedValue(mockMessage) },
        conversation: { updateMany: mockUpdateMany },
        participant: { updateMany: jest.fn() },
      });
    });

    await service.sendMessage(dto, TENANT_ID);

    expect(mockUpdateMany).toHaveBeenCalledWith({
      where: { id: CONVERSATION_ID, tenantId: TENANT_ID },
      data: {
        lastMessage: "Updated last message",
        lastMessageAt: expect.any(Date),
        updatedAt: expect.any(Date),
      },
    });
  });

  it("should increment unread count for participants other than the sender", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: USER_ID_BUYER,
      content: "New message",
      messageType: MessageType.TEXT,
    };

    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

    const mockUpdateMany = jest.fn().mockResolvedValue({ count: 1 });
    mockPrisma.$transaction.mockImplementation(async (callback: any) => {
      return callback({
        message: { create: jest.fn().mockResolvedValue(mockMessage) },
        conversation: { updateMany: jest.fn().mockResolvedValue({ count: 1 }) },
        participant: { updateMany: mockUpdateMany },
      });
    });

    await service.sendMessage(dto, TENANT_ID);

    expect(mockUpdateMany).toHaveBeenCalledWith({
      where: {
        tenantId: TENANT_ID,
        conversationId: CONVERSATION_ID,
        userId: { not: USER_ID_BUYER },
      },
      data: {
        unreadCount: { increment: 1 },
      },
    });
  });

  it("should wrap unexpected transaction errors as BadRequestException", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: USER_ID_BUYER,
      content: "This will fail",
      messageType: MessageType.TEXT,
    };

    mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);
    mockPrisma.$transaction.mockRejectedValue(new Error("Deadlock detected"));

    await expect(service.sendMessage(dto, TENANT_ID)).rejects.toThrow(
      BadRequestException,
    );
  });

  it("should re-throw NotFoundException and BadRequestException without wrapping", async () => {
    const dto: SendMessageDto = {
      conversationId: CONVERSATION_ID,
      senderId: USER_ID_BUYER,
      content: "Test",
      messageType: MessageType.TEXT,
    };

    // NotFoundException case: conversation not found
    mockPrisma.conversation.findFirst.mockResolvedValue(null);

    await expect(service.sendMessage(dto, TENANT_ID)).rejects.toThrow(
      NotFoundException,
    );
  });

  it("should retrieve paginated messages in chronological order", async () => {
    const messagesDesc = [
      { ...mockMessage, id: "msg-2", createdAt: new Date("2026-03-01T11:00:00Z") },
      { ...mockMessage, id: "msg-1", createdAt: new Date("2026-03-01T10:00:00Z") },
    ];
    mockPrisma.message.findMany.mockResolvedValue(messagesDesc);
    mockPrisma.message.count.mockResolvedValue(2);

    const result = await service.getMessages(CONVERSATION_ID, 1, 50, TENANT_ID);

    expect(result.messages).toHaveLength(2);
    // Should be reversed to chronological order
    expect(result.messages[0].id).toBe("msg-1");
    expect(result.messages[1].id).toBe("msg-2");
    expect(result.total).toBe(2);
    expect(result.page).toBe(1);
    expect(result.limit).toBe(50);
    expect(result.totalPages).toBe(1);
  });

  it("should calculate pagination offset correctly for page 3", async () => {
    mockPrisma.message.findMany.mockResolvedValue([]);
    mockPrisma.message.count.mockResolvedValue(250);

    const result = await service.getMessages(CONVERSATION_ID, 3, 50, TENANT_ID);

    expect(mockPrisma.message.findMany).toHaveBeenCalledWith(
      expect.objectContaining({
        where: { conversationId: CONVERSATION_ID, tenantId: TENANT_ID },
        skip: 100,
        take: 50,
      }),
    );
    expect(result.totalPages).toBe(5);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Participant Management Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("ChatService - Participant Management", () => {
  let service: ChatService;
  let mockPrisma: ReturnType<typeof createMockPrisma>;

  beforeEach(async () => {
    mockPrisma = createMockPrisma();
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ChatService,
        { provide: PrismaService, useValue: mockPrisma },
          { provide: ChatEventsService, useValue: { publishMessageSent: jest.fn(), publishMessageRead: jest.fn(), isConnected: jest.fn().mockReturnValue(false) } },
      ],
    }).compile();

    service = module.get<ChatService>(ChatService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("getUserConversations", () => {
    it("should return conversations with unread counts for a user", async () => {
      const conversationsFromDb = [
        {
          ...mockConversation,
          _count: { messages: 3 },
        },
        {
          ...mockConversation,
          id: "conv-002",
          _count: { messages: 0 },
        },
      ];
      mockPrisma.conversation.findMany.mockResolvedValue(conversationsFromDb);

      const result = await service.getUserConversations(USER_ID_BUYER, TENANT_ID);

      expect(result).toHaveLength(2);
      expect(result[0].unreadCount).toBe(3);
      expect(result[1].unreadCount).toBe(0);
      // Should not contain the raw _count property
      expect(result[0]).not.toHaveProperty("_count");
    });

    it("should filter by tenant and only return active conversations", async () => {
      mockPrisma.conversation.findMany.mockResolvedValue([]);

      await service.getUserConversations(USER_ID_BUYER, TENANT_ID);

      expect(mockPrisma.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: {
            tenantId: TENANT_ID,
            participantIds: { has: USER_ID_BUYER },
            isActive: true,
          },
          orderBy: { updatedAt: "desc" },
        }),
      );
    });

    it("should return empty array when user has no conversations", async () => {
      mockPrisma.conversation.findMany.mockResolvedValue([]);

      const result = await service.getUserConversations(USER_ID_BUYER, TENANT_ID);

      expect(result).toEqual([]);
    });

    it("should include lastReadAt from participant data", async () => {
      const convWithParticipant = {
        ...mockConversation,
        _count: { messages: 1 },
      };
      mockPrisma.conversation.findMany.mockResolvedValue([convWithParticipant]);

      const result = await service.getUserConversations(USER_ID_BUYER, TENANT_ID);

      expect(result[0]).toHaveProperty("lastReadAt");
    });
  });

  describe("getConversationById", () => {
    it("should return conversation with participants for a valid ID", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(CONVERSATION_ID, TENANT_ID);

      expect(result).toEqual(mockConversation);
      expect(mockPrisma.conversation.findFirst).toHaveBeenCalledWith({
        where: { id: CONVERSATION_ID, tenantId: TENANT_ID },
        include: { participants: true },
      });
    });

    it("should throw NotFoundException for a non-existent conversation", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue(null);

      await expect(
        service.getConversationById("non-existent", TENANT_ID),
      ).rejects.toThrow(NotFoundException);
      await expect(
        service.getConversationById("non-existent", TENANT_ID),
      ).rejects.toThrow("Conversation not found");
    });

    it("should scope the lookup to the tenant", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue(null);

      try {
        await service.getConversationById(CONVERSATION_ID, "other-tenant");
      } catch {}

      expect(mockPrisma.conversation.findFirst).toHaveBeenCalledWith({
        where: { id: CONVERSATION_ID, tenantId: "other-tenant" },
        include: { participants: true },
      });
    });
  });

  describe("markMessageAsRead", () => {
    it("should mark a message as read when the reader is not the sender", async () => {
      const msgWithConversation = {
        ...mockMessage,
        senderId: USER_ID_BUYER,
        conversation: mockConversation,
      };
      mockPrisma.message.findFirst.mockResolvedValue(msgWithConversation);
      mockPrisma.message.updateMany.mockResolvedValue({ count: 1 });
      mockPrisma.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.markMessageAsRead(MESSAGE_ID, USER_ID_SELLER, TENANT_ID);

      expect(result).toBeDefined();
      expect(mockPrisma.message.updateMany).toHaveBeenCalledWith({
        where: { id: MESSAGE_ID, tenantId: TENANT_ID },
        data: {
          isRead: true,
          readAt: expect.any(Date),
        },
      });
      expect(mockPrisma.participant.updateMany).toHaveBeenCalledWith({
        where: {
          tenantId: TENANT_ID,
          conversationId: CONVERSATION_ID,
          userId: USER_ID_SELLER,
        },
        data: {
          lastReadAt: expect.any(Date),
          unreadCount: 0,
        },
      });
    });

    it("should not update read status when the reader is the sender", async () => {
      const ownMsg = {
        ...mockMessage,
        senderId: USER_ID_BUYER,
        conversation: mockConversation,
      };
      mockPrisma.message.findFirst.mockResolvedValue(ownMsg);

      await service.markMessageAsRead(MESSAGE_ID, USER_ID_BUYER, TENANT_ID);

      expect(mockPrisma.message.updateMany).not.toHaveBeenCalled();
      expect(mockPrisma.participant.updateMany).not.toHaveBeenCalled();
    });

    it("should throw NotFoundException when message does not exist", async () => {
      mockPrisma.message.findFirst.mockResolvedValue(null);

      await expect(
        service.markMessageAsRead("bad-id", USER_ID_BUYER, TENANT_ID),
      ).rejects.toThrow(NotFoundException);
    });

    it("should scope the message lookup to the tenant", async () => {
      mockPrisma.message.findFirst.mockResolvedValue(null);

      try {
        await service.markMessageAsRead(MESSAGE_ID, USER_ID_BUYER, TENANT_ID);
      } catch {}

      expect(mockPrisma.message.findFirst).toHaveBeenCalledWith({
        where: { id: MESSAGE_ID, tenantId: TENANT_ID },
        include: { conversation: true },
      });
    });
  });

  describe("markConversationAsRead", () => {
    it("should mark all unread messages and reset participant unread count", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue(mockConversation);
      mockPrisma.message.updateMany.mockResolvedValue({ count: 5 });
      mockPrisma.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.markConversationAsRead(
        CONVERSATION_ID,
        USER_ID_SELLER,
        TENANT_ID,
      );

      expect(result).toEqual({ success: true, conversationId: CONVERSATION_ID });

      expect(mockPrisma.message.updateMany).toHaveBeenCalledWith({
        where: {
          tenantId: TENANT_ID,
          conversationId: CONVERSATION_ID,
          senderId: { not: USER_ID_SELLER },
          isRead: false,
        },
        data: {
          isRead: true,
          readAt: expect.any(Date),
        },
      });

      expect(mockPrisma.participant.updateMany).toHaveBeenCalledWith({
        where: {
          tenantId: TENANT_ID,
          conversationId: CONVERSATION_ID,
          userId: USER_ID_SELLER,
        },
        data: {
          lastReadAt: expect.any(Date),
          unreadCount: 0,
        },
      });
    });

    it("should throw NotFoundException if conversation does not exist", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue(null);

      await expect(
        service.markConversationAsRead("bad-conv", USER_ID_BUYER, TENANT_ID),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("updateTypingIndicator", () => {
    it("should set typing status to true for a participant", async () => {
      mockPrisma.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.updateTypingIndicator(
        CONVERSATION_ID,
        USER_ID_BUYER,
        true,
        TENANT_ID,
      );

      expect(result).toEqual({
        conversationId: CONVERSATION_ID,
        userId: USER_ID_BUYER,
        isTyping: true,
      });
      expect(mockPrisma.participant.updateMany).toHaveBeenCalledWith({
        where: {
          tenantId: TENANT_ID,
          conversationId: CONVERSATION_ID,
          userId: USER_ID_BUYER,
        },
        data: { isTyping: true },
      });
    });

    it("should set typing status to false for a participant", async () => {
      mockPrisma.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.updateTypingIndicator(
        CONVERSATION_ID,
        USER_ID_BUYER,
        false,
        TENANT_ID,
      );

      expect(result.isTyping).toBe(false);
    });
  });

  describe("updateOnlineStatus", () => {
    it("should mark user as online and update lastSeenAt", async () => {
      mockPrisma.participant.updateMany.mockResolvedValue({ count: 2 });
      const before = new Date();

      const result = await service.updateOnlineStatus(USER_ID_BUYER, true, TENANT_ID);

      expect(result).toEqual({ userId: USER_ID_BUYER, isOnline: true });
      const callArg = mockPrisma.participant.updateMany.mock.calls[0][0];
      expect(callArg.where).toEqual({ userId: USER_ID_BUYER, tenantId: TENANT_ID });
      expect(callArg.data.isOnline).toBe(true);
      expect(callArg.data.lastSeenAt).toBeInstanceOf(Date);
      expect(callArg.data.lastSeenAt.getTime()).toBeGreaterThanOrEqual(before.getTime());
    });

    it("should mark user as offline", async () => {
      mockPrisma.participant.updateMany.mockResolvedValue({ count: 2 });

      const result = await service.updateOnlineStatus(USER_ID_BUYER, false, TENANT_ID);

      expect(result.isOnline).toBe(false);
    });

    it("should work with tenantId parameter", async () => {
      mockPrisma.participant.updateMany.mockResolvedValue({ count: 3 });

      const result = await service.updateOnlineStatus(USER_ID_BUYER, true, TENANT_ID);

      expect(result).toEqual({ userId: USER_ID_BUYER, isOnline: true });
      const callArg = mockPrisma.participant.updateMany.mock.calls[0][0];
      expect(callArg.where).toEqual({ userId: USER_ID_BUYER, tenantId: TENANT_ID });
    });
  });

  describe("getUnreadCount", () => {
    it("should sum unread counts across all conversations", async () => {
      mockPrisma.participant.findMany.mockResolvedValue([
        { unreadCount: 3 },
        { unreadCount: 7 },
        { unreadCount: 2 },
      ]);

      const result = await service.getUnreadCount(USER_ID_BUYER, TENANT_ID);

      expect(result).toBe(12);
      expect(mockPrisma.participant.findMany).toHaveBeenCalledWith({
        where: { userId: USER_ID_BUYER, tenantId: TENANT_ID },
        select: { unreadCount: true },
        take: 500,
      });
    });

    it("should return zero when all conversations have been read", async () => {
      mockPrisma.participant.findMany.mockResolvedValue([
        { unreadCount: 0 },
        { unreadCount: 0 },
      ]);

      const result = await service.getUnreadCount(USER_ID_BUYER, TENANT_ID);

      expect(result).toBe(0);
    });

    it("should return zero when user has no conversations", async () => {
      mockPrisma.participant.findMany.mockResolvedValue([]);

      const result = await service.getUnreadCount(USER_ID_BUYER, TENANT_ID);

      expect(result).toBe(0);
    });

    it("should work with tenantId parameter", async () => {
      mockPrisma.participant.findMany.mockResolvedValue([{ unreadCount: 5 }]);

      const result = await service.getUnreadCount(USER_ID_BUYER, TENANT_ID);

      expect(result).toBe(5);
      const callArg = mockPrisma.participant.findMany.mock.calls[0][0];
      expect(callArg.where).toEqual({ userId: USER_ID_BUYER, tenantId: TENANT_ID });
    });
  });

  describe("getMessagesCursor - cursor-based pagination", () => {
    it("should return messages without cursor for initial load", async () => {
      const messages = [
        { ...mockMessage, id: "msg-1" },
        { ...mockMessage, id: "msg-2" },
      ];
      mockPrisma.message.findMany.mockResolvedValue(messages);

      const result = await service.getMessagesCursor(CONVERSATION_ID, TENANT_ID, undefined, 50);

      expect(result.messages).toHaveLength(2);
      expect(result.hasMore).toBe(false);
      expect(result.nextCursor).toBeNull();
    });

    it("should indicate hasMore when more messages exist beyond the limit", async () => {
      // Return limit + 1 to indicate there are more
      const messages = Array.from({ length: 11 }, (_, i) => ({
        ...mockMessage,
        id: `msg-${i}`,
      }));
      mockPrisma.message.findMany.mockResolvedValue(messages);

      const result = await service.getMessagesCursor(CONVERSATION_ID, TENANT_ID, undefined, 10);

      expect(result.hasMore).toBe(true);
      expect(result.messages).toHaveLength(10);
      expect(result.nextCursor).toBeDefined();
      expect(result.nextCursor).not.toBeNull();
    });

    it("should use cursor and skip for subsequent pages", async () => {
      mockPrisma.message.findMany.mockResolvedValue([mockMessage]);

      await service.getMessagesCursor(CONVERSATION_ID, TENANT_ID, "cursor-msg-50", 20);

      expect(mockPrisma.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          cursor: { id: "cursor-msg-50" },
          skip: 1,
          take: 21,
        }),
      );
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Ported field-chat capabilities — scope lookup, archive, search,
// participant add/remove. Mocks stand in for Prisma so the tests stay
// pure-unit (no DB connection required).
// ═══════════════════════════════════════════════════════════════════════════

describe("ChatService - Ported Field-Chat Features", () => {
  let service: ChatService;
  let mockPrisma: ReturnType<typeof createMockPrisma>;

  beforeEach(async () => {
    mockPrisma = createMockPrisma();
    mockPrismaForTx = mockPrisma; // $transaction callback reads this

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ChatService,
        { provide: PrismaService, useValue: mockPrisma },
        {
          provide: ChatEventsService,
          useValue: { publishConversationCreated: jest.fn(), publishMessageSent: jest.fn() },
        },
      ],
    }).compile();

    service = module.get<ChatService>(ChatService);
  });

  describe("getConversationByScope", () => {
    it("returns the conversation when (scopeType, scopeId) matches", async () => {
      const expected = { id: "c1", tenantId: TENANT_ID, scopeType: "field", scopeId: "fld_1", participantIds: [USER_ID_BUYER] };
      mockPrisma.conversation.findFirst.mockResolvedValue(expected);

      const result = await service.getConversationByScope("field", "fld_1", TENANT_ID);

      expect(result).toEqual(expected);
      expect(mockPrisma.conversation.findFirst).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { tenantId: TENANT_ID, scopeType: "field", scopeId: "fld_1" },
        }),
      );
    });

    it("throws 404 when no conversation exists for that scope", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue(null);
      await expect(
        service.getConversationByScope("field", "missing", TENANT_ID),
      ).rejects.toThrow(NotFoundException);
    });

    it("rejects missing scopeType/scopeId with 400", async () => {
      await expect(
        service.getConversationByScope("", "x", TENANT_ID),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe("archiveConversation", () => {
    it("sets isActive=false and stamps archivedAt", async () => {
      const now = Date.now();
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER],
        isActive: true,
      });
      mockPrisma.conversation.update.mockImplementation(async ({ data }: any) => ({
        id: CONVERSATION_ID,
        ...data,
      }));

      const result = await service.archiveConversation(
        CONVERSATION_ID,
        USER_ID_BUYER,
        TENANT_ID,
      );

      expect(result.isActive).toBe(false);
      expect(result.archivedAt).toBeInstanceOf(Date);
      // Non-null asserted: the previous expect already checks archivedAt is a
      // Date, which narrows the union but TS structural checks don't follow
      // that across a `.toBeInstanceOf`. `!` keeps strictNullChecks happy.
      expect((result.archivedAt as Date).getTime()).toBeGreaterThanOrEqual(now);
    });

    it("is idempotent: archiving an already-archived conversation is a no-op", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER],
        isActive: false,
      });

      await service.archiveConversation(CONVERSATION_ID, USER_ID_BUYER, TENANT_ID);
      expect(mockPrisma.conversation.update).not.toHaveBeenCalled();
    });

    it("rejects a non-participant", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER],
        isActive: true,
      });
      await expect(
        service.archiveConversation(CONVERSATION_ID, "stranger", TENANT_ID),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe("searchMessages", () => {
    it("does a case-insensitive contains search scoped to tenant", async () => {
      mockPrisma.message.findMany.mockResolvedValue([{ id: "m1", content: "Hello there" }]);

      const result = await service.searchMessages("hello", TENANT_ID);

      expect(result).toHaveLength(1);
      expect(mockPrisma.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            tenantId: TENANT_ID,
            content: { contains: "hello", mode: "insensitive" },
          }),
        }),
      );
    });

    it("narrows search to a single conversation when provided", async () => {
      mockPrisma.message.findMany.mockResolvedValue([]);
      await service.searchMessages("x-word", TENANT_ID, { conversationId: CONVERSATION_ID });
      const call = mockPrisma.message.findMany.mock.calls[0][0];
      expect(call.where.conversationId).toBe(CONVERSATION_ID);
    });

    it("rejects queries shorter than 2 chars", async () => {
      await expect(service.searchMessages(" ", TENANT_ID)).rejects.toThrow(
        BadRequestException,
      );
    });

    it("clamps the limit to [1, 200]", async () => {
      mockPrisma.message.findMany.mockResolvedValue([]);
      await service.searchMessages("hi", TENANT_ID, { limit: 9999 });
      expect(mockPrisma.message.findMany.mock.calls[0][0].take).toBe(200);

      mockPrisma.message.findMany.mockClear();
      await service.searchMessages("hi", TENANT_ID, { limit: -3 });
      expect(mockPrisma.message.findMany.mock.calls[0][0].take).toBe(1);
    });
  });

  describe("addParticipant", () => {
    it("appends the new user, creates the Participant row, and returns the updated conversation", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER],
      });
      mockPrisma.conversation.update.mockResolvedValue({
        id: CONVERSATION_ID,
        participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      });

      const result = await service.addParticipant(
        CONVERSATION_ID,
        USER_ID_SELLER,
        USER_ID_BUYER,
        TENANT_ID,
        "SELLER",
      );

      expect(result.participantIds).toContain(USER_ID_SELLER);
      expect(mockPrisma.participant.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          tenantId: TENANT_ID,
          conversationId: CONVERSATION_ID,
          userId: USER_ID_SELLER,
          role: "SELLER",
        }),
      });
    });

    it("is a no-op if the user is already a participant", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      });

      const result = await service.addParticipant(
        CONVERSATION_ID,
        USER_ID_SELLER,
        USER_ID_BUYER,
        TENANT_ID,
      );

      expect(mockPrisma.participant.create).not.toHaveBeenCalled();
      expect(result.participantIds).toContain(USER_ID_SELLER);
    });

    it("rejects a non-participant requester", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER],
      });
      await expect(
        service.addParticipant(CONVERSATION_ID, USER_ID_SELLER, "stranger", TENANT_ID),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe("removeParticipant", () => {
    it("removes the user and returns the pruned participant list", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      });
      mockPrisma.conversation.update.mockResolvedValue({
        id: CONVERSATION_ID,
        participantIds: [USER_ID_BUYER],
      });

      const result = await service.removeParticipant(
        CONVERSATION_ID,
        USER_ID_SELLER,
        USER_ID_BUYER,
        TENANT_ID,
      );

      expect(result.participantIds).not.toContain(USER_ID_SELLER);
      expect(mockPrisma.participant.deleteMany).toHaveBeenCalledWith({
        where: { tenantId: TENANT_ID, conversationId: CONVERSATION_ID, userId: USER_ID_SELLER },
      });
    });

    it("refuses to remove the last participant (asks caller to archive instead)", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER],
      });
      await expect(
        service.removeParticipant(CONVERSATION_ID, USER_ID_BUYER, USER_ID_BUYER, TENANT_ID),
      ).rejects.toThrow(BadRequestException);
    });

    it("404s when the target user is not actually a participant", async () => {
      mockPrisma.conversation.findFirst.mockResolvedValue({
        id: CONVERSATION_ID,
        tenantId: TENANT_ID,
        participantIds: [USER_ID_BUYER, USER_ID_SELLER],
      });
      await expect(
        service.removeParticipant(CONVERSATION_ID, "ghost-user", USER_ID_BUYER, TENANT_ID),
      ).rejects.toThrow(NotFoundException);
    });
  });
});

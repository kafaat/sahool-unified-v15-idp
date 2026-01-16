/**
 * SAHOOL Chat Service Tests
 * اختبارات خدمة المحادثات
 */

import { Test, TestingModule } from "@nestjs/testing";
import { NotFoundException, BadRequestException } from "@nestjs/common";
import { ChatService } from "../src/chat/chat.service";
import { PrismaService } from "../src/prisma/prisma.service";
import { CreateConversationDto } from "../src/chat/dto/create-conversation.dto";
import { SendMessageDto } from "../src/chat/dto/send-message.dto";
import { MessageType } from "../src/chat/dto/send-message.dto";

describe("ChatService", () => {
  let service: ChatService;
  let prismaService: PrismaService;

  // Mock data
  const mockConversation = {
    id: "conv-123",
    participantIds: ["user-123", "user-456"],
    productId: "prod-789",
    orderId: null,
    isActive: true,
    lastMessage: null,
    lastMessageAt: null,
    createdAt: new Date(),
    updatedAt: new Date(),
    participants: [
      {
        id: "part-1",
        conversationId: "conv-123",
        userId: "user-123",
        role: "BUYER",
        unreadCount: 0,
        lastReadAt: null,
        isTyping: false,
        isOnline: true,
        lastSeenAt: new Date(),
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      {
        id: "part-2",
        conversationId: "conv-123",
        userId: "user-456",
        role: "SELLER",
        unreadCount: 0,
        lastReadAt: null,
        isTyping: false,
        isOnline: true,
        lastSeenAt: new Date(),
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ],
    messages: [],
  };

  const mockMessage = {
    id: "msg-123",
    conversationId: "conv-123",
    senderId: "user-123",
    content: "Hello, I am interested in buying your product",
    messageType: "TEXT",
    attachmentUrl: null,
    offerAmount: null,
    offerCurrency: "YER",
    isRead: false,
    readAt: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockPrismaService = {
    conversation: {
      findFirst: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
    message: {
      findUnique: jest.fn(),
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
      count: jest.fn(),
    },
    participant: {
      findMany: jest.fn(),
      updateMany: jest.fn(),
    },
    $transaction: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ChatService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<ChatService>(ChatService);
    prismaService = module.get<PrismaService>(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // =========================================================================
  // Create Conversation Tests - اختبارات إنشاء محادثة
  // =========================================================================

  describe("createConversation - إنشاء محادثة", () => {
    it("should create a new conversation successfully", async () => {
      const createDto: CreateConversationDto = {
        participantIds: ["user-123", "user-456"],
        productId: "prod-789",
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      const result = await service.createConversation(createDto);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.findFirst).toHaveBeenCalledWith({
        where: {
          participantIds: {
            hasEvery: createDto.participantIds,
          },
          productId: "prod-789",
          orderId: null,
        },
        include: {
          participants: true,
          messages: {
            orderBy: { createdAt: "desc" },
            take: 1,
          },
        },
      });
      expect(mockPrismaService.conversation.create).toHaveBeenCalled();
    });

    it("should return existing conversation if already exists", async () => {
      const createDto: CreateConversationDto = {
        participantIds: ["user-123", "user-456"],
        productId: "prod-789",
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(
        mockConversation,
      );

      const result = await service.createConversation(createDto);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.create).not.toHaveBeenCalled();
    });

    it("should create conversation with orderId", async () => {
      const createDto: CreateConversationDto = {
        participantIds: ["user-123", "user-456"],
        orderId: "order-101",
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue({
        ...mockConversation,
        orderId: "order-101",
      });

      const result = await service.createConversation(createDto);

      expect(result.orderId).toBe("order-101");
    });

    it("should create conversation with correct participant roles", async () => {
      const createDto: CreateConversationDto = {
        participantIds: ["user-123", "user-456"],
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      await service.createConversation(createDto);

      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            participantIds: createDto.participantIds,
            participants: {
              create: expect.arrayContaining([
                expect.objectContaining({
                  userId: "user-123",
                  role: "BUYER",
                }),
                expect.objectContaining({
                  userId: "user-456",
                  role: "SELLER",
                }),
              ]),
            },
          }),
        }),
      );
    });
  });

  // =========================================================================
  // Send Message Tests - اختبارات إرسال رسالة
  // =========================================================================

  describe("sendMessage - إرسال رسالة", () => {
    it("should send a message successfully", async () => {
      const sendDto: SendMessageDto = {
        conversationId: "conv-123",
        senderId: "user-123",
        content: "Hello, I am interested in buying your product",
        messageType: MessageType.TEXT,
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: {
            create: jest.fn().mockResolvedValue(mockMessage),
          },
          conversation: {
            update: jest.fn().mockResolvedValue(mockConversation),
          },
          participant: {
            updateMany: jest.fn().mockResolvedValue({ count: 1 }),
          },
        });
      });

      const result = await service.sendMessage(sendDto);

      expect(result).toBeDefined();
      expect(mockPrismaService.conversation.findUnique).toHaveBeenCalledWith({
        where: { id: "conv-123" },
      });
    });

    it("should throw NotFoundException when conversation not found", async () => {
      const sendDto: SendMessageDto = {
        conversationId: "conv-999",
        senderId: "user-123",
        content: "Hello",
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(service.sendMessage(sendDto)).rejects.toThrow(
        NotFoundException,
      );
    });

    it("should throw BadRequestException when sender is not a participant", async () => {
      const sendDto: SendMessageDto = {
        conversationId: "conv-123",
        senderId: "user-999",
        content: "Hello",
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );

      await expect(service.sendMessage(sendDto)).rejects.toThrow(
        BadRequestException,
      );
    });

    it("should send message with attachment", async () => {
      const sendDto: SendMessageDto = {
        conversationId: "conv-123",
        senderId: "user-123",
        content: "Check this image",
        messageType: MessageType.IMAGE,
        attachmentUrl: "https://cdn.sahool.com/images/product.jpg",
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: {
            create: jest.fn().mockResolvedValue({
              ...mockMessage,
              attachmentUrl: sendDto.attachmentUrl,
            }),
          },
          conversation: {
            update: jest.fn().mockResolvedValue(mockConversation),
          },
          participant: {
            updateMany: jest.fn().mockResolvedValue({ count: 1 }),
          },
        });
      });

      const result = await service.sendMessage(sendDto);

      expect(result).toBeDefined();
    });

    it("should send message with offer amount", async () => {
      const sendDto: SendMessageDto = {
        conversationId: "conv-123",
        senderId: "user-123",
        content: "I offer 5000 YER for this product",
        messageType: MessageType.OFFER,
        offerAmount: 5000,
        offerCurrency: "YER",
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: {
            create: jest.fn().mockResolvedValue({
              ...mockMessage,
              offerAmount: 5000,
              offerCurrency: "YER",
            }),
          },
          conversation: {
            update: jest.fn().mockResolvedValue(mockConversation),
          },
          participant: {
            updateMany: jest.fn().mockResolvedValue({ count: 1 }),
          },
        });
      });

      const result = await service.sendMessage(sendDto);

      expect(result).toBeDefined();
    });

    it("should increment unread count for other participants", async () => {
      const sendDto: SendMessageDto = {
        conversationId: "conv-123",
        senderId: "user-123",
        content: "Hello",
      };

      const mockUpdateMany = jest.fn().mockResolvedValue({ count: 1 });
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: {
            create: jest.fn().mockResolvedValue(mockMessage),
          },
          conversation: {
            update: jest.fn().mockResolvedValue(mockConversation),
          },
          participant: {
            updateMany: mockUpdateMany,
          },
        });
      });

      await service.sendMessage(sendDto);

      expect(mockUpdateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: {
            conversationId: "conv-123",
            userId: { not: "user-123" },
          },
          data: {
            unreadCount: { increment: 1 },
          },
        }),
      );
    });
  });

  // =========================================================================
  // Get Messages Tests - اختبارات جلب الرسائل
  // =========================================================================

  describe("getMessages - جلب الرسائل", () => {
    it("should get messages for a conversation with pagination", async () => {
      const mockMessages = [
        { ...mockMessage, id: "msg-1", content: "Message 1" },
        { ...mockMessage, id: "msg-2", content: "Message 2" },
        { ...mockMessage, id: "msg-3", content: "Message 3" },
      ];

      mockPrismaService.message.findMany.mockResolvedValue(mockMessages);
      mockPrismaService.message.count.mockResolvedValue(10);

      const result = await service.getMessages("conv-123", 1, 50);

      expect(result).toEqual({
        messages: mockMessages.reverse(),
        total: 10,
        page: 1,
        limit: 50,
        totalPages: 1,
      });
      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith({
        where: { conversationId: "conv-123" },
        orderBy: { createdAt: "desc" },
        skip: 0,
        take: 50,
      });
    });

    it("should handle pagination correctly for page 2", async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(100);

      const result = await service.getMessages("conv-123", 2, 50);

      expect(result.page).toBe(2);
      expect(result.totalPages).toBe(2);
      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: 50,
          take: 50,
        }),
      );
    });

    it("should return messages in chronological order", async () => {
      const mockMessages = [
        { ...mockMessage, id: "msg-3", createdAt: new Date("2024-01-03") },
        { ...mockMessage, id: "msg-2", createdAt: new Date("2024-01-02") },
        { ...mockMessage, id: "msg-1", createdAt: new Date("2024-01-01") },
      ];

      mockPrismaService.message.findMany.mockResolvedValue(mockMessages);
      mockPrismaService.message.count.mockResolvedValue(3);

      const result = await service.getMessages("conv-123", 1, 50);

      // Messages should be reversed to chronological order
      expect(result.messages).toEqual(mockMessages.reverse());
    });

    it("should calculate total pages correctly", async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(75);

      const result = await service.getMessages("conv-123", 1, 25);

      expect(result.totalPages).toBe(3);
    });
  });

  // =========================================================================
  // Get Conversation Tests - اختبارات جلب المحادثة
  // =========================================================================

  describe("getConversationById - جلب المحادثة بالمعرف", () => {
    it("should return conversation by ID", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );

      const result = await service.getConversationById("conv-123");

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.findUnique).toHaveBeenCalledWith({
        where: { id: "conv-123" },
        include: {
          participants: true,
        },
      });
    });

    it("should throw NotFoundException when conversation not found", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(service.getConversationById("conv-999")).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  // =========================================================================
  // Get User Conversations Tests - اختبارات جلب محادثات المستخدم
  // =========================================================================

  describe("getUserConversations - جلب محادثات المستخدم", () => {
    it("should return all conversations for a user", async () => {
      const mockConversations = [mockConversation];
      mockPrismaService.conversation.findMany.mockResolvedValue(
        mockConversations,
      );
      mockPrismaService.message.count.mockResolvedValue(2);

      const result = await service.getUserConversations("user-123");

      expect(result).toHaveLength(1);
      expect(result[0]).toHaveProperty("unreadCount");
      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith({
        where: {
          participantIds: {
            has: "user-123",
          },
          isActive: true,
        },
        include: {
          participants: {
            where: {
              userId: "user-123",
            },
          },
          messages: {
            orderBy: { createdAt: "desc" },
            take: 1,
          },
        },
        orderBy: {
          updatedAt: "desc",
        },
      });
    });

    it("should include unread count for each conversation", async () => {
      const mockConversations = [mockConversation];
      mockPrismaService.conversation.findMany.mockResolvedValue(
        mockConversations,
      );
      mockPrismaService.message.count.mockResolvedValue(5);

      const result = await service.getUserConversations("user-123");

      expect(result[0].unreadCount).toBe(5);
    });
  });

  // =========================================================================
  // Mark Message as Read Tests - اختبارات تحديد الرسالة كمقروءة
  // =========================================================================

  describe("markMessageAsRead - تحديد الرسالة كمقروءة", () => {
    it("should mark message as read", async () => {
      const messageWithConversation = {
        ...mockMessage,
        conversation: mockConversation,
      };

      mockPrismaService.message.findUnique.mockResolvedValue(
        messageWithConversation,
      );
      mockPrismaService.message.update.mockResolvedValue({
        ...messageWithConversation,
        isRead: true,
      });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.markMessageAsRead("msg-123", "user-456");

      expect(mockPrismaService.message.update).toHaveBeenCalledWith({
        where: { id: "msg-123" },
        data: {
          isRead: true,
          readAt: expect.any(Date),
        },
      });
    });

    it("should not mark message as read if user is the sender", async () => {
      const messageWithConversation = {
        ...mockMessage,
        senderId: "user-123",
        conversation: mockConversation,
      };

      mockPrismaService.message.findUnique.mockResolvedValue(
        messageWithConversation,
      );

      await service.markMessageAsRead("msg-123", "user-123");

      expect(mockPrismaService.message.update).not.toHaveBeenCalled();
    });

    it("should throw NotFoundException when message not found", async () => {
      mockPrismaService.message.findUnique.mockResolvedValue(null);

      await expect(
        service.markMessageAsRead("msg-999", "user-123"),
      ).rejects.toThrow(NotFoundException);
    });
  });

  // =========================================================================
  // Unread Count Tests - اختبارات عدد الرسائل غير المقروءة
  // =========================================================================

  describe("getUnreadCount - عدد الرسائل غير المقروءة", () => {
    it("should return total unread count for user", async () => {
      const mockParticipants = [
        { unreadCount: 3 },
        { unreadCount: 5 },
        { unreadCount: 2 },
      ];

      mockPrismaService.participant.findMany.mockResolvedValue(
        mockParticipants,
      );

      const result = await service.getUnreadCount("user-123");

      expect(result).toBe(10);
      expect(mockPrismaService.participant.findMany).toHaveBeenCalledWith({
        where: { userId: "user-123" },
        select: { unreadCount: true },
      });
    });

    it("should return 0 when user has no unread messages", async () => {
      mockPrismaService.participant.findMany.mockResolvedValue([]);

      const result = await service.getUnreadCount("user-123");

      expect(result).toBe(0);
    });
  });

  // =========================================================================
  // Mark Conversation as Read Tests - اختبارات تحديد المحادثة كمقروءة
  // =========================================================================

  describe("markConversationAsRead - تحديد المحادثة كمقروءة", () => {
    it("should mark all messages in conversation as read", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 5 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.markConversationAsRead(
        "conv-123",
        "user-456",
      );

      expect(result).toEqual({
        success: true,
        conversationId: "conv-123",
      });
      expect(mockPrismaService.message.updateMany).toHaveBeenCalledWith({
        where: {
          conversationId: "conv-123",
          senderId: { not: "user-456" },
          isRead: false,
        },
        data: {
          isRead: true,
          readAt: expect.any(Date),
        },
      });
    });

    it("should reset unread count for participant", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 5 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      await service.markConversationAsRead("conv-123", "user-456");

      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith({
        where: {
          conversationId: "conv-123",
          userId: "user-456",
        },
        data: {
          lastReadAt: expect.any(Date),
          unreadCount: 0,
        },
      });
    });
  });

  // =========================================================================
  // Typing Indicator Tests - اختبارات مؤشر الكتابة
  // =========================================================================

  describe("updateTypingIndicator - تحديث مؤشر الكتابة", () => {
    it("should update typing indicator", async () => {
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.updateTypingIndicator(
        "conv-123",
        "user-123",
        true,
      );

      expect(result).toEqual({
        conversationId: "conv-123",
        userId: "user-123",
        isTyping: true,
      });
      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith({
        where: {
          conversationId: "conv-123",
          userId: "user-123",
        },
        data: {
          isTyping: true,
        },
      });
    });
  });

  // =========================================================================
  // Online Status Tests - اختبارات حالة الاتصال
  // =========================================================================

  describe("updateOnlineStatus - تحديث حالة الاتصال", () => {
    it("should update user online status", async () => {
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 2 });

      const result = await service.updateOnlineStatus("user-123", true);

      expect(result).toEqual({
        userId: "user-123",
        isOnline: true,
      });
      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith({
        where: { userId: "user-123" },
        data: {
          isOnline: true,
          lastSeenAt: expect.any(Date),
        },
      });
    });

    it("should set user offline status", async () => {
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 2 });

      const result = await service.updateOnlineStatus("user-123", false);

      expect(result.isOnline).toBe(false);
    });
  });
});

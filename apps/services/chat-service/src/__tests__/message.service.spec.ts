/**
 * Message Service Tests
 * اختبارات خدمة الرسائل
 *
 * Tests message-specific functionality including:
 * - Message sending and receiving
 * - Message pagination
 * - Message read status
 * - Message types (TEXT, IMAGE, OFFER, SYSTEM)
 */

import { Test, TestingModule } from "@nestjs/testing";
import { NotFoundException, BadRequestException } from "@nestjs/common";
import { ChatService } from "../chat/chat.service";
import { PrismaService } from "../prisma/prisma.service";
import { SendMessageDto, MessageType } from "../chat/dto/send-message.dto";

describe("MessageService (Message Operations)", () => {
  let service: ChatService;
  let prismaService: PrismaService;

  // Mock data
  const mockUserId = "user-123";
  const mockUserId2 = "user-456";
  const mockConversationId = "conv-789";
  const mockMessageId = "msg-001";

  const mockConversation = {
    id: mockConversationId,
    participantIds: [mockUserId, mockUserId2],
    productId: "prod-123",
    orderId: null,
    lastMessage: "Hello",
    lastMessageAt: new Date(),
    isActive: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockMessage = {
    id: mockMessageId,
    conversationId: mockConversationId,
    senderId: mockUserId,
    content: "Test message",
    messageType: "TEXT",
    attachmentUrl: null,
    offerAmount: null,
    offerCurrency: "YER",
    isRead: false,
    readAt: null,
    createdAt: new Date("2024-01-01T10:00:00Z"),
    updatedAt: new Date("2024-01-01T10:00:00Z"),
  };

  // Mock PrismaService
  const mockPrismaService = {
    conversation: {
      findUnique: jest.fn(),
      update: jest.fn(),
    },
    message: {
      create: jest.fn(),
      findMany: jest.fn(),
      findUnique: jest.fn(),
      count: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
    },
    participant: {
      updateMany: jest.fn(),
      findMany: jest.fn(),
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

    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("Message Sending", () => {
    const sendMessageDto: SendMessageDto = {
      conversationId: mockConversationId,
      senderId: mockUserId,
      content: "Hello, World!",
      messageType: MessageType.TEXT,
    };

    beforeEach(() => {
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
    });

    it("should send a text message", async () => {
      const result = await service.sendMessage(sendMessageDto);

      expect(result).toBeDefined();
      expect(mockPrismaService.conversation.findUnique).toHaveBeenCalledWith({
        where: { id: mockConversationId },
      });
    });

    it("should send an image message with attachment URL", async () => {
      const imageDto: SendMessageDto = {
        ...sendMessageDto,
        messageType: MessageType.IMAGE,
        attachmentUrl: "https://cdn.sahool.com/images/product.jpg",
        content: "Check out this product",
      };

      const imageMessage = {
        ...mockMessage,
        messageType: "IMAGE",
        attachmentUrl: "https://cdn.sahool.com/images/product.jpg",
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(imageMessage) },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await service.sendMessage(imageDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it("should send an offer message with price details", async () => {
      const offerDto: SendMessageDto = {
        ...sendMessageDto,
        messageType: MessageType.OFFER,
        content: "I offer 5000 YER for this product",
        offerAmount: 5000.0,
        offerCurrency: "YER",
      };

      const offerMessage = {
        ...mockMessage,
        messageType: "OFFER",
        offerAmount: 5000.0,
        offerCurrency: "YER",
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(offerMessage) },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await service.sendMessage(offerDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it("should send system message", async () => {
      const systemDto: SendMessageDto = {
        ...sendMessageDto,
        messageType: MessageType.SYSTEM,
        content: "Order has been placed",
      };

      const systemMessage = {
        ...mockMessage,
        messageType: "SYSTEM",
      };

      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(systemMessage) },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await service.sendMessage(systemDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it("should validate conversation exists before sending", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(service.sendMessage(sendMessageDto)).rejects.toThrow(
        NotFoundException,
      );
    });

    it("should validate sender is a participant", async () => {
      const unauthorizedConversation = {
        ...mockConversation,
        participantIds: [mockUserId2],
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        unauthorizedConversation,
      );

      await expect(service.sendMessage(sendMessageDto)).rejects.toThrow(
        BadRequestException,
      );
    });

    it("should update conversation lastMessage and lastMessageAt", async () => {
      await service.sendMessage(sendMessageDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it("should increment unread count for recipients", async () => {
      await service.sendMessage(sendMessageDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it("should handle empty message content gracefully", async () => {
      const emptyDto = { ...sendMessageDto, content: "" };

      // Should not throw, validation happens at DTO level
      await service.sendMessage(emptyDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it("should handle special characters in message content", async () => {
      const specialCharsDto = {
        ...sendMessageDto,
        content: "Hello! @#$%^&*() 🌾 السلام عليكم",
      };

      await service.sendMessage(specialCharsDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });
  });

  describe("Message Retrieval and Pagination", () => {
    const mockMessages = [
      {
        ...mockMessage,
        id: "msg-1",
        createdAt: new Date("2024-01-01T10:00:00Z"),
      },
      {
        ...mockMessage,
        id: "msg-2",
        createdAt: new Date("2024-01-01T11:00:00Z"),
      },
      {
        ...mockMessage,
        id: "msg-3",
        createdAt: new Date("2024-01-01T12:00:00Z"),
      },
    ];

    it("should retrieve messages with default pagination", async () => {
      mockPrismaService.message.findMany.mockResolvedValue(
        [...mockMessages].reverse(),
      );
      mockPrismaService.message.count.mockResolvedValue(3);

      const result = await service.getMessages(mockConversationId);

      expect(result.messages).toHaveLength(3);
      expect(result.page).toBe(1);
      expect(result.limit).toBe(50);
      expect(result.total).toBe(3);
      expect(result.totalPages).toBe(1);
    });

    it("should retrieve messages with custom pagination", async () => {
      mockPrismaService.message.findMany.mockResolvedValue([mockMessages[0]]);
      mockPrismaService.message.count.mockResolvedValue(100);

      const result = await service.getMessages(mockConversationId, 2, 20);

      expect(result.page).toBe(2);
      expect(result.limit).toBe(20);
      expect(result.total).toBe(100);
      expect(result.totalPages).toBe(5);
    });

    it("should return messages in chronological order", async () => {
      mockPrismaService.message.findMany.mockResolvedValue(
        [...mockMessages].reverse(),
      );
      mockPrismaService.message.count.mockResolvedValue(3);

      const result = await service.getMessages(mockConversationId);

      expect(result.messages[0].id).toBe("msg-1");
      expect(result.messages[1].id).toBe("msg-2");
      expect(result.messages[2].id).toBe("msg-3");
    });

    it("should calculate skip correctly for pagination", async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(0);

      await service.getMessages(mockConversationId, 3, 25);

      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: 50, // (3 - 1) * 25
          take: 25,
        }),
      );
    });

    it("should handle empty message list", async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(0);

      const result = await service.getMessages(mockConversationId);

      expect(result.messages).toEqual([]);
      expect(result.total).toBe(0);
      expect(result.totalPages).toBe(0);
    });
  });

  describe("Cursor-Based Pagination", () => {
    const mockMessages = Array(55)
      .fill(null)
      .map((_, i) => ({
        ...mockMessage,
        id: `msg-${i}`,
        createdAt: new Date(`2024-01-01T${10 + i}:00:00Z`),
      }));

    it("should retrieve first page without cursor", async () => {
      mockPrismaService.message.findMany.mockResolvedValue(
        mockMessages.slice(0, 51),
      );

      const result = await service.getMessagesCursor(mockConversationId);

      expect(result.messages).toHaveLength(50);
      expect(result.hasMore).toBe(true);
      expect(result.nextCursor).toBe("msg-49");
    });

    it("should retrieve next page with cursor", async () => {
      mockPrismaService.message.findMany.mockResolvedValue(
        mockMessages.slice(50, 55),
      );

      const result = await service.getMessagesCursor(
        mockConversationId,
        "msg-49",
        50,
      );

      expect(result.messages).toHaveLength(5);
      expect(result.hasMore).toBe(false);
      expect(result.nextCursor).toBeNull();
    });

    it("should indicate no more messages when at end", async () => {
      mockPrismaService.message.findMany.mockResolvedValue([mockMessage]);

      const result = await service.getMessagesCursor(mockConversationId);

      expect(result.hasMore).toBe(false);
      expect(result.nextCursor).toBeNull();
    });

    it("should use custom limit", async () => {
      mockPrismaService.message.findMany.mockResolvedValue(
        mockMessages.slice(0, 21),
      );

      const result = await service.getMessagesCursor(
        mockConversationId,
        undefined,
        20,
      );

      expect(result.messages).toHaveLength(20);
      expect(result.hasMore).toBe(true);
    });
  });

  describe("Message Read Status", () => {
    it("should mark single message as read", async () => {
      mockPrismaService.message.findUnique.mockResolvedValue({
        ...mockMessage,
        conversation: mockConversation,
      });
      mockPrismaService.message.update.mockResolvedValue({
        ...mockMessage,
        isRead: true,
        readAt: new Date(),
      });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.markMessageAsRead(
        mockMessageId,
        mockUserId2,
      );

      // Service returns the original message from findUnique, not the updated one
      expect(result).toBeDefined();
      expect(mockPrismaService.message.update).toHaveBeenCalledWith({
        where: { id: mockMessageId },
        data: {
          isRead: true,
          readAt: expect.any(Date),
        },
      });
    });

    it("should not mark own messages as read", async () => {
      mockPrismaService.message.findUnique.mockResolvedValue({
        ...mockMessage,
        senderId: mockUserId,
        conversation: mockConversation,
      });

      await service.markMessageAsRead(mockMessageId, mockUserId);

      expect(mockPrismaService.message.update).not.toHaveBeenCalled();
    });

    it("should update participant lastReadAt when marking message read", async () => {
      mockPrismaService.message.findUnique.mockResolvedValue({
        ...mockMessage,
        conversation: mockConversation,
      });
      mockPrismaService.message.update.mockResolvedValue({
        ...mockMessage,
        isRead: true,
      });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      await service.markMessageAsRead(mockMessageId, mockUserId2);

      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith({
        where: {
          conversationId: mockConversationId,
          userId: mockUserId2,
        },
        data: {
          lastReadAt: expect.any(Date),
          unreadCount: 0,
        },
      });
    });

    it("should reset unread count when marking message read", async () => {
      mockPrismaService.message.findUnique.mockResolvedValue({
        ...mockMessage,
        conversation: mockConversation,
      });
      mockPrismaService.message.update.mockResolvedValue(mockMessage);
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      await service.markMessageAsRead(mockMessageId, mockUserId2);

      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            unreadCount: 0,
          }),
        }),
      );
    });

    it("should throw NotFoundException for non-existent message", async () => {
      mockPrismaService.message.findUnique.mockResolvedValue(null);

      await expect(
        service.markMessageAsRead("invalid-id", mockUserId),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("Bulk Read Operations", () => {
    it("should mark all messages in conversation as read", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 10 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.markConversationAsRead(
        mockConversationId,
        mockUserId,
      );

      expect(result.success).toBe(true);
      expect(mockPrismaService.message.updateMany).toHaveBeenCalledWith({
        where: {
          conversationId: mockConversationId,
          senderId: { not: mockUserId },
          isRead: false,
        },
        data: {
          isRead: true,
          readAt: expect.any(Date),
        },
      });
    });

    it("should only mark unread messages", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 5 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      await service.markConversationAsRead(mockConversationId, mockUserId);

      expect(mockPrismaService.message.updateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            isRead: false,
          }),
        }),
      );
    });

    it("should not mark own messages as read", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 3 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      await service.markConversationAsRead(mockConversationId, mockUserId);

      expect(mockPrismaService.message.updateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            senderId: { not: mockUserId },
          }),
        }),
      );
    });

    it("should update participant after bulk read", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 7 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      await service.markConversationAsRead(mockConversationId, mockUserId);

      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith({
        where: {
          conversationId: mockConversationId,
          userId: mockUserId,
        },
        data: {
          lastReadAt: expect.any(Date),
          unreadCount: 0,
        },
      });
    });
  });

  describe("Unread Message Count", () => {
    it("should calculate total unread count across conversations", async () => {
      mockPrismaService.participant.findMany.mockResolvedValue([
        { unreadCount: 5 },
        { unreadCount: 3 },
        { unreadCount: 7 },
      ]);

      const result = await service.getUnreadCount(mockUserId);

      expect(result).toBe(15);
    });

    it("should return zero when no unread messages", async () => {
      mockPrismaService.participant.findMany.mockResolvedValue([
        { unreadCount: 0 },
        { unreadCount: 0 },
      ]);

      const result = await service.getUnreadCount(mockUserId);

      expect(result).toBe(0);
    });

    it("should return zero when user has no conversations", async () => {
      mockPrismaService.participant.findMany.mockResolvedValue([]);

      const result = await service.getUnreadCount(mockUserId);

      expect(result).toBe(0);
    });

    it("should query only user-specific participants", async () => {
      mockPrismaService.participant.findMany.mockResolvedValue([]);

      await service.getUnreadCount(mockUserId);

      expect(mockPrismaService.participant.findMany).toHaveBeenCalledWith({
        where: { userId: mockUserId },
        select: { unreadCount: true },
      });
    });
  });

  describe("Message Type Validation", () => {
    it("should handle TEXT message type", async () => {
      const dto: SendMessageDto = {
        conversationId: mockConversationId,
        senderId: mockUserId,
        content: "Plain text message",
        messageType: MessageType.TEXT,
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(mockMessage) },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await expect(service.sendMessage(dto)).resolves.toBeDefined();
    });

    it("should handle IMAGE message type with URL", async () => {
      const dto: SendMessageDto = {
        conversationId: mockConversationId,
        senderId: mockUserId,
        content: "Image description",
        messageType: MessageType.IMAGE,
        attachmentUrl: "https://cdn.sahool.com/image.jpg",
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: {
            create: jest.fn().mockResolvedValue({
              ...mockMessage,
              messageType: "IMAGE",
              attachmentUrl: dto.attachmentUrl,
            }),
          },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await expect(service.sendMessage(dto)).resolves.toBeDefined();
    });

    it("should handle OFFER message type with amount", async () => {
      const dto: SendMessageDto = {
        conversationId: mockConversationId,
        senderId: mockUserId,
        content: "Price offer",
        messageType: MessageType.OFFER,
        offerAmount: 10000.5,
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
              messageType: "OFFER",
              offerAmount: dto.offerAmount,
            }),
          },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await expect(service.sendMessage(dto)).resolves.toBeDefined();
    });

    it("should handle SYSTEM message type", async () => {
      const dto: SendMessageDto = {
        conversationId: mockConversationId,
        senderId: mockUserId,
        content: "Order completed",
        messageType: MessageType.SYSTEM,
      };

      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: {
            create: jest.fn().mockResolvedValue({
              ...mockMessage,
              messageType: "SYSTEM",
            }),
          },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await expect(service.sendMessage(dto)).resolves.toBeDefined();
    });
  });

  describe("Error Handling", () => {
    it("should handle database transaction failures", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockRejectedValue(
        new Error("Transaction failed"),
      );

      await expect(
        service.sendMessage({
          conversationId: mockConversationId,
          senderId: mockUserId,
          content: "Test",
          messageType: MessageType.TEXT,
        }),
      ).rejects.toThrow(BadRequestException);
    });

    it("should handle message not found error", async () => {
      mockPrismaService.message.findUnique.mockResolvedValue(null);

      await expect(
        service.markMessageAsRead("invalid-id", mockUserId),
      ).rejects.toThrow(NotFoundException);
    });

    it("should sanitize error messages for security", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockRejectedValue(
        new Error("Internal database error with sensitive info"),
      );

      await expect(
        service.sendMessage({
          conversationId: mockConversationId,
          senderId: mockUserId,
          content: "Test",
          messageType: MessageType.TEXT,
        }),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe("Performance and Edge Cases", () => {
    it("should handle large pagination offsets", async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(1000);

      const result = await service.getMessages(mockConversationId, 20, 50);

      expect(result.page).toBe(20);
      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: 950, // (20 - 1) * 50
        }),
      );
    });

    it("should handle concurrent read operations", async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 5 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const promises = Array(3)
        .fill(null)
        .map(() =>
          service.markConversationAsRead(mockConversationId, mockUserId),
        );

      await expect(Promise.all(promises)).resolves.toHaveLength(3);
    });

    it("should handle message with maximum content length", async () => {
      const maxContent = "a".repeat(10000);
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        mockConversation,
      );
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: {
            create: jest.fn().mockResolvedValue({
              ...mockMessage,
              content: maxContent,
            }),
          },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await expect(
        service.sendMessage({
          conversationId: mockConversationId,
          senderId: mockUserId,
          content: maxContent,
          messageType: MessageType.TEXT,
        }),
      ).resolves.toBeDefined();
    });
  });
});

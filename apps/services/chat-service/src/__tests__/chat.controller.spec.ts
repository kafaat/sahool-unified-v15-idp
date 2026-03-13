/**
 * Chat Controller Tests
 * اختبارات متحكم المحادثات
 */

import { Test, TestingModule } from "@nestjs/testing";
import { UnauthorizedException, NotFoundException } from "@nestjs/common";
import { ChatController } from "../chat/chat.controller";
import { ChatService } from "../chat/chat.service";
import { CreateConversationDto } from "../chat/dto/create-conversation.dto";
import { SendMessageDto } from "../chat/dto/send-message.dto";
import { MessageType } from "../chat/dto/send-message.dto";

describe("ChatController", () => {
  let controller: ChatController;
  let chatService: ChatService;

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
    messages: [],
    participants: [
      {
        id: "part-1",
        conversationId: mockConversationId,
        userId: mockUserId,
        role: "BUYER",
        lastReadAt: new Date(),
        unreadCount: 0,
        isOnline: true,
        lastSeenAt: new Date(),
        isTyping: false,
        joinedAt: new Date(),
      },
    ],
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
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  // Mock ChatService
  const mockChatService = {
    createConversation: jest.fn(),
    getUserConversations: jest.fn(),
    getConversationById: jest.fn(),
    getMessages: jest.fn(),
    sendMessage: jest.fn(),
    markMessageAsRead: jest.fn(),
    markConversationAsRead: jest.fn(),
    getUnreadCount: jest.fn(),
  };

  const mockReq = {
    user: { tenantId: "tenant-001" },
    headers: { "x-tenant-id": "tenant-001" },
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ChatController],
      providers: [
        {
          provide: ChatService,
          useValue: mockChatService,
        },
      ],
    }).compile();

    controller = module.get<ChatController>(ChatController);
    chatService = module.get<ChatService>(ChatService);

    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("Constructor and Initialization", () => {
    it("should be defined", () => {
      expect(controller).toBeDefined();
    });

    it("should have chatService injected", () => {
      expect(chatService).toBeDefined();
    });
  });

  describe("Health Check", () => {
    it("should return health status", () => {
      const result = controller.healthCheck();

      expect(result).toHaveProperty("status", "ok");
      expect(result).toHaveProperty("service", "chat-service");
      expect(result).toHaveProperty("timestamp");
      expect(typeof result.timestamp).toBe("string");
    });

    it("should return current timestamp", () => {
      const before = new Date();
      const result = controller.healthCheck();
      const after = new Date();

      const timestamp = new Date(result.timestamp);
      expect(timestamp.getTime()).toBeGreaterThanOrEqual(before.getTime());
      expect(timestamp.getTime()).toBeLessThanOrEqual(after.getTime());
    });
  });

  describe("Create Conversation", () => {
    const createDto: CreateConversationDto = {
      participantIds: [mockUserId, mockUserId2],
      productId: "prod-123",
    };

    it("should create a new conversation when user is a participant", async () => {
      mockChatService.createConversation.mockResolvedValue(mockConversation);

      const result = await controller.createConversation(createDto, mockUserId, mockReq);

      expect(result).toEqual(mockConversation);
      expect(mockChatService.createConversation).toHaveBeenCalledWith(
        createDto,
        "tenant-001",
      );
      expect(mockChatService.createConversation).toHaveBeenCalledTimes(1);
    });

    it("should create conversation with orderId", async () => {
      const dtoWithOrder = { ...createDto, orderId: "order-123" };
      mockChatService.createConversation.mockResolvedValue({
        ...mockConversation,
        orderId: "order-123",
      });

      const result = await controller.createConversation(dtoWithOrder, mockUserId, mockReq);

      expect(result.orderId).toBe("order-123");
      expect(mockChatService.createConversation).toHaveBeenCalledWith(
        dtoWithOrder,
        "tenant-001",
      );
    });

    it("should return existing conversation if already exists", async () => {
      const existingConv = { ...mockConversation, id: "existing-conv" };
      mockChatService.createConversation.mockResolvedValue(existingConv);

      const result = await controller.createConversation(createDto, mockUserId, mockReq);

      expect(result).toEqual(existingConv);
    });

    it("should throw UnauthorizedException if user is not a participant", async () => {
      const unauthorizedUserId = "user-999";

      await expect(
        controller.createConversation(createDto, unauthorizedUserId, mockReq),
      ).rejects.toThrow(UnauthorizedException);

      // Service should not be called if authorization fails
      expect(mockChatService.createConversation).not.toHaveBeenCalled();
    });

    it("should allow second participant to create conversation", async () => {
      mockChatService.createConversation.mockResolvedValue(mockConversation);

      const result = await controller.createConversation(createDto, mockUserId2, mockReq);

      expect(result).toEqual(mockConversation);
      expect(mockChatService.createConversation).toHaveBeenCalledWith(createDto, "tenant-001");
    });

    it("should handle service errors", async () => {
      mockChatService.createConversation.mockRejectedValue(
        new Error("Database error"),
      );

      await expect(controller.createConversation(createDto, mockUserId, mockReq)).rejects.toThrow();
    });
  });

  describe("Get User Conversations", () => {
    const mockConversations = [
      mockConversation,
      {
        ...mockConversation,
        id: "conv-999",
        unreadCount: 5,
        lastReadAt: new Date(),
      },
    ];

    it("should return user conversations", async () => {
      mockChatService.getUserConversations.mockResolvedValue(mockConversations);

      const result = await controller.getUserConversations(mockUserId, mockReq);

      expect(result).toEqual(mockConversations);
      expect(mockChatService.getUserConversations).toHaveBeenCalledWith(
        mockUserId, "tenant-001",
      );
      expect(mockChatService.getUserConversations).toHaveBeenCalledTimes(1);
    });

    it("should return empty array if user has no conversations", async () => {
      mockChatService.getUserConversations.mockResolvedValue([]);

      const result = await controller.getUserConversations(mockUserId, mockReq);

      expect(result).toEqual([]);
      expect(Array.isArray(result)).toBe(true);
    });

    it("should include unread counts", async () => {
      const convsWithUnread = mockConversations.map((conv) => ({
        ...conv,
        unreadCount: 3,
      }));
      mockChatService.getUserConversations.mockResolvedValue(convsWithUnread);

      const result = await controller.getUserConversations(mockUserId, mockReq);

      expect(result[0]).toHaveProperty("unreadCount");
      expect(result[1]).toHaveProperty("unreadCount");
    });
  });

  describe("Get Conversation by ID", () => {
    it("should return conversation details", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      const result = await controller.getConversation(
        mockConversationId,
        mockUserId,
        mockReq,
      );

      expect(result).toEqual(mockConversation);
      expect(mockChatService.getConversationById).toHaveBeenCalledWith(
        mockConversationId, "tenant-001",
      );
    });

    it("should verify user access before returning conversation", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      await controller.getConversation(mockConversationId, mockUserId, mockReq);

      // Called twice: once for verification, once for returning
      expect(mockChatService.getConversationById).toHaveBeenCalledTimes(2);
    });

    it("should throw UnauthorizedException if user is not a participant", async () => {
      const unauthorizedUserId = "user-999";
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      await expect(
        controller.getConversation(mockConversationId, unauthorizedUserId, mockReq),
      ).rejects.toThrow(UnauthorizedException);
    });

    it("should throw NotFoundException if conversation does not exist", async () => {
      mockChatService.getConversationById.mockRejectedValue(
        new NotFoundException("Conversation not found"),
      );

      await expect(
        controller.getConversation("invalid-id", mockUserId, mockReq),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("Get Messages", () => {
    const mockMessagesResponse = {
      messages: [mockMessage],
      total: 10,
      page: 1,
      limit: 50,
      totalPages: 1,
    };

    it("should return paginated messages", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);
      mockChatService.getMessages.mockResolvedValue(mockMessagesResponse);

      const result = await controller.getMessages(
        mockConversationId,
        "1",
        "50",
        mockUserId,
        mockReq,
      );

      expect(result).toEqual(mockMessagesResponse);
      expect(mockChatService.getMessages).toHaveBeenCalledWith(
        mockConversationId,
        1,
        50,
        "tenant-001",
      );
    });

    it("should use default pagination values", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);
      mockChatService.getMessages.mockResolvedValue(mockMessagesResponse);

      await controller.getMessages(
        mockConversationId,
        undefined,
        undefined,
        mockUserId,
        mockReq,
      );

      expect(mockChatService.getMessages).toHaveBeenCalledWith(
        mockConversationId,
        1,
        50,
        "tenant-001",
      );
    });

    it("should handle custom pagination", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);
      mockChatService.getMessages.mockResolvedValue({
        ...mockMessagesResponse,
        page: 2,
        limit: 20,
      });

      await controller.getMessages(mockConversationId, "2", "20", mockUserId, mockReq);

      expect(mockChatService.getMessages).toHaveBeenCalledWith(
        mockConversationId,
        2,
        20,
        "tenant-001",
      );
    });

    it("should verify user access before returning messages", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);
      mockChatService.getMessages.mockResolvedValue(mockMessagesResponse);

      await controller.getMessages(mockConversationId, "1", "50", mockUserId, mockReq);

      expect(mockChatService.getConversationById).toHaveBeenCalledWith(
        mockConversationId, "tenant-001",
      );
    });

    it("should throw UnauthorizedException for unauthorized access", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      await expect(
        controller.getMessages(mockConversationId, "1", "50", "user-999", mockReq),
      ).rejects.toThrow(UnauthorizedException);
    });
  });

  describe("Send Message", () => {
    const sendMessageDto: SendMessageDto = {
      conversationId: mockConversationId,
      senderId: mockUserId,
      content: "Test message",
      messageType: MessageType.TEXT,
    };

    it("should send a message", async () => {
      mockChatService.sendMessage.mockResolvedValue(mockMessage);

      const result = await controller.sendMessage(sendMessageDto, mockUserId, mockReq);

      expect(result).toEqual(mockMessage);
      expect(mockChatService.sendMessage).toHaveBeenCalledWith({
        ...sendMessageDto,
        senderId: mockUserId,
      }, "tenant-001");
    });

    it("should override senderId with authenticated userId", async () => {
      const dtoWithWrongSender = { ...sendMessageDto, senderId: "wrong-user" };
      mockChatService.sendMessage.mockResolvedValue(mockMessage);

      await controller.sendMessage(dtoWithWrongSender, mockUserId, mockReq);

      expect(mockChatService.sendMessage).toHaveBeenCalledWith({
        ...dtoWithWrongSender,
        senderId: mockUserId,
      }, "tenant-001");
    });

    it("should send message with offer", async () => {
      const offerMessage = {
        ...sendMessageDto,
        messageType: MessageType.OFFER,
        offerAmount: 5000.0,
        offerCurrency: "YER",
      };
      mockChatService.sendMessage.mockResolvedValue({
        ...mockMessage,
        messageType: "OFFER",
        offerAmount: 5000.0,
      });

      const result = await controller.sendMessage(offerMessage, mockUserId, mockReq);

      expect(result.messageType).toBe("OFFER");
      expect(result.offerAmount).toBe(5000.0);
    });

    it("should send message with attachment", async () => {
      const imageMessage = {
        ...sendMessageDto,
        messageType: MessageType.IMAGE,
        attachmentUrl: "https://cdn.sahool.com/image.jpg",
      };
      mockChatService.sendMessage.mockResolvedValue({
        ...mockMessage,
        messageType: "IMAGE",
        attachmentUrl: "https://cdn.sahool.com/image.jpg",
      });

      const result = await controller.sendMessage(imageMessage, mockUserId, mockReq);

      expect(result.messageType).toBe("IMAGE");
      expect(result.attachmentUrl).toBe("https://cdn.sahool.com/image.jpg");
    });

    it("should handle service errors", async () => {
      mockChatService.sendMessage.mockRejectedValue(
        new NotFoundException("Conversation not found"),
      );

      await expect(
        controller.sendMessage(sendMessageDto, mockUserId, mockReq),
      ).rejects.toThrow();
    });
  });

  describe("Mark Message as Read", () => {
    it("should mark a message as read", async () => {
      const readMessage = { ...mockMessage, isRead: true, readAt: new Date() };
      mockChatService.markMessageAsRead.mockResolvedValue(readMessage);

      const result = await controller.markMessageAsRead(
        mockMessageId,
        mockUserId,
        mockReq,
      );

      expect(result.isRead).toBe(true);
      expect(result.readAt).toBeDefined();
      expect(mockChatService.markMessageAsRead).toHaveBeenCalledWith(
        mockMessageId,
        mockUserId, "tenant-001",
      );
    });

    it("should not mark own message as read", async () => {
      mockChatService.markMessageAsRead.mockResolvedValue(mockMessage);

      const result = await controller.markMessageAsRead(
        mockMessageId,
        mockUserId,
        mockReq,
      );

      expect(mockChatService.markMessageAsRead).toHaveBeenCalledWith(
        mockMessageId,
        mockUserId, "tenant-001",
      );
    });

    it("should throw NotFoundException for invalid messageId", async () => {
      mockChatService.markMessageAsRead.mockRejectedValue(
        new NotFoundException("Message not found"),
      );

      await expect(
        controller.markMessageAsRead("invalid-id", mockUserId, mockReq),
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe("Mark Conversation as Read", () => {
    it("should mark all messages in conversation as read", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);
      mockChatService.markConversationAsRead.mockResolvedValue({
        success: true,
        conversationId: mockConversationId,
      });

      const result = await controller.markConversationAsRead(
        mockConversationId,
        mockUserId,
        mockReq,
      );

      expect(result.success).toBe(true);
      expect(result.conversationId).toBe(mockConversationId);
      expect(mockChatService.markConversationAsRead).toHaveBeenCalledWith(
        mockConversationId,
        mockUserId, "tenant-001",
      );
    });

    it("should verify user access before marking as read", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);
      mockChatService.markConversationAsRead.mockResolvedValue({
        success: true,
        conversationId: mockConversationId,
      });

      await controller.markConversationAsRead(mockConversationId, mockUserId, mockReq);

      expect(mockChatService.getConversationById).toHaveBeenCalledWith(
        mockConversationId, "tenant-001",
      );
    });

    it("should throw UnauthorizedException for unauthorized access", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      await expect(
        controller.markConversationAsRead(mockConversationId, "user-999", mockReq),
      ).rejects.toThrow(UnauthorizedException);
    });
  });

  describe("Get Unread Count", () => {
    it("should return unread message count", async () => {
      mockChatService.getUnreadCount.mockResolvedValue(5);

      const result = await controller.getUnreadCount(mockUserId, mockReq);

      expect(result).toEqual({
        userId: mockUserId,
        unreadCount: 5,
      });
      expect(mockChatService.getUnreadCount).toHaveBeenCalledWith(mockUserId, "tenant-001");
    });

    it("should return zero for no unread messages", async () => {
      mockChatService.getUnreadCount.mockResolvedValue(0);

      const result = await controller.getUnreadCount(mockUserId, mockReq);

      expect(result.unreadCount).toBe(0);
    });

    it("should handle large unread counts", async () => {
      mockChatService.getUnreadCount.mockResolvedValue(999);

      const result = await controller.getUnreadCount(mockUserId, mockReq);

      expect(result.unreadCount).toBe(999);
    });
  });

  describe("Access Control", () => {
    it("should verify conversation access correctly", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      // Should not throw for authorized user
      await expect(
        controller.getConversation(mockConversationId, mockUserId, mockReq),
      ).resolves.toBeDefined();
    });

    it("should deny access to non-participants", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      // Should throw for unauthorized user
      await expect(
        controller.getConversation(mockConversationId, "unauthorized-user", mockReq),
      ).rejects.toThrow(UnauthorizedException);
    });

    it("should allow access to all participants", async () => {
      mockChatService.getConversationById.mockResolvedValue(mockConversation);

      // Both users should have access
      await expect(
        controller.getConversation(mockConversationId, mockUserId, mockReq),
      ).resolves.toBeDefined();

      await expect(
        controller.getConversation(mockConversationId, mockUserId2, mockReq),
      ).resolves.toBeDefined();
    });
  });

  describe("Error Handling", () => {
    it("should propagate NotFoundException", async () => {
      mockChatService.getConversationById.mockRejectedValue(
        new NotFoundException("Conversation not found"),
      );

      await expect(
        controller.getConversation("invalid-id", mockUserId, mockReq),
      ).rejects.toThrow(NotFoundException);
    });

    it("should handle database connection errors", async () => {
      mockChatService.getUserConversations.mockRejectedValue(
        new Error("Database connection failed"),
      );

      await expect(
        controller.getUserConversations(mockUserId, mockReq),
      ).rejects.toThrow();
    });

    it("should handle validation errors", async () => {
      const invalidDto = { participantIds: [mockUserId] } as CreateConversationDto;
      mockChatService.createConversation.mockRejectedValue(
        new Error("Validation failed"),
      );

      await expect(controller.createConversation(invalidDto, mockUserId, mockReq)).rejects.toThrow();
    });
  });
});

/**
 * WebSocket Gateway Tests
 * اختبارات بوابة الاتصال الفوري
 *
 * Tests WebSocket functionality including:
 * - Client connections and disconnections
 * - Message sending/receiving via WebSocket
 * - Room management
 * - Real-time indicators (typing, online status)
 * - Read receipts
 */

import { Test, TestingModule } from "@nestjs/testing";
import { ChatGateway } from "../chat/chat.gateway";
import { ChatService } from "../chat/chat.service";
import { Socket } from "socket.io";
import * as jwt from "jsonwebtoken";

describe("WebSocket Gateway (ChatGateway)", () => {
  let gateway: ChatGateway;
  let chatService: ChatService;
  let mockSocket: Partial<Socket>;
  let mockServer: any;

  // Mock data
  const mockUserId = "user-123";
  const mockUserId2 = "user-456";
  const mockConversationId = "conv-789";
  const mockMessageId = "msg-001";
  const mockToken = "valid-jwt-token";

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
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  // Mock ChatService
  const mockChatService = {
    getConversationById: jest.fn(),
    sendMessage: jest.fn(),
    markMessageAsRead: jest.fn(),
    markConversationAsRead: jest.fn(),
    updateTypingIndicator: jest.fn(),
    updateOnlineStatus: jest.fn(),
  };

  beforeEach(async () => {
    // Mock Socket.IO server
    mockServer = {
      emit: jest.fn(),
      to: jest.fn().mockReturnThis(),
    };

    // Mock Socket client
    mockSocket = {
      id: "socket-123",
      handshake: {
        auth: { token: mockToken },
        query: {},
      } as any,
      data: {},
      emit: jest.fn(),
      join: jest.fn(),
      leave: jest.fn(),
      to: jest.fn().mockReturnThis(),
      disconnect: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ChatGateway,
        {
          provide: ChatService,
          useValue: mockChatService,
        },
      ],
    }).compile();

    gateway = module.get<ChatGateway>(ChatGateway);
    chatService = module.get<ChatService>(ChatService);

    // Assign mock server to gateway
    gateway.server = mockServer;

    // Mock JWT environment variable
    process.env.JWT_SECRET = "test-secret";

    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllMocks();
    delete process.env.JWT_SECRET;
  });

  describe("Gateway Initialization", () => {
    it("should be defined", () => {
      expect(gateway).toBeDefined();
    });

    it("should have server instance", () => {
      expect(gateway.server).toBeDefined();
    });

    it("should have chatService injected", () => {
      expect(chatService).toBeDefined();
    });
  });

  describe("Client Connection", () => {
    beforeEach(() => {
      // Mock JWT verification
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "HS256" },
      } as any);
      jest.spyOn(jwt, "verify").mockReturnValue({
        userId: mockUserId,
        sub: mockUserId,
      } as any);
      mockChatService.updateOnlineStatus.mockResolvedValue({
        userId: mockUserId,
        isOnline: true,
      });
    });

    it("should accept authenticated connection", async () => {
      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.data.userId).toBe(mockUserId);
      expect(mockChatService.updateOnlineStatus).toHaveBeenCalledWith(
        mockUserId,
        true,
      );
      expect(mockServer.emit).toHaveBeenCalledWith("user_online", {
        userId: mockUserId,
        timestamp: expect.any(Date),
      });
    });

    it("should reject unauthenticated connection", async () => {
      mockSocket.handshake!.auth = {};

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.emit).toHaveBeenCalledWith("error", {
        message: "Authentication required",
      });
      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it("should reject connection with invalid token", async () => {
      jest.spyOn(jwt, "verify").mockImplementation(() => {
        throw new Error("Invalid token");
      });

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it('should reject connection with "none" algorithm', async () => {
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "none" },
      } as any);

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.emit).toHaveBeenCalledWith("error", {
        message: "Authentication required",
      });
      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it("should reject connection with unsupported algorithm", async () => {
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "HS128" },
      } as any);

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it("should accept token from query parameter", async () => {
      mockSocket.handshake!.auth = {};
      mockSocket.handshake!.query = { token: mockToken };

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.data.userId).toBe(mockUserId);
      expect(mockChatService.updateOnlineStatus).toHaveBeenCalled();
    });

    it("should store userId in socket data", async () => {
      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.data.userId).toBe(mockUserId);
    });

    it("should handle connection errors gracefully", async () => {
      mockChatService.updateOnlineStatus.mockRejectedValue(
        new Error("Database error"),
      );

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.emit).toHaveBeenCalledWith("error", {
        message: "Connection failed",
      });
      expect(mockSocket.disconnect).toHaveBeenCalled();
    });
  });

  describe("Client Disconnection", () => {
    beforeEach(() => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.updateOnlineStatus.mockResolvedValue({
        userId: mockUserId,
        isOnline: false,
      });
    });

    it("should handle disconnection", async () => {
      await gateway.handleDisconnect(mockSocket as Socket);

      expect(mockChatService.updateOnlineStatus).toHaveBeenCalledWith(
        mockUserId,
        false,
      );
      expect(mockServer.emit).toHaveBeenCalledWith("user_offline", {
        userId: mockUserId,
        timestamp: expect.any(Date),
      });
    });

    it("should update user offline status", async () => {
      await gateway.handleDisconnect(mockSocket as Socket);

      expect(mockChatService.updateOnlineStatus).toHaveBeenCalledWith(
        mockUserId,
        false,
      );
    });

    it("should notify other users about offline status", async () => {
      await gateway.handleDisconnect(mockSocket as Socket);

      expect(mockServer.emit).toHaveBeenCalledWith(
        "user_offline",
        expect.objectContaining({
          userId: mockUserId,
        }),
      );
    });

    it("should handle disconnection without userId", async () => {
      mockSocket.data = {};

      await gateway.handleDisconnect(mockSocket as Socket);

      expect(mockChatService.updateOnlineStatus).not.toHaveBeenCalled();
    });

    it("should handle disconnection errors gracefully", async () => {
      mockChatService.updateOnlineStatus.mockRejectedValue(
        new Error("Database error"),
      );

      await expect(
        gateway.handleDisconnect(mockSocket as Socket),
      ).resolves.not.toThrow();
    });
  });

  describe("Join Conversation", () => {
    beforeEach(() => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.getConversationById.mockResolvedValue(mockConversation);
    });

    it("should allow participant to join conversation", async () => {
      const result = await gateway.handleJoinConversation(
        { conversationId: mockConversationId, userId: mockUserId },
        mockSocket as Socket,
      );

      expect(mockSocket.join).toHaveBeenCalledWith(mockConversationId);
      expect(result.event).toBe("joined_conversation");
      expect(result.data.conversationId).toBe(mockConversationId);
    });

    it("should verify user is a participant", async () => {
      await gateway.handleJoinConversation(
        { conversationId: mockConversationId, userId: mockUserId },
        mockSocket as Socket,
      );

      expect(mockChatService.getConversationById).toHaveBeenCalledWith(
        mockConversationId,
      );
    });

    it("should reject non-participant from joining", async () => {
      const unauthorizedSocket = {
        ...mockSocket,
        data: { userId: "user-999" },
      };

      const result = await gateway.handleJoinConversation(
        { conversationId: mockConversationId, userId: "user-999" },
        unauthorizedSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Access denied");
      expect(mockSocket.join).not.toHaveBeenCalled();
    });

    it("should require authentication", async () => {
      mockSocket.data = {};

      const result = await gateway.handleJoinConversation(
        { conversationId: mockConversationId, userId: mockUserId },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Authentication required");
    });

    it("should handle invalid conversation", async () => {
      mockChatService.getConversationById.mockRejectedValue(
        new Error("Conversation not found"),
      );

      const result = await gateway.handleJoinConversation(
        { conversationId: "invalid-id", userId: mockUserId },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
    });
  });

  describe("Send Message", () => {
    beforeEach(() => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.sendMessage.mockResolvedValue(mockMessage);
    });

    it("should send message successfully", async () => {
      const messageData = {
        conversationId: mockConversationId,
        senderId: mockUserId,
        content: "Hello",
        messageType: "TEXT" as any,
      };

      const result = await gateway.handleSendMessage(
        messageData,
        mockSocket as Socket,
      );

      expect(result.event).toBe("message_sent");
      expect(result.data.message).toBeDefined();
      expect(mockChatService.sendMessage).toHaveBeenCalledWith(messageData);
    });

    it("should broadcast message to conversation room", async () => {
      const messageData = {
        conversationId: mockConversationId,
        senderId: mockUserId,
        content: "Hello",
        messageType: "TEXT" as any,
      };

      await gateway.handleSendMessage(messageData, mockSocket as Socket);

      expect(mockServer.to).toHaveBeenCalledWith(mockConversationId);
      expect(mockServer.emit).toHaveBeenCalledWith("message_received", {
        message: mockMessage,
        timestamp: expect.any(Date),
      });
    });

    it("should verify authenticated userId matches senderId", async () => {
      const messageData = {
        conversationId: mockConversationId,
        senderId: "different-user",
        content: "Hello",
        messageType: "TEXT" as any,
      };

      const result = await gateway.handleSendMessage(
        messageData,
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Unauthorized");
      expect(mockChatService.sendMessage).not.toHaveBeenCalled();
    });

    it("should require authentication", async () => {
      mockSocket.data = {};

      const result = await gateway.handleSendMessage(
        {
          conversationId: mockConversationId,
          senderId: mockUserId,
          content: "Hello",
          messageType: "TEXT" as any,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Authentication required");
    });

    it("should handle send errors", async () => {
      mockChatService.sendMessage.mockRejectedValue(new Error("Send failed"));

      const result = await gateway.handleSendMessage(
        {
          conversationId: mockConversationId,
          senderId: mockUserId,
          content: "Hello",
          messageType: "TEXT" as any,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Failed to send message");
    });
  });

  describe("Typing Indicator", () => {
    beforeEach(() => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.updateTypingIndicator.mockResolvedValue({
        conversationId: mockConversationId,
        userId: mockUserId,
        isTyping: true,
      });
    });

    it("should update typing status", async () => {
      const result = await gateway.handleTyping(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          isTyping: true,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("typing_updated");
      expect(mockChatService.updateTypingIndicator).toHaveBeenCalledWith(
        mockConversationId,
        mockUserId,
        true,
      );
    });

    it("should broadcast typing indicator to other participants", async () => {
      await gateway.handleTyping(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          isTyping: true,
        },
        mockSocket as Socket,
      );

      expect(mockSocket.to).toHaveBeenCalledWith(mockConversationId);
      expect(mockSocket.emit).toHaveBeenCalledWith("typing_indicator", {
        conversationId: mockConversationId,
        userId: mockUserId,
        isTyping: true,
        timestamp: expect.any(Date),
      });
    });

    it("should handle stop typing", async () => {
      const result = await gateway.handleTyping(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          isTyping: false,
        },
        mockSocket as Socket,
      );

      expect(mockChatService.updateTypingIndicator).toHaveBeenCalledWith(
        mockConversationId,
        mockUserId,
        false,
      );
    });

    it("should require authentication", async () => {
      mockSocket.data = {};

      const result = await gateway.handleTyping(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          isTyping: true,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
    });

    it("should handle errors gracefully", async () => {
      mockChatService.updateTypingIndicator.mockRejectedValue(
        new Error("Update failed"),
      );

      const result = await gateway.handleTyping(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          isTyping: true,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
    });
  });

  describe("Read Receipt", () => {
    beforeEach(() => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.markMessageAsRead.mockResolvedValue(mockMessage);
    });

    it("should mark message as read", async () => {
      const result = await gateway.handleReadReceipt(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          messageId: mockMessageId,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("read_receipt_sent");
      expect(mockChatService.markMessageAsRead).toHaveBeenCalledWith(
        mockMessageId,
        mockUserId,
      );
    });

    it("should notify sender about read receipt", async () => {
      await gateway.handleReadReceipt(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          messageId: mockMessageId,
        },
        mockSocket as Socket,
      );

      expect(mockServer.to).toHaveBeenCalledWith(mockConversationId);
      expect(mockServer.emit).toHaveBeenCalledWith("message_read", {
        conversationId: mockConversationId,
        messageId: mockMessageId,
        userId: mockUserId,
        timestamp: expect.any(Date),
      });
    });

    it("should require authentication", async () => {
      mockSocket.data = {};

      const result = await gateway.handleReadReceipt(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          messageId: mockMessageId,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
    });

    it("should handle errors", async () => {
      mockChatService.markMessageAsRead.mockRejectedValue(
        new Error("Mark failed"),
      );

      const result = await gateway.handleReadReceipt(
        {
          conversationId: mockConversationId,
          userId: mockUserId,
          messageId: mockMessageId,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
    });
  });

  describe("Mark Conversation Read", () => {
    beforeEach(() => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.markConversationAsRead.mockResolvedValue({
        success: true,
        conversationId: mockConversationId,
      });
    });

    it("should mark conversation as read", async () => {
      const result = await gateway.handleMarkConversationRead(
        { conversationId: mockConversationId },
        mockSocket as Socket,
      );

      expect(result.event).toBe("conversation_marked_read");
      expect(mockChatService.markConversationAsRead).toHaveBeenCalledWith(
        mockConversationId,
        mockUserId,
      );
    });

    it("should notify other participants", async () => {
      await gateway.handleMarkConversationRead(
        { conversationId: mockConversationId },
        mockSocket as Socket,
      );

      expect(mockSocket.to).toHaveBeenCalledWith(mockConversationId);
      expect(mockSocket.emit).toHaveBeenCalledWith("conversation_read", {
        conversationId: mockConversationId,
        userId: mockUserId,
        timestamp: expect.any(Date),
      });
    });

    it("should require authentication", async () => {
      mockSocket.data = {};

      const result = await gateway.handleMarkConversationRead(
        { conversationId: mockConversationId },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
    });

    it("should handle errors", async () => {
      mockChatService.markConversationAsRead.mockRejectedValue(
        new Error("Mark failed"),
      );

      const result = await gateway.handleMarkConversationRead(
        { conversationId: mockConversationId },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
    });
  });

  describe("Leave Conversation", () => {
    beforeEach(() => {
      mockSocket.data = { userId: mockUserId };
    });

    it("should allow user to leave conversation", () => {
      const result = gateway.handleLeaveConversation(
        { conversationId: mockConversationId },
        mockSocket as Socket,
      );

      expect(mockSocket.leave).toHaveBeenCalledWith(mockConversationId);
      expect(result.event).toBe("left_conversation");
      expect(result.data.conversationId).toBe(mockConversationId);
    });

    it("should require authentication", () => {
      mockSocket.data = {};

      const result = gateway.handleLeaveConversation(
        { conversationId: mockConversationId },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(mockSocket.leave).not.toHaveBeenCalled();
    });
  });

  describe("User Online Status", () => {
    beforeEach(() => {
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "HS256" },
      } as any);
      jest.spyOn(jwt, "verify").mockReturnValue({
        userId: mockUserId,
      } as any);
      mockChatService.updateOnlineStatus.mockResolvedValue({
        userId: mockUserId,
        isOnline: true,
      });
    });

    it("should check if user is online", async () => {
      await gateway.handleConnection(mockSocket as Socket);

      const isOnline = gateway.isUserOnline(mockUserId);

      expect(isOnline).toBe(true);
    });

    it("should return false for offline user", () => {
      const isOnline = gateway.isUserOnline("offline-user");

      expect(isOnline).toBe(false);
    });

    it("should update online status on connection", async () => {
      await gateway.handleConnection(mockSocket as Socket);

      expect(mockChatService.updateOnlineStatus).toHaveBeenCalledWith(
        mockUserId,
        true,
      );
    });

    it("should update offline status on disconnection", async () => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.updateOnlineStatus.mockResolvedValue({
        userId: mockUserId,
        isOnline: false,
      });

      await gateway.handleDisconnect(mockSocket as Socket);

      expect(mockChatService.updateOnlineStatus).toHaveBeenCalledWith(
        mockUserId,
        false,
      );
    });
  });

  describe("Send to User", () => {
    beforeEach(() => {
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "HS256" },
      } as any);
      jest.spyOn(jwt, "verify").mockReturnValue({
        userId: mockUserId,
      } as any);
      mockChatService.updateOnlineStatus.mockResolvedValue({
        userId: mockUserId,
        isOnline: true,
      });
    });

    it("should send event to specific user", async () => {
      await gateway.handleConnection(mockSocket as Socket);

      gateway.sendToUser(mockUserId, "test_event", { data: "test" });

      expect(mockServer.to).toHaveBeenCalledWith("socket-123");
      expect(mockServer.emit).toHaveBeenCalledWith("test_event", {
        data: "test",
      });
    });

    it("should not send to offline user", () => {
      gateway.sendToUser("offline-user", "test_event", { data: "test" });

      expect(mockServer.to).not.toHaveBeenCalled();
    });

    it("should send notifications to online users", async () => {
      await gateway.handleConnection(mockSocket as Socket);

      gateway.sendToUser(mockUserId, "notification", {
        type: "new_message",
        message: "You have a new message",
      });

      expect(mockServer.emit).toHaveBeenCalledWith("notification", {
        type: "new_message",
        message: "You have a new message",
      });
    });
  });

  describe("Security and Validation", () => {
    it("should reject token without userId", async () => {
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "HS256" },
      } as any);
      jest.spyOn(jwt, "verify").mockReturnValue({} as any);

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it("should reject connection without JWT_SECRET", async () => {
      delete process.env.JWT_SECRET;

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it("should use authenticated userId from socket data", async () => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.sendMessage.mockResolvedValue(mockMessage);

      // Try to send with different senderId
      const result = await gateway.handleSendMessage(
        {
          conversationId: mockConversationId,
          senderId: "malicious-user",
          content: "Test",
          messageType: "TEXT" as any,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Unauthorized");
    });

    it("should validate algorithm from token header", async () => {
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "ES256" },
      } as any);

      await gateway.handleConnection(mockSocket as Socket);

      expect(mockSocket.disconnect).toHaveBeenCalled();
    });
  });

  describe("Memory Management", () => {
    beforeEach(() => {
      jest.spyOn(jwt, "decode").mockReturnValue({
        header: { alg: "HS256" },
      } as any);
      jest.spyOn(jwt, "verify").mockReturnValue({
        userId: mockUserId,
      } as any);
      mockChatService.updateOnlineStatus.mockResolvedValue({
        userId: mockUserId,
        isOnline: true,
      });
    });

    it("should clean up user socket map on disconnect", async () => {
      await gateway.handleConnection(mockSocket as Socket);
      expect(gateway.isUserOnline(mockUserId)).toBe(true);

      mockSocket.data = { userId: mockUserId };
      mockChatService.updateOnlineStatus.mockResolvedValue({
        userId: mockUserId,
        isOnline: false,
      });
      await gateway.handleDisconnect(mockSocket as Socket);

      expect(gateway.isUserOnline(mockUserId)).toBe(false);
    });

    it("should prevent duplicate socket entries", async () => {
      await gateway.handleConnection(mockSocket as Socket);

      const secondSocket = {
        ...mockSocket,
        id: "socket-456",
      };
      await gateway.handleConnection(secondSocket as Socket);

      // Second connection should replace first
      expect(gateway.isUserOnline(mockUserId)).toBe(true);
    });
  });

  describe("Error Messages", () => {
    it("should not expose internal errors to clients", async () => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.sendMessage.mockRejectedValue(
        new Error("Internal database connection failed on server X"),
      );

      const result = await gateway.handleSendMessage(
        {
          conversationId: mockConversationId,
          senderId: mockUserId,
          content: "Test",
          messageType: "TEXT" as any,
        },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Failed to send message");
      expect(result.data.message).not.toContain("database");
      expect(result.data.message).not.toContain("server X");
    });

    it("should provide generic error messages", async () => {
      mockSocket.data = { userId: mockUserId };
      mockChatService.getConversationById.mockRejectedValue(
        new Error("Prisma error: Connection pool exhausted"),
      );

      const result = await gateway.handleJoinConversation(
        { conversationId: mockConversationId, userId: mockUserId },
        mockSocket as Socket,
      );

      expect(result.event).toBe("error");
      expect(result.data.message).toBe("Failed to join conversation");
      expect(result.data.message).not.toContain("Prisma");
    });
  });
});

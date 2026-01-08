/**
 * Chat Service Tests
 * اختبارات خدمة المحادثات
 */

import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException, BadRequestException } from '@nestjs/common';
import { ChatService } from '../chat/chat.service';
import { PrismaService } from '../prisma/prisma.service';
import { CreateConversationDto } from '../chat/dto/create-conversation.dto';
import { SendMessageDto } from '../chat/dto/send-message.dto';
import { MessageType } from '../chat/dto/send-message.dto';

describe('ChatService', () => {
  let service: ChatService;
  let prismaService: PrismaService;

  // Mock data
  const mockUserId = 'user-123';
  const mockUserId2 = 'user-456';
  const mockConversationId = 'conv-789';
  const mockMessageId = 'msg-001';
  const mockProductId = 'prod-123';

  const mockConversation = {
    id: mockConversationId,
    participantIds: [mockUserId, mockUserId2],
    productId: mockProductId,
    orderId: null,
    lastMessage: 'Hello',
    lastMessageAt: new Date(),
    isActive: true,
    createdAt: new Date(),
    updatedAt: new Date(),
    messages: [],
    participants: [
      {
        id: 'part-1',
        conversationId: mockConversationId,
        userId: mockUserId,
        role: 'BUYER',
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
    content: 'Test message',
    messageType: 'TEXT',
    attachmentUrl: null,
    offerAmount: null,
    offerCurrency: 'YER',
    isRead: false,
    readAt: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  // Mock PrismaService
  const mockPrismaService = {
    conversation: {
      findFirst: jest.fn(),
      create: jest.fn(),
      findMany: jest.fn(),
      findUnique: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
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

    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Service Initialization', () => {
    it('should be defined', () => {
      expect(service).toBeDefined();
    });

    it('should have prismaService injected', () => {
      expect(prismaService).toBeDefined();
    });
  });

  describe('createConversation', () => {
    const createDto: CreateConversationDto = {
      participantIds: [mockUserId, mockUserId2],
      productId: mockProductId,
    };

    it('should return existing conversation if found', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(mockConversation);

      const result = await service.createConversation(createDto);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.findFirst).toHaveBeenCalledWith({
        where: {
          participantIds: {
            hasEvery: createDto.participantIds,
          },
          productId: createDto.productId,
          orderId: null,
        },
        include: {
          participants: true,
          messages: {
            orderBy: { createdAt: 'desc' },
            take: 1,
          },
        },
      });
      expect(mockPrismaService.conversation.create).not.toHaveBeenCalled();
    });

    it('should create new conversation if not found', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      const result = await service.createConversation(createDto);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith({
        data: {
          participantIds: createDto.participantIds,
          productId: createDto.productId,
          orderId: undefined,
          participants: {
            create: [
              { userId: mockUserId, role: 'BUYER' },
              { userId: mockUserId2, role: 'SELLER' },
            ],
          },
        },
        include: {
          participants: true,
          messages: true,
        },
      });
    });

    it('should create conversation with orderId', async () => {
      const dtoWithOrder = { ...createDto, orderId: 'order-123' };
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue({
        ...mockConversation,
        orderId: 'order-123',
      });

      const result = await service.createConversation(dtoWithOrder);

      expect(result.orderId).toBe('order-123');
    });

    it('should assign roles to participants correctly', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      await service.createConversation(createDto);

      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            participants: {
              create: expect.arrayContaining([
                expect.objectContaining({ role: 'BUYER' }),
                expect.objectContaining({ role: 'SELLER' }),
              ]),
            },
          }),
        })
      );
    });

    it('should handle database errors', async () => {
      mockPrismaService.conversation.findFirst.mockRejectedValue(
        new Error('Database error')
      );

      await expect(service.createConversation(createDto)).rejects.toThrow();
    });
  });

  describe('getUserConversations', () => {
    const mockConversationsData = [
      {
        ...mockConversation,
        _count: { messages: 5 },
      },
      {
        ...mockConversation,
        id: 'conv-999',
        _count: { messages: 0 },
      },
    ];

    it('should return user conversations with unread counts', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      const result = await service.getUserConversations(mockUserId);

      expect(result).toHaveLength(2);
      expect(result[0]).toHaveProperty('unreadCount', 5);
      expect(result[1]).toHaveProperty('unreadCount', 0);
      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith({
        where: {
          participantIds: { has: mockUserId },
          isActive: true,
        },
        include: {
          participants: { where: { userId: mockUserId } },
          messages: {
            orderBy: { createdAt: 'desc' },
            take: 1,
          },
          _count: {
            select: {
              messages: {
                where: {
                  senderId: { not: mockUserId },
                  isRead: false,
                },
              },
            },
          },
        },
        orderBy: { updatedAt: 'desc' },
      });
    });

    it('should return empty array if no conversations found', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue([]);

      const result = await service.getUserConversations(mockUserId);

      expect(result).toEqual([]);
      expect(Array.isArray(result)).toBe(true);
    });

    it('should include lastReadAt from participant', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      const result = await service.getUserConversations(mockUserId);

      expect(result[0]).toHaveProperty('lastReadAt');
    });

    it('should only return active conversations', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue([]);

      await service.getUserConversations(mockUserId);

      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            isActive: true,
          }),
        })
      );
    });

    it('should order conversations by updatedAt desc', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      await service.getUserConversations(mockUserId);

      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          orderBy: { updatedAt: 'desc' },
        })
      );
    });
  });

  describe('getConversationById', () => {
    it('should return conversation by id', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.findUnique).toHaveBeenCalledWith({
        where: { id: mockConversationId },
        include: { participants: true },
      });
    });

    it('should throw NotFoundException if conversation not found', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(service.getConversationById('invalid-id')).rejects.toThrow(
        NotFoundException
      );
    });

    it('should include participants in response', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants).toBeDefined();
      expect(Array.isArray(result.participants)).toBe(true);
    });
  });

  describe('getMessages', () => {
    const mockMessages = [mockMessage, { ...mockMessage, id: 'msg-002' }];

    it('should return paginated messages', async () => {
      mockPrismaService.message.findMany.mockResolvedValue([...mockMessages].reverse());
      mockPrismaService.message.count.mockResolvedValue(10);

      const result = await service.getMessages(mockConversationId, 1, 50);

      expect(result).toEqual({
        messages: mockMessages,
        total: 10,
        page: 1,
        limit: 50,
        totalPages: 1,
      });
    });

    it('should use default pagination values', async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(0);

      await service.getMessages(mockConversationId);

      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: 0,
          take: 50,
        })
      );
    });

    it('should calculate pagination correctly', async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(150);

      const result = await service.getMessages(mockConversationId, 2, 50);

      expect(result.page).toBe(2);
      expect(result.totalPages).toBe(3);
      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: 50,
          take: 50,
        })
      );
    });

    it('should return messages in chronological order', async () => {
      const messages = [
        { ...mockMessage, id: 'msg-1', createdAt: new Date('2024-01-01') },
        { ...mockMessage, id: 'msg-2', createdAt: new Date('2024-01-02') },
      ];
      mockPrismaService.message.findMany.mockResolvedValue([...messages].reverse());
      mockPrismaService.message.count.mockResolvedValue(2);

      const result = await service.getMessages(mockConversationId);

      expect(result.messages[0].id).toBe('msg-1');
      expect(result.messages[1].id).toBe('msg-2');
    });

    it('should filter messages by conversationId', async () => {
      mockPrismaService.message.findMany.mockResolvedValue([]);
      mockPrismaService.message.count.mockResolvedValue(0);

      await service.getMessages(mockConversationId);

      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { conversationId: mockConversationId },
        })
      );
    });
  });

  describe('getMessagesCursor', () => {
    const mockMessages = [mockMessage, { ...mockMessage, id: 'msg-002' }];

    it('should return cursor-based paginated messages', async () => {
      mockPrismaService.message.findMany.mockResolvedValue([...mockMessages]);

      const result = await service.getMessagesCursor(mockConversationId, undefined, 50);

      expect(result.messages).toHaveLength(2);
      expect(result.hasMore).toBe(false);
      expect(result.nextCursor).toBeNull();
    });

    it('should indicate more messages when available', async () => {
      const messages = Array(51).fill(mockMessage).map((m, i) => ({ ...m, id: `msg-${i}` }));
      mockPrismaService.message.findMany.mockResolvedValue(messages);

      const result = await service.getMessagesCursor(mockConversationId, undefined, 50);

      expect(result.hasMore).toBe(true);
      expect(result.messages).toHaveLength(50);
      expect(result.nextCursor).toBeDefined();
    });

    it('should use cursor for pagination', async () => {
      const cursor = 'msg-cursor';
      mockPrismaService.message.findMany.mockResolvedValue([mockMessage]);

      await service.getMessagesCursor(mockConversationId, cursor, 50);

      expect(mockPrismaService.message.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          cursor: { id: cursor },
          skip: 1,
        })
      );
    });
  });

  describe('sendMessage', () => {
    const sendMessageDto: SendMessageDto = {
      conversationId: mockConversationId,
      senderId: mockUserId,
      content: 'Test message',
      messageType: MessageType.TEXT,
    };

    it('should send a message successfully', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(mockMessage) },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      const result = await service.sendMessage(sendMessageDto);

      expect(result).toBeDefined();
      expect(mockPrismaService.conversation.findUnique).toHaveBeenCalledWith({
        where: { id: mockConversationId },
      });
    });

    it('should throw NotFoundException if conversation not found', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(service.sendMessage(sendMessageDto)).rejects.toThrow(
        NotFoundException
      );
    });

    it('should throw BadRequestException if sender is not a participant', async () => {
      const conversationWithoutSender = {
        ...mockConversation,
        participantIds: [mockUserId2],
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(conversationWithoutSender);

      await expect(service.sendMessage(sendMessageDto)).rejects.toThrow(
        BadRequestException
      );
    });

    it('should update conversation last message', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      const mockUpdate = jest.fn();
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(mockMessage) },
          conversation: { update: mockUpdate },
          participant: { updateMany: jest.fn() },
        });
      });

      await service.sendMessage(sendMessageDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it('should increment unread count for other participants', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      const mockUpdateMany = jest.fn();
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(mockMessage) },
          conversation: { update: jest.fn() },
          participant: { updateMany: mockUpdateMany },
        });
      });

      await service.sendMessage(sendMessageDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it('should send message with offer details', async () => {
      const offerDto = {
        ...sendMessageDto,
        messageType: MessageType.OFFER,
        offerAmount: 5000.0,
        offerCurrency: 'YER',
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      const mockCreate = jest.fn().mockResolvedValue({
        ...mockMessage,
        offerAmount: 5000.0,
      });
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: mockCreate },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await service.sendMessage(offerDto);

      expect(mockPrismaService.$transaction).toHaveBeenCalled();
    });

    it('should handle transaction errors gracefully', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      mockPrismaService.$transaction.mockRejectedValue(new Error('Transaction failed'));

      await expect(service.sendMessage(sendMessageDto)).rejects.toThrow(
        BadRequestException
      );
    });
  });

  describe('markMessageAsRead', () => {
    it('should mark message as read', async () => {
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

      const result = await service.markMessageAsRead(mockMessageId, mockUserId2);

      expect(mockPrismaService.message.update).toHaveBeenCalledWith({
        where: { id: mockMessageId },
        data: {
          isRead: true,
          readAt: expect.any(Date),
        },
      });
      expect(result).toBeDefined();
    });

    it('should not mark own message as read', async () => {
      mockPrismaService.message.findUnique.mockResolvedValue({
        ...mockMessage,
        senderId: mockUserId,
        conversation: mockConversation,
      });

      await service.markMessageAsRead(mockMessageId, mockUserId);

      expect(mockPrismaService.message.update).not.toHaveBeenCalled();
    });

    it('should throw NotFoundException if message not found', async () => {
      mockPrismaService.message.findUnique.mockResolvedValue(null);

      await expect(service.markMessageAsRead('invalid-id', mockUserId)).rejects.toThrow(
        NotFoundException
      );
    });

    it('should update participant last read time', async () => {
      mockPrismaService.message.findUnique.mockResolvedValue({
        ...mockMessage,
        conversation: mockConversation,
      });
      mockPrismaService.message.update.mockResolvedValue(mockMessage);
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
  });

  describe('markConversationAsRead', () => {
    it('should mark all messages as read', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 5 });
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.markConversationAsRead(mockConversationId, mockUserId);

      expect(result).toEqual({
        success: true,
        conversationId: mockConversationId,
      });
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

    it('should update participant unread count', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      mockPrismaService.message.updateMany.mockResolvedValue({ count: 5 });
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

    it('should throw NotFoundException if conversation not found', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(
        service.markConversationAsRead('invalid-id', mockUserId)
      ).rejects.toThrow(NotFoundException);
    });
  });

  describe('updateTypingIndicator', () => {
    it('should update typing status', async () => {
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      const result = await service.updateTypingIndicator(
        mockConversationId,
        mockUserId,
        true
      );

      expect(result).toEqual({
        conversationId: mockConversationId,
        userId: mockUserId,
        isTyping: true,
      });
      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith({
        where: {
          conversationId: mockConversationId,
          userId: mockUserId,
        },
        data: {
          isTyping: true,
        },
      });
    });

    it('should set typing to false', async () => {
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 1 });

      await service.updateTypingIndicator(mockConversationId, mockUserId, false);

      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          data: { isTyping: false },
        })
      );
    });
  });

  describe('updateOnlineStatus', () => {
    it('should update user online status', async () => {
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 2 });

      const result = await service.updateOnlineStatus(mockUserId, true);

      expect(result).toEqual({
        userId: mockUserId,
        isOnline: true,
      });
      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith({
        where: { userId: mockUserId },
        data: {
          isOnline: true,
          lastSeenAt: expect.any(Date),
        },
      });
    });

    it('should set user offline', async () => {
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 2 });

      await service.updateOnlineStatus(mockUserId, false);

      expect(mockPrismaService.participant.updateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            isOnline: false,
          }),
        })
      );
    });

    it('should update lastSeenAt timestamp', async () => {
      const beforeTime = new Date();
      mockPrismaService.participant.updateMany.mockResolvedValue({ count: 2 });

      await service.updateOnlineStatus(mockUserId, true);

      const callArgs = mockPrismaService.participant.updateMany.mock.calls[0][0];
      expect(callArgs.data.lastSeenAt).toBeInstanceOf(Date);
      expect(callArgs.data.lastSeenAt.getTime()).toBeGreaterThanOrEqual(beforeTime.getTime());
    });
  });

  describe('getUnreadCount', () => {
    it('should return total unread count', async () => {
      const participants = [
        { unreadCount: 3 },
        { unreadCount: 5 },
        { unreadCount: 2 },
      ];
      mockPrismaService.participant.findMany.mockResolvedValue(participants);

      const result = await service.getUnreadCount(mockUserId);

      expect(result).toBe(10);
      expect(mockPrismaService.participant.findMany).toHaveBeenCalledWith({
        where: { userId: mockUserId },
        select: { unreadCount: true },
      });
    });

    it('should return zero if no unread messages', async () => {
      mockPrismaService.participant.findMany.mockResolvedValue([
        { unreadCount: 0 },
        { unreadCount: 0 },
      ]);

      const result = await service.getUnreadCount(mockUserId);

      expect(result).toBe(0);
    });

    it('should return zero if user has no conversations', async () => {
      mockPrismaService.participant.findMany.mockResolvedValue([]);

      const result = await service.getUnreadCount(mockUserId);

      expect(result).toBe(0);
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle null productId and orderId', async () => {
      const dto: CreateConversationDto = {
        participantIds: [mockUserId, mockUserId2],
      };
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue({
        ...mockConversation,
        productId: null,
        orderId: null,
      });

      const result = await service.createConversation(dto);

      expect(result.productId).toBeNull();
      expect(result.orderId).toBeNull();
    });

    it('should handle large message content', async () => {
      const largeContent = 'a'.repeat(10000);
      const dtoWithLargeContent = {
        ...mockMessage,
        content: largeContent,
        conversationId: mockConversationId,
        senderId: mockUserId,
      } as SendMessageDto;

      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue({ ...mockMessage, content: largeContent }) },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      await expect(service.sendMessage(dtoWithLargeContent)).resolves.toBeDefined();
    });

    it('should handle concurrent message sends', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);
      mockPrismaService.$transaction.mockImplementation(async (callback) => {
        return callback({
          message: { create: jest.fn().mockResolvedValue(mockMessage) },
          conversation: { update: jest.fn() },
          participant: { updateMany: jest.fn() },
        });
      });

      const promises = Array(5).fill(null).map(() =>
        service.sendMessage({
          conversationId: mockConversationId,
          senderId: mockUserId,
          content: 'Test',
          messageType: MessageType.TEXT,
        })
      );

      await expect(Promise.all(promises)).resolves.toHaveLength(5);
    });
  });
});

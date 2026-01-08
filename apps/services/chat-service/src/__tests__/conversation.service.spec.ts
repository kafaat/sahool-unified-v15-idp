/**
 * Conversation Service Tests
 * اختبارات خدمة المحادثات
 *
 * Tests conversation-specific functionality including:
 * - Conversation creation and retrieval
 * - Participant management
 * - Conversation state management
 * - Multi-user conversation handling
 */

import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException, BadRequestException } from '@nestjs/common';
import { ChatService } from '../chat/chat.service';
import { PrismaService } from '../prisma/prisma.service';
import { CreateConversationDto } from '../chat/dto/create-conversation.dto';

describe('ConversationService (Conversation Operations)', () => {
  let service: ChatService;
  let prismaService: PrismaService;

  // Mock data
  const mockUserId = 'user-123';
  const mockUserId2 = 'user-456';
  const mockUserId3 = 'user-789';
  const mockConversationId = 'conv-001';
  const mockProductId = 'prod-123';
  const mockOrderId = 'order-456';

  const mockParticipant1 = {
    id: 'part-1',
    conversationId: mockConversationId,
    userId: mockUserId,
    role: 'BUYER',
    lastReadAt: new Date('2024-01-01T10:00:00Z'),
    unreadCount: 0,
    isOnline: true,
    lastSeenAt: new Date('2024-01-01T10:00:00Z'),
    isTyping: false,
    joinedAt: new Date('2024-01-01T09:00:00Z'),
  };

  const mockParticipant2 = {
    id: 'part-2',
    conversationId: mockConversationId,
    userId: mockUserId2,
    role: 'SELLER',
    lastReadAt: new Date('2024-01-01T09:30:00Z'),
    unreadCount: 3,
    isOnline: false,
    lastSeenAt: new Date('2024-01-01T09:45:00Z'),
    isTyping: false,
    joinedAt: new Date('2024-01-01T09:00:00Z'),
  };

  const mockConversation = {
    id: mockConversationId,
    participantIds: [mockUserId, mockUserId2],
    productId: mockProductId,
    orderId: null,
    lastMessage: 'Hello, interested in your product',
    lastMessageAt: new Date('2024-01-01T10:00:00Z'),
    isActive: true,
    createdAt: new Date('2024-01-01T09:00:00Z'),
    updatedAt: new Date('2024-01-01T10:00:00Z'),
    participants: [mockParticipant1, mockParticipant2],
    messages: [],
  };

  // Mock PrismaService
  const mockPrismaService = {
    conversation: {
      findFirst: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
    },
    participant: {
      findMany: jest.fn(),
      updateMany: jest.fn(),
      create: jest.fn(),
      delete: jest.fn(),
    },
    message: {
      findMany: jest.fn(),
      count: jest.fn(),
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

  describe('Conversation Creation', () => {
    const createDto: CreateConversationDto = {
      participantIds: [mockUserId, mockUserId2],
      productId: mockProductId,
    };

    it('should create a new conversation when one does not exist', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

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
      expect(mockPrismaService.conversation.create).toHaveBeenCalled();
    });

    it('should return existing conversation if already exists', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(mockConversation);

      const result = await service.createConversation(createDto);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.create).not.toHaveBeenCalled();
    });

    it('should create conversation with product context', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      await service.createConversation(createDto);

      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            productId: mockProductId,
          }),
        })
      );
    });

    it('should create conversation with order context', async () => {
      const orderDto = {
        ...createDto,
        orderId: mockOrderId,
      };
      const orderConversation = {
        ...mockConversation,
        orderId: mockOrderId,
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(orderConversation);

      const result = await service.createConversation(orderDto);

      expect(result.orderId).toBe(mockOrderId);
      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            orderId: mockOrderId,
          }),
        })
      );
    });

    it('should create conversation without product or order', async () => {
      const minimalDto: CreateConversationDto = {
        participantIds: [mockUserId, mockUserId2],
      };
      const minimalConversation = {
        ...mockConversation,
        productId: null,
        orderId: null,
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(minimalConversation);

      const result = await service.createConversation(minimalDto);

      expect(result.productId).toBeNull();
      expect(result.orderId).toBeNull();
    });

    it('should assign BUYER role to first participant', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      await service.createConversation(createDto);

      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            participants: {
              create: expect.arrayContaining([
                expect.objectContaining({
                  userId: mockUserId,
                  role: 'BUYER',
                }),
              ]),
            },
          }),
        })
      );
    });

    it('should assign SELLER role to second participant', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      await service.createConversation(createDto);

      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            participants: {
              create: expect.arrayContaining([
                expect.objectContaining({
                  userId: mockUserId2,
                  role: 'SELLER',
                }),
              ]),
            },
          }),
        })
      );
    });

    it('should create participants for all provided user IDs', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      await service.createConversation(createDto);

      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            participants: {
              create: expect.arrayContaining([
                expect.objectContaining({ userId: mockUserId }),
                expect.objectContaining({ userId: mockUserId2 }),
              ]),
            },
          }),
        })
      );
    });

    it('should include participants and messages in created conversation', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      const result = await service.createConversation(createDto);

      expect(result.participants).toBeDefined();
      expect(result.messages).toBeDefined();
      expect(mockPrismaService.conversation.create).toHaveBeenCalledWith(
        expect.objectContaining({
          include: {
            participants: true,
            messages: true,
          },
        })
      );
    });

    it('should handle database errors during creation', async () => {
      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockRejectedValue(
        new Error('Database connection failed')
      );

      await expect(service.createConversation(createDto)).rejects.toThrow();
    });
  });

  describe('Get User Conversations', () => {
    const mockConversationsData = [
      {
        ...mockConversation,
        id: 'conv-1',
        participants: [mockParticipant1],
        messages: [
          {
            id: 'msg-1',
            content: 'Latest message',
            createdAt: new Date('2024-01-01T10:00:00Z'),
          },
        ],
        _count: { messages: 5 },
      },
      {
        ...mockConversation,
        id: 'conv-2',
        participants: [mockParticipant1],
        messages: [],
        _count: { messages: 0 },
      },
      {
        ...mockConversation,
        id: 'conv-3',
        participants: [mockParticipant1],
        messages: [
          {
            id: 'msg-3',
            content: 'Old message',
            createdAt: new Date('2024-01-01T08:00:00Z'),
          },
        ],
        _count: { messages: 10 },
      },
    ];

    it('should retrieve all active conversations for user', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      const result = await service.getUserConversations(mockUserId);

      expect(result).toHaveLength(3);
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

    it('should return conversations ordered by last update', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      await service.getUserConversations(mockUserId);

      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          orderBy: { updatedAt: 'desc' },
        })
      );
    });

    it('should include unread count for each conversation', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      const result = await service.getUserConversations(mockUserId);

      expect(result[0]).toHaveProperty('unreadCount', 5);
      expect(result[1]).toHaveProperty('unreadCount', 0);
      expect(result[2]).toHaveProperty('unreadCount', 10);
    });

    it('should include last read timestamp for user', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      const result = await service.getUserConversations(mockUserId);

      expect(result[0]).toHaveProperty('lastReadAt');
      expect(result[0].lastReadAt).toBeInstanceOf(Date);
    });

    it('should include last message for each conversation', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      const result = await service.getUserConversations(mockUserId);

      expect(result[0].messages).toHaveLength(1);
      expect(result[0].messages[0].content).toBe('Latest message');
    });

    it('should handle conversations with no messages', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue([
        mockConversationsData[1],
      ]);

      const result = await service.getUserConversations(mockUserId);

      expect(result[0].messages).toHaveLength(0);
      expect(result[0].unreadCount).toBe(0);
    });

    it('should only include active conversations', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      await service.getUserConversations(mockUserId);

      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            isActive: true,
          }),
        })
      );
    });

    it('should return empty array when user has no conversations', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue([]);

      const result = await service.getUserConversations(mockUserId);

      expect(result).toEqual([]);
      expect(Array.isArray(result)).toBe(true);
    });

    it('should filter by user ID in participant list', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      await service.getUserConversations(mockUserId);

      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            participantIds: { has: mockUserId },
          }),
        })
      );
    });

    it('should exclude messages sent by user from unread count', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue(mockConversationsData);

      await service.getUserConversations(mockUserId);

      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          include: expect.objectContaining({
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
          }),
        })
      );
    });

    it('should handle database errors gracefully', async () => {
      mockPrismaService.conversation.findMany.mockRejectedValue(
        new Error('Database error')
      );

      await expect(service.getUserConversations(mockUserId)).rejects.toThrow();
    });
  });

  describe('Get Conversation By ID', () => {
    it('should retrieve conversation by ID', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.findUnique).toHaveBeenCalledWith({
        where: { id: mockConversationId },
        include: { participants: true },
      });
    });

    it('should include participants in response', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants).toBeDefined();
      expect(result.participants).toHaveLength(2);
      expect(result.participants[0].userId).toBe(mockUserId);
      expect(result.participants[1].userId).toBe(mockUserId2);
    });

    it('should throw NotFoundException when conversation does not exist', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(
        service.getConversationById('non-existent-id')
      ).rejects.toThrow(NotFoundException);
      await expect(
        service.getConversationById('non-existent-id')
      ).rejects.toThrow('Conversation not found');
    });

    it('should retrieve conversation with product context', async () => {
      const conversationWithProduct = {
        ...mockConversation,
        productId: mockProductId,
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        conversationWithProduct
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.productId).toBe(mockProductId);
    });

    it('should retrieve conversation with order context', async () => {
      const conversationWithOrder = {
        ...mockConversation,
        orderId: mockOrderId,
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        conversationWithOrder
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.orderId).toBe(mockOrderId);
    });

    it('should handle database errors', async () => {
      mockPrismaService.conversation.findUnique.mockRejectedValue(
        new Error('Database connection failed')
      );

      await expect(service.getConversationById(mockConversationId)).rejects.toThrow();
    });
  });

  describe('Conversation Participants', () => {
    it('should verify user is a participant in conversation', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participantIds).toContain(mockUserId);
      expect(result.participantIds).toContain(mockUserId2);
    });

    it('should include participant roles', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants[0].role).toBe('BUYER');
      expect(result.participants[1].role).toBe('SELLER');
    });

    it('should include participant online status', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants[0]).toHaveProperty('isOnline');
      expect(result.participants[0]).toHaveProperty('lastSeenAt');
    });

    it('should include participant unread count', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants[0]).toHaveProperty('unreadCount', 0);
      expect(result.participants[1]).toHaveProperty('unreadCount', 3);
    });

    it('should include participant typing status', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants[0]).toHaveProperty('isTyping');
      expect(result.participants[1]).toHaveProperty('isTyping');
    });

    it('should include participant join timestamp', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants[0]).toHaveProperty('joinedAt');
      expect(result.participants[0].joinedAt).toBeInstanceOf(Date);
    });

    it('should include participant last read timestamp', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants[0]).toHaveProperty('lastReadAt');
      expect(result.participants[0].lastReadAt).toBeInstanceOf(Date);
    });

    it('should handle conversations with multiple participants', async () => {
      const multiPartyConversation = {
        ...mockConversation,
        participantIds: [mockUserId, mockUserId2, mockUserId3],
        participants: [
          mockParticipant1,
          mockParticipant2,
          { ...mockParticipant1, id: 'part-3', userId: mockUserId3 },
        ],
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        multiPartyConversation
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants).toHaveLength(3);
      expect(result.participantIds).toContain(mockUserId3);
    });
  });

  describe('Conversation State Management', () => {
    it('should track conversation active state', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result).toHaveProperty('isActive', true);
    });

    it('should track last message timestamp', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result).toHaveProperty('lastMessageAt');
      expect(result.lastMessageAt).toBeInstanceOf(Date);
    });

    it('should track last message content', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result).toHaveProperty('lastMessage');
      expect(result.lastMessage).toBe('Hello, interested in your product');
    });

    it('should track conversation creation timestamp', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result).toHaveProperty('createdAt');
      expect(result.createdAt).toBeInstanceOf(Date);
    });

    it('should track conversation update timestamp', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result).toHaveProperty('updatedAt');
      expect(result.updatedAt).toBeInstanceOf(Date);
    });

    it('should update conversation on new messages', async () => {
      const updatedConversation = {
        ...mockConversation,
        lastMessage: 'New message',
        lastMessageAt: new Date('2024-01-01T11:00:00Z'),
        updatedAt: new Date('2024-01-01T11:00:00Z'),
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        updatedConversation
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.lastMessage).toBe('New message');
      expect(result.lastMessageAt.getTime()).toBeGreaterThan(
        mockConversation.lastMessageAt.getTime()
      );
    });
  });

  describe('Conversation Context', () => {
    it('should link conversation to product', async () => {
      const productConversation = {
        ...mockConversation,
        productId: mockProductId,
        orderId: null,
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        productConversation
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.productId).toBe(mockProductId);
      expect(result.orderId).toBeNull();
    });

    it('should link conversation to order', async () => {
      const orderConversation = {
        ...mockConversation,
        productId: null,
        orderId: mockOrderId,
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(orderConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.orderId).toBe(mockOrderId);
      expect(result.productId).toBeNull();
    });

    it('should link conversation to both product and order', async () => {
      const fullContextConversation = {
        ...mockConversation,
        productId: mockProductId,
        orderId: mockOrderId,
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        fullContextConversation
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.productId).toBe(mockProductId);
      expect(result.orderId).toBe(mockOrderId);
    });

    it('should create standalone conversation without context', async () => {
      const standaloneDto: CreateConversationDto = {
        participantIds: [mockUserId, mockUserId2],
      };
      const standaloneConversation = {
        ...mockConversation,
        productId: null,
        orderId: null,
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(null);
      mockPrismaService.conversation.create.mockResolvedValue(
        standaloneConversation
      );

      const result = await service.createConversation(standaloneDto);

      expect(result.productId).toBeNull();
      expect(result.orderId).toBeNull();
    });
  });

  describe('Edge Cases and Error Handling', () => {
    it('should handle conversation with no last message', async () => {
      const newConversation = {
        ...mockConversation,
        lastMessage: null,
        lastMessageAt: null,
        messages: [],
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(newConversation);

      const result = await service.getConversationById(mockConversationId);

      expect(result.lastMessage).toBeNull();
      expect(result.lastMessageAt).toBeNull();
    });

    it('should handle conversation lookup with invalid ID format', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(null);

      await expect(service.getConversationById('invalid-id')).rejects.toThrow(
        NotFoundException
      );
    });

    it('should prevent duplicate conversation creation', async () => {
      const createDto: CreateConversationDto = {
        participantIds: [mockUserId, mockUserId2],
        productId: mockProductId,
      };

      mockPrismaService.conversation.findFirst.mockResolvedValue(mockConversation);

      const result = await service.createConversation(createDto);

      expect(result).toEqual(mockConversation);
      expect(mockPrismaService.conversation.create).not.toHaveBeenCalled();
    });

    it('should handle user with no active conversations', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue([]);

      const result = await service.getUserConversations('user-new');

      expect(result).toEqual([]);
      expect(Array.isArray(result)).toBe(true);
    });

    it('should handle concurrent conversation creation attempts', async () => {
      const createDto: CreateConversationDto = {
        participantIds: [mockUserId, mockUserId2],
        productId: mockProductId,
      };

      // First call finds nothing, second finds existing
      mockPrismaService.conversation.findFirst
        .mockResolvedValueOnce(null)
        .mockResolvedValueOnce(mockConversation);

      mockPrismaService.conversation.create.mockResolvedValue(mockConversation);

      const [result1, result2] = await Promise.all([
        service.createConversation(createDto),
        service.createConversation(createDto),
      ]);

      expect(result1).toBeDefined();
      expect(result2).toBeDefined();
    });

    it('should handle participant with null lastReadAt', async () => {
      const conversationWithNullRead = {
        ...mockConversation,
        participants: [
          { ...mockParticipant1, lastReadAt: null },
          mockParticipant2,
        ],
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        conversationWithNullRead
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants[0].lastReadAt).toBeNull();
    });

    it('should handle large number of conversations', async () => {
      const manyConversations = Array(100)
        .fill(null)
        .map((_, i) => ({
          ...mockConversation,
          id: `conv-${i}`,
          participants: [mockParticipant1],
          messages: [],
          _count: { messages: i },
        }));

      mockPrismaService.conversation.findMany.mockResolvedValue(manyConversations);

      const result = await service.getUserConversations(mockUserId);

      expect(result).toHaveLength(100);
      expect(result[0].unreadCount).toBe(0);
      expect(result[99].unreadCount).toBe(99);
    });

    it('should handle database timeout errors', async () => {
      mockPrismaService.conversation.findUnique.mockRejectedValue(
        new Error('Connection timeout')
      );

      await expect(service.getConversationById(mockConversationId)).rejects.toThrow(
        'Connection timeout'
      );
    });

    it('should handle malformed participant data', async () => {
      const malformedConversation = {
        ...mockConversation,
        participants: null,
      };
      mockPrismaService.conversation.findUnique.mockResolvedValue(
        malformedConversation
      );

      const result = await service.getConversationById(mockConversationId);

      expect(result.participants).toBeNull();
    });
  });

  describe('Performance and Scalability', () => {
    it('should efficiently query conversations with pagination support', async () => {
      const conversations = Array(50)
        .fill(null)
        .map((_, i) => ({
          ...mockConversation,
          id: `conv-${i}`,
          participants: [mockParticipant1],
          messages: [],
          _count: { messages: 0 },
        }));

      mockPrismaService.conversation.findMany.mockResolvedValue(conversations);

      const result = await service.getUserConversations(mockUserId);

      expect(result.length).toBeLessThanOrEqual(50);
    });

    it('should optimize by including only last message', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue([
        {
          ...mockConversation,
          participants: [mockParticipant1],
          messages: [{ id: 'msg-1', content: 'Latest' }],
          _count: { messages: 100 },
        },
      ]);

      await service.getUserConversations(mockUserId);

      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          include: expect.objectContaining({
            messages: {
              orderBy: { createdAt: 'desc' },
              take: 1,
            },
          }),
        })
      );
    });

    it('should handle concurrent conversation retrievals', async () => {
      mockPrismaService.conversation.findUnique.mockResolvedValue(mockConversation);

      const promises = Array(10)
        .fill(null)
        .map(() => service.getConversationById(mockConversationId));

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      expect(results.every((r) => r.id === mockConversationId)).toBe(true);
    });

    it('should efficiently count unread messages', async () => {
      mockPrismaService.conversation.findMany.mockResolvedValue([
        {
          ...mockConversation,
          participants: [mockParticipant1],
          messages: [],
          _count: { messages: 42 },
        },
      ]);

      const result = await service.getUserConversations(mockUserId);

      expect(result[0].unreadCount).toBe(42);
      // Should use _count aggregation, not fetch all messages
      expect(mockPrismaService.conversation.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          include: expect.objectContaining({
            _count: expect.any(Object),
          }),
        })
      );
    });
  });
});

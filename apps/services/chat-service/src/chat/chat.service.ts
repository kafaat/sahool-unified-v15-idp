/**
 * Chat Service
 * خدمة المحادثات - منطق الأعمال
 */

import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CreateConversationDto } from "./dto/create-conversation.dto";
import { SendMessageDto } from "./dto/send-message.dto";
import {
  GENERAL_TRANSACTION_CONFIG,
  READ_TRANSACTION_CONFIG,
} from "../utils/db-utils";

// Define ParticipantRole locally to avoid Prisma client generation dependency
type ParticipantRole = "BUYER" | "SELLER" | "ADMIN";

@Injectable()
export class ChatService {
  constructor(private prisma: PrismaService) {}

  /**
   * Create a new conversation
   * إنشاء محادثة جديدة
   */
  async createConversation(dto: CreateConversationDto, tenantId: string) {
    // Check if conversation already exists between these participants
    const existingConversation = await this.prisma.conversation.findFirst({
      where: {
        tenantId,
        participantIds: {
          hasEvery: dto.participantIds,
        },
        productId: dto.productId || null,
        orderId: dto.orderId || null,
      },
      include: {
        participants: true,
        messages: {
          orderBy: { createdAt: "desc" },
          take: 1,
        },
      },
    });

    if (existingConversation) {
      return existingConversation;
    }

    // Create new conversation
    const conversation = await this.prisma.conversation.create({
      data: {
        tenantId,
        participantIds: dto.participantIds,
        productId: dto.productId,
        orderId: dto.orderId,
        participants: {
          create: dto.participantIds.map((userId, index) => ({
            tenantId,
            userId,
            role: index === 0 ? "BUYER" : "SELLER",
          })),
        },
      },
      include: {
        participants: true,
        messages: true,
      },
    });

    return conversation;
  }

  /**
   * Get user's conversations
   * الحصول على محادثات المستخدم
   */
  async getUserConversations(userId: string, tenantId: string) {
    const conversations = await this.prisma.conversation.findMany({
      where: {
        tenantId,
        participantIds: {
          has: userId,
        },
        isActive: true,
      },
      take: 100,
      include: {
        participants: {
          where: {
            userId,
          },
        },
        messages: {
          orderBy: { createdAt: "desc" },
          take: 1,
        },
        _count: {
          select: {
            messages: {
              where: {
                senderId: { not: userId },
                isRead: false,
              },
            },
          },
        },
      },
      orderBy: {
        updatedAt: "desc",
      },
    });

    // Map conversations with unread count from _count
    const conversationsWithUnread = conversations.map((conv: any) => {
      const participant = conv.participants[0];
      const { _count, ...conversationData } = conv;

      return {
        ...conversationData,
        unreadCount: _count.messages,
        lastReadAt: participant?.lastReadAt,
      };
    });

    return conversationsWithUnread;
  }

  /**
   * Get conversation by ID
   * الحصول على محادثة بواسطة المعرف
   */
  async getConversationById(conversationId: string, tenantId: string) {
    const conversation = await this.prisma.conversation.findFirst({
      where: { id: conversationId, tenantId },
      include: {
        participants: true,
      },
    });

    if (!conversation) {
      throw new NotFoundException("Conversation not found");
    }

    return conversation;
  }

  /**
   * Get messages for a conversation with pagination
   * الحصول على رسائل المحادثة مع الترقيم
   */
  async getMessages(
    conversationId: string,
    page: number = 1,
    limit: number = 50,
    tenantId: string,
  ) {
    const skip = (page - 1) * limit;

    const [messages, total] = await Promise.all([
      this.prisma.message.findMany({
        where: { conversationId, tenantId },
        orderBy: { createdAt: "desc" },
        skip,
        take: limit,
      }),
      this.prisma.message.count({
        where: { conversationId, tenantId },
      }),
    ]);

    return {
      messages: messages.reverse(), // Return in chronological order
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit),
    };
  }

  /**
   * Get messages with cursor-based pagination (optimized for large datasets)
   * الحصول على الرسائل مع ترقيم مبني على المؤشر (محسّن للبيانات الكبيرة)
   */
  async getMessagesCursor(
    conversationId: string,
    tenantId: string,
    cursor?: string,
    limit: number = 50,
  ) {
    const messages = await this.prisma.message.findMany({
      where: { conversationId, tenantId },
      orderBy: { createdAt: "desc" },
      take: limit + 1, // Fetch one extra to determine if there are more
      ...(cursor && {
        cursor: { id: cursor },
        skip: 1, // Skip the cursor itself
      }),
    });

    const hasMore = messages.length > limit;
    const results = hasMore ? messages.slice(0, limit) : messages;
    const nextCursor = hasMore ? results[results.length - 1].id : null;

    return {
      messages: results.reverse(), // Return in chronological order
      nextCursor,
      hasMore,
    };
  }

  /**
   * Send a message
   * إرسال رسالة
   */
  async sendMessage(dto: SendMessageDto, tenantId: string) {
    try {
      // Verify conversation exists within tenant
      const conversation = await this.prisma.conversation.findFirst({
        where: { id: dto.conversationId, tenantId },
      });

      if (!conversation) {
        throw new NotFoundException("Conversation not found");
      }

      // Verify sender is a participant
      if (!conversation.participantIds.includes(dto.senderId)) {
        throw new BadRequestException(
          "User is not a participant in this conversation",
        );
      }

      // Use transaction with timeout to ensure atomicity
      const message = await this.prisma.$transaction(async (tx) => {
        // Create message
        const newMessage = await tx.message.create({
          data: {
            tenantId,
            conversationId: dto.conversationId,
            senderId: dto.senderId,
            content: dto.content,
            messageType: dto.messageType || "TEXT",
            attachmentUrl: dto.attachmentUrl,
            offerAmount: dto.offerAmount,
            offerCurrency: dto.offerCurrency || "YER",
          },
        });

        // Update conversation's last message
        await tx.conversation.update({
          where: { id: dto.conversationId },
          data: {
            lastMessage: dto.content,
            lastMessageAt: new Date(),
            updatedAt: new Date(),
          },
        });

        // Update unread count for other participants
        await tx.participant.updateMany({
          where: {
            conversationId: dto.conversationId,
            userId: { not: dto.senderId },
          },
          data: {
            unreadCount: { increment: 1 },
          },
        });

        return newMessage;
      }, GENERAL_TRANSACTION_CONFIG);

      return message;
    } catch (error) {
      // Sanitize error messages - don't expose internal details
      if (
        error instanceof NotFoundException ||
        error instanceof BadRequestException
      ) {
        throw error;
      }
      throw new BadRequestException("Failed to send message");
    }
  }

  /**
   * Mark message as read
   * تحديد الرسالة كمقروءة
   */
  async markMessageAsRead(messageId: string, userId: string, tenantId: string) {
    const message = await this.prisma.message.findFirst({
      where: { id: messageId, tenantId },
      include: { conversation: true },
    });

    if (!message) {
      throw new NotFoundException("Message not found");
    }

    // Only mark as read if user is not the sender
    if (message.senderId !== userId) {
      await this.prisma.message.update({
        where: { id: messageId },
        data: {
          isRead: true,
          readAt: new Date(),
        },
      });

      // Update participant's last read time and reset unread count
      await this.prisma.participant.updateMany({
        where: {
          conversationId: message.conversationId,
          userId,
        },
        data: {
          lastReadAt: new Date(),
          unreadCount: 0,
        },
      });
    }

    return message;
  }

  /**
   * Mark all messages in conversation as read
   * تحديد جميع الرسائل في المحادثة كمقروءة
   */
  async markConversationAsRead(conversationId: string, userId: string, tenantId: string) {
    const conversation = await this.getConversationById(conversationId, tenantId);

    // Update all unread messages
    await this.prisma.message.updateMany({
      where: {
        tenantId,
        conversationId,
        senderId: { not: userId },
        isRead: false,
      },
      data: {
        isRead: true,
        readAt: new Date(),
      },
    });

    // Update participant's last read time and reset unread count
    await this.prisma.participant.updateMany({
      where: {
        tenantId,
        conversationId,
        userId,
      },
      data: {
        lastReadAt: new Date(),
        unreadCount: 0,
      },
    });

    return { success: true, conversationId };
  }

  /**
   * Update typing indicator
   * تحديث مؤشر الكتابة
   */
  async updateTypingIndicator(
    conversationId: string,
    userId: string,
    isTyping: boolean,
    tenantId: string,
  ) {
    await this.prisma.participant.updateMany({
      where: {
        tenantId,
        conversationId,
        userId,
      },
      data: {
        isTyping,
      },
    });

    return { conversationId, userId, isTyping };
  }

  /**
   * Update user online status
   * تحديث حالة الاتصال
   */
  async updateOnlineStatus(userId: string, isOnline: boolean, tenantId: string) {
    await this.prisma.participant.updateMany({
      where: { userId, tenantId },
      data: {
        isOnline,
        lastSeenAt: new Date(),
      },
    });

    return { userId, isOnline };
  }

  /**
   * Get unread message count for user
   * الحصول على عدد الرسائل غير المقروءة للمستخدم
   */
  async getUnreadCount(userId: string, tenantId: string): Promise<number> {
    const participants = await this.prisma.participant.findMany({
      where: { userId, tenantId },
      select: { unreadCount: true },
      take: 500,
    });

    return participants.reduce((total: number, p: { unreadCount: number }) => total + p.unreadCount, 0);
  }
}

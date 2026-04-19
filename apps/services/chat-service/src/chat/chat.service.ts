/**
 * Chat Service
 * خدمة المحادثات - منطق الأعمال
 */

import {
  Injectable,
  NotFoundException,
  BadRequestException,
  ForbiddenException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { ChatEventsService } from "../events/chat-events.service";
import { CreateConversationDto } from "./dto/create-conversation.dto";
import { SendMessageDto } from "./dto/send-message.dto";
import {
  GENERAL_TRANSACTION_CONFIG,
  READ_TRANSACTION_CONFIG,
} from "../utils/db-utils";

// Define ParticipantRole locally to avoid Prisma client generation dependency
type ParticipantRole = "BUYER" | "SELLER" | "ADMIN";

/** Max chars of message content emitted on the event bus — avoid
 *  leaking full message bodies across services. */
const MESSAGE_PREVIEW_MAX_LEN = 200;

@Injectable()
export class ChatService {
  constructor(
    private prisma: PrismaService,
    private events: ChatEventsService,
  ) {}

  /**
   * Create a new conversation
   * إنشاء محادثة جديدة
   */
  async createConversation(dto: CreateConversationDto, tenantId: string) {
    // Scope handling — if the caller gave us (scopeType, scopeId), prefer
    // that as the uniqueness key (matches field-chat semantics: one thread
    // per field/task/incident). Otherwise fall back to the marketplace
    // (productId, orderId) de-dup.
    //
    // Security: the scope-dedupe path also requires `hasEvery: participantIds`
    // so a tenant user who guesses a scopeId cannot read back an existing
    // scoped conversation they're not part of (which would leak the most
    // recent message body via the `messages` include). Callers must include
    // their own userId in dto.participantIds — enforced by the controller
    // which overrides participantIds[0] with the authenticated user.
    const hasScope = !!(dto.scopeType && dto.scopeId);
    const existingConversation = await this.prisma.conversation.findFirst({
      where: hasScope
        ? {
            tenantId,
            scopeType: dto.scopeType!,
            scopeId: dto.scopeId!,
            participantIds: {
              hasEvery: dto.participantIds,
            },
          }
        : {
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

    // Create new conversation — scopeType/scopeId are nullable in the
    // schema, so omitting them keeps marketplace flows unchanged while
    // field-chat style calls now persist their domain anchor.
    //
    // If a scoped conversation already exists for (tenantId, scopeType,
    // scopeId) but the caller isn't in its participants, the unique index
    // `uq_conversation_scope` will fire on insert (Prisma P2002). Translate
    // that to a ForbiddenException rather than a 500 — it means the caller
    // tried to "create" a scope that already exists without access.
    try {
      const conversation = await this.prisma.conversation.create({
        data: {
          tenantId,
          participantIds: dto.participantIds,
          productId: dto.productId,
          orderId: dto.orderId,
          scopeType: dto.scopeType,
          scopeId: dto.scopeId,
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
    } catch (e: any) {
      if (e?.code === "P2002") {
        throw new ForbiddenException(
          "A conversation with this scope already exists and you are not a participant",
        );
      }
      throw e;
    }
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

        // Update conversation's last message (tenant-scoped)
        await tx.conversation.updateMany({
          where: { id: dto.conversationId, tenantId },
          data: {
            lastMessage: dto.content,
            lastMessageAt: new Date(),
            updatedAt: new Date(),
          },
        });

        // Update unread count for other participants (tenant-scoped)
        await tx.participant.updateMany({
          where: {
            tenantId,
            conversationId: dto.conversationId,
            userId: { not: dto.senderId },
          },
          data: {
            unreadCount: { increment: 1 },
          },
        });

        return newMessage;
      }, GENERAL_TRANSACTION_CONFIG);

      // Fan-out push notifications via NATS. Fire-and-forget — if the
      // event bus is unavailable, the message still went to the DB and
      // real-time WebSocket subscribers already got it.
      const recipientIds = conversation.participantIds.filter(
        (id) => id !== dto.senderId,
      );
      const preview =
        dto.content.length > MESSAGE_PREVIEW_MAX_LEN
          ? dto.content.slice(0, MESSAGE_PREVIEW_MAX_LEN) + "…"
          : dto.content;

      void this.events.publishMessageSent({
        tenantId,
        messageId: message.id,
        conversationId: dto.conversationId,
        senderId: dto.senderId,
        recipientIds,
        messageType: message.messageType,
        preview,
        hasAttachment: !!dto.attachmentUrl,
        hasOffer: dto.offerAmount != null,
        offerAmount: dto.offerAmount,
        offerCurrency: dto.offerCurrency,
        sentAt: message.createdAt,
      });

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
      await this.prisma.message.updateMany({
        where: { id: messageId, tenantId },
        data: {
          isRead: true,
          readAt: new Date(),
        },
      });

      // Update participant's last read time and reset unread count (tenant-scoped)
      await this.prisma.participant.updateMany({
        where: {
          tenantId,
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

  // ═══════════════════════════════════════════════════════════════════════════
  // Ported from the archived field-chat service (field/task/incident scope,
  // archive flag, participants, message search). Nullable schema fields keep
  // the marketplace flows (product/order conversations) unchanged.
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Find an existing conversation for (scopeType, scopeId) within a tenant.
   *
   * Throws NotFoundException when no match exists. The archived field-chat
   * service returned null; chat-service's convention (see
   * `getConversationById` above) is to 404 on missing rows so the
   * controller can pass the exception through without extra branching.
   * Callers that want "find-or-create" should use `createConversation`
   * with scopeType/scopeId in the DTO — that path de-dups on scope.
   */
  async getConversationByScope(
    scopeType: string,
    scopeId: string,
    tenantId: string,
  ) {
    if (!scopeType || !scopeId) {
      throw new BadRequestException("scopeType and scopeId are required");
    }
    const conversation = await this.prisma.conversation.findFirst({
      where: { tenantId, scopeType, scopeId },
      include: {
        participants: true,
        messages: {
          orderBy: { createdAt: "desc" },
          take: 1,
        },
      },
    });
    if (!conversation) {
      throw new NotFoundException(
        `No conversation found for scope ${scopeType}/${scopeId}`,
      );
    }
    return conversation;
  }

  /**
   * Archive a conversation (soft-delete semantics).
   * Sets isActive=false and records archivedAt. Idempotent: archiving an
   * already-archived conversation is a no-op that still returns the row.
   */
  async archiveConversation(
    conversationId: string,
    userId: string,
    tenantId: string,
  ) {
    const conversation = await this.getConversationById(
      conversationId,
      tenantId,
    );
    if (!conversation.participantIds.includes(userId)) {
      throw new BadRequestException(
        "Only a participant can archive this conversation",
      );
    }
    if (!conversation.isActive) {
      return conversation;
    }
    return this.prisma.conversation.update({
      where: { id: conversationId },
      data: {
        isActive: false,
        archivedAt: new Date(),
      },
    });
  }

  /**
   * Full-text-ish search across messages.
   * Scoped to the caller's tenant; an optional conversationId restricts the
   * search to a single thread. Returns newest-first, capped to `limit`.
   */
  async searchMessages(
    query: string,
    tenantId: string,
    opts: { conversationId?: string; limit?: number } = {},
  ) {
    const q = (query || "").trim();
    if (q.length < 2) {
      throw new BadRequestException("Search query must be at least 2 characters");
    }
    const limit = Math.min(Math.max(opts.limit ?? 50, 1), 200);
    return this.prisma.message.findMany({
      where: {
        tenantId,
        ...(opts.conversationId ? { conversationId: opts.conversationId } : {}),
        content: { contains: q, mode: "insensitive" },
      },
      orderBy: { createdAt: "desc" },
      take: limit,
    });
  }

  /**
   * Add a participant to a conversation.
   * No-op if the user is already a participant; otherwise appends to
   * participantIds and creates the Participant row inside a transaction.
   */
  async addParticipant(
    conversationId: string,
    newUserId: string,
    requesterId: string,
    tenantId: string,
    role: ParticipantRole = "BUYER",
  ) {
    const conversation = await this.getConversationById(
      conversationId,
      tenantId,
    );
    if (!conversation.participantIds.includes(requesterId)) {
      throw new BadRequestException(
        "Only a participant can add other participants",
      );
    }
    if (conversation.participantIds.includes(newUserId)) {
      return conversation;
    }
    // Race-safe: two concurrent addParticipant() calls for the same user
    // can both pass the pre-check above. The Participant row has a
    // (conversationId, userId) unique index, so the loser hits Prisma error
    // P2002 — treat that as "already added" and return the current row,
    // matching the read-modify-write semantics that single callers see.
    try {
      return await this.prisma.$transaction(async (tx: any) => {
        await tx.participant.create({
          data: {
            tenantId,
            conversationId,
            userId: newUserId,
            role,
          },
        });
        return tx.conversation.update({
          where: { id: conversationId },
          data: { participantIds: { push: newUserId } },
          include: { participants: true },
        });
      });
    } catch (e: any) {
      if (e?.code === "P2002") {
        return this.getConversationById(conversationId, tenantId);
      }
      throw e;
    }
  }

  /**
   * Remove a participant from a conversation.
   * The last participant cannot leave — archive the conversation instead.
   */
  async removeParticipant(
    conversationId: string,
    userIdToRemove: string,
    requesterId: string,
    tenantId: string,
  ) {
    const conversation = await this.getConversationById(
      conversationId,
      tenantId,
    );
    if (!conversation.participantIds.includes(requesterId)) {
      throw new BadRequestException(
        "Only a participant can remove participants",
      );
    }
    if (!conversation.participantIds.includes(userIdToRemove)) {
      throw new NotFoundException("User is not a participant of this conversation");
    }
    if (conversation.participantIds.length <= 1) {
      throw new BadRequestException(
        "Cannot remove the last participant. Archive the conversation instead.",
      );
    }
    const remaining = conversation.participantIds.filter(
      (id: string) => id !== userIdToRemove,
    );
    return this.prisma.$transaction(async (tx: any) => {
      await tx.participant.deleteMany({
        where: { tenantId, conversationId, userId: userIdToRemove },
      });
      return tx.conversation.update({
        where: { id: conversationId },
        data: { participantIds: { set: remaining } },
        include: { participants: true },
      });
    });
  }
}

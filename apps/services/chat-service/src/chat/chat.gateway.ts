/**
 * Chat Gateway - WebSocket (Socket.IO)
 * بوابة المحادثات - الاتصال الفوري
 */

import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Logger } from '@nestjs/common';
import { ChatService } from './chat.service';
import { JoinConversationDto } from './dto/join-conversation.dto';
import { SendMessageDto } from './dto/send-message.dto';
import { TypingIndicatorDto } from './dto/typing-indicator.dto';
import { ReadReceiptDto } from './dto/read-receipt.dto';
import * as jwt from 'jsonwebtoken';

@WebSocketGateway({
  cors: {
    origin: process.env.CORS_ALLOWED_ORIGINS?.split(',') || [
      'https://sahool.com',
      'https://app.sahool.com',
      'http://localhost:3000',
      'http://localhost:8080',
    ],
    credentials: true,
  },
  namespace: '/chat',
})
export class ChatGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;

  private readonly logger = new Logger(ChatGateway.name);
  private userSocketMap = new Map<string, { socketId: string; timestamp: number }>(); // userId -> {socketId, timestamp}
  private readonly SOCKET_TIMEOUT = 30 * 60 * 1000; // 30 minutes

  constructor(private readonly chatService: ChatService) {
    // Periodically clean up stale socket entries
    setInterval(() => this.cleanupStaleEntries(), 5 * 60 * 1000); // Every 5 minutes
  }

  /**
   * Clean up stale socket entries to prevent memory leak
   */
  private cleanupStaleEntries() {
    const now = Date.now();
    for (const [userId, data] of this.userSocketMap.entries()) {
      if (now - data.timestamp > this.SOCKET_TIMEOUT) {
        this.logger.log(`Removing stale socket entry for user ${userId}`);
        this.userSocketMap.delete(userId);
      }
    }
  }

  /**
   * Verify JWT token from socket handshake
   * Validates JWT tokens in production
   */
  private verifyAuthentication(client: Socket): string | null {
    try {
      // Extract token from auth or query parameters
      const token = client.handshake.auth?.token || client.handshake.query?.token;

      if (!token) {
        this.logger.warn('No authentication token provided');
        return null;
      }

      // Validate JWT token
      const jwtSecret = process.env.JWT_SECRET;
      if (!jwtSecret) {
        this.logger.error('JWT_SECRET environment variable is not set');
        return null;
      }

      // SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
      // Never trust algorithm from environment variables or token header
      const ALLOWED_ALGORITHMS: jwt.Algorithm[] = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512'];

      // Decode header without verification to check algorithm
      const header = jwt.decode(token, { complete: true })?.header;
      if (!header || !header.alg) {
        this.logger.warn('Invalid token: missing algorithm');
        return null;
      }

      // Reject 'none' algorithm explicitly
      if (header.alg.toLowerCase() === 'none') {
        this.logger.warn('Invalid token: none algorithm not allowed');
        return null;
      }

      // Verify algorithm is in whitelist
      if (!ALLOWED_ALGORITHMS.includes(header.alg as jwt.Algorithm)) {
        this.logger.warn(`Invalid token: unsupported algorithm ${header.alg}`);
        return null;
      }

      const decoded = jwt.verify(token, jwtSecret, {
        algorithms: ALLOWED_ALGORITHMS,
      }) as { userId: string; sub?: string };
      const userId = decoded.userId || decoded.sub;

      if (!userId) {
        this.logger.warn('No userId found in decoded token');
        return null;
      }

      return userId;
    } catch (error) {
      this.logger.error('Authentication verification failed', error instanceof Error ? error.message : 'Unknown error');
      return null;
    }
  }

  /**
   * Handle client connection
   */
  async handleConnection(client: Socket) {
    this.logger.log(`Client attempting connection: ${client.id}`);

    // Verify authentication
    const userId = this.verifyAuthentication(client);

    if (!userId) {
      this.logger.warn(`Unauthenticated connection attempt from ${client.id}`);
      client.emit('error', { message: 'Authentication required' });
      client.disconnect();
      return;
    }

    // Store userId in client data for later use
    client.data.userId = userId;

    // Update userSocketMap with timestamp
    this.userSocketMap.set(userId, {
      socketId: client.id,
      timestamp: Date.now(),
    });

    try {
      // Update user online status
      await this.chatService.updateOnlineStatus(userId, true);

      // Notify other users that this user is online
      this.server.emit('user_online', { userId, timestamp: new Date() });

      this.logger.log(`User ${userId} authenticated and connected with socket ${client.id}`);
    } catch (error) {
      this.logger.error('Failed to update user online status');
      // Don't expose internal error to client
      client.emit('error', { message: 'Connection failed' });
      client.disconnect();
    }
  }

  /**
   * Handle client disconnection
   */
  async handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);

    // Get userId from client data (set during authentication)
    const disconnectedUserId = client.data.userId;

    if (disconnectedUserId) {
      // Remove from userSocketMap
      this.userSocketMap.delete(disconnectedUserId);

      try {
        // Update user offline status
        await this.chatService.updateOnlineStatus(disconnectedUserId, false);

        // Notify other users that this user is offline
        this.server.emit('user_offline', {
          userId: disconnectedUserId,
          timestamp: new Date(),
        });

        this.logger.log(`User ${disconnectedUserId} disconnected`);
      } catch (error) {
        this.logger.error('Failed to update user offline status');
        // Don't expose error details
      }
    }
  }

  /**
   * Join a conversation room
   * Event: join_conversation
   */
  @SubscribeMessage('join_conversation')
  async handleJoinConversation(
    @MessageBody() data: JoinConversationDto,
    @ConnectedSocket() client: Socket,
  ) {
    try {
      const { conversationId } = data;

      // Use authenticated userId from client.data, not from client-provided data
      const userId = client.data.userId;

      if (!userId) {
        return {
          event: 'error',
          data: { message: 'Authentication required' },
        };
      }

      // Verify conversation exists and user is a participant
      const conversation = await this.chatService.getConversationById(conversationId);

      if (!conversation.participantIds.includes(userId)) {
        return {
          event: 'error',
          data: { message: 'Access denied' },
        };
      }

      // Join the conversation room
      client.join(conversationId);

      this.logger.log(`User ${userId} joined conversation ${conversationId}`);

      return {
        event: 'joined_conversation',
        data: {
          conversationId,
          userId,
          timestamp: new Date(),
        },
      };
    } catch (error) {
      this.logger.error('Error joining conversation');
      return {
        event: 'error',
        data: { message: 'Failed to join conversation' },
      };
    }
  }

  /**
   * Send a message
   * Event: send_message
   */
  @SubscribeMessage('send_message')
  async handleSendMessage(
    @MessageBody() data: SendMessageDto,
    @ConnectedSocket() client: Socket,
  ) {
    try {
      // Use authenticated userId from client.data, not from client-provided data
      const authenticatedUserId = client.data.userId;

      if (!authenticatedUserId) {
        return {
          event: 'error',
          data: { message: 'Authentication required' },
        };
      }

      // Verify the authenticated user matches the senderId
      if (authenticatedUserId !== data.senderId) {
        return {
          event: 'error',
          data: { message: 'Unauthorized' },
        };
      }

      // Save message to database
      const message = await this.chatService.sendMessage(data);

      // Emit message to all participants in the conversation room
      this.server.to(data.conversationId).emit('message_received', {
        message,
        timestamp: new Date(),
      });

      this.logger.log(
        `Message sent in conversation ${data.conversationId} by ${authenticatedUserId}`,
      );

      return {
        event: 'message_sent',
        data: { message },
      };
    } catch (error) {
      this.logger.error('Error sending message');
      return {
        event: 'error',
        data: { message: 'Failed to send message' },
      };
    }
  }

  /**
   * Typing indicator
   * Event: typing
   */
  @SubscribeMessage('typing')
  async handleTyping(
    @MessageBody() data: TypingIndicatorDto,
    @ConnectedSocket() client: Socket,
  ) {
    try {
      const { conversationId, isTyping } = data;

      // Use authenticated userId from client.data
      const userId = client.data.userId;

      if (!userId) {
        return {
          event: 'error',
          data: { message: 'Authentication required' },
        };
      }

      // Update typing status in database
      await this.chatService.updateTypingIndicator(conversationId, userId, isTyping);

      // Broadcast typing indicator to other participants in the conversation
      client.to(conversationId).emit('typing_indicator', {
        conversationId,
        userId,
        isTyping,
        timestamp: new Date(),
      });

      return {
        event: 'typing_updated',
        data: { conversationId, userId, isTyping },
      };
    } catch (error) {
      this.logger.error('Error updating typing indicator');
      return {
        event: 'error',
        data: { message: 'Failed to update typing indicator' },
      };
    }
  }

  /**
   * Read receipt
   * Event: read_receipt
   */
  @SubscribeMessage('read_receipt')
  async handleReadReceipt(
    @MessageBody() data: ReadReceiptDto,
    @ConnectedSocket() client: Socket,
  ) {
    try {
      const { conversationId, messageId } = data;

      // Use authenticated userId from client.data
      const userId = client.data.userId;

      if (!userId) {
        return {
          event: 'error',
          data: { message: 'Authentication required' },
        };
      }

      // Mark message as read
      await this.chatService.markMessageAsRead(messageId, userId);

      // Notify sender that message was read
      this.server.to(conversationId).emit('message_read', {
        conversationId,
        messageId,
        userId,
        timestamp: new Date(),
      });

      return {
        event: 'read_receipt_sent',
        data: { messageId, userId },
      };
    } catch (error) {
      this.logger.error('Error handling read receipt');
      return {
        event: 'error',
        data: { message: 'Failed to mark message as read' },
      };
    }
  }

  /**
   * Mark conversation as read
   * Event: mark_conversation_read
   */
  @SubscribeMessage('mark_conversation_read')
  async handleMarkConversationRead(
    @MessageBody() data: { conversationId: string },
    @ConnectedSocket() client: Socket,
  ) {
    try {
      const { conversationId } = data;

      // Use authenticated userId from client.data
      const userId = client.data.userId;

      if (!userId) {
        return {
          event: 'error',
          data: { message: 'Authentication required' },
        };
      }

      // Mark all messages as read
      await this.chatService.markConversationAsRead(conversationId, userId);

      // Notify other participants
      client.to(conversationId).emit('conversation_read', {
        conversationId,
        userId,
        timestamp: new Date(),
      });

      return {
        event: 'conversation_marked_read',
        data: { conversationId, userId },
      };
    } catch (error) {
      this.logger.error('Error marking conversation as read');
      return {
        event: 'error',
        data: { message: 'Failed to mark conversation as read' },
      };
    }
  }

  /**
   * Leave a conversation room
   * Event: leave_conversation
   */
  @SubscribeMessage('leave_conversation')
  handleLeaveConversation(
    @MessageBody() data: { conversationId: string },
    @ConnectedSocket() client: Socket,
  ) {
    const { conversationId } = data;

    // Use authenticated userId from client.data
    const userId = client.data.userId;

    if (!userId) {
      return {
        event: 'error',
        data: { message: 'Authentication required' },
      };
    }

    client.leave(conversationId);

    this.logger.log(`User ${userId} left conversation ${conversationId}`);

    return {
      event: 'left_conversation',
      data: { conversationId, userId },
    };
  }

  /**
   * Get online status of a user
   */
  isUserOnline(userId: string): boolean {
    return this.userSocketMap.has(userId);
  }

  /**
   * Send notification to specific user
   */
  sendToUser(userId: string, event: string, data: any) {
    const socketData = this.userSocketMap.get(userId);
    if (socketData) {
      this.server.to(socketData.socketId).emit(event, data);
    }
  }
}

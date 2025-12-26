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
  private userSocketMap = new Map<string, string>(); // userId -> socketId

  constructor(private readonly chatService: ChatService) {}

  /**
   * Handle client connection
   */
  async handleConnection(client: Socket) {
    this.logger.log(`Client connected: ${client.id}`);

    // Get userId from handshake query or auth
    const userId = client.handshake.query.userId as string;

    if (userId) {
      this.userSocketMap.set(userId, client.id);

      // Update user online status
      await this.chatService.updateOnlineStatus(userId, true);

      // Notify other users that this user is online
      this.server.emit('user_online', { userId, timestamp: new Date() });

      this.logger.log(`User ${userId} connected with socket ${client.id}`);
    }
  }

  /**
   * Handle client disconnection
   */
  async handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);

    // Find and remove user from map
    let disconnectedUserId: string | null = null;
    for (const [userId, socketId] of this.userSocketMap.entries()) {
      if (socketId === client.id) {
        disconnectedUserId = userId;
        this.userSocketMap.delete(userId);
        break;
      }
    }

    if (disconnectedUserId) {
      // Update user offline status
      await this.chatService.updateOnlineStatus(disconnectedUserId, false);

      // Notify other users that this user is offline
      this.server.emit('user_offline', {
        userId: disconnectedUserId,
        timestamp: new Date(),
      });

      this.logger.log(`User ${disconnectedUserId} disconnected`);
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
      const { conversationId, userId } = data;

      // Verify conversation exists and user is a participant
      const conversation = await this.chatService.getConversationById(conversationId);

      if (!conversation.participantIds.includes(userId)) {
        return {
          event: 'error',
          data: { message: 'User is not a participant in this conversation' },
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
      this.logger.error(`Error joining conversation: ${error.message}`);
      return {
        event: 'error',
        data: { message: error.message },
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
      // Save message to database
      const message = await this.chatService.sendMessage(data);

      // Emit message to all participants in the conversation room
      this.server.to(data.conversationId).emit('message_received', {
        message,
        timestamp: new Date(),
      });

      this.logger.log(
        `Message sent in conversation ${data.conversationId} by ${data.senderId}`,
      );

      return {
        event: 'message_sent',
        data: { message },
      };
    } catch (error) {
      this.logger.error(`Error sending message: ${error.message}`);
      return {
        event: 'error',
        data: { message: error.message },
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
      const { conversationId, userId, isTyping } = data;

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
      this.logger.error(`Error updating typing indicator: ${error.message}`);
      return {
        event: 'error',
        data: { message: error.message },
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
      const { conversationId, userId, messageId } = data;

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
      this.logger.error(`Error handling read receipt: ${error.message}`);
      return {
        event: 'error',
        data: { message: error.message },
      };
    }
  }

  /**
   * Mark conversation as read
   * Event: mark_conversation_read
   */
  @SubscribeMessage('mark_conversation_read')
  async handleMarkConversationRead(
    @MessageBody() data: { conversationId: string; userId: string },
    @ConnectedSocket() client: Socket,
  ) {
    try {
      const { conversationId, userId } = data;

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
      this.logger.error(`Error marking conversation as read: ${error.message}`);
      return {
        event: 'error',
        data: { message: error.message },
      };
    }
  }

  /**
   * Leave a conversation room
   * Event: leave_conversation
   */
  @SubscribeMessage('leave_conversation')
  handleLeaveConversation(
    @MessageBody() data: { conversationId: string; userId: string },
    @ConnectedSocket() client: Socket,
  ) {
    const { conversationId, userId } = data;

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
    const socketId = this.userSocketMap.get(userId);
    if (socketId) {
      this.server.to(socketId).emit(event, data);
    }
  }
}

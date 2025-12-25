/**
 * Chat Controller
 * متحكم المحادثات - REST API
 */

import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  HttpStatus,
  HttpCode,
} from '@nestjs/common';
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
} from '@nestjs/swagger';
import { ChatService } from './chat.service';
import { CreateConversationDto } from './dto/create-conversation.dto';
import { SendMessageDto } from './dto/send-message.dto';

@ApiTags('Chat')
@Controller('chat')
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  /**
   * Health check endpoint
   */
  @Get('/health')
  @ApiOperation({ summary: 'Health check' })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    return {
      status: 'ok',
      service: 'chat-service',
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Create a new conversation
   * POST /api/v1/chat/conversations
   */
  @Post('conversations')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Create new conversation',
    description: 'Create a new conversation between buyer and seller',
  })
  @ApiResponse({
    status: 201,
    description: 'Conversation created successfully',
  })
  @ApiResponse({
    status: 400,
    description: 'Bad request - invalid data',
  })
  async createConversation(@Body() createConversationDto: CreateConversationDto) {
    return this.chatService.createConversation(createConversationDto);
  }

  /**
   * Get user's conversations
   * GET /api/v1/chat/conversations/:userId
   */
  @Get('conversations/user/:userId')
  @ApiOperation({
    summary: 'Get user conversations',
    description: 'Get all conversations for a specific user',
  })
  @ApiParam({
    name: 'userId',
    description: 'User ID',
    example: 'user-123',
  })
  @ApiResponse({
    status: 200,
    description: 'List of user conversations',
  })
  async getUserConversations(@Param('userId') userId: string) {
    return this.chatService.getUserConversations(userId);
  }

  /**
   * Get conversation by ID
   * GET /api/v1/chat/conversations/:id
   */
  @Get('conversations/:id')
  @ApiOperation({
    summary: 'Get conversation details',
    description: 'Get conversation by ID with participants',
  })
  @ApiParam({
    name: 'id',
    description: 'Conversation ID',
    example: 'conv-123',
  })
  @ApiResponse({
    status: 200,
    description: 'Conversation details',
  })
  @ApiResponse({
    status: 404,
    description: 'Conversation not found',
  })
  async getConversation(@Param('id') id: string) {
    return this.chatService.getConversationById(id);
  }

  /**
   * Get messages for a conversation
   * GET /api/v1/chat/conversations/:id/messages
   */
  @Get('conversations/:id/messages')
  @ApiOperation({
    summary: 'Get conversation messages',
    description: 'Get paginated messages for a conversation',
  })
  @ApiParam({
    name: 'id',
    description: 'Conversation ID',
    example: 'conv-123',
  })
  @ApiQuery({
    name: 'page',
    required: false,
    description: 'Page number (default: 1)',
    example: 1,
  })
  @ApiQuery({
    name: 'limit',
    required: false,
    description: 'Messages per page (default: 50)',
    example: 50,
  })
  @ApiResponse({
    status: 200,
    description: 'Paginated messages',
  })
  async getMessages(
    @Param('id') conversationId: string,
    @Query('page') page: string = '1',
    @Query('limit') limit: string = '50',
  ) {
    return this.chatService.getMessages(
      conversationId,
      parseInt(page, 10),
      parseInt(limit, 10),
    );
  }

  /**
   * Send a message (REST fallback)
   * POST /api/v1/chat/messages
   */
  @Post('messages')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Send message',
    description: 'Send a message to a conversation (REST fallback)',
  })
  @ApiResponse({
    status: 201,
    description: 'Message sent successfully',
  })
  @ApiResponse({
    status: 400,
    description: 'Bad request',
  })
  @ApiResponse({
    status: 404,
    description: 'Conversation not found',
  })
  async sendMessage(@Body() sendMessageDto: SendMessageDto) {
    return this.chatService.sendMessage(sendMessageDto);
  }

  /**
   * Mark message as read
   * POST /api/v1/chat/messages/:messageId/read
   */
  @Post('messages/:messageId/read')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Mark message as read',
    description: 'Mark a specific message as read',
  })
  @ApiParam({
    name: 'messageId',
    description: 'Message ID',
    example: 'msg-123',
  })
  @ApiResponse({
    status: 200,
    description: 'Message marked as read',
  })
  async markMessageAsRead(
    @Param('messageId') messageId: string,
    @Body('userId') userId: string,
  ) {
    return this.chatService.markMessageAsRead(messageId, userId);
  }

  /**
   * Mark all messages in conversation as read
   * POST /api/v1/chat/conversations/:id/read
   */
  @Post('conversations/:id/read')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Mark conversation as read',
    description: 'Mark all messages in a conversation as read',
  })
  @ApiParam({
    name: 'id',
    description: 'Conversation ID',
    example: 'conv-123',
  })
  @ApiResponse({
    status: 200,
    description: 'Conversation marked as read',
  })
  async markConversationAsRead(
    @Param('id') conversationId: string,
    @Body('userId') userId: string,
  ) {
    return this.chatService.markConversationAsRead(conversationId, userId);
  }

  /**
   * Get unread message count
   * GET /api/v1/chat/users/:userId/unread-count
   */
  @Get('users/:userId/unread-count')
  @ApiOperation({
    summary: 'Get unread count',
    description: 'Get total unread message count for user',
  })
  @ApiParam({
    name: 'userId',
    description: 'User ID',
    example: 'user-123',
  })
  @ApiResponse({
    status: 200,
    description: 'Unread message count',
  })
  async getUnreadCount(@Param('userId') userId: string) {
    const count = await this.chatService.getUnreadCount(userId);
    return { userId, unreadCount: count };
  }
}

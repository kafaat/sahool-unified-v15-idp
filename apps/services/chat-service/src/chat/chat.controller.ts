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
  UnauthorizedException,
  UseGuards,
} from "@nestjs/common";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiQuery,
  ApiBearerAuth,
} from "@nestjs/swagger";
import { Throttle } from "@nestjs/throttler";
import { ChatService } from "./chat.service";
import { CreateConversationDto } from "./dto/create-conversation.dto";
import { SendMessageDto } from "./dto/send-message.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { UserId, CurrentUser } from "../auth/decorators";

@ApiTags("Chat")
@Controller("chat")
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  /**
   * Verify user is a participant in the conversation
   */
  private async verifyConversationAccess(
    conversationId: string,
    userId: string,
  ) {
    const conversation =
      await this.chatService.getConversationById(conversationId);
    if (!conversation.participantIds.includes(userId)) {
      throw new UnauthorizedException("Access denied to this conversation");
    }
  }

  /**
   * Health check endpoint
   */
  @Get("/health")
  @Throttle({ default: { limit: 10, ttl: 60000 } }) // 10 requests per minute
  @ApiOperation({ summary: "Health check" })
  @ApiResponse({ status: 200, description: "Service is healthy" })
  healthCheck() {
    return {
      status: "ok",
      service: "chat-service",
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Create a new conversation
   * POST /api/v1/chat/conversations
   */
  @Post("conversations")
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: "Create new conversation",
    description: "Create a new conversation between buyer and seller",
  })
  @ApiResponse({
    status: 201,
    description: "Conversation created successfully",
  })
  @ApiResponse({
    status: 400,
    description: "Bad request - invalid data",
  })
  async createConversation(
    @Body() createConversationDto: CreateConversationDto,
  ) {
    return this.chatService.createConversation(createConversationDto);
  }

  /**
   * Get user's conversations
   * GET /api/v1/chat/conversations/me
   */
  @Get("conversations/me")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Get user conversations",
    description: "Get all conversations for the authenticated user",
  })
  @ApiResponse({
    status: 200,
    description: "List of user conversations",
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized - Valid JWT token required",
  })
  async getUserConversations(@UserId() userId: string) {
    return this.chatService.getUserConversations(userId);
  }

  /**
   * Get conversation by ID
   * GET /api/v1/chat/conversations/:id
   */
  @Get("conversations/:id")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Get conversation details",
    description: "Get conversation by ID with participants",
  })
  @ApiParam({
    name: "id",
    description: "Conversation ID",
    example: "conv-123",
  })
  @ApiResponse({
    status: 200,
    description: "Conversation details",
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized - User is not a participant",
  })
  @ApiResponse({
    status: 404,
    description: "Conversation not found",
  })
  async getConversation(@Param("id") id: string, @UserId() userId: string) {
    await this.verifyConversationAccess(id, userId);
    return this.chatService.getConversationById(id);
  }

  /**
   * Get messages for a conversation
   * GET /api/v1/chat/conversations/:id/messages
   */
  @Get("conversations/:id/messages")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Get conversation messages",
    description: "Get paginated messages for a conversation",
  })
  @ApiParam({
    name: "id",
    description: "Conversation ID",
    example: "conv-123",
  })
  @ApiQuery({
    name: "page",
    required: false,
    description: "Page number (default: 1)",
    example: 1,
  })
  @ApiQuery({
    name: "limit",
    required: false,
    description: "Messages per page (default: 50)",
    example: 50,
  })
  @ApiResponse({
    status: 200,
    description: "Paginated messages",
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized - User is not a participant",
  })
  async getMessages(
    @Param("id") conversationId: string,
    @Query("page") page: string = "1",
    @Query("limit") limit: string = "50",
    @UserId() userId: string,
  ) {
    await this.verifyConversationAccess(conversationId, userId);
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
  @Post("messages")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: "Send message",
    description: "Send a message to a conversation (REST fallback)",
  })
  @ApiResponse({
    status: 201,
    description: "Message sent successfully",
  })
  @ApiResponse({
    status: 400,
    description: "Bad request",
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized - Valid JWT token required",
  })
  @ApiResponse({
    status: 404,
    description: "Conversation not found",
  })
  async sendMessage(
    @Body() sendMessageDto: SendMessageDto,
    @UserId() userId: string,
  ) {
    // Ensure the senderId matches the authenticated user
    sendMessageDto.senderId = userId;
    return this.chatService.sendMessage(sendMessageDto);
  }

  /**
   * Mark message as read
   * POST /api/v1/chat/messages/:messageId/read
   */
  @Post("messages/:messageId/read")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Mark message as read",
    description: "Mark a specific message as read",
  })
  @ApiParam({
    name: "messageId",
    description: "Message ID",
    example: "msg-123",
  })
  @ApiResponse({
    status: 200,
    description: "Message marked as read",
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized - Valid JWT token required",
  })
  async markMessageAsRead(
    @Param("messageId") messageId: string,
    @UserId() userId: string,
  ) {
    return this.chatService.markMessageAsRead(messageId, userId);
  }

  /**
   * Mark all messages in conversation as read
   * POST /api/v1/chat/conversations/:id/read
   */
  @Post("conversations/:id/read")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Mark conversation as read",
    description: "Mark all messages in a conversation as read",
  })
  @ApiParam({
    name: "id",
    description: "Conversation ID",
    example: "conv-123",
  })
  @ApiResponse({
    status: 200,
    description: "Conversation marked as read",
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized",
  })
  async markConversationAsRead(
    @Param("id") conversationId: string,
    @UserId() userId: string,
  ) {
    await this.verifyConversationAccess(conversationId, userId);
    return this.chatService.markConversationAsRead(conversationId, userId);
  }

  /**
   * Get unread message count
   * GET /api/v1/chat/unread-count
   */
  @Get("unread-count")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Get unread count",
    description: "Get total unread message count for authenticated user",
  })
  @ApiResponse({
    status: 200,
    description: "Unread message count",
  })
  @ApiResponse({
    status: 401,
    description: "Unauthorized - Valid JWT token required",
  })
  async getUnreadCount(@UserId() userId: string) {
    const count = await this.chatService.getUnreadCount(userId);
    return { userId, unreadCount: count };
  }
}

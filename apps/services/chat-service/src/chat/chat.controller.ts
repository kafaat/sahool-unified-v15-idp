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
  Req,
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
import { UserId } from "../auth/decorators";

@ApiTags("Chat")
@Controller("chat")
export class ChatController {
  constructor(private readonly chatService: ChatService) {}

  /**
   * Extract the JWT-bound tenant id from the authenticated request.
   *
   * Previously each handler resolved tenant as
   *   `req.user?.tenantId || req.headers['x-tenant-id']`
   * which let an authenticated caller of tenant A read/write tenant B's
   * conversations by setting the header whenever the JWT tenant claim
   * was missing. The header fallback is removed: with `JwtAuthGuard`
   * mounted on every route, `req.user.tenantId` must be present, and
   * requests without it are rejected as 401 rather than silently
   * accepting an attacker-controlled value.
   */
  private requireTenantId(req: any): string {
    const tenantId = req.user?.tenantId;
    if (!tenantId) {
      throw new UnauthorizedException("Missing tenant context in token");
    }
    return tenantId;
  }

  /**
   * Verify user is a participant in the conversation
   */
  private async verifyConversationAccess(
    conversationId: string,
    userId: string,
    tenantId: string,
  ) {
    const conversation =
      await this.chatService.getConversationById(conversationId, tenantId);
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
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
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
  @ApiResponse({
    status: 401,
    description: "Unauthorized - Valid JWT token required",
  })
  async createConversation(
    @Body() createConversationDto: CreateConversationDto,
    @UserId() userId: string,
    @Req() req: any,
  ) {
    const tenantId = this.requireTenantId(req);
    // Security: Ensure the authenticated user is one of the participants
    if (!createConversationDto.participantIds.includes(userId)) {
      throw new UnauthorizedException(
        "User must be a participant in the conversation",
      );
    }
    return this.chatService.createConversation(createConversationDto, tenantId);
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
  async getUserConversations(@UserId() userId: string, @Req() req: any) {
    const tenantId = this.requireTenantId(req);
    return this.chatService.getUserConversations(userId, tenantId);
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
  async getConversation(@Param("id") id: string, @UserId() userId: string, @Req() req: any) {
    const tenantId = this.requireTenantId(req);
    await this.verifyConversationAccess(id, userId, tenantId);
    return this.chatService.getConversationById(id, tenantId);
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
    @Req() req: any,
  ) {
    const tenantId = this.requireTenantId(req);
    await this.verifyConversationAccess(conversationId, userId, tenantId);
    return this.chatService.getMessages(
      conversationId,
      parseInt(page, 10),
      parseInt(limit, 10),
      tenantId,
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
    @Req() req: any,
  ) {
    const tenantId = this.requireTenantId(req);
    // Ensure the senderId matches the authenticated user
    sendMessageDto.senderId = userId;
    return this.chatService.sendMessage(sendMessageDto, tenantId);
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
    @Req() req: any,
  ) {
    const tenantId = this.requireTenantId(req);
    return this.chatService.markMessageAsRead(messageId, userId, tenantId);
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
    @Req() req: any,
  ) {
    const tenantId = this.requireTenantId(req);
    await this.verifyConversationAccess(conversationId, userId, tenantId);
    return this.chatService.markConversationAsRead(conversationId, userId, tenantId);
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
  async getUnreadCount(@UserId() userId: string, @Req() req: any) {
    const tenantId = this.requireTenantId(req);
    const count = await this.chatService.getUnreadCount(userId, tenantId);
    return { userId, unreadCount: count };
  }
}

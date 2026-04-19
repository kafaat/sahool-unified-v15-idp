/**
 * Chat Controller
 * متحكم المحادثات - REST API
 */

import {
  Controller,
  Get,
  Post,
  Delete,
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
import { AddParticipantDto } from "./dto/add-participant.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { UserId } from "../auth/decorators";

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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
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
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'];
    const count = await this.chatService.getUnreadCount(userId, tenantId);
    return { userId, unreadCount: count };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Ported from the archived field-chat service.
  // Gives chat-service feature parity for thread-style conversations (field/
  // task/incident scope) without altering the marketplace (product/order)
  // contract already exposed by this controller.
  // ═══════════════════════════════════════════════════════════════════════════

  @Get("conversations/by-scope/:scopeType/:scopeId")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Get conversation by domain scope",
    description:
      "Resolve the conversation attached to a (scopeType, scopeId) pair — e.g. field:fld_abc, task:task_123. 404 if none exists. Ported from field-chat.",
  })
  @ApiParam({ name: "scopeType", example: "field" })
  @ApiParam({ name: "scopeId", example: "fld_abc" })
  async getConversationByScope(
    @Param("scopeType") scopeType: string,
    @Param("scopeId") scopeId: string,
    @UserId() userId: string,
    @Req() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers["x-tenant-id"];
    const conversation = await this.chatService.getConversationByScope(
      scopeType,
      scopeId,
      tenantId,
    );
    if (!conversation.participantIds.includes(userId)) {
      throw new UnauthorizedException("Access denied to this conversation");
    }
    return conversation;
  }

  @Post("conversations/:id/archive")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Archive a conversation",
    description: "Soft-delete: sets isActive=false and records archivedAt. Idempotent.",
  })
  @ApiParam({ name: "id", description: "Conversation UUID" })
  async archiveConversation(
    @Param("id") conversationId: string,
    @UserId() userId: string,
    @Req() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers["x-tenant-id"];
    return this.chatService.archiveConversation(
      conversationId,
      userId,
      tenantId,
    );
  }

  @Get("messages/search")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({
    summary: "Search messages",
    description:
      "Case-insensitive substring search over message content. Tenant-scoped; optional conversationId narrows to a single thread.",
  })
  @ApiQuery({ name: "q", required: true, description: "Search query (>= 2 chars)" })
  @ApiQuery({ name: "conversationId", required: false })
  @ApiQuery({ name: "limit", required: false, description: "Default 50, max 200" })
  async searchMessages(
    @Query("q") q: string,
    @Query("conversationId") conversationId: string | undefined,
    @Query("limit") limit: string | undefined,
    @Req() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers["x-tenant-id"];
    const parsedLimit = limit ? Math.max(1, parseInt(limit, 10) || 50) : 50;
    const messages = await this.chatService.searchMessages(q, tenantId, {
      conversationId,
      limit: parsedLimit,
    });
    return { query: q, total: messages.length, messages };
  }

  @Post("conversations/:id/participants")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Add participant",
    description: "Append a user to the conversation's participant list. No-op if already a participant.",
  })
  async addParticipant(
    @Param("id") conversationId: string,
    @Body() dto: AddParticipantDto,
    @UserId() requesterId: string,
    @Req() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers["x-tenant-id"];
    return this.chatService.addParticipant(
      conversationId,
      dto.userId,
      requesterId,
      tenantId,
      dto.role ?? "BUYER",
    );
  }

  @Delete("conversations/:id/participants/:userId")
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: "Remove participant",
    description:
      "Detach a user from the conversation. Refuses the operation if it would leave the thread empty — use archive instead.",
  })
  async removeParticipant(
    @Param("id") conversationId: string,
    @Param("userId") userIdToRemove: string,
    @UserId() requesterId: string,
    @Req() req: any,
  ) {
    const tenantId = req.user?.tenantId || req.headers["x-tenant-id"];
    return this.chatService.removeParticipant(
      conversationId,
      userIdToRemove,
      requesterId,
      tenantId,
    );
  }
}

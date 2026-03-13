/**
 * Join Conversation DTO (WebSocket)
 * بيانات الانضمام للمحادثة عبر WebSocket
 */

import { IsNotEmpty, IsUUID } from "class-validator";

export class JoinConversationDto {
  @IsNotEmpty()
  @IsUUID()
  conversationId: string;

  @IsNotEmpty()
  @IsUUID()
  userId: string;
}

/**
 * Join Conversation DTO (WebSocket)
 * بيانات الانضمام للمحادثة عبر WebSocket
 */

import { IsNotEmpty, IsString } from 'class-validator';

export class JoinConversationDto {
  @IsNotEmpty()
  @IsString()
  conversationId: string;

  @IsNotEmpty()
  @IsString()
  userId: string;
}

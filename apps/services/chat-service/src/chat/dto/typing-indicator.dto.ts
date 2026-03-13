/**
 * Typing Indicator DTO (WebSocket)
 * بيانات مؤشر الكتابة
 */

import { IsBoolean, IsNotEmpty, IsUUID } from "class-validator";

export class TypingIndicatorDto {
  @IsNotEmpty()
  @IsUUID()
  conversationId: string;

  @IsNotEmpty()
  @IsUUID()
  userId: string;

  @IsBoolean()
  isTyping: boolean;
}

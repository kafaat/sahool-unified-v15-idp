/**
 * Typing Indicator DTO (WebSocket)
 * بيانات مؤشر الكتابة
 */

import { IsBoolean, IsNotEmpty, IsString } from 'class-validator';

export class TypingIndicatorDto {
  @IsNotEmpty()
  @IsString()
  conversationId: string;

  @IsNotEmpty()
  @IsString()
  userId: string;

  @IsBoolean()
  isTyping: boolean;
}

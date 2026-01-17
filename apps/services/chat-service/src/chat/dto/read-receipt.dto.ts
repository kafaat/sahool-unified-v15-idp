/**
 * Read Receipt DTO (WebSocket)
 * بيانات تأكيد القراءة
 */

import { IsNotEmpty, IsString } from "class-validator";

export class ReadReceiptDto {
  @IsNotEmpty()
  @IsString()
  conversationId: string;

  @IsNotEmpty()
  @IsString()
  userId: string;

  @IsNotEmpty()
  @IsString()
  messageId: string;
}

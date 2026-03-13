/**
 * Read Receipt DTO (WebSocket)
 * بيانات تأكيد القراءة
 */

import { IsNotEmpty, IsUUID } from "class-validator";

export class ReadReceiptDto {
  @IsNotEmpty()
  @IsUUID()
  conversationId: string;

  @IsNotEmpty()
  @IsUUID()
  userId: string;

  @IsNotEmpty()
  @IsUUID()
  messageId: string;
}

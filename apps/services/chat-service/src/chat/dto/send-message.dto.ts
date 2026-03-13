/**
 * Send Message DTO
 * بيانات إرسال رسالة
 */

import {
  IsEnum,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsString,
  IsUUID,
  MaxLength,
  IsUrl,
  Min,
} from "class-validator";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import { SanitizePlainText, IsMoneyValue } from "../../utils/validation";

export enum MessageType {
  TEXT = "TEXT",
  IMAGE = "IMAGE",
  OFFER = "OFFER",
  SYSTEM = "SYSTEM",
}

export class SendMessageDto {
  @ApiProperty({
    description: "Conversation ID (UUID)",
    example: "550e8400-e29b-41d4-a716-446655440000",
  })
  @IsNotEmpty()
  @IsUUID()
  conversationId: string;

  @ApiProperty({
    description: "Sender user ID (UUID)",
    example: "550e8400-e29b-41d4-a716-446655440001",
  })
  @IsNotEmpty()
  @IsUUID()
  senderId: string;

  @ApiProperty({
    description: "Message content",
    example: "Hello, I am interested in buying your wheat harvest.",
  })
  @IsNotEmpty()
  @IsString()
  @MaxLength(10000)
  @SanitizePlainText()
  content: string;

  @ApiPropertyOptional({
    description: "Message type",
    enum: MessageType,
    default: MessageType.TEXT,
  })
  @IsOptional()
  @IsEnum(MessageType)
  messageType?: MessageType;

  @ApiPropertyOptional({
    description: "Attachment URL for images",
    example: "https://cdn.sahool.com/images/product-photo.jpg",
  })
  @IsOptional()
  @IsUrl()
  attachmentUrl?: string;

  @ApiPropertyOptional({
    description:
      "Offer amount for OFFER type messages (YER, max 2 decimal places)",
    example: 5000.0,
  })
  @IsOptional()
  @IsMoneyValue()
  offerAmount?: number;

  @ApiPropertyOptional({
    description: "Currency for offer (default YER)",
    example: "YER",
    default: "YER",
  })
  @IsOptional()
  @IsString()
  offerCurrency?: string;
}

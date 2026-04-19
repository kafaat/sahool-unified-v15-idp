/**
 * Create Conversation DTO
 * بيانات إنشاء محادثة جديدة
 */

import {
  IsArray,
  IsOptional,
  IsString,
  IsUUID,
  ArrayMinSize,
} from "class-validator";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

export class CreateConversationDto {
  @ApiProperty({
    description: "Array of participant user IDs",
    example: ["user-123", "user-456"],
    type: [String],
  })
  @IsArray()
  @ArrayMinSize(2)
  @IsString({ each: true })
  participantIds: string[];

  @ApiPropertyOptional({
    description: "Product ID if conversation is about a product",
    example: "prod-789",
  })
  @IsOptional()
  @IsString()
  productId?: string;

  @ApiPropertyOptional({
    description: "Order ID if conversation is about an order",
    example: "order-101",
  })
  @IsOptional()
  @IsString()
  orderId?: string;

  @ApiPropertyOptional({
    description:
      "Generic domain scope type (field | task | incident | ...). Paired with scopeId. Ported from field-chat so a single service handles marketplace + field-operations conversations.",
    example: "field",
  })
  @IsOptional()
  @IsString()
  scopeType?: string;

  @ApiPropertyOptional({
    description: "Scope identifier — value interpretation depends on scopeType.",
    example: "fld_7e3a…",
  })
  @IsOptional()
  @IsString()
  scopeId?: string;
}

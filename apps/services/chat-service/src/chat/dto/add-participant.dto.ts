/**
 * Add Participant DTO
 * بيانات إضافة مشارك جديد إلى محادثة
 *
 * Ported from the archived field-chat service. Matches the shape expected
 * by POST /chat/conversations/:id/participants.
 */

import { IsIn, IsOptional, IsString } from "class-validator";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

export class AddParticipantDto {
  @ApiProperty({
    description: "User ID of the participant to add",
    example: "user-789",
  })
  @IsString()
  userId: string;

  @ApiPropertyOptional({
    description: "Participant role within the conversation",
    enum: ["BUYER", "SELLER", "ADMIN"],
    default: "BUYER",
  })
  @IsOptional()
  @IsIn(["BUYER", "SELLER", "ADMIN"])
  role?: "BUYER" | "SELLER" | "ADMIN";
}

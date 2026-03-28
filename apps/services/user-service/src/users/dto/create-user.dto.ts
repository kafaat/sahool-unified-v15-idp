/**
 * Create User DTO
 * كائن نقل البيانات لإنشاء مستخدم
 */

import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import {
  IsEmail,
  IsString,
  IsEnum,
  IsOptional,
  MinLength,
  MaxLength,
  IsBoolean,
  IsUUID,
  ValidateIf,
} from "class-validator";
import { Transform } from "class-transformer";
import {
  IsYemeniPhone,
  IsStrongPassword,
  SanitizePlainText,
  UserRole,
  UserStatus,
} from "../../utils/validation";

export class CreateUserDto {
  @ApiPropertyOptional({
    description: "Tenant ID",
    example: "123e4567-e89b-12d3-a456-426614174000",
  })
  @IsOptional()
  @IsUUID("4", { message: "Tenant ID must be a valid UUID" })
  tenantId?: string;

  @ApiProperty({
    description: "User email address",
    example: "user@example.com",
  })
  @IsEmail()
  email: string;

  @ApiPropertyOptional({
    description: "User phone number (Yemen format: +967XXXXXXXX or 7XXXXXXXX)",
    example: "+967712345678",
  })
  @IsOptional()
  @IsYemeniPhone()
  phone?: string;

  @ApiProperty({
    description:
      "User password (min 8 characters, must contain uppercase, lowercase, number, and special character)",
    example: "SecurePassword123!",
  })
  @IsStrongPassword(8)
  password: string;

  @ApiPropertyOptional({
    description: "User full name (will be split into firstName and lastName)",
    example: "أحمد محمد",
  })
  @IsOptional()
  @IsString()
  @MinLength(2)
  @MaxLength(200)
  @SanitizePlainText()
  name?: string;

  @ApiPropertyOptional({
    description: "User first name",
    example: "أحمد",
  })
  @ValidateIf((o) => !o.name)
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @SanitizePlainText()
  firstName?: string;

  @ApiPropertyOptional({
    description: "User last name",
    example: "محمد",
  })
  @ValidateIf((o) => !o.name)
  @IsString()
  @MinLength(2)
  @MaxLength(100)
  @SanitizePlainText()
  lastName?: string;

  @ApiPropertyOptional({
    description: "User role",
    enum: UserRole,
    default: UserRole.VIEWER,
  })
  @IsOptional()
  @IsString()
  @Transform(({ value }) => {
    if (typeof value === "string") {
      return value.toUpperCase();
    }
    return value;
  })
  @IsEnum(UserRole)
  role?: UserRole;

  @ApiPropertyOptional({
    description: "User status",
    enum: UserStatus,
    default: UserStatus.PENDING,
  })
  @IsOptional()
  @IsString()
  @Transform(({ value }) => {
    if (typeof value === "string") {
      return value.toUpperCase();
    }
    return value;
  })
  @IsEnum(UserStatus)
  status?: UserStatus;

  @ApiPropertyOptional({
    description: "Email verification status",
    default: false,
  })
  @IsOptional()
  @IsBoolean()
  emailVerified?: boolean;

  @ApiPropertyOptional({
    description: "Phone verification status",
    default: false,
  })
  @IsOptional()
  @IsBoolean()
  phoneVerified?: boolean;
}
